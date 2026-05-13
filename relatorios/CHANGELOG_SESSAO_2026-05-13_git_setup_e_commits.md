# Changelog — Sessão 2026-05-13: Setup do Git e organização dos commits

## Objetivo

Organizar 56 arquivos `untracked` acumulados no repositório `PROJETO_PRODAM` em commits semânticos, com revisão humana arquivo-a-arquivo antes do `git add`. Gate manual obrigatório: nenhum `git add` sem `"OK, commita"` literal; nenhum `git push backup main` sem `"OK, push"` literal. Proibição estrita de `git add .`.

## 7 commits da sessão (em ordem cronológica)

| # | Hash | Mensagem curta | Δ |
|---|------|----------------|---|
| 1 | `d032c64` | `chore(gitignore): ignorar CLAUDE.md de subpastas (logs claude-mem)` | +6 |
| 2 | `b1bc028` | `chore(config): adicionar configs raiz do projeto` | +170 |
| 3 | `c48351d` | `docs(.claude): adicionar agents curados e runbook napkin` | +444 |
| 4 | `e76b09a` | `docs(relatorios): adicionar auditoria de ecossistema + 4 changelogs de sessao` | +610 |
| 5 | `046062b` | `feat(auditoria_DE): adicionar 6 scripts read-only de triagem prescricional` | +590 |
| 6 | `bae4da7` | `feat(ad_hoc): adicionar 6 scripts de classificacao e triagem de PDFs` | +1.641 |
| 7 | `442ee41` | `feat(scripts): adicionar 11 utilitarios soltos (skills, PDFs, relatorios, git)` | +3.493 |

**Total**: 36 arquivos versionados, +6.954 linhas, todos com push sincronizado para `backup/main` (`C:/Users/gabri/git-backups/PROJETO_PRODAM.git`).

## Saldo das 56 entradas originais

- ✅ **36 commitadas** (4 + 3 + 5 + 6 + 6 + 11 + 1 do .gitignore)
- 🗑️ **1 apagada do disco**: `DETRAN_AUDITORIA/CLAUDE.md` (continha "R$4,4M + DETRAN" em texto plano — log do claude-mem)
- 🚫 **17 ignoradas por regra**: dumps `<claude-mem-context>` em subpastas (cobertos pela nova regra `**/CLAUDE.md`)
- ⏸️ **2 deferidas para próxima sessão** (ver abaixo)

## Decisões tomadas

### D1 — Opção A para o `napkin.md` (Grupo 3)
**Contexto**: `.claude/napkin.md` linha 10 contém `SES/SUSAM prescreve 2026-08-31 (113 dias) — R$ 14.748.048,96`.

**Decisão**: commitar como está. Justificativa: o mesmo valor já vive no `CLAUDE.md` raiz canônico (gerado por `auto_update_claude_md.py`) e em `AUDITORIA_COBERTURA_DOCUMENTAL.md` (já tracked há tempo). Cortar agora seria teatro de segurança — não-segurança real. Aplicado consistentemente nos Grupos 3 e 4.

### D2 — Apagar `DETRAN_AUDITORIA/CLAUDE.md` do disco antes do `.gitignore`
**Contexto**: o arquivo era log do plugin claude-mem com "R$4,4M em DETRAN_EMPENHOS.csv" + nome de devedor em texto plano. Valor financeiro NÃO replicado em outros arquivos versionados (diferente do napkin).

**Decisão**: `Remove-Item DETRAN_AUDITORIA/CLAUDE.md` ANTES de adicionar `**/CLAUDE.md` ao `.gitignore`. Princípio: `.gitignore` só impede tracking futuro — não tira o arquivo do filesystem, onde pode vazar por backup automático, screenshot, indexação local ou compartilhamento acidental. **Dado sensível em texto plano = remover do disco; `.gitignore` só protege contra commits futuros.**

### D3 — Regra `**/CLAUDE.md` com exceção `!/CLAUDE.md` no `.gitignore`
**Contexto**: 19 dos 20 CLAUDE.md untracked eram stubs vazios do plugin claude-mem (`<claude-mem-context></claude-mem-context>`), regenerados automaticamente em sessões futuras.

**Decisão**: bloquear `**/CLAUDE.md` (todos os CLAUDE.md em subpastas) e fazer exceção `!/CLAUDE.md` (preservar o canônico raiz, regenerado por `auto_update_claude_md.py`). Substitui o trabalho repetitivo de inspecionar cada novo CLAUDE.md surgido em sessões futuras.

### D4 — `scripts/detalhamento_faturas.py` adiado por bug F821
**Contexto**: 5 erros F821 (`Undefined name 'ws'`) nas linhas 292-329. Variável `ws` (worksheet do openpyxl) usada antes de ser definida. Bug pré-existente, documentado em memória 2026-05-12 (ID 576).

**Decisão**: opção (c) — excluir o arquivo do Grupo 7. Razão: o pre-commit `ruff check` aborta o commit inteiro se algum arquivo no stage tem erro de lint. Excluí-lo do Grupo 7 desacopla o bug do escopo limpo. Fix dedicado em sessão futura, após leitura do contexto completo das linhas 280-340 para identificar onde inserir `ws = wb.create_sheet("CONSOLIDADO")`.

## 2 untracked restantes (retomada na próxima sessão)

```
?? DOCUMENTOS_GERADOS/_TESTE_AGENT/
?? scripts/detalhamento_faturas.py
```

### `DOCUMENTOS_GERADOS/_TESTE_AGENT/` (diretório)
- **Status**: ⚠️ pasta listada como **diretório sensível** no `~/.claude/CLAUDE.md` global (gate jurídico aplica).
- **Hipótese provável**: contém `teste_adversarial_20260507.md` (peça de teste falsificável com 3 furos plantados — notificação Modelo A DETRAN sintética), citado no `CHANGELOG_SESSAO_2026-05-07_setup_subagent_adversarial.md` já commitado.
- **Próxima ação**: rodar varredura padrão (`Get-ChildItem` recursivo + grep R$/CNPJ/devedores + Read header de cada arquivo). Se for teste sintético sem dado real, padrão de commit dos grupos anteriores. Se tiver dado real de devedor, tratar caso a caso.

### `scripts/detalhamento_faturas.py` (702 linhas)
- **Status**: bug F821 conhecido — 5 ocorrências de `ws` undefined nas linhas 292, 323, 325, 326, 329.
- **Fix proposto** (carece confirmação por leitura do contexto): inserir `ws = wb.create_sheet("CONSOLIDADO")` ou equivalente antes da linha 292. Verificar se `wb = Workbook()` já existe acima.
- **Próxima ação**: Read linhas 270-340, propor patch mínimo, gate manual, commit dedicado: `fix(scripts): corrigir F821 em detalhamento_faturas.py (ws undefined)`.

## Follow-ups identificados (não tratados nesta sessão)

### F1 — `scripts/ad_hoc/gerar_memorial_preliminar_ses.py` (já tracked, fora do escopo desta sessão)
Contém CNPJ SES/SUSAM `00.697.295/0001-05` + múltiplos valores monetários hardcoded:
- Fatura excluída: `id 122703 (R$ 29.001,42)`
- Principal bruto Tier 1, Tier 2, total atualizado
- Honorários 20% explícitos

Detectado durante a varredura do Grupo 6. Não bloqueia esta sessão (já está no repo desde antes).

### F2 — `scripts/ad_hoc/gerar_trd_ses_docx.py` (já tracked, fora do escopo desta sessão)
Contém CNPJ PRODAM `04.407.920/0001-80` + CNPJ SES/SUSAM `00.697.295/0001-05` + valores hardcoded:
- `Principal bruto: R$ 4.783.356,52`
- `Total atualizado SELIC: R$ 8.230.061,40`
- Memorial de cálculo com fator SELIC série BCB 4390

Detectado durante a varredura do Grupo 6. Não bloqueia esta sessão (já está no repo desde antes).

### Risco e mitigações futuras (apenas se algum dia repo virar público)
Ambos F1 e F2 são scripts de geração de documentos jurídicos para um cliente real (SES/SUSAM). Enquanto o repo for **local/privado** com remote único no `backup/main` em `C:/Users/gabri/git-backups/`, a exposição é equivalente à do `CLAUDE.md` raiz canônico (que também tem CNPJ PRODAM, R$ 83M total exigível e TOP 10 devedores com valores). Padrão coerente.

Se o repo for tornado público ou compartilhado em algum momento, considerar:
1. **Refatorar para ler de `profiles.json` em runtime** (que já está no `.gitignore` desde 2026-04-20) — elimina o hardcode mas exige edição cuidadosa
2. **`git filter-repo`** para remover do histórico — destrutivo, exige force-push, mantém os arquivos no working tree mas limpa o passado
3. **Mascarar valores** com placeholders + script de hidratação local — preserva código mas perde executabilidade direta

Decisão pendente, sem urgência.

## Padrões consolidados nesta sessão

1. **Varredura padrão antes de cada `git add`**: contagem de linhas + `Get-ChildItem` + grep dos 13 devedores (DETRAN, SEDUC, SES/SUSAM, SUSAM, SSP, SEAD, SEJUSC, FUHAM, FHAJ, BRADESCO, CETAM, SALUX, SEDECTI, AADESAM) + R$ + CNPJ + Read das 25 primeiras linhas de cada arquivo.
2. **`pre-commit run ruff-check --files <paths>` com paths explícitos**: o glob `*.py` é ignorado pelo pre-commit ("no files to check Skipped"); precisa listar arquivo por arquivo. Aprendizado do Grupo 5.
3. **Commit via `_COMMIT_MSG.tmp` + cleanup com `;`**: `git add ... && git commit -F _COMMIT_MSG.tmp ; Remove-Item _COMMIT_MSG.tmp -Force ; git status --short`. O `;` garante cleanup mesmo se o commit falhar; o `&&` evita commitar com arquivos não-staged.
4. **Co-Authored-By em todos os commits**: `Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.
5. **Mensagens de commit sem acentos**: padrão herdado dos commits anteriores no repo (subject + body em ASCII puro). Documentação em `.md` mantém acentos.
6. **2 gates separados por commit**: `"OK, commita"` para `git add` + `git commit`; `"OK, push"` para `git push backup main`. Permite revisão entre etapas.

## Estado final do repositório

- `main` em `442ee41` (HEAD)
- `backup/main` em `442ee41` (sincronizado)
- Working tree: 2 untracked (ver retomada acima); nenhum modificado; nenhum staged
- 7 commits adicionados nesta sessão
