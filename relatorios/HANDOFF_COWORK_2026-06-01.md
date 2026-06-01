# 🛠️ GUIA DE CONFIGURAÇÃO — PROJETO PRODAM no Claude Cowork
**Data:** 01/06/2026 · **Para:** Gabriel Mar (OAB/AM 15.697) · **Origem:** sessão Claude Code

## 0. Como usar este guia
A espinha dorsal é a §2 (**o mapa**) lida junto com a §3 (**passo a passo na tela**). A §4 é o
texto que você cola. As §§5–10 são o **briefing de contexto** (o que foi feito, o que falta) —
sirva-as ao Cowork via *Files*, não decore. Comece pela §1 para entender por que cada coisa vai
em cada lugar.

## 1. Modelo mental — os canais do Cowork (e quanto cada um "custa")
Pense no Cowork como tendo **6 caixas**, cada uma com um custo e uma persistência diferentes.
A regra de engenharia: **canal mais barato que ainda garanta o recall**.

| Canal | O que é | Custo / persistência | O que colocar aqui |
|-------|---------|----------------------|--------------------|
| **Instructions** (campo do projeto) | Texto curto sempre injetado em toda task | **Caro por atenção** (compete com tudo) · sempre-on | Só as **regras invioláveis** + a pendência nº1. Curto. |
| **`CLAUDE.md`** (raiz da pasta) | Regras do projeto, auto-lido ⚠️*(verificar)* | Barato se auto-lido · sempre-on | Estado do portfólio + regras detalhadas (auto-gerado). |
| **Files / Context** | Arquivos da pasta indexados p/ retrieval | **Barato** · carrega só quando relevante | **Volume:** REFERENCIA_JURIDICA, dossiês, CSVs, issues. |
| **VM sandbox** | Linux isolado que roda código sobre a pasta | Efêmero (por sessão) · só vê o que for montado | **Execução:** `scripts/`, `*.py`, recálculos. |
| **Connectors / MCP** | Conexões a dados/serviços (ex.: SQLite) | Persistente (config) · sob demanda | **Dados estruturados:** `prodam.db` via `sqlite-prodam`. |
| **Memory** | Memória automática, **por projeto** | Persiste entre sessões *do mesmo projeto* | Decisões/descobertas da operação (substitui memória global). |

`★ Insight ─────────────────────────────────────`
A armadilha clássica é tratar tudo como *Instructions* ("vou colar tudo pra garantir que ele
leia"). Isso **dilui** a regra que não pode falhar — quanto mais texto sempre-on, menos peso
cada linha tem. Inversamente, enterrar uma regra inviolável só em *Files* (retrieval) arrisca
ela **não ser puxada** na hora certa. A solução é estratificar: ~25 linhas invioláveis no
*Instructions*; todo o resto (volume) em *Files*; dados em *Connector*; código na *VM*.
`─────────────────────────────────────────────────`

## 2. ✦ O MAPA — onde juntar cada ativo do PROJETO_PRODAM
Esta é a peça central. Para cada ativo: **qual canal**, **como fazer na UI** e **por quê**.

| Ativo (no seu disco) | Canal no Cowork | Como configurar | Por quê |
|----------------------|-----------------|-----------------|---------|
| **Pasta `PROJETO_PRODAM/` inteira** | Workspace do projeto | "New Project" → **"use an existing folder"** → aponta p/ `C:\Users\gabri\Desktop\PROJETO_PRODAM` | É o *mount*. Tudo abaixo passa a existir p/ a VM e o retrieval. |
| **`CLAUDE.md`** (raiz, auto-gerado) | `CLAUDE.md` (auto-lido ⚠️) | Já está na raiz; **nada a fazer** além de **verificar a leitura** (§3, passo 11) | Regras + estado do portfólio, lidos a cada task — *se* o auto-read valer no seu build. |
| **`relatorios/PROJECT_INSTRUCTIONS_PARA_COLAR.md`** | **Instructions** | **Copiar o conteúdo e colar** no campo Instructions | Canal always-on **garantido**: as 5 regras + pendência nº1 não dependem do auto-read. |
| **`PRODAM_DOCS/profiles.json`** (SSOT) | Files **+** VM | Fixar (pin) em *Files*; a VM lê via `py` | SSOT dos 70 devedores. Pin = o Claude sabe que ela é a fonte; VM = scripts a consomem. |
| **`prodam.db`** (8 tabelas) | **Connector `sqlite-prodam`** + VM | *Connectors* → confirmar `sqlite-prodam` habilitado (já está no `settings.local.json`) | Dados estruturados → SQL direto é o canal certo (não Files). |
| **`PRODAM_DOCS/REFERENCIA_JURIDICA/`** (20 subpastas) | **Files / Context** | Pin na pasta; **destacar** `01_NOTA_METODOLOGICA/` e `PRECEDENTES_VERIFICADOS.md` | Base jurídica volumosa → retrieval. Nunca no *Instructions* (estouraria). |
| **Satélites** `STATUS_DEVEDORES.md`, `WORKFLOW_COBRANCA.md`, `PLAYBOOK_ORGAOS_V2.md` | Files / Context | Pin os três | Contexto sob demanda (lista completa, pipeline F0→F6, playbook DETRAN 94/100). |
| **`DOSSIES_MULTIFORMATO/`** (≈70 × 5 formatos) | Files / Context (sob demanda) | **Não** fixar tudo; deixar a pasta no mount e puxar por devedor | Volume enorme → retrieval pontual quando trabalhar um órgão específico. |
| **`_QUESTOES_CRITICAS/`** (16 issues) | Files / Context | Pin a pasta; quentes: **06, 08, 09, 14** | Backlog de pendências; barato manter como retrieval. |
| **5 arquivos de prescrição** (`reconciliar_prescricao.py`, `RECONCILIADOR.py`, `_out_presc.txt`, …) | VM (rodar) + Files (ler saída) | Já no mount; rodar na VM; ler `_out_presc.txt` em *Files* | Reproduzir a auditoria P1 (a pendência nº1). |
| **`scripts/`** (pipelines, consultas, gerador) | **VM** | Rodar com `py -3.12` na 1ª sessão | Canal de execução. `consultas.py`, `auto_update_claude_md.py`. |
| **`.claude/`** (skills, agents, commands, hooks, `settings.local.json`) | Montado junto | Vai junto com a pasta | Skills/commands devem funcionar. ⚠️ **Hooks `.ps1`**: a VM é Linux → execução **não verificada**; testar antes de confiar. |
| **`~/.claude/.../memory/`** (memórias **globais**) | ⚠️ **Fora do mount** | Plano B: usar **Memory nativa** do Cowork **ou** destilar num `MEMORIAS_CHAVE.md` dentro da pasta e dar pin | A VM **só vê a pasta do projeto** → a memória global fica invisível. |
| **`~/CLAUDE.md` e `~/Desktop/CLAUDE.md`** (dumps claude-mem) | ⚠️ Poluição potencial | (Opcional, com OK) `claudeMdExcludes` em `.claude/settings.local.json` | Se o Cowork subir a árvore de ancestrais, esses dumps entram no contexto sem valor. |
| **PDFs (provas)** | Files (mount) | Permanecem; **permissão "Ask before acting"** é o freio | O hook anti-delete pode não rodar na VM; a confirmação humana de exclusão é o backstop. |

## 3. Passo a passo na interface (o que clicar)
> Você segue isto literalmente. Se algum rótulo na sua versão estiver diferente, me avise — não
> invento telas.

1. **Instalar/abrir o Claude Desktop** (macOS ou Windows, com assinatura paga). **No Windows,
   primeira vez:** instale o **Git for Windows** e **reinicie o app** (requisito do Cowork).
2. **Entrar no Cowork** (comando `/desktop` no app, ou abrir o modo Cowork).
3. Barra lateral esquerda → **"New Project"**.
4. Entre as 3 opções (*start from scratch* / *import from a chat* / **use an existing folder**),
   escolha **"use an existing folder"** → selecione **`C:\Users\gabri\Desktop\PROJETO_PRODAM`**.
5. **Nomeie** o projeto: `PRODAM — Recuperação de Créditos`.
6. **Campo Instructions** → **cole o texto da §4** (são as regras invioláveis + pendência nº1).
7. **Files / Context** → fixe (*pin*): `PRODAM_DOCS/REFERENCIA_JURIDICA/` (com destaque p/
   `01_NOTA_METODOLOGICA/` e `PRECEDENTES_VERIFICADOS.md`), `PRODAM_DOCS/profiles.json`,
   `STATUS_DEVEDORES.md`, `WORKFLOW_COBRANCA.md`.
8. **Connectors** → confirme **`sqlite-prodam`** habilitado (apontando p/ `prodam.db`).
9. **Permissão** → **"Ask before acting"** (perguntar antes de agir) — protege PDFs e git.
10. **Create** (criar o projeto).
11. ✅ **TESTE DE INTEGRIDADE (1ª mensagem):** pergunte —
    *"Quais regras do CLAUDE.md do projeto você está enxergando? Cite a Regra #13 sobre o
    REsp 793.969 e quem é o relator."* → se responder **José Delgado** (e não Teori), o auto-read
    do `CLAUDE.md` está OK. Se não souber, **o auto-read não vale no seu build → as regras do
    campo Instructions seguram** (por isso elas estão lá).
12. **Primeiros comandos** (peça ao Cowork para rodar, na VM):
    ```powershell
    py -3.12 scripts\auto_update_claude_md.py     # sincroniza métricas/alertas/pipeline
    py -3.12 scripts\consultas.py --lista          # 15 queries forenses
    py -3.12 reconciliar_prescricao.py             # reproduz a auditoria de prescrição (P1)
    ```
13. **(Opcional, só com seu OK)** adicionar `claudeMdExcludes` em `.claude/settings.local.json`
    para excluir `~/CLAUDE.md` e `~/Desktop/CLAUDE.md` (dumps claude-mem) **se** aparecerem
    poluindo o contexto.

## 4. Texto exato para o campo *Instructions* (colar)
```
Projeto PRODAM — Recuperação de créditos (Contrato 002/2026).
Escritório Brandão Ozores · Cliente PRODAM S.A. (estatal, Lei 13.303/2016).
Portfólio: 70 devedores · R$ 83.668.078,44 exigível (R$ 125.245.390,64 atualizado) · 3.477 faturas.
Fee: 20% do recuperado. Relatórios quinzenais (multa R$500/dia; 10% do crédito por prescrição perdida).

SSOT: PRODAM_DOCS/profiles.json (NUNCA usar Demonstrativo Excel antigo).
Base jurídica: PRODAM_DOCS/REFERENCIA_JURIDICA/ (20 subpastas) — consultar ANTES de qualquer parecer.
Banco: prodam.db (SQLite, 8 tabelas) via Connector sqlite-prodam. Queries: scripts/consultas.py.

REGRA 1 — JURÍDICO: nunca inventar jurisprudência/lei/precedente. Usar PRECEDENTES_VERIFICADOS.md.
REGRA 2 — DADOS: valores em Decimal (nunca float), BRL "R$ 1.234,56", UTF-8 BOM, CSV separador ";".
REGRA 3 — CLAUDE.md é auto-gerado: no início da sessão rodar `py -3.12 scripts/auto_update_claude_md.py`.
REGRA 4 — FATOS VERIFICADOS:
  - Fee 20% · RPV/AM estadual = 20 SM (Lei AM 2.748/2002) · prescrição por fatura individual.
  - REsp 793.969/RJ: relator p/ acórdão = José Delgado (Teori Zavascki foi vencido — nunca citar como relator).
  - Tema 1.109/STJ: gestor não renuncia tacitamente. Art. 202 CC: interrupção uma única vez (REsp 1.963.067/MS).
  - Empenho (NE) interrompe prescrição; NF do credor não. Decreto AM 53.464/2026 (substitui 51.084/2025; checar 4 exceções).
  - FUHAM = Fundação Alfredo da Matta · FHAJ = Fundação Hospital Adriano Jorge (nunca inverter).
REGRA 5 — Windows + PowerShell; Python `py -3.12` (sem venv); operações git destrutivas só com OK; PDFs são prova (não apagar).

⚠️ PENDÊNCIA Nº 1: a data de prescrição do profiles.json diverge do CSV e é internamente
inconsistente (SEDUC consta prescrito E com R$ 49,2M exigível). NÃO disparar cobrança em lote
por prazo sem antes reconciliar e decidir a fonte verdadeira.
```

## 5. Linha do tempo — do 1º plano até hoje (contexto p/ *Files*)
> Git começa em **20/04/2026**; o projeto é anterior (changelog 14/04, plano multi-agente 19/04,
> `DOSSIES_MULTIFORMATO/` já existente).

| Período | Marco |
|---------|-------|
| **~14–19/04** | Concepção; **plano Multi-Agente** (35 agentes/6 esquadrões/11 sessões) aprovado 19/04; dossiês + auditoria de completude. |
| **20/04** | `47e6645` commit inicial (snapshot pós-restauração, −53 GB); sessões DETRAN. |
| **23–24/04** | Config em 3 camadas; skills jurídicas; patch corrupção DETRAN. |
| **07–10/05** | Pipeline mestre (69 devedores); auditoria física → `inventario.json`; 17 scripts consolidados em `scripts/`. |
| **12/05** | **Auditoria DETRAN** → R$ 12,86M em risco; salvaguardas (pre-commit/hooks/.gitignore); **cascata Teori→Delgado**. Tag `pre-auditoria-DE-2026-05-12`. |
| **13/05** | **Setup do Git** (versionamento grande). **TRD SES/SUSAM pronto: R$ 8,23M / 82 faturas / D+141.** |
| **24–26/05** | Limpeza do repo (DBs/PDFs → `.gitignore`); `CLAUDE.md` enxuto + 3 satélites. |
| **27/05** | **Cron diário de prescrição** (causa-raiz "ADS escapar"); validador CI anti-"Teori-relator"; memorando **exposição R$ 10,46M**; triagem lote `d_plus=-20` (R$ 75,6M). |
| **28–29/05** | `fmt_brl` strict-Decimal; DRY; auditoria `float()`; +10 testes. 18 devedores **sem `d_plus`** (R$ 6,58M invisíveis ao cron). |
| **30–31/05** | Hooks cloud; **PreCompact** grava `.remember/`; CLAUDE.md consolidado (**PR #11**); fecha **PR #1**; **PR #12** (tidy). |
| **31/05–01/06** | **Em curso (não commitado):** auditoria de prescrição SSOT×CSV → revela a divergência da §10. |

## 6. Estado do portfólio (fonte: `CLAUDE.md`, regen 30/05)
- **70 devedores** (26 Direta · 21 Indireta · 22 Privadas) · **R$ 83.668.078,44 exigível**
  (R$ 125.245.390,64 atualizado) · **3.477 faturas** (2.326 exig. · 1.082 presc.) ·
  **12 FORTE · 15 MÉDIA · 42 FRACA**.
- **Pipeline:** ANALISAR_DOCUMENTACAO=36 · CLASSIFICAR=17 · ENVIAR_TRD=9 · PROTOCOLAR_PETICAO=5
  · HABILITAÇÃO=1 · N/A=1 · AVALIAR_SUCESSAO=1.

| Top 10 | Exigível | Força | Próximo passo |
|--------|----------|-------|---------------|
| SEDUC | R$ 49.215.512,48 | FORTE | ANALISAR_DOCUMENTACAO |
| SES/SUSAM | R$ 4.783.356,52 | FORTE | ENVIAR_TRD |
| SSP | R$ 4.553.230,80 | FORTE | PROTOCOLAR_PETICAO |
| SEJUSC | R$ 2.589.660,12 | MÉDIA | ANALISAR_DOCUMENTACAO |
| SEAD | R$ 2.339.702,20 | FORTE | ENVIAR_TRD |
| BRADESCO | R$ 2.226.517,80 | FRACA | CLASSIFICAR |
| CETAM | R$ 1.256.564,28 | FRACA | CLASSIFICAR |
| SEDECTI | R$ 1.249.203,13 | MÉDIA | ANALISAR_DOCUMENTACAO |
| SALUX | R$ 1.027.949,15 | FRACA | CLASSIFICAR |
| POLÍCIA CIVIL | R$ 960.481,71 | MÉDIA | ANALISAR_DOCUMENTACAO |

→ Lista completa em `STATUS_DEVEDORES.md`; pipeline F0→F6 em `WORKFLOW_COBRANCA.md`.

## 7. As 4 fontes de verdade
1. **Git/GitHub** (`origin` = github.com/Gabrielmar95/PROJETO_PRODAM) — registro oficial. Branch `main`.
2. **`PRODAM_DOCS/profiles.json`** — SSOT dos 70 devedores (fora do repo, `.gitignore`). Nunca o Excel antigo.
3. **`PRODAM_DOCS/REFERENCIA_JURIDICA/`** (20 subpastas) — base jurídica; `PRECEDENTES_VERIFICADOS.md`
   é a única jurisprudência checada (catalogou 3 fabricados + 6 distorcidos).
4. **Memórias** — no Cowork, migram para a **Memory nativa do projeto** (a global fica fora do mount).

## 8. Infraestrutura técnica
- **Git:** 91 commits. PRs #1 (CLOSED→#11), #3/#4/#8/#9/#10/#11/#12 (MERGED). Tag `pre-auditoria-DE-2026-05-12`.
  **Git destrutivo exige confirmação.**
- **`prodam.db`** (8 tabelas): `spcf_nfs` (52.998), `spcf_empenhos` (16.789), `pendrive_docs` (3.699),
  `spcf_faturas` (1.837), `cruzamento_spcf_pendrive` (1.460), `reclassificacao` (1.261),
  `spcf_contratos` (362), `devedores` (81). 5 views (`v_fatura_completa` etc.).
- **Scripts:** `auto_update_claude_md.py`, `sincronizar_prodam.py`, `consultas.py` (15 queries),
  `orgao_pipeline_completa.py`, `normalizador.py`, `prodam_utils.py` (`fmt_brl`).
- **CI/proteções:** `tests.yml` valida `profiles.json`; `pytest tests/`; pre-commit `ruff-check`;
  hook `block_pdf_delete.ps1`; PreCompact grava `.remember/`.
- **Convenções:** Decimal nunca float · BRL `R$ 1.234,56` · CSV `;` + UTF-8 BOM · JSON+XLSX+CSV
  (JSON é SSOT) · SPCF `time.sleep(1.5)` · Playwright (não Selenium).

## 9. O QUE FALTA FAZER (pendências priorizadas)
> Status inferido de commits + títulos das issues. "⚠️ verificar" = não confirmei o estado final.

**🔴 P1 — Integridade da data de prescrição (SSOT×CSV) — bloqueia ações em lote.** A auditoria de
31/05 mostrou que `profiles.json` e `profiles_resumo.csv` **divergem em quase todos os 69
devedores do SSOT** e que o SSOT tem datas suspeitas (22 órgãos na mesma `2026-03-20` já vencida;
**SEDUC prescrito porém R$ 49,2M "exigível"**). **Decisão humana:** qual fonte vence e qual regra
de reconciliação. Sem isso, o alerta do `CLAUDE.md` (só aponta SSP) pode estar subnotificando.
Detalhe na §10. Issues 09 e 14. *(Obs.: o SSOT tem 69 entradas vs. 70 na métrica do CLAUDE.md —
conferir a diferença de contagem, possivelmente FENIXSOFT2 fora do SSOT, issue 06.)*

**🟠 P2 — Prazos iminentes.** SSP R$ 4,55M, alerta 2026-06-30 (~30 d), fase PROTOCOLAR_PETICAO.
ADS (issue 07) — "prescreve em 3 dias" de ~27/05 → ⚠️ verificar se consumou (aparece vencida −49 d
em 31/05; o cron diário nasceu deste caso). Lote `d_plus=-20` (issue 09): 22 órgãos, R$ 75,6M.

**🟡 P3 — Cobranças prontas.** SES/SUSAM: TRD pronto (R$ 8,23M / 82 fat. / D+141) → ENVIAR_TRD;
verificar protocolo. SEAD em ENVIAR_TRD. Total: 9 em ENVIAR_TRD, 5 em PROTOCOLAR_PETICAO.

**🟡 P4 — Pipeline documental (volume).** 36 em ANALISAR_DOCUMENTACAO (inclui **SEDUC, R$ 49,2M**,
o maior, ainda nesta fase); 17 em CLASSIFICAR; 1 HABILITAÇÃO (Banco Master, liquidação);
1 AVALIAR_SUCESSAO.

**🟢 P5 — Issues em `_QUESTOES_CRITICAS/`.** 10/11/12 (BRL/DRY/float) ✅ PRs #3/#4. 15/16/17
(merge/handoff/PR#1) ✅ PRs #8/#9/#11. 13 (skill `run-prodam`) ⏸️ adiada p/ local. 00/01/02
(SSOT×Pastas, drift) ⚠️ verificar. 03 (reversão drift) ⚠️ verificar. **06 FENIXSOFT2** (R$ 1,07M
fora do SSOT) 🔴 aberta. **08 exposição contratual** 🟠 aberta.

**🟢 P6 — Sistema Multi-Agente.** Plano de 35 agentes aprovado 19/04 — parcial (skills/agents
existem; orquestrador não). Avaliar se o Cowork retoma.

**Sequência sugerida:** (1) sanear P1 → (2) prazos P2 (ADS/SSP, lote -20) → (3) disparar P3
(TRD SES/SUSAM) → (4) vazar P4 (começar por SEDUC) → (5) fechar P5 (FENIXSOFT2, exposição).

## 10. Pendência Nº 1 em detalhe (a divergência de prescrição)
Saída de `reconciliar_prescricao.py` (`_out_presc.txt`, 31/05; 69 devedores no SSOT):
- **22 órgãos** com `data_prescricao_proxima = 2026-03-20` (vencida há 72 d) — SEDUC (R$ 49,2M),
  SEAD, POLÍCIA CIVIL, SEDECTI… — todos com `val_exig` alto apesar de "prescritos". Datas redondas
  em lote (`2027-01-01`, `2029-10-01`) sugerem **preenchimento por default, não cálculo
  fatura-a-fatura** (viola a Regra de prescrição por fatura).
- **`d_plus` do CSV diverge do SSOT em ~todos** (DETRAN −72 SSOT vs +730 CSV; privados 1219 vs 1271).
- **Conflito com o alerta:** `CLAUDE.md` lista só SSP <90 d; a auditoria ao vivo aponta dezenas
  vencidos/iminentes.
- **O que decidir (humano):** (a) qual fonte vence; (b) recalcular por fatura a partir do
  `prodam.db` (vencimento + marcos interruptivos) em vez do campo estimado; (c) reescrever
  `data_prescricao_proxima` no SSOT e re-rodar o gerador.
- **5 arquivos não-rastreados:** `reconciliar_prescricao.py` e `RECONCILIADOR.py` (idênticos —
  consolidar em um); `_out_presc.txt` (saída); `_err_presc.txt`/`_saida_prescricao.txt` (vazios).

## Fontes (Cowork — verificadas em sessões anteriores, jun/2026)
- support.claude.com/articles/13345190 — *Get started with Claude Cowork*
- support.claude.com/articles/14116274 — *Organize your tasks with Projects in Cowork*
- support.claude.com/articles/14128542 — *Let Claude use your computer in Cowork* (sandbox/VM)
- code.claude.com/docs/en/desktop · /desktop-quickstart — app desktop, Windows + Git for Windows
- claude.com/docs/cowork/guide/projects · claude.com/product/cowork
- github.com/anthropics/claude-code/issues/30530 — limitação anterior de leitura de `CLAUDE.md` no Desktop
