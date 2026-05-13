# Changelog — Sessão 2026-05-11: Ciclo de 3 edits no KNOWLEDGE_BASE_JURIDICO.md

## Objetivo

Alinhar `PRODAM_DOCS/REFERENCIA_JURIDICA/00_KNOWLEDGE_BASE/KNOWLEDGE_BASE_JURIDICO.md` (SSOT jurídica) com a realidade factual de 2026-05-11, corrigindo três focos críticos:

1. **Anti-alucinação ativa** — relator do REsp 793.969/RJ catalogado de forma incompleta.
2. **Resistência a reajuste anual** — teto RPV-AM hardcoded em valor absoluto (R$ 32.420).
3. **Fontes inexistentes citadas como autoritativas** — `config_prodam.py` referenciado em ~232 arquivos do ecossistema PRODAM mas inexistente no disco.

Cada edit foi aplicado com seu próprio gate (backup + diff + confirmação literal "OK, prosseguir") e seguido de Greps de verificação.

---

## EDIT 1 — REsp 793.969/RJ (anti-alucinação)

### Problema
O KNOWLEDGE_BASE catalogava o relator do REsp 793.969/RJ de forma inconsistente em 6 linhas distintas. Em algumas, citava apenas "Min. Teori Zavascki" sem qualificar que ele foi voto **vencido**. A omissão dá impressão errada — exploitable em embargos — de que o voto de Teori prevaleceu, quando na verdade o acórdão foi redigido por **Min. José Delgado**.

Caso especialmente grave na linha 371 da tabela de erratas (seção 9.2): instruía a corrigir citações errôneas de "Luiz Fux" trocando para "Min. Teori Zavascki" isoladamente — propagando a meia-verdade.

### Locais corrigidos (6 linhas)

| Linha | Seção | Tipo |
|---|---|---|
| 37 | 1.1 — Tabela das 5 vias do Art. 784 CPC | Citação curta |
| 48 | 1.2 — Composição Documental | Definição canônica |
| 303 | 8.1 — Jurisprudência verificada | Tabela detalhada |
| 335 | 8.3 — Precedentes distorcidos | Errata interna |
| 371 | 9.2 — Erros conhecidos | Tabela de errata |
| 434 | 10.3 — Top 12 Teses | Matriz consolidada |

### Padrão canônico adotado

```
Rel. Min. Teori Zavascki (vencido), Rel. p/ acórdão Min. José Delgado
```

Com nota explicativa onde o contexto permite: "Teori foi vencido; José Delgado redigiu o acórdão."

### Verificações pós-Edit

- (a) "Luiz Fux" como relator de **793.969** → 0 ocorrências (3 menções restantes ao "Luiz Fux" são relator REAL de **outro** REsp 1.143.216/RS, ou aparecem entre aspas em errata)
- (b) Toda menção a 793.969 com relator → cita **ambos** os ministros
- (c) "Teori Zavascki" isolado sem "vencido"/"Delgado" próximo → 0

---

## EDIT 2 — Teto RPV-AM (resistência a reajuste anual do SM)

### Problema
O teto RPV-AM (Lei AM 2.748/2002) é definido como **20 × SM vigente**. O valor absoluto (R$ 32.420 em 2026, com SM = R$ 1.621) muda a cada reajuste anual. O documento citava o valor fixo em 6 trechos — 5 pontos de manutenção sincronizada que ficariam silenciosamente desatualizados a cada janeiro.

### Locais corrigidos (4 edits cobrindo 6 trechos)

| Edit | Linha(s) | Tipo |
|---|---|---|
| 2.1 | 120-122, 285-287, 422-424 (3 callouts idênticos) | `replace_all=true` (1 op → 9 linhas afetadas) |
| 2.2 | 132 | Tabela "Adm. Direta (Estado)" |
| 2.3 | 143 | Bullet canônica da seção 3.2 |
| 2.4 | 370 | Tabela de errata 9.2 |

### Padrão consolidado

```
20 × SM vigente (Lei AM 2.748/2002 — NÃO "2.478").
Em 2026: R$ 32.420 (SM = R$ 1.621/mês).
Atualizar a cada reajuste anual do SM.
```

Valor 2026 mantido como **exemplo entre parênteses**, fórmula `20 × SM` ou `20×SM` como anchor primário.

### Verificações pós-Edit

- (a) `R$ 32.420` sem `20 × SM` próximo → 0 (todas as 6 ocorrências passaram a citar a fórmula)
- (b) Toda `RPV` em contexto AM/Lei 2.748 → contém `20 × SM` ou `20×SM`
- (c) `Lei 2.478` (errado) → só aparece nos contextos esperados de errata explícita ("NÃO '2.478'" + tabela de erros conhecidos)

---

## EDIT 3 — Regra 4 (DETRAN PRESUMIDO + config_prodam.py fantasma)

### Problema 1 — DETRAN "IGPM + 1% + 2%"
Índice do DETRAN-AM apresentado como confirmado, com qualificação fraca ("PRESUMIDO, não confirmado documentalmente") que não impediria reutilização em peças. Citação contratual (CT 022/2014, Cl. 11.1) carece de auditoria contratual real.

### Problema 2 — `config_prodam.py` (fantasma documental)
Linhas 213 e 233 citavam `config_prodam.py` como "fonte autoritativa de índices" e como fundamento da resposta à defesa "Valor ilíquido". O arquivo **NÃO EXISTE no disco** desde pelo menos 2026-04 e está referenciado em **~232 arquivos** do ecossistema PRODAM como fantasma documental.

As SSOTs reais para os tópicos cobertos pelo fantasma já existem:
- **Mapa contrato/ano → regime de correção:** `~/.claude/skills/normalizador-contratos-prodam/scripts/normalizador.py`
- **Taxas vivas SELIC/IGPM/IPCA/INPC:** `~/.claude/skills/memorial-calculo-prodam/scripts/gerar_memorial.py` (API BCB live, cache 24h, Decimal)
- **Valores absolutos (SM, RPV, custas, honorários):** sem SSOT consolidada — hoje vivem inline em scripts de cálculo

### Locais corrigidos (3 trechos)

| Edit | Linha | Mudança |
|---|---|---|
| 3.1 | 209 | "PRESUMIDO" → "(a confirmar)" + "carece de auditoria contratual antes de citar em peça" |
| 3.2 | 213 | `config_prodam.py` removido como SSOT → bloco de 5 linhas declarando `normalizador.py`, `gerar_memorial.py` e o caráter fantasma de `config_prodam.py` |
| 3.3 | 233/239 | Tabela "Valor ilíquido": `config_prodam.py + SPCF` → `gerar_memorial.py (BCB live) + SPCF` |

### Verificações pós-Edit

- (a) `config_prodam` em qualquer contexto → 1 menção total (linha 215), e é o aviso de inexistência. Zero menções como "fonte autoritativa"
- (b) DETRAN + IGPM no mesmo contexto → contém "a confirmar" + "carece de auditoria contratual"
- (c) `normalizador.py` e `gerar_memorial.py` → ambos presentes como SSOTs declaradas

---

## Evolução do arquivo (bytes / linhas)

| Estado | Bytes | Linhas | Δ |
|---|---|---|---|
| Original (pré-Edit 1) | 28.795 | 470 | — |
| Pós-Edit 1 (REsp 793.969) | 29.262 | 470 | +467 |
| Pós-Edit 2 (RPV-AM) | 29.560 | 470 | +298 |
| Pós-Edit 3 (Regra 4) | 30.184 | 476 | +624 |

**Total:** +1.389 bytes (+4,82%) e +6 linhas. Crescimento de linhas concentrado no Edit 3 (bloco de aviso `config_prodam.py`). Edits 1 e 2 só expandiram conteúdo dentro de linhas existentes.

---

## Backups preservados (rollback granular)

Diretório: `PRODAM_DOCS/REFERENCIA_JURIDICA/00_KNOWLEDGE_BASE/`

| Backup | Bytes | Estado preservado | Restaura |
|---|---|---|---|
| `.bak-20260511-edit1` | 28.795 | Pré-Edit 1 | Estado original (rollback total) |
| `.bak-20260511-edit2` | 29.262 | Pós-Edit 1 / Pré-Edit 2 | Mantém REsp 793.969 corrigido; reverte RPV + Regra 4 |
| `.bak-20260511-edit3` | 29.560 | Pós-Edit 2 / Pré-Edit 3 | Mantém REsp + RPV corrigidos; reverte só Regra 4 |

---

## Arquivos modificados nesta sessão

### KNOWLEDGE_BASE_JURIDICO.md
Caminho: `PRODAM_DOCS/REFERENCIA_JURIDICA/00_KNOWLEDGE_BASE/KNOWLEDGE_BASE_JURIDICO.md`
Antes: 28.795 bytes / 470 linhas
Depois: 30.184 bytes / 476 linhas
13 trechos corrigidos em 6 linhas (Edit 1) + 6 trechos em 4 edits (Edit 2) + 3 trechos em 3 edits (Edit 3) = **15 trechos em 10 operações de Edit**.

### Configurações do harness (sessões anteriores) — não tocadas hoje, mas relevantes ao contexto
- `~/.claude/CLAUDE.md` — recebeu bloco SAFEGUARD JURIDICO no topo (operação anterior nesta sessão, registrada separadamente)
- `scripts/auto_update_claude_md.py` — edits da Regra 4 e Regra 14 já estão materializados no script (registrado em memória 2026-05-11), mas **não executado** hoje.

---

## Decisões tomadas

1. **Padrão de citação do REsp 793.969/RJ** — explicitar ambos os ministros com qualificação ("vencido" / "p/ acórdão") sempre. Citações curtas ficam "(Rel. Min. Teori Zavascki vencido; Rel. p/ acórdão Min. José Delgado)". Aplicado uniformemente.

2. **RPV-AM como fórmula auto-atualizável** — fórmula `20 × SM vigente` como anchor primário; valor 2026 (R$ 32.420) preservado como exemplo entre parênteses. Documento agora resistente a reajuste anual.

3. **`config_prodam.py` declarado fantasma in-loco** — em vez de fingir que existe ou silenciar a referência, o documento agora avisa que existem ~232 referências espalhadas e instrui a NÃO criar sem auditoria prévia. Pointer explícito para `normalizador.py` e `gerar_memorial.py` como SSOTs reais.

4. **DETRAN IGPM endurecido** — "(a confirmar)" no índice + "carece de auditoria contratual antes de citar em peça" no fundamento. Impede uso em dossiê/petição sem checagem manual da Cl. 11.1 do CT 022/2014.

---

## Pendências geradas / persistentes

### Da sessão de hoje
1. **`auto_update_claude_md.py` adiado** para próximo ciclo natural. Motivo: script é all-or-nothing — apaga o bloco "DECISÃO PENDENTE config_prodam.py" do CLAUDE.md gerado (35 linhas). Antes de rodar, considerar patch `--preserve-manual-blocks` ou copiar bloco para `_QUESTOES_CRITICAS/` com pointer no CLAUDE.md.
2. **`config_prodam.py` — decisão definitiva pendente** (A/B/C/X registrada no CLAUDE.md raiz). Opções: criar com auditoria, deprecar formalmente as ~232 referências, ou manter status quo formalizado.
3. **Padronizar frase do gate** — divergência atual: SAFEGUARD global (`~/.claude/CLAUDE.md`) usa **"OK, prosseguir"**; Gate jurídico (`~/.claude/CLAUDE.md`, seção mais abaixo) usa **"OK, salvar"**. Padronizar em sessão futura.

### Urgência operacional (não tocada nesta sessão)
- 🔴 **SES/SUSAM**: prescrição **2026-08-31 (113 dias)** — R$ 14.748.048,96. Status em `profiles.json`: ENVIAR_TRD (fase F3). Único alerta ativo do portfólio.
- ⚠️ **ADS**: prescrição em D+3 (data-base ~2026-04-09 no `profiles.json`, snapshot congelado). Janela provavelmente fechou — diagnóstico forense recomendado antes de qualquer ação.

---

## Próxima sessão — começar por

1. Endereçar a urgência **SES/SUSAM** — preparar TRD (fase F3) com dossiê comprobatório.
2. **Diagnóstico forense de ADS** — confirmar via `prodam.db` se as faturas críticas já prescreveram ou se ainda há janela útil.
3. **Decisão final sobre `config_prodam.py`** — escolher A/B/C/X. Esta sessão preparou o terreno (KNOWLEDGE_BASE já não cita o fantasma como SSOT); falta a decisão estratégica de fechar a issue.
4. (Opcional) Antes de qualquer execução de `auto_update_claude_md.py`, implementar `--preserve-manual-blocks` ou migrar bloco "DECISÃO PENDENTE" para `_QUESTOES_CRITICAS/`.
