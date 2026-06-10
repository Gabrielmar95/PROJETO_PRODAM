# RELATÓRIO DE ORGANIZAÇÃO — 2026-06-10
## Projeto PRODAM · skill `organizador-arquivos-prodam` v2.0 · modo CÓPIA não-destrutivo

**Escopo aprovado:** opção A (acervo completo). **Origem intocada** — nenhum arquivo original foi apagado, movido ou alterado. Pastas `*_archive*` ignoradas por regra do projeto.

## 1. Números finais

| Métrica | Valor |
|---|---|
| Arquivos inventariados (após exclusões de regra) | 91.256 (32,4 GB) |
| Cópias únicas criadas em `_ORGANIZADO_2026-06-10/` | **70.298** (19,3 GB) |
| Verificação de integridade | **MD5 origem==destino em 100% das cópias** + spot-check independente 300/300 |
| Duplicatas exatas NÃO recopiadas (1 cópia mantida) | 20.958 arquivos em 9.129 grupos (~13,4 GB poupados) |
| Renomeados no padrão PRODAM (prefixo DEVEDOR_TAG) | 70,250 |
| Zero-bytes copiados com flag `ZERO_BYTES` (possível download falho) | 140 |
| Erros de cópia / faltantes na auditoria | **0 / 0** |

## 2. Árvore criada (devedor → tipo)

`_ORGANIZADO_2026-06-10/<DEVEDOR>/<TIPO>/` — tipos: 01_CONTRATOS, 02_NOTAS_EMPENHO, 03_NOTAS_LIQUIDACAO, 04_FATURAS, 05_ACEITES_TECNICOS, 06_OFICIOS, 07_NOTIFICACOES, 12_PECAS_E_DOSSIES, 14_PLANILHAS, 15_DADOS, 16_COBRANCAS, 98_TECNICO, 99_OUTROS etc.

| Pasta (1º nível) | Arquivos |
|---|---|
| _NAO_IDENTIFICADO | 54.360 |
| DETRAN | 8.661 |
| SEAD | 812 |
| SES_SUSAM | 805 |
| SEDUC | 636 |
| SSP | 572 |
| SEFAZ | 378 |
| FAAR_SEDEL | 215 |
| FVS | 159 |
| IPAAM | 158 |
| FHAJ | 149 |
| SEDECTI | 145 |
| FCECON | 140 |
| FUAM_FUHAM | 132 |
| FMT | 125 |
| ARSEPAM | 124 |
| ADS | 118 |
| SUHAB | 117 |

## 3. Tabela "nome original → nome novo → destino"

Tabela completa (91.256 linhas, separador `;`, abre no Excel): **`_ORGANIZADO_2026-06-10/_MANIFESTO/manifesto_20260610_FASE2.csv`** — colunas `origem_rel`, `nome_sugerido`, `destino_rel`, `acao`, `resultado_copia`, `duplicata_de`, `flags`, `md5`. Exemplos:

| Original (final do caminho) | Nome novo | Destino |
|---|---|---|
| `00_RESUMO_GERAL_DETRAN-AM.md` | `DETRAN_DOC_00-resumo-geral-detran-am.md` | `DETRAN/99_OUTROS` |
| `60423/_OUT_inventario_detran_externo_20260423_110633/classificados.csv` | `DETRAN_PLAN_classificados.csv` | `DETRAN/14_PLANILHAS` |
| `_20260423/_OUT_inventario_detran_externo_20260423_110633/progresso.log` | `DETRAN_TEC_progresso.log` | `DETRAN/98_TECNICO` |
| `O_20260423/_OUT_inventario_detran_externo_20260423_110633/relatorio.md` | `DETRAN_RELAT_relatorio.md` | `DETRAN/08_RELATORIOS` |
| `3/_OUT_inventario_detran_externo_20260423_110633/renomear_proposto.csv` | `DETRAN_PLAN_renomear-proposto.csv` | `DETRAN/14_PLANILHAS` |
| `O_20260423/_OUT_inventario_detran_externo_20260423_110633/universo.csv` | `DETRAN_PLAN_universo.csv` | `DETRAN/14_PLANILHAS` |

## 4. Duplicatas exatas eliminadas da estrutura

20.958 cópias redundantes não foram recopiadas; cada uma está registrada no manifesto com `acao=DUPLICATA` e a coluna `duplicata_de` apontando o arquivo mantido. Nenhum original foi tocado.

## 5. Quase-duplicatas — PENDENTES DE DECISÃO HUMANA

**9.476 grupos / 33.590 arquivos** (mesmo nome normalizado, conteúdo diferente — ex.: mesmo documento escaneado 2x, versões de dossiês). Nenhuma decisão automática foi tomada. Lista completa: inventário da FASE 1 (`outputs/_STATE_INVENTARIO/inventario_20260610_063121_678.json`, chave `quase_duplicatas_para_revisao_humana`) e flag `QUASE_DUP_CANDIDATA` no manifesto.

## 6. Triagem manual (`_NAO_IDENTIFICADO/`)

**54,360 arquivos** sem devedor reconhecido pelo nome/caminho (profiles.json como SSOT) — majoritariamente material técnico (HTML/JSON/TXT de extrações SPCF). Inclui 1,094 casos com flag `DEVEDOR_AMBIGUO` (ex.: certidão SEFAZ em pasta DETRAN). A auditoria encontrou **0 RECLASSIFICÁVEIS** (nenhum nome identifica devedor com segurança).

## 7. Achados da auditoria (`_MANIFESTO/auditoria_20260610_093351_974.*`)

- **0 FALTANTES** (manifesto × disco), 0 PASTA_DESCONHECIDA, 0 DEVEDOR_DIVERGENTE, 0 FORA_DA_ESTRUTURA.
- **105 TIPO_DIVERGENTE** (CSV da auditoria): o nome renomeado sugere tipo diferente da pasta — em geral falso-positivo de reclassificação pós-renome; revisar quando conveniente.
- **16 zero-bytes homônimos colapsaram** no mesmo destino `_NAO_IDENTIFICADO/99_OUTROS/DOC_guidelines_hd41d8c.md` (sufixo de desambiguação usa MD5, idêntico para arquivos vazios). Sem perda de conteúdo (vazios); origens listadas no manifesto (`resultado_copia=JA_EXISTE`).
- **1 grupo de "duplicata entre devedores"**: artefato dos zero-bytes (mesmo MD5 vazio em 25 pastas).
- **4 resíduos técnicos** de cópia retomável não removíveis via sessão (limitação do filesystem montado) — remover no PowerShell:

```powershell
Remove-Item "C:\Users\gabri\Desktop\PROJETO_PRODAM\_ORGANIZADO_2026-06-10\ADAF\99_OUTROS\ADAF_DOC_01-01-018202-0068192023-27-ok.pdf.partial","C:\Users\gabri\Desktop\PROJETO_PRODAM\_ORGANIZADO_2026-06-10\_NAO_IDENTIFICADO\98_TECNICO\.speed_test","C:\Users\gabri\Desktop\PROJETO_PRODAM\_ORGANIZADO_2026-06-10\_NAO_IDENTIFICADO\98_TECNICO\TEC_ocr-consolidado.db.partial","C:\Users\gabri\Desktop\PROJETO_PRODAM\_ORGANIZADO_2026-06-10\_NAO_IDENTIFICADO\98_TECNICO\TEC_prodam-analise.db.partial"
```

## 8. Rastreabilidade

`_MANIFESTO/`: manifesto JSON (SSOT) + CSV; `auditoria_*.json/.csv`; `cache_md5.json` (91.256 hashes). Estado de execução e inventário da FASE 1: pasta `outputs/_STATE_INVENTARIO` da sessão. Execução em blocos retomáveis com 9 subagentes (hash 3× + plano 1× + cópia 5×), exigida pelo limite de 45 s/chamada do ambiente.

_Nota: a renomeação segue o padrão conservador da skill (prefixo `DEVEDOR_TAG` + descritor real). O nome canônico fatura-a-fatura (`NE-<id>_CT-<contrato>_id<spcf>`) exige lookup SPCF e ficou fora do escopo, conforme documentação da skill._
