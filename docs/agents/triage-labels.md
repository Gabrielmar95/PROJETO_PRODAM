# Triage Labels

Mapeamento dos 5 papéis canônicos do `triage` para o vocabulário deste repo.

| Label canônico    | Label aqui        | Significado |
| ----------------- | ----------------- | ----------- |
| `needs-triage`    | `needs-triage`    | Aguarda avaliação humana inicial |
| `needs-info`      | `needs-info`      | Aguardando informação (do PRODAM, do devedor, de fonte externa) |
| `ready-for-agent` | `ready-for-agent` | Totalmente especificada — sub-agent pode executar sem contexto humano adicional |
| `ready-for-human` | `ready-for-human` | Exige decisão jurídica/estratégica humana |
| `wontfix`         | `wontfix`         | Decidido não atuar (arquivada, prescrita ou inviável) |

## Como o label é aplicado

Strings na linha `Status:` no topo de cada arquivo em `_QUESTOES_CRITICAS/`:

```markdown
# 03 — FENIXSOFT2 ação imediata

Status: ready-for-human
Criado: 2026-05-12
```

Quando uma skill mencionar um papel (ex.: "apply the AFK-ready triage label"), use a string da coluna direita.
