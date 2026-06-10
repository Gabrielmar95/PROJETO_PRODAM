---
name: registro-acao-devedor
description: "Registra cada ação tomada por devedor: notificações, respostas, documentos, escalações. Mantém histórico rastreável para dossiê e relatório."
user_invocable: true
args: "Devedor e ação. Ex: 'SES notificação enviada' ou 'DETRAN resposta recebida'"
---

# Registro de Ações — Projeto PRODAM

Registra e rastreia cada ação por devedor, mantendo histórico para dossiês e prestação de contas.

## Tipos de Ação

| Código | Tipo | Exemplo |
|--------|------|---------|
| NOT | Notificação enviada | Notificação Modelo A enviada via AR |
| RES | Resposta recebida | Devedor contestou valores |
| DOC | Documento gerado | Dossiê comprobatório v2 |
| TRD | TRD gerado/assinado | TRD 8 cláusulas enviado |
| PRO | Protesto | Título protestado 1º Cartório Manaus |
| JUD | Ação judicial | Petição inicial protocolada |
| REU | Reunião | Reunião com PGE sobre CPRAC |
| PAG | Pagamento recebido | Parcela 1/12 R$ X.XXX,XX |
| ESC | Escalação | Devedor escalado F4→F6 |
| OBS | Observação | SEAD criando contrato novo |
| INT | Instrução PRODAM | Não notificar SES (acordo SEFAZ) |

## Formato do Registro

Salvo em `memory/devedores/{devedor-sigla}.md`:

```markdown
## Histórico de Ações

| Data | Tipo | Descrição | Documento | Responsável |
|------|------|-----------|-----------|-------------|
| dd/mm/aaaa | NOT | Notificação Modelo A via AR | NOT_SES_AAAAMMDD.docx | Gabriel |
| dd/mm/aaaa | DOC | Dossiê v2 gerado | DOSSIE_SES_v2.docx | Gabriel |
```

## Fluxo

### Passo 1: Identificar Devedor
Extrair sigla, validar em profiles.json. Se ambíguo, perguntar.

### Passo 2: Classificar Ação
Mapear para código (NOT/RES/DOC/etc.). Se não claro, perguntar.

### Passo 3: Registrar
1. Adicionar linha em `memory/devedores/{devedor}.md`
2. Se muda fase → atualizar perfil
3. Se gera tarefa → adicionar em TASKS.md
4. Se conclui tarefa → marcar concluída

### Consequências Automáticas

| Ação | Consequência |
|------|-------------|
| NOT enviada | Criar tarefa AGUARDANDO "resposta 15 dias úteis" |
| RES recebida | Mover AGUARDANDO → EM ANDAMENTO |
| DOC gerado | Se dossiê → avançar fase |
| PRO realizado | Registrar marco interruptivo |
| JUD protocolada | Avançar F7/F8 + criar tarefas processuais |
| PAG recebido | Calcular saldo; se quitação → F9 |

## Consultar Histórico

"O que foi feito com [DEVEDOR]?":
1. Ler `memory/devedores/{devedor}.md`
2. Apresentar em ordem cronológica reversa
3. Resumir: X ações em 30 dias, fase atual, próximo passo

## Regras
1. Toda ação precisa de data (hoje se não especificada).
2. Nunca fabricar ações.
3. Vincular documento se gerou arquivo.
4. Registro + TASKS.md = operação atômica.
5. Um registro por ação.
