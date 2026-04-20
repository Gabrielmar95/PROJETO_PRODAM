"""
detran_ocr_fase2.py — Aplica OCR aos PDFs marcados com precisa_ocr=True.

Atualiza os JSONs existentes em DETRAN_CONSOLIDADO_JSON/ adicionando:
  - ocr_texto (texto OCR)
  - pdf_meta.metodo_ocr
  - campos_estruturados_atualizados

Paralelismo: 6 workers.
"""
from __future__ import annotations
import sys, json, re, time
from pathlib import Path
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import pytesseract
from pdf2image import convert_from_path

OUT = ROOT / "DETRAN_CONSOLIDADO_JSON"
SRC = ROOT / "PRODAM_DOCS" / "DETRAN_CONSOLIDADO"
TESS_CONFIG = "--psm 3 -l por"

# Encontra JSONs que precisam OCR
pendentes = []
for folder in OUT.iterdir():
    if not folder.is_dir(): continue
    for jf in folder.glob("*.json"):
        try:
            d = json.loads(jf.read_text(encoding="utf-8"))
        except: continue
        if d.get("precisa_ocr") and d.get("texto_length",0) < 100:
            pdf_path = SRC / d["categoria"] / d["filename"]
            if pdf_path.exists():
                pendentes.append({"json": jf, "pdf": pdf_path, "data": d})

print(f"PDFs pendentes OCR: {len(pendentes)}")

RE_VALOR = re.compile(r"R\$\s*([\d.]+(?:[,.]\d{2})?)")
RE_DATA = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b")
RE_CNPJ = re.compile(r"\b(\d{2}[.\s]\d{3}[.\s]\d{3}[/\s]\d{4}[-\s]\d{2})\b")
RE_NE = re.compile(r"\b(\d{4}NE\d{4,7})\b", re.IGNORECASE)
RE_INDICES = {k: re.compile(rf"\b{k}\b", re.IGNORECASE) for k in ("IGPM","IGP-M","IPCA","INPC","SELIC")}

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

def ocr_worker(item):
    pdf = item["pdf"]
    jf = item["json"]
    data = item["data"]
    try:
        t0 = time.time()
        images = convert_from_path(str(pdf), dpi=200, grayscale=True)
        textos = [pytesseract.image_to_string(img, config=TESS_CONFIG) for img in images]
        texto_ocr = "\n\n===PAGINA===\n\n".join(textos)

        # Merge com texto existente
        data["ocr_texto"] = texto_ocr
        data["texto_completo"] = texto_ocr  # sobrescreve (vazio anterior)
        data["texto_preview"] = texto_ocr[:800]
        data["texto_length"] = len(texto_ocr)
        data["precisa_ocr"] = False
        data["pdf_meta"]["metodo"] = "ocr_tesseract_fase2"
        data["pdf_meta"]["paginas_ocr"] = len(images)
        data["pdf_meta"]["tempo_ocr_s"] = round(time.time() - t0, 1)

        # Re-parse campos
        campos_novos = parse_comum(texto_ocr)
        if "campos_estruturados" not in data:
            data["campos_estruturados"] = {}
        data["campos_estruturados"].update(campos_novos)

        jf.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return {"ok": True, "filename": pdf.name, "paginas": len(images), "tempo": round(time.time()-t0,1), "texto_len": len(texto_ocr)}
    except Exception as e:
        return {"ok": False, "filename": pdf.name, "erro": str(e)[:200]}

if not pendentes:
    print("Nada a fazer.")
    sys.exit(0)

inicio = time.time()
resultados = []
with ThreadPoolExecutor(max_workers=6) as ex:
    futures = {ex.submit(ocr_worker, it): it for it in pendentes}
    for i, fut in enumerate(as_completed(futures), 1):
        r = fut.result()
        resultados.append(r)
        if i % 10 == 0 or i == len(pendentes):
            elapsed = time.time() - inicio
            eta = elapsed/i * (len(pendentes)-i)
            ok = sum(1 for rr in resultados if rr.get("ok"))
            print(f"  [{i:3d}/{len(pendentes)}] {elapsed:.0f}s | ETA {eta:.0f}s | OK={ok}")

total_s = time.time() - inicio
ok = sum(1 for r in resultados if r.get("ok"))
print(f"\nOCR fase 2 concluído em {total_s:.0f}s ({total_s/60:.1f} min)")
print(f"Sucessos: {ok}/{len(pendentes)}")
