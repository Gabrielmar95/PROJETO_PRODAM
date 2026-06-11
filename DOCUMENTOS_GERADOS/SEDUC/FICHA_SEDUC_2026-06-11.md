# FICHA EXECUTIVA — SEDUC · Secretaria de Educação do Amazonas
**Contrato 002/2026 — PRODAM S.A. × Brandão Ozores Advogados** · Gabriel Mar, OAB/AM 15.697 · 11/06/2026

| Identificação | |
|---|---|
| CNPJ | 04.312.419/0001-30 · GOV_DIRETA (Secretaria de Estado) |
| Posição no portfólio | **Devedor nº 1 em valor** (rank 2 em prioridade) · Força probatória **FORTE** · Score 80/100 |
| Fase / próximo passo | F0-F1 — **ANALISAR_DOCUMENTACAO** |
| Status | **Negativa expressa** (Of. 316/2020-GS/SEDUC) — não interrompe prescrição nem renuncia (Tema 1.109/STJ) |

## Quanto deve (dois universos, declarados)

| Universo | Faturas | Principal | Atualizado | Honorários 20% |
|---|---:|---:|---:|---:|
| **SPCF em aberto (jun/2026)** — memorial preliminar, SELIC/EC 113 até 04/2026 | 106 | R$ 54.535.717,29 | **R$ 61.484.720,69** | R$ 12.296.944,14 |
| — cenário conservador (só "Emitida") | 104 | R$ 51.709.253,23 | R$ 57.863.602,47 | R$ 11.572.720,49 |
| SSOT histórico (snapshot mar/2026) | 84 (76 exig.) | R$ 38.705.633,18 | R$ 49.215.512,48 exig. / R$ 50.263.263,56 atual. | — |
| Expectativa de recuperação (profile) | — | EV **R$ 34.450.858,74** · Monte Carlo p50 R$ 24.391.879,65 | — | EV honorários R$ 6.890.171,75 |

> Universo do memorial: 106 faturas em aberto, competências 05/2023–03/2026, 100% dentro do quinquênio. O snapshot de mar/2026 (84 faturas, 8 prescritas) usa corte anterior e não compõe o universo atual. Memorial completo: `MEMORIAL_PRELIMINAR_SEDUC_2026-06-11.{md,xlsx}`.

## Prescrição e marcos
- **Primeira prescrição do universo atual: 30/06/2028** (folga de 2 anos) — sem urgência prescricional na SEDUC (≠ SSP/SUHAB, que vencem 30/06/2026).
- **38 NEs ativas 2025-2026 = R$ 62.120.412,29** sobre os mesmos contratos → reconhecimento tácito (Art. 202 VI CC), pendente de vinculação fatura a fatura.

## Contratos (6 — profile dizia 1, corrigir)
| CT | Faturas | Valor bruto | Contrato PDF? |
|---|---:|---:|---|
| 14/2018 | 73 | R$ 19.853.061,12 | ❌ |
| 20/2022 | 20 | R$ 22.503.061,05 | ❌ |
| 23/2021 | 8 | R$ 11.646.894,20 | ❌ |
| 2/2021 · 54/2017 · 21/2026 | 2 · 2 · 1 | R$ 0,53M | ❌ |

## Riscos (por que MONITORIA e não execução)
1. **Sem título executivo** (blindagem 20/22) — cadeia REsp 793.969 (Contrato+NE+NF+Atesto) incompleta: **0 contratos PDF, sem atestos/NLs** (completude documental 54,5%).
2. **Negativa expressa** exige prova documental robusta.
3. **Regime SELIC presumido** — confirmar na cláusula econômica de cada contrato (Regra 10).
4. **Decreto AM 53.464/2026** — verificar as 4 exceções antes de qualquer ação contra o Estado.
5. 2 faturas "Parcialmente Paga" (R$ 2,83M) computadas pelo bruto — abater pagamentos com extrato SPCF.

## Próximos passos (esta semana)
1. **Hoje à noite** — `RUNBOOK_SEDUC_ACERVO.md` na máquina local: memorial FINAL contra o `prodam.db` real + ingestão DPCON/pendrive + lacunas SPCF.
2. Caçar **contratos-base dos 6 CTs** (prioridade CT 14/2018) no DPCON/pendrive; o que faltar → Ofício LAI (modelo DETRAN 003/2026).
3. Localizar o **Of. 316/2020-GS/SEDUC** e os atestos (ofício interno à PRODAM, modelo CT 8/2021).
4. Extrair cláusulas econômicas (`extracao-clausulas-contratuais`) → regime deixa de ser presumido → memorial v2.
5. Vincular as 38 NEs 2025-2026 às faturas (marcos Art. 202 VI) → registrar em profiles.json.
