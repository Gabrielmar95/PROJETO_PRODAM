---
description: Auditoria rápida de consistência do projeto (SSOT, prazos, índice git)
---

Execute a auditoria rápida do Projeto PRODAM e apresente um painel único. Todas as checagens são SOMENTE LEITURA (use `py -3.12` no Windows):

1. **profiles.json**: parse OK? Quantos devedores (CI exige ≥ 50)? Todos com CNPJ e `_metadata`? Quantos sem data de prescrição registrada?
2. **Prazos**: liste devedores com prescrição nos próximos 90 dias (🔴 < 30 dias, 🟡 < 90), e marcos interruptivos com data no passado pendentes de reconfirmação.
3. **Bancos**: `prodam.db` (raiz) × `PRODAM_DOCS/_ANALISE/prodam.db` — mesmas contagens em `spcf_faturas`, `spcf_empenhos`, `spcf_contratos`? Divergência = alerta de drift (direção de sync correta: DETRAN_AUDITORIA_COMPLETA → PROJETO_PRODAM).
4. **Estrutura .claude**: existe exatamente UMA `.claude/` ativa na raiz? `git ls-files | grep .claude` aponta só para arquivos existentes? `settings.local.json` e `scheduled_tasks.lock` fora do índice?
5. **Relatório quinzenal**: data do último em `DOCUMENTOS_GERADOS/` — atraso gera multa contratual de R$ 500/dia.

Formato de saída: tabela `Checagem | Status (✅/⚠️/🔴) | Detalhe | Ação sugerida`. Termine com no máximo 3 ações prioritárias. Não corrija nada automaticamente — toda correção é proposta para aprovação.
