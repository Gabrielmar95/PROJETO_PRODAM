# URGENTE — SES/SUSAM: Prescrição em 29 dias (13/05/2026)

**Data:** 14/04/2026 | **Deadline PRODAM:** 15/04/2026 (AMANHÃ)
**Escritório:** Brandão Ozores — Contrato 002/2026
**Autor:** Gabriel Mar — reconciliação multi-fonte executada em 14/04/2026
**Versão:** 2.0 (reconciliada) — substitui v1.0 que continha valores superestimados do profiles.json

---

## RESUMO EXECUTIVO (1 parágrafo)

Após reconciliação automatizada de 4 fontes SPCF (`consolidado_faturas`, `rel_faturas_aberto`, `rel_geral_faturas 2019-2026`, `cobrancas.json`), **o número real de faturas SES exigíveis é 73 — valor R$ 3.745.779,18 (bruto SPCF)**, não as 144 do `profiles.json`. Das 176 faturas classificadas como prescritas (R$ 4.567.134,92), uma parcela significativa pode ser **ressuscitada por marcos interruptivos (Art. 202 VI CC)**: há 475 empenhos SES ativos, incluindo NEs de 2025-2026 em contratos-chave (018/2021, 021/2021, 055/2018, P.254/2017), que constituem reconhecimento tácito e reiniciam a prescrição. **Ação imediata:** protocolar protesto extrajudicial das 73 exigíveis até 25/04 e, em paralelo, cruzar empenhos × faturas prescritas para recuperar valores adicionais.

---

## 1. CORREÇÃO DOS NÚMEROS — profiles.json vs fontes SPCF verificadas

### Divergência detectada

| Métrica | `profiles.json` | **Reconciliação (14/04)** | Ajuste |
|---------|-----------------|---------------------------|--------|
| Faturas exigíveis | 144 | **73** | −71 (profile superestimou ~97%) |
| Valor exigível (bruto) | R$ 14.748.048,96 | **R$ 3.745.779,18** | −R$ 11.002.269,78 |
| Faturas prescritas | 180 | 176 | −4 (coerente) |
| Faturas total universo | 324 | 1.016 (inclui pagas) | — |
| Pagas | — | 860 | — |
| Canceladas | — | 19 | — |

**Metodologia:** `ses_reconciliacao_completa.py` (raiz do projeto) cruza IDs de fatura SES com normalização (`161532` = `161532.0`), classifica cada uma por situação (Paga/Emitida/Cancelada/Parc. Paga) e aplica cutoff de prescrição `2021-04-14` (HOJE − 5 anos, Art. 206 §5º I CC).

### Por que `profiles.json` ficou inflado?

Hipóteses (que não bloqueiam a ação imediata):

1. **Dupla contagem** — `faturas_exigiveis=144` não bate com `spcf_fat_aberto_qtd=137` nem com `spcf_fat_devidas_qtd=228`. Pode ter sido contagem manual desatualizada.
2. **`val_exig=R$ 14,75M`** não aparece em nenhuma soma SPCF direta (`cobrancas.json` bruto = R$ 6,66M; `rel_faturas_aberto` tem 137 faturas somando outros valores). Possivelmente extraído de um XLS/PDF que já tinha correção monetária embutida.
3. **Campo `Corrigido` = R$ 0,00 para 110/110 faturas** — mesmo bug de scraper relatado para DETRAN (113/113). Valor corrigido precisa ser calculado por `atualizacao-monetaria-sob-demanda` com SELIC.

**Impacto prático:** o valor atualizado final (com SELIC desde o vencimento) tende a ser ~1,7–2× maior que o bruto. R$ 3,75M × 1,7 (fator SELIC aproximado 2021-2026) ≈ R$ 6,37M atualizados. Não os R$ 14,75M do profile, mas ainda relevante.

---

## 2. AS 73 FATURAS EXIGÍVEIS — CADEIA COMPLETA

### Distribuição por origem documental

| Fonte | Qtd | Observação |
|-------|-----|------------|
| Em DB (cobrança ativa SPCF) | 47 | Cadeia documental mapeada; 5-elos classificada |
| Em `rel_faturas_aberto` **sem** DB | 26 | Faturas 2024-2026 ainda não integradas (delta do scraper) |
| Só em `rel_geral` (Emitida sem cobrança ativa) | 0 | Após dedup ID, nenhuma resta nesta categoria |
| **TOTAL** | **73** | **R$ 3.745.779,18** |

### Distribuição por contrato (exigíveis)

| Contrato | Qtd | Valor exigível (bruto) | NE mais recente (prodam.db) | Marco interruptivo |
|----------|-----|------------------------|-----------------------------|--------------------|
| 018/2021 | 36 | R$ 1.568.591,96 | 31/10/2025 | **SIM — Art.202 VI** |
| 021/2021 | 20 | R$ 1.262.467,17 | 31/03/2026 | **SIM — Art.202 VI** |
| 018/2024 | 2 | R$ 292.024,70 | 30/04/2025 | SIM (contrato novo) |
| 054/2018 | 2 | R$ 222.113,52 | 29/09/2022 | SIM |
| 074/2021 | 3 | R$ 220.019,73 | investigar | — |
| 005/2021 | 10 | R$ 180.562,10 | 30/09/2021 | marco fraco (5m após cutoff) |
| Demais | 0 | 0 | vários | — |

> **Subtotal 2 contratos dominantes (018/2021 + 021/2021):** 56 de 73 exigíveis = 77% | R$ 2.831.059,13 = 76% do valor

### Top 10 exigíveis por valor (deduplicados)

| ID | Contrato | Comp. | Valor | Fontes |
|----|----------|-------|-------|--------|
| 161532 | 018/2021 | 07/2025 | R$ 185.399,50 | DB+GERAL+ABERTO |
| 127265 | 054/2018 | 09/2021 | R$ 165.777,43 | ABERTO |
| 163045 | 021/2021 | 09/2025 | R$ 160.469,55 | DB+GERAL+ABERTO |
| 163914 | 021/2021 | 10/2025 | R$ 160.469,55 | DB+GERAL+ABERTO |
| 166662 | 021/2021 | 02/2026 | R$ 160.469,55 | ABERTO |
| 167205 | 021/2021 | 03/2026 | R$ 158.160,62 | ABERTO |
| 166730 | 018/2024 | 02/2026 | R$ 146.012,35 | ABERTO |
| 167245 | 018/2024 | 03/2026 | R$ 146.012,35 | ABERTO |
| 166733 | 018/2021 | 02/2026 | R$ 114.100,00 | ABERTO |
| 167274 | 018/2021 | 03/2026 | R$ 114.100,00 | ABERTO |

---

## 3. AS 176 PRESCRITAS — RESGATÁVEIS POR MARCOS INTERRUPTIVOS

### Base legal

**Art. 202 VI CC:** "A interrupção da prescrição [...] por qualquer ato inequívoco, ainda que extrajudicial, que importe reconhecimento do direito pelo devedor."

**Jurisprudência consolidada:** empenho (NE) configura reconhecimento tácito da dívida contratual. Se há NE emitida **após** o vencimento da fatura, a prescrição foi interrompida e reinicia-se do zero (Art. 202 caput — interrupção única, reinicia metade = 2,5 anos para Fazenda Pública pelo Decreto 20.910/1932).

### Contratos SES com NEs recentes → PRESCRITAS RESGATÁVEIS

Fonte: `prodam.db/spcf_empenhos` (475 NEs SES ativas, R$ 107.076.806,49).

| Contrato | Último NE | Data | Valor NE | Efeito |
|----------|-----------|------|----------|--------|
| 021/2021 | 2026NE0001323 | **31/03/2026** | R$ 289.705,28 | Reset prescrição de TUDO anterior |
| 002/2015 | (vários 2026) | 13-20/03/2026 | ~R$ 1,57M total | 20 faturas antigas RESSUSCITADAS |
| 055/2018 | 2026NE0001079 | 16/03/2026 | R$ 154.015,81 | Reset prescrição |
| P.254/2017 | 2026NE0001375 | 08/04/2026 | R$ 73.266,06 | 1 fatura RESSUSCITADA |
| 018/2021 | 2025NE0006464 | 31/10/2025 | R$ 545.307,06 | Reset prescrição |
| 018/2024 | 2025NE0002172 | 30/04/2025 | R$ 146.012,35 | Contrato novo |
| 054/2018 | 2022NE0004104 | 29/09/2022 | R$ 146.012,35 | Prescritas anteriores RESSUSCITADAS até 29/09/2027 |
| 005/2021 | 2021NE0003457 | 30/09/2021 | R$ 34.245,60 | Marco fraco (5m pós-cutoff) |

### Contratos SES SEM NE recente → PRESCRIÇÃO CONSUMADA

| Contrato | Último NE | Prescrito desde | Faturas no consolidado |
|----------|-----------|-----------------|------------------------|
| 116/2013 | 30/07/2015 | 30/07/2020 | 14 faturas |
| 081/2010 | 29/09/2014 | 29/09/2019 | 4 faturas |
| 052/2008, 051/2008 | 30/06/2014 | 30/06/2019 | — |
| 024/2016 | 01/04/2016 | 01/04/2021 | 2 faturas |
| P.248/2016 | 14/12/2017 | 14/12/2022 | 16 faturas |
| P.125/2016 | 14/12/2017 | 14/12/2022 | 5 faturas |

> **Conclusão probabilística:** das 176 prescritas, **100+ são resgatáveis** via NE recente. Rodar `marcos-interruptivos-prescricao` + `validador-cadeia-documental-fatura` fatura-a-fatura para confirmação definitiva.

---

## 4. O QUE SIGNIFICA A DATA 13/05/2026

O `profiles.json` marca `data_prescricao_proxima = 2026-05-13` com observação "Of. 129/2021 expira ~13/05/2026".

### Interpretação jurídica correta

| Elemento | Classificação | Interrompe prescrição? |
|----------|---------------|------------------------|
| Ofício 129/2021 (PRODAM → SES) | Cobrança do credor | **NÃO** (Art. 202 CC taxativo: cobrança não é causa) |
| Resposta da SES ao Ofício (se houver) | Ato do devedor | **SIM** se contiver reconhecimento (Art. 202 VI) |
| Empenho (NE) da SES | Ato unilateral do devedor | **SIM** (Art. 202 VI — reconhecimento tácito) |

> **13/05/2026 NÃO é data de prescrição de faturas.** É uma estimativa derivada da expiração de 5 anos do Of.129/2021. **A real data de prescrição depende de cada fatura individualmente**, contada do vencimento (Art. 206 §5º I CC). Já há muitas faturas prescritas antes dessa data; e já há marcos interruptivos posteriores via NE.

### Faturas com prescrição iminente (D+ 0-90 dias) — foco real

Filtro: `venc_est` entre `2026-04-14` (hoje) e `2026-07-13` (HOJE+90). Serão faturas com competências **04-06/2021** (venc. ~05-07/2021 → prescrição ~05-07/2026). **Essas devem ser protestadas PRIMEIRO.**

Comando:
```bash
py -3.12 -c "import json; d=json.load(open('ses_reconciliacao.json',encoding='utf-8')); \
  ur=[e for e in d['exigiveis'] if e.get('venc_estimado') and '2026-04-14' <= e['venc_estimado'] <= '2026-07-13']; \
  print(f'Faturas iminentes: {len(ur)}'); [print(e) for e in ur]"
```

---

## 5. AÇÃO IMEDIATA — ORDEM DE PRIORIDADE

### PRIORIDADE 1 — HOJE/AMANHÃ (14-15/04)

- [ ] Validar este relatório com escritório Brandão Ozores
- [ ] **Decisão binária:** aguardar resposta PRODAM ao Of.129/2021 (até 15/04) OU agir independente
- [ ] Executar `py -3.12 ses_reconciliacao_completa.py` para gerar dataset atualizado (feito)
- [ ] Filtrar faturas com `venc_est` ≤ 2026-07-13 → subset de emergência

### PRIORIDADE 2 — ESTA SEMANA (16-18/04)

- [ ] Rodar `marcos-interruptivos-prescricao` para cada fatura das 176 prescritas
- [ ] Rodar `atualizacao-monetaria-sob-demanda` (SELIC) para valores atualizados
- [ ] Gerar memorial de cálculo por fatura (`antigravity-prodam:xlsx-official`)
- [ ] **Corrigir `profiles.json`:** `faturas_exigiveis: 73`, `val_exig: 3745779.18`

### PRIORIDADE 3 — SEMANA 2 (21-25/04)

- [ ] **Protocolar protesto extrajudicial** das 73 exigíveis em 2 lotes:
   - Lote A: 47 faturas com cadeia em DB (pronto para protesto)
   - Lote B: 26 faturas de `rel_faturas_aberto` (integrar ao DB primeiro via `integracao-dados-novos-spcf`)
- [ ] Preparar petição de execução subsidiária (blindagem Art.784 + cadeia 5-elos) — skill `blindagem-pre-execucao`
- [ ] Notificar SES por TRD das 176 prescritas resgatáveis por NE

### PRIORIDADE 4 — SEMANA 3 (28/04-02/05)

- [ ] Validar protestos protocolados (certidão de registro)
- [ ] Ajuizar execução/monitória se protesto for sustado
- [ ] Atualizar dashboard PRODAM com números corretos

### PRIORIDADE 5 — SEMANA 4 (05-09/05) — ÚLTIMA ANTES DE 13/05

- [ ] Revisão final — todas faturas em risco protegidas?
- [ ] Protocolo backup: petição judicial como garantia (caso protesto não registre)
- [ ] Verificação em 08/05 (D-5)

---

## 6. CENÁRIOS FINANCEIROS (dados reais)

| Cenário | Faturas | Valor bruto | Valor atualizado¹ | Honorários 20% |
|---------|---------|-------------|-------------------|----------------|
| Nenhuma ação | 0 | R$ 0 | R$ 0 | R$ 0 |
| **Exigíveis apenas (73)** | 73 | R$ 3.745.779,18 | ~R$ 6.367.824,61 | **~R$ 1.273.564,92** |
| Exigíveis + 50% prescritas resgatáveis | ~161 | R$ 6.029.346,64 | ~R$ 10.249.889,29 | ~R$ 2.049.977,86 |
| Exigíveis + 100% prescritas resgatáveis | 249 | R$ 8.312.914,10 | ~R$ 14.131.953,97 | ~R$ 2.826.390,79 |

¹ Fator SELIC aproximado 1,7× para período 2021-2026 — calcular exato com `atualizacao-monetaria-sob-demanda`

---

## 7. PERGUNTAS QUE PRECISAM DE RESPOSTA

1. **PRODAM respondeu ao Ofício 129/2021?** Se sim, contém reconhecimento tácito (Art. 202 VI)?
2. **As 228 "faturas devidas" (`spcf_fat_devidas_qtd=228`) coincidem com quais?** Rodar reconciliação com `rel_fat_devidas_*.xlsx`.
3. **Há faturas SES pré-2019 fora do `rel_geral`?** Verificar em PDFs do pendrive (`SES_DOSSIE/`).
4. **Contratos 116/2013, 081/2010, P.248/2016, P.125/2016** — houve transação/reconhecimento depois da última NE? Verificar evidências de cobrança.

---

## 8. ARQUIVOS GERADOS POR ESTA ANÁLISE

| Arquivo | Conteúdo |
|---------|----------|
| `ses_reconciliacao_completa.py` | Script reexecutável — fonte única da verdade |
| `ses_reconciliacao.json` | Dataset completo com 1.016 faturas classificadas |
| `ses_reconciliacao.csv` | Planilha UTF-8 BOM para Excel/import |
| `ses_reconciliacao_summary.md` | Sumário automático gerado pelo script |
| `atualizar_db.py` | Wrapper de rebuild do `prodam.db` (na raiz) |
| `ses_susam_faturas_cruzamento.json` | (legado — análise anterior) |
| `ses_susam_exigiveis_drill.json` | (legado — 47+27 da análise anterior) |

---

## 9. SKILLS E FRAMEWORKS UTILIZADOS

- `prodam-juridico` — orquestração desta análise
- `analise-prescricao-creditos` — cutoff 2021-04-14, classificação por vencimento
- `marcos-interruptivos-prescricao` — Art. 202 VI CC aplicado a NEs 2021+
- `validador-cadeia-documental-fatura` — 5 elos (Contrato → NE → NL → NF → Aceite)
- `reconhecimento-divida-tacito` — empenho como reconhecimento tácito
- `atualizacao-monetaria-sob-demanda` — SELIC (rodar antes do protesto)
- `proximo-passo-advisor` — escolha de via (protesto → execução → monitória)

---

## 10. REPRODUTIBILIDADE — COMO VALIDAR ESTE RELATÓRIO

```bash
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"

# Regenerar prodam.db a partir dos JSONs SPCF
py -3.12 atualizar_db.py

# Executar reconciliação
py -3.12 ses_reconciliacao_completa.py

# Verificar resultados
cat ses_reconciliacao_summary.md
```

**Integridade (gerado em 14/04/2026):**
- Universo deduplicado: 1.016 faturas únicas (após normalização de ID)
- Classificação: 73 exigíveis + 176 prescritas + 860 pagas + 19 canceladas = 1.128 classificações (faturas com competência ambígua em múltiplas classes: 112)
- Cruzamento: `prodam.db/spcf_faturas` (110 SES) × `spcf_empenhos` (475 SES)
- Totais: R$ 3.745.779,18 exigível (bruto) + R$ 4.567.134,92 prescrito (resgatável parcial)

---

**FIM DO RELATÓRIO — v2.0 (reconciliada, 14/04/2026 13:15)**
**Próxima revisão:** após resposta PRODAM ao Of.129/2021 (até 15/04/2026)
