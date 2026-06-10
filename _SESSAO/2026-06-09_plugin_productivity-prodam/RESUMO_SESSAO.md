# Sessão 2026-06-09 — Customização do plugin `productivity-prodam`

> Registro de sessão. Projeto PRODAM — Contrato 002/2026 (Brandão Ozores × PRODAM S.A.).
> Advogado: Gabriel Mar (OAB/AM 15.697).

## Objetivo
Alinhar o plugin de produtividade `productivity-prodam` ao estado atual do projeto.

## O que estava desatualizado (diagnóstico)
- Plugin dizia **51 devedores**; o projeto hoje tem **69**.
- Exemplos defasados (SES/SUSAM como maior crédito a ~R$ 45 mi, prescrição 13/05/2026).
- `.mcp.json` vazio — nenhum conector ligado.
- Skill `/start` referenciava `setup/*.template` que **não existiam** (o comando quebrava).
- `dashboard.html` com dados de demonstração antigos e coluna "Fase" em vez de "próximo passo".

## O que foi feito (v1.0.0 → v1.1.0)
1. **Sincronização do portfólio** — 51 → 69 devedores em todo o plugin; exemplos atualizados
   (SEDUC como maior crédito; SSP com prescrição em 30/06/2026; SEJUSC em 31/08/2026);
   força 12 FORTE / 15 MÉDIA / 42 FRACA; estados reais do pipeline (ANALISAR_DOCUMENTACAO,
   CLASSIFICAR, ENVIAR_TRD, PROTOCOLAR_PETICAO, etc.).
   Arquivos: `.claude-plugin/plugin.json`, `README.md`, e as skills `painel-devedores`,
   `task-management`, `alerta-prazos`, `memory-management`.
2. **Correção do `/start`** — criada a pasta `setup/` com `CLAUDE.md.template`,
   `TASKS.md.template` e `glossario.md.template`. São modelos com lacunas `{{...}}`
   preenchidas em tempo de execução a partir do `profiles.json` — nenhum dado sensível
   fica embutido no arquivo do plugin.
3. **Conectores Gmail + Calendar** — declarados como categorias recomendadas em `.mcp.json`
   (`email`, `calendar`, `documents`); `CONNECTORS.md` reescrito; as skills
   `update --comprehensive` e `alerta-prazos` passam a usar Gmail (respostas de devedores,
   instruções da PRODAM) e Calendar (eventos para prescrições e prazos processuais).
4. **Dashboard refeito** — KPIs reais agregados (69 devedores, R$ 83.668.078,44 exigível,
   R$ 125.245.390,64 atualizado, 2 prescrições < 90 dias); top 10 por valor; coluna
   "Fase" substituída por "Próximo Passo" (como o projeto rastreia hoje).

## Princípio anti-alucinação
Nada foi fabricado: prescrições só aparecem onde confirmadas (SSP, SEJUSC); o devedor SALUX
ficou sem nome por não constar no contexto; valores e contagens vieram do `CLAUDE.md` do
projeto gerado em 09/06/2026 (SSOT = `PRODAM_DOCS/profiles.json`).

## Entregável
- `productivity-prodam.plugin` (v1.1.0) — instalável pelo app (botão "Save/Instalar").
- Código-fonte completo em `productivity-prodam/`.

## Observações e pendências
- **Confidencialidade:** o `.plugin` e o `dashboard.html` contêm nomes de órgãos e valores
  reais do portfólio. Tratar como sigiloso (sigilo profissional + LGPD); não compartilhar
  fora do escritório. Há a opção de gerar uma versão "demonstração" com dados fictícios
  caso seja preciso distribuir o plugin.
- **Hook quebrado em outro plugin instalado:** `check-sql-files.py` com `${CLAUDE_PLUGIN_ROOT}`
  não resolvido dispara erro a cada gravação de arquivo (PostToolUse:Write). Não afetou este
  trabalho, mas convém revisar a configuração desse outro plugin.
- Plugin original (cache do app): id `plugin_01JXME7CfmhM9aSCefFAkJTe`.

## Inventário do plugin
```
.claude-plugin/plugin.json
.mcp.json
CONNECTORS.md
README.md
setup/CLAUDE.md.template
setup/TASKS.md.template
setup/glossario.md.template
skills/dashboard.html
skills/start/SKILL.md
skills/update/SKILL.md
skills/task-management/SKILL.md
skills/memory-management/SKILL.md
skills/painel-devedores/SKILL.md
skills/alerta-prazos/SKILL.md
skills/registro-acao-devedor/SKILL.md
```
