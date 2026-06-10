# Auditoria de Completude — ADS
**Agência de Desenvolvimento Sustentável do Amazonas** | Categoria: **GOV_INDIRETA** | Data: 2026-06-10

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
| Empenhos no DB | 256 | R$ 1.191.974,61 |
| Faturas no DB | 6 | R$ 10.230,60 |
| Cobranças SPCF | 6 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/PRODAM_DOCS/ADS_DOSSIE |
| Pasta Consolidado | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/PRODAM_DOCS/ADS_CONSOLIDADO |
| SPCF por_devedor | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/SPCF_EXTRACAO/por_devedor/ADS |

## Documentos Faltantes (6)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ reconhecimento: Atos de reconhecimento tácito/expresso
- ❌ cnd: CNDs / Certidões

## Divergências (1)

### Tipo: `valor_aberto_vs_db_faturas`
- **profile:** 13278.28
- **db_faturas:** 10230.6
- **delta:** 3047.68
- **pct:** 23.0%

