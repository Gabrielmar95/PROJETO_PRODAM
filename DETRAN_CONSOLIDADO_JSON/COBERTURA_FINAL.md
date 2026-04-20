# DETRAN_CONSOLIDADO → JSON — COBERTURA 99,8%

**Data:** 14/04/2026 | **Pipeline:** Multi-formato (8 tipos suportados)

---

## 🎯 Resultado Final

| Categoria | Fonte | JSONs | % | Formatos |
|-----------|-------|-------|---|----------|
| 01_CONTRATOS | 70 | **70** | 100% | pdf |
| 02_EMPENHOS | 111 | **111** | 100% | pdf |
| 03_FATURAS | 121 | **121** | 100% | pdf |
| 04_NOTAS_LIQUIDACAO | 0 | — | — | (vazia) |
| 05_ACEITES | 17 | **17** | 100% | pdf |
| **06_COBRANCAS** | 91 | **90** | **99%** | pdf + docx + xls + png |
| 07_SCRAPING_SPCF | 8 | **8** | 100% | csv → json |
| 08_PDFS_ORIGINAIS | 24 | **24** | 100% | pdf |
| **09_RELATORIOS** | 13 | **13** | **100%** | md + html + xlsx + py + json + pdf |
| **TOTAL** | **455** | **454** | **99,8%** | 10 formatos |

**Único arquivo não processado:** `Thumbs.db` (metadata de thumbnail do Windows — sem conteúdo útil).

---

## 📦 Tipos de arquivo processados

| Formato | Qtd | Lib usada |
|---------|-----|-----------|
| .pdf | 424 | PyMuPDF + Tesseract (OCR) |
| .csv | 8 | csv stdlib |
| .docx | 8 | python-docx |
| .py | 4 | texto direto + regex (funções/classes/imports) |
| .md | 3 | texto direto + regex (headers) |
| .html | 2 | BeautifulSoup 4 |
| .xlsx | 2 | openpyxl (todas abas) |
| .xls | 1 | xlrd |
| .png | 1 | pytesseract OCR |
| .json | 1 | json stdlib |
| **TOTAL** | **454** | **9 libs** |

---

## 🆕 Novos JSONs gerados nesta rodada (22 arquivos)

### 06_COBRANCAS (10 arquivos não-PDF)

| Arquivo | Tipo | Origem |
|---------|------|--------|
| 194.DETRAN - Cobrança Financeira.docx | DOCX | Word editável |
| 197.PRESI - DETRAN-ITRANSITO.docx | DOCX | Word editável |
| Captura de tela 2025-08-14 101346.png | IMAGEM_OCR | Screenshot OCR |
| Carta Circular nº 01-2025.docx | DOCX | Comunicação oficial |
| Carta Circular nº 02-2025.docx | DOCX | Comunicação oficial |
| Carta Circular nº 02-2025 (DETRAN-CPA).docx | DOCX | Carta CPA |
| Carta Circular nº 03-2025.docx | DOCX | Comunicação oficial |
| Minuta de Carta DAF ao DETRAN.docx | DOCX | Minuta |
| PRESI xxx.DETRAN - Cobrança Financeira.docx | DOCX | Word |
| relatorio - 2025-11-27 - Faturas até dezembro.xls | PLANILHA | XLS antigo |

### 09_RELATORIOS (13 arquivos)

| Arquivo | Tipo | Conteúdo |
|---------|------|----------|
| AUDITORIA_DETRAN.xlsx | PLANILHA | Auditoria em 7 abas |
| AUDITORIA_DETRAN_COMPLETA.html | HTML_RELATORIO | Relatório visual |
| AUDITORIA_DETRAN_COMPLETA.md | MARKDOWN | Relatório textual |
| AUDITORIA_DETRAN_COMPLETA__1a4babf63a.md | MARKDOWN | Versão com hash |
| AUDITORIA_DETRAN__5c396e3d98.xlsx | PLANILHA | Versão com hash |
| AUDITORIA_DETRAN_COMPLETA.pdf | PDF | Relatório imprimível |
| README.md | MARKDOWN | Documentação da pasta |
| consolidar_detran.py | SCRIPT_PYTHON | Script de consolidação |
| dados_completos.json | JSON_DADOS | Dump bruto |
| dashboard.html | HTML_RELATORIO | Dashboard Chart.js |
| dossie_detran.py | SCRIPT_PYTHON | Script dossiê |
| dossie_detran__e7060af66b.py | SCRIPT_PYTHON | Versão |
| organizar_detran.py | SCRIPT_PYTHON | Script organização |

---

## 📋 Cada JSON tem

```json
{
  "filename": "AUDITORIA_DETRAN_COMPLETA.md",
  "path": "...",
  "categoria": "09_RELATORIOS",
  "extensao": ".md",
  "tipo_doc": "MARKDOWN",
  "tamanho_bytes": 45678,
  "metodo": "texto_direto",
  "texto_preview": "...",
  "texto_completo": "...",
  "texto_length": 12345,

  // Específico por tipo:
  "num_headers": 42,
  "titulos": ["Introdução", "Análise", ...],
  "num_funcoes": 15 (se .py),
  "funcoes": ["calc_correcao", "atualizar_ne", ...],
  "num_abas": 7 (se .xlsx),
  "abas": {"Inventario": {...}, "NEs": {...}, ...},
  "num_tabelas": 5 (se .docx/.html),
  "tabelas": [[["Header1","Header2"],[...]],...],

  "campos_estruturados": {
    "cnpjs": ["04.224.028/0001-63"],
    "datas_encontradas": [...],
    "valores_brl": [...],
    "nes_referenciadas": [...],
    "indices_mencionados": ["IGPM"]
  }
}
```

---

## 🔍 Consultas Python

### Todos relatórios com IGPM
```python
import json
from pathlib import Path
O = Path("DETRAN_CONSOLIDADO_JSON/09_RELATORIOS")
for f in O.glob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    if "IGPM" in (d.get("campos_estruturados",{}).get("indices_mencionados",[])):
        print(d["filename"], "→", d["texto_preview"][:100])
```

### Extrair tabela de auditoria xlsx
```python
d = json.load(open("DETRAN_CONSOLIDADO_JSON/09_RELATORIOS/AUDITORIA_DETRAN.json"))
for aba_nome, aba_data in d["abas"].items():
    print(f"Aba {aba_nome}: {aba_data['total_linhas']} linhas")
    print(aba_data["amostra"][:3])
```

### Conteúdo de uma carta circular
```python
d = json.load(open("DETRAN_CONSOLIDADO_JSON/06_COBRANCAS/Carta_Circular_n__01-2025___DAF_-_GEFIN__DETRAN__docx.json"))
print(d["texto_completo"])
print("Tabelas:", d["num_tabelas"])
```

---

## 🏆 Status final do DETRAN

| Métrica | Valor |
|---------|-------|
| **Score composto** | **94,0/100 → A+** |
| **Integridade de Dados** | **100/100** ✅ |
| **Arquivos em JSON estruturado** | **454/455 (99,8%)** |
| Contratos no DB | 13 (1 vigente + 12 ingeridos de PDFs) |
| NEs com `data_emissao` correta | 470/470 ✅ |
| Índices por contrato granulares | 10 contratos mapeados |
| Formatos suportados pelo pipeline | **10** |

---

## 📁 Estrutura consolidada

```
DETRAN_CONSOLIDADO_JSON/
├── 01_CONTRATOS/           70 JSONs (pdf)
├── 02_EMPENHOS/            111 JSONs (pdf)
├── 03_FATURAS/             121 JSONs (pdf)
├── 05_ACEITES/             17 JSONs (pdf)
├── 06_COBRANCAS/           90 JSONs (pdf+docx+xls+png)
├── 07_SCRAPING_SPCF/       8 JSONs (csv convertido)
├── 08_PDFS_ORIGINAIS/      24 JSONs (pdf - certidões)
├── 09_RELATORIOS/          13 JSONs (pdf+md+html+xlsx+py+json)
├── MASTER_DETRAN_CONSOLIDADO.json   (índice global)
├── ANALISE_INDICES_CORRECAO.json    (por contrato)
├── RELATORIO_FINAL_PIPELINE.md
├── RELATORIO_FINAL_COMPLETO.md
└── COBERTURA_FINAL.md (este arquivo)
```

---

## 🔁 Reprodutibilidade

```bash
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"

# 1. PDFs (fast path)
py -3.12 detran_pipeline_fast.py

# 2. OCR em PDFs imagem (8 min)
py -3.12 detran_ocr_fase2.py

# 3. Não-PDFs (docx, xlsx, html, md, py, png)
py -3.12 detran_pipeline_nao_pdf.py

# 4. Ingestão de contratos no DB
py -3.12 detran_ingest_contratos_db.py

# 5. Score final
py -3.12 detran_score_auditor.py
```

---

**Tempo total pipeline:** ~9 minutos | **Cobertura:** 99,8% | **Score DETRAN:** 94,0 (A+)
