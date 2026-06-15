# Revisão Técnica de Código — Geradores SEDUC (2026-06-11)

> Terceira perna da tripla revisão (jurídica ✅ · adversarial ✅ · **técnica**).
> Escopo: `scripts/gerar_memorial_devedor.py` (crítico), `gerar_relatorio_quinzenal.py`,
> `gerar_seduc_master.py`/`gerar_seduc_html.py`, `scripts/config/regimes_por_devedor.json`,
> `scripts/acervo/*.py` (7 scripts) e o reuso de `prodam_utils.brl/fmt_brl`.
> Régua: vedações do CLAUDE.md (NUNCA-2 Decimal, Regra 9 SELIC, CSV `;`+BOM, JSON SSOT, ISO).

## Veredicto

**APTO PARA USO na apresentação de 12/06.** A matemática monetária está correta
(Decimal estrito no pipeline de cálculo, SELIC sem dupla contagem, assert de
integridade que falha alto). Os 3 achados abaixo foram **corrigidos nesta mesma
sessão** e o memorial foi regenerado com totais idênticos (106 fat ·
R$ 54.535.717,29 → R$ 61.484.720,69) + 159 testes verdes.

## Achados (todos corrigidos)

### A1 — ALTO · `faturas_do_db` sem filtro de `situacao` (corrigido)
- **Onde:** `scripts/gerar_memorial_devedor.py` (fonte `db`).
- **Problema:** o SELECT trazia **todas** as faturas do órgão; o `prodam.db` local
  contém também `Totalmente Paga`/`Cancelada`. O assert de total só rodava na
  fonte dossiê (`if not usar_db`), então na máquina local (`--fonte db` — Passo 1
  do RUNBOOK) o universo seria **inflado silenciosamente**.
- **Correção aplicada:** filtro `situacao IN ('Emitida','Parcialmente Paga')`
  (parametrizável via `--situacoes`, mesma semântica do dossiê), `AVISO:` com o
  breakdown das situações descartadas, e cross-check de contagem/total contra o
  dossiê (divergência nunca silenciosa; não aborta porque o DB pode estar mais
  fresco). RUNBOOK Passo 1 atualizado com o critério de sucesso (esperado: 106
  fat · R$ 54.535.717,29).

### A2 — MÉDIO · `float()` em dinheiro na fronteira XLSX (corrigido)
- **Onde:** `gravar_saidas()` — `ws.append([float(ln[k]) ...])`.
- **Problema:** desvio de NUNCA-2 na saída derivada (JSON SSOT não era afetado;
  valores já quantizados a 2 casas, erro sub-centavo — mas a regra é absoluta e
  o `SUM()` no Excel sobre 106 floats pode derivar no 9º dígito). Mesmo padrão
  herdado do precedente SES (`scripts/ad_hoc/gerar_memorial_preliminar_ses.py:361-396`,
  que permanece com o desvio — é ad-hoc, não regerar sem corrigir).
- **Correção aplicada:** openpyxl aceita `Decimal` nativamente — a linha passa o
  Decimal direto, sem conversão.

### A3 — BAIXO · `fmt_brl("n/d")` renderiza "R$ 0,00" (corrigido)
- **Onde:** linha "Referência SSOT" do MD quando `profiles.json` está ausente
  (caso real do sandbox: o profile vem do fallback `_ARQUIVO/`).
- **Problema:** `brl("n/d")` → `Decimal(0)` → "R$ 0,00", enganoso num documento
  jurídico (parece valor apurado).
- **Correção aplicada:** helper `ref_brl()` preserva "n/d" literal.

## Conferido e CORRETO (sem ação)

| Item | Evidência |
|---|---|
| **SELIC sem dupla contagem** (Regra 9) | único fator Π(1 + i/100) do mês seguinte ao vencimento até a data-base; `correcao_juros_selic` é derivado por diferença (display), nunca somado de volta |
| **Acumulação do fator** | mês-a-mês sobre a SGS 4390 (% a.m.); mês ausente no cache → `SystemExit` (nunca estima índice) |
| **Assert de integridade** | fonte dossiê: soma `valor_bruto` ≠ `stats.faturas.valor_total` → falha alto (dinâmico, não hardcoded) |
| **Decimal estrito no cálculo** | `getcontext().prec=28`, `ROUND_HALF_UP`, quantização única por fatura (2 casas) e nos totais; honorários `* Decimal("0.20")` |
| **Tier 1/2** | `add_meses` por aniversário calendário com clamp de dia (Art. 132 §3º CC); Tier 2 exige `venc < marco ≤ prazo_natural` (tempestividade) + reinício de 30 meses; Súmula 383/STF **não** implementada de propósito — regra seca de 2,5 anos é conservadora **contra o credor** (exclui mais), documentado no §3 do memorial |
| **CSV** | `;` + `utf-8-sig` + vírgula decimal — em todos os geradores e nos 7 scripts de acervo |
| **JSON SSOT → XLSX/CSV/MD** | mesma lista `linhas` alimenta as 4 saídas; sem recomputação paralela |
| **Datas ISO** | vencimentos/prescrições serializados `isoformat()`; BR só na camada de exibição |
| **Quinzenal** | Decimal-estrito, zero `float()` em dinheiro; KPIs do bloco REF com lastro |
| **Dashboard (master/html)** | zero `float()` — valores fluem como strings já formatadas do JSON do memorial; números p/ ECharts vêm quantizados |
| **Acervo (7 scripts)** | paths `C:\` só em docstrings de exemplo (alvo é Windows); argparse `--raiz/--orgao/--out`; `--dry-run` em todos; nenhum toca PDF original |
| **DB read-only** | `sqlite3.connect("file:...?mode=ro", uri=True)` — gerador não consegue gravar no banco |

## Observações residuais (sem correção, registradas)

1. **LIKE `%ORGAO%`** no filtro de cliente pode sobre-casar se outro cliente
   contiver a sigla no nome — para SEDUC o cross-check de contagem (A1) detecta;
   ao portar para siglas curtas (ex.: SES), conferir o `AVISO:` de divergência.
2. **`scripts/ad_hoc/gerar_memorial_preliminar_ses.py`** mantém o `float()` na
   fronteira XLSX (A2). É ad-hoc/histórico; se for regerado o memorial SES,
   migrar para `gerar_memorial_devedor.py` (já genérico) em vez de corrigir lá.
3. Scripts legados com `float()` em dinheiro (`dossie_multiformato_devedor.py`,
   `detalhamento_faturas.py`, `scripts/detran/*`) **antecedem** esta frente e
   estão fora do escopo — candidatos ao saneamento iniciado em 28/05.

---

_Revisão executada na sessão de 11/06/2026 (sandbox remoto, branch
`claude/seduc-debt-automation-8sabcb`). Verificação pós-correção: ruff limpo ·
`pytest tests/ -q` = **159 passed** · memorial regenerado com totais idênticos._
