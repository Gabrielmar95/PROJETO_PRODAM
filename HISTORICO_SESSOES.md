# Histórico de Sessões — PROJETO PRODAM

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
