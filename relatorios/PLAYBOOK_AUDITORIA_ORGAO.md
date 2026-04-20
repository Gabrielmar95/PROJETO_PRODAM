# PLAYBOOK — Auditoria Completa de Órgão Devedor

**Projeto PRODAM — Contrato 002/2026**
**Template validado em DETRAN (Score A+ 94,0/100)**

Aplique este playbook a qualquer um dos 78 devedores com pasta `*_CONSOLIDADO` em `PRODAM_DOCS/`.

---

## 🎯 O que esse playbook entrega

Para cada órgão processado:
1. **TODOS os documentos** (PDFs + docx + xlsx + html + md + png) convertidos em **JSON estruturado**
2. **Contratos ingeridos no DB** (`spcf_contratos`) com índices de correção granulares
3. **Análise de índices de correção** por contrato (IGPM vs IPCA vs SELIC)
4. **Score composto 0-100** em 12 dimensões (integridade, cadeia, prescrição, blindagem, compliance, etc.)
5. **Relatórios** MD + Dashboard HTML
6. **Profile.json atualizado** com metadados da auditoria

---

## 📋 Pré-requisitos

### Instalação única (1 vez por máquina)
```bash
py -3.12 -m pip install -r requirements.txt
py -3.12 -m pip install python-docx openpyxl xlrd beautifulsoup4 pymupdf pdf2image pytesseract unidecode
```

### Tesseract OCR (binário Windows)
- Baixar: https://github.com/UB-Mannheim/tesseract/wiki
- Instalar com idioma **português**
- Verificar: `tesseract --version`

### Estrutura esperada
```
PROJETO_PRODAM/
├── prodam.db                    # SQLite (auto-gerado)
├── PRODAM_DOCS/
│   ├── profiles.json            # SSOT devedores
│   └── <ORGAO>_CONSOLIDADO/     # pasta do órgão
│       ├── 01_CONTRATOS/        # PDFs de contratos + aditivos
│       ├── 02_EMPENHOS/         # PDFs de NEs
│       ├── 03_FATURAS/          # PDFs de faturas/NFs
│       ├── 05_ACEITES/          # PDFs de aceites técnicos
│       ├── 06_COBRANCAS/        # PDFs + docx de ofícios
│       ├── 07_SCRAPING_SPCF/    # CSVs SPCF
│       ├── 08_PDFS_ORIGINAIS/   # Certidões
│       └── 09_RELATORIOS/       # md, xlsx, html, py
```

---

## 🚀 Execução — 3 comandos

### Pipeline completa em 1 comando
```bash
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"
py -3.12 orgao_pipeline_completa.py --orgao SEDUC
```

Rode `--listar` para ver todos os órgãos disponíveis.

**Fases que executa automaticamente:**
1. **Fase 1** — Fast-path (PyMuPDF + docx + xlsx + html + md + png): ~20s para 500 arquivos
2. **Fase 2** — OCR Tesseract (PDFs imagem): ~8 min para 100 scans
3. **Fase 3** — Ingestão de contratos no DB (`spcf_contratos`)

### Score + auditoria profunda (opcional, 2º comando)
```bash
# Adapte detran_score_auditor.py para o órgão (copiar + renomear consts DETRAN → ORGAO)
py -3.12 orgao_score_auditor.py --orgao SEDUC
```

### Atualizar CLAUDE.md + sincronização
```bash
py -3.12 sincronizar_prodam.py
```

---

## 📂 Saídas geradas

Em `PROJETO_PRODAM/<ORGAO>_CONSOLIDADO_JSON/`:

```
├── 01_CONTRATOS/*.json        # 1 JSON por contrato/aditivo
├── 02_EMPENHOS/*.json
├── 03_FATURAS/*.json
├── 05_ACEITES/*.json
├── 06_COBRANCAS/*.json        # inclui docx, xls, png
├── 07_SCRAPING_SPCF/*.json    # CSVs → JSON
├── 08_PDFS_ORIGINAIS/*.json
├── 09_RELATORIOS/*.json       # md, html, xlsx, py
└── MASTER_<ORGAO>.json        # índice consolidado
```

Cada JSON contém:
```json
{
  "filename": "...",
  "categoria": "01_CONTRATOS",
  "tipo_doc": "CONTRATO_PRINCIPAL",
  "texto_completo": "...",           ← full-text para LLM
  "texto_preview": "primeiros 800",
  "pdf_meta": {"metodo":"pymupdf|ocr_tesseract","paginas":42},
  "campos_estruturados": {
    "cnpjs": [...],
    "datas_encontradas": [...],
    "valores_brl": [...],
    "nes_referenciadas": [...],
    "indices_mencionados": ["IGPM"],
    "clausula_11": "...",           ← reajuste (contratos)
    "clausula_objeto": "...",
    "reajustes_pct": [6.54]
  }
}
```

---

## 🔍 Consultas Python sobre os JSONs

### Todos contratos com IGPM
```python
import json
from pathlib import Path
O = Path("SEDUC_CONSOLIDADO_JSON/01_CONTRATOS")
igpm = [json.loads(f.read_text(encoding="utf-8"))["filename"]
        for f in O.glob("*.json")
        if "IGPM" in json.loads(f.read_text(encoding="utf-8")).get("campos_estruturados",{}).get("indices_mencionados",[])]
print(igpm)
```

### Cláusula 11 do contrato 022/2014
```python
for f in Path("SEDUC_CONSOLIDADO_JSON/01_CONTRATOS").glob("*022*2014*"):
    d = json.loads(f.read_text(encoding="utf-8"))
    print(d["campos_estruturados"].get("clausula_11",""))
```

### Corpus RAG completo para LLM
```python
corpus = []
for f in Path("SEDUC_CONSOLIDADO_JSON").rglob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    corpus.append({
        "id": d["filename"],
        "categoria": d.get("categoria"),
        "text": d.get("texto_completo",""),
        "metadata": d.get("campos_estruturados",{})
    })
# Pronto para Chroma/Pinecone
```

---

## 🧪 Validação pós-execução

### Verificar cobertura
```bash
py -3.12 -c "
from pathlib import Path
O = Path('SEDUC_CONSOLIDADO_JSON')
total = sum(1 for _ in O.rglob('*.json'))
print(f'JSONs gerados: {total}')
"
```

### Verificar ingestão de contratos
```bash
py -3.12 -c "
import sqlite3
c = sqlite3.connect('prodam.db')
r = c.execute('SELECT COUNT(*) FROM spcf_contratos WHERE UPPER(cliente) LIKE \"%SEDUC%\"').fetchone()
print(f'Contratos SEDUC no DB: {r[0]}')
"
```

### Re-rodar auditoria de completude
```bash
py -3.12 auditoria_completude_devedor.py
cat AUDITORIA_COMPLETUDE/AUDITORIA_SEDUC.md
```

---

## 🎯 Casos de uso por categoria

| Objetivo | Categoria | Parser |
|----------|-----------|--------|
| Analisar cláusula de reajuste | 01_CONTRATOS | `clausula_11` |
| Listar empenhos por ano | 02_EMPENHOS | `numero_ne`, `datas_encontradas` |
| Cruzar faturas com contratos | 03_FATURAS | `competencia`, `numero_nfse` |
| Prova de aceite técnico | 05_ACEITES | `tipo_doc: ACEITE_TECNICO` |
| Trilha de cobranças | 06_COBRANCAS | `oficio_numero`, `destinatario` |
| Reconciliação | 07_SCRAPING_SPCF | dados completos |
| Verificar CND | 08_PDFS_ORIGINAIS | `tipo_cnd`, `orgao` |

---

## ⚠️ Ordem de execução recomendada para TOP 5

Priorizar pelos TOP devedores do portfólio (84,6% do valor exigível):

1. **SEDUC** (R$ 49,2M) — 1º do ranking, FORTE
2. **DETRAN** (R$ 31,7M) — já executado ✅ (referência A+)
3. **SES/SUSAM** (R$ 14,7M) — FORTE, TRD pronto
4. **SSP** (R$ 4,6M) — FORTE, Petição pronta
5. **SEAD** (R$ 2,3M) — FORTE, TRD pronto

```bash
for ORGAO in SEDUC "SES/SUSAM" SSP SEAD; do
    py -3.12 orgao_pipeline_completa.py --orgao "$ORGAO"
done
```

---

## 📈 Resultado esperado (benchmark DETRAN)

| Métrica | DETRAN (benchmark) |
|---------|--------------------|
| Arquivos fonte | 455 |
| JSONs gerados | 454 (99,8%) |
| Tempo total | ~9 min |
| Contratos ingeridos no DB | 12 |
| Índices identificados | IGPM (7) + IPCA (3) |
| Score composto | 94,0/100 (A+) |

Órgãos menores (~50-100 arquivos) devem rodar em 2-5 min.

---

## 🛠️ Troubleshooting

### Tesseract não encontrado
```bash
# Adicionar ao PATH ou configurar:
py -3.12 -c "
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
"
```

### PDFs gigantes (>100MB) demoram muito
Ajuste DPI no OCR de 200 → 150 em `detran_ocr_fase2.py:50`.

### Órgão sem pasta _CONSOLIDADO
Criar pasta manualmente e popular conforme estrutura de 9 subpastas. Alternativa: adaptar o script para ler estrutura diferente.

### Contratos não ingeridos
Verificar se os filenames têm padrão `NNN.YYYY` (ex: `022.2014`). Se não, editar regex `RE_CONTRATO_FN`.

---

## 📜 Assinatura técnica do playbook

- **Libs SOTA:** PyMuPDF + Tesseract + python-docx + openpyxl + BeautifulSoup + pdf2image
- **Paralelismo:** 8 workers fast-path, 6 workers OCR
- **Fallback cascade:** PyMuPDF → pdfplumber → OCR
- **Formato saída:** JSON padronizado com `texto_completo` + `campos_estruturados`
- **Testes unitários:** 49 testes em `tests/test_prodam_utils.py`

---

## 🔗 Arquivos relacionados

| Arquivo | Função |
|---------|--------|
| `orgao_pipeline_completa.py` | **Pipeline genérica** (este playbook) |
| `detran_score_auditor.py` | Score DETRAN-específico — copiar e adaptar |
| `prodam_utils.py` | Utilitários compartilhados (norm, brl, datas) |
| `sincronizar_prodam.py` | Comando mestre do projeto |
| `auditoria_completude_devedor.py` | Audita todos os 69 devedores |
| `dossie_multiformato_devedor.py` | Dossiê em 5 formatos (md/html/xlsx/csv/json) |

---

**Última validação:** 14/04/2026 com DETRAN (A+ 94,0/100, 454 JSONs em 9 min)
