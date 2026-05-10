"""
Sincroniza referencias aos PDFs renomeados no profiles.json e nos 5 prodam.db.

Dry-run (default): conta referencias encontradas sem modificar nada.
--apply: faz backup + substituicao dos nomes.

Usa log_renomeacao.csv como mapa (nome_original -> nome_novo).

Seguranca:
  - Backup .BAK_<ts> antes de qualquer escrita
  - Dry-run conta referencias, mostra amostra
  - Reversivel: basta restaurar .BAK_

Uso:
  py -3.12 sincronizar_referencias.py              # dry-run
  py -3.12 sincronizar_referencias.py --apply      # aplica
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sqlite3
import sys
import traceback
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

RAIZ = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")

ALVOS_JSON = [
    Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\profiles.json"),
]

ALVOS_DB = [
    Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM\prodam.db"),
    Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_ANALISE\prodam.db"),
    Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM\detran_dashboard\data-real\prodam.db"),
    # NOTA: DBs em DETRAN_AUDITORIA_COMPLETA ficam fora do escopo por padrao.
    # O usuario pediu pra nao mexer naquela pasta (rodando OCR em paralelo).
    # Se quiser incluir, passar via --incluir-detran-auditoria.
]

ALVOS_DB_DETRAN_AUD = [
    Path(r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\16_BANCOS_DADOS\prodam.db"),
    Path(r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\detran_dashboard\data-real\prodam.db"),
]


def acha_log_rename() -> Path:
    cand = sorted(
        RAIZ.glob("_OUT_rename_inplace_*/log_renomeacao.csv"),
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    if not cand:
        print("[ERRO] log_renomeacao.csv nao encontrado", file=sys.stderr)
        sys.exit(1)
    return cand[0]


def carregar_mapa(log: Path) -> dict[str, str]:
    """Retorna {nome_original: nome_novo} filtrando casos validos."""
    m = {}
    with open(log, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f, delimiter=";"):
            if row.get("status") not in ("OK", "OK_SEM_HASH"):
                continue
            nome_antigo = row["nome_original"]
            nome_novo = row["nome_novo"]
            if nome_antigo and nome_novo and nome_antigo != nome_novo:
                m[nome_antigo] = nome_novo
    return m


def contar_refs_json(path: Path, mapa: dict[str, str]) -> dict:
    """Le JSON como texto, conta quantas vezes cada nome_antigo aparece."""
    if not path.exists():
        return {"path": str(path), "exists": False, "refs": 0, "detalhe": {}}
    try:
        texto = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"path": str(path), "exists": True, "erro": str(e)}
    detalhe = {}
    total = 0
    for antigo in mapa:
        c = texto.count(antigo)
        if c > 0:
            detalhe[antigo] = c
            total += c
    return {"path": str(path), "exists": True, "refs": total, "detalhe": detalhe,
            "tamanho_bytes": path.stat().st_size}


def contar_refs_db(path: Path, mapa: dict[str, str]) -> dict:
    """Procura cada nome_antigo em todas colunas TEXT do DB."""
    if not path.exists():
        return {"path": str(path), "exists": False}
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        cur = con.cursor()
    except Exception as e:
        return {"path": str(path), "exists": True, "erro": str(e)}

    tabelas = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%'"
    ).fetchall()]

    refs_por_tabela = {}
    total = 0
    # Pra eficiencia, concatena todo texto do DB numa string e conta por substring.
    # Simplificacao: dump textual de cada tabela (pode ser pesado pra DBs grandes).
    for t in tabelas:
        try:
            cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()
                    if r[2].upper() in ("TEXT", "")]
            if not cols:
                continue
            # Concatena todas colunas TEXT
            sel = " || ' ' || ".join(f"COALESCE(CAST({c} AS TEXT), '')" for c in cols)
            rows = cur.execute(f"SELECT {sel} FROM {t}").fetchall()
            dump = " ".join(r[0] for r in rows if r[0])
        except Exception as e:
            refs_por_tabela[t] = {"erro": str(e)}
            continue

        detalhe_t = {}
        subtotal = 0
        for antigo in mapa:
            c = dump.count(antigo)
            if c > 0:
                detalhe_t[antigo] = c
                subtotal += c
        if subtotal > 0:
            refs_por_tabela[t] = {"refs": subtotal, "amostra": dict(list(detalhe_t.items())[:5])}
            total += subtotal

    con.close()
    return {"path": str(path), "exists": True, "refs": total, "tabelas": refs_por_tabela}


def aplicar_json(path: Path, mapa: dict[str, str], backup_dir: Path) -> dict:
    """Substitui nomes antigos por novos em arquivo JSON (modo texto)."""
    if not path.exists():
        return {"path": str(path), "status": "NAO_EXISTE"}
    bak = backup_dir / f"{path.name}.BAK"
    shutil.copy2(path, bak)
    texto = path.read_text(encoding="utf-8")
    subs = 0
    for antigo, novo in mapa.items():
        if antigo in texto:
            c = texto.count(antigo)
            texto = texto.replace(antigo, novo)
            subs += c
    path.write_text(texto, encoding="utf-8")
    return {"path": str(path), "status": "OK", "substituicoes": subs,
            "backup": str(bak)}


def aplicar_db(path: Path, mapa: dict[str, str], backup_dir: Path) -> dict:
    """Para cada tabela/coluna TEXT, aplica UPDATE substituindo nomes."""
    if not path.exists():
        return {"path": str(path), "status": "NAO_EXISTE"}
    bak = backup_dir / f"{path.name}.BAK"
    shutil.copy2(path, bak)

    con = sqlite3.connect(path)
    cur = con.cursor()
    tabelas = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%'"
    ).fetchall()]
    total_subs = 0
    por_tabela = {}
    for t in tabelas:
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()
                if r[2].upper() in ("TEXT", "")]
        sub_t = 0
        for col in cols:
            for antigo, novo in mapa.items():
                try:
                    r = cur.execute(
                        f"UPDATE {t} SET {col} = REPLACE({col}, ?, ?) "
                        f"WHERE {col} LIKE '%' || ? || '%'",
                        (antigo, novo, antigo)
                    )
                    sub_t += r.rowcount if r.rowcount else 0
                except Exception:
                    pass
        if sub_t > 0:
            por_tabela[t] = sub_t
            total_subs += sub_t
    con.commit()
    con.close()
    return {"path": str(path), "status": "OK", "substituicoes": total_subs,
            "tabelas": por_tabela, "backup": str(bak)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Aplica substituicao")
    parser.add_argument("--incluir-detran-auditoria", action="store_true",
                        help="Inclui DBs em DETRAN_AUDITORIA_COMPLETA (cuidado)")
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    modo = "APPLY" if args.apply else "DRY-RUN"

    saida = RAIZ / f"_OUT_sync_referencias_{ts}"
    saida.mkdir(parents=True, exist_ok=True)
    log_path = saida / "progresso.log"
    backup_dir = saida / "backups"
    backup_dir.mkdir(exist_ok=True)

    def log(m):
        linha = f"[{datetime.now().strftime('%H:%M:%S')}] {m}"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        print(linha, flush=True)

    log(f"Modo: {modo}")
    log_rename = acha_log_rename()
    mapa = carregar_mapa(log_rename)
    log(f"Mapa: {len(mapa)} pares (nome_antigo -> nome_novo)")

    dbs_alvo = list(ALVOS_DB)
    if args.incluir_detran_auditoria:
        dbs_alvo.extend(ALVOS_DB_DETRAN_AUD)

    relatorio = {
        "data": datetime.now().isoformat(),
        "modo": modo,
        "mapa_size": len(mapa),
        "json": [],
        "db": [],
    }

    # JSON
    log("=== PROCESSANDO JSON ===")
    for path in ALVOS_JSON:
        r = contar_refs_json(path, mapa)
        log(f"  {path}: refs={r.get('refs', 0)}")
        if args.apply and r.get("refs", 0) > 0:
            r_apply = aplicar_json(path, mapa, backup_dir)
            r.update(r_apply)
            log(f"    APLICADO: {r_apply.get('substituicoes')} substituicoes, backup={r_apply.get('backup')}")
        relatorio["json"].append(r)

    # DBs
    log("=== PROCESSANDO DBs ===")
    for path in dbs_alvo:
        r = contar_refs_db(path, mapa)
        log(f"  {path}: refs={r.get('refs', 0)} | exists={r.get('exists')}")
        if args.apply and r.get("refs", 0) > 0:
            r_apply = aplicar_db(path, mapa, backup_dir)
            r.update(r_apply)
            log(f"    APLICADO: {r_apply.get('substituicoes')} UPDATEs | backup={r_apply.get('backup')}")
        relatorio["db"].append(r)

    # Salvar relatorio
    out_json = saida / "relatorio_sync.json"
    out_json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    log(f"Relatorio: {out_json}")

    # Resumo MD
    total_json_refs = sum(j.get("refs", 0) for j in relatorio["json"])
    total_db_refs = sum(d.get("refs", 0) for d in relatorio["db"])
    md = [
        f"# Sync Referencias — {ts} ({modo})",
        "",
        f"**Mapa:** {len(mapa)} pares",
        f"**Total refs em JSON:** {total_json_refs}",
        f"**Total refs em DBs:** {total_db_refs}",
        "",
        "## JSON",
    ]
    for j in relatorio["json"]:
        md.append(f"- `{j['path']}`: {j.get('refs', 0)} refs")
    md.append("\n## DBs")
    for d in relatorio["db"]:
        md.append(f"- `{d['path']}`: {d.get('refs', 0)} refs")
        for t, info in (d.get("tabelas") or {}).items():
            if isinstance(info, dict) and "refs" in info:
                md.append(f"  - tabela `{t}`: {info['refs']} refs")
    out_md = saida / "relatorio_sync.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    log(f"MD: {out_md}")
    log("TERMINOU")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
