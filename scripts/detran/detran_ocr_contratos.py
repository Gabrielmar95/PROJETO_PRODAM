"""
detran_ocr_contratos.py — Aplica OCR aos PDFs de contratos DETRAN que são imagens.

Usa pytesseract + pdf2image. Atualiza os JSONs existentes em DETRAN_CONTRATOS_JSON/
com o texto OCR extraído.

Executa em paralelo (4 workers) pra acelerar. Priorização:
  1. Contratos principais sem índice identificado
  2. Aditivos com "reajuste" no filename (mais importantes)
  3. Demais

Dependências: pytesseract 5.5, pdf2image, Pillow, poppler (via pdf2image).
"""
from __future__ import annotations
import sys, json, re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from logging_config import get_logger
_logger = get_logger(__name__)

ROOT = Path(__file__).parent.parent.parent
SRC = ROOT / "PRODAM_DOCS" / "DETRAN_CONSOLIDADO" / "01_CONTRATOS"
OUT = ROOT / "DETRAN_CONTRATOS_JSON"

# Tesseract config — português, OCR standard
TESS_CONFIG = "--psm 3 -l por"

# ============================================================
# Pega PDFs que precisam OCR (baseado nos JSONs já gerados)
# ============================================================
pdfs_a_ocr = []
for folder in OUT.iterdir():
    if not folder.is_dir(): continue
    for json_file in folder.glob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("pdf_meta", {}).get("tem_imagens_sem_texto"):
            pdf_path = SRC / Path(data["filename"]).name
            if pdf_path.exists():
                pdfs_a_ocr.append({
                    "pdf": pdf_path,
                    "json": json_file,
                    "filename": data["filename"],
                })

print(f"PDFs para OCR: {len(pdfs_a_ocr)}")

# Priorização
def prioridade(item):
    fn = item["filename"].lower()
    if "reajuste" in fn: return 0
    if re.search(r"^\d{2,3}\.\d{2,4}", fn) or "contrato principal" in fn: return 1
    return 2

pdfs_a_ocr.sort(key=prioridade)

# ============================================================
# Função OCR
# ============================================================
def ocr_pdf(pdf_path: Path) -> tuple[str, dict]:
    """Converte PDF em imagens e aplica Tesseract."""
    meta = {"metodo": "ocr_pytesseract", "paginas_ocr": 0, "paginas_total": 0}
    try:
        images = convert_from_path(str(pdf_path), dpi=200, grayscale=True)
        meta["paginas_total"] = len(images)
        textos = []
        for i, img in enumerate(images):
            texto = pytesseract.image_to_string(img, config=TESS_CONFIG)
            textos.append(texto)
            if texto.strip():
                meta["paginas_ocr"] += 1
        return "\n\n===PAGINA===\n\n".join(textos), meta
    except Exception as e:
        meta["erro"] = str(e)[:300]
        return "", meta

# ============================================================
# Parser de cláusulas (mesmo do script anterior, mais refinado para OCR)
# ============================================================
RE_CLAUSULAS_OCR = {
    "indice_correcao_contexto": re.compile(
        r"(reajust[ae].{0,500})", re.IGNORECASE | re.DOTALL
    ),
    "IGPM": re.compile(r"\bIGP-?M\b|\bIGPM\b", re.IGNORECASE),
    "IPCA": re.compile(r"\bIPCA\b", re.IGNORECASE),
    "INPC": re.compile(r"\bINPC\b", re.IGNORECASE),
    "SELIC": re.compile(r"\bSELIC\b", re.IGNORECASE),
    "valor_contrato": re.compile(
        r"(R\$\s*[\d.]+[,.]?\d*)", re.IGNORECASE
    ),
    "clausula_11": re.compile(
        r"cl[áa]usula\s+(?:d[ée]cima\s+primeira|11[°ªa]?|onze).{0,600}",
        re.IGNORECASE | re.DOTALL,
    ),
    "vigencia_datas": re.compile(
        r"(\d{1,2}/\d{1,2}/\d{2,4})\b.{0,100}?\b(\d{1,2}/\d{1,2}/\d{2,4})",
    ),
    "reajuste_percentual": re.compile(
        r"reajuste.{0,200}?(\d{1,2}[,.]?\d{1,3})\s*%", re.IGNORECASE | re.DOTALL
    ),
    "multa": re.compile(r"multa.{0,100}?(\d+[,.]?\d*)\s*%", re.IGNORECASE | re.DOTALL),
    "juros_mora": re.compile(
        r"juros.{0,100}?(\d+[,.]?\d*)\s*%\s*(?:a\.?\s*m\.?|ao\s+m[êe]s)",
        re.IGNORECASE | re.DOTALL,
    ),
    "cnpj": re.compile(r"(\d{2}[.\s]\d{3}[.\s]\d{3}[/\s]\d{4}[-\s]\d{2})"),
}

def parse_clausulas_ocr(texto: str) -> dict:
    resultado = {}
    # Indices detectados globalmente
    indices_presentes = []
    for idx in ("IGPM", "IPCA", "INPC", "SELIC"):
        if RE_CLAUSULAS_OCR[idx].search(texto):
            indices_presentes.append(idx)
    if indices_presentes:
        resultado["indices_presentes"] = indices_presentes

    # Contexto cláusula 11 (reajuste em contratos DETRAN)
    m = RE_CLAUSULAS_OCR["clausula_11"].search(texto)
    if m:
        resultado["clausula_11"] = m.group(0).strip()[:800]

    # Reajuste específico com %
    matches = RE_CLAUSULAS_OCR["reajuste_percentual"].findall(texto)
    if matches:
        resultado["reajustes_percentuais"] = [float(m.replace(",", ".")) for m in matches[:10]]

    # Contexto com índice
    m = RE_CLAUSULAS_OCR["indice_correcao_contexto"].search(texto)
    if m:
        ctx = m.group(1)[:500]
        resultado["contexto_reajuste"] = ctx

    # Vigência
    matches = RE_CLAUSULAS_OCR["vigencia_datas"].findall(texto)
    if matches:
        resultado["datas_vigencia"] = [list(t) for t in matches[:3]]

    # Multa
    matches = RE_CLAUSULAS_OCR["multa"].findall(texto)
    if matches:
        resultado["multas_pct"] = [float(m.replace(",", ".")) for m in matches[:5]]

    # Juros mora
    matches = RE_CLAUSULAS_OCR["juros_mora"].findall(texto)
    if matches:
        resultado["juros_mora_pct"] = [float(m.replace(",", ".")) for m in matches[:5]]

    # CNPJ
    matches = RE_CLAUSULAS_OCR["cnpj"].findall(texto)
    if matches:
        # dedupe
        resultado["cnpjs"] = list(dict.fromkeys(matches[:5]))

    # Valores R$
    matches = RE_CLAUSULAS_OCR["valor_contrato"].findall(texto)
    if matches:
        resultado["valores_detectados"] = list(dict.fromkeys(matches[:10]))

    return resultado

# ============================================================
# Processamento paralelo (4 workers)
# ============================================================
def processar_item(item: dict) -> dict:
    pdf = item["pdf"]
    json_path = item["json"]
    texto, meta = ocr_pdf(pdf)

    # Carrega JSON existente
    data = json.loads(json_path.read_text(encoding="utf-8"))

    # Atualiza com OCR
    data["ocr_texto_length"] = len(texto)
    data["ocr_texto_preview"] = texto[:800]
    data["ocr_texto_completo"] = texto
    data["pdf_meta"]["ocr"] = meta
    data["pdf_meta"]["metodo"] = meta["metodo"]
    data["pdf_meta"]["tem_imagens_sem_texto"] = False  # foi resolvido

    # Parse cláusulas do texto OCR
    if texto:
        clausulas_ocr = parse_clausulas_ocr(texto)
        data["clausulas_ocr"] = clausulas_ocr
        # Merge com cláusulas já detectadas
        if "clausulas_detectadas" in data:
            data["clausulas_detectadas"].update(clausulas_ocr)
        else:
            data["clausulas_detectadas"] = clausulas_ocr

    # Salva
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "filename": item["filename"],
        "paginas": meta.get("paginas_total", 0),
        "texto_len": len(texto),
        "indices": data.get("clausulas_ocr", {}).get("indices_presentes", []),
        "reajustes": data.get("clausulas_ocr", {}).get("reajustes_percentuais", []),
    }

# Processa em paralelo
print(f"\nIniciando OCR de {len(pdfs_a_ocr)} PDFs (4 workers paralelos)...")
resultados = []
completo = 0
with ThreadPoolExecutor(max_workers=4) as ex:
    futures = {ex.submit(processar_item, item): item for item in pdfs_a_ocr}
    for fut in as_completed(futures):
        completo += 1
        try:
            r = fut.result()
            resultados.append(r)
            indices = ",".join(r["indices"]) or "-"
            print(f"  [{completo}/{len(pdfs_a_ocr)}] {r['filename'][:55]:<55} {r['paginas']}pg | {indices}")
        except Exception as e:
            item = futures[fut]
            print(f"  [{completo}/{len(pdfs_a_ocr)}] ERRO {item['filename']}: {e}")

# ============================================================
# Regenera MASTER e INDICES com dados OCR
# ============================================================
print(f"\nRegenerando MASTER.json e INDICES_CORRECAO.json com OCR...")
all_data = []
for folder in OUT.iterdir():
    if not folder.is_dir(): continue
    for json_file in folder.glob("*.json"):
        try:
            all_data.append(json.loads(json_file.read_text(encoding="utf-8")))
        except Exception as exc: _logger.warning("JSON corrompido %s: %s", json_file.name, exc)

# Agrupa por contrato
from collections import defaultdict
por_contrato = defaultdict(list)
for d in all_data:
    ref = d.get("filename_parsed", {}).get("contrato_ref")
    if ref:
        por_contrato[ref].append(d)

# Rebuild MASTER
master = {"data": date.today().isoformat(), "total_pdfs": len(all_data), "total_contratos_unicos": len(por_contrato), "contratos": {}}
for ref, items in sorted(por_contrato.items()):
    # Coleta índices: filename + OCR
    indices_fn = set()
    indices_ocr = set()
    reajustes = []
    for i in items:
        idx_fn = i.get("filename_parsed", {}).get("indice")
        if idx_fn:
            indices_fn.add(idx_fn)
        idx_ocr = i.get("clausulas_ocr", {}).get("indices_presentes", [])
        for ii in idx_ocr:
            indices_ocr.add(ii)
        pct = i.get("filename_parsed", {}).get("percentual_reajuste")
        if pct:
            reajustes.append({
                "ta": i.get("filename_parsed", {}).get("ta_numero"),
                "indice": idx_fn,
                "pct": pct,
                "fonte": "filename",
                "arquivo": i.get("filename",""),
            })
        ocr_pcts = i.get("clausulas_ocr", {}).get("reajustes_percentuais", [])
        for p in ocr_pcts:
            reajustes.append({
                "ta": i.get("filename_parsed", {}).get("ta_numero"),
                "indice": (list(idx_ocr)[0] if idx_ocr else None),
                "pct": p,
                "fonte": "ocr_texto",
                "arquivo": i.get("filename",""),
            })

    master["contratos"][ref] = {
        "tem_principal": any(i.get("filename_parsed",{}).get("tipo") == "CONTRATO_PRINCIPAL" for i in items),
        "num_aditivos": sum(1 for i in items if i.get("filename_parsed",{}).get("tipo") == "TERMO_ADITIVO"),
        "indices_filename": sorted(indices_fn),
        "indices_ocr": sorted(indices_ocr),
        "reajustes_aplicados": reajustes,
        "total_documentos": len(items),
    }

json.dump(master, open(OUT / "MASTER.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"  MASTER.json regenerado")

# INDICES_CORRECAO.json
indices_master = {
    "data": date.today().isoformat(),
    "total_contratos": len(por_contrato),
    "por_contrato": {},
}
for ref, info in master["contratos"].items():
    todos_indices = set(info["indices_filename"]) | set(info["indices_ocr"])
    indice_principal = "IPCA" if "IPCA" in todos_indices else ("IGPM" if "IGPM" in todos_indices else (list(todos_indices)[0] if todos_indices else "DESCONHECIDO"))
    indices_master["por_contrato"][ref] = {
        "indice_principal": indice_principal,
        "indices_filename": info["indices_filename"],
        "indices_ocr": info["indices_ocr"],
        "reajustes": info["reajustes_aplicados"],
    }
json.dump(indices_master, open(OUT / "INDICES_CORRECAO.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"  INDICES_CORRECAO.json regenerado")

print(f"\n[FINAL] OCR completo. {len(resultados)} PDFs processados.")
indices_final = {}
for r in resultados:
    for idx in r["indices"]:
        indices_final[idx] = indices_final.get(idx, 0) + 1
print(f"Índices detectados no texto OCR: {indices_final}")
