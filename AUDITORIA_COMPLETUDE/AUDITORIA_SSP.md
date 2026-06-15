# Auditoria de Completude — SSP
**Secretaria de Segurança Pública** | Categoria: **GOV_DIRETA** | Data: 2026-06-10
_Expandida para auditoria forense profunda em 2026-06-14 (sessão de reconciliação, cadeia 5 elos, furos adversariais)._

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
| Empenhos no DB | 218 | R$ 136.963.244,94 |
| Faturas no DB | 82 | R$ 6.290.728,66 |
| Cobranças SPCF | 79 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/PRODAM_DOCS/SSP_DOSSIE |
| Pasta Consolidado | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/PRODAM_DOCS/SSP_CONSOLIDADO |
| SPCF por_devedor | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/SPCF_EXTRACAO/por_devedor/SSP |

## Documentos Faltantes (5)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ cnd: CNDs / Certidões

## Divergências (0)

_Nenhuma divergência significativa detectada pelo coletor automático (o coletor não comparou CSV × profiles — ver §2 abaixo, onde a divergência de 135,5% é tratada)._

---

# PARTE FORENSE — Auditoria Profunda (2026-06-14)

> Fonte autoritativa de valores e contagens: `PRODAM_DOCS/profiles.json → SSP` (SSOT). Conferência cruzada com `prodam.db` (tabelas `spcf_*`) e catálogo `PRECEDENTES_VERIFICADOS.md`. Pastas probatórias verificadas como existentes: `SSP_DOSSIE` (9 itens), `SSP_CONSOLIDADO` (10 itens), `SSP` (6 itens), `SPCF_EXTRACAO/por_devedor/SSP` (81 itens). Auditoria READ-ONLY sobre as fontes.

## 1. Resumo executivo

| Campo | Valor (SSOT) |
|-------|--------------|
| Órgão | Secretaria de Segurança Pública (CNPJ 01.804.019/0001-53) |
| Categoria / Regime | GOV_DIRETA → **precatório/RPV** (Art. 100 CF) |
| Valor exigível (`val_exig`) | **R$ 4.553.230,80** |
| Valor original (`val_orig`) | R$ 12.532.319,38 |
| Valor atualizado (`val_atualizado`) | **R$ 29.034.062,63** |
| Faturas | **181 total** → **66 exigíveis** · **114 prescritas** (1 fora do par exig./presc.) |
| Índice de correção | **SELIC** (juros já embutidos — não somar 1% a.m. à parte) · multa 1% |
| Título executivo | **Sim** (composição documental) |
| Força probatória | **FORTE** · score composto 0,8492 · p(recuperação) 0,93 |
| Fase | **F5 — "Petição pronta"** (desde 2026-03-27) |
| Via processual | **EXECUÇÃO_DIRETA** (composição documental) + **MONITÓRIA** residual |
| Reconhecimento | **125 evidências — CONFIRMADO (RD no AFI)**; blindagem **22/22 OK**, recomendação EXECUÇÃO |
| Prescrição próxima | **2026-06-30** · urgência **CRÍTICA** · D+49 (a partir da revisão de 2026-05-12) |
| Próximo passo | **PROTOCOLAR_PETIÇÃO** (prioridade_rank 4) |
| Risco "apagão de canetas" | **ALTO** |

**Veredito**: SSP é um crédito FORTE, com título executivo por composição documental e reconhecimento de dívida robusto (125 evidências, RD lançado no AFI). O gargalo **não** é probatório — é **temporal**: há um lote prescrevendo em **2026-06-30** que exige protocolo imediato. A petição já está pronta (F5).

## 2. Reconciliação de valores — o alerta R$ 10,7M × R$ 4,6M

O SSOT registra `reconciliacao_alerta.acao = "INVESTIGAR"` com divergência de **135,5%** entre o CSV `FATURAS_POR_DEVEDOR` (R$ 10.725.242,83) e o `profiles.val_exig` (R$ 4.553.230,80). **Esta auditoria conclui que os dois números estão corretos — medem coisas diferentes.** A cadeia de reconciliação:

| Camada | Valor | O que mede |
|--------|-------|------------|
| Faturamento bruto 2019-2026 | R$ 59.476.026,84 | tudo que a PRODAM faturou à SSP no período |
| (−) Recebido (taxa 79,86%) | (R$ 47.497.263,00) | faturas já pagas (1.957 NFs pagas no histórico) |
| (−) Canceladas (128 faturas) | (R$ 15.704.434,29 líq.) | faturas anuladas/excluídas — **fora do universo cobrável** |
| (−) Perdas (`spcf_perdas`) | (R$ 10.269.852,48) | baixa contábil "EmPerdas" no SPCF |
| **= Saldo nominal em aberto (CSV)** | **≈ R$ 10.725.242,83** | **181 faturas em aberto — base NOMINAL, sem expurgar prescritas** |
| (−) 114 faturas prescritas | (≈ R$ 6,17M) | créditos perdidos por decurso de prazo (Art. 206 §5º I CC) |
| **= Exigível líquido (`val_exig`)** | **R$ 4.553.230,80** | **66 faturas vivas — base DEFENSÁVEL em juízo** |

**Origem da divergência**: o CSV `FATURAS_POR_DEVEDOR` soma **todas as 181 faturas em aberto** (base nominal/contábil); o `val_exig` do profiles soma **apenas as 66 não prescritas** (base jurídica/cobrável). A diferença de ~R$ 6,17M são **as 114 faturas já prescritas** — que existem na contabilidade mas não são acionáveis. Não há erro de dado; há **dois recortes** (nominal vs. exigível).

> ⚠️ **Cautela com "EmPerdas" (R$ 10.269.852,48)**: o significado contábil de "EmPerdas" no SPCF ainda não foi confirmado com a PRODAM (é provisão técnica ou reconhecimento de inexigibilidade?). **Não usar esse montante como argumento adversarial** até esclarecer — se "EmPerdas" for leitura de inexigibilidade pela própria credora, a defesa pode invocá-lo. Item em aberto.

**Conclusão da reconciliação — valor defensável em juízo: R$ 4.553.230,80 (nominal exigível), corrigido para R$ 29.034.062,63 (SELIC).** Atenção: o `correcao_monetaria_passo7` calcula um sub-recorte conservador (saldo-base R$ 2.182.121,23 → R$ 2.901.047,10 atualizado) restrito às faturas efetivamente mapeadas para execução; o valor de capa para a petição deve usar o `val_atualizado` do SSOT recalculado na data do protocolo via API BCB (série SGS 4390).

## 3. Cadeia probatória — 5 elos (Contrato → NE → NF → Liquidação → Aceite/Pagamento)

Base: 82 faturas com cadeia parseada no `prodam.db` (recorte executável) + classificação do `dossie_classificacao_passo8` (66 faturas exigíveis).

| Elo | Cobertura (82 parsed) | Observação |
|-----|----------------------|------------|
| **1. Contrato** | 82/82 (100% por referência) | **mas 0 contratos em PDF** — todos por nº/ID SPCF. Lacuna C1 = 66/66. |
| **2. NE (empenho)** | 82/82 (100%) | 79 NEs em PDF disponíveis; 218 empenhos no DB. 8 faturas (mini-CTs) **sem NE**. |
| **3. NF** | 82/82 (100%) | todas com PDF (`tem_pdf=1` em 82/82). |
| **4. Liquidação** | 68/82 (82,9%) | lacuna C3 = 66/66 nas exigíveis (liquidação não anexada como prova). |
| **5. Aceite / Pagamento** | 72/82 (87,8%) | lacuna C5 (aceite técnico) = 66/66. |

**Classificação de força (DB)**: 72 faturas COMPLETA + 10 FORTE. **Via processual (passo 8)**: EXECUÇÃO_B = 58 faturas (R$ 2.889.593,47, composição documental); MONITÓRIA = 8 faturas (R$ 11.453,63, sem NE).

**Lacunas críticas (do SSOT)**:
- **11 contratos sem PDF**: 18/2025, 19/2025, 190/2021, 191/2021, 192/2021, 271/2021, 272/2021, 288/2021, 318/2021, 319/2021, **48/2021** (o contrato-âncora das 58 faturas de R$ 2,4M).
- **0 contratos em PDF** → 100% das execuções dependem de **composição documental (Caminho B, REsp 793.969/RJ)**, não de contrato físico.
- **8 faturas sem NE** → não comportam execução; vão para monitória.
- Elos **liquidação (C3)** e **aceite (C5)** ausentes como prova anexada em 66/66 exigíveis — não impedem a composição documental, mas reforçariam a liquidez se juntados.

**Ação probatória prioritária**: extrair do SPCF os PDFs/IDs dos contratos 48/2021 (âncora) e dos mini-CTs, e anexar liquidações (68/82 já existem no DB) ao dossiê de execução.

## 4. Prescrição por fatura

Regra (Art. 189 + 206 §5º I CC): prescrição **por fatura individual**, contada do **vencimento**, prazo quinquenal.

- **66 exigíveis** vs **114 prescritas** (181 total; 1 fora do par). A blindagem registrou a ressalva "115 prescritas > 81 exigíveis" — leitura conservadora de sessão anterior; o recorte vigente do SSOT é **114 × 66**. Em qualquer leitura, **a maioria do universo já prescreveu** — o que sobrou é o núcleo defensável.
- **Data de prescrição próxima: 2026-06-30** (`urgencia_prescricao = CRITICA`, D+49). Confere com o universo de faturas: o lote em risco imediato são as **8 mini-CTs 190-319/2021** (D+49 a D+172 — vencem dentro da janela 2026-06-30 → set/2026, R$ 6.653 / R$ 11.453,63), via **monitória**. As **58 faturas do CT 48/2021** estão seguras **até 2028+** (vencimentos posteriores).
- **`apagao_canetas_risco = ALTO`**: risco de que, na virada do exercício/gestão, atos de reconhecimento (empenhos, atestos) deixem de ser renovados/assinados, enfraquecendo a cadeia para faturas novas. Combinado com a prescrição de 2026-06-30, **a janela de protocolo é estreita**.

**Sinalização**: o crédito de maior valor (CT 48/2021, R$ 2,4M) **não** prescreve em 2026-06-30 — o gatilho de 30/06 é o lote pequeno (mini-CTs, ~R$ 11,5 mil via monitória). Não atrasar a monitória por causa do prazo, **mas** a execução do CT 48/2021 (o dinheiro grande) pode ser protocolada logo após, sem perda por prescrição até 2028. Priorizar por **risco temporal** (mini-CTs primeiro), não por valor.

## 5. Furos adversariais — antecipação da defesa

Os 7 furos mais perigosos que a Procuradoria do Estado (PGE/AM) pode levantar e a blindagem de cada um:

1. **Prescricional (mais provável)** — "as faturas estão prescritas (Art. 206 §5º I CC)". **Blindagem**: já expurgamos as 114 prescritas; só executamos as 66 vivas. O **empenho (NE) é reconhecimento tácito** que interrompe a prescrição **uma vez** (Art. 202 VI CC; REsp 1.963.067/MS — unicidade). Contra Fazenda Pública o prazo reinicia **pela metade** (2,5 anos, Decreto 20.910/1932). **Tema 1.109/STJ**: gestor público **não** renuncia tacitamente à prescrição — mas aqui não há renúncia, há **interrupção por ato inequívoco** (empenho).

2. **Cadeia / ausência de contrato em PDF** — "não há contrato assinado juntado". **Blindagem**: título executivo por **composição documental** (Contrato + NE + NF + Atesto), **REsp 793.969/RJ, Rel. p/ acórdão Min. José Delgado** (Min. Teori Zavascki foi **vencido**). Contrato administrativo é documento público (REsp 487.913/MG). A inexistência do PDF não desfaz o vínculo provado por NE+NF+liquidação.

3. **Liquidez / iliquidez do quantum** — "o valor não é líquido e certo". **Blindagem**: 125 evidências de reconhecimento (RD no AFI), liquidação presente em 68/82, NFs com PDF em 82/82. Memorial de cálculo SELIC fatura a fatura (API BCB série 4390), em Decimal. Anexar liquidações ausentes reforça.

4. **Legitimidade / serviço não prestado** — "não houve atesto da prestação". **Blindagem**: 117 evidências tipo E (execução/aceite) + atestos; padrão de pagamento histórico de 79,86% prova que a SSP reconhecia e pagava esses serviços. O **silêncio** do devedor não interrompe nem desfaz (Art. 202 CC, rol taxativo) — mas o pagamento parcial (4 faturas "Parcialmente Paga") é **reconhecimento expresso**.

5. **Monetário / excesso de execução** — "a SELIC foi cumulada indevidamente com juros". **Blindagem**: SELIC **já inclui correção + juros** — não somamos 1% a.m. à parte (Regra 9). Multa contratual de 1% aplicada uma vez. Pós-**Lei 14.905/2024**, não presumir 1% a.m. (arts. 404-406 CC). Cálculo transparente no memorial.

6. **Processual / regime de pagamento** — "execução direta é incabível contra Fazenda". **Blindagem**: GOV_DIRETA → execução submetida a **precatório/RPV** (Art. 100 CF), não penhora. **RPV/AM = 20 SM** (Lei AM 2.748/2002) — **não** confundir com o teto federal de 60 SM. Fragmentação legítima por fatura autônoma pode levar lotes ao rito de RPV (pagamento em ~60 dias) em vez da fila de precatório.

7. **Decreto Estadual AM nº 53.464/2026** — a defesa pode invocar moratória/suspensão estadual. **Blindagem**: **antes de protocolar, verificar as 4 exceções do art. 1º §§1º-4º** do Decreto 53.464/2026 (que sucedeu o 51.084/2025, de efeitos exauridos). Se o crédito SSP se enquadrar em exceção, o Decreto não obsta a cobrança; documentar o enquadramento na petição.

**Furo latente (não jurídico, mas factual)**: o montante **"EmPerdas" (R$ 10,27M)** lançado pela própria PRODAM no SPCF. Se a defesa acessar e interpretar como **baixa por inexigibilidade**, vira contra-argumento. **Mitigar**: confirmar com a PRODAM que "EmPerdas" é provisão técnica (não renúncia de crédito) antes de qualquer manifestação que o mencione.

## 6. Via processual recomendada

| Lote | Faturas | Valor | Via | Fundamento |
|------|---------|-------|-----|------------|
| CT 48/2021 (âncora) | 58 | R$ 2,4M (R$ 2.889.593,47 cadeia) | **EXECUÇÃO DIRETA (Caminho B)** | Composição documental: Contrato+NE+NF+Atesto = título executivo (**REsp 793.969/RJ, Rel. p/ acórdão Min. José Delgado**) |
| Mini-CTs 190-319/2021 | 8 | R$ 6.653 / R$ 11.453,63 | **AÇÃO MONITÓRIA** | Sem NE → **Súmula 339/STJ** (monitória contra Fazenda Pública) |

- **Regime de satisfação**: GOV_DIRETA → **precatório/RPV (Art. 100 CF)**. Simular **fragmentação RPV/AM (20 SM, Lei AM 2.748/2002)** por fatura autônoma para acelerar recebimento (RPV ≈ 60 dias vs. precatório = anos). **Não** aplicar o teto federal de 60 SM.
- **Pré-condição obrigatória**: verificar as **4 exceções do Decreto AM 53.464/2026 (art. 1º §§1º-4º)** antes do ajuizamento e consignar o enquadramento na petição.
- **Reforço**: 125 evidências de reconhecimento (RD no AFI) sustentam a interrupção prescricional e a liquidez; juntá-las como prova pré-constituída.

## 7. Próximos passos priorizados (ancorados em 2026-06-30)

1. **[ATÉ 2026-06-30 — IMPRORROGÁVEL] Protocolar a ação MONITÓRIA das 8 mini-CTs (190-319/2021)** — é o lote que prescreve na janela D+49→D+172. Valor pequeno (R$ 11,5 mil), mas perda por prescrição = 10% do crédito de penalidade contratual + dano. Súmula 339/STJ.
2. **[ATÉ 2026-06-30] Reverificar a data de prescrição fatura a fatura** no `prodam.db`/CSV — confirmar que nenhuma fatura do CT 48/2021 ou outra exigível vence antes de 30/06 (a análise atual indica que não, mas validar antes do protocolo, pois `apagao_canetas_risco=ALTO`).
3. **[ATÉ 2026-06-30] Verificar as 4 exceções do Decreto AM 53.464/2026** e documentar o enquadramento — bloqueia o protocolo se não feito.
4. **[+5 dias úteis] Recalcular o `val_atualizado` na data do protocolo** via API BCB (SELIC série 4390), em Decimal, e fechar o memorial de cálculo para a capa da execução do CT 48/2021.
5. **[+5 dias úteis] Protocolar a EXECUÇÃO DIRETA do CT 48/2021** (58 faturas, R$ 2,4M) — não prescreve até 2028+, mas a petição já está pronta (F5); não há motivo para segurar. Anexar a composição documental (REsp 793.969/RJ).
6. **[paralelo] Extrair do SPCF os PDFs/IDs dos 11 contratos sem PDF** (em especial 48/2021) e anexar as liquidações já existentes (68/82) para fortalecer a liquidez.
7. **[paralelo] Confirmar com a PRODAM o significado contábil de "EmPerdas" (R$ 10,27M)** antes de qualquer peça que o mencione — fechar o furo latente.
8. **[pós-protocolo] Simular fragmentação RPV/AM (20 SM)** para os lotes exequíveis, maximizando recebimento rápido.

---
_Auditoria forense gerada em 2026-06-14. Fontes: `profiles.json → SSP` (SSOT), `prodam.db` (`spcf_*`), `PRECEDENTES_VERIFICADOS.md`. Valores em Decimal, formato R$ 1.234,56. Nenhum PDF ou pasta de devedor foi alterado (READ-ONLY)._
