#!/usr/bin/env python3
"""consultas.py — 15 queries de auditoria forense do prodam.db.

Uso:
    py -3.12 consultas.py <consulta> [--csv]
    py -3.12 consultas.py --lista
"""
from __future__ import annotations

import argparse
import csv
import datetime
import sqlite3
import sys
import time
from decimal import Decimal
from pathlib import Path

DB_PATH = Path(__file__).parent / "prodam.db"
CSV_DIR = Path(__file__).parent / "_ANALISE" / "consultas_csv"

CURRENT_YEAR  = datetime.datetime.now().year
PRESCRIC_YEAR = CURRENT_YEAR - 4

PRIVADO_LIKE = (
    "(cliente LIKE '%LTDA%' OR cliente LIKE '%S.A.%' OR cliente LIKE '%S/A%' "
    "OR cliente LIKE '%EIRELI%' OR cliente LIKE '%BANCO%' OR cliente LIKE '%CAIXA%' "
    "OR cliente LIKE '%BRADESCO%' OR cliente LIKE '%FINANCIAMENTO%' OR cliente LIKE '%CRED%' "
    "OR cliente LIKE '%PROVER%' OR cliente LIKE '%MASTER%' OR cliente LIKE '%SALUX%' "
    "OR cliente LIKE '%PROMO%')"
)

# ============================== format helpers =============================

def brl(v) -> str:
    if v is None:
        return ""
    try:
        d = Decimal(str(v))
    except Exception:
        return str(v)
    s = f"{d:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {s}"

def is_brl_col(name: str) -> bool:
    n = str(name).lower()
    return "valor" in n

def format_cell(col: str, value) -> str:
    if value is None:
        return ""
    if is_brl_col(col) and isinstance(value, (int, float, Decimal)):
        return brl(value)
    if isinstance(value, float):
        return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")
    return str(value)

def print_table(cols, rows, max_rows=50):
    formatted = [[format_cell(cols[i], v) for i, v in enumerate(r)] for r in rows]
    widths = [len(str(c)) for c in cols]
    for fr in formatted[:max_rows]:
        for i, v in enumerate(fr):
            widths[i] = max(widths[i], len(v))
    print(" | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cols)))
    print("-+-".join("-" * w for w in widths))
    for fr in formatted[:max_rows]:
        print(" | ".join(fr[i].ljust(widths[i]) for i in range(len(cols))))
    total = len(rows)
    if total > max_rows:
        print(f"  ... +{total - max_rows:,} linhas omitidas")
    print(f"\n  Total: {total:,} linha(s)")

def export_csv(name, cols, rows) -> Path:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = CSV_DIR / f"{name}_{ts}.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cols)
        for r in rows:
            w.writerow([format_cell(cols[i], v) for i, v in enumerate(r)])
    print(f"\n[CSV] exportado: {path}  ({len(rows):,} linhas)")
    return path

# ============================== composite query ===========================

def q_resumo_geral(conn):
    tbls = ["spcf_contratos", "spcf_empenhos", "spcf_faturas", "spcf_nfs",
            "pendrive_docs", "devedores", "reclassificacao", "cruzamento_spcf_pendrive"]
    rows_t = [(t, conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]) for t in tbls]

    rows_c = list(conn.execute("""
        SELECT COALESCE(cadeia_completude, '(null)') cadeia,
               COUNT(*) qtd,
               COALESCE(SUM(valor_bruto), 0) valor_total
        FROM spcf_faturas
        GROUP BY cadeia_completude
        ORDER BY qtd DESC
    """).fetchall())

    com = conn.execute("SELECT COUNT(*) FROM spcf_nfs WHERE tem_pagamento=1").fetchone()[0]
    sem = conn.execute("SELECT COUNT(*) FROM spcf_nfs WHERE tem_pagamento=0").fetchone()[0]
    vt  = conn.execute("SELECT COALESCE(SUM(valor_bruto),0) FROM spcf_faturas").fetchone()[0]
    va  = conn.execute("""
        SELECT COALESCE(SUM(f.valor_bruto),0)
        FROM spcf_faturas f
        JOIN spcf_nfs n ON n.numero_nf = f.nf
        WHERE n.tem_pagamento = 0
    """).fetchone()[0]
    vse = conn.execute("""
        SELECT COALESCE(SUM(valor_bruto),0), COUNT(*)
        FROM spcf_faturas
        WHERE total_empenhos_vinculados = 0 AND valor_bruto > 0
    """).fetchone()
    pct_pg = com / (com + sem) * 100 if (com + sem) else 0

    rows_m = [
        ("NFs com pagamento",           f"{com:,}".replace(",", ".")),
        ("NFs sem pagamento",           f"{sem:,}".replace(",", ".")),
        ("% NFs pagas",                 f"{pct_pg:.1f}%"),
        ("Valor total faturas",         brl(vt)),
        ("Valor em aberto (NF s/ pg)",  brl(va)),
        ("Faturas sem empenho",         f"{vse[1]:,}".replace(",", ".")),
        ("Valor sem empenho",           brl(vse[0])),
    ]

    return [
        ("Totais por tabela", ["tabela", "registros"], rows_t),
        ("Cadeia 5 elos",     ["cadeia", "qtd", "valor_total"], rows_c),
        ("Métricas globais",  ["métrica", "valor"], rows_m),
    ]

# ============================== query registry ============================

QUERIES = {
    "resumo_geral": {
        "desc": "Totais por tabela + cadeia 5 elos + métricas globais",
        "composite": True,
        "fn": q_resumo_geral,
    },
    "top_devedores": {
        "desc": "Ranking por valor (faturas COMPLETA + FORTE)",
        "sql": """
            SELECT cliente,
                   COUNT(*) qtd_faturas,
                   SUM(valor_bruto) valor_total
            FROM spcf_faturas
            WHERE cadeia_completude IN ('COMPLETA', 'FORTE')
              AND cliente IS NOT NULL
              AND valor_bruto > 0
            GROUP BY cliente
            ORDER BY valor_total DESC
        """,
    },
    "cadeia_por_devedor": {
        "desc": "Distribuição COMPLETA/FORTE/MEDIA/FRACA por cliente",
        "sql": """
            SELECT cliente,
                   SUM(CASE WHEN cadeia_completude='COMPLETA' THEN 1 ELSE 0 END) completa,
                   SUM(CASE WHEN cadeia_completude='FORTE'    THEN 1 ELSE 0 END) forte,
                   SUM(CASE WHEN cadeia_completude='MEDIA'    THEN 1 ELSE 0 END) media,
                   SUM(CASE WHEN cadeia_completude='FRACA'    THEN 1 ELSE 0 END) fraca,
                   COUNT(*) total,
                   COALESCE(SUM(valor_bruto), 0) valor_total
            FROM spcf_faturas
            WHERE cliente IS NOT NULL
            GROUP BY cliente
            ORDER BY valor_total DESC
        """,
    },
    "faturas_sem_empenho": {
        "desc": "Faturas sem empenho vinculado (gap real), por valor",
        "sql": """
            SELECT cliente, nf, contrato_num, competencia,
                   valor_bruto, situacao, cadeia_completude
            FROM spcf_faturas
            WHERE total_empenhos_vinculados = 0
              AND valor_bruto > 0
            ORDER BY valor_bruto DESC
        """,
    },
    "faturas_completas": {
        "desc": "Faturas com cadeia COMPLETA (5 elos fechados)",
        "sql": """
            SELECT cliente, nf, contrato_num, competencia, valor_bruto, situacao
            FROM spcf_faturas
            WHERE cadeia_completude = 'COMPLETA'
              AND valor_bruto > 0
            ORDER BY valor_bruto DESC
        """,
    },
    "nfs_sem_pagamento": {
        "desc": "NFs liquidadas sem pagamento (R$ em aberto)",
        "sql": """
            SELECT f.cliente, f.nf, f.competencia,
                   f.valor_bruto, f.cadeia_completude
            FROM spcf_faturas f
            JOIN spcf_nfs n ON n.numero_nf = f.nf
            WHERE n.tem_pagamento = 0
              AND f.valor_bruto > 0
            ORDER BY f.valor_bruto DESC
        """,
    },
    "nfs_pagas_por_devedor": {
        "desc": "Taxa de pagamento por devedor (% pagas, R$ aberto)",
        "sql": """
            SELECT f.cliente,
                   COUNT(*) total_nfs,
                   SUM(CASE WHEN n.tem_pagamento=1 THEN 1 ELSE 0 END) pagas,
                   ROUND(100.0 * SUM(CASE WHEN n.tem_pagamento=1 THEN 1 ELSE 0 END) / COUNT(*), 1) pct_pagas,
                   COALESCE(SUM(f.valor_bruto), 0) valor_total,
                   COALESCE(SUM(CASE WHEN n.tem_pagamento=0 THEN f.valor_bruto ELSE 0 END), 0) valor_aberto
            FROM spcf_faturas f
            JOIN spcf_nfs n ON n.numero_nf = f.nf
            WHERE f.cliente IS NOT NULL
            GROUP BY f.cliente
            ORDER BY valor_aberto DESC
        """,
    },
    "gap_nf_spcf_sem_pendrive": {
        "desc": "NFs do SPCF sem documento físico no pen drive",
        "sql": """
            SELECT f.cliente, f.nf, f.competencia,
                   f.valor_bruto, f.cadeia_completude
            FROM spcf_faturas f
            LEFT JOIN cruzamento_spcf_pendrive c ON c.numero_nf = f.nf
            WHERE c.numero_nf IS NULL
              AND f.valor_bruto > 0
            ORDER BY f.valor_bruto DESC
        """,
    },
    "gap_nf_pendrive_sem_spcf": {
        "desc": "NFs físicas no pen drive sem correspondência no SPCF",
        "sql": """
            SELECT p.devedor_pasta, p.arquivo, p.caminho
            FROM pendrive_docs p
            LEFT JOIN cruzamento_spcf_pendrive c ON c.hash_pendrive = p.hash
            WHERE p.tipo_documento = 'NOTA_FISCAL'
              AND c.hash_pendrive IS NULL
            ORDER BY p.devedor_pasta, p.arquivo
        """,
    },
    "cobertura_cruzada": {
        "desc": "% de match NF × pen drive por devedor",
        "sql": """
            SELECT p.devedor_pasta,
                   COUNT(DISTINCT CASE WHEN p.tipo_documento='NOTA_FISCAL' THEN p.hash END) nfs_pendrive,
                   COUNT(DISTINCT c.hash_pendrive) com_match,
                   ROUND(100.0 * COUNT(DISTINCT c.hash_pendrive) /
                         NULLIF(COUNT(DISTINCT CASE WHEN p.tipo_documento='NOTA_FISCAL' THEN p.hash END), 0), 1) pct_cobertura
            FROM pendrive_docs p
            LEFT JOIN cruzamento_spcf_pendrive c ON c.hash_pendrive = p.hash
            WHERE p.devedor_pasta IS NOT NULL
            GROUP BY p.devedor_pasta
            HAVING nfs_pendrive > 0
            ORDER BY pct_cobertura DESC, nfs_pendrive DESC
        """,
    },
    "faturas_por_competencia": {
        "desc": "Faturas agrupadas por ano/mês de competência",
        "sql": """
            SELECT SUBSTR(competencia, 4, 4) ano,
                   SUBSTR(competencia, 1, 2) mes,
                   COUNT(*) qtd,
                   COALESCE(SUM(valor_bruto), 0) valor_total
            FROM spcf_faturas
            WHERE competencia IS NOT NULL
              AND LENGTH(competencia) = 7
            GROUP BY ano, mes
            ORDER BY ano DESC, mes DESC
        """,
    },
    "faturas_antigas": {
        "desc": f"Faturas com competência < {PRESCRIC_YEAR} (risco prescrição)",
        "sql": """
            SELECT cliente, nf, contrato_num, competencia,
                   valor_bruto, cadeia_completude
            FROM spcf_faturas
            WHERE competencia IS NOT NULL
              AND LENGTH(competencia) = 7
              AND CAST(SUBSTR(competencia, 4, 4) AS INTEGER) < ?
              AND valor_bruto > 0
            ORDER BY SUBSTR(competencia, 4, 4) ASC,
                     SUBSTR(competencia, 1, 2) ASC,
                     valor_bruto DESC
        """,
        "params": (PRESCRIC_YEAR,),
    },
    "privados_sem_empenho": {
        "desc": "Devedores privados sem empenho (alvo monitória/cobrança)",
        "sql": f"""
            SELECT cliente,
                   COUNT(*) qtd_faturas,
                   COALESCE(SUM(valor_bruto), 0) valor_total
            FROM spcf_faturas
            WHERE total_empenhos_vinculados = 0
              AND valor_bruto > 0
              AND {PRIVADO_LIKE}
            GROUP BY cliente
            ORDER BY valor_total DESC
        """,
    },
    "privados_top_valor": {
        "desc": "Ranking de devedores privados por valor total",
        "sql": f"""
            SELECT cliente,
                   COUNT(*) qtd_faturas,
                   COALESCE(SUM(valor_bruto), 0) valor_total,
                   SUM(CASE WHEN total_empenhos_vinculados = 0 THEN 1 ELSE 0 END) sem_empenho
            FROM spcf_faturas
            WHERE valor_bruto > 0
              AND {PRIVADO_LIKE}
            GROUP BY cliente
            ORDER BY valor_total DESC
        """,
    },
    "pendrive_desconhecido": {
        "desc": "Documentos ainda DESCONHECIDO por devedor (pen drive)",
        "sql": """
            SELECT devedor_pasta, COUNT(*) qtd
            FROM pendrive_docs
            WHERE tipo_documento = 'DESCONHECIDO'
              AND devedor_pasta IS NOT NULL
            GROUP BY devedor_pasta
            ORDER BY qtd DESC
        """,
    },
}

# ============================== runner ====================================

def run_query(name: str, csv_flag: bool):
    if name not in QUERIES:
        print(f"ERRO: consulta '{name}' não existe.", file=sys.stderr)
        print("Use --lista para ver as disponíveis.", file=sys.stderr)
        sys.exit(2)

    if not DB_PATH.exists():
        print(f"ERRO: DB não encontrado em {DB_PATH}", file=sys.stderr)
        sys.exit(3)

    q = QUERIES[name]
    print(f"=== {name}  —  {q['desc']} ===")
    print(f"DB: {DB_PATH}")
    t0 = time.time()
    conn = sqlite3.connect(DB_PATH)

    if q.get("composite"):
        for subtitle, cols, rows in q["fn"](conn):
            print(f"\n-- {subtitle} --")
            print_table(cols, rows)
        if csv_flag:
            print("\n[CSV] consulta composta — exportação não suportada.")
    else:
        cur = conn.execute(q["sql"], q.get("params", ()))
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
        print()
        print_table(cols, rows)
        if csv_flag:
            export_csv(name, cols, rows)

    conn.close()
    print(f"\n[tempo] {time.time() - t0:.2f}s")

def listar():
    print("Consultas disponíveis:\n")
    w = max(len(k) for k in QUERIES)
    for name, q in QUERIES.items():
        tag = "  [composta]" if q.get("composite") else ""
        print(f"  {name:<{w}}  — {q['desc']}{tag}")
    print(f"\nUso: py -3.12 consultas.py <nome> [--csv]")

def main():
    ap = argparse.ArgumentParser(description="Queries forenses do prodam.db")
    ap.add_argument("consulta", nargs="?", help="Nome da consulta (veja --lista)")
    ap.add_argument("--csv", action="store_true", help="Exportar CSV (UTF-8 BOM, ';')")
    ap.add_argument("--lista", action="store_true", help="Lista consultas disponíveis")
    args = ap.parse_args()

    if args.lista or not args.consulta:
        listar()
        return

    run_query(args.consulta, args.csv)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
