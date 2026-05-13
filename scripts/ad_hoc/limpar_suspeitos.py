"""
Remove sufixo `-SUSPEITO` dos PDFs cujos contratos foram promovidos ao whitelist.

Apos a triagem que descobriu 12 contratos historicos reais (001/2011, 028/2012,
023/2014, 005/2016, 011/2016, 014/2019, 008/2021, 078/2022, 021/2014, 024/2014,
026/2014, 017/2016), estes precisam deixar de ser marcados como suspeitos no
nome. Gera nome novo sem `-SUSPEITO`, renomeia in-place, grava log reversivel.

Input: log_renomeacao.csv (ultimo rename)
Output: _OUT_limpar_suspeitos_<ts>/
  - log_limpar_suspeitos.csv (nome_antigo -> nome_novo, sha256)
  - relatorio.md
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path

SKILL_PADROES = Path(r"C:\Users\gabri\.claude\skills\renomeador-pdfs-prodam\scripts")
sys.path.insert(0, str(SKILL_PADROES))
try:
    from padroes import MAPAS_POR_DEVEDOR, validar_contrato_canonico  # type: ignore
except Exception as e:
    print(f"[ERRO] Skill renomeador-pdfs-prodam nao acessivel: {e}")
    sys.exit(1)

MAPA_DETRAN = MAPAS_POR_DEVEDOR["DETRAN"]
RAIZ = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")


def acha_log_rename() -> Path:
    cand = sorted(
        RAIZ.glob("_OUT_rename_inplace_*/log_renomeacao.csv"),
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    if not cand:
        print("[ERRO] log_renomeacao.csv nao encontrado", file=sys.stderr)
        sys.exit(1)
    return cand[0]


def sha256_file(p: Path) -> str:
    try:
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def extrair_ct_do_suspeito(nome: str) -> tuple[str, str] | None:
    """Extrai (NNN, AAAA) de um nome tipo NE-YYYY-NNNNN_CT-028.2012-SUSPEITO_Ordinario.pdf"""
    m = re.search(r"CT-(\d{3})\.(\d{4})-SUSPEITO", nome)
    if m:
        return m.group(1), m.group(2)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    modo = "APPLY" if args.apply else "DRY-RUN"
    saida = RAIZ / f"_OUT_limpar_suspeitos_{ts}"
    saida.mkdir(parents=True, exist_ok=True)
    log_path = saida / "progresso.log"

    def log(m):
        linha = f"[{datetime.now().strftime('%H:%M:%S')}] {m}"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        print(linha, flush=True)

    log(f"Modo: {modo}")
    log_rename = acha_log_rename()
    log(f"Log fonte: {log_rename}")

    # Carrega log e filtra SUSPEITOs
    candidatos = []
    with open(log_rename, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f, delimiter=";"):
            if row.get("status") not in ("OK", "OK_SEM_HASH"):
                continue
            nome_atual = row["nome_novo"]  # nome apos v5
            if "-SUSPEITO" not in nome_atual:
                continue
            ct = extrair_ct_do_suspeito(nome_atual)
            if not ct:
                continue
            status = validar_contrato_canonico(ct, MAPA_DETRAN)
            if status == "canonico":
                candidatos.append({
                    "caminho_atual": row["caminho_novo"],
                    "nome_atual": nome_atual,
                    "contrato": f"{ct[0]}/{ct[1]}",
                    "status_validacao": status,
                })
    log(f"Candidatos a remover -SUSPEITO (promovidos a canonico): {len(candidatos)}")

    # Processa
    resultados = []
    ok = 0
    erro = 0
    for c in candidatos:
        p_atual = Path(c["caminho_atual"])
        nome_limpo = c["nome_atual"].replace("-SUSPEITO", "")
        p_novo = p_atual.parent / nome_limpo

        if not p_atual.exists():
            resultados.append({**c, "nome_limpo": nome_limpo, "status": "ARQUIVO_NAO_EXISTE",
                               "sha_antes": "", "sha_depois": "", "erro": "original nao existe"})
            erro += 1
            continue

        if args.apply:
            sha_antes = sha256_file(p_atual)
            try:
                # Dedup se ja existir
                if p_novo.exists() and p_novo != p_atual:
                    stem = p_novo.stem
                    suf = p_novo.suffix
                    i = 2
                    while True:
                        cand = p_novo.parent / f"{stem}_dup-{i:02d}{suf}"
                        if not cand.exists():
                            p_novo = cand
                            break
                        i += 1
                p_atual.rename(p_novo)
                sha_depois = sha256_file(p_novo)
                status_r = "OK" if sha_antes == sha_depois else "HASH_MISMATCH"
                erro_r = "" if status_r == "OK" else f"{sha_antes[:12]} vs {sha_depois[:12]}"
            except Exception as e:
                status_r = "ERRO"
                erro_r = str(e)[:200]
                sha_antes = sha_antes
                sha_depois = ""
                erro += 1
            else:
                ok += 1
        else:
            sha_antes = ""
            sha_depois = ""
            status_r = "DRY_RUN"
            erro_r = ""
            ok += 1

        resultados.append({
            **c,
            "nome_limpo": p_novo.name,
            "caminho_novo": str(p_novo),
            "sha_antes": sha_antes,
            "sha_depois": sha_depois,
            "status": status_r,
            "erro": erro_r,
        })

    # Grava CSV
    out_csv = saida / "log_limpar_suspeitos.csv"
    cols = ["caminho_atual", "nome_atual", "nome_limpo", "caminho_novo",
            "contrato", "status_validacao", "sha_antes", "sha_depois", "status", "erro"]
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in resultados:
            w.writerow(r)

    # Relatorio
    from collections import Counter
    por_ct = Counter(c["contrato"] for c in candidatos)
    md = [
        f"# Limpar SUSPEITOs — {ts} ({modo})",
        "",
        f"**Total candidatos:** {len(candidatos)}",
        f"**OK:** {ok}",
        f"**Erros:** {erro}",
        "",
        "## Por contrato (contratos promovidos a canonicos)",
        "| Contrato | Qtd |",
        "|---|---:|",
    ]
    for ct, n in por_ct.most_common():
        md.append(f"| {ct} | {n} |")
    (saida / "relatorio.md").write_text("\n".join(md), encoding="utf-8")

    log(f"OK: {ok} | Erros: {erro}")
    log(f"CSV: {out_csv}")
    log(f"MD: {saida / 'relatorio.md'}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
