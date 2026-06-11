# Nota sobre as bases — SEDUC (auditoria somente leitura, 2026-06-11)

> Parecer do agent `auditor-dados` que fundamenta a Seção 2 do `MEMORIAL_PRELIMINAR_SEDUC_2026-06-11.md`.

**Fontes:** A = `_ARQUIVO/Melhorar ainda mais esse dashboard/profiles.json` (entrada SEDUC, snapshot arquivado) · B = `DOSSIES_MULTIFORMATO/SEDUC/dossie.json` (106 faturas + 286 empenhos + 105 cobranças + stats). O `prodam.db` da raiz tem 0 bytes neste clone e foi ignorado. Valores calculados com `Decimal`.

## a) Somas de faturas — divergências quantificadas

| Métrica | Valor exato (R$) |
|---|---|
| Soma `valor_bruto` das 106 faturas (B) | **54.535.717,29** |
| `stats.faturas.valor_total` (B) | 54.535.717,29 — diferença 0,00 (consistente) |
| `val_exig` (A) | 49.215.512,48334964 |
| `val_orig` (A) | 38.705.633,18000001 |
| `val_atualizado` (A) | 50.263.263,55696253 |
| Soma B − val_exig A | **+5.320.204,81** |
| Soma B − val_orig A | **+15.830.084,11** |

A soma B é valor **bruto nominal**, não corrigido — incompatível com mera atualização monetária do universo A.

## b) Competência e contrato

| Ano comp. | Qtd | Valor bruto (R$) |
|---|---:|---|
| 2023 | 7 | 5.937.523,76 |
| 2024 | 8 | 5.164.860,31 |
| 2025 | 90 | 43.293.533,22 |
| 2026 | 1 | 139.800,00 |

Competência mínima **05/2023**, máxima 03/2026. Nenhuma fatura < 2023 → a fatura mais antiga só prescreve em **30/06/2028** (coincide com `data_prescricao_proxima` do profile embutido no dossiê, recalc 2026-06-09). As 8 prescritas do profile A **não existem** no universo do dossiê.

| Contrato | Qtd | Valor bruto (R$) |
|---|---:|---|
| 14/2018 | 73 | 19.853.061,12 |
| 20/2022 | 20 | 22.503.061,05 |
| 23/2021 | 8 | 11.646.894,20 |
| 2/2021 | 2 | 390.241,08 |
| 54/2017 | 2 | 2.659,84 |
| 21/2026 | 1 | 139.800,00 |

## c) Situação — não existe filtro 106→84
104 Emitida (R$ 51.709.253,23) + 2 Parcialmente Paga (R$ 2.826.464,06: id 141565/NF 37928/CT 23-2021/05-2023/R$ 1.449.441,38 e id 156790/NF 51924/CT 20-2022/01-2025/R$ 1.377.022,68). Nenhuma combinação de situação produz 84/76/8; não há canceladas no dossiê.

## d) Empenhos
286 NEs ativas, R$ 482.690.583,05. **NEs 2025-2026 (marco Art. 202 VI CC): 38 NEs = R$ 62.120.412,29** — 2025: CT 20/2022 (12), CT 23/2021 (9), CT 2/2021 (6), sem contrato (5); 2026: CT 21/2026 (2), CT 23/2021 (1), CT 2/2021 (1), sem contrato (2). 7 NEs sem contrato identificado foram desconsideradas como marco. Vs profile A (234 NEs / R$ 383,66M): dossiê tem +52 NEs / +R$ 99,03M; `emp_2026` bate exato (6 / R$ 24.998.189,56).

## e) Cadeia documental
83 COMPLETA (R$ 41.313.183,98) + 23 FORTE (R$ 13.222.533,31). (83 ≈ 84 do profile é coincidência, não correspondência comprovada.)

## f) Veredito
**As duas fontes descrevem universos diferentes.** O profile (84/76/8, R$ 49,2M exigível) é corte analítico de mar/2026 com critérios não reproduzíveis a partir do dossiê. O dossiê (10/06/2026) é o retrato SPCF das faturas **em aberto**: 106 faturas, R$ 54.535.717,29 bruto, todas ≥ 05/2023, zero prescritas, 6 contratos, 100% com empenho vinculado.

## Divergências e severidade

| Campo | Profile (A) | Dossiê (B) | Severidade | Ação |
|---|---|---|---|---|
| valor faturas | 49,2M exig / 38,7M orig | 54,5M bruto | CRÍTICA | Memorial declara a base e justifica o delta |
| faturas_total | 84 (76+8) | 106 em aberto | CRÍTICA | Fixar universo único contra SPCF no DB local |
| faturas_prescritas | 8 | 0 possíveis | ALTA | Identificar as 8 no snapshot antigo |
| n_contratos | 1 | 6 distintos | CRÍTICA | Corrigir profile |
| data_prescricao_proxima | 2026-03-20 (obsoleto) | 2028-06-30 (recalc 09/06) | ALTA | Usar 2028-06-30; atualizar campos derivados |
| empenhos | 234 / 383,66M | 286 / 482,69M | MÉDIA | Documentar +52 NEs de raspagem posterior |
| marcos interruptivos | nenhum registrado | 38 NEs 2025-26 (62,12M) | MÉDIA | Registrar marco Art. 202 VI por contrato (unicidade REsp 1.963.067/MS) |
| cobranças | — | 106 faturas vs 105 cobranças | BAIXA | Identificar a fatura sem cobrança |

## Não pôde ser verificado neste clone
1. Identidade das 8 faturas prescritas do profile (DB vazio).
2. Derivação exata de val_exig 49,2M e do corte 84/76.
3. Vínculo NE↔fatura individual (dossiê só traz contagem agregada `empenhos_vinc`).
4. `PRODAM_DOCS/profiles.json` (SSOT da máquina local) — o arquivado em `_ARQUIVO/` diverge do profile embutido no dossiê ao menos em `data_prescricao_proxima`.
