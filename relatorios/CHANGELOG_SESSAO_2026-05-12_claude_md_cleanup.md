# CHANGELOG — Limpeza CLAUDE.md (2026-05-12)

## Contexto
Auditoria de obsolescência e paths quebrados no `CLAUDE.md` do PROJETO_PRODAM.
Todos os paths validados com `Test-Path` no disco real (`C:\Users\gabri\Desktop\PROJETO_PRODAM\`).

## Correções de path (7)

| # | Linha | Antes | Depois | Motivo |
|---|-------|-------|--------|--------|
| 1 | 47 | 20 subpastas | 18 subpastas | Contagem real: 00-17 = 18 pastas |
| 2 | 81 | `01_NOTA_METODOLOGICA` | `09_NOTA_METODOLOGICA` | Pasta 01 é TITULO_EXECUTIVO; Nota Metodológica é 09 |
| 3 | 86 | 20 subpastas | 18 subpastas | Segunda ocorrência |
| 4 | 111 | `PLAYBOOK_ORGAOS_V2.md` | `relatorios\PLAYBOOK_ORGAOS_V2.md` | Arquivo real em `relatorios\`, não na raiz |
| 5 | 246 | `PLAYBOOK_ORGAOS_V2.md` | `relatorios\PLAYBOOK_ORGAOS_V2.md` | Segunda ocorrência |
| 6 | 249 | `01_NOTA_METODOLOGICA` | `09_NOTA_METODOLOGICA` | Segunda ocorrência (tabela OUTROS MAPAS) |
| 7 | 250 | `REFERENCIA_JURIDICA\PRECEDENTES_VERIFICADOS.md` | `REFERENCIA_JURIDICA\11_PESQUISAS_ORIGINAIS\PRECEDENTES_VERIFICADOS.md` | Arquivo está dentro de 11_PESQUISAS_ORIGINAIS |

## Remoções (4)

| # | Linhas | Conteúdo removido | Motivo |
|---|--------|-------------------|--------|
| 8 | 72 | HTML comment `<!-- auditado 2026-05-12: cascata propagada em 7 arquivos (11 ocorrências); regra #13 sem citações errôneas remanescentes em .md/.py do projeto -->` | Rastreabilidade preservada neste CHANGELOG; info vive no commit `69b8e30` |
| 9 | 96-108 | Tabela "Distribuição DETRAN por formato" (13 linhas com contagens de PDF/JSON/HTML/CSV/MD/TXT/XLSX/PY/DOCX/JSONL) | Contagens congeladas de auditoria concluída; pasta referenciada em linha 90 já basta |
| 10 | 125 | `— fix 2026-04-22` na header de SCRIPTS PRINCIPAIS | Data de sessão stale no título de seção |
| 11 | 207 | `**Arquivo destino**: PROJETO_PRODAM/CLAUDE.md (tracked no git; hook backup-claude-md.ps1 ...)` | Meta-nota auto-referencial; leitor já sabe qual arquivo está lendo |

## Arquivo global também editado

`~/.claude/CLAUDE.md`: bloco SAFEGUARD JURIDICO (32 linhas) condensado em 3 linhas de ponteiro para o Gate jurídico canônico. Nenhuma regra perdida.
