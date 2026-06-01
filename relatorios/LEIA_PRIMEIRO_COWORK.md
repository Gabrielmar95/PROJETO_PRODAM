# ✅ LEIA PRIMEIRO — Checklist de configuração do PRODAM no Cowork
**Para:** Gabriel Mar (OAB/AM 15.697) · **Data:** 01/06/2026

> Este é o **checklist de cliques**. O detalhe e o "porquê" de cada passo estão no
> guia grande: [HANDOFF_COWORK_2026-06-01.md](HANDOFF_COWORK_2026-06-01.md).
> Só **um** passo envolve colar texto (Passo 4) — todo o resto é apontar/clicar.

---

## ⚙️ ANTES de abrir o Cowork (só na 1ª vez no Windows)

- [ ] **1.** Claude Desktop instalado (assinatura paga).
- [ ] **2.** Instalar o **Git for Windows**.
- [ ] **3.** **Reiniciar** o Claude Desktop depois de instalar o Git.

## 🖥️ CRIAR o projeto no Cowork

- [ ] **4.** Abrir o Cowork (digitar `/desktop` ou abrir pelo menu).
- [ ] **5.** Barra lateral → **"New Project"** → **"use an existing folder"**.
- [ ] **6.** Selecionar a pasta: `C:\Users\gabri\Desktop\PROJETO_PRODAM`.
- [ ] **7.** Nomear: `PRODAM — Recuperação de Créditos`.

## 📌 CONFIGURAR os canais

- [ ] **8. COLAR as regras** → campo **Instructions**: abrir
      [PROJECT_INSTRUCTIONS_PARA_COLAR.md](PROJECT_INSTRUCTIONS_PARA_COLAR.md),
      copiar tudo abaixo da linha tracejada e colar aqui.
      *(É o ÚNICO texto que você cola. Este arquivo aqui NÃO vai no campo.)*
- [ ] **9. FIXAR (pin)** em **Files / Context**:
  - [ ] `PRODAM_DOCS/REFERENCIA_JURIDICA/` (destaque: `01_NOTA_METODOLOGICA/` e `PRECEDENTES_VERIFICADOS.md`)
  - [ ] `PRODAM_DOCS/profiles.json`
  - [ ] `STATUS_DEVEDORES.md`
  - [ ] `WORKFLOW_COBRANCA.md`
- [ ] **10. Connectors** → confirmar **`sqlite-prodam`** ligado (aponta p/ `prodam.db`).
- [ ] **11. Permissão** → **"Ask before acting"** (protege PDFs e git).
- [ ] **12. Create** (criar o projeto).

## ✅ TESTAR se funcionou

- [ ] **13. Teste de integridade** — 1ª mensagem ao Cowork:
      > *"Quais regras do CLAUDE.md do projeto você está enxergando?
      > Cite a Regra #13 sobre o REsp 793.969 e quem é o relator."*
      - Respondeu **José Delgado** → ✅ ele está lendo o CLAUDE.md sozinho.
      - Não soube → tudo bem: as regras do Passo 8 já seguram o essencial.
- [ ] **14. Primeiros comandos** (pedir ao Cowork para rodar):
      ```powershell
      py -3.12 scripts\auto_update_claude_md.py
      py -3.12 scripts\consultas.py --lista
      py -3.12 reconciliar_prescricao.py
      ```

---

### Os dois arquivos que você vai usar — não confundir
| Arquivo | O que é | O que fazer |
|---------|---------|-------------|
| **este (`LEIA_PRIMEIRO_COWORK.md`)** | checklist de cliques | **ler e seguir** |
| [`PROJECT_INSTRUCTIONS_PARA_COLAR.md`](PROJECT_INSTRUCTIONS_PARA_COLAR.md) | as regras invioláveis | **colar** no campo Instructions (Passo 8) |
| [`HANDOFF_COWORK_2026-06-01.md`](HANDOFF_COWORK_2026-06-01.md) | guia completo + briefing | consultar só se quiser o detalhe |
