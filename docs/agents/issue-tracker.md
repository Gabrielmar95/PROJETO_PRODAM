# Issue tracker: _QUESTOES_CRITICAS/

Issues, PRDs e questões críticas deste repo vivem em `_QUESTOES_CRITICAS/` como arquivos markdown numerados.

## Convenções

- **Índice geral**: `_QUESTOES_CRITICAS/00_LEIA_PRIMEIRO.md` lista todas as questões abertas — atualizar quando criar nova.
- **Uma questão por arquivo**: `_QUESTOES_CRITICAS/NN_TITULO.md` (numerada a partir de `01`).
- **Estado de triagem**: linha `Status: <label>` no topo (vocabulário em `triage-labels.md`).
- **Cabeçalho mínimo**:

  ```markdown
  # NN — Título curto

  Status: needs-triage
  Criado: 2026-MM-DD

  ## Contexto
  ...

  ## Próximo passo
  ...
  ```

- **Artefatos auxiliares** (CSV, JSON, scripts `.ps1`/`.py`) ficam soltos na mesma pasta, com nome casando com a questão. Exemplo já existente: `01_RECONCILIACAO_SSOT.md` + `reconciliacao_ssot.csv` + `reconciliar_ssot.py`.
- **Questões grandes** (multi-issue): subpasta `NN_TITULO/` com `PRD.md` dentro + `issues/NN-slug.md` para sub-issues. Exemplo: `_QUESTOES_CRITICAS/auditoria_DE_2026-05-12/`.
- **Comentários e conversa** se acumulam no fim do arquivo sob cabeçalho `## Comentários`.

## Quando uma skill diz "publish to the issue tracker"

Criar novo arquivo `NN_TITULO.md` em `_QUESTOES_CRITICAS/` (próximo número livre) e adicionar entrada em `00_LEIA_PRIMEIRO.md`.

## Quando uma skill diz "fetch the relevant ticket"

Ler o arquivo no caminho referido. Você normalmente passa o caminho ou o número da questão.

## Quando uma skill diz "label/triage this issue"

Editar a linha `Status:` no topo do arquivo.
