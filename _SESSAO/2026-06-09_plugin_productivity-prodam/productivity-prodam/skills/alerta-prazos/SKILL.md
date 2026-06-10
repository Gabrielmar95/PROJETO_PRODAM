---
name: alerta-prazos
description: "Monitora e alerta sobre prazos críticos: prescrição por fatura, resposta a notificação, protesto, prazos processuais e entregas contratuais."
user_invocable: true
args: "Opcional: nome do devedor para prazos específicos"
---

# Alerta de Prazos — Projeto PRODAM

Monitora todos os prazos críticos do portfólio e gera alertas por urgência.

## Tipos de Prazo

### 1. Prescrição de Faturas (Art. 206 §5° CC — 5 anos)
- Fonte: profiles.json + faturas individuais
- Alerta: <30d, 30-90d, 90-180d

### 2. Resposta à Notificação (15 dias úteis)
- Fonte: TASKS.md AGUARDANDO + registro de interações
- Alerta: vencido, <5 dias úteis, <10 dias úteis

### 3. Protesto (3 dias após notificação vencida)
- Alerta: protesto não iniciado após notificação vencida

### 4. Prazos Processuais (dias úteis — CPC)
- Contestação 15d, recurso 15d, embargo 15d
- Alerta: <3 dias úteis, <7 dias úteis

### 5. Entregas Contratuais
- Relatório quinzenal: a cada 15 dias
- Alerta: <3d e <7d para entrega

## Fluxo

### Sem argumentos: Varredura Completa
1. Ler profiles.json → extrair prescrições
2. Ler TASKS.md → extrair prazos
3. Calcular dias restantes
4. Classificar e gerar relatório
5. (Se Calendar conectado) criar/atualizar evento para cada alerta CRÍTICO/URGENTE — checar antes para não duplicar

### Com devedor: Prazos Específicos
1. Filtrar para o devedor
2. Listar faturas com prescrição
3. Listar tarefas com prazo
4. Calcular marcos interruptivos (Art. 202 CC)
5. Gerar timeline

## Formato de Saída

```
ALERTAS DE PRAZO — dd/mm/aaaa

CRÍTICO (X alertas)
   1. [SSP] Prescrição em 21 dias (30/06/2026)
      Ação: protocolar petição judicial IMEDIATAMENTE

URGENTE (X alertas)
   2. [SEJUSC] Prescrição em 31/08/2026
      Ação: priorizar análise e notificação

ATENÇÃO (X alertas)
   3. [DEVEDOR] Faturas prescrevendo em 90-180 dias
      Ação: planejar notificação no próximo ciclo

RESUMO: X faturas em risco | R$ XX.XXX.XXX,XX em jogo
```

## Regras Jurídicas
1. Prescrição é irreversível.
2. Unicidade da interrupção (Art. 202 caput CC): só ocorre UMA VEZ.
3. Tema 1.109/STJ: Governo NÃO renuncia tacitamente à prescrição.
4. Dias úteis vs. corridos: processuais em úteis (CPC), prescrição em corridos (CC).
5. Dados de profiles.json, nunca fabricados.
