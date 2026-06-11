# TASKS — Projeto PRODAM (Contrato 002/2026)

> Gerado em 2026-06-09 a partir de `PRODAM_DOCS/profiles.json` (via `STATUS_DEVEDORES.md` de 09/06 19:28).
> Fonte de verdade: `profiles.json` (`fase_atual` + `proximo_passo`). Este arquivo é operacional — ao concluir uma tarefa, atualize o profile e regenere os satélites (`/sincronizar-prodam`).
> Portfólio: 69 devedores · R$ 83.668.078,44 exigível · R$ 125.245.390,64 atualizado.

## 🚨 PRAZOS CRÍTICOS

| Prazo | Devedor | O quê | Valor em risco |
|---|---|---|---|
| 🔴 **30/06/2026** (21 dias) | **SSP** | Prescrição — PROTOCOLAR_PETICAO antes do prazo | R$ 4.553.230,80 |
| 🔴 **30/06/2026** (21 dias) | **SUHAB** | Prescrição — acelerar ANALISAR_DOCUMENTACAO → medida interruptiva | R$ 840.061,15 |
| 🟡 **31/08/2026** (83 dias) | **SEJUSC** | Prescrição — concluir análise documental | R$ 2.589.660,12 |
| 🛡️ reconfirmar | **DETRAN** | Marco interruptivo (Art. 202 VI CC) registrado com data no passado (2026-03-20) — reconfirmar e atualizar `data_prescricao_proxima` | — |
| ⚠️ contínuo | — | Relatório quinzenal PRODAM (multa R$ 500/dia de atraso) | — |

## ⭐ PRIORITÁRIOS

### DETRAN — F5 · PROTOCOLAR_PETICAO · FORTE
- [ ] Obter revisão do Dr. Fábio: Notificação v5 + briefing `_ATUALIZACAO_v5_PARA_DR_FABIO.md` (6 decisões pendentes)
- [ ] Reduzir Ofício LAI 003/2026 de 4 para 2 contratos (CT 023/2014 + CT 179/2018) antes da assinatura
- [ ] Resolver pendência **B1**: 89 faturas em `DETRAN_AUDITORIA_COMPLETA/88_FATURAS_RECONCILIAR.csv` (decisão jurídica fatura a fatura)
- [ ] Reconciliar divergência: `profiles.json` registra exigível R$ 0,00, mas o valor canônico do sub-projeto é **R$ 28.196.572,22** (`DETRAN.valor_canonico`) — alinhar campos antes de qualquer peça
- [ ] Monitorar cutoff prescricional NF 110654 (CT 179/2018): **19/08/2026**

### SES/SUSAM — F3 · ENVIAR_TRD · FORTE
- [ ] Emitir e enviar TRD (R$ 4.783.356,52 exigível / R$ 8.230.061,40 atualizado); prescrição em 113 dias
- [ ] Conferir as 62 faturas fora do universo de cobrança (29 exclusões documentadas em `faturas_exigiveis_breakdown` + canceladas SPCF)

### SSP — F5 · PROTOCOLAR_PETICAO · FORTE
- [ ] **PROTOCOLAR ANTES DE 30/06/2026** — rodar blindagem pré-execução + checklist de 20 itens
- [ ] Verificar exceções do Decreto Estadual 53.464/2026 (art. 1º §§1º-4º) antes do protocolo

### SEDUC — F0 · ANALISAR_DOCUMENTACAO · FORTE
- [ ] Maior crédito do portfólio (R$ 49.215.512,48): rodar pipeline de auditoria (`py -3.12 scripts\orgao_pipeline_completa.py --orgao SEDUC`); prescrição confortável (752 dias)

### SEAD — F3 · ENVIAR_TRD · FORTE
- [ ] Emitir e enviar TRD (R$ 2.339.702,20 / R$ 4.296.278,76 atualizado); prescrição em 478 dias

## 📋 FILA POR PRÓXIMO PASSO

### PROTOCOLAR_PETICAO (5 — fase F5)
- [ ] SSP 🔴 · [ ] SEAS (206d) · [ ] FHAJ (783d) · [ ] FUAM/FUHAM (1756d) · [ ] DETRAN 🛡️

### ENVIAR_TRD (9 — fase F3)
- [ ] SES/SUSAM (113d) · [ ] SEAD · [ ] IPAAM (206d) · [ ] SEINFRA (206d) · [ ] FCECON · [ ] IDAM · [ ] FMT · [ ] FHEMOAM · [ ] CBMAM

### AVALIAR_SUCESSAO (1)
- [ ] SETRAB (extinta — definir sucessor antes de qualquer medida; sem data de prescrição registrada)

### HABILITAÇÃO DE CRÉDITO (1)
- [ ] BANCO MASTER (R$ 889.270,87 — habilitação em liquidação)

### ANALISAR_DOCUMENTACAO (36)
SEJUSC 🟡 · SUHAB 🔴 · SEDUC · SEDECTI · POLÍCIA CIVIL · FENIXSOFT (264d) · CAIXA · AMAZONPREV · FAAR/SEDEL · PGE · PROVER · FVS (206d) · FMT · SECT · SEMIG · SEFAZ · CPA · IKM DE · ANOREG · SEC · SEPROR · BMC · ARSEPAM (206d) · BANCO BMG · SEMA · ITRANSITO · ASSOC. GESTÃO INOV. SAÚDE · FUNTEA (206d) · BANCO SICOOB · PMAM · SNPH (206d) · PSA TECHNOLOGY · SUL AMERICA · B23 TECNOLOGIA · BANCO SAFRA · ODONTOMED · EASYTECH

### CLASSIFICAR (17)
BRADESCO · CETAM · SALUX · UGPI · SEJEL · ADS · BRADESCO FINANCIAMENTO · ADAF · AADESAM · BANCO DAYCOVAL · DPE · FMPES · CGE · CASA CIVIL · FJJA · CASA MILITAR · COSAMA

## 🗂️ HIGIENE DE DADOS
- [ ] 9 devedores sem data de prescrição registrada: AADESAM · BRADESCO · CASA MILITAR · CGE · FJJA · FMPES · SEJEL · SETRAB · UGPI — levantar vencimentos e preencher no profile
- [ ] Itemizar as 69 faturas "fora do universo" (canceladas/excluídas) fatura a fatura (SES/SUSAM 62 · SEJUSC 6 · SSP 1)
- [ ] Rodar `py -3.12 scripts\auto_update_claude_md.py` no Windows para regenerar CLAUDE.md com a nova Regra 14

## 📌 PENDÊNCIAS DE SESSÃO (manuais — seção preservar em regenerações)

### Sessão 2 DETRAN — 10/06/2026 (registro: `relatorios/sessoes/SESSAO_2026-06-10_sessao2-detran-renomeacao-csvs.md`)
- [ ] **Explorer (~2 min)**: levar `.gitignore.backup-20260423-153153` e `CLAUDE.md.bak.20260507_163710` da raiz de `DETRAN_AUDITORIA_COMPLETA` para `_BACKUPS_EMERGENCIA\` — hook `bloqueia-destrutivos.ps1` impede via shell (não contornado, por decisão)
- [ ] **Explorer**: apagar `RENOMEACOES_20260610_DRYRUN.csv` + `.json` (redundantes com índice final `RENOMEACOES_20260610.csv/.json`)
- [ ] **Quando API GitHub voltar**: `gh pr view 24` — confirmar se PR #24 ficou merged ou precisa fechar manualmente (conteúdo já está na main via push direto)
- [ ] **Decisão**: estender renomeação aos ~1.282 não-CSV do mesmo padrão em `DETRAN_AUDITORIA_COMPLETA` (HTML/JSON/XLSX/MD)? Script `10_SCRIPTS_PYTHON\rename_csvs_sessao2_20260610.py` generaliza trivialmente
- [ ] Confirmar envio do Relatório Quinzenal 10/06 à PRODAM → depois decidir destino do docx+html adiados na raiz
- [ ] Sanear 79 violações de citação em `_ORGANIZADO_2026-06-10\` antes de trackear a pasta (CI `test_projeto_inteiro_passa` quebraria)
- [ ] Atualizar `test_exatamente_13_regras` (gerador emite 14 regras desde a Regra 14 DETRAN — teste desatualizado)
