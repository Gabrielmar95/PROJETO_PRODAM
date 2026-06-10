# AUDITORIA DE SKILLS — Projeto PRODAM / Engeco / Utilitários
**Data:** 09/06/2026 · **Modo:** análise apenas (read-only) · **Nada foi apagado, movido ou editado.**

> Esta é uma auditoria de leitura. Toda ação (consolidar, aposentar, editar) está **proposta**, não executada. Nenhuma referência jurídica foi inventada — onde faltou dado, está marcado como "uso não verificável" ou listado em "O que preciso que você verifique".

---

## PASSO 0 — Onde estão suas skills

### A. Conjunto ATIVO (é o que o assistente realmente carrega e dispara)

| Local (Windows) | Conteúdo | Qtde |
|---|---|---|
| `…\.claude\skills\` (skills de usuário/projeto) | Skills standalone — jurídicas PRODAM, Engeco e utilitários | **106** |
| `…\.remote-plugins\plugin_…015cwq…` | Plugin **superpowers** | 14 |
| `…\.remote-plugins\plugin_…01JXME7…` | Plugin **productivity-prodam** | 7 |
| `…\.remote-plugins\plugin_…01EjycmV…` e `…01J1ZUJ…` | Plugin **cockroachdb** (2 cópias idênticas instaladas) | 33 ×2 |
| `…\.remote-plugins\plugin_…0155z…` e `…01CxFj…` | Plugin **cowork-plugin-management** (2 cópias idênticas) | 2 ×2 |
| `PROJETO_PRODAM\.claude\skills\INDEX.md` | Índice das skills do projeto (não contém SKILL.md próprio; aponta para as 106) | — |

A auditoria de mérito (redundância, gatilho, bloco jurídico) recai sobre as **106 skills ativas** + os 4 plugins distintos. As cópias duplas de cockroachdb e cowork-plugin-management são item de limpeza (abaixo).

### B. Cópias LEGADAS / staging no disco (NÃO são skills ativas — fontes de "drift")

Encontrei centenas de `SKILL.md` adicionais que **não estão no conjunto ativo**. São versões antigas, importações e staging. Não os auditei um a um (não disparam), mas listo as origens porque são a causa provável de confusão futura:

| Local | Natureza |
|---|---|
| `PROJETO_PRODAM\PRODAM_DOCS\_WORKFLOW_IMPORTADO\SKILLS NOVA\…` (incl. `SKILLS_ORGANIZADAS_v2`, `_ARQUIVO_LEGADO`, `_ARQUIVO_LEGADO\SKILLS_MELHORADAS_v2`) | Dezenas de cópias antigas das mesmas skills PRODAM (várias gerações sobrepostas) |
| `PROJETO_PRODAM\PRODAM_DOCS\_SKILLS\` | Staging com `.skill`, `_SKILL.md` soltos + 2 skills em subpasta (`dossie-juridico-prodam`, `sincronizacao-referencias-pdf`) que **não estão no conjunto ativo** |
| `PROJETO_PRODAM\_SKILLS_NOVAS_20260423\` | `normalizador-contratos-prodam`, `renomeador-pdfs-prodam` (não instaladas) |
| `DETRAN_AUDITORIA_COMPLETA\_SKILLS_NOVAS_20260420\` | `auditoria-paridade-db-csv`, `diagnostico-forense-dados`, `normalizador-contratos-prodam`, `schema-navigator-prodam`, `sync-prodam-dbs` (não instaladas — o próprio CLAUDE.md do DETRAN já registra que faltam) |
| `PROJETO_PRODAM\detran_dashboard\node_modules\@trpc\…`, `dotenv\…` | `SKILL.md` de bibliotecas de terceiros — **ruído**, ignorar |
| `PROJETO_PRODAM\impeccable-main\**` | Repositório clonado replicado em `.claude/.cursor/.gemini/…` — **ruído**, ignorar |

Conforme instruído, **ignorei tudo dentro de `_ARCHIVE`**. Observação: as pastas `_ARQUIVO_LEGADO` e `_WORKFLOW_IMPORTADO` não se chamam `_ARCHIVE`, mas têm função de arquivo — sinalizo abaixo (não toquei).

---

## Metodologia e limites (leia antes da tabela)

- **Data de modificação:** 104 das 106 skills ativas têm `mtime = 2026-05-29` (foram escritas/sincronizadas em lote). Só 8 são de 09/06 e 1 de 30/05. **Conclusão honesta:** a data não distingue "mais nova vs mais antiga" entre as jurídicas — para decidir a "mais completa" usei conteúdo (tamanho, cobertura, integração), não a data.
- **"Uso/integração":** medido por citação (a) nos `CLAUDE.md`/`INDEX.md`/docs do projeto e (b) no corpo de outras skills. Coluna `Cit. = nº docs / nº skills que citam`. **Citação zero ≠ skill inútil** — significa "uso não verificável" (você pode invocá-la manualmente). Nunca presumi não-uso.
- **Bloco jurídico:** testei a presença literal da seção `## FONTE JURÍDICA OBRIGATÓRIA` (o padrão definido no seu próprio `FONTE_JURIDICA_SKILL_UPDATES_SPEC.md`). `✓` = tem; `–` = não tem; `n/a` = não é skill jurídica substantiva.
- **Precedentes fabricados:** os 3 precedentes que seu projeto cataloga como fabricados (REsp 1.014.496/SC, REsp 2.792.731/SP, TJ-AM 2008.000901-9) aparecem em ~28 skills **apenas como alerta "NUNCA citar"**. Verifiquei o contexto: **nenhuma skill os cita como precedente válido**. Isso é o comportamento correto, não um defeito.

---

## Resumo executivo

- **106 skills ativas** + 4 plugins. Distribuição de veredito: **MANTER 61 · CONSOLIDAR 12 · APOSENTAR 2 · REVISAR 31**.
- **3 grupos de duplicação "limpa"** (mesma função): tipografia jurídica (2), atualização monetária (2), criar-skills (3) — além de pares utilitários (SQL, viz) e duplicatas de plugin (brainstorming, writing-plans).
- **2 grupos juridicamente sensíveis para consolidar:** dossiê (2 skills) e pipeline/workflow por devedor (2 skills) — risco de **dois fluxos divergentes** gerando saídas inconsistentes.
- **Bloco jurídico:** 26/106 têm o bloco. As **2 skills meta mais críticas do spec — `prodam-juridico` e `proximo-passo-advisor` — estão SEM o bloco padrão** (embora referenciem a SSOT). Outras ~9 jurídicas substantivas também não têm.
- **Conflito plugin × standalone:** o plugin `productivity-prodam` (alerta-prazos, registro-acao-devedor, painel-devedores, memory) duplica funções de skills standalone suas (`controle-sla-alertas`, `registro-interacoes-devedor`, `proximo-passo-advisor`, `consolidate-memory`). Decisão de arquitetura pendente.
- **2 cópias idênticas** de cockroachdb e de cowork-plugin-management instaladas — remover as duplicatas.

---

## PASSO 1 + Veredito — Tabela mestra (106 skills ativas)

Legenda — **Cat:** J=Jurídico PRODAM · D=Dados/SPCF · R=Relatório/Documento · G=Governança/QA · M=Meta/criação · E=Engeco (outro projeto) · U=Utilitário genérico. **Cit:** docs/skills. **Bloco:** ✓/–/n-a.

### Categoria J — Jurídico PRODAM (núcleo)

| Skill | Mod | Apoio | Cit (d/s) | Bloco | Veredito | Justificativa (1 linha) |
|---|---|---|---|---|---|---|
| aceite-tecnico-catalogador | 05-29 | não | 1/4 | ✓ | MANTER | Cataloga aceites/atestos (prova de serviço); integrada e com bloco. |
| arvore-decisao-contestacao | 05-29 | não | 1/2 | ✓ | MANTER | Árvore de defesa do devedor; única no escopo, com bloco. |
| atualizacao-monetaria-creditos | 05-29 | não | 3/8 | – | REVISAR | Base de cálculo em escala (polars); muito citada, mas **sem bloco** e duplica a "sob-demanda". |
| atualizacao-monetaria-sob-demanda | 05-29 | não | 3/6 | ✓ | CONSOLIDAR → atualizacao-monetaria-creditos | Mesmo domínio (SELIC/IGPM/juros); vira o "modo sob-demanda + memorial BCB" da base. |
| blindagem-pre-execucao | 05-29 | não | 4/6 | ✓ | MANTER | Antecipa embargos; muito integrada, com bloco. |
| certidoes-estrategia | 05-29 | não | 1/1 | ✓ | MANTER | Pressão via CND/CAUC; escopo próprio. |
| classificacao-forca-probatoria | 05-29 | não | 4/4 | – | REVISAR | Classifica força/título executivo; central e citada, mas **sem bloco**. |
| compensacao-administrativa-workflow | 05-29 | não | 1/5 | ✓ | MANTER | Rota Tesouro/TCE (85% do portfólio); com bloco. |
| compliance-contratual-prodam | 05-29 | não | 1/1 | ✓ | MANTER | Compliance do Contrato 002/2026; escopo próprio. |
| desconsideracao-pj-checklist | 05-29 | não | 1/3 | ✓ | MANTER | Art. 50 CC p/ privadas; com bloco. |
| extracao-clausulas-contratuais | 05-29 | não | 3/0 | – | REVISAR | Porta de entrada p/ cálculo (v2.0, citada no DETRAN), mas **sem bloco**. |
| geracao-documentos-juridicos | 05-29 | não | 3/4 | – | REVISAR | Gera TRD/notificações/dossiês; central, mas **sem bloco**. |
| marcos-interruptivos-prescricao | 05-29 | não | 4/6 | – | REVISAR | Art. 202 CC; muito citada, mas **sem bloco**; gatilho toca reconhecimento-tácito. |
| montagem-dossie-comprobatorio | 05-29 | não | 2/3 | – | REVISAR (base do grupo dossiê) | 7 tipos de peça + cadeia 5 elos; mais ampla juridicamente, mas **sem bloco**. |
| montagem-dossie-devedor-detalhado | 05-29 | não | 0/0 | – | CONSOLIDAR → montagem-dossie-comprobatorio | Mesmo objetivo (dossiê); contribui o gerador multi-formato (docx/xlsx/json). |
| nota-empenho-classificador | 05-29 | não | 2/5 | ✓ | MANTER | NE = reconhecimento tácito; integrada, com bloco. |
| nota-liquidacao-extrator | 05-29 | não | 2/6 | ✓ | MANTER | NL = reconhecimento incontestável; integrada, com bloco. |
| precatorios-rpv-fragmentacao | 05-29 | não | 2/3 | ✓ | MANTER | RPV×precatório; com bloco. |
| prodam-juridico | 05-29 | não | 2/2 | – | REVISAR (crítico) | Skill "advogado sênior" meta; **falta o bloco padrão** (1 das 2 do spec). |
| protesto-estrategico | 05-29 | não | 1/1 | ✓ | MANTER | Protesto Lei 9.492/97; com bloco. |
| proximo-passo-advisor | 05-29 | não | 3/6 | – | REVISAR (crítico) | Decide a via (8 rotas); muito citada; **falta o bloco padrão** (2 do spec) — já tem o aviso anti-fabricados solto. |
| reconhecimento-divida-tacito | 05-29 | não | 3/7 | – | REVISAR | Catálogo 17 atos; muito citada, **sem bloco**; gatilho colide com "revisar-reconhecimento". |
| recuperacao-creditos-empresas-privadas | 05-29 | não | 1/2 | ✓ | MANTER | Regime de privadas; com bloco. |
| revisar-reconhecimento-divida | 05-29 | não | 3/5 | – | REVISAR | Gate de validação de reconhecimento; **sem bloco**; gatilho colide com o catálogo. |
| risco-processual-matriz | 05-29 | não | 2/1 | ✓ | MANTER | Matriz de risco; com bloco. |
| validador-cadeia-documental-fatura | 05-29 | não | 4/8 | – | REVISAR | Valida cadeia 5 elos por fatura; muito citada, **sem bloco**. |

### Categoria D — Dados / SPCF

| Skill | Mod | Apoio | Cit (d/s) | Bloco | Veredito | Justificativa |
|---|---|---|---|---|---|---|
| auditoria-base-dados-camadas | 05-29 | não | 2/0 | ✓ | MANTER | Auditoria de qualidade em 4 camadas; rever fronteira com "completude". |
| auditoria-completude-devedor | 05-29 | não | 1/1 | – | MANTER | Checklist de gaps por devedor; escopo distinto da de camadas. |
| integracao-dados-novos-spcf | 05-29 | não | 2/1 | ✓ | MANTER | Workflow de ingestão de lote SPCF; rever fronteira com reconciliação. |
| normalizador-valores-brl | 05-29 | não | 2/2 | ✓ | MANTER | Parsing BRL (Decimal); utilitário-base citado. |
| ocr-pdfs-prodam | 05-29 | não | 1/1 | ✓ | MANTER | OCR de PDFs-imagem; com bloco. |
| prodam-data-analyst | 05-29 | 5 ref | 0/0 | – | REVISAR | Base de contexto do analista; **uso não verificável** (0 citações). |
| rastreamento-procedencia-dados | 05-29 | não | 1/1 | ✓ | MANTER | Procedência P1–P4 das provas; com bloco. |
| reconciliacao-spcf-pipeline | 05-29 | não | 0/3 | – | MANTER | Cruza SPCF×PDF (fuzzy); citada por 3 skills; rever fronteira com integração. |

### Categoria R — Relatório / Documento / Tipografia

| Skill | Mod | Apoio | Cit (d/s) | Bloco | Veredito | Justificativa |
|---|---|---|---|---|---|---|
| design-relatorio-quinzenal-prodam | 05-29 | não | 0/3 | n/a | MANTER | Identidade visual PRODAM (timbrado, azul+dourado); usada por vários docs. Conflito de gatilho com "gerador". |
| gerador-relatorio-quinzenal | 05-29 | não | 1/1 | ✓ | MANTER | Gera o conteúdo do relatório quinzenal (KPIs); escopo distinto da de design. |
| tipografia-juridica | 05-29 | py+ref | 0/2 | n/a | MANTER (base tipografia) | Padrão Dupincel + perfil Times p/ NDA; tem scripts de apoio e desambiguação. |
| tipografia-juridica-gabriel | 05-29 | não | 0/2 | n/a | CONSOLIDAR → tipografia-juridica | Mesmo "padrão do escritório"; vira o perfil "Honorários/Gabriel" da base. |
| build-dashboard | 05-29 | não | 0/1 | n/a | MANTER | Dashboard HTML interativo; distinto de gráfico estático. |

### Categoria G — Governança / QA / Workflow

| Skill | Mod | Apoio | Cit (d/s) | Bloco | Veredito | Justificativa |
|---|---|---|---|---|---|---|
| protocolo-juridico-prodam | 05-29 | não | 5/2 | ✓ | MANTER | Camada de governança (7 etapas obrigatórias); a mais citada em docs. |
| auditoria-documentos-juridicos | 05-29 | não | 2/5 | ✓ | MANTER (base do QA pré-envio) | Auditoria 5 níveis antes de enviar; integrada e com bloco. |
| validacao-pos-geracao | 05-29 | não | 2/4 | ✓ | CONSOLIDAR → auditoria-documentos-juridicos | Valida vs profiles.json; é subconjunto do QA pré-envio (63 linhas). |
| guardrails-anti-alucinacao | 05-29 | não | 2/3 | – | MANTER | Fact-check pré-geração contra base; distinto do QA pós; rever fronteira. |
| pipeline-devedor-completo | 05-29 | não | 1/1 | n/a | MANTER (base do grupo workflow) | Orquestra 7 etapas ponta-a-ponta integrando 12+ skills. |
| workflow-pos-analise-devedor | 05-29 | não | 1/0 | ✓ | CONSOLIDAR → pipeline-devedor-completo | Mesmas 7 etapas pós-análise; sobreposição quase total. |
| workflow-orchestrator | 05-29 | não | 1/4 | ✓ | REVISAR | Orquestrador genérico (58 linhas); verificar se agrega algo além do pipeline. |
| contexto-projeto-manutencao | 05-29 | não | 1/0 | ✓ | MANTER | Mantém o documento de contexto; rever sobreposição com sync/rastreamento. |
| sync-skills-prodam | 05-29 | não | 0/1 | ✓ | MANTER | Sincroniza/valida skills entre si; rever sobreposição meta. |
| triagem-consistencia-versoes | 05-29 | não | 1/0 | ✓ | MANTER | Compara versões/cascata; rever sobreposição com sync. |
| rastreamento-qualidade-prompts | 05-29 | não | 1/0 | ✓ | MANTER | Métrica de acerto de prompts no fim de sessão; meta. |
| controle-sla-alertas | 05-29 | não | 1/1 | ✓ | REVISAR | Conflito direto com plugin `productivity-prodam:alerta-prazos` — decidir qual fica. |
| registro-interacoes-devedor | 05-29 | não | 1/0 | ✓ | REVISAR | Conflito com plugin `productivity-prodam:registro-acao-devedor` — decidir qual fica. |

### Categoria M — Meta / Criação / Cowork

| Skill | Mod | Apoio | Cit (d/s) | Bloco | Veredito | Justificativa |
|---|---|---|---|---|---|---|
| skill-creator | 06-09 | scripts | 2/0 | n/a | MANTER (base do grupo "criar skill") | Mais completa (scripts + evals + otimização de descrição). |
| criar-skills | 05-30 | ref | 0/0 | n/a | CONSOLIDAR → skill-creator | Versão PT enxuta da mesma função. |
| writing-skills | 05-29 | não | 0/0 | n/a | CONSOLIDAR → skill-creator | Duplica skill-creator e também o plugin `superpowers:writing-skills`. |
| writing-plans | 05-29 | não | 0/1 | n/a | CONSOLIDAR → superpowers:writing-plans | Duplicata exata de skill já existente no plugin superpowers. |
| brainstorming | 05-29 | não | 0/1 | n/a | CONSOLIDAR → superpowers:brainstorming | Duplicata exata de skill do plugin superpowers. |
| cowork-plugin-customizer | 05-29 | não | 0/0 | n/a | APOSENTAR | Duplica o plugin `cowork-plugin-management` (instalado 2×). |
| create-cowork-plugin | 05-29 | não | 0/0 | n/a | APOSENTAR | Duplica o plugin `cowork-plugin-management` (instalado 2×). |
| consolidate-memory | 06-09 | não | 0/0 | n/a | REVISAR | Nova (31 linhas); relação com plugin `productivity-prodam:memory-management` a definir. |
| schedule | 06-09 | não | 0/3 | n/a | MANTER | Agendamento de tarefas; citada por 3 skills. |
| setup-cowork | 06-09 | não | 0/0 | n/a | REVISAR | Onboarding do Cowork; **uso não verificável**. |

### Categoria E — Engeco (projeto NDA — fora do escopo PRODAM, mas coeso)

| Skill | Mod | Apoio | Cit (d/s) | Bloco | Veredito | Justificativa |
|---|---|---|---|---|---|---|
| engeco-nda-builder | 05-29 | não | 0/11 | n/a | MANTER (orquestrador do grupo NDA) | Monta a minuta + 9 anexos; citada por 11 skills do grupo. |
| gerar-minuta-nda-engeco | 05-29 | py+data | 0/2 | n/a | CONSOLIDAR → engeco-nda-builder | Também gera a minuta-padrão; sobreposição forte de gatilho ("gera o NDA"). |
| triage-nda | 05-29 | data+ref | 0/4 | n/a | MANTER | Triagem GO/NO-GO; rever gatilho "revisa esse contrato" (colide com review-contract). |
| review-contract | 05-29 | data+ref | 0/5 | n/a | MANTER | Revisão cláusula-a-cláusula + redline; fase distinta da triagem. |
| engeco-comparador-minutas | 05-29 | não | 0/4 | n/a | MANTER | Diff entre minutas; rever gatilho com checklist/review. |
| engeco-checklist-clausulas | 05-29 | não | 0/3 | n/a | MANTER | Gate de cláusulas obrigatórias; rever gatilho com comparador. |
| engeco-qualificacao-partes | 05-29 | não | 0/5 | n/a | MANTER | Bloco de qualificação das 5 SPEs. |
| engeco-extrator-cnpj-qsa | 05-29 | não | 0/1 | n/a | MANTER | Extrai qualificação do cartão CNPJ/QSA; complementa a anterior. |
| engeco-data-context-extractor | 05-29 | não | 0/2 | n/a | MANTER | Contexto canônico do projeto Engeco. |
| engeco-pesquisa-juridica-nda | 05-29 | não | 0/2 | n/a | MANTER | Biblioteca jurídica do NDA (citação verbatim). |
| engeco-resposta-incidente-lgpd | 05-29 | não | 0/2 | n/a | MANTER | Playbook de incidente LGPD (ANPD). |
| engeco-revogacao-procuracoes | 05-29 | não | 0/3 | n/a | MANTER | Workflow de encerramento/revogação de acessos. |
| engeco-controle-acessos-ecac | 05-29 | não | 0/3 | n/a | MANTER | Planilha de governança de acessos (Anexo I). |
| engeco-anexo-estadual-sefaz | 05-29 | não | 0/1 | n/a | MANTER | Anexo estadual SEFAZ; escopo próprio. |
| engeco-logos | 05-29 | assets | 0/0 | n/a | MANTER | Assets de marca das 5 SPEs; usada sob demanda (uso não verificável por citação, mas é biblioteca de assets). |
| validar-contraparte | 05-29 | py | 0/1 | n/a | MANTER | Valida CNPJ/QSA da contraparte; due diligence pré-NDA. |
| analyze | 05-29 | não | 1/5 | n/a | MANTER | Consulta a dados do projeto Engeco; citada e integrada. |
| signature-request | 05-29 | não | 0/0 | n/a | REVISAR | Roteamento de e-assinatura genérico; **uso não verificável**. |

### Categoria U — Utilitários genéricos (Anthropic/base)

| Skill | Mod | Apoio | Cit (d/s) | Bloco | Veredito | Justificativa |
|---|---|---|---|---|---|---|
| docx | 05-29 | 60 arq | 9/22 | n/a | MANTER | Essencial — geração de Word; a 2ª mais citada. |
| pdf | 05-29 | 11 arq | 7/23 | n/a | MANTER | Essencial — manipulação de PDF; muito citada. |
| xlsx | 05-29 | 53 arq | 5/23 | n/a | MANTER | Essencial — planilhas; muito citada. |
| pptx | 05-29 | 58 arq | 0/1 | n/a | MANTER | Essencial — apresentações. |
| brief | 05-29 | não | 3/5 | n/a | MANTER | Briefing jurídico diário; integrada. |
| python-pro | 05-29 | não | 1/6 | n/a | MANTER | Padrões Python; citada por 6 skills. |
| testing-qa | 05-29 | não | 3/6 | n/a | MANTER | QA de artefatos/scripts; citada. |
| code-review-excellence | 05-29 | não | 1/2 | n/a | MANTER | Revisão de código; citada no diagnóstico. |
| data-visualization | 05-29 | não | 0/1 | n/a | MANTER (base viz) | Gráficos Python (mais completa que create-viz). |
| create-viz | 05-29 | não | 0/0 | n/a | CONSOLIDAR → data-visualization | Mesma função (criar gráficos). |
| sql-queries | 05-29 | não | 0/2 | n/a | MANTER (base SQL) | SQL multi-dialeto (mais completa que write-query). |
| write-query | 05-29 | não | 0/0 | n/a | CONSOLIDAR → sql-queries | Mesma função (escrever SQL). |
| data-context-extractor | 05-29 | não | 0/3 | n/a | MANTER | Gera skill de contexto de dados; citada por 3. |
| legal-risk-assessment | 05-29 | não | 0/5 | n/a | REVISAR | Framework de risco genérico; citada por 5 — confirmar se usado no seu fluxo. |
| legal-response | 05-29 | não | 0/2 | n/a | REVISAR | Respostas a inquéritos legais (template genérico); **uso não verificável**. |
| compliance-check | 05-29 | não | 0/2 | n/a | REVISAR | Compliance genérico; sobrepõe compliance-contratual-prodam; **uso não verificável**. |
| vendor-check | 05-29 | não | 0/0 | n/a | REVISAR | Status de acordos com fornecedor; **uso não verificável**. |
| meeting-briefing | 05-29 | não | 0/0 | n/a | REVISAR | Sobrepõe `brief`; **uso não verificável**. |
| view-pdf | 05-29 | não | 0/0 | n/a | REVISAR | Visualizador interativo de PDF; **uso não verificável**. |
| validate-data | 05-29 | não | 0/0 | n/a | REVISAR | QA de análise genérico; sobrepõe QA jurídico; **uso não verificável**. |
| explore-data | 05-29 | não | 0/0 | n/a | REVISAR | Profiling de dataset; **uso não verificável**. |
| statistical-analysis | 05-29 | não | 0/0 | n/a | REVISAR | Métodos estatísticos; **uso não verificável**. |
| mcp-builder | 06-09 | scripts | 0/1 | n/a | REVISAR | Construção de MCP servers; **uso não verificável** no contexto jurídico. |
| web-artifacts-builder | 06-09 | ref | 0/0 | n/a | REVISAR | Artefatos web complexos (React/shadcn); **uso não verificável**. |
| webdev-quality-sprint | 06-09 | ref | 0/0 | n/a | REVISAR | Sprint de qualidade p/ projeto web; **uso não verificável**. |
| algorithmic-art | 06-09 | ref | 0/0 | n/a | REVISAR | Arte generativa p5.js; fora do escopo; **uso não verificável**. |

### Plugins (4 distintos)

| Plugin | Skills | Veredito | Observação |
|---|---|---|---|
| superpowers | 14 | MANTER | Recebe as consolidações de `brainstorming`, `writing-plans`, `writing-skills`. |
| productivity-prodam | 7 | REVISAR | Duplica funções de 4 skills standalone suas (SLA, registro, painel, memory) — decidir arquitetura. |
| cockroachdb | 33 | REVISAR + limpar | Banco distribuído; sem relação aparente com o trabalho jurídico. **Instalado 2× (idêntico)** — remover 1. |
| cowork-plugin-management | 2 | MANTER + limpar | **Instalado 2× (idêntico)** — remover 1; torna redundantes as standalone `create-cowork-plugin`/`cowork-plugin-customizer`. |

---

## Grupos de redundância

Para cada grupo: a **base recomendada** (a que sobrevive) e o que se funde nela.

1. **Atualização monetária** — `atualizacao-monetaria-creditos` (base: 463 linhas, em escala/polars, citada por 8) ⟵ `atualizacao-monetaria-sob-demanda` (memorial + SELIC/IGPM via API BCB). *Por que fundir:* duas lógicas de cálculo separadas é risco de valores divergentes na mesma cobrança. A base precisa absorver o "modo sob-demanda + memorial" e ganhar o bloco jurídico.

2. **Dossiê do devedor** — `montagem-dossie-comprobatorio` (base: 7 tipos de peça + cadeia 5 elos + classificação P1–P3) ⟵ `montagem-dossie-devedor-detalhado` (11 seções + saída docx/xlsx/json/md). *Por que fundir:* mesmo objetivo; a base é juridicamente mais ampla, a outra contribui o gerador multi-formato. **Decisão sua:** confirmar a base — a "detalhado" é maior em linhas (621), mas a "comprobatorio" é a integrada/citada.

3. **Pipeline por devedor** — `pipeline-devedor-completo` (base: 7 etapas, integra 12+ skills) ⟵ `workflow-pos-analise-devedor` (mesmas 7 etapas). `workflow-orchestrator` (genérico, 58 linhas) entra em REVISAR — provavelmente também absorvível.

4. **Tipografia do escritório** — `tipografia-juridica` (base: tem scripts + perfil Times p/ NDA) ⟵ `tipografia-juridica-gabriel` (vira perfil "Honorários/Gabriel"). *Nota:* `design-relatorio-quinzenal-prodam` é coisa distinta (identidade visual Brandão Ozores) — **não** fundir, só separar o gatilho.

5. **QA pré-envio** — `auditoria-documentos-juridicos` (base: 5 níveis) ⟵ `validacao-pos-geracao` (63 linhas, valida vs profiles.json). `guardrails-anti-alucinacao` fica separada (fact-check pré-geração), mas a fronteira entre as três precisa ficar explícita.

6. **Criar/editar skills** — `skill-creator` (base: scripts + evals) ⟵ `criar-skills` + `writing-skills`. Atenção: `writing-skills` também existe no plugin `superpowers` — escolher uma única fonte de verdade.

7. **NDA Engeco — geração de minuta** — `engeco-nda-builder` (base: minuta + 9 anexos) ⟵ `gerar-minuta-nda-engeco`.

8. **Duplicatas de plugin** — `brainstorming` → `superpowers:brainstorming`; `writing-plans` → `superpowers:writing-plans`; `create-cowork-plugin` + `cowork-plugin-customizer` → plugin `cowork-plugin-management`.

9. **Utilitários de dados** — `create-viz` → `data-visualization`; `write-query` → `sql-queries`.

---

## Conflitos de gatilho (descriptions que disparam juntas)

| Termo(s) em colisão | Skills que disputam o disparo | Ação proposta |
|---|---|---|
| "relatório quinzenal", "gerar relatório" | gerador-relatorio-quinzenal · design-relatorio-quinzenal-prodam | Separar: uma "gerar conteúdo", outra "formatar/design". |
| "montar dossiê", "compilar evidências", "preparar execução" | montagem-dossie-comprobatorio · montagem-dossie-devedor-detalhado | Consolidar (grupo 2). |
| "correção monetária", "SELIC", "juros de mora", "atualizar valor" | atualizacao-monetaria-creditos · atualizacao-monetaria-sob-demanda | Consolidar (grupo 1). |
| "reconhecimento", "Art. 202 VI", "FORTÍSSIMO/FORTE/MÉDIO" | reconhecimento-divida-tacito · revisar-reconhecimento-divida · marcos-interruptivos-prescricao | Definir fase: detectar / validar / interromper. |
| "workflow devedor", "processar devedor", "pós-análise", "etapas" | pipeline-devedor-completo · workflow-pos-analise-devedor · workflow-orchestrator | Consolidar (grupo 3). |
| "no meu padrão", "Dupincel", "tipografia do escritório", "estilo Gabriel" | tipografia-juridica · tipografia-juridica-gabriel | Consolidar (grupo 4). |
| "auditar documento", "validar para envio", "pré-envio", "anti-alucinação", "verificar fatos" | auditoria-documentos-juridicos · validacao-pos-geracao · guardrails-anti-alucinacao | Consolidar parte + delimitar fronteira (grupo 5). |
| "criar skill", "SKILL.md", "melhorar skill" | criar-skills · skill-creator · writing-skills (+ superpowers) | Consolidar (grupo 6). |
| "revisa esse contrato", "minuta", "NDA", "acordo de confidencialidade" | triage-nda · review-contract · engeco-comparador-minutas · engeco-checklist-clausulas · engeco-nda-builder · gerar-minuta-nda-engeco | Mapear por fase (triagem → comparação → checklist → revisão → geração); consolidar geração (grupo 7). |
| "compliance", "contrato", "cláusula" | compliance-check · compliance-contratual-prodam | Manter a PRODAM; rever a genérica. |
| "validar dados", "QA da análise", "qualidade" | validate-data · validacao-pos-geracao · auditoria-base-dados-camadas | Delimitar dados vs documento jurídico. |
| "prazo", "SLA", "alerta", "vencimento" | controle-sla-alertas · **plugin** productivity-prodam:alerta-prazos | Escolher um (skill × plugin). |
| "registrar interação/ação", "devedor respondeu" | registro-interacoes-devedor · **plugin** productivity-prodam:registro-acao-devedor | Escolher um (skill × plugin). |
| "próximo passo", "painel", "o que fazer" | proximo-passo-advisor · **plugin** productivity-prodam:painel-devedores | Escolher um (skill × plugin). |
| "memória", "consolidar memória" | consolidate-memory · **plugin** productivity-prodam:memory-management | Escolher um (skill × plugin). |
| "brainstorm" | brainstorming · **plugin** superpowers:brainstorming | Consolidar no plugin. |
| "SQL", "query" | sql-queries · write-query | Consolidar (grupo 9). |
| "gráfico", "visualização", "viz" | create-viz · data-visualization | Consolidar (grupo 9). |
| "briefing" | brief · meeting-briefing | Manter `brief`; rever `meeting-briefing`. |

---

## Candidatas a aposentar / "uso não verificável"

**Aposentar (duplicação confirmada, não por falta de uso):**
- `cowork-plugin-customizer`, `create-cowork-plugin` — função já entregue pelo plugin `cowork-plugin-management` (instalado, e em duplicidade).

**Uso não verificável (0 citações em docs e 0 em outras skills) — NÃO afirmo que estão sem uso; você pode invocá-las manualmente. Recomendo decidir caso a caso:**

- *Genéricas fora do núcleo jurídico:* `algorithmic-art`, `web-artifacts-builder`, `webdev-quality-sprint`, `mcp-builder`, `statistical-analysis`, `explore-data`, `view-pdf`.
- *"Legal ops" genéricas (template) que podem ser redundantes com suas skills PRODAM/Engeco:* `legal-response`, `legal-risk-assessment`, `compliance-check`, `vendor-check`, `signature-request`, `meeting-briefing`, `validate-data`.
- *PRODAM sem citação:* `prodam-data-analyst` (parece base de contexto — pode estar sendo "lida" sem ser citada; confirmar).
- *Cowork/meta novas:* `setup-cowork`, `consolidate-memory`.

> Nenhuma destas foi marcada APOSENTAR só por falta de citação — todas estão em REVISAR, porque ausência de citação ≠ ausência de uso.

---

## Bloco jurídico obrigatório (FONTE JURÍDICA OBRIGATÓRIA)

**Padrão de referência:** seu `PRODAM_DOCS\_SKILLS\FONTE_JURIDICA_SKILL_UPDATES_SPEC.md` (07/04/2026), que exige a seção `## FONTE JURÍDICA OBRIGATÓRIA` logo após o frontmatter em 12 skills críticas.

**Situação real no disco (verificada agora):**
- **26 skills ativas têm o bloco** — inclusive várias além das 12 do spec (a implementação foi mais longe que o documento original previa).
- **Das 12 do spec, 10 têm o bloco. Faltam exatamente 2 — e são as mais críticas:**
  - 🔴 `prodam-juridico` (skill "advogado sênior" — referencia a SSOT internamente, mas **sem o bloco padrão**).
  - 🔴 `proximo-passo-advisor` (decide a via de cobrança — **sem o cabeçalho padrão**, embora já tenha o aviso "NUNCA citar" e uma tabela de precedentes verificados soltos).
- **Outras jurídicas substantivas do PRODAM sem o bloco** (candidatas a padronizar, além das 12 do spec): `atualizacao-monetaria-creditos`, `classificacao-forca-probatoria`, `marcos-interruptivos-prescricao`, `reconhecimento-divida-tacito`, `revisar-reconhecimento-divida`, `validador-cadeia-documental-fatura`, `geracao-documentos-juridicos`, `extracao-clausulas-contratuais`, `montagem-dossie-comprobatorio`.
- ✅ **Precedentes fabricados:** os 3 (REsp 1.014.496/SC, REsp 2.792.731/SP, TJ-AM 2008.000901-9) aparecem em ~28 skills **somente como alerta "NUNCA citar"** — verifiquei e **não há citação afirmativa**. Comportamento correto.

> Não inventei nenhuma referência. A lista de consolidados que cada skill deveria citar já está no seu spec; a decisão de aplicar (e em quais skills além das 12) é sua.

---

## Lista enxuta final proposta

Saindo de **106 → ~92 skills ativas** (12 consolidações + 2 aposentadorias), mais decisões de REVISAR. Sobrevivem:

- **Jurídico PRODAM (núcleo):** aceite-tecnico-catalogador, arvore-decisao-contestacao, **atualizacao-monetaria** (unificada), blindagem-pre-execucao, certidoes-estrategia, classificacao-forca-probatoria, compensacao-administrativa-workflow, compliance-contratual-prodam, desconsideracao-pj-checklist, extracao-clausulas-contratuais, geracao-documentos-juridicos, marcos-interruptivos-prescricao, **montagem-dossie** (unificada), nota-empenho-classificador, nota-liquidacao-extrator, precatorios-rpv-fragmentacao, prodam-juridico, protesto-estrategico, proximo-passo-advisor, reconhecimento-divida-tacito, recuperacao-creditos-empresas-privadas, revisar-reconhecimento-divida, risco-processual-matriz, validador-cadeia-documental-fatura.
- **Dados/SPCF:** auditoria-base-dados-camadas, auditoria-completude-devedor, integracao-dados-novos-spcf, normalizador-valores-brl, ocr-pdfs-prodam, rastreamento-procedencia-dados, reconciliacao-spcf-pipeline.
- **Relatório/Documento:** design-relatorio-quinzenal-prodam, gerador-relatorio-quinzenal, **tipografia-juridica** (unificada), build-dashboard.
- **Governança/QA:** protocolo-juridico-prodam, auditoria-documentos-juridicos (absorve validacao-pos-geracao), guardrails-anti-alucinacao, **pipeline-devedor-completo** (absorve workflow-pos-analise), contexto-projeto-manutencao, sync-skills-prodam, triagem-consistencia-versoes, rastreamento-qualidade-prompts.
- **Documentos (ferramentas):** docx, pdf, pptx, xlsx.
- **Dados/eng (genéricas usadas):** sql-queries, data-visualization, data-context-extractor, python-pro, testing-qa, code-review-excellence, brief, build-dashboard, schedule.
- **Criação:** skill-creator.
- **Engeco (bloco coeso):** as 17 skills engeco-*/analyze/triage-nda/review-contract/validar-contraparte (com `engeco-nda-builder` absorvendo `gerar-minuta-nda-engeco`).
- **A decidir (REVISAR):** controle-sla-alertas e registro-interacoes-devedor (vs plugin productivity-prodam); workflow-orchestrator; e o bloco de "uso não verificável" acima.

---

## Plano de ação — o que faço exatamente quando você aprovar

Nada abaixo será executado sem o seu "OK", item a item. Em todos os casos: **crio versão nova / movo para uma pasta de quarentena com data — nunca apago o original**, e mantenho backup.

**Consolidações (12):**
1. `atualizacao-monetaria-sob-demanda` → mesclo o "modo sob-demanda + memorial BCB" dentro de `atualizacao-monetaria-creditos`; ajusto a description para um só gatilho; movo a antiga para quarentena.
2. `montagem-dossie-devedor-detalhado` → incorporo as 11 seções/saída multi-formato em `montagem-dossie-comprobatorio`.
3. `workflow-pos-analise-devedor` → incorporo em `pipeline-devedor-completo`.
4. `tipografia-juridica-gabriel` → vira "perfil Gabriel/Honorários" dentro de `tipografia-juridica`.
5. `validacao-pos-geracao` → incorporo em `auditoria-documentos-juridicos`.
6. `criar-skills` + `writing-skills` → incorporo em `skill-creator`.
7. `gerar-minuta-nda-engeco` → incorporo em `engeco-nda-builder`.
8. `brainstorming`, `writing-plans` → removo as standalone, passo a usar as do plugin `superpowers`.
9. `create-viz` → incorporo em `data-visualization`; `write-query` → incorporo em `sql-queries`.

**Aposentadorias (2):** `cowork-plugin-customizer`, `create-cowork-plugin` → quarentena (função coberta pelo plugin).

**Limpeza de plugin:** remover a 2ª cópia idêntica de `cockroachdb` e de `cowork-plugin-management`.

**Bloco jurídico:** aplicar a seção `FONTE JURÍDICA OBRIGATÓRIA` (texto do seu spec) primeiro em `prodam-juridico` e `proximo-passo-advisor`, depois nas 9 jurídicas substantivas listadas — **só após você confirmar** o escopo e os consolidados de cada uma.

**Drift no disco (opcional, alto valor de organização):** propor mover `_WORKFLOW_IMPORTADO`, `_SKILLS` staging e `_SKILLS_NOVAS_*` para um único `_ARCHIVE_SKILLS_<data>` — **com sua confirmação**, sem tocar em PDFs/provas.

---

## O que preciso que você verifique (não presumi)

1. **Base de cada consolidação sensível:** confirmar se a base do dossiê é `montagem-dossie-comprobatorio` (minha recomendação) e do pipeline é `pipeline-devedor-completo`.
2. **Plugin productivity-prodam × skills standalone:** você quer manter o **plugin** (alerta-prazos/registro/painel/memory) e aposentar as standalone equivalentes, ou o contrário? Hoje os dois coexistem.
3. **Skills "legal ops" genéricas** (`legal-response`, `legal-risk-assessment`, `compliance-check`, `vendor-check`, `signature-request`): fazem parte do seu fluxo ou são resíduo do pacote padrão?
4. **`prodam-data-analyst`** e demais "uso não verificável": alguma é lida/usada de forma que não aparece em citação?
5. **Escopo do bloco jurídico:** além das 12 do spec, quer padronizar as outras 9 que listei?
6. **cockroachdb:** tem uso real? Se não, é a maior economia de ruído (33 skills ×2).

---

_Documento gerado em modo somente-análise. Nenhum arquivo de skill foi criado, movido, editado ou apagado nesta sessão._

