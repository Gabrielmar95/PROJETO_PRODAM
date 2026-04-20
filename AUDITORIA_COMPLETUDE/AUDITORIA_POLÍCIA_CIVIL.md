# Auditoria de Completude — POLÍCIA CIVIL
**Polícia Civil do Amazonas** | Categoria: **GOV_DIRETA** | Data: 2026-04-17

## Score de Completude: **27.3%**

## Checklist de Documentos

| Item | Status | Descrição |
|------|--------|-----------|
| `contrato` | ❌ FALTANDO | Pelo menos 1 contrato PDF ou ID |
| `empenhos` | ✅ OK | NEs vinculadas ao contrato |
| `nls` | ❌ FALTANDO | Notas de Liquidação |
| `nfs` | ✅ OK | Notas Fiscais / RPS |
| `aceites` | ❌ FALTANDO | Aceites técnicos / recibos |
| `cobrancas` | ❌ FALTANDO | Registros de cobrança SPCF |
| `oficios` | ❌ FALTANDO | Ofícios de cobrança |
| `reconhecimento` | ✅ OK | Atos de reconhecimento tácito/expresso |
| `cnd` | ❌ FALTANDO | CNDs / Certidões |
| `dossie_folder` | ❌ FALTANDO | Pasta <DEVEDOR>_DOSSIE/ no PRODAM_DOCS |
| `consolidado_folder` | ❌ FALTANDO | Pasta <DEVEDOR>_CONSOLIDADO/ no PRODAM_DOCS |


## Contagens (todas as fontes)

| Fonte | Qtd | Valor |
|-------|-----|-------|
| Contratos SPCF | 0 | — |
| Contratos no DB | 0 | — |
| Empenhos no DB | 158 | R$ 18.307.206,98 |
| Faturas no DB | 18 | R$ 625.567,97 |
| Cobranças SPCF | 0 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | *(AUSENTE)* |
| Pasta Consolidado | *(AUSENTE)* |
| SPCF por_devedor | C:\Users\gabri\Desktop\PROJETO_PRODAM\SPCF_EXTRACAO\por_devedor\POLÍCIA CIVIL |

## Documentos Faltantes (8)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ cobrancas: Registros de cobrança SPCF
- ❌ oficios: Ofícios de cobrança
- ❌ cnd: CNDs / Certidões
- ❌ dossie_folder: Pasta <DEVEDOR>_DOSSIE/ no PRODAM_DOCS
- ❌ consolidado_folder: Pasta <DEVEDOR>_CONSOLIDADO/ no PRODAM_DOCS

## Divergências (2)

### Tipo: `valor_exig_vs_db_faturas`
- **profile:** 960481.713334285
- **db_faturas:** 625567.97
- **delta:** 334913.743334285
- **pct:** 34.9%

### Tipo: `faturas_qtd_profile_vs_db`
- **profile:** 32
- **db:** 18
- **delta:** 14

