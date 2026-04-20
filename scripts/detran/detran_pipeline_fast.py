"""
detran_pipeline_fast.py — Versão rápida da pipeline.

Otimizações:
  - 8 workers (vs 4)
  - Fast-path: só PyMuPDF (sem OCR inicial)
  - OCR fica para fase 2 (arquivos que falharam no fast-path)
  - Skip JSONs já existentes
  - Progresso em tempo real

Estratégia: primeiro cobrir TODOS com extração rápida. OCR depois se preciso.
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
sys.path.insert(0, str(ROOT / "scripts"))
import fitz

SRC = ROOT / "PRODAM_DOCS" / "DETRAN_CONSOLIDADO"
OUT = ROOT / "DETRAN_CONSOLIDADO_JSON"
OUT.mkdir(exist_ok=True)

# Regex reusables
RE_VALOR = re.compile(r"R\$\s*([\d.]+(?:[,.]\d{2})?)")
RE_DATA = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b")
RE_CNPJ = re.compile(r"\b(\d{2}[.\s]\d{3}[.\s]\d{3}[/\s]\d{4}[-\s]\d{2})\b")
RE_NE = re.compile(r"\b(\d{4}NE\d{4,7})\b", re.IGNORECASE)
RE_CONTRATO = re.compile(r"\b(?:C(?:ontrato)?\.?\s*|CT\s*)?(\d{2,3})[./](\d{2,4})\b")
RE_INDICES = {k: re.compile(rf"\b{k}\b", re.IGNORECASE) for k in ("IGPM", "IGP-M", "IPCA", "INPC", "SELIC")}
RE_OFICIO = re.compile(r"\b(?:Of[íi]cio|OF\.?)\s*(?:Nº?|n\.?)?\s*(\d+[/\-.]?\d{2,4})", re.IGNORECASE)

def extrair_pymupdf(path: Path) -> tuple[str, dict]:
    meta = {"metodo": "pymupdf", "paginas": 0, "tem_texto": False}
    try:
        with fitz.open(str(path)) as doc:
            meta["paginas"] = len(doc)
            textos = [pg.get_text() for pg in doc]
            texto = "\n".join(textos)
            meta["tem_texto"] = len(texto.strip()) > 100
        return texto, meta
    except Exception as e:
        meta["erro"] = str(e)[:150]
        return "", meta

def parse_comum(texto: str) -> dict:
    out = {}
    cnpjs = list(dict.fromkeys(RE_CNPJ.findall(texto)))
    if cnpjs: out["cnpjs"] = cnpjs[:5]
    datas = list(dict.fromkeys(RE_DATA.findall(texto)))
    if datas: out["datas_encontradas"] = datas[:10]
    valores = RE_VALOR.findall(texto)
    if valores: out["valores_brl"] = list(dict.fromkeys(valores))[:15]
    nes = list(dict.fromkeys(m.group(1) for m in RE_NE.finditer(texto)))
    if nes: out["nes_referenciadas"] = nes[:15]
    indices = [k.replace("-","") for k,rx in RE_INDICES.items() if rx.search(texto)]
    if indices: out["indices_mencionados"] = list(dict.fromkeys(indices))
    return out

def parse_contrato(texto, filename):
    out = parse_comum(texto)
    out["tipo_doc"] = "TERMO_ADITIVO" if re.search(r"\d[°ºo]\s*TA|aditivo", filename, re.IGNORECASE) else "CONTRATO_PRINCIPAL"
    m = re.search(r"cl[áa]usula\s+(?:d[ée]cima\s+primeira|11[°ªa]?|onze).{0,600}", texto, re.IGNORECASE | re.DOTALL)
    if m: out["clausula_11"] = m.group(0)[:500]
    m = re.search(r"cl[áa]usula\s+primeira.{0,400}", texto, re.IGNORECASE | re.DOTALL)
    if m: out["clausula_objeto"] = m.group(0)[:350]
    pcts = re.findall(r"(?:reajuste|atualiza).{0,80}?(\d{1,2}[,.]?\d{1,3})\s*%", texto, re.IGNORECASE | re.DOTALL)
    if pcts: out["reajustes_pct"] = [float(p.replace(",",".")) for p in pcts[:5]]
    return out

def parse_empenho(texto, filename):
    out = parse_comum(texto)
    out["tipo_doc"] = "NOTA_EMPENHO"
    m = re.search(r"(\d{4}NE\d+)", texto, re.IGNORECASE)
    if m: out["numero_ne"] = m.group(1)
    m = re.search(r"Descri[çc][ãa]o[:\s]+(.+?)(?:\n\s*\n|Situa|Evento)", texto, re.IGNORECASE | re.DOTALL)
    if m: out["descricao"] = m.group(1).strip()[:400]
    return out

def parse_fatura(texto, filename):
    out = parse_comum(texto)
    out["tipo_doc"] = "FATURA"
    m = re.search(r"Compet[êe]ncia[:\s]+(\d{1,2}/\d{4})", texto, re.IGNORECASE)
    if m: out["competencia"] = m.group(1)
    m = re.search(r"NFS?[e\-]?\s*(?:Nº|n\.?)?\s*(\d{4,7})", texto, re.IGNORECASE)
    if m: out["numero_nfse"] = m.group(1)
    return out

def parse_aceite(texto, filename):
    out = parse_comum(texto)
    out["tipo_doc"] = "ACEITE_TECNICO"
    return out

def parse_cobranca(texto, filename):
    out = parse_comum(texto)
    out["tipo_doc"] = "OFICIO_COBRANCA"
    m = RE_OFICIO.search(texto)
    if m: out["oficio_numero"] = m.group(1)
    return out

def parse_certidao(texto, filename):
    out = parse_comum(texto)
    out["tipo_doc"] = "CERTIDAO"
    if "negativa" in texto.lower(): out["tipo_cnd"] = "NEGATIVA"
    elif "positiva" in texto.lower(): out["tipo_cnd"] = "POSITIVA"
    return out

def parse_rel(texto, filename):
    out = parse_comum(texto)
    out["tipo_doc"] = "RELATORIO"
    return out

PARSERS = {
    "01_CONTRATOS": parse_contrato,
    "02_EMPENHOS": parse_empenho,
    "03_FATURAS": parse_fatura,
    "05_ACEITES": parse_aceite,
    "06_COBRANCAS": parse_cobranca,
    "08_PDFS_ORIGINAIS": parse_certidao,
    "09_RELATORIOS": parse_rel,
}

def safe_filename(name): return re.sub(r"[^\w.-]", "_", name)

def processar_pdf(pdf, folder, parser_fn, json_out):
    if json_out.exists() and json_out.stat().st_size > 500:
        return {"ok": True, "skip": True, "filename": pdf.name, "folder": folder}
    try:
        texto, meta = extrair_pymupdf(pdf)
        precisa_ocr = not meta.get("tem_texto")
        campos = parser_fn(texto, pdf.name) if texto else {}
        data = {
            "filename": pdf.name,
            "path": str(pdf.relative_to(ROOT)),
            "categoria": folder,
            "data_extracao": date.today().isoformat(),
            "tamanho_bytes": pdf.stat().st_size,
            "texto_length": len(texto),
            "texto_preview": texto[:800],
            "texto_completo": texto,
            "pdf_meta": meta,
            "precisa_ocr": precisa_ocr,
            "campos_estruturados": campos,
        }
        json_out.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return {"ok": True, "filename": pdf.name, "folder": folder, "precisa_ocr": precisa_ocr, "paginas": meta["paginas"]}
    except Exception as e:
        return {"ok": False, "filename": pdf.name, "folder": folder, "erro": str(e)[:150]}

def processar_csv(csv_path, json_out):
    if json_out.exists():
        return {"ok": True, "skip": True, "filename": csv_path.name, "folder": "07_SCRAPING_SPCF"}
    try:
        rows = []
        with open(csv_path, encoding="utf-8", errors="ignore") as f:
            try: rows = list(csv.DictReader(f, delimiter=";"))
            except: pass
        if not rows:
            with open(csv_path, encoding="utf-8", errors="ignore") as f:
                rows = list(csv.DictReader(f))
        data = {
            "filename": csv_path.name,
            "tipo_doc": "CSV_SPCF",
            "categoria": "07_SCRAPING_SPCF",
            "total_linhas": len(rows),
            "campos": list(rows[0].keys()) if rows else [],
            "amostra_5_linhas": rows[:5],
            "dados_completos": rows,
        }
        json_out.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return {"ok": True, "filename": csv_path.name, "folder": "07_SCRAPING_SPCF"}
    except Exception as e:
        return {"ok": False, "filename": csv_path.name, "erro": str(e)[:150]}

# =========================================================
# Coleta tarefas
# =========================================================
tarefas = []
for folder_name, parser_fn in PARSERS.items():
    folder = SRC / folder_name
    if not folder.exists(): continue
    out_folder = OUT / folder_name
    out_folder.mkdir(exist_ok=True)
    for pdf in folder.glob("*.pdf"):
        json_out = out_folder / (safe_filename(pdf.stem) + ".json")
        tarefas.append(("pdf", pdf, folder_name, parser_fn, json_out))

csv_folder = SRC / "07_SCRAPING_SPCF"
if csv_folder.exists():
    out_csv_folder = OUT / "07_SCRAPING_SPCF"
    out_csv_folder.mkdir(exist_ok=True)
    for csv_path in csv_folder.glob("*.csv"):
        json_out = out_csv_folder / (csv_path.stem + ".json")
        tarefas.append(("csv", csv_path, "07_SCRAPING_SPCF", None, json_out))

# Excluir já processados
total_inicial = len(tarefas)
tarefas_novas = [t for t in tarefas if not (t[4].exists() and t[4].stat().st_size > 500)]
print(f"Tarefas totais: {total_inicial} | Já processadas: {total_inicial-len(tarefas_novas)} | Pendentes: {len(tarefas_novas)}")

# =========================================================
# Processamento paralelo
# =========================================================
def worker(t):
    kind = t[0]
    if kind == "pdf":
        _, pdf, folder, parser_fn, json_out = t
        return processar_pdf(pdf, folder, parser_fn, json_out)
    else:
        _, csv_path, folder, _, json_out = t
        return processar_csv(csv_path, json_out)

inicio = time.time()
resultados = []
precisam_ocr = []
with ThreadPoolExecutor(max_workers=8) as ex:
    futures = {ex.submit(worker, t): t for t in tarefas_novas}
    for i, fut in enumerate(as_completed(futures), 1):
        r = fut.result()
        resultados.append(r)
        if r.get("precisa_ocr"):
            precisam_ocr.append(r["filename"])
        if i % 25 == 0 or i == len(tarefas_novas):
            elapsed = time.time() - inicio
            eta = elapsed/i * (len(tarefas_novas)-i)
            print(f"  [{i:3d}/{len(tarefas_novas)}] {elapsed:.0f}s | ETA {eta:.0f}s")

print(f"\nFast-path concluído em {time.time()-inicio:.0f}s")
print(f"  Sucessos: {sum(1 for r in resultados if r.get('ok'))}")
print(f"  Precisam OCR: {len(precisam_ocr)}")

# =========================================================
# Gera MASTER atualizado
# =========================================================
all_jsons = []
for folder in OUT.iterdir():
    if folder.is_dir():
        for jf in folder.glob("*.json"):
            try: all_jsons.append(json.loads(jf.read_text(encoding="utf-8")))
            except: pass

master = {
    "data": date.today().isoformat(),
    "total_arquivos": len(all_jsons),
    "por_categoria": defaultdict(int),
    "precisam_ocr": [d["filename"] for d in all_jsons if d.get("precisa_ocr")],
    "por_tipo_doc": defaultdict(int),
    "indices_agregados": defaultdict(int),
}
for d in all_jsons:
    master["por_categoria"][d.get("categoria","?")] += 1
    master["por_tipo_doc"][d.get("campos_estruturados",{}).get("tipo_doc") or d.get("tipo_doc","?")] += 1
    for idx in d.get("campos_estruturados",{}).get("indices_mencionados",[]):
        master["indices_agregados"][idx] += 1

master["por_categoria"] = dict(master["por_categoria"])
master["por_tipo_doc"] = dict(master["por_tipo_doc"])
master["indices_agregados"] = dict(master["indices_agregados"])

json.dump(master, open(OUT / "MASTER_DETRAN_CONSOLIDADO.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
print(f"\n[MASTER] {master['total_arquivos']} JSONs indexados")
print(f"  Por categoria: {master['por_categoria']}")
print(f"  Por tipo: {master['por_tipo_doc']}")
print(f"  Índices agregados: {master['indices_agregados']}")
print(f"  Precisam OCR (fase 2): {len(master['precisam_ocr'])}")

# Lista de OCR pendentes
if master['precisam_ocr']:
    with open(OUT / "PDFS_PRECISAM_OCR.txt", "w", encoding="utf-8") as f:
        for fn in master['precisam_ocr']:
            f.write(fn + "\n")
    print(f"  Lista salva em: PDFS_PRECISAM_OCR.txt")
