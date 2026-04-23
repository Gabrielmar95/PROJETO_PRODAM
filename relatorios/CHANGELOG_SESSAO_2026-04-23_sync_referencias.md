# Sessão 2026-04-23 — Sincronização de Referências PDF (pipeline DETRAN)

**Operador:** Gabriel Mar (OAB/AM 15.697)
**Duração ativa:** ~14:00 → 17:15
**Tema:** concluir pipeline DETRAN de renomeação + descobrir/corrigir 2 bugs estruturais em `sincronizar_referencias.py` + extrair skill reutilizável.

---

## 1. Ponto de partida

Pipeline DETRAN de renomeação canônica estava a meio caminho:
- 2.473 PDFs renomeados canonicamente (`_OUT_rename_inplace_20260423_141648/`)
- Sync v1 das 14:41 propagou 1858 pares × 3 bancos (1912 UPDATEs cada)
- `limpar_suspeitos` das 15:59 promoveu 196 PDFs dos 12 contratos ao whitelist (removeu sufixo `-SUSPEITO`)
- Faltava rodar sync final para propagar os 196 nomes limpos nos 3 `prodam.db` + `profiles.json`.

## 2. Descobertas críticas

### 2.1 Gargalo O(44k queries) na v1

`sincronizar_referencias.py` (v1) fazia `UPDATE col = REPLACE(col, ?, ?) WHERE col LIKE '%?%'` para **todos os 1858 pares × cada coluna TEXT × cada tabela**, totalizando ~44k queries por banco, das quais ~99% retornavam zero linhas. Tempo real observado: **~68 minutos** para os 3 bancos (22min + 19min + 25min no run das 14:41).

### 2.2 Bug #1 — Colisão silenciosa de chaves em dict Python

Ao construir o mapa `{nome_antigo: nome_novo}` direto do CSV, **712 pares foram silenciosamente sobrescritos** porque arquivos homônimos em pastas diferentes colidiam na chave:
- `log_renomeacao.csv`: 2.473 linhas → 1.858 chaves únicas (615 perdidos)
- `log_limpar_suspeitos.csv`: 196 linhas → 99 chaves únicas (97 perdidos)

Nenhum warning do Python. Detectado por comparação entre `len(csv_ok_rows)` e `len(mapa)`.

### 2.3 Bug #2 — SQL REPLACE não-idempotente quando `novo ⊃ busca`

Quando `nome_novo` contém `nome_busca` como substring (típico de prefixo classificatório tipo `INDEFINIDO_`), cada execução do UPDATE REPLACE adiciona mais um prefixo:

```
X.pdf → INDEFINIDO_X.pdf → INDEFINIDO_INDEFINIDO_X.pdf → INDEFINIDO_INDEFINIDO_INDEFINIDO_X.pdf
```

**9 células foram corrompidas** (`AUDITORIA_DETRAN_COMPLETA.pdf` em `pendrive_docs.arquivo/caminho/texto_preview` nos 3 bancos) antes da detecção.

### 2.4 Bug colateral — BAK único sobrescrito

A v1 criava `backup_dir / path.name` como nome do BAK, mas os 3 `prodam.db` têm mesmo basename → os 3 BAKs se sobrescreviam na mesma pasta. No final sobrou só o BAK do banco 3 (`detran_dashboard`). Os dos bancos 1 e 2 foram perdidos.

## 3. Ações tomadas

### 3.1 Criação do `sincronizar_referencias_v2.py`

Arquitetura em 2 fases:
- **FASE 1 (detecção read-only):** scan coluna-a-coluna identifica triplos `(tabela, coluna, par)` com match real. Retorna `{tabela: {coluna: {antigo: count}}}`.
- **FASE 2 (apply direcionado):** UPDATE executado só nos triplos detectados.

Features:
- Mapa unificado (`log_renomeacao.csv` + `log_limpar_suspeitos.csv`)
- Chave = caminho completo (fix do Bug #1)
- `Path(chave).name` na busca/UPDATE
- Dedup `(nome_busca, novo)` por coluna (fix do Bug #2 intra-run)
- `filtrar_pares_inseguros()` (fix do Bug #2 inter-run)
- BAK único por caminho: `{parent_dir}__{filename}.BAK`

**Resultado:** 77s total (vs ~68min da v1) — redução de ~53×.

### 3.2 Patch cirúrgico das 9 células corrompidas

3 BAKs únicos criados em `_OUT_patch_corrupcao_20260423_170609/backups/`, depois:

```sql
UPDATE pendrive_docs
SET arquivo = REPLACE(arquivo, 'INDEFINIDO_INDEFINIDO_', ''),
    caminho = REPLACE(caminho, 'INDEFINIDO_INDEFINIDO_', ''),
    texto_preview = REPLACE(texto_preview, 'INDEFINIDO_INDEFINIDO_', '')
WHERE arquivo LIKE '%INDEFINIDO_INDEFINIDO_%'
```

Resultado: 3 linhas (1 por banco) corrigidas, 0 duplicações remanescentes. Valor final: `INDEFINIDO_AUDITORIA_DETRAN_COMPLETA.pdf` (1x INDEFINIDO), consistente com o rename original.

### 3.3 Skill extraída — `sincronizacao-referencias-pdf`

Criada em `PRODAM_DOCS/_SKILLS/sincronizacao-referencias-pdf/SKILL.md` (447 linhas). Documenta:
- As 2 armadilhas com caso real + números
- Padrão dry-run → aprovação → apply → validação → patch cirúrgico
- Código de referência (detectar_ocorrencias_db, aplicar_db_otimizado, filtrar_pares_inseguros)
- Alvos conhecidos no projeto
- 8 regras invioláveis + métricas de sanity check

Aplicabilidade explícita: DETRAN foi piloto; próximos são **SEDUC (R$ 49,2M), SSP (R$ 4,6M), SEAD (R$ 2,3M), SES/SUSAM (R$ 14,7M)**.

### 3.4 Memória atualizada

Arquivo `~/.claude/projects/.../memory/feedback_replace_nao_idempotente.md` criado com regra reutilizável. Referenciado em `MEMORY.md`.

## 4. Estado final dos dados

| Banco | mtime | Hash pós-patch | Refs falsos positivos (substring) | Corrupções |
|---|---|---|---:|---:|
| `prodam.db` (raiz) | 16:22 | alterado | 6 (esperado, não é trabalho pendente) | 0 |
| `PRODAM_DOCS/_ANALISE/prodam.db` | 16:22 | alterado | 6 | 0 |
| `detran_dashboard/data-real/prodam.db` | 16:22 | alterado | 6 | 0 |

Todos os 3 bancos apontam corretamente para os nomes canônicos pós-rename. Os 6 "refs" reportados pelo dry-run são falsos positivos causados por substring dentro do próprio valor canônico (`novo ⊃ busca`). Os 525 pares inseguros filtrados pelo script garantem que não há trabalho pendente real.

## 5. Arquivos criados/modificados

### Criados
- `sincronizar_referencias_v2.py` — script otimizado com 2 fases + 3 camadas de defesa
- `PRODAM_DOCS/_SKILLS/sincronizacao-referencias-pdf/SKILL.md` — skill 447 linhas
- `~/.claude/projects/.../memory/feedback_replace_nao_idempotente.md`
- `_OUT_patch_corrupcao_20260423_170609/` — 3 BAKs + log do patch

### Modificados
- `prodam.db` (raiz) — patch cirúrgico + apply v2
- `PRODAM_DOCS/_ANALISE/prodam.db` — idem
- `detran_dashboard/data-real/prodam.db` — idem
- `~/.claude/projects/.../memory/MEMORY.md` — 1 linha adicionada

### Gerados (outputs de runs)
- `_OUT_sync_referencias_v2_20260423_163224/` (dry-run 1)
- `_OUT_sync_referencias_v2_20260423_164206/` (dry-run com mapa unificado pré-fix)
- `_OUT_sync_referencias_v2_20260423_165325/` (dry-run pós-fix de chave)
- `_OUT_sync_referencias_v2_20260423_165544/` (apply!)
- `_OUT_sync_referencias_v2_20260423_165807/` (validação pós-apply — revelou corrupção)
- `_OUT_sync_referencias_v2_20260423_170714/` (dry-run pós-patch)
- `_OUT_sync_referencias_v2_20260423_171133/` (dry-run final, 0 refs reais)
- `_OUT_sync_referencias_20260423_155926/` (dry-run v1 antes de matar — 16:08)

## 6. Próximos passos (ordem prioritária)

1. **Aplicar pipeline `renomear → limpar_suspeitos → sincronizar_referencias_v2` para SEDUC** (R$ 49,2M, maior exigível do portfólio, status: ANALISAR_DOCUMENTACAO)
2. **Repetir para SES/SUSAM** (R$ 14,7M, prescrição 2026-05-13 — 21 dias)
3. **Repetir para SSP** (R$ 4,6M, PROTOCOLAR_PETICAO)
4. **Repetir para SEAD** (R$ 2,3M, ENVIAR_TRD)
5. **Considerar** automação do pipeline completo (um script orquestrador que roda os 3 em sequência com gates)

A skill `sincronizacao-referencias-pdf` é o ponto de entrada obrigatório para cada um desses runs.

## 7. Pendências explícitas

- **`_OUT_sync_referencias_v2_*` em disco:** 7 pastas de output acumuladas nesta sessão (~poucos MB cada). Considerar limpeza ou arquivo compactado depois de validar que os BAKs não são mais necessários.
- **3 bancos com alterações não-commitadas:** `prodam.db` alterado em 3 locais, .BAK em `_OUT_patch_corrupcao_*/backups/`. Se alguém fizer rebuild com `atualizar_db.py`, perde o patch cirúrgico. Avaliar se o rebuild já incorpora os nomes canônicos do log_renomeacao.
- **Script v1 (`sincronizar_referencias.py`) ainda existe no disco.** Mantido como referência histórica, mas **não usar** — contém os 2 bugs. O v2 é o oficial daqui pra frente.

---

**Lição estruturante:** o bug não estava no código de cada linha — estava na **interação** entre 3 decisões aparentemente inócuas (chave de dict, REPLACE textual, múltiplas execuções). Passou por dry-run, passou por apply "bem-sucedido", só foi detectado quando o dry-run pós-apply mostrou refs "remanescentes" que numericamente não deveriam existir. Sem a prática de rodar dry-run depois do apply para validação, o dano teria permanecido silencioso.
