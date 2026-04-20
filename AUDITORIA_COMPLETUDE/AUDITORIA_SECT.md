# Auditoria de Completude — SECT
**Secretaria de Ciência e Tecnologia** | Categoria: **GOV_DIRETA** | Data: 2026-04-17

## Score de Completude: **54.5%**

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
| `reconhecimento` | ✅ OK | Atos de reconhecimento tácito/expresso |
| `cnd` | ❌ FALTANDO | CNDs / Certidões |
| `dossie_folder` | ✅ OK | Pasta <DEVEDOR>_DOSSIE/ no PRODAM_DOCS |
| `consolidado_folder` | ✅ OK | Pasta <DEVEDOR>_CONSOLIDADO/ no PRODAM_DOCS |


## Contagens (todas as fontes)

| Fonte | Qtd | Valor |
|-------|-----|-------|
| Contratos SPCF | 0 | — |
| Contratos no DB | 0 | — |
| Empenhos no DB | 220 | R$ 3.231.567,49 |
| Faturas no DB | 8 | R$ 38.747,15 |
| Cobranças SPCF | 15 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\SECT_DOSSIE |
| Pasta Consolidado | C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\SECT_CONSOLIDADO |
| SPCF por_devedor | C:\Users\gabri\Desktop\PROJETO_PRODAM\SPCF_EXTRACAO\por_devedor\SECT |

## Documentos Faltantes (5)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ cnd: CNDs / Certidões

## Divergências (2)

### Tipo: `valor_exig_vs_db_faturas`
- **profile:** 258328.5777689927
- **db_faturas:** 38747.15
- **delta:** 219581.4277689927
- **pct:** 85.0%

### Tipo: `faturas_qtd_profile_vs_db`
- **profile:** 35
- **db:** 8
- **delta:** 27

