# Relatório de Sessão — 08/06/2026

## Faxina de infra (Claude Code local) + Lacuna 4 + diagnóstico P1 (prescrição)

> Autor: Gabriel Mar (OAB/AM 15.697) · Projeto PRODAM · Contrato 002/2026 (PRODAM S.A. × Brandão Ozores).
> Sessão conduzida no Claude Code local (Windows/PowerShell). Encerramento solicitado: salvar o realizado/erros/acertos e sincronizar com o GitHub.

---

## 1. Pedido da sessão

Duas frentes entrelaçadas, decididas em plan mode:

1. **Status + próximos passos** da operação de recuperação de créditos.
2. **Auditoria de infra** — conferir hooks, agents, `CLAUDE.md`, settings e o ecossistema de skills/plugins.

Decisões em vigor: **foco = Claude Code local** (não Cowork agora); **faxina de infra primeiro**, depois o núcleo jurídico; Lacuna 4 = **higienizar inline** (remover menções ao `config_prodam.py` fantasma, sem criar arquivo novo).

---

## 2. ✅ Realizado (acertos)

### 2.1 Proteção anti-delete de PDF religada (furo real fechado)
- `block_pdf_delete.ps1` existia em `.claude/hooks/` mas **não estava conectado a nenhum settings** — a proteção documentada no `CLAUDE.md §7` estava **inativa**.
- Adicionado bloco `PreToolUse` (matcher `Bash|PowerShell`) em [.claude/settings.json](../.claude/settings.json), espelhando o padrão dos hooks globais. PDFs são prova judicial — o hook agora bloqueia remoção via Bash/PowerShell pelo Claude Code.

### 2.2 Bug real no gerador `auto_update_claude_md.py` (contagem fantasma)
- `compute_metrics` contava a chave `_metadata` do `profiles.json` como se fosse devedor → `total` virava **70** (em vez de **69**) e injetava uma categoria fantasma **`N/A=1`** no pipeline.
- Correção: filtro `data = {k: v for k, v in data.items() if not k.startswith("_")}` antes de agregar. Não é cosmético — corrige a fonte que reimprimia "70 devedores" a cada sincronização.

### 2.3 CLAUDE.md + 3 satélites regenerados
- Rodado `py -3.12 scripts\auto_update_claude_md.py` → [CLAUDE.md](../CLAUDE.md), [STATUS_DEVEDORES.md](../STATUS_DEVEDORES.md), [WORKFLOW_COBRANCA.md](../WORKFLOW_COBRANCA.md), [PLAYBOOK_ORGAOS_V2.md](../PLAYBOOK_ORGAOS_V2.md) atualizados (timestamp 08/06/2026 12:24).
- Contagem corrigida para **69 devedores** em todo o documento.
- Backup automático `CLAUDE.md.bak.20260608_125259` criado (não versionado).
- ⚠️ A seção **§3 ALERTAS DE PRESCRIÇÃO** (SSP 🔴 22 dias; SEJUSC 🟡 84 dias) é **provisória**: deriva das datas do `profiles.json`, que estão sob suspeita (ver §4 P1). Regenerar de novo após sanear o SSOT.

### 2.4 Lacuna 4 — Regra 4 corrigida (config_prodam.py / normalizador.py fantasmas)
- Confirmado por glob recursivo: **nem `config_prodam.py` nem `scripts/normalizador.py` existem** em código ativo.
- A Regra 4 (no gerador e no `CLAUDE.md`) afirmava falsamente que `normalizador.py` era a "SSOT real" de índices.
- Texto reescrito (gerador + `CLAUDE.md` raiz): declara que **não há arquivo-SSOT de índices**; regime/índice (SELIC/IGPM/IPCA) é confirmado por **cláusula contratual**; correção SELIC vem da **API live do BCB** (série SGS 4390) em `scripts/ad_hoc/gerar_memorial_preliminar_ses.py`. Guarda estendida: "não criar `config_prodam.py`/`normalizador.py` sem auditoria prévia".

### 2.5 Órfãos arquivados (não deletados)
- `.claude/hooks/CLAUDE.md` (dump vazio do claude-mem) e `.claude/hooks/gsd-check-update-worker.js` (resíduo dos plugins GSD removidos em 12/05) **não eram referenciados por nenhum settings**.
- Movidos para `_BACKUPS/_orfaos_faxina_20260608/` (arquivados, não `rm` — disciplina de provas por analogia) e removidos do diretório de hooks.

### 2.6 ⭐ Guard anti-"Teori-relator" estendido a `.js` — pegou erro jurídico REAL
- `validar_citacoes.py` e o workflow CI `validar_citacoes.yml` passaram a cobrir arquivos **`.js`** (antes só `.md`/`.py`).
- A validação pegou uma **citação distorcida em [gera_notificacao_ses.js](../gera_notificacao_ses.js)**: o script gerava notificação à SES afirmando que o título executivo era sustentado por **"Min. Teori Zavascski"** — quando, no `REsp 793.969/RJ`, **Teori foi VENCIDO**; o relator p/ acórdão é o **Min. José Delgado**.
- Corrigido para: *"REsp 793.969/RJ, Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido"*. **Esse erro iria para uma peça real** — é o achado de maior valor da sessão.

### 2.7 Verificação
- `py -3.12 -m pytest tests\ -q` → **136 passed**. Base (`prodam_utils`: BRL/Decimal/datas/prescrição) verde após as mudanças.

---

## 3. ⚠️ Erros e correções de rota

### 3.1 Premissa de redirect inválida (corrigida a tempo)
- O plano inicial era **redirecionar** as menções de `config_prodam.py` para `scripts/normalizador.py`. Verificação de ground truth mostrou que `normalizador.py` **também é fantasma** — eu teria trocado um fantasma por outro.
- Correção: abandonei o redirect e declarei o estado real (alinhado à decisão "remover menções"). Lição reforçada: confirmar existência antes de apontar um caminho como SSOT.

### 3.2 Fantasmas adjacentes flagrados, não consertados (escopo)
- O satélite WORKFLOW do gerador ainda emite 4 caminhos inexistentes: `extracao_contratual.py`, `atualizacao_monetaria_bcb.py`, `blindagem_pre_execucao.py`, `normalizador.py`. **Flagrados como achado adjacente**, não corrigidos neste turno (disciplina de escopo).

### 3.3 O resumo de contexto subestimou o realizado
- O resumo da sessão anterior dizia que o `CLAUDE.md` **não** havia sido regenerado e que vários itens da faxina estavam pendentes. A inspeção do working tree no encerramento mostrou que a faxina foi de fato executada (itens 2.1–2.6). Relatório baseado no **estado real do disco**, não no resumo.

---

## 4. 🔴 Diagnóstico P1 — crise de integridade das datas de prescrição (NÃO resolvido)

Rodado `py -3.12 scripts\alerta_prescricao.py --json`. Achados:

- **23 devedores classificados como prescritos** → R$ 104.636.986,17 atualizado → **"multa 10%" projetada de R$ 10.463.698,62**.
- **22 dos 23 com `d_plus = -20` idêntico** → é **carimbo default, não cálculo fatura-a-fatura** (viola a **Regra 7**: prescrição por fatura individual, do vencimento).
- Contradições no SSOT:
  - **SSP**: CSV diz prescrito (`d_plus -39`, R$ 29,03M atu., `PROTOCOLAR_PETICAO`), mas `CLAUDE.md §3` aponta alerta para **2026-06-30**.
  - **SEDUC**: marcado `PRESCRITA` e ao mesmo tempo `ANALISAR_DOCUMENTACAO` com R$ 50,26M.
  - **ADS**: `d_plus +3` (R$ 211.657,47) — **crítico iminente**.

**Conclusão:** os R$ 10,46M de "multa" são **provável poluição de dado**, não exposição real. Mutar o SSOT exige **recálculo fatura-a-fatura** a partir do `prodam.db` (vencimento + marcos do Art. 202 CC), **validado primeiro contra o DETRAN** (ground truth) antes de generalizar para os 68 demais. **Nada foi mutado no `profiles.json`** — decisão humana pendente.

---

## 5. Pendências (próxima sessão)

| Prioridade | Item | Observação |
|---|---|---|
| 🔴 P1 | Recálculo de prescrição fatura-a-fatura | DETRAN-first; reescrever `data_prescricao_proxima` no SSOT e re-rodar o gerador. Decisão humana: qual fonte vence. |
| 🟠 P2 | **ADS** (`d_plus +3`) | Confirmar se a prescrição consumou; ação imediata se ainda houver janela. |
| 🟠 P2 | **SSP** R$ 4,55M, `PROTOCOLAR_PETICAO` | Resolver a contradição de data e protocolar se a peça estiver pronta. |
| 🟡 — | 4 fantasmas do satélite WORKFLOW | Higienizar no gerador (achado 3.2). |
| 🟡 — | Consolidação-autoria 2b + bulk skill-sweep `config_prodam` | ~95 menções em SKILL.md; **não tocar** o `sincronizador-juridico-matriz` (usa `config_prodam` como âncora de detecção) nem os `.bak`. |
| 🟢 — | Lacunas 1/2a do ecossistema | `relatorios/AUDITORIA_ECOSSISTEMA_20260512.md`. |

---

## 6. Restrições respeitadas

PDFs nunca apagados (órfãos **arquivados**, não removidos) · `profiles.json` **não mutado** (SSOT intacta) · valores em Decimal · sem git destrutivo · gate jurídico sobre docs sensíveis preservado · PowerShell only.

---

## 7. Arquivos tocados nesta sessão (no repo)

- `.claude/settings.json` — bloco `PreToolUse` (hook PDF).
- `scripts/auto_update_claude_md.py` — fix `compute_metrics` (`_metadata`) + Regra 4.
- `scripts/validar_citacoes.py` + `.github/workflows/validar_citacoes.yml` — cobertura `.js`.
- `gera_notificacao_ses.js` — correção da citação REsp 793.969/RJ.
- `CLAUDE.md`, `STATUS_DEVEDORES.md`, `WORKFLOW_COBRANCA.md`, `PLAYBOOK_ORGAOS_V2.md` — regenerados (69 devedores).
- `INSTRUCOES_COWORK.md` — ajuste de texto.
- `.claude/hooks/CLAUDE.md`, `.claude/hooks/gsd-check-update-worker.js` — removidos (arquivados em `_BACKUPS/`).
- **Fora do repo:** memória `project_ssot_valores_monetarios_prodam.md` atualizada em `~/.claude/projects/.../memory/`.
