# Changelog — Sessão 2026-05-07: Setup do subagent `adversarial-meta-auditor` (etapa 1/5)

## Objetivo
Iniciar a implementação do plano de automações Claude Code para o Projeto PRODAM, em ordem de menor risco. Esta sessão cobre **somente a etapa 1** (subagent adversarial-meta-auditor) — teste isolado antes de avançar para hooks e MCP.

## Plano completo (5 etapas, ordenado pelo Gabriel)
1. **(esta sessão)** Subagent `adversarial-meta-auditor` em `.claude/agents/`
2. Hook `validate_profiles_json.ps1` (modo `deny`)
3. MCP `mcp-server-time` (timezone `America/Manaus`)
4. Hook `enforce_spcf_rate_limit.ps1` (modo `ask` na primeira semana, calibração de FP)
5. Hook `block_float_money.ps1` (modo `ask` sempre — float tem uso legítimo em datas/percentuais)

Cortes vs. proposta original: `regenerate_claude_md` deslocado para depois de validate_profiles_json; `block_precedentes_verificados_edit` vira regra de `permissions` em settings.json em vez de hook; `jurisprudence-fact-checker` e `prescription-watchdog` postergados (gate seletivo apenas em peças formais); `elo-5-chain-validator` e `monetary-calculator` postergados (skill atual basta).

## Realizações

### 1. Recomendação inicial (skill `claude-code-setup:claude-automation-recommender`)
Análise do setup atual: 50+ skills PRODAM, MCP `sqlite-prodam`, hook `block_pdf_delete.ps1`, slash `/sincronizar-prodam`, CI GitHub Actions. Identificados gaps: zero subagents em `.claude/agents/`, hooks cobrindo só PDF, MCP só do banco. Aprofundamento gerou +5 hooks e +4 subagents candidatos.

### 2. Subagent criado
- **Arquivo**: `.claude/agents/adversarial-meta-auditor.md`
- **Tools**: `Read, Grep, Glob` (read-only — não escreve nem edita arquivos)
- **Função**: simular defesa do devedor antes do protocolo, em contexto isolado do gerador da peça
- **7 ângulos adversariais**: cadeia documental, contratual, legitimidade, monetário, prescricional, processual, tributário
- **Verificação anti-alucinação jurisprudencial obrigatória** contra blocklist (3 fabricados + 6 distorcidos) e `PRECEDENTES_VERIFICADOS.md`
- **Output**: 3 buckets (🔴/🟡/🟢) + verdict (`APROVADA_PARA_PROTOCOLO` / `NECESSITA_AJUSTE_NAO_BLOQUEANTE` / `BLOQUEADA_FUROS_CRITICOS`)
- **Regras invioláveis**: NUNCA aprovar peça com furo crítico; NUNCA citar Teori Zavascki como relator do REsp 793.969/RJ (é José Delgado); read-only

### 3. Revisão crítica do subagent — 4 correções aplicadas
- **(1) Regime DETRAN reescrito** (linha 39+) com 2 cenários: pré-Lei 14.905/2024 = IGPM+1%+2% (Cláusula 11.1 do CT 022/2014, lido em PDF original em 16/04/2026 — confirmado, sem caveat "PRESUMIDO"); pós-30/08/2024 = SELIC pura. Adicionado aviso explícito: Cláusula 12.3.2 (1%/dia, máx. 30 dias) protege DETRAN como contratada × PRODAM — **NUNCA invocar contra DETRAN como devedor**.
- **(2) Decreto 53.464/2026 confirmado** em 4 fontes independentes (`03_ESTRATEGIA_COBRANCA/CONSOLIDADO_03_*` linha 162; headers das 4 subpastas consolidadas; `KNOWLEDGE_BASE_JURIDICO.md` v2.1; `MAPA_REFERENCIAS_LEGAIS_API.md`). Mantido como está.
- **(3) REsp 1.963.067/MS confirmado** em `PRODAM_DOCS/REFERENCIA_JURIDICA/11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md:22`. Enriquecido com relator: **Min. Nancy Andrighi, 3ª Turma, 05/04/2022**.
- **(4) Skills referenciadas — verificação empírica via filesystem** (não system-reminder):
  - `agente-prescricional-defensivo` ❌ encontrada APENAS em `C:\Users\gabri\Desktop\skills_lixo_20260507-1550\` (timestamp 15:50 do dia da sessão, sem path live). **Substituída por `marcos-interruptivos-prescricao`** (✅ live em `~/.claude/skills/`).
  - `extracao-clausulas-contratuais`, `normalizador-contratos-prodam`, `proximo-passo-advisor`, `desconsideracao-pj-checklist`: todas live em `~/.claude/skills/` — mantidas.

### 4. Teste falsificável — Via B (bancada com 3 furos plantados)
- **Peça-base**: `PRODAM_DOCS/_DOCUMENTOS_JURIDICOS/Projeto_PRODAM__Notificacao_Modelo_A_DETRAN.docx` (notificação Modelo A, 51 parágrafos)
- **Pivot técnico**: `.docx` → `.md` via `python-docx` 1.2.0. Razão: subagent só tem `Read, Grep, Glob`; `Read` rejeita binário.
- **Peça de teste**: `DOCUMENTOS_GERADOS/_TESTE_AGENT/teste_adversarial_20260507.md`
- **3 furos plantados** em parágrafos-âncora únicos:

| Furo | Posição (após §) | Tipo esperado |
|------|------------------|---------------|
| 3 — Súmula 999/STJ fabricada | §19 (`"(b) Os créditos foram expressamente reconhecidos pelo devedor..."`) | 🔴 anti-alucinação fabricada |
| 1 — Teori como relator do REsp 793.969/RJ | §21 (`"Assim, a credora está autorizada a promover a execução direta..."`) | 🔴 anti-alucinação relator (regra #13) |
| 2 — NF 12345/2025 venc. 15/10/2025 com IGPM+1%+2% | §26 (`"(c) Honorários advocatícios de 20%..."`) | 🔴 ângulo 4 monetário (pós-marco deve ser SELIC pura) |

**Achado bônus na peça-base** (não-plantado, mas relevante): §15 e §24 já aplicam IGPM+1%+2% sistêmico para **todas as 179 faturas** até 20/03/2026 sem distinção pré/pós-Lei 14.905/2024. Provável que outras notificações Modelo A geradas pelo mesmo template compartilhem esse furo — pendência de auditoria pré-protocolo.

### 5. Critério de aceitação calibrado
- **PASSA**: 3 furos plantados pegos com âncora textual + verdict `BLOQUEADA_FUROS_CRITICOS`. Achados bônus com âncora textual contam como reforço positivo.
- **CRÉDITO PARCIAL**: 2/3 furos com âncora, ou 3 só por categoria genérica sem âncora textual.
- **FALHA**: <2 furos pegos, ou peça aprovada, ou plantados marcados como 🟡 em vez de 🔴.

### 6. Falha do harness na invocação
Tentativa de invocar `Agent(subagent_type="adversarial-meta-auditor", ...)` retornou:
```
Agent type 'adversarial-meta-auditor' not found.
Available agents: claude-code-guide, code-simplifier:code-simplifier, Explore,
feature-dev:code-architect, feature-dev:code-explorer, feature-dev:code-reviewer,
general-purpose, Plan, statusline-setup
```
Lista exclui qualquer custom de `.claude/agents/`. Hipótese: o harness Claude Code carrega o registro de subagents na inicialização da sessão — agents criados em runtime não são re-descobertos. **Teste falsificável NÃO RODOU nesta sessão.**

## Decisões tomadas
1. **Pivot `.docx` → `.md`** para a peça de teste — subagent não tem `Bash`, `Read` não abre binário, e o subagent declara aceitar `.md`.
2. **Não invocar `general-purpose` com prompt mimicado** — fraudaria o teste falsificável (testaria conversa, não o subagent isolado em contexto novo).
3. **Verificação de skills por filesystem ≠ system-reminder** — system-reminder pode listar skill em path frágil ou de lixo (`skills_lixo_*` aparece como disponível). Fonte de verdade é `~/.claude/skills/`.
4. **Re-leitura da peça pós-plantio proibida** — preserva isolamento dos dois lados (Claude Code e subagent).
5. **Pular Etapas 2/3 da skill `fechamento-sessao`** (TASKS.md / CLAUDE.md manual) — não aplicáveis a este projeto: TASKS.md não existe na raiz; CLAUDE.md é auto-gerado por `auto_update_claude_md.py`.

## Descobertas
1. **Skill movida para lixo durante a sessão**: `agente-prescricional-defensivo` reclassificada para `Desktop\skills_lixo_20260507-1550\` (timestamp 15:50 — concomitante à sessão). Sugere faxina de skills paralela.
2. **Decreto 53.464/2026** confirmadamente vigente desde 30/01/2026, substitui Decreto 51.084/2025, menciona PRODAM, tem 4 exceções documentadas.
3. **REsp 1.963.067/MS — relatoria confirmada**: Min. Nancy Andrighi, 3ª Turma, 05/04/2022 (unicidade da interrupção prescricional, Art. 202 caput CC).
4. **Furo monetário sistêmico** em notificações DETRAN existentes — template aplica IGPM+1%+2% para todas as 179 faturas, ignora marco Lei 14.905/2024.
5. **Limitação do harness**: `.claude/agents/` carrega só na inicialização. Cada novo subagent precisa de restart de sessão antes de ser invocável.
6. `python-docx` 1.2.0 disponível no ambiente local (não está em `requirements.txt`, mas instalado).

## Pendências
1. 🔴 **CRÍTICA — Teste falsificável do subagent não rodou.** Necessário reabrir sessão Claude Code para o harness registrar `adversarial-meta-auditor`. Após reabrir, invocar com a peça em `DOCUMENTOS_GERADOS/_TESTE_AGENT/teste_adversarial_20260507.md` e profile DETRAN. Comando preparado:
   ```
   Agent(subagent_type="adversarial-meta-auditor",
         prompt="Audite DOCUMENTOS_GERADOS/_TESTE_AGENT/teste_adversarial_20260507.md contra perfil DETRAN. 7 ângulos + anti-alucinação. Reporte 3 buckets + verdict.")
   ```
2. 🟡 **PENDENTE — Etapas 2-5 do plano de automação** (validate_profiles_json, mcp-server-time, enforce_spcf_rate_limit, block_float_money) — gated na validação da etapa 1.
3. 🟡 **PENDENTE — Auditar peças DETRAN existentes** com Modelo A quanto ao furo sistêmico monetário (IGPM+1%+2% sem segmentação Lei 14.905/2024) — antes de protocolar qualquer uma.
4. 🟢 **INFORMATIVA — Documentar em `.claude/napkin.md`**: subagents customizados precisam de restart de sessão após criação.

## Arquivos criados
- `.claude/agents/adversarial-meta-auditor.md` — subagent meta-adversarial, 7 ângulos + anti-alucinação, read-only (`Read, Grep, Glob`)
- `DOCUMENTOS_GERADOS/_TESTE_AGENT/teste_adversarial_20260507.md` — peça de teste falsificável (notificação Modelo A DETRAN com 3 furos plantados)
- `relatorios/CHANGELOG_SESSAO_2026-05-07_setup_subagent_adversarial.md` (este arquivo)

## Arquivos modificados
- Nenhum arquivo do projeto além dos criados acima.

## Arquivos NÃO modificados (por design)
- `CLAUDE.md` — auto-gerado por `scripts/auto_update_claude_md.py`; `profiles.json` intocado nesta sessão.
- `.claude/settings.json` — etapas 2-5 não rodaram; sem motivo para mexer.
- `.mcp.json` — etapa 3 (mcp-server-time) ainda não rodou.

## Próxima sessão — primeiro comando
Reabrir Claude Code no diretório do projeto. Validar que o subagent aparece listado. Se sim, invocar o teste falsificável diretamente. Se não, sanity-check do frontmatter do `.md` antes de seguir.
