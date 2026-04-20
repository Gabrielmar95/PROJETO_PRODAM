# AUDITORIA GLOBAL — Duas pastas PRODAM no Desktop

**Data:** 14/04/2026 | **Escopo:** PROJETO_PRODAM (novo) + Projeto PRODAM (Cowork/Claude Desktop)

---

## DESCOBERTA CRÍTICA (ler primeiro)

Você tem **DUAS pastas** com o mesmo projeto:

| Pasta | Caminho | Estado | Tamanho |
|-------|---------|--------|---------|
| **PROJETO_PRODAM** (novo) | `Desktop\PROJETO_PRODAM` | ATIVO | ~32 GB |
| **Projeto PRODAM** (Cowork) | `Desktop\Projeto PRODAM` | **VAZIA** (0 bytes) | 0 GB |
| Projeto PRODAM (arquivado) | `_ARCHIVE\2026-04-13\Projeto_PRODAM` | Arquivado | 12 GB |

**PROBLEMA #1 — CRÍTICO:** A pasta do Cowork (`Desktop\Projeto PRODAM` com espaço) está **VAZIA**. O Claude Desktop quando abrir essa pasta não vai achar nada. O conteúdo foi movido para `_ARCHIVE` em 13/04 e nunca restaurado/re-apontado.

**Impacto:** se você abrir o Claude Desktop agora, ele não terá contexto do projeto (sem `CLAUDE.md`, sem `profiles.json`, sem skills acessíveis por lá).

---

# PARTE 1 — PROJETO_PRODAM (pasta ativa)

## 1.1 Métricas gerais

- **Tamanho:** ~32 GB
- **Estrutura:** 2 subpastas grandes + 41 arquivos na raiz
- **Git:** 2 repos aninhados (PRODAM_DOCS/.git = 1.1 GB, SPCF_EXTRACAO/.git = 131 MB)
- **Scripts Python:** 8 scripts principais (2.636 linhas)
- **Devedores:** 67 (66 válidos + 1 entrada `_metadata` corrompida)

## 1.2 Problemas de estrutura

### 🔴 Triplicação documental (5-8 GB desperdiçados)
Cada devedor aparece em 3 lugares:
- `PRODAM_DOCS/<SIGLA>_CONSOLIDADO/` — 78 pastas (PDFs brutos)
- `PRODAM_DOCS/<SIGLA>_DOSSIE/` — 82 pastas (OCR + análise)
- `DOSSIES_MULTIFORMATO/<SIGLA>/` — 67 pastas (o que eu gerei hoje)

**Recomendação:** consolidar em UMA estrutura. O `DOSSIES_MULTIFORMATO` é o mais novo e completo. Os outros dois podem ser movidos para `_ARCHIVE` ou a estrutura `<SIGLA>_DOSSIE` promovida a canônica.

### 🔴 JSONs gigantes não-gitignored
- `DOSSIE_COMPLETO.json` (222 MB)
- `DOSSIE_COMPLETO_SLIM.json` (113 MB)
- `MASTER_DOSSIE/corpus_consolidado.jsonl` (104 MB)
- `PRODAM_DOCS/_ANALISE/prodam.db` (92 MB — cópia redundante de `prodam.db` da raiz)
- `PRODAM_DOCS/_ANALISE/ANALISE_COMPLETA.json` (84 MB)

**Total:** ~615 MB que deveriam estar em `.gitignore` (são gerados, não fonte).

### 🟡 Lixo do sistema de arquivos
- 7× `.fuse_hidden*` (32 KB cada) — artefatos de mount que travam sync
- `.CLAUDE.md.bak` (3 KB)

## 1.3 Problemas de código Python

### 🔴 `/tmp/` hardcoded (Windows vai falhar silenciosamente)
**Arquivo:** `reconciliacao_4_fontes.py:215`
```python
tmp_db = "/tmp/reconciliacao_prodam.db"   # não existe em Windows
```
**Fix:** `tempfile.gettempdir()`.

### 🔴 Datas hardcoded (script expira em si mesmo)
**Arquivo:** `ses_reconciliacao_completa.py:33-34`
```python
HOJE = date(2026, 4, 14)
PRESCRICAO_CUTOFF = date(2021, 4, 14)
```
**Fix:** `date.today()` e subtração dinâmica.

### 🟡 Sem testes, sem `requirements.txt`
- Nenhum `test_*.py` ou `tests/`
- Dependências implícitas: `openpyxl` (opcional), `sqlite3`, `json`, `pathlib`
- Funções monetárias críticas (`brl()`, `pct_diff()`) sem cobertura

## 1.4 Problemas de integridade de dados

### 🔴 179 clientes órfãos em spcf_faturas sem entrada em profiles.json
Top 10: SES (110 fat), BRADESCO FINANCIAMENTO (72), FAAR (63), CAIXA (60), PREF COARI (53), BANCO MASTER (51), PROVER (48), PGE (46), BRADESCO (43), SEMIG (30).

**Impacto:** faturas ativas sem estratégia jurídica definida.

### 🔴 22 devedores em profiles.json sem faturas no DB
Ex: AADESAM, ANOREG, B23 TECNOLOGIA, FMPES, SNPH, UGPI, FUNTEA, SUL AMERICA…

**Impacto:** devedores cadastrados mas sem nenhum contrato/fatura rastreada. Verificar se foram extintos.

### 🔴 Entrada `_metadata` corrompida
Entrada "_metadata" em profiles.json com todos os campos críticos nulos. **Deletar ou popular.**

### 🟠 4 devedores sem CNPJ
CASA CIVIL, COSAMA, CASA MILITAR, BANCO DAYCOVAL.

### 🟠 Score médio de completude = 36.9%
Gerado pelo `auditoria_completude_devedor.py` de hoje. Metade dos devedores com < 50% de documentos essenciais.

### 🟡 233 empenhos a mais no consolidado_empenhos.json do que no spcf_empenhos (DB)
17.022 no JSON × 16.789 no DB. Reprocessar `build_sqlite.py` pode resolver.

---

# PARTE 2 — Projeto PRODAM (Cowork — pasta com espaço)

## 2.1 Estado atual

**`Desktop\Projeto PRODAM\` está VAZIA** (0 bytes, 0 arquivos).

O Claude Desktop configurado para essa pasta **não encontra nada** — projeto sem contexto.

## 2.2 Conteúdo histórico (em `_ARCHIVE/2026-04-13/Projeto_PRODAM/`)

**12 GB** arquivados em 13/04. Conteúdo:

| Categoria | Itens |
|-----------|-------|
| Pastas (workflow) | ANALISE, ASSETS, DADOS_5DEV, DASHBOARDS, DATA, DOCUMENTOS, DOCUMENTOS_GERADOS, DOSSIES, FATURAS_POR_DEVEDOR, INVENTARIO, LOGS, META, PEN DRIVE PRODAM OCR, RELATORIOS, REFERENCES, REFERENCIA_JURIDICA, SCRIPTS, `SKILLS NOVA`, SPCF, TESTS, `_ARQUIVO`, `_BACKUPS`, pipeline_output |
| Código | Dockerfile, docker-compose.yml, node_modules/, package.json, pytest.ini, mypy.ini, requirements.txt, `run_extraction.py`, `config_prodam.py`, `instalar_skills.ps1`, `inventario_prodam.ps1`, `PRODAM-CLI.ps1` |
| Dados | `profiles.json` (+ .bak + .bkp + .lock + .sha256) |
| Skills | 38 `*_SKILL.md` + `antigravity-prodam.plugin` + `prodam-juridico.skill` + `normalizador-valores-brl/` |
| Documentação | CLAUDE.md, README.md, TASKS.md, PENDENCIAS.md, CHANGELOG.md, VERSION, AUDITORIA_REPOSITORIO.md, INSTRUCOES_PROJETO.md, GUIA_INSTALACAO_MCPs.md |

## 2.3 Diferenças entre Cowork (arquivado) e PROJETO_PRODAM (atual)

| Item | Cowork (arquivado) | PROJETO_PRODAM (atual) |
|------|---------------------|------------------------|
| profiles.json — nº campos | **77** | **126** |
| Devedores | 66 (sem _metadata) | 67 (inclui _metadata) |
| Força FRACA | 35 | 39 |
| Arquitetura | Docker + Node | Python puro |
| Skills | 38 skills (+ .plugin) | 49+ skills no `_SKILLS/` + 2 novas em `~/.claude/skills/` |
| Tests | Tem `TESTS/` + pytest.ini | Nenhum teste |
| Backups profiles | `.bak` + `.bkp` + `.sha256` + `.lock` | Nenhum |
| Sistema CLI | `PRODAM-CLI.ps1` | `sincronizar_prodam.py` + `.bat` |
| Scripts | `run_extraction.py`, `config_prodam.py` | `atualizar_db.py`, `sincronizar_prodam.py`, `dossie_multiformato_devedor.py`, `auditoria_completude_devedor.py` |
| Infra jurídica | REFERENCIA_JURIDICA/ (18 pastas) | REFERENCIA_JURIDICA/ em PRODAM_DOCS/ (20 pastas) |
| Última atualização CLAUDE.md | 13/04/2026 Sessão 77 | 14/04/2026 13:22 |
| Obrigação diária | Relatórios quinzenais com multas (R$500/dia) — **visível** | Não visível em CLAUDE.md — regressão de contexto |

## 2.4 Problemas do Cowork

### 🔴 Cowork sem contexto (pasta vazia)
Se você abrir o Claude Desktop agora, ele não encontra nada. Precisa escolher 1 de 3 soluções:

**A) Apontar Cowork para a pasta nova** (RECOMENDADO)
No Claude Desktop, mudar a pasta do projeto de `Projeto PRODAM` para `PROJETO_PRODAM`. Cowork passa a ler o conteúdo atual.

**B) Restaurar conteúdo arquivado**
```powershell
Copy-Item -Recurse "C:\Users\gabri\Desktop\_ARCHIVE\2026-04-13\Projeto_PRODAM\*" `
                   "C:\Users\gabri\Desktop\Projeto PRODAM\"
```
Problema: fica desatualizado vs PROJETO_PRODAM novo.

**C) Symlink** (melhor técnica)
Criar link da pasta Cowork apontando para PROJETO_PRODAM:
```powershell
# Remove a pasta vazia, cria junction
Remove-Item "C:\Users\gabri\Desktop\Projeto PRODAM"
cmd /c mklink /J "C:\Users\gabri\Desktop\Projeto PRODAM" "C:\Users\gabri\Desktop\PROJETO_PRODAM"
```
Assim, as 2 pastas viram a MESMA — qualquer edição reflete nas duas.

### 🔴 Regressão de contexto
O CLAUDE.md do Cowork (antigo) tinha informações que o novo perdeu:
- Multas contratuais (R$ 500/dia + 10% por prescrição)
- Identidade completa (OAB, escritório, contrato)
- Distribuição por fase (F0, F3, F5) por devedor
- Status granular ("TRD pronto", "Petição pronta", "Negativa expressa")

O CLAUDE.md novo (gerado por `auto_update_claude_md.py`) é mais pobre — só tem métricas top-level.

**Recomendação:** mesclar o conteúdo jurídico-contratual do CLAUDE.md arquivado no novo, ou fazer o `auto_update_claude_md.py` preservar seções estáticas.

### 🟡 Skills duplicadas entre 3 lugares
Mesma skill pode existir em:
- `_ARCHIVE/Projeto_PRODAM/*_SKILL.md` (arquivado, 38 skills)
- `PROJETO_PRODAM/PRODAM_DOCS/_SKILLS/*_SKILL.md` (atual, 49+ skills)
- `C:\Users\gabri\.claude\skills/<nome>/SKILL.md` (user-level, 39 skills)

Fonte da verdade não definida. Algumas skills podem estar desatualizadas em alguns lugares.

---

# PARTE 3 — Plano de correção priorizado

## 🔴 AGORA (15 min)

1. **Decidir destino do Cowork** — recomendado: criar junction (Opção C acima) ou apontar Claude Desktop para a pasta nova. Sem isso, Cowork está inutilizável.
2. **Deletar `_metadata` do profiles.json** — cria bug em qualquer script que itere sobre devedores.
3. **Fix `/tmp/` em `reconciliacao_4_fontes.py:215`** — bug silencioso no Windows.
4. **Fix `HOJE` hardcoded em `ses_reconciliacao_completa.py:33`** — script vira útil por apenas 1 dia.

## 🟠 HOJE/AMANHÃ (2 horas)

5. **Resolver 179 clientes órfãos** — rodar reconciliação para criar profiles para SES×110, BRADESCO×72, etc., ou documentar por que NÃO devem ser cobrados.
6. **Preencher CNPJs faltantes** — 4 devedores (CASA CIVIL, COSAMA, CASA MILITAR, BANCO DAYCOVAL).
7. **Popular `faturas_exigiveis` faltantes** — 4 devedores sem esse campo.
8. **Criar `.gitignore`** com: `*.db`, `DOSSIE_COMPLETO*.json`, `ANALISE_COMPLETA.json`, `_ANALISE/prodam.db`, `MASTER_DOSSIE/corpus*`, `DOSSIES_MULTIFORMATO/`, `AUDITORIA_COMPLETUDE/`, `.fuse_hidden*`.
9. **Criar `requirements.txt`** com openpyxl e dependências opcionais.

## 🟡 ESTA SEMANA (1 dia)

10. **Desdobrar triplicação documental** — decidir entre `CONSOLIDADO/` + `DOSSIE/` + `DOSSIES_MULTIFORMATO/`. Manter 1, arquivar/deletar 2.
11. **Restaurar seções perdidas do CLAUDE.md** (identidade, multas, fases, status granular).
12. **Git cleanup** — rodar `git gc --aggressive` em `PRODAM_DOCS/.git` (1.1 GB) e `SPCF_EXTRACAO/.git` (131 MB).
13. **Adicionar testes unitários** para funções monetárias críticas.
14. **Validar 22 devedores órfãos reversos** — marcar como EXTINTO ou re-scrape do SPCF.

## 🟢 DEPOIS (ajuste fino)

15. Padronizar nomes de pasta (UPPER_SNAKE_CASE ou lowercase_snake).
16. Refatorar funções > 100 linhas (`reconciliar()`, `auditar_devedor()`).
17. Remover `except: pass` nos scripts em `_SCRIPTS_IMPORTADOS/`.

---

# RESUMO EM 1 FRASE POR PASTA

- **PROJETO_PRODAM (ativo):** funcional mas com ~9 GB de duplicação, 179 clientes órfãos, 2 bugs críticos (paths/datas), e `_metadata` corrompida no profiles.json.
- **Projeto PRODAM (Cowork):** **vazio, inutilizável agora** — precisa apontar Claude Desktop para a pasta nova OU criar junction. Conteúdo histórico preservado em `_ARCHIVE` mas desatualizado.

**Ação #1 absoluta:** resolver o Cowork vazio (junction ou redirect) antes de qualquer outra coisa.

---

_Relatório gerado por auditoria paralela (3 agentes Explore + consolidação) em 14/04/2026._
