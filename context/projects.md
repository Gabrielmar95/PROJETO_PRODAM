# Projetos ativos

> Foco atual do trabalho com você. Os números e o status de cada devedor são voláteis e sigilosos — a fonte da verdade é `PRODAM_DOCS/profiles.json`. Não reproduza valores, CNPJ ou nomes de devedores em arquivos que possam sair do meu computador sem necessidade.

## 1. Projeto PRODAM — Recuperação de Créditos (eixo principal)
- **Contrato:** 002/2026 — Brandão Ozores Advogados × PRODAM S.A. (Processamento de Dados Amazonas S.A., sociedade de economia mista estadual).
- **Meu papel:** advogado responsável (Gabriel Mar — OAB/AM 15.697).
- **Objeto:** recuperar créditos da PRODAM contra órgãos e entes do Estado do Amazonas e contra devedores privados.
- **Frente atual: administrativa.** Prioridade para a cobrança extrajudicial — TRD, notificações, compensação administrativa, protesto, certidões. A via judicial (execução, monitória, habilitação de crédito) entra nos casos já maduros ou quando a administrativa se esgota; **avise antes de mudar de via**.
- **Obrigações contratuais sensíveis:** relatórios quinzenais (há penalidade por atraso) e responsabilidade pelo crédito perdido por prescrição — por isso **prazo prescricional é alarme máximo**.
- **Portfólio:** dezenas de devedores (governo direto, governo indireto e privados), em estágios distintos de um fluxo de cobrança F0→F6.

### Fontes da verdade (consultar nesta ordem; a de cima corrige a de baixo)
1. `CLAUDE.md` — regras, método e métricas do projeto (autoridade máxima; auto-gerado).
2. `PRODAM_DOCS/profiles.json` — SSOT dos devedores (valores, força probatória, prescrição, próximo passo).
3. `PRODAM_DOCS/REFERENCIA_JURIDICA/` — base jurídica (começar pelo `INDEX.md`); jurisprudência apenas a verificada.
4. `WORKFLOW_COBRANCA.md` — fluxo de cobrança F0→F6.
5. `PLAYBOOK_ORGAOS_V2.md` — tratamento por órgão.
6. `STATUS_DEVEDORES.md` — estágio e dados de cada devedor.
7. `prodam.db` — base SQLite (canônico em `PRODAM_DOCS/_ANALISE/prodam.db`).

> Se as fontes divergirem entre si, **pare e pergunte** — não escolha sozinho.

### Regras jurídicas que mais custam caro se ignoradas
- Prescrição é **por fatura individual**, contada do vencimento (Art. 189 + 206 §5º, I, do CC).
- Marcos interruptivos: somente os do **Art. 202 do CC** (rol taxativo). Silêncio do devedor e NFs do credor **não** interrompem; empenho (NE) configura reconhecimento tácito.
- Verificar a vigência e as exceções do **Decreto Estadual do AM** aplicável antes de qualquer ação contra o Governo do Amazonas.
- Índice/regime de correção (SELIC / IGP-M / IPCA) é definido **por contrato** — confirmar na cláusula econômica, nunca presumir.

## 2. Sub-projeto DETRAN-AM (mais avançado)
- Auditoria e cobrança do crédito da PRODAM contra o **DETRAN-AM** — o devedor com a documentação mais consolidada do portfólio.
- Particularidade: o crédito reúne vários contratos com **regimes de correção diferentes** (IGP-M, IPCA, SELIC e contratos silentes), tratados contrato a contrato.
- Estágio: peça de cobrança extrajudicial em revisão final, instruída com anexos (memorial de cálculo e cadeia documental por fatura).
- Pasta dedicada: `DETRAN_AUDITORIA_COMPLETA/`, com `CLAUDE.md` próprio.

---

_Por opção minha, Engeco (NDA) e demais frentes ficam fora destes arquivos de contexto. Reincluir somente se eu pedir._
