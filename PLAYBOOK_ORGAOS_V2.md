# Playbook Replicável — Auditoria de Órgão (V2)
_13 passos validados no DETRAN/AM A+ 94/100. Atualizado em 10/06/2026 17:45._

Use este playbook para auditar **qualquer novo órgão** do portfólio. Cada passo tem entrada, ferramenta e saída esperada. Score-alvo: A (≥85) — DETRAN atingiu 94 (A+).

## Comando único (pipeline orquestrada)
```powershell
py -3.12 scripts\orgao_pipeline_completa.py --orgao SEDUC
```
Esse script executa F1→F11 automaticamente. Os passos abaixo descrevem o que ele faz e o que validar manualmente.

## Os 13 passos

### Passo 1 — Localizar PDFs e organizar pastas
- **Entrada**: pasta `PRODAM_DOCS/<ORGAO>/` com PDFs originais.
- **Ferramenta**: skill `organizador-arquivos-prodam` (modo cópia não-destrutivo) ou organização manual.
- **Saída**: subpastas por tipo (CONTRATOS/, NES/, FATURAS/, NFs/, COBRANCAS/).
- **Critério**: nenhum PDF apagado; backup em `_BACKUPS/`.

### Passo 2 — OCR completo dos PDFs
- **Entrada**: PDFs do passo 1.
- **Ferramenta**: `scripts/ocr_lote_sem_texto_externo.py` + skill `ocr-pdfs-prodam` (pytesseract/pdf2image, 200 DPI, pt-BR).
- **Saída**: texto pesquisável por PDF (originais preservados como prova).
- **Critério**: ≥95% de páginas com texto extraído (relatório do próprio script).

### Passo 3 — Ingestão no `prodam.db`
- **Entrada**: JSONs do passo 2.
- **Ferramenta**: `PRODAM_DOCS/build_sqlite.py` ou `scripts/atualizar_db.py`.
- **Saída**: registros em `spcf_contratos`, `spcf_empenhos`, `spcf_faturas`, `spcf_nfs`.
- **Critério**: contagens batem com o esperado por contrato.

### Passo 4 — Normalização de contratos
- **Entrada**: 3 formatos coexistindo (`006/2021`, `6/2021`, `2021/006`).
- **Ferramenta**: normalização inline nos scripts de reconciliação (`scripts/reconciliacao_4_fontes.py`) — **não** criar `normalizador.py` (NUNCA-4).
- **Saída**: coluna `contrato_normalizado` em todas as tabelas.
- **Critério**: zero contratos órfãos após reconciliação.

### Passo 5 — Extração contratual cláusula-a-cláusula
- **Entrada**: contratos do passo 1.
- **Ferramenta**: skill `extracao-clausulas-contratuais` + confirmação manual da cláusula econômica (Regra 10).
- **Saída**: JSON por contrato com cláusulas econômicas (índice, juros, multa, foro, prazos).
- **Critério**: índice de correção identificado (IGPM/IPCA/SELIC) por contrato.

### Passo 6 — Reconciliação SPCF × Pendrive × DB
- **Entrada**: dados do passo 3 + pendrive (`pendrive_docs`).
- **Ferramenta**: `scripts/reconciliar_orfaos_reversos.py`.
- **Saída**: tabela `cruzamento_spcf_pendrive` + relatório de gaps.
- **Critério**: divergência <5% e gaps documentados.

### Passo 7 — Cálculo de prescrição por fatura
- **Entrada**: `spcf_faturas` + vencimentos + marcos interruptivos.
- **Ferramenta**: `scripts/alerta_prescricao.py` (buckets/alertas) + skill `analise-prescricao-creditos`.
- **Saída**: classificação `EXIGIVEL`/`PRESCRITA` por fatura + `data_prescricao_proxima` por devedor.
- **Critério**: regra Art. 202 VI CC aplicada (empenho interrompe; silêncio não).

### Passo 8 — Atualização monetária
- **Entrada**: faturas exigíveis do passo 7.
- **Ferramenta**: `scripts/ad_hoc/gerar_memorial_preliminar_ses.py` (BCB live SGS 4390 + Decimal; adaptar por órgão) + skill `atualizacao-monetaria-sob-demanda`.
- **Saída**: `val_atualizado` por devedor; índice aplicado (IGPM/IPCA/SELIC) conforme contrato.
- **Critério**: SELIC já inclui juros (não somar separado); IGPM = só correção.

### Passo 9 — Score composto 12 dimensões
- **Entrada**: dados completos do devedor.
- **Ferramenta**: skill `classificacao-forca-probatoria` (score gravado em `profiles.json`).
- **Saída**: `score_composto` (0-100) + classificação A+/A/A-/B+/B.
- **Critério**: cadeia documental 5 elos (15%), prescrição (15%), blindagem (10%), compliance (10%).

### Passo 10 — Dossiê multi-formato
- **Entrada**: tudo dos passos 1-9.
- **Ferramenta**: `scripts/dossie_multiformato_devedor.py`.
- **Saída**: 5 formatos (JSON + XLSX + CSV + MD + PDF) em `DOSSIES/<ORGAO>/`.
- **Critério**: PDF assinável + JSON estruturado para LLM.

### Passo 11 — Peça processual (TRD ou petição)
- **Entrada**: dossiê do passo 10.
- **Ferramenta**: `protocolo-juridico-prodam` (skill) + revisão humana.
- **Saída**: `.docx` em `DOCUMENTOS_GERADOS/<ORGAO>/`.
- **Critério**: diff revisado antes de salvar; sem alucinação de jurisprudência (consultar `PRECEDENTES_VERIFICADOS.md`).

### Passo 12 — Blindagem pré-execução (22 itens)
- **Entrada**: peça do passo 11.
- **Ferramenta**: skill `blindagem-pre-execucao` (checklist pré-protocolo + 6 teses de embargos antecipadas).
- **Saída**: checklist completo (legitimidade, competência, prescrição, título, índice, juros, multa, etc).
- **Critério**: todos os itens do checklist validados antes de protocolar.

### Passo 13 — Atualização de `profiles.json` e commit
- **Entrada**: tudo dos passos anteriores.
- **Ferramenta**: `scripts/atualizar_profiles_pos_acao.py` ou edição auditada (backup antes: `profiles_BACKUP_ANTES_<motivo>.json`).
- **Saída**: `profiles.json` atualizado + commit auditado.
- **Critério**: `_metadata.last_updated` atualizado; campos obrigatórios preenchidos; CI passa.

## Benchmark DETRAN/AM (referência A+)
- **Score composto**: 94,0/100 → A+ (EXCEPCIONAL).
- **Pasta consolidada**: `Desktop\DETRAN_AUDITORIA_COMPLETA\` (3,2 GB, 8.210 arquivos).
- **Estrutura**: 13 pastas tipo × 14 formatos (PDF/JSON/CSV/MD/HTML/XLSX/DOCX/TXT/PY/JSONL/PNG/LOG).
- **Contratos ingeridos no DB**: 13 (12 PDFs + 1 vigente).
- **Índices mapeados**: IGPM (7 contratos) + IPCA (3 contratos).
- **Valor contratual total**: R$ 244,46M | Exigível: R$ 31,7M.

### Distribuição DETRAN por formato
| Formato | Arquivos | Uso |
|---------|---------:|-----|
| PDF | 3.631 | Documentos originais (contratos, NEs, faturas, cobranças) |
| JSON | 1.698 | Textos extraídos + campos estruturados p/ LLM |
| HTML | 1.428 | Scraping SPCF + dashboards |
| CSV | 861 | Dados tabulares (prescrição, inadimplentes, pagamentos) |
| MD | 222 | Relatórios + documentação |
| TXT | 209 | Texto bruto + logs |
| XLSX | 90 | Planilhas auditoria |
| PY | 34 | Scripts reutilizáveis |
| DOCX | 17 | Cartas + minutas |
| JSONL | 8 | Corpora RAG/LLM |

## Score composto — 12 dimensões (peso%)
1. Integridade de Dados (10%)
2. Cadeia Documental 5 elos (15%) — REsp 793.969/RJ
3. Prescrição & Marcos Interruptivos (15%) — Art. 202 VI CC
4. Blindagem Pré-Execução (10%) — 22/22 itens
5. Compliance Jurídico (10%) — regime/índice/título/modelo
6. Evidências Documentais (8%)
7. Reconhecimento Tácito (8%) — Art. 202 VI CC (empenhos)
8. Atualização Monetária (6%) — IGPM/IPCA/SELIC via BCB
9. Priorização (6%)
10. Risco Processual (5%) — p_recuperação
11. Valor Recuperável E[V] (4%)
12. Urgência/Prazo (3%)

**Classificação**: A+ ≥90 · A ≥85 · A- ≥80 · B+ ≥75 · B ≥70.

