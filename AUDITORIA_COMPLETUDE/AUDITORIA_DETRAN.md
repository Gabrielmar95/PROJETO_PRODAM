# Auditoria de Completude — DETRAN
**Departamento Estadual de Trânsito do Amazonas** | Categoria: **GOV_INDIRETA** | Data: 2026-06-09

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
| Empenhos no DB | 470 | R$ 250.316.057,30 |
| Faturas no DB | 113 | R$ 17.802.420,55 |
| Cobranças SPCF | 113 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | /sessions/wizardly-affectionate-babbage/mnt/PROJETO_PRODAM/PRODAM_DOCS/DETRAN_DOSSIE |
| Pasta Consolidado | /sessions/wizardly-affectionate-babbage/mnt/PROJETO_PRODAM/PRODAM_DOCS/DETRAN_CONSOLIDADO |
| SPCF por_devedor | /sessions/wizardly-affectionate-babbage/mnt/PROJETO_PRODAM/SPCF_EXTRACAO/por_devedor/DETRAN |

## Documentos Faltantes (5)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ cnd: CNDs / Certidões

## Divergências (2)

### Tipo: `valor_aberto_vs_db_faturas`
- **profile:** 22448434.53
- **db_faturas:** 17802420.549999997
- **delta:** 4646013.980000003
- **pct:** 20.7%

### Tipo: `faturas_aberto_qtd_profile_vs_db`
- **profile:** 149
- **db:** 113
- **delta:** 36

