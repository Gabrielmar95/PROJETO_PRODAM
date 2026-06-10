# Classificacao + Renomeacao por CONTEUDO — 20260423_115328

**Input:** `C:\Users\gabri\Desktop\PROJETO_PRODAM\_OUT_inventario_detran_externo_20260423_110633\universo.csv`
**PDFs processados:** 2473
**OK:** 2473 | **Erros:** 0
**Tempo:** 30.0 min
**Confianca >= 0.7:** 1801 (72.8%)

## Distribuicao por tipo final
| Tipo | Qtd |
|---|---:|
| NE | 1044 |
| Indefinido | 611 |
| NF | 244 |
| Fatura | 224 |
| Contrato-Base | 129 |
| Certidao | 116 |
| Cobranca | 80 |
| Aceite | 21 |
| Proposta | 2 |
| Oficio-DIRAF | 2 |

## Flags
- Fora de escopo (sem contrato identificado): **2344**
- Com texto util extraido: 2170

## Proximos passos
1. Revisar `renomear_proposto_conteudo.csv`
2. Se OK: invocar `renomeador-pdfs-prodam --apply` com flag in-place
3. O SHA-256 de cada PDF ja esta no CSV → use como ancora de rollback
