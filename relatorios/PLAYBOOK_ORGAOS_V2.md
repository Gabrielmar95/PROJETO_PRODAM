# PLAYBOOK v2 — Auditoria Completa de Órgão Devedor

**Validado em:** DETRAN/AM (Score A+ 94,0/100, 454 PDFs → JSON, 3,2 GB organizados)
**Última atualização:** 14/04/2026

---

## 🎯 O que este playbook entrega

Para **qualquer órgão** do Projeto PRODAM (70+ devedores):

1. **Todos os PDFs em JSON estruturado** (texto + metadados + cláusulas)
2. **Pasta consolidada no Desktop** organizada **por tipo de documento × formato**
3. **Inventário automático** com detecção de gaps (contratos faltantes, PDFs ausentes)
4. **Score composto 0-100** em 12 dimensões
5. **Contratos ingeridos no DB** `spcf_contratos`
6. **Índices de correção granulares** por contrato (IGPM/IPCA/INPC/SELIC)
7. **Dashboard HTML + Relatórios** prontos para compartilhar

---

## 📋 Sequência de Execução (13 passos)

### Fase 1 — Pipeline PDF→JSON (scripts em PROJETO_PRODAM/)

```bash
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"

# Passo 1: Pipeline completa (fast + OCR + não-PDF + ingestão DB)
py -3.12 orgao_pipeline_completa.py --orgao SEDUC
```

Isso executa automaticamente:
- **Fase 1.1** — Fast-path PyMuPDF (texto nativo, ~20s para 500 arquivos)
- **Fase 1.2** — OCR Tesseract PT (PDFs imagem, ~8 min para 100 scans)
- **Fase 1.3** — docx/xlsx/html/md/py/png handlers
- **Fase 1.4** — Ingestão de contratos em `spcf_contratos`
- **Fase 1.5** — Análise de índices por contrato

### Fase 2 — Score + Auditoria Profunda

```bash
# Adapta detran_score_auditor.py para o novo órgão (copiar + renomear orgao):
cp detran_score_auditor.py seduc_score_auditor.py
# Editar: trocar "DETRAN" → "SEDUC" (6 ocorrências)
py -3.12 seduc_score_auditor.py

# Auditoria profunda (cadeia + prescrição + blindagem):
cp detran_auditoria_profunda.py seduc_auditoria_profunda.py
# Editar: trocar constantes
py -3.12 seduc_auditoria_profunda.py
```

### Fase 3 — Consolidação no Desktop

```bash
# Cria pasta isolada no Desktop com tudo
# Script genérico (a construir, baseado no DETRAN):
py -3.12 orgao_consolidar_desktop.py --orgao SEDUC
```

Gera `Desktop/SEDUC_AUDITORIA_COMPLETA/` com:

```
00_VISAO_GERAL/              Dashboard + Score + Executivo
01_CONTRATOS/                ├─ PDF/ ├─ JSON/ ├─ CSV/ ├─ MD/ ├─ HTML/
02_NOTAS_EMPENHO/            ├─ PDF/ ├─ JSON/ ├─ CSV/ ├─ HTML/ ├─ MD/
03_NOTAS_LIQUIDACAO/         ├─ PDF/ ├─ MD/ (LEIA-ME)
04_FATURAS/                  ├─ PDF/ ├─ JSON/ ├─ CSV/ ├─ HTML/ ├─ XLSX/
05_ACEITES_TECNICOS/         ├─ PDF/ ├─ JSON/ ├─ MD/
06_COBRANCAS_OFICIOS/        ├─ PDF/ ├─ DOCX/ ├─ JSON/ ├─ PNG/
07_CERTIDOES/                ├─ PDF/ ├─ JSON/
08_DADOS_SPCF/               ├─ CSV/ ├─ JSON/ ├─ PDF/ ├─ TXT/
09_RELATORIOS_AUDITORIAS/    ├─ PDF/ ├─ JSON/ ├─ HTML/ ├─ MD/ ├─ CSV/
10_SCRIPTS_PYTHON/           ├─ Ordem_Execucao/ ├─ _archive/
11_PROFILES_BACKUPS/
12_TEMPLATE_DOSSIE/
INVENTARIO_GERAL.md          Tabela tipo × formato + gaps
README.md                    Roteiro completo
```

### Fase 4 — Validação e Inventário

Inventário automático mostra:
- Quantos de cada formato por tipo
- Gaps identificados (ex: "06_COBRANCAS_OFICIOS/PDF: faltam 12")
- Recomendação de busca em fontes secundárias

---

## 🛠️ Scripts Reutilizáveis (em PROJETO_PRODAM/)

### Pipeline principais
| Script | Função |
|--------|--------|
| `prodam_utils.py` | Utilitários: `norm()`, `brl()`, datas, match_flex |
| `orgao_pipeline_completa.py` | Pipeline genérica `--orgao SIGLA` |
| `sincronizar_prodam.py` | Comando mestre (rebuild DB + auditoria + dossiês) |
| `atualizar_db.py` | Rebuild prodam.db |

### Específicos DETRAN (templates para adaptar)
| Script | Função |
|--------|--------|
| `detran_pipeline_fast.py` | Fast-path PyMuPDF |
| `detran_ocr_fase2.py` | OCR Tesseract em paralelo |
| `detran_pipeline_nao_pdf.py` | docx + xlsx + html + md + py + png |
| `detran_ingest_contratos_db.py` | Ingere contratos extraídos no DB |
| `detran_auditoria_profunda.py` | Análise cadeia + prescrição + blindagem |
| `detran_score_auditor.py` | Score 12 dimensões |

### Suporte
| Script | Função |
|--------|--------|
| `auditoria_completude_devedor.py` | Checklist 11 itens para todos 69 devedores |
| `dossie_multiformato_devedor.py` | Dossiê 5 formatos por devedor |
| `reconciliar_orfaos_reversos.py` | Popular devedores sem faturas via `norm()` |

---

## 📦 Bibliotecas Python Instaladas

Confirmadas em 14/04/2026:

```bash
# Core
python-3.12
pip install unidecode  # já instalado

# PDF
pip install pymupdf pdfplumber pypdf pypdfium2

# OCR
pip install pytesseract pdf2image pillow
# Tesseract binário Windows: C:\Program Files\Tesseract-OCR (com português)

# Office
pip install python-docx openpyxl xlrd beautifulsoup4

# Avançado (disponível, uso opcional)
pip install docling unstructured ocrmypdf tabula-py
```

---

## 🎯 12 Dimensões do Score Composto

Pesos validados em DETRAN (referência):

| # | Dimensão | Peso | Ideal |
|---|----------|------|-------|
| 1 | Integridade de Dados | 10% | 100/100 (DB + profile + JSONs) |
| 2 | Cadeia Documental 5 elos | 15% | ≥95 (REsp 793.969) |
| 3 | Prescrição & Marcos | 15% | ≥90 (Art. 202 VI CC) |
| 4 | Blindagem Pré-Execução | 10% | 22/22 válidos |
| 5 | Compliance Jurídico | 10% | 100 (regime + índice + título + modelo) |
| 6 | Evidências Documentais | 8% | ≥95 (reconhecimento) |
| 7 | Reconhecimento Tácito | 8% | 100 (empenhos = reconhecimento) |
| 8 | Atualização Monetária | 6% | ≥95 (IGPM/IPCA/SELIC via BCB) |
| 9 | Priorização (rank portfolio) | 6% | ≥90 |
| 10 | Risco Processual | 5% | ≥90 (p_recuperação) |
| 11 | Valor Recuperável E[V] | 4% | proporcional ao portfolio |
| 12 | Urgência/Prazo | 3% | ≥90 (sem ATENÇÃO próxima) |

### Conceitos
- **A+** ≥ 90 (EXCEPCIONAL)
- **A**  ≥ 85 (EXCELENTE)
- **A-** ≥ 80 (MUITO BOM)
- **B+** ≥ 75 (BOM)
- **B**  ≥ 70 (ACEITÁVEL)

---

## ⚠️ Lições Aprendidas (Troubleshooting)

### Bugs conhecidos e correções

| Bug | Correção |
|-----|----------|
| `spcf_empenhos.data_emissao` = 2026 em 98% dos registros | Re-rodar `atualizar_db.py` |
| 0 contratos do órgão em `spcf_contratos` | Rodar `detran_ingest_contratos_db.py` (adaptar) |
| PDFs imagem com texto vazio | OCR via `detran_ocr_fase2.py` (fallback automático) |
| `POLÍCIA CIVIL` ≠ `POLICIA CIVIL` no DB | Usar `norm()` de `prodam_utils.py` (unidecode) |
| Nomes com `.0` artifact (pandas) | Usar `norm_id()` |
| `_metadata` iterado como devedor | Skip com `is_metadata_key()` |
| `/tmp/` hardcoded no Windows | `tempfile.gettempdir()` |
| `HOJE = date(fixed)` | `date.today()` dinâmico |

### Gaps comuns encontrados

1. **PDFs de cobrança misturados em 08_DADOS_SPCF** — a pipeline de preenchimento detecta por regex de nome
2. **Cobranças têm 2 fontes distintas**: ofícios físicos (80) + faturas raspadas via SPCF (68) — total 148, não duplicatas
3. **Índices granulares por contrato** — profile simplifica "IGPM+1%+2%" mas contratos recentes (2022+) usam IPCA
4. **`.DOCX` e `.PNG` em 06_COBRANCAS** precisam handler específico

---

## 📊 Benchmark DETRAN (referência A+)

| Métrica | DETRAN |
|---------|--------|
| Score composto | **94,0/100 (A+)** |
| Arquivos fonte | 455 |
| JSONs gerados | 454 (99,8%) |
| Tempo pipeline | ~9 min |
| PDFs pós-consolidação no Desktop | 3.542 |
| Contratos ingeridos no DB | 12 (+ 1 vigente = 13) |
| NEs documentadas | 500 |
| Índices mapeados | IGPM:7 + IPCA:3 |
| Valor contratual total | R$ 244,46M |
| Valor exigível | R$ 31,7M |
| Honorários projetados 20% | R$ 6,02M |

---

## 🎯 TOP 5 Próximos Órgãos Recomendados

Por valor exigível (84,6% do portfolio):

1. **SEDUC** — R$ 49,2M | FORTE | ANALISAR_DOCUMENTACAO | F0
2. **DETRAN** — R$ 31,7M | FORTE | PROTOCOLAR_PETICAO | F5 ✅ (já A+)
3. **SES/SUSAM** — R$ 14,7M | FORTE | ENVIAR_TRD | F3
4. **SSP** — R$ 4,6M | FORTE | PROTOCOLAR_PETICAO | F5
5. **SEAD** — R$ 2,3M | FORTE | ENVIAR_TRD | F3

```bash
for ORGAO in SEDUC "SES/SUSAM" SSP SEAD; do
    py -3.12 orgao_pipeline_completa.py --orgao "$ORGAO"
done
```

---

## 🔁 Consolidação no Desktop (padrão DETRAN)

Estrutura final replicável:

```
Desktop/<ORGAO>_AUDITORIA_COMPLETA/
├── 00_VISAO_GERAL/              (6 arquivos essenciais)
├── 01_CONTRATOS/                (PDF + JSON + CSV + HTML + MD)
├── 02_NOTAS_EMPENHO/            (PDF + JSON + CSV + HTML + MD)
├── 03_NOTAS_LIQUIDACAO/         (LEIA-ME — geralmente vazia)
├── 04_FATURAS/                  (PDF + JSON + CSV + HTML + XLSX)
├── 05_ACEITES_TECNICOS/         (PDF + JSON)
├── 06_COBRANCAS_OFICIOS/        (PDF + DOCX + JSON + PNG)
├── 07_CERTIDOES/                (PDF + JSON)
├── 08_DADOS_SPCF/               (CSV + JSON + PDF + TXT)
├── 09_RELATORIOS_AUDITORIAS/    (todos formatos)
├── 10_SCRIPTS_PYTHON/           (reexecução)
├── 11_PROFILES_BACKUPS/         (snapshots)
├── 12_TEMPLATE_DOSSIE/          (20 pastas temáticas)
├── INVENTARIO_GERAL.md          (gaps visíveis)
└── README.md                    (roteiro de leitura)
```

Cada pasta tipo contém **INVENTARIO.md** com contagens e status (✅/⚠️) por formato.

---

## 🎓 Classificadores Automáticos de PDF por Tipo

Para preencher gaps (busca em pastas secundárias):

```python
CLASSIFICADORES = [
    ("empenhos",  r"\b(empenho|\bNE[_\s]|\d{4}NE\d+)"),
    ("faturas",   r"(fatura|NFS[e\-]?|\bNF[_\s]\d|nota[\s_]fiscal)"),
    ("aceites",   r"(aceite|recibo|atesto|ateste)"),
    ("cobrancas", r"(cobran[çc]|of[íi]cio|carta[\s_]circular|Minuta|DAF[\s_-])"),
    ("certidoes", r"(CND|certidao|certid[ãa]o|FGTS|trabalhista|negativa|falencia|fal[êe]ncia|RFB|Receita[\s_]Federal)"),
    ("contratos", r"(contrato|\bTA\b|\d[°ºo]\s*TA|termo[\s_]aditivo|proposta|\b\d{2,3}\.\d{2,4}\b)"),
]
```

---

## ✅ Checklist Pós-Execução

Antes de marcar órgão como auditado:

- [ ] Score ≥ 80 (A-) ou justificar
- [ ] Todos os gaps de PDF resolvidos (preenchidos da fonte)
- [ ] INVENTARIO.md gerado em cada pasta tipo
- [ ] INVENTARIO_GERAL.md sem "Gaps críticos"
- [ ] Contratos ingeridos em `spcf_contratos`
- [ ] `profiles.json` atualizado com `auditoria_cruzada_<data>` + `indices_correcao_por_contrato`
- [ ] Dashboard HTML aberto e validado
- [ ] Pasta `Desktop/<ORGAO>_AUDITORIA_COMPLETA/` existe e README atualizado

---

_Playbook validado em DETRAN/AM (14/04/2026) | Score A+ 94,0/100 | 454 PDFs → JSON | 3,2 GB organizados por tipo × formato_
