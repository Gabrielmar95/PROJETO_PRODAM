"""
classificar_e_renomear_por_conteudo.py — v3 DEFINITIVO
===========================================================================

Pipeline de 3 camadas por PDF:
  1. PATH     → define tipo canonico (NE, NF, TA, Contrato-Base, Aceite, etc)
  2. FILENAME → extrai ID/numero quando o path ja e autoritativo (SPCF)
  3. TEXTO    → usa OCR das 3 primeiras paginas para enriquecer:
                * numero canonico real (2018NE00683)
                * contrato referenciado (CT-006.2021)
                * data de emissao
                * competencia (AAAA-MM)
                * fiscal (aceite tecnico)
                * referencias NE (para NL)

Usa as skills instaladas globalmente:
  - `renomeador-pdfs-prodam\\scripts\\padroes.py`    → regex + mapas DETRAN
  - `renomeador-pdfs-prodam\\scripts\\renomeador.py` → gerar_nome_canonico()

Input : _OUT_inventario_detran_externo_*\\universo.csv (Fase 1)
Output: _OUT_conteudo_<ts>\\
        - renomear_proposto_conteudo.csv  (nomes RICOS, com contrato/data/valor)
        - classificados_conteudo.csv      (tipo final + evidencias extraidas)
        - progresso.log
        - relatorio.md

Regra jurídica: PDFs sao provas — so o nome muda, bytes nao sao tocados nesta
fase (dry-run). A aplicacao in-place vem depois via renomeador.py --apply.
"""
from __future__ import annotations

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

# Importa as skills instaladas globalmente
SKILL_RENOMEADOR = Path(r"C:\Users\gabri\.claude\skills\renomeador-pdfs-prodam\scripts")
sys.path.insert(0, str(SKILL_RENOMEADOR))

try:
    from padroes import MAPAS_POR_DEVEDOR  # type: ignore
    from renomeador import gerar_nome_canonico  # type: ignore
except Exception as e:
    print(f"[ERRO] Falha ao importar skill renomeador-pdfs-prodam: {e}",
          file=sys.stderr)
    sys.exit(1)

MAPA_DETRAN = MAPAS_POR_DEVEDOR["DETRAN"]

RAIZ_PROJETO = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")


# ---------------------------------------------------------------------------
# CLASSIFICACAO POR PATH (heranca do reclassificar_por_path.py)
# Mapeia para os tipos canonicos da skill (TIPOS_DOCUMENTO de padroes.py)
# ---------------------------------------------------------------------------
REGRAS_PATH_TIPO_HINT: list[tuple[str, str]] = [
    # DETRAN_CONSOLIDADO (prioridade maxima — estrutura canonica)
    (r"DETRAN_CONSOLIDADO[\\/]01_CONTRATOS[\\/]",        "Contrato-Base"),
    (r"DETRAN_CONSOLIDADO[\\/]02_EMPENHOS[\\/]",         "NE"),
    (r"DETRAN_CONSOLIDADO[\\/]03_FATURAS[\\/]",          "NF"),
    (r"DETRAN_CONSOLIDADO[\\/]04_NOTAS_LIQUIDACAO[\\/]", "NL"),
    (r"DETRAN_CONSOLIDADO[\\/]05_ACEITES[\\/]",          "Aceite"),
    (r"DETRAN_CONSOLIDADO[\\/]06_COBRANCAS[\\/]",        "Cobranca"),
    (r"DETRAN_CONSOLIDADO[\\/]07_SCRAPING_SPCF[\\/]",    "Extracao-SPCF"),
    (r"DETRAN_CONSOLIDADO[\\/]08_PDFS_ORIGINAIS[\\/]",   "Certidao"),
    (r"DETRAN_CONSOLIDADO[\\/]09_RELATORIOS[\\/]",       "Indefinido"),
    (r"PRODAM_DOCS[\\/]DETRAN[\\/]",                     "Indefinido"),

    # SPCF_EXTRACAO — estrutura do scraper
    (r"[\\/]SPCF_EXTRACAO[\\/]pdfs_empenhos[\\/]",       "NE"),
    (r"[\\/]SPCF_EXTRACAO[\\/]pdfs_oficiais_SPCF[\\/]",  "Extracao-SPCF"),
    (r"[\\/]SPCF_EXTRACAO[\\/]pdfs_convertidos[\\/]",    "Extracao-SPCF"),
    (r"[\\/]SPCF_EXTRACAO[\\/]htmls_brutos[\\/]",        "Extracao-SPCF"),

    # SPCF aninhado (pdfs_gerados dentro de AUDITORIA_DETRAN_COMPLETA)
    (r"[\\/]pdfs_gerados[\\/]empenhos[\\/]",             "NE"),
    (r"[\\/]pdfs_gerados[\\/]contratos[\\/]",            "Contrato-Base"),
    (r"[\\/]pdfs_gerados[\\/]faturas[\\/]",              "NF"),

    # Fallbacks genericos
    (r"[\\/]empenhos[\\/]",                              "NE"),
    (r"[\\/]faturas[\\/]",                               "NF"),
    (r"[\\/]contratos[\\/]",                             "Contrato-Base"),
    (r"[\\/]cobrancas?[\\/]",                            "Cobranca"),
    (r"[\\/]aceites?[\\/]",                              "Aceite"),
    (r"[\\/]certid[oõ]es?[\\/]",                         "Certidao"),
    (r"[\\/]notas?_liquidacao[\\/]",                     "NL"),
]


def tipo_hint_por_path(caminho: str) -> str:
    """Retorna tipo canonico (valor de TIPOS_DOCUMENTO) inferido do path."""
    for padrao, tipo in REGRAS_PATH_TIPO_HINT:
        if re.search(padrao, caminho, re.IGNORECASE):
            return tipo
    return ""  # deixa a skill decidir pelo conteudo


# ---------------------------------------------------------------------------
# EXTRACAO DE TEXTO DO PDF (primeiras 3 paginas)
# ---------------------------------------------------------------------------
def extrair_texto_pdf(p: Path, max_pages: int = 3) -> str:
    """Extrai texto das primeiras N paginas via pdfplumber.

    Se o PDF original retornar texto vazio ou muito curto (<100 chars),
    tenta abrir `<caminho>.ocr.pdf` ao lado — output do `ocr_lote_sem_texto_externo.py`.
    Isso permite que PDFs OCRizados em cascata sejam lidos sem precisar re-rodar
    o inventario.
    """
    def _ler(pdf_path: Path) -> str:
        try:
            import pdfplumber  # type: ignore
            with pdfplumber.open(str(pdf_path)) as pdf:
                paginas = pdf.pages[:max_pages]
                return "\n".join((pg.extract_text() or "") for pg in paginas)
        except Exception:
            return ""

    texto = _ler(p)
    if len(texto.strip()) >= 100:
        return texto

    # Fallback: tenta .ocr.pdf ao lado
    ocr_path = p.with_name(p.stem + ".ocr.pdf")
    if ocr_path.exists() and ocr_path != p:
        texto_ocr = _ler(ocr_path)
        if len(texto_ocr.strip()) > len(texto.strip()):
            return texto_ocr
    return texto


def sha256_file(p: Path) -> str:
    """SHA-256 do arquivo (para log de rollback da fase 3)."""
    try:
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# PROCESSAMENTO DE UM PDF
# ---------------------------------------------------------------------------
def processar(row: dict) -> dict:
    caminho = row["caminho"]
    nome = row["nome"]
    p = Path(caminho)

    if not p.exists():
        return _erro_row(row, "arquivo nao existe no disco")

    # Camada 1 — PATH
    tipo_hint = tipo_hint_por_path(caminho)

    # Camada 2/3 — sempre tenta extrair texto (extrair_texto_pdf tem fallback
    # para <caminho>.ocr.pdf quando o original nao tem texto — cobre os PDFs
    # OCRizados apos o inventario inicial).
    tem_texto = row.get("tem_texto") == "1"
    texto_ocr = extrair_texto_pdf(p)

    # Chamada da skill — gerar_nome_canonico combina filename + texto + hint
    try:
        r = gerar_nome_canonico(
            nome_original=nome,
            mapa=MAPA_DETRAN,
            orgao_hint="DETRAN",
            texto_ocr=texto_ocr,
            tipo_hint=tipo_hint,
            numero_hint="",
            data_hint="",
        )
    except Exception as e:
        return _erro_row(row, f"gerar_nome_canonico falhou: {e}")

    sha = sha256_file(p)
    try:
        size = p.stat().st_size
    except OSError:
        size = 0

    return {
        "caminho_original": caminho,
        "nome_original": nome,
        "nome_canonico": r["novo_nome"],
        "tipo_hint_path": tipo_hint,
        "tipo_final": r["tipo"],
        "contrato": r.get("contrato", ""),
        "numero": r.get("numero", ""),
        "objeto": r.get("objeto", ""),
        "fora_escopo": "1" if r.get("fora_escopo") else "0",
        "confianca": f"{float(r.get('confianca', 0.0)):.2f}",
        "tem_texto": "1" if tem_texto else "0",
        "tem_texto_util": "1" if texto_ocr else "0",
        "len_texto": str(len(texto_ocr)),
        "sha256": sha,
        "tamanho_bytes": str(size),
        "raiz": row.get("raiz", ""),
        "status": "OK",
    }


def _erro_row(row: dict, msg: str) -> dict:
    return {
        "caminho_original": row.get("caminho", ""),
        "nome_original": row.get("nome", ""),
        "nome_canonico": "",
        "tipo_hint_path": "",
        "tipo_final": "ERRO",
        "contrato": "",
        "numero": "",
        "objeto": "",
        "fora_escopo": "0",
        "confianca": "0.00",
        "tem_texto": row.get("tem_texto", "0"),
        "tem_texto_util": "0",
        "len_texto": "0",
        "sha256": "",
        "tamanho_bytes": row.get("size_bytes", "0"),
        "raiz": row.get("raiz", ""),
        "status": f"ERRO: {msg[:200]}",
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def encontrar_universo_csv() -> Path:
    """Acha o universo.csv mais recente."""
    candidatos = sorted(
        RAIZ_PROJETO.glob("_OUT_inventario_detran_externo_*/universo.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidatos:
        print("[ERRO] Nenhum universo.csv. Rode inventario_detran_externo.py antes.",
              file=sys.stderr)
        sys.exit(1)
    return candidatos[0]


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    saida = RAIZ_PROJETO / f"_OUT_conteudo_{ts}"
    saida.mkdir(parents=True, exist_ok=True)
    log_path = saida / "progresso.log"
    out_csv = saida / "renomear_proposto_conteudo.csv"

    def log(m):
        linha = f"[{datetime.now().strftime('%H:%M:%S')}] {m}"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        print(linha, flush=True)

    log(f"Saida: {saida}")

    universo_csv = encontrar_universo_csv()
    log(f"Universo: {universo_csv}")

    # Ler universo
    rows = []
    with open(universo_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)
    log(f"Total PDFs: {len(rows)}")

    # Paraleliza — pdfplumber + SHA-256 e CPU-ish mas I/O-bound no inicio
    resultados: list[dict] = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(processar, row): row for row in rows}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                resultados.append(f.result())
            except Exception as e:
                resultados.append(_erro_row(futs[f], f"exception: {e}"))
            if i % 100 == 0:
                gravar_csv(out_csv, resultados)
                tempo = time.time() - t0
                vel = i / tempo if tempo > 0 else 0
                eta_min = (len(rows) - i) / vel / 60 if vel > 0 else 0
                log(f"  {i}/{len(rows)} ({vel:.1f} pdf/s, ETA {eta_min:.1f} min)")

    gravar_csv(out_csv, resultados)

    # Relatorio
    tempo_total = time.time() - t0
    n_ok = sum(1 for r in resultados if r.get("status") == "OK")
    n_erro = sum(1 for r in resultados if r.get("status", "").startswith("ERRO"))
    tipos = Counter(r.get("tipo_final", "?") for r in resultados)
    fora_escopo = sum(1 for r in resultados if r.get("fora_escopo") == "1")
    conf_alta = sum(1 for r in resultados
                    if float(r.get("confianca", 0) or 0) >= 0.7)

    log(f"\nTerminou em {tempo_total/60:.1f} min")
    log(f"  OK: {n_ok} | Erros: {n_erro}")
    log(f"  Fora de escopo (sem CT): {fora_escopo}")
    log(f"  Confianca >= 0.7: {conf_alta}")
    log(f"  Por tipo: {dict(tipos.most_common())}")

    # Relatorio MD
    rel_md = saida / "relatorio.md"
    linhas = [
        f"# Classificacao + Renomeacao por CONTEUDO — {ts}",
        "",
        f"**Input:** `{universo_csv}`",
        f"**PDFs processados:** {len(resultados)}",
        f"**OK:** {n_ok} | **Erros:** {n_erro}",
        f"**Tempo:** {tempo_total/60:.1f} min",
        f"**Confianca >= 0.7:** {conf_alta} ({conf_alta/len(resultados)*100:.1f}%)",
        "",
        "## Distribuicao por tipo final",
        "| Tipo | Qtd |",
        "|---|---:|",
    ]
    for t, n in tipos.most_common():
        linhas.append(f"| {t} | {n} |")

    linhas += [
        "",
        "## Flags",
        f"- Fora de escopo (sem contrato identificado): **{fora_escopo}**",
        f"- Com texto util extraido: {sum(1 for r in resultados if r.get('tem_texto_util') == '1')}",
        "",
        "## Proximos passos",
        "1. Revisar `renomear_proposto_conteudo.csv`",
        "2. Se OK: invocar `renomeador-pdfs-prodam --apply` com flag in-place",
        "3. O SHA-256 de cada PDF ja esta no CSV → use como ancora de rollback",
        "",
    ]
    with open(rel_md, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    log(f"  gravado: {rel_md}")


def gravar_csv(path: Path, resultados: list[dict]):
    cols = ["caminho_original", "nome_original", "nome_canonico",
            "tipo_hint_path", "tipo_final", "contrato", "numero", "objeto",
            "fora_escopo", "confianca", "tem_texto", "tem_texto_util",
            "len_texto", "sha256", "tamanho_bytes", "raiz", "status"]
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
