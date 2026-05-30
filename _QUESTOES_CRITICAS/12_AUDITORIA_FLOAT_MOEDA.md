# 12 — Auditoria: `float()` em valores monetários (Regra #16)

> Status: needs-human-decision
> Aberta em: 2026-05-28 (auditoria read-only, derivada da Issue 10)
> Tipo: dívida técnica / risco de precisão
> Severidade: 🟠 (1 caso corrompe o SSOT; restante é precisão/consistência)
> Escopo desta issue: **somente inventário** — nenhum script foi editado.

## Resumo

`grep -rn "float(" scripts/` → **76 ocorrências**. Após descontar usos legítimos
(percentuais, scores de confiança, normalização de ID, 1 docstring) e 1 arquivo `.bak`,
restam **~50 `float()` tocando moeda** em código vivo. A Regra #16 ("Valores monetários:
Decimal, nunca float") é categórica; este é o mapa para saldá-la por tiers.

## Tier 1 — corrige precisão real (cálculo/acúmulo/SSOT em float) 🚨

| Local | Código | Problema |
|---|---|---|
| `reconciliar_orfaos_reversos.py:103` | `pr["val_exig"] = float(val_fat)` | **🚨 GRAVE: escreve float no `profiles.json` (SSOT).** `val_fat` já é Decimal (linha 76). Fix de 1 linha: `str(val_fat)`. **Toca escrita no profiles.json → gate jurídico.** Causa-raiz plausível da deriva de precisão decimal vista na Issue 03 (achado E). |
| `reconciliar_orfaos_reversos.py:66` | `float(val_exig_atual.replace(",","."))` | parse de entrada money→float (+ `except:` nu) |
| `ad_hoc/profile_pasta_mae.py:183,187` | `valor_*_total += float(...)` | acumula totais de carteira em float |
| `auto_update_claude_md.py:197-199` | `ve/vo/va = float(val_exig/val_orig/val_atualizado)` | métricas do CLAUDE.md somadas/exibidas via float |
| `detran/detran_auditoria_profunda.py:77,88,225-235,300` | `sum(float(...))` | soma de empenhos/faturas em float |
| `detran/detran_score_auditor.py:250,271-272,328-329` | `sum(float(...))` + helper parse money→float | idem |
| `detran/detran_consolidado_to_json_pipeline.py:155`, `detran/detran_ingest_contratos_db.py:150`, `orgao_pipeline_completa.py:490` | `float(str(s).replace(".","").replace(",","."))` | parse money→float na ingestão (entra no fluxo do DB) |

## Tier 2 — fronteira de serialização JSON (necessário p/ `json.dump`, mas Regra #16-adjacent)

`json.dump` rejeita `Decimal`, então estes scripts fazem `float()` campo-a-campo antes de serializar (Chart.js / dashboards):

| Local | Nº aprox. |
|---|---|
| `detalhamento_faturas.py:203-237,411` | ~15 campos `*_val` |
| `dossie_multiformato_devedor.py:144-183,467,493` | ~8 campos empenho/fatura |

**Fix estrutural recomendado**: um encoder Decimal-aware (`json.dump(..., default=str)` ou `JSONEncoder` custom que serializa Decimal como string) em vez de `float()` em cada campo. Resolve os dois de uma vez sem perda de precisão.

## Tier 3 — legal-sensitive (gate jurídico obrigatório)

| Local | Risco |
|---|---|
| `ad_hoc/gerar_memorial_preliminar_ses.py:361-396` (~10×) | `float()` em valores do memorial SES (DOCX) — **é a metodologia do TRD SES/SUSAM (Issue 03)**; qualquer mudança de arredondamento é material. Só com gate. |

## Tier 4 — já rastreado na sub-issue 11

| Local | Nota |
|---|---|
| `detran/gerar_dossie_detran_v2.py:30` | `v = float(v or 0)` dentro do helper `brl` local — coberto pela Issue 11 (Categoria C). |

## Não-violações (revisado, mantém `float`)

Legítimos — não são moeda: percentuais de reajuste/multa/juros (`orgao_pipeline_completa:140`, `detran_contratos_to_json:114`, `detran_pipeline_fast:78`, `detran_ocr_contratos:138/154/159`, `reconciliacao_4_fontes:184`), scores de confiança (`classificar_e_renomear_por_conteudo:202/303`), normalização de ID inteiro (`prodam_utils:199`, `ses_reconciliacao_completa:93`). A "ocorrência" em `prodam_utils.py:58` é a **docstring** do fix da Issue 10 (`nunca usa float()`), não uma chamada.

## Achado lateral (fora de escopo)

`scripts/detran/detran_auditoria_profunda.py.bak` está **versionado no git** (9 `float()`, código morto duplicado do `.py` vivo). `.bak` não deveria estar no repo — abrir limpeza separada.

## Recomendação de execução (ordem)

1. **`reconciliar_orfaos_reversos.py:103`** — fix de 1 linha (`float`→`str`), mas **gate** (escreve SSOT) + smoke-test local. Prioridade máxima: é o único que **corrompe dado persistido**.
2. **Tier 2** — encoder Decimal-aware (1 mudança resolve `detalhamento_faturas` + `dossie_multiformato`). Sem gate; exige smoke-test (PRODAM_DOCS).
3. **Tier 1 restante** — saldar por arquivo, com smoke-test de cada relatório.
4. **Tier 3 (SES)** — só com gate jurídico.

## Critério de aceite

- [ ] `reconciliar_orfaos_reversos.py:103` não usa `float()` ao escrever no profile.
- [ ] Tier 2 migrado para encoder Decimal-aware (sem `float()` por campo).
- [ ] Tier 1 restante saldado ou justificado.
- [ ] `.bak` removido do versionamento (achado lateral).
- [ ] `grep -rn "float(" scripts/` retorna apenas usos não-monetários (percentuais/scores/ID) + a docstring.
