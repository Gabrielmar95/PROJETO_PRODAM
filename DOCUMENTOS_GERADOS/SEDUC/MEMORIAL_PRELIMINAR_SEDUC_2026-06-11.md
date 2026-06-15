> 🔒 **USO INTERNO — PRODAM / BRANDÃO OZORES ADVOGADOS.** Este documento contém expectativas de recuperação, score e estratégia. **NÃO anexar à TRD nem a peça processual.** Versão externável exige supressão da linha 'Referência SSOT', das expectativas (EV/Monte Carlo), da recomendação de via e dos honorários.

# Memorial Preliminar de Cálculo — SEDUC

**Contrato 002/2026 — PRODAM S.A. × Brandão Ozores Advogados**
**Data-base:** 30/04/2026 (último mês com SELIC fechada no cache BCB)  
**Devedor:** Secretaria de Educação do Amazonas (SEDUC) — CNPJ 04.312.419/0001-30  
**Faturas exigíveis:** 106 (Tier 1: 106 | Tier 2: 0)

---

## 1. Fundamentação da Atualização Monetária

A SEDUC é órgão da **administração direta estadual** do Amazonas. Para débitos da Fazenda Pública estadual, a atualização monetária e os juros de mora seguem regime estabelecido em **norma legal** — não em cláusula contratual — conforme:

- **Arts. 389, parágrafo único, e 406, §1º, do Código Civil** (redação da Lei nº 14.905/2024) — correção monetária pelo **IPCA** e juros pela **taxa legal (SELIC deduzido o IPCA)**, cuja incidência conjunta equivale, em termos práticos, à aplicação da **SELIC acumulada**, quando inexistente cláusula contratual específica.
- **EC 113/2021, Art. 3º** — por convergência material: nas discussões e condenações que envolvam a Fazenda Pública, incidência única da taxa SELIC acumulada mensalmente. A extensão à fase pré-judicial é adotada por convergência com o regime civil acima, sem prejuízo de rediscussão em juízo.
- **REsp 793.969/RJ** (1ª Turma STJ, Rel. p/ acórdão Min. José Delgado, j. 21/02/2006) — admite a composição documental (Contrato + NE + NF + Atesto) como lastro de título executivo.

Como a metodologia equivale à SELIC acumulada (EC 113/2021, art. 3º), **não se somam** correção e juros em separado, nem multa.

**Série:** BCB/SGS **4390** (SELIC % a.m.). **Arredondamento:** ROUND_HALF_UP, 2 casas.

> ⚠️ **REGIME PRESUMIDO** — 0 contratos em PDF disponíveis nesta data; o índice definitivo confirma-se na cláusula econômica de cada contrato (Regra 10). Havendo cláusula diversa, o memorial será refeito por contrato antes de qualquer peça.

---

## 2. Nota sobre as bases (universos de dados)

O presente memorial adota como universo de cobrança as **106 faturas em aberto** extraídas do SPCF (dossiê de 10/06/2026), no valor bruto nominal de **R$ 54.535.717,29**, distribuídas por 6 contratos e competências de 05/2023 a 03/2026 — integralmente dentro do prazo quinquenal (primeira prescrição: **30/06/2028**). Os valores do perfil consolidado de mar/2026 (84 faturas; R$ 38.705.633,18 original; **R$ 49.215.512,48 exigível**; R$ 50.263.263,56 atualizado) refletem snapshot anterior, com critérios de corte distintos e 8 faturas então tidas por prescritas que **foram excluídas do universo de cobrança** deste memorial. A **conciliação id-a-id** entre os dois universos será produzida contra o `prodam.db` na máquina principal e apresentada em anexo; até lá, os critérios do corte de mar/2026 permanecem pendentes de validação. Reforça a exigibilidade a existência de **38 notas de empenho ativas emitidas em 2025-2026 (R$ 62.120.412,29)** sobre 4 dos 6 contratos do universo — reconhecimento tácito (Art. 202, VI, CC), pendente de vinculação fatura a fatura.

> ⚠️ **VENCIMENTOS ESTIMADOS** — a fonte preliminar (dossiê) não traz a data de vencimento; adotou-se *último dia do mês de competência + 30 dias*. A versão final (prodam.db local) usa vencimentos reais do SPCF.

---

## 3. Universo, Prescrição e Marcos (Tier 1 / Tier 2)

- **Tier 1** — vencimento dentro do quinquênio (Art. 206 §5º I CC).
- **Tier 2** — quinquênio vencido, porém interrompido tempestivamente por NE (Art. 202 VI CC; unicidade — REsp 1.963.067/MS), reiniciando **pela metade** (Dec. 20.910/1932, art. 9º = 2,5 anos); observado que, interrompida a prescrição na primeira metade do quinquênio, o prazo total não fica reduzido aquém de cinco anos (Súmula 383/STF — *conferir inclusão no catálogo PRECEDENTES_VERIFICADOS.md antes de uso em peça externa*). O cálculo deste memorial usa a regra seca de 2,5 anos — **conservadora contra o credor**.
- **Excluídas por prescrição consumada:** 0.

NEs-marco (mais recente por contrato, anos 2025-2026):

| Contrato | NE mais recente |
|---|---|
| 14/2018 | — (NE 2025-2026 não localizada no dossiê; vinculação pendente) |
| 2/2021 | 05/01/2026 |
| 20/2022 | 04/07/2025 |
| 21/2026 | 23/03/2026 |
| 23/2021 | 28/01/2026 |
| 54/2017 | — (NE 2025-2026 não localizada no dossiê; vinculação pendente) |

---

## 4. Memorial Fatura-a-Fatura

| # | ID | NF | Contrato | Comp. | Venc.* | Tier | Situação | Valor Bruto | Meses | Fator SELIC | Valor Atualizado |
|---|----|----|----------|-------|-------|------|----------|------------:|------:|------------:|-----------------:|
| 1 | 145907 | 145907 | 14/2018 | 11/2023 | 30/12/2023 | 1 | Emitida | R$ 123.025,58 | 28 | 1.319542 | R$ 162.337,38 |
| 2 | 156802 | 51971 | 14/2018 | 01/2025 | 02/03/2025 | 1 | Emitida | R$ 9.051,74 | 13 | 1.155436 | R$ 10.458,71 |
| 3 | 156803 | 51967 | 14/2018 | 01/2025 | 02/03/2025 | 1 | Emitida | R$ 134.008,96 | 13 | 1.155436 | R$ 154.838,81 |
| 4 | 156804 | 51969 | 14/2018 | 01/2025 | 02/03/2025 | 1 | Emitida | R$ 353.200,00 | 13 | 1.155436 | R$ 408.100,08 |
| 5 | 156805 | 51970 | 14/2018 | 01/2025 | 02/03/2025 | 1 | Emitida | R$ 123.025,58 | 13 | 1.155436 | R$ 142.148,21 |
| 6 | 156806 | 51966 | 14/2018 | 01/2025 | 02/03/2025 | 1 | Emitida | R$ 234.215,23 | 13 | 1.155436 | R$ 270.620,77 |
| 7 | 156807 | 51968 | 14/2018 | 01/2025 | 02/03/2025 | 1 | Emitida | R$ 987.736,23 | 13 | 1.155436 | R$ 1.141.266,24 |
| 8 | 157426 | 52788 | 14/2018 | 02/2025 | 30/03/2025 | 1 | Emitida | R$ 9.051,74 | 13 | 1.155436 | R$ 10.458,71 |
| 9 | 157427 | 52789 | 14/2018 | 02/2025 | 30/03/2025 | 1 | Emitida | R$ 134.008,96 | 13 | 1.155436 | R$ 154.838,81 |
| 10 | 157428 | 52790 | 14/2018 | 02/2025 | 30/03/2025 | 1 | Emitida | R$ 353.200,00 | 13 | 1.155436 | R$ 408.100,08 |
| 11 | 157429 | 52791 | 14/2018 | 02/2025 | 30/03/2025 | 1 | Emitida | R$ 123.025,58 | 13 | 1.155436 | R$ 142.148,21 |
| 12 | 157623 | 52786 | 14/2018 | 02/2025 | 30/03/2025 | 1 | Emitida | R$ 241.750,08 | 13 | 1.155436 | R$ 279.326,80 |
| 13 | 157624 | 52787 | 14/2018 | 02/2025 | 30/03/2025 | 1 | Emitida | R$ 891.324,20 | 13 | 1.155436 | R$ 1.029.868,29 |
| 14 | 158192 | 53516 | 14/2018 | 03/2025 | 30/04/2025 | 1 | Emitida | R$ 9.051,74 | 12 | 1.143317 | R$ 10.349,01 |
| 15 | 158193 | 53514 | 14/2018 | 03/2025 | 30/04/2025 | 1 | Emitida | R$ 134.008,96 | 12 | 1.143317 | R$ 153.214,73 |
| 16 | 158194 | 53513 | 14/2018 | 03/2025 | 30/04/2025 | 1 | Emitida | R$ 353.200,00 | 12 | 1.143317 | R$ 403.819,59 |
| 17 | 158195 | 53515 | 14/2018 | 03/2025 | 30/04/2025 | 1 | Emitida | R$ 123.025,58 | 12 | 1.143317 | R$ 140.657,25 |
| 18 | 158372 | 53511 | 14/2018 | 03/2025 | 30/04/2025 | 1 | Emitida | R$ 218.922,71 | 12 | 1.143317 | R$ 250.298,07 |
| 19 | 158373 | 53512 | 14/2018 | 03/2025 | 30/04/2025 | 1 | Emitida | R$ 897.306,14 | 12 | 1.143317 | R$ 1.025.905,44 |
| 20 | 158973 | 54297 | 14/2018 | 04/2025 | 30/05/2025 | 1 | Emitida | R$ 9.051,74 | 11 | 1.130430 | R$ 10.232,36 |
| 21 | 158974 | 54294 | 14/2018 | 04/2025 | 30/05/2025 | 1 | Emitida | R$ 134.008,96 | 11 | 1.130430 | R$ 151.487,77 |
| 22 | 158975 | 54296 | 14/2018 | 04/2025 | 30/05/2025 | 1 | Emitida | R$ 353.200,00 | 11 | 1.130430 | R$ 399.267,94 |
| 23 | 158976 | 54298 | 14/2018 | 04/2025 | 30/05/2025 | 1 | Emitida | R$ 123.025,58 | 11 | 1.130430 | R$ 139.071,83 |
| 24 | 159166 | 54293 | 14/2018 | 04/2025 | 30/05/2025 | 1 | Emitida | R$ 79.226,57 | 11 | 1.130430 | R$ 89.560,11 |
| 25 | 159167 | 54295 | 14/2018 | 04/2025 | 30/05/2025 | 1 | Emitida | R$ 898.750,69 | 11 | 1.130430 | R$ 1.015.974,90 |
| 26 | 159796 | 55046 | 14/2018 | 05/2025 | 30/06/2025 | 1 | Emitida | R$ 123.025,58 | 10 | 1.118131 | R$ 137.558,68 |
| 27 | 159797 | 55047 | 14/2018 | 05/2025 | 30/06/2025 | 1 | Emitida | R$ 353.200,00 | 10 | 1.118131 | R$ 394.923,78 |
| 28 | 159798 | 55042 | 14/2018 | 05/2025 | 30/06/2025 | 1 | Emitida | R$ 134.008,96 | 10 | 1.118131 | R$ 149.839,54 |
| 29 | 159799 | 55045 | 14/2018 | 05/2025 | 30/06/2025 | 1 | Emitida | R$ 9.051,74 | 10 | 1.118131 | R$ 10.121,03 |
| 30 | 159998 | 55044 | 14/2018 | 05/2025 | 30/06/2025 | 1 | Emitida | R$ 147.205,04 | 10 | 1.118131 | R$ 164.594,48 |
| 31 | 159999 | 55043 | 14/2018 | 05/2025 | 30/06/2025 | 1 | Emitida | R$ 892.813,84 | 10 | 1.118131 | R$ 998.282,60 |
| 32 | 160729 | 55848 | 14/2018 | 06/2025 | 30/07/2025 | 1 | Emitida | R$ 9.051,74 | 9 | 1.104000 | R$ 9.993,12 |
| 33 | 160730 | 55851 | 14/2018 | 06/2025 | 30/07/2025 | 1 | Emitida | R$ 134.008,96 | 9 | 1.104000 | R$ 147.945,83 |
| 34 | 160731 | 55850 | 14/2018 | 06/2025 | 30/07/2025 | 1 | Emitida | R$ 353.200,00 | 9 | 1.104000 | R$ 389.932,64 |
| 35 | 160732 | 55849 | 14/2018 | 06/2025 | 30/07/2025 | 1 | Emitida | R$ 123.025,58 | 9 | 1.104000 | R$ 135.820,18 |
| 36 | 160787 | 55847 | 14/2018 | 06/2025 | 30/07/2025 | 1 | Emitida | R$ 133.898,10 | 9 | 1.104000 | R$ 147.823,44 |
| 37 | 160788 | 55846 | 14/2018 | 06/2025 | 30/07/2025 | 1 | Emitida | R$ 883.929,50 | 9 | 1.104000 | R$ 975.857,77 |
| 38 | 161429 | 56646 | 14/2018 | 07/2025 | 30/08/2025 | 1 | Emitida | R$ 9.051,74 | 8 | 1.091340 | R$ 9.878,53 |
| 39 | 161430 | 56645 | 14/2018 | 07/2025 | 30/08/2025 | 1 | Emitida | R$ 134.008,96 | 8 | 1.091340 | R$ 146.249,34 |
| 40 | 161431 | 56642 | 14/2018 | 07/2025 | 30/08/2025 | 1 | Emitida | R$ 353.200,00 | 8 | 1.091340 | R$ 385.461,29 |
| 41 | 161432 | 56644 | 14/2018 | 07/2025 | 30/08/2025 | 1 | Emitida | R$ 123.025,58 | 8 | 1.091340 | R$ 134.262,74 |
| 42 | 161609 | 56643 | 14/2018 | 07/2025 | 30/08/2025 | 1 | Emitida | R$ 156.545,39 | 8 | 1.091340 | R$ 170.844,25 |
| 43 | 161610 | 56641 | 14/2018 | 07/2025 | 30/08/2025 | 1 | Emitida | R$ 886.264,10 | 8 | 1.091340 | R$ 967.215,47 |
| 44 | 162437 | 57468 | 14/2018 | 08/2025 | 30/09/2025 | 1 | Emitida | R$ 123.025,58 | 7 | 1.078186 | R$ 132.644,47 |
| 45 | 162438 | 57465 | 14/2018 | 08/2025 | 30/09/2025 | 1 | Emitida | R$ 353.200,00 | 7 | 1.078186 | R$ 380.815,34 |
| 46 | 162439 | 57464 | 14/2018 | 08/2025 | 30/09/2025 | 1 | Emitida | R$ 134.008,96 | 7 | 1.078186 | R$ 144.486,60 |
| 47 | 162440 | 57467 | 14/2018 | 08/2025 | 30/09/2025 | 1 | Emitida | R$ 9.051,74 | 7 | 1.078186 | R$ 9.759,46 |
| 48 | 162441 | 57466 | 14/2018 | 08/2025 | 30/09/2025 | 1 | Emitida | R$ 164.060,40 | 7 | 1.078186 | R$ 176.887,65 |
| 49 | 162442 | 57463 | 14/2018 | 08/2025 | 30/09/2025 | 1 | Emitida | R$ 1.002.289,26 | 7 | 1.078186 | R$ 1.080.654,38 |
| 50 | 163243 | 58231 | 14/2018 | 09/2025 | 30/10/2025 | 1 | Emitida | R$ 9.051,74 | 6 | 1.064560 | R$ 9.636,12 |
| 51 | 163244 | 58233 | 14/2018 | 09/2025 | 30/10/2025 | 1 | Emitida | R$ 134.008,96 | 6 | 1.064560 | R$ 142.660,55 |
| 52 | 163245 | 58230 | 14/2018 | 09/2025 | 30/10/2025 | 1 | Emitida | R$ 353.200,00 | 6 | 1.064560 | R$ 376.002,51 |
| 53 | 163246 | 58232 | 14/2018 | 09/2025 | 30/10/2025 | 1 | Emitida | R$ 123.025,58 | 6 | 1.064560 | R$ 130.968,08 |
| 54 | 163247 | 58229 | 14/2018 | 09/2025 | 30/10/2025 | 1 | Emitida | R$ 187.875,22 | 6 | 1.064560 | R$ 200.004,40 |
| 55 | 163248 | 58228 | 14/2018 | 09/2025 | 30/10/2025 | 1 | Emitida | R$ 1.003.760,37 | 6 | 1.064560 | R$ 1.068.562,91 |
| 56 | 163868 | 59058 | 14/2018 | 10/2025 | 30/11/2025 | 1 | Emitida | R$ 9.051,74 | 5 | 1.053498 | R$ 9.535,99 |
| 57 | 163869 | 59059 | 14/2018 | 10/2025 | 30/11/2025 | 1 | Emitida | R$ 134.008,96 | 5 | 1.053498 | R$ 141.178,18 |
| 58 | 163870 | 59057 | 14/2018 | 10/2025 | 30/11/2025 | 1 | Emitida | R$ 353.200,00 | 5 | 1.053498 | R$ 372.095,51 |
| 59 | 163871 | 59060 | 14/2018 | 10/2025 | 30/11/2025 | 1 | Emitida | R$ 123.025,58 | 5 | 1.053498 | R$ 129.607,21 |
| 60 | 164104 | 59056 | 14/2018 | 10/2025 | 30/11/2025 | 1 | Emitida | R$ 181.753,63 | 5 | 1.053498 | R$ 191.477,09 |
| 61 | 164105 | 59055 | 14/2018 | 10/2025 | 30/11/2025 | 1 | Emitida | R$ 989.383,85 | 5 | 1.053498 | R$ 1.042.313,95 |
| 62 | 164628 | 60069 | 14/2018 | 11/2025 | 30/12/2025 | 1 | Emitida | R$ 9.051,74 | 4 | 1.040800 | R$ 9.421,05 |
| 63 | 164629 | 60074 | 14/2018 | 11/2025 | 30/12/2025 | 1 | Emitida | R$ 134.008,96 | 4 | 1.040800 | R$ 139.476,56 |
| 64 | 164630 | 60073 | 14/2018 | 11/2025 | 30/12/2025 | 1 | Emitida | R$ 353.200,00 | 4 | 1.040800 | R$ 367.610,66 |
| 65 | 164631 | 60072 | 14/2018 | 11/2025 | 30/12/2025 | 1 | Emitida | R$ 123.025,58 | 4 | 1.040800 | R$ 128.045,06 |
| 66 | 165157 | 60071 | 14/2018 | 11/2025 | 30/12/2025 | 1 | Emitida | R$ 95.596,59 | 4 | 1.040800 | R$ 99.496,96 |
| 67 | 165305 | 60221 | 14/2018 | 11/2025 | 30/12/2025 | 1 | Emitida | R$ 519.741,03 | 4 | 1.040800 | R$ 540.946,61 |
| 68 | 164940 | 388 | 14/2018 | 12/2025 | 30/01/2026 | 1 | Emitida | R$ 9.051,74 | 3 | 1.028865 | R$ 9.313,02 |
| 69 | 164941 | 387 | 14/2018 | 12/2025 | 30/01/2026 | 1 | Emitida | R$ 134.008,96 | 3 | 1.028865 | R$ 137.877,19 |
| 70 | 164942 | 385 | 14/2018 | 12/2025 | 30/01/2026 | 1 | Emitida | R$ 353.200,00 | 3 | 1.028865 | R$ 363.395,27 |
| 71 | 164943 | 386 | 14/2018 | 12/2025 | 30/01/2026 | 1 | Emitida | R$ 123.025,58 | 3 | 1.028865 | R$ 126.576,77 |
| 72 | 166071 | 383 | 14/2018 | 12/2025 | 30/01/2026 | 1 | Emitida | R$ 84.394,28 | 3 | 1.028865 | R$ 86.830,36 |
| 73 | 166072 | 384 | 14/2018 | 12/2025 | 30/01/2026 | 1 | Emitida | R$ 519.857,73 | 3 | 1.028865 | R$ 534.863,65 |
| 74 | 155127 | 50349 | 2/2021 | 11/2024 | 30/12/2024 | 1 | Emitida | R$ 195.120,54 | 16 | 1.189976 | R$ 232.188,69 |
| 75 | 155525 | 50650 | 2/2021 | 12/2024 | 30/01/2025 | 1 | Emitida | R$ 195.120,54 | 15 | 1.178077 | R$ 229.867,03 |
| 76 | 154422 | 49673 | 20/2022 | 10/2024 | 30/11/2024 | 1 | Emitida | R$ 1.273.521,48 | 17 | 1.201042 | R$ 1.529.553,32 |
| 77 | 154425 | 49672 | 20/2022 | 10/2024 | 30/11/2024 | 1 | Emitida | R$ 390.085,64 | 17 | 1.201042 | R$ 468.509,40 |
| 78 | 155272 | 50426 | 20/2022 | 11/2024 | 30/12/2024 | 1 | Emitida | R$ 283.141,89 | 16 | 1.189976 | R$ 336.931,95 |
| 79 | 155273 | 50425 | 20/2022 | 11/2024 | 30/12/2024 | 1 | Emitida | R$ 1.377.022,68 | 16 | 1.189976 | R$ 1.638.623,45 |
| 80 | 155527 | 50651 | 20/2022 | 12/2024 | 30/01/2025 | 1 | Emitida | R$ 283.141,89 | 15 | 1.178077 | R$ 333.562,97 |
| 81 | 155536 | 50725 | 20/2022 | 12/2024 | 30/01/2025 | 1 | Emitida | R$ 1.167.705,65 | 15 | 1.178077 | R$ 1.375.647,25 |
| 82 | 156790 | 51924 | 20/2022 | 01/2025 | 02/03/2025 | 1 | Parcialmente Paga | R$ 1.377.022,68 | 13 | 1.155436 | R$ 1.591.061,92 |
| 83 | 157625 | 52792 | 20/2022 | 02/2025 | 30/03/2025 | 1 | Emitida | R$ 1.434.464,68 | 13 | 1.155436 | R$ 1.657.432,48 |
| 84 | 158371 | 53510 | 20/2022 | 03/2025 | 30/04/2025 | 1 | Emitida | R$ 1.434.464,68 | 12 | 1.143317 | R$ 1.640.047,98 |
| 85 | 159169 | 54292 | 20/2022 | 04/2025 | 30/05/2025 | 1 | Emitida | R$ 1.434.464,68 | 11 | 1.130430 | R$ 1.621.562,17 |
| 86 | 160535 | 55579 | 20/2022 | 05/2025 | 30/06/2025 | 1 | Emitida | R$ 1.439.753,04 | 10 | 1.118131 | R$ 1.609.832,14 |
| 87 | 160790 | 55863 | 20/2022 | 06/2025 | 30/07/2025 | 1 | Emitida | R$ 1.439.753,04 | 9 | 1.104000 | R$ 1.589.486,71 |
| 88 | 160791 | 55862 | 20/2022 | 06/2025 | 30/07/2025 | 1 | Emitida | R$ 209.445,61 | 9 | 1.104000 | R$ 231.227,86 |
| 89 | 161637 | 56684 | 20/2022 | 07/2025 | 30/08/2025 | 1 | Emitida | R$ 1.440.272,24 | 8 | 1.091340 | R$ 1.571.826,71 |
| 90 | 161638 | 56683 | 20/2022 | 07/2025 | 30/08/2025 | 1 | Emitida | R$ 209.445,61 | 8 | 1.091340 | R$ 228.576,37 |
| 91 | 162718 | 57731 | 20/2022 | 08/2025 | 30/09/2025 | 1 | Emitida | R$ 1.440.272,24 | 7 | 1.078186 | R$ 1.552.881,56 |
| 92 | 163239 | 58223 | 20/2022 | 09/2025 | 30/10/2025 | 1 | Emitida | R$ 1.466.822,97 | 6 | 1.064560 | R$ 1.561.520,72 |
| 93 | 164103 | 59054 | 20/2022 | 10/2025 | 30/11/2025 | 1 | Emitida | R$ 1.466.825,77 | 5 | 1.053498 | R$ 1.545.298,07 |
| 94 | 165304 | 60220 | 20/2022 | 11/2025 | 30/12/2025 | 1 | Emitida | R$ 1.468.611,61 | 4 | 1.040800 | R$ 1.528.531,37 |
| 95 | 166073 | 382 | 20/2022 | 12/2025 | 30/01/2026 | 1 | Emitida | R$ 1.466.822,97 | 3 | 1.028865 | R$ 1.509.163,46 |
| 96 | 167169 | 167169 | 21/2026 | 03/2026 | 30/04/2026 | 1 | Emitida | R$ 139.800,00 | 0 | 1.000000 | R$ 139.800,00 |
| 97 | 141565 | 37928 | 23/2021 | 05/2023 | 30/06/2023 | 1 | Parcialmente Paga | R$ 1.449.441,38 | 34 | 1.400578 | R$ 2.030.056,30 |
| 98 | 145317 | 41278 | 23/2021 | 10/2023 | 30/11/2023 | 1 | Emitida | R$ 1.448.755,22 | 29 | 1.331286 | R$ 1.928.706,99 |
| 99 | 146031 | 41899 | 23/2021 | 11/2023 | 30/12/2023 | 1 | Emitida | R$ 1.454.992,31 | 28 | 1.319542 | R$ 1.919.923,02 |
| 100 | 146667 | 42489 | 23/2021 | 12/2023 | 30/01/2024 | 1 | Emitida | R$ 1.458.649,43 | 27 | 1.306865 | R$ 1.906.258,04 |
| 101 | 163238 | 58226 | 23/2021 | 09/2025 | 30/10/2025 | 1 | Emitida | R$ 1.458.753,43 | 6 | 1.064560 | R$ 1.552.930,21 |
| 102 | 164099 | 59049 | 23/2021 | 10/2025 | 30/11/2025 | 1 | Emitida | R$ 1.458.776,53 | 5 | 1.053498 | R$ 1.536.818,21 |
| 103 | 165291 | 60114 | 23/2021 | 11/2025 | 30/12/2025 | 1 | Emitida | R$ 1.458.761,44 | 4 | 1.040800 | R$ 1.518.279,31 |
| 104 | 166074 | 381 | 23/2021 | 12/2025 | 30/01/2026 | 1 | Emitida | R$ 1.458.764,46 | 3 | 1.028865 | R$ 1.500.872,33 |
| 105 | 142845 | 39137 | 54/2017 | 07/2023 | 30/08/2023 | 1 | Emitida | R$ 706,41 | 32 | 1.370131 | R$ 967,87 |
| 106 | 142846 | 39136 | 54/2017 | 07/2023 | 30/08/2023 | 1 | Emitida | R$ 1.953,43 | 32 | 1.370131 | R$ 2.676,46 |

\* Venc. estimado = fim do mês de competência + 30 dias (fonte preliminar).
\** A coluna *Situação/Cadeia* reflete a classificação **registral no SPCF** (vínculos NE/NF no sistema), e **não** a posse dos documentos físicos — ver Ressalva 3.

---

## 5. Totais e Cenários

| Métrica | Valor |
|---------|------:|
| Principal bruto (exigíveis) | R$ 54.535.717,29 |
| Correção + juros SELIC | R$ 6.949.003,40 |
| **VALOR ATUALIZADO TOTAL** | **R$ 61.484.720,69** |
| Honorários (20%) | R$ 12.296.944,14 |

| Cenário | Faturas | Principal | Atualizado | Honorários 20% |
|---------|--------:|----------:|-----------:|---------------:|
| Conservador — só 'Emitida' exigíveis | 104 | R$ 51.709.253,23 | R$ 57.863.602,47 | R$ 11.572.720,49 |
| Base — todas exigíveis (Tier 1 + Tier 2) | 106 | R$ 54.535.717,29 | R$ 61.484.720,69 | R$ 12.296.944,14 |
| _Referência SSOT (universo histórico 84 fat.)_ | 84 | R$ 49.215.512,48¹ | R$ 50.263.263,56 | — |

¹ exigível do profile (mar/2026). Referências de expectativa: EV R$ 34.450.858,74 · Monte Carlo p50 R$ 24.391.879,65.

---

## 6. Caráter Preliminar e Ressalvas

1. **Memorial preliminar** para fins de apresentação interna/TRD; não substitui memorial pericial de execução.
2. **Regime presumido** (SELIC/EC 113) — confirmar na cláusula econômica dos 6 contratos (14/2018, 20/2022, 23/2021, 2/2021, 54/2017, 21/2026) via `extracao-clausulas-contratuais`.
3. **Sem título executivo nesta data** (blindagem 20/22 → recomendação **MONITORIA**). A classificação 'COMPLETA/FORTE' do anexo refere-se à cadeia **registral no SPCF**; os **documentos físicos** (contratos em PDF e atestos) ainda não foram reunidos — o REsp 793.969/RJ exige a composição documental material (Contrato + NE + NF + Atesto).
4. **Negativa expressa** (Of. 316/2020-GS/SEDUC) não constitui renúncia nem interrompe prescrição (Tema 1.109/STJ) — deverá ser enfrentada com a cadeia documental completa (Contrato + NE + NF + Atesto) de cada fatura.
5. **Decreto Estadual AM 53.464/2026** — verificar as 4 exceções (art. 1º §§1º-4º) antes de qualquer ação contra o Estado.
6. Faturas **Parcialmente Pagas** computadas pelo bruto no cenário Base; abater pagamentos parciais com extrato SPCF antes de qualquer peça.
7. Valores **atualizados até 04/2026** (última SELIC fechada no cache local). A SELIC de mai/2026 possivelmente já está disponível na série SGS 4390 — atualizar o cache (`baixar_indices_bcb.py`) e regerar antes do protocolo; os valores presentes são, portanto, **conservadores (a menor)**.
8. **Termo inicial da mora (dies a quo)** — com vencimentos estimados e sem cláusula contratual de prazo de pagamento em mãos, a defesa sustentará mora *ex persona* (Art. 397, parágrafo único, CC) com juros só da citação (Art. 405 CC). Antes de qualquer peça: obter vencimentos reais do SPCF e a cláusula de prazo de cada contrato; se necessário, estruturar cálculo bifásico (correção desde a exigibilidade / juros conforme cláusula ou citação).
9. **Vigência contratual dos CTs antigos** — CT 14/2018 é cobrado até a competência 12/2025 (8º ano) e CT 54/2017 até 07/2023 (7º ano) **sem termos aditivos de prorrogação mapeados nesta data**. Mapear a cadeia de vigência (TAs) no acervo DPCON/pendrive antes de qualquer peça; inexistindo prorrogação válida, a causa de pedir dessas faturas muda (vedação ao enriquecimento sem causa), com outro regime de encargos. Exposição: R$ 19.853.061,12 (CT 14/2018).
10. As NEs 2025-2026 são, nesta data, **elemento corroborativo** da relação contratual — o universo deste memorial não depende de marco interruptivo (Tier 2 = 0; primeira prescrição 30/06/2028). Como a interrupção é única (REsp 1.963.067/MS), não invocar marco sem vinculação NE↔fatura comprovada.

---

Manaus/AM, 11/06/2026.

**Gabriel Mar** — OAB/AM 15.697  
Gabriel Mar Sociedade Individual de Advocacia