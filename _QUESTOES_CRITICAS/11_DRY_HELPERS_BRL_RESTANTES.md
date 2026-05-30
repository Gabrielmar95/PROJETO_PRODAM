# 11 — DRY dos helpers brl/fmt_brl restantes (8 scripts)

> Status: cat-A-code-done / cat-B-C-needs-decision — Cat A consolidada (2026-05-30); ver "Resolução Cat A"
> Aberta em: 2026-05-28 (sub-issue derivada da Issue 10, critério de aceite #4)
> Tipo: refactor + DRY incompleto
> Severidade: 🟡 atenção (dívida técnica; sem urgência prescricional)
> Bloqueio cloud: **smoke-test exige PRODAM_DOCS local** — nenhum destes scripts roda em sessão cloud (carregam `profiles.json`/`prodam.db` no import).

## Contexto

A Issue 10 (fechada em 28/05) tornou `prodam_utils.fmt_brl` strict-Decimal (sem `float()`) e
consolidou `auditoria_completude_devedor.py` (helpers locais idênticos ao SSOT, DRY seguro).

Restam **8 scripts** com helpers `brl`/`fmt_brl` locais. Esta issue documenta o triage por
script — **não é DRY mecânico**: 4 dos 8 têm comportamento divergente ou são juridicamente
sensíveis e exigem decisão antes de tocar.

## Triage por script

### Categoria A — idênticos ao SSOT refatorado (DRY seguro, mas exige smoke-test local)

Implementação `f"R$ {v:,.2f}".replace(...)` — comportamento idêntico ao `prodam_utils.fmt_brl`
pós-Issue-10 para entradas numéricas (Decimal/int/float). Consolidação não muda saída.

| Script | Linha | Helper | Observação |
|---|---|---|---|
| `scripts/ses_reconciliacao_completa.py` | 42 (`brl`), 55 (`fmt_brl`) | ambos | `brl` local ≈ `prodam_utils.brl` (regex de strip menos abrangente, irrelevante p/ entradas limpas) |
| `scripts/auto_update_claude_md.py` | 236 (`fmt_brl`) | fmt_brl | gera o próprio `CLAUDE.md` — validar visualmente o diff do CLAUDE.md pós-DRY |
| `scripts/gerar_relatorio_docx.py` | 30 (`brl`) | semântica `fmt_brl` | ⚠️ nome `brl` mas RETORNA "R$ ..." — mapear para `fmt_brl` ao importar |
| `scripts/detalhamento_faturas.py` | 722 (`brl`, aninhada) | semântica `fmt_brl` | ⚠️ helper aninhado dentro de função + nome `brl`; ⚠️ arquivo tem **5 erros F821 pré-existentes** (linhas 292-329) não relacionados a este DRY |

### Categoria B — comportamento divergente: NÃO consolidar sem decisão explícita

| Script | Linha | Divergência vs SSOT |
|---|---|---|
| `scripts/consultas.py` | 35 (`brl`) | **Sem prefixo `R$ `**; retorna `""` para `None` (não `"R$ 0,00"`); retorna `str(v)` em exceção. É outra função — consolidar mudaria toda a saída do CLI de consultas. |
| `scripts/reconciliacao_4_fontes.py` | 169 (`fmt_brl`) | Retorna `"N/D"` para `None` (não `"R$ 0,00"`). Se algum relatório distingue "N/D" de "R$ 0,00", consolidar perde o sinal. |

### Categoria C — gate jurídico / cuidado extra

| Script | Linha | Risco |
|---|---|---|
| `scripts/ad_hoc/gerar_memorial_preliminar_ses.py` | 49 (`fmt_brl`) | Usa `q2(x)` (quantize) antes de formatar — modo de arredondamento pode divergir do `:,.2f`. **É a metodologia do TRD SES/SUSAM (Issue 03)** → gate jurídico obrigatório; qualquer mudança de centavo é material. |
| `scripts/detran/gerar_dossie_detran_v2.py` | 28 (`brl`) | Usa `float(v or 0)` — o próprio anti-padrão da Regra #16. Gera dossiê DETRAN (benchmark A+). Consolidar é desejável (mata um `float()`), mas exige revisar saída do dossiê. |

## Recomendação de execução (na máquina local com PRODAM_DOCS)

1. **Categoria A primeiro** (4 scripts): DRY + rodar cada script + `git diff` nos artefatos
   (`CLAUDE.md`, `.docx`, `.md` de detalhamento) para confirmar zero mudança visual.
   - Atenção ao mapeamento de nome: `brl`→`fmt_brl` onde o helper local formata (retorna "R$ ").
2. **Categoria C — `detran/gerar_dossie_detran_v2.py`**: consolidar (elimina `float()`), smoke-test do dossiê.
3. **Categoria B**: decidir caso a caso se a diferença (`""`/`"N/D"`/sem prefixo) é intencional.
   Se for, manter local com comentário; se não, alinhar ao SSOT.
4. **Categoria C — `gerar_memorial_preliminar_ses.py`**: só com gate jurídico (toca cálculo SES).

## Resolução Cat A (2026-05-30, commit `eaa36fb`)

Os **4 scripts da Categoria A** consolidados para importar de `prodam_utils` (Regra #16):

| Script | Antes | Depois |
|---|---|---|
| `ses_reconciliacao_completa.py` | `brl` (parser) + `fmt_brl` locais | `from prodam_utils import norm, norm_variants, brl, fmt_brl`; `InvalidOperation` órfão removido do import de `decimal` |
| `auto_update_claude_md.py` | `fmt_brl` local | `from prodam_utils import fmt_brl` (+ `sys.path`) |
| `gerar_relatorio_docx.py` | `brl` local que **formatava** | `from prodam_utils import fmt_brl as brl` |
| `detalhamento_faturas.py` | `brl` aninhado que **formatava** | `from prodam_utils import fmt_brl as brl` |

**Mapeamento de nome:** em `gerar_relatorio_docx`/`detalhamento_faturas` o helper chamava-se `brl`
mas retornava `"R$ ..."` (semântica de `fmt_brl`). Importados como `fmt_brl as brl` → **call
sites intactos**, diff mínimo.

**Equivalência provada (cloud, sem rodar os scripts):** `fmt_brl` e `brl` antigos vs
`prodam_utils` → **0 divergências** em todos os tipos que os scripts passam (Decimal/int/float;
parser de string BR incl. `None`/`""`/`"-"`/`"14.748.048,95"`).

**Por que sem smoke-test de artefato:** os 4 carregam `prodam.db`/`profiles.json` no import (ou
regeneram `CLAUDE.md`) → não rodam em cloud. Travado por **AST** em
`tests/test_regression_decimal_dry.py::TestIssue11CatADRY` (8 casos = 4 scripts × {sem helper
local, importa de prodam_utils}). Suite: **125 → 133 passed**; ruff `E9/F63/F7/F82` limpo;
`compileall` OK nos 4.

**Caveat do issue corrigido:** a "Nota lateral" abaixo dizia que `detalhamento_faturas.py` tinha
5 erros F821 — **desatualizado** (corrigido em `6fcb5d9`); ruff está limpo. Mantida só por
histórico.

**Pendente local (opcional):** rodar cada script com `PRODAM_DOCS` e `git diff` no artefato
(`CLAUDE.md`/`.docx`/`.md`) para confirmação visual — a equivalência numérica já garante zero
mudança de saída.

## Critério de aceite

- [x] Categoria A consolidada (4 scripts) — equivalência numérica provada; diff de artefato visual fica como conferência local opcional.
- [ ] `detran/gerar_dossie_detran_v2.py` consolidado (sem `float()`).
- [ ] Categoria B: decisão registrada por script (consolidar ou manter-com-justificativa).
- [ ] Categoria C/SES: gate jurídico aprovado OU mantido fora de escopo com nota.
- [x] `grep -rnE "def (brl|fmt_brl)"` nos 4 scripts da Cat A retorna vazio (helpers locais eliminados). Cat B/C ainda têm helpers locais (por decisão pendente).

## Nota lateral (fora de escopo desta issue)

`scripts/detalhamento_faturas.py` tem 5 erros ruff **F821** (undefined name) pré-existentes
nas linhas 292-329, sem relação com brl/fmt_brl. Pre-commit (`--select E9,F63,F7,F82`, `files: ^scripts/`)
falharia se esse arquivo fosse staged. Abrir issue separada se for mexer nele.
