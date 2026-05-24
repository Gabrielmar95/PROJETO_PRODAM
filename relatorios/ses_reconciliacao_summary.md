# Reconciliação SES/SUSAM — 2026-04-14

## Universo consolidado
- **1016 faturas únicas** cruzadas de 4 fontes SPCF
- Cutoff prescrição: 2021-04-14 (HOJE −5 anos)

## Distribuição por exigibilidade

| Classe | Qtd | Valor |
|--------|-----|-------|
| Exigíveis (não prescritas + em aberto) | **73** | **R$ 3.745.779,18** |
| Prescritas | 176 | R$ 4.567.134,92 |
| Pagas | 860 | — |
| Canceladas | 19 | — |

## Distribuição por fontes

| Combinação de fontes | Qtd |
|----------------------|-----|
| GERAL | 879 |
| ABERTO+DB | 62 |
| ABERTO+DB+GERAL | 48 |
| ABERTO+GERAL | 26 |
| ABERTO | 1 |


## Exigíveis por rastreabilidade documental

| Cenário | Qtd | Observação |
|---------|-----|------------|
| Em DB (cobrança ativa SPCF) | 47 | Cadeia documental já mapeada |
| Em ABERTO sem DB | 26 | Faturas novas (2024-2026) — integrar ao DB |
| Só em GERAL | 0 | Sem cobrança ativa nem aberto — investigar |

## Divergência com profiles.json

| Campo | profiles.json | Reconciliação | Status |
|-------|--------------|---------------|--------|
| faturas_exigiveis | 144 | **73** | DIVERGE |
| val_exig | R$ 14.748.048,95 | **R$ 3.745.779,18** | DIVERGE |

## Top 10 exigíveis por valor

| ID | Contrato | Comp. | Valor | Fontes |
|----|----------|-------|-------|--------|
| 161532 | 018/2021 | 07/2025 | R$ 185.399,50 | ABERTO+DB+GERAL |
| 163045 | 021/2021 | 09/2025 | R$ 160.469,55 | ABERTO+DB+GERAL |
| 163914 | 021/2021 | 10/2025 | R$ 160.469,55 | ABERTO+DB+GERAL |
| 166662 | C.21/2021 | 02/2026 | R$ 160.469,55 | ABERTO+GERAL |
| 167205 | C.21/2021 | 03/2026 | R$ 158.160,62 | ABERTO+GERAL |
| 161534 | 018/2021 | 07/2025 | R$ 151.234,43 | ABERTO+DB+GERAL |
| 137096 | 054/2018 | 11/2022 | R$ 146.012,35 | ABERTO+DB+GERAL |
| 166730 | C.18/2024 | 02/2026 | R$ 146.012,35 | ABERTO+GERAL |
| 167245 | C.18/2024 | 03/2026 | R$ 146.012,35 | ABERTO+GERAL |
| 126765 | 074/2021 | 08/2021 | R$ 139.166,79 | ABERTO+DB+GERAL |
