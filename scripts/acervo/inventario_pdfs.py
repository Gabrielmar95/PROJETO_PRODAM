#!/usr/bin/env python3
"""
inventario_pdfs.py — Inventario generico de PDFs de um acervo (portado do DETRAN).

Origem: DETRAN_AUDITORIA_COMPLETA/10_SCRIPTS_PYTHON/inventario_classificacao_global.py
Mudancas no porte:
  - Paths hardcoded (C:\\Users\\gabri\\...) substituidos por argparse (--raiz/--out).
  - Dependencia do classificador da skill `ocr-pdfs-prodam` REMOVIDA:
    este script SO inventaria (a classificacao e feita por classificar_universo.py).
  - MD5 completo por arquivo (deduplicacao e cadeia probatoria).

O inventario NUNCA modifica nenhum PDF — somente leitura + escrita de CSV/MD novos.

Saidas em --out:
  universo.csv   (1 linha por PDF: caminho, pasta_raiz, nome, size_bytes, md5,
                  paginas, tem_texto, chars_p1, suspeito, erro)
  relatorio.md   (resumo executivo)
  progresso.log

Uso (Windows):
  py -3.12 scripts\\acervo\\inventario_pdfs.py --raiz C:\\Users\\gabri\\Desktop\\DPCON\\SEDUC ^
      --out C:\\Users\\gabri\\Desktop\\SEDUC_AUDITORIA_COMPLETA\\20_OCR_OUTPUT\\__INV_DPCON ^
      --excluir _LIXEIRA --excluir PDF_LEGADO --threads 8
  py -3.12 scripts\\acervo\\inventario_pdfs.py --raiz ... --out ... --dry-run
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Exclusoes sempre ativas (vedacoes do projeto — CLAUDE.md NUNCA-1/NUNCA-5)
EXCLUIR_SEMPRE = [
    "_LIXO_NAO_USAR",
    "_LIXEIRA",
    "_BACKUPS",
    "_BACKUPS_EMERGENCIA",
    ".git",
]

RE_SUSPEITO = re.compile(
    r"^(scan_\d+|img_\d+|document(\s*\(\d+\))?|documento\s*\(\d+\)|untitled"
    r"|\d{6,}|[a-f0-9]{16,})\.pdf$",
    re.IGNORECASE,
)

COLS = ["caminho", "pasta_raiz", "nome", "size_bytes", "md5",
        "paginas", "tem_texto", "chars_p1", "suspeito", "erro"]


def nome_suspeito(nome: str) -> bool:
    if RE_SUSPEITO.match(nome):
        return True
    stem = nome.rsplit(".", 1)[0]
    if not stem:
        return False
    digs = sum(c.isdigit() for c in stem)
    return digs / len(stem) >= 0.7


def md5_file(p: Path) -> str:
    h = hashlib.md5()
    try:
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return ""


def scan_texto_pymupdf(p: Path) -> tuple[bool, int, int, str]:
    """(tem_texto, num_paginas, chars_primeira_pagina, erro)."""
    try:
        import fitz  # pymupdf — import tardio (so necessario na execucao real)
    except Exception:
        return False, 0, 0, "pymupdf nao instalado (py -3.12 -m pip install pymupdf)"
    try:
        with fitz.open(str(p)) as doc:
            n = len(doc)
            if n == 0:
                return False, 0, 0, "0 paginas"
            pages_com_texto = 0
            chars_p1 = 0
            for i, pg in enumerate(doc):
                txt = pg.get_text() or ""
                c = len(txt.strip())
                if i == 0:
                    chars_p1 = c
                if c >= 30:
                    pages_com_texto += 1
            tem = pages_com_texto >= max(1, int(n * 0.3))
            return tem, n, chars_p1, ""
    except Exception as e:
        return False, 0, 0, f"pymupdf: {str(e)[:120]}"


def processar(p: Path, raiz: Path) -> dict:
    try:
        sz = p.stat().st_size
    except OSError:
        sz = 0
    tem, n, c1, erro = scan_texto_pymupdf(p)
    try:
        rel = p.relative_to(raiz)
        pasta = rel.parts[0] if len(rel.parts) > 1 else ""
    except ValueError:
        pasta = ""
    return {
        "caminho": str(p),
        "pasta_raiz": pasta,
        "nome": p.name,
        "size_bytes": sz,
        "md5": md5_file(p),
        "paginas": n,
        "tem_texto": int(tem),
        "chars_p1": c1,
        "suspeito": int(nome_suspeito(p.name)),
        "erro": erro,
    }


def enumerar(raiz: Path, excluir: list[str]) -> list[Path]:
    excl = [e.lower() for e in (EXCLUIR_SEMPRE + excluir)]

    def eh_excluido(p: Path) -> bool:
        s = str(p).lower()
        return any(e in s for e in excl)

    vistos: set[Path] = set()
    alvos: list[Path] = []
    for pattern in ("*.pdf", "*.PDF"):
        for p in raiz.rglob(pattern):
            if p in vistos or eh_excluido(p):
                continue
            # nunca inventariar os derivados .ocr.pdf como originais distintos
            vistos.add(p)
            alvos.append(p)
    return alvos


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Inventario de PDFs (pymupdf): tem_texto, paginas, MD5, tamanho. Somente leitura.")
    ap.add_argument("--raiz", required=True, help="Pasta raiz do acervo a inventariar")
    ap.add_argument("--excluir", action="append", default=[],
                    help="Subpasta/fragmento de path a excluir (repetivel)")
    ap.add_argument("--out", required=True, help="Pasta de saida (universo.csv etc.)")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true",
                    help="So enumera e mostra o plano; nao escreve nada")
    args = ap.parse_args()

    raiz = Path(args.raiz)
    out = Path(args.out)

    if not raiz.exists():
        if args.dry_run:
            print(f"[DRY-RUN] raiz inexistente neste ambiente: {raiz}")
            print(f"[DRY-RUN] plano: rglob('*.pdf') excluindo {EXCLUIR_SEMPRE + args.excluir}")
            print(f"[DRY-RUN] saida seria: {out / 'universo.csv'} (CSV ';' utf-8-sig)")
            return 0
        print(f"ERRO: raiz nao existe: {raiz}", file=sys.stderr)
        return 1

    alvos = enumerar(raiz, args.excluir)
    print(f"PDFs enumerados (apos exclusoes): {len(alvos)}")

    if args.dry_run:
        for p in alvos[:10]:
            print(f"  [DRY-RUN] inventariaria: {p}")
        if len(alvos) > 10:
            print(f"  ... e mais {len(alvos) - 10}")
        print(f"[DRY-RUN] nada foi escrito. Saida seria: {out / 'universo.csv'}")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    log_path = out / "progresso.log"

    def log(msg: str):
        linha = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        print(linha, flush=True)

    log(f"Raiz: {raiz} | PDFs: {len(alvos)} | threads: {args.threads}")
    rows: list[dict] = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, args.threads)) as ex:
        futs = {ex.submit(processar, p, raiz): p for p in alvos}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                rows.append(f.result())
            except Exception as e:
                rows.append({"caminho": str(futs[f]), "pasta_raiz": "", "nome": futs[f].name,
                             "size_bytes": 0, "md5": "", "paginas": 0, "tem_texto": 0,
                             "chars_p1": 0, "suspeito": 0, "erro": str(e)[:150]})
            if i % 200 == 0:
                log(f"  scan {i}/{len(alvos)} ({i / (time.time() - t0):.1f} pdf/s)")
    log(f"Scan concluido em {time.time() - t0:.1f}s")

    universo_csv = out / "universo.csv"
    with open(universo_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda r: r["caminho"]):
            w.writerow(r)
    log(f"Gravado: {universo_csv}")

    sem_texto = sum(1 for r in rows if r["tem_texto"] == 0 and not r["erro"])
    com_erro = sum(1 for r in rows if r["erro"])
    md5s = Counter(r["md5"] for r in rows if r["md5"])
    duplicados = sum(n - 1 for n in md5s.values() if n > 1)
    pastas = Counter(r["pasta_raiz"] for r in rows)
    total_mb = sum(r["size_bytes"] for r in rows) / (1024 * 1024)

    rel = out / "relatorio.md"
    linhas = [
        "# Inventario de PDFs",
        "",
        f"**Data:** {datetime.now().isoformat(timespec='seconds')}",
        f"**Raiz:** `{raiz}`",
        "",
        f"- PDFs inventariados: **{len(rows)}** ({total_mb:.0f} MB)",
        f"- Com texto embutido: **{sum(1 for r in rows if r['tem_texto'] == 1)}**",
        f"- Sem texto (candidatos a OCR): **{sem_texto}**",
        f"- Com erro de leitura: **{com_erro}**",
        f"- Duplicatas por MD5: **{duplicados}**",
        f"- Nome suspeito: **{sum(1 for r in rows if r['suspeito'] == 1)}**",
        "",
        "## Distribuicao por pasta (top 20)",
        "| Pasta | PDFs |",
        "|---|---:|",
    ]
    for pasta, n in pastas.most_common(20):
        linhas.append(f"| {pasta or '(raiz)'} | {n} |")
    linhas += ["", "## Proximo passo",
               "- `ocr_lote.py --universo universo.csv` nos PDFs com `tem_texto=0`.", ""]
    rel.write_text("\n".join(linhas), encoding="utf-8")
    log(f"Gravado: {rel}")
    log("TERMINOU.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
