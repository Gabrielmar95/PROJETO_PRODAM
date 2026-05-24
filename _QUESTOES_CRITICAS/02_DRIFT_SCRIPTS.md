# Drift entre Scripts Duplicados — Diagnóstico

_Gerado em 2026-04-22T03:51:16_

## Visão geral

- **Total de scripts `.py` analisados:** 362
- **Nomes duplicados (≥2 cópias):** 5

### Distribuição por tipo de drift

- **DRIFT_LEVE**: 3 grupos
- **IDENTICOS**: 2 grupos

## Por que isso importa

Imagine que você tem três cópias do mesmo contrato em pastas diferentes. Se um cliente te pedir para corrigir uma cláusula e você alterar só uma das cópias, na próxima reunião alguém pode abrir outra e achar que você não fez o trabalho. É exatamente isso que acontece quando o mesmo script existe em vários lugares.

- **IDENTICOS**: cópias idênticas — seguro deletar as duplicatas.
- **DRIFT_LEVE**: diferenças pequenas (<20% de linhas) — provavelmente correções não propagadas.
- **DRIFT_GRAVE**: diferenças grandes (≥20%) — são scripts diferentes que por coincidência têm o mesmo nome. Precisam renomear.

## ⚠️ Scripts CRÍTICOS com duplicação

Estes scripts estão listados no `CLAUDE.md` como canônicos do projeto. Duplicação aqui é alto risco.

| Script | Tipo | Nº cópias | Canonical (mais recente) |
|--------|------|-----------|--------------------------|
| `auto_update_claude_md.py` | IDENTICOS | 3 | `auto_update_claude_md.py` |
| `consultas.py` | DRIFT_LEVE | 2 | `scripts/consultas.py` |
| `orgao_pipeline_completa.py` | DRIFT_LEVE | 2 | `scripts/orgao_pipeline_completa.py` |
| `prodam_utils.py` | IDENTICOS | 2 | `PRODAM_DOCS/prodam_utils.py` |

### `auto_update_claude_md.py`

- `auto_update_claude_md.py` ← canonical
- `PRODAM_DOCS/auto_update_claude_md.py`
- `scripts/auto_update_claude_md.py`

### `consultas.py`

- `scripts/consultas.py` ← canonical
- `PRODAM_DOCS/consultas.py`

### `orgao_pipeline_completa.py`

- `scripts/orgao_pipeline_completa.py` ← canonical
- `PRODAM_DOCS/orgao_pipeline_completa.py`

### `prodam_utils.py`

- `PRODAM_DOCS/prodam_utils.py` ← canonical
- `scripts/prodam_utils.py`

## Tabela completa de grupos

| Script | Tipo | Cópias | Canonical |
|--------|------|--------|-----------|
| `auto_update_claude_md.py` | IDENTICOS | 3 | `auto_update_claude_md.py` |
| `consultas.py` | DRIFT_LEVE | 2 | `scripts/consultas.py` |
| `gerar_trd_sead.py` | DRIFT_LEVE | 2 | `PRODAM_DOCS/_SKILLS/dossie-juridico-prodam-workspace/iteration-1/eval-3-trd-sead/gerar_trd_sead.py` |
| `orgao_pipeline_completa.py` | DRIFT_LEVE | 2 | `scripts/orgao_pipeline_completa.py` |
| `prodam_utils.py` | IDENTICOS | 2 | `PRODAM_DOCS/prodam_utils.py` |

## Próximos passos

1. Revisar este relatório e `drift_scripts.csv`.
2. Rodar `consolidar_scripts.ps1` (ele pergunta antes de cada ação).
3. Para cada `IDENTICOS`, o script deleta as cópias e mantém só o canonical.
4. Para cada `DRIFT_LEVE`/`DRIFT_GRAVE`, o script ARQUIVA as versões antigas em `_ARQUIVO_DRIFT/` — você depois abre o canonical e merge manual se necessário.
5. Ao final, atualizar `CLAUDE.md` para apontar unicamente ao canonical.

## Nota específica sobre `consultas.py` e `orgao_pipeline_completa.py`

Investiguei as duas versões com `diff -u` e descobri que **o drift é apenas de caminho, não de lógica**:

- `consultas.py`: as duas versões diferem em 1 linha — `DB_PATH` aponta para `_ANALISE/prodam.db` (versão em `PRODAM_DOCS/`) vs `prodam.db` direto (versão em `scripts/`).
- `orgao_pipeline_completa.py`: as duas versões diferem em ~3 linhas — `ROOT = Path(__file__).parent` vs `ROOT = Path(__file__).parent.parent` (porque `scripts/` está um nível abaixo).

**Interpretação**: alguém copiou o script para `scripts/` e ajustou os paths relativos. Não é bug — é adaptação. Mas manter as duas versões significa que qualquer correção numa consulta precisa ser feita duas vezes.

**Recomendação**: manter apenas a versão em `scripts/` (é a canônica do CLAUDE.md) e arquivar a cópia em `PRODAM_DOCS/` em `_ARQUIVO_DRIFT/`. O PowerShell gerado já faz isso.
