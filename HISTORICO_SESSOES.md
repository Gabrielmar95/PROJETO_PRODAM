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

Se disparar em 2/3 ou mais → aprovada na prática. Se <2/3 → reverter via `git revert` do commit isolado.

#### Comando de reversão (caso degradação seja detectada)

```powershell
# Reverte só a mudança da description na skill
# (SKILL.md não está em git, então reversão é manual: copiar o bloco "ANTES" acima de volta)
Set-Content -Path "$env:USERPROFILE\.claude\skills\reconhecimento-tacito-hunter\SKILL.md" `
  -Value (Get-Content -Path <arquivo>.bak -Raw)
```

Alternativamente, a description original fica registrada neste HISTORICO_SESSOES.md (bloco "ANTES") e pode ser colada de volta em 10 segundos.
