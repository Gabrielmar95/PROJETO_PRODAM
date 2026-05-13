# PROJETO PRODAM — Recuperação de Créditos
## Contrato 002/2026 — PRODAM S.A. × Brandão Ozores Advogados
**Atualizado automaticamente em 13/05/2026 00:25 via auto_update_claude_md.py**

## IDENTIDADE
- **Advogado**: Gabriel Mar (OAB/AM 15.697)
- **Escritório**: Gabriel Mar Sociedade Individual de Advocacia
- **Contratante**: Brandão Ozores Advogados
- **Cliente**: PRODAM S.A. (CNPJ 04.407.920/0001-80, economia mista, Lei 13.303/2016)
- **Fee**: 20% sobre créditos recuperados
- **Obrigações**: Relatórios quinzenais (R$500/dia atraso | 10% do crédito por prescrição perdida)

## MÉTRICAS DO PORTFÓLIO
- 70 devedores (26 Gov Direta, 21 Gov Indireta, 22 Privadas)
- R$ 83.668.078,44 exigível | R$ 125.245.390,64 atualizado
- 3477 faturas (2326 exigíveis, 1082 prescritas)
- Força: 12 FORTE, 15 MÉDIA, 42 FRACA

## PIPELINE POR PRÓXIMO PASSO
- ANALISAR_DOCUMENTACAO: 36 devedores
- CLASSIFICAR: 17 devedores
- ENVIAR_TRD: 9 devedores
- PROTOCOLAR_PETICAO: 5 devedores
- HABILITAÇÃO DE CRÉDITO: 1 devedores
- N/A: 1 devedores
- AVALIAR_SUCESSAO: 1 devedores

## TOP 10 DEVEDORES (por valor exigível)
- SEDUC: R$ 49.215.512,48 | FORTE | ANALISAR_DOCUMENTACAO
- SES/SUSAM: R$ 4.783.356,52 | FORTE | ENVIAR_TRD
- SSP: R$ 4.553.230,80 | FORTE | PROTOCOLAR_PETICAO
- SEJUSC: R$ 2.589.660,12 | MÉDIA | ANALISAR_DOCUMENTACAO
- SEAD: R$ 2.339.702,20 | FORTE | ENVIAR_TRD
- BRADESCO: R$ 2.226.517,80 | FRACA | CLASSIFICAR
- CETAM: R$ 1.256.564,28 | FRACA | CLASSIFICAR
- SEDECTI: R$ 1.249.203,13 | MÉDIA | ANALISAR_DOCUMENTACAO
- SALUX: R$ 1.027.949,15 | FRACA | CLASSIFICAR
- POLÍCIA CIVIL: R$ 960.481,71 | MÉDIA | ANALISAR_DOCUMENTACAO

## ALERTAS DE PRESCRIÇÃO (<90 dias)
- 🟠 SSP: 2026-06-30 (48 dias) — R$ 4.553.230,80

## ESTRUTURA DO PROJETO
- `PRODAM_DOCS/_ANALISE/prodam.db` — DB **canônico** (gerado por `PRODAM_DOCS/build_sqlite.py`)
- `prodam.db` (raiz) — cópia derivada, atualizada por `scripts/atualizar_db.py` (é a que `scripts/consultas.py` lê)
- `PRODAM_DOCS/profiles.json` — SSOT dos devedores (fonte autoritativa)
- `PRODAM_DOCS/REFERENCIA_JURIDICA/` — base jurídica (20 subpastas; consultar ANTES de qualquer parecer)
- `PRODAM_DOCS/_SKILLS/` — skills jurídicas pareadas
- `SPCF_EXTRACAO/` — web scraping SPCF (rate-limit `time.sleep(1.5)` entre requisições)
- `scripts/` — scripts Python principais (consultas, pipeline, dossiês, sync, auto-update)
- `tests/test_prodam_utils.py` — testes unitários (pytest)
- `.github/workflows/tests.yml` — CI: pytest + compileall + valida `profiles.json` em push/PR

## SQLITE prodam.db
Tabelas: spcf_contratos (362), spcf_empenhos (16.789), spcf_faturas (1.837), spcf_nfs (52.998), pendrive_docs (3.699), devedores (81), reclassificacao (1.261), cruzamento_spcf_pendrive (1.460)
Views: v_fatura_completa, v_fatura_sem_empenho, v_nf_sem_pagamento, v_pendrive_por_devedor, v_cruzamento_nf

## REGRAS JURÍDICAS OBRIGATÓRIAS
1. **Decreto Estadual nº 53.464/2026** (substitui 51.084/2025) — verificar 4 exceções antes de qualquer ação contra Gov AM
2. Silêncio do devedor **NÃO** interrompe prescrição — exige ato inequívoco (Art. 202 CC taxativo)
3. Juros pós-**Lei 14.905/2024** — NÃO presumir 1% a.m.; verificar arts. 404-406 CC
4. Índices por contrato: consultar `normalizador.py` (mapa contrato/ano → regime, SSOT real). ⚠️ Valores absolutos (SM vigente, teto RPV, custas, honorários) NÃO têm SSOT consolidada — hoje inline em scripts de cálculo. NÃO criar `config_prodam.py` sem auditoria prévia.
5. Adm. Direta → precatório/RPV (Art. 100 CF) | Adm. Indireta concorrencial → penhora direta (Tema 253/STF)
6. NFs do credor **NÃO** são marcos interruptivos (exige ato do devedor)
7. Prescrição é por **FATURA individual** (Art. 189 + 206 §5º I CC), contada do **VENCIMENTO**
8. FUHAM = Fund. Alfredo da Matta | FHAJ = Fund. Hosp. Adriano Jorge — **NUNCA** inverter
9. Empenho (NE) = reconhecimento tácito (Art. 202 VI CC) — interrompe prescrição
10. SELIC já inclui correção + juros — **NÃO** somar separado. IGPM = só correção (juros à parte)
11. Art. 202 CC: interrupção ocorre **UMA VEZ** (unicidade — REsp 1.963.067/MS). Fazenda reinicia por metade (Decreto 20.910/1932 = 2,5 anos)
12. Tema 1.109/STJ: gestor público **NÃO** renuncia tacitamente a prescrição
13. Composição documental (Contrato+NE+NF+Atesto) = título executivo (REsp 793.969/RJ, Min. **José Delgado** — Teori Zavascki foi vencido; nunca citar Teori como relator) <!-- auditado 2026-05-12: cascata propagada em 7 arquivos (11 ocorrências); regra #13 sem citações errôneas remanescentes em .md/.py do projeto -->
14. Fee: **20%** sobre créditos recuperados (não 30%). RPV AM estadual = 20 × SM vigente (Lei AM 2.748/2002)
15. `profiles.json` é a SSOT — NUNCA usar Demonstrativo Excel antigo
16. Valores monetários: **Decimal**, nunca float. Formato BRL: `R$ 1.234,56`
17. `PRECEDENTES_VERIFICADOS.md` é a única fonte de jurisprudência verificada (3 fabricados + 6 distorcidos listados em references/)
18. NUNCA emita opinião jurídica sem consultar `REFERENCIA_JURIDICA/` antes

## HIERARQUIA DE FONTES JURÍDICAS (consultar nessa ordem)
1. **Nota Metodológica** (`PRODAM_DOCS/REFERENCIA_JURIDICA/01_NOTA_METODOLOGICA/`) — corrige todos os demais
2. **Estudo Consolidado** (002/2026) — adaptado ao contrato atual
3. **Estudo Exaustivo** — matriz genérica com minutas
4. **Pesquisa Jurisprudencial** — STJ/STF/TJAM (usar só precedentes verificados)
5. **Extração Contratual** — cláusula a cláusula dos contratos dos devedores
6. `REFERENCIA_JURIDICA/` (20 subpastas) — SSOT jurídica, ANTES de qualquer tarefa

## BENCHMARK AUDITORIA — DETRAN/AM (referência A+)
- **Score composto:** 94,0/100 → A+ (EXCEPCIONAL)
- **Pasta consolidada:** `Desktop\DETRAN_AUDITORIA_COMPLETA\` (3,2 GB, **8.210 arquivos**)
- **Estrutura:** 13 pastas tipo × 14 formatos (PDF/JSON/CSV/MD/HTML/XLSX/DOCX/TXT/PY/JSONL/PNG/LOG)
- **Contratos ingeridos DB:** 13 (12 PDFs + 1 vigente)
- **Índices mapeados:** IGPM (7 contratos) + IPCA (3 contratos)
- **Valor contratual total:** R$ 244,46M | Exigível: R$ 31,7M

### Distribuição DETRAN por formato
| Formato | Arquivos | Uso |
|---------|----------|-----|
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

## PLAYBOOK REPLICÁVEL (outros órgãos)
Ver `PLAYBOOK_ORGAOS_V2.md` (passo-a-passo completo)

### Comando único
```powershell
py -3.12 scripts\orgao_pipeline_completa.py --orgao SEDUC
```

### TOP 5 próximos órgãos (por valor exigível)
1. SEDUC (R$ 49,2M) | FORTE | F0 — ANALISAR_DOCUMENTACAO
2. DETRAN (R$ 31,7M) ✅ A+ | Petição pronta F5 — PROTOCOLAR
3. SES/SUSAM (R$ 14,7M) | FORTE | F3 — ENVIAR_TRD
4. SSP (R$ 4,6M) | FORTE | F5 — PROTOCOLAR
5. SEAD (R$ 2,3M) | FORTE | F3 — ENVIAR_TRD

## SCRIPTS PRINCIPAIS (em `scripts/` — fix 2026-04-22)
| Script | Função |
|--------|--------|
| `scripts/prodam_utils.py` | `norm()` unidecode + `brl()` + datas + `match_flex` |
| `scripts/orgao_pipeline_completa.py` | **Pipeline genérica `--orgao`** (PDF→JSON, OCR, ingestão DB, score) |
| `scripts/sincronizar_prodam.py` | Comando mestre (rebuild DB + auditoria + dossiês + valida skills) |
| `scripts/atualizar_db.py` | Rebuild `prodam.db` (chama `PRODAM_DOCS/build_sqlite.py`) |
| `scripts/consultas.py` | 15 queries forenses (CLI + export CSV em `_ANALISE/consultas_csv/`) |
| `scripts/detran/*.py` | Templates DETRAN (copiar e adaptar para outros órgãos) |
| `scripts/auditoria_completude_devedor.py` | Checklist 11 itens (69 devedores) |
| `scripts/dossie_multiformato_devedor.py` | 5 formatos por devedor |
| `scripts/reconciliar_orfaos_reversos.py` | Popular devedores sem faturas via `norm()` |
| `scripts/auto_update_claude_md.py` | Regenera este `CLAUDE.md` a partir de `profiles.json` |

## SCORE COMPOSTO — 12 dimensões (peso%)
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

**Classificação:** A+ ≥90 | A ≥85 | A- ≥80 | B+ ≥75 | B ≥70

## COMANDOS ÚTEIS (PowerShell)
```powershell
py -3.12 scripts\consultas.py --lista              # ver todas as queries
py -3.12 scripts\consultas.py resumo_geral         # visão geral
py -3.12 scripts\consultas.py top_devedores        # ranking por valor
py -3.12 scripts\orgao_pipeline_completa.py --orgao SEDUC  # audita novo órgão
py -3.12 scripts\auto_update_claude_md.py          # regenerar este CLAUDE.md
py -3.12 scripts\sincronizar_prodam.py             # sincronização completa
py -3.12 -m pytest tests\ -v                       # testes unitários
```
Slash command equivalente: `/sincronizar-prodam` (definido em `.claude\commands\sincronizar-prodam.md`).

## DESENVOLVIMENTO
- **Plataforma:** Windows + PowerShell (não usar bash). Python via launcher `py -3.12` (sem venv).
- **Dependências:** `py -3.12 -m pip install -r requirements.txt` (essenciais: `openpyxl`, `polars`, `requests`; OCR/scraping são opt-in comentado).
- **Testes:** `py -3.12 -m pytest tests\ -v` — cobre `prodam_utils` (BRL, normalização, datas, prescrição).
- **CI:** `.github\workflows\tests.yml` em push/PR para `main` — pytest + `compileall` (sintaxe) + valida `profiles.json` (≥50 devedores, todos com CNPJ, `_metadata` presente) + smoke test do `sincronizar_prodam.py`.
- **Convenções de dados (críticas):**
  - Valores monetários: **`Decimal`**, nunca `float`. Formato BRL `R$ 1.234,56` via `prodam_utils.fmt_brl`.
  - CSV: separador **`;`** + encoding **`utf-8-sig`** (BOM) — abre direto no Excel.
  - Salvar extrações em **JSON + XLSX + CSV** no mesmo script. JSON é a SSOT; XLSX/CSV são derivados.
  - PDFs são prova jurídica — **nunca apagar originais**; backup em `_BACKUPS/` ou `_ARQUIVO_DRIFT/`.
  - SPCF: `time.sleep(1.5)` entre requisições (rate limit obrigatório).
  - Contratos têm 3 formatos coexistindo (`006/2021` em `spcf_contratos`/PDFs, `6/2021` em `profiles.json`, `2021/006` em outras fontes) — usar skill `normalizador-contratos-prodam` ANTES de qualquer JOIN.

## PLUGINS INSTALADOS (Claude Code)

### Inventário
**Local ao PROJETO_PRODAM** (`.claude\settings.local.json`):
- `superpowers@claude-plugins-official` v5.1.0 — instalado 08/05/2026 (source: `github.com/obra/superpowers.git`). 14 skills `superpowers:*`. Sem hooks.

**Global ao usuário** (`~\.claude\`):
- `get-shit-done-cc` (GSD) v1.41.0 — 66 skills `gsd-*`, 33 agents `gsd-*`, 12 hooks, statusline override, bundle CommonJS em `~\.claude\get-shit-done\bin\`.
- `context-mode@context-mode` v1.0.111 — ~11 skills `context-mode:*` + MCP server `mcp__plugin_context-mode_*` (ctx_execute, ctx_batch_execute, ctx_doctor) + 2 hooks (PreToolUse + SessionStart).
- 5 plugins user-scope habilitados em `enabledPlugins`: `commit-commands`, `claude-md-management`, `claude-code-setup`, `context7`, `pyright-lsp`.

### ⚠️ Modo manual obrigatório em arquivos jurídicos
Regra agnóstica de plugin — vale para **qualquer skill, atual ou futura**, independente de qual marketplace ou plugin a tenha instalado.

**Não auto-acionar skill** quando o trabalho tocar em:
- TRDs, notificações extrajudiciais, memoriais, ofícios, petições, dossiês
- `profiles.json`, `KNOWLEDGE_BASE_JURIDICO.md`, `PRECEDENTES_VERIFICADOS.md`
- Qualquer arquivo em `DOCUMENTOS_GERADOS/`, `PRODAM_DOCS/REFERENCIA_JURIDICA/`, `DETRAN_AUDITORIA_COMPLETA/`, `DOSSIES/`

**Padrão exigido**: mostrar diff antes de salvar; aguardar 'aplicar' explícito; respeitar `protocolo-juridico-prodam` quando aplicável.

**Sinais de gatilho amplo** que exigem cautela (independente do plugin de origem): descrições contendo 'use whenever', 'use before any response', 'requires Skill tool invocation before', 'automatically', 'autonomous', 'use SEMPRE', 'must use'. Esses verbetes **não** dão licença para pular o gate manual no escopo jurídico.

**Exceção**: skills em `~/.claude/skills/` curadas pelo advogado e que seguem `protocolo-juridico-prodam` — essas são o próprio gate manual, não o objeto da cautela.

Fundamento: memórias persistentes `feedback_modo_manual_juridico` + `feedback_parecer_humano_areas_nao_curadas`.

**Arquivo destino**: `PROJETO_PRODAM/CLAUDE.md` (tracked no git; hook `backup-claude-md.ps1` cria snapshot adicional pré-edição como safety net intra-sessão).

## ABRIR O prodam.db SEM CÓDIGO
```powershell
# Datasette (web UI):
datasette serve "PRODAM_DOCS\_ANALISE\prodam.db" --open

# DuckDB (SQL no terminal):
duckdb -c "SELECT * FROM spcf_faturas WHERE cliente='SEDUC' LIMIT 10" "PRODAM_DOCS\_ANALISE\prodam.db"
```
Beekeeper Studio: File → Open → escolher `PRODAM_DOCS\_ANALISE\prodam.db`.

## OUTROS MAPAS DO PROJETO (consultar quando relevante)
| Arquivo | O que cobre |
|---------|-------------|
| `LEIAME.md` | Mapa de navegação curto: 3 pastas ativas, fontes canônicas, comandos para abrir o DB |
| `PRODAM_DOCS\CLAUDE.md` | Detalhe OCR v4 + 78 pastas `_CONSOLIDADO` + dossiês multi-formato + reorganização Desktop |
| `PLAYBOOK_ORGAOS_V2.md` | Passo-a-passo replicável (13 passos para auditar novo órgão; validado no DETRAN A+ 94/100) |
| `.claude\napkin.md` | Regras priorizadas (curated runbook re-priorizado a cada leitura) |
| `HISTORICO_SESSOES.md` | Decisões recentes — **histórico, pode estar desatualizado** |
| `PRODAM_DOCS\REFERENCIA_JURIDICA\01_NOTA_METODOLOGICA\` | Corrige todos os demais estudos jurídicos |
| `PRODAM_DOCS\REFERENCIA_JURIDICA\PRECEDENTES_VERIFICADOS.md` | Única fonte de jurisprudência verificada (3 fabricados + 6 distorcidos catalogados) |

