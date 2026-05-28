# 10 — Consolidar brl/fmt_brl: tornar prodam_utils strict-Decimal (Regra #16)

> Status: resolved
> Aberta em: 2026-05-28 (derivada da Janela 2 item 2.4)
> Fechada em: 2026-05-28 (core refactor + DRY de `auditoria_completude_devedor.py`)
> Tipo: refactor + DRY incompleto
> Severidade: 🟡 atenção (sem urgência prescricional, mas é dívida técnica que contradiz a Regra #16)

## Resolução (28/05/2026)

- `prodam_utils.fmt_brl` agora é **strict-Decimal** (sem `float()`) — preserva precisão exata acima de 15 dígitos.
- `auditoria_completude_devedor.py` importa `brl, fmt_brl` de `prodam_utils` (helpers locais removidos; `InvalidOperation` órfão também removido do import).
- Testes: `test_aceita_decimal_grande_precisao` deixou de ser `xfail` e passa; novo `test_aceita_string_brl` trava o ganho de parsear strings BRL. Suite: **115 passed**.
- Bônus: `import pytest` órfão removido do test → runner standalone (`python3 tests/test_prodam_utils.py`) agora funciona sem pytest, como já prometia o docstring.
- Os **8 scripts restantes** com helpers locais (4 divergem ou são jurídicos) foram triados na sub-issue **`11_DRY_HELPERS_BRL_RESTANTES.md`** — não consolidados aqui por exigirem smoke-test com PRODAM_DOCS local + decisão caso a caso.

## Resumo

Há duas implementações de `fmt_brl()` no projeto, e a SSOT (`prodam_utils.fmt_brl`) é **menos rigorosa** do que a versão local de `scripts/auditoria_completude_devedor.py`. Isso impede DRY total sem mudança de comportamento.

## Contexto

A Janela 2 item 2.4 fez DRY de `brl`/`fmt_brl` em `scripts/dossie_multiformato_devedor.py`, removendo os helpers locais e importando de `prodam_utils`. Ao tentar aplicar o mesmo em `scripts/auditoria_completude_devedor.py`, descobri que **o `fmt_brl` local de `auditoria_completude_devedor.py:50` é mais rigoroso do que o de `prodam_utils.fmt_brl`**:

| Helper | Implementação | Comportamento |
|---|---|---|
| `auditoria_completude_devedor.py:50` (local) | `f"R$ {v:,.2f}".replace(...)` | Aceita `Decimal` direto via format spec — **precisão exata**. Lança `TypeError` em `None`/`"abc"`. |
| `scripts/prodam_utils.py:55` (SSOT) | `n = float(v); f"R$ {n:,.2f}".replace(...)` | Converte tudo para `float` antes de formatar — **perde precisão em Decimal >15 dígitos significativos** (limite IEEE 754 double). Tolerante a `None`/`"abc"` (vira `0`). |

O `float(v)` em `prodam_utils.fmt_brl` **contradiz o espírito da Regra #16 do `CLAUDE.md`**: "Valores monetários: **Decimal**, nunca float".

## Por que importa

Em valores até R$ 999 bilhões (15 dígitos significativos), `float()` é seguro o suficiente. Mas:

1. **A Regra #16 é categórica** — `float()` em qualquer ponto da cadeia de exibição/cálculo de valor monetário é um "code smell" que deveria ser eliminado.
2. **Auditorias futuras podem cruzar valores agregados** (soma de carteira inteira, projeções com SELIC composta de longo prazo) onde 15 dígitos não bastam.
3. **DRY incompleto**: enquanto `prodam_utils.fmt_brl` usar `float()`, não dá pra aplicar DRY em `auditoria_completude_devedor.py` sem mudar comportamento sutil.

## Proposta

Refatorar `scripts/prodam_utils.py:55-61` para **não usar `float()`**:

```python
# ANTES
def fmt_brl(v: Any) -> str:
    try:
        n = float(v)
    except (ValueError, TypeError):
        n = 0.0
    return f"R$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# DEPOIS (proposta)
def fmt_brl(v: Any) -> str:
    # Strict-Decimal: nunca usar float() em moeda (Regra #16).
    # Tolerância a None/"abc" via brl() (já é Decimal-aware).
    d = brl(v) if not isinstance(v, Decimal) else v
    return f"R$ {d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
```

Pontos a validar antes:

- [ ] Format spec `:,.2f` aceita `Decimal` direto em Python 3.10+ (confirmado — testado em 28/05/2026).
- [ ] Cobertura: o `tests/test_prodam_utils.py::TestFmtBrl::test_aceita_decimal` já valida o caso pós-refactor (adicionado na Janela 2 item 2.4).
- [ ] Adicionar teste: `fmt_brl(Decimal("9999999999999999.99"))` deve preservar precisão exata (caso que `float()` quebraria).
- [ ] Auditar 3-5 chamadores que passam `int`/`float` direto a `fmt_brl` — vão continuar funcionando (Decimal aceita int/float no construtor).

Depois do refactor:

- [ ] Aplicar DRY em `scripts/auditoria_completude_devedor.py:42-50` — remover helpers locais, importar `brl, fmt_brl` de `prodam_utils`.
- [ ] Mesmo padrão em qualquer outro script que tenha helper local (verificar com `grep -rn "^def fmt_brl\|^def brl" scripts/`).

## Risco

- **Baixo**: refactor isolado em uma função de display, com teste já existente cobrindo o caso esperado.
- **Mitigação**: rodar `pytest tests/ -v` + smoke test manual de `scripts/auditoria_completude_devedor.py` (que produz tabela MD com valores R$) antes de commit.

## Por que não foi feito no commit da Janela 2 item 2.4

- Fora do escopo cirúrgico (3 fixes + 8 testes).
- Mexer aqui exigiria revisar chamadores de `fmt_brl` em outros scripts (>5 arquivos) — risco de regressão visual em relatórios.
- A descoberta é consequência da revisão pré-commit; vira issue para próximo ciclo.

## Critério de aceite

- [x] `prodam_utils.fmt_brl` não contém a string `float(`.
- [x] `tests/test_prodam_utils.py::TestFmtBrl::test_aceita_decimal_grande_precisao` passa (deixou de ser `xfail`; valida Decimal >15 dígitos).
- [x] `auditoria_completude_devedor.py` importa `brl, fmt_brl` de `prodam_utils` e não define helpers locais.
- [x] `grep -rn "^def fmt_brl\|^def brl" scripts/` ainda retorna 8 scripts além de `prodam_utils.py` — documentados na sub-issue `_QUESTOES_CRITICAS/11_DRY_HELPERS_BRL_RESTANTES.md`. Verificação inicial (28/05/2026) encontrou esses helpers locais (`auto_update_claude_md.py`, `gerar_relatorio_docx.py`, `consultas.py`, `ad_hoc/gerar_memorial_preliminar_ses.py`, `reconciliacao_4_fontes.py`, `detran/gerar_dossie_detran_v2.py`, `ses_reconciliacao_completa.py`, `detalhamento_faturas.py`) — 4 divergem em comportamento ou são juridicamente sensíveis, por isso não foram consolidados em massa.
