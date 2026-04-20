# Auditoria de Cobertura Documental — 66 Devedores
**Data:** 14/04/2026 | **Fonte:** prodam.db (reconstruído) + SPCF_EXTRACAO + PRODAM_DOCS

## Resumo Executivo

| Métrica | Valor |
|---------|-------|
| Devedores analisados | 66 |
| Total de lacunas detectadas | 103 |
| Devedores sem lacunas (OK) | 8 |
| Devedores com gap CRÍTICO | 8 |
| Devedores com gap ALTO | 35 |

## Lacunas por Tipo

| Tipo de Lacuna | Devedores afetados | Valor exigível em risco | O que falta |
|----------------|-------------------|------------------------|-------------|
| FATURAS_INCOMPLETAS | 29 | R$ 58.382.701,56 | DB tem menos faturas que profiles.json (faturas históricas faltando) |
| NFS_SEM_PAGAMENTO | 29 | R$ 8.288.169,06 | NFs vinculadas sem registro de pagamento |
| SEM_FATURAS_JSON | 11 | R$ 2.817.587,51 | Pasta SPCF existe mas sem consolidado_faturas JSON |
| SEM_FATURAS_DB | 8 | R$ 2.286.025,53 | Faturas do profiles.json não estão no banco SQLite |
| SEM_CRUZAMENTO | 7 | R$ 1.859.621,78 | Tem faturas e PDFs mas sem match NF×PDF na tabela cruzamento |
| SEM_PENDRIVE | 7 | R$ 1.299.776,73 | Nenhum documento do pen drive classificado |
| SEM_DOSSIE | 6 | R$ 1.032.979,04 | Sem pasta *_DOSSIE em PRODAM_DOCS (sem inventário PDF) |
| SEM_SPCF_JSON | 3 | R$ 82.621,72 | Sem pasta em SPCF_EXTRACAO/por_devedor/ (scraping não cobriu) |
| SEM_EMPENHOS | 3 | R$ 47.860,93 | Devedor governamental sem Notas de Empenho no banco |

## Cobertura por Devedor (todos os 66)

| Devedor | Cat | Exigível | Fat DB | Fat Prof | Cadeia | NEs | Pendrive | Dossiê | Cruz. | Gaps |
|---------|-----|----------|--------|----------|--------|-----|----------|--------|-------|------|
| SEDUC | GOV | R$ 49.215.512,48 | 106 | 84 | 83C+23F | 286 | 112 | OK | 45 | 0 |
| DETRAN | GOV | R$ 31.684.739,01 | 113 | 233 | 99C+14F | 470 | 444 | OK | 175 | **1** |
| SES/SUSAM | GOV | R$ 14.748.048,96 | 110 | 324 | 105C+5F | 475 | 76 | OK | 42 | **1** |
| SSP | GOV | R$ 4.553.230,80 | 82 | 196 | 72C+10F | 218 | 785 | OK | 162 | 0 |
| SEJUSC | GOV | R$ 2.589.660,12 | 58 | 165 | 29C+27F+2M | 322 | 85 | OK | 21 | **1** |
| SEAD | GOV | R$ 2.339.702,20 | 56 | 69 | 29C+27F | 693 | 87 | OK | 51 | 0 |
| CETAM | GOV | R$ 1.256.564,28 | 0 | 16 | — | 276 | 26 | OK | 0 | **2** |
| SEDECTI | GOV | R$ 1.249.203,13 | 42 | 228 | 33C+9F | 524 | 133 | OK | 63 | **2** |
| POLÍCIA CIVIL | GOV | R$ 960.481,71 | 18 | 56 | 11C+7F | 158 | 62 | OK | 24 | **2** |
| BANCO MASTER | EMP | R$ 889.270,87 | 51 | 0 | 45C+3F+3M | 0 | 50 | OK | 0 | **2** |
| FENIXSOFT | EMP | R$ 888.250,00 | 7 | 0 | 4C+3F | 0 | 14 | OK | 14 | 0 |
| CAIXA | EMP | R$ 844.328,88 | 60 | 0 | 57C+3M | 0 | 59 | OK | 59 | **1** |
| SUHAB | GOV | R$ 840.061,15 | 13 | 123 | 12C+1F | 322 | 49 | OK | 11 | **1** |
| AMAZONPREV | GOV | R$ 736.219,79 | 5 | 23 | 5C | 174 | 53 | OK | 14 | **2** |
| FAAR/SEDEL | GOV | R$ 734.498,94 | 72 | 221 | 44C+28F | 155 | 100 | OK | 54 | **1** |
| PGE | GOV | R$ 680.239,77 | 46 | 47 | 29C+17F | 428 | 47 | OK | 17 | **1** |
| IPAAM | GOV | R$ 652.339,89 | 19 | 58 | 16C+3F | 235 | 83 | OK | 33 | **1** |
| SEAS | GOV | R$ 651.041,09 | 25 | 63 | 18C+7F | 415 | 44 | OK | 18 | **2** |
| FCECON | GOV | R$ 637.106,68 | 11 | 113 | 9C+2F | 386 | 65 | OK | 31 | **1** |
| PROVER | EMP | R$ 549.105,70 | 48 | 0 | 46C+2M | 0 | 46 | OK | 0 | **3** |
| SETRAB | GOV | R$ 505.961,79 | 0 | 81 | — | 176 | 0 | **FALTA** | 0 | **4** |
| SEINFRA | GOV | R$ 379.631,55 | 12 | 38 | 11C+1F | 395 | 36 | OK | 8 | **2** |
| UGPI | GOV | R$ 353.473,42 | 4 | 18 | 4C | 407 | 0 | **FALTA** | 0 | **3** |
| IDAM | GOV | R$ 328.735,51 | 7 | 35 | 6C+1F | 414 | 42 | OK | 12 | **1** |
| FVS | GOV | R$ 321.372,96 | 1 | 23 | 1C | 517 | 39 | OK | 24 | **1** |
| SEJEL | GOV | R$ 280.242,25 | 0 | 96 | — | 101 | 50 | OK | 0 | **2** |
| FMT | GOV | R$ 272.130,68 | 3 | 83 | 2C+1F | 480 | 49 | OK | 13 | **1** |
| FHAJ | GOV | R$ 259.910,78 | 6 | 75 | 2C+4F | 297 | 0 | OK | 44 | **3** |
| SECT | GOV | R$ 258.328,58 | 8 | 44 | 4C+4F | 198 | 45 | OK | 0 | **3** |
| ADS | GOV | R$ 211.657,47 | 6 | 119 | 6C | 256 | 48 | OK | 9 | **1** |
| SEFAZ | GOV | R$ 198.980,49 | 5 | 5 | 5C | 206 | 19 | OK | 6 | 0 |
| CPA | EMP | R$ 165.830,96 | 6 | 0 | 5C+1F | 0 | 10 | OK | 6 | **1** |
| ADAF | GOV | R$ 149.600,91 | 27 | 44 | 19C+8F | 275 | 58 | OK | 19 | **2** |
| AADESAM | GOV | R$ 125.682,90 | 0 | 34 | — | 4 | 0 | **FALTA** | 0 | **4** |
| IKM DE | EMP | R$ 116.263,60 | 12 | 0 | 5C+7F | 0 | 19 | OK | 0 | **2** |
| ANOREG | EMP | R$ 102.267,91 | 12 | 0 | 11C+1F | 0 | 18 | OK | 18 | 0 |
| SEC | GOV | R$ 99.050,71 | 7 | 23 | 4C+3F | 271 | 61 | OK | 39 | **1** |
| SEPROR | GOV | R$ 77.960,49 | 3 | 25 | 2C+1F | 298 | 33 | OK | 3 | **1** |
| BMC | EMP | R$ 58.142,00 | 6 | 0 | 5C+1M | 0 | 6 | OK | 6 | **1** |
| ARSEPAM | GOV | R$ 49.618,85 | 20 | 23 | 18C+2F | 166 | 65 | OK | 45 | **2** |
| FUAM/FUHAM | GOV | R$ 44.020,01 | 0 | 75 | — | 349 | 124 | OK | 5 | **2** |
| BANCO BMG | EMP | R$ 39.242,00 | 10 | 0 | 9C+1F | 0 | 10 | OK | 10 | **1** |
| SEMA | GOV | R$ 38.541,11 | 2 | 10 | 2C | 220 | 45 | OK | 4 | **2** |
| ITRANSITO | EMP | R$ 38.360,67 | 12 | 0 | 9C+3M | 0 | 10 | OK | 10 | 0 |
| ASSOC. DE GESTÃO INOVAÇÃO E RES. EM SAÚDE | EMP | R$ 34.760,79 | 6 | 0 | 3C+3M | 0 | 6 | OK | 0 | **3** |
| FUNTEA | GOV | R$ 34.186,19 | 3 | 11 | 1C+2F | 224 | 21 | OK | 7 | **2** |
| BANCO SICOOB | EMP | R$ 30.290,00 | 21 | 0 | 19C+2M | 0 | 19 | OK | 19 | **1** |
| DPE | GOV | R$ 28.060,05 | 1 | 7 | 1C | 79 | 16 | OK | 3 | **2** |
| FMPES | GOV | R$ 27.264,57 | 0 | 3 | — | 0 | 0 | **FALTA** | 0 | **5** |
| PMAM | GOV | R$ 27.020,90 | 2 | 13 | 1C+1F | 95 | 36 | OK | 8 | **1** |
| CGE | GOV | R$ 25.693,37 | 0 | 9 | — | 174 | 15 | OK | 0 | **2** |
| SNPH | GOV | R$ 25.117,34 | 13 | 8 | 12C+1F | 224 | 53 | OK | 18 | **1** |
| PSA TECHNOLOGY | EMP | R$ 21.007,21 | 0 | 0 | — | 0 | 1 | OK | 1 | **1** |
| FJJA | GOV | R$ 20.596,36 | 0 | 5 | — | 0 | 0 | **FALTA** | 0 | **5** |
| SUL AMERICA | EMP | R$ 18.196,00 | 20 | 0 | 18C+2M | 0 | 19 | OK | 19 | **1** |
| B23 TECNOLOGIA | EMP | R$ 11.892,24 | 3 | 0 | 3C | 0 | 3 | OK | 0 | **2** |
| BANCO SAFRA | EMP | R$ 9.310,00 | 6 | 0 | 5C+1M | 0 | 5 | OK | 5 | **2** |
| ODONTOMED | EMP | R$ 7.541,10 | 14 | 0 | 14C | 0 | 15 | OK | 15 | **1** |
| EASYTECH | EMP | R$ 6.927,16 | 10 | 0 | 8C+2F | 0 | 11 | OK | 9 | **1** |
| FHEMOAM | GOV | R$ 6.886,91 | 3 | 8 | 2C+1F | 44 | 0 | OK | 10 | **3** |
| CBMAM | GOV | R$ 3.134,03 | 2 | 24 | 2C | 150 | 39 | OK | 9 | **1** |
| SEMIG | GOV | R$ 0 | 30 | 0 | 22C+8F | 22 | 14 | OK | 3 | 0 |
| CASA CIVIL | GOV | R$ 0 | 4 | 0 | 1C+3F | 194 | 35 | OK | 0 | **1** |
| COSAMA | GOV | R$ 0 | 0 | 0 | — | 0 | 25 | OK | 0 | **2** |
| CASA MILITAR | GOV | R$ 0 | 0 | 0 | — | 28 | 2 | OK | 0 | **1** |
| BANCO DAYCOVAL | EMP | R$ 0 | 4 | 0 | 3F+1M | 0 | 0 | **FALTA** | 0 | **1** |

## Detalhamento — Devedores com Lacunas

### CRÍTICO

**CETAM** (R$ 1.256.564,28 exigível, GOV_INDIRETA)
- SEM_FATURAS_DB: profiles diz 16 faturas mas DB tem 0
  - **Ação**: Rodar web scraping SPCF para este devedor ou importar faturas do XLS

**SETRAB** (R$ 505.961,79 exigível, GOV_DIRETA)
- SEM_FATURAS_DB: profiles diz 81 faturas mas DB tem 0
  - **Ação**: Rodar web scraping SPCF para este devedor ou importar faturas do XLS

**SEJEL** (R$ 280.242,25 exigível, GOV_DIRETA)
- SEM_FATURAS_DB: profiles diz 96 faturas mas DB tem 0
  - **Ação**: Rodar web scraping SPCF para este devedor ou importar faturas do XLS

**AADESAM** (R$ 125.682,90 exigível, GOV_INDIRETA)
- SEM_FATURAS_DB: profiles diz 34 faturas mas DB tem 0
  - **Ação**: Rodar web scraping SPCF para este devedor ou importar faturas do XLS

**FUAM/FUHAM** (R$ 44.020,01 exigível, GOV_INDIRETA)
- SEM_FATURAS_DB: profiles diz 75 faturas mas DB tem 0
  - **Ação**: Rodar web scraping SPCF para este devedor ou importar faturas do XLS

**FMPES** (R$ 27.264,57 exigível, GOV_INDIRETA)
- SEM_FATURAS_DB: profiles diz 3 faturas mas DB tem 0
  - **Ação**: Rodar web scraping SPCF para este devedor ou importar faturas do XLS

**CGE** (R$ 25.693,37 exigível, GOV_DIRETA)
- SEM_FATURAS_DB: profiles diz 9 faturas mas DB tem 0
  - **Ação**: Rodar web scraping SPCF para este devedor ou importar faturas do XLS

**FJJA** (R$ 20.596,36 exigível, GOV_INDIRETA)
- SEM_FATURAS_DB: profiles diz 5 faturas mas DB tem 0
  - **Ação**: Rodar web scraping SPCF para este devedor ou importar faturas do XLS

### ALTO

**DETRAN** (R$ 31.684.739,01 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 113 vs 179 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**SES/SUSAM** (R$ 14.748.048,96 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 110 vs 144 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**SEJUSC** (R$ 2.589.660,12 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 58 vs 65 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**SEDECTI** (R$ 1.249.203,13 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 42 vs 52 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**POLÍCIA CIVIL** (R$ 960.481,71 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 18 vs 32 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**SUHAB** (R$ 840.061,15 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 13 vs 87 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**AMAZONPREV** (R$ 736.219,79 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 5 vs 21 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**FAAR/SEDEL** (R$ 734.498,94 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 72 vs 113 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**IPAAM** (R$ 652.339,89 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 19 vs 58 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**SEAS** (R$ 651.041,09 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 25 vs 63 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**FCECON** (R$ 637.106,68 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 11 vs 85 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**SETRAB** (R$ 505.961,79 exigível, GOV_DIRETA)
- SEM_DOSSIE: Sem pasta *_DOSSIE em PRODAM_DOCS
  - **Ação**: Criar pasta SETRAB_DOSSIE com INVENTARIO.xlsx

**SEINFRA** (R$ 379.631,55 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 12 vs 38 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**UGPI** (R$ 353.473,42 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 4 vs 18 exigíveis no profiles
- SEM_DOSSIE: Sem pasta *_DOSSIE em PRODAM_DOCS
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano
  - **Ação**: Criar pasta UGPI_DOSSIE com INVENTARIO.xlsx

**IDAM** (R$ 328.735,51 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 7 vs 30 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**FVS** (R$ 321.372,96 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 1 vs 23 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**FMT** (R$ 272.130,68 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 3 vs 41 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**FHAJ** (R$ 259.910,78 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 6 vs 34 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**SECT** (R$ 258.328,58 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 8 vs 35 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**ADS** (R$ 211.657,47 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 6 vs 119 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**ADAF** (R$ 149.600,91 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 27 vs 44 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**AADESAM** (R$ 125.682,90 exigível, GOV_INDIRETA)
- SEM_DOSSIE: Sem pasta *_DOSSIE em PRODAM_DOCS
  - **Ação**: Criar pasta AADESAM_DOSSIE com INVENTARIO.xlsx

**SEC** (R$ 99.050,71 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 7 vs 11 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**SEPROR** (R$ 77.960,49 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 3 vs 15 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**ARSEPAM** (R$ 49.618,85 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 20 vs 23 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**SEMA** (R$ 38.541,11 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 2 vs 5 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**FUNTEA** (R$ 34.186,19 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 3 vs 11 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**DPE** (R$ 28.060,05 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 1 vs 7 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**FMPES** (R$ 27.264,57 exigível, GOV_INDIRETA)
- SEM_EMPENHOS: Devedor governo sem NEs no banco
- SEM_DOSSIE: Sem pasta *_DOSSIE em PRODAM_DOCS
  - **Ação**: Verificar se devedor tem empenhos no SPCF (pode ser nome diferente)
  - **Ação**: Criar pasta FMPES_DOSSIE com INVENTARIO.xlsx

**PMAM** (R$ 27.020,90 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 2 vs 8 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**FJJA** (R$ 20.596,36 exigível, GOV_INDIRETA)
- SEM_EMPENHOS: Devedor governo sem NEs no banco
- SEM_DOSSIE: Sem pasta *_DOSSIE em PRODAM_DOCS
  - **Ação**: Verificar se devedor tem empenhos no SPCF (pode ser nome diferente)
  - **Ação**: Criar pasta FJJA_DOSSIE com INVENTARIO.xlsx

**FHEMOAM** (R$ 6.886,91 exigível, GOV_INDIRETA)
- FATURAS_INCOMPLETAS: DB tem 3 vs 7 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**CBMAM** (R$ 3.134,03 exigível, GOV_DIRETA)
- FATURAS_INCOMPLETAS: DB tem 2 vs 4 exigíveis no profiles
  - **Ação**: Reconciliar faturas do profiles com rel_geral_faturas por ano

**COSAMA** (R$ 0 exigível, GOV_INDIRETA)
- SEM_EMPENHOS: Devedor governo sem NEs no banco
  - **Ação**: Verificar se devedor tem empenhos no SPCF (pode ser nome diferente)

**BANCO DAYCOVAL** (R$ 0 exigível, EMPRESA_PRIVADA)
- SEM_DOSSIE: Sem pasta *_DOSSIE em PRODAM_DOCS
  - **Ação**: Criar pasta BANCO DAYCOVAL_DOSSIE com INVENTARIO.xlsx

### MÉDIO

**CETAM** (R$ 1.256.564,28 exigível, GOV_INDIRETA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas

**BANCO MASTER** (R$ 889.270,87 exigível, EMPRESA_PRIVADA)
- SEM_CRUZAMENTO: Tem faturas e PDFs mas sem cruzamento NF×PDF

**PROVER** (R$ 549.105,70 exigível, EMPRESA_PRIVADA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas
- SEM_CRUZAMENTO: Tem faturas e PDFs mas sem cruzamento NF×PDF

**SETRAB** (R$ 505.961,79 exigível, GOV_DIRETA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas
- SEM_PENDRIVE: Nenhum doc do pen drive para este devedor
  - **Ação**: Verificar se há PDFs deste devedor no pendrive com nome diferente

**UGPI** (R$ 353.473,42 exigível, GOV_DIRETA)
- SEM_PENDRIVE: Nenhum doc do pen drive para este devedor
  - **Ação**: Verificar se há PDFs deste devedor no pendrive com nome diferente

**SEJEL** (R$ 280.242,25 exigível, GOV_DIRETA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas

**FHAJ** (R$ 259.910,78 exigível, GOV_INDIRETA)
- SEM_PENDRIVE: Nenhum doc do pen drive para este devedor
  - **Ação**: Verificar se há PDFs deste devedor no pendrive com nome diferente

**SECT** (R$ 258.328,58 exigível, GOV_DIRETA)
- SEM_CRUZAMENTO: Tem faturas e PDFs mas sem cruzamento NF×PDF

**AADESAM** (R$ 125.682,90 exigível, GOV_INDIRETA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas
- SEM_PENDRIVE: Nenhum doc do pen drive para este devedor
  - **Ação**: Verificar se há PDFs deste devedor no pendrive com nome diferente

**IKM DE** (R$ 116.263,60 exigível, EMPRESA_PRIVADA)
- SEM_CRUZAMENTO: Tem faturas e PDFs mas sem cruzamento NF×PDF

**FUAM/FUHAM** (R$ 44.020,01 exigível, GOV_INDIRETA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas

**ASSOC. DE GESTÃO INOVAÇÃO E RES. EM SAÚDE** (R$ 34.760,79 exigível, EMPRESA_PRIVADA)
- SEM_SPCF_JSON: Sem pasta em SPCF_EXTRACAO/por_devedor/
- SEM_CRUZAMENTO: Tem faturas e PDFs mas sem cruzamento NF×PDF
  - **Ação**: Rodar scraper SPCF para este devedor

**FMPES** (R$ 27.264,57 exigível, GOV_INDIRETA)
- SEM_SPCF_JSON: Sem pasta em SPCF_EXTRACAO/por_devedor/
- SEM_PENDRIVE: Nenhum doc do pen drive para este devedor
  - **Ação**: Rodar scraper SPCF para este devedor
  - **Ação**: Verificar se há PDFs deste devedor no pendrive com nome diferente

**CGE** (R$ 25.693,37 exigível, GOV_DIRETA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas

**PSA TECHNOLOGY** (R$ 21.007,21 exigível, EMPRESA_PRIVADA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas

**FJJA** (R$ 20.596,36 exigível, GOV_INDIRETA)
- SEM_SPCF_JSON: Sem pasta em SPCF_EXTRACAO/por_devedor/
- SEM_PENDRIVE: Nenhum doc do pen drive para este devedor
  - **Ação**: Rodar scraper SPCF para este devedor
  - **Ação**: Verificar se há PDFs deste devedor no pendrive com nome diferente

**B23 TECNOLOGIA** (R$ 11.892,24 exigível, EMPRESA_PRIVADA)
- SEM_CRUZAMENTO: Tem faturas e PDFs mas sem cruzamento NF×PDF

**BANCO SAFRA** (R$ 9.310,00 exigível, EMPRESA_PRIVADA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas

**FHEMOAM** (R$ 6.886,91 exigível, GOV_INDIRETA)
- SEM_PENDRIVE: Nenhum doc do pen drive para este devedor
  - **Ação**: Verificar se há PDFs deste devedor no pendrive com nome diferente

**CASA CIVIL** (R$ 0 exigível, GOV_DIRETA)
- SEM_CRUZAMENTO: Tem faturas e PDFs mas sem cruzamento NF×PDF

**COSAMA** (R$ 0 exigível, GOV_INDIRETA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas

**CASA MILITAR** (R$ 0 exigível, GOV_DIRETA)
- SEM_FATURAS_JSON: Pasta SPCF existe mas sem consolidado_faturas

## Documentação Faltante por Formato

| Formato | Onde buscar | Devedores afetados | Prioridade |
|---------|-----------|-------------------|------------|
| Faturas SPCF (JSON/CSV) | SPCF web scraping → consolidado_faturas | 8 sem nenhuma, 29 incompletas | ALTA |
| Notas de Empenho (NE) | SPCF/empenhos ou PDFs pendrive | 3 gov sem NEs | ALTA |
| PDFs (contratos, NEs, NLs, NFs) | Pen drive original | 7 sem nenhum doc | MÉDIA |
| Dossiê + INVENTARIO.xlsx | Gerar via pipeline/analise_massiva | 6 sem dossiê | MÉDIA |
| Cruzamento NF×PDF | Rodar reconciliacao_spcf.py | 7 sem cruzamento | BAIXA |

## Divergências entre Fontes

As principais divergências detectadas entre profiles.json e prodam.db:

| Devedor | Fat profiles | Fat DB | Diff | Val profiles (exig) | Val DB (bruto) |
|---------|-------------|--------|------|--------------------|--------------------|
| SES/SUSAM | 324 | 110 | +214 | R$ 14.748.048,96 | R$ 6.752.368,26 |
| SEDECTI | 228 | 42 | +186 | R$ 1.249.203,13 | R$ 1.319.548,29 |
| FAAR/SEDEL | 221 | 72 | +149 | R$ 734.498,94 | R$ 364.632,44 |
| DETRAN | 233 | 113 | +120 | R$ 31.684.739,01 | R$ 17.802.420,55 |
| SSP | 196 | 82 | +114 | R$ 4.553.230,80 | R$ 6.290.728,66 |
| ADS | 119 | 6 | +113 | R$ 211.657,47 | R$ 10.230,60 |
| SUHAB | 123 | 13 | +110 | R$ 840.061,15 | R$ 364.460,14 |
| SEJUSC | 165 | 58 | +107 | R$ 2.589.660,12 | R$ 2.434.441,61 |
| FCECON | 113 | 11 | +102 | R$ 637.106,68 | R$ 68.362,95 |
| FMT | 83 | 3 | +80 | R$ 272.130,68 | R$ 23.228,19 |
| FHAJ | 75 | 6 | +69 | R$ 259.910,78 | R$ 28.541,60 |
| IPAAM | 58 | 19 | +39 | R$ 652.339,89 | R$ 233.596,95 |
| POLÍCIA CIVIL | 56 | 18 | +38 | R$ 960.481,71 | R$ 625.567,97 |
| SEAS | 63 | 25 | +38 | R$ 651.041,09 | R$ 219.783,61 |
| SECT | 44 | 8 | +36 | R$ 258.328,58 | R$ 38.747,15 |

**Causa raiz**: profiles.json consolida faturas de SPCF + PDFs + planilhas históricas. 
O prodam.db contém apenas faturas do SPCF web scraping (abertas atuais).
Faturas históricas (pagas, canceladas, pré-2019) existem em profiles mas não no banco.