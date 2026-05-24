# Reconciliação 4 Fontes — Projeto PRODAM

**Data:** 20/04/2026 07:04
**Devedores analisados:** 70

## Resumo Executivo

| Métrica | Valor |
|---------|-------|
| Total exigível (profiles.json) | R$ 93.632.770,88 |
| Total bruto (prodam.db) | R$ 108.161.955,58 |
| Divergências detectadas | 89 |
| Devedores sem dossiê | 10 |
| Alertas críticos (>20% diff) | 33 |

## ALERTAS CRÍTICOS (divergência > 20%)

| Devedor | profiles.json (val_orig) | prodam.db (bruto) | Diff % |
|---------|------------------------|-------------------|--------|
| ADS | R$ 211.657,47 | R$ 10.230,60 | 95.2% |
| CBMAM | R$ 27.570,74 | R$ 1.398,60 | 94.9% |
| FVS | R$ 253.753,07 | R$ 14.638,55 | 94.2% |
| FMT | R$ 390.275,52 | R$ 23.228,19 | 94.0% |
| FHAJ | R$ 304.898,42 | R$ 28.541,60 | 90.6% |
| FCECON | R$ 581.141,44 | R$ 68.362,95 | 88.2% |
| DPE | R$ 28.060,05 | R$ 4.662,12 | 83.4% |
| SECT | R$ 222.910,14 | R$ 38.747,15 | 82.6% |
| SEFAZ | R$ 188.362,64 | R$ 39.025,32 | 79.3% |
| SEAD | R$ 2.772.731,09 | R$ 4.941.372,73 | 78.2% |
| FHEMOAM | R$ 7.743,77 | R$ 1.688,61 | 78.2% |
| SEINFRA | R$ 294.139,13 | R$ 71.805,43 | 75.6% |
| FUNTEA | R$ 23.998,67 | R$ 6.346,65 | 73.6% |
| SES/SUSAM | R$ 22.406.424,64 | R$ 6.752.368,26 | 69.9% |
| AMAZONPREV | R$ 777.884,59 | R$ 277.932,98 | 64.3% |
| SEPROR | R$ 103.810,40 | R$ 38.581,46 | 62.8% |
| FAAR/SEDEL | R$ 877.764,20 | R$ 364.632,44 | 58.5% |
| FENIXSOFT | R$ 888.250,00 | R$ 1.405.000,00 | 58.2% |
| SEMA | R$ 35.326,64 | R$ 14.934,45 | 57.7% |
| SEAS | R$ 474.659,77 | R$ 219.783,61 | 53.7% |
| SSP | R$ 12.532.319,38 | R$ 6.290.728,66 | 49.8% |
| IPAAM | R$ 465.482,72 | R$ 233.596,95 | 49.8% |
| SUHAB | R$ 710.644,00 | R$ 364.460,14 | 48.7% |
| IDAM | R$ 505.375,17 | R$ 268.974,18 | 46.8% |
| POLÍCIA CIVIL | R$ 1.066.717,79 | R$ 625.567,97 | 41.4% |
| SEDUC | R$ 38.705.633,18 | R$ 54.535.717,29 | 40.9% |
| PMAM | R$ 24.351,49 | R$ 15.075,80 | 38.1% |
| SEDECTI | R$ 2.012.035,99 | R$ 1.319.548,29 | 34.4% |
| UGPI | R$ 353.473,42 | R$ 234.247,40 | 33.7% |
| BANCO SAFRA | R$ 9.310,00 | R$ 12.102,00 | 30.0% |
| PGE | R$ 849.643,14 | R$ 1.083.736,85 | 27.6% |
| BANCO BMG | R$ 39.242,00 | R$ 48.574,00 | 23.8% |
| ITRANSITO | R$ 38.360,67 | R$ 46.954,40 | 22.4% |

## Tabela Consolidada por Devedor

| Devedor | Cat. | Val Exig (profiles) | Val Orig (profiles) | Bruto (DB) | Fat Prof | Fat DB | SPCF JSON | Dossiê | Diverg. |
|---------|------|--------------------|--------------------|------------|----------|--------|-----------|--------|---------|
| SEDUC | GOV | R$ 49.215.512,48 | R$ 38.705.633,18 | R$ 54.535.717,29 | 84 | 106 | 106 | OK | **2** |
| SES/SUSAM | GOV | R$ 14.748.048,96 | R$ 22.406.424,64 | R$ 6.752.368,26 | 324 | 110 | 110 | OK | **2** |
| SSP | GOV | R$ 4.553.230,80 | R$ 12.532.319,38 | R$ 6.290.728,66 | 196 | 82 | 84 | OK | **3** |
| SEJUSC | GOV | R$ 2.589.660,12 | R$ 3.025.777,73 | R$ 2.434.441,61 | 165 | 58 | 58 | OK | **2** |
| SEAD | GOV | R$ 2.339.702,20 | R$ 2.772.731,09 | R$ 4.941.372,73 | 69 | 56 | 56 | OK | **2** |
| BRADESCO | EMP | R$ 2.226.517,80 | R$ 2.226.517,80 | R$ 0,00 | 115 | 0 | - | FALTA | **1** |
| CETAM | GOV | R$ 1.256.564,28 | R$ 1.256.564,28 | R$ 0,00 | 16 | 0 | - | OK | 0 |
| SEDECTI | GOV | R$ 1.249.203,13 | R$ 2.012.035,99 | R$ 1.319.548,29 | 228 | 42 | 42 | OK | **2** |
| SALUX | EMP | R$ 1.027.949,15 | R$ 1.027.949,15 | R$ 0,00 | 16 | 0 | - | FALTA | **1** |
| POLÍCIA CIVIL | GOV | R$ 960.481,71 | R$ 1.066.717,79 | R$ 625.567,97 | 56 | 18 | 18 | OK | **2** |
| BANCO MASTER | EMP | R$ 889.270,87 | R$ 889.270,87 | R$ 893.374,87 | 51 | 51 | 51 | OK | 0 |
| FENIXSOFT | EMP | R$ 888.250,00 | R$ 888.250,00 | R$ 1.405.000,00 | 7 | 7 | 7 | OK | **1** |
| CAIXA | EMP | R$ 844.328,88 | R$ 844.328,88 | R$ 920.891,34 | 60 | 60 | 60 | OK | **1** |
| SUHAB | GOV | R$ 840.061,15 | R$ 710.644,00 | R$ 364.460,14 | 123 | 13 | 13 | OK | **2** |
| AMAZONPREV | GOV | R$ 736.219,79 | R$ 777.884,59 | R$ 277.932,98 | 23 | 5 | 5 | OK | **2** |
| FAAR/SEDEL | GOV | R$ 734.498,94 | R$ 877.764,20 | R$ 364.632,44 | 221 | 72 | 72 | OK | **2** |
| PGE | GOV | R$ 680.239,77 | R$ 849.643,14 | R$ 1.083.736,85 | 47 | 46 | 46 | OK | **2** |
| IPAAM | GOV | R$ 652.339,89 | R$ 465.482,72 | R$ 233.596,95 | 58 | 19 | 19 | OK | **2** |
| SEAS | GOV | R$ 651.041,09 | R$ 474.659,77 | R$ 219.783,61 | 63 | 25 | 25 | OK | **2** |
| FCECON | GOV | R$ 637.106,68 | R$ 581.141,44 | R$ 68.362,95 | 113 | 11 | 11 | OK | **2** |
| PROVER | EMP | R$ 549.105,70 | R$ 549.105,70 | R$ 600.636,00 | 48 | 48 | - | OK | **1** |
| SETRAB | GOV | R$ 505.961,79 | R$ 505.961,79 | R$ 0,00 | 81 | 0 | - | FALTA | **1** |
| SEINFRA | GOV | R$ 379.631,55 | R$ 294.139,13 | R$ 71.805,43 | 38 | 12 | 12 | OK | **2** |
| UGPI | GOV | R$ 353.473,42 | R$ 353.473,42 | R$ 234.247,40 | 18 | 4 | 3 | FALTA | **4** |
| IDAM | GOV | R$ 328.735,51 | R$ 505.375,17 | R$ 268.974,18 | 35 | 7 | 7 | OK | **2** |
| FVS | GOV | R$ 321.372,96 | R$ 253.753,07 | R$ 14.638,55 | 23 | 1 | 1 | OK | **2** |
| SEJEL | GOV | R$ 280.242,25 | R$ 280.242,25 | R$ 0,00 | 96 | 0 | - | OK | 0 |
| FMT | GOV | R$ 272.130,68 | R$ 390.275,52 | R$ 23.228,19 | 83 | 3 | 3 | OK | **2** |
| FHAJ | GOV | R$ 259.910,78 | R$ 304.898,42 | R$ 28.541,60 | 75 | 6 | 6 | OK | **2** |
| SECT | GOV | R$ 258.328,58 | R$ 222.910,14 | R$ 38.747,15 | 44 | 8 | 8 | OK | **2** |
| SEMIG | GOV | R$ 235.353,15 | R$ 0,00 | R$ 235.353,15 | 30 | 30 | 30 | OK | 0 |
| ADS | GOV | R$ 211.657,47 | R$ 211.657,47 | R$ 10.230,60 | 119 | 6 | 6 | OK | **2** |
| SEFAZ | GOV | R$ 198.980,49 | R$ 188.362,64 | R$ 39.025,32 | 5 | 5 | 5 | OK | **1** |
| BRADESCO FINANCIAMENTO | EMP | R$ 194.783,80 | R$ 194.783,80 | R$ 194.783,80 | 72 | 72 | - | FALTA | **1** |
| CPA | EMP | R$ 165.830,96 | R$ 165.830,96 | R$ 165.830,96 | 6 | 6 | 6 | OK | 0 |
| ADAF | GOV | R$ 149.600,91 | R$ 149.600,91 | R$ 122.182,04 | 44 | 27 | 27 | OK | **2** |
| AADESAM | GOV | R$ 125.682,90 | R$ 125.682,90 | R$ 0,00 | 34 | 0 | - | FALTA | **1** |
| IKM DE | EMP | R$ 116.263,60 | R$ 116.263,60 | R$ 116.263,60 | 12 | 12 | 12 | OK | 0 |
| ANOREG | EMP | R$ 102.267,91 | R$ 102.267,91 | R$ 102.286,08 | 12 | 12 | 12 | OK | 0 |
| BANCO DAYCOVAL | EMP | R$ 99.481,64 | R$ 0,00 | R$ 99.481,64 | 4 | 4 | 4 | FALTA | **1** |
| SEC | GOV | R$ 99.050,71 | R$ 152.126,16 | R$ 182.178,56 | 23 | 7 | 7 | OK | **2** |
| SEPROR | GOV | R$ 77.960,49 | R$ 103.810,40 | R$ 38.581,46 | 25 | 3 | 3 | OK | **2** |
| BMC | EMP | R$ 58.142,00 | R$ 58.142,00 | R$ 58.142,00 | 6 | 6 | 6 | OK | 0 |
| ARSEPAM | GOV | R$ 49.618,85 | R$ 35.923,02 | R$ 30.809,93 | 23 | 20 | 20 | OK | **2** |
| FUAM/FUHAM | GOV | R$ 44.020,01 | R$ 368.561,63 | R$ 0,00 | 75 | 0 | - | OK | 0 |
| BANCO BMG | EMP | R$ 39.242,00 | R$ 39.242,00 | R$ 48.574,00 | 10 | 10 | 10 | OK | **1** |
| SEMA | GOV | R$ 38.541,11 | R$ 35.326,64 | R$ 14.934,45 | 10 | 2 | 2 | OK | **2** |
| ITRANSITO | EMP | R$ 38.360,67 | R$ 38.360,67 | R$ 46.954,40 | 12 | 12 | 12 | OK | **1** |
| ASSOC. DE GESTÃO INOVAÇÃO E RES. EM SAÚDE | EMP | R$ 34.760,79 | R$ 34.760,79 | R$ 34.760,79 | 0 | 6 | - | OK | 0 |
| FUNTEA | GOV | R$ 34.186,19 | R$ 23.998,67 | R$ 6.346,65 | 11 | 3 | 3 | OK | **2** |
| BANCO SICOOB | EMP | R$ 30.290,00 | R$ 30.290,00 | R$ 32.618,00 | 21 | 21 | 21 | OK | **1** |
| DPE | GOV | R$ 28.060,05 | R$ 28.060,05 | R$ 4.662,12 | 7 | 1 | 1 | OK | **2** |
| FMPES | GOV | R$ 27.264,57 | R$ 27.264,57 | R$ 0,00 | 3 | 0 | - | FALTA | **1** |
| PMAM | GOV | R$ 27.020,90 | R$ 24.351,49 | R$ 15.075,80 | 13 | 2 | 2 | OK | **2** |
| CGE | GOV | R$ 25.693,37 | R$ 25.693,37 | R$ 0,00 | 9 | 0 | - | OK | 0 |
| SNPH | GOV | R$ 25.117,34 | R$ 17.526,63 | R$ 19.802,66 | 8 | 13 | 13 | OK | **2** |
| PSA TECHNOLOGY | EMP | R$ 21.007,21 | R$ 21.007,21 | R$ 0,00 | 0 | 0 | - | OK | 0 |
| CASA CIVIL | GOV | R$ 20.927,09 | R$ 0,00 | R$ 20.927,09 | 4 | 4 | 4 | OK | 0 |
| FJJA | GOV | R$ 20.596,36 | R$ 20.596,36 | R$ 0,00 | 5 | 0 | - | FALTA | **1** |
| SUL AMERICA | EMP | R$ 18.196,00 | R$ 18.196,00 | R$ 18.998,00 | 20 | 20 | 20 | OK | 0 |
| B23 TECNOLOGIA | EMP | R$ 11.892,24 | R$ 11.892,24 | R$ 12.039,08 | 3 | 3 | 3 | OK | 0 |
| BANCO SAFRA | EMP | R$ 9.310,00 | R$ 9.310,00 | R$ 12.102,00 | 6 | 6 | - | OK | **1** |
| ODONTOMED | EMP | R$ 7.541,10 | R$ 7.541,10 | R$ 7.350,00 | 14 | 14 | 14 | OK | 0 |
| EASYTECH | EMP | R$ 6.927,16 | R$ 6.927,16 | R$ 7.804,22 | 10 | 10 | 10 | OK | **1** |
| FHEMOAM | GOV | R$ 6.886,91 | R$ 7.743,77 | R$ 1.688,61 | 8 | 3 | 3 | OK | **2** |
| CBMAM | GOV | R$ 3.134,03 | R$ 27.570,74 | R$ 1.398,60 | 24 | 2 | 2 | OK | **2** |
| DETRAN | GOV | R$ 0,00 | R$ 22.745.276,48 | R$ 22.448.434,53 | 233 | 149 | 113 | OK | **2** |
| COSAMA | GOV | R$ 0,00 | R$ 0,00 | R$ 0,00 | 0 | 0 | - | OK | 0 |
| CASA MILITAR | GOV | R$ 0,00 | R$ 0,00 | R$ 0,00 | 0 | 0 | - | OK | 0 |
| _sync_meta | N/D | R$ 0,00 | R$ 0,00 | R$ 0,00 | 0 | 0 | - | FALTA | **1** |

## Detalhamento de Divergências

### SEDUC

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=84, db=106 (diff=22). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 38.705.633,18, db=R$ 54.535.717,29 (diff=40.9%). Diferença > 5% — verificar filtros de prescrição

### SES/SUSAM

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=324, db=110 (diff=214). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 22.406.424,64, db=R$ 6.752.368,26 (diff=69.9%). Diferença > 5% — verificar filtros de prescrição

### SSP

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=196, db=82 (diff=114). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 12.532.319,38, db=R$ 6.290.728,66 (diff=49.8%). Diferença > 5% — verificar filtros de prescrição
- **QTD_FATURAS_SPCF_VS_DB** (SPCF_JSON vs prodam.db): {"tipo": "QTD_FATURAS_SPCF_VS_DB", "fontes": "SPCF_JSON vs prodam.db", "spcf_json": 84, "db": 82, "diff": 2}

### SEJUSC

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=165, db=58 (diff=107). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 3.025.777,73, db=R$ 2.434.441,61 (diff=19.5%). Diferença > 5% — verificar filtros de prescrição

### SEAD

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=69, db=56 (diff=13). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 2.772.731,09, db=R$ 4.941.372,73 (diff=78.2%). Diferença > 5% — verificar filtros de prescrição

### BRADESCO

- **SEM_DOSSIE**: Nenhuma pasta *_DOSSIE encontrada para BRADESCO

### SEDECTI

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=228, db=42 (diff=186). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 2.012.035,99, db=R$ 1.319.548,29 (diff=34.4%). Diferença > 5% — verificar filtros de prescrição

### SALUX

- **SEM_DOSSIE**: Nenhuma pasta *_DOSSIE encontrada para SALUX

### POLÍCIA CIVIL

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=56, db=18 (diff=38). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 1.066.717,79, db=R$ 625.567,97 (diff=41.4%). Diferença > 5% — verificar filtros de prescrição

### FENIXSOFT

- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 888.250,00, db=R$ 1.405.000,00 (diff=58.2%). Diferença > 5% — verificar filtros de prescrição

### CAIXA

- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 844.328,88, db=R$ 920.891,34 (diff=9.1%). Diferença > 5% — verificar filtros de prescrição

### SUHAB

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=123, db=13 (diff=110). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 710.644,00, db=R$ 364.460,14 (diff=48.7%). Diferença > 5% — verificar filtros de prescrição

### AMAZONPREV

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=23, db=5 (diff=18). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 777.884,59, db=R$ 277.932,98 (diff=64.3%). Diferença > 5% — verificar filtros de prescrição

### FAAR/SEDEL

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=221, db=72 (diff=149). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 877.764,20, db=R$ 364.632,44 (diff=58.5%). Diferença > 5% — verificar filtros de prescrição

### PGE

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=47, db=46 (diff=1). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 849.643,14, db=R$ 1.083.736,85 (diff=27.6%). Diferença > 5% — verificar filtros de prescrição

### IPAAM

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=58, db=19 (diff=39). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 465.482,72, db=R$ 233.596,95 (diff=49.8%). Diferença > 5% — verificar filtros de prescrição

### SEAS

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=63, db=25 (diff=38). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 474.659,77, db=R$ 219.783,61 (diff=53.7%). Diferença > 5% — verificar filtros de prescrição

### FCECON

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=113, db=11 (diff=102). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 581.141,44, db=R$ 68.362,95 (diff=88.2%). Diferença > 5% — verificar filtros de prescrição

### PROVER

- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 549.105,70, db=R$ 600.636,00 (diff=9.4%). Diferença > 5% — verificar filtros de prescrição

### SETRAB

- **SEM_DOSSIE**: Nenhuma pasta *_DOSSIE encontrada para SETRAB

### SEINFRA

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=38, db=12 (diff=26). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 294.139,13, db=R$ 71.805,43 (diff=75.6%). Diferença > 5% — verificar filtros de prescrição

### UGPI

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=18, db=4 (diff=14). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 353.473,42, db=R$ 234.247,40 (diff=33.7%). Diferença > 5% — verificar filtros de prescrição
- **QTD_FATURAS_SPCF_VS_DB** (SPCF_JSON vs prodam.db): {"tipo": "QTD_FATURAS_SPCF_VS_DB", "fontes": "SPCF_JSON vs prodam.db", "spcf_json": 3, "db": 4, "diff": 1}
- **SEM_DOSSIE**: Nenhuma pasta *_DOSSIE encontrada para UGPI

### IDAM

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=35, db=7 (diff=28). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 505.375,17, db=R$ 268.974,18 (diff=46.8%). Diferença > 5% — verificar filtros de prescrição

### FVS

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=23, db=1 (diff=22). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 253.753,07, db=R$ 14.638,55 (diff=94.2%). Diferença > 5% — verificar filtros de prescrição

### FMT

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=83, db=3 (diff=80). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 390.275,52, db=R$ 23.228,19 (diff=94.0%). Diferença > 5% — verificar filtros de prescrição

### FHAJ

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=75, db=6 (diff=69). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 304.898,42, db=R$ 28.541,60 (diff=90.6%). Diferença > 5% — verificar filtros de prescrição

### SECT

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=44, db=8 (diff=36). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 222.910,14, db=R$ 38.747,15 (diff=82.6%). Diferença > 5% — verificar filtros de prescrição

### ADS

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=119, db=6 (diff=113). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 211.657,47, db=R$ 10.230,60 (diff=95.2%). Diferença > 5% — verificar filtros de prescrição

### SEFAZ

- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 188.362,64, db=R$ 39.025,32 (diff=79.3%). Diferença > 5% — verificar filtros de prescrição

### BRADESCO FINANCIAMENTO

- **SEM_DOSSIE**: Nenhuma pasta *_DOSSIE encontrada para BRADESCO FINANCIAMENTO

### ADAF

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=44, db=27 (diff=17). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 149.600,91, db=R$ 122.182,04 (diff=18.3%). Diferença > 5% — verificar filtros de prescrição

### AADESAM

- **SEM_DOSSIE**: Nenhuma pasta *_DOSSIE encontrada para AADESAM

### BANCO DAYCOVAL

- **SEM_DOSSIE**: Nenhuma pasta *_DOSSIE encontrada para BANCO DAYCOVAL

### SEC

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=23, db=7 (diff=16). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 152.126,16, db=R$ 182.178,56 (diff=19.8%). Diferença > 5% — verificar filtros de prescrição

### SEPROR

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=25, db=3 (diff=22). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 103.810,40, db=R$ 38.581,46 (diff=62.8%). Diferença > 5% — verificar filtros de prescrição

### ARSEPAM

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=23, db=20 (diff=3). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 35.923,02, db=R$ 30.809,93 (diff=14.2%). Diferença > 5% — verificar filtros de prescrição

### BANCO BMG

- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 39.242,00, db=R$ 48.574,00 (diff=23.8%). Diferença > 5% — verificar filtros de prescrição

### SEMA

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=10, db=2 (diff=8). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 35.326,64, db=R$ 14.934,45 (diff=57.7%). Diferença > 5% — verificar filtros de prescrição

### ITRANSITO

- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 38.360,67, db=R$ 46.954,40 (diff=22.4%). Diferença > 5% — verificar filtros de prescrição

### FUNTEA

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=11, db=3 (diff=8). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 23.998,67, db=R$ 6.346,65 (diff=73.6%). Diferença > 5% — verificar filtros de prescrição

### BANCO SICOOB

- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 30.290,00, db=R$ 32.618,00 (diff=7.7%). Diferença > 5% — verificar filtros de prescrição

### DPE

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=7, db=1 (diff=6). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 28.060,05, db=R$ 4.662,12 (diff=83.4%). Diferença > 5% — verificar filtros de prescrição

### FMPES

- **SEM_DOSSIE**: Nenhuma pasta *_DOSSIE encontrada para FMPES

### PMAM

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=13, db=2 (diff=11). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 24.351,49, db=R$ 15.075,80 (diff=38.1%). Diferença > 5% — verificar filtros de prescrição

### SNPH

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=8, db=13 (diff=5). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 17.526,63, db=R$ 19.802,66 (diff=13.0%). Diferença > 5% — verificar filtros de prescrição

### FJJA

- **SEM_DOSSIE**: Nenhuma pasta *_DOSSIE encontrada para FJJA

### BANCO SAFRA

- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 9.310,00, db=R$ 12.102,00 (diff=30.0%). Diferença > 5% — verificar filtros de prescrição

### EASYTECH

- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 6.927,16, db=R$ 7.804,22 (diff=12.7%). Diferença > 5% — verificar filtros de prescrição

### FHEMOAM

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=8, db=3 (diff=5). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 7.743,77, db=R$ 1.688,61 (diff=78.2%). Diferença > 5% — verificar filtros de prescrição

### CBMAM

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=24, db=2 (diff=22). DB pode incluir faturas de outros status
- **VALOR_ORIGINAL** (profiles.json(val_orig) vs prodam.db(valor_bruto)): profiles=R$ 27.570,74, db=R$ 1.398,60 (diff=94.9%). Diferença > 5% — verificar filtros de prescrição

### DETRAN

- **QTD_FATURAS** (profiles.json vs prodam.db): profiles=233, db=149 (diff=84). DB pode incluir faturas de outros status
- **QTD_FATURAS_SPCF_VS_DB** (SPCF_JSON vs prodam.db): {"tipo": "QTD_FATURAS_SPCF_VS_DB", "fontes": "SPCF_JSON vs prodam.db", "spcf_json": 113, "db": 149, "diff": 36}

### _sync_meta

- **SEM_DOSSIE**: Nenhuma pasta *_DOSSIE encontrada para _sync_meta

## Legenda

- **Val Exig**: Valor exigível (não prescrito) segundo profiles.json
- **Val Orig**: Valor original histórico (sem correção)
- **Bruto (DB)**: Soma de valor_bruto de todas as faturas no prodam.db (inclui prescritas)
- **Fat Prof / Fat DB**: Contagem de faturas no profiles.json vs prodam.db
- **SPCF JSON**: Faturas encontradas nos JSONs de SPCF_EXTRACAO/por_devedor/
- **Dossiê**: Se existe pasta *_DOSSIE com INVENTARIO.xlsx

### Fontes de Dados

1. **profiles.json** (SSOT) — Fonte autoritativa com valores consolidados por devedor
2. **prodam.db** — Banco SQLite com faturas e empenhos importados do SPCF
3. **SPCF_EXTRACAO/por_devedor/** — JSONs crus extraídos do sistema SPCF por web scraping
4. **PRODAM_DOCS/*_DOSSIE/** — Dossiês documentais com INVENTARIO.xlsx dos PDFs originais