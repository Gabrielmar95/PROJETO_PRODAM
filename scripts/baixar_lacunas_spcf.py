"""
RASCUNHO — download em lote dos PDFs faltantes da Notificacao DETRAN 001/2026
via Playwright sobre o SPCF/PRODAM (VPN obrigatoria).

Le:     DETRAN_AUDITORIA_COMPLETA/_NOTIFICACAO_ASSINADA/LACUNAS_PARA_DOWNLOAD.csv
Salva:  PROJETO_PRODAM/downloads_spcf/
          ├── contratos/    (PDFs dos 5 contratos sem PDF)
          ├── faturas/      (PDFs das 85 NFs sem PDF)
          └── _log.jsonl    (registro por item: ok / erro / skipped)

Pre-requisitos:
    pip install playwright python-dotenv
    playwright install chromium
    VPN PRODAM ativa (10.20.0.x precisa resolver)
    .env com SPCF_USER, SPCF_PASS, SPCF_URL

Modo de uso:
    python baixar_lacunas_spcf.py                  # baixa tudo faltante
    python baixar_lacunas_spcf.py --tipo CONTRATO  # so contratos
    python baixar_lacunas_spcf.py --tipo FATURA    # so faturas
    python baixar_lacunas_spcf.py --dry-run        # simula, nao baixa
    python baixar_lacunas_spcf.py --limite 5       # para debug: so 5 items

AVISO — RASCUNHO:
    Seletores DOM do formulario de login e da listagem de faturas sao heuristicos
    (foram inferidos do fluxo documentado no CLAUDE.md §3 Etapa 5, nao testados
    em sessao real). Ajustar apos primeiro run com VPN ativa.
    Ordem de login: login -> GET /spcf -> so depois URLs internas (regra do projeto).
"""
from __future__ import annotations
import os, csv, json, time, re, argparse, sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

# ================= PATHS =================
BASE_PROJ = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")
BASE_DETRAN = Path(r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA")
CSV_IN = BASE_DETRAN / "_NOTIFICACAO_ASSINADA" / "LACUNAS_PARA_DOWNLOAD.csv"
OUT_DIR = BASE_PROJ / "downloads_spcf"
DIR_CONTRATOS = OUT_DIR / "contratos"
DIR_FATURAS   = OUT_DIR / "faturas"
LOG_PATH = OUT_DIR / "_log.jsonl"
STORAGE_STATE = OUT_DIR / ".playwright_state.json"

for d in (OUT_DIR, DIR_CONTRATOS, DIR_FATURAS):
    d.mkdir(parents=True, exist_ok=True)

# ================= CONFIG =================
load_dotenv(BASE_PROJ / ".env")
SPCF_USER = os.environ.get("SPCF_USER")
SPCF_PASS = os.environ.get("SPCF_PASS")
SPCF_URL  = (os.environ.get("SPCF_URL") or "").rstrip("/")
if not (SPCF_USER and SPCF_PASS and SPCF_URL):
    sys.exit("ERRO: .env incompleto — precisa SPCF_USER, SPCF_PASS, SPCF_URL")

RATE_LIMIT_S = 1.5          # regra CLAUDE.md: 1.5s entre requisicoes
TIMEOUT_MS   = 30_000       # 30s padrao por operacao
HEADLESS     = True         # mude para False para depurar visualmente

# ================= LOG =================
def log(evento: str, **dados):
    rec = {"ts": datetime.now().isoformat(), "evento": evento, **dados}
    line = json.dumps(rec, ensure_ascii=False, default=str)
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ================= SPCF CLIENT =================
class SPCFClient:
    """Wrapper Playwright com login + download de faturas e contratos.
    Regra do projeto (memoria): apos login, nunca goto direto para endpoint interno
    sem antes passar por /index.php/spcf para consolidar a sessao."""

    def __init__(self, ctx: BrowserContext, base_url: str):
        self.ctx = ctx
        self.base = base_url
        self.logado = False

    def login(self, usuario: str, senha: str) -> None:
        page = self.ctx.new_page()
        try:
            log("login.start", url=f"{self.base}/index.php/usuarios/login")
            page.goto(f"{self.base}/index.php/usuarios/login", wait_until="networkidle", timeout=TIMEOUT_MS)
            # seletores heuristicos (CakePHP gera name="data[Usuario][login]")
            page.fill('input[name="data[Usuario][login]"]', usuario)
            page.fill('input[name="data[Usuario][senha]"]', senha)
            # botao pode ser <button type="submit"> ou <input type="submit">
            for sel in ('button[type="submit"]', 'input[type="submit"]', 'form button:has-text("Entrar")'):
                try:
                    page.click(sel, timeout=3000)
                    break
                except PlaywrightTimeoutError:
                    continue
            page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
            # consolidar sessao SPCF (regra do projeto)
            page.goto(f"{self.base}/index.php/spcf", wait_until="networkidle", timeout=TIMEOUT_MS)
            # heuristica: se voltou para login, deu errado
            if "/usuarios/login" in page.url:
                raise RuntimeError("login falhou — voltou para tela de login")
            self.logado = True
            log("login.ok", url=page.url)
            # salvar storage state para reuso entre runs
            self.ctx.storage_state(path=str(STORAGE_STATE))
        finally:
            page.close()

    def listar_faturas_contrato(self, contrato_id: int) -> list[dict]:
        """Usa POST /contratos/relatorioFaturas e extrai (nf, fatura_id).
        Chave para mapear NF -> fatura_id antes de baixar cada uma."""
        url = f"{self.base}/index.php/contratos/relatorioFaturas"
        resp = self.ctx.request.post(
            url,
            form={"data[ContratoRelatorio][contrato_id]": str(contrato_id)},
            headers={"X-Requested-With": "XMLHttpRequest"},
            timeout=TIMEOUT_MS,
        )
        if resp.status != 200:
            raise RuntimeError(f"relatorioFaturas status {resp.status}")
        html = resp.text()
        # Extracao heuristica: linhas com NF e link contendo /contratos/fatura/{id}
        ids = re.findall(r"/contratos/fatura/(\d+)", html)
        # NF costuma ser 5-6 digitos em <td>
        nfs = re.findall(r"<td[^>]*>\s*(\d{4,7})\s*</td>", html)
        pares = list(dict.fromkeys(zip(nfs, ids)))  # dedup preservando ordem
        log("listar_faturas.ok", contrato_id=contrato_id, qtd=len(pares))
        return [{"nf": nf, "fatura_id": fid} for nf, fid in pares]

    def baixar_fatura_pdf(self, fatura_id: int, dst: Path) -> bool:
        if dst.exists() and dst.stat().st_size > 5_000:
            log("fatura.skip_existe", fatura_id=fatura_id, dst=str(dst))
            return True
        page = self.ctx.new_page()
        try:
            url = f"{self.base}/index.php/contratos/fatura/{fatura_id}"
            page.goto(url, wait_until="networkidle", timeout=TIMEOUT_MS)
            # sanity: se veio pra login, sessao perdida
            if "/usuarios/login" in page.url:
                raise RuntimeError("sessao perdida — redirecionou para login")
            page.emulate_media(media="print")
            page.pdf(path=str(dst), format="A4", print_background=True, margin={"top":"10mm","bottom":"10mm","left":"10mm","right":"10mm"})
            log("fatura.ok", fatura_id=fatura_id, bytes=dst.stat().st_size)
            return True
        except Exception as e:
            log("fatura.erro", fatura_id=fatura_id, erro=str(e))
            return False
        finally:
            page.close()

    def baixar_contrato_pdf(self, contrato_id: int, dst: Path, proposta: bool = False) -> bool:
        if dst.exists() and dst.stat().st_size > 5_000:
            log("contrato.skip_existe", contrato_id=contrato_id, dst=str(dst))
            return True
        page = self.ctx.new_page()
        try:
            if proposta:
                url = f"{self.base}/index.php/propostas/imprimir/{contrato_id}"
            else:
                url = f"{self.base}/index.php/contratos/imprimir/{contrato_id}"
            page.goto(url, wait_until="networkidle", timeout=TIMEOUT_MS)
            if "/usuarios/login" in page.url:
                raise RuntimeError("sessao perdida — redirecionou para login")
            page.emulate_media(media="print")
            page.pdf(path=str(dst), format="A4", print_background=True, margin={"top":"10mm","bottom":"10mm","left":"10mm","right":"10mm"})
            log("contrato.ok", contrato_id=contrato_id, bytes=dst.stat().st_size)
            return True
        except Exception as e:
            log("contrato.erro", contrato_id=contrato_id, erro=str(e))
            return False
        finally:
            page.close()


# ================= MAIN =================
def carregar_lacunas(csv_path: Path) -> list[dict]:
    itens = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if row.get("status") != "DOWNLOAD_SPCF":
                continue
            itens.append(row)
    return itens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipo", choices=["CONTRATO","FATURA","NE","TODOS"], default="TODOS")
    ap.add_argument("--limite", type=int, default=0, help="Max items (0 = sem limite)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--headful", action="store_true", help="roda com janela visivel")
    args = ap.parse_args()

    itens = carregar_lacunas(CSV_IN)
    if args.tipo != "TODOS":
        itens = [i for i in itens if i["categoria"] == args.tipo]
    if args.limite > 0:
        itens = itens[:args.limite]

    log("main.start", total=len(itens), tipo=args.tipo, dry_run=args.dry_run)

    if args.dry_run:
        for i in itens:
            print(i)
        log("main.dry_run_end", total=len(itens))
        return

    # agrupar faturas por contrato para fazer 1 listagem (capturar fatura_id) por contrato
    faturas_por_contrato: dict[str, list[dict]] = {}
    for i in itens:
        if i["categoria"] == "FATURA":
            faturas_por_contrato.setdefault(i["contrato_norm"], []).append(i)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headful)
        storage_arg = str(STORAGE_STATE) if STORAGE_STATE.exists() else None
        ctx = browser.new_context(storage_state=storage_arg, accept_downloads=True)
        ctx.set_default_timeout(TIMEOUT_MS)
        client = SPCFClient(ctx, SPCF_URL)

        try:
            # se nao tem storage ou se expirou, login
            if not storage_arg:
                client.login(SPCF_USER, SPCF_PASS)
            else:
                # probe leve para saber se a sessao ainda vale
                probe = ctx.new_page()
                probe.goto(f"{SPCF_URL}/index.php/spcf", timeout=TIMEOUT_MS)
                if "/usuarios/login" in probe.url:
                    probe.close()
                    client.login(SPCF_USER, SPCF_PASS)
                else:
                    client.logado = True
                    probe.close()

            # ---- CONTRATOS ----
            if args.tipo in ("CONTRATO","TODOS"):
                for i in itens:
                    if i["categoria"] != "CONTRATO":
                        continue
                    cn = i["contrato_norm"].replace("/", "_")
                    spcf_id = i.get("spcf_id") or ""
                    if not spcf_id or spcf_id.startswith("PDF_"):
                        # nao tem id SPCF — 5 sao exatamente esse caso no CSV atual
                        log("contrato.sem_spcf_id", contrato=i["contrato"])
                        continue
                    dst = DIR_CONTRATOS / f"CT_{cn}_contrato.pdf"
                    client.baixar_contrato_pdf(int(spcf_id), dst, proposta=False)
                    time.sleep(RATE_LIMIT_S)

            # ---- FATURAS ----
            if args.tipo in ("FATURA","TODOS"):
                for contrato_norm, faturas in faturas_por_contrato.items():
                    # capturar contrato_id_spcf (coluna do CSV guarda `contrato_id` do fatura_parsed)
                    contrato_id = None
                    for f in faturas:
                        sid = f.get("spcf_id")
                        if sid and sid.isdigit():
                            contrato_id = int(sid)
                            break
                    if not contrato_id:
                        log("faturas.sem_contrato_id", contrato_norm=contrato_norm, qtd=len(faturas))
                        continue

                    # 1) listar faturas do contrato para obter fatura_id por NF
                    try:
                        pares = client.listar_faturas_contrato(contrato_id)
                    except Exception as e:
                        log("listar_faturas.erro", contrato_id=contrato_id, erro=str(e))
                        continue
                    map_nf_id = {p["nf"]: p["fatura_id"] for p in pares}

                    # 2) iterar faturas faltantes
                    for f in faturas:
                        nf = f["numero_documento"]
                        fatura_id = map_nf_id.get(nf)
                        if not fatura_id:
                            log("fatura.id_nao_encontrado", nf=nf, contrato_norm=contrato_norm)
                            continue
                        cn_safe = contrato_norm.replace("/", "_")
                        dst = DIR_FATURAS / f"NF_{nf}_CT{cn_safe}.pdf"
                        client.baixar_fatura_pdf(int(fatura_id), dst)
                        time.sleep(RATE_LIMIT_S)

            # ---- NEs ----
            if args.tipo in ("NE","TODOS"):
                # SPCF provavelmente NAO expoe endpoint de NE (sao do SIAFEM/AFI).
                # Pipeline separado necessario: capturar via SGTI (scraper distinto).
                log("NE.skip", motivo="NEs sao do SIAFEM/AFI, nao do SPCF — precisa pipeline separado")

            log("main.ok", tipo=args.tipo)
        finally:
            ctx.close()
            browser.close()


if __name__ == "__main__":
    main()
