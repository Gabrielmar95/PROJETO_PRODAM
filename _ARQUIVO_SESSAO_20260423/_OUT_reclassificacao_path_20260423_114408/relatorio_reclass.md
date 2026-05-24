# Reclassificacao por PATH — PDFs DETRAN externos

**Data:** 2026-04-23T11:44:08
**Input:** C:\Users\gabri\Desktop\PROJETO_PRODAM\_OUT_inventario_detran_externo_20260423_110633\classificados.csv
**PDFs reclassificados:** 2473
**Propostas de renomeacao:** 2473
**PDFs sem texto incluidos:** 303

## Comparacao: tipo_original vs tipo_reclass

### Tipos originais (classificador generico)
| Tipo | Qtd |
|---|---:|
| CONTRATO | 1379 |
| TA | 492 |
| SEM_TEXTO | 303 |
| NE | 174 |
| NF | 64 |
| OUTRO | 45 |
| CERTIDAO | 16 |

### Tipos reclass (PATH-based)
| Tipo | Qtd |
|---|---:|
| NE | 883 |
| SPCF_HTML | 469 |
| SPCF_OFICIAL | 254 |
| SPCF_CONVERTIDO | 245 |
| FATURA | 226 |
| NF | 129 |
| TA | 100 |
| COBRANCA | 80 |
| CERTIDAO | 36 |
| CONTRATO | 28 |
| ACEITE | 21 |
| RELATORIO | 2 |

## Matriz de mudancas (top 20)
| Original -> Reclass | Qtd |
|---|---:|
| CONTRATO -> NE | 401 |
| CONTRATO -> SPCF_HTML | 337 |
| CONTRATO -> FATURA | 226 |
| TA -> NE | 202 |
| CONTRATO -> SPCF_CONVERTIDO | 152 |
| SEM_TEXTO -> NE | 137 |
| TA -> SPCF_HTML | 132 |
| CONTRATO -> SPCF_OFICIAL | 117 |
| TA -> SPCF_CONVERTIDO | 93 |
| SEM_TEXTO -> SPCF_OFICIAL | 88 |
| CONTRATO -> COBRANCA | 63 |
| CONTRATO -> NF | 55 |
| SEM_TEXTO -> TA | 43 |
| NE -> SPCF_OFICIAL | 32 |
| TA -> SPCF_OFICIAL | 16 |
| OUTRO -> COBRANCA | 15 |
| SEM_TEXTO -> CERTIDAO | 12 |
| CONTRATO -> ACEITE | 11 |
| SEM_TEXTO -> CONTRATO | 11 |
| OUTRO -> TA | 8 |

## Proximos passos
1. Revisar `renomear_proposto_reclass.csv`
2. Se OK: rodar aplicador de renomeacao (renomeador-pdfs-prodam em modo --apply)
3. Preservar log de mapeamento SHA-256 antes de aplicar in-place
