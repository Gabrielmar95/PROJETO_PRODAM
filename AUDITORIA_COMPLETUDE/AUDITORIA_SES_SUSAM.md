# Auditoria de Completude — SES/SUSAM
**Secretaria de Saúde do Amazonas / Fundação de Medicina Tropical** | Categoria: **GOV_DIRETA** | Data: 2026-06-10

## Score de Completude: **36.4%**

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
| `dossie_folder` | ❌ FALTANDO | Pasta <DEVEDOR>_DOSSIE/ no PRODAM_DOCS |
| `consolidado_folder` | ❌ FALTANDO | Pasta <DEVEDOR>_CONSOLIDADO/ no PRODAM_DOCS |


## Contagens (todas as fontes)

| Fonte | Qtd | Valor |
|-------|-----|-------|
| Contratos SPCF | 0 | — |
| Contratos no DB | 0 | — |
| Empenhos no DB | 475 | R$ 107.076.806,49 |
| Faturas no DB | 111 | R$ 6.752.583,41 |
| Cobranças SPCF | 111 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | *(AUSENTE)* |
| Pasta Consolidado | *(AUSENTE)* |
| SPCF por_devedor | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/SPCF_EXTRACAO/por_devedor/SES_SUSAM |

## Documentos Faltantes (7)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ cnd: CNDs / Certidões
- ❌ dossie_folder: Pasta <DEVEDOR>_DOSSIE/ no PRODAM_DOCS
- ❌ consolidado_folder: Pasta <DEVEDOR>_CONSOLIDADO/ no PRODAM_DOCS

## Divergências (2)

### Tipo: `valor_aberto_vs_db_faturas`
- **profile:** 8268269.07
- **db_faturas:** 6752583.409999997
- **delta:** 1515685.660000003
- **pct:** 18.3%

### Tipo: `faturas_aberto_qtd_profile_vs_db`
- **profile:** 137
- **db:** 111
- **delta:** 26

