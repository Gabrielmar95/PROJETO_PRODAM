# Auditoria de Completude — SEPROR
**Secretaria de Produção Rural** | Categoria: **GOV_DIRETA** | Data: 2026-06-10

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
| Pasta Dossiê | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/PRODAM_DOCS/SEPROR_DOSSIE |
| Pasta Consolidado | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/PRODAM_DOCS/SEPROR_CONSOLIDADO |
| SPCF por_devedor | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/SPCF_EXTRACAO/por_devedor/SEPROR |

## Documentos Faltantes (5)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ cnd: CNDs / Certidões

## Divergências (1)

### Tipo: `valor_aberto_vs_db_faturas`
- **profile:** 56588.49
- **db_faturas:** 38581.46000000001
- **delta:** 18007.02999999999
- **pct:** 31.8%

