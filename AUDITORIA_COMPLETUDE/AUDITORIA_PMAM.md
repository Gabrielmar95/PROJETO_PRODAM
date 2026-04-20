# Auditoria de Completude — PMAM
**Polícia Militar do Amazonas** | Categoria: **GOV_DIRETA** | Data: 2026-04-17

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
| Empenhos no DB | 95 | R$ 2.536.803,94 |
| Faturas no DB | 2 | R$ 15.075,80 |
| Cobranças SPCF | 2 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\PMAM_DOSSIE |
| Pasta Consolidado | C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\PMAM_CONSOLIDADO |
| SPCF por_devedor | C:\Users\gabri\Desktop\PROJETO_PRODAM\SPCF_EXTRACAO\por_devedor\PMAM |

## Documentos Faltantes (6)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ reconhecimento: Atos de reconhecimento tácito/expresso
- ❌ cnd: CNDs / Certidões

## Divergências (2)

### Tipo: `valor_exig_vs_db_faturas`
- **profile:** 27020.90058524942
- **db_faturas:** 15075.8
- **delta:** 11945.10058524942
- **pct:** 44.2%

### Tipo: `faturas_qtd_profile_vs_db`
- **profile:** 8
- **db:** 2
- **delta:** 6

