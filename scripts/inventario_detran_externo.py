"""
Inventario + classificacao dos PDFs DETRAN fora de DETRAN_AUDITORIA_COMPLETA.

Escopo (multi-raiz, ao contrario do script original):
  - SPCF_EXTRACAO\           (filtrar: so PDFs DETRAN — nome ou path contem 'detran')
  - PRODAM_DOCS\DETRAN_CONSOLIDADO\  (tudo)
  - PRODAM_DOCS\DETRAN\      (tudo — 1 PDF)

Pipeline (dry-run, nao renomeia nada):
  Camada 1: scanner de texto (pymupdf) — detecta sem-texto (candidatos a OCR)
  Camada 2: classificacao de conteudo (pdfplumber + classificador da skill ocr-pdfs-prodam)
  Camada 3: propostas de renomeacao canonica (so suspeitos com conf >= 0.3)

Saidas em PROJETO_PRODAM\_OUT_inventario_detran_externo_<ts>\:
  - universo.csv           (1 linha por PDF)
  - classificados.csv      (tipo, num, orgao, data, valor, conf)
  - renomear_proposto.csv  (propostas com conf >= MEDIA)
  - relatorio.md           (resumo executivo)
  - progresso.log          (log com timestamp)

Baseado em: DETRAN_AUDITORIA_COMPLETA\10_SCRIPTS_PYTHON\inventario_classificacao_global.py
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

# Importa classificador da skill ocr-pdfs-prodam
SKILL_SCRIPTS = Path(r"C:\Users\gabri\.claude\skills\ocr-pdfs-prodam\scripts")
sys.path.insert(0, str(SKILL_SCRIPTS))
try:
    from classificador_conteudo import classificar_conteudo  # type: ignore
except Exception as e:
    print(f"[ERRO] Nao conseguiu importar classificador: {e}", file=sys.stderr)
    sys.exit(1)


# Raizes a varrer
RAIZ_PROJETO = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")
RAIZES = [
    Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM\SPCF_EXTRACAO"),
    Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\DETRAN_CONSOLIDADO"),
    Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\DETRAN"),
]

# Filtros de pastas a ignorar dentro das raizes
INTOCAVEIS = [
    ".git",
    "__pycache__",
    "_ARCHIVE",
    "_LIXEIRA",
]

# Filtros de arquivo a ignorar (dentro do SPCF_EXTRACAO, so queremos DETRAN)
def filtrar_detran_se_preciso(p: Path, raiz: Path) -> bool:
    """Em SPCF_EXTRACAO: so PDFs com 'detran' no nome ou path. Nas outras raizes: tudo."""
    if raiz.name == "SPCF_EXTRACAO":
        s = str(p).lower()
        return "detran" in s
    return True


def eh_intocavel(p: Path) -> bool:
    s = str(p).lower()
    return any(i.lower() in s for i in INTOCAVEIS)


RE_SUSPEITO = re.compile(
    r"^(scan_\d+|img_\d+|document(\s*\(\d+\))?|documento\s*\(\d+\)|untitled"
    r"|\d{6,}|[a-f0-9]{16,})\.pdf$",
    re.IGNORECASE,
)


def nome_suspeito(nome: str) -> bool:
    if RE_SUSPEITO.match(nome):
        return True
    stem = nome.rsplit(".", 1)[0]
    if not stem:
        return False
    digs = sum(c.isdigit() for c in stem)
    return digs / len(stem) >= 0.7


def scan_texto_pymupdf(p: Path) -> tuple[bool, int, int]:
    """(tem_texto, num_paginas, chars_primeira_pagina). Falhas -> (False, 0, 0)."""
    try:
        import fitz  # type: ignore
    except Exception:
        return False, 0, 0
    try:
        with fitz.open(str(p)) as doc:
            n = len(doc)
            if n == 0:
                return False, 0, 0
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
            return tem, n, chars_p1
    except Exception:
        return False, 0, 0


def extrair_texto_3pag(p: Path) -> str:
    """Extrai texto das primeiras 3 paginas via pdfplumber."""
    try:
        import pdfplumber  # type: ignore
        with pdfplumber.open(str(p)) as pdf:
            return "\n".join((pg.extract_text() or "") for pg in pdf.pages[:3])
    except Exception:
        return ""


def rel_to_projeto(p: Path) -> str:
    try:
        return str(p.relative_to(RAIZ_PROJETO))
    except ValueError:
        return str(p)


def raiz_de(p: Path) -> str:
    """Retorna o nome da raiz em que o PDF esta."""
    for r in RAIZES:
        try:
            p.relative_to(r)
            return r.name
        except ValueError:
            continue
    return "?"


def processar_scan(p: Path) -> dict:
    try:
        sz = p.stat().st_size
    except OSError:
        sz = 0
    tem, n, c1 = scan_texto_pymupdf(p)
    rel = rel_to_projeto(p)
    return {
        "caminho": str(p),
        "caminho_rel": rel,
        "raiz": raiz_de(p),
        "nome": p.name,
        "size_bytes": sz,
        "paginas": n,
        "tem_texto": int(tem),
        "chars_p1": c1,
        "suspeito": int(nome_suspeito(p.name)),
    }


def processar_class(p: Path) -> dict:
    texto = extrair_texto_3pag(p)
    try:
        r = classificar_conteudo(texto, nome_arquivo=p.name)
    except Exception as e:
        r = {"tipo": "OUTRO", "erro": str(e), "confianca": 0.0}
    return {
        "caminho": str(p),
        "nome": p.name,
        "raiz": raiz_de(p),
        "tipo": r.get("tipo", "OUTRO"),
        "numero": r.get("numero") or "",
        "orgao": r.get("orgao") or "",
        "cnpj": r.get("cnpj") or "",
        "data": r.get("data") or "",
        "valor": str(r.get("valor") or ""),
        "confianca": r.get("confianca", 0.0),
    }


def hash6(p: Path) -> str:
    try:
        s = f"{p.name}|{p.stat().st_size}|{int(p.stat().st_mtime)}"
    except OSError:
        s = p.name
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:6]


def nome_canonico(c: dict, original: Path) -> str:
    tipo = c.get("tipo", "OUTRO") or "OUTRO"
    num = (c.get("numero") or "").replace("/", "").replace("-", "").replace(".", "")
    orgao = c.get("orgao") or ""
    data = c.get("data") or ""
    h = hash6(original)
    partes = [tipo]
    if num:
        partes.append(num)
    if orgao:
        partes.append(orgao)
    if data:
        partes.append(data)
    partes.append(h)
    return "_".join(partes) + ".pdf"


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    saida = RAIZ_PROJETO / f"_OUT_inventario_detran_externo_{ts}"
    saida.mkdir(parents=True, exist_ok=True)

    log_path = saida / "progresso.log"
    def log(msg):
        linha = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        print(linha, flush=True)

    log(f"Saida: {saida}")
    log(f"Raizes: {[str(r) for r in RAIZES]}")

    # ------------------------------------------------------------------
    # CAMADA 1: enumeracao + scanner de texto
    # ------------------------------------------------------------------
    log("Camada 1/3: enumerando PDFs...")
    t0 = time.time()
    alvos: list[Path] = []
    for raiz in RAIZES:
        if not raiz.exists():
            log(f"  AVISO: raiz nao existe: {raiz}")
            continue
        for p in raiz.rglob("*.pdf"):
            if eh_intocavel(p):
                continue
            if not filtrar_detran_se_preciso(p, raiz):
                continue
            alvos.append(p)
        for p in raiz.rglob("*.PDF"):
            if eh_intocavel(p) or p in alvos:
                continue
            if not filtrar_detran_se_preciso(p, raiz):
                continue
            alvos.append(p)
    log(f"  {len(alvos)} PDFs enumerados em {time.time()-t0:.1f}s")

    log("Camada 1/3: scanner de texto (pymupdf) com 8 threads...")
    scan_rows: list[dict] = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(processar_scan, p): p for p in alvos}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                scan_rows.append(f.result())
            except Exception as e:
                scan_rows.append({
                    "caminho": str(futs[f]), "caminho_rel": "", "raiz": "",
                    "nome": futs[f].name,
                    "size_bytes": 0, "paginas": 0, "tem_texto": 0, "chars_p1": 0,
                    "suspeito": 0, "erro": str(e),
                })
            if i % 500 == 0:
                log(f"  scan {i}/{len(alvos)} ({i/(time.time()-t0):.1f} pdf/s)")
    log(f"  scan concluido em {time.time()-t0:.1f}s")

    universo_csv = saida / "universo.csv"
    cols = ["caminho", "caminho_rel", "raiz", "nome", "size_bytes", "paginas",
            "tem_texto", "chars_p1", "suspeito"]
    with open(universo_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in scan_rows:
            w.writerow(r)
    log(f"  gravado: {universo_csv}")

    sem_texto = [Path(r["caminho"]) for r in scan_rows if r.get("tem_texto") == 0]
    suspeitos = [Path(r["caminho"]) for r in scan_rows if r.get("suspeito") == 1]
    log(f"  PDFs sem texto (candidatos a OCR): {len(sem_texto)}")
    log(f"  PDFs com nome suspeito          : {len(suspeitos)}")

    # ------------------------------------------------------------------
    # CAMADA 2: classificacao de conteudo
    # ------------------------------------------------------------------
    # Classifica TODOS os com texto (em SPCF/CONSOLIDADO queremos saber tipo de tudo).
    candidatos_class = [Path(r["caminho"]) for r in scan_rows if r.get("tem_texto") == 1]
    log(f"Camada 2/3: classificando {len(candidatos_class)} PDFs (4 threads)...")
    class_rows: list[dict] = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(processar_class, p): p for p in candidatos_class}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                class_rows.append(f.result())
            except Exception as e:
                class_rows.append({
                    "caminho": str(futs[f]), "nome": futs[f].name, "raiz": "",
                    "tipo": "ERRO", "numero": "", "orgao": "", "cnpj": "",
                    "data": "", "valor": "", "confianca": 0.0,
                })
            if i % 200 == 0:
                log(f"  class {i}/{len(candidatos_class)} ({i/(time.time()-t0):.1f} pdf/s)")
    log(f"  classificacao concluida em {time.time()-t0:.1f}s")

    class_csv = saida / "classificados.csv"
    cols = ["caminho", "nome", "raiz", "tipo", "numero", "orgao", "cnpj",
            "data", "valor", "confianca"]
    with open(class_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in class_rows:
            w.writerow(r)
    log(f"  gravado: {class_csv}")

    # ------------------------------------------------------------------
    # CAMADA 3: propostas de renomeacao (dry-run)
    # ------------------------------------------------------------------
    log("Camada 3/3: propostas de renomeacao (conf >= 0.3)...")
    class_por_path = {r["caminho"]: r for r in class_rows}
    renomear_rows: list[dict] = []

    # Cobertura ampla: propor renomear TODOS classificados com conf >= 0.3
    # (usuario pediu renomear in-place baseado em conteudo)
    for r in class_rows:
        p = Path(r["caminho"])
        conf = r.get("confianca", 0.0)
        if conf < 0.3:
            continue
        canonico = nome_canonico(r, p)
        # So propoe se o nome novo for diferente do atual
        if canonico == p.name:
            continue
        renomear_rows.append({
            "caminho_original": str(p),
            "nome_original": p.name,
            "nome_proposto": canonico,
            "raiz": r.get("raiz", ""),
            "confianca": conf,
            "tipo": r.get("tipo"),
            "numero": r.get("numero"),
            "orgao": r.get("orgao"),
            "data": r.get("data"),
            "suspeito": int(nome_suspeito(p.name)),
        })

    renomear_csv = saida / "renomear_proposto.csv"
    cols = ["caminho_original", "nome_original", "nome_proposto", "raiz",
            "confianca", "tipo", "numero", "orgao", "data", "suspeito"]
    with open(renomear_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in renomear_rows:
            w.writerow(r)
    log(f"  gravado: {renomear_csv} ({len(renomear_rows)} propostas)")

    # ------------------------------------------------------------------
    # Relatorio MD
    # ------------------------------------------------------------------
    rel = saida / "relatorio.md"
    total_sz_mb = sum(r.get("size_bytes", 0) for r in scan_rows) / (1024 * 1024)
    por_raiz = Counter(r.get("raiz", "") for r in scan_rows)
    tipos = Counter(r.get("tipo", "") for r in class_rows)
    sem_texto_por_raiz = Counter(r.get("raiz", "") for r in scan_rows if r.get("tem_texto") == 0)
    suspeitos_por_raiz = Counter(r.get("raiz", "") for r in scan_rows if r.get("suspeito") == 1)

    linhas = [
        "# Inventario + Classificacao — PDFs DETRAN externos",
        "",
        f"**Data:** {datetime.now().isoformat(timespec='seconds')}",
        f"**Raizes:**",
    ]
    for r in RAIZES:
        linhas.append(f"- `{r}`")
    linhas += [
        "",
        "## Universo",
        f"- PDFs totais: **{len(scan_rows)}**",
        f"- Tamanho: **{total_sz_mb:.0f} MB**",
        f"- Com texto embutido: **{sum(1 for r in scan_rows if r.get('tem_texto')==1)}**",
        f"- Sem texto (candidatos a OCR): **{len(sem_texto)}**",
        f"- Com nome suspeito: **{len(suspeitos)}**",
        "",
        "## Distribuicao por raiz",
        "| Raiz | PDFs | Sem texto | Suspeitos |",
        "|---|---:|---:|---:|",
    ]
    for raiz_nome, n in por_raiz.most_common():
        linhas.append(
            f"| {raiz_nome} | {n} | {sem_texto_por_raiz.get(raiz_nome, 0)} "
            f"| {suspeitos_por_raiz.get(raiz_nome, 0)} |"
        )

    linhas += [
        "",
        "## Classificacao de conteudo",
        f"- PDFs classificados (com texto): **{len(class_rows)}**",
        "",
        "| Tipo | Qtd |",
        "|---|---:|",
    ]
    for t, n in tipos.most_common():
        linhas.append(f"| {t} | {n} |")

    linhas += [
        "",
        "## Propostas de renomeacao (dry-run)",
        f"- Propostas geradas (conf >= 0.3, nome diferente): **{len(renomear_rows)}**",
        "- Arquivo: `renomear_proposto.csv`",
        "- Nada foi renomeado. Gabriel revisa antes de Fase 3.",
        "",
        "## Proximos passos",
        f"1. Rodar OCR em **{len(sem_texto)} PDFs sem texto** via ocr_lote_sem_texto_externo.py",
        f"2. Revisar `renomear_proposto.csv` ({len(renomear_rows)} itens)",
        "3. Aplicar renomeacao in-place na Fase 3",
        "",
    ]
    with open(rel, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    log(f"  gravado: {rel}")

    log("TERMINOU.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
