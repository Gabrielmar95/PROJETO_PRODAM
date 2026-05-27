# Triagem do lote `d_plus=-20` — 22 órgãos, R$ 75,6M atualizado

**Status:** ready-for-human (decisão de Gabriel por grupo)
**Aberto em:** 2026-05-27
**Decisor:** Gabriel Mar
**Fonte:** `profiles_resumo.csv` (snapshot 27/05/2026)
**Plano-mãe:** Janela 1, item 1.4

---

## TL;DR

Em vez de tratar 22 devedores prescritos individualmente, este documento **agrupa por causa raiz + valor + via processual** em 5 GRUPOS DE AÇÃO. Cada grupo tem um plano coletivo (com custo, benefício esperado e gate jurídico).

- **Grupo A (TIER 1, 4 devs, R$ 63,8M)** — tratamento individual ainda assim (volume justifica)
- **Grupo B (Gov Indireta TIER 2, 3 devs, R$ 3,8M)** — notificação extrajudicial coletiva
- **Grupo C (Gov Direta TIER 2, 2 devs, R$ 3,5M)** — parecer precatório/RPV
- **Grupo D (TIER 3+4, 9 devs, R$ 4,3M)** — notificação padronizada por similaridade
- **Grupo E (TIER 5 cauda longa, 4 devs, R$ 174K)** — parecer de inviabilidade + arquivamento

---

## 🔴 ACHADOS-CHAVE antes da triagem

### Achado 1 — d_plus uniforme = carimbo, não data real
**Todos os 22 têm exatamente `d_plus = -20`**. Estatisticamente impossível se fosse data real de prescrição (cada fatura tem vencimento próprio). É **marca-d'água da Rota B de 12/05 ou triagem de 07/05** (27/05 − 20 dias = 07/05/2026).

**Implicação**: `d_plus` reflete **detecção** ("eu identifiquei prescrição nesse devedor há 20 dias"), não prescrição efetiva por fatura. Re-execução do pipeline `orgao_pipeline_completa.py --orgao <X>` pode revelar faturas prescritas há +5 anos OU faturas com marco interruptivo (Art. 202 VI CC) ainda vigentes.

### Achado 2 — 8 devedores com `proximo_passo` contraditório
Devedores marcados como `ENVIAR_TRD` ou `PROTOCOLAR_PETICAO` mas com `urg_presc=PRESCRITA`:

| Sigla | Categoria | proximo_passo | val_atualizado |
|---|---|---|---:|
| SEAD | GOV_DIRETA | ENVIAR_TRD | R$ 4.296.278,76 |
| FCECON | GOV_INDIRETA | ENVIAR_TRD | R$ 828.620,63 |
| IDAM | GOV_INDIRETA | ENVIAR_TRD | R$ 892.277,93 |
| FMT | GOV_INDIRETA | ENVIAR_TRD | R$ 693.107,38 |
| CBMAM | GOV_DIRETA | ENVIAR_TRD | R$ 71.483,16 |
| FHEMOAM | GOV_INDIRETA | ENVIAR_TRD | R$ 13.276,75 |
| FUAM/FUHAM | GOV_INDIRETA | PROTOCOLAR_PETICAO | R$ 356.355,07 |
| FHAJ | GOV_INDIRETA | PROTOCOLAR_PETICAO | R$ 493.519,13 |

Hipóteses:
- **H1**: o `proximo_passo` foi definido ANTES do recálculo de prescrição em 07/05; ficou stale
- **H2**: esses 8 órgãos têm marcos interruptivos potenciais (NEs, aceites) que não foram contabilizados no `d_plus` — TRD/peça ainda viável
- **H3**: erro de pipeline (campo `proximo_passo` não foi atualizado em batch)

**Ação preliminar:** rodar `orgao_pipeline_completa.py` para esses 8 antes de marcar como perda. Custo: ~10h total no agregado. Ganho potencial se H2 for verdadeiro: até R$ 7,64M reabertos.

### Achado 3 — Concentração extrema no TIER 1
4 devedores (SEDUC, SEJUSC, SEAD, SEDECTI) = R$ 63,8M = **84,4% do lote** (atualizado). Os outros 18 somam R$ 11,8M = 15,6%.

**Implicação**: a "triagem coletiva" só faz sentido para os 18 da cauda. Os 4 do topo exigem tratamento individual.

---

## Estatísticas-base do lote

| Métrica | Valor |
|---|---:|
| N devedores | 22 |
| val_exig total | R$ 61.597.386,17 |
| val_atualizado total | R$ 75.602.923,54 |
| Multa 10% potencial | R$ 7.560.292,35 |
| **Por categoria** | |
| GOV_DIRETA | 13 devs · R$ 68.499.667,11 (90,6%) |
| GOV_INDIRETA | 9 devs · R$ 7.103.256,43 (9,4%) |
| **Por força** | |
| FORTE | 7 devs · R$ 56.557.675,73 |
| MÉDIA | 11 devs · R$ 16.627.861,97 |
| FRACA | 4 devs · R$ 2.417.385,84 |

---

## GRUPO A — TIER 1 INDIVIDUAL (4 devedores, R$ 63,8M)

| Sigla | Cat | Força | proximo_passo | val_exig | val_atu | Multa 10% |
|---|---|---|---|---:|---:|---:|
| SEDUC | GOV_DIRETA | FORTE | ANALISAR_DOCUMENTACAO | R$ 49.215.512,48 | R$ 50.263.263,56 | R$ 5.026.326,36 |
| SEJUSC | GOV_DIRETA | MÉDIA | ANALISAR_DOCUMENTACAO | R$ 2.589.660,12 | R$ 5.262.537,82 | R$ 526.253,78 |
| SEAD | GOV_DIRETA | FORTE | ENVIAR_TRD ⚠️ | R$ 2.339.702,20 | R$ 4.296.278,76 | R$ 429.627,88 |
| SEDECTI | GOV_DIRETA | MÉDIA | ANALISAR_DOCUMENTACAO | R$ 1.249.203,13 | R$ 4.007.244,35 | R$ 400.724,44 |
| **TOTAL** | | | | **R$ 55.394.077,93** | **R$ 63.829.324,49** | **R$ 6.382.932,46** |

**Plano coletivo (mas execução individual):**
1. **Pipeline de ingestão completa** para os 4: `py -3.12 scripts\orgao_pipeline_completa.py --orgao <X>` — custo: 2-4h por órgão
2. **Confirmar prescrição fatura-a-fatura** via auditoria pós-ingestão — pode mover algumas faturas para "exigível" se NE encontrada
3. **Parecer individual por devedor** com gate `adversarial-meta-auditor`
4. **TRD ou notificação extrajudicial** mesmo após prescrição (mitiga inércia + abre canal)

**Roteiro por sigla:**
- **SEDUC (R$ 50,3M)**: TOP 1 da carteira. Decretar via Janela 2 do plano-mãe (rodar `orgao_pipeline_completa.py --orgao SEDUC` pré-parecer). Auditoria atual: 44%. Há `SEDUC_AUDITORIA_COMPLETA` no Desktop com PDFs não-ingeridos.
- **SEJUSC (R$ 5,3M)**: Foco em "43 NEs sem contrato" (item 9 das Decisões Pendentes do plano).
- **SEAD (R$ 4,3M)**: `proximo_passo=ENVIAR_TRD` mas prescrita — revisar coerência (Achado 2/H2). Pode ter NE recente.
- **SEDECTI (R$ 4,0M)**: Auditar 176 faturas prescritas no CSV vs. 52 exigíveis — discrepância sugere reconhecimento parcial possível.

**Gate jurídico**: cada peça gerada exige `adversarial-meta-auditor` + OK explícito.

**ETA**: 7-14 dias para os 4 (1 órgão por dia útil de execução de pipeline + 1 dia para parecer).

---

## GRUPO B — GOV_INDIRETA TIER 2 (3 devedores, R$ 3,8M)

| Sigla | Força | proximo_passo | val_exig | val_atu | Multa 10% |
|---|---|---|---:|---:|---:|
| FAAR/SEDEL | FRACA | ANALISAR_DOCUMENTACAO | R$ 734.498,94 | R$ 1.472.879,25 | R$ 147.287,93 |
| SUHAB | MÉDIA | ANALISAR_DOCUMENTACAO | R$ 840.061,15 | R$ 1.210.268,55 | R$ 121.026,86 |
| AMAZONPREV | MÉDIA | ANALISAR_DOCUMENTACAO | R$ 736.219,79 | R$ 1.142.951,74 | R$ 114.295,17 |
| **TOTAL** | | | **R$ 2.310.779,88** | **R$ 3.826.099,54** | **R$ 382.609,96** |

**Plano coletivo:**
1. **Notificação extrajudicial com AR individual** (cada uma com fundamento Tema 253/STF — penhora direta possível para Adm. Indireta)
2. **Pacote padrão**: Art. 202 II CC (protesto extrajudicial) + REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado) + Tema 1.109/STJ (gestor público não renuncia)
3. **Não rodar pipeline completo** (custo>benefício para R$ 1-1,5M cada) — confiar no CSV atual + dados Rota B
4. **Custo total estimado**: R$ 90 (3 ARs) + R$ 0 (sem protesto cartório nesta fase)
5. **Decisão posterior** de execução após resposta (ou silêncio em 30d)

**Por que GOV_INDIRETA juntas**: 
- Mesma via processual (penhora direta — Tema 253/STF)
- Sem restrição precatório
- Patrimônio próprio penhorável
- Pacote jurídico idêntico

**Gate jurídico**: notificação padronizada → `adversarial-meta-auditor` → 3 ARs em batch.

**ETA**: 3-5 dias.

---

## GRUPO C — GOV_DIRETA TIER 2 (2 devedores, R$ 3,5M)

| Sigla | Força | proximo_passo | val_exig | val_atu | Multa 10% |
|---|---|---|---:|---:|---:|
| POLÍCIA CIVIL | MÉDIA | ANALISAR_DOCUMENTACAO | R$ 960.481,71 | R$ 1.908.089,75 | R$ 190.808,98 |
| PGE | MÉDIA | ANALISAR_DOCUMENTACAO | R$ 680.239,77 | R$ 1.603.066,41 | R$ 160.306,64 |
| **TOTAL** | | | **R$ 1.640.721,48** | **R$ 3.511.156,16** | **R$ 351.115,62** |

**Plano coletivo:**
1. **Parecer de viabilidade pelo regime de precatório/RPV** (Art. 100 CF) — ANTES de qualquer ação
2. **PGE é peculiar**: é a própria Procuradoria-Geral do Estado. Notificá-la é simbólico mas pode constranger administrativamente.
3. **POLÍCIA CIVIL**: rito de precatório AM (Lei 2.748/2002, RPV = 20×SM)
4. **Atos**: parecer único de viabilidade comparada (precatório vs notificação extrajudicial) + decisão por sigla

**Gate jurídico**: parecer obrigatoriamente revisado por `adversarial-meta-auditor` (regra #1, exceções Decreto 53.464/2026).

**ETA**: 5-7 dias.

---

## GRUPO D — TIER 3+4 (9 devedores, R$ 4,3M)

| Sigla | Cat | Força | proximo_passo | val_exig | val_atu | Multa 10% |
|---|---|---|---|---:|---:|---:|
| IDAM | GOV_INDIRETA | FRACA | ENVIAR_TRD ⚠️ | R$ 328.735,51 | R$ 892.277,93 | R$ 89.227,79 |
| FCECON | GOV_INDIRETA | FORTE | ENVIAR_TRD ⚠️ | R$ 637.106,68 | R$ 828.620,63 | R$ 82.862,06 |
| FMT | GOV_INDIRETA | MÉDIA | ENVIAR_TRD ⚠️ | R$ 272.130,68 | R$ 693.107,38 | R$ 69.310,74 |
| FHAJ | GOV_INDIRETA | FORTE | PROTOCOLAR_PETICAO ⚠️ | R$ 259.910,78 | R$ 493.519,13 | R$ 49.351,91 |
| FUAM/FUHAM | GOV_INDIRETA | FORTE | PROTOCOLAR_PETICAO ⚠️ | R$ 44.020,01 | R$ 356.355,07 | R$ 35.635,51 |
| SECT | GOV_DIRETA | MÉDIA | ANALISAR_DOCUMENTACAO | R$ 258.328,58 | R$ 296.246,97 | R$ 29.624,70 |
| SEFAZ | GOV_DIRETA | MÉDIA | ANALISAR_DOCUMENTACAO | R$ 198.980,49 | R$ 283.622,83 | R$ 28.362,28 |
| SEC | GOV_DIRETA | FORTE | ANALISAR_DOCUMENTACAO | R$ 99.050,71 | R$ 248.155,42 | R$ 24.815,54 |
| SEPROR | GOV_DIRETA | MÉDIA | ANALISAR_DOCUMENTACAO | R$ 77.960,49 | R$ 170.884,10 | R$ 17.088,41 |
| **TOTAL** | | | | **R$ 2.176.223,93** | **R$ 4.262.789,46** | **R$ 426.278,95** |

**Plano coletivo:**
1. **Re-confirmar `proximo_passo` dos 5 com flag ⚠️** — IDAM, FCECON, FMT, FHAJ, FUAM/FUHAM têm `ENVIAR_TRD`/`PROTOCOLAR_PETICAO` apesar de prescritos. Rodar pipeline mini (foco em NEs).
   - **Hipótese forte**: esses 5 têm marco interruptivo recente (NE/aceite); revisão pode movê-los de PRESCRITA para EXIGÍVEL.
   - **Ganho potencial**: até R$ 3,26M reabertos
2. **Para os 4 com `ANALISAR_DOCUMENTACAO`** (SECT, SEFAZ, SEC, SEPROR): notificação padronizada coletiva (template único + 4 ARs).
3. **Custo total estimado**: 4 ARs (~R$ 120) + 5 mini-pipelines (~5h totais).

**Gate jurídico**: 
- 4 notificações genéricas → `adversarial-meta-auditor` em batch
- 5 mini-pipelines → revisão coerência → reclassificação no CSV

**ETA**: 5-7 dias (paralelo).

---

## GRUPO E — TIER 5 cauda longa (4 devedores, R$ 174K)

| Sigla | Cat | Força | proximo_passo | val_exig | val_atu | Multa 10% |
|---|---|---|---|---:|---:|---:|
| CBMAM | GOV_DIRETA | FORTE | ENVIAR_TRD ⚠️ | R$ 3.134,03 | R$ 71.483,16 | R$ 7.148,32 |
| SEMA | GOV_DIRETA | MÉDIA | ANALISAR_DOCUMENTACAO | R$ 38.541,11 | R$ 49.842,07 | R$ 4.984,21 |
| PMAM | GOV_DIRETA | FRACA | ANALISAR_DOCUMENTACAO | R$ 27.020,90 | R$ 38.951,91 | R$ 3.895,19 |
| FHEMOAM | GOV_INDIRETA | FRACA | ENVIAR_TRD ⚠️ | R$ 6.886,91 | R$ 13.276,75 | R$ 1.327,68 |
| **TOTAL** | | | | **R$ 75.582,95** | **R$ 173.553,89** | **R$ 17.355,40** |

**Plano coletivo:**
1. **Parecer de inviabilidade fática + arquivamento** — custo de recuperação > benefício esperado
2. **Justificativa por sigla**:
   - **CBMAM (R$ 71K)**: força FORTE mas val_exig baixo (R$ 3K); val_atu inflado por correção. Diligência limitada justifica arquivamento.
   - **SEMA, PMAM (R$ 89K combinado)**: cauda longa pura. Custo de notificação + AR + protesto + execução = ordem de R$ 800-2000 + tempo do advogado >> recuperação esperada (0,15-0,40 × R$ 89K = R$ 13K-36K).
   - **FHEMOAM (R$ 13K)**: caso paradigmático. Recuperação esperada = 0,15-0,35 × R$ 13K = R$ 2-5K. Custo proibitivo.
3. **MAS**: enviar notificação genérica padrão (custo R$ 30/AR) AINDA mitiga multa 10% (R$ 17K agregado). **ROI: gastar R$ 120 para mitigar R$ 17K = 142x**. Mesmo que recuperação seja zero, vale enviar o AR.

**Recomendação dual:**
- **A — Arquivar** (custo zero, exposição multa 10% mantida em R$ 17K)
- **B — Enviar 4 ARs genéricos** (custo ~R$ 120, mitiga exposição inteira)

**Gate jurídico**: parecer único de "arquivamento OU notificação genérica simbólica" — Gabriel decide A vs B.

**ETA**: 1-2 dias.

---

## Resumo financeiro — totais e custos por grupo

| Grupo | N | val_atu | Custo R$ | Multa 10% mitigável | ROI |
|---|---:|---:|---:|---:|---:|
| A (TIER 1) | 4 | R$ 63.829.324,49 | R$ 5.000+ (pipeline + parecer) | R$ 6.382.932 | ✅ obrigatório |
| B (Indireta T2) | 3 | R$ 3.826.099,54 | R$ 90 (3 ARs) | R$ 382.610 | 4.250× |
| C (Direta T2) | 2 | R$ 3.511.156,16 | R$ 500 (parecer) | R$ 351.116 | 700× |
| D (T3+T4) | 9 | R$ 4.262.789,46 | R$ 300 (5 pipelines + 4 ARs) | R$ 426.279 | 1.420× |
| E (T5 cauda) | 4 | R$ 173.553,89 | R$ 120 (4 ARs) OU R$ 0 (arquivar) | R$ 17.355 | 142× ou 0 |
| **TOTAL** | **22** | **R$ 75.602.923,54** | **~R$ 6.000** | **R$ 7.560.292** | **1.260×** |

> **A leitura**: gastando ~R$ 6.000 em ARs + pareceres, mitiga-se até R$ 7,56M de exposição. ROI agregado de 1.260×. Mesmo no cenário pior (recuperação zero), o investimento defensivo se paga.

---

## Cronograma recomendado (paralelo)

| Semana | Ação | Grupos |
|---|---|---|
| 1 (até 03/06) | Disparar ARs grupos B + D-genéricos (7 ARs) | B, D-parcial, E (opção B) |
| 1 | Iniciar pipeline SEDUC + parecer | A — SEDUC |
| 2 (até 10/06) | Mini-pipelines D-flag ⚠️ (5 órgãos) | D-parcial |
| 2 | Parecer SEJUSC + SEAD + SEDECTI | A — outros 3 |
| 2 | Parecer C (precatório vs notificação) | C |
| 3 (até 17/06) | Pareceres D (4 ARs simples + 5 reclassificações) | D |
| 3 | Decidir E (arquivar vs notificar) | E |
| 4 (até 24/06) | Consolidação + relatório quinzenal | todos |

---

## Próximas ações para Gabriel (gate-by-gate)

1. **Aprovar este plano de triagem** — "OK, triagem em grupos"
2. **Por grupo, autorizar:**
   - **A**: "OK rodar pipeline SEDUC primeiro" (item por item)
   - **B**: "OK gerar 3 notificações Gov Indireta" (batch único)
   - **C**: "OK parecer precatório PC + PGE"
   - **D**: "OK 5 mini-pipelines D-flag" + depois "OK 4 ARs SECT/SEFAZ/SEC/SEPROR"
   - **E**: "OK arquivar" OU "OK 4 ARs simbólicos"
3. **Cada peça jurídica gerada → `adversarial-meta-auditor` → você revisa → AR**

---

## Referências
- `profiles_resumo.csv` (SSOT-snapshot 27/05/2026, linhas filtradas por `d_plus=-20`)
- `_QUESTOES_CRITICAS/08_EXPOSICAO_CONTRATUAL.md` (memorando para Brandão sobre exposição agregada)
- CLAUDE.md regras #1 (Dec. 53.464/2026), #5 (precatório/penhora direta), #9 (Art. 202 VI), #11 (unicidade), #12 (Tema 1.109), #13 (REsp 793.969/RJ)
- `scripts/orgao_pipeline_completa.py` (pipeline pré-parecer)
- `.claude/agents/adversarial-meta-auditor.md` (gate obrigatório)
- `_QUESTOES_CRITICAS/07_ADS_PRESCRICAO_IMINENTE.md` (caso paradigmático: notificação após prescrição)
