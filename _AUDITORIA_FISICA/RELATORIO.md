# Auditoria Física PROJETO_PRODAM — Relatório Final

**Data:** 2026-05-10
**Branch worktree:** `worktree-auditoria-fisica-2026-05-10`
**Branch main commit pré-auditoria:** `e269f0d` (capturado em `_AUDITORIA_FISICA/baseline_head.txt`)

## Sumário executivo

Pipeline 3 camadas (sweep → classify → act) executou com sucesso. Inventário identificou 145 itens; classificador rotulou todos por regra determinística; 3 batches de mutação aplicados, todos reversíveis.

| Métrica | Valor |
|---|---|
| Itens inventariados | 145 |
| Limpezas aplicadas (3 batches) | OK |
| Tasks decididas para sessão futura | 47 (`NEEDS_HUMAN_DECISION`) |
| Commits criados (worktree) | 4 (`47273ae`, `4508239`, `50dcb4d`, `a11c5b5`) |
| Commits criados (main) | 1 (`99f9ee7`) |
| Pytest baseline | 49/49 → 59/59 (+10 novos) |

## Distribuição da classificação

| Label | Count | Destino |
|---|---|---|
| KEEP | 28 | nenhum |
| GITIGNORE | 50 | append `.gitignore` (Batch 1) |
| NEEDS_HUMAN_DECISION | 47 | sessão futura |
| MOVE_TO_SCRIPTS | 11 | `scripts/` (Batch 3a) |
| MOVE_TO_SCRIPTS_AD_HOC | 6 | `scripts/ad_hoc/` (Batch 3b) |
| ARCHIVE_TO_LEGACY | 3 | `_BACKUPS/relocados-2026-05-10/` (Batch 2) |

## Limpezas aplicadas

### Batch 1 — `.gitignore` endurecido
- **Commit (worktree branch):** `a11c5b5 chore(gitignore): endurecer regras (node_modules, *.bak, _AUDITORIA_FISICA)`
- **Regras adicionadas:** `*.backup`, `*.backup-*`, `*.bak-*`, `*.bak.*`, `_AUDITORIA_FISICA/` (5 novas; `node_modules/` e `*.bak` já existiam)
- **Verificação:** 50 ocorrências de `node_modules` em `detran_dashboard/` agora cobertas; `_AUDITORIA_FISICA/` agora gitignored
- **Verificação anti-regressão:** `git check-ignore` testou que `scripts/auditoria_fisica/sweep.py`, `scripts/auditoria_fisica/classify.py`, `tests/auditoria_fisica/*` NÃO foram afetados.
- **Reverter:** `git restore .gitignore` (em qualquer checkout)

### Batch 2 — `.bak` da raiz relocados
- **Mutação:** `Move-Item` no MAIN checkout (arquivos eram untracked, sem commit)
- **Origem:** `C:\Users\gabri\Desktop\PROJETO_PRODAM` (raiz)
- **Destino:** `C:\Users\gabri\Desktop\PROJETO_PRODAM\_BACKUPS\relocados-2026-05-10\`
- **Arquivos:** `.gitignore.backup-20260423-153153` (2613 B), `.mcp.json.bak-20260508-234719` (239 B), `CLAUDE.md.bak.20260510_022119` (14381 B)
- **Verificação:** sweep re-rodou e contou 0 itens `root_bak_file` no main
- **Reverter:** `Move-Item _BACKUPS\relocados-2026-05-10\* .` no main checkout

### Batch 3 — 17 scripts soltos consolidados
- **Commit (main branch):** `99f9ee7 chore(scripts): consolidar 17 scripts .py soltos da raiz em scripts/ e scripts/ad_hoc/`
- **5 tracked renames (via `git mv`):** `baixar_lacunas_spcf.py`, `gera_notificacao_ses_script.py`, `notificacao_simples.py`, `sincronizar_referencias.py`, `sincronizar_referencias_v2.py` → `scripts/`
- **12 untracked moves (via `Move-Item`):** 6 ad-hoc → `scripts/ad_hoc/`; 6 outros canônicos → `scripts/`
- **Colisão tratada:** `scripts/sincronizar_referencias_v2.py` já existia como cópia stale untracked (14297 B). Implementer fez backup → `scripts/sincronizar_referencias_v2.py.untracked-bak-20260510-054606` antes de colocar a versão tracked canônica (16942 B).
- **Verificação anti-regressão:** dependency hunt achou 0 imports diretos dos 17 scripts; pytest ainda 59/59.
- **Reverter:** `git revert 99f9ee7` (tracked) + `Move-Item` reverso (untracked)

## Itens deixados para sessão futura (`NEEDS_HUMAN_DECISION`)

47 `scattered_claude_md` espalhados em subpastas — política unificada exige decisão manual:
- Quais merecem permanecer (contexto-de-domínio legítimo)
- Quais são derivados de cópias antigas obsoletas
- Quais devem virar README.md ao invés de CLAUDE.md
- Possíveis duplicados a colapsar

## Concerns / observações secundárias

1. **Worktree × main checkout — tensão de design**
   - Worktree é thin clone (só arquivos tracked). 3 `.bak` raiz e ~12 scripts untracked NÃO existem no worktree por padrão.
   - Implementer da Task 1 copiou os 3 `.bak` para worktree raiz para o teste passar (test de smoke usa `repo_root = parents[2]`).
   - **Limpezas das Tasks 4 e 5 atuaram contra MAIN checkout** para alcançar o objetivo real da auditoria.
   - **Follow-up:** redesenhar `tests/auditoria_fisica/test_sweep.py` para usar fixture sintética em `tmp_path` ao invés de depender do filesystem real.

2. **Stale backup em `scripts/sincronizar_referencias_v2.py.untracked-bak-...`**
   - Cópia de 14297 B preservada após colisão. Recomendo inspeção e remoção depois de confirmar obsoleta.

3. **`PRODAM_DOCS/profiles.json` é gitignored por regra pré-existente** (`PRODAM_DOCS/` em `.gitignore` linha 99)
   - Independente desta auditoria, mas levanta questão: a SSOT do projeto NÃO está versionada. Discussão em sessão futura.

4. **Modificações pré-existentes em `gera_notificacao_ses_script.py` e `notificacao_simples.py`**
   - Eram `M` no git status original (antes da auditoria). `git mv` carregou a modificação para o novo caminho. Continuam unstaged em `scripts/<nome>.py`.
   - Não introduzidas por esta auditoria; herdadas do estado anterior do projeto.

5. **`STAGE_FOR_COMMIT` é label sem regra** em `classify.py`
   - Existe no set `LABELS` do test mas nenhuma regra emite. Reservado para uso futuro ou dead code. Decidir.

## Reversibilidade total

Todas as mutações são reversíveis:
- `git revert a11c5b5` (Batch 1)
- `git revert 99f9ee7` (Batch 3 tracked)
- `Move-Item _BACKUPS\relocados-2026-05-10\* .` (Batch 2)
- `Move-Item scripts\<nome>.py .` (Batch 3 untracked)
- `git restore .gitignore` (Batch 1)
- `_AUDITORIA_FISICA/` é gitignored agora; pode ser apagado sem efeito no repo.

## Próximos passos sugeridos

1. **Decidir política para 47 `scattered_claude_md`** — sessão dedicada com inventário item-a-item.
2. **Resolver triplicação semântica** — `DOSSIES/`, `DOSSIES_MULTIFORMATO/`, `DOCUMENTOS_GERADOS/` parecem ter overlap; consolidar.
3. **8 pastas legadas `_*` na raiz** — manter como estão ou consolidar em `_ARCHIVE/<data>/`?
4. **Avaliar saída de pastas grandes do git** — `OCR_PESQUISAVEL_CONSOLIDADO/` (6.5GB), `SPCF_EXTRACAO/` (7.2GB), `DETRAN_AUDITORIA_COMPLETA/` (3.2GB já gitignored?). LFS ou external storage?
5. **Discutir `profiles.json` gitignored** — SSOT do projeto deveria estar versionada?
6. **Test design refactor** — `test_sweep.py` deve usar fixture sintética, não filesystem real.
7. **Limpar stale backup** `scripts/sincronizar_referencias_v2.py.untracked-bak-20260510-054606`.
8. **Mergear branch worktree para main** — quando aprovado: `git checkout main; git merge worktree-auditoria-fisica-2026-05-10` (apenas se todas as 4 commits da branch worktree forem desejadas no main).

## Audit trail

- `_AUDITORIA_FISICA/baseline_git_status.txt` — git status pré-Task 0
- `_AUDITORIA_FISICA/baseline_head.txt` — HEAD pré-Task 0 (`e269f0d`)
- `_AUDITORIA_FISICA/inventario.json` — sweep inicial (145 itens)
- `_AUDITORIA_FISICA/inventario_pos_task4.json` — sweep pós-relocação .bak (142 itens, 0 root_bak_file)
- `_AUDITORIA_FISICA/classificacao.json` — classificação completa com `label` e `reason`
- `_AUDITORIA_FISICA/RELATORIO.md` — este arquivo
- Plano detalhado: `docs/superpowers/plans/2026-05-10-auditoria-fisica-prodam.md`

## Verificação final

```
Worktree branch tip: a11c5b5
Main branch tip:     99f9ee7
Pytest:              59/59 PASS
Main root:           sem .bak/.backup, sem 17 scripts soltos (0 .py na raiz)
scripts/:            26 .py
scripts/ad_hoc/:     6 .py
_BACKUPS/relocados-2026-05-10/: 3 arquivos
```
