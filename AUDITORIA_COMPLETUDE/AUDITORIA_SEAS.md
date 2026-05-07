# Auditoria de Completude — SEAS
**Secretaria de Assuntos Estratégicos** | Categoria: **GOV_DIRETA** | Data: 2026-05-07

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
| Empenhos no DB | 415 | R$ 11.691.051,78 |
| Faturas no DB | 25 | R$ 219.783,61 |
| Cobranças SPCF | 25 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\SEAS_DOSSIE |
| Pasta Consolidado | C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\SEAS_CONSOLIDADO |
| SPCF por_devedor | C:\Users\gabri\Desktop\PROJETO_PRODAM\SPCF_EXTRACAO\por_devedor\SEAS |

## Documentos Faltantes (5)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ cnd: CNDs / Certidões

## Divergências (2)

### Tipo: `valor_aberto_vs_db_faturas`
- **profile:** 362026.30
- **db_faturas:** 219783.61000000002
- **delta:** 142242.68999999998
- **pct:** 39.3%

### Tipo: `faturas_aberto_qtd_profile_vs_db`
- **profile:** 38
- **db:** 25
- **delta:** 13

