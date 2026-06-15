# Auditoria de Completude — SUHAB
**Superintendência da Zona Franca de Manaus - Habitação** | Categoria: **GOV_INDIRETA** | Data: 2026-06-10

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
| Empenhos no DB | 322 | R$ 9.193.518,20 |
| Faturas no DB | 13 | R$ 364.460,14 |
| Cobranças SPCF | 13 | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/PRODAM_DOCS/SUHAB_DOSSIE |
| Pasta Consolidado | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/PRODAM_DOCS/SUHAB_CONSOLIDADO |
| SPCF por_devedor | /sessions/fervent-serene-hawking/mnt/PROJETO_PRODAM/SPCF_EXTRACAO/por_devedor/SUHAB |

## Documentos Faltantes (5)

- ❌ contrato: Pelo menos 1 contrato PDF ou ID
- ❌ nls: Notas de Liquidação
- ❌ aceites: Aceites técnicos / recibos
- ❌ oficios: Ofícios de cobrança
- ❌ cnd: CNDs / Certidões

## Divergências (0)

_Nenhuma divergência significativa detectada pelo coletor automático — porém a auditoria forense abaixo identifica divergências materiais (ver §9)._

---

# AUDITORIA FORENSE — SUHAB
_Auditor: Gabriel Mar (OAB/AM 15.697) — Contrato 002/2026 PRODAM × Brandão Ozores · Data da análise: 2026-06-14 · Fonte primária: `PRODAM_DOCS/profiles.json` (SSOT) + `prodam.db` + pastas probatórias. READ-ONLY sobre as fontes._

## 1. Resumo executivo

| Campo | Valor (SSOT) |
|---|---|
| Devedor | SUHAB — Superintendência **Estadual de Habitação** do Amazonas (ver §9 — rótulo do cadastro está errado) |
| CNPJ | 04.355.863/0001-32 |
| Categoria / natureza | GOV_INDIRETA / Superintendência (autarquia estadual) |
| Regime de execução | **Penhora direta** (Tema 253/STF) — NÃO precatório |
| Valor exigível | **R$ 840.061,15** |
| Valor original | R$ 710.644,00 |
| Valor atualizado | **R$ 1.210.268,55** (índice SELIC, juros 1% a.m., multa 1%) |
| Faturas | **123 total · 87 exigíveis · 36 prescritas** |
| Título executivo | **FALSE** (não formado) |
| Força probatória | **MÉDIA** |
| Fase | **F0** — "Análise pendente" / "Documentação fraca" (desde 2026-03-01) |
| Reconhecimento | **7 evidências — CONFIRMADO (pagamento parcial)** — tipos E×6, F×1 |
| Via processual recomendada | **PROTESTO** (aguarda procuração; 14 faturas ≈ R$135K) |
| Padrão de inadimplência | PONTUAL — taxa histórica de pagamento **84,56%** (2019-2026) |

**Leitura de 1 minuto.** A SUHAB é devedor de porte médio (R$ 840 mil exigível / R$ 1,21 mi atualizado) com um perfil incomum: **historicamente bom pagador** (84,56% de adimplência, padrão PONTUAL, último faturamento 03/2026 — relação viva). Não há título executivo formado e a documentação é classificada como fraca no SSOT, embora o `prodam.db` mostre cadeia de 5 elos COMPLETA em 12 das 13 faturas estruturadas (divergência — §9). O problema dominante **não é mérito nem prova: é tempo.** Há um bloco de faturas de 2021 sob prescrição quinquenal em que **parte já caiu** e o restante cai mês a mês, com a próxima fatura prescrevendo em **2026-06-30 (16 dias)**. A ação correta e urgente é **protesto/interrupção imediata** sobre as faturas ainda salváveis, destravando a pendência de procuração. Por ser autarquia estadual indireta sem prerrogativas concorrenciais claras, discute-se penhora direta vs. precatório (§5).

## 2. Prescrição — análise crítica (SEÇÃO PRIORITÁRIA)

### 2.1. O conflito no cadastro
O `profiles.json` traz três sinais aparentemente contraditórios sobre a SUHAB:

| Campo | Valor | Leitura literal |
|---|---|---|
| `data_prescricao_proxima` | **2026-06-30** | "ainda há prazo, falta cerca de 16 dias" |
| `urgencia_prescricao` | **PRESCRITA** | "já prescreveu" |
| `d_plus_prescricao` | **-20** | "o marco de referência já passou há 20 dias" |
| `data_prescricao_proxima_anterior_recalc20260609` | 2026-03-20 | valor anterior ao recálculo |
| `faturas_abertas_presc_estourada_recalc20260609` | **n=5; primeira=2021-06-30** | "5 faturas em aberto já prescreveram, a 1ª desde 2021" |

E o `CLAUDE.md` do projeto ainda anuncia, na seção 3, "🔴 **SUHAB**: 2026-06-30 (19 dias)".

### 2.2. Reconciliação (auditada fatura a fatura)
Reproduzi a metodologia do recalc de 2026-06-09 (`scripts/recalcular_prescricao_proxima.py`) sobre as 13 faturas estruturadas do SPCF (`cobrancas_SUHAB.json`): **prescrição = último dia do mês seguinte à competência + 5 anos** (Art. 189 + 206 §5º I CC), cenário conservador sem marcos interruptivos não registrados. Referência: hoje = 2026-06-14.

| Comp. | Contrato | NF | Valor | Prescreve em | Status (14/06/2026) |
|---|---|---|---|---:|---|
| 05/2016 | 025/2013 | 92689 | R$ 29.148,16 | **2021-06-30** | 🔴 PRESCRITA (há ~5 anos) |
| 01/2021 | 046/2021 | 122694 | R$ 33.380,89 | 2026-02-28 | 🔴 PRESCRITA |
| 02/2021 | 046/2021 | 122692 | R$ 33.380,89 | 2026-03-31 | 🔴 PRESCRITA |
| 03/2021 | 046/2021 | 123185 | R$ 33.380,89 | 2026-04-30 | 🔴 PRESCRITA |
| 04/2021 | 046/2021 | 123872 | R$ 33.380,89 | 2026-05-31 | 🔴 PRESCRITA |
| 05/2021 | 046/2021 | 124586 | R$ 33.380,89 | **2026-06-30** | 🟡 SALVÁVEL — **16 dias** |
| 06/2021 | 046/2021 | 125289 | R$ 33.380,89 | 2026-07-31 | 🟡 SALVÁVEL |
| 07/2021 | 046/2021 | 126050 | R$ 33.380,89 | 2026-08-31 | 🟡 SALVÁVEL |
| 08/2021 | 046/2021 | 126606 | R$ 33.380,89 | 2026-09-30 | 🟡 SALVÁVEL |
| 09/2021 | 046/2021 | 127412 | R$ 33.380,89 | 2026-10-31 | 🟡 SALVÁVEL |
| 10/2021 | 046/2021 | 128052 | R$ 33.380,89 | 2026-11-30 | 🟡 SALVÁVEL |
| 10/2024 | 010/2018 | 154323 | R$ 420,77 | 2029-11-30 | 🟢 SALVÁVEL (folga) |
| 01/2026 | 004/2024 | 166426 | R$ 300,88 | 2031-02-28 | 🟢 SALVÁVEL (folga) |

### 2.3. Veredito da prescrição
- **As três datas não se contradizem — descrevem coisas diferentes.** O campo `data_prescricao_proxima = 2026-06-30` está tecnicamente correto, mas significa apenas **"a próxima fatura ainda salvável a prescrever"** (a de comp. 05/2021). Ele **não** descreve a situação do bloco: `urgencia=PRESCRITA` e `d_plus=-20` estão **igualmente corretos** porque **5 faturas já em aberto cruzaram a barreira quinquenal** — a metodologia do recalc apurou exatamente `n=5; primeira=2021-06-30`, que esta auditoria reproduziu bit a bit.
- **A data "correta" depende da pergunta.** Para *"qual o prazo da próxima perda evitável?"* → **2026-06-30 (16 dias)**. Para *"o devedor já tem crédito prescrito?"* → **SIM, desde 2021** (a NF 92689) e, no bloco 2021, desde 2026-02-28. O `CLAUDE.md` que anuncia "30/06/2026 (19 dias)" como se fosse a foto completa é **enganoso** e deve ser corrigido para refletir que metade do bloco de 2021 **já caiu** (recomendação operacional em §9 e §6).
- **Quantum (sobre as 13 faturas estruturadas, base SSOT/SPCF):**
  - **Já perdido por prescrição: 5 faturas = R$ 162.671,72** (valor nominal de face) — composto por R$ 29.148,16 (comp. 05/2016, perda antiga e consolidada) + 4 faturas do bloco 2021 (comp. 01–04/2021) = R$ 133.523,56.
  - **Ainda salvável: 8 faturas = R$ 201.006,99** (nominal), das quais **R$ 166.904,45 são o "miolo" urgente** (comp. 05–10/2021, 6 faturas que prescrevem entre 30/06 e 30/11/2026) e R$ 721,65 têm folga (2024/2026).
  - Observação de escopo: estes R$ 363.678,71 são as **13 faturas estruturadas** do SPCF com cadeia mapeada. O SSOT contabiliza **123 faturas / R$ 840.061,15 exigível** no universo total; a aritmética acima é o subconjunto auditável fatura a fatura. O padrão (bloco 2021 caindo mês a mês) projeta-se sobre o restante do universo de 2021, mas só pode ser quantificado com precisão sobre as faturas estruturadas. As demais 36 faturas marcadas "prescritas" no SSOT reforçam que **a perda já é material e crescente**.
- **Ação urgente (prazo-limite 2026-06-30):** **protesto extrajudicial e/ou ato interruptivo** sobre as 6 faturas do miolo 2021 (comp. 05–10/2021, R$ 166.904,45) **antes de 30/06/2026**, a começar pela de comp. 05/2021. Cada mês de inação custa ~R$ 33,4 mil nominais. Detalhe processual em §5.

### 2.4. Caveats jurídicos da prescrição
1. **Marcos interruptivos não registrados podem mudar o quadro.** O recalc é conservador: ignora interrupções. A SUHAB tem **7 evidências de reconhecimento, classificadas como CONFIRMADO (pagamento parcial)** — e há no DB a NF 49556 (comp. 10/2024) com situação **"Parcialmente Paga"**. Pagamento parcial é **ato inequívoco de reconhecimento (Art. 202 VI CC)** e **interrompe a prescrição**, reiniciando o prazo. **Antes de declarar qualquer fatura definitivamente prescrita, é mandatório datar o último pagamento parcial / reconhecimento** e recalcular do marco. Se houver reconhecimento posterior a 2021, faturas hoje "prescritas" podem estar vivas.
2. **Unicidade e prazo pela metade (Fazenda):** interrupção ocorre uma vez (REsp 1.963.067/MS); contra a Fazenda Pública, reinicia **pela metade** = 2,5 anos (Decreto 20.910/1932). Atenção ao aplicar à autarquia (§5).
3. **Tema 1.109/STJ:** gestor público não renuncia tacitamente à prescrição — não presumir renúncia a partir do silêncio da SUHAB.
4. **Prescrição fulmina cobrança judicial E extrajudicial** (REsp 2.088.100/SP, Rel. Min. Nancy Andrighi — princípio da indiferença das vias): faturas prescritas **não** podem nem ser protestadas. Logo o protesto deve mirar **somente** as 8 salváveis.

## 3. Cadeia probatória (5 elos) — por que título executivo = FALSE

A composição documental que forma título executivo extrajudicial contra ente público segue **REsp 793.969/RJ** (1ª Turma, **Rel. p/ acórdão Min. José Delgado** — Min. Teori Zavascki foi **vencido**): **Contrato + Nota de Empenho + Nota Fiscal + Atesto/aceite**, com 2 testemunhas para enquadrar no Art. 784 III CPC.

**Estado dos 5 elos na SUHAB:**

| Elo | Situação documental | Observação |
|---|---|---|
| 1. Contrato | ⚠️ Parcial | `n_contratos=1` no SSOT; `prodam.db` referencia contratos 046/2021, 025/2013, 010/2018, 004/2024 etc., mas pasta `01_CONTRATOS/` do consolidado está **vazia (0 PDFs)**. Há **número** de contrato, falta o **instrumento assinado**. |
| 2. Nota de Empenho (NE) | ✅ Forte | 322 empenhos "Ativo" no DB (R$ 9,19 mi); pasta `02_EMPENHOS/` vazia (0 PDFs), mas dados estruturados robustos. Empenho = reconhecimento tácito (Art. 202 VI CC). |
| 3. Nota Fiscal (NF) | ✅ OK | 8 NFS-e em PDF + dados no DB. **Mas NF emitida pelo credor NÃO interrompe prescrição** (exige ato do devedor). |
| 4. Nota de Liquidação (NL) | ❌ Faltando (PDF) | Checklist e inventário: 0 NLs em PDF. Porém o DB marca `liquidacao=true` em 12/13 faturas — **divergência (§9)**: o dado de liquidação existe na base estruturada, falta o documento probatório digitalizado. |
| 5. Atesto / Aceite / Pagamento | ⚠️ Parcial | 2 Relatórios/Aceites em PDF; DB marca `pagamento=true` em 11/13. Pagamento parcial confirmado (reconhecimento). |

**Diagnóstico.** O título executivo é FALSE porque a cadeia, embora **rica em dados estruturados** (DB mostra 12 faturas com 5 elos lógicos COMPLETOS), **carece dos instrumentos físicos** dos elos 1 (contrato assinado) e 4 (NL) e do atesto formal com testemunhas. É uma cadeia **"forte no banco, fraca no dossiê"** — o que falta é **digitalização/anexação de documentos que provavelmente existem** (contrato, NL, atesto), não a inexistência do crédito. Por isso a fase é F0 "documentação fraca" mas a força é MÉDIA (não FRACA): há lastro, falta acabamento probatório.

**O que falta para formar título executivo:**
1. Contrato(s) assinado(s) — recuperar PDF de 046/2021 (núcleo do crédito 2021) junto à PRODAM/SPCF.
2. Notas de Liquidação dos empenhos vinculados (existem no fluxo orçamentário — solicitar à SEFAZ/SUHAB).
3. Atesto/recibo de prestação de serviço com 2 testemunhas (REsp 541.267/RJ — testemunhas podem assinar após formação do ato).
4. Datar o(s) pagamento(s) parcial(is) — serve duplamente: reconhecimento (Art. 202 VI) e prova de execução do contrato.

## 4. Furos adversariais — antecipação da defesa e blindagem

| # | Eixo | Tese provável da SUHAB | Blindagem PRODAM |
|---|---|---|---|
| **1** | **Prescricional (tese central)** | "As faturas de 2021 e a de 2016 estão prescritas (Art. 206 §5º I CC); a cobrança é inexigível, inclusive extrajudicialmente (REsp 2.088.100/SP)." | **Furo real e parcialmente procedente.** Reconhecer a perda das faturas já estouradas (não insistir nelas — protestá-las seria abuso, REsp 2.088.100/SP) e **concentrar fogo nas 8 salváveis com interrupção imediata**. Reativar prazo via **pagamento parcial documentado** (Art. 202 VI CC) e marcos interruptivos. Tema 1.109/STJ: silêncio da SUHAB não é renúncia, mas também não a beneficia. |
| **2** | **Cadeia documental** | "Falta contrato assinado, NL e atesto — não há título executivo (Art. 784 CPC)." | Verdadeiro hoje. Suprir os 3 documentos (§3) **antes** de qualquer execução; enquanto não suprido, **via monitória** (Súmula 339/STJ) com a prova documental existente (NE+NF+pagamento parcial), que dispensa título executivo. |
| **3** | **Reconhecimento / venire** | (a favor da PRODAM) — | **Blindagem ativa:** SUHAB pagou ~84,56% historicamente e fez **pagamento parcial** → legítima expectativa e vedação ao *venire contra factum proprium* (REsp 836.495/RS; REsp 1.143.216/RS, repetitivo Min. Luiz Fux). As próprias **Cartas Circulares da DIRAF/DAF-GEFIN da SUHAB** (2024/2025) reconhecem as faturas devidas. |
| **4** | **Regulatório — Decreto AM 53.464/2026** | "O art. 1º, II, **'e'** veda pagamento de despesas de **exercícios anteriores a 2025** — o Estado está proibido de pagar as faturas de 2016 e 2021." | **Furo regulatório forte sobre o passivo antigo.** O Decreto (vigente até 31/12/2026) realmente veda pagar 2016/2021. **Mas:** (i) atinge faturas que em larga medida **já estão prescritas** (perda dupla, reforça abandonar 2016 e bloco 01-04/2021); (ii) **não atinge** as faturas de **10/2024 e 01/2026** (exercícios 2024/2025+); (iii) examinar as **4 exceções dos §§1º-4º** — recursos vinculados/convênios/SUS/Fundos (§1º), contrato que economize/incremente arrecadação com aval do Comitê (§2º). Serviço de TI da PRODAM tende a se enquadrar como despesa de custeio essencial; mapear a fonte orçamentária da SUHAB. O Decreto é argumento de **timing de pagamento**, não de **inexistência do crédito** — o crédito sobrevive ao decreto (vence em 31/12/2026); a cobrança/protesto preserva o direito até a vedação expirar. |
| **5** | **Legitimidade / sucessão** | "Autarquia estadual com regime próprio; cobrança deve seguir rito de Fazenda Pública (precatório), não penhora direta." | Discutir natureza (§5). Se reconhecida prerrogativa de Fazenda, migrar para compensação administrativa / monitória → precatório/RPV; se concorrencial, penhora direta (Tema 253/STF). Não é furo fatal, é furo de **via**. |
| **6** | **Monetário** | "Correção/juros aplicados a maior; SELIC não cumula com 1% a.m." | Atenção: **SELIC já embute juros + correção — não somar 1% a.m. por cima** (Regra 9). O SSOT registra "SELIC + 1% a.m. + multa 1%", o que pode gerar bis in idem se SELIC for o índice. **Revisar a memória de cálculo** antes de protocolar (gerar memorial com `atualizacao-monetaria-sob-demanda`); pós-Lei 14.905/2024 não presumir 1% a.m. |
| **7** | **Processual — protesto** | "Falta procuração; protesto de título privado contra ente público é indevido." | Procuração é pendência **interna** (resolver já — §6). Protesto contra ente público é **admitido** (REsp 1.686.659/SP; ADI 5.135/DF — protesto de CDA constitucional, por analogia). Protestar **apenas** faturas não prescritas (furo #1). |
| **8** | **Tributário / cancelamentos** | "Há 32 faturas canceladas (R$ 110,5 mil) e R$ 555,3 mil em 'EmPerdas' no SPCF — o crédito não é líquido e certo." | Segregar: as 32 canceladas (R$ 107,1 mil líquido) **saem do universo exigível** — não cobrar. Sobre "EmPerdas" (R$ 555,3 mil): **não usar como argumento e não tratar como inexigível sem confirmar com a PRODAM** se é provisão técnica contábil ou reconhecimento de inexigibilidade (pendência aberta do projeto). O exigível auditado (R$ 840.061,15) já deve excluir canceladas. |

## 5. Via processual

**Natureza e regime.** SUHAB é **autarquia estadual de habitação** (Administração Indireta, GOV_INDIRETA no SSOT). O ponto a decidir é se goza de prerrogativas de Fazenda Pública (impenhorabilidade → precatório/RPV) ou se, por atuar em regime contratual/não-concorrencial de serviço público, comporta penhora direta.

- **Posição do SSOT:** `regime_execucao = penhora_direta` (Tema 253/STF — RE 599.628). O Tema 253 afasta prerrogativas para entidades que atuam em **regime concorrencial**. **Cautela:** autarquia de habitação não é tipicamente concorrencial; o precedente **AgInt no REsp 2.092.441/DF** (1ª Turma, Min. Paulo Sérgio Domingues, 03/11/2025) submete EP de **serviço público essencial, não concorrencial, sem lucro** ao **regime de precatórios** — e diverge da regra geral do projeto. **Recomendação:** tratar a penhora direta como hipótese **a confirmar**, não como certeza; se a SUHAB for reconhecida como Fazenda, a execução desemboca em **precatório/RPV** (RPV/AM = 20 × SM, Lei AM 2.748/2002 — fatura de ~R$ 33,4 mil cabe em RPV, pagamento em ~60 dias, evitando fila de precatório).

**Medida imediata — PROTESTO (interrupção):** independente do desfecho execução vs. precatório, o passo urgente é **protesto extrajudicial** das faturas salváveis para **interromper a prescrição** antes de 30/06/2026 (admitido contra ente público — REsp 1.686.659/SP; ADI 5.135/DF). Protestar **só** as 8 não prescritas (REsp 2.088.100/SP veda protestar prescritas). Pendência: **procuração** (`via_processual_recomendada.fundamentacao = "Aguarda procuração, 14 faturas R$135K"`) — destravar com a PRODAM em regime de urgência.

**Via de cobrança do mérito (alternativas, por força da cadeia):**
- **Monitória (Súmula 339/STJ)** — recomendada enquanto o título não estiver formado: aproveita NE+NF+pagamento parcial sem exigir título executivo; converte-se em título judicial.
- **Execução de título extrajudicial** — só após suprir contrato assinado + NL + atesto c/ testemunhas (§3).
- **Compensação administrativa** (via Tesouro/TCE-AM) — rota natural para ente da Administração estadual, contornando inclusive a vedação de pagamento do Decreto 53.464 (que é sobre *pagamento direto*, não sobre *compensação/retenção de repasses*).

**Decreto AM 53.464/2026 — 4 exceções (verificação obrigatória antes de ação contra Gov AM):**
1. §1º — recursos vinculados (Operações de Crédito, convênios, SUS, Fundos, emendas, transferências federais) — **mapear a fonte orçamentária da SUHAB**;
2. §2º — contratos que incrementem arrecadação ou economizem, com **autorização prévia do Comitê de Gestão Fiscal**;
3. §3º — despesas de exercícios anteriores de SEFAZ-Encargos Gerais/contas públicas/aluguéis;
4. §4º — pessoal no passivo, desembolso único < R$ 5 mil com aval do Comitê.

O **art. 1º, II, "e"** (veda pagar despesas de exercícios anteriores a 2025) **não extingue o crédito** — apenas suspende o *pagamento direto* até 31/12/2026. Protesto/cobrança/compensação **preservam** o direito durante a vigência do decreto.

## 6. Próximos passos priorizados (contenção da prescrição primeiro)

1. **🔴 URGENTE — até 2026-06-30 (16 dias): destravar procuração e protestar as 6 faturas do miolo 2021** (comp. 05–10/2021, NFs 124586/125289/126050/126606/127412/128052, R$ 166.904,45 nominal), começando pela de comp. 05/2021 que prescreve em 30/06. Interrompe a prescrição e blinda o crédito salvável. Pendência única: procuração — escalar à PRODAM hoje.
2. **🔴 Datar o último pagamento parcial / reconhecimento** (NF 49556 "Parcialmente Paga" e as 7 evidências CONFIRMADO). Se posterior a 2021, **recalcular a prescrição do marco interruptivo** (Art. 202 VI CC) — pode ressuscitar faturas hoje contadas como prescritas.
3. **🟠 Corrigir o cadastro/CLAUDE.md:** trocar a mensagem "SUHAB 30/06/2026 (19 dias)" por uma que explicite "**5 faturas já prescritas (desde 2021); próxima salvável vence 30/06/2026**". Sinalizar o **erro de denominação** (§9). Trabalho do gerador `auto_update_claude_md.py` — registrar como pendência.
4. **🟠 Revisar a memória de cálculo monetário** (furo #6): confirmar se há cumulação indevida SELIC + 1% a.m.; gerar memorial atualizado com `atualizacao-monetaria-sob-demanda` antes de qualquer protocolo.
5. **🟡 Suprir os 3 documentos do título** (§3): contrato 046/2021 assinado, NLs, atesto c/ 2 testemunhas — habilita execução; até lá, **monitória** (Súmula 339/STJ).
6. **🟡 Definir a via de mérito** (§5): confirmar natureza (penhora direta vs. precatório/RPV) e mapear fonte orçamentária para as 4 exceções do Decreto 53.464/2026. Avaliar **compensação administrativa** como rota paralela (ente estadual).
7. **🟢 Não cobrar:** as 36 faturas prescritas (SSOT) e as 32 canceladas (R$ 107,1 mil líquido); confirmar com a PRODAM a natureza dos R$ 555,3 mil em "EmPerdas" antes de qualquer uso adversarial.

## 7. Precedentes aplicáveis (catálogo verificado — `PRECEDENTES_VERIFICADOS.md`)
- **REsp 2.088.100/SP** (3ª T., Min. Nancy Andrighi, 17/10/2023) — prescrição fulmina cobrança judicial **e extrajudicial**; não protestar faturas prescritas. *(impacto direto)*
- **REsp 793.969/RJ** (1ª T., **Rel. p/ acórdão Min. José Delgado**; Teori Zavascki vencido) — Contrato+NE+NF+atesto = título executivo.
- **Tema 1.109/STJ** (Min. Sérgio Kukina) — não há renúncia tácita à prescrição pela Adm. Pública.
- **REsp 1.963.067/MS** (Min. Nancy Andrighi) — unicidade da interrupção.
- **REsp 1.143.216/RS** (repetitivo, Min. Luiz Fux) + **REsp 836.495/RS** (Min. Mauro Campbell) — pagamento por anos gera legítima expectativa; *venire contra factum proprium*.
- **Súmula 339/STJ** — monitória contra Fazenda Pública.
- **RE 599.628 / Tema 253/STF** — SEM/entidade concorrencial sem prerrogativas (penhora direta).
- **AgInt no REsp 2.092.441/DF** (Min. Paulo Sérgio Domingues, 03/11/2025) — EP de serviço essencial não concorrencial → precatórios (alerta para o regime da SUHAB).
- **REsp 1.686.659/SP** + **ADI 5.135/DF** (Min. Roberto Barroso) — protesto contra ente público / protesto de CDA constitucional.

## 8. Cadeia documental observada nas pastas probatórias (READ-ONLY)
- **SUHAB_CONSOLIDADO/** (49 arquivos, 32,9 MB): 8 NFS-e (PDF), 2 Aceites/Relatórios, 31 Cobranças (inclui **Cartas Circulares da própria SUHAB — DIRAF/DAF-GEFIN 2024/2025**, fortes para reconhecimento), 8 PDFs originais (Cartas). **Vazias:** 01_CONTRATOS, 02_EMPENHOS, 04_NOTAS_LIQUIDACAO, 07_SCRAPING_SPCF, 09_RELATORIOS.
- **SPCF_EXTRACAO/por_devedor/SUHAB/**: 10 JSONs (contratos, empenhos, faturas, cobranças, propostas) — dados estruturados completos; as 13 faturas detalhadas estão com status **"Suspenso"** no SPCF (cobrança suspensa pela PRODAM, não inexistente).
- **prodam.db**: 5 contratos SPCF (1/2022, 9/2022, 4/2024, 2/2026, 3/2026), **322 empenhos Ativo (R$ 9,19 mi)**, 13 faturas estruturadas (12 cadeia COMPLETA, 1 FORTE; 1 "Parcialmente Paga"). PDFs **nunca** apagados/movidos — auditoria estritamente read-only.

## 9. Divergências forenses detectadas (a corrigir no SSOT/cadastro)
1. **Denominação errada (rótulo).** SSOT: `nome_completo = "Superintendência da Zona Franca de Manaus - Habitação"`. **Incorreto.** SUHAB é a **Superintendência Estadual de Habitação** (autarquia do **Governo do Estado do Amazonas**, CNPJ estadual 04.355.863/0001-32, alcançada pelo Decreto estadual 53.464/2026 art. 5º). A "Zona Franca de Manaus" pertence à **SUFRAMA** (autarquia **federal**) — denominação confundida no cadastro. **Corrigir** para "Superintendência Estadual de Habitação do Amazonas".
2. **"Documentação fraca" vs. cadeia COMPLETA no DB.** SSOT/checklist marcam doc. fraca e NL/contrato faltando; o `prodam.db` registra 12/13 faturas com 5 elos lógicos COMPLETOS (`liquidacao=true`, `pagamento=true`). A divergência é **documento físico ausente vs. dado estruturado presente** — não contradição de mérito, mas indica que **os documentos provavelmente existem e só precisam ser digitalizados/anexados** (esforço de coleta, não de litígio).
3. **Mensagem de prescrição enganosa no CLAUDE.md.** "SUHAB 30/06/2026 (19 dias)" omite que 5 faturas em aberto já prescreveram (desde 2021). Corrigir conforme §6.3.
4. **Possível cumulação monetária indevida** (SELIC + 1% a.m. + multa 1%) — revisar antes de protocolar (§4 furo #6).

---

_Auditoria forense gerada em 2026-06-14 para o branch `audit/suhab` (worktree isolado). Valores e contagens conferidos contra `profiles.json` (SSOT) e `prodam.db`; aritmética de prescrição reproduzida fatura a fatura sobre `SPCF_EXTRACAO/por_devedor/SUHAB/cobrancas_SUHAB.json`. Precedentes restritos ao catálogo `PRECEDENTES_VERIFICADOS.md`. Nenhum PDF foi apagado, movido ou renomeado._
