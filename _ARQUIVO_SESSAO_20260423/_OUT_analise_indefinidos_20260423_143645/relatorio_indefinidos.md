# Analise dos 525 Indefinidos — 20260423_143645

**Input:** `C:\Users\gabri\Desktop\PROJETO_PRODAM\_OUT_rename_inplace_20260423_141648\log_renomeacao.csv`

## Distribuicao por categoria de tamanho de texto

| Categoria | Qtd | O que provavelmente e |
|---|---:|---|
| VAZIO (<100 chars) | 2 | Menu SPCF 1 pagina ou PDF imagem sem OCR util |
| CURTO_MENU_OU_CABECALHO (100-999) | 0 | Cabecalho SPCF / pagina unica de sistema |
| MEDIO_COM_CONTEUDO (1000-4999) | 523 | Documento curto — pode ser empenho/recibo nao classificado |
| GRANDE_DOCUMENTO (>=5000) | 0 | Documento substancial — **possivelmente valioso, regex falhou** |

## Por raiz
| Raiz | Qtd |
|---|---:|
| SPCF_EXTRACAO | 523 |
| PRODAM_DOCS | 1 |
| DETRAN_CONSOLIDADO | 1 |

## Cruzamento raiz × tamanho

### SPCF_EXTRACAO
| Categoria | Qtd |
|---|---:|
| MEDIO_COM_CONTEUDO | 521 |
| VAZIO | 2 |

### PRODAM_DOCS
| Categoria | Qtd |
|---|---:|
| MEDIO_COM_CONTEUDO | 1 |

### DETRAN_CONSOLIDADO
| Categoria | Qtd |
|---|---:|
| MEDIO_COM_CONTEUDO | 1 |

## Amostras por categoria (5 cada)

### GRANDE_DOCUMENTO

### MEDIO_COM_CONTEUDO
- **INDEFINIDO_empenho_DETRAN_view_10000.pdf**
  - Original: `empenho_DETRAN_view_10000.pdf`
  - Raiz: SPCF_EXTRACAO | Pgs: 2 | Chars: 2075
  - Amostra: `SPCF Sair Gabriel Mar Da Silva Sistemas Cobranca Propostas GestÃ£o de Propostas Contratos e ConvÃªnios GestÃ£o de Contratos GestÃ£o dos Empenhos Fatur`

- **INDEFINIDO_empenho_DETRAN_view_10012.pdf**
  - Original: `empenho_DETRAN_view_10012.pdf`
  - Raiz: SPCF_EXTRACAO | Pgs: 2 | Chars: 2027
  - Amostra: `SPCF Sair Gabriel Mar Da Silva Sistemas Cobranca Propostas GestÃ£o de Propostas Contratos e ConvÃªnios GestÃ£o de Contratos GestÃ£o dos Empenhos Fatur`

- **INDEFINIDO_empenho_DETRAN_view_10001.pdf**
  - Original: `empenho_DETRAN_view_10001.pdf`
  - Raiz: SPCF_EXTRACAO | Pgs: 2 | Chars: 2015
  - Amostra: `SPCF Sair Gabriel Mar Da Silva Sistemas Cobranca Propostas GestÃ£o de Propostas Contratos e ConvÃªnios GestÃ£o de Contratos GestÃ£o dos Empenhos Fatur`

- **INDEFINIDO_empenho_DETRAN_view_10009.pdf**
  - Original: `empenho_DETRAN_view_10009.pdf`
  - Raiz: SPCF_EXTRACAO | Pgs: 2 | Chars: 2070
  - Amostra: `SPCF Sair Gabriel Mar Da Silva Sistemas Cobranca Propostas GestÃ£o de Propostas Contratos e ConvÃªnios GestÃ£o de Contratos GestÃ£o dos Empenhos Fatur`

- **INDEFINIDO_empenho_DETRAN_view_10014.pdf**
  - Original: `empenho_DETRAN_view_10014.pdf`
  - Raiz: SPCF_EXTRACAO | Pgs: 2 | Chars: 2078
  - Amostra: `SPCF Sair Gabriel Mar Da Silva Sistemas Cobranca Propostas GestÃ£o de Propostas Contratos e ConvÃªnios GestÃ£o de Contratos GestÃ£o dos Empenhos Fatur`


### CURTO_MENU_OU_CABECALHO

### VAZIO
- **INDEFINIDO_empenho_DETRAN_1244.pdf**
  - Original: `empenho_DETRAN_1244.pdf`
  - Raiz: SPCF_EXTRACAO | Pgs: 2 | Chars: 0

- **INDEFINIDO_empenho_DETRAN_13098.pdf**
  - Original: `empenho_DETRAN_13098.pdf`
  - Raiz: SPCF_EXTRACAO | Pgs: 0 | Chars: 0

## Sugestoes de acao

1. **VAZIO e CURTO**: descartaveis ou merecem OCR agressivo (cascata estagio 3). Total: 2
2. **MEDIO e GRANDE**: potencialmente documentos valiosos que escaparam dos regex. Total: 523
   - Vale abrir amostra manual dos maiores (>5000 chars) pra ver se sao: empenhos em formato novo, notificacoes, ofícios internos, etc
   - Pode valer estender os regex de `parse_tipo_doc` da skill `renomeador-pdfs-prodam`
