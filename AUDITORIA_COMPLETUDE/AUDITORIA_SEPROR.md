# Auditoria de Completude — SEPROR
**Secretaria de Produção Rural** | Categoria: **GOV_DIRETA** | Data: 2026-04-17

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
| Empenhos no DB | 298 | R$ 3.296.503,19 |
| Faturas no DB | 3 | R$ 38.581,46 |
| Cobranças SPCF | 3 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\SEPROR_DOSSIE |
| Pasta Consolidado | C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\SEPROR_CONSOLIDADO |
| SPCF por_devedor | C:\Users\gabri\Desktop\PROJETO_PRODAM\SPCF_EXTRACAO\por_devedor\SEPROR |

## Documentos Faltantes (5)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ cnd: CNDs / Certidões

## Divergências (2)

### Tipo: `valor_exig_vs_db_faturas`
- **profile:** 77960.49143925689
- **db_faturas:** 38581.46
- **delta:** 39379.03143925689
- **pct:** 50.5%

### Tipo: `faturas_qtd_profile_vs_db`
- **profile:** 15
- **db:** 3
- **delta:** 12

