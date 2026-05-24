# Classificacao + Renomeacao por CONTEUDO — 20260423_133722

**Input:** `C:\Users\gabri\Desktop\PROJETO_PRODAM\_OUT_inventario_detran_externo_20260423_110633\universo.csv`
**PDFs processados:** 2473
**OK:** 2473 | **Erros:** 0
**Tempo:** 22.2 min
**Confianca >= 0.7:** 1893 (76.5%)

## Distribuicao por tipo final
| Tipo | Qtd |
|---|---:|
| NE | 1129 |
| Indefinido | 525 |
| NF | 244 |
| Fatura | 224 |
| Contrato-Base | 129 |
| Certidao | 117 |
| Cobranca | 80 |
| Aceite | 21 |
| Proposta | 2 |
| Oficio-DIRAF | 2 |

## Flags
- Fora de escopo (sem contrato identificado): **1683**
- Com texto util extraido: 2471

## Proximos passos
1. Revisar `renomear_proposto_conteudo.csv`
2. Se OK: invocar `renomeador-pdfs-prodam --apply` com flag in-place
3. O SHA-256 de cada PDF ja esta no CSV → use como ancora de rollback
