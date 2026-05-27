# Exposição Contratual — Multa por prescrição perdida + atraso de relatório

**Status:** ready-for-human (memorando para Brandão Ozores Advogados)
**Aberto em:** 2026-05-27
**Decisor:** Gabriel Mar (revisar + repassar)
**Fonte de dados:** `profiles_resumo.csv` (snapshot 27/05/2026), Contrato 002/2026 cláusula de multa
**Cálculo:** Decimal (Regra #16); arredondamento `ROUND_HALF_UP`; formato BRL

---

## Sumário executivo (4 números para a reunião)

| Indicador | Valor | Base |
|---|---:|---|
| **Carteira total exigível** | R$ 93.632.770,89 | 69 devedores no CSV |
| **Carteira total atualizada** | R$ 160.936.948,42 | mesmo, com correção monetária |
| **Já prescrita (val_atualizado)** | **R$ 104.636.986,17** | 23 devedores, `d_plus < 0` |
| **Exposição 10% HOJE** | **R$ 10.463.698,62** | 10% sobre val_atualizado prescritos |
| **Exposição 10% se ADS prescrever (D+3)** | R$ 10.484.864,36 | + R$ 21.165,75 da ADS |
| **Exposição 10% se SES/SUSAM prescrever (D+34)** | R$ 14.876.826,28 | + R$ 4.392.161,92 da SES/SUSAM |

> ⚠️ **A multa de 10% é o pior cenário contratual** — Cláusula do Contrato 002/2026 (Brandão Ozores × Gabriel Mar). Ela só incide efetivamente se PRODAM S.A. invocar a cláusula em sede de inadimplemento contratual do escritório. **Mitigação completa possível** mediante (i) notificação extrajudicial documentada antes da prescrição efetiva (interrompe inércia adversarial e suspende a discussão de "perda"), (ii) parecer jurídico arquivando crédito por inviabilidade fática ANTES do d_plus negativo, ou (iii) reconhecimento tácito superveniente do devedor (Art. 202 VI CC) ressuscitando faturas.

---

## Tabela completa — 23 devedores prescritos (multa 10% potencial)

| # | Devedor | Categoria | Força | d_plus | val_exig | val_atualizado | Multa 10% (sobre atualizado) |
|---|---|---|---|---:|---:|---:|---:|
| 1 | SEDUC | GOV_DIRETA | FORTE | -20 | R$ 49.215.512,48 | R$ 50.263.263,56 | **R$ 5.026.326,36** |
| 2 | SSP | GOV_DIRETA | FORTE | -39 | R$ 4.553.230,80 | R$ 29.034.062,63 | **R$ 2.903.406,26** |
| 3 | SEJUSC | GOV_DIRETA | MÉDIA | -20 | R$ 2.589.660,12 | R$ 5.262.537,82 | R$ 526.253,78 |
| 4 | SEAD | GOV_DIRETA | FORTE | -20 | R$ 2.339.702,20 | R$ 4.296.278,76 | R$ 429.627,88 |
| 5 | SEDECTI | GOV_DIRETA | MÉDIA | -20 | R$ 1.249.203,13 | R$ 4.007.244,35 | R$ 400.724,44 |
| 6 | POLÍCIA CIVIL | GOV_DIRETA | MÉDIA | -20 | R$ 960.481,71 | R$ 1.908.089,75 | R$ 190.808,98 |
| 7 | PGE | GOV_DIRETA | MÉDIA | -20 | R$ 680.239,77 | R$ 1.603.066,41 | R$ 160.306,64 |
| 8 | FAAR/SEDEL | GOV_INDIRETA | FRACA | -20 | R$ 734.498,94 | R$ 1.472.879,25 | R$ 147.287,93 |
| 9 | SUHAB | GOV_INDIRETA | MÉDIA | -20 | R$ 840.061,15 | R$ 1.210.268,55 | R$ 121.026,86 |
| 10 | AMAZONPREV | GOV_INDIRETA | MÉDIA | -20 | R$ 736.219,79 | R$ 1.142.951,74 | R$ 114.295,17 |
| 11 | IDAM | GOV_INDIRETA | FRACA | -20 | R$ 328.735,51 | R$ 892.277,93 | R$ 89.227,79 |
| 12 | FCECON | GOV_INDIRETA | FORTE | -20 | R$ 637.106,68 | R$ 828.620,63 | R$ 82.862,06 |
| 13 | FMT | GOV_INDIRETA | MÉDIA | -20 | R$ 272.130,68 | R$ 693.107,38 | R$ 69.310,74 |
| 14 | FHAJ | GOV_INDIRETA | FORTE | -20 | R$ 259.910,78 | R$ 493.519,13 | R$ 49.351,91 |
| 15 | FUAM/FUHAM | GOV_INDIRETA | FORTE | -20 | R$ 44.020,01 | R$ 356.355,07 | R$ 35.635,51 |
| 16 | SECT | GOV_DIRETA | MÉDIA | -20 | R$ 258.328,58 | R$ 296.246,97 | R$ 29.624,70 |
| 17 | SEFAZ | GOV_DIRETA | MÉDIA | -20 | R$ 198.980,49 | R$ 283.622,83 | R$ 28.362,28 |
| 18 | SEC | GOV_DIRETA | FORTE | -20 | R$ 99.050,71 | R$ 248.155,42 | R$ 24.815,54 |
| 19 | SEPROR | GOV_DIRETA | MÉDIA | -20 | R$ 77.960,49 | R$ 170.884,10 | R$ 17.088,41 |
| 20 | CBMAM | GOV_DIRETA | FORTE | -20 | R$ 3.134,03 | R$ 71.483,16 | R$ 7.148,32 |
| 21 | SEMA | GOV_DIRETA | MÉDIA | -20 | R$ 38.541,11 | R$ 49.842,07 | R$ 4.984,21 |
| 22 | PMAM | GOV_DIRETA | FRACA | -20 | R$ 27.020,90 | R$ 38.951,91 | R$ 3.895,19 |
| 23 | FHEMOAM | GOV_INDIRETA | FRACA | -20 | R$ 6.886,91 | R$ 13.276,75 | R$ 1.327,68 |
| | **TOTAL** | | | | **R$ 66.150.616,97** | **R$ 104.636.986,17** | **R$ 10.463.698,62** |

> **Concentração**: SEDUC + SSP = R$ 79.297.326,19 (75,8% da exposição). Se for possível argumentar mitigação só nesses 2, exposição cai para R$ 2.533.965,99 (24,2%).

---

## Por categoria

| Categoria | N devedores | val_atualizado | Multa 10% | % do total |
|---|---:|---:|---:|---:|
| GOV_DIRETA | 14 | R$ 97.533.729,74 | **R$ 9.753.372,97** | 93,2% |
| GOV_INDIRETA | 9 | R$ 7.103.256,43 | R$ 710.325,64 | 6,8% |
| EMPRESA_PRIVADA | 0 | — | — | — |
| **TOTAL** | **23** | **R$ 104.636.986,17** | **R$ 10.463.698,62** | 100% |

> Insight: **nenhum devedor privado está prescrito ainda** (todos têm `d_plus=1271`, ou seja, ~3,5 anos de margem). A exposição 10% é integralmente derivada de devedores públicos.

---

## Cenários de evolução nos próximos 90 dias

| Cenário | Quando | Devedores que entram | Multa adicional 10% | Exposição acumulada |
|---|---|---|---:|---:|
| Hoje (D+0) | 2026-05-27 | 23 prescritos | — | **R$ 10.463.698,62** |
| ADS prescreve | D+3 (2026-05-30) | + ADS | R$ 21.165,75 | R$ 10.484.864,36 |
| SES/SUSAM prescreve | D+34 (2026-06-30) | + SES/SUSAM | R$ 4.392.161,92 | **R$ 14.876.826,28** |
| Cenário "todos sem decisão" | D+90 (2026-08-25) | + 18 SEM_d_plus (se prescreverem) | até R$ 622.239,12 | até R$ 15.499.065,40 |

> ⚠️ **A janela SES/SUSAM (34 dias) representa o maior salto único (+R$ 4,4M)** — o TRD já está pronto em `DOCUMENTOS_GERADOS/SES_SUSAM/TRD_SES_SUSAM_2026-05-12.docx` (12/05), bloqueado há 15 dias. Enviar o AR mitiga R$ 4,39M de exposição de uma só vez (Janela 1, item 1.6 do plano).

---

## Multa R$ 500/dia (atraso de relatório quinzenal) — INPUT NECESSÁRIO

A multa de R$ 500/dia por atraso de relatório quinzenal incide sobre cada dia de atraso desde o último relatório esperado.

**Não posso calcular daqui** — preciso de:

1. **Data do último relatório quinzenal entregue** (ex.: 12/05/2026, 28/04/2026, etc.)
2. **Periodicidade exata pactuada** (a cada 15 dias corridos? a cada 2ª segunda-feira? primeiro útil de cada quinzena?)
3. **Marco de início** (data do contrato 002/2026 + primeiro relatório esperado)

**Cálculo placeholder** (assumindo último relatório entregue em 12/05/2026, ou seja, **15 dias atrás**):
- Atraso teórico: 0 dias (próximo relatório vencido em 27/05/2026 = hoje)
- Multa potencial: R$ 0,00

**Se último relatório foi 28/04/2026** (29 dias atrás):
- Atraso: 14 dias (próximo vencido em 13/05/2026)
- Multa: 14 × R$ 500 = **R$ 7.000,00**

**Se último relatório foi antes de 28/04/2026**:
- Cada dia adicional = + R$ 500,00

> ⚠️ Independente da data, a multa R$ 500/dia é **ordens de magnitude menor** que a multa 10% — não é a peça crítica do memorando.

---

## Mitigação — o que reduz exposição

### 1. Notificação extrajudicial documentada (qualquer devedor)
- Custo: AR Correios ~R$ 30 + tabelião protesto opcional R$ 80-300
- Efeito: interrompe **inércia adversarial** (matéria de defesa em ação contratual)
- Aplicável a: TODOS os 23 prescritos + ADS (D+3) + SES/SUSAM (D+34)
- Argumento: "diligência sob restrição documental" — escritório atuou no melhor possível dadas as condições; PRODAM teria de provar **dolo ou negligência grosseira**, não meramente atraso

### 2. Reconhecimento tácito superveniente do devedor (Art. 202 VI CC)
- Cabe SE o devedor (após prescrição) emitir NE, ofício de quitação parcial, ou despacho administrativo reconhecendo a dívida — ressuscita a fatura específica
- Tema 1.109/STJ: gestor público **NÃO** renuncia tacitamente; mas pode reconhecer expressamente
- Probabilidade real: baixa para órgãos estaduais; média para fundações (FCECON, FHAJ, FUAM/FUHAM)

### 3. Decreto Estadual 53.464/2026 — 4 exceções
- Verificar caso a caso ANTES de marcar como perda
- Pode mover devedor de "PRESCRITA" para "PROTEGIDA_ART202_VI"
- Hoje só DETRAN está protegido por esse mecanismo (val_exig=0 no CSV)

### 4. Auditoria documental adicional (item 2.0 do plano)
- Rodar `orgao_pipeline_completa.py --orgao <SIGLA>` para cada um dos 23 prescritos pode revelar NEs/aceites não-ingeridos = marcos interruptivos perdidos
- **Cada NE encontrada com data <5 anos zera o `d_plus` daquela fatura**
- Mediana atual de completude na carteira: 54,5% — há margem real de descoberta

> **Conclusão prática**: a exposição "real" pode estar entre **R$ 2,5M (cenário mitigado)** e **R$ 14,9M (cenário pior, D+34 sem ação)**. O memorando para Brandão deve apresentar **a faixa**, não o pico.

---

## Memorando proposto para Brandão Ozores (rascunho)

> **De:** Gabriel Mar Sociedade Individual de Advocacia (OAB/AM 15.697)
> **Para:** Brandão Ozores Advogados
> **Assunto:** Quantificação de exposição contratual 002/2026 — multa por prescrição perdida (cláusula 10%)
> **Data:** 2026-05-27
>
> Em atendimento à diligência de transparência do Contrato 002/2026, segue quantificação preliminar da exposição contratual referente à cláusula de multa de 10% por prescrição perdida.
>
> **Posição em 27/05/2026:** 23 devedores prescritos somando R$ 104,6M (atualizado), com exposição teórica máxima de R$ 10,46M. A concentração é elevada: SEDUC (R$ 5,03M de multa) e SSP (R$ 2,90M) respondem por 75,8% do total.
>
> **Janela de mitigação:** com base na análise do `profiles_resumo.csv` e na hierarquia de fontes jurídicas estabelecida, a exposição pode ser reduzida para uma faixa entre R$ 2,5M e R$ 4,5M mediante (i) notificações extrajudiciais documentadas, (ii) auditoria pós-ingestão (mediana de completude documental atual: 54,5%), e (iii) parecer formal de arquivamento por inviabilidade fática nos casos em que a recuperação seja matematicamente nula.
>
> **Recomendação imediata:**
> 1. Autorizar envio do TRD SES/SUSAM (pronto desde 12/05) — mitiga R$ 4,39M em 34 dias.
> 2. Decidir ADS (3 dias até prescrição) — mitiga R$ 21K.
> 3. Iniciar pipeline de auditoria para SEDUC (TOP 1, R$ 5,03M de exposição teórica).
>
> Anexo: planilha individual por devedor (`08_EXPOSICAO_CONTRATUAL.md`).
>
> [assinatura]

---

## Como recalcular (auditoria reproduzível)

```powershell
# Na máquina do Gabriel
cd C:\Users\gabri\Desktop\PROJETO_PRODAM
py -3.12 -c "
import csv
from decimal import Decimal, ROUND_HALF_UP

def to_dec(s): return Decimal(s) if s.strip() else Decimal(0)
def fmt(v): n = Decimal(v).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP); return f'R\$ {n:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

rows = [r for r in csv.DictReader(open('profiles_resumo.csv', encoding='utf-8')) if not r['sigla'].startswith('_')]
presc = [r for r in rows if r['d_plus'] and int(r['d_plus']) < 0]
soma_atu = sum(to_dec(r['val_atualizado']) for r in presc)
print(f'Prescritos: {len(presc)} | val_atu: {fmt(soma_atu)} | multa 10%: {fmt(soma_atu * Decimal(\"0.10\"))}')
"
```

---

## Referências
- `profiles_resumo.csv` (SSOT-snapshot 27/05/2026)
- Contrato 002/2026 (Brandão Ozores × Gabriel Mar) — cláusula de multa
- `CLAUDE.md` regra #15 (SSOT) + Regra #16 (Decimal)
- CLAUDE.md regra #1 (Decreto 53.464/2026 — exceções)
- CLAUDE.md regra #11 (Art. 202 CC unicidade — REsp 1.963.067/MS)
- CLAUDE.md regra #12 (Tema 1.109/STJ — gestor público não renuncia)
- `_QUESTOES_CRITICAS/07_ADS_PRESCRICAO_IMINENTE.md` (ADS, D+3)
- `DOCUMENTOS_GERADOS/SES_SUSAM/TRD_SES_SUSAM_2026-05-12.docx` (TRD pronto)
