---
name: update
description: "Sincroniza tarefas e memória com dados atualizados: reconcilia profiles.json, detecta prazos vencidos, importa novas faturas SPCF."
user_invocable: true
args: "--comprehensive para varredura completa incluindo emails e calendário"
---

# Atualizar Sistema — Projeto PRODAM

Sincroniza o sistema de produtividade com o estado atual do projeto.

## Modo Padrão (sem argumentos)

### Passo 1: Carregar Estado Atual
Ler TASKS.md, CLAUDE.md, memory/, profiles.json (SSOT).

### Passo 2: Detectar Mudanças em profiles.json
Para cada devedor, comparar:
- Fase atual vs. TASKS.md → se mudou, atualizar tarefas
- Valor exigível vs. memória → se mudou, atualizar CLAUDE.md
- Prescrição → recalcular urgências
- Novo devedor → criar perfil + tarefa inicial

### Passo 3: Triagem de Prazos
1. Prescrição <30 dias → mover para URGENTE
2. Prescrição <90 dias → adicionar alerta em CLAUDE.md
3. Prazos de resposta vencidos → AGUARDANDO → URGENTE com nota "VENCIDO"
4. Tarefas paradas >15 dias → sinalizar

### Passo 4: Verificar Consistência
- Tarefas referenciando devedor inexistente → alertar
- Fases divergentes → corrigir
- Valores desatualizados → atualizar

### Passo 5: Atualizar CLAUDE.md
Recalcular top 12, alertas ativos, contagens.

### Passo 6: Relatório
```
Atualização concluída — dd/mm/aaaa
- X tarefas movidas para URGENTE
- X devedores com mudança de fase
- X prazos de resposta vencidos
- X novas tarefas criadas
- Próximo relatório quinzenal: dd/mm/aaaa
- Top 3 ações mais urgentes
```

## Modo Completo (--comprehensive)

Tudo acima, MAIS:
1. **Gmail** (se conectado): emails de/para devedores, PRODAM, PGE
   - Resposta de devedor → mover tarefa AGUARDANDO → EM ANDAMENTO e registrar (registro-acao-devedor)
   - Instrução da PRODAM / Brandão Ozores → criar tarefa e nota em memory/
   - Confirmação de envio (AR/protocolo) → anotar no histórico do devedor
2. **Calendário** (se conectado): reuniões e audiências relacionadas
   - Criar/atualizar um evento para cada prescrição <90 dias e prazo processual
   - Audiência ou reunião nova (PRODAM, PGE) → criar tarefa de preparação
   - Lembrete da próxima entrega do relatório quinzenal
3. **Arquivos novos**: detectar novos PDFs/Excels no projeto
4. **Memória**: devedores sem perfil, termos novos, limpeza de obsoletos

## Regras
1. Nunca alterar profiles.json (apenas ler).
2. Backup antes de alterar TASKS.md.
3. Não fabricar dados.
4. Prescrição primeiro.
5. Idempotente (rodar múltiplas vezes não duplica). Antes de criar um evento no Calendar, verificar se já existe.
