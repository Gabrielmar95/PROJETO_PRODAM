"""
detran_consolidado_to_json_pipeline.py — Pipeline industrial para converter TODO
o DETRAN_CONSOLIDADO em JSON estruturado.

Subpastas processadas:
  01_CONTRATOS/       (70 PDFs — contratos + aditivos)
  02_EMPENHOS/        (111 PDFs — Notas de Empenho)
  03_FATURAS/         (121 PDFs — NFSe/faturas)
  04_NOTAS_LIQUIDACAO/ (vazia)
  05_ACEITES/         (17 PDFs — aceites técnicos)
  06_COBRANCAS/       (91 PDFs — ofícios cobrança)
  07_SCRAPING_SPCF/   (8 arquivos CSV)
  08_PDFS_ORIGINAIS/  (24 — certidões, etc)
  09_RELATORIOS/      (13 — auditorias MD/HTML/PDF)

Arquitetura por PDF:
  1. Extrator rápido: PyMuPDF (se texto nativo) → sucesso em ~50%
  2. Fallback: pdfplumber (tabelas e layouts complexos)
  3. Fallback: pytesseract OCR (scans)
  4. Parser específico por categoria (regex + heurísticas)
  5. JSON saída com:
     - texto completo
     - metadados (páginas, tamanho, método)
     - campos estruturados por categoria
     - tabelas extraídas (quando aplicável)

Saída:
  DETRAN_CONSOLIDADO_JSON/
    ├── 01_CONTRATOS/*.json (70)
    ├── 02_EMPENHOS/*.json (111)
    ├── 03_FATURAS/*.json (121)
    ├── 05_ACEITES/*.json (17)
    ├── 06_COBRANCAS/*.json (91)
    ├── 07_SCRAPING_SPCF/*.json (8)
    ├── 08_PDFS_ORIGINAIS/*.json (24)
    ├── 09_RELATORIOS/*.json (13)
    ├── MASTER_DETRAN_CONSOLIDADO.json — índice global
    └── RELATORIO_PIPELINE.md

Paralelismo: 4 workers via ThreadPoolExecutor.
"""
from __future__ import annotations
import sys, json, re, csv, time
from pathlib import Path
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
from prodam_utils import brl, fmt_brl, parse_br_date, norm

import fitz       # PyMuPDF
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

SRC = ROOT / "PRODAM_DOCS" / "DETRAN_CONSOLIDADO"
OUT = ROOT / "DETRAN_CONSOLIDADO_JSON"
OUT.mkdir(exist_ok=True)

TESS_CONFIG = "--psm 3 -l por"

# ============================================================
# EXTRAÇÃO DE TEXTO — 3 estratégias em cascata
# ============================================================
def extrair_pymupdf(path: Path) -> tuple[str, dict, list]:
    """Rápido, texto nativo. Retorna (texto, meta, tabelas=[])."""
    meta = {"metodo": "pymupdf", "paginas": 0}
    try:
        with fitz.open(str(path)) as doc:
            meta["paginas"] = len(doc)
            textos = [pg.get_text() for pg in doc]
            texto = "\n".join(textos)
        return texto, meta, []
    except Exception as e:
        meta["erro"] = str(e)[:200]
        return "", meta, []

def extrair_pdfplumber(path: Path) -> tuple[str, dict, list]:
    """Mais lento mas melhor para tabelas e layouts complexos."""
    meta = {"metodo": "pdfplumber", "paginas": 0}
    tabelas = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            meta["paginas"] = len(pdf.pages)
            textos = []
            for pg in pdf.pages:
                t = pg.extract_text() or ""
                textos.append(t)
                tabs = pg.extract_tables()
                for tab in tabs:
                    if tab:
                        tabelas.append(tab)
        texto = "\n".join(textos)
        return texto, meta, tabelas
    except Exception as e:
        meta["erro"] = str(e)[:200]
        return "", meta, []

def extrair_ocr(path: Path) -> tuple[str, dict, list]:
    """Último recurso — OCR com pytesseract."""
    meta = {"metodo": "ocr_tesseract", "paginas": 0}
    try:
        images = convert_from_path(str(path), dpi=200, grayscale=True)
        meta["paginas"] = len(images)
        textos = [pytesseract.image_to_string(img, config=TESS_CONFIG) for img in images]
        texto = "\n\n===PAGINA===\n\n".join(textos)
        return texto, meta, []
    except Exception as e:
        meta["erro"] = str(e)[:200]
        return "", meta, []

def extrair_texto_com_fallback(path: Path) -> tuple[str, dict, list]:
    """Cascade: PyMuPDF → pdfplumber → OCR."""
    # 1. PyMuPDF
    texto, meta, tabs = extrair_pymupdf(path)
    if texto and len(texto.strip()) > 100:
        return texto, meta, tabs

    # 2. pdfplumber (pega tabelas que PyMuPDF pode perder)
    texto2, meta2, tabs2 = extrair_pdfplumber(path)
    if texto2 and len(texto2.strip()) > 100:
        meta2["fallback_from"] = "pymupdf"
        return texto2, meta2, tabs2

    # 3. OCR (scans)
    texto3, meta3, tabs3 = extrair_ocr(path)
    meta3["fallback_from"] = "pymupdf_e_pdfplumber"
    return texto3, meta3, tabs3

# ============================================================
# PARSERS POR CATEGORIA
# ============================================================
RE_VALOR = re.compile(r"R\$\s*([\d.]+(?:[,.]\d{2})?)")
RE_DATA = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b")
RE_CNPJ = re.compile(r"\b(\d{2}[.\s]?\d{3}[.\s]?\d{3}[/\s]?\d{4}[-\s]?\d{2})\b")
RE_CONTRATO = re.compile(r"(?:C(?:ontrato)?\.?\s*|CT\s*|CONTRATO\s+(?:Nº?\s*)?)?(\d{2,3})\.(\d{2,4})", re.IGNORECASE)
RE_NE = re.compile(r"\b(\d{4}NE\d{4,7})\b", re.IGNORECASE)
RE_NF = re.compile(r"\bNFS?[e\-]?\s*(?:Nº|n\.?|número)?\s*(\d{4,7})\b", re.IGNORECASE)
RE_EMPENHO_NUM = re.compile(r"(?:empenho|NE)\s*(?:n[°º]?|nº|N\.)?\s*(\d{4}NE\d+)", re.IGNORECASE)
RE_OFICIO = re.compile(r"\b(?:Of[íi]cio|OF\.?)\s*(?:Nº?|n\.?)?\s*(\d+[/\-.]?\d{2,4})", re.IGNORECASE)

RE_INDICES = {
    "IGPM": re.compile(r"\bIGP-?M\b", re.IGNORECASE),
    "IPCA": re.compile(r"\bIPCA\b", re.IGNORECASE),
    "INPC": re.compile(r"\bINPC\b", re.IGNORECASE),
    "SELIC": re.compile(r"\bSELIC\b", re.IGNORECASE),
}

def _num(s: str) -> float:
    try:
        return float(str(s).replace(".", "").replace(",", "."))
    except: return 0.0

def parse_comum(texto: str) -> dict:
    """Campos comuns a todos tipos."""
    out = {}
    # CNPJs
    cnpjs = list(dict.fromkeys(RE_CNPJ.findall(texto)))
    if cnpjs: out["cnpjs"] = cnpjs[:5]
    # Datas
    datas = list(dict.fromkeys(RE_DATA.findall(texto)))
    if datas: out["datas_encontradas"] = datas[:10]
    # Valores
    valores = RE_VALOR.findall(texto)
    if valores: out["valores_brl"] = list(dict.fromkeys(valores))[:15]
    # Contratos referenciados
    contratos = list(dict.fromkeys(f"{int(m.group(1)):03d}/{m.group(2) if len(m.group(2))==4 else '20'+m.group(2)}" for m in RE_CONTRATO.finditer(texto)))
    if contratos: out["contratos_referenciados"] = contratos[:5]
    # NE / NF
    nes = list(dict.fromkeys(m.group(0) for m in RE_NE.finditer(texto)))
    if nes: out["nes_referenciadas"] = nes[:15]
    # Índices
    indices = [k for k,rx in RE_INDICES.items() if rx.search(texto)]
    if indices: out["indices_mencionados"] = indices
    return out

def parse_contrato(texto: str, filename: str) -> dict:
    """Parser específico de contrato/aditivo."""
    out = parse_comum(texto)
    # Tipo (filename)
    fn_lower = filename.lower()
    if "aditivo" in fn_lower or re.search(r"\d[°ºo]\s*TA", filename, re.IGNORECASE):
        out["tipo_doc"] = "TERMO_ADITIVO"
    elif "proposta" in fn_lower:
        out["tipo_doc"] = "PROPOSTA"
    else:
        out["tipo_doc"] = "CONTRATO_PRINCIPAL"
    # Cláusula 11 (reajuste)
    m = re.search(r"cl[áa]usula\s+(?:d[ée]cima\s+primeira|11[°ªa]?|XI|onze).{0,800}", texto, re.IGNORECASE | re.DOTALL)
    if m:
        out["clausula_11"] = m.group(0)[:600]
    # Objeto (cláusula 1 / primeira)
    m = re.search(r"cl[áa]usula\s+(?:primeira|1[ªa°]?|I\b).{0,500}", texto, re.IGNORECASE | re.DOTALL)
    if m:
        out["clausula_objeto"] = m.group(0)[:400]
    # Vigência datas
    dts = re.findall(r"(\d{1,2}/\d{1,2}/\d{2,4})\s*(?:a|at[ée])\s*(\d{1,2}/\d{1,2}/\d{2,4})", texto)
    if dts: out["periodos_vigencia"] = [list(d) for d in dts[:3]]
    # Percentual reajuste
    pcts = re.findall(r"(?:reajuste|atualiza).{0,100}?(\d{1,2}[,.]?\d{1,3})\s*%", texto, re.IGNORECASE | re.DOTALL)
    if pcts: out["reajustes_pct"] = [_num(p) for p in pcts[:5]]
    # Multa
    multas = re.findall(r"multa.{0,50}?(\d+[,.]?\d*)\s*%", texto, re.IGNORECASE)
    if multas: out["multas_pct"] = [_num(m) for m in multas[:3]]
    # Juros
    juros = re.findall(r"juros.{0,80}?(\d+[,.]?\d*)\s*%\s*(?:a\.?\s*m\.?|ao\s+m[êe]s)", texto, re.IGNORECASE)
    if juros: out["juros_pct_am"] = [_num(j) for j in juros[:3]]
    return out

def parse_empenho(texto: str, filename: str) -> dict:
    """Parser de Nota de Empenho."""
    out = parse_comum(texto)
    out["tipo_doc"] = "NOTA_EMPENHO"
    m = RE_EMPENHO_NUM.search(texto)
    if m: out["numero_ne"] = m.group(1)
    # Valor (provável primeiro R$ grande)
    if "valores_brl" in out:
        for v in out["valores_brl"]:
            num = _num(v)
            if 100 <= num <= 100_000_000:
                out["valor_empenho"] = num; break
    # Descrição (após "Descrição:" ou "Objeto:")
    m = re.search(r"Descri[çc][ãa]o.{0,20}?[:\.]?\s*(.+?)(?:\n\s*\n|Evento|Valor|Situa)", texto, re.IGNORECASE | re.DOTALL)
    if m: out["descricao"] = m.group(1).strip()[:400]
    # Situação
    if "Ativo" in texto: out["situacao"] = "Ativo"
    elif "Cancelado" in texto: out["situacao"] = "Cancelado"
    elif "Liquidado" in texto: out["situacao"] = "Liquidado"
    return out

def parse_fatura(texto: str, filename: str) -> dict:
    """Parser de NF/NFSe/fatura."""
    out = parse_comum(texto)
    out["tipo_doc"] = "FATURA"
    m = RE_NF.search(texto)
    if m: out["numero_nfse"] = m.group(1)
    # Competência (MM/YYYY)
    m = re.search(r"Compet[êe]ncia[:\s]+(\d{1,2}/\d{4})", texto, re.IGNORECASE)
    if m: out["competencia"] = m.group(1)
    # Serviço prestado
    m = re.search(r"Servi[çc]o[:\s]+(.+?)(?:\n|Valor)", texto, re.IGNORECASE | re.DOTALL)
    if m: out["servico"] = m.group(1).strip()[:300]
    return out

def parse_aceite(texto: str, filename: str) -> dict:
    out = parse_comum(texto)
    out["tipo_doc"] = "ACEITE_TECNICO"
    if re.search(r"ACEIT[EO]|HOMOLOGA[ÇC][ÃA]O", texto, re.IGNORECASE):
        out["confirma_aceite"] = True
    # Responsável
    m = re.search(r"(?:Fiscal|Respons[áa]vel|Gestor)[:\s]+(.+?)(?:\n|CPF)", texto, re.IGNORECASE)
    if m: out["responsavel"] = m.group(1).strip()[:150]
    return out

def parse_cobranca(texto: str, filename: str) -> dict:
    out = parse_comum(texto)
    out["tipo_doc"] = "OFICIO_COBRANCA"
    m = RE_OFICIO.search(texto)
    if m: out["oficio_numero"] = m.group(1)
    # Destinatário
    m = re.search(r"(?:Ao Senhor|Exmo|Ilmo|Senhor[a]?)[:,]?\s*(.+?)(?:\n|CPF|CNPJ)", texto, re.IGNORECASE)
    if m: out["destinatario"] = m.group(1).strip()[:150]
    # Valor reclamado
    if "valores_brl" in out:
        out["valor_cobrado_possivel"] = out["valores_brl"][0] if out["valores_brl"] else None
    return out

def parse_certidao(texto: str, filename: str) -> dict:
    out = parse_comum(texto)
    out["tipo_doc"] = "CERTIDAO"
    if "negativa" in texto.lower(): out["tipo_cnd"] = "NEGATIVA"
    elif "positiva" in texto.lower(): out["tipo_cnd"] = "POSITIVA_COM_EFEITOS_NEGATIVA" if "efeitos de negativa" in texto.lower() else "POSITIVA"
    if "FGTS" in texto: out["orgao"] = "FGTS/CEF"
    elif "Receita Federal" in texto or "RFB" in texto: out["orgao"] = "RFB"
    elif "Trabalhista" in texto: out["orgao"] = "TST"
    elif "Fal[êe]ncia" in texto or "Fal" in texto: out["orgao"] = "CARTORIO_FALENCIA"
    return out

def parse_relatorio(texto: str, filename: str) -> dict:
    out = parse_comum(texto)
    out["tipo_doc"] = "RELATORIO"
    return out

CATEGORIAS = {
    "01_CONTRATOS": ("CONTRATO_OU_ADITIVO", parse_contrato),
    "02_EMPENHOS": ("NOTA_EMPENHO", parse_empenho),
    "03_FATURAS": ("FATURA", parse_fatura),
    "05_ACEITES": ("ACEITE_TECNICO", parse_aceite),
    "06_COBRANCAS": ("OFICIO_COBRANCA", parse_cobranca),
    "08_PDFS_ORIGINAIS": ("CERTIDAO_OU_OUTROS", parse_certidao),
    "09_RELATORIOS": ("RELATORIO", parse_relatorio),
}

# ============================================================
# 07_SCRAPING_SPCF são CSVs — conversão direta
# ============================================================
def processar_csv(path: Path) -> dict:
    out = {"tipo_doc": "CSV_SPCF", "filename": path.name, "path": str(path.relative_to(ROOT))}
    try:
        rows = []
        with open(path, encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter=";")
            rows = list(reader)
        if not rows:
            # Tenta vírgula
            with open(path, encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        out["total_linhas"] = len(rows)
        out["campos"] = list(rows[0].keys()) if rows else []
        out["amostra_5_linhas"] = rows[:5]
        out["dados_completos"] = rows
    except Exception as e:
        out["erro"] = str(e)
    return out

# ============================================================
# PROCESSADOR GENÉRICO
# ============================================================
def processar_pdf(path: Path, categoria_folder: str, parser_fn) -> dict:
    inicio = time.time()
    texto, meta, tabelas = extrair_texto_com_fallback(path)
    campos = parser_fn(texto, path.name) if texto else {}
    return {
        "filename": path.name,
        "path": str(path.relative_to(ROOT)),
        "categoria": categoria_folder,
        "data_extracao": date.today().isoformat(),
        "tamanho_bytes": path.stat().st_size,
        "texto_length": len(texto),
        "texto_preview": texto[:800] if texto else "",
        "texto_completo": texto,
        "pdf_meta": meta,
        "tabelas_detectadas_qtd": len(tabelas),
        "tabelas": [{"linhas": len(t), "colunas": len(t[0]) if t else 0, "amostra": t[:3]} for t in tabelas[:5]],
        "campos_estruturados": campos,
        "tempo_segundos": round(time.time() - inicio, 1),
    }

# ============================================================
# MAIN — processa todas subpastas em paralelo
# ============================================================
def safe_filename(name: str) -> str:
    return re.sub(r"[^\w.-]", "_", name)

tarefas = []
for folder_name, (tipo, parser_fn) in CATEGORIAS.items():
    folder = SRC / folder_name
    if not folder.exists(): continue
    out_folder = OUT / folder_name
    out_folder.mkdir(exist_ok=True)
    for pdf in folder.glob("*.pdf"):
        json_out = out_folder / (safe_filename(pdf.stem) + ".json")
        tarefas.append((pdf, folder_name, parser_fn, json_out))

# CSVs (07_SCRAPING_SPCF)
csv_folder = SRC / "07_SCRAPING_SPCF"
if csv_folder.exists():
    out_csv_folder = OUT / "07_SCRAPING_SPCF"
    out_csv_folder.mkdir(exist_ok=True)
    for csv_path in csv_folder.glob("*.csv"):
        json_out = out_csv_folder / (csv_path.stem + ".json")
        tarefas.append((csv_path, "07_SCRAPING_SPCF", None, json_out))

print(f"Tarefas: {len(tarefas)} (PDFs + CSVs)")
print(f"Estrategia: PyMuPDF → pdfplumber → OCR (cascade)")
print(f"Paralelismo: 4 workers\n")

def worker(tarefa):
    path, folder_name, parser_fn, json_out = tarefa
    try:
        if path.suffix.lower() == ".csv":
            data = processar_csv(path)
            data["categoria"] = folder_name
        else:
            data = processar_pdf(path, folder_name, parser_fn)
        json_out.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return {"ok": True, "filename": path.name, "categoria": folder_name, "metodo": data.get("pdf_meta",{}).get("metodo") or "csv", "tempo": data.get("tempo_segundos",0)}
    except Exception as e:
        return {"ok": False, "filename": path.name, "categoria": folder_name, "erro": str(e)[:200]}

resultados = []
inicio = time.time()
with ThreadPoolExecutor(max_workers=4) as ex:
    futures = {ex.submit(worker, t): t for t in tarefas}
    for i, fut in enumerate(as_completed(futures), 1):
        r = fut.result()
        resultados.append(r)
        if i % 20 == 0 or i == len(tarefas):
            elapsed = time.time() - inicio
            eta = elapsed/i * (len(tarefas)-i)
            print(f"  [{i:3d}/{len(tarefas)}] {elapsed:.0f}s | ETA {eta:.0f}s | {r['filename'][:50]}")

print(f"\nConcluído em {time.time()-inicio:.0f}s")
print(f"Sucessos: {sum(1 for r in resultados if r.get('ok'))}/{len(resultados)}")

# ============================================================
# MASTER e RELATÓRIO
# ============================================================
master = {
    "data_pipeline": date.today().isoformat(),
    "total_arquivos": len(resultados),
    "total_sucesso": sum(1 for r in resultados if r.get('ok')),
    "por_categoria": {},
    "por_metodo": defaultdict(int),
}
for r in resultados:
    cat = r["categoria"]
    master["por_categoria"].setdefault(cat, {"total": 0, "sucesso": 0})
    master["por_categoria"][cat]["total"] += 1
    if r.get("ok"):
        master["por_categoria"][cat]["sucesso"] += 1
    master["por_metodo"][r.get("metodo","?")] += 1

master["por_metodo"] = dict(master["por_metodo"])

json.dump(master, open(OUT / "MASTER_DETRAN_CONSOLIDADO.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)

# Relatório MD
md = f"""# DETRAN_CONSOLIDADO → JSON Pipeline

**Data:** {date.today().isoformat()}
**Fonte:** `PRODAM_DOCS/DETRAN_CONSOLIDADO/` (455 arquivos, 1.06 GB)
**Saída:** `DETRAN_CONSOLIDADO_JSON/` (JSONs estruturados por categoria)

## Estatísticas de processamento

- Total de tarefas: {len(resultados)}
- Sucessos: {master["total_sucesso"]} ({master["total_sucesso"]/len(resultados)*100:.1f}%)

### Por categoria

| Categoria | Total | Sucesso |
|-----------|-------|---------|
"""
for cat, s in sorted(master["por_categoria"].items()):
    md += f"| {cat} | {s['total']} | {s['sucesso']} |\n"

md += f"\n### Por método de extração\n\n| Método | Arquivos |\n|--------|----------|\n"
for metodo, n in sorted(master["por_metodo"].items(), key=lambda x: -x[1]):
    md += f"| {metodo} | {n} |\n"

md += f"""

## Estrutura de saída

```
DETRAN_CONSOLIDADO_JSON/
├── 01_CONTRATOS/*.json          (70 arquivos)
├── 02_EMPENHOS/*.json           (111 arquivos)
├── 03_FATURAS/*.json            (121 arquivos)
├── 05_ACEITES/*.json            (17 arquivos)
├── 06_COBRANCAS/*.json          (91 arquivos)
├── 07_SCRAPING_SPCF/*.json      (8 CSVs convertidos)
├── 08_PDFS_ORIGINAIS/*.json     (24 arquivos)
├── 09_RELATORIOS/*.json         (13 arquivos)
├── MASTER_DETRAN_CONSOLIDADO.json
└── RELATORIO_PIPELINE.md (este arquivo)
```

## Campos estruturados por tipo

### Contratos/Aditivos
- `clausula_11` (reajuste monetário)
- `clausula_objeto`
- `reajustes_pct`, `multas_pct`, `juros_pct_am`
- `indices_mencionados` (IGPM/IPCA/INPC/SELIC)
- `periodos_vigencia`

### Notas de Empenho
- `numero_ne`, `valor_empenho`
- `descricao`, `situacao`

### Faturas
- `numero_nfse`, `competencia`, `servico`

### Ofícios de Cobrança
- `oficio_numero`, `destinatario`
- `valor_cobrado_possivel`

### Certidões
- `tipo_cnd` (NEGATIVA/POSITIVA)
- `orgao` (FGTS/RFB/TST/CARTORIO_FALENCIA)

## Campos comuns (todos tipos)
- `cnpjs` — todos CNPJs encontrados
- `valores_brl` — todos valores R$
- `datas_encontradas` — todas datas DD/MM/YYYY
- `contratos_referenciados`
- `nes_referenciadas`
- `indices_mencionados`
- `texto_completo` — texto full-text para LLM
- `texto_preview` — primeiros 800 chars

## Uso por LLMs

Qualquer JSON contém texto completo + campos estruturados. LLMs podem:
1. Fazer RAG sobre `texto_completo`
2. Consultar campos específicos (`numero_ne`, `valor`, etc.)
3. Cruzar contratos → NEs → faturas via `contratos_referenciados`/`nes_referenciadas`
"""

(OUT / "RELATORIO_PIPELINE.md").write_text(md, encoding="utf-8")
print(f"\n[OK] MASTER_DETRAN_CONSOLIDADO.json e RELATORIO_PIPELINE.md gerados")
