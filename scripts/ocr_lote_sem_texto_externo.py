"""
OCR em lote dos PDFs identificados como 'sem texto' pelo inventario_detran_externo.py.

Le universo.csv (Fase 1), filtra PDFs com tem_texto=0, e roda ocr_pdf_cascata()
em cada um.

Gera .ocr.pdf ao lado do original (ocrmypdf nao toca no original — preserva
prova documental). Registra resultado num CSV.

Paraleliza com ThreadPoolExecutor(2 — OCR e CPU-intensivo, mais workers competem
por memoria e diminuem throughput). Checkpoint a cada 25 PDFs.

Baseado em: DETRAN_AUDITORIA_COMPLETA/10_SCRIPTS_PYTHON/ocr_lote_sem_texto.py
"""
from __future__ import annotations

import csv
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

SKILL_SCRIPTS = Path(r"C:\Users\gabri\.claude\skills\ocr-pdfs-prodam\scripts")
sys.path.insert(0, str(SKILL_SCRIPTS))
try:
    from cascata_ocr import ocr_pdf_cascata  # type: ignore
except Exception as e:
    print(f"[ERRO] Nao importou cascata_ocr: {e}", file=sys.stderr)
    sys.exit(1)

RAIZ_PROJETO = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")


def encontrar_universo_csv() -> Path:
    """Acha o universo.csv mais recente gerado por inventario_detran_externo.py."""
    candidatos = sorted(
        RAIZ_PROJETO.glob("_OUT_inventario_detran_externo_*/universo.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidatos:
        print("[ERRO] Nenhum universo.csv encontrado. Rode inventario_detran_externo.py primeiro.",
              file=sys.stderr)
        sys.exit(1)
    return candidatos[0]


def ler_pdfs_sem_texto(universo_csv: Path) -> list[Path]:
    """Retorna lista de PDFs com tem_texto=0 do universo.csv."""
    pdfs: list[Path] = []
    with open(universo_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if row.get("tem_texto") == "0":
                p = Path(row["caminho"])
                if p.exists():
                    pdfs.append(p)
    return pdfs


def processar(p: Path) -> dict:
    t0 = time.time()
    try:
        r = ocr_pdf_cascata(p, usar_paddle=False)
        pesq = r.get("pdf_pesquisavel")
        return {
            "caminho": str(p),
            "nome": p.name,
            "estagio": r.get("estagio", "?"),
            "score": r.get("score", 0.0),
            "paginas": r.get("total_paginas", 0),
            "procedencia": r.get("procedencia", ""),
            "pdf_pesquisavel": str(pesq) if pesq else "",
            "segundos": round(time.time() - t0, 1),
            "status": "OK",
        }
    except Exception as e:
        return {
            "caminho": str(p), "nome": p.name, "estagio": "ERRO",
            "score": 0.0, "paginas": 0, "procedencia": "",
            "pdf_pesquisavel": "", "segundos": round(time.time() - t0, 1),
            "status": f"ERRO: {str(e)[:200]}",
        }


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    saida = RAIZ_PROJETO / f"_OUT_ocr_lote_externo_{ts}"
    saida.mkdir(parents=True, exist_ok=True)
    log_path = saida / "progresso.log"
    resultado_csv = saida / "resultado_ocr.csv"

    def log(m):
        linha = f"[{datetime.now().strftime('%H:%M:%S')}] {m}"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        print(linha, flush=True)

    log(f"Saida: {saida}")

    universo_csv = encontrar_universo_csv()
    log(f"Universo: {universo_csv}")

    alvos = ler_pdfs_sem_texto(universo_csv)
    log(f"PDFs sem texto a processar: {len(alvos)}")

    if not alvos:
        log("Nenhum PDF sem texto. Saindo.")
        return

    t0 = time.time()
    resultados: list[dict] = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(processar, p): p for p in alvos}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                resultados.append(f.result())
            except Exception as e:
                resultados.append({
                    "caminho": str(futs[f]), "nome": futs[f].name,
                    "estagio": "ERRO", "score": 0.0, "paginas": 0,
                    "procedencia": "", "pdf_pesquisavel": "",
                    "segundos": 0.0, "status": f"ERRO: {e}",
                })
            # Checkpoint a cada 25
            if i % 25 == 0:
                _gravar_csv_parcial(resultado_csv, resultados)
                tempo = time.time() - t0
                vel = i / tempo if tempo > 0 else 0
                eta_min = (len(alvos) - i) / vel / 60 if vel > 0 else 0
                log(f"  checkpoint {i}/{len(alvos)} ({vel:.2f} pdf/s, ETA {eta_min:.0f} min)")

    _gravar_csv_parcial(resultado_csv, resultados)

    # Resumo final
    n_ok = sum(1 for r in resultados if r.get("status") == "OK")
    n_erro = sum(1 for r in resultados if r.get("status", "").startswith("ERRO"))
    por_estagio = {}
    for r in resultados:
        e = r.get("estagio", "?")
        por_estagio[e] = por_estagio.get(e, 0) + 1

    log(f"\nTERMINOU em {(time.time()-t0)/60:.1f} min")
    log(f"  OK: {n_ok} | Erros: {n_erro}")
    log(f"  Por estagio: {por_estagio}")
    log(f"  CSV: {resultado_csv}")


def _gravar_csv_parcial(path: Path, resultados: list[dict]):
    cols = ["caminho", "nome", "estagio", "score", "paginas", "procedencia",
            "pdf_pesquisavel", "segundos", "status"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in resultados:
            w.writerow(r)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
