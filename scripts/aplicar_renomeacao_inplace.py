"""
Aplica renomeacao IN-PLACE nos PDFs DETRAN segundo o CSV v5 do classificador.

Seguranca:
  - Verifica SHA-256 antes (ja no CSV) e depois do rename — conferencia de integridade
  - Dedup por suffix `_dup-NN.pdf` quando multiplos PDFs geram mesmo nome canonico
  - Grava log reversivel em `log_renomeacao.csv` (usavel para rollback)
  - Idempotente: se o rename ja foi feito, pula
  - Nao renomeia se nome_canonico == nome_original ou vazio
  - Nao apaga bytes — so altera nome (cumpre regra juridica PRODAM)

Uso:
  py -3.12 aplicar_renomeacao_inplace.py           # dry-run (default, nao renomeia)
  py -3.12 aplicar_renomeacao_inplace.py --apply   # aplica in-place
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import traceback
from collections import Counter
from datetime import datetime
from pathlib import Path

RAIZ_PROJETO = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")


def sha256_file(p: Path) -> str:
    try:
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def encontrar_csv_v5() -> Path:
    cand = sorted(
        RAIZ_PROJETO.glob("_OUT_conteudo_*/renomear_proposto_conteudo.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not cand:
        print("[ERRO] Nenhum CSV v5 encontrado.", file=sys.stderr)
        sys.exit(1)
    return cand[0]


def dedup_nome(destino: Path, usados: set[str]) -> Path:
    """Retorna destino unico. Se colidir, adiciona _dup-02, _dup-03..."""
    if str(destino) not in usados and not destino.exists():
        usados.add(str(destino))
        return destino
    stem = destino.stem
    suf = destino.suffix
    i = 2
    while True:
        cand = destino.parent / f"{stem}_dup-{i:02d}{suf}"
        if str(cand) not in usados and not cand.exists():
            usados.add(str(cand))
            return cand
        i += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Aplica o rename in-place (default: dry-run)")
    parser.add_argument("--csv", type=str, default=None,
                        help="CSV v5 (default: mais recente)")
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    modo = "APPLY" if args.apply else "DRY-RUN"

    saida = RAIZ_PROJETO / f"_OUT_rename_inplace_{ts}"
    saida.mkdir(parents=True, exist_ok=True)
    log_path = saida / "progresso.log"
    resultado_csv = saida / "log_renomeacao.csv"

    def log(m):
        linha = f"[{datetime.now().strftime('%H:%M:%S')}] {m}"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        print(linha, flush=True)

    log(f"Modo: {modo}")
    log(f"Saida: {saida}")

    csv_v5 = Path(args.csv) if args.csv else encontrar_csv_v5()
    log(f"CSV v5: {csv_v5}")

    # Ler CSV v5
    rows = []
    with open(csv_v5, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    log(f"Total PDFs no CSV: {len(rows)}")

    # Filtrar: status=OK, nome_canonico != nome_original, nome_canonico nao vazio
    alvos = []
    skipped_iguais = 0
    skipped_vazios = 0
    skipped_status = 0
    for r in rows:
        if r.get("status") != "OK":
            skipped_status += 1
            continue
        nc = r.get("nome_canonico", "").strip()
        no = r.get("nome_original", "").strip()
        if not nc:
            skipped_vazios += 1
            continue
        if nc == no:
            skipped_iguais += 1
            continue
        alvos.append(r)
    log(f"Alvos validos: {len(alvos)}")
    log(f"  Skipped status!=OK: {skipped_status}")
    log(f"  Skipped nome_canonico vazio: {skipped_vazios}")
    log(f"  Skipped nome igual original: {skipped_iguais}")

    # Executar renames (ou simular)
    resultados = []
    usados: set[str] = set()
    ok_count = 0
    erro_count = 0
    dedup_count = 0
    hash_ok = 0
    hash_fail = 0
    ja_renomeado = 0

    for r in alvos:
        caminho_orig = Path(r["caminho_original"])
        nome_novo_propos = r["nome_canonico"]
        destino_propos = caminho_orig.parent / nome_novo_propos
        sha_csv = r.get("sha256", "")
        tipo = r.get("tipo_final", "")

        # Idempotencia: se original nao existe mas destino existe, skip
        if not caminho_orig.exists():
            if destino_propos.exists():
                ja_renomeado += 1
                resultados.append({
                    "caminho_original": str(caminho_orig),
                    "nome_original": caminho_orig.name,
                    "nome_novo": destino_propos.name,
                    "caminho_novo": str(destino_propos),
                    "sha256_antes": sha_csv,
                    "sha256_depois": "",
                    "tipo_final": tipo,
                    "status": "JA_RENOMEADO",
                    "erro": "",
                })
                continue
            resultados.append({
                "caminho_original": str(caminho_orig),
                "nome_original": caminho_orig.name,
                "nome_novo": "", "caminho_novo": "",
                "sha256_antes": sha_csv, "sha256_depois": "",
                "tipo_final": tipo, "status": "ARQUIVO_NAO_EXISTE",
                "erro": "original nao encontrado no disco",
            })
            erro_count += 1
            continue

        # Dedup
        destino_final = dedup_nome(destino_propos, usados)
        if destino_final != destino_propos:
            dedup_count += 1

        if args.apply:
            try:
                caminho_orig.rename(destino_final)
                sha_depois = sha256_file(destino_final)
                integ = (sha_depois == sha_csv) if sha_csv else None
                if integ is True:
                    hash_ok += 1
                    status = "OK"
                    erro = ""
                elif integ is False:
                    hash_fail += 1
                    status = "HASH_MISMATCH"
                    erro = f"sha antes={sha_csv[:12]} depois={sha_depois[:12]}"
                else:
                    status = "OK_SEM_HASH"
                    erro = ""
                ok_count += 1
            except Exception as e:
                status = "ERRO_RENAME"
                erro = str(e)[:200]
                sha_depois = ""
                erro_count += 1
        else:
            # dry-run
            status = "DRY_RUN"
            erro = ""
            sha_depois = ""
            ok_count += 1

        resultados.append({
            "caminho_original": str(caminho_orig),
            "nome_original": caminho_orig.name,
            "nome_novo": destino_final.name,
            "caminho_novo": str(destino_final),
            "sha256_antes": sha_csv,
            "sha256_depois": sha_depois,
            "tipo_final": tipo,
            "status": status,
            "erro": erro,
        })

        if (ok_count + erro_count) % 200 == 0:
            log(f"  progresso: {ok_count + erro_count}/{len(alvos)}")

    # Grava log
    cols = ["caminho_original", "nome_original", "nome_novo", "caminho_novo",
            "sha256_antes", "sha256_depois", "tipo_final", "status", "erro"]
    with open(resultado_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in resultados:
            w.writerow(r)

    # Resumo
    tipos = Counter(r.get("tipo_final", "?") for r in resultados)
    log("")
    log("=" * 60)
    log(f"RESUMO ({modo})")
    log(f"  Alvos: {len(alvos)}")
    log(f"  OK (renomeados ou dry-run): {ok_count}")
    log(f"  Erros: {erro_count}")
    log(f"  Ja renomeados (idempotencia): {ja_renomeado}")
    log(f"  Dedup aplicados (_dup-NN): {dedup_count}")
    if args.apply:
        log(f"  Hash OK (bytes identicos): {hash_ok}")
        log(f"  Hash mismatch: {hash_fail}")
    log(f"  Por tipo: {dict(tipos.most_common())}")
    log(f"  Log: {resultado_csv}")
    log("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
