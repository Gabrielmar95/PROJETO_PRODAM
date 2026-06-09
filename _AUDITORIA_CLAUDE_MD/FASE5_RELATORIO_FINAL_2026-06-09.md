# FASE 5 — Relatório Final: refatoração do CLAUDE.md + gerador
_2026-06-09 · Commits: `a2c93dc` (backup) → `1c79210` refactor(gerador) em PROJETO_PRODAM · `89e6c83` fix(skills) em PRODAM_DOCS · `ee59c3c` fix em DETRAN_AUDITORIA_COMPLETA._

## 1. Problemas confirmados e corrigidos

O achado mais grave não estava na pré-análise: o filtro de alertas (`0 < dias <= 90`) **escondia em silêncio 23 devedores com data de prescrição no passado/stale — Σ R$ 59,2M exigível, incluindo SEDUC (R$ 49,2M)** — num contrato com multa de 10% por prescrição perdida. O CLAUDE.md agora expõe a linha 🔥 agregada (§3) e o STATUS_DEVEDORES.md traz a lista nominal, com a cautela jurídica correta (data vencida ≠ prescrição consumada; conferir marcos do Art. 202 VI CC). Também corrigidos: PLAYBOOK/WORKFLOW gerados que citavam ~10 scripts e 7 skills inexistentes (incl. `normalizador.py`, contradizendo a própria regra 5.4); somas em `float` no gerador (violava a própria Regra 16); ausência de validação da fonte (profiles.json corrompido geraria lixo com exit 0); path errado do catálogo de precedentes na regra 5.17; `_ARQUIVO_DRIFT/` inexistente; "20 subpastas" (são 18, agora contagem dinâmica).

## 2. O que mudou no gerador (`scripts/auto_update_claude_md.py`)

`validate_profiles()` fail-fast (≥50 devedores, `_metadata`, soma>0 — exit 1 sem escrever nada); `compute_metrics()` com `Decimal` via `prodam_utils.brl` e 3 buckets de prescrição (urgente/vencida/sem-data), ordenação com tie-break determinístico; CLAUDE.md com bloco **NUNCA (8 vedações)** no topo, **13 regras** renumeradas (ex-18, fusões 5.6+5.9 e 5.17+5.18, históricos preservados em comentários `#`), top-5, armadilhas novas (`_ARCHIVE`, `ANTHROPIC_API_KEY`); STATUS_DEVEDORES.md ganhou a tabela 🔥 de vencidas, a lista de sem-data e as contagens vivas do `prodam.db` (migradas do §10); WORKFLOW/PLAYBOOK passaram a citar só scripts/skills existentes no disco. Novo `tests/test_auto_update_claude_md.py` (21 testes, incl. regressão "vencida não some").

## 3. Drifts corrigidos nas skills (`PRODAM_DOCS/_SKILLS/` — 13 arquivos)

Decreto **53.464/2026** como vigente (revogou 51.084/2025): `arvore-decisao-contestacao` (ramo 2 inteiro), `registro-interacoes-devedor`, `workflow-pos-analise-devedor` (com ressalva de conferir o dispositivo correspondente), `triagem-consistencia-versoes`. REsp 793.969/RJ com **Rel. p/ acórdão Min. José Delgado (Teori vencido)**: `classificacao-forca-probatoria` (3 pontos), `nota-liquidacao-extrator`, `prodam-juridico`, `validador-cadeia-documental-fatura`, `montagem-dossie-comprobatorio` (2 pontos). Teto de **RPV/AM = 20 SM (Lei 2.748/2002, confirmada na ALEAM/Legisla.AM) = R$ 32.420 em 2026**: `risco-processual-matriz` (nota reescrita — FUHAM R$ 44K na verdade EXCEDE o teto estadual), `precatorios-rpv-fragmentacao` (description + tabela + simulação), `blindagem-pre-execucao`, `montagem-dossie-comprobatorio`, `compensacao-administrativa-workflow` (2 pontos). DETRAN: Lei "2.478" → 2.748/2002 e R$ 30.360 → 20×SM vigente.

## 4. Validação

**Ciclo fechado**: gerador rodou 3× — idempotente (0 divergências além do timestamp nos 5 arquivos); `pytest tests\ -v` → **157 passed**; `/sincronizar-prodam` intacto (mesmo nome de script, mesma CLI, exit codes agora corretos para a etapa "claude"). **Regressão nominal 24/24**: as 18 regras e 6 fontes têm destino confirmado no output regenerado (R1-R13 + NUNCA-2/4/6/7 + Identidade + §6.1-6.6 — rastreabilidade na tabela da Fase 3). **Cobertura (10 perguntas típicas)**: índice do CT 022/2014 → Regra 10 (cláusula econômica + skill `extracao-clausulas-contratuais`); apagar PDF? → NUNCA-1; decreto vigente? → Regra 1; rodar sincronização? → §9; teto RPV/AM? → Regra 12; checar antes de rodar no terminal? → NUNCA-5 e NUNCA-8; citar REsp achado no Google? → Regra 13 + NUNCA-3; juros default? → Regras 8-10; prescrições críticas? → §3 (SSP 21d, SEJUSC 83d, 🔥23); FUHAM=Adriano Jorge? → NUNCA-7 (não — Alfredo da Matta). Sem lacunas.

**Tokens (chars/4)**: CLAUDE.md 2.148 → **2.212 (+3%)** — a estimativa da Fase 3 (−9%) não se confirmou: os cortes aprovados (−336) foram consumidos pelo bloco NUNCA completo e pela linha 🔥 (+400). Avaliação: troca favorável (8 vedações + risco de R$ 59,2M visível por +64 tokens), mas se quiser enxugar, o caminho é encurtar a redação do NUNCA (~−150 tokens) — 1 edit no gerador.

## 5. Lacunas deixadas para depois (fora do escopo desta refatoração)

1. **profiles.json**: conciliar `faturas_total ≠ exig+presc` (SES/SUSAM 62 · SEJUSC 6 · SSP 1) e **recalcular as 23 datas de prescrição vencidas/stale** + 18 sem data — o gerador agora expõe, não resolve.
2. **Decreto 53.464/2026**: arquivar o PDF do DOE na REFERENCIA_JURIDICA (não localizado na web; base local é a única prova de teor).
3. **Skills no Cowork**: o cache instalado ainda espelha as versões antigas — reinstalar as 13 skills corrigidas via Settings > Capabilities (cache é somente leitura).
4. **Conflitos documentados sem mexer (C-1..C-6 da Fase 3)**: plugin `productivity-prodam` (start/update escrevem CLAUDE.md que o gerador sobrescreve; thresholds de alerta divergentes) e regra global de dados sensíveis × satélites versionados — decisão sua quando quiser.
5. Hook quebrado de terceiros: plugin CockroachDB dispara `check-sql-files.py` com path inválido a cada edição (ruído inofensivo) — desativável nas configurações do plugin.
