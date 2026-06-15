#!/usr/bin/env python3
"""
spcf_captura_view.py — Fallback `_VIEW`: captura a ficha HTML do empenho SPCF como PDF A4 (portado do DETRAN).

Origem: DETRAN_AUDITORIA_COMPLETA/10_SCRIPTS_PYTHON/fase2_captura_view_html_pdf.py
Mudancas no porte:
  - Parametrizado por argparse: --cliente SEDUC --csv-faltantes PATH --out DIR.
  - Login MANUAL em browser HEADED (o original recebia usuario/senha em argv —
    removido por seguranca e padronizacao com spcf_baixar_nes.py).
  - page.pdf() so funciona em headless; em headed usamos CDP Page.printToPDF
    (mesmo motor Chromium, resultado identico).
Mantido (obrigatorio):
  - Sufixo `_VIEW` no nome (sinaliza captura de ficha HTML, nao Crystal Reports).
  - Rate-limit 1.5s entre requisicoes.
  - Validacao de PDF (header %PDF, paginas > 0) + SHA256 no log.

Quando usar: para empenhos cujo campo "Documento Comprovante" esta vazio no SPCF
(spcf_baixar_nes.py falhou com "nenhum botao PDF"). Dados oficiais; apenas a
metadata do PDF e Chromium — documentar ao perito (licao DETRAN §5).

USO (Windows):
  py -3.12 scripts\\acervo\\spcf_captura_view.py --cliente SEDUC --csv-faltantes lacunas_ne.csv ^
      --out <pasta destino> --dry-run
  ... --apply --limit 5
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

RATE_LIMIT_SEG = 1.5  # OBRIGATORIO
TIMEOUT_MS = 20000
LOG_COLS = ["emp_id", "num_ne", "contrato", "status", "nome_gerado_ou_erro",
            "paginas", "bytes", "sha256"]


def ler_env() -> tuple[str, str]:
    base_url = os.environ.get("SPCF_BASE_URL", "").strip()
    login_path = os.environ.get("SPCF_LOGIN_PATH", "/index.php/usuarios/login").strip()
    for cwd in (Path.cwd(), Path(__file__).resolve().parent):
        env_file = cwd / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if "=" not in line or line.startswith("#"):
                    continue
                k, v = line.split("=", 1)
                k = k.strip(); v = v.strip().strip('"').strip("'")
                if k == "SPCF_BASE_URL" and not base_url:
                    base_url = v
                elif k == "SPCF_LOGIN_PATH":
                    login_path = v
            break
    return base_url, login_path


def normalizar_contrato(c: str) -> str:
    if not c:
        return "CT-indefinido"
    m = re.match(r"^\s*(\d+)\s*/\s*(\d{4})\s*$", str(c))
    if m:
        return f"CT-{int(m.group(1)):03d}.{m.group(2)}"
    return f'CT-{re.sub(r"[^0-9A-Za-z.-]", "-", str(c))}'


def normalizar_ne(n: str) -> str:
    return "NE-" + re.sub(r"[^0-9A-Za-z]", "", str(n)) if n else "NE-semnumero"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validar_pdf(p: Path):
    with open(p, "rb") as f:
        if not f.read(5).startswith(b"%PDF"):
            return False, "header nao eh %PDF"
    try:
        try:
            from pypdf import PdfReader
        except ImportError:
            from PyPDF2 import PdfReader
        n = len(PdfReader(p).pages)
        return (n > 0), n
    except Exception as e:
        return False, f"pypdf erro: {e}"


def ler_faltantes(csv_path: Path) -> list[dict]:
    with open(csv_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    out = []
    for r in rows:
        out.append({
            "emp_id": (r.get("emp_id") or r.get("id") or r.get("empenho_id") or "").strip(),
            "num_ne": (r.get("num_ne") or r.get("ne") or r.get("numero_ne") or "").strip(),
            "contrato": (r.get("contrato") or r.get("ct") or "").strip(),
        })
    return [r for r in out if r["emp_id"]]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Captura ficha /empenhos/view/<id> do SPCF como PDF A4 com sufixo _VIEW (fallback).")
    ap.add_argument("--cliente", required=True, help="Devedor (ex: SEDUC)")
    ap.add_argument("--csv-faltantes", required=True, help="CSV ';' com emp_id;num_ne;contrato")
    ap.add_argument("--out", required=True, help="Pasta destino dos PDFs _VIEW")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--apply", action="store_true", help="Executa de verdade (default: dry-run)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    dry = args.dry_run or not args.apply
    csv_path = Path(args.csv_faltantes)
    out = Path(args.out)
    base_url, login_path = ler_env()

    if not csv_path.exists():
        if dry:
            print(f"[DRY-RUN] CSV inexistente neste ambiente: {csv_path}")
            print(f"[DRY-RUN] plano: login manual -> /empenhos/view/<id> -> "
                  f"CDP Page.printToPDF A4 -> {out}\\NE-<n>_CT-<ct>_id<id>_VIEW.pdf "
                  f"(rate {RATE_LIMIT_SEG}s, valida %PDF+paginas+SHA256)")
            return 0
        print(f"ERRO: CSV nao existe: {csv_path}", file=sys.stderr)
        return 1

    faltantes = ler_faltantes(csv_path)
    if args.limit > 0:
        faltantes = faltantes[:args.limit]
    print(f"Cliente: {args.cliente} | capturar _VIEW de: {len(faltantes)} empenhos")

    if dry:
        for r in faltantes[:5]:
            print(f"  [DRY-RUN] id={r['emp_id']} -> "
                  f"{normalizar_ne(r['num_ne'])}_{normalizar_contrato(r['contrato'])}_id{r['emp_id']}_VIEW.pdf")
        print(f"[DRY-RUN] destino: {out} | nada foi capturado. Use --apply.")
        return 0

    if not base_url:
        print("ERRO: SPCF_BASE_URL nao definido (env var ou .env).", file=sys.stderr)
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERRO: playwright nao instalado. Rode:", file=sys.stderr)
        print("  py -3.12 -m pip install playwright pypdf", file=sys.stderr)
        print("  py -3.12 -m playwright install chromium", file=sys.stderr)
        return 2

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    log_path = out / f"__SPCF_CAPTURA_VIEW_{args.cliente}_{ts}.csv"
    log_rows: list[list] = []
    ok_count = fail_count = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, args=["--start-maximized"])
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()

        page.goto(f'{base_url.rstrip("/")}{login_path}', timeout=30000)
        print("\n>>> GABRIEL: faca login no browser aberto agora <<<")
        input("    ao terminar, pressione ENTER aqui para continuar... ")

        cdp = ctx.new_cdp_session(page)  # printToPDF funciona em headed via CDP

        for i, r in enumerate(faltantes, 1):
            eid, ne, ct = r["emp_id"], r["num_ne"], r["contrato"]
            nome_dest = f"{normalizar_ne(ne)}_{normalizar_contrato(ct)}_id{eid}_VIEW.pdf"
            dst = out / nome_dest
            if dst.exists():
                print(f"[{i:3d}/{len(faltantes)}] id={eid} SKIP (ja existe — nunca sobrescreve)")
                log_rows.append([eid, ne, ct, "SKIP_EXISTENTE", nome_dest, 0, 0, ""])
                continue
            try:
                page.goto(f'{base_url.rstrip("/")}/index.php/empenhos/view/{eid}',
                          timeout=TIMEOUT_MS)
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
                if "login" in page.url.lower():
                    print(f"[{i:3d}] id={eid} sessao expirou — refaca o login no browser")
                    input("    apos relogar, pressione ENTER para repetir este empenho... ")
                    page.goto(f'{base_url.rstrip("/")}/index.php/empenhos/view/{eid}',
                              timeout=TIMEOUT_MS)

                res = cdp.send("Page.printToPDF", {
                    "paperWidth": 8.27, "paperHeight": 11.69,  # A4 em polegadas
                    "marginTop": 0.47, "marginBottom": 0.47,
                    "marginLeft": 0.39, "marginRight": 0.39,
                    "printBackground": True,
                })
                dst.write_bytes(base64.b64decode(res["data"]))

                ok, paginas = validar_pdf(dst)
                if ok:
                    sha = sha256_file(dst)
                    sz = dst.stat().st_size
                    ok_count += 1
                    print(f"[{i:3d}/{len(faltantes)}] id={eid} OK {paginas}pg {sz / 1024:.0f}KB")
                    log_rows.append([eid, ne, ct, "OK", nome_dest, paginas, sz, sha])
                else:
                    fail_count += 1
                    print(f"[{i:3d}/{len(faltantes)}] id={eid} FALHA_VALIDACAO: {paginas}")
                    log_rows.append([eid, ne, ct, "FALHA_VALIDACAO", nome_dest, 0,
                                     dst.stat().st_size if dst.exists() else 0, ""])
            except Exception as e:
                fail_count += 1
                print(f"[{i:3d}/{len(faltantes)}] id={eid} ERRO: {str(e)[:80]}")
                log_rows.append([eid, ne, ct, "ERRO", str(e)[:100], 0, 0, ""])

            time.sleep(RATE_LIMIT_SEG)
        browser.close()

    with open(log_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(LOG_COLS)
        for r in log_rows:
            w.writerow(r)

    print(f"\nRESUMO: OK={ok_count} / FALHA={fail_count} | log: {log_path}")
    print("Proximo passo: inventario + OCR sobre a pasta de destino.")
    if ok_count == 0 and faltantes:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
