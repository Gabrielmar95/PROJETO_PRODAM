# Cascata REsp 793.969/RJ — Teori Zavascki → José Delgado

**Status:** ✅ CONCLUÍDA — auditado em 27/05/2026 (Janela 1, item 1.8)
**Data abertura:** 2026-05-12
**Data fechamento:** 2026-05-27
**Origem:** Plano `C:\Users\gabri\.claude\plans\que-correcoes-voce-acha-adaptive-liskov.md`
**Modo:** read-only nesta etapa (classificação). Edits aguardam OK literal do advogado.

> **Auditoria 27/05/2026**: validação por `grep -n "Teori\|Zavasc"` em cada um dos 8 arquivos TROCAR confirma que TODAS as 11 ocorrências foram migradas para o padrão canônico (`Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido`). Os edits foram aplicados em sessão não-versionada entre 12/05 e 27/05 (provavelmente cassação local sem changelog em HISTORICO_SESSOES.md). Fechamento documental nesta data.
>
> **Resíduo identificado (não-bloqueante)**: `PRODAM_DOCS/_SKILLS/dossie-juridico-prodam/SKILL.md` linhas 464 e 684 — citadas em `relatorios/AUDITORIA_ECOSSISTEMA_20260512.md` linha 56. Pasta gitignored; correção exige máquina local. **Ação local do Gabriel**: rodar `Select-String -Path PRODAM_DOCS\_SKILLS\dossie-juridico-prodam\SKILL.md -Pattern "Teori\|Zavasc"` e aplicar substituição manual.

---

## Sumário

- **Total de hits relevantes** (fora de backups): **8 arquivos**, ~13 ocorrências
- **MANTER** (regra de blindagem, log histórico, peça-teste intencional): 8 arquivos
- **TROCAR** (alucinação a corrigir): 8 arquivos
- **DUVIDA**: 0 após análise contextual
- **Backups out-of-scope** (`_BACKUPS/correcao-ses-susam-prescricao-20260510-021419/`): 3 arquivos — NÃO TOCAR

---

## Tabela completa — MANTER

| # | Path | Linha | Trecho (resumo) | Por que MANTER |
|---|------|-------|-----------------|----------------|
| M1 | `CLAUDE.md` | 72 | "REsp 793.969/RJ, Min. **José Delgado** — Teori Zavascki foi vencido; nunca citar Teori como relator" | Regra #13 CORRETA — citação canônica. |
| M2 | `.claude\agents\adversarial-meta-auditor.md` | 82, 101 | "Teori citado como relator do REsp 793.969/RJ" / "NUNCA cite Teori Zavascki como relator do REsp 793.969/RJ — é José Delgado (Teori foi vencido)" | Regra de blindagem do agente. Apagar quebra a detecção. |
| M3 | `scripts\auto_update_claude_md.py` | 168 | Template Python que GERA a regra #13 do CLAUDE.md raiz, já com o padrão CORRETO | Se trocar, próxima regeração do CLAUDE.md vai ficar errada. |
| M4 | `relatorios\CHANGELOG_SESSAO_2026-05-07_setup_subagent_adversarial.md` | 27, 46 | Log da implementação da regra de blindagem | Log histórico — não reescrever histórico. |
| M5 | `relatorios\CHANGELOG_SESSAO_2026-05-11_kb_juridico_3edits.md` | 36, 151 | Log do padrão canônico de citação ("Rel. Min. Teori Zavascki vencido; Rel. p/ acórdão Min. José Delgado") | Log histórico — padrão canônico documentado. |
| M6 | `HISTORICO_SESSOES.md` | 6 | "REsp 793.969/RJ corrigido em 6 linhas... Padrão canônico adotado: Rel. Min. Teori Zavascki (vencido), Rel. p/ acórdão Min. José Delgado" | Log histórico já com padrão CORRETO. |
| M7 | `scripts\corrigir_skills_prodam.py` | 429-432 | Script que APLICA a correção: "Teori Zavascki foi relator originário (vencido); acórdão redigido pelo Min. José Delgado" | Script de correção. Apagar quebra a automação. |
| M8 | `DOCUMENTOS_GERADOS\_TESTE_AGENT\teste_adversarial_20260507.md` | 23 | "REsp 793.969/RJ, sob relatoria do Min. Teori Zavascki" | **Peça-teste intencional** com 3+ furos conhecidos (Súmula 999 fabricada, cálculo IGPM pós-marco indevido, honorários sobre valor da causa). Corromper destrói o teste do agente adversarial. |

---

## Tabela completa — TROCAR

| # | Path | Linha | Trecho original (ERRADO) | Trecho proposto (CORRETO) |
|---|------|-------|--------------------------|----------------------------|
| T1 | `DETRAN_AUDITORIA\RELATORIO_DETRAN.md` | 95 | `título executivo extrajudicial nos termos do REsp 793.969/RJ (Min. Teori Zavascki).` | `título executivo extrajudicial nos termos do REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido).` |
| T2 | `_SKILLS_NOVAS_20260423\renomeador-pdfs-prodam\SKILL.md` | 326 | `REsp 793.969/RJ (Min. Teori Zavascki) — composição documental como título` | `REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori vencido) — composição documental como título` |
| T3 | `relatorios\DOSSIE_DETRAN_PIPELINE_COMPLETO.md` | 124 | `REsp 793.969/RJ (Rel. Teori Zavascki) — NE+NL+Fatura` | `REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori vencido) — NE+NL+Fatura` |
| T3 | `relatorios\DOSSIE_DETRAN_PIPELINE_COMPLETO.md` | 192 | `REsp 793.969/RJ (Rel. Teori Zavascki): composição NE+Fatura forma título.` | `REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori vencido): composição NE+Fatura forma título.` |
| T3 | `relatorios\DOSSIE_DETRAN_PIPELINE_COMPLETO.md` | 313 | `Art. 784, II e III, CPC + REsp 793.969/RJ (Rel. Teori Zavascki) — composição documental` | `Art. 784, II e III, CPC + REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori vencido) — composição documental` |
| T3 | `relatorios\DOSSIE_DETRAN_PIPELINE_COMPLETO.md` | 348 | `PRECEDENTES VERIFICADOS: REsp 793.969/RJ (Rel. Teori Zavascki), Súmula 339/STJ` | `PRECEDENTES VERIFICADOS: REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori vencido), Súmula 339/STJ` |
| T4 | `relatorios\BRIEFING_JURIDICO_PRODAM_v2.md` | 110 | `Referência jurídica: REsp 793.969/RJ (Min. Teori Zavascki — NÃO Luiz Fux)` | `Referência jurídica: REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori vencido — NÃO Luiz Fux)` |
| T4 | `relatorios\BRIEFING_JURIDICO_PRODAM_v2.md` | 224 | Tabela: \| REsp 793.969/RJ relator \| Luiz Fux \| **Teori Zavascki** \| | Tabela: \| REsp 793.969/RJ relator \| Luiz Fux \| **José Delgado (Teori vencido)** \| |
| T5 | `relatorios\PROJECT_INSTRUCTIONS_PARA_COLAR.md` | 30 | `REsp 793.969/RJ relator: Teori Zavascki (não Luiz Fux)` | `REsp 793.969/RJ relator: José Delgado p/ acórdão (Teori vencido, não Luiz Fux)` |
| T6 | `scripts\notificacao_simples.py` | 165 | `(REsp 793.969/RJ, Min. Teori Zavascski).` | `(REsp 793.969/RJ, Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido).` |
| T7 | `scripts\gera_notificacao_ses_script.py` | 240 | `(REsp 793.969/RJ, Min. Teori Zavascski).` | `(REsp 793.969/RJ, Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido).` |

**Observação T6/T7:** ambos os scripts têm typo `Zavascski` (com -ck-sk-). A substituição já corrige o typo de quebra.

---

## Out of scope — não tocar

- `_BACKUPS\correcao-ses-susam-prescricao-20260510-021419\CLAUDE.md` linha 71 (CORRETO mas backup)
- `_BACKUPS\correcao-ses-susam-prescricao-20260510-021419\notificacao_simples.py` linha 155 (ERRADO mas backup)
- `_BACKUPS\correcao-ses-susam-prescricao-20260510-021419\gera_notificacao_ses_script.py` linha 230 (ERRADO mas backup)

**Justificativa:** backups são imagens-no-tempo. Modificá-los apaga evidência de auditoria.

---

## Status final (auditoria 2026-05-27)

✅ **Todas as 11 ocorrências TROCAR confirmadas no formato canônico**:

| # | Arquivo | Linha esperada | Linha real | Status |
|---|---------|----------------|------------|--------|
| T1 | `DETRAN_AUDITORIA/RELATORIO_DETRAN.md` | 95 | 95 | ✅ |
| T2 | `_SKILLS_NOVAS_20260423/renomeador-pdfs-prodam/SKILL.md` | 326 | 326 | ✅ |
| T3a | `relatorios/DOSSIE_DETRAN_PIPELINE_COMPLETO.md` | 124 | 124 | ✅ |
| T3b | `relatorios/DOSSIE_DETRAN_PIPELINE_COMPLETO.md` | 192 | 192 | ✅ |
| T3c | `relatorios/DOSSIE_DETRAN_PIPELINE_COMPLETO.md` | 313 | 313 | ✅ |
| T3d | `relatorios/DOSSIE_DETRAN_PIPELINE_COMPLETO.md` | 348 | 348 | ✅ |
| T4a | `relatorios/BRIEFING_JURIDICO_PRODAM_v2.md` | 110 | 110 | ✅ |
| T4b | `relatorios/BRIEFING_JURIDICO_PRODAM_v2.md` | 224 | 224 | ✅ |
| T5 | `relatorios/PROJECT_INSTRUCTIONS_PARA_COLAR.md` | 30 | 30 | ✅ |
| T6 | `scripts/notificacao_simples.py` | 165 | 168 (linha mudou) | ✅ (typo `Zavascski` corrigido) |
| T7 | `scripts/gera_notificacao_ses_script.py` | 240 | 242 (linha mudou) | ✅ (typo `Zavascski` corrigido) |

**Padrão de citação canônica em uso:** `Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido` (alinhado com `CHANGELOG_SESSAO_2026-05-11_kb_juridico_3edits.md`).

**Pendência local (não bloqueante)**: `PRODAM_DOCS/_SKILLS/dossie-juridico-prodam/SKILL.md` linhas 464 e 684 — gitignored. Aplicar correção localmente conforme nota no topo do arquivo.

**Próxima ação automática**: nenhuma. CLAUDE.md raiz (regra #13) e `scripts/auto_update_claude_md.py:329` já têm a citação correta + tag de auditoria.
