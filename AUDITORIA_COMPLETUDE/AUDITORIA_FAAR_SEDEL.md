# Auditoria de Completude — FAAR/SEDEL
**Fundação de Amparo à Pesquisa do Amazonas / Secretaria de Desenvolvimento Econômico** | Categoria: **GOV_INDIRETA** | Data: 2026-05-07

## Score de Completude: **27.3%**

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
| `dossie_folder` | ❌ FALTANDO | Pasta <DEVEDOR>_DOSSIE/ no PRODAM_DOCS |
| `consolidado_folder` | ❌ FALTANDO | Pasta <DEVEDOR>_CONSOLIDADO/ no PRODAM_DOCS |


## Contagens (todas as fontes)

| Fonte | Qtd | Valor |
|-------|-----|-------|
| Contratos SPCF | 0 | — |
| Contratos no DB | 0 | — |
| Empenhos no DB | 155 | R$ 2.446.703,48 |
| Faturas no DB | 72 | R$ 364.632,44 |
| Cobranças SPCF | 72 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | *(AUSENTE)* |
| Pasta Consolidado | *(AUSENTE)* |
| SPCF por_devedor | C:\Users\gabri\Desktop\PROJETO_PRODAM\SPCF_EXTRACAO\por_devedor\FAAR_SEDEL |

## Documentos Faltantes (8)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ reconhecimento: Atos de reconhecimento tácito/expresso
- ❌ cnd: CNDs / Certidões
- ❌ dossie_folder: Pasta <DEVEDOR>_DOSSIE/ no PRODAM_DOCS
- ❌ consolidado_folder: Pasta <DEVEDOR>_CONSOLIDADO/ no PRODAM_DOCS

## Divergências (2)

### Tipo: `valor_aberto_vs_db_faturas`
- **profile:** 104811.74
- **db_faturas:** 364632.44
- **delta:** 259820.70
- **pct:** 247.9%

### Tipo: `faturas_aberto_qtd_profile_vs_db`
- **profile:** 23
- **db:** 72
- **delta:** 49

