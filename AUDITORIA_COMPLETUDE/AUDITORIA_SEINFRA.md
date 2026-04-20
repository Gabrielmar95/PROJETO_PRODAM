# Auditoria de Completude — SEINFRA
**Secretaria de Infraestrutura** | Categoria: **GOV_DIRETA** | Data: 2026-04-17

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
| Empenhos no DB | 395 | R$ 7.754.214,44 |
| Faturas no DB | 12 | R$ 71.805,43 |
| Cobranças SPCF | 12 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\SEINFRA_DOSSIE |
| Pasta Consolidado | C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\SEINFRA_CONSOLIDADO |
| SPCF por_devedor | C:\Users\gabri\Desktop\PROJETO_PRODAM\SPCF_EXTRACAO\por_devedor\SEINFRA |

## Documentos Faltantes (5)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ cnd: CNDs / Certidões

## Divergências (2)

### Tipo: `valor_exig_vs_db_faturas`
- **profile:** 379631.5477448804
- **db_faturas:** 71805.43000000001
- **delta:** 307826.11774488039
- **pct:** 81.1%

### Tipo: `faturas_qtd_profile_vs_db`
- **profile:** 38
- **db:** 12
- **delta:** 26

