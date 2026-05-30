# 15 — Retomar merge do PR #4 (branch protection misconfig)

> Status: ready-for-human / needs-admin
> Aberta em: 2026-05-30 (handoff cloud → local)
> Tipo: GitHub branch protection / merge bloqueado
> Severidade: 🟡 baixa (não bloqueia código novo; atrasa consolidação de 20 commits em `main`)
> Executor: Gabriel Mar (admin do repo Gabrielmar95/PROJETO_PRODAM)

## TL;DR

PR #4 (`claude/serene-hawking-nX853 → main`, head `31badab`) está com `mergeable_state: blocked`
mesmo com **2/2 checks reais verdes** (`PRODAM Tests / Run tests + validate scripts (3.12)` +
`Validador de citações jurídicas / Bloqueia Teori como relator do REsp 793.969`). Causa: a
branch protection rule de `main` exige um required status check chamado **`feat(janela-3.3)`**
que **não é nome de workflow nem de job** — é o título do commit `442c91c`
(`feat(janela-3.3): validador CI de citações jurídicas (anti-Teori-como-relator)`). Foi
configuração errada de sessão anterior (provavelmente confusão entre commit title e check
name). Nenhum sistema vai reportar status com esse nome → fica "Waiting for status to be
reported" pra sempre.

## Estado verificado (2026-05-30 ~02:00)

- **Branch local**: `claude/serene-hawking-nX853` @ `6cc1cb1` (cloud) — está **4 commits atrás**
  do remoto, que avançou pra `31badab` via "Update branch" feito na UI do GitHub
  (merge `main → branch`, sem conflito).
- **PR #4**: head `31badab`, base `efa9f7d`, 27 arquivos alterados, +1241/−235, 21 commits no
  GH (20 novos + o merge), `mergeable_state: blocked`.
- **PR #3** (`claude/jolly-heisenberg-mK6VU → main` @ `efa89b6`): aberto, ainda redundante
  com #4 (fechar APÓS o merge do #4).
- **PR #1** (`reorg-claude-md-20260526 → main` @ `aa34cf0`): aberto, `dirty`, **deixar aberto
  intencionalmente** (parte "remove gate jurídico" já entrou via #4, parte "root enxuto + 3
  satélites" é reorg estrutural a decidir depois).
- **CI no head `31badab`**: ✅ `Run tests + validate scripts (3.12)` (15s), ✅ `Bloqueia Teori`
  (5s), 🟡 `feat(janela-3.3)` *Waiting for status to be reported* (esse é o problema).
- **Pré-check de conflito local** (Etapa 0 do plano): SEM CONFLITO no merge `main → branch`.
- **Pytest local no cloud**: 136/136 passed em 1.09s.

## Causa

Required status check `feat(janela-3.3)` configurado em
`Settings → Branches → main → Require status checks to pass before merging`, mas o nome não
casa com nenhum workflow do `.github/workflows/`:

| Workflow YAML | Workflow name | Check name reportado em PR |
|---|---|---|
| `tests.yml` | PRODAM Tests | Run tests + validate scripts (3.12) |
| `validar_citacoes.yml` | Validador de citações jurídicas | Bloqueia Teori como relator do REsp 793.969 |
| `alerta_prescricao.yml` | Alerta diário de prescrição | (cron + push, não dispara em PR) |

Nenhum reporta como `feat(janela-3.3)`. O nome foi confundido com o título do commit `442c91c`.

## Próximos passos

### Passo 1 — Fix da branch protection rule (admin, ~3 min)

1. Abrir https://github.com/Gabrielmar95/PROJETO_PRODAM/settings/branches
2. Encontrar a rule de `main` → **Edit**
3. Em **"Require status checks to pass before merging"**:
   - **REMOVER** `feat(janela-3.3)` da lista
   - **(Opcional, recomendado) ADICIONAR** os 2 nomes corretos:
     - `Run tests + validate scripts (3.12)`
     - `Bloqueia Teori como relator do REsp 793.969`
4. **Save changes**
5. Voltar pro PR #4 e atualizar a página — `mergeable_state` vira `clean` em ~10s.

### Passo 2 — Squash and merge (admin, ~30s)

1. Clicar **"Squash and merge"**.
2. Editar o **título do squash commit** (literal abaixo, copiar e colar):

```
feat(janelas-2-3): Issue 10/11A/12T1 + cron + validador anti-Teori (20 commits)
```

3. Editar o **body do squash commit** (literal abaixo, copiar e colar):

```
Consolida 20 commits novos da branch claude/serene-hawking-nX853
(os outros 9 da branch já estão em main via d96340b "Janelas 0+1+3.1").

Marcos rastreáveis (cascata Teori→Delgado, correções monetárias, infra CI):
- 442c91c — feat(janela-3.3): validador CI anti-Teori-como-relator
- 253d264 — chore(janela-1.8): fecha cascata Teori→Delgado
- 8969ac8 — fix(janela-3.1): datetime.utcnow() → timezone-aware
- acbc6a4 — feat(janela-3.1): cron diário de prescrição
- 1b7ab06 — refactor(issue-10): fmt_brl strict-Decimal
- eaa36fb — refactor(issue-11): DRY Cat A — 4 scripts (~120 LOC)
- 6cc1cb1 — fix(issue-12-tier1): elimina float() em val_exig (SSOT)
- 7f2dd69 + 9c30963 — chore(gate-fluxo): remove + suaviza agents

Cobre também: 7 issues novas em _QUESTOES_CRITICAS/ (08-14),
hook SessionStart, atualização do PRECEDENTES_VERIFICADOS,
CI workflow validar_citacoes.yml.

Granularidade completa preservada em:
- PR #4
- Branch claude/serene-hawking-nX853 (viva por 30 dias após o merge)

Verificações pré-merge:
- pytest local 136/136 verde
- CI GitHub 2/2 verde no head 31badab
- Pré-detecção de conflito merge main→branch: sem conflito
```

4. **⚠️ DESMARCAR a checkbox "Delete branch"** antes de confirmar.
5. **Confirm squash and merge.**

### Passo 3 — Fechar PR #3 (Claude, via API, com seu OK)

Após o merge do #4, pedir pro Claude:

1. Ler `merge_commit_sha` do PR #4 via `mcp__github__pull_request_read get pullNumber=4`.
2. Comentar no PR #3 (`mcp__github__add_issue_comment`):
   > Supersedido por #4 — esta PR (`claude/jolly-heisenberg-mK6VU` @ `efa89b6`) contém os
   > mesmos 14 commits dos primeiros do #4, sem o commit `1b7ab06` (Issue 10) nem os 14
   > commits posteriores. PR #4 foi mergeado em `<merge_commit_sha real>` via squash. Manter
   > este aberto seria armadilha de merge duplo — fechando.
3. Fechar PR #3 (`mcp__github__update_pull_request state=closed pullNumber=3`).

**PR #1 NÃO é tocado** (decisão consciente — fica aberto pra revisita futura).

### Passo 4 — Verificação obrigatória pós-merge

- PR #4: `merged=true`, `merge_commit_sha` preenchido.
- CI verde no novo HEAD de `main` (`mcp__github__list_commits sha=main perPage=1` + check_runs).
- Working tree local limpa após `git pull origin main`.

### Passo 5 — Sync local e TTL da branch

```powershell
cd C:\Users\gabri\Desktop\PROJETO_PRODAM
git fetch origin
git checkout main
git pull origin main
git log -1 --pretty='%h %s'
# Esperado: <SHA-do-squash> feat(janelas-2-3): Issue 10/11A/12T1 + cron + validador anti-Teori (20 commits)
```

**TTL da branch `claude/serene-hawking-nX853`**: deletar em **2026-06-29** (30 dias após o
merge) via `git push origin --delete claude/serene-hawking-nX853` ou pela UI.

## Referências

- Plan file completo (cloud, efêmero): `/root/.claude/plans/cheerful-munching-shell.md` —
  conteúdo principal já replicado neste arquivo.
- PR #4: https://github.com/Gabrielmar95/PROJETO_PRODAM/pull/4
- PR #3: https://github.com/Gabrielmar95/PROJETO_PRODAM/pull/3
- PR #1: https://github.com/Gabrielmar95/PROJETO_PRODAM/pull/1
- Branch protection settings: https://github.com/Gabrielmar95/PROJETO_PRODAM/settings/branches
- CLAUDE.md regra #13 (cascata Teori→Delgado) — motivo do validador anti-Teori.
- CLAUDE.md regra #16 (Decimal, nunca float) — motivo das Issues 10/11/12.

## Como retomar comigo localmente (instrução pro Claude da próxima sessão)

> Leia este arquivo (`_QUESTOES_CRITICAS/15_retomar_merge_pr4.md`) e me oriente nos Passos
> 1→5. Quando eu confirmar que o merge foi feito, execute os Passos 3 e 4 via tools MCP do
> GitHub (read merge_commit_sha + comment supersede + close PR #3). Não toque no PR #1.
