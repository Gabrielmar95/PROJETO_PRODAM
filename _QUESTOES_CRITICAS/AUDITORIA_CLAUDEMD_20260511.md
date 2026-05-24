# Auditoria CLAUDE.md — PROJETO_PRODAM

**Data:** 2026-05-11 18:00 GMT-4
**Skill:** `claude-md-management:claude-md-improver`
**Escopo:** 47 arquivos CLAUDE.md no working tree (`Glob **/CLAUDE.md`)
**Modo:** read-only — nenhuma edição aplicada (gate jurídico ativo)

---

## ACHADO PRINCIPAL — 47 não são 47

O `Glob` retorna 47 arquivos, mas **apenas 3-4 são documentação real**. Os outros **~43** são placeholders de cache do plugin `claude-mem` no formato:

```
<claude-mem-context>

</claude-mem-context>
```

(vazios ou com 1-2 linhas de "Recent Activity" injetadas pelo plugin)

**Implicação prática:** o número 47 cria falsa impressão de cobertura documental densa. A documentação real do projeto está concentrada em **4 arquivos canônicos**.

---

## TABELA — Status por arquivo

| # | Arquivo | Linhas | Tipo | Score | Observação |
|---|---------|--------|------|-------|------------|
| 1 | `CLAUDE.md` (raiz) | ~250 (visto no contexto) | DOC REAL | **A- (87)** | SSOT do projeto. Já contém Decisão Pendente `config_prodam.py` |
| 2 | `PRODAM_DOCS/CLAUDE.md` | 57 | DOC REAL | **A (90)** | Bem-estruturado: OCR + dossiês + 8 invariantes técnicas |
| 3 | `SPCF_EXTRACAO/CLAUDE.md` | 115 | DOC REAL | **A+ (94)** | Excelente: 10 invariantes de scraping + dual-key + gaps explícitos |
| 4 | `DETRAN_AUDITORIA/CLAUDE.md` | 9 | claude-mem cache | **N/A** | 1 entry "Cascade Map Of. 129/2021" — não é documentação |
| 5 | `scripts/auditoria_fisica/CLAUDE.md` | 9 | claude-mem cache | **N/A** | 1 entry "Audit Pipeline Directory Structure Created" |
| 6-47 | resto | 1-3 | claude-mem cache vazio | **N/A** | `<claude-mem-context></claude-mem-context>` puro |

**Arquivos auditados em detalhe (10/47):** raiz, PRODAM_DOCS, scripts, DETRAN_AUDITORIA, DOSSIES_MULTIFORMATO, DOSSIES_MULTIFORMATO/SES_SUSAM, tests, relatorios, dados, .claude/agents, scripts/auditoria_fisica, _AUDITORIA_FISICA, tests/auditoria_fisica, SPCF_EXTRACAO, detran_dashboard/server, .claude/CLAUDE.md.

---

## CLAUDE.md RAIZ — Assessment detalhado

| Critério | Peso | Score | Notas |
|----------|------|-------|-------|
| Commands/workflows | 20 | 18 | Bloco "COMANDOS ÚTEIS" rico; `py -3.12 scripts\...` por caso de uso |
| Architecture clarity | 20 | 17 | "ESTRUTURA DO PROJETO" + tabela SQLite OK; falta diagrama de fluxo entre `_ANALISE/prodam.db` (canônico) e `prodam.db` (raiz, derivada) |
| Non-obvious patterns | 15 | 14 | 18 regras jurídicas + 3 formatos de contrato + dual-key PRODAM↔PMM cobertos |
| Conciseness | 15 | 11 | Bloco "DECISÃO PENDENTE — config_prodam.py" tem 35 linhas — útil mas pesa no contexto que toda sessão carrega |
| Currency | 15 | 13 | Métricas datadas 08/05/2026; aviso `config_prodam.py` é de 2026-05-10/11 |
| Actionability | 15 | 14 | Comandos copy-pasteable; Decreto 53.464/2026 sem link explícito ao DOE |
| **Total** | 100 | **87** | **A-** |

**Sub-issues identificadas (sem propor edits — só listar):**

1. **Regra 4 atual mantém DETRAN sem `(PRESUMIDO)`** — decisão consciente registrada em memória 2026-05-11. CLAUDE.md raiz ainda diz `DETRAN=IGPM+1%+2% (PRESUMIDO)` na linha 64. Memória 2026-05-11 `CLAUDE.md Edit 1: Removed DETRAN "(PRESUMIDO)"` indica que essa edição foi feita em `auto_update_claude_md.py` mas **ainda não materializada** no CLAUDE.md publicado. Próximo run do gerador irá propagar.

2. **Bloco "DECISÃO PENDENTE"** (linhas finais, ~35 linhas) — apropriado como anchor de investigação D ativa, mas custa contexto em toda sessão. Após decisão final A/B/C/X, mover para `_QUESTOES_CRITICAS/` e deixar pointer de 1 linha.

3. **Regra 13** — REsp 793.969/RJ Min. José Delgado já corrigida (memória confirma 2026-05-08). OK.

4. **Regra 14** — RPV AM = 20 SM + Lei AM 2.748/2002. Hardcoded R$ 32.420 ainda presente. `auto_update_claude_md.py` já foi atualizado para "20 × SM vigente"; aguarda materialização.

---

## PRODAM_DOCS/CLAUDE.md — Assessment

**Score: A (90)** — Documento técnico denso de OCR; aponta corretamente para `..\CLAUDE.md` como canônico.

Forças:
- 8 invariantes técnicas concretas (MuPDF silence, OCR cascata, dedupe SHA-256, etc.)
- Comandos reexecutáveis com flags
- Valor canônico DETRAN R$ 17.802.420,55 + ressalva sobre reconciliações alternativas

Gap menor: a tabela "ARQUIVOS-CHAVE" não menciona `analisar_v4.py` substitui v3 explicitamente no contexto de migração — só na própria linha. Aceitável.

---

## SPCF_EXTRACAO/CLAUDE.md — Assessment

**Score: A+ (94)** — Melhor CLAUDE.md do repo. Modelo a replicar.

Por quê:
- 10 invariantes numeradas (Referer obrigatório, magic bytes vs Content-Type mentiroso, dual-key PRODAM+PMM, paginador limitado, etc.)
- Cada descoberta tem **dado quantitativo** ("perde 92%", "subiu 8,4% → 78,4%", "1.837/1.837 100%")
- Seção "GAPS ESTRUTURAIS REMANESCENTES" lista 5 limitações conhecidas sem solução técnica — economia de horas a quem tentar refazer
- Best-engine surpresa documentada (pdfminer > pdfplumber em layouts quebrados)

Sem issues materiais.

---

## CLAUDE.md PLACEHOLDERS — diagnóstico

**~43 arquivos** seguem o padrão `<claude-mem-context></claude-mem-context>` (vazio) ou contêm tabela de 1 linha de "Recent Activity".

**Origem:** plugin `claude-mem` v6.x (instalado conforme `~/.claude/settings.json` / `~/.claude/plugins`). Plugin cria/atualiza esses arquivos para injetar histórico de observações na sessão.

**Problema:** poluem o `find . -name CLAUDE.md` e inflam métricas de "documentação". Para auditorias futuras, filtrar com:

```powershell
Get-ChildItem -Path . -Recurse -Filter CLAUDE.md |
  Where-Object { (Get-Content $_.FullName -Raw).Trim() -notmatch '^<claude-mem-context>\s*</claude-mem-context>$' } |
  Select-Object FullName
```

**Não são "CLAUDE.md ruins"** — são caches do plugin. Não recomendar criação de conteúdo neles; eles são reescritos pelo plugin automaticamente.

---

## RECOMENDAÇÕES (sem aplicar — esperam aprovação)

### Tier 1 — Crítico
Nenhuma. A documentação real está em estado bom-a-excelente.

### Tier 2 — Útil
1. **CLAUDE.md raiz, bloco DECISÃO PENDENTE:** após o usuário escolher A/B/C/X para `config_prodam.py`, mover bloco para `_QUESTOES_CRITICAS/DECISAO_config_prodam.md` e deixar 1 linha de pointer no CLAUDE.md.
2. **Materializar edits já aprovados** que estão em `auto_update_claude_md.py` aguardando próximo run:
   - Regra 4: remoção do "(PRESUMIDO)" do DETRAN + redirect para `normalizador.py` como SSOT
   - Regra 14: RPV AM = "20 × SM vigente" (Lei AM 2.748/2002) em vez de R$ 32.420 hardcoded
   - Procedimento seguro: `Copy-Item CLAUDE.md CLAUDE.md.bak; py -3.12 scripts\auto_update_claude_md.py; diff CLAUDE.md.bak CLAUDE.md` — revisar diff ANTES de commitar.

### Tier 3 — Cosmético
3. Em `PRODAM_DOCS/CLAUDE.md`, na tabela de arquivos-chave, sinalizar `analisar_v4.py` como ativo e `_HISTORICO_OCR.md` como histórico arquivado.
4. Documentar em `CLAUDE.md` raiz (seção "OUTROS MAPAS DO PROJETO") que `<claude-mem-context>` é cache do plugin e **não** documentação editável.

### Anti-recomendação
- **NÃO** criar novos CLAUDE.md em subdiretórios profundos. O plugin claude-mem já gera artefatos lá; criar manualmente quebra a expectativa de reescrita automática.
- **NÃO** preencher os ~43 placeholders vazios com conteúdo manual.

---

## PRÓXIMOS PASSOS

Aguardando direção do usuário:

- (a) Aplicar Tier 2 #1 (mover bloco DECISÃO PENDENTE) — exige decisão A/B/C/X antes
- (b) Aplicar Tier 2 #2 (executar `auto_update_claude_md.py` com backup+diff)
- (c) Aplicar Tier 3 (cosmético)
- (d) Apenas registrar relatório e parar

**Gate jurídico ativo:** qualquer edit em `CLAUDE.md` raiz exige confirmação explícita com diff completo. Esta auditoria respeitou o gate — zero edits aplicados.
