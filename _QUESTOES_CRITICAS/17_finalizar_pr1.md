# 17 — Finalizar PR #1 → ✅ RESOLVIDA via caminho B (PR #11)

> Status: ✅ RESOLVIDA — PR #11 mergeado (merged:true; merge-commit cdaa7b5 = tip de main). Nada pendente.
> Aberta em: 2026-05-30 (sessão cloud encerrada antes de executar o rebase)
> Resolvida em: 2026-05-30 (sessão local — caminho B executado: PR #11 aberto, #1 fechado)
> Mergeada em: 2026-05-30T21:17 (PR #11 mergeado por Gabrielmar95; `main` avançou para cdaa7b5)
> Tipo: handoff de sessão / plano de execução
> Severidade: 🟢 baixa (desfecho aplicado e mergeado em `main`)
> Predecessor: `16_handoff_proxima_sessao.md` (parte das recomendações já tratadas: hook PreCompact em PR #10)

## DESFECHO (2026-05-30) — caminho B, NÃO o rebase

O plano de rebase abaixo (caminho A) **não foi executado**. O advogado optou pelo
**caminho B**: em vez de rebasar o PR #1 sujo e force-pushar, partir do `main` atual
(pós-#10, `487d569`) numa **branch limpa** e abrir um **PR novo**.

| Item | Resultado |
|---|---|
| Branch nova | `claude/reorg-claude-md-enxuto-20260530` (a partir de `487d569`) |
| Commit | `a3979c5` — gerador com `from prodam_utils import fmt_brl` (DRY/SSOT restaurado) + 4 `.md` regenerados do `profiles.json` vivo |
| **PR #11** | **OPEN**, `mergeStateStatus: CLEAN`, **2/2 required checks verdes** (`Run tests + validate scripts (3.12)` + `Bloqueia Teori como relator do REsp 793.969`) |
| **PR #1** | **CLOSED** (comentário referenciando #11 como substituto) |
| Regressão Issue 11 | **NÃO herdada** — o caminho B nasceu do gerador do `main` (que já importava `fmt_brl`), corrigindo a regressão que o PR #1 tinha |

**Por que caminho B venceu o A:** o rebase (A) herdaria a regressão DRY do PR #1 (cópia
local de `def fmt_brl`) e exigiria `git push --force-with-lease` numa branch publicada
(operação destrutiva). O caminho B é aditivo (branch nova, sem force), e regenera os `.md`
do `profiles.json` vivo — métricas atuais, sem o drift de 24/05 do PR #1.

**Decisões pendentes da seção homônima abaixo — como ficaram:**
1. Regressão Issue 11 → **resolvida na origem** (caminho B partiu do gerador correto do `main`); não há followup a abrir.
2. Anotações `napkin.md` ("diretriz #3" / "nota cloud vs local") → **preservadas** (estavam no `main`; caminho B não as toca, só traz o diff de 6 linhas do PR #1 via `git checkout`).
3. Quando mergear PR #10 → **já mergeado** (`487d569`), foi a base do caminho B.

**Único pendente:** mergear o PR #11 — trava no "OK, merge" explícito do advogado
(`merge_method=merge`, convenção). Sem isso, #11 permanece OPEN.

> ⚠️ O plano de rebase a seguir é **histórico** (caminho A preterido). Mantido como
> registro da deliberação. NÃO executar.

---

## TL;DR (histórico — caminho A, NÃO executado)

- Sessão cloud anterior encerrou **com o PR #1 ainda aberto** (missão final pendente).
- **PR #10** (hook PreCompact, branch `claude/precompact-hook`) está **VERDE / clean / 3-3 CI success**, aberto, esperando OK pra merge. Decidido NÃO mergear na sessão anterior.
- **PR #1** (`reorg-claude-md-20260526`) tem **plano de finalização totalmente investigado e revisado** abaixo (estratégia: rebase em main, `--theirs` nos 3 conflitos, validação local).
- Esta issue é o ponto de retomada. Próxima sessão lê este arquivo e segue.

## Estado dos PRs (verificado em 2026-05-30)

| PR | Estado | head | base | Observação |
|---|---|---|---|---|
| #1 | open / dirty | `aa34cf0` | `a6b746c` (24/05) | 39 ahead, 1 behind. 3 arquivos conflitantes (verificado via `git merge-tree --write-tree`). |
| #10 | open / clean / 3-3 verde | `bb1ad84` | `e081ae0` | Hook PreCompact. Mergeio quando der OK explícito. |
| #4, #8, #9 | ✅ merged | — | — | Mergeados em sessões anteriores. |

## Fatos verificados (com hashes e comandos reais)

### Conflitos REAIS do PR #1
`git merge-tree --write-tree --messages origin/main origin/reorg-claude-md-20260526` mostrou 3 conflitos content-level:
- `.claude/napkin.md`
- `CLAUDE.md`
- `scripts/auto_update_claude_md.py`

### Mudanças em `main` (pós merge-base `a6b746c`) que afetam os 3 arquivos

**`scripts/auto_update_claude_md.py`** — 3 commits em main tocaram:
- `7f2dd69` — remove gate de fluxo + para de regenerar SAFEGUARDS no script
- `eaa36fb` — refactor(issue-11): DRY — importa `fmt_brl` de `prodam_utils` (Regra #16)
- `e447c46` — fix path latente prodam_utils + Regra #15 SSOT

Stats: **main = +5/−23 (líquido)** vs **PR = +435/−301 (reescrita maior)**.

**`CLAUDE.md`** — 1 commit em main: `7f2dd69` (regera CLAUDE.md sem "Modo manual" mas COM SAFEGUARDS expandida — 228 linhas vs 108 da PR).

**`.claude/napkin.md`** — 3 commits em main: `9231cd8` (diretriz #3 — "validar/testar antes de ação definitiva"), `7f2dd69`, `a505600` (nota "cloud vs local").

### Custo real de escolher `--theirs` em cada arquivo

- **`CLAUDE.md`**: irrelevante — é REGENERADO pelo script. Pegar PR é OK; próximo `/sincronizar-prodam` produz o enxuto.
- **`scripts/auto_update_claude_md.py`** ⚠️ **PERDA REAL**: a PR não tem o refactor `from prodam_utils import fmt_brl` (Issue 11 — DRY). A PR tem sua própria `fmt_brl` local (linha 255). Funcionalmente equivalente, mas regride a Issue 11. **Decisão pendente**: aceitar regressão + abrir issue followup, OU resolver manualmente pegando o import de main e o resto da PR (cherry-pick parcial — mais complexo).
- **`.claude/napkin.md`** ⚠️ **PERDA MENOR**: a PR não tem a "diretriz #3" nem a "nota cloud vs local". Vale aceitar e re-adicionar pós-merge se importante.

### Outros fatos validados
- **`--theirs` durante rebase** = a branch sendo replayed (= a PR). Sintaxe correta no plano.
- **Pre-commit hook** (`.pre-commit-config.yaml`: ruff E9,F63,F7,F82 em scripts/) **NÃO instalado no cloud** (`.git/hooks/pre-commit` ausente). Não bloqueia rebase no cloud. **Pode** bloquear se Gabriel rodou `pre-commit install` no local.
- **Script da PR compila**: `py_compile` OK (684 linhas, blob sha256 verificado: `2886d205d66e41436c0e25fea18eaa4c1727d0af1558e60d6800eaed0c8b2aaa`).
- **`profiles.json` AUSENTE no cloud** → não dá pra rodar `auto_update_claude_md.py` aqui. Validação exige máquina local do Gabriel.
- **Branch protection ruleset 16958653** exige 2 checks: `Run tests + validate scripts (3.12)` + `Bloqueia Teori como relator do REsp 793.969`. Ambos rodam em PR.

## Plano de execução (próxima sessão segue daqui)

### Etapa 0 — Sair do `claude/precompact-hook` (cloud está nessa branch se for cloud novo)
```
git checkout main && git pull origin main
git fetch origin reorg-claude-md-20260526
git rev-parse origin/reorg-claude-md-20260526   # esperado: aa34cf036da30da3670cdba46c634efdddb6676f
```

### Etapa 1 — Checkout + ponto de restauração
```
git checkout -b reorg-claude-md-20260526 origin/reorg-claude-md-20260526
git tag rescue/reorg-pre-rebase
```

### Etapa 2 — Rebase + resolução
```
git rebase origin/main
# Para CADA arquivo conflitante (esperados: .claude/napkin.md, CLAUDE.md, scripts/auto_update_claude_md.py):
git checkout --theirs <arquivo>
git add <arquivo>
git rebase --continue
```

### Etapa 3 — Validação pós-rebase no cloud
```
python3 -m py_compile scripts/auto_update_claude_md.py
python3 -m pytest tests/ -q     # esperado: 136 passed
```

### Etapa 4 — Force-push com lease (ancorado no SHA antigo)
```
git push --force-with-lease=reorg-claude-md-20260526:aa34cf036da30da3670cdba46c634efdddb6676f \
  origin reorg-claude-md-20260526
```

### Etapa 5 — CI verde no novo head
- `mcp__github__pull_request_read get pullNumber=1` → confirmar `mergeable_state: clean`.
- `mcp__github__pull_request_read get_check_runs pullNumber=1` → 2/2 success.
- Se CI vermelho: parar, reportar, NÃO mergear.

### Etapa 6 — Validação local pelo Gabriel
```powershell
cd C:\Users\gabri\Desktop\PROJETO_PRODAM
git fetch origin
git checkout reorg-claude-md-20260526
git pull --ff-only origin reorg-claude-md-20260526

py -3.12 scripts\auto_update_claude_md.py

Get-Content CLAUDE.md | Measure-Object -Line                                   # esperado ~108 linhas
Get-Item STATUS_DEVEDORES.md, WORKFLOW_COBRANCA.md, PLAYBOOK_ORGAOS_V2.md
git status --short                                                              # esperado: VAZIO
```
Critério de aceitação: `git status` limpo. Se mostrar diff → investigar com Gabriel.

### Etapa 7 — Merge via API com OK explícito
```
mcp__github__merge_pull_request
  pullNumber: 1
  merge_method: merge
  commit_title: "Merge pull request #1 from Gabrielmar95/reorg-claude-md-20260526"
  commit_message: "refactor(claude-md): root enxuto + 3 satelites; remove gate juridico (rebased)"
```

## Decisões pendentes pra próxima sessão

1. Aceitar regressão Issue 11 (perda do import `fmt_brl` de `prodam_utils` no script) e abrir issue followup? OU fazer cherry-pick parcial pra preservar?
2. Aceitar perda das anotações napkin "diretriz #3" + "nota cloud vs local"? OU re-adicionar em commit pós-merge?
3. Quando mergear PR #10 (hook PreCompact)? Antes ou depois do PR #1?

## Frase pra abrir o próximo chat

> Continuação da sessão anterior. Leia `_QUESTOES_CRITICAS/17_finalizar_pr1.md` integralmente. Confirme HEAD de origin/main com `git log -1 origin/main`. Pergunte se prossigo com o rebase do PR #1 conforme as 7 etapas, ou se prefiro mergear o PR #10 (hook PreCompact, verde) primeiro. Não execute nada sem OK explícito.

## O que NÃO foi feito na sessão de origem (intencional)

- PR #10 não foi mergeado (decidido esperar).
- Rebase do PR #1 não foi executado (sessão encerrou antes; plan mode estava ativo).

## Limpeza de housekeeping (opcional, próxima sessão)

- Branches deletáveis (já 100% em main): `claude/docs-issue16-handoff`, `claude/jolly-heisenberg-mK6VU`.
- Branches a preservar: `claude/serene-hawking-nX853` (TTL 2026-06-29), `claude/precompact-hook` (PR #10 ativo), `reorg-claude-md-20260526` (PR #1 ativo).
