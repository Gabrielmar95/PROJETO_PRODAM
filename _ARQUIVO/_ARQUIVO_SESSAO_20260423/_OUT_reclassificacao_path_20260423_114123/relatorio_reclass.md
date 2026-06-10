# Reclassificacao por PATH — PDFs DETRAN externos

**Data:** 2026-04-23T11:41:23
**Input:** C:\Users\gabri\Desktop\PROJETO_PRODAM\_OUT_inventario_detran_externo_20260423_110633\classificados.csv
**PDFs reclassificados:** 2473
**Propostas de renomeacao:** 780
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
| INDETERMINADO | 1693 |
| NE | 388 |
| NF | 129 |
| TA | 100 |
| COBRANCA | 80 |
| CERTIDAO | 36 |
| CONTRATO | 24 |
| ACEITE | 21 |
| RELATORIO | 2 |

## Matriz de mudancas (top 20)
| Original -> Reclass | Qtd |
|---|---:|
| CONTRATO -> INDETERMINADO | 1101 |
| TA -> INDETERMINADO | 350 |
| SEM_TEXTO -> INDETERMINADO | 176 |
| CONTRATO -> NE | 136 |
| TA -> NE | 93 |
| NE -> INDETERMINADO | 64 |
| CONTRATO -> COBRANCA | 63 |
| CONTRATO -> NF | 55 |
| SEM_TEXTO -> NE | 49 |
| SEM_TEXTO -> TA | 43 |
| OUTRO -> COBRANCA | 15 |
| SEM_TEXTO -> CERTIDAO | 12 |
| CONTRATO -> ACEITE | 11 |
| SEM_TEXTO -> CONTRATO | 11 |
| OUTRO -> TA | 8 |
| OUTRO -> CERTIDAO | 8 |
| SEM_TEXTO -> NF | 8 |
| OUTRO -> ACEITE | 6 |
| OUTRO -> NF | 4 |
| SEM_TEXTO -> ACEITE | 4 |

## Proximos passos
1. Revisar `renomear_proposto_reclass.csv`
2. Se OK: rodar aplicador de renomeacao (renomeador-pdfs-prodam em modo --apply)
3. Preservar log de mapeamento SHA-256 antes de aplicar in-place
