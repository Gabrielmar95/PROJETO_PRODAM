# Histórico de Sessões — PROJETO PRODAM

## 2026-06-09 (tarde) — Diagnóstico do portfólio (projeto-mãe × subprojetos): pronto vs. pendente, gaps e priorização

Sessão de diagnóstico, **somente leitura** (nenhum arquivo de dado alterado). Objetivo: a partir do estado real do projeto-mãe e dos subprojetos por devedor, (1) mapear pronto vs. pendente por devedor (fase F0–F9, próximo passo, prescrição), (2) achar gaps/divergências entre fontes, (3) propor próximos passos priorizados (prescrição > valor > força > impacto) e (4) indicar skill + entregável por passo.

### Método

- Lidos os dados **reais**: `PRODAM_DOCS/profiles.json` (SSOT, mtime 13/05/2026) e `prodam.db` (raiz, mtime 07/05/2026), via scripts Python ad-hoc no sandbox (sem gravar no disco do projeto).
- Conferência de schema por devedor (val_exig, val_atualizado, forca_probatoria, fase_atual, proximo_passo, data_prescricao_proxima, reconciliacao_status/divergencia_pct, titulo_executivo, valor_canonico).

### Números conferidos (não presumidos)

- **69 devedores** · **R$ 83.668.078,44 exigível registrado** · R$ 125.245.390,64 atualizado · **R$ 0,00 recuperado**.
- Categoria: 26 Gov Direta · 21 Gov Indireta · 22 Privadas. Força: 12 FORTE · 15 MÉDIA · 42 FRACA.
- Fase: 51 F0 · 4 F0_DIAGNOSTICO · 9 F3 · 5 F5 → **só 14 (20%) saíram do diagnóstico**.
- Próximo passo: 36 ANALISAR_DOCUMENTACAO · 17 CLASSIFICAR · 9 ENVIAR_TRD · 5 PROTOCOLAR_PETICAO · 1 HABILITAÇÃO · 1 AVALIAR_SUCESSAO (bate com o `CLAUDE.md` auto-gerado).

### Pronto vs. pendente

- **Acionáveis agora (14):** F5 "Petição pronta" = SSP, DETRAN, SEAS, FHAJ, FUAM/FUHAM. F3 "TRD pronto/recomendado" = SES/SUSAM, SEAD, IPAAM, FCECON, SEINFRA, FMT, IDAM, CBMAM, FHEMOAM.
- **Maior crédito parado:** **SEDUC — R$ 49.215.512,48, FORTE, mas em F0/ANALISAR_DOCUMENTACAO** (e com 44,8% de divergência).
- **55 devedores ainda em F0** (diagnóstico/classificação).

### Gaps e divergências encontrados (coração do diagnóstico)

1. **DETRAN entra com `val_exig = 0` no master** — seu valor vive em `valor_canonico = R$ 28.196.572,22`. O total de R$ 83,67M **subestima o portfólio**; o exigível real é da ordem de **R$ 111,9M**. O `CLAUDE.md` auto-gerado **herda o mesmo erro** no headline.
2. **Reconciliação SPCF × exigível: 48 de 69 (70%) com status CRITICAL (32) ou MAJOR (16)**; só 12 MATCH. Extremos: SEMIG/CASA CIVIL/COSAMA/CASA MILITAR 100%, SAFRA 125%, SNPH 165%. **Inclui SEDUC (44,8%), SES (47,0%) e SEAD (90,9%)** → `val_exig` desses não é confiável para petição.
3. **`prodam.db` (07/05) defasado vs SSOT (13/05)** — 6 dias. O DB da raiz mostra `spcf_faturas = 1.837`, enquanto a nota do subprojeto DETRAN registra 1.927 pós-sync → **este DB pode não ser o mais recente** (compatível com o incidente de drift de 07/05).
4. **Prescrição não individualizada:** **22 devedores compartilham a data placeholder `2026-03-20`** (já vencida há 81 dias), 17 como `None`, 17 em `2029-10-01`. Como prescrição é por fatura (Art. 189 + 206 §5º I CC), data única para 22 órgãos é impossível ser real. Só SES/SUSAM (recalc. 12/05), SSP (30/06), SEJUSC (31/08) e ADS (12/04) têm data com algum lastro.
5. **Cobertura documental rasa:** só **5/69** com `cruzamento_empenho_completo`; só **17/69** com CSV de faturas; só **2 títulos executivos** formados.

### Priorização proposta (prescrição > valor > força > impacto)

- **P1 SSP** — prescrição ~30/06 (~21 dias), R$ 4,55M, FORTE, petição pronta → protocolar. Skills: `blindagem-pre-execucao` → `auditoria-documentos-juridicos` → `geracao-documentos-juridicos`.
- **P2 DETRAN** — R$ 28,2M, petição pronta; cutoff real NF 110654 = 19/08. Destravar revisão Dr. Fábio + reduzir Ofício LAI p/ 2 contratos.
- **P3 SES/SUSAM** — ~30/09 (~113d), R$ 4,78M; confirmar se TRD já foi protocolado (há `TRD_protocolo_20260513.pdf`, mas `proximo_passo` ainda diz ENVIAR_TRD).
- **P4 SEDUC** — maior valor, F0, div. 44,8% → reconciliar antes. Skills: `reconciliacao-spcf-pipeline` + `auditoria-completude-devedor` + `pipeline-devedor-completo`.
- **P5 SEJUSC** — ~31/08 (~83d), R$ 2,59M, ainda F0.
- **P6 SEAD** — TRD pronto, mas div. 90,9% → reconciliar antes do TRD.
- **P7** — lote F5/F3 menores (SEAS, FHAJ, IPAAM, FCECON, FMT, IDAM, FUAM, CBMAM, FHEMOAM).
- **Transversal** — recalcular prescrição por fatura dos acionáveis e ressincronizar `prodam.db`.

### A verificar (sinalizado ao usuário, não presumir)

- Prescrição real fatura a fatura de SSP/DETRAN/SES/SEJUSC/SEDUC (base traz placeholder; mesmo SSP tem `metodologia = None`).
- SES/SUSAM: TRD já protocolado em 13/05 ou não? (contradição com `proximo_passo`).
- Qual `profiles.json` é o SSOT hoje (master `PRODAM_DOCS/` × `11_PROFILES_BACKUPS/ativo/` do DETRAN) e se o DETRAN (R$ 28,2M) deve somar ao total.
- Ressync `prodam.db` (07/05 → 13/05) antes de citar número do banco.
- Decreto AM 53.464/2026 (4 exceções) por órgão antes de execução contra Gov AM.
- Índices de correção por contrato (não há arquivo-SSOT; conferir cláusula econômica).

### Estado final

- Diagnóstico entregue no chat; **nada gravado em dados** (profiles.json/db intactos). Decisão pendente do usuário: começar pelo **P1 (SSP)** ou primeiro **recalcular prescrição por fatura** dos acionáveis. Oferta de salvar o diagnóstico como relatório formatado em aberto.

---

## 2026-06-09 — Skill `organizador-arquivos-prodam` (File Organizer): criação, uso e indexação

Sessão de produto + operação. Criada do zero, via `skill-creator`, uma skill de organização de arquivos para o projeto; depois usada para organizar um acervo real e registrada no índice.

### Skill criada e instalada
- **Local:** `PRODAM_DOCS/_SKILLS/organizador-arquivos-prodam/` (`SKILL.md`, `scripts/planejar_organizacao.py`, `references/convencoes_prodam.md`, `evals/`).
- **Função:** organiza POR DEVEDOR (cruza nomes com `profiles.json` via `match_flex`/`norm_variants` do `prodam_utils`, com fallback stdlib), detecta DUPLICATAS exatas (hash MD5) e drift, e renomeia de forma conservadora no padrão PRODAM (sem inventar nº de contrato/NE/NF).
- **Segurança:** modo CÓPIA não-destrutivo — nunca apaga nem move originais (PDFs = provas); dry-run é o padrão (gera só manifesto JSON+CSV+XLSX); só copia com `--aplicar`, conferindo MD5 destino×origem; colisão de nome vira `_dup-NN`.
- **Bugs corrigidos em teste:** (a) "EXECUÇÃO" isolado classificava como PETIÇÃO (pegava "regime/blindagem de execução") → restringido a EXECUÇÃO FISCAL/DE TÍTULO/CUMPRIMENTO DE SENTENÇA/MONITÓRIA/EMBARGOS; (b) `_ . -` passam a ser tratados como separadores (senão `\b` não casava em "OFICIO_E...").

### Validação (evals + subagentes)
- 3 execuções de teste (2 com a skill, 1 baseline sem) sobre cópias descartáveis de pastas reais. Com a skill: organização padronizada + manifesto auditável + cruzamento com `profiles.json`. Baseline sem skill: estrutura ad-hoc não reproduzível, ~250s vs 144s. Eval viewer estático gerado para revisão humana.

### Organização executada — "Arquivos Principais Projeto PRODAM"
- Saída em `_ORGANIZADO/` na própria pasta (originais intactos: 19). **16 copiados** (MD5 16/16, 0 falhas) + **3 duplicatas** puladas.
- **Item 1 (reclassificação):** dos 18 "não identificados", só 1 era de devedor — Notificação Extrajudicial 001/2026 ao DETRAN → movida para `DETRAN/`. Os 17 restantes são institucionais do Contrato 002/2026 (BOA×PRODAM) → balde renomeado `_INSTITUCIONAL_CONTRATO-002-2026`.
- **Item 2 (duplicatas, conteúdo conferido nos PDFs):** "Canal Comunicação Oficial.pdf" é, na verdade, o **Ofício PRESI/045/2026 da PRODAM** (resposta ao Ofício 001/2026) → reclassificado para `06_OFICIOS`; o par "PROCURAÇÃO PROTOCOLO VIRTUAL"/"COBRANÇA DETREAN" = a notificação ao DETRAN; `Relatorio_Quinzenal_003_2026ass (1).pdf` = cópia de download. Versões assinada × não assinada NÃO são duplicatas (ambas mantidas). Detalhe em `_ORGANIZADO/_DECISOES_REVISAO.md`.

### Otimização da description + indexação
- Eval set de disparo (10 devem ativar + 10 near-misses) em `…/_SKILLS/organizador-arquivos-prodam/evals/trigger_eval_set.json`. O loop **medido** (`run_loop.py`) NÃO rodou no Cowork (CLI `claude` deslogado); otimização feita por análise, fechando disparos indevidos (gerar peças, renomear variável de código, consultar dados, "duplicata" jurídica, backup). description final ~955 chars (≤1024), 1ª frase curta para o índice ficar limpo.
- **Indexação:** rodada apenas a função oficial `generate_skills_index()` do `auto_update_claude_md.py` → reescreveu **somente** `.claude/skills/INDEX.md` (53 skills; a nossa na linha 36, ordem alfabética). O `CLAUDE.md` **não** foi regenerado (puxa métricas de profiles/db; rodar `/sincronizar-prodam` no Windows quando quiser).

### Arquivos tocados / observações
- Criados: a skill em `_SKILLS/`; `SESSAO_2026-06-09_organizador-arquivos-prodam.md` (raiz); `_ORGANIZADO/` na pasta de origem; backups `INDEX.md.bak-20260609` e `HISTORICO_SESSOES.md.bak-20260609`. Alterado: `.claude/skills/INDEX.md` (apenas +1 linha).
- Ambiente Cowork: `rm` bloqueado pelo mount (restam subpastas vazias e um `_artefato_teste_ignorar.txt` inofensivos); nada foi commitado/enviado — entra no próximo commit do projeto.

## 2026-06-09 — Customização do plugin `productivity-prodam` (v1.0.0 → v1.1.0)

Sessão de tooling, não jurídica. Objetivo: alinhar o plugin de produtividade `productivity-prodam` ao estado atual do portfólio (69 devedores) e corrigir o que estava quebrado. Empacotado como `.plugin` instalável.

### Diagnóstico (o que estava defasado)
- Plugin dizia **51 devedores**; o projeto tem **69**.
- Exemplos antigos (SES/SUSAM como maior crédito ~R$ 45 mi, prescrição 13/05/2026).
- `.mcp.json` vazio — nenhum conector ligado.
- `/start` referenciava `setup/*.template` inexistentes (o comando quebrava).
- `dashboard.html` com dados de demonstração antigos e coluna "Fase" em vez de "próximo passo".

### O que foi feito
1. **Sync do portfólio** — 51→69 devedores; exemplos atualizados (SEDUC maior crédito; SSP prescrição 30/06/2026; SEJUSC 31/08/2026; força 12/15/42; estados ANALISAR_DOCUMENTACAO / CLASSIFICAR / ENVIAR_TRD / PROTOCOLAR_PETICAO). Em `plugin.json`, `README.md` e nas skills `painel-devedores`, `task-management`, `alerta-prazos`, `memory-management`.
2. **Correção do `/start`** — criada a pasta `setup/` com `CLAUDE.md.template`, `TASKS.md.template`, `glossario.md.template`. Modelos com lacunas `{{...}}` preenchidas em runtime a partir do `profiles.json` (nada sensível embutido no plugin).
3. **Gmail + Calendar** — categorias recomendadas em `.mcp.json` (email/calendar/documents); `CONNECTORS.md` reescrito; `update --comprehensive` passa a usar Gmail (respostas de devedores, instruções PRODAM) e `alerta-prazos` lança eventos de prescrição/prazo no Calendar.
4. **Dashboard refeito** — KPIs agregados reais (69 devedores, R$ 83.668.078,44 exigível, R$ 125.245.390,64 atualizado, 2 prescrições <90 dias), top 10 por valor, "Fase" → "Próximo Passo".

### Salvaguardas
- Anti-alucinação: prescrições só onde confirmadas (SSP, SEJUSC); devedor SALUX sem nome (não constava); contagens/valores vindos do `CLAUDE.md` do projeto (SSOT `PRODAM_DOCS/profiles.json`).
- Não-destrutivo: plugin original (cache do app `plugin_01JXME7CfmhM9aSCefFAkJTe`) intocado; tudo gerado em cópia nova.

### Estado final / entregáveis
- `_SESSAO/2026-06-09_plugin_productivity-prodam/` com `RESUMO_SESSAO.md`, `productivity-prodam.plugin` (instalável) e o código-fonte em `productivity-prodam/`.
- Pendência: gerar versão "demonstração" (dados fictícios) se o `.plugin` precisar sair do escritório — contém nomes de órgãos e valores reais.
- Hook quebrado persiste: `check-sql-files.py` (`${CLAUDE_PLUGIN_ROOT}` literal) dispara erro a cada `Write` — revisar/desativar em Configurações → Capacidades.

---

## 2026-06-09 (tarde) — Personalização do plugin CockroachDB para o PRODAM

Sessão de setup/infra, não jurídica. Objetivo: adaptar o plugin oficial `cockroachdb` (Cockroach Labs) ao Projeto PRODAM e empacotá-lo para instalação.

### O que foi feito

- **Cópia editável** do plugin instalado (somente leitura) para área de trabalho; 33 skills, 3 agentes e scripts preservados íntegros.
- **`tools.yaml`:** banco padrão alterado de `defaultdb` para `prodam`; `application_name` para `prodam-claude-plugin`; cabeçalho de comentário explicando a personalização; modo somente leitura mantido (`readOnlyMode: true`, `enableWriteMode: false`); descrições das 3 ferramentas reescritas em pt-BR citando o esquema PRODAM.
- **Agentes (DBA, Desenvolvedor, Operador):** adicionada seção "Contexto do Projeto PRODAM" em cada um — esquema (`devedores`, `spcf_contratos`, `spcf_empenhos`, `spcf_faturas`, `spcf_nfs` + views), regras (dinheiro em `DECIMAL`, formato BRL, prescrição por fatura, normalização de número de contrato `006/2021 ≡ 6/2021 ≡ 2021/006`) e ênfase específica por papel. Front-matter (`name`) preservado.
- **`README.md`:** banner de personalização no topo, com variáveis de ambiente (PowerShell) e caminho de migração.
- **Empacotado** como `cockroachdb.plugin` (≈475 KB, 202 arquivos) na pasta de saída e apresentado para instalação.

### Decisões do usuário (via formulário)

1. **Situação:** "deixar pronto" para uso futuro (ainda sem cluster).
2. **Segurança:** somente leitura.
3. **Contexto nos agentes:** completo.
4. **Nome do banco:** informado "PRODAM COCKROACh" → **normalizado para `prodam`** (identificador válido: minúsculas, sem espaço). Ajustável em `COCKROACHDB_DATABASE`.

### Ressalva técnica sinalizada (importante)

- O plugin foi feito para **CockroachDB** (banco distribuído cliente-servidor, porta 26257). O PRODAM hoje roda em **SQLite** (`prodam.db`). As ferramentas do plugin **não leem arquivo SQLite** — só operam contra um cluster CockroachDB.
- **Migração não é direta:** as ferramentas MOLT do plugin suportam PostgreSQL, MySQL, Oracle e MSSQL — **não há conector SQLite**. Caminho típico: exportar `prodam.db` → CSV ou PostgreSQL intermediário → `IMPORT INTO`/MOLT no CockroachDB. Roteiro oferecido, não executado (pendente de decisão).

### Salvaguardas (confidencialidade / LGPD)

- Nenhum dado de conexão (host, usuário, senha, cluster ID) gravado em arquivo — só variáveis de ambiente.
- Nenhum dado sensível de cliente nos arquivos do plugin: sem CNPJ, valores, nomes de devedores ou número de processo. Apenas nomes de tabela e regras estruturais.

### Observação

- O mesmo **hook quebrado** (`check-sql-files.py` com `${CLAUDE_PLUGIN_ROOT}` não resolvido) voltou a disparar a cada `Edit` — contornado fazendo as edições via shell. Consistente com a pendência da entrada anterior; sugerido corrigir/desativar em Configurações → Capacidades.

### Próximos passos (se for adiante com CockroachDB)

1. Instalar o `cockroachdb.plugin`.
2. Provisionar/escolher um cluster e definir as variáveis de ambiente.
3. Decidir o roteiro de migração `prodam.db → CockroachDB` (passo intermediário obrigatório).

## 2026-06-09 — Arquivos de contexto do Cowork (about-me / preferences / voice / projects)

Sessão de setup, não jurídica. Objetivo: criar os quatro arquivos de contexto do Cowork para calibrar como o assistente trabalha no projeto.

### O que foi criado

Nova pasta `context/` na raiz do PROJETO_PRODAM, com quatro arquivos `.md`:

- **`context/about-me.md`** — perfil profissional (Gabriel Mar, OAB/AM 15.697; Direito Administrativo, Licitações e Contratos, Recuperação de Créditos) centrado em PRODAM + como prefiro colaborar (direto, contraditório, pergunta antes de presumir, iniciante em programação).
- **`context/preferences.md`** — pt-BR conciso; rigor anti-alucinação (citar dispositivo/precedente, pesquisar índices voláteis); confirmação explícita antes de apagar/mover/sobrescrever; Windows + PowerShell + `py -3.12`; confidencialidade (LGPD; nada de CNPJ/valores/`.env` em saídas).
- **`context/voice.md`** — voz jurídica formal para peças (notificações, ofícios, pareceres, dossiês): fundamentação obrigatória, estrutura por tipo de documento, sinalização de prazos/riscos, BRL com data-base.
- **`context/projects.md`** — só PRODAM (Contrato 002/2026, frente administrativa) + sub-projeto DETRAN-AM; hierarquia das fontes da verdade e regras de prescrição. `PRODAM_DOCS/profiles.json` apontado como SSOT.

### Decisões de calibração (respondidas pelo usuário)

1. **Foco:** centrado em PRODAM (não toda a prática).
2. **Voz:** sempre jurídica formal.
3. **Pessoal:** moderado (perfil + estilo de colaboração; sem vida pessoal).
4. **Projetos:** somente PRODAM + DETRAN. **Engeco (NDA) deliberadamente excluído** — reincluir só a pedido.

### Salvaguardas aplicadas

- Conteúdo alinhado ao `CLAUDE.md` e ao `INSTRUCOES_COWORK.md` (objeto, fontes da verdade, frente administrativa, rigor jurídico).
- Nenhum dado sensível de terceiros nos arquivos: sem CNPJ, sem valores concretos, sem nomes de devedores, sem número de processo. Verificado por `grep` (0 ocorrências de CNPJ/valor). O único `R$` é o exemplo de formatação `R$ 1.234,56`.

### Pendência / observação

- **Hook quebrado disparando a cada `Write`:** o plugin de checagem de SQL (`check-sql-files.py`) está com caminho não resolvido (`${CLAUDE_PLUGIN_ROOT}` literal). Não afeta a escrita dos arquivos, mas gera ruído de erro. Sugerido corrigir/desativar em Configurações → Capacidades.

### Estado final

- 4 arquivos em `C:\Users\gabri\Desktop\PROJETO_PRODAM\context\` (about-me.md, preferences.md, voice.md, projects.md).
- Localização default no workspace principal; mover se o usuário preferir uma pasta de contexto global do Cowork.

---

## 2026-06-08 — Setup Semgrep no Windows + isolamento pipx (erros e acertos)

Sessão de tooling, não jurídica. Objetivo: ativar o plugin Semgrep do Claude Code (mínimo `semgrep >= 1.146.0`). A skill `setup-semgrep-plugin` é só-macOS (`brew`, `which`) — precisou ser traduzida para Windows + PowerShell.

### ✅ Acertos

1. **Semgrep tem suporte nativo Windows (GA desde verão/2025)** — sem WSL, sem Docker. PyPI publica wheel `win_amd64`. Versão final instalada: **1.165.0** (mínimo do plugin 1.146.0 — satisfeito). Fontes: <https://semgrep.dev/resources/whats-new/summer-25/>, <https://pypi.org/project/semgrep/>.
2. **Isolamento via `pipx`** — CLI fica em venv próprio, não polui o site-packages global compartilhado pelo pipeline forense. `py -3.12 -m pipx install semgrep` põe o `semgrep.exe` em `C:\Users\gabri\.local\bin` (já no PATH). O próprio `pipx` ficou em `C:\Users\gabri\AppData\Roaming\Python\Python312\Scripts` (fora do PATH — invocar via `py -3.12 -m pipx`).
3. **Commit seletivo limpo** (`170e89a`) — staged só os 2 arquivos pretendidos (`.vscode/extensions.json` + `_QUESTOES_CRITICAS/CLAUDE.md.preview-20260511`), deixando backups/vendored (`_BACKUPS/`, `awesome-design-md-main/`, `impeccable-main/`, `CLAUDE.md.bak.*`, `_legado/.sql`) fora. Usado o padrão arquivo-temp + `git commit -F` (sem heredoc bash).

### ❌ Erros (não repetir)

1. **`pip install semgrep` GLOBAL quebrou o pipeline forense.** O `py -3.12 -m pip install --upgrade semgrep` fez downgrade silencioso de deps compartilhadas: `click` 8.3.2→8.1.8, `mcp` 1.27.0→1.23.3, `wrapt` 2.1.2→1.17.3 (+ tomli, ruamel.yaml.clib), gerando conflito para `marker-pdf`, `unstructured`, `sqlite-utils`, `fastmcp` (ferramentas de PDF/OCR/DB do projeto).
   - **Correção:** desinstalar o semgrep global → `py -3.12 -m pip install "click==8.3.2" "mcp==1.27.0" "wrapt==2.1.2"` (pin-restore) → `py -3.12 -m pipx install semgrep` (isolado). Verificado que o ambiente voltou ao estado anterior; conflitos residuais (pypdf/pdfminer/pydantic/pillow/pandas/opentelemetry+wrapt) são **pré-existentes**, não introduzidos.
   - **Lição durável:** ferramenta CLI em ambiente forense compartilhado → **sempre `pipx`, nunca `pip` global**. Antes de instalar CLI Python, perguntar: "isso é biblioteca (import) ou ferramenta (executável)?" — executável vai em pipx.
2. **`py -3.12 -m semgrep` está deprecado** desde 1.38.0 ("Please simply run `semgrep`"). **Correção:** usar o comando `semgrep` puro / caminho completo do `.exe`, nunca `python -m semgrep`.
3. **`semgrep install-semgrep-pro` pode falhar no Windows** — baixa binário nativo historicamente só-Linux/macOS. O engine OSS/Community funciona sem isso e sem login. `semgrep login` é interativo (browser) e só serve para Pro/cloud. **Não bloquear o setup** se o Pro falhar.
4. **`npx skills find <termo-chutado>` foi rejeitado pelo usuário.** Não rodar busca de skills num termo adivinhado sem query explícita do usuário. `/find-skills` sem args = não quer Q&A guiado naquele momento.
5. **`python-executor` roda em sandbox REMOTO (inference.sh)** — **não enviar dado sensível do PRODAM** (profiles.json, valores, CNPJs) para esse skill.

### Estado final verificado

- `semgrep` → `C:\Users\gabri\.local\bin\semgrep.exe`, v1.165.0, mínimo do plugin satisfeito.
- Pacotes do pipeline forense restaurados (click 8.3.2 / mcp 1.27.0 / wrapt 2.1.2).
- Tools MCP do Semgrep disponíveis (`semgrep_scan`, `semgrep_scan_with_custom_rule`, `semgrep_findings`, etc.).
- Commit `170e89a` no `main`, pronto para push.

---

## 2026-05-28 — Sessão Janela 2.4 + 1.2 + /simplify (cloud, branch `claude/jolly-heisenberg-mK6VU`)

**Trabalho fechado em 3 commits**: bugs D1 (float→Decimal) + DRY de helpers + auditoria forense da reversão de drift 13/05 + review max-effort com 13 fixes aplicados. Working tree limpo, 113 testes verdes + 1 xfailed.

### Commit `f8290de` — Janela 2.4 (D1 float→Decimal cirúrgico + DRY brl/fmt_brl)

- `scripts/auditoria_completude_devedor.py:250,252`: `float()` → `brl()` em `empenhos_valor` e `faturas_valor` (Regra #16 do CLAUDE.md: "Decimal, nunca float").
- `scripts/dossie_multiformato_devedor.py:25-60`: removidos helpers locais `brl()` e `fmt_brl()` (16 linhas) — agora importa de `prodam_utils` (DRY).
- Bug D3 colateralmente resolvido: o `brl()` local removido tinha `except:` nu (engole erros silenciosos).
- `tests/test_prodam_utils.py`: +2 testes funcionais (`brl` aceita resultado SQL SUM; `fmt_brl` aceita Decimal).
- `tests/test_regression_decimal_dry.py` (NOVO, 94 linhas): 6 lints estruturais que travam regressão.
- `_QUESTOES_CRITICAS/10_CONSOLIDAR_BRL_FMT_BRL_STRICT.md` (NOVO, 80 linhas): follow-up — refatorar `prodam_utils.fmt_brl` para não usar `float()` internamente; depois aplicar DRY nos 7 outros scripts com helpers locais (`auto_update_claude_md.py`, `gerar_relatorio_docx.py`, `consultas.py`, `ad_hoc/gerar_memorial_preliminar_ses.py`, `reconciliacao_4_fontes.py`, `detran/gerar_dossie_detran_v2.py`, `ses_reconciliacao_completa.py`).

Escopo cirúrgico: 3 dos 26 `float()` totais em valores monetários. Os 23 restantes (serialização JSON para Chart.js em `dossie_multiformato_devedor.py` linhas 145-185 + `scripts/detalhamento_faturas.py`) ficam para audit downstream antes de mexer — Chart.js consumidor precisa de número, não string Decimal.

### Commit `11d0c40` — Janela 1.2 (Auditoria forense reversão drift 13/05)

`_QUESTOES_CRITICAS/03_REVERSAO_DRIFT_20260513.md` (NOVO, 175 linhas inicialmente; ajustado para 168 após `/simplify`).

**Achado central**: a "reversão de drift" de 13/05 NÃO foi bug aleatório — desfez silenciosamente a reconciliação metodológica validada na Sessão TRD SES/SUSAM (12/05). O backup `_BACKUPS/profiles_PRE-REVERSAO-DRIFT-20260513-155115.json` (334 KB) preserva 12 campos `*_anterior` para SES/SUSAM documentando exatamente o que foi revertido.

**4 siglas materialmente divergentes** (backup 12/05 vs CSV atual):

| Sigla | Δ val_exig | Δ val_atualizado | Δ fat_exig | Bloqueio |
|---|---:|---:|---:|---|
| **SES/SUSAM** | +R$ 9.964.692,44 | +R$ 35.691.557,77 | +62 | Item 1.6 (TRD em disco usa R$ 4,78M, CSV diz R$ 14,75M) |
| **SSP** | 0 | 0 | +15 | Perdeu campo `evidencias_reconhecimento: 125` (Art. 202 VI CC) |
| **SEJUSC** | ~0 | 0 | -4 | Sutil |
| **FENIXSOFT** | 0 | 0 | +5 (sign correto após /simplify) | 5 prescritas viraram exigíveis sem justificativa |

**Perda informacional massiva**: JSON tinha 128 campos por devedor; CSV tem 11 colunas. Perdidos: `cnpj` (identificador fiscal!), `evidencias_reconhecimento`, `reconhecimento_revisado`, `modelo_notificacao`, `regime_execucao`, `indice_correcao`, `juros_mora`, `multa`, `score_composto`, `ev_valor_esperado`, `ev_honorarios`, `val_*_anterior` (rastros), etc.

**Conclusão estrutural**: o CSV **não é SSOT real** — é índice resumido. JSON era a fonte verdadeira, hoje só preservado em `_BACKUPS/`. A causa raiz provável é o `auto_update_claude_md.py` all-or-nothing (bug D4 do plano) regenerando o JSON a partir do CSV/SPCF entre 12/05 e 13/05.

**Decisões pendentes (gate humano)**:
1. SES/SUSAM val_exig real = A (R$ 4,78M backup, reconciliado fatura-a-fatura, defensável adversarialmente) OU B (R$ 14,75M CSV, soma bruta SPCF)?
2. Restaurar `PRODAM_DOCS/profiles.json` a partir do backup? R1 (total) / R2 (seletivo) / R3 (migrar CSV permanente).
3. Validar 125 evidências SSP (sustentáveis adversarialmente?).

### Commit `cb61891` — `/simplify` (13 findings aplicados)

Code review max-effort com 9 angles paralelos + sweep:

- **4 bugs de regex no `tests/test_regression_decimal_dry.py`** (substituídos por AST walk):
  - `[^,\n]+` truncava no `,` interno do `.get()` → `[^\n]+` (linha inteira)
  - `from prodam_utils import` falhava em imports multi-linha PEP8 parentetizados → `ast.ImportFrom`
  - `^\s*except\s*:\s*$` MULTILINE não pegava `except: # comment` → `ast.ExceptHandler.type is None`
  - `^def brl` MULTILINE só top-level → `ast.FunctionDef` qualquer nível
- **6 testes redundantes** parametrizados via `@pytest.mark.parametrize` em 4 métodos-base.
- **`test_aceita_resultado_sql_sum`** duplicava `test_none` e `test_numero_simples` — reduzido a 1 assert único (int grande).
- **Novo teste de fronteira**: `test_aceita_decimal_grande_precisao` com `@pytest.mark.xfail(reason="Issue 10")` — vira XPASS quando Issue 10 land.
- **3 erros factuais na Issue 03**: sign FENIXSOFT `-5` → `+5`, `p_recuperacao` marcado como preservado em `p_rec`, seção "Anexos" removida (duplicava links).
- **Issue 10 critério #4 ajustado**: disclaim sobre os 7 outros scripts com helpers locais.
- **Comentário "Regra #16" redundante removido** do `dossie_multiformato_devedor.py:32` (CLAUDE.md default: no comments).
- **Standalone runner adicionado** ao `test_regression_decimal_dry.py` (paridade com `test_prodam_utils.py`).

**Skipped com justificativa** (15 categorias documentadas no resumo do `/simplify`):
- Já em Issue 10: `fmt_brl` float() em prodam_utils, Decimal→float round-trip
- Fora do escopo declarado: 8+ float() restantes em dossie, top-level DB connect, norm_cliente_nome duplicação
- Defensivo/prematuro: re-adicionar Decimal import "pra defesa", `sys.path broad`
- Refutado pelos próprios angles: `_MONEY_STRIP_RX` edge, file I/O caching em tests

### Roadmap após esta sessão

| Janela | Estado em 28/05 |
|---|---|
| 0 — Imediata 72h | ✅ Fechada |
| 1 — Primeira semana | 1.4 ✅, 1.7 ✅, 1.8 ✅, **1.2 ✅**; 1.1/1.3/1.5/1.6 ⏸ aguardando gate humano ou PRODAM_DOCS |
| 2 — Protocolar + bugs | **2.4 ✅**; 2.0/2.2/2.6/2.7/2.8 ⏸ |
| 3 — Automação | 3.1 ✅, 3.3 ✅; 3.2/3.4-3.10 ⏸ |
| 4 — Higiene contínua | Não iniciada |

### Métricas da sessão

- 3 commits adicionais no branch `claude/jolly-heisenberg-mK6VU`
- 6 arquivos novos/modificados no commit f8290de; 1 no 11d0c40; 5 no cb61891 (alguns repetidos)
- ~640 linhas adicionadas, ~88 removidas (net +552)
- Testes: 105 → 113 passed + 1 xfailed
- 1 nova issue aberta (`03_REVERSAO_DRIFT_20260513.md`), 1 follow-up aberta (`10_CONSOLIDAR_BRL_FMT_BRL_STRICT.md`)

### Aprendizados / decisões duráveis

1. **CSV ≠ SSOT** — é índice resumido com perda de 117 campos por devedor. Decisões jurídicas finais não podem ser tomadas só do CSV.
2. **Regex em testes estruturais é fonte recorrente de falsos negativos** — AST resolve 4 classes de bugs simultaneamente.
3. **Surgical fix + Issue follow-up funciona bem** — mantém commits coerentes em escopo, força documentação explícita do que ficou de fora.
4. **Adversarial-meta-auditor era pré-requisito de TRDs** — mas auditoria de drift e refactor de testes não exigem (boa divisão de gates).
5. **Próxima sessão**: começar por Decisões 1/2/3 da Issue 03 (gate humano) OU item 2.2 (triagem 18 SEM_d_plus, sem gate).

---

## 2026-05-11 — Ciclo de 3 edits no KNOWLEDGE_BASE_JURIDICO.md (errata jurídica + RPV auto-atualizável + config_prodam.py fantasma)

### Resumo
- **Edit 1** — REsp 793.969/RJ corrigido em **6 linhas** (37, 48, 303, 335, 371, 434). Padrão canônico adotado: `Rel. Min. Teori Zavascki (vencido), Rel. p/ acórdão Min. José Delgado`. Anti-alucinação ativa (que sugeria "Teori venceu") resolvida.
- **Edit 2** — Teto RPV-AM convertido de valor fixo (R$ 32.420) para fórmula auto-atualizável (`20 × SM vigente`) em **6 trechos** (3 callouts via `replace_all` + tabela + bullet canônica + errata). Documento agora resistente a reajuste anual do SM. Lei AM 2.748/2002 mantida como anchor legal.
- **Edit 3** — DETRAN "IGPM+1%+2%" endurecido como `(a confirmar); carece de auditoria contratual antes de citar em peça`. `config_prodam.py` documentado in-loco como **fantasma documental** (~232 referências no ecossistema, **NÃO EXISTE no disco**). SSOTs reais declaradas: `normalizador.py` (mapa contrato/ano → regime) e `gerar_memorial.py` (taxas vivas API BCB).

### Métricas
- Arquivo: 28.795 → 30.184 bytes (+1.389; +4,82%); 470 → 476 linhas.
- 15 trechos corrigidos em 10 operações de Edit.
- 3 backups granulares preservados (rollback por bloco).

### Backups preservados em `PRODAM_DOCS/REFERENCIA_JURIDICA/00_KNOWLEDGE_BASE/`
- `KNOWLEDGE_BASE_JURIDICO.md.bak-20260511-edit1` — 28.795 bytes — pré-todas-as-edições
- `KNOWLEDGE_BASE_JURIDICO.md.bak-20260511-edit2` — 29.262 bytes — pós-Edit 1 / pré-Edit 2
- `KNOWLEDGE_BASE_JURIDICO.md.bak-20260511-edit3` — 29.560 bytes — pós-Edit 2 / pré-Edit 3

### Pendências em aberto
- **`auto_update_claude_md.py` adiado** para próximo ciclo natural. Script é all-or-nothing — apagaria o bloco "DECISÃO PENDENTE config_prodam.py" do CLAUDE.md gerado. Antes de rodar: implementar `--preserve-manual-blocks` ou migrar o bloco para `_QUESTOES_CRITICAS/`.
- **`config_prodam.py`** — decisão definitiva A/B/C/X pendente (criar com auditoria vs deprecar formalmente as ~232 referências). KNOWLEDGE_BASE já não cita como SSOT; falta decisão estratégica.
- **Padronizar frase do gate** — divergência: SAFEGUARD global (`~/.claude/CLAUDE.md` topo) usa **"OK, prosseguir"**; Gate jurídico do projeto (mesma `~/.claude/CLAUDE.md`, seção mais abaixo) usa **"OK, salvar"**. Padronizar em sessão futura.

### Detalhe completo
`relatorios/CHANGELOG_SESSAO_2026-05-11_kb_juridico_3edits.md`

---

## 2026-04-24 — Otimização da description da skill `extracao-clausulas-contratuais`

### O que foi feito
- **Skill alvo:** `extracao-clausulas-contratuais` — a description original (~1.400 chars, YAML folded multi-line) foi substituída por versão mais enxuta (~960 chars, linha única).
- **Método:** rodado `skill-creator/run_loop.py` (otimização quantitativa) em cima de um `trigger-eval.json` com 20 queries (10 positivas + 10 negativas).
- **Descoberta colateral:** 3 bugs novos do skill-creator no Windows (detalhe em memória `skill_creator_bugs_workaround.md`):
  - Bug 4 — `select.select()` em pipe de subprocess (WinError 10038). Patch aplicado em `run_eval.py` do cache do plugin.
  - Bug 5 — `thinking.type.enabled` incompatível com Opus 4.7 (exige `adaptive`). Patch aplicado em `improve_description.py`.
  - Bug 7 — subprocess `claude -p` não enxerga as cópias hash-suffixed da skill → medição sai zerada (recall=0% em todas as iterações, apesar do script rodar limpo). Bloqueia uso quantitativo do optimizer; decisão final foi manual sobre as 4 propostas geradas pelo Opus.
- **Description adotada:** Proposta 2 (iter 2) — PT, formato list-like, menciona DETRAN + padrão "número de contrato + órgão devedor".
- **Teste qualitativo:** 6/6 (3 positivas + 3 negativas do eval set).

### Arquivos fora do repo que foram modificados nesta sessão
- `C:\Users\gabri\.claude\skills\extracao-clausulas-contratuais\SKILL.md` (description)
- `C:\Users\gabri\.claude\plugins\cache\claude-plugins-official\skill-creator\unknown\skills\skill-creator\scripts\run_eval.py` (Bug 4)
- `C:\Users\gabri\.claude\plugins\cache\claude-plugins-official\skill-creator\unknown\skills\skill-creator\scripts\run_loop.py` (Bug 6 — defensivo, asyncio policy)
- `C:\Users\gabri\.claude\plugins\cache\claude-plugins-official\skill-creator\unknown\skills\skill-creator\scripts\improve_description.py` (Bug 5)
- `C:\Users\gabri\.claude\projects\C--Users-gabri\memory\skill_creator_bugs_workaround.md` (bugs 4, 5, 6)
- `C:\Users\gabri\.claude\projects\C--Users-gabri\memory\firecrawl_cli.md` (novo — referência Firecrawl)
- `C:\Users\gabri\.claude\projects\C--Users-gabri\memory\MEMORY.md` (2 novos pointers)

### Custo da sessão
- Tokens pagos Opus 4.7 via API direta: ~$1–2 (5 iterações de reescrita)
- Ciclo API da conta permanece íntegro (`ANTHROPIC_API_KEY` configurada permanentemente via `SetEnvironmentVariable User`).

### ⚠️ Atenção — patches em caminho volátil
Os 3 patches em `skill-creator/scripts/` ficam no **cache do plugin**. Se o plugin for reinstalado ou atualizado pelo marketplace, os patches serão sobrescritos. Reaplicar se sintomas (WinError 10038, thinking.type.enabled) voltarem.

---

## 2026-04-24 — Otimização da description da skill `consulta-acervo-prodam`

### O que foi feito
- **Skill alvo:** `consulta-acervo-prodam` — skill nova (v1.0, criada no mesmo dia). Description original ~900 chars, YAML folded multi-line. Substituída por Proposta 4 do Opus 4.7 (~880 chars, linha única, padrão "intent + expected output + triggers + exclusions").
- **Método:** mesmo pipeline da otimização anterior (`run_loop.py` com `trigger-eval.json`), mas agora com **30 queries (15 positivas + 15 negativas)** para melhor cobertura.
- **Instalação prévia:** skill veio em `C:\Users\gabri\Downloads\consulta-acervo-prodam\`. Copiada para `C:\Users\gabri\.claude\skills\consulta-acervo-prodam\` antes da otimização.
- **Estratégia B no conflito com `extracao-clausulas-contratuais`:** 3 queries negativas do eval foram deliberadamente construídas para ir na outra skill ("abre o CT X e me mostra a cláusula de juros", "qual o regime de correção do 145/2023?", "o TA-02 mexeu no IGPM?") — para treinar o classificador a separar "achar arquivo" de "ler cláusula".
- **Description adotada:** Proposta 4 (iter 4) — PT, 4 parágrafos lógicos em linha única. Destaques: (1) intenção = recuperar arquivo; (2) output esperado = caminho de PDF / lista de arquivos; (3) lista ampla de exclusões (incluindo "avaliar prescrição"); (4) menciona DETRAN/SES/SSP/SEDUC/Banco Master explicitamente.

### Custo da sessão
- **Primeira tentativa falhou por saldo API insuficiente** ("Your credit balance is too low") ao passar da iter 1 → 2. As 60 chamadas de avaliação via `claude -p` rodam grátis pela assinatura Claude Code; mas `improve_description` vai pela API direta paga e estourou saldo.
- **Ação corretiva:** Gabriel comprou créditos em `console.anthropic.com` → Plans & Billing.
- **Segunda tentativa completou 5/5 iterações.** Custo total estimado: ~$2–3 em tokens pagos.

### Arquivos fora do repo modificados
- `C:\Users\gabri\.claude\skills\consulta-acervo-prodam\` (pasta inteira copiada de Downloads; depois SKILL.md editado).
- `C:\Users\gabri\.claude\skills\consulta-acervo-prodam\trigger-eval.json` (30 queries criadas).

### Observações
- **Bug 7 persiste:** medição quantitativa continua zerada (precision=100%, recall=0% em todas 5 iterações). O valor real entregue pela ferramenta é qualitativo — as 4 descriptions geradas pelo Opus 4.7.
- **Keywords preservadas:** o frontmatter da skill tem um campo `keywords:` com 40 entradas — mantido intacto na edição; só a `description:` foi substituída.
- **Padrão "Intent → Output → Triggers → Exclusões"** da Proposta 4 é um insight generalizável — define o *output esperado* explicitamente (caminho de PDF, lista de arquivos), não apenas o input. Pode ser reusado em otimizações futuras de descriptions que competem com outras skills.

---

## 2026-04-24 — Skill `reconhecimento-tacito-hunter` (revisão jurídica + otimização)

### Contexto estratégico
Gabriel recebeu skill `reconhecimento-tacito-hunter` (560 linhas de Python + 17 atos tácitos + referência jurídica) e pediu parecer jurídico antes de usar em peças reais. Decisão: a nova skill **substitui** somente o agente direto sobreposto — o `agente-reconhecimento-tacito` (E3.4) será excluído. Os demais 34 agentes do multi-agente (maestro, renomeador, conversor, scanner, downloader, inventariador, extrator, consolidador, verificador-elo-5, detector-faltantes, classificador-procedencia, classificador-regime, calculador-monetario, prescricional-defensivo, reconhecimento-tacito JÁ NÃO, forca-probatoria, auditor-orquestrador, 7 adversariais, sintetizador, blindagem-reversa, revisor-meta, geradores E5.x, guardrails, testing-qa, sla-alertas) permanecem ativos.

### Parecer jurídico — 5 citações STJ validadas empiricamente (Firecrawl + STJ oficial)

| Citação | Status | Achado |
|---|---|---|
| REsp 1.963.067/MS | ✅ **REAL** | Unicidade da interrupção — notícia oficial STJ confirma "Prescrição só ocorre uma vez na mesma relação jurídica" |
| AgInt no AREsp 1.388.464/MS | ✅ **REAL** | Pagamento parcial interrompe prescrição (Art. 202 VI CC) — validado em CogniJus |
| AgInt no REsp 1.826.395/RJ | ✅ **REAL** | Ato inequívoco de reconhecimento — LexML oficial, 1ª Turma, 17/05/2021 |
| REsp 1.956.817/MS | ⚠️ **DESCRIÇÃO ERRADA** | Existe mas é sobre interrupção por ação conexa, não "texto do Art. 202" — adicionado à lista de distorcidos na memória |
| REsp 1.200.556/SP | 🚩 **FABRICADO** | Não existe com esse UF. REsp 1.200.556/**AM** é sobre concurso público (Min. Mauro Campbell) — adicionado como 4º precedente fabricado |

### 3 erros jurídicos críticos corrigidos nas referências da skill

1. **Reinício integral × metade para Fazenda** (seção 5.1 do `jurisprudencia_e_consequencias.md`) — a skill afirmava "prazo recomeça integralmente (Art. 202 § único CC)" sem distinguir privado vs. Fazenda. **Corrigido:** contra Fazenda aplica-se Dec. 20.910/1932 Art. 9º, prazo reinicia pela METADE (2,5 anos vs 5 anos). Exemplos numéricos reescritos para cada regime. Esse era um erro que faria perder faturas por ajuizamento fora do prazo.

2. **Renúncia tácita sem alerta Tema 1.109/STJ** (seção 5.2) — skill afirmava que reconhecimento pós-consumação "ressuscita" dívida via Art. 191 CC. **Corrigido:** adicionado alerta crítico com Tema 1.109/STJ que **impede** renúncia tácita da Administração. Art. 191 CC só funciona contra privados. Regra prática incluída para cada tipo de devedor.

3. **Citações incompletas/fabricadas** (seção 3.4 + catalogo) — "TJGO, Apelação Cível XXXXX-85.2019.8.09.0006" (placeholder literal) + "TJPR, precedente análogo" sem número. **Corrigido:** substituídos por AgInt no REsp 1.826.395/RJ validado.

### Pipeline executado
- **Instalação:** copiado de `Downloads/` para `.claude/skills/reconhecimento-tacito-hunter/` (5 arquivos: SKILL.md, README.md, scripts/cacar.py, 2 references/)
- **Correções jurídicas:** 4 edits aplicados nos 2 arquivos de referência
- **Eval montado:** 30 queries (15 positivas + 15 negativas com near-misses contra `consulta-acervo-prodam` e `extracao-clausulas-contratuais` já otimizadas)
- **`run_loop.py` disparado:** ID `blt4428o3`, 5 iterações, Opus 4.7

### Decisão estratégica registrada
**Skills "hunter" autônomas (com código Python embutido) vão substituir os 35 agentes do multi-agente PRODAM** (`agente-maestro-prodam`, `agente-renomeador-inteligente`, `agente-conversor-formatos`, ... até os `agente-sla-alertas-multiagente` e todos os `auditor-adversarial-*`). Os agentes eram só instruções; as hunters combinam instruções + script executável + referências jurídicas validadas.

### Observações
- Parecer jurídico desta sessão ressalta um padrão importante: **skills geradas por IA sem revisor advogado tendem a (a) citar precedentes inexistentes com números que parecem plausíveis e (b) misturar regimes (privado vs Fazenda) sem distinção**. Esses dois erros foram achados nesta única skill. Padronizar revisão humana jurídica como gate obrigatório antes de qualquer skill jurídica entrar em produção.
- Bug 7 do skill-creator persiste (medição zerada — 3ª skill consecutiva). Aceito como limitação estrutural do `claude -p` subprocess.

### Re-execução (2ª rodada) + Description adotada — 2026-04-24

- **2ª rodada do `run_loop.py`:** ID `bwwqtr31d`, disparado após patch completo do Bug 5 em `improve_description.py` (2 blocos `thinking={"type": "enabled"}` trocados por `"adaptive"` — o segundo em linha 154 havia sido omitido na 1ª rodada por indentação diferente do 1º bloco).
- **5 iterações rodaram limpas (exit code 0).** Custo ~$2-3 em tokens pagos.
- **Bug 7 novamente:** precision=100%, recall=0% em todas iterações. Ranking automático inválido — `best_description` no JSON aponta para a **original** com score 6/12, mas esse score é artefato do Bug 7. Decisão 100% qualitativa.
- **Salvaguarda de reversibilidade:** backup da description original (YAML folded) preservado abaixo; commit separado só dessa mudança para permitir `git revert` em 10 segundos se a Proposta 5 degradar na prática.

#### Description antes × depois

**ANTES (original, preservada para reversão):**
```yaml
description: >
  Varre o acervo do Projeto PRODAM para detectar reconhecimentos tácitos de dívida (Art. 202 VI CC) escondidos em documentos — ofícios, emails, empenhos novos, pagamentos parciais, atas. Cada reconhecimento detectado INTERROMPE a prescrição e pode ressuscitar faturas dadas como prescritas. Cobre os 17 atos tácitos em 4 categorias (orçamentário, administrativo, financeiro, comportamental). Combina 3 estratégias: padrões de nome/texto, LLM para casos ambíguos, e cruzamento SQLite para detectar NE nova referenciando NF antiga. Gera relatório por devedor, atualiza profiles.json e produz memorial jurídico pronto para citação. Use SEMPRE que o usuário pedir: "procurar reconhecimento", "ressuscitar faturas prescritas", "cadê atos interruptivos", "reviver crédito do [devedor]", "reconhecimento tácito", "marcos interruptivos", "Art. 202 CC", ou antes de descartar qualquer fatura por prescrição.
```

**DEPOIS (Proposta 5 adotada — iter 5 do run_loop `bwwqtr31d`, padrão "Intent → Triggers → Output/Exclusões"):**
```yaml
description: |
  Use para buscar, no acervo PRODAM, qualquer indício de que um devedor (DETRAN, SES, SSP, SEDUC, SEJUSC, SUSAM, SEAD, TCE e outros órgãos) tenha reconhecido dívida — pagamento parcial, pedido de parcelamento ou prorrogação, nova NE/empenho citando contrato antigo, ofício/email/ata/DOE/relatório de gestão mencionando o débito. O objetivo do usuário é interromper a prescrição quinquenal e salvar faturas antigas ou já dadas como prescritas.

  Acione sempre que a pergunta envolver: caçar/varrer/escanear/vasculhar/localizar reconhecimentos ou marcos interruptivos; verificar se determinado órgão pagou, parcelou, prorrogou ou admitiu dívida em documento; Art. 202 VI CC; ressuscitar ou reviver fatura/crédito; reconhecimento tácito.

  Produz relatório, atualiza profiles.json e gera memorial jurídico. NÃO use para cálculo puro de prescrição, validação de cadeia documental, geração de TRD, OCR ou consultas cadastrais simples.
```

#### Justificativa da escolha (sobre as 5 propostas)

- **Proposta 1** (~1055 chars, parágrafo denso): descartada — sem exclusões e volume excessivo.
- **Proposta 2** (~995 chars, bullets + 3 exclusões): descartada — bullets em description parecem lidar pior com o classificador que parágrafos (empírico cross-skills).
- **Proposta 3** (~960 chars, bullets "Sinais típicos:"): descartada pelo mesmo motivo.
- **Proposta 4** (~540 chars, parágrafo curto): descartada — corta verbos de ação (caçar/varrer/escanear) e termos jurídicos (Art. 202 VI CC, ressuscitar) necessários para disparo.
- **Proposta 5** (~850 chars, 3 parágrafos Intent → Triggers → Output/Exclusões): **ADOTADA**. Mesmo padrão que venceu em `consulta-acervo-prodam` (Proposta 4 da sessão anterior). Exclusões explícitas previnem conflito com `extracao-clausulas-contratuais`, `consulta-acervo-prodam`, `analise-prescricao-creditos`, `geracao-documentos-juridicos`.

#### Protocolo de validação pós-aplicação

Testar manualmente com 2-3 prompts que DEVEM ativar a skill:
1. "varre o acervo atrás de pagamento parcial do SES"
2. "a SEDUC tem algum ofício admitindo o débito?"
3. "cadê atos interruptivos das faturas prescritas do DETRAN?"

Se disparar em 2/3 ou mais → aprovada na prática. Se <2/