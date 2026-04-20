# Drill-Down Fatura a Fatura — 5 Devedores Prioritários
**Data:** 14/04/2026

---
## DETRAN — Departamento Estadual de Trânsito do Amazonas

### 1. Profiles.json (SSOT)
| Campo | Valor |
|-------|-------|
| val_exig | R$ 31.684.739,01 |
| val_orig | R$ 22.745.276,48 |
| val_atualizado | R$ 37.960.629,19 |
| faturas_total | 233 |
| faturas_exigiveis | 179 |
| faturas_prescritas | 54 |
| cobrancas_spcf_count | 113 |
| num_faturas_spcf_mar2026 | 202 |
| spcf_fat_devidas_qtd | 214 |
| spcf_fat_devidas_val | R$ 20.848.440,34 |
| spcf_fat_aberto_qtd | 149 |
| spcf_fat_aberto_val | R$ 22.448.434,53 |

### 2. prodam.db — 113 faturas, R$ 17.802.420,55

**Por situação:**

| Situação | Qtd | Valor |
|----------|-----|-------|
| Emitida | 107 | R$ 16.069.705,56 |
| Parcialmente Paga | 6 | R$ 1.732.714,99 |

**Por contrato:**

| Contrato | Qtd | Valor |
|----------|-----|-------|
| 10/2021 | 21 | R$ 8.536.876,76 |
| 296/2025 | 4 | R$ 2.522.329,40 |
| 22/2014 | 9 | R$ 1.578.124,94 |
| 4/2016 | 5 | R$ 1.527.017,45 |
| 6/2021 | 40 | R$ 1.076.978,46 |
| 3/2026 | 1 | R$ 630.582,35 |
| 12/2021 | 7 | R$ 626.691,89 |
| 71/2022 | 2 | R$ 520.000,00 |
| 17/2015 | 4 | R$ 335.879,03 |
| 25/2014 | 6 | R$ 196.758,68 |
| 83/2022 | 5 | R$ 123.873,07 |
| 27/2014 | 5 | R$ 86.169,58 |
| 60/2022 | 1 | R$ 29.500,00 |
| 8/2021 | 3 | R$ 11.638,94 |

### 3. Empenhos (DB): 470 registros, R$ 250.316.057,30

### 4. SPCF JSON (DETRAN)
- Faturas: 113, total=R$ 16.561.585,39
- Match com DB: 113, só DB: 0, só SPCF: 0
- Divergências de valor: 6
- Empenhos JSON: 480

### 5. cobrancas.csv: 113 registros
- Total: R$ 16.561.585,39
- Status: {'Suspenso': 113}

### 6. Cruzamento Pendrive: 175 matches

### DIAGNÓSTICO

**120 faturas em profiles.json sem correspondência no banco.**
- profiles: 233 faturas (R$ 22.745.276,48 original)
- banco: 113 faturas (R$ 17.802.420,55 bruto)
- lacuna estimada: 120 faturas, ~R$ 4.942.855,93

**Origem provável da lacuna:**
- profiles.cobrancas_spcf_count = 113 = DB faturas → **O banco está correto para o SPCF atual**
- As 120 faturas extras vêm de fontes FORA do SPCF (PDFs antigos, planilhas manuais)
- Relatórios XLS do SPCF (rel_fat_emitidas/recebidas) podem conter faturas históricas já quitadas
- PDFs do pendrive podem registrar faturas pré-sistema SPCF

---
## SEDUC — Secretaria de Educação do Amazonas

### 1. Profiles.json (SSOT)
| Campo | Valor |
|-------|-------|
| val_exig | R$ 49.215.512,48 |
| val_orig | R$ 38.705.633,18 |
| val_atualizado | R$ 50.263.263,56 |
| faturas_total | 84 |
| faturas_exigiveis | 76 |
| faturas_prescritas | 8 |
| cobrancas_spcf_count | N/D |
| num_faturas_spcf_mar2026 | 128 |
| spcf_fat_devidas_qtd | 136 |
| spcf_fat_devidas_val | R$ 56.040.239,62 |
| spcf_fat_aberto_qtd | 120 |
| spcf_fat_aberto_val | R$ 60.107.842,84 |

### 2. prodam.db — 106 faturas, R$ 54.535.717,29

**Por situação:**

| Situação | Qtd | Valor |
|----------|-----|-------|
| Emitida | 104 | R$ 51.709.253,23 |
| Parcialmente Paga | 2 | R$ 2.826.464,06 |

**Por contrato:**

| Contrato | Qtd | Valor |
|----------|-----|-------|
| 20/2022 | 20 | R$ 22.503.061,05 |
| 14/2018 | 73 | R$ 19.853.061,12 |
| 23/2021 | 8 | R$ 11.646.894,20 |
| 2/2021 | 2 | R$ 390.241,08 |
| 21/2026 | 1 | R$ 139.800,00 |
| 54/2017 | 2 | R$ 2.659,84 |

### 3. Empenhos (DB): 286 registros, R$ 482.690.583,05

### 4. SPCF JSON (SEDUC)
- Faturas: 106, total=R$ 51.827.578,06
- Match com DB: 106, só DB: 0, só SPCF: 0
- Divergências de valor: 3
- Empenhos JSON: 288

### 5. cobrancas.csv: 105 registros
- Total: R$ 51.827.578,06
- Status: {'Suspenso': 105}

### 6. Cruzamento Pendrive: 45 matches

### DIAGNÓSTICO

**Banco tem 22 faturas A MAIS que profiles.json.**
- profiles: 84 faturas (R$ 38.705.633,18)
- banco: 106 faturas (R$ 54.535.717,29)
- Possível causa: faturas de contratos não contabilizados ou status não filtrado

---
## SSP — Secretaria de Segurança Pública

### 1. Profiles.json (SSOT)
| Campo | Valor |
|-------|-------|
| val_exig | R$ 4.553.230,80 |
| val_orig | R$ 12.532.319,38 |
| val_atualizado | R$ 29.034.062,63 |
| faturas_total | 196 |
| faturas_exigiveis | 81 |
| faturas_prescritas | 115 |
| cobrancas_spcf_count | N/D |
| num_faturas_spcf_mar2026 | 181 |
| spcf_fat_devidas_qtd | 191 |
| spcf_fat_devidas_val | R$ 10.725.242,83 |
| spcf_fat_aberto_qtd | 82 |
| spcf_fat_aberto_val | R$ 6.290.728,66 |

### 2. prodam.db — 82 faturas, R$ 6.290.728,66

**Por situação:**

| Situação | Qtd | Valor |
|----------|-----|-------|
| Emitida | 78 | R$ 6.270.764,85 |
| Parcialmente Paga | 4 | R$ 19.963,81 |

**Por contrato:**

| Contrato | Qtd | Valor |
|----------|-----|-------|
| 68/2012 | 12 | R$ 2.295.357,44 |
| 48/2021 | 52 | R$ 2.148.732,66 |
| 94/2011 | 3 | R$ 854.365,32 |
| 67/2012 | 4 | R$ 847.124,76 |
| 54/2015 | 4 | R$ 90.297,78 |
| 55/2015 | 1 | R$ 27.470,92 |
| 18/2025 | 2 | R$ 19.762,00 |
| 19/2025 | 4 | R$ 7.617,78 |

### 3. Empenhos (DB): 218 registros, R$ 136.963.244,94

### 4. SPCF JSON (SSP)
- Faturas: 84, total=R$ 6.697.257,65
- Match com DB: 82, só DB: 0, só SPCF: 2
- Divergências de valor: 7
- Empenhos JSON: 751

### 5. cobrancas.csv: 79 registros
- Total: R$ 6.263.161,36
- Status: {'Suspenso': 79}

### 6. Cruzamento Pendrive: 162 matches

### DIAGNÓSTICO

**114 faturas em profiles.json sem correspondência no banco.**
- profiles: 196 faturas (R$ 12.532.319,38 original)
- banco: 82 faturas (R$ 6.290.728,66 bruto)
- lacuna estimada: 114 faturas, ~R$ 6.241.590,72

**Origem provável da lacuna:**
- profiles tem campo SPCF = 181, DB = 82
- Relatórios XLS do SPCF (rel_fat_emitidas/recebidas) podem conter faturas históricas já quitadas
- PDFs do pendrive podem registrar faturas pré-sistema SPCF

---
## SES/SUSAM — Secretaria de Saúde do Amazonas / Fundação de Medicina Tropical

### 1. Profiles.json (SSOT)
| Campo | Valor |
|-------|-------|
| val_exig | R$ 14.748.048,96 |
| val_orig | R$ 22.406.424,64 |
| val_atualizado | R$ 43.921.619,17 |
| faturas_total | 324 |
| faturas_exigiveis | 144 |
| faturas_prescritas | 180 |
| cobrancas_spcf_count | N/D |
| num_faturas_spcf_mar2026 | 215 |
| spcf_fat_devidas_qtd | 228 |
| spcf_fat_devidas_val | R$ 11.877.761,92 |
| spcf_fat_aberto_qtd | 137 |
| spcf_fat_aberto_val | R$ 8.268.269,07 |

### 2. prodam.db — 110 faturas, R$ 6.752.368,26

**Por situação:**

| Situação | Qtd | Valor |
|----------|-----|-------|
| Emitida | 107 | R$ 6.543.207,54 |
| Parcialmente Paga | 3 | R$ 209.160,72 |

**Por contrato:**

| Contrato | Qtd | Valor |
|----------|-----|-------|
| 2/2015 | 20 | R$ 1.612.949,24 |
| 18/2021 | 24 | R$ 1.051.806,53 |
| 248/2016 | 16 | R$ 810.566,44 |
| 116/2013 | 14 | R$ 710.239,89 |
| 21/2021 | 12 | R$ 686.365,54 |
| 81/2010 | 4 | R$ 419.539,20 |
| 125/2016 | 5 | R$ 413.606,46 |
| 54/2018 | 2 | R$ 311.789,78 |
| 24/2016 | 2 | R$ 296.298,22 |
| 74/2021 | 4 | R$ 249.021,15 |
| 5/2021 | 6 | R$ 108.337,26 |
| 254/2017 | 1 | R$ 81.848,55 |

### 3. Empenhos (DB): 475 registros, R$ 107.076.806,49

### 4. SPCF JSON (SES_SUSAM)
- Faturas: 110, total=R$ 6.660.692,00
- Match com DB: 110, só DB: 0, só SPCF: 0
- Divergências de valor: 3
- Empenhos JSON: 478

### 5. cobrancas.csv: 110 registros
- Total: R$ 6.660.692,00
- Status: {'Suspenso': 110}

### 6. Cruzamento Pendrive: 42 matches

### DIAGNÓSTICO

**214 faturas em profiles.json sem correspondência no banco.**
- profiles: 324 faturas (R$ 22.406.424,64 original)
- banco: 110 faturas (R$ 6.752.368,26 bruto)
- lacuna estimada: 214 faturas, ~R$ 15.654.056,38

**Origem provável da lacuna:**
- profiles tem campo SPCF = 215, DB = 110
- Relatórios XLS do SPCF (rel_fat_emitidas/recebidas) podem conter faturas históricas já quitadas
- PDFs do pendrive podem registrar faturas pré-sistema SPCF

---
## SEAD — Secretaria de Administração

### 1. Profiles.json (SSOT)
| Campo | Valor |
|-------|-------|
| val_exig | R$ 2.339.702,20 |
| val_orig | R$ 2.772.731,09 |
| val_atualizado | R$ 4.296.278,76 |
| faturas_total | 69 |
| faturas_exigiveis | 25 |
| faturas_prescritas | 44 |
| cobrancas_spcf_count | N/D |
| num_faturas_spcf_mar2026 | 97 |
| spcf_fat_devidas_qtd | 105 |
| spcf_fat_devidas_val | R$ 5.293.077,30 |
| spcf_fat_aberto_qtd | 62 |
| spcf_fat_aberto_val | R$ 5.452.410,11 |

### 2. prodam.db — 56 faturas, R$ 4.941.372,73

**Por situação:**

| Situação | Qtd | Valor |
|----------|-----|-------|
| Emitida | 55 | R$ 4.714.414,31 |
| Parcialmente Paga | 1 | R$ 226.958,42 |

**Por contrato:**

| Contrato | Qtd | Valor |
|----------|-----|-------|
| 7/2020 | 13 | R$ 2.310.769,65 |
| 9/2022 | 3 | R$ 875.938,02 |
| 108/2022 | 2 | R$ 561.973,76 |
| 17/2016 | 4 | R$ 385.467,89 |
| 5/2017 | 2 | R$ 245.636,66 |
| 4/2025 | 6 | R$ 190.521,72 |
| 157/2020 | 1 | R$ 130.927,03 |
| 9/2015 | 4 | R$ 90.573,92 |
| 18/2016 | 3 | R$ 63.067,50 |
| 6/2020 | 6 | R$ 37.110,90 |
| 8/2022 | 5 | R$ 29.200,99 |
| 5/2020 | 6 | R$ 17.658,40 |
| 4/2020 | 1 | R$ 2.526,29 |

### 3. Empenhos (DB): 693 registros, R$ 91.267.344,85

### 4. SPCF JSON (SEAD)
- Faturas: 56, total=R$ 4.549.420,78
- Match com DB: 56, só DB: 0, só SPCF: 0
- Divergências de valor: 10
- Empenhos JSON: 707

### 5. cobrancas.csv: 47 registros
- Total: R$ 4.549.420,78
- Status: {'Suspenso': 47}

### 6. Cruzamento Pendrive: 51 matches

### DIAGNÓSTICO

**13 faturas em profiles.json sem correspondência no banco.**
- profiles: 69 faturas (R$ 2.772.731,09 original)
- banco: 56 faturas (R$ 4.941.372,73 bruto)
- lacuna estimada: 13 faturas, ~R$ -2.168.641,64

**Origem provável da lacuna:**
- profiles tem campo SPCF = 97, DB = 56
- Relatórios XLS do SPCF (rel_fat_emitidas/recebidas) podem conter faturas históricas já quitadas
- PDFs do pendrive podem registrar faturas pré-sistema SPCF
