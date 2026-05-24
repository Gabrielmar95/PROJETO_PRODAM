# _ARQUIVO_DRIFT — Scripts arquivados por conflito de drift

**Atualizado em:** 2026-04-22

## Por que estes arquivos estão aqui?

Cada arquivo tem o prefixo do caminho original de onde foi movido. Ex:
`PRODAM_DOCS__consultas.py` significa que antes estava em `PRODAM_DOCS/consultas.py`.

A versão **canônica** (mais recente e correta) está em `scripts/`.

## Como fazer rollback

```powershell
# Exemplo: restaurar consultas.py em PRODAM_DOCS
Move-Item "_ARQUIVO_DRIFT\PRODAM_DOCS__consultas.py" "PRODAM_DOCS\consultas.py"
```

## Lista do que foi arquivado

| Arquivo | Origem | Motivo |
|---------|--------|--------|
| PRODAM_DOCS__consultas.py | PRODAM_DOCS/consultas.py | DRIFT_LEVE (1 linha de path) |
| PRODAM_DOCS__orgao_pipeline_completa.py | PRODAM_DOCS/orgao_pipeline_completa.py | DRIFT_LEVE (3 linhas de path) |
| PRODAM_DOCS__prodam_utils.py | PRODAM_DOCS/prodam_utils.py | IDÊNTICA (md5 == scripts/prodam_utils.py) |
