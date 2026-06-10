---
name: task-management
description: "Gestão de tarefas por devedor com priorização por prescrição, valor e força probatória. Rastreia fases F0-F9, prazos críticos e entregas do Projeto PRODAM."
user_invocable: false
---

# Gestão de Tarefas — Projeto PRODAM

Gerencia o arquivo TASKS.md como registro central de ações pendentes, organizadas por urgência e fase processual.

## Estrutura do TASKS.md

```markdown
# Tarefas — Projeto PRODAM
> Atualizado: dd/mm/aaaa | Próximo relatório quinzenal: dd/mm/aaaa

## URGENTE — Prescrição Iminente (<30 dias)
- [ ] **[SSP] Protocolar petição judicial** — prescrição 30/06/2026, R$ 4.553.230,80, FORTE

## EM ANDAMENTO — Ação em Curso
- [ ] **[SES/SUSAM] Enviar TRD (8 cláusulas)** — R$ 4.783.356,52, FORTE
- [ ] **[SEDUC] Analisar documentação** — R$ 49.215.512,48, FORTE

## AGUARDANDO — Resposta de Terceiro
- [ ] **[DEVEDOR] Aguardando resposta à notificação** — vence dd/mm/aaaa

## PRÓXIMO CICLO — Ações Planejadas
- [ ] **[Geral] Relatório quinzenal** — entrega dd/mm/aaaa

## LOTE — Ações em Massa
- [ ] **Classificar 17 devedores (próximo passo CLASSIFICAR)**
- [ ] **Enviar TRD para 9 devedores (próximo passo ENVIAR_TRD)**

## CONCLUÍDO (últimos 30 dias)
- [x] ~~**[DETRAN] Dossiê concluído**~~ (dd/mm/2026) — F3→F4
```

## Formato de Cada Tarefa

```
- [ ] **[DEVEDOR] Descrição da ação** — contexto, prazo dd/mm/aaaa, valor R$ X,XX, fase FN
```

Campos obrigatórios: [DEVEDOR] (sigla), descrição (imperativo), prazo (data absoluta).
Campos opcionais: valor (BRL Decimal), fase (F0-F9), força probatória, responsável, origem.

## Regras de Priorização (3 critérios em cascata)

1. **Prescrição iminente** — faturas mais próximas de prescrever primeiro
2. **Valor do crédito** — maior valor exigível primeiro
3. **Força probatória** — FORTE > MÉDIA > FRACA

## Operações

### Adicionar Tarefa
1. Identificar devedor (sigla)
2. Classificar seção (URGENTE/EM ANDAMENTO/AGUARDANDO/PRÓXIMO CICLO/LOTE)
3. Inserir na posição correta pela regra de priorização
4. Se prescrição <30 dias → URGENTE automaticamente

### Concluir Tarefa
1. Mover para CONCLUÍDO com data e strikethrough
2. Anotar transição de fase se aplicável (ex: F3→F4)
3. Criar próxima ação automática se existir (dossiê pronto → gerar notificação)

### Revisar/Triar
1. Mover vencidas de AGUARDANDO → URGENTE
2. Recalcular prescrições (faturas que entraram na zona <30 dias)
3. Limpar CONCLUÍDO >30 dias
4. Verificar consistência com profiles.json

### Ações em Lote
Tarefas de LOTE são expandidas quando executadas em subtarefas individuais.

## Regras Específicas PRODAM

1. **Nunca inventar prazos.** Consultar profiles.json ou perguntar.
2. **Relatório quinzenal:** Sempre manter tarefa no PRÓXIMO CICLO.
3. **Prescrição é sagrada:** <90 dias = alerta; <30 dias = URGENTE automático.
4. **Rastreabilidade:** CONCLUÍDO fica 30 dias antes de arquivar.
5. **profiles.json é SSOT.**
