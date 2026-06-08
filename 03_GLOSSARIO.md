# Glossário — Projeto PRODAM

_Siglas, termos e classificações usados no projeto. Para denominações oficiais de órgãos e valores, a fonte é o contrato do devedor e `PRODAM_DOCS/profiles.json`._

## Termos do contrato e das partes

- **PRODAM** — Processamento de Dados Amazonas S.A. Cliente final; sociedade de economia mista estadual (Lei 13.303/2016). CNPJ 04.407.920/0001-80.
- **Brandão Ozores** — escritório contratante (Contrato 002/2026).
- **Fee** — honorários de 20% sobre o crédito efetivamente recuperado.
- **SSOT** (Single Source of Truth) — fonte única da verdade. No projeto, é o `profiles.json` para devedores.
- **SPCF** — sistema interno de origem dos dados financeiros da PRODAM (contratos, empenhos, faturas), de onde os dados são extraídos por scraping. Tratar a expansão da sigla como interna; o que importa é a função.

## Documentos do ciclo de despesa pública

- **NE — Nota de Empenho**: reserva orçamentária da despesa pelo ente público. No projeto, empenho que referencia contrato inadimplido funciona como **reconhecimento tácito** de dívida (Art. 202, VI, CC) e interrompe a prescrição.
- **NL — Nota de Liquidação**: confirmação formal, pelo devedor, de que o serviço foi prestado e o valor está correto (Lei 4.320/64, arts. 63–65). NL assinada é reconhecimento forte.
- **NF — Nota Fiscal**: documento do credor. Por ser ato do credor, **não** é marco interruptivo de prescrição.
- **Atesto / Aceite técnico**: atestado do fiscal do contrato de que o serviço foi prestado. Derruba a alegação de "serviço não prestado".
- **Carta de cobrança**: comunicação de cobrança; pode conter elementos de reconhecimento dependendo do emissor.

## Termos jurídicos e de método

- **TRD — Termo de Reconhecimento de Dívida**: instrumento extrajudicial em que o devedor reconhece o débito; etapa F3 do pipeline.
- **Cadeia documental (5 elos)**: Contrato → NE → NL → NF → Pagamento. Quanto mais completa, maior a força executória da fatura.
- **Composição documental para título executivo**: Contrato + NE + NF + Atesto formam título executivo, conforme o precedente do projeto (REsp 793.969/RJ). Ver `04_GUIA_RAPIDO_JURIDICO.md`.
- **Marco interruptivo**: ato que zera a contagem da prescrição (rol do Art. 202 CC). Empenho interrompe; silêncio e atos do credor (NF, ofício do credor) não.
- **Reconhecimento tácito**: ato do devedor que admite a dívida sem declará-la expressamente (ex.: empenho) — Art. 202, VI, CC. O projeto cataloga 17 atos típicos em 4 categorias (orçamentário, administrativo, financeiro, comportamental).
- **Prescrição**: perda da pretensão pelo decurso do prazo. No projeto, contada **por fatura**, do vencimento (quinquenal — ver guia jurídico).
- **RPV — Requisição de Pequeno Valor**: via de pagamento rápido (≈60 dias) para créditos contra a Fazenda abaixo do teto legal; alternativa ao precatório. No AM, o teto estadual usado no projeto é 20 salários mínimos (Lei AM 2.748/2002 — confirmar vigência/valor).
- **Precatório**: requisição de pagamento contra a Fazenda acima do teto de RPV; entra em fila anual (Art. 100 CF).
- **Fragmentação RPV × precatório**: estratégia de separar faturas autônomas para enquadrar parte do crédito em RPV e acelerar recebimento.
- **Compensação administrativa**: recuperação via retenção/encontro de contas no Tesouro Estadual e TCE-AM; rota administrativa para parte do portfólio de governo.
- **Protesto**: levada do título a cartório como pressão; para entes públicos há regra específica (Lei 9.492/97).
- **CND / CPEN / CAUC**: certidões usadas como pressão institucional. CND = Certidão Negativa de Débitos; CPEN = Certidão Positiva com Efeitos de Negativa; CAUC = serviço de checagem de regularidade para transferências voluntárias da União (confirmar denominação oficial atual). Devedor irregular pode ficar impedido de receber repasses.
- **Desconsideração da personalidade jurídica**: alcançar o patrimônio dos sócios (Art. 50 CC); aplicável a devedores privados, mediante checklist de viabilidade.
- **Blindagem pré-execução**: checklist (no projeto, 22 itens) que antecipa teses de embargos antes de protocolar execução.
- **Score composto**: nota 0–100 do devedor calculada em 12 dimensões (cadeia documental, prescrição, blindagem, compliance, etc.). Classes: A+ ≥90 · A ≥85 · A- ≥80 · B+ ≥75 · B ≥70.
- **CPRAC**: procedimento de recuperação de crédito junto à PGE-AM citado nos tipos de dossiê (confirmar expansão e cabimento antes de usar em peça).

## Índices e atualização de valores

- **SELIC**: taxa que **já inclui correção + juros** — não somar juros à parte.
- **IGPM** / **IPCA**: índices de correção; quando aplicados, os **juros entram à parte**.
- **Regra do projeto**: o índice aplicável é **por contrato** (ver `scripts/normalizador.py`). Não presumir 1% a.m. de juros — verificar arts. 404–406 CC após a Lei 14.905/2024.

## Classificações do portfólio

- **Categoria**: **Gov Direta** (secretarias e órgãos da Administração Direta), **Gov Indireta** (autarquias, fundações, institutos), **Privado** (empresas, bancos).
- **Força probatória**: **FORTE** (documentação robusta, tende a título executivo) · **MÉDIA** (lacunas, geralmente caminho de monitória) · **FRACA** (cobrança/diagnóstico antes de avançar).
- **Fases (pipeline F0→F6)**: F0 triagem · F1 análise documental · F2 classificação/priorização · F3 notificação/TRD · F4 negociação/resposta · F5 protocolo judicial/execução · F6 recebimento/encerramento. Variante **F0_DIAGNÓSTICO** = devedor ainda em diagnóstico inicial.
- **Próximo passo** (campo `proximo_passo`): ANALISAR_DOCUMENTAÇÃO, CLASSIFICAR, ENVIAR_TRD, PROTOCOLAR_PETIÇÃO, HABILITAÇÃO DE CRÉDITO, AVALIAR_SUCESSÃO.
- **Procedência de dados (P1–P4)**: P1-DOC = documento original · P2-PARCIAL = documento incompleto · P3-SISTEMA = só registro no SPCF · P4-INDETERMINADO. Usado para garantir lastro documental das provas.

## Órgãos do portfólio (siglas)

Denominações abaixo seguem o uso corrente no Amazonas; **confirme a denominação/razão social exata no contrato do devedor e em `profiles.json`** antes de usar em peça. Onde há incerteza, está marcado "(confirmar)".

Garantidas pelo projeto (nunca inverter):

- **FUHAM** (também grafado FUAM/FUHAM) — Fundação Alfredo da Matta.
- **FHAJ** — Fundação Hospital Adriano Jorge.

Secretarias e órgãos de governo (denominação corrente):

- **SEDUC** — Educação · **SES** — Saúde · **SUSAM** — sistema de saúde estadual (aparece como "SES/SUSAM") · **SSP** — Segurança Pública · **SEFAZ** — Fazenda · **SEAD** — Administração e Gestão · **SEMA** — Meio Ambiente · **SEINFRA** — Infraestrutura · **PGE** — Procuradoria-Geral do Estado · **DPE** — Defensoria Pública do Estado · **CGE** — Controladoria-Geral do Estado · **CBMAM** — Corpo de Bombeiros Militar do AM · **PMAM** — Polícia Militar do AM · **POLÍCIA CIVIL** · **DETRAN** — Departamento Estadual de Trânsito · **CASA CIVIL** · **CASA MILITAR**.
- (confirmar denominação): **SEJUSC, SEDECTI, SEJEL, SEPROR, SECT, SEMIG, SETRAB, SEAS, SEC, UGPI**.

Autarquias, fundações e institutos (Gov Indireta):

- **AMAZONPREV** — regime próprio de previdência do AM · **IPAAM** — proteção ambiental · **IDAM** — desenvolvimento agropecuário/florestal · **ARSEPAM** — agência reguladora de serviços públicos · **SUHAB** — habitação · **CETAM** — centro de educação tecnológica · **ADAF** — defesa agropecuária e florestal · **ADS** — agência de desenvolvimento sustentável · **FVS** — vigilância em saúde · **FCECON** — oncologia · **FMT** — medicina tropical · **FHEMOAM** — hematologia/hemoterapia · **FUNTEA, FJJA, FMPES, SNPH, COSAMA, IDAM, AADESAM, ANOREG, CPA, ITRANSITO, FAAR/SEDEL** (confirmar denominação e natureza).

Privados (empresas e bancos):

- **BRADESCO, BRADESCO FINANCIAMENTO, CAIXA, BANCO MASTER, BANCO DAYCOVAL, BANCO BMG, BANCO SAFRA, BANCO SICOOB, BMC, SUL AMERICA** (instituições financeiras) · **SALUX, FENIXSOFT, PROVER, IKM DE, B23 TECNOLOGIA, PSA TECHNOLOGY, EASYTECH, ODONTOMED, ASSOC. DE GESTÃO INOVAÇÃO E RES. EM SAÚDE** (empresas/associações).

A categorização definitiva (Direta/Indireta/Privado) de cada devedor está em `profiles.json`; a lista acima é orientativa.
