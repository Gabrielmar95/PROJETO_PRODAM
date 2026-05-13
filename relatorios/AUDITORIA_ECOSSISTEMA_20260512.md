# Auditoria Ecossistema PROJETO_PRODAM — 2026-05-12

## O que foi executado nesta sessao

### Parte A — 32 plugins desabilitados
- Settings.json global editado: 32 plugins `true` -> `false`
- Backup: `~/.claude/settings.json.bak-20260512-171931`
- Plugins restantes ativos: 65 (de ~97)
- Categorias removidas: SaaS/Cloud (14), Mensageria/CRM (12), Frameworks nao usados (6)

### Parte B — GSD removido do pool
- 5 hooks GSD removidos do settings.json (PreToolUse, SessionStart, PostToolUse)
- 33 agents gsd-*.md movidos para `~/.claude/agents/_DISABLED/`
- Hooks mantidos: backup-claude-md.ps1, long_cmd_router.ps1, context-mode-cache-heal.mjs
- Statusline-prodam.cjs mantido intacto

### Verificacao
- JSON valido confirmado
- 65 plugins true / 38 plugins false
- 0 agents gsd-* no diretorio ativo / 33 em _DISABLED/

---

## Propostas pendentes (aguardam aprovacao caso-a-caso)

### Lacuna 1 — Consolidar 6 workflow skills em 1

**Sobrevivente:** `pipeline-devedor-completo` (unica com comandos vivos + run SES validado 14/04/2026)

**Aposentar (5):**
1. `workflow-orchestrator` — generica, autor Manus AI, sem conteudo PRODAM
2. `workflow-pos-analise-devedor` — 90% coberta por pipeline-devedor-completo
3. `orquestrador-pipeline` — refs a TASKS.md/PROMPTS/ que nao existem; auto-trigger "Use SEMPRE" viola gate
4. `pipeline-integrada-prodam` — script declarado nao existe; erro Teori Zavascki (C01)
5. `workflow-completo-recuperacao` — APOS migrar: customizacoes por devedor (L423-435), cascata (L355-382), escalacao D+ (L386-420), template relatorio quinzenal (L465-495)

**Bloqueadores:** migrar 4 blocos antes de aposentar #5; atualizar `_HIERARQUIA_VALIDACAO.md` e `corrigir_skills_prodam.py:68`

### Lacuna 2a — Consolidar trio reconhecimento em 2

**Manter:** `reconhecimento-tacito-hunter` (deteccao) + `revisar-reconhecimento-divida` (gate)
**Aposentar:** `reconhecimento-divida-tacito` (catalogo — ja coberto pelo hunter)

**Bloqueadores:**
- Discrepancia juridica ato #4 (LRF vs dotacao orcamentaria) exige parecer humano
- Migrar regex Python (PADROES_TACITO_COMPLETOS), logica de reversao de empenho, schema fatura-level
- `revisar-reconhecimento-divida` e parte do gate manual — edit exige diff explicito

### Lacuna 2b — Consolidar 5 dossie skills em 2

**Sobrevivente A (F1-F3 extracao):** S4 `extracao-automatizada-dossie` (renomear para `extracao-documentos-prodam`)
**Sobrevivente B (F4-F5 montagem):** S5 `dossie-juridico-prodam` (manter pareada em PRODAM_DOCS)
**Aposentar (3):** S1 `montagem-dossie-automatizada`, S2 `montagem-dossie-comprobatorio`, S3 `montagem-dossie-devedor-detalhado`

**Bloqueadores:**
- S5 tem 2 ocorrencias de "Teori Zavascki" como relator (linhas 464, 684) — viola regra 13
- S4 description "Use SEMPRE" viola gate manual — reescrever
- 11 capacidades unicas das aposentadas precisam migrar para S5

### Lacuna 4 — Refactor config_prodam.py fantasma em 73 SKILL.md

**Numeros:** 73 SKILL.md, 102 ocorrencias, ZERO imports executaveis
**Achado-chave:** 64 das 102 sao UM boilerplate identico -> sweep PowerShell em 1 execucao
**38 restantes** em 14 skills exigem edit caso-a-caso (protocolo-juridico-prodam = 11 hits, mais critico)

**Decisoes humanas pendentes (Fase 0):**
1. D.1 vs D.2: criar `PRODAM_DOCS/config_constantes.py` para SM/RPV/custas, OU manter inline?
2. CAMPOS_ATUALIZAVEIS (pipeline-integrada-prodam:141): existe em algum arquivo real?
3. Estilo boilerplate: linha unica longa OU lista 4 bullets?
4. Backup: confiar em git OU snapshot em `_BACKUPS/`?

**Templates de refactor prontos**: 5 templates (boilerplate, Cat A/B indice, Cat C taxa live, Cat D valor absoluto, Cat E caso-a-caso). Ver conversa original para texto exato.

---

## Impacto agregado

| Acao | Reducao |
|------|---------|
| Parte A (plugins) | -32 plugins ativos (97 -> 65) |
| Parte B (GSD) | -33 agents + -5 hooks |
| Lacuna 1 (workflows) | -5 skills (proposta) |
| Lacuna 2a (reconhecimento) | -1 skill (proposta) |
| Lacuna 2b (dossie) | -3 skills (proposta) |
| Lacuna 4 (config_prodam) | 73 skills higienizadas, 0 removidas |
| **Total aplicado** | -32 plugins, -33 agents, -5 hooks |
| **Total proposto** | -9 skills adicionais |

---

## Como retomar

1. Abrir nova sessao Claude Code no PROJETO_PRODAM
2. Pedir: "retomar auditoria do ecossistema — ver relatorios/AUDITORIA_ECOSSISTEMA_20260512.md"
3. Aprovar lacunas caso-a-caso: "OK, executar Lacuna 1" / "OK, executar Lacuna 4 Fase 1.1 (sweep)"
4. Para reverter Partes A+B: `Copy-Item "$env:USERPROFILE\.claude\settings.json.bak-20260512-171931" "$env:USERPROFILE\.claude\settings.json" -Force`
