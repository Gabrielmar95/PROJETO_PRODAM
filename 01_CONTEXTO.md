# Contexto do Projeto — PRODAM / Recuperação de Créditos

_Retrato de 30/05/2026 (última sincronização automática). Kit montado em 08/06/2026. Para valores e prazos vigentes, a fonte é sempre `PRODAM_DOCS/profiles.json`._

## 1. Identidade e contrato

- **Advogado responsável**: Gabriel Mar — OAB/AM 15.697 (Gabriel Mar Sociedade Individual de Advocacia).
- **Contratante**: Brandão Ozores Advogados.
- **Cliente final**: PRODAM S.A. — Processamento de Dados Amazonas S.A. (CNPJ 04.407.920/0001-80), sociedade de economia mista estadual, regida pela Lei 13.303/2016.
- **Contrato**: 002/2026 (Brandão Ozores × PRODAM).
- **Honorários (fee)**: 20% sobre os créditos efetivamente recuperados.
- **Obrigações contratuais com prazo/multa**: relatórios quinzenais — multa de R$ 500/dia de atraso; e 10% do crédito perdido por prescrição imputável.

## 2. Objeto

Recuperação de créditos da PRODAM contra órgãos e entes do Estado do Amazonas (Administração Direta e Indireta) e contra devedores privados, decorrentes de serviços de tecnologia/processamento de dados prestados e não pagos.

**Frente atual: administrativa.** A prioridade é a cobrança extrajudicial — Termo de Reconhecimento de Dívida (TRD), notificações, compensação administrativa, protesto e uso estratégico de certidões. A via judicial (execução, monitória, habilitação de crédito) entra nos casos já maduros para isso ou quando a via administrativa se esgota. Antes de mudar de via em qualquer devedor, confirmar com o Gabriel.

## 3. Status do portfólio (snapshot 30/05/2026)

- **70 devedores**: 26 Governo Direta, 21 Governo Indireta, 22 Privados (1 linha é `_metadata`, não é devedor).
- **R$ 83.668.078,44 exigível** | R$ 125.245.390,64 já atualizado (correção + juros conforme índice por contrato).
- **3.477 faturas** no total — 2.326 exigíveis, 1.082 prescritas.
- **Força probatória**: 12 FORTE · 15 MÉDIA · 42 FRACA.

**Distribuição por fase** (pipeline F0→F6): F0 = 51 · F3 = 9 · F5 = 5 · F0_DIAGNÓSTICO = 4 · N/A = 1.

**Próximo passo agregado**: ANALISAR_DOCUMENTAÇÃO = 36 · CLASSIFICAR = 17 · ENVIAR_TRD = 9 · PROTOCOLAR_PETIÇÃO = 5 · HABILITAÇÃO DE CRÉDITO = 1 · AVALIAR_SUCESSÃO = 1.

## 4. Top 10 devedores por valor exigível

| # | Sigla | Exigível | Atualizado | Força | Próximo passo | Fase |
|---|-------|---------:|-----------:|-------|---------------|------|
| 1 | SEDUC | R$ 49.215.512,48 | R$ 50.263.263,56 | FORTE | ANALISAR_DOCUMENTAÇÃO | F0 |
| 2 | SES/SUSAM | R$ 4.783.356,52 | R$ 8.230.061,40 | FORTE | ENVIAR_TRD | F3 |
| 3 | SSP | R$ 4.553.230,80 | R$ 29.034.062,63 | FORTE | PROTOCOLAR_PETIÇÃO | F5 |
| 4 | SEJUSC | R$ 2.589.660,12 | R$ 5.262.537,82 | MÉDIA | ANALISAR_DOCUMENTAÇÃO | F0 |
| 5 | SEAD | R$ 2.339.702,20 | R$ 4.296.278,76 | FORTE | ENVIAR_TRD | F3 |
| 6 | BRADESCO | R$ 2.226.517,80 | R$ 2.226.517,80 | FRACA | CLASSIFICAR | F0 |
| 7 | CETAM | R$ 1.256.564,28 | R$ 1.256.564,28 | FRACA | CLASSIFICAR | F0 |
| 8 | SEDECTI | R$ 1.249.203,13 | R$ 4.007.244,35 | MÉDIA | ANALISAR_DOCUMENTAÇÃO | F0 |
| 9 | SALUX | R$ 1.027.949,15 | R$ 1.027.949,15 | FRACA | CLASSIFICAR | F0 |
| 10 | POLÍCIA CIVIL | R$ 960.481,71 | R$ 1.908.089,75 | MÉDIA | ANALISAR_DOCUMENTAÇÃO | F0 |

A lista completa dos 70 devedores está em `STATUS_DEVEDORES.md` (raiz da pasta), e os dados vivos em `PRODAM_DOCS/profiles.json`.

Observação sobre concentração: **SEDUC sozinha representa ~59% do exigível** do portfólio. SSP chama atenção pelo salto entre exigível (R$ 4,55M) e atualizado (R$ 29,03M), efeito de correção/juros acumulados — confirmar a base de cálculo antes de usar o valor atualizado em peça.

## 5. Prazos de prescrição — como ler

A prescrição no projeto é contada **por fatura individual**, do vencimento (Art. 189 c/c Art. 206, §5º, I, CC). O `STATUS_DEVEDORES.md` traz uma coluna `dias_presc` (dias até a próxima prescrição) que é uma **contagem do snapshot de 30/05/2026** — não a leia como se fosse hoje.

- No snapshot, vários devedores aparecem com `dias_presc` **negativo** (ex.: SEDUC, SEAD, SEDECTI, POLÍCIA CIVIL com −71): significa que a data da "próxima prescrição" registrada já passou. Isso é um sinal de alerta — exige reconciliação na fonte (pode indicar faturas já prescritas ou data desatualizada). Não presuma nem que está tudo perdido nem que está tudo bem: confirme em `profiles.json`/scripts.
- Alerta de prescrição futura mais próximo no snapshot: **SSP — 30/06/2026** (eram 31 dias em 30/05; ≈22 dias a partir de 08/06/2026), R$ 4.553.230,80.
- **ADS** aparecia como alerta crítico de prescrição em aberto nos registros de sessão.

Antes de qualquer afirmação sobre prazo, recalcule pela fonte. Datas de prescrição são o risco número um do contrato (multa de 10% do crédito perdido).

## 6. Pipeline de cobrança (F0 → F6)

Cada devedor caminha pelas fases abaixo; `fase_atual` em `profiles.json` marca o ponto vigente. Detalhe completo em `WORKFLOW_COBRANCA.md`.

- **F0 — Triagem**: identificar se está no portfólio, categoria (Direta/Indireta/Privada), documentação básica.
- **F1 — Análise documental**: validar a cadeia Contrato + NE + NF + Atesto; checklist de 11 itens; identificar marcos interruptivos (empenho = Art. 202, VI, CC).
- **F2 — Classificação e priorização**: definir `proximo_passo` e rank; gate humano antes de F3+.
- **F3 — Notificação extrajudicial (TRD)**: emitir TRD/notificação; mostrar diff antes de salvar; revisão humana; envio com AR ou e-mail certificado.
- **F4 — Negociação / resposta**: acompanhar aceite, contraproposta ou silêncio (silêncio **não** interrompe prescrição).
- **F5 — Protocolo judicial / execução**: ajuizar ou habilitar crédito; Adm. Direta → precatório/RPV (Art. 100 CF); Adm. Indireta concorrencial → penhora direta (Tema 253/STF).
- **F6 — Recebimento / encerramento**: confirmar pagamento, baixar do portfólio, calcular fee de 20%.

Para auditar um órgão de ponta a ponta existe o playbook de 13 passos validado no DETRAN (`PLAYBOOK_ORGAOS_V2.md`), orquestrado por `scripts/orgao_pipeline_completa.py --orgao <NOME>`. O DETRAN é o caso-referência (score composto 94/100 — A+).

## 7. Fontes da verdade (ordem de autoridade)

Consulte nesta ordem; o item de cima corrige o de baixo. Não afirme o que não estiver nelas.

1. `CLAUDE.md` (raiz) — regras, método e métricas do projeto (auto-gerado).
2. `PRODAM_DOCS/profiles.json` — **SSOT** dos devedores. Valores, força, prescrição e próximo passo saem daqui.
3. `PRODAM_DOCS/REFERENCIA_JURIDICA/` — base jurídica (18 subpastas temáticas; comece pelo `INDEX.md`). Consulte ANTES de qualquer parecer. **Jurisprudência: só a verificada em `11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md`.**
4. `WORKFLOW_COBRANCA.md` — fluxo F0→F6.
5. `PLAYBOOK_ORGAOS_V2.md` — tratamento por órgão.
6. `STATUS_DEVEDORES.md` — estágio e dados de cada devedor (snapshot).
7. `prodam.db` — base SQLite. Canônico: `PRODAM_DOCS/_ANALISE/prodam.db`; o `prodam.db` da raiz é cópia derivada usada por `scripts/consultas.py`.
8. `PRODAM_DOCS/` e `OCR_PESQUISAVEL_CONSOLIDADO/` — documentos-fonte digitalizados (provas).
9. `knowledge-agents.md` e `HISTORICO_SESSOES.md` — contexto acumulado.

**Se as fontes divergirem, pare e pergunte — não escolha sozinho.** Divergências já conhecidas: a data de prescrição em `profiles.json` pode divergir de CSVs antigos; o `LEIAME.md` (18/04) está desatualizado quanto à localização de algumas pastas.

## 8. Estrutura da pasta — trabalhe vs. ignore

**Trabalhe a partir de**: `PRODAM_DOCS/`, `dados/`, `DETALHAMENTO_FATURAS/`, `DOSSIES/`, `DOSSIES_MULTIFORMATO/`, `DOCUMENTOS_GERADOS/`, `relatorios/`, `scripts/`, `SPCF_EXTRACAO/`, `AUDITORIA_COMPLETUDE/`, `OCR_PESQUISAVEL_CONSOLIDADO/` e as pastas por órgão em MAIÚSCULAS (ex.: `DETRAN_*`).

**Ignore como histórico/lixo** (não é fonte, não editar):

- qualquer pasta iniciada por `_` — `_ARQUIVO_*`, `_BACKUPS`, `_SESSAO`, `_legado`, `_QUESTOES_CRITICAS`, `_AUDITORIA_FISICA`, etc.;
- qualquer arquivo de backup — com `.bak`, `.backup`, `BAK` ou `BACKUP` no nome (`CLAUDE.md.bak.*`, `prodam_BAK_*.db`, etc.);
- temporários/sessão — `_tmp_*.py`, `_out_*.txt`, `.fuse_hidden*`, `.continue-here.md`.

Regra prática: o que não está na lista de "trabalhe" e tem cara de backup, tmp ou sessão é lixo.

## 9. Onde salvar as saídas

- Peças e documentos → `DOCUMENTOS_GERADOS/`.
- Relatórios → `relatorios/`.
- Dossiês → `DOSSIES/` (ou `DOSSIES_MULTIFORMATO/` quando houver versões em vários formatos).

Mantenha nomenclatura consistente de devedores, valores e referências contratuais entre todos os arquivos. Valores em `Decimal` (nunca `float`), formato BRL `R$ 1.234,56`; CSV com separador `;` e encoding `utf-8-sig` (BOM).

## 10. Convenções técnicas

- **Plataforma**: Windows + PowerShell. Python via `py -3.12` (sem venv). Comandos de terminal sempre em bloco único, prontos para colar.
- **Dados financeiros**: `Decimal`, nunca `float`. Formato BRL `R$ 1.234,56`.
- **Contratos** têm 3 formatos coexistindo (`006/2021`, `6/2021`, `2021/006`) — normalizar antes de cruzar (`scripts/normalizador.py`).
- **PDFs são prova jurídica** — nunca apagar originais; backup em `_BACKUPS/`.
- **SPCF** (sistema de origem dos dados): respeitar `time.sleep(1.5)` entre requisições (rate limit).

## 11. Pendências críticas vivas (gate humano)

Itens que dependem de decisão do Gabriel e travam ações a jusante. Estavam abertos no último registro de sessão (31/05/2026); confirmar se já foram resolvidos antes de seguir.

- **SES/SUSAM — valor exigível divergente**: o TRD em disco usa R$ 4,78M (reconciliado em 12/05); um CSV posterior trazia R$ 14,75M (revertido em 13/05 sem changelog). O envio do TRD está **bloqueado** até definir qual valor é o real. (Há também a correção já aplicada de que a próxima prescrição SES é **31/08/2026**, e não 13/05 — o Of. 129/2021 é ato do credor e não interrompe prescrição.)
- **SUHAB — possível perda por prescrição**: lotes 1 e 2 (≈ R$ 6,3 mil + R$ 40,9 mil) tinham prazo em 23/04 e 27/04/2026 sem confirmação de protesto extrajudicial nos registros. Verificar tabelionato e relatório quinzenal de abr/mai 2026.
- **ADS** — alerta de prescrição crítico em aberto.
- **Alertas de prescrição (cron)**: o monitor automático apontou um conjunto de faturas em risco/prescritas — tratar como prioridade e reconciliar na fonte.

Nenhuma dessas conclusões deve ser repetida como fato sem checar o estado atual de `profiles.json` e dos relatórios — são pendências registradas, não desfechos.

## 12. O que o assistente sabe fazer neste projeto

O projeto tem dezenas de skills especializadas (índice em `.claude/skills/INDEX.md` e nas skills do Cowork). As principais famílias:

- **Análise por devedor**: classificação de força probatória, cadeia documental de 5 elos, score composto de 12 dimensões, auditoria de completude.
- **Prescrição**: cálculo por fatura, marcos interruptivos (Art. 202 CC), reconhecimento tácito (catálogo de 17 atos), revisão de reconhecimento antes de usar em peça.
- **Atualização monetária**: correção + juros por índice contratual (SELIC/IGPM/IPCA), com busca de índices via API do Banco Central; memorial de cálculo.
- **Documentos**: TRD, notificações (modelos A–G), dossiês multiformato, ofícios, relatório quinzenal, com auditoria anti-alucinação antes do envio.
- **Estratégia de recuperação**: compensação administrativa (Tesouro/TCE-AM), protesto estratégico, certidões (CND/CPEN/CAUC) como pressão, RPV vs precatório, desconsideração de PJ e cobrança de privados.
- **Dados**: OCR dos PDFs, reconciliação SPCF × pendrive × DB, normalização de valores BRL, rastreamento de procedência (P1–P4).

Use as skills do projeto em vez de improvisar — elas já trazem o fundamento legal e o método validado.
