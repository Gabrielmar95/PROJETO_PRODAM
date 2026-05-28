# 11 — DRY dos helpers brl/fmt_brl restantes (8 scripts)

> Status: needs-human-decision
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

## Critério de aceite

- [ ] Categoria A consolidada (4 scripts) com diff de artefato validado.
- [ ] `detran/gerar_dossie_detran_v2.py` consolidado (sem `float()`).
- [ ] Categoria B: decisão registrada por script (consolidar ou manter-com-justificativa).
- [ ] Categoria C/SES: gate jurídico aprovado OU mantido fora de escopo com nota.
- [ ] `grep -rn "^def fmt_brl\|^def brl\|^    def brl\|^    def fmt_brl" scripts/` retorna só `prodam_utils.py` (ou os mantidos-por-decisão estão documentados aqui).

## Nota lateral (fora de escopo desta issue)

`scripts/detalhamento_faturas.py` tem 5 erros ruff **F821** (undefined name) pré-existentes
nas linhas 292-329, sem relação com brl/fmt_brl. Pre-commit (`--select E9,F63,F7,F82`, `files: ^scripts/`)
falharia se esse arquivo fosse staged. Abrir issue separada se for mexer nele.
