# Inventario + Classificacao — PDFs DETRAN externos

**Data:** 2026-04-23T11:19:18
**Raizes:**
- `C:\Users\gabri\Desktop\PROJETO_PRODAM\SPCF_EXTRACAO`
- `C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\DETRAN_CONSOLIDADO`
- `C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\DETRAN`

## Universo
- PDFs totais: **2473**
- Tamanho: **1753 MB**
- Com texto embutido: **2170**
- Sem texto (candidatos a OCR): **303**
- Com nome suspeito: **51**

## Distribuicao por raiz
| Raiz | PDFs | Sem texto | Suspeitos |
|---|---:|---:|---:|
| SPCF_EXTRACAO | 1921 | 176 | 0 |
| DETRAN_CONSOLIDADO | 551 | 127 | 51 |
| DETRAN | 1 | 0 | 0 |

## Classificacao de conteudo
- PDFs classificados (com texto): **2170**

| Tipo | Qtd |
|---|---:|
| CONTRATO | 1379 |
| TA | 492 |
| NE | 174 |
| NF | 64 |
| OUTRO | 45 |
| CERTIDAO | 16 |

## Propostas de renomeacao (dry-run)
- Propostas geradas (conf >= 0.3, nome diferente): **2135**
- Arquivo: `renomear_proposto.csv`
- Nada foi renomeado. Gabriel revisa antes de Fase 3.

## Proximos passos
1. Rodar OCR em **303 PDFs sem texto** via ocr_lote_sem_texto_externo.py
2. Revisar `renomear_proposto.csv` (2135 itens)
3. Aplicar renomeacao in-place na Fase 3
