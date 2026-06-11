#!/usr/bin/env python3
"""
cruzar_pendrive_spcf.py — Cruzamento pendrive x SPCF por orgao (NOVO — nao existia no DETRAN).

Consulta SOMENTE LEITURA (URI mode=ro) sobre prodam.db:
  pendrive_docs x spcf_faturas x cruzamento_spcf_pendrive

Resiliente a schema: roda PRAGMA table_info primeiro e escolhe as colunas por
listas de candidatos (o DB real tem ~3699 pendrive_docs, ~1460 cruzamento,
~1837 spcf_faturas — este ambiente nao tem o DB, por isso o --dry-run imprime
o plano de queries e sai com codigo 0).

Saida (CSV ';' utf-8-sig) em --out:
  cruzamento_<ORGAO>_<ts>.csv com coluna `categoria`:
    FATURA_SEM_DOC_PENDRIVE  — fatura do orgao sem documento de pendrive vinculado
    DOC_PENDRIVE_SEM_FATURA  — doc de pendrive (do orgao, se identificavel) sem fatura

Valores monetarios via Decimal (prodam_utils.brl/fmt_brl) — NUNCA float.

USO (Windows, a partir da raiz do PROJETO_PRODAM):
  py -3.12 scripts\\acervo\\cruzar_pendrive_spcf.py --db prodam.db --orgao SEDUC --out _SESSAO\\SEDUC
  py -3.12 scripts\\acervo\\cruzar_pendrive_spcf.py --db prodam.db --orgao SEDUC --out . --dry-run
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# prodam_utils mora em scripts/ (um nivel acima de scripts/acervo/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from prodam_utils import brl, fmt_brl, norm  # noqa: E402
except ImportError:  # fallback minimo se rodado fora do repo
    def brl(v):
        from decimal import Decimal as D, InvalidOperation
        if v in (None, ""):
            return D(0)
        s = str(v).replace("R$", "").replace(" ", "")
        if "," in s:
            s = s.replace(".", "").replace(",", ".")
        try:
            return D(s)
        except (InvalidOperation, ValueError):
            return D(0)

    def fmt_brl(v):
        d = v if isinstance(v, Decimal) else brl(v)
        return f"R$ {d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def norm(s):
        return str(s or "").strip().upper()

TABELAS = ["pendrive_docs", "spcf_faturas", "cruzamento_spcf_pendrive"]

# Candidatos de colunas (primeiro que existir vence; match case-insensitive)
CAND = {
    "fat_id":     ["id", "fatura_id", "numero_fatura", "num_fatura"],
    "fat_orgao":  ["orgao", "cliente", "devedor", "nome_cliente", "cliente_nome", "orgao_sigla"],
    "fat_valor":  ["valor", "valor_total", "val_servicos", "valor_servicos", "valor_fatura"],
    "fat_extra":  ["nf", "situacao", "vencimento", "emissao", "data_emissao", "contrato"],
    "cru_fat":    ["fatura_id", "spcf_id", "id_fatura", "fatura", "numero_fatura", "spcf_fatura_id"],
    "cru_doc":    ["pendrive_id", "doc_id", "id_doc", "pendrive_doc_id", "arquivo_id", "documento_id"],
    "doc_id":     ["id", "doc_id", "documento_id"],
    "doc_path":   ["caminho", "path", "arquivo", "filepath", "caminho_relativo", "nome", "nome_arquivo"],
    "doc_orgao":  ["orgao", "cliente", "devedor", "pasta", "orgao_sigla"],
}

COLS_OUT = ["categoria", "ref_id", "orgao", "descricao", "valor", "detalhe"]


def imprimir_plano(db: Path, orgao: str, out: Path):
    print("PLANO DE QUERIES (somente leitura, mode=ro):")
    print(f"  0. sqlite3.connect('file:{db}?mode=ro', uri=True)")
    for t in TABELAS:
        print(f"  1. PRAGMA table_info({t})  -- descobrir colunas reais")
    print("  2. Escolha resiliente de colunas (primeiro candidato existente):")
    for k, v in CAND.items():
        print(f"       {k}: {v}")
    print(f"  3. SELECT * FROM spcf_faturas WHERE upper(<fat_orgao>) LIKE '%{norm(orgao)}%'")
    print("  4. SELECT <cru_fat>, <cru_doc> FROM cruzamento_spcf_pendrive  -- join em Python")
    print("  5. SELECT <doc_id>, <doc_path>[, <doc_orgao>] FROM pendrive_docs")
    print("  6. Diferencas de conjuntos:")
    print("       FATURA_SEM_DOC_PENDRIVE = faturas do orgao - faturas presentes no cruzamento")
    print("       DOC_PENDRIVE_SEM_FATURA = docs (do orgao, se coluna existir) - docs no cruzamento")
    print(f"  7. Grava CSV ';' utf-8-sig em {out} | valores via Decimal (fmt_brl)")


def escolher(colunas: list[str], candidatos: list[str]) -> str | None:
    low = {c.lower(): c for c in colunas}
    for cand in candidatos:
        if cand.lower() in low:
            return low[cand.lower()]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Cruza pendrive_docs x spcf_faturas x cruzamento_spcf_pendrive (somente leitura).")
    ap.add_argument("--db", required=True, help="Caminho do prodam.db")
    ap.add_argument("--orgao", required=True, help="Sigla do devedor (ex: SEDUC)")
    ap.add_argument("--out", required=True, help="Pasta de saida do CSV")
    ap.add_argument("--dry-run", action="store_true",
                    help="So imprime o plano de queries e sai 0 (nao precisa do DB)")
    args = ap.parse_args()

    db = Path(args.db)
    out = Path(args.out)
    orgao = norm(args.orgao)

    if args.dry_run:
        imprimir_plano(db, orgao, out)
        if not db.exists() or db.stat().st_size == 0:
            print(f"\n[DRY-RUN] DB ausente/vazio neste ambiente ({db}) — plano acima e o contrato.")
        print("[DRY-RUN] nada foi consultado nem escrito.")
        return 0

    if not db.exists() or db.stat().st_size == 0:
        print(f"ERRO: DB ausente ou vazio: {db}", file=sys.stderr)
        return 1

    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # 1) Descobrir schema real
    schema: dict[str, list[str]] = {}
    for t in TABELAS:
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()]
        if not cols:
            todas = [r[0] for r in cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
            print(f"ERRO: tabela '{t}' nao existe no DB. Tabelas disponiveis: {todas}",
                  file=sys.stderr)
            return 1
        schema[t] = cols
        print(f"PRAGMA {t}: {cols}")

    # 2) Escolha resiliente de colunas
    fat_id = escolher(schema["spcf_faturas"], CAND["fat_id"])
    fat_orgao = escolher(schema["spcf_faturas"], CAND["fat_orgao"])
    fat_valor = escolher(schema["spcf_faturas"], CAND["fat_valor"])
    cru_fat = escolher(schema["cruzamento_spcf_pendrive"], CAND["cru_fat"])
    cru_doc = escolher(schema["cruzamento_spcf_pendrive"], CAND["cru_doc"])
    doc_id = escolher(schema["pendrive_docs"], CAND["doc_id"])
    doc_path = escolher(schema["pendrive_docs"], CAND["doc_path"])
    doc_orgao = escolher(schema["pendrive_docs"], CAND["doc_orgao"])

    faltando = [n for n, v in [("spcf_faturas.id", fat_id), ("spcf_faturas.orgao", fat_orgao),
                               ("cruzamento.fatura", cru_fat), ("cruzamento.doc", cru_doc),
                               ("pendrive_docs.id", doc_id)] if v is None]
    if faltando:
        print(f"ERRO: nao identifiquei colunas essenciais: {faltando}. "
              f"Ajuste CAND em {__file__} conforme PRAGMA acima.", file=sys.stderr)
        return 1
    print(f"\nColunas escolhidas: fat_id={fat_id} fat_orgao={fat_orgao} fat_valor={fat_valor} "
          f"cru_fat={cru_fat} cru_doc={cru_doc} doc_id={doc_id} doc_path={doc_path} "
          f"doc_orgao={doc_orgao}")

    # 3) Faturas do orgao
    faturas = cur.execute(
        f"SELECT * FROM spcf_faturas WHERE upper(COALESCE({fat_orgao},'')) LIKE ?",
        (f"%{orgao}%",)).fetchall()
    print(f"Faturas de {orgao} em spcf_faturas: {len(faturas)}")

    # 4) Cruzamento inteiro (join em Python — resiliente a tipos TEXT/INT)
    cruz = cur.execute(
        f"SELECT {cru_fat} AS f, {cru_doc} AS d FROM cruzamento_spcf_pendrive").fetchall()
    fat_com_doc = {str(r["f"]).strip() for r in cruz if r["f"] is not None}
    doc_com_fat = {str(r["d"]).strip() for r in cruz if r["d"] is not None}
    print(f"Vinculos no cruzamento: {len(cruz)} "
          f"(faturas distintas: {len(fat_com_doc)}, docs distintos: {len(doc_com_fat)})")

    # 5) Docs de pendrive (filtra por orgao se a coluna existir)
    if doc_orgao:
        docs = cur.execute(
            f"SELECT * FROM pendrive_docs WHERE upper(COALESCE({doc_orgao},'')) LIKE ?",
            (f"%{orgao}%",)).fetchall()
        escopo_docs = f"do orgao ({doc_orgao} LIKE %{orgao}%)"
    else:
        docs = cur.execute("SELECT * FROM pendrive_docs").fetchall()
        escopo_docs = "TODOS (sem coluna de orgao em pendrive_docs — revisar manualmente)"
    print(f"Docs de pendrive no escopo: {len(docs)} [{escopo_docs}]")

    # 6) Diferencas
    extras_fat = [c for c in CAND["fat_extra"] if escolher(schema["spcf_faturas"], [c])]
    rows_out: list[dict] = []
    total_sem_doc = Decimal(0)
    for f in faturas:
        fid = str(f[fat_id]).strip()
        if fid in fat_com_doc:
            continue
        valor = brl(f[fat_valor]) if fat_valor else Decimal(0)
        total_sem_doc += valor
        detalhe = " | ".join(f"{c}={f[c]}" for c in extras_fat if f[c] is not None)
        rows_out.append({
            "categoria": "FATURA_SEM_DOC_PENDRIVE",
            "ref_id": fid,
            "orgao": f[fat_orgao],
            "descricao": f"fatura {fid} sem documento de pendrive vinculado",
            "valor": fmt_brl(valor) if fat_valor else "",
            "detalhe": detalhe,
        })

    for d in docs:
        did = str(d[doc_id]).strip()
        if did in doc_com_fat:
            continue
        rows_out.append({
            "categoria": "DOC_PENDRIVE_SEM_FATURA",
            "ref_id": did,
            "orgao": (d[doc_orgao] if doc_orgao else ""),
            "descricao": (d[doc_path] if doc_path else f"doc {did}"),
            "valor": "",
            "detalhe": "doc de pendrive sem fatura SPCF vinculada",
        })
    con.close()

    # 7) Grava CSV
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = out / f"cruzamento_{orgao}_{ts}.csv"
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS_OUT, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in rows_out:
            w.writerow(r)

    n_fat = sum(1 for r in rows_out if r["categoria"] == "FATURA_SEM_DOC_PENDRIVE")
    n_doc = sum(1 for r in rows_out if r["categoria"] == "DOC_PENDRIVE_SEM_FATURA")
    print(f"\nRESUMO {orgao}:")
    print(f"  Faturas sem doc de pendrive : {n_fat} (valor {fmt_brl(total_sem_doc)})")
    print(f"  Docs de pendrive sem fatura : {n_doc}")
    print(f"  CSV: {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
