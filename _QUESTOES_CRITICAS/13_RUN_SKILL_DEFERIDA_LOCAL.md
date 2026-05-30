# 13 — Skill `run-prodam` (smoke harness) adiada para a máquina local

> Status: deferred-to-local / needs-human-decision
> Aberta em: 2026-05-28 (derivada da avaliacao do /run-skill-generator)
> Tipo: tooling de engenharia (NAO juridico — fora do gate manual)
> Severidade: 🟢 baixa (conveniencia; sem urgencia prescricional)

## Por que adiada

O `/run-skill-generator` exige, no "definition of done", **lançar o app real neste
container e interagir com ele**. O "app real" do PRODAM é o pipeline forense de dados, que
depende de `PRODAM_DOCS/` + `prodam.db` (gitignored, local-only, 25 GB). Em sessao cloud
esses dados estao ausentes, entao a parte que mais importa **nao roda** — a regua do gerador
so e cumprivel na maquina local. Decisao do advogado: autorar a skill completa localmente.

## Mapa de fronteira (o valor a preservar)

**Cat A — roda em checkout limpo (sem PRODAM_DOCS/prodam.db):**
- `pytest tests/` (suite: 125 testes, zero dependencia de dados)
- `python3 scripts/validar_citacoes.py` (varre `.md`/`.py` do repo; exit 0 esperado)
- `python3 scripts/alerta_prescricao.py --check` (le `profiles_resumo.csv` commitado; exit
  0/1 = rodou ok, 2 = CSV faltando)
- `python3 -m compileall -q scripts/ tests/` (sintaxe)
- `ruff check --select E9,F63,F7,F82 scripts/ tests/` (lint gate do pre-commit)

**Cat B — precisa de dados local; crash no import:**
- `scripts/auditoria_completude_devedor.py:25` — `sqlite3.connect("prodam.db")` no topo
- `scripts/dossie_multiformato_devedor.py:37` — idem
- `scripts/consultas.py:16` — DB no load (crash na query)
- `scripts/sincronizar_prodam.py` — orquestrador (rebuild DB + auditoria + dossies)
- `scripts/orgao_pipeline_completa.py --orgao X` — precisa `PRODAM_DOCS/<X>/_CONSOLIDADO/`

## Design proposto (para autorar na maquina local)

- `.claude/skills/run-prodam/{SKILL.md, driver.py}`.
- `driver.py` **nao-mutante**: roda os 5 checks da Cat A, imprime tabela PASS/FAIL/SKIP,
  exit 0 sse nenhum FAIL. Trata `alerta --check` exit 0/1 como OK (1 = ha alertas = normal),
  so 2 = FAIL. `ruff` opcional (SKIP se ausente).
- **Cuidado critico:** excluir `auto_update_claude_md.py` do driver — sem DB ele regenera o
  `CLAUDE.md` como placeholder (clobber).
- `SKILL.md` (frontmatter auto-load com verbos "rodar/testar/verificar/smoke") documenta o
  agent-path (rodar o driver) + este mapa de fronteira + ponteiro para `/sincronizar-prodam`.
- Na maquina local, verificar o driver end-to-end **e** o pipeline real (que aqui nao roda).

## Feito nesta sessao (cloud)

- `requirements-dev.txt` criado (fecha o loop de `requirements.txt:31-33`): pytest + mypy + ruff.
- Nota no `.claude/napkin.md` (item 5 de "Execução & Pipeline"): resumo "cloud vs local".

## Criterio de aceite (quando autorada local)

- [ ] `.claude/skills/run-prodam/driver.py` roda os 5 checks da Cat A e sai 0 em repo limpo.
- [ ] `SKILL.md` com boundary map e todos os blocos verificados na maquina local.
- [ ] Verificado que o driver nao muta arquivo rastreado (so `__pycache__`/`.pytest_cache`).
- [ ] Decisao: manter a skill so-cloud-smoke ou estende-la para dirigir o pipeline real local.
