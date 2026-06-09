# FASE 3 — Diagnóstico e Proposta: CLAUDE.md + gerador `auto_update_claude_md.py`
_Auditoria de 2026-06-09. Fases 1-2 concluídas (somente leitura; nada foi editado). Implementação aguarda aprovação item a item._

---

## 1. TABELA DE ACHADOS — Fase 1 (pré-análise confirmada/refutada + extras)

| # | Achado | Veredito | Evidência (1 linha) |
|---|--------|----------|---------------------|
| A1 | Regra 5.4 é anti-regra longa (histórico datado do que NÃO existe) | **CONFIRMADO** | 94 palavras, "verificado 2026-06-08" no output; gerador linha 322 |
| A2 | Regra 5.14 mistura dois assuntos (fee + RPV) | **CONFIRMADO** | Fee 20% também já está na Seção 1 (3ª linha) — tripla ocorrência com WORKFLOW |
| A3 | Regra 5.15 duplica Seção 8 (profiles.json SSOT) | **CONFIRMADO** | §8 tabela linha 1 já diz "**SSOT** dos 69 devedores" |
| A4 | Regras 5.17 × 5.18 se sobrepõem | **CONFIRMADO** | Ambas mandam consultar `REFERENCIA_JURIDICA/`; **agravante**: path da 5.17 está ERRADO — `PRECEDENTES_VERIFICADOS.md` está em `11_PESQUISAS_ORIGINAIS/`, não na raiz |
| A5 | Inconsistência de pastas de arquivamento | **CONFIRMADO** | `_BACKUPS/` existe; `_ARQUIVO_DRIFT/` **não existe** no disco; `_ARCHIVE` só em `Desktop\_LIXO_NAO_USAR\`; armadilha "não executar de dentro de _ARCHIVE" ausente |
| A6 | Falta seção "NUNCA" consolidada | **CONFIRMADO** | Vedações diluídas em 5.4/5.8/5.15/5.16/§7 |
| A7 | Falta armadilha `ANTHROPIC_API_KEY` | **CONFIRMADO** | Zero menções no CLAUDE.md/satélites (prejuízo ~US$100 relatado pelo usuário) |
| A8 | Links vs `@import` | **CONFIRMADO correto como está** | Nenhum `@import` em uso; satélites custariam +~2.5k tokens/conversa se importados (STATUS ~1.674 + WORKFLOW ~837). Manter links |
| A9 | Custo Seções 2-3 | **MEDIDO** | §2 ≈ 263 tokens, §3 ≈ 37 tokens (total arquivo ≈ 2.148). Alertas valem (multa 10%/prescrição); top-10→top-5 economiza ~110 tokens |
| A10 | Números batem com profiles.json? | **BATEM (recomputado com Decimal)** | 69 (26/21/22) ✓ · R$ 83.668.078,44 ✓ · R$ 125.245.390,64 ✓ · 3477/2326/1082 ✓ · força 12/15/42 ✓ · pipeline ✓ · top-10 ✓ |
| A11 | **EXTRA — alertas ocultam prescrições vencidas/stale** | **CONFIRMADO (grave)** | Filtro `0 < dias <= 90` (gerador l.247) descarta em silêncio: **22 devedores com data 2026-03-20** (inclui SEDUC R$ 49,2M), ADS 2026-04-12, SEMIG `'N/A'`, 17 null. Risco: multa contratual de 10% por prescrição perdida |
| A12 | EXTRA — profiles.json internamente inconsistente | **CONFIRMADO (fonte, não gerador)** | 3477 ≠ 2326+1082 (gap 69): SES/SUSAM 324≠82+180 (62), SEJUSC 160≠61+93 (6), SSP 181≠66+114 (1) — faturas excluídas/canceladas sem conciliação |
| A13 | EXTRA — gerador usa `float` em dinheiro | **CONFIRMADO** | `compute_metrics` l.218-221 e l.424 (`float(d.get("val_exig"...))`) — viola a própria Regra 16 |
| A14 | EXTRA — gerador não valida a fonte antes de escrever | **CONFIRMADO** | `main()` só checa `PROFILES.exists()`; profiles.json truncado geraria CLAUDE.md lixo sem erro |
| A15 | EXTRA — PLAYBOOK gerado cita ≥8 scripts inexistentes | **CONFIRMADO** | `ocr_v4.py`, `normalizador.py` (contradiz a regra 5.4 do MESMO gerador!), `extracao_contratual.py`, `prescricao_por_fatura.py`, `atualizacao_monetaria_bcb.py`, `score_composto.py`, `blindagem_pre_execucao.py`, `atualizar_profile.py`, `organizar_pdfs_orgao.py`, `ocr_audit.py` — nenhum em `scripts/` |
| A16 | EXTRA — WORKFLOW gerado cita skills inexistentes | **CONFIRMADO** | `trd-gerador-prodam`, `negociacao-prodam`, `peticao-inicial-prodam`, `habilitacao-credito-prodam`, `controle-recebimento-prodam`, `classificacao-prodam`, `decisao-documental-prodam` — não estão em `_SKILLS/` nem no INDEX |
| A17 | EXTRA — "20 subpastas" na REFERENCIA_JURIDICA | **DIVERGE** | Disco tem **18** subpastas numeradas (00-17) |
| A18 | EXTRA — WORKFLOW duplica regras (fee/RPV/silêncio) | **CONFIRMADO (risco controlado)** | Mesmo gerador produz ambos; ainda assim é segunda cópia a manter |
| A19 | Checklist geral: identidade ≤5 linhas, comandos válidos | **OK** | Identidade = 3 linhas; `tests/` EXISTE (6 arquivos — falso alarme de subagente corrigido por verificação direta); comandos §9 válidos |
| A20 | EXTRA — `val_atualizado` null em 4 devedores somado como 0 | **CONFIRMADO (cosmético)** | CASA CIVIL, COSAMA, CASA MILITAR, BANCO DAYCOVAL — exibir "(65/69 com valor atualizado)" |

---

## 2. TABELA DE DESTINO — 18 regras + 6 fontes + seções (rastreabilidade nominal)

Legenda: **M**=mantém · **F**=funde · **MV**=move · **C**=corta (coberto em outro lugar). Numeração nova proposta entre parênteses.

### 2.1 As 18 regras da Seção 5

| Regra atual | Destino | Detalhe |
|---|---|---|
| 5.1 Decreto 53.464/2026 | **M** (→R1) | Igual: "Decreto Estadual AM 53.464/2026 (revogou 51.084/2025) — verificar as 4 exceções antes de ação contra Gov AM." |
| 5.2 Silêncio não interrompe | **M** (→R3) | Inalterada |
| 5.3 Juros Lei 14.905/2024 | **M** (→R8) | Inalterada |
| 5.4 Índices/anti-regra | **F** (→R10 + NUNCA-4) | Vira 2 linhas: R10 "Índice de correção: confirmar na cláusula econômica de cada contrato (SELIC/IGPM/IPCA); SELIC live = BCB série SGS 4390." + NUNCA-4 "não criar `config_prodam.py`/`normalizador.py` sem auditoria". Histórico ("verificado 2026-06-08", ref ao script ad_hoc) vai para **comentário `#` no gerador** |
| 5.5 Vias (precatório × penhora) | **M** (→R11) | Inalterada (Tema 253/STF) |
| 5.6 NF do credor não interrompe | **F** (→R4) | Funde com 5.9 numa única regra "marcos interruptivos": NE interrompe (Art. 202 VI CC); NF emitida pelo credor não |
| 5.7 Prescrição por fatura | **M** (→R2) | Inalterada (Art. 189 + 206 §5º I CC) |
| 5.8 FUHAM × FHAJ | **MV** (→NUNCA-7) | "Nunca inverter FUHAM (Alfredo da Matta) × FHAJ (Adriano Jorge)" |
| 5.9 NE = reconhecimento tácito | **F** (→R4) | Ver 5.6 |
| 5.10 SELIC inclui juros / IGPM só correção | **M** (→R9) | Inalterada |
| 5.11 Unicidade + Fazenda metade | **M** (→R5) | Inalterada (REsp 1.963.067/MS; Dec. 20.910/1932) |
| 5.12 Tema 1.109/STJ | **M** (→R6) | Inalterada |
| 5.13 Composição = título (REsp 793.969/RJ) | **M** (→R7) | Inalterada (Rel. p/ acórdão José Delgado; Teori vencido) |
| 5.14 Fee + RPV | **Separa**: fee **C** (já coberto na Seção 1, linha 3); RPV **M** (→R12) | R12: "RPV/AM = 20 SM vigentes (Lei AM 2.748/2002 — confirmada em fonte oficial); 60 SM é o teto FEDERAL — não aplicar contra o Estado." Sem valor em R$ hardcoded (SM muda anualmente) |
| 5.15 profiles.json SSOT / nunca Excel | **MV** (→NUNCA-6) | Tabela §8 mantém a marcação "**SSOT**"; a vedação "nunca Demonstrativo Excel" vive só no NUNCA |
| 5.16 Decimal nunca float | **MV** (→NUNCA-2) | §7 mantém só a referência positiva ao `prodam_utils.fmt_brl` (sem repetir a vedação) |
| 5.17 PRECEDENTES_VERIFICADOS único | **F** (→R13) | Funde com 5.18 + **corrige o path**: `REFERENCIA_JURIDICA/11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md` (3 fabricados + 6 distorcidos) |
| 5.18 Consultar REFERENCIA_JURIDICA | **F** (→R13) | "Jurisprudência só do catálogo verificado; antes de parecer, consultar `REFERENCIA_JURIDICA/` na ordem da Seção 6" |

**Resultado: 18 regras → 13 regras + 4 entradas no bloco NUNCA. Nenhuma desaparece.**

### 2.2 As 6 fontes da Seção 6 (hierarquia)

| Fonte | Destino |
|---|---|
| 6.1 Nota Metodológica | **M** — inalterada (corrige todos os demais) |
| 6.2 Estudo Consolidado 002/2026 | **M** — inalterada |
| 6.3 Estudo Exaustivo | **M** — inalterada |
| 6.4 Pesquisa Jurisprudencial | **M** + nota "só o catálogo da R13" |
| 6.5 Extração Contratual | **M** — inalterada |
| 6.6 REFERENCIA_JURIDICA (20 subpastas) | **M corrigida** — contagem de subpastas passa a ser **dinâmica** (gerador conta no disco; hoje = 18) |

### 2.3 Seções do output

| Seção | Destino |
|---|---|
| Cabeçalho + nota de regeneração | **M** |
| **(NOVO) 0. NUNCA** | 8 vedações de maior dano no topo (lista na §3 abaixo) |
| 1. Identidade | **M** (3 linhas; fee permanece aqui) |
| 2. Status | **M**, top-10 → **top-5** + link STATUS (decisão D2) e nota "(65/69 com atualizado)" |
| 3. Alertas | **M + CORREÇÃO CRÍTICA**: além das <90d futuras, linha agregada 🔥 "N devedores com data de prescrição vencida/stale (inclui X de maior valor) — recalcular" + "N sem data"; detalhe por devedor vai ao STATUS_DEVEDORES.md |
| 4. Workflow (link) | **M** |
| 5. Regras | 13 regras renumeradas (§2.1) |
| 6. Fontes | **M** com R13 fundida e contagem dinâmica |
| 7. Convenções | **M enxuta**: remove `_ARQUIVO_DRIFT/` (não existe) → padroniza `_BACKUPS/`; proteções do repo em 3 linhas curtas |
| 8. Mapas | **M** (tabela igual, descrições encurtadas) |
| 9. Comandos | **M** (validados no disco) |
| 10. Skills + DB | **M**; contagens de tabelas do DB → **movem para STATUS_DEVEDORES.md** (métrica viva, não instrução) — decisão D7 |
| Satélite PLAYBOOK | **Corrigir refs fantasma** (A15): citar só scripts existentes (`orgao_pipeline_completa.py`, `atualizar_db.py`, `dossie_multiformato_devedor.py`, `reconciliar_orfaos_reversos.py`, `PRODAM_DOCS/build_sqlite.py` ✓ existe) e marcar etapas sem script como "(manual/skill)" — decisão D5 |
| Satélite WORKFLOW | **Corrigir skills fantasma** (A16): apontar para skills reais do INDEX — decisão D5 |

### 2.4 Bloco NUNCA proposto (novo, no topo)

1. Nunca apagar/mover/sobrescrever **PDF** — prova jurídica (hook ativo; backup: `_BACKUPS/`).
2. Nunca `float` em valores BRL — `Decimal` + `prodam_utils.fmt_brl` (`R$ 1.234,56`). _[ex-5.16]_
3. Nunca citar lei/jurisprudência fora do catálogo verificado (R13).
4. Nunca criar `config_prodam.py`/`normalizador.py` sem auditoria prévia — não existem em código ativo. _[ex-5.4]_
5. Nunca executar comandos de dentro de `_LIXO_NAO_USAR\_ARCHIVE` — `cd C:\Users\gabri` antes. _[novo]_
6. Nunca usar o Demonstrativo Excel como fonte de valores — SSOT é `PRODAM_DOCS/profiles.json`. _[ex-5.15]_
7. Nunca inverter **FUHAM** (Alfredo da Matta) × **FHAJ** (Adriano Jorge). _[ex-5.8]_
8. Antes de rodar Claude Code no terminal: confirmar que `ANTHROPIC_API_KEY` **não** está definida (`Get-ChildItem Env:ANTHROPIC_API_KEY`) — env var ativa cobra a API do Console em vez do plano (prejuízo já ocorrido ~US$100). _[novo]_

---

## 3. PLANO DE MUDANÇA NO GERADOR (alto nível)

| Bloco/função | Mudança |
|---|---|
| **NOVA `validate_profiles(data)`** | Fail-fast antes de escrever qualquer arquivo: ≥50 devedores, `_metadata` presente, campos numéricos parseáveis, soma exigível > 0. Falhou → não escreve, exit code ≠ 0 (protege `/sincronizar-prodam` de gravar lixo) |
| `compute_metrics()` | `Decimal` no lugar de `float` (l.218-221); novos buckets `prescricao_vencida` (dias ≤ 0), `prescricao_sem_data` (null/'N/A'); ordenação de pipeline com tie-break determinístico `key=(-count, nome)` |
| `generate_claude_md()` | Bloco NUNCA; 13 regras renumeradas; histórico da ex-5.4 vira comentário `#`; contagem dinâmica de subpastas da REFERENCIA_JURIDICA; §3 com linha 🔥 agregada de vencidas/stale; top-N parametrizado (`TOP_N = 5`); "(65/69 com atualizado)" |
| `generate_status_devedores()` | Recebe os buckets novos: seção "Prescrições vencidas/stale (recalcular)" com a lista nominal + contagens do `prodam.db` (se D7 aprovado) |
| `generate_playbook_orgaos()` / `generate_workflow_cobranca()` | Substituir refs fantasma por scripts/skills reais; onde não houver equivalente, marcar "(etapa manual / skill X)" |
| Docstrings | "70 devedores" → 69 + `_metadata`; rodar 2× e conferir que só o timestamp muda |
| `tests/` | Atualizar `test_alerta_prescricao.py` para a nova lógica (vencidas não somem) + novo teste de `validate_profiles` fail-fast |

Ciclo de fechamento (restrição 4): commit backup → editar gerador → `py -3.12 scripts\auto_update_claude_md.py` → conferir output → rodar 2ª vez (idempotência) → `py -3.12 -m pytest tests\ -v` → conferir `/sincronizar-prodam` (`scripts/sincronizar_prodam.py` chama o gerador ao final — confirmado).

---

## 4. DRIFTS NORMATIVOS (Fase 2.3) — para decisão

Varredura: 53 fontes de skill em `PRODAM_DOCS/_SKILLS/` (5 lotes de subagentes) + grep no cache Cowork instalado + REFERENCIA_JURIDICA + web.

**Verificações externas**: Lei AM 2.748/2002 **confirmada em fonte oficial** (SAPL/ALEAM e Legisla.AM — pequeno valor = 20 SM perante a Fazenda Estadual; 15 SM Manaus; 10 SM demais municípios). SM 2026 = **R$ 1.621** (Agência Brasil) → teto estadual 2026 = R$ 32.420; teto federal 60 SM = R$ 97.260. Decreto **53.464/2026**: documentado na base local (00_KNOWLEDGE_BASE, 4 exceções nos §§1º-4º do art. 1º), **não localizado na busca web** — recomendo guardar o PDF do DOE na REFERENCIA_JURIDICA como prova de vigência (decretos vizinhos 53.233/2025 e 53.496/2026 existem; numeração compatível).

| # | Arquivo | Drift | Correção proposta |
|---|---------|-------|-------------------|
| D-1 | `_SKILLS/arvore-decisao-contestacao_SKILL.md` | Ramo 2 inteiro baseado no **Decreto 51.084/2025** como vigente | Atualizar para 53.464/2026 (manter nota "revogou 51.084/2025") |
| D-2 | `_SKILLS/registro-interacoes-devedor_SKILL.md` | L~110 cita 51.084/2025 como vigente | Idem |
| D-3 | `_SKILLS/classificacao-forca-probatoria_SKILL.md` | REsp 793.969/RJ atribuído a "Rel. Min. Teori Zavascki" | "Rel. p/ acórdão Min. José Delgado (Teori vencido)" — distorção já catalogada no PRECEDENTES_VERIFICADOS.md |
| D-4 | `_SKILLS/risco-processual-matriz_SKILL.md` | L~55 usa 60 SM (federal) p/ execução contra o Estado sem ressalva | Tabela: União 60 SM / Estado AM 20 SM (Lei 2.748/2002) |
| D-5 | `_SKILLS/precatorios-rpv-fragmentacao_SKILL.md` | "RPV < 60 SM ≈ R$ 97.260" sem distinção de ente (description e corpo) | Explicitar 20 SM/AM como regra do portfólio (devedores = Estado) |
| D-6 | `_SKILLS/` — blindagem-pre-execucao, montagem-dossie-comprobatorio, compensacao-administrativa-workflow | Hits de "60 SM"/RPV com contexto a confirmar | Verificar e ressalvar onde faltar (na implementação) |
| D-7 | `_SKILLS/` — nota-liquidacao-extrator, prodam-juridico, validador-cadeia-documental-fatura | Menções a "Teori" a normalizar | Conferir que todas dizem "vencido", nunca "relator" |
| D-8 | Skills com "51.084" em contexto já correto (protocolo-juridico, proximo-passo-advisor, triagem-consistencia, workflow-pos-analise) | Citam como revogado/histórico — OK | Padronizar fraseologia "53.464/2026 (revogou 51.084/2025)" |
| D-9 | **Cache Cowork instalado** (espelha D-1..D-7 + `montagem-dossie-devedor-detalhado`, `prodam-data-analyst/references/metrics.md`) | Mesmos drifts | Cache é somente leitura nesta sessão: corrigir as fontes em `_SKILLS/` e **reinstalar via Settings > Capabilities** (passo manual seu) |
| D-10 | `DETRAN_AUDITORIA_COMPLETA\CLAUDE.md` (projeto irmão, editado à mão) | "Lei AM **2.478**/2002" e "≈ R$ 30.360" (SM 2025) | Corrigir p/ 2.748/2002 e 20×SM vigente — **fora do escopo do gerador**; corrijo se você aprovar |

**Dado para decisão (a correção do decreto nas skills entra no escopo?):** recomendo SIM para D-1..D-5 e D-8 (são regra órfã/skill desatualizada que a Fase 4 não pode deixar sobrar), com commit separado `fix(skills)`. D-6/D-7 verifico arquivo a arquivo antes de editar. D-9/D-10 dependem de você.

---

## 5. CONFLITOS (Fase 2.4) — lado a lado, sem resolver

| # | Fonte A | Fonte B | Conflito |
|---|---------|---------|----------|
| C-1 | Plugin `productivity-prodam:start` e `:update` | Gerador | Plugin **cria/edita CLAUDE.md e TASKS.md**; o gerador sobrescreve CLAUDE.md a cada `/sincronizar-prodam` — edição do plugin é perdida |
| C-2 | Plugin `:update` (alertas) | Gerador §3 | Dois cálculos de alerta de prescrição com thresholds/semântica diferentes (<30d "URGENTE" vs "CRÍTICO") |
| C-3 | Plugin `:memory-management` | CLAUDE.md gerado | Memória do plugin promove contexto que a regeneração não conhece — duas memórias paralelas |
| C-4 | `~/.claude/CLAUDE.md` global ("não incluir dados sensíveis de clientes em arquivos") | CLAUDE.md/STATUS_DEVEDORES.md **versionados** com nomes de devedores + valores | O repo é local/privado, mas a regra global é literal — decidir: exceção explícita no global ou anonimizar satélites |
| C-5 | Global ("trate como iniciante", confirmação antes de alterar arquivos) | Projeto (regras técnicas avançadas) | Convivem; duplicação benigna de anti-alucinação (global × R13) — sem ação |
| C-6 | Plugin `:alerta-prazos` | Skill `controle-sla-alertas` (_SKILLS) | Dois sistemas de SLA/alerta para os mesmos prazos |

Recomendação (decisão sua): tratar o CLAUDE.md como **artefato do gerador** e o plugin como consumidor (desativar a escrita de CLAUDE.md pelo plugin ou aceitar perda na próxima sincronização); C-4 documentar exceção.

---

## 6. ESTIMATIVA DE TOKENS (metodologia chars/4)

| Versão | Tokens |
|---|---|
| CLAUDE.md atual | **~2.148** |
| Remoções (ex-5.4 enxuta −70 · 5.15 −18 · 5.17/18 fusão −25 · fee dup −8 · §7 proteções −60 · top-5 −110 · DB→STATUS −45) | −336 |
| Adições (NUNCA +90 · API key +18 · linha 🔥 vencidas +25) | +133 |
| **Proposto** | **~1.945 (−9%)** · com top-10 mantido: ~2.055 (−4%) |

O ganho principal não é tamanho (o arquivo já é enxuto) — é **corrigir o risco jurídico invisível (A11), a contradição interna (A15) e a deduplicação que evita drift**.

---

## 7. FORA DO ESCOPO DESTA REFATORAÇÃO (tarefas separadas recomendadas)

1. **profiles.json**: conciliar `faturas_total ≠ exigíveis+prescritas` em SES/SUSAM (62), SEJUSC (6), SSP (1) e **recalcular as 23 datas de prescrição vencidas/stale** (lote 2026-03-20 + ADS) — o gerador novo passará a EXPOR isso, não a resolver.
2. Guardar o PDF do DOE do Decreto 53.464/2026 na REFERENCIA_JURIDICA (prova de vigência; web não confirma).
3. Reinstalar skills corrigidas no Cowork (Settings > Capabilities) — cache é somente leitura.
4. INDEX.md lista 62 skills vs 53 fontes hoje no disco — regenerar e conferir após a Fase 4.

## 8. DECISÕES PENDENTES (aprovar item a item)

- **D1** Bloco NUNCA no topo (8 itens da §2.4)
- **D2** Top-10 → Top-5 (−110 tokens) ou manter 10
- **D3** Alertas: linha 🔥 agregada de vencidas/stale no CLAUDE.md + lista nominal no STATUS (recomendo fortemente)
- **D4** Fusões/moves da tabela §2.1 (18→13 regras + NUNCA)
- **D5** Corrigir refs fantasma no PLAYBOOK e WORKFLOW gerados
- **D6** Corrigir drifts D-1..D-8 nas skills de `_SKILLS/` (commit `fix(skills)`)
- **D7** Contagens do `prodam.db` saem do §10 → STATUS_DEVEDORES.md
- **D8** `validate_profiles()` fail-fast no gerador + teste novo
- **D9** D-10: corrigir também o CLAUDE.md do DETRAN (2.478→2.748; R$ 30.360→20×SM vigente)
- **D10** C-1/C-4: postura sobre plugin × gerador e dados sensíveis nos satélites (posso só documentar, sem mexer)
