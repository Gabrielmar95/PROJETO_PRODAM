# Guia Rápido Jurídico — Projeto PRODAM

_Síntese das regras já consolidadas no projeto (fonte primária: `CLAUDE.md` §5 e `PRODAM_DOCS/REFERENCIA_JURIDICA/`). Não é parecer novo nem pesquisa independente — é um resumo de consulta rápida._

## Aviso de uso (ler antes de citar qualquer coisa daqui)

- Este guia **não substitui** a consulta às fontes. Antes de usar em peça, confirme o dispositivo em `REFERENCIA_JURIDICA/` e, para jurisprudência, **exclusivamente** em `11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md`.
- O acervo do projeto **já catalogou precedentes fabricados e distorcidos**. Não reintroduza precedente que não esteja na lista verificada, mesmo que pareça plausível.
- Dados que mudam (SELIC/IGPM/IPCA, salário mínimo, teto de RPV, vigência de norma) devem ser conferidos na **fonte oficial** no momento do uso — não confie nos números deste arquivo.
- A hierarquia metodológica do projeto manda: **Nota Metodológica** corrige tudo; depois Estudo Consolidado (002/2026), Estudo Exaustivo, Pesquisa Jurisprudencial (só verificada) e Extração Contratual.

## 1. Prescrição

- **Quinquenal e por fatura individual**, contada do **vencimento** de cada fatura (Art. 189 c/c Art. 206, §5º, I, do Código Civil). Cada fatura tem seu próprio relógio — nunca tratar o crédito como bloco único.
- **Interrupção ocorre uma única vez** (unicidade do Art. 202, *caput*, CC) — o projeto referencia o REsp 1.963.067/MS. Confirmar antes de citar.
- **Fazenda Pública**: após interrupção, a prescrição reinicia **pela metade** (Decreto 20.910/1932), resultando em 2,5 anos no entendimento adotado pelo projeto.
- **Gestor público não renuncia tacitamente à prescrição** — Tema 1.109/STJ (conforme registrado no projeto; confirmar na base verificada).
- Dívida prescrita vira **obrigação natural** (Art. 882 CC): não exigível judicialmente, mas o pagamento espontâneo não é repetível.
- **Risco contratual**: o Contrato 002/2026 prevê multa de 10% do crédito perdido por prescrição imputável — prescrição é o risco número um do projeto.

## 2. Marcos interruptivos (o que zera o prazo)

Rol **taxativo** do Art. 202 CC. No projeto:

- **Interrompe**: empenho (NE) que referencia o contrato inadimplido = reconhecimento tácito da dívida (Art. 202, **VI**, CC). Demais atos inequívocos do **devedor** também.
- **NÃO interrompe**: silêncio do devedor; e atos do **credor** (a própria PRODAM) — Nota Fiscal emitida pelo credor e ofício do credor não são marcos interruptivos. Erro recorrente já corrigido no projeto (caso SES/SUSAM: o Of. 129/2021, ato do credor, foi indevidamente tratado como marco).

## 3. Título executivo e cadeia documental

- **Composição documental que forma título executivo**: Contrato + NE + NF + Atesto, conforme o precedente adotado pelo projeto — **REsp 793.969/RJ** (Rel. p/ acórdão **Min. José Delgado**; Min. Teori Zavascki foi **vencido** — atenção a esta atribuição, é um ponto que o projeto corrigiu). Base legal do título executivo extrajudicial: Art. 784 do CPC.
- **Nota de Liquidação (NL)**: confirmação formal do devedor de que o serviço foi prestado e o valor confere (Lei 4.320/64, arts. 63–65). Reforça a liquidez/certeza.
- **Aceite técnico / atesto** do fiscal: prova de que o serviço foi prestado — neutraliza a defesa de "serviço não prestado".

## 4. Via processual conforme o devedor

- **Administração Direta** (secretarias, órgãos sem personalidade própria): pagamento por **precatório/RPV** (Art. 100 da CF). Não há penhora de bens públicos.
- **Administração Indireta que atua em regime concorrencial**: admite **penhora direta** de bens — Tema 253/STF (conforme adotado pelo projeto; confirmar enquadramento do ente concreto).
- **Privados**: cobrança comum, protesto, negativação, e, conforme o caso, **desconsideração da personalidade jurídica** (Art. 50 CC) ou habilitação em **falência** (Lei 11.101/2005).

## 5. Atualização monetária e juros

- **Índice é por contrato** — consultar o mapa em `scripts/normalizador.py`. Não presumir índice; cada contrato define o seu (SELIC, IGPM ou IPCA).
- **SELIC já embute correção + juros** — não somar juros separadamente.
- **IGPM (e IPCA)**: só correção; **juros entram à parte**.
- **Juros**: após a **Lei 14.905/2024**, não presumir 1% a.m. — verificar os arts. 404–406 do CC na redação vigente.
- Valores sempre em `Decimal`; antes de protocolar, **atualizar na data** (índices via fonte oficial / API do Banco Central).

## 6. Norma estadual de regência (Gov AM)

- **Decreto Estadual AM nº 53.464/2026** (que substitui o Decreto 51.084/2025): antes de qualquer ação contra ente do Governo do Amazonas, **verificar as 4 exceções** previstas. Confirmar vigência e texto atual na fonte oficial — é norma recente e pode ter sido alterada.

## 7. Honorários e pagamento rápido

- **Fee**: 20% sobre o crédito recuperado.
- **RPV estadual no AM**: teto de **20 salários mínimos**, com fundamento na **Lei AM 2.748/2002** (atenção: **não** é a Lei 3.683/2012). Conferir o valor do salário mínimo vigente e a vigência da lei antes de calcular o enquadramento RPV × precatório.

## 8. Recuperação fora do processo (rotas administrativas)

- **Compensação administrativa**: via Tesouro Estadual e TCE-AM — rota principal para boa parte do portfólio de governo.
- **Protesto de entes públicos**: cabível, observada a **Lei 9.492/97** (em especial o art. 1º, parágrafo único). Priorizar por impacto institucional, não só por valor.
- **Certidões (CND/CPEN/CAUC)** como pressão: a irregularidade do devedor pode travar repasses e transferências voluntárias.

## 9. Armadilhas conhecidas do projeto

- **FUHAM ≠ FHAJ**: FUHAM = Fundação Alfredo da Matta; FHAJ = Fundação Hospital Adriano Jorge. Nunca inverter.
- **Atribuição do REsp 793.969/RJ**: relator p/ acórdão é Min. **José Delgado** (Teori vencido) — o inverso já apareceu errado e foi corrigido.
- **Ato do credor não interrompe prescrição** — vale tanto para NF quanto para ofício da PRODAM.
- **Precedentes fabricados/distorcidos** já catalogados no acervo — a única lista confiável é `PRECEDENTES_VERIFICADOS.md`.

## Checklist "verificar sempre antes de afirmar"

1. Índice de correção do contrato específico (não presumir).
2. Salário mínimo e teto de RPV vigentes na data.
3. Vigência e texto atual da norma estadual (Decreto 53.464/2026 e exceções).
4. Data de prescrição recalculada por fatura na fonte (`profiles.json`/scripts), não a do snapshot.
5. Precedente conferido em `PRECEDENTES_VERIFICADOS.md` antes de ir para a peça.
