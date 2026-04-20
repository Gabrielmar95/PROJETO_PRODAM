# DOSSIE CONSOLIDADO - DETRAN/AM
_Gerado em 2026-04-15 | fonte: prodam.db + DETRAN_AUDITORIA_COMPLETA_

## 1. IDENTIFICACAO

- **Devedor:** DETRAN/AM
- **CNPJ:** 04.224.028/0001-63
- **Ranking portfolio:** #1
- **Score composto:** 0.9318 (A+)
- **Regime execucao:** `penhora_direta` (Tema 253/STF)
- **Blindagem pre-execucao:** 22/22 VALIDADOS

## 2. NUMEROS-CHAVE

| Metrica | prodam.db | DASHBOARD_DATA.json |
|---|---:|---:|
| Contratos | 13 | 13 |
| Empenhos (NEs) | 470 | 193 |
| Valor empenhos | R$ 250.316.057,30 | R$ 189.121.079,40 |
| Faturas | 149 | 149 |
| Valor faturas (bruto) | R$ 22.448.434,53 | R$ 22.448.434,53 |
| Valor atualizado | - | R$ 29.536.206,43 |
| Fator correcao medio | - | 1.3157x |

## 3. PRESCRICAO (distribuicao)

| Status | Qtde |
|---|---:|
| PRESCRITA | 24 |
| ATENCAO_12m | 6 |
| VIGENTE | 119 |

## 4. CADEIA DOCUMENTAL 5 ELOS (prodam.db)

| Completude | Faturas | Valor bruto |
|---|---:|---:|
| COMPLETA | 99 | R$ 16.019.101,26 |
| FORTE | 50 | R$ 6.429.333,27 |

## 5. CONTRATOS (13 ativos/historicos)

| N | Numero | PDF | Indice (dashboard) |
|---:|---|:-:|---|
| 1 | 004/2016 | - | IGPM |
| 2 | 006/2021 | - | IGPM |
| 3 | 010/2021 | - | IGPM |
| 4 | 012/2021 | - | IPCA |
| 5 | 017/2015 | - | IGPM |
| 6 | 022/2014 | - | IGPM |
| 7 | 025/2014 | - | IGPM |
| 8 | 027/2014 | - | IGPM |
| 9 | 060/2022 | - | INDETERMINADO |
| 10 | 071/2022 | - | INDETERMINADO |
| 11 | 075/2022 | - | IPCA |
| 12 | 083/2022 | - | IPCA |
| 13 | 3/2026 | OK | - |

## 6. FATURAS POR CONTRATO (top 10)

| Contrato | Faturas | Valor bruto |
|---|---:|---:|
| 10/2021 | 27 | R$ 10.855.971,05 |
| 296/2025 | 4 | R$ 2.522.329,40 |
| 3/2026 | 3 | R$ 1.891.747,05 |
| 22/2014 | 9 | R$ 1.578.124,94 |
| 4/2016 | 5 | R$ 1.527.017,45 |
| 6/2021 | 58 | R$ 1.420.555,08 |
| 12/2021 | 9 | R$ 707.848,01 |
| 75/2022 | 2 | R$ 567.872,80 |
| 71/2022 | 2 | R$ 520.000,00 |
| 17/2015 | 4 | R$ 335.879,03 |

## 7. ALERTAS DE PRESCRICAO

- Criticas (<90 dias): **0**
- Atencao (<12 meses): **6**

### Top-6 em ATENCAO 12m

| ID | NF | Contrato | Vencimento | Dias | Bruto | Atualizado |
|---|---|---|---|---:|---:|---:|
| 128770 | 25586 | 006/2021 | 2021-12-01 | 231 | R$ 26.634,00 | R$ 44.922,69 |
| 129515 | 26309 | 010/2021 | 2021-12-31 | 261 | R$ 371.260,32 | R$ 622.028,18 |
| 129613 | 26401 | 006/2021 | 2021-12-31 | 261 | R$ 26.634,00 | R$ 44.623,94 |
| 129612 | 26402 | 006/2021 | 2021-12-31 | 261 | R$ 39.951,00 | R$ 66.935,91 |
| 130540 | 27118 | 004/2016 | 2022-03-03 | 323 | R$ 305.403,49 | R$ 491.737,44 |
| 131182 | 27929 | 004/2016 | 2022-03-31 | 351 | R$ 305.403,49 | R$ 479.723,39 |

## 8. INVENTARIO DA PASTA `DETRAN_AUDITORIA_COMPLETA\`

| Subpasta | Arquivos | Formatos (top) |
|---|---:|---|
| 00_VISAO_GERAL | 6 | html:3, md:2, json:1 |
| 01_CONTRATOS | 283 | json:144, pdf:88, csv:44, html:4, md:3 |
| 02_NOTAS_EMPENHO | 3167 | pdf:1524, json:860, html:760, csv:21, md:2 |
| 03_NOTAS_LIQUIDACAO | 45 | csv:26, json:14, md:5 |
| 04_FATURAS | 1880 | pdf:753, csv:436, json:348, html:287, xls:53 |
| 05_ACEITES_TECNICOS | 36 | json:17, pdf:17, md:2 |
| 06_COBRANCAS_OFICIOS | 300 | pdf:154, json:96, docx:13, txt:13, csv:12 |
| 07_CERTIDOES | 50 | json:24, pdf:24, md:2 |
| 08_DADOS_SPCF | 1542 | pdf:662, json:369, csv:276, txt:185, xls:30 |
| 09_RELATORIOS_AUDITORIAS | 1712 | json:590, pdf:409, html:373, md:202, csv:75 |
| 10_SCRIPTS_PYTHON | 10 | py:10 |
| 11_PROFILES_BACKUPS | 3 | json:3 |
| 12_TEMPLATE_DOSSIE_DETRAN-AM | 21 | md:21 |

## 9. BASES DE DADOS DE APOIO

- `prodam.db` (raiz PROJETO_PRODAM) - SSOT tabular (8 tabelas, 80k+ registros)
- `DASHBOARD_DATA.json` (DETRAN_AUDITORIA_COMPLETA) - camada curada p/ dashboard v7.0
- `01_CONTRATOS/JSON/*.json` - contratos por numero + TAs (LLM-ready)
- `04_FATURAS/JSON/*.json` - 149 faturas estruturadas
- `02_NOTAS_EMPENHO/JSON/*.json` - 470 NEs estruturadas

## 10. PROXIMOS PASSOS SUGERIDOS

1. **Distribuir execucao F5** (petition pronta) - regime penhora direta
2. **Atualizar IGPM BCB real** - re-rodar skill `atualizacao-monetaria-sob-demanda`
3. **Assinar TRD faltante** - unico gap critico da blindagem (nota 75/100)
4. **Monitorar 53 faturas em ATENCAO** - primeira prescricao 2026-10-27

---
_Dossie gerado por `scripts/detran/gerar_dossie_detran_v2.py`_