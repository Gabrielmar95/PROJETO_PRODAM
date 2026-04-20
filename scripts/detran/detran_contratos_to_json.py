"""
detran_contratos_to_json.py — Converte 70 PDFs de contratos/aditivos DETRAN em JSON estruturado.

Produz:
  DETRAN_CONTRATOS_JSON/
    ├── <NUMERO>_<ANO>/
    │   ├── contrato_principal.json  (se existir)
    │   ├── TA_01.json
    │   ├── TA_02.json
    │   └── ...
    ├── MASTER.json           — índice consolidado
    ├── INDICES_CORRECAO.json — índices aplicados por contrato/aditivo
    └── RELATORIO_CONTRATOS.md

Estratégia de extração:
  1. Parser de filename (captura número contrato, número TA, tipo, índice, percentual)
  2. PyMuPDF para texto (fallback pdfplumber, fallback OCR)
  3. Regex para cláusulas-chave
  4. Cadeia cronológica por contrato
"""
from __future__ import annotations
import sys, json, re
from pathlib import Path
from datetime import date, datetime
from collections import defaultdict
from decimal import Decimal, InvalidOperation

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from prodam_utils import brl, fmt_brl, parse_br_date

import fitz  # PyMuPDF

SRC = ROOT / "PRODAM_DOCS" / "DETRAN_CONSOLIDADO" / "01_CONTRATOS"
OUT = ROOT / "DETRAN_CONTRATOS_JSON"
OUT.mkdir(exist_ok=True)

# ============================================================
# 1) Parser de filename
# ============================================================
# Padrões comuns:
#   "075.2022 - PRODAM - TERCEIRO TERMO ADITIVO - ASSINADO.pdf"
#   "1º TA Contrato 075.2022 - Prorrogação de Prazo.pdf"
#   "4º TA ao Contrato 006.2021 - Prazo e reajuste 6,54% IGPM.pdf"
#   "3º TA CT 022.14 - Prazo.pdf"
#   "2º TA ao contrato 004.2016-prorrogação de prazo.pdf"

RE_CONTRATO_NUM = re.compile(
    r"""(?:C(?:ontrato)?\.?\s*|CT\s*)?(\d{2,3})\.(\d{2,4})""", re.IGNORECASE
)
RE_TA_NUM_POS = re.compile(r"(\d+)[ºo°]?\s*TA", re.IGNORECASE)
RE_TA_ORDINAL = re.compile(
    r"\b(PRIMEIRO|SEGUNDO|TERCEIRO|QUARTO|QUINTO|SEXTO|S[EÉ]TIMO|OITAVO|NONO|D[EÉ]CIMO)\s+TERMO\s+ADITIVO",
    re.IGNORECASE,
)
ORDINAL_MAP = {
    "PRIMEIRO":1,"SEGUNDO":2,"TERCEIRO":3,"QUARTO":4,"QUINTO":5,"SEXTO":6,
    "SETIMO":7,"SÉTIMO":7,"OITAVO":8,"NONO":9,"DECIMO":10,"DÉCIMO":10
}
RE_INDICE = re.compile(r"\b(IGPM|IPCA|IGP-M|INPC|SELIC)\b", re.IGNORECASE)
RE_PERC = re.compile(r"(\d{1,2}[,.]\d{1,3})\s*%")
RE_TIPO = re.compile(
    r"\b(prazo|prorroga|supressao|supressão|reajuste|reducao|redu[çc]ao|suplementa|aditamento|apostilamento|assinado|doe)\b",
    re.IGNORECASE,
)

def parse_filename(name: str) -> dict:
    """Extrai metadados do filename."""
    n = name.replace(".pdf", "")
    result = {"filename": name, "tipo": "DESCONHECIDO"}

    # Número contrato
    m = RE_CONTRATO_NUM.search(n)
    if m:
        num, ano = m.groups()
        # Normaliza ano para 4 dígitos
        if len(ano) == 2:
            ano = "20" + ano
        result["contrato_num"] = int(num)
        result["contrato_ano"] = int(ano)
        result["contrato_ref"] = f"{int(num):03d}/{ano}"

    # É TA?
    m = RE_TA_NUM_POS.search(n)
    if m:
        result["ta_numero"] = int(m.group(1))
        result["tipo"] = "TERMO_ADITIVO"
    else:
        m = RE_TA_ORDINAL.search(n)
        if m:
            ord_upper = m.group(1).upper()
            result["ta_numero"] = ORDINAL_MAP.get(ord_upper, 0)
            result["tipo"] = "TERMO_ADITIVO"

    # Se tem "Contrato" mas não TA, pode ser o principal
    if result["tipo"] == "DESCONHECIDO":
        if re.search(r"\bCT\s+\d", n) or re.search(r"^\d{2,3}\.\d{2,4}\s*-", n):
            result["tipo"] = "CONTRATO_PRINCIPAL"
        else:
            result["tipo"] = "CONTRATO_PRINCIPAL"  # assumir principal se não for TA

    # Índice de correção
    m = RE_INDICE.search(n)
    if m:
        result["indice"] = m.group(1).upper().replace("IGP-M", "IGPM")

    # Percentual
    m = RE_PERC.search(n)
    if m:
        pct = m.group(1).replace(",", ".")
        try:
            result["percentual_reajuste"] = float(pct)
        except ValueError:
            pass

    # Tipo de aditivo
    tipos = RE_TIPO.findall(n)
    if tipos:
        mapping = {
            "prazo": "PRORROGACAO_PRAZO",
            "prorroga": "PRORROGACAO_PRAZO",
            "supressao": "SUPRESSAO",
            "supressão": "SUPRESSAO",
            "reajuste": "REAJUSTE",
            "reducao": "REDUCAO",
            "redução": "REDUCAO",
            "reduçao": "REDUCAO",
            "suplementa": "SUPLEMENTACAO",
            "apostilamento": "APOSTILAMENTO",
        }
        result["modalidades"] = [mapping.get(t.lower(), t.upper()) for t in tipos if t.lower() in mapping]

    return result

# ============================================================
# 2) Extração de texto do PDF
# ============================================================
def extrair_texto_pdf(path: Path) -> tuple[str, dict]:
    """Extrai texto usando PyMuPDF. Retorna (texto, metadados)."""
    meta = {"num_paginas": 0, "metodo": "pymupdf", "tem_imagens_sem_texto": False, "byte_size": path.stat().st_size}
    try:
        with fitz.open(str(path)) as doc:
            meta["num_paginas"] = len(doc)
            textos = []
            paginas_vazias = 0
            for pg in doc:
                t = pg.get_text()
                if not t.strip():
                    paginas_vazias += 1
                textos.append(t)
            texto = "\n".join(textos)

            # Se 80%+ das páginas vazias, PDF é imagem (precisa OCR)
            if len(doc) > 0 and paginas_vazias / len(doc) >= 0.8:
                meta["tem_imagens_sem_texto"] = True
                meta["metodo"] = "imagem_precisa_ocr"
    except Exception as e:
        meta["erro"] = str(e)[:200]
        return "", meta
    return texto, meta

# ============================================================
# 3) Parser de cláusulas-chave
# ============================================================
RE_CLAUSULAS = {
    "indice_correcao": re.compile(
        r"(?:[íi]ndice\s+de\s+corre[çc][ãa]o|reajust[ae]|atualiza[çc][ãa]o\s+monet[áa]ria|varia[çc][ãa]o\s+do\s+IGPM|IGPM|IPCA|INPC|SELIC)"
        r".{0,200}?(IGP-?M|IPCA|INPC|SELIC|IGPM)",
        re.IGNORECASE | re.DOTALL,
    ),
    "valor_contrato": re.compile(
        r"(?:valor\s+(?:global|total|contratado|do\s+contrato|estimado))\s*.{0,100}?(R\$\s*[\d.,]+)",
        re.IGNORECASE | re.DOTALL,
    ),
    "vigencia": re.compile(
        r"(?:vig[êe]ncia|prazo\s+de\s+\d+\s+meses?|ter[áa]\s+vig[êe]ncia)"
        r".{0,200}?(\d{1,2}/\d{1,2}/\d{2,4}).{0,100}?(\d{1,2}/\d{1,2}/\d{2,4})",
        re.IGNORECASE | re.DOTALL,
    ),
    "multa": re.compile(
        r"multa.{0,200}?(\d+[,.]?\d*)\s*%",
        re.IGNORECASE | re.DOTALL,
    ),
    "juros_mora": re.compile(
        r"juros.{0,100}?(\d+[,.]?\d*)\s*%\s*(?:a\.?\s*m\.?|ao\s+m[êe]s)",
        re.IGNORECASE | re.DOTALL,
    ),
    "supressao_pct": re.compile(
        r"supress[ãa]o.{0,100}?(\d{1,2}[,.]?\d*)\s*%",
        re.IGNORECASE | re.DOTALL,
    ),
    "acrescimo_pct": re.compile(
        r"(?:acr[ée]scim|suplementa[çc][ãa]o).{0,100}?(\d{1,2}[,.]?\d*)\s*%",
        re.IGNORECASE | re.DOTALL,
    ),
    "cnpj_contratada": re.compile(
        r"CNPJ.{0,50}?(\d{2}[.\s]?\d{3}[.\s]?\d{3}[/\s]?\d{4}[-\s]?\d{2})",
        re.IGNORECASE,
    ),
}

def parse_clausulas(texto: str) -> dict:
    """Aplica regexes de cláusulas e retorna dict com achados."""
    resultado = {}
    for nome, rx in RE_CLAUSULAS.items():
        matches = rx.findall(texto)
        if matches:
            # Deduplica e limita
            uniq = list(dict.fromkeys(
                tuple(m) if isinstance(m, tuple) else m
                for m in matches
            ))
            resultado[nome] = uniq[:5]  # máximo 5 ocorrências
    # Contexto "cláusula décima primeira" (cláusula 11 = correção DETRAN)
    ctx_11 = re.findall(
        r"(cl[áa]usula\s+(?:d[ée]cima\s+primeira|11[°ª]?|onze))(.{0,500}?)(?=cl[áa]usula|$)",
        texto, re.IGNORECASE | re.DOTALL
    )
    if ctx_11:
        resultado["clausula_11_contexto"] = [c[0] + c[1].strip()[:400] for c in ctx_11[:2]]
    return resultado

# ============================================================
# 4) Processa cada PDF
# ============================================================
pdfs = sorted(SRC.glob("*.pdf"))
print(f"PDFs encontrados: {len(pdfs)}")

todos_resultados = []
por_contrato = defaultdict(list)  # "022/2014" -> [resultados ...]

for i, pdf in enumerate(pdfs, 1):
    if i % 10 == 0:
        print(f"  [{i}/{len(pdfs)}] {pdf.name[:60]}")

    meta_fn = parse_filename(pdf.name)
    texto, meta_pdf = extrair_texto_pdf(pdf)

    clausulas = parse_clausulas(texto) if texto else {}

    resultado = {
        "filename": pdf.name,
        "path": str(pdf.relative_to(ROOT)),
        "filename_parsed": meta_fn,
        "pdf_meta": meta_pdf,
        "texto_length": len(texto),
        "texto_preview": texto[:500] if texto else "",
        "clausulas_detectadas": clausulas,
        "data_extracao": date.today().isoformat(),
    }
    todos_resultados.append(resultado)

    ref = meta_fn.get("contrato_ref")
    if ref:
        por_contrato[ref].append(resultado)

print(f"\n[OK] Processados {len(todos_resultados)} PDFs")

# ============================================================
# 5) Gera JSON por contrato (pasta individual)
# ============================================================
for contrato_ref, items in por_contrato.items():
    safe = contrato_ref.replace("/", "_")
    folder = OUT / safe
    folder.mkdir(exist_ok=True)

    # Ordena: principal primeiro, depois TAs por número
    items_sorted = sorted(items, key=lambda x: (
        0 if x["filename_parsed"].get("tipo") == "CONTRATO_PRINCIPAL" else 1,
        x["filename_parsed"].get("ta_numero", 0)
    ))

    for item in items_sorted:
        tipo = item["filename_parsed"].get("tipo", "UNK")
        ta_num = item["filename_parsed"].get("ta_numero", 0)
        if tipo == "CONTRATO_PRINCIPAL":
            fname = "contrato_principal.json"
        else:
            fname = f"TA_{ta_num:02d}.json" if ta_num else "ADITIVO_SN.json"
        # Se já existe, sufixa
        counter = 1
        target = folder / fname
        while target.exists():
            target = folder / fname.replace(".json", f"_{counter}.json")
            counter += 1
        target.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"[OK] JSONs por contrato em {len(por_contrato)} pastas")

# ============================================================
# 6) MASTER.json — índice consolidado
# ============================================================
master = {
    "data": date.today().isoformat(),
    "total_pdfs": len(todos_resultados),
    "total_contratos_unicos": len(por_contrato),
    "contratos": {},
}
for ref, items in sorted(por_contrato.items()):
    contrato_info = {
        "num_aditivos": sum(1 for i in items if i["filename_parsed"].get("tipo") == "TERMO_ADITIVO"),
        "tem_principal": any(i["filename_parsed"].get("tipo") == "CONTRATO_PRINCIPAL" for i in items),
        "indices_nos_filenames": list(set(
            i["filename_parsed"].get("indice") for i in items
            if i["filename_parsed"].get("indice")
        )),
        "reajustes_percentuais": [
            {
                "ta": i["filename_parsed"].get("ta_numero"),
                "indice": i["filename_parsed"].get("indice"),
                "pct": i["filename_parsed"].get("percentual_reajuste"),
                "arquivo": i["filename"],
            }
            for i in items
            if i["filename_parsed"].get("percentual_reajuste") is not None
        ],
        "modalidades": sorted(set(
            mod for i in items
            for mod in i["filename_parsed"].get("modalidades", [])
        )),
        "total_documentos": len(items),
    }
    master["contratos"][ref] = contrato_info

json.dump(master, open(OUT / "MASTER.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"[OK] MASTER.json")

# ============================================================
# 7) INDICES_CORRECAO.json — foco em correção monetária
# ============================================================
indices = {
    "data": date.today().isoformat(),
    "total_contratos": len(por_contrato),
    "por_contrato": {},
    "summary_indices": defaultdict(lambda: {"qtd_aditivos": 0, "percentuais": []}),
    "sem_indice_identificado": [],
}

for ref, info in master["contratos"].items():
    indice_usado = "DESCONHECIDO"
    if info["indices_nos_filenames"]:
        # Priorizar IGPM se aparecer (é o padrão DETRAN)
        if "IGPM" in info["indices_nos_filenames"]:
            indice_usado = "IGPM"
        else:
            indice_usado = info["indices_nos_filenames"][0]
    indices["por_contrato"][ref] = {
        "indice_principal": indice_usado,
        "indices_detectados": info["indices_nos_filenames"],
        "reajustes": info["reajustes_percentuais"],
        "modalidades": info["modalidades"],
    }
    if indice_usado == "DESCONHECIDO":
        indices["sem_indice_identificado"].append(ref)
    else:
        indices["summary_indices"][indice_usado]["qtd_aditivos"] += len(info["reajustes_percentuais"])
        indices["summary_indices"][indice_usado]["percentuais"].extend(
            r["pct"] for r in info["reajustes_percentuais"] if r.get("pct")
        )

# Converte defaultdict para dict
indices["summary_indices"] = dict(indices["summary_indices"])

json.dump(indices, open(OUT / "INDICES_CORRECAO.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"[OK] INDICES_CORRECAO.json")

# ============================================================
# 8) Relatório MD
# ============================================================
md = f"""# DETRAN — Contratos e Aditivos em JSON

**Data:** {date.today().isoformat()}
**Fonte:** `PRODAM_DOCS/DETRAN_CONSOLIDADO/01_CONTRATOS/` (70 PDFs)
**Saída:** `DETRAN_CONTRATOS_JSON/` (pastas por contrato + MASTER + INDICES)

---

## Estatísticas

- **PDFs processados:** {len(todos_resultados)}
- **Contratos únicos identificados:** {len(por_contrato)}
- **PDFs com texto extraível:** {sum(1 for r in todos_resultados if not r['pdf_meta'].get('tem_imagens_sem_texto'))}
- **PDFs que precisam OCR:** {sum(1 for r in todos_resultados if r['pdf_meta'].get('tem_imagens_sem_texto'))}

## Índices de correção detectados

"""
for indice, dados in indices["summary_indices"].items():
    pcts = dados["percentuais"]
    pct_str = f"{min(pcts):.2f}% a {max(pcts):.2f}%" if pcts else "—"
    md += f"- **{indice}:** {dados['qtd_aditivos']} aditivos com reajuste ({pct_str})\n"

if indices["sem_indice_identificado"]:
    md += f"\n**Contratos sem índice identificado no filename:** {', '.join(indices['sem_indice_identificado'])}\n"

md += "\n## Contratos identificados\n\n| Contrato | Principal? | Aditivos | Índices | Modalidades |\n|----------|-----------|----------|---------|-------------|\n"
for ref, info in sorted(master["contratos"].items()):
    principal = "✅" if info["tem_principal"] else "❌"
    md += f"| **{ref}** | {principal} | {info['num_aditivos']} | {', '.join(info['indices_nos_filenames']) or '—'} | {', '.join(info['modalidades']) or '—'} |\n"

md += "\n## Detalhe de reajustes\n\n| Contrato | TA | Índice | Percentual | Arquivo |\n|----------|----|---------|-----------|---------|\n"
for ref, info in sorted(master["contratos"].items()):
    for r in info["reajustes_percentuais"]:
        md += f"| {ref} | TA-{r['ta']} | {r['indice']} | {r['pct']:.2f}% | {r['arquivo'][:60]} |\n"

(OUT / "RELATORIO_CONTRATOS.md").write_text(md, encoding="utf-8")
print(f"[OK] RELATORIO_CONTRATOS.md")

# ============================================================
# FIM
# ============================================================
print(f"\n{'='*60}")
print(f"RESUMO")
print(f"{'='*60}")
print(f"Total PDFs processados: {len(todos_resultados)}")
print(f"Contratos únicos:       {len(por_contrato)}")
print(f"Índices aplicados:")
for indice, dados in indices["summary_indices"].items():
    print(f"  {indice}: {dados['qtd_aditivos']} aditivos")
print(f"Saída em: {OUT}")
