# Reconciliação SSOT × Pastas — Diagnóstico

_Gerado em 2026-04-22T03:48:25_

## Visão geral

- **SSOT (profiles.json):** 70 siglas
- **Pastas `_CONSOLIDADO`:** 78
- **Pastas `_DOSSIE`:** 82
- **Tabela `devedores` (prodam.db):** 81
- **Total de divergências detectadas:** 57

### Distribuição por causa raiz

- **A_COMPOSITE_SPLIT**: 7
- **C_SSOT_SEM_PASTA**: 12
- **D_PASTA_ORFA_CONS**: 18
- **D_PASTA_ORFA_DOS**: 20

### Distribuição por severidade

- **ALTA**: 36
- **BAIXA**: 1
- **MEDIA**: 20

## Interpretação (linguagem simples)

Imagine que `profiles.json` é o registro civil do projeto: ele diz quem existe oficialmente. As pastas `_CONSOLIDADO`/`_DOSSIE` são os 'cartórios' onde os documentos ficam guardados.

Quando o registro civil e o cartório não batem, podem acontecer 4 coisas:

1. **Nome composto dividido (A)**: o registro diz `FAAR/SEDEL`, mas existem duas pastas `FAAR` e `SEDEL` separadas. Como se uma certidão de casamento tivesse virado duas certidões de solteiro.
2. **Abreviação diferente (B)**: o registro diz `SES/SUSAM`, mas a pasta se chama só `SES`. Mesma pessoa, nomes diferentes.
3. **Existe no registro mas sem cartório (C)**: sigla aparece no `profiles.json` mas não tem pasta. Pode ser devedor novo sem documentação ainda, ou sigla fantasma que precisa ser removida.
4. **Cartório sem registro (D)**: existe pasta mas nenhuma sigla aponta para ela. Perigoso: dados ali são invisíveis para qualquer script automatizado.

## Detalhe — A_COMPOSITE_SPLIT

| SSOT | Pasta(s) afetada(s) | Severidade | Ação recomendada |
|------|---------------------|------------|------------------|
| `SES/SUSAM` | SES | ALTA | Consolidar pastas [SES] em única canonical 'SESSUSAM' (ou manter como filhas e fazer profiles.json apontar para múltiplas) |
| `FUAM/FUHAM` | FUAM, FUHAM | ALTA | Consolidar pastas [FUAM, FUHAM] em única canonical 'FUAMFUHAM' (ou manter como filhas e fazer profiles.json apontar para múltiplas) |
| `FAAR/SEDEL` | SEDEL, FAAR | ALTA | Consolidar pastas [FAAR, SEDEL] em única canonical 'FAARSEDEL' (ou manter como filhas e fazer profiles.json apontar para múltiplas) |
| `BANCO MASTER` | MASTER | ALTA | Consolidar pastas [MASTER] em única canonical 'BANCOMASTER' (ou manter como filhas e fazer profiles.json apontar para múltiplas) |
| `IKM DE` | IKM | ALTA | Consolidar pastas [IKM] em única canonical 'IKMDE' (ou manter como filhas e fazer profiles.json apontar para múltiplas) |
| `B23 TECNOLOGIA` | B23 | ALTA | Consolidar pastas [B23] em única canonical 'B23TECNOLOGIA' (ou manter como filhas e fazer profiles.json apontar para múltiplas) |
| `PSA TECHNOLOGY` | PSA | ALTA | Consolidar pastas [PSA] em única canonical 'PSATECHNOLOGY' (ou manter como filhas e fazer profiles.json apontar para múltiplas) |

## Detalhe — C_SSOT_SEM_PASTA

| SSOT | Pasta(s) afetada(s) | Severidade | Ação recomendada |
|------|---------------------|------------|------------------|
| `ASSOC. DE GESTÃO INOVAÇÃO E RES. EM SAÚDE` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `_metadata` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `UGPI` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `FMPES` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `SEJEL` | — | BAIXA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `SETRAB` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `AADESAM` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `FJJA` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `BANCO DAYCOVAL` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `BRADESCO` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `SALUX` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |
| `BRADESCO FINANCIAMENTO` | — | ALTA | Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json |

## Detalhe — D_PASTA_ORFA_CONS

| SSOT | Pasta(s) afetada(s) | Severidade | Ação recomendada |
|------|---------------------|------------|------------------|
| `—` | ALEAM_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'ALEAM' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | AMAZONASTUR_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'AMAZONASTUR' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | ASSOC_SAUDE_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'ASSOC_SAUDE' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | CIAMA_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'CIAMA' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | DEFESA_CIVIL_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'DEFESA_CIVIL' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | FAPEAM_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'FAPEAM' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | FEPIAM_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'FEPIAM' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | IMPRENSA_OFICIAL_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'IMPRENSA_OFICIAL' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | JUCEA_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'JUCEA' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | PGJ_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'PGJ' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | PROCON_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'PROCON' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | SECOM_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'SECOM' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | SEDURB_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'SEDURB' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | SEPA_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'SEPA' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | SUBCOMADEC_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'SUBCOMADEC' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | TCE_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'TCE' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | UEA_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'UEA' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |
| `—` | UGPE_CONSOLIDADO | ALTA | Decisão: (1) adicionar 'UGPE' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/ |

## Detalhe — D_PASTA_ORFA_DOS

| SSOT | Pasta(s) afetada(s) | Severidade | Ação recomendada |
|------|---------------------|------------|------------------|
| `—` | ALEAM_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/ALEAM_DOSSIE ou remapear |
| `—` | AMAZONASTUR_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/AMAZONASTUR_DOSSIE ou remapear |
| `—` | ASSOC_SAUDE_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/ASSOC_SAUDE_DOSSIE ou remapear |
| `—` | CIAMA_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/CIAMA_DOSSIE ou remapear |
| `—` | DEFESA_CIVIL_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/DEFESA_CIVIL_DOSSIE ou remapear |
| `—` | DESCONHECIDO_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/DESCONHECIDO_DOSSIE ou remapear |
| `—` | FAPEAM_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/FAPEAM_DOSSIE ou remapear |
| `—` | FEPIAM_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/FEPIAM_DOSSIE ou remapear |
| `—` | IMPRENSA_OFICIAL_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/IMPRENSA_OFICIAL_DOSSIE ou remapear |
| `—` | JUCEA_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/JUCEA_DOSSIE ou remapear |
| `—` | PGJ_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/PGJ_DOSSIE ou remapear |
| `—` | PROCON_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/PROCON_DOSSIE ou remapear |
| `—` | SECOM_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/SECOM_DOSSIE ou remapear |
| `—` | SEDURB_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/SEDURB_DOSSIE ou remapear |
| `—` | SEPA_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/SEPA_DOSSIE ou remapear |
| `—` | SRMM_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/SRMM_DOSSIE ou remapear |
| `—` | SUBCOMADEC_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/SUBCOMADEC_DOSSIE ou remapear |
| `—` | TCE_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/TCE_DOSSIE ou remapear |
| `—` | UEA_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/UEA_DOSSIE ou remapear |
| `—` | UGPE_DOSSIE | MEDIA | Decisão: arquivar em _ARQUIVO_ORFA/UGPE_DOSSIE ou remapear |

## Próximos passos

1. Revisar este relatório e `reconciliacao_ssot.csv` com o usuário.
2. Para cada linha, marcar decisão: **CONSOLIDAR**, **RENOMEAR**, **ARQUIVAR**, **ADICIONAR_SSOT** ou **REMOVER_SSOT**.
3. Executar `executar_reconciliacao.ps1` (ele solicita confirmação antes de cada ação).
4. Rodar `sincronizar_prodam.py` para regerar SSOT e artefatos.
