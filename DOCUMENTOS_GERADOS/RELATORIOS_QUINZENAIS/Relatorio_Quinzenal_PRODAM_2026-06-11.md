# Relatório Quinzenal nº [005/2026] — Contrato 002/2026

## Recuperação de Créditos — PRODAM S.A. × Brandão Ozores Advogados

**Cliente:** PRODAM — Processamento de Dados Amazonas S.A. (CNPJ 04.407.920/0001-80)  
**Contratante:** Brandão Ozores Advogados  
**Elaboração:** Gabriel Mar — OAB/AM 15.697  
**Período de referência:** [28/05/2026 a 11/06/2026]  
**Data de emissão:** 11/06/2026  

---

## 1. Sumário Executivo

O portfólio sob gestão compreende 69 devedores, com crédito exigível de R$ 83.668.078,44 e valor atualizado de R$ 125.245.390,64 (65/69 devedores com atualização monetária calculada). O universo de faturas soma 3477 documentos: 2326 exigíveis, 1082 prescritas e 69 fora do universo de cobrança (canceladas/excluídas). (*)

Destaques da quinzena: (i) restauração do arquivo-mestre de dados do portfólio (profiles.json), detectado corrompido em 10/06, com validação integral pós-restauração; (ii) recálculo das datas de prescrição, individualizando prazos antes registrados com data-placeholder; (iii) organização não-destrutiva de todo o acervo documental (70.298 cópias verificadas por hash MD5); e (iv) início do memorial preliminar de cálculo da SEDUC, maior crédito do portfólio (R$ 49,2 milhões exigíveis), em andamento nesta data.

Pontos de atenção imediata: SSP e SUHAB têm prescrição projetada para 30/06/2026 (seção 3). Não houve recuperação de valores no período.

## 2. Panorama do Portfólio

### 2.1 Composição por categoria, força probatória e fase

| Categoria | Devedores |
|---|---|
| Governo — Adm. Direta | 26 |
| Governo — Adm. Indireta | 21 |
| Empresas Privadas | 22 |

| Força probatória | Devedores |
|---|---|
| FORTE | 12 |
| MÉDIA | 15 |
| FRACA | 42 |

| Fase do pipeline | Devedores |
|---|---|
| F0 (diagnóstico/documentação) | 51 |
| F0_DIAGNOSTICO | 4 |
| F3 (TRD) | 9 |
| F5 (petição pronta) | 5 |

### 2.2 Pipeline — próximo passo por devedor

| Próximo passo | Devedores |
|---|---|
| ANALISAR_DOCUMENTACAO | 36 |
| CLASSIFICAR | 17 |
| ENVIAR_TRD | 9 |
| PROTOCOLAR_PETICAO | 5 |
| AVALIAR_SUCESSAO | 1 |
| HABILITAÇÃO DE CRÉDITO | 1 |

### 2.3 Cinco maiores devedores (por valor exigível)

| Devedor | Exigível | Atualizado | Força | Próximo passo | Prescrição |
|---|---|---|---|---|---|
| SEDUC | R$ 49.215.512,48 | R$ 50.263.263,56 | FORTE | ANALISAR_DOCUMENTACAO | 751 dias |
| SES/SUSAM | R$ 4.783.356,52 | R$ 8.230.061,40 | FORTE | ENVIAR_TRD | 112 dias |
| SSP | R$ 4.553.230,80 | R$ 29.034.062,63 | FORTE | PROTOCOLAR_PETICAO | 🔴 30/06/2026 |
| SEJUSC | R$ 2.589.660,12 | R$ 5.262.537,82 | MÉDIA | ANALISAR_DOCUMENTACAO | 🟡 31/08/2026 |
| SEAD | R$ 2.339.702,20 | R$ 4.296.278,76 | FORTE | ENVIAR_TRD | 477 dias |

Lista completa dos 69 devedores em STATUS_DEVEDORES.md (anexo de referência, seção 6).

## 3. Alertas de Prescrição

A prescrição é apurada por fatura individual, contada do vencimento (arts. 189 e 206, §5º, I, do Código Civil). Os marcos abaixo são as datas críticas registradas na base do projeto:

| Devedor | Data crítica | Valor exigível | Providência |
|---|---|---|---|
| 🔴 SSP | 30/06/2026 | R$ 4.553.230,80 | Petição pronta (fase F5). Protocolar antes do prazo, com blindagem pré-execução, checklist de 20 itens e verificação das exceções do Decreto Estadual AM nº 53.464/2026 (art. 1º, §§1º–4º). |
| 🔴 SUHAB | 30/06/2026 | R$ 840.061,15 | Em ANALISAR_DOCUMENTACAO. Acelerar análise e adotar medida interruptiva da prescrição antes do prazo. |
| 🟡 SEJUSC | 31/08/2026 | R$ 2.589.660,12 | Concluir análise documental até o prazo. |
| 🛡️ DETRAN | marco interruptivo | — | Protegido por marco interruptivo (Art. 202, VI, CC) com data registrada no passado — marco prevalece; reconfirmar e atualizar a data. Monitorar cutoff da NF 110654 (CT 179/2018): 19/08/2026. |

> 🔴 **ATENÇÃO: SSP (R$ 4.553.230,80) e SUHAB (R$ 840.061,15) prescrevem em 30/06/2026 — ação interruptiva impreterível dentro do mês corrente.**

9 devedores sem data de prescrição registrada (AADESAM, BRADESCO, CASA MILITAR, CGE, FJJA, FMPES, SEJEL, SETRAB, UGPI) — levantamento de vencimentos pendente.

## 4. Ações Realizadas na Quinzena

Período de referência: [28/05/2026 a 11/06/2026]. Relacionam-se apenas fatos com registro nos arquivos do projeto (fonte indicada entre parênteses); itens sem registro documental estão marcados "[a confirmar com o advogado]".

### 4.1 Gestão do portfólio e prescrição

- 09/06 — Diagnóstico integral do portfólio (somente leitura): mapeamento pronto × pendente por devedor, identificação de 14 devedores acionáveis (5 com petição pronta, 9 com TRD pronto/recomendado), gaps de reconciliação SPCF × exigível e priorização P1–P7 com a SSP em primeiro lugar (fonte: HISTORICO_SESSOES.md, sessão 09/06 tarde).
- 09/06 — Recálculo das datas de prescrição no profiles.json: cerca de 30 devedores saíram da data-placeholder 2026-03-20 para datas individualizadas, com backup pré-recálculo preservado; a metodologia do recálculo segue em conferência (fonte: relatorios/sessoes/REGISTRO_SESSAO_2026-06-10_panorama_dashboard_relatorio.md).
- 10/06 — Panorama do portfólio com números conferidos entre profiles.json, TASKS.md e STATUS_DEVEDORES.md; geração de dashboard HTML autocontido e de minuta de relatório quinzenal em .docx (documento de gestão, datado de 10/06); o envio desse documento à PRODAM está [a confirmar com o advogado] (fontes: REGISTRO_SESSAO_2026-06-10_panorama_dashboard_relatorio.md; TASKS.md, pendências de sessão).
- 10/06 — Programação de 3 alertas pontuais de prazo: 24/06 (prescrição SSP + SUHAB em 30/06), 01/08 (SEJUSC em 31/08) e 05/08 (DETRAN — marco interruptivo e cutoff NF 110654 em 19/08) (fonte: REGISTRO_SESSAO_2026-06-10_panorama_dashboard_relatorio.md, seção 4).

### 4.2 Integridade de dados e acervo documental

- 28/05 — Saneamento de qualidade de código e dados (3 commits): eliminação de usos de float em valores monetários (regra Decimal), consolidação dos helpers de formatação BRL e auditoria forense da reversão de drift de 13/05 no profiles.json, com 113 testes automatizados aprovados (fonte: HISTORICO_SESSOES.md, sessão 28/05).
- 10/06 — Detecção e restauração do profiles.json (SSOT) corrompido/truncado: restaurado a partir de snapshot íntegro de 09/06, com backup do arquivo corrompido preservado e validação pós-restauração (69 devedores; soma R$ 83.668.078,44); satélites do projeto (CLAUDE.md, STATUS_DEVEDORES.md) regenerados às 17:45 (fontes: REGISTRO_SESSAO_2026-06-10_panorama_dashboard_relatorio.md; cabeçalho do CLAUDE.md).
- 10/06 — Organização não-destrutiva do acervo completo do projeto: 91.256 arquivos inventariados (32,4 GB), 70.298 cópias organizadas por devedor/tipo com verificação de integridade MD5 em 100% das cópias, 20.958 duplicatas exatas identificadas (não recopiadas) e manifesto auditável de 91.256 linhas; originais intactos (fonte: relatorios/sessoes/RELATORIO_ORGANIZACAO_2026-06-10.md).
- 10/06 — DETRAN (Sessão 2): renomeação forense de 229 CSVs do subprojeto DETRAN_AUDITORIA_COMPLETA com hash MD5 pré-ação, índice de auditoria (CSV+JSON) e rollback integral possível; nenhum PDF tocado; alterações sincronizadas com o GitHub (commit 031b20a0) (fonte: relatorios/sessoes/SESSAO_2026-06-10_sessao2-detran-renomeacao-csvs.md).
- 09/06 — Organização da pasta "Arquivos Principais Projeto PRODAM" em modo cópia (16 arquivos copiados com conferência MD5; 3 duplicatas detectadas), com identificação documental relevante: o PDF "Canal Comunicação Oficial" é, na verdade, o Ofício PRESI/045/2026 da PRODAM (resposta ao Ofício 001/2026), reclassificado para a pasta de ofícios (fonte: HISTORICO_SESSOES.md, sessão 09/06 — organizador-arquivos-prodam).

### 4.3 Ferramentas e governança interna

- 09/06 — Auditoria de leitura das 106 skills ativas do ecossistema do projeto, com veredito individual (61 manter · 12 consolidar · 2 aposentar · 31 revisar), checagem de que nenhuma skill cita os precedentes catalogados como fabricados e mapeamento das cópias legadas que geram drift (fonte: AUDITORIA_SKILLS_2026-06-09.md).
- 09/06 — Criação, validação (evals) e indexação da skill organizador-arquivos-prodam (organização por devedor com cruzamento no profiles.json, detecção de duplicatas por MD5 e modo cópia não-destrutivo) (fontes: HISTORICO_SESSOES.md; relatorios/sessoes/SESSAO_2026-06-09_organizador-arquivos-prodam.md).
- 09–10/06 — Hub do projeto no Notion: página central, database com os 69 devedores (valores em BRL), 3 visões (pipeline, alertas de prescrição, fases) e sincronização diária agendada a partir dos satélites do projeto (fonte: relatorios/sessoes/SESSAO_2026-06-10_notion-hub-conexoes.md).
- 09/06 — Atualização do plugin de produtividade do projeto (v1.0.0 → v1.1.0): sincronizado de 51 para 69 devedores, dashboard refeito com KPIs reais e correções de comandos quebrados (fonte: HISTORICO_SESSOES.md, sessão 09/06 — productivity-prodam).
- 08/06 — Instalação isolada (pipx) da ferramenta de análise estática Semgrep no ambiente Windows e restauração do pipeline forense de dependências Python afetado por instalação global anterior (fonte: HISTORICO_SESSOES.md, sessão 08/06).

### 4.4 Em andamento nesta data (11/06/2026)

- SEDUC — Memorial preliminar de cálculo em elaboração sobre o universo recente do SPCF (106 faturas; base R$ 54.535.717,29), com atualização monetária pela SELIC/EC 113 até a competência 04/2026 e ressalvas expressas de regime presumido (índice contratual por contrato ainda em confirmação).
- SEDUC — Plano de auditoria documental do acervo (DPCON, pendrive e SPCF) em elaboração, para suprir a cadeia probatória (Contrato + NE + NF + Atesto) do maior crédito do portfólio.

### 4.5 Registro negativo (transparência)

- Não há, nos arquivos do repositório relativos ao período, registro de protocolos judiciais, notificações extrajudiciais enviadas a devedores ou reuniões externas nesta quinzena [a confirmar com o advogado].

## 5. Próximos Passos

- **SSP — até 30/06/2026 (crítico)** — Protocolar a petição pronta antes da prescrição de 30/06/2026 (R$ 4.553.230,80 em risco): rodar blindagem pré-execução, checklist de 20 itens e verificar as exceções do Decreto Estadual AM nº 53.464/2026 (art. 1º, §§1º–4º).
- **SUHAB — até 30/06/2026 (crítico)** — Acelerar a análise documental e adotar medida interruptiva da prescrição antes de 30/06/2026 (R$ 840.061,15 em risco).
- **SEDUC — maior crédito (R$ 49,2 mi)** — Finalizar o memorial preliminar de cálculo (106 faturas SPCF; SELIC/EC 113 até 04/2026) e executar o plano de auditoria documental do acervo (DPCON/pendrive/SPCF), inclusive reconciliação da divergência SPCF × exigível apontada no diagnóstico de 09/06.
- **DETRAN — destravar protocolo** — Obter a revisão da Notificação v5 e do briefing pelo Dr. Fábio; reduzir o Ofício LAI 003/2026 de 4 para 2 contratos; reconciliar o exigível R$ 0,00 do perfil-mãe com o valor canônico R$ 28.196.572,22 do subprojeto; monitorar o cutoff prescricional da NF 110654 (19/08/2026).
- **SES/SUSAM e SEAD — TRDs** — Emitir e enviar os Termos de Reconhecimento de Dívida (SES/SUSAM: R$ 4.783.356,52, prescrição em ~112 dias; SEAD: R$ 2.339.702,20).
- **SEJUSC — até 31/08/2026** — Concluir a análise documental (R$ 2.589.660,12).
- **Higiene de dados** — Levantar vencimentos dos 9 devedores sem data de prescrição registrada; conferir a metodologia do recálculo de prescrição de 09/06; investigar a causa do truncamento do profiles.json e adotar escrita atômica com validação.
- **Obrigação contratual** — Manter a cadência dos relatórios quinzenais à PRODAM (multa contratual de R$ 500,00/dia de atraso).

## 6. Anexos e Referências

Documentos e bases que lastreiam este relatório (disponíveis no repositório do projeto):

- PRODAM_DOCS/profiles.json — SSOT dos devedores (restaurado em 10/06/2026; fora deste repositório).
- CLAUDE.md e STATUS_DEVEDORES.md — satélites regenerados em 10/06/2026 17:45 (KPIs, alertas e pipeline).
- TASKS.md — prazos críticos e fila por próximo passo (gerado em 09/06/2026).
- HISTORICO_SESSOES.md — registro das sessões de 28/05 a 10/06/2026.
- relatorios/sessoes/REGISTRO_SESSAO_2026-06-10_panorama_dashboard_relatorio.md — panorama, dashboard e restauração do SSOT.
- relatorios/sessoes/SESSAO_2026-06-10_sessao2-detran-renomeacao-csvs.md — renomeação forense de 229 CSVs DETRAN.
- relatorios/sessoes/RELATORIO_ORGANIZACAO_2026-06-10.md — organização não-destrutiva do acervo (70.298 cópias).
- relatorios/sessoes/SESSAO_2026-06-10_notion-hub-conexoes.md — hub Notion e sincronização diária.
- relatorios/sessoes/SESSAO_2026-06-09_organizador-arquivos-prodam.md — skill de organização de arquivos.
- AUDITORIA_SKILLS_2026-06-09.md — auditoria das 106 skills ativas.
- relatorios/CHANGELOG_SESSAO_2026-04-29_design_brandao_ozores.md — decisão institucional sobre assinaturas (29/04/2026).

### Nota de rodapé

(*) Conferência de KPIs: o único profiles.json disponível neste clone do repositório (_ARQUIVO/Melhorar ainda mais esse dashboard/profiles.json) é um snapshot antigo e diverge da SSOT viva — soma 70 registros, R$ 121.512.497,26 exigível, R$ 195.448.326,85 atualizado e 2958 faturas (1873 exigíveis / 1085 prescritas). Os números do corpo deste relatório seguem os satélites oficiais regenerados em 10/06/2026 17:45 a partir do SSOT restaurado (CLAUDE.md / STATUS_DEVEDORES.md). Antes do envio, revalidar os KPIs contra o PRODAM_DOCS/profiles.json vivo [a confirmar com o advogado].


---

**Gabriel Mar**  
OAB/AM 15.697  
Gabriel Mar Sociedade Individual de Advocacia
