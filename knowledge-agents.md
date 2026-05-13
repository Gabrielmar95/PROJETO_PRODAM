# Knowledge Agents — Projeto PRODAM

Registro dos corpora claude-mem criados para consulta semântica.

---

## prodam-prescricao-2026

**Criado:** 2026-05-10T01:11:11Z
**Última atualização:** 2026-05-10T04:15:01Z (rebuild após learn-codebase)
**Session IDs históricos:**
- Prime inicial: `ae46a0ec-649b-4647-89af-c7d30274002a`
- Pós-learn-codebase: `fe5b4f92-a115-4a69-be41-c97044b2baad`
- Atual: `a26af4e8-11eb-46db-8e51-78430d6e761a`

### Descrição
Prescrição PRODAM — fundamentos legais, marcos interruptivos, reconhecimento tácito, status por devedor, conflitos críticos.

### Filtros aplicados
- **query:** `prescrição quinquenal Art 202 CC Súmula 383 STF Decreto-Lei 4597 marco interruptivo reconhecimento tácito unicidade negativa expressa fragmentação RPV empenho TRD protesto`
- **types:** `bugfix, decision, discovery, change` (gotcha rejeitado pelo schema → substituído por change)
- **limit:** 200
- **dateStart/dateEnd:** sem cutoff temporal
- **concepts/files/project:** não filtrados

### Evolução do corpus

| Snapshot | Data | observation_count | token_estimate | type_breakdown |
|---|---|---|---|---|
| Build inicial | 2026-05-10T01:11Z | 8 | 6.376 | decision: 1, discovery: 7 |
| Rebuild pós-learn-codebase | 2026-05-10T04:15Z | **14** | **10.526** | decision: 2, discovery: 11, bugfix: 1 |

### Enriquecimento via learn-codebase (2026-05-10)

Executado `claude-mem:learn-codebase` em escopo Opção A (subset jurídico):
- **4 SKILLs prescrição core:** `analise-prescricao-creditos`, `marcos-interruptivos-prescricao`, `reconhecimento-divida-tacito`, `revisar-reconhecimento-divida`
- **5 SKILLs suporte:** `precatorios-rpv-fragmentacao`, `classificacao-forca-probatoria`, `nota-empenho-classificador`, `blindagem-pre-execucao`, `validador-cadeia-documental-fatura`
- **9 REFERENCIA_JURIDICA core:** `Nota_Metodologica_Consolidada.md`, `ESTUDO_JURIDICO_002_2026.md`, `PASSO6_PRESCRICAO_CONSOLIDADO.md`, `PRESCRICAO_SUHAB_05042026.md`, `BLINDAGEM_PENHORA_VS_PRECATORIO.md`, `ERRATA_GLOBAL_ACERVO_JURIDICO.md`, `PRECEDENTES_VERIFICADOS.md`, `KNOWLEDGE_BASE_JURIDICO.md`, `ALERTAS_CRITICOS_API.md` + `MAPA_REFERENCIAS_LEGAIS_API.md`
- **profiles.json completo:** 9712 linhas, 70+ devedores

Worker capturou +6 observations adicionais (8 → 14). Outras leituras foram filtradas pelo critério semântico do filter query.

### Queries executadas (rodada 2 — pós-learn-codebase)

| # | Query | Resultado |
|---|---|---|
| 1 | "Quais observations o corpus contém sobre prescrição PRODAM?" | ✅ Inventário completo das 14 obs (decision/discovery/bugfix/change) |
| 2 | "SUHAB Lotes 1-2 expiraram 23/04 e 27/04/2026. Houve protesto?" | ✅ **GAP ABERTO confirmado** — corpus não tem observation pós-05/04/2026 confirmando protesto. Lotes 1-2 (R$6.329 + R$40.926) provavelmente prescritos como obrigação natural Art. 882 CC |
| 3 | "Quais devedores tem prescrição em maio 2026? Liste com data e valor." | ✅ **SUHAB Lote 3 (20/05, R$5.923, D+10) + Lote 4 (28/05, R$40.926, D+18)**. Total maio: R$46.849. Próximas: SSP 30/07 R$2.398 (3NF), SES/SUSAM 31/08 (5 fat) |
| 4 | "SES/SUSAM tem prescrição 13/05/2026 ou 31/08/2026?" | ✅ **31/08/2026 é a CORRETA**. 13/05/2026 vinha de `Of. 129/2021` (ato do credor — não interrompe prescrição Art. 202 CC). PASSO6 reclassificou. **Correção aplicada em `profiles.json` em 10/05/2026 (FASE 3 / cascata em 10 arquivos VIVOS — ver `PRODAM_DOCS/REFERENCIA_JURIDICA/17_ERRATA_CORRECOES/ERRATA_SES_SUSAM_20260510.md`).** |

### Achados críticos consolidados

**Conflito A — SES/SUSAM (✅ RESOLVIDO em ambas as fontes — FASE 3 concluída em 10/05/2026)**
- profiles.json linha 53: `"data_prescricao_proxima": "2026-08-31"` ✅
- profiles.json linha 20: `"observacoes"` reescrito com `"...reclassificado em PASSO6 (Sessão 52, 05/04/2026): ato do credor não interrompe prescrição (Art. 202 VI CC; REsp 793.969/RJ; KB v2.1)..."` ✅
- profiles.json linha 650: `"d_plus_prescricao": 113` ✅ | `"urgencia_prescricao": "MEDIA"` ✅ (mantido)
- **Posição correta (PASSO6 + ERRATA + KB v2.1):** próxima fatura SES = **31/08/2026** (D+148 da Sessão 52 / D+113 a partir de 10/05/2026)
- **Cascata aplicada (10 arquivos VIVOS, 17 edits):** `profiles.json` (3), `CLAUDE.md` (raiz), `.claude/napkin.md`, `DOSSIES_MULTIFORMATO/SES_SUSAM/{json,md,html}`, `gerar_relatorio_docx.py` (substituição A3), `notificacao_simples.py` + `gera_notificacao_ses_script.py` + `gera_notificacao_ses.js` (cada um: bloqueio manual + data)
- **Bloqueio adicional:** 3 scripts geradores receberam `sys.exit` / `throw` no topo por colisão `NOT/001/2026` × NE 001/2026 DETRAN (já protocolada via ICP-Brasil em 20/04/2026). Para destravar: substituir numeração SES e remover bloco.
- **Auditoria SHA256 (`profiles.json`):** antes `B63406136EAA898EBE41D28A133F2BCF2A8BADC10A8D5CE85013BDA726920ED7` / depois `317C3BFBC7236490CAF66D19422B7353851496735CADE4EC9C51523F0AC2DF61`. Backup imutável em `_BACKUPS/correcao-ses-susam-prescricao-20260510-021419/` (10 arquivos, estrutura preservada).
- **Validação cruzada FASE 4:** ✅ diff (apenas L20/53/650 no nó SES), ✅ deep compare 69 outros devedores idênticos byte-a-byte, ✅ 0 hits da blacklist (REsp 1.014.496/SC, REsp 2.792.731/SP, TJ-AM 2008.000901-9), ✅ sweep regressão `13/05/2026|2026-05-13` — 17 hits, todos em BACKUPS/HISTÓRICOS/META auto-gerado, zero em VIVOS não-mapeados.
- **ERRATA:** `PRODAM_DOCS/REFERENCIA_JURIDICA/17_ERRATA_CORRECOES/ERRATA_SES_SUSAM_20260510.md`
- **Pendências para roadmap (não bloqueantes):** (1) Passo 5.3 vincular 25 NEs SES (2025-2026) + 397 NLs a faturas específicas; (2) NE 2026NE0000005 (R$2.522.329,40) — confirmar se constitui marco interruptivo SES adicional; se sim, recalcular base de prescrição.

**Conflito B — SUHAB Lotes 1-2 (GAP ABERTO crítico)**
- Lote 1 (23/04/2026, R$6.329, 4 NFs CT P.46/2021) — prescreveu há 17 dias
- Lote 2 (27/04/2026, R$40.926, 2 NFs CT P.46/2021) — prescreveu há 13 dias
- Corpus tem 0 observation pós-05/04 confirmando protesto extrajudicial
- Action item Sessão 52: "PROTESTO EXTRAJUDICIAL antes de 23/04/2026" — sem confirmação de execução
- **Total potencialmente perdido: R$47.255**
- **Verificações pendentes:**
  1. Tabelionato de protesto: lavratura entre 05/04 e 23/04/2026?
  2. Relatório quinzenal abr/mai 2026?
  3. profiles.json SUHAB pós-Sessão 52?

**Próximas datas críticas (ordem de urgência):**
1. SUHAB Lote 3 — **20/05/2026 (D+10)** — R$5.923
2. SUHAB Lote 4 — **28/05/2026 (D+18)** — R$40.926
3. SUHAB Lote 5 — **29/06/2026 (D+50)** — R$40.926
4. SSP — 30/07/2026 (D+81) — R$2.398 (3 NFs)
5. SES/SUSAM — 31/08/2026 (D+113) — 5 faturas

### Anomalias Worker API claude-mem

Comportamento observado em 4 sessões de query:
- **Padrão:** primeira query da sessão de prime ~25-35s (sucesso), segunda+ → timeout 45s
- **Hipótese:** Worker carrega histórico Q&A da sessão a cada query, com Sonnet 4.6 e contexto crescente extrapola SLA 45s
- **Workaround validado:** após cada query bem-sucedida, executar `reprime_corpus` para sessão fresh ANTES da próxima query
- **Custo:** 1 reprime por query consultada

### Comandos de manutenção
```
# Listar corpora
mcp__plugin_claude-mem_mcp-search__list_corpora

# Re-prime (sessão fresh — RECOMENDADO antes de cada query nova)
mcp__plugin_claude-mem_mcp-search__reprime_corpus name="prodam-prescricao-2026"

# Rebuild (após novas observations geradas em sessões futuras)
mcp__plugin_claude-mem_mcp-search__rebuild_corpus name="prodam-prescricao-2026"

# Query (após reprime)
mcp__plugin_claude-mem_mcp-search__query_corpus name="prodam-prescricao-2026" question="..."
```

### Próximas ações sugeridas

1. ~~**URGENTE — atualizar profiles.json SES/SUSAM** (data 13/05 → 31/08; remover Of. 129/2021 como marco)~~ **✅ CONCLUÍDO em 10/05/2026** — FASE 3 do workflow 7 fases / 17 edits em 10 arquivos VIVOS / ERRATA registrada / FASE 4 validada sem regressões
2. **URGENTE — verificar status SUHAB Lotes 1-2** (tabelionato de protesto + relatório quinzenal abr/mai 2026)
3. **PROTESTO IMEDIATO — SUHAB Lote 3** (D+10, prazo até 20/05/2026, R$5.923)
4. **Aprofundar corpus:** rodar mais sessões de trabalho com claude-mem ativo (cada Read alimenta worker), ou ampliar escopo learn-codebase para incluir DETRAN_AUDITORIA_COMPLETA + DOSSIES/
5. **Workaround timeout:** padrão fixo `reprime → query → repeat` ao consultar o corpus
6. **Considerar:** baixar `CLAUDE_MEM_TIER_QUERY_MODEL` para `claude-haiku-4-5` se latência persistir (Sonnet 4.6 caro/lento para queries de catálogo)
