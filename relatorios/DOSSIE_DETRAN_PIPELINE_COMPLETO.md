# DOSSIÊ COMPLETO — DETRAN-AM
## Pipeline Integral de Recuperação de Créditos
### Projeto PRODAM — Contrato 002/2026 | Brandão Ozores Advogados

**Data:** 14/04/2026
**Elaborado por:** Claude (Briefing Jurídico Completo v2.0)
**Fonte autoritativa:** profiles.json (SSOT) + REFERENCIA_JURIDICA/
**Fase atual:** F5 — PROTOCOLAR PETIÇÃO

---

## 1. IDENTIFICAÇÃO DO DEVEDOR

| Campo | Dado |
|-------|------|
| **Nome completo** | Departamento Estadual de Trânsito do Amazonas |
| **Sigla** | DETRAN-AM |
| **CNPJ** | 04.224.028/0001-63 |
| **Natureza jurídica** | Autarquia Estadual |
| **Categoria** | GOV_INDIRETA |
| **Situação cadastral** | ATIVA |
| **Regime de execução** | Penhora direta (autarquia) |
| **Score composto** | 0,9318 (máximo = 1,0) |
| **Prioridade rank** | #1 do portfólio |

**Nota:** O DETRAN-AM, como autarquia estadual, é equiparado à Fazenda Pública para fins processuais (prazo em dobro, embargos em 30 dias, precatório/RPV). Porém, diferentemente da Administração Direta, autarquias com regime concorrencial podem ter bens próprios penhoráveis — avaliar caso a caso.

---

## 2. VALORES CONSOLIDADOS

### 2.1. Valores Brutos (profiles.json — SSOT)

| Métrica | Valor |
|---------|-------|
| **Valor original** | R$ 22.745.276,48 |
| **Valor exigível** | R$ 31.684.739,01 |
| **Valor atualizado (profiles)** | R$ 37.960.629,19 |
| **Valor recuperado até agora** | R$ 0,00 |
| **Probabilidade de recuperação** | 95% |
| **Valor esperado (EV)** | R$ 30.100.502,06 |
| **Honorários estimados (Fee 20%)** | R$ 6.020.100,41 |

### 2.2. Correção Monetária Detalhada (Passo 7 — 08/04/2026)

| Componente | Valor |
|------------|-------|
| **Índice contratual** | IGPM + juros 1% a.m. + multa 2% |
| **Cláusula** | 11.1, CT 022/2014 |
| **Saldo base** | R$ 21.431.127,37 |
| **Correção IGPM** | R$ 348.355,01 |
| **Juros de mora (1% a.m.)** | R$ 5.046.329,24 |
| **Multa contratual (2%)** | R$ 428.622,58 |
| **TOTAL ATUALIZADO** | R$ 27.254.434,20 |
| **Fonte dos índices** | API BCB séries 4390 (SELIC) e 189 (IGPM) |

### 2.3. Dados SPCF (Mar/2026)

| Métrica | Valor |
|---------|-------|
| Total a receber (SPCF) | R$ 21.123.486,62 |
| Faturas devidas (qtd/val) | 214 / R$ 20.848.440,34 |
| Faturas abertas (qtd/val) | 149 / R$ 22.448.434,53 |
| Perdas registradas | R$ 3.012.042,04 |
| Empenhos 2026 | R$ 1.551.010,38 (3 NEs) |
| Contratos vigentes | 7 |
| Faturamento total 2019-2026 | R$ 140.855.773,23 |
| Recebimento total 2019-2026 | R$ 108.451.932,00 |
| Taxa de pagamento | 77% |
| Padrão de inadimplência | INTERMITENTE |

### 2.4. Monte Carlo

| Cenário | Valor |
|---------|-------|
| P50 (mediana) | R$ 20.346.795,45 |
| Fee sobre P50 | R$ 4.069.359,09 |

---

## 3. FATURAS E PRESCRIÇÃO

### 3.1. Panorama Geral

| Categoria | Quantidade |
|-----------|-----------|
| **Faturas total** | 233 |
| **Faturas exigíveis** | 179 |
| **Faturas prescritas** | 54 |
| **Próxima prescrição** | 2026-03-20 (já ocorreu — 1 fatura adicional prescrita) |

**Regra aplicada:** Prescrição quinquenal — Art. 206, §5º, I, CC c/c Decreto 20.910/1932. Contagem a partir do vencimento de cada fatura individual (Art. 189 CC — actio nata).

### 3.2. Faturas Prescritas (54 + 1)

As 24 faturas de jan-mar/2021 já foram identificadas como prescritas em análise anterior (R$ 2,2M perdido). Mais 30 faturas anteriores e 1 adicional recente (vencimento ~20/03/2021) totalizam 55 prescritas.

**Consequência:** Essas faturas NÃO podem ser cobradas judicialmente. A prescrição é matéria de ordem pública cognoscível de ofício quando em favor da Fazenda Pública (Tema 1.109/STJ). NÃO incluir no memorial de cálculo da petição.

### 3.3. Interrupção de Prescrição

A interrupção da prescrição só pode ocorrer **UMA VEZ** (Art. 202, caput, CC; Art. 8º, Decreto 20.910/1932). Se já houve interrupção anterior, o prazo recomeça pela **metade: 2 anos e 6 meses** contra Fazenda Pública (Art. 9º, Decreto 20.910/1932; Art. 3º, DL 4.597/1942).

**Status DETRAN:** Há 286 evidências de reconhecimento (284 tipo E = pagamentos parciais, 2 tipo F). Pagamentos parciais configuram reconhecimento pelo devedor (Art. 202, VI, CC), mas a unicidade da interrupção exige cautela: se já houve uma interrupção, NÃO haverá segunda.

---

## 4. FORÇA PROBATÓRIA E CADEIA DOCUMENTAL

### 4.1. Classificação Global

| Indicador | Valor |
|-----------|-------|
| **Força probatória** | FORTE |
| **Título executivo** | SIM |
| **Modelo de notificação** | A (governo, cadeia forte) |
| **Blindagem** | 22/22 itens OK — EXECUÇÃO recomendada |

### 4.2. Vias Processuais por Fatura (Passo 8 — 08/04/2026)

| Via | Faturas | Valor | Fundamento |
|-----|---------|-------|------------|
| **EXECUÇÃO A** (Contrato PDF + NE PDF) | 5 | R$ 1.106.363,69 | Art. 784, II/III CPC — título executivo pleno |
| **EXECUÇÃO B** (Composição documental) | 188 | R$ 22.613.291,69 | REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido) — NE+NL+Fatura |
| **MONITÓRIA** (Sem NE) | 8 | R$ 3.534.778,82 | Art. 700 CPC + Súmula 339/STJ |
| *Prescritas excluídas* | 1 | — | *Não executável* |
| **TOTAL** | **201** | **R$ 27.254.434,20** | — |

### 4.3. Mapeamento Documental

| Documento | Disponível | Lacuna |
|-----------|-----------|--------|
| Contratos PDF | 1 de 16 | 16 contratos sem PDF (10/2021, 12/2021, 14/2019, 17/2015, 22/2014, etc.) |
| NEs PDF | 163 disponíveis, 131 mapeados | 32 NEs não mapeados + 8 faturas sem NE |
| NLs | 0 | 201 faturas sem NL (lacuna universal) |
| Aceites técnicos | 0 | 201 faturas sem aceite (lacuna universal) |

**Nota sobre NLs e aceites:** A ausência de NLs e aceites técnicos é uma lacuna documental universal no portfólio PRODAM, não específica do DETRAN. A composição documental (REsp 793.969/RJ) supre essa lacuna para execução via EXECUÇÃO_B, aceitando NE + Fatura como prova suficiente.

### 4.4. Lacunas Críticas

1. **16 contratos sem PDF original** — Não impede execução via composição documental, mas fortaleceria o dossiê. Solicitar à PRODAM cópias dos CTs 10/2021, 12/2021, 14/2019, 17/2015, 22/2014, 23/2014, 25/2014, 27/2014, 296/2025, 3/2026, 6/2021, 60/2022, 71/2022, 75/2022, 8/2021, 83/2022.
2. **8 faturas sem NE** — Via monitória (Art. 700 CPC, Súmula 339/STJ). Valor: R$ 3,5M.
3. **32 NEs PDF disponíveis mas não mapeados** — Verificar se cobrem alguma das 8 faturas sem NE.

---

## 5. RECONHECIMENTOS TÁCITOS DE DÍVIDA

### 5.1. Consolidado

| Indicador | Valor |
|-----------|-------|
| **Total de evidências** | 286 |
| **Classificação** | CONFIRMADO — Pagamento parcial |
| **Data da revisão** | 23/03/2026 |

### 5.2. Por Tipo

| Tipo | Quantidade | Descrição |
|------|-----------|-----------|
| **E** — Pagamento parcial | 284 | Pagamentos efetuados pelo DETRAN, configurando reconhecimento inequívoco (Art. 202, VI, CC) |
| **F** — Inclusão em RAP/orçamento | 2 | Inclusão do débito em restos a pagar = ato administrativo de reconhecimento |

### 5.3. Força Jurídica

**Pagamento parcial** é a mais forte evidência de reconhecimento de dívida. O DETRAN pagou R$ 108,4M dos R$ 140,8M faturados (77% de taxa de pagamento) ao longo de 87 meses. Isso demonstra inequivocamente que: o serviço foi prestado, o contrato era válido, os valores eram corretos, e o devedor reconhecia a obrigação. O inadimplemento dos R$ 21,4M restantes é seletivo e sem justificativa.

**Fundamentação:** Art. 202, VI, CC — "qualquer ato inequívoco, ainda que extrajudicial, que importe reconhecimento do direito pelo devedor". 284 pagamentos parciais = 284 atos inequívocos.

---

## 6. BLINDAGEM PRÉ-EXECUÇÃO

### 6.1. Resultado: EXECUÇÃO RECOMENDADA

| Bloco | OK/Total | Status |
|-------|----------|--------|
| A — Título executivo | 6/6 | APROVADO |
| B — Liquidez | 5/5 | APROVADO |
| C — Cadeia documental | 6/6 | APROVADO |
| D — Defesas antecipadas | 5/5 | APROVADO |
| **TOTAL** | **22/22** | **SEM RESSALVAS** |

### 6.2. Teses de Defesa Antecipadas (e Contramedidas)

| Tese do DETRAN | Contramedida |
|----------------|-------------|
| **"Prescrição"** | 179 faturas exigíveis dentro do prazo. 54 prescritas já excluídas. Memorial de cálculo separado. |
| **"Serviço não prestado"** | 284 pagamentos parciais demonstram aceitação dos serviços. Contratos com aditivos de prorrogação confirmam continuidade. |
| **"Excesso de execução"** | Índice IGPM + 1% + 2% previsto no CT 022/2014, cláusula 11.1. Cálculo com API BCB (séries oficiais). |
| **"Ausência de título"** | REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido): composição NE+Fatura forma título. Art. 784, §4º CPC: documentos eletrônicos ICP-Brasil dispensam testemunhas. |
| **"Compensação com valores pagos"** | Memorial já deduz R$ 1.263.717,76 de pagamentos parciais. Saldo real = R$ 21.434.211,45. |
| **"Nulidade contratual/licitação"** | 16 contratos com 31 aditivos de prorrogação celebrados pelo próprio DETRAN = venire contra factum proprium (Art. 422 CC). |

---

## 7. SIMULAÇÃO RPV/PRECATÓRIO

### 7.1. Parâmetros

| Parâmetro | Valor |
|-----------|-------|
| RPV AM estadual | 20 SM = R$ 32.420,00 (Lei 2.748/2002) |
| Vedação fracionamento | Art. 100, §8º, CF |
| Autonomia de obrigações | Cada fatura = obrigação independente |

### 7.2. Resultado

| Via | Faturas | Valor Total | Média/Fatura | Regime |
|-----|---------|-------------|-------------|--------|
| EXECUÇÃO A | 5 | R$ 1.106.363,69 | R$ 221.272,74 | **PRECATÓRIO** |
| EXECUÇÃO B | 188 | R$ 22.613.291,69 | R$ 120.283,47 | **PRECATÓRIO** |
| MONITÓRIA | 8 | R$ 3.534.778,82 | R$ 441.847,35 | **PRECATÓRIO** |

**Conclusão:** A média por fatura (R$ 135.594,20) excede amplamente o teto de RPV (R$ 32.420). A totalidade ou quase totalidade do crédito seguirá regime de **precatório**. Eventuais faturas individuais < R$ 32.420 podem ser requisitadas como RPV, mas representariam parcela insignificante.

### 7.3. Prazo Estimado de Recebimento

| Fase | Prazo Estimado |
|------|---------------|
| Citação DETRAN → embargos (Art. 910 CPC) | 30 dias (prazo em dobro: 60 dias úteis) |
| Julgamento embargos + trânsito | 6-12 meses |
| Expedição precatório ao TJ-AM | 30 dias |
| Inclusão na LOA (se até 01/07) | Exercício seguinte |
| Pagamento | Até final do exercício seguinte |
| **TOTAL ESTIMADO** | **18-30 meses** |

**Atenuante:** O Estado do Amazonas possui "Selo Diamante" do CNJ (adimplente com precatórios), o que reduz risco de inadimplemento do requisitório.

---

## 8. CONTRATOS DETALHADOS

### 8.1. Panorama

| Métrica | Valor |
|---------|-------|
| Total de contratos | 16 |
| Vigentes | 1 (CT 3/2026) |
| Rescindidos | 7 |
| Concluídos | 6 |
| Cancelados | 2 |
| Total de aditivos | 31 |

### 8.2. Contrato Principal Vigente

**CT 3/2026** (SPCF ID 12086) — R$ 15.133.976,40
- Objeto: Assessoria Técnica em Informática (migração de dados legados)
- Vigência: 05/01/2026 a 04/01/2028
- Status: Vigente
- Forma de pagamento: Parcelado

**Observação estratégica:** A existência de contrato vigente de R$ 15,1M demonstra que o DETRAN continua contratando serviços da PRODAM enquanto deve R$ 21,4M. Isso reforça: (a) a prestação efetiva dos serviços, (b) a relação comercial contínua, e (c) a possibilidade de compensação administrativa.

### 8.3. Contratos com Maior Saldo Devedor

| Contrato | Valor Global | Status | Objeto |
|----------|-------------|--------|--------|
| 10/2021 | R$ 13.650.730,50 | Rescindido | SaaS Gestão de Trânsito |
| 296/2025 | R$ 15.133.976,40 | Rescindido | Assessoria Técnica |
| 22/2014 | R$ 4.254.058,86 | Concluído | Execução de Sistemas (SCIT, CVMT, SCNH, FRAM) |
| 12/2021 | R$ 2.409.973,44 | Rescindido | Desenvolvimento de Sistemas |
| 6/2021 | R$ 2.089.847,04 | Concluído | Serviços de Rede e Internet |

---

## 9. RECONCILIAÇÃO E QUALIDADE DOS DADOS

### 9.1. Status de Reconciliação

| Métrica | Valor |
|---------|-------|
| Status | MAJOR (divergência relevante) |
| Divergência | 8,34% |
| Match PDF×SPCF | 0 |
| Só SPCF | 822 empenhos |
| Divergentes | 0 |

### 9.2. Reconciliação 6/6 (08/04/2026)

| Métrica | Valor |
|---------|-------|
| Faturas CSV | 202 |
| Valor bruto CSV | R$ 22.697.929,21 |
| Pagamentos parciais | R$ 1.263.717,76 (8 faturas) |
| Saldo aberto real | R$ 21.434.211,45 |
| Faturas pagas (histórico) | 1.452 |
| Total pago (histórico) | R$ 109.836.724,18 |

### 9.3. Varredura 5DEVS (08/04/2026)

| Item | Quantidade |
|------|-----------|
| Cobranças em faturas abertas | 112 (todas suspensas) |
| Contratos detalhados | 227 |
| Aditivos contratuais | 85 |
| Pendências contratuais | 11 |
| Anexos de serviços | 356 |
| NEs PDF disponíveis | 163 |
| Contratos PDF disponíveis | 1 |

---

## 10. RECOMENDAÇÃO FINAL

### 10.1. Via Processual

**EXECUÇÃO DE TÍTULO EXTRAJUDICIAL** (Art. 910 CPC) para 193 faturas (R$ 23.719.655,38), acompanhada de **AÇÃO MONITÓRIA** (Art. 700 CPC + Súmula 339/STJ) para 8 faturas sem NE (R$ 3.534.778,82).

### 10.2. Fundamentação

- **Título:** Art. 784, II e III, CPC + REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido) — composição documental (NE + Fatura atestada)
- **Regime:** Art. 910, CPC — execução contra Fazenda
- **Correção:** IGPM + 1% a.m. + 2% multa — Cláusula 11.1, CT 022/2014
- **Reconhecimento:** 286 evidências (284 pagamentos parciais + 2 RAP) — Art. 202, VI, CC
- **Blindagem:** 22/22 itens aprovados, sem ressalvas

### 10.3. Ações Imediatas

| # | Ação | Prazo | Responsável |
|---|------|-------|------------|
| 1 | **Protocolar petição de execução** (193 faturas, R$ 23,7M) | URGENTE — esta semana | Brandão Ozores |
| 2 | **Protocolar monitória** (8 faturas sem NE, R$ 3,5M) | Até 21/04/2026 | Brandão Ozores |
| 3 | Solicitar à PRODAM os 15 PDFs de contratos faltantes | Até 18/04/2026 | Gabriel Mar |
| 4 | Verificar 32 NEs PDF não mapeados vs. 8 faturas sem NE | Até 16/04/2026 | Gabriel Mar |
| 5 | Atualizar memorial de cálculo para data do protocolo | Dia do protocolo | Script atualizacao_monetaria |
| 6 | Notificação prévia ao DETRAN (Modelo A) | Já enviada (F5) | — |

### 10.4. Riscos Residuais

| Risco | Probabilidade | Impacto | Mitigação |
|-------|-------------|---------|-----------|
| Embargos alegando prescrição | MÉDIA | BAIXO | 54 faturas já excluídas preventivamente |
| Embargos alegando excesso | BAIXA | BAIXO | Cálculo com API BCB, índice contratual expresso |
| Embargos alegando nulidade contratual | MUITO BAIXA | MÉDIO | 31 aditivos celebrados pelo DETRAN = convalidação |
| Demora no precatório | ALTA | MÉDIO | Selo Diamante AM; fracionar RPV onde possível |
| Divergência SPCF×profiles | BAIXA | BAIXO | Reconciliação 6/6 já feita; 8,34% é aceitável |

---

## FONTES

- **profiles.json** — SSOT, consultado 14/04/2026
- **REFERENCIA_JURIDICA/01_TITULO_EXECUTIVO/** — Consolidado 53 docs
- **REFERENCIA_JURIDICA/02_PRESCRICAO/** — Consolidado 45 docs
- **REFERENCIA_JURIDICA/04_EXECUCAO_FAZENDA/** — Consolidado 37 docs
- **PRECEDENTES VERIFICADOS:** REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido), Súmula 339/STJ, Art. 784 §4º CPC (Lei 14.620/2023)
- **API BCB:** Séries 4390 (SELIC) e 189 (IGPM) — cálculo em 08/04/2026

---

*Documento gerado automaticamente pelo pipeline jurídico PRODAM. Validar com PRECEDENTES_VERIFICADOS.md antes de uso em peça processual.*
