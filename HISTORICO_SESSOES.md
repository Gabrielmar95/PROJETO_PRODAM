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
