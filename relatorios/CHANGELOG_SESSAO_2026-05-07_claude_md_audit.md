# Changelog — Sessão 2026-05-07: Auditoria e melhoria dos CLAUDE.md

## Objetivo
Auditar todos os arquivos `CLAUDE.md` do projeto, eliminar conflitos entre versões e tornar visível ao Claude Code o estado operacional real do repositório (pastas novas, scripts em drift, issues em aberto).

## Realizações

### Round 1 — Inventário e enxugamento dos sub-CLAUDE.md
- **6 arquivos `CLAUDE.md` mapeados** (1 raiz + 2 sub-pastas + 3 órfãos em `_WORKFLOW_IMPORTADO/`)
- **Score médio inicial: 64/100**
- **3 órfãos neutralizados** (renomeados para `_CLAUDE_HISTORICO.md`) — eram auto-descobertos pelo Claude com conteúdo desatualizado de abril/2026 (caminhos `SCRIPTS/` antigos, urgências passadas, contagens divergentes do estado atual)
- **`PRODAM_DOCS/CLAUDE.md` enxugado** de 373 → 56 linhas. Histórico técnico de OCR/dossiês movido para `PRODAM_DOCS/_HISTORICO_OCR.md` (144 linhas)
- **`SPCF_EXTRACAO/CLAUDE.md` enxugado** de 671 → 114 linhas. Mantidas as 10 descobertas críticas de scraping (Referer obrigatório, magic bytes PDF, dual-key PRODAM/PMM, `<dt>/<dd>` HTML, Content-Type mentiroso, etc.). Detalhe das pipelines em `SPCF_EXTRACAO/_HISTORICO_SESSOES.md` (177 linhas)

### Round 2 — Atualização do gerador `auto_update_claude_md.py`
- Confirmado que `./CLAUDE.md` é totalmente regenerado a cada execução do script (edição manual seria sobrescrita). Correção real é no gerador
- **Tabela de scripts ampliada**: 10 → 17 entradas. Adicionados `sincronizar_referencias_v2`, `detalhamento_faturas`, `reconciliacao_4_fontes`, `ses_reconciliacao_completa`, `gerar_trd_sead`, `corrigir_skills_prodam`, `commit_sessao`
- **Nova seção dinâmica "PASTAS OPERACIONAIS"**: detecta via `Path.exists()` as 6 pastas operacionais (`DETRAN_AUDITORIA_COMPLETA/`, `DETALHAMENTO_FATURAS/`, `DOCUMENTOS_GERADOS/`, `OCR_PESQUISAVEL_CONSOLIDADO/`, `detran_dashboard/`, `_QUESTOES_CRITICAS/`)
- **Nova seção dinâmica "⚠️ DRIFT — SCRIPTS SOLTOS NA RAIZ"**: usa `Path.glob("*.py")` para contar e listar scripts soltos. Aponta `_QUESTOES_CRITICAS/02_DRIFT_SCRIPTS.md` como diagnóstico e `consolidar_scripts.ps1` como resolução
- **Ponteiros de "OUTROS MAPAS"** atualizados para refletir versão slim + sub-CLAUDE de `SPCF_EXTRACAO/`

### Resultado final
- **Total de linhas de CLAUDE.md ativos**: 1.242 → 412 (-67%)
- **CLAUDE.md raiz regenerado**: 198 → 242 linhas (+22%, mas com ganho real de visibilidade)
- **17 scripts soltos na raiz** agora visíveis ao Claude (eram invisíveis)
- **6 pastas operacionais** documentadas
- **2 issues críticas** (`_QUESTOES_CRITICAS/`) sinalizadas
- Score médio final: **78/100**

## Decisões tomadas
1. **Renomear ao invés de deletar** os 3 CLAUDE.md órfãos em `_WORKFLOW_IMPORTADO/` — conteúdo histórico preservado em `_CLAUDE_HISTORICO.md`, sem auto-discovery pelo Claude
2. **Mover histórico para arquivos `_HISTORICO_*.md` separados** — sub-CLAUDE.md fica enxuto e legível, mas todo conteúdo continua disponível via grep/leitura explícita
3. **Detecção dinâmica de pastas e drift** — não depende de manutenção manual; pastas que sumirem desaparecem sozinhas da listagem; novos scripts soltos aparecem automaticamente

## Descobertas
- `auto_update_claude_md.py` é completamente declarativo — qualquer edição manual em `CLAUDE.md` é sobrescrita. Atualização permanente exige editar o gerador
- **17 scripts `.py` soltos na raiz** violam a regra "scripts vivem em `scripts/`" (criados majoritariamente em 21-23/04). Inclui scripts com aparência operacional como `gera_notificacao_ses_script.py`, `notificacao_simples.py`, `baixar_lacunas_spcf.py` — não one-shot
- Existe **`DETRAN_AUDITORIA_COMPLETA/` na raiz do projeto** distinto da pasta homônima de 3,2 GB no Desktop. Contém `88_FATURAS_RECONCILIAR.csv` (trabalho de 02/05) — não estava documentado
- **Issues em aberto desde 22/04** em `_QUESTOES_CRITICAS/` (57 divergências SSOT × pastas + drift de scripts duplicados) — nunca foram referenciadas no CLAUDE.md, ficaram invisíveis ao Claude Code

## Arquivos criados
- `PRODAM_DOCS/_HISTORICO_OCR.md` (144 linhas)
- `SPCF_EXTRACAO/_HISTORICO_SESSOES.md` (177 linhas)
- `relatorios/CHANGELOG_SESSAO_2026-05-07_claude_md_audit.md` (este arquivo)

## Arquivos modificados
- `PRODAM_DOCS/CLAUDE.md` (373 → 56 linhas)
- `SPCF_EXTRACAO/CLAUDE.md` (671 → 114 linhas)
- `scripts/auto_update_claude_md.py` (3 edits — tabela de scripts, 2 seções dinâmicas, ponteiros)
- `CLAUDE.md` (regenerado pelo gerador atualizado)

## Arquivos renomeados
- `PRODAM_DOCS/_WORKFLOW_IMPORTADO/DADOS_5DEV/NEs_PDF/CLAUDE.md` → `_CLAUDE_HISTORICO.md`
- `PRODAM_DOCS/_WORKFLOW_IMPORTADO/SKILLS NOVA/CLAUDE.md` → `_CLAUDE_HISTORICO.md`
- `PRODAM_DOCS/_WORKFLOW_IMPORTADO/RASTREABILIDADE_DASHBOARDS_PRODAM/02_FONTES_DE_DADOS/MARKDOWN/CLAUDE.md` → `_CLAUDE_HISTORICO.md`

## Pendências geradas / persistentes

### Da auditoria
1. **Triar 17 scripts soltos na raiz** — mover para `scripts/`, integrar a pipeline existente, ou arquivar em `_ARQUIVO_DRIFT/`. Resolução semi-automática em `_QUESTOES_CRITICAS/consolidar_scripts.ps1` (não executado nesta sessão)
2. **Reconciliar SSOT × pastas** — 57 divergências entre `profiles.json` e `PRODAM_DOCS/*_CONSOLIDADO`. Script pronto: `_QUESTOES_CRITICAS/executar_reconciliacao.ps1` (não executado)
3. **Investigar `DETRAN_AUDITORIA_COMPLETA/` na raiz** — verificar se é trabalho ativo ou se deveria estar consolidado com a pasta de 3,2 GB no Desktop

### Urgência operacional (não tocada nesta sessão)
- 🔴 **SES/SUSAM**: prescrição em **2026-05-13 (6 dias)** — R$ 14.748.048,96. Status atual em `profiles.json`: ENVIAR_TRD

## Próxima sessão — começar por
1. Triar os 17 scripts soltos na raiz (decisão por arquivo: mover/integrar/arquivar)
2. Endereçar a urgência SES/SUSAM (6 dias para prescrição) — TRD precisa ser enviada
3. Decidir sobre `DETRAN_AUDITORIA_COMPLETA/` da raiz (consolidar ou separar do Desktop)
