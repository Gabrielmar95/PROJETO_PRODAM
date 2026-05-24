# Sessão 2026-05-08 — Sincronizador Jurídico (Opção A)

Snapshot da varredura `etapa2_varredura.py` contra os 3 CLAUDE.md do PROJETO_PRODAM, sem `--strict`. Objetivo: validar formato do output e confirmar que não trava antes de partir para escopo maior.

## Comando executado

```powershell
py -3.12 "C:\Users\gabri\.claude\skills\sincronizador-juridico-matriz\scripts\etapa2_varredura.py" --corpus "C:\Users\gabri\Desktop\PROJETO_PRODAM\CLAUDE.md" "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\CLAUDE.md" "C:\Users\gabri\Desktop\PROJETO_PRODAM\SPCF_EXTRACAO\CLAUDE.md"
```

Sem `--strict` → modo warn-first (bloqueios viram WARN, exit 0 ou 1).

## Cabeçalho do output

```
etapa2_varredura: 182 skills, categorias={'operacional': 82, 'excluir': 53, 'nucleo': 39, 'referencia': 8}, strict=False, pendentes_validacao=['E04'], --corpus=3 arquivos, overrides={13 skills, 13 silenciamentos, 1 mudanças categoria}
hits totais: 504  |  bloqueios: 0  |  warnings: 290
```

- **Exit code: 1** (EXIT_WARN — comportamento esperado sem `--strict`).
- **0 bloqueios** — nenhum hit virou exit 2.
- **Tempo de execução:** ~5–10 segundos. Não travou.

## Hits do `PROJETO_PRODAM\CLAUDE.md` (tier `peca`) — 8 hits, todos falsos positivos

| # | Detector | Gravidade | Linha | Trecho | Avaliação |
|---|----------|-----------|-------|--------|-----------|
| 1 | E01 | CRÍTICO | 11 | `prescrição` | FP — contexto de catálogo de regras, não afirma cutoff próprio |
| 2 | E01 | CRÍTICO | 16 | `prescritas` | FP — métricas do portfólio (1085 prescritas / 2412 exigíveis) |
| 3 | E01 | CRÍTICO | 40 | `PRESCRIÇÃO` | FP — header de seção "ALERTAS DE PRESCRIÇÃO" |
| 4 | E01 | CRÍTICO | 100 | `prescrição` | FP — referência a Art. 202 CC em regra educativa |
| 5 | E01 | CRÍTICO | 168 | `prescrição` | FP — testes unitários de `prodam_utils` |
| 6 | E03 | ALTO | 62 | `SELIC` | FP — texto explica que "SELIC já inclui correção + juros" (regra anti-bis-in-idem, não bis-in-idem) |
| 7 | E05 | MÉDIO | 91 | `IPCA` | FP — tabela DETRAN cita "IGPM (7 contratos) + IPCA (3 contratos)"; sem âncora de cláusula no contexto |
| 8 | E06 | CRÍTICO | 72 | `30%` | **FP grave** — linha diz literalmente "Fee: **20%** ... (não 30%)". Detector não distingue afirmação de negação contextual. **Em modo `--strict` viraria EXIT_BLOCK CRÍTICO num arquivo que ensina exatamente o oposto do erro que o E06 caça.** |

Todos os 8 saíram como `[WARN ... warn-first]` por ausência de `--strict`. Em modo rigoroso, os 6 hits CRÍTICO/ALTO virariam EXIT_BLOCK.

## Sub-CLAUDE.md — confirmados em zero hits

| Arquivo | Hits | Confirmação |
|---|---|---|
| `PRODAM_DOCS\CLAUDE.md` | 0 | Não aparece no detalhe (etapa2_varredura.py linha 1373: `if not hits: continue`). Grep manual confirmou ausência de termos gatilho (`prescri`/`SELIC`/`IGPM`/`IPCA`/`30%`/`51.084`/`Teori Zavascki`/`José Delgado`). Conteúdo é só OCR/dossiês. |
| `SPCF_EXTRACAO\CLAUDE.md` | 0 | Idem. Conteúdo técnico (scraping/OCR/FTS5), sem termos jurídicos quentes. |

## Origem dos 290 warnings (decomposição)

| Origem | Hits WARN | % do total |
|---|---|---|
| `PROJETO_PRODAM\CLAUDE.md` (peca) | 8 | 2,8% |
| `PRODAM_DOCS\CLAUDE.md` (peca) | 0 | 0% |
| `SPCF_EXTRACAO\CLAUDE.md` (peca) | 0 | 0% |
| **Subtotal `--corpus`** | **8** | **2,8%** |
| 182 skills do registry (varridas independentemente do `--corpus`) | 282 | 97,2% |
| **Total** | **290** | **100%** |

Os 504 hits totais menos 290 WARN = 214 hits classificados como `[passa]` (silenciados por skill via overrides ou tier não bloqueia naquela gravidade).

## TODO aberto no repo do sincronizador

Adicionado em `~/.claude/skills/sincronizador-juridico-matriz/TODO.md`, dentro da seção "Próximas iterações do sincronizador", após "Detectores E10 e E11":

> **FP E06 — negação contextual ("não 30%", "ao invés de 30%", "diferente de 30%")**
>
> Detector E06 dispara em qualquer ocorrência de `30%` cuja janela contém termos de remuneração, mas não distingue afirmação de negação contextual. Caso real: CLAUDE.md raiz do PROJETO_PRODAM, linha 72.
>
> Cobre: sintoma, fix proposto (regex de exclusão `(?:n[aã]o|nem|inv[eé]s|diferente)\s+...` à esquerda do número, janela ~30 chars), 4 fixtures de teste sugeridas, critério de aceite, risco de falso negativo, e pergunta colateral sobre E07 (Decreto 51.084 "revogado pelo 53.464") ter mesmo bug latente.

Não corrigi o detector — só registrei.

## Outros artefatos da sessão (fora do escopo da varredura)

- **Memória corrigida:** `reference_resp_793969_relator.md` — removida afirmação obsoleta de que CLAUDE.md regra #13 contém erro (verificado em 2026-05-08 que o arquivo já cita "Min. José Delgado" corretamente). MEMORY.md também atualizado.
- **`.claude/settings.local.json` mesclado:** 25 itens existentes + 11 novos = 36 itens em `permissions.allow`. JSON validado (parsea OK). `enabledMcpjsonServers` preservado.

## Pendências para próxima sessão

1. **Opção B com `--strict`:**
   ```powershell
   py -3.12 "C:\Users\gabri\.claude\skills\sincronizador-juridico-matriz\scripts\etapa2_varredura.py" --corpus "C:\Users\gabri\Desktop\PROJETO_PRODAM\CLAUDE.md" "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\REFERENCIA_JURIDICA" --strict
   ```
   - Esperar exit 2 (EXIT_BLOCK) por causa dos 6 hits CRÍTICO/ALTO já visíveis no CLAUDE.md raiz da Opção A.
   - Se quiser separar o ruído do CLAUDE.md raiz: rodar só `--corpus PRODAM_DOCS\REFERENCIA_JURIDICA --strict` para ver hits exclusivos da base jurídica curada.

2. **Limpeza do `settings.local.json`** (registrada para passo separado):
   - **3 entradas `Bash(git -C C:/Users/gabri/Desktop/PROJETO_PRODAM ...)`** com path absoluto: redundantes com os novos genéricos `Bash(git log*)`/`Bash(git diff*)`. Quebram se o projeto for movido de pasta.
   - **3 entradas `Bash(mv ...CLAUDE.md ..._CLAUDE_HISTORICO.md)`**: operações destrutivas já consumadas. Provavelmente não devem repetir; podem ser removidas com segurança.
   - Decisão: revisar e remover na próxima sessão de manutenção do settings.

3. **Issues do CLAUDE.md raiz não atacadas nesta sessão** (registradas no relatório anterior do `claude-md-improver`):
   - Linha 14: soma 26+21+22 = **69**, não 70 devedores. Correção precisa ser em `scripts/auto_update_claude_md.py` para não ser sobrescrita.
   - PRODAM_DOCS/CLAUDE.md: sem nota explicando diferença DETRAN R$ 17,8M (113 faturas SPCF) vs R$ 31,7M (exigível total no raiz).

## Não-objetivos desta sessão

- Não houve commit. Sem alteração em `prodam.db`, `profiles.json`, ou qualquer arquivo do portfólio jurídico.
- Não houve geração de documento jurídico (TRD, notificação, petição, dossiê).
- Não houve varredura de `.docx`/`.pdf` — bug Iter 14b (read_text com binários) permanece em aberto, evitado por omissão (pattern default `*.md *.txt`).
