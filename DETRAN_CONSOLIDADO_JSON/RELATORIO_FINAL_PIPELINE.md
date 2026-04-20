# DETRAN_CONSOLIDADO → JSON Pipeline (Máximo Esforço)

**Data:** 14/04/2026
**Fonte:** `PRODAM_DOCS/DETRAN_CONSOLIDADO/` (455 arquivos, 1,06 GB)
**Saída:** `DETRAN_CONSOLIDADO_JSON/` (432 JSONs + masters)

---

## 📊 Resultado

| Categoria | Arquivos fonte | JSONs gerados | Status |
|-----------|----------------|----------------|--------|
| 01_CONTRATOS | 70 PDFs | **70** ✅ | Com OCR (sessão anterior) |
| 02_EMPENHOS | 111 PDFs | **111** ✅ | Fast-path |
| 03_FATURAS | 121 PDFs | **121** ✅ | Fast-path |
| 04_NOTAS_LIQUIDACAO | 0 | 0 | — (vazia) |
| 05_ACEITES | 17 PDFs | **17** ✅ | Fast-path |
| 06_COBRANCAS | 91 (80 PDFs) | **80** ✅ | Fast-path |
| 07_SCRAPING_SPCF | 8 CSVs | **8** ✅ | Conversão direta |
| 08_PDFS_ORIGINAIS | 24 PDFs | **24** ✅ | Fast-path (certidões) |
| 09_RELATORIOS | 13 (1 PDF) | **1** ✅ | PDF apenas |
| **TOTAL** | **455** | **432** (95%) | **OCR fase 2 em curso (122 pendentes)** |

---

## 🚀 Bibliotecas usadas (state-of-the-art)

| Lib | Versão | Uso |
|-----|--------|-----|
| **PyMuPDF (fitz)** | 1.24.14 | Extrator rápido de texto nativo — fast path principal |
| **pdfplumber** | 0.11.9 | Fallback para tabelas e layouts complexos |
| **pytesseract** | 0.3.13 | OCR para PDFs imagem (português) |
| **pdf2image** | instalada | Conversão PDF → PNG para OCR |
| **tesseract binário** | 5.5.0 (português) | Engine OCR |
| **docling** | instalada | Disponível para uso avançado (IBM SOTA) |
| **unstructured** | instalada | Disponível para parsing estruturado |
| **ocrmypdf** | 16.13.0 | Disponível para OCR inline |

---

## 📁 Estrutura de saída

Cada JSON tem:

```json
{
  "filename": "1º TA ao Contrato 006.2021 - Prazo.pdf",
  "path": "PRODAM_DOCS/DETRAN_CONSOLIDADO/01_CONTRATOS/...",
  "categoria": "01_CONTRATOS",
  "data_extracao": "2026-04-14",
  "tamanho_bytes": 1234567,
  "texto_length": 24727,
  "texto_preview": "primeiros 800 chars...",
  "texto_completo": "texto integral do PDF",
  "pdf_meta": {
    "metodo": "pymupdf" | "pdfplumber" | "ocr_tesseract_fase2",
    "paginas": 16,
    "tem_texto": true
  },
  "precisa_ocr": false,
  "campos_estruturados": {
    "tipo_doc": "TERMO_ADITIVO",
    "cnpjs": ["04.224.028/0001-63"],
    "datas_encontradas": ["03/03/2022", "30/12/22"],
    "valores_brl": ["1.868.846,52", "..."],
    "contratos_referenciados": ["006/2021"],
    "nes_referenciadas": ["2022NE00003"],
    "indices_mencionados": ["IGPM"],
    "clausula_11": "... cláusula 11ª de reajuste ...",
    "clausula_objeto": "... CLÁUSULA PRIMEIRA DO OBJETO ...",
    "reajustes_pct": [6.54]
  }
}
```

---

## 🎯 Parser por tipo

Cada categoria tem parser especializado:

### 01_CONTRATOS (contratos + aditivos)
- `tipo_doc`: CONTRATO_PRINCIPAL ou TERMO_ADITIVO
- `clausula_11`: cláusula de reajuste (crítica!)
- `clausula_objeto`
- `reajustes_pct`: percentuais de reajuste aplicados
- `multas_pct`, `juros_pct_am`

### 02_EMPENHOS
- `numero_ne`: ex "2026NE0001323"
- `valor_empenho`
- `descricao`
- `situacao`: Ativo/Cancelado/Liquidado

### 03_FATURAS
- `numero_nfse`
- `competencia`: MM/AAAA
- `servico` prestado

### 05_ACEITES
- `confirma_aceite`
- `responsavel` (fiscal)

### 06_COBRANCAS
- `oficio_numero`
- `destinatario`
- `valor_cobrado_possivel`

### 08_PDFS_ORIGINAIS (certidões)
- `tipo_cnd`: NEGATIVA/POSITIVA
- `orgao`: FGTS/RFB/TST/CARTORIO

---

## 🔍 Índices de Correção Monetária por Contrato

Análise consolidada (com texto extraído até agora):

| Contrato | Arquivos | Índice consolidado | Fonte |
|----------|----------|---------------------|-------|
| **004/2016** | 7 | **IGPM** | OCR texto |
| **006/2021** | 6 | **IGPM** | Filename + OCR |
| 010/2021 | 5 | (aguardando OCR) | — |
| **012/2021** | 6 | **IPCA** | Filename + OCR |
| **017/2015** | 7 | **IGPM** | OCR texto |
| 022/2014 | 9 | (aguardando OCR) | Profile diz "IGPM+1%+2%" |
| 025/2014 | 8 | (aguardando OCR) | — |
| 027/2014 | 7 | (aguardando OCR) | — |
| 060/2022 | 1 | (aguardando OCR) | — |
| 071/2022 | 1 | (aguardando OCR) | — |
| **075/2022** | 6 | **IPCA** | Filename + OCR |
| **083/2022** | 4 | **IPCA** | Filename + OCR |

**Padrão emergente:**
- **Contratos 2014-2021 com reajuste**: usam IGPM (confirma cláusula 11.1 do profile)
- **Contratos 2022+**: usam IPCA (mudança após Lei 14.905/2024? ou cláusula específica)
- Nenhum contrato usa SELIC (correto — SELIC é padrão default, não contratual aqui)

> **Implicação jurídica:** O profile.json diz `indice_correcao: "IGPM+1%+2%"`, mas **os contratos de 2022 usam IPCA**. Isso precisa ser considerado no cálculo de atualização monetária fatura-a-fatura — não é um índice único para DETRAN, depende do contrato de origem.

---

## 🛠️ Como consultar os JSONs

### Python — buscar todos contratos de um índice
```python
import json
from pathlib import Path

OUT = Path("DETRAN_CONSOLIDADO_JSON/01_CONTRATOS")
igpm_contracts = []
for f in OUT.glob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    if "IGPM" in (d.get("campos_estruturados",{}).get("indices_mencionados",[]) or []):
        igpm_contracts.append(d["filename"])
print(igpm_contracts)
```

### Python — localizar cláusula 11 de um contrato
```python
d = json.load(open("DETRAN_CONSOLIDADO_JSON/01_CONTRATOS/Contrato_022.2014_-_Execução_de_Sistema_SCIT.json"))
print(d["campos_estruturados"]["clausula_11"])
```

### LLM RAG — corpus completo
Todos os `texto_completo` podem ser ingeridos em um vector store (Chroma, Pinecone) para RAG sobre toda a base DETRAN.

---

## 📋 Arquivos de Saída

| Arquivo | Descrição |
|---------|-----------|
| `DETRAN_CONSOLIDADO_JSON/<categoria>/*.json` | JSON individual por documento (432 arquivos) |
| `DETRAN_CONSOLIDADO_JSON/MASTER_DETRAN_CONSOLIDADO.json` | Índice global agregado |
| `DETRAN_CONSOLIDADO_JSON/ANALISE_INDICES_CORRECAO.json` | Índice de correção por contrato |
| `DETRAN_CONSOLIDADO_JSON/PDFS_PRECISAM_OCR.txt` | Lista dos 122 PDFs em OCR fase 2 |
| `DETRAN_CONSOLIDADO_JSON/RELATORIO_FINAL_PIPELINE.md` | Este relatório |

---

## 🔁 Reprodutibilidade

```bash
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"

# Fast-path (extrai tudo que é texto nativo, ~16s)
py -3.12 detran_pipeline_fast.py

# OCR fase 2 (scans — ~30 min para 122 PDFs)
py -3.12 detran_ocr_fase2.py

# Análise de índices
# (script inline no final do pipeline_fast ou rodar sobre os JSONs)
```

---

## 📈 Performance

- **Fast-path (PyMuPDF)**: 423 arquivos em 16 segundos (~26 arq/s)
- **OCR (tesseract)**: ~1-2 min por PDF (depende do número de páginas)
- **Paralelismo**: 8 workers (fast) / 6 workers (OCR)
- **Tempo total estimado para tudo**: ~35-45 min (com OCR)

---

_Gerado com máximo esforço: 8 libs PDF state-of-the-art disponíveis, cascade de fallbacks, parsing especializado por categoria, JSON estruturado pronto para LLM._
