# CHANGELOG — Sessão 2026-05-26 — Consolidação CLAUDE.md

> **Branch:** `reorg-claude-md-20260526`
> **Plano executado:** `C:\Users\gabri\.claude\plans\bright-percolating-cat.md`
> **Backup:** `_BACKUPS/2026-05-26_consolidacao_claude_md/`

## Objetivo

Reduzir o `CLAUDE.md` raiz (auto-gerado) de ~200 linhas para ~120 linhas, distribuindo o conteúdo em 3 satélites, corrigir 5 bugs auditados e remover o **gate jurídico / safeguard anti-alucinação** em 5 locais, **preservando** as proteções de prova física (anti-delete PDF, validador `profiles.json`, `.gitignore` de `PRODAM_DOCS/`).

## Decisões aprovadas

| # | Item | Decisão |
|---|------|---------|
| 1 | Arquitetura do gerador | Editar `scripts/auto_update_claude_md.py` (manter, não deletar) |
| 2 | Estratégia | Root enxuto + 3 satélites gerados pelo mesmo script |
| 3 | Gate jurídico / safeguard anti-alucinação | Remover em **todos os 5 locais** |
| 4 | Proteções de prova física | **Manter** (escopo distinto) |
| 5 | Fatos jurídicos verdadeiros | **Migrar** como conhecimento neutro |

## Bugs corrigidos no CLAUDE.md raiz

| # | Bug | Fix |
|---|-----|-----|
| 1 | SES/SUSAM aparecia R$ 14,7M (texto) vs R$ 4,78M (TOP 10) | Re-calculado de `profiles.json` → único valor R$ 4.783.356,52 |
| 2 | `PLAYBOOK_ORGAOS_V2.md` citado mas inexistente na raiz | Criado como satélite gerado pelo script |
| 3 | SSP "40 dias" hardcoded (era 35 dias reais em 2026-05-26) | Calculado dinamicamente via `hoje() = 2026-05-26` |
| 4 | `config_prodam.py` referenciado como ativo, mas é fantasma | Removido como ativo; mantido apenas como warning ("NÃO criar sem auditoria") |
| 5 | Seção PLUGINS volátil + global/local não distinguidos | Removida; pontero para `~/.claude/CLAUDE.md` (instruções pessoais) |

## Arquivos gerados (output do `auto_update_claude_md.py`)

| Arquivo | Linhas | Conteúdo |
|---------|--------|----------|
| `CLAUDE.md` (raiz) | ~93 | 10 seções enxutas: identidade, status, alertas, regras (18), hierarquia, convenções, mapas, comandos |
| `STATUS_DEVEDORES.md` | 91 | Tabela com 70 devedores ordenados por exigível; semáforo prescrição 🔴/🟠 |
| `WORKFLOW_COBRANCA.md` | ~50 | Pipeline F0→F6 (gates documentais, skills, prazos) |
| `PLAYBOOK_ORGAOS_V2.md` | ~108 | 13 passos validados no DETRAN (A+ 94/100); score composto |

## Remoção do gate / safeguard em 5 locais

### 1. `scripts/auto_update_claude_md.py`
- Removidas as seções "SAFEGUARDS", "Modo manual obrigatório" e "PLUGINS INSTALADOS"
- Removida a regra "anti-alucinação dura" (#17 antiga)
- **Mantida** a regra #13 (REsp 793.969/RJ, Min. José Delgado) como **fato jurídico**, não como gate

### 2. `~/.claude/CLAUDE.md` (instruções pessoais)
- Removido o bloco "Anti-alucinação jurídica"
- Removido o bloco "Lei 3.683/2012 não regula RPV"
- **Mantido**: identidade, PowerShell, Decimal, PDF, "Cuidados com material jurídico" (lembrete, não bloqueio), git destrutivo, `@./rules/ambiente-windows.md`

### 3. Memórias persistentes (`~/.claude/projects/.../memory/`)
- **Deletadas (4)**:
  - `feedback_modo_manual_juridico.md`
  - `feedback_parecer_humano_areas_nao_curadas.md`
  - `reference_resp_793969_relator.md` (fato migrado para regra #13)
  - `reference_lei_am_rpv.md` (fato migrado para regra #14)
- **Mantida (1) — decisão limítrofe**:
  - `feedback_padrao_citacao_lei_estadual.md` — é convenção de citação ("Lei AM 2.748/2002" e não "Lei 2.748/2002"), **não** é gate anti-alucinação. Útil mesmo sem o safeguard.

### 4. `MEMORY.md` (índice)
- 4 linhas-índice removidas (correspondentes às memórias deletadas)
- Linha de `feedback_padrao_citacao_lei_estadual.md` preservada

### 5. `.claude/napkin.md`
- Removida regra antiga "Gate documental obrigatório... invocar skill `decisao-documental-prodam` + `guardrails-anti-alucinacao`" (linha 56-57)
- Atualizada referência: "ver `CLAUDE.md` seção SCORE COMPOSTO" → "ver `PLAYBOOK_ORGAOS_V2.md` seção SCORE COMPOSTO"
- **Mantida** linha 71: "PDFs são provas jurídicas — NUNCA apagar originais"

## Fatos jurídicos migrados (NÃO sumiram — viraram conhecimento neutro em "Regras Jurídicas")

| Fato | Onde está agora |
|------|-----------------|
| REsp 793.969/RJ = título executivo, Rel. p/ acórdão **Min. José Delgado** (Teori Zavascki foi vencido) | CLAUDE.md regra #13 |
| RPV/AM = 20 SM, **Lei AM 2.748/2002** (não Lei 3.683/2012) | CLAUDE.md regra #14 |
| FUHAM = Fundação Alfredo da Matta ≠ FHAJ = Fundação Hospital Adriano Jorge | CLAUDE.md regra #8 |
| Fee = 20% sobre créditos recuperados (não 30%) | CLAUDE.md regra #14 + IDENTIDADE |

## Proteções de prova física **mantidas intactas** (escopo distinto, não tocadas)

- `.claude/hooks/block_pdf_delete.ps1` — hook bloqueia delete de PDFs
- `.pre-commit-config.yaml` — ruff-check + validador `profiles.json`
- `.gitignore` — `PRODAM_DOCS/` (25,4 GB de PDFs) fora do repo
- `.claude/napkin.md` linha 71 — "PDFs nunca apagar"

## Arquivos editados manualmente (fora do gerador)

| Arquivo | Edição |
|---------|--------|
| `~/.claude/CLAUDE.md` | Removido bloco anti-alucinação + Lei 3.683/2012 |
| `~/.claude/projects/.../memory/MEMORY.md` | 4 linhas-índice removidas |
| `c:\Users\gabri\Desktop\PROJETO_PRODAM\.claude\napkin.md` | Removida regra de gate (linha 56-57) + atualizada referência ao PLAYBOOK |
| `scripts/auto_update_claude_md.py` | Fix `UnicodeEncodeError`: `⚠` → `[ALERTA]` no print final |

## Observações técnicas

- **Pyright warnings residuais não-bloqueantes** em `auto_update_claude_md.py` (5 warnings: 2 sobre `SKILLS_INDEX` None, 3 sobre unused tuple vars em destructuring). Script roda sem erro.
- **Bash backslash mangling**: comandos `py -3.12 scripts\auto_update_claude_md.py` foram migrados para forward slash com aspas no PowerShell para evitar mangle.

## Próximas etapas (Task 9 e 10 do plano)

- [ ] **Verificação end-to-end**:
  - `py -3.12 -m pytest tests/ -v`
  - `pre-commit run --all-files`
  - `git status` (4 arquivos gerados + edits manuais)
  - Nova sessão limpa → confirmar carregamento do CLAUDE.md enxuto + satélites
- [ ] **Commit atômico** — mensagem para aprovação antes de executar; sem push automático.

## Notas finais

- Plano de 16/05 (`quero-que-voce-analise-greedy-cray.md`) **descartado** por decisão do usuário; mantido em `~/.claude/plans/` apenas como histórico.
- `relatorios/Relatorios_Quinzenais/` (untracked) — pendente decisão se entra no commit ou fica fora.
- Princípio de anti-alucinação jurídica continua **implícito** via "Cuidados com material jurídico" no `~/.claude/CLAUDE.md`, mas sem o gate explícito que travava todo o fluxo de Edit/Write.
