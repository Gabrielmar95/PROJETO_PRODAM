# PROJETO PRODAM — Recuperação de Créditos

**Última atualização:** 20/04/2026 (manhã — pós-restauração de infra + git inicializado)
**Contrato:** 002/2026 — PRODAM S.A. × Brandão Ozores Advogados
**Status:** DETRAN notificação extrajudicial 001/2026 assinada (17/04, ICP-Brasil) · Sistema Multi-Agente S3 concluído + S3-bis patch renomeador v2 (R1 ✅, abort benigno em A/C) · Etapa 5 E1.5 Inventariador pausada pelo usuário às 02:38 · próximos devedores: SES/SUSAM, SSP, SEDUC, SEAD

---

## 1. IDENTIDADE

- **Advogado:** Gabriel Mar — OAB/AM 15.697 (Gabriel Mar Sociedade Individual de Advocacia)
- **Contratante:** Brandão Ozores Advogados
- **Cliente:** PRODAM S.A. — Processamento de Dados Amazonas (CNPJ 04.407.920/0001-80, sociedade de economia mista estadual, Lei AM 941/1970 e Lei 13.303/2016)
- **Objeto do contrato 002/2026:** recuperação extrajudicial e judicial de créditos contra os devedores em carteira
- **Fee:** 20% sobre créditos efetivamente recuperados
- **Obrigações contratuais:**
  - Relatórios quinzenais (multa R$ 500/dia de atraso)
  - Multa de 10% do crédito por prescrição perdida por omissão

---

## 2. VISÃO GERAL DO PORTFÓLIO

### Números-chave (consolidados em 17/04/2026)

- **69 devedores** em carteira (não 51, não 70 — a chave `_metadata` em `profiles.json` não é devedor)
- **~R$ 121 M exigível · ~R$ 199 M atualizado** (data-base 17/04/2026)
- **~3.500 faturas** (parte prescrita, parte exigível)

### Composição do portfólio (69 devedores)

| Categoria | Qtd | Exemplos |
|---|---:|---|
| **Administração Direta / Autarquias / Fundações** | **52** | SES/SUSAM, SSP, DETRAN, SEDUC, SEAD, SEJUSC, FUAM/FUHAM, PMAM, FHAJ, FHEMOAM, SEFAZ, SUHAB, CETAM, ADS, COSAMA... |
| **Bancos** | **6** | CAIXA, Banco Master (em liquidação), Banco Sicoob, Banco BMG, Banco Safra, Banco Daycoval, Bradesco |
| **Seguradoras / Previdência privada** | **2** | Prover, Sul América |
| **Empresas privadas (tech/serviços)** | **10** | B23 Tecnologia, PSA Technology, FenixSoft, Itransito, EasyTech, SALUX, CPA, BMC, Anoreg, Odontomed |

### 5 devedores prioritários

| # | Devedor | Status atual | Próxima ação |
|---|---|---|---|
| 1 | **DETRAN** | ✅ Concluído (organização + jurídico) | Protocolar ofícios; aguardar resposta 20 dias |
| 2 | **SES/SUSAM** | Pendente | Próximo na fila — iniciar organização |
| 3 | **SSP** | Pendente | Após SES/SUSAM |
| 4 | **SEDUC** | Pendente | Após SSP |
| 5 | **SEAD** | Pendente | Após SEDUC |

---

## 3. WORKFLOW PADRÃO POR DEVEDOR (6 ETAPAS)

Modelo validado com DETRAN em 17/04/2026. Replicar para próximos devedores:

### Etapa 1 — Criar pasta-devedor
```
C:\Users\gabri\Desktop\{DEVEDOR}_AUDITORIA_COMPLETA\
```
Com 18 subpastas oficiais (00_VISAO_GERAL a 18_RELATORIOS_EXECUTIVOS) + auxiliares (_TEMP_ANALISE, _LIXEIRA).

### Etapa 2 — Organizar em Fases A/B/C/D
- **Fase A:** Limpeza segura (backups/WIP/duplicatas óbvias → `_LIXEIRA/`)
- **Fase B:** Reorganização da raiz em pastas temáticas
- **Fase C:** Consolidação de pastas redundantes (com análise de nome+tamanho)
- **Fase D:** Deduplicação por SHA-256 (arquivos > 100 KB)

Cada fase gera `_LIXEIRA/_LOG_FASE_X.csv` + `_LIXEIRA/_REVERTER_FASE_X.py` (reversão em 1 comando).

### Etapa 3 — Reestruturar profiles.json
- Verificar se cláusulas específicas de um contrato foram propagadas indevidamente a outros
- Classificar cada contrato por regime: `contratual_igpm`, `contratual_ipca`, `igpm_aditivo`, `ipca_aditivo`, `selic_pura`, `silente_administrativo` (Tema 810)
- Adicionar contratos faltantes (ex: DETRAN tinha 14 no profile mas 18 no memorial)
- Backup antes de cada modificação

### Etapa 4 — Investigar faturas flagadas
- Consultar `16_BANCOS_DADOS/prodam.db` (tabelas: spcf_contratos, spcf_empenhos, spcf_faturas, spcf_nfs)
- Cruzar com `15_CONSOLIDADOS_JSON/consolidado_*.json`
- Classificar cadeia documental (TRIO / FORTE / MÉDIA / FRACA)
- Identificar marcos interruptivos (Art. 202 CC) para faturas potencialmente prescritas

### Etapa 5 — Baixar PDFs oficiais do SPCF
**Credenciais:** CPF `02542720290` / senha `GMS2026` (VPN PRODAM necessária)
**Endpoints descobertos:**
- Contrato (proposta): `/index.php/propostas/imprimir/{id_proposta}`
- Fatura individual: `/index.php/contratos/fatura/{id_fatura}` (renderiza RPS/NFS-e — usar Chrome printToPDF)
- Relatório de faturas do contrato: `POST /index.php/contratos/relatorioFaturas` (data[ContratoRelatorio][...])

Estratégia: Selenium headless para login + requests com cookies para GET de páginas + Chrome CDP `Page.printToPDF` para converter HTML em PDF individual.

### Etapa 6 — Gerar peças jurídicas
- Notificação extrajudicial (modelo Brandão Ozores: Garamond + azul #1F3864 + dourado #B8963E + rodapé institucional)
- Memorial de cálculo fatura-a-fatura (docx + xlsx + csv + json + md)
- TRD (Termo de Reconhecimento de Dívida) quando aplicável
- Dossiê comprobatório
- Ofícios (LAI, Art. 38 §2º Lei 8.666/93, Lei 4.320/64 arts. 63-65)

---

## 4. ARQUIVOS E PASTAS DE REFERÊNCIA

| Objetivo | Caminho |
|---|---|
| **Profile SSOT** (69 devedores, todos os contratos) | `DETRAN_AUDITORIA_COMPLETA/11_PROFILES_BACKUPS/ativo/profiles.json` |
| **Banco SQLite** (dados SPCF consolidados) | `DETRAN_AUDITORIA_COMPLETA/16_BANCOS_DADOS/prodam.db` |
| **Base bruta de documentos PRODAM** (25,2 GB) | `DETRAN_AUDITORIA_COMPLETA/PRODAM_DOCS/` (INTOCÁVEL) |
| **Referência jurídica** (jurisprudência, estudos, knowledge base) | `DETRAN_AUDITORIA_COMPLETA/PRODAM_DOCS/REFERENCIA_JURIDICA/` |
| Projeto DETRAN (case concluído, referência) | `C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\` |
| Resumo do case DETRAN | `DETRAN_AUDITORIA_COMPLETA/18_RELATORIOS_EXECUTIVOS/__RESUMO_SESSAO_17_04_2026.md` |
| Extração SPCF (histórico) | `C:\Users\gabri\Desktop\SPCF_EXTRACAO\` |

---

## 5. REGRAS OBRIGATÓRIAS

### Financeiras
- **Fee:** 20% sobre créditos recuperados
- **RPV AM:** teto de **20 salários mínimos** (Lei AM 2.478/2002)
- **Precatório vs RPV:** se valor ≤ 20 SM → RPV (pagamento em 60 dias); > 20 SM → precatório (anos)
- **Valores BRL:** SEMPRE `Decimal`, NUNCA `float`
- **CSV:** separador `;` (ponto-e-vírgula), encoding `UTF-8 com BOM` (`utf-8-sig`)

### Jurídicas
- **`profiles.json` é fonte autoritativa** de valores/regimes/status — nunca o Demonstrativo Excel
- **Consultar `PRODAM_DOCS/REFERENCIA_JURIDICA/`** antes de qualquer análise/parecer
- **Prescrição quinquenal** (Art. 206 §5º I CC + Decreto 20.910/1932 + Súmula 85/STJ) — contada do vencimento, por fatura individual
- **Marcos interruptivos** taxativos (Art. 202 CC): NL emitida pelo devedor, pagamento parcial, proposta de acordo, reconhecimento documentado
- **Lei 14.905/2024** — marco 30/08/2024: contratos silentes celebrados após essa data → **SELIC pura** (Art. 406 CC)
- **Tema 810 STF** (RE 870.947/SE, 20/09/2017): contratos silentes de Fazenda Pública → IPCA-E + poupança até 29/08/2024; SELIC pura a partir de 30/08/2024
- **REsp 793.969/RJ + Art. 784 III CPC:** cadeia de 5 elos (contrato + NE + NL + NF + aceite) = título executivo extrajudicial

### Operacionais
- **PDFs são provas jurídicas:** nunca apagar, sempre manter originais
- **PRODAM_DOCS/** é intocável (fonte bruta)
- **01_CONTRATOS/PDF/** é intocável em cada pasta-devedor
- **Rate limiting SPCF:** `time.sleep(1.5)` entre requisições
- **Backup antes de modificar** qualquer JSON/DB crítico (padrão: `profiles_BACKUP_ANTES_{operacao}.json`)

---

## 6. CREDENCIAIS E ACESSOS

### SPCF (Sistema de Processamento de Contratos e Faturas — PRODAM)
- **URL:** `https://spcf.prodam.am.gov.br/` (via SGTI SSO: `https://sgti.prodam.am.gov.br/`)
- **VPN PRODAM necessária** (domínio resolve apenas em intranet 10.20.0.x)
- **Credenciais:** carregar de `PROJETO_PRODAM/.env` (variáveis `SPCF_USER`, `SPCF_PASS`, `SPCF_URL`). Arquivo listado em `.gitignore`. Usar `python-dotenv` ou equivalente nos scripts.
- **Fluxo de login:** `POST /index.php/usuarios/login` com `data[Usuario][login]` e `data[Usuario][senha]`, depois `GET /index.php/spcf` para estabelecer cookie SPCF

### Rede interna PRODAM
- `spcf.prodam.am.gov.br` → 10.20.0.29
- `sgti.prodam.am.gov.br` → 10.20.0.29
- Sessão CAKEPHP (path `.prodam.am.gov.br`, secure)

---

## 7. FERRAMENTAS E STACK TÉCNICO

### Python (ambiente principal)
- **Python 3.12** com venv local
- **Bibliotecas principais:**
  - `pandas` · `polars` (dataframes; polars para >50K linhas)
  - `pytesseract` · `pdf2image` (OCR de PDFs)
  - `pdfplumber` · `PyMuPDF (fitz)` (extração texto de PDFs)
  - `python-docx` (geração de .docx com estilo Brandão Ozores)
  - `openpyxl` (geração de .xlsx)
  - `requests` · `selenium` (acesso SPCF; usar ambos em conjunto)
  - `beautifulsoup4` (parsing HTML)
  - `sqlite3` (prodam.db)

### Shell
- **PowerShell 7.6** (Windows 11) — padrão do usuário
- **Git Bash** (disponível para comandos Unix)

### IDE/Agent
- **Claude Code Opus 4.6+** (usar Opus 4.7 quando disponível — 1M contexto)
- Habilitar skills: `atualizacao-monetaria-sob-demanda`, `classificacao-forca-probatoria`, `validador-cadeia-documental-fatura`, `blindagem-pre-execucao`

---

## 8. PENDÊNCIAS ATIVAS (17/04/2026)

| # | Pendência | Prazo / Gatilho |
|---|---|---|
| 1 | **Iniciar organização SES/SUSAM** (2º devedor prioritário) | A partir de 18/04/2026 |
| 2 | Protocolar 2 ofícios DETRAN ao DETRAN-AM | Imediato |
| 3 | Aguardar resposta DETRAN (20 dias úteis) | ~15/05/2026 |
| 4 | Revisar `_LIXEIRA/` DETRAN (400 MB · 1.265 arquivos) | 24/04/2026 |
| 5 | Monitorar cutoff NF 110654 (marco 19/08/2021 + 5a) | **19/08/2026** |
| 6 | Complementar documentação 5 NFs antigas CT 8/2021 | Após resposta DETRAN |

---

## 9. ESTILO VISUAL (peças jurídicas)

Padrão Brandão Ozores (extraído do PDF modelo em 16/04/2026):
- **Fonte:** Garamond
- **Cores:** Azul #1F3864 (títulos) · Dourado #B8963E (separadores) · Carvão #2D2D2D (texto) · Cinza #595959 (rodapé)
- **Rodapé institucional** (em toda página):
  - Linha 1: `BRANDÃO OZORES ADVOGADOS • Av. Via Láctea, nº 1374 – Morada do Sol/Aleixo – Manaus/AM – CEP 69.060-085`
  - Linha 2: `Tel. (92) 3347-8115 • fsandrade@ozoresadv.com.br • ozoresadv.com.br`
- **Títulos em letras espaçadas** (spacing 20): `N O T I F I C A Ç Ã O   E X T R A J U D I C I A L   ...`
- **Formato A4 retrato**, margens 2,5 cm

---

## 10. HISTÓRICO DE SESSÕES IMPORTANTES

| Data | Devedor | Ação principal |
|---|---|---|
| 14/04/2026 | Portfólio | Snapshot de 70 devedores (pré-consolidação) |
| 16/04/2026 | DETRAN | Notificação v1-v3 · memorial v1 (185 faturas) |
| **17/04/2026** | **DETRAN** | **Organização Fases A/B/C/D · memorial v202 · 4 PDFs SPCF · marco NF 110654 · 2 ofícios · concluído** |
| **19/04/2026** | **DETRAN + arquitetura** | **Sistema Multi-Agente v2 aprovado (35 agentes, 11 sessões, DETRAN-only até S10) · Gate S0 5/5 ✅ em `DETRAN_AUDITORIA_COMPLETA/19_ESTADO_AGENTES/00_PREREQS/` · skill `atualizacao-monetaria-creditos` v2.0→v2.1 (nova flag `perspectiva={credor\|devedor}`) · backup SHA-256 `CCA29E8B...C7EA` (60.513 arquivos, 34,84 GB) · Lei AM RPV confirmada 2.748/2002 (não 2.478) · Playwright oficial (não Selenium)** |
| **19/04/2026 (noite)** | **DETRAN — pós-notificação** | **Notificação assinada (SHA-256 `c4f05236...`) arquivada em `_NOTIFICACAO_ASSINADA/` com `hash_protocolo.txt` · conteúdo extraído (18 cts × 202 NFs × R$ 28.142.624,30) em `CONTEUDO_NOTIFICACAO_EXTRAIDO.json` · validação cruzada com prodam.db (`VALIDACAO_CRUZADA_BANCO_19_04_2026.md`) · gap analysis vs 4 fontes (`GAP_ANALYSIS_NOTIFICACAO_vs_FONTES.md` — 18 cts classificados A-OK/A/B · 5 ausentes do DB confirmados no profile · 4 (`8/2021`,`14/2019`,`23/2014`,`179/2018`) removidos do profile em 16/04 e re-adicionados em 17/04 14:36 pós-assinatura) · marco NF 110654 (CT 179/2018) totalmente documentado: NL 2021NL0001165 + OB 2021OB0001606 + PD 2021PD0001589 (19/08/2021 · José Maria Pinto GerFin DETRAN · cutoff 19/08/2026) · briefing `BRIEFING_REUNIAO_DR_FABIO.txt` com 3 decisões (4 cts sem PDF · redação Art. 202 VI CC na pág. 3 · divergência CSV vs profile para NF 110654) · inventário de lacunas: **5 cts + 85 NFs + 28 NEs** p/ download SPCF/SGTI + **646 HTMLs** p/ converter (`INVENTARIO_DOWNLOADS_E_CONVERSOES.md` + `LACUNAS_PARA_DOWNLOAD.csv` + `HTMLS_PARA_CONVERTER.csv`) · rascunho do pipeline `baixar_lacunas_spcf.py` (Playwright+dotenv) · `.env` criado e populado em `PROJETO_PRODAM/.env` (SPCF_USER/PASS/URL) + `.gitignore` com `.env` + credenciais removidas do §6** |
| **20/04/2026 (tarde)** | **DETRAN — reconciliação profile + notificação v5 + anexos II/III + TRD + auditoria forense** | **Profile.json DETRAN reconciliado: `valor_canonico = R$ 28.196.572,22` criado como SSOT, `val_exig` e `val_atualizado` zerados como RESÍDUO (preservados em `_residuos_zerados_2026_04_20`), `correcao_monetaria_passo7` marcado SUPERADO, campos derivados (`ev_valor_esperado`, `ev_honorarios`) recalculados via Opção B; espelho `PRODAM_DOCS/profiles.json` sincronizado com `_sync_meta`. Laudo de auditoria forense v4 em 5 camadas concluído: veredito CORRETA COM RESSALVAS (`13_PECAS_JURIDICAS/auditorias/AUDITORIA_NOTIFICACAO_v4_2026-04-20.md`). Notificação v5 gerada (R$ 28.196.572,22 · CT 075/2022 corrigido com fator 1,0950 · nova Seção IV.A de ressalva CT 8/2021 · REsp 1.089.720/RS + AREsp 1.503.902 como reforço · regime precatório explicitado · 9 alterações rastreadas em `CHANGELOG_v4_para_v5.md`). Anexo II — Certidão Técnica de Cálculo BCB gerada com séries reais 189/433/4390/196. Anexo III v3 — cadeia 5 elos das 202 NFs com reconciliação 4 fontes, casamento 151/202 = 75% (vs 36/202 v2). Minuta TRD v2 (10 cláusulas · à vista 5% desc R$ 26.786.743,61 · 24 parcelas de R$ 1.174.857,18). Investigação dos Ofícios 001/002 no sistema PRODAM concluiu: **Ofício 001 pode ser reduzido em escopo** (CT 003/2026 já em `spcf_contratos` + `dados_completos.json` + PDF físico), **Ofício 002 indispensável** (aceites das 12 NFs CT 8/2021 ausentes em `05_ACEITES`). Commit `PRODAM_DOCS`: `9492ac4` pushed para GitHub.** |
| **20/04/2026 (madrugada→manhã)** | **DETRAN — incidente de infra + restauração + git inicial** | **Pasta `Desktop\DETRAN_AUDITORIA_COMPLETA` apagada às 03:07 (provável agente automático — possivelmente confundido pela existência do backup `_BACKUP_PRE_AGENTES_20260419_024647` criado por `robocopy /MIR` em 19/04 02:46). Restaurada da Lixeira via Shell.Application `Verbs().Item(0).DoIt()` em 13 s — **36.500 arquivos / 7,07 GB** recuperados (casco correto, sem `PRODAM_DOCS` físico — junction NTFS preservada apontando para `PROJETO_PRODAM\PRODAM_DOCS`). **Decisão:** NÃO usar o backup gordo de 32,46 GB (era enganoso — robocopy seguiu a junction e duplicou `PRODAM_DOCS` dentro). Backup `_BACKUP_PRE_AGENTES_20260419_024647` mantido como redundância **até 05/05/2026** (15 dias), depois pode apagar. **REGRA arquitetural fixada** em `DETRAN_AUDITORIA_COMPLETA/CLAUDE.md` (topo do arquivo): pasta filha = ~7 GB de análise, **nunca** duplicar `PRODAM_DOCS` dentro; se subir para 30+ GB, algum script copiou em vez de seguir a junction — investigar antes que a pasta seja apagada de novo. **Para futuros backups com robocopy:** usar `/XJ` (exclude junctions). **Git:** `PROJETO_PRODAM` inicializado como repo (`main`) com remote bare local em `C:\Users\gabri\git-backups\PROJETO_PRODAM.git` (mesmo padrão do SEDUC). **Commit inicial `47e6645` — 1.242 arquivos / 25,75 MB** (snapshot pós-restauração; bare comprimido = 5,64 MB). Inclui `DOSSIES_MULTIFORMATO/` (71 devedores × 5 formatos) + `AUDITORIA_COMPLETUDE/` (70 MDs por devedor) — tirados do `.gitignore` por terem alto valor de versionamento. `.gitignore` ampliado para excluir `PRODAM_DOCS/` (25,4 GB), `SPCF_EXTRACAO/` (6,9 GB), `_BACKUP_*/`, `*.sqlite`. Próximo push: `git -C "...\PROJETO_PRODAM" push` (tracking já configurado para `backup/main`). Ver §12 para detalhes de restauração.** |

---

## 11. SISTEMA MULTI-AGENTE — STATE (19/04/2026)

Plano consolidado: `C:\Users\gabri\.claude\plans\estou-querendo-fazer-um-fluffy-wall.md`.

**Gate S0 (5/5 ✅ VALIDADO):**
- `00_PREREQS/lei_am_rpv.md` — Lei AM 2.748/2002, RPV Fazenda Estadual 20 SM = R$ 32.420 (SM 2026 R$ 1.621)
- `00_PREREQS/spcf_health.md` — VPN + SSO + Playwright OK; caveat: não fazer page.goto() direto pós-login
- `00_PREREQS/backup_hash.md` — backup DETRAN em `_BACKUP_PRE_AGENTES_20260419_024647/` · hash `CCA29E8BD87AA24DCA12670CA3FEF7F74E1F918A99E42C04409B78D94000C7EA`
- `00_PREREQS/patch_monetario.md` — skill patchada v2.0 → v2.1 · hash `5599ae7ea35de67847e38613860693d97b343663a244a8170f045a24fcb52af4` · backup em `SKILL.md.BAK_20260419` (hash `6fff91e446d41f2cfe064097ce86d42cfc88a2e7003163220f2ed82cfa182bdb`)
- `00_PREREQS/skill_marcos_confirmada.md` — `marcos-interruptivos-prescricao` v2.1 instalada (hash `ff15a1cfca72f3f4fbd716ec2d5c3e2824ac8b7342921d6cf473f79b6d0ce997`)

**S1 Maestro (E6.1) ✅ implementado:** `~/.claude/skills/agente-maestro-prodam/SKILL.md` + `10_SCRIPTS_PYTHON/agentes/esquadrao_6_qa/maestro_gate_s0.py` (testado: Gate OK 5/5 em prod, Gate FAIL em dir vazio emite `_GATE_FALHA_*`).

**S2 E1-E6 — 35/35 skills criadas em 2026-04-19 (MVP):**
- **E1 Ingestão (7):** agente-renomeador-inteligente (✅ testado 93% precisão) · agente-conversor-formatos · agente-scanner-pdf-ocr (✅ testado) · agente-downloader-spcf · agente-inventariador-documental · agente-extrator-dados-pdf · agente-consolidador-ssot.
- **E2 Cadeia (3):** agente-verificador-elo-5 · agente-detector-faltantes · agente-classificador-procedencia.
- **E3 Jurídico defensivo (5):** agente-classificador-regime · agente-calculador-monetario · agente-prescricional-defensivo · agente-reconhecimento-tacito · agente-forca-probatoria.
- **E4 Adversarial (11):** auditor-orquestrador-dossie · auditor-adversarial-prescricional · -cadeia · -monetario · -tributario (GATED, S11) · -processual · -contratual · -legitimidade · -sintetizador · -blindagem-reversa · -revisor-meta.
- **E5 Geração (5):** agente-gerador-notificacao · -trd · -memorial · -oficios · -dossie.
- **E6 QA (4):** agente-maestro-prodam (S1 ✅) · agente-guardrails-multiagente · agente-testing-qa-multiagente · agente-sla-alertas-multiagente.

**Scripts Python MVP (3):** `maestro_gate_s0.py` (S1 ✅) · `renomeador_inteligente.py` (✅ testado 93%) · `scanner_pdf_ocr.py` (✅ testado 100%).

**Status agentes:** 3 funcionais + testados (maestro, renomeador, scanner) · 32 skills com lógica documentada, execução real virá sessão-a-sessão conforme S2-S11 do cronograma.

**S3 — E1.1+E1.3 em produção (DETRAN, 19/04/2026 tarde → 20/04/2026 madrugada):**
- ✅ Gate S0 revalidado 5/5
- ✅ E1.1 Renomeador sample (200): 197 ALTA / 2 MÉD / 1 BAIXA · CSV: `19_ESTADO_AGENTES/S3_E1.1_renomeacao_proposta.csv`
- ⚠️ E1.1 full **DIAGNÓSTICO BUGADO** — 3.435 suspeitos (67% dos PDFs DETRAN) · 860 casos (25%) com PRODAM como devedora · 274 (8%) sem devedor. CSV: `S3_E1.1_DIAGNOSTICO_BUGADO_NAO_APLICAR.csv` (gitignored, NÃO aplicar).
- ✅ E1.3 Scanner sample (200 PDFs): 144 OK / 56 OCR (28%) · 1.130 páginas · 262 MB · CSV: `S3_E1.3_relatorio_ocr_SAMPLE.csv`.
- ❌ **E1.3 full ABORTADO** após 8h36min (Python >2 GB RAM, CSV nunca criado). Hipótese: memory leak ou PDF corrompido. **Task #21 S3-bis-2** criada para investigar. Sample vira baseline.

**S3-bis — Patch renomeador v2 (20/04/2026 madrugada):**
- ✅ Backup v1: `renomeador_inteligente.py.BAK_v1_20260420`
- ✅ v2 criado: `renomeador_inteligente_v2.py` com R1+R2+R3 + flag `--assert-no-prodam-devedora`
- ✅ Sample 200 com v2: **Gate B (PRODAM=0) OK** — R1 100% eficaz · Gates A e C violaram (mas BENIGNO: os 5 casos PRODAM-errados viraram "sem devedor/MÉDIA" = conservação de massa).
- 📋 **Gate humano pendente:** autorizar relaxamento de Gates A (>5%) e C (>5 p.p.) p/ próxima iteração. Ver `S3-bis_ABORT_A_C_BENIGNO.md` e `S3-bis_RELATORIO.md`.
- 📋 **Apply físico do renomeador:** BLOQUEADO até autorização.

**Achado crítico — sessão 20/04/2026:** `03_NOTAS_LIQUIDACAO/` DETRAN tem **ZERO PDFs**. NL é marco interruptivo do Art. 202 CC — gap preocupante para prescrição. Investigar em S4.

**Sessão autônoma parcial (19/04 tarde → 20/04 02:38):** 4 etapas concluídas (Checkpoint S3 · S3-bis patch · S3-bis re-teste · S3-bis relatório). Etapa 5 (E1.5 Inventariador) iniciada com mapeamento das 4 fontes (profiles: 18 contratos DETRAN · prodam.db: 13c+470e+149f · consolidados OK · físico: NL ausente), pausada pelo usuário.

**S3-bis — Patch Renomeador (3 REGRAS NÃO-NEGOCIÁVEIS):**

**REGRA 1 — PRODAM NUNCA é DEVEDORA.** No Contrato 002/2026, PRODAM é sempre a CREDORA. Se o extrator identificar PRODAM como parte devedora em qualquer linha, descartar o match e relançar a análise ignorando essa string. **Teste automatizado:** se full run propuser PRODAM como devedora em 1+ linha, script ABORTA com exit code não-zero.

**REGRA 2 — STRIP DE BOILERPLATE ANTES DO REGEX.** PDFs gerados a partir de HTML do SPCF trazem menu lateral, breadcrumbs e cabeçalho do sistema como texto. Antes de aplicar regex de extração: remover blocos de menu/navegação/breadcrumb · ignorar cabeçalho "Sistema PRODAM" e rodapé institucional · preferir PDF original do pen drive (`PRODAM_DOCS/*/ORIGINAIS/`) sobre HTML-to-PDF.

**REGRA 3 — DATA DE TRAMITAÇÃO ≠ DATA DO CONTRATO.** Data extraída do SPCF web é data de processamento no sistema, não data de assinatura. Buscar data do contrato APENAS no texto do documento (cláusula de foro, rodapé, etc.), nunca nos metadados da página HTML.

**Próximo passo:** S3-bis (corrigir renomeador respeitando as 3 regras) → revalidar amostra DETRAN → só então rodar full apply.

**Cronograma REVISADO 2026-04-19 tarde (Leitura B confirmada — 14 sessões):**

| Sessão | Foco | Status |
|---|---|---|
| **S0** | Gate Pré-Requisitos (5 PRs) | ✅ |
| **S1** | E6.1 Maestro esqueleto | ✅ |
| **S2** | Scaffolding 35 skills + 3 scripts testados | ✅ |
| **S3** | E1 parcial em produção (E1.1+E1.3 DETRAN) | 🔄 |
| **S3-bis** | Patch renomeador (3 regras não-negociáveis) | 📋 next |
| **S4** | E1 restante DETRAN (E1.2+E1.4+E1.5+E1.6+E1.7) | 📋 |
| **S5** | E2 completo (3 agentes: cadeia/faltantes/procedência) | 📋 |
| **S6** | E3 completo (5 agentes: regime/monetário/prescrição/reconhecimento/força) | 📋 |
| **S7** | E4.0 + E4.1 + E4.10 (orquestrador + adversarial-prescricional + revisor-meta) | 📋 |
| **S8** | E4.2 + E4.3 (cadeia + monetário; E4.4 GATED → S13) | 📋 |
| **S9** | E4.5 + E4.6 + E4.7 (processual + contratual + legitimidade) | 📋 |
| **S10** | E4.8 + E4.9 (sintetizador + blindagem-reversa) | 📋 |
| **S11** | E5 completo (5 agentes geradores) | 📋 |
| **S12** | E6 restantes + end-to-end DETRAN | 📋 |
| **S13** | Generalização SES/SUSAM + E4.4 com parecer humano | 📋 |

**Por que revisado:** plano original previa S2 = E1 produção. Realidade: S2 entregou só scaffolding. S3 atual rodou E1.1+E1.3 e expôs 3 bugs sistêmicos no renomeador. Leitura B isola fix em S3-bis e fecha E1 restante em S4. Cronograma desliza ~2 sessões. Razão: rodar E2/E3 com E1 quebrado = corromper memorial DETRAN (ground truth do sistema). Detalhes em `~/.claude/plans/estou-querendo-fazer-um-fluffy-wall.md`.

**Descobertas colaterais a aplicar eventualmente** (não bloqueantes):
- Skill `blindagem-pre-execucao` v1.1 tem referências incorretas: "RPV máx ≈ 60 SM" (teto federal, inaplicável AM) e SM R$ 1.618 desatualizado — patchar para 20 SM + R$ 1.621.
- Skill `proximo-passo-advisor` linha 184 e `protocolo-juridico-prodam` linha 235 citam "20 SM = R$ 32.420" sem mencionar Lei 2.748/2002 explicitamente.
- CLAUDE.md §3 Etapa 5 menciona Selenium; Playwright é a ferramenta preferida agora.

**Regra permanente do Gate:** o Maestro (E6.1) recusa executar qualquer esquadrão se algum arquivo do `00_PREREQS/` estiver ausente ou com hash inválido.

---

## 12. VERSIONAMENTO E BACKUP (git, desde 20/04/2026)

**Working repo:** `C:\Users\gabri\Desktop\PROJETO_PRODAM\.git` · branch `main` · tracking `backup/main`
**Bare backup:** `C:\Users\gabri\git-backups\PROJETO_PRODAM.git` (mesmo padrão do `SEDUC_AUDITORIA_COMPLETA.git` ao lado)

### Ciclo padrão a cada sessão

```powershell
# Após editar arquivos e querer salvar
cd C:\Users\gabri\Desktop\PROJETO_PRODAM
git add -A
git status                              # conferir o que entrou
git commit -m "<descricao curta>"
git push                                # tracking ja vai para backup/main
```

### O que está versionado (1.242 arq / 25,75 MB no commit inicial)

- Todos os scripts Python (`scripts/`, `tests/`, raiz)
- `CLAUDE.md`, `LEIAME.md`, `requirements.txt`
- `DETRAN_AUDITORIA/`, `DETRAN_CONSOLIDADO_JSON/`, `DETRAN_CONTRATOS_JSON/`
- `DOSSIES_MULTIFORMATO/` (71 devedores × html+json+md+xlsx + 4 csvs)
- `AUDITORIA_COMPLETUDE/` (70 MDs de auditoria por devedor)
- `dados/`, `relatorios/`
- `.claude/`, `.github/`

### O que NÃO está versionado (precisa restaurar manualmente após clone)

| Item | Tamanho | Como recuperar |
|---|---:|---|
| `PRODAM_DOCS/` (fonte bruta) | 25,4 GB | Pen drive · OneDrive · `_BACKUP_PRE_AGENTES_20260419_024647/` (até 05/05/2026) |
| `SPCF_EXTRACAO/` (cache) | 6,9 GB | Re-executar `baixar_lacunas_spcf.py` (precisa VPN + `.env`) |
| `prodam.db` | 91 MB | `python scripts/atualizar_db.py` (regenera de PRODAM_DOCS) |
| `.env` (credenciais SPCF) | <1 KB | Recriar manual: `SPCF_USER=02542720290` + `SPCF_PASS=GMS2026` + `SPCF_URL=https://spcf.prodam.am.gov.br/` |
| Junction `DETRAN_AUDITORIA_COMPLETA\PRODAM_DOCS` | 0 (link) | `New-Item -ItemType Junction -Path "C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\PRODAM_DOCS" -Target "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS"` |

### Restauração em caso de desastre

```powershell
# Cenario 1: perdi PROJETO_PRODAM inteira
cd C:\Users\gabri\Desktop
git clone "C:\Users\gabri\git-backups\PROJETO_PRODAM.git" PROJETO_PRODAM
# (depois recriar PRODAM_DOCS, .env, prodam.db, junction — tabela acima)

# Cenario 2: perdi o bare backup (mas working copy intacta)
git init --bare "C:\Users\gabri\git-backups\PROJETO_PRODAM.git"
git -C "C:\Users\gabri\Desktop\PROJETO_PRODAM" push backup main

# Cenario 3: inspecionar snapshot historico em outro local
git clone "C:\Users\gabri\git-backups\PROJETO_PRODAM.git" C:\Temp\snapshot_inspecao
```

### Cuidados ao versionar

- **Nunca** adicionar `PRODAM_DOCS/`, `SPCF_EXTRACAO/`, `_BACKUP_*/`, `.env`, `prodam.db` ao staging — `.gitignore` protege, mas `git add -f` ignora o `.gitignore`. Não usar `-f`.
- Antes de commits grandes, conferir tamanho: `git status --short | wc -l` e listar top maiores.
- Para futuros backups com `robocopy` da pasta DETRAN, usar `/XJ` (exclude junctions) — senão o robocopy segue o link e duplica `PRODAM_DOCS` (gera o "backup gordo" de 32 GB que originou o incidente de 19-20/04).

---

_Leitura prioritária em toda nova sessão do projeto. Mantenha sincronizado com o estado real._
