# 14 — Triagem dos 18 devedores SEM `d_plus` (limbo prescricional) — R$ 6,58M

> Status: ready-for-human / needs-PRODAM_DOCS (triagem cloud feita; falta calcular `d_plus` local)
> Aberta em: 2026-05-29 (roadmap Janela 2 item 2.2)
> Tipo: triagem / ponto-cego de monitoramento
> Severidade: 🟠 média (R$ 6,58M sem relógio de prescrição — risco silencioso)
> Executor: Gabriel Mar (classificação local com PRODAM_DOCS)

## TL;DR

18 dos 69 devedores do `profiles_resumo.csv` têm `d_plus` **e** `urg_presc` **vazios**. Como
`scripts/alerta_prescricao.py:classificar` (L87-98) só alerta quem tem `d_plus` numérico ou
`urg_presc ∈ {CRITICA_IMINENTE, URGENTE, PRESCRITA}`, esses 18 caem todos no bucket
`sem_alerta` — **são invisíveis ao cron diário** (`.github/workflows/alerta_prescricao.yml`).
É o mesmo ponto-cego que deixou o ADS escapar 14 dias (insight #6 do `.continue-here.md`).

**Exposição total no limbo: R$ 6.578.152,53 exigível.** Nenhum tem relógio de prescrição
calculado — uma fatura pode estar prescrevendo agora e o alerta não dispararia.

## Causa

**16 dos 18 estão em `proximo_passo=CLASSIFICAR`** — o estágio mais cru do pipeline, anterior
ao cálculo de vencimento/prescrição. Os outros 2: **SEMIG** (`ANALISAR_DOCUMENTACAO`) e
**SETRAB** (`AVALIAR_SUCESSAO`). Sem a etapa de classificação, o `d_plus` (dias até/desde a
prescrição da fatura mais próxima) nunca foi computado → campo vazio → silêncio no cron.

## Os 18 (ordenados por `val_exig`)

| # | Sigla | val_exig | Categoria | Força | fat_exig | proximo_passo |
|--:|---|--:|---|---|--:|---|
| 1 | BRADESCO | R$ 2.226.517,80 | EMPRESA_PRIVADA | FRACA | 115 | CLASSIFICAR |
| 2 | CETAM | R$ 1.256.564,28 | GOV_INDIRETA | FRACA | 16 | CLASSIFICAR |
| 3 | SALUX | R$ 1.027.949,15 | EMPRESA_PRIVADA | FRACA | 16 | CLASSIFICAR |
| 4 | SETRAB | R$ 505.961,79 | GOV_DIRETA | FRACA | 81 | AVALIAR_SUCESSAO |
| 5 | UGPI | R$ 353.473,42 | GOV_DIRETA | FRACA | 18 | CLASSIFICAR |
| 6 | SEJEL | R$ 280.242,25 | GOV_DIRETA | FRACA | 96 | CLASSIFICAR |
| 7 | SEMIG | R$ 235.353,15 | GOV_DIRETA | MÉDIA | 30 | ANALISAR_DOCUMENTACAO |
| 8 | BRADESCO FINANCIAMENTO | R$ 194.783,80 | EMPRESA_PRIVADA | FRACA | 72 | CLASSIFICAR |
| 9 | ADAF | R$ 149.600,91 | GOV_INDIRETA | FRACA | 44 | CLASSIFICAR |
| 10 | AADESAM | R$ 125.682,90 | GOV_INDIRETA | FRACA | 34 | CLASSIFICAR |
| 11 | BANCO DAYCOVAL | R$ 99.481,64 | EMPRESA_PRIVADA | FRACA | 4 | CLASSIFICAR |
| 12 | DPE | R$ 28.060,05 | GOV_DIRETA | FRACA | 7 | CLASSIFICAR |
| 13 | FMPES | R$ 27.264,57 | GOV_INDIRETA | FRACA | 3 | CLASSIFICAR |
| 14 | CGE | R$ 25.693,37 | GOV_DIRETA | FRACA | 9 | CLASSIFICAR |
| 15 | CASA CIVIL | R$ 20.927,09 | GOV_DIRETA | FRACA | 4 | CLASSIFICAR |
| 16 | FJJA | R$ 20.596,36 | GOV_INDIRETA | FRACA | 5 | CLASSIFICAR |
| 17 | COSAMA | R$ 0,00 | GOV_INDIRETA | FRACA | 0 | CLASSIFICAR |
| 18 | CASA MILITAR | R$ 0,00 | GOV_DIRETA | FRACA | 0 | CLASSIFICAR |
| | **TOTAL** | **R$ 6.578.152,53** | | | **571** | |

## Agrupamento por tier (onde mirar primeiro)

| Tier | Faixa | Devedores | Soma | % do limbo |
|---|---|---|--:|--:|
| **A** | > R$ 1M | CETAM, BRADESCO, SALUX | R$ 4.511.031,23 | 68,6% |
| **B** | R$ 100K–1M | SETRAB, UGPI, SEJEL, SEMIG, BRADESCO FINANC., ADAF, AADESAM | R$ 1.845.098,22 | 28,0% |
| **C** | < R$ 100K | BANCO DAYCOVAL, DPE, FMPES, CGE, CASA CIVIL, FJJA | R$ 222.023,08 | 3,4% |
| **Z** | R$ 0 | COSAMA, CASA MILITAR | R$ 0,00 | 0% |

**3 devedores (Tier A) = 68,6% do limbo.** Classificá-los primeiro tira mais de dois terços
do valor do escuro com o menor esforço. Nota de regime: BRADESCO, BRADESCO FINANCIAMENTO e
SALUX são privadas (penhora direta, Tema 253/STF — não precatório); CETAM é Gov Indireta.

## Próximos passos (máquina local com PRODAM_DOCS)

Esta triagem é o teto do que dá pra fazer no cloud — o `d_plus` real depende do vencimento das
faturas, que está no `prodam.db`/`PRODAM_DOCS` (local-only). Na máquina local:

1. **Tier A primeiro** (CETAM, BRADESCO, SALUX): rodar o passo de classificação que calcula
   vencimento → popula `d_plus`/`urg_presc`.
2. **Tier B/C**: lote único após o Tier A.
3. **Tier Z** (COSAMA, CASA MILITAR — `val_exig` R$ 0, 0 faturas exigíveis): decidir se é
   encerrável/arquivável (provável ruído de cadastro).
4. Após popular `d_plus`, rodar `py -3.12 scripts\alerta_prescricao.py --md` e confirmar que os
   18 saíram do silêncio (entraram num bucket real).

## Risco se nada for feito

Os 18 permanecem fora do radar do cron. Se alguma fatura entre eles prescrever, a multa
contratual (R$ 500/dia + 10% do crédito perdido) incide sem aviso — o oposto do que a Janela
3.1 (cron diário) foi feita pra prevenir. **BRADESCO** (R$ 2,23M, 115 faturas exigíveis) é o
maior exposto.

## Critério de aceite

- [ ] Os 18 ganham `d_plus` e `urg_presc` calculados (classificação local).
- [ ] `scripts\alerta_prescricao.py --check` passa a enxergar os que estiverem em risco.
- [ ] Tier Z (COSAMA, CASA MILITAR) decidido: arquivar ou manter.
- [ ] Nenhum dos 18 fica em `CLASSIFICAR` sem `d_plus` após a passagem.

## Como reproduzir (cloud, read-only)

`python3` lendo `profiles_resumo.csv` (vírgula, sem BOM): filtrar `d_plus` vazio (excluir
`_metadata`), somar `val_exig` → 18 devedores, R$ 6.578.152,53. A lógica de leitura/bucketing
já vive em `scripts/alerta_prescricao.py` (`carregar_csv`, `classificar`) — não foi criado
script novo.
