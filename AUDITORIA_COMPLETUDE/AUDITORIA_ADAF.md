# Auditoria de Completude — ADAF
**Agência de Defesa Agropecuária e Florestal do Amazonas** | Categoria: **GOV_INDIRETA** | Data: 2026-06-09

## Score de Completude: **45.5%**

## Checklist de Documentos

| Item | Status | Descrição |
|------|--------|-----------|
| `contrato` | ❌ FALTANDO | Pelo menos 1 contrato PDF ou ID |
| `empenhos` | ✅ OK | NEs vinculadas ao contrato |
| `nls` | ❌ FALTANDO | Notas de Liquidação |
| `nfs` | ✅ OK | Notas Fiscais / RPS |
| `aceites` | ❌ FALTANDO | Aceites técnicos / recibos |
| `cobrancas` | ✅ OK | Registros de cobrança SPCF |
| `oficios` | ❌ FALTANDO | Ofícios de cobrança |
| `reconhecimento` | ❌ FALTANDO | Atos de reconhecimento tácito/expresso |
| `cnd` | ❌ FALTANDO | CNDs / Certidões |
| `dossie_folder` | ✅ OK | Pasta <DEVEDOR>_DOSSIE/ no PRODAM_DOCS |
| `consolidado_folder` | ✅ OK | Pasta <DEVEDOR>_CONSOLIDADO/ no PRODAM_DOCS |


## Contagens (todas as fontes)

| Fonte | Qtd | Valor |
|-------|-----|-------|
| Contratos SPCF | 0 | — |
| Contratos no DB | 0 | — |
| Empenhos no DB | 275 | R$ 2.425.272,36 |
| Faturas no DB | 27 | R$ 122.182,04 |
| Cobranças SPCF | 27 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | /sessions/wizardly-affectionate-babbage/mnt/PROJETO_PRODAM/PRODAM_DOCS/ADAF_DOSSIE |
| Pasta Consolidado | /sessions/wizardly-affectionate-babbage/mnt/PROJETO_PRODAM/PRODAM_DOCS/ADAF_CONSOLIDADO |
| SPCF por_devedor | /sessions/wizardly-affectionate-babbage/mnt/PROJETO_PRODAM/SPCF_EXTRACAO/por_devedor/ADAF |

## Documentos Faltantes (6)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ reconhecimento: Atos de reconhecimento tácito/expresso
- ❌ cnd: CNDs / Certidões

## Divergências (2)

### Tipo: `valor_aberto_vs_db_faturas`
- **profile:** 150294.16
- **db_faturas:** 122182.04
- **delta:** 28112.12
- **pct:** 18.7%

### Tipo: `faturas_aberto_qtd_profile_vs_db`
- **profile:** 39
- **db:** 27
- **delta:** 12

