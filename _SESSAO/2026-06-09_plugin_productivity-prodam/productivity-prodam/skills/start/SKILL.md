---
name: start
description: "Inicializa o sistema de produtividade PRODAM: cria TASKS.md, CLAUDE.md, memory/ e dashboard a partir de profiles.json e dados existentes."
user_invocable: true
---

# Inicializar Sistema — Projeto PRODAM

Configura o ambiente de produtividade criando ou atualizando os arquivos de gestão a partir de profiles.json.

## Pré-Requisitos

Verificar existência de:
1. `profiles.json` — SSOT de devedores (OBRIGATÓRIO — abortar se não existir)
2. Pasta `02_SPCF/` — dados do SPCF
3. Pasta `REFERENCIA_JURIDICA/` — base jurídica

## Fluxo de Inicialização

### Etapa 1: Inventário do Estado Atual
Verificar: TASKS.md, CLAUDE.md, memory/, dashboard.html
- Todos existem → perguntar: reinicializar ou apenas atualizar?
- Nenhum existe → criar do zero

### Etapa 2: Bootstrap a partir de profiles.json
Ler profiles.json e extrair por devedor: sigla, nome, val_orig, val_exig, fase (F0-F9), prescricao_proxima, forca_probatoria, proximo_passo.

Popular:
1. **CLAUDE.md** → template de `setup/CLAUDE.md.template` + top 12 devedores
2. **TASKS.md** → template de `setup/TASKS.md.template` + tarefas por fase
3. **memory/devedores/** → 1 arquivo por devedor com perfil completo
4. **memory/glossario.md** → template de `setup/glossario.md.template`

### Etapa 3: Gerar Tarefas Iniciais por Fase
- F0 → "Iniciar inventário documental"
- F1 → "Executar extração OCR dos PDFs"
- F2 → "Cruzar dados SPCF × PDFs"
- F3 → "Montar dossiê comprobatório"
- F4 → "Gerar e enviar notificação extrajudicial"
- F5 → "Monitorar prazo de resposta à notificação"
- F6 → "Decidir escalação: protesto, monitória ou execução"
- F7 → "Preparar petição judicial"
- F8 → "Acompanhar execução judicial"
- F9 → (concluído, não gerar tarefa)

Tarefas recorrentes: relatório quinzenal, atualização monetária mensal, verificação de prescrições semanal.

### Etapa 4: Dashboard
Copiar `skills/dashboard.html` para o diretório do projeto.

### Etapa 5: Resumo
Apresentar: devedores importados, tarefas criadas, alertas de prescrição, valor total, top 5 ações urgentes.

## Regras
1. profiles.json obrigatório. Sem ele, abortar.
2. Não sobrescrever sem confirmar. Backup como .bak antes.
3. Valores de profiles.json, nunca fabricados.
4. Datas em dd/mm/aaaa.
