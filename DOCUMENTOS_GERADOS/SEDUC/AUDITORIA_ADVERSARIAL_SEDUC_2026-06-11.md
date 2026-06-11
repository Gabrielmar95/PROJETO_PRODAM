# Auditoria Adversarial — SEDUC (simulação de defesa PGE/AM) · 2026-06-11
**Agent:** `adversarial-meta-auditor` · **Peças:** memorial preliminar, ficha executiva, auditoria de bases (+ dossiê e parecer do revisor como contexto).
**Veredito:** **BLOQUEADA_FUROS_CRITICOS para uso externo** (TRD/notificação/peça) · **APTA como material interno** da apresentação de 12/06 (autodeclarada preliminar, com ressalvas).

## Furos CRÍTICOS
| # | Furo | Argumento da defesa | Réplica hoje | Neutralização |
|---|---|---|---|---|
| C1 | **Dies a quo da mora** sobre vencimentos estimados | Sem termo certo provado → mora *ex persona* (Art. 397 § ún. CC), juros só da citação (Art. 405) — ataca os R$ 6,9M de acréscimo e a liquidez | Fraca: correção pura é devida da exigibilidade; prática de pagamento ~30d (taxa histórica 75,14%) | RUNBOOK Passo 1 (vencimentos reais do DB) + cláusulas de prazo; cálculo bifásico se preciso. **Ressalva 8 adicionada ao memorial** |
| C2 | **Regime SELIC presumido, 0 contratos PDF** | Iliquidez; sem contrato, nem a obrigação-base está demonstrada | Taxa legal supletiva (arts. 389/406 CC) declarando recálculo se houver cláusula | RUNBOOK Passos 2-4 + 7.2; prioridade CT 14/2018; faltantes → Ofício LAI |
| C3 | **Sem atesto/NL** — defesa nega o fato gerador | Cadeia REsp 793.969 incompleta em 3 dos 4 elos; NF é unilateral | Rota monitória + SPCF/NEs/pagamentos parciais como começo de prova | Ofício interno de atestos (modelo CT 8/2021) |
| C4 | **2 "Parcialmente Paga" pelo bruto** (ids 141565, 156790 = R$ 2,83M) | Cobrança de valor já pago → repetição em dobro (Art. 940 CC) + descrédito do cálculo | Cenário Conservador já as exclui; Ressalva 6 manda abater | Extrato SPCF das 2 faturas; checar se o "parcial" é retenção tributária (ver M5) |
| C5 | **Vigência contratual estourada** — CT 14/2018 cobrado até comp. 12/2025 (8º ano), CT 54/2017 até 07/2023, sem TAs mapeados | Sem contrato vigente → causa de pedir vira enriquecimento sem causa, sem encargos contratuais; atinge R$ 19,8M | **Nenhuma documentada** (furo não ressalvado antes desta auditoria) | RUNBOOK Passo 4 (filtrar `tipo=TA` dos CTs 14/2018 e 54/2017) + 7.2; mapear vigência ANTES de qualquer peça. **Ressalva 9 adicionada ao memorial; risco 2 da ficha** |

## Furos ALTOS
- **A1 — 4 universos, não 2**: além de 84 e 106, o profile embutido registra 120 em aberto (R$ 60,1M) e 136 devidas (R$ 56,0M) + 36 canceladas (R$ 13,8M). Neutralizar com conciliação id-a-id no DB real e prova de que as 8 "prescritas" do snapshot não estão entre as 106.
- **A2 — Of. 316/2020 citado, não lido**: se contiver glosa técnica fundamentada, o caso muda de inadimplência para disputa de mérito; "prestou ciente da recusa" atinge a boa-fé das competências 2023-26 dos CTs pré-2020. Localizar e ler (RUNBOOK 7.4).
- **A3 — NE como reconhecimento tácito**: NE é ato orçamentário prévio à despesa (Lei 4.320/64); sem vinculação NE↔fatura a tese é frágil, e a interrupção é única (REsp 1.963.067/MS) — não desperdiçar com marco fraco. Posição atual correta (corroborativo; Tier 2 = 0). **Ressalva 10 adicionada.**
- **A4 — Decreto 53.464/2026**: 4 exceções não conferidas; ler o decreto antes da TRD e documentar o enquadramento.
- **A5 — Buracos de competência** (CT 23/2021: salto 12/2023→09/2025; CT 14/2018: 11/2023→01/2025): preparar a narrativa pago×glosado×cancelado antes que a defesa imponha a dela.

## Furos MÉDIOS
M1 fator mensal sem pro-rata + cache 04/2026 (conservador; pro-rata em memorial pericial) · M2 nota bifásica pré/pós-Lei 14.905 para vencimentos < 30/08/2024 · M3 higiene do profile (floats, `multa: "1%"` contraditória) — corrigir no SSOT vivo · M4 fatura sem cobrança (106×105) · M5 retenções na fonte (ISS/IR) não analisadas — pode explicar os 2 "parciais".

## OK confirmados
Anti-alucinação (nenhuma citação fabricada/distorcida; sem 1%/dia, sem Lei 3.683/2012, sem 60 SM) · legitimidade (CNPJ ativo, GOV_DIRETA → monitória + precatório) · prescrição do universo atual (1ª em 30/06/2028, contagem por fatura/aniversário) · Regra 9 (SELIC única) · escalation TRD→monitória · transparência interna (tarja, presumido, estimados, cenários).

## Ordem de prioridade adversarial para o RUNBOOK (hoje à noite)
1. Passo 1 — vencimentos reais (mata C1) · 2. Passos 2-4 + 7.2 — contratos-base **e TAs** do CT 14/2018 (mata C2/C5) · 3. Extrato ids 141565/156790 (mata C4) · 4. Passo 7.4 — Of. 316/2020 (desarma A2) · 5. Ofício de atestos (ataca C3). **Sem esses cinco, nem TRD.**
