---
name: painel-devedores
description: "Visão rápida do portfólio: quem está atrasado, quem precisa de ação urgente, o que vence esta semana. Consulta profiles.json e TASKS.md."
user_invocable: true
---

# Painel de Devedores — Projeto PRODAM

Gera visão instantânea do portfólio de 69 devedores: "quem está atrasado?", "quem precisa de ação?", "o que vence esta semana?".

## Quando Usar
- Início de cada sessão de trabalho
- "Como está o portfólio?" / "Quem precisa de atenção?"
- Antes de reuniões com a PRODAM
- Para preparar relatórios quinzenais

## Classificação por Urgência

**CRÍTICO (ação imediata):** Prescrição <30 dias, prazo vencido, instrução PRODAM pendente.
**URGENTE (esta semana):** Prescrição 30-90 dias, tarefa com prazo esta semana, notificação >10 dias sem resposta.
**ATENÇÃO (próximos 30 dias):** Dossiê parado >15 dias, mudança de fase pendente, correção monetária desatualizada.
**NORMAL:** Todos os demais.

## Formato de Saída

```
═══════════════════════════════════════════
   PAINEL DO PORTFÓLIO — dd/mm/aaaa
═══════════════════════════════════════════

RESUMO GERAL
   69 devedores | R$ XXX.XXX.XXX,XX total exigível
   XX em andamento | XX aguardando | XX concluídos

CRÍTICO (X devedores)
   SSP — prescreve em DD dias (30/06/2026)
     R$ 4.553.230,80 | FORTE | Ação: protocolar petição

URGENTE (X devedores)
   SEJUSC — prescrição em 31/08/2026
     R$ 2.589.660,12 | MÉDIA | Ação: analisar documentação

ESTA SEMANA
   seg dd/mm: [DEVEDOR] prazo de resposta vence
   sex dd/mm: entrega relatório quinzenal #X

PROGRESSO (últimos 15 dias)
   X devedores avançaram de fase
   X notificações enviadas
   R$ X.XXX.XXX,XX com ação judicial iniciada
═══════════════════════════════════════════
```

## Próximas Ações
Sugere 5 ações de maior impacto: prescrição → valor → força probatória → ações em lote.

## Regras
1. Dados de profiles.json e TASKS.md. Nunca fabricar.
2. Valores em BRL com Decimal.
3. Prescrição é critério #1.
4. Conciso e acionável.
