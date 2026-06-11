#!/usr/bin/env python3
"""
ocr_lote.py — OCR em lote dos PDFs sem texto detectados pelo inventario (portado do DETRAN).

Origem: DETRAN_AUDITORIA_COMPLETA/10_SCRIPTS_PYTHON/ocr_lote_sem_texto.py
Mudancas no porte:
  - Paths hardcoded substituidos por argparse (--universo/--out).
  - A funcao ocr_pdf_cascata() vinha da skill `ocr-pdfs-prodam` (nao versionada):
    reimplementada inline via subprocess `ocrmypdf --skip-text --deskew` com timeout.
  - Fallback gracioso: se o binario `ocrmypdf` estiver ausente, registra SKIP
    no CSV de resultado em vez de abortar.

REGRA PROBATORIA (CLAUDE.md NUNCA-1): o original NUNCA e tocado.
Sempre gera `arquivo.ocr.pdf` AO LADO do original. Se o .ocr.pdf ja existe,
registra SKIP_EXISTENTE (nunca sobrescreve).

Saidas em --out:
  resultado_ocr.csv  (caminho, status, pdf_pesquisavel, paginas, segundos, detalhe)
  relatorio.md
  progresso.log

Uso (Windows):
  py -3.12 scripts\\acervo\\ocr_lote.py --universo <out_inventario>\\universo.csv ^
      --out <out_inventario>\\__OCR --threads 4
  py -3.12 scripts\\acervo\\ocr_lote.py --universo ... --out ... --limit 5 --dry-run
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

OCR_TIMEOUT_SEG = 300  # 5 min por PDF (deskew em scans grandes e lento)
COLS = ["caminho", "nome", "status", "pdf_pesquisavel", "paginas", "segundos", "detalhe"]


def contar_paginas(p: Path) -> int:
    try:
        import fitz  # pymupdf — import tardio
        with fitz.open(str(p)) as doc:
            return len(doc)
    except Exception:
        return 0


def ocr_um_pdf(p: Path, ocrmypdf_bin: str | None) -> dict:
    """Roda ocrmypdf sobre p, gerando p.with_suffix('.ocr.pdf') ao lado.
    NUNCA modifica o original."""
    t0 = time.time()
    destino = p.with_name(p.stem + ".ocr.pdf")
    base = {"caminho": str(p), "nome": p.name, "pdf_pesquisavel": "", "paginas": 0}

    if ocrmypdf_bin is None:
        return {**base, "status": "SKIP",
                "segundos": 0.0, "detalhe": "ocrmypdf nao instalado (binario ausente)"}
    if destino.exists():
        return {**base, "status": "SKIP_EXISTENTE", "pdf_pesquisavel": str(destino),
                "segundos": 0.0, "detalhe": ".ocr.pdf ja existe — nao sobrescreve"}
    if not p.exists():
        return {**base, "status": "ERRO", "segundos": 0.0, "detalhe": "original nao encontrado"}

    cmd = [
        ocrmypdf_bin,
        "--skip-text",            # nao re-OCRiza paginas que ja tem texto
        "--deskew",
        "--output-type", "pdf",
        "-l", "por",
        str(p), str(destino),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=OCR_TIMEOUT_SEG)
    except subprocess.TimeoutExpired:
        destino.unlink(missing_ok=True)  # remove APENAS o derivado parcial, nunca o original
        return {**base, "status": "ERRO", "segundos": round(time.time() - t0, 1),
                "detalhe": f"timeout > {OCR_TIMEOUT_SEG}s"}
    except OSError as e:
        return {**base, "status": "ERRO", "segundos": round(time.time() - t0, 1),
                "detalhe": f"exec: {str(e)[:120]}"}

    if r.returncode != 0 and not destino.exists():
        # tentativa 2 sem deskew (alguns PDFs quebram no unpaper)
        cmd2 = [c for c in cmd if c != "--deskew"]
        try:
            r = subprocess.run(cmd2, capture_output=True, text=True, timeout=OCR_TIMEOUT_SEG)
        except (subprocess.TimeoutExpired, OSError):
            pass

    if destino.exists() and destino.stat().st_size > 0:
        return {**base, "status": "OK", "pdf_pesquisavel": str(destino),
                "paginas": contar_paginas(destino),
                "segundos": round(time.time() - t0, 1),
                "detalhe": f"rc={r.returncode}"}
    return {**base, "status": "ERRO", "segundos": round(time.time() - t0, 1),
            "detalhe": (r.stderr or r.stdout or "saida nao gerada")[-180:].replace("\n", " ")}


def carregar_alvos(universo_csv: Path, limit: int) -> list[Path]:
    alvos: list[Path] = []
    with open(universo_csv, encoding="utf-8-sig") as f:
        rd = csv.DictReader(f, delimiter=";")
        for row in rd:
            if row.get("tem_texto") != "0":
                continue
            if row.get("erro"):  # erro de leitura no inventario — nao vale OCR cego
                continue
            if row.get("nome", "").lower().endswith(".ocr.pdf"):
                continue
            alvos.append(Path(row["caminho"]))
    if limit > 0:
        alvos = alvos[:limit]
    return alvos


def main() -> int:
    ap = argparse.ArgumentParser(
        description="OCR em lote (ocrmypdf --skip-text --deskew). Gera .ocr.pdf ao lado; nunca toca no original.")
    ap.add_argument("--universo", required=True, help="universo.csv gerado por inventario_pdfs.py")
    ap.add_argument("--out", required=True, help="Pasta de saida (resultado_ocr.csv)")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0, help="Processa so os N primeiros (teste)")
    ap.add_argument("--dry-run", action="store_true", help="So lista o que seria OCRizado")
    args = ap.parse_args()

    universo = Path(args.universo)
    out = Path(args.out)

    if not universo.exists():
        if args.dry_run:
            print(f"[DRY-RUN] universo.csv inexistente neste ambiente: {universo}")
            print("[DRY-RUN] plano: filtrar tem_texto=0, rodar "
                  "`ocrmypdf --skip-text --deskew --output-type pdf -l por IN OUT.ocr.pdf`")
            return 0
        print(f"ERRO: universo.csv nao existe: {universo}", file=sys.stderr)
        return 1

    alvos = carregar_alvos(universo, args.limit)
    ocrmypdf_bin = shutil.which("ocrmypdf")
    print(f"Candidatos a OCR (tem_texto=0): {len(alvos)}")
    print(f"Binario ocrmypdf: {ocrmypdf_bin or 'AUSENTE (tudo vira SKIP)'}")

    if args.dry_run:
        for p in alvos[:10]:
            print(f"  [DRY-RUN] OCRizaria: {p} -> {p.with_name(p.stem + '.ocr.pdf')}")
        if len(alvos) > 10:
            print(f"  ... e mais {len(alvos) - 10}")
        print("[DRY-RUN] nada foi executado.")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    log_path = out / "progresso.log"
    resultado_csv = out / "resultado_ocr.csv"

    def log(m: str):
        linha = f"[{datetime.now().strftime('%H:%M:%S')}] {m}"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        print(linha, flush=True)

    with open(resultado_csv, "w", newline="", encoding="utf-8-sig") as f:
        csv.DictWriter(f, fieldnames=COLS, delimiter=";").writeheader()

    log(f"OCR de {len(alvos)} PDFs com {args.threads} threads (timeout {OCR_TIMEOUT_SEG}s/pdf)")
    cont = {"OK": 0, "ERRO": 0, "SKIP": 0, "SKIP_EXISTENTE": 0}
    t_ini = time.time()
    with ThreadPoolExecutor(max_workers=max(1, args.threads)) as ex:
        futs = {ex.submit(ocr_um_pdf, p, ocrmypdf_bin): p for p in alvos}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                r = f.result()
            except Exception as e:
                r = {"caminho": str(futs[f]), "nome": futs[f].name, "status": "ERRO",
                     "pdf_pesquisavel": "", "paginas": 0, "segundos": 0.0,
                     "detalhe": str(e)[:150]}
            with open(resultado_csv, "a", newline="", encoding="utf-8-sig") as fh:
                csv.DictWriter(fh, fieldnames=COLS, delimiter=";",
                               extrasaction="ignore").writerow(r)
            cont[r["status"]] = cont.get(r["status"], 0) + 1
            if i % 25 == 0:
                el = time.time() - t_ini
                rate = i / el if el > 0 else 0
                eta = (len(alvos) - i) / rate if rate > 0 else 0
                log(f"  {i}/{len(alvos)} ({rate:.2f} pdf/s) ETA {eta / 60:.1f} min {cont}")

    el = time.time() - t_ini
    log(f"OCR concluido em {el / 60:.1f} min: {cont}")

    rel = out / "relatorio.md"
    rel.write_text(
        "# OCR em lote\n\n"
        f"**Data:** {datetime.now().isoformat(timespec='seconds')}\n"
        f"**Duracao:** {el / 60:.1f} min\n"
        f"**Candidatos:** {len(alvos)}\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in cont.items())
        + "\n\n## Observacoes\n"
        "- Originais preservados (NUNCA-1 do CLAUDE.md).\n"
        "- `.ocr.pdf` gerado ao lado de cada original.\n"
        "- SKIP = ocrmypdf ausente; SKIP_EXISTENTE = derivado ja existia.\n",
        encoding="utf-8")
    log(f"Relatorio: {rel}")
    log("TERMINOU.")
    # erro real = nenhum sucesso E havia candidatos E binario presente
    if alvos and ocrmypdf_bin and cont["OK"] == 0 and cont["SKIP_EXISTENTE"] == 0:
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
