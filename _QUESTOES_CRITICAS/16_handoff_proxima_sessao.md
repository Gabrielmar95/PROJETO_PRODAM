# 16 — Handoff para próxima sessão (recomendações pendentes + sync com main)

> Status: 🟡 needs-human (decisão de prioridade do advogado)
> Aberta em: 2026-05-30 (sessão `988964a6`, branch `claude/serene-hawking-nX853`)
> Reaberta em: 2026-05-30 (sessão cloud sucessora — `_metadata` atualizado abaixo)
> Tipo: handoff de sessão / continuidade
> Severidade: 🟢 baixa (nada quebrado; tudo aqui é melhoria opt-in)
> Predecessor: `15_retomar_merge_pr4.md` (✅ RESOLVIDA no commit `15a2161`)

## TL;DR

Sessão `988964a6` (local) resolveu a causa-raiz do bloqueio de checkout (commit `15a2161`,
letra B + issue 15 marcada resolvida) **e abriu PR #8** com essa correção. Sessão cloud
sucessora confirmou: **PR #8 já está VERDE pra merge** (`mergeable_state: clean`, 3/3
checks success). Restaram **3 grupos de pendências**:

1. **Sync com main**: PR #8 aberto e verde, aguardando OK para `--merge`.
2. **Recomendações de automação** geradas pelo `claude-automation-recommender`
   (subagentes / MCP / hooks) — todas opt-in.
3. **Allowlist de permissões** do `fewer-permission-prompts` — nada aplicado ainda.

## §1 — Sync com `origin/main` (decisão imediata)

### Estado verificado em 2026-05-30 (cloud sucessora)

| Lado | SHA | Conteúdo |
|---|---|---|
| `origin/main` | `aded4b6` | merge commit PR #4 |
| `origin/claude/serene-hawking-nX853` | `15a2161` | destrack settings.local.json + issue 15 resolvida |
| **PR #8** | `15a2161 → aded4b6` | aberto, `mergeable_state: clean`, 3/3 checks ✅ |

**Diff do PR #8:** 3 arquivos, +31/−63 (a redução grande é a remoção do
`.claude/settings.local.json` do tracking — não é apagado do disco, só destracked).

### Caminhos restantes

| Caminho | Quando faz sentido | Risco |
|---|---|---|
| **A.** `mcp__github__merge_pull_request` `merge_method=merge` no PR #8 | Convenção do projeto = merge commit. PR já verde, é o desfecho natural. | Nenhum — fluxo padrão. |
| **B.** Esperar acumular mais commits, depois 1 PR só | Se a próxima sessão for adicionar mais arquivos pequenos no MESMO escopo | PR fica aberto mais tempo; branch acumula divergência. |
| **C.** Fechar PR #8 sem mergear (descartar `15a2161`) | Se a mudança for considerada "só local-machine, não merece main" | Issue 15 fica "resolvida só na branch", main não recebe a doc atualizada. |

**Recomendação**: **A** — merge agora via MCP. PR #8 está pronto, 3/3 verde, é decisão de 1 OK.

Comando (executar SOMENTE com "OK, merge" do advogado):

```
mcp__github__merge_pull_request
  owner: Gabrielmar95
  repo: PROJETO_PRODAM
  pullNumber: 8
  merge_method: merge
  commit_title: "Merge pull request #8 from Gabrielmar95/claude/serene-hawking-nX853"
  commit_message: "chore(git): destrastra settings.local.json + fecha issue 15"
```

⚠️ `merge_method=merge` (NÃO `squash`) — convenção do projeto.

## §2 — Recomendações de automação (do claude-automation-recommender)

Todas read-only até aqui — **nada foi criado**. Cada item exige OK explícito e (para subagentes) passar pelo `arquiteto-agents-prodam` como gate.

### 2.1 — Hooks (PostToolUse + PreCompact)

| Hook | Função | Por que faria sentido aqui |
|---|---|---|
| **PostToolUse: SSOT `profiles.json`** | Após Edit/Write em `profiles.json`, rodar `auto_update_claude_md.py` automaticamente | Hoje sincronização é manual; já houve drift entre profiles e CLAUDE.md |
| **PreCompact: handoff automático** | Antes do `/compact` consumir contexto, dump em `.remember/remember.md` | Hoje o handoff é manual (foi o que a sessão `988964a6` fez); automatizar evita esquecimento |

Local de instalação: `.claude/settings.json` (project-scoped). NÃO em `~/.claude/` (per constraint fewer-permission-prompts).

### 2.2 — MCP Server (2 opções mutuamente exclusivas)

| Opção | O que faz | Custo |
|---|---|---|
| **A. SQLite read-only** | Conecta `prodam.db` via driver MCP com `?mode=ro` | Baixo: 1 config no `.mcp.json`, zero código |
| **B. `mcp_prodam.py` próprio** | Server Python custom expondo `consultas.py` como tools MCP | Alto: 1 arquivo Python novo, manutenção, testes |

**Recomendação**: **A** — começa simples, valida se MCP de DB ajuda no fluxo. Se ajudar e a granularidade da query SQL não bastar, aí promove pra B.

### 2.3 — Subagentes (4 candidatos)

Cada um exige passar por `arquiteto-agents-prodam` antes de criar (gate anti-duplicação).

| Candidato | Função | Já existe algo parecido? |
|---|---|---|
| **`devedor-pipeline-runner`** | Auditar 1 devedor seguindo playbook DETRAN A+ (13 passos) | Não — `orgao_pipeline_completa.py` é script, não agent |
| **`prescricao-calculadora`** | Calcular prescrição por fatura (Art. 189+206 §5º I CC, marco vencimento) | A confirmar — Gabriel cogitou criar isso em sessão anterior |
| **`cadeia-documental-auditor`** | Validar 5 elos (Contrato+NE+NF+Atesto+Pagamento) por devedor | Não — hoje é coluna de score, não auditor dedicado |
| **`peticao-redator`** | Gerar minutas a partir de skill `_SKILLS/peticao-*` | Parcial — skills existem; agent que coordena, não |

**Pipeline sugerida** (Workflow tool): `discover devedores → for each: cadeia-auditor → prescricao-calculadora → adversarial-meta-auditor (já existe) → peticao-redator`.

## §3 — Allowlist `fewer-permission-prompts` (NÃO aplicada)

O scanner `C:\Users\gabri\AppData\Local\Temp\perm_scan.py` foi escrito mas **nunca rodado nem aplicado**. Razão: sessão derivou pra letra B antes.

**Para retomar**:
1. Rodar: `py -3.12 C:\Users\gabri\AppData\Local\Temp\perm_scan.py | Out-File -Encoding UTF8 perm_report.txt`
2. Inspecionar `perm_report.txt` — apresentar top-20 ao advogado.
3. Mergir em `.claude/settings.json` (project-scoped, NÃO `.local.json`, NÃO `~/.claude/`).
4. Filtros obrigatórios: read-only only; sem interpretadores (py/python/node); sem `npm run *`; sem `gh api *` curinga.

## §4 — Constraints carregadas (ainda valem)

- **PR #1** open por decisão; não tocar.
- Branch `claude/serene-hawking-nX853` TTL 2026-06-29.
- Git destrutivo confirmar antes (push força, reset hard, branch -D, rebase publicado).
- PDFs = prova: nunca apagar originais.
- Decimal sempre; float nunca (regra #16 do CLAUDE.md root).
- CSV `;` + utf-8-sig (BOM).
- PowerShell puro para user-facing; >948 bytes → temp `.ps1` ou `.py` via `py -3.12`.
- VS Code CLI: `code.cmd`, nunca `Code.exe`.
- claude-automation-recommender é read-only — não cria nada sozinho.
- **Cloud é efêmero** — `.remember/remember.md` NÃO existe no remoto; é local apenas. Issue 16 (este arquivo) é a fonte versionada equivalente.

## §5 — Referências

- Commit `15a2161` — `chore(git): destrastra .claude/settings.local.json + marca issue 15 resolvida`
- Commit `aded4b6` — merge commit do PR #4 em main
- Issue 15: [`15_retomar_merge_pr4.md`](15_retomar_merge_pr4.md) (✅ RESOLVIDA)
- PR #8: https://github.com/Gabrielmar95/PROJETO_PRODAM/pull/8 (open, verde pra merge)
- PR #1: https://github.com/Gabrielmar95/PROJETO_PRODAM/pull/1 (open intencional, NÃO tocar)
- Sessão de origem local: `988964a6-9955-47b9-adde-a7ee422d90b3`
- Sessão cloud sucessora: registrou este arquivo no remoto

## §6 — Como retomar (instrução para Claude da próxima sessão)

> Leia este arquivo (`_QUESTOES_CRITICAS/16_handoff_proxima_sessao.md`).
> Se estiver na sessão cloud, ele é a fonte primária (não há `.remember/remember.md` no remoto).
> Se estiver local, complemente com `.remember/remember.md` se existir.
>
> Confirme com `git log -1 --pretty='%h %s'` o HEAD atual.
> Verifique se PR #8 ainda está open: `mcp__github__pull_request_read get pullNumber=8`.
>
> Pergunte ao advogado qual prioridade quer atacar primeiro:
> (a) merge do PR #8 via MCP (§1 caminho A) — 1 OK basta;
> (b) hook PreCompact (§2.1) — alto valor, baixo custo;
> (c) MCP SQLite ro (§2.2 opção A) — médio valor, baixíssimo custo;
> (d) `arquiteto-agents-prodam` audita os 4 candidatos a subagente (§2.3);
> (e) `fewer-permission-prompts` (§3) — alto valor recorrente.
>
> NÃO execute nada sem OK explícito por item.
