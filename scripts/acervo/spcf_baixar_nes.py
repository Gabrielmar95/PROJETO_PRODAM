#!/usr/bin/env python3
"""
spcf_baixar_nes.py — Baixa PDFs oficiais de NEs faltantes do SPCF via Playwright (portado do DETRAN).

Origem: DETRAN_AUDITORIA_COMPLETA/10_SCRIPTS_PYTHON/fase2_scraping_spcf_playwright.py
Mudancas no porte:
  - Parametrizado por argparse: --cliente SEDUC --csv-faltantes PATH --out DIR.
  - Removidos paths DETRAN hardcoded e o update do consolidado DETRAN-especifico
    (a saida vai toda para --out + log CSV).
Mantido (obrigatorio):
  - Login MANUAL do usuario em browser HEADED (visivel) — sem senha em CLI.
  - Rate-limit 1.5s entre requisicoes (regra SPCF do projeto).
  - Validacao de PDF: header %PDF, paginas > 0, tamanho minimo, SHA256.
  - Checkpoint a cada 10 NEs com confirmacao do usuario.

CSV de faltantes esperado (';', utf-8-sig) com colunas: emp_id;num_ne;contrato
(colunas alternativas aceitas: id, empenho_id / ne, numero_ne / ct).

USO (Windows):
  py -3.12 scripts\\acervo\\spcf_baixar_nes.py --cliente SEDUC --csv-faltantes lacunas_ne.csv ^
      --out C:\\Users\\gabri\\Desktop\\SEDUC_AUDITORIA_COMPLETA\\02_NOTAS_EMPENHO\\PDF --dry-run
  ... --apply --limit 5    (teste com 5)
  ... --apply              (lote completo)

CONFIG: SPCF_BASE_URL em env var ou .env (ex: SPCF_BASE_URL=https://spcf.prodam.am.gov.br)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

RATE_LIMIT_SEG = 1.5     # OBRIGATORIO (regra SPCF do projeto)
TIMEOUT_MS = 20000
TAMANHO_MINIMO = 30_000  # 30KB — alguns empenhos antigos sao pequenos
BATCH_CONFIRM = 10
LOG_COLS = ["emp_id", "num_ne", "contrato", "status", "erro_ou_detalhe",
            "nome_novo", "sha256", "bytes"]


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


def normalizar_contrato(c: str) -> str:
    if not c:
        return "CT-indefinido"
    m = re.match(r"^\s*(\d+)\s*/\s*(\d{4})\s*$", str(c))
    if m:
        n, a = m.groups()
        return f"CT-{int(n):03d}.{a}"
    safe = re.sub(r"[^0-9A-Za-z.-]", "-", str(c))
    return f"CT-{safe}" if safe else "CT-indefinido"


def normalizar_ne(n: str) -> str:
    if not n:
        return "NE-semnumero"
    return "NE-" + re.sub(r"[^0-9A-Za-z]", "", str(n))


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validar_pdf(p: Path):
    """(ok, paginas_ou_motivo) — header %PDF + paginas > 0 + tamanho minimo."""
    if p.stat().st_size < TAMANHO_MINIMO:
        return False, f"tamanho {p.stat().st_size} < minimo {TAMANHO_MINIMO}"
    with open(p, "rb") as f:
        header = f.read(5)
    if not header.startswith(b"%PDF"):
        return False, f"header {header!r} nao eh %PDF"
    try:
        try:
            from pypdf import PdfReader
        except ImportError:
            from PyPDF2 import PdfReader
        r = PdfReader(p)
        n = len(r.pages)
        if n == 0:
            return False, "0 paginas"
        return True, n
    except Exception as e:
        return False, f"pypdf erro: {e}"


def confirmar(msg: str) -> bool:
    resp = input(f"{msg} [s/n]: ").strip().lower()
    return resp in ("s", "sim", "y", "yes", "")


def tentar_baixar_pdf(page, base_url: str, emp_id: str, download_dir: Path):
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    url = f'{base_url.rstrip("/")}/index.php/empenhos/view/{emp_id}'
    try:
        page.goto(url, timeout=TIMEOUT_MS, wait_until="domcontentloaded")
    except PlaywrightTimeout:
        return None, f"timeout ao abrir {url}"

    if "login" in page.url.lower() or "entrar" in page.url.lower():
        return None, f"redirecionado para login: {page.url} (sessao expirou)"

    selectors = [
        'a[href*="pdf" i]', 'a[href*="print" i]', 'a[href*="download" i]',
        'a:has-text("PDF")', 'a:has-text("Imprimir")', 'a:has-text("Gerar")',
        'button:has-text("PDF")', 'button:has-text("Imprimir")',
        '[title*="imprimir" i]', '[title*="pdf" i]',
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() == 0:
                continue
            href = loc.get_attribute("href") or ""
            if href and href.lower().endswith(".pdf"):
                full = href if href.startswith("http") else \
                    f'{base_url.rstrip("/")}{href if href.startswith("/") else "/" + href}'
                resp = page.context.request.get(full, timeout=TIMEOUT_MS)
                if resp.ok and resp.body().startswith(b"%PDF"):
                    dst = download_dir / f"empenho_{emp_id}.pdf"
                    dst.write_bytes(resp.body())
                    return dst, None
            with page.expect_download(timeout=TIMEOUT_MS) as dlinfo:
                loc.click()
            dl = dlinfo.value
            dst = download_dir / f"empenho_{emp_id}.pdf"
            dl.save_as(str(dst))
            return dst, None
        except Exception:
            continue
    return None, "nenhum botao PDF/imprimir encontrado (revisar seletores)"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Baixa PDFs de NEs faltantes do SPCF (login manual headed, rate 1.5s, validacao %PDF+SHA256).")
    ap.add_argument("--cliente", required=True, help="Devedor (ex: SEDUC)")
    ap.add_argument("--csv-faltantes", required=True, help="CSV ';' com emp_id;num_ne;contrato")
    ap.add_argument("--out", required=True, help="Pasta destino dos PDFs baixados")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--apply", action="store_true", help="Executa de verdade (default: dry-run)")
    ap.add_argument("--dry-run", action="store_true", help="Forca dry-run (explicito)")
    args = ap.parse_args()

    dry = args.dry_run or not args.apply
    csv_path = Path(args.csv_faltantes)
    out = Path(args.out)
    base_url, login_path = ler_env()

    if not csv_path.exists():
        if dry:
            print(f"[DRY-RUN] CSV de faltantes inexistente neste ambiente: {csv_path}")
            print(f"[DRY-RUN] plano: login manual em {base_url or '<SPCF_BASE_URL>'}"
                  f"{login_path} -> /empenhos/view/<id> -> download PDF "
                  f"-> validar %PDF/paginas/SHA256 -> {out}\\NE-<n>_CT-<ct>_id<id>.pdf "
                  f"(rate {RATE_LIMIT_SEG}s)")
            return 0
        print(f"ERRO: CSV nao existe: {csv_path}", file=sys.stderr)
        return 1

    faltantes = ler_faltantes(csv_path)
    if args.limit > 0:
        faltantes = faltantes[:args.limit]
    print(f"Cliente: {args.cliente} | a baixar: {len(faltantes)} NEs | "
          f"rate {RATE_LIMIT_SEG}s | checkpoint a cada {BATCH_CONFIRM}")

    if dry:
        print("[DRY-RUN] primeiros 3 alvos:")
        for r in faltantes[:3]:
            print(f"  id={r['emp_id']} NE={r['num_ne']} CT={r['contrato']} -> "
                  f"{normalizar_ne(r['num_ne'])}_{normalizar_contrato(r['contrato'])}_id{r['emp_id']}.pdf")
        print(f"[DRY-RUN] destino: {out} | nada foi baixado. Use --apply para executar.")
        return 0

    if not base_url:
        print("ERRO: SPCF_BASE_URL nao definido (env var ou .env).", file=sys.stderr)
        print("Exemplo: $env:SPCF_BASE_URL='https://spcf.prodam.am.gov.br'", file=sys.stderr)
        return 1

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        print("ERRO: playwright nao instalado. Rode:", file=sys.stderr)
        print("  py -3.12 -m pip install playwright pypdf", file=sys.stderr)
        print("  py -3.12 -m playwright install chromium", file=sys.stderr)
        return 2

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    tmp_dir = out / f"_tmp_downloads_{ts}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    log_path = out / f"__SPCF_BAIXAR_NES_{args.cliente}_{ts}.csv"

    sucesso = 0
    falha: list[tuple[str, str]] = []
    log_rows: list[list] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(accept_downloads=True, no_viewport=True)
        page = context.new_page()

        print("\n" + "=" * 70)
        print(f"Abrindo {base_url}{login_path}")
        print("=" * 70)
        try:
            page.goto(f'{base_url.rstrip("/")}{login_path}', timeout=TIMEOUT_MS)
        except PlaywrightTimeout:
            print("AVISO: timeout no login page — tentando URL base")
            page.goto(base_url, timeout=TIMEOUT_MS)

        print("\n>>> GABRIEL: faca login no browser aberto agora <<<")
        input("    ao terminar, pressione ENTER aqui para continuar... ")
        if not confirmar("voce esta logado e vendo o dashboard SPCF?"):
            print("abortando. feche o browser e tente de novo.")
            browser.close()
            return 1

        print(f"\nComecando ciclo — {len(faltantes)} empenhos\n")
        for i, row in enumerate(faltantes, 1):
            eid, num_ne, ct = row["emp_id"], row["num_ne"], row["contrato"]
            print(f"[{i:3d}/{len(faltantes)}] id={eid} NE={num_ne} CT={ct} ...",
                  end=" ", flush=True)
            dst_tmp, erro = tentar_baixar_pdf(page, base_url, eid, tmp_dir)
            if erro:
                print(f"FALHA: {erro}")
                falha.append((eid, erro))
                log_rows.append([eid, num_ne, ct, "FALHA", erro, "", "", 0])
                time.sleep(RATE_LIMIT_SEG)
                continue

            ok, info = validar_pdf(dst_tmp)
            if not ok:
                print(f"FALHA validacao: {info}")
                dst_tmp.unlink(missing_ok=True)  # remove APENAS o download temporario invalido
                falha.append((eid, f"validacao: {info}"))
                log_rows.append([eid, num_ne, ct, "FALHA_VALIDACAO", str(info), "", "", 0])
                time.sleep(RATE_LIMIT_SEG)
                continue

            nome_dest = f"{normalizar_ne(num_ne)}_{normalizar_contrato(ct)}_id{eid}.pdf"
            dst = out / nome_dest
            if dst.exists():
                print("SKIP: destino ja existe (nunca sobrescreve PDF)")
                log_rows.append([eid, num_ne, ct, "SKIP_EXISTENTE", "", nome_dest, "", 0])
                time.sleep(RATE_LIMIT_SEG)
                continue
            dst_tmp.replace(dst)  # move o temporario para o nome formal
            sha = sha256_file(dst)
            sz = dst.stat().st_size
            print(f"OK {info}pg {sz / 1024:.0f}KB")
            sucesso += 1
            log_rows.append([eid, num_ne, ct, "OK", "", nome_dest, sha, sz])
            time.sleep(RATE_LIMIT_SEG)

            if i % BATCH_CONFIRM == 0 and i < len(faltantes):
                print(f"--- checkpoint: {sucesso} OK, {len(falha)} falhas ---")
                if not confirmar("continuar com o proximo batch?"):
                    print("pausando por escolha do usuario.")
                    break
        browser.close()

    with open(log_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(LOG_COLS)
        for r in log_rows:
            w.writerow(r)

    print(f"\nRESUMO: sucesso={sucesso} / falha={len(falha)} / log={log_path}")
    print("PROXIMO PASSO: rodar inventario+OCR na pasta de destino para indexar os novos PDFs.")
    if sucesso == 0 and faltantes:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
