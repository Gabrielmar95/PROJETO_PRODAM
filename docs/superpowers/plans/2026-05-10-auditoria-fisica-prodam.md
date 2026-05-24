# Auditoria Física PROJETO_PRODAM — Sweep + Classify + Aplicar Limpezas Seguras

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mapear toda a desorganização física da pasta `PROJETO_PRODAM/`, classificar cada item por regra determinística, e aplicar apenas limpezas reversíveis com gate de aprovação por categoria (`.gitignore`, relocação de `.bak` da raiz, consolidação de scripts `.py` soltos).

**Architecture:** Pipeline de 3 camadas isoladas. (1) **Sweep** — script Python read-only que percorre a árvore e emite `_AUDITORIA_FISICA/inventario.json`. (2) **Classify** — script Python aplica regras determinísticas e produz `_AUDITORIA_FISICA/classificacao.json` com rótulos por item (`KEEP`, `ARCHIVE_TO_LEGACY`, `MOVE_TO_SCRIPTS`, `GITIGNORE`, `STAGE_FOR_COMMIT`, `NEEDS_HUMAN_DECISION`). (3) **Act** — três batches independentes de mutação (`gitignore_hardening`, `relocate_root_baks`, `consolidate_loose_scripts`), cada um confirmado pelo usuário antes de executar; cada mutação é um `git mv` ou append em `.gitignore`, totalmente reversível via `git restore`/`git revert`.

**Escopo / Não-escopo:**
- ✅ **No escopo:** raiz do projeto, scripts soltos na raiz, `.bak/.backup` na raiz, `node_modules` não-ignorados, `_AUDITORIA_FISICA/` (criação).
- ❌ **Fora do escopo (gate humano explícito):** mover/apagar conteúdo dentro de `PRODAM_DOCS/`, `OCR_PESQUISAVEL_CONSOLIDADO/`, `SPCF_EXTRACAO/`, `DETRAN_AUDITORIA_COMPLETA/`, `_BACKUPS/`, qualquer `*.docx`/`*.pdf` jurídico, `profiles.json`, `prodam.db`, `REFERENCIA_JURIDICA/`, `DOSSIES*`, `DOCUMENTOS_GERADOS/`, `relatorios/`. Esses só recebem rótulo no JSON, nunca mutação automática.
- ❌ **Fora do escopo:** consolidar/decidir destino dos 30 `CLAUDE.md` espalhados (sai como `NEEDS_HUMAN_DECISION` no JSON; tratamento em sessão futura).
- ❌ **Fora do escopo:** mexer com `_ARQUIVO_*`, `_legado`, `_BACKUP_*`, `_QUESTOES_CRITICAS`, `_SESSAO`, `_SKILLS_NOVAS_*` (rotular `KEEP` por já estarem isolados).

**Tech Stack:** Python 3.12 (`py -3.12`), `pytest` para regras de classificação, PowerShell para `git mv` em batch, `git` para reversibilidade.

**Reversão garantida:** todo `git mv` é desfeito com `git mv` reverso. Append em `.gitignore` é desfeito com `git restore .gitignore`. Os artefatos `_AUDITORIA_FISICA/*.json` são puramente informativos; podem ser apagados sem efeito colateral.

---

## File Structure

**Criar:**
- `scripts/auditoria_fisica/__init__.py` — pacote vazio
- `scripts/auditoria_fisica/sweep.py` — sweep read-only, emite `inventario.json`
- `scripts/auditoria_fisica/classify.py` — regras determinísticas, emite `classificacao.json`
- `scripts/auditoria_fisica/apply_gitignore.py` — aplica appends em `.gitignore`
- `scripts/auditoria_fisica/apply_relocate_baks.py` — `git mv` dos `.bak` raiz para `_BACKUPS/relocados-AAAA-MM-DD/`
- `scripts/auditoria_fisica/apply_move_scripts.py` — `git mv` dos `.py` raiz para `scripts/` ou `scripts/ad_hoc/`
- `tests/auditoria_fisica/__init__.py` — pacote vazio
- `tests/auditoria_fisica/test_classify.py` — testes das regras
- `_AUDITORIA_FISICA/inventario.json` — saída do sweep
- `_AUDITORIA_FISICA/classificacao.json` — saída do classify
- `_AUDITORIA_FISICA/RELATORIO.md` — relatório executivo final
- `scripts/ad_hoc/` (diretório)

**Modificar:**
- `.gitignore` — adicionar regras para `node_modules/`, `*.bak`, `*.backup-*`, `*.bak-*`

**Não tocar:** todo o resto.

---

## Tasks

### Task 0: Setup do diretório de auditoria e baseline git

**Files:**
- Create: `_AUDITORIA_FISICA/baseline_git_status.txt`
- Create: `scripts/auditoria_fisica/__init__.py`
- Create: `tests/auditoria_fisica/__init__.py`
- Create: `scripts/ad_hoc/.gitkeep`

- [ ] **Step 1: Criar diretórios e arquivos sentinela**

```powershell
New-Item -ItemType Directory -Force -Path "_AUDITORIA_FISICA" | Out-Null
New-Item -ItemType Directory -Force -Path "scripts/auditoria_fisica" | Out-Null
New-Item -ItemType Directory -Force -Path "tests/auditoria_fisica" | Out-Null
New-Item -ItemType Directory -Force -Path "scripts/ad_hoc" | Out-Null
New-Item -ItemType File -Force -Path "scripts/auditoria_fisica/__init__.py" | Out-Null
New-Item -ItemType File -Force -Path "tests/auditoria_fisica/__init__.py" | Out-Null
New-Item -ItemType File -Force -Path "scripts/ad_hoc/.gitkeep" | Out-Null
```

- [ ] **Step 2: Capturar baseline de git status (snapshot pré-mudanças)**

```powershell
git status --short > _AUDITORIA_FISICA/baseline_git_status.txt
git rev-parse HEAD > _AUDITORIA_FISICA/baseline_head.txt
```

Expected: dois arquivos criados; `baseline_git_status.txt` lista todos os untracked/modified atuais.

- [ ] **Step 3: Commit do scaffolding**

```bash
git add scripts/auditoria_fisica/__init__.py tests/auditoria_fisica/__init__.py scripts/ad_hoc/.gitkeep
git commit -m "chore(auditoria): scaffold pacote auditoria_fisica + scripts/ad_hoc"
```

`_AUDITORIA_FISICA/` permanece untracked nesta etapa (será ignorado posteriormente ou commitado conforme decisão do usuário).

---

### Task 1: Sweep — inventário read-only

**Files:**
- Create: `scripts/auditoria_fisica/sweep.py`
- Test: `tests/auditoria_fisica/test_sweep.py` (smoke test)

- [ ] **Step 1: Escrever smoke test do sweep**

`tests/auditoria_fisica/test_sweep.py`:

```python
"""Smoke test: sweep gera JSON com chaves esperadas."""
import json
import subprocess
import sys
from pathlib import Path


def test_sweep_produces_inventario_with_required_keys(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    out_path = tmp_path / "inventario.json"
    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "auditoria_fisica" / "sweep.py"),
            "--root",
            str(repo_root),
            "--out",
            str(out_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert "generated_at" in data
    assert "root" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert any(item["kind"] == "loose_root_script" for item in data["items"])
    assert any(item["kind"] == "root_bak_file" for item in data["items"])
    assert any(item["kind"] == "scattered_claude_md" for item in data["items"])
```

- [ ] **Step 2: Rodar o teste e ver falhar**

Run: `py -3.12 -m pytest tests/auditoria_fisica/test_sweep.py -v`
Expected: FAIL — `sweep.py` ainda não existe.

- [ ] **Step 3: Implementar `sweep.py`**

`scripts/auditoria_fisica/sweep.py`:

```python
"""Sweep read-only da pasta PROJETO_PRODAM.

Gera _AUDITORIA_FISICA/inventario.json com cada item categorizado por 'kind'.
Não escreve nada fora do --out path.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

LOOSE_SCRIPT_EXTENSIONS = {".py"}
BAK_PATTERNS = (".bak", ".backup", ".backup-", ".bak-", ".bak.")
LEGACY_DIR_PREFIXES = ("_ARQUIVO_", "_BACKUP_", "_BACKUPS", "_legado",
                      "_QUESTOES_CRITICAS", "_SESSAO", "_SKILLS_NOVAS_")
JURIDICAL_DIRS = {
    "PRODAM_DOCS", "OCR_PESQUISAVEL_CONSOLIDADO", "SPCF_EXTRACAO",
    "DETRAN_AUDITORIA_COMPLETA", "DETRAN_AUDITORIA",
    "DOSSIES", "DOSSIES_MULTIFORMATO", "DOCUMENTOS_GERADOS",
    "relatorios", "DETALHAMENTO_FATURAS", "_BACKUPS",
    "DETRAN_CONSOLIDADO_JSON", "DETRAN_CONTRATOS_JSON",
}


def is_bak(name: str) -> bool:
    lower = name.lower()
    return any(p in lower for p in BAK_PATTERNS)


def sweep(root: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    # 1. Scripts .py soltos na raiz
    for entry in sorted(root.iterdir()):
        if entry.is_file() and entry.suffix in LOOSE_SCRIPT_EXTENSIONS:
            items.append({
                "kind": "loose_root_script",
                "path": entry.name,
                "size": entry.stat().st_size,
                "mtime": dt.datetime.fromtimestamp(entry.stat().st_mtime).isoformat(),
            })

    # 2. Arquivos .bak/.backup na raiz
    for entry in sorted(root.iterdir()):
        if entry.is_file() and is_bak(entry.name):
            items.append({
                "kind": "root_bak_file",
                "path": entry.name,
                "size": entry.stat().st_size,
                "mtime": dt.datetime.fromtimestamp(entry.stat().st_mtime).isoformat(),
            })

    # 3. CLAUDE.md espalhados (excluindo a raiz)
    for claude_md in root.rglob("CLAUDE.md"):
        rel = claude_md.relative_to(root)
        if str(rel) == "CLAUDE.md":
            continue
        items.append({
            "kind": "scattered_claude_md",
            "path": str(rel).replace("\\", "/"),
            "size": claude_md.stat().st_size,
            "mtime": dt.datetime.fromtimestamp(claude_md.stat().st_mtime).isoformat(),
        })

    # 4. Pastas legadas top-level
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and any(entry.name.startswith(p) for p in LEGACY_DIR_PREFIXES):
            items.append({
                "kind": "legacy_top_dir",
                "path": entry.name,
                "mtime": dt.datetime.fromtimestamp(entry.stat().st_mtime).isoformat(),
            })

    # 5. node_modules detectados (potencial gitignore-miss)
    for nm in root.rglob("node_modules"):
        if nm.is_dir():
            rel = nm.relative_to(root)
            items.append({
                "kind": "node_modules",
                "path": str(rel).replace("\\", "/"),
            })

    # 6. Pastas top-level "ativas" (não-jurídicas, não-legacy) para classificação
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if any(entry.name.startswith(p) for p in LEGACY_DIR_PREFIXES):
            continue
        if entry.name in JURIDICAL_DIRS:
            items.append({"kind": "juridical_dir", "path": entry.name})
        else:
            items.append({"kind": "active_top_dir", "path": entry.name})

    return items


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    payload = {
        "generated_at": dt.datetime.now().isoformat(),
        "root": str(root),
        "items": sweep(root),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"sweep: {len(payload['items'])} items -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Rodar o teste e ver passar**

Run: `py -3.12 -m pytest tests/auditoria_fisica/test_sweep.py -v`
Expected: PASS.

- [ ] **Step 5: Rodar o sweep no projeto real**

```powershell
py -3.12 scripts/auditoria_fisica/sweep.py --root . --out _AUDITORIA_FISICA/inventario.json
```

Expected stdout: `sweep: <N> items -> _AUDITORIA_FISICA/inventario.json` (espera-se ~70+ items).

- [ ] **Step 6: Commit**

```bash
git add scripts/auditoria_fisica/sweep.py tests/auditoria_fisica/test_sweep.py
git commit -m "feat(auditoria): sweep read-only gera inventario.json"
```

---

### Task 2: Classify — regras determinísticas

**Files:**
- Create: `scripts/auditoria_fisica/classify.py`
- Test: `tests/auditoria_fisica/test_classify.py`

- [ ] **Step 1: Escrever testes das regras de classificação**

`tests/auditoria_fisica/test_classify.py`:

```python
"""Regras de classificação devem ser determinísticas e cobrir os 6 rótulos."""
from scripts.auditoria_fisica.classify import classify_item

LABELS = {
    "KEEP", "ARCHIVE_TO_LEGACY", "MOVE_TO_SCRIPTS",
    "MOVE_TO_SCRIPTS_AD_HOC", "GITIGNORE",
    "STAGE_FOR_COMMIT", "NEEDS_HUMAN_DECISION",
}


def test_all_labels_known():
    sample = {"kind": "root_bak_file", "path": "foo.bak"}
    assert classify_item(sample)["label"] in LABELS


def test_root_bak_is_archived():
    item = {"kind": "root_bak_file", "path": ".gitignore.backup-20260423-153153"}
    assert classify_item(item)["label"] == "ARCHIVE_TO_LEGACY"


def test_node_modules_is_gitignored():
    item = {"kind": "node_modules", "path": "detran_dashboard/server/node_modules"}
    assert classify_item(item)["label"] == "GITIGNORE"


def test_canonical_loose_script_moves_to_scripts():
    item = {"kind": "loose_root_script", "path": "gera_notificacao_ses_script.py"}
    assert classify_item(item)["label"] == "MOVE_TO_SCRIPTS"


def test_ad_hoc_loose_script_moves_to_ad_hoc():
    item = {"kind": "loose_root_script", "path": "limpar_suspeitos.py"}
    assert classify_item(item)["label"] == "MOVE_TO_SCRIPTS_AD_HOC"


def test_juridical_dir_is_kept():
    item = {"kind": "juridical_dir", "path": "PRODAM_DOCS"}
    assert classify_item(item)["label"] == "KEEP"


def test_legacy_top_dir_is_kept_already_isolated():
    item = {"kind": "legacy_top_dir", "path": "_ARQUIVO_DRIFT"}
    assert classify_item(item)["label"] == "KEEP"


def test_scattered_claude_md_needs_human_decision():
    item = {"kind": "scattered_claude_md", "path": "DOSSIES_MULTIFORMATO/CLAUDE.md"}
    assert classify_item(item)["label"] == "NEEDS_HUMAN_DECISION"


def test_active_top_dir_is_kept_by_default():
    item = {"kind": "active_top_dir", "path": "scripts"}
    assert classify_item(item)["label"] == "KEEP"
```

- [ ] **Step 2: Rodar testes e ver falhar**

Run: `py -3.12 -m pytest tests/auditoria_fisica/test_classify.py -v`
Expected: FAIL — `classify` ainda não existe.

- [ ] **Step 3: Implementar `classify.py`**

`scripts/auditoria_fisica/classify.py`:

```python
"""Classificação determinística do inventário.

Aplica regras puras (sem I/O) sobre cada item de inventario.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

CANONICAL_SCRIPT_PREFIXES = (
    "gera_", "gerar_", "sincronizar_", "baixar_", "ocr_",
    "inventario_", "notificacao_", "aplicar_", "insights_",
)

AD_HOC_SCRIPT_PREFIXES = (
    "analisar_", "classificar_", "limpar_", "profile_",
    "triar_", "reclassificar_",
)


def classify_item(item: dict[str, Any]) -> dict[str, Any]:
    kind = item.get("kind")
    path = item.get("path", "")

    if kind == "root_bak_file":
        return {**item, "label": "ARCHIVE_TO_LEGACY",
                "reason": "Arquivo .bak/.backup na raiz não pertence ao tracking ativo"}

    if kind == "node_modules":
        return {**item, "label": "GITIGNORE",
                "reason": "node_modules não deve estar tracked"}

    if kind == "loose_root_script":
        name = path.lower()
        if any(name.startswith(p) for p in AD_HOC_SCRIPT_PREFIXES):
            return {**item, "label": "MOVE_TO_SCRIPTS_AD_HOC",
                    "reason": "Script one-shot identificado por prefixo (ad-hoc)"}
        if any(name.startswith(p) for p in CANONICAL_SCRIPT_PREFIXES):
            return {**item, "label": "MOVE_TO_SCRIPTS",
                    "reason": "Script canônico identificado por prefixo"}
        return {**item, "label": "NEEDS_HUMAN_DECISION",
                "reason": "Script .py raiz sem prefixo conhecido"}

    if kind == "scattered_claude_md":
        return {**item, "label": "NEEDS_HUMAN_DECISION",
                "reason": "30+ CLAUDE.md exigem política unificada (sessão futura)"}

    if kind == "legacy_top_dir":
        return {**item, "label": "KEEP",
                "reason": "Pasta legada já isolada por convenção"}

    if kind == "juridical_dir":
        return {**item, "label": "KEEP",
                "reason": "Pasta jurídica fora do escopo de mutação automática"}

    if kind == "active_top_dir":
        return {**item, "label": "KEEP",
                "reason": "Pasta ativa do projeto"}

    return {**item, "label": "NEEDS_HUMAN_DECISION",
            "reason": f"Kind desconhecido: {kind}"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventario", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    raw = json.loads(args.inventario.read_text(encoding="utf-8"))
    classified = [classify_item(item) for item in raw["items"]]
    payload = {
        "generated_at": dt.datetime.now().isoformat(),
        "source_inventario": str(args.inventario),
        "items": classified,
        "summary": _summarize(classified),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"classify: {len(classified)} items -> {args.out}")
    for label, count in payload["summary"].items():
        print(f"  {label}: {count}")
    return 0


def _summarize(items: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        out[item["label"]] = out.get(item["label"], 0) + 1
    return out


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Rodar testes e ver passar**

Run: `py -3.12 -m pytest tests/auditoria_fisica/test_classify.py -v`
Expected: PASS (todos os 9 testes).

- [ ] **Step 5: Rodar classify no inventário real**

```powershell
py -3.12 scripts/auditoria_fisica/classify.py --inventario _AUDITORIA_FISICA/inventario.json --out _AUDITORIA_FISICA/classificacao.json
```

Expected stdout: contagens por rótulo. Espera-se aprox.: `KEEP: 30+`, `ARCHIVE_TO_LEGACY: 3` (3 .bak), `GITIGNORE: 1+`, `MOVE_TO_SCRIPTS: ~9`, `MOVE_TO_SCRIPTS_AD_HOC: ~6`, `NEEDS_HUMAN_DECISION: ~30+` (CLAUDE.md espalhados).

- [ ] **Step 6: GATE DE APROVAÇÃO HUMANA**

**PARAR e mostrar ao usuário:**
- O `classificacao.json` resumido
- Os 3 batches que serão aplicados (Tasks 3, 4, 5)
- Os itens em `NEEDS_HUMAN_DECISION` (informativos, não serão tocados)

Comando de inspeção:

```powershell
py -3.12 -c "import json; d = json.load(open('_AUDITORIA_FISICA/classificacao.json', encoding='utf-8')); [print(f\"{i['label']:30} {i['path']}\") for i in d['items']]"
```

Aguardar aprovação explícita antes de prosseguir para Task 3.

- [ ] **Step 7: Commit**

```bash
git add scripts/auditoria_fisica/classify.py tests/auditoria_fisica/test_classify.py
git commit -m "feat(auditoria): regras de classificação + classificacao.json"
```

---

### Task 3: Apply — endurecer `.gitignore`

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Verificar `.gitignore` atual**

```powershell
Get-Content .gitignore | Select-String -Pattern "node_modules|\.bak|\.backup"
```

Anotar o que já existe.

- [ ] **Step 2: Append de regras faltantes**

Apenas adicionar regras que **não** existem ainda. Padrão de append:

```
# === auditoria-fisica 2026-05-10 ===
node_modules/
*.bak
*.backup
*.backup-*
*.bak-*
*.bak.*
_AUDITORIA_FISICA/
```

(Justificativa para `_AUDITORIA_FISICA/`: artefatos JSON são derivados, não devem entrar no repo; podem ser regenerados a qualquer momento via sweep+classify.)

- [ ] **Step 3: Verificar que arquivos jurídicos NÃO foram afetados**

```powershell
git check-ignore -v PRODAM_DOCS/profiles.json
git check-ignore -v relatorios/CHANGELOG_SESSAO_2026-04-29_design_brandao_ozores.md
```

Expected: ambos NÃO devem retornar match (saída vazia, exit code 1). Se retornarem match, **REVERTER** o `.gitignore` e abrir issue.

- [ ] **Step 4: Rodar testes para garantir CI ainda passa**

```powershell
py -3.12 -m pytest tests/ -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .gitignore
git commit -m "chore(gitignore): endurecer regras (node_modules, *.bak, _AUDITORIA_FISICA)"
```

---

### Task 4: Apply — relocar `.bak` da raiz para `_BACKUPS/relocados-AAAA-MM-DD/`

**Files:**
- Move: `.gitignore.backup-20260423-153153` → `_BACKUPS/relocados-2026-05-10/.gitignore.backup-20260423-153153`
- Move: `.mcp.json.bak-20260508-234719` → `_BACKUPS/relocados-2026-05-10/.mcp.json.bak-20260508-234719`
- Move: `CLAUDE.md.bak.20260510_022119` → `_BACKUPS/relocados-2026-05-10/CLAUDE.md.bak.20260510_022119`

- [ ] **Step 1: Criar diretório de destino**

```powershell
$dest = "_BACKUPS/relocados-2026-05-10"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
```

- [ ] **Step 2: Confirmar que os 3 arquivos são untracked (não tracked no git)**

```powershell
git ls-files --error-unmatch .gitignore.backup-20260423-153153 2>$null
git ls-files --error-unmatch .mcp.json.bak-20260508-234719 2>$null
git ls-files --error-unmatch CLAUDE.md.bak.20260510_022119 2>$null
```

Expected: cada comando retorna não-zero (untracked). Se algum estiver tracked, usar `git mv` em vez de `Move-Item`.

- [ ] **Step 3: Mover via PowerShell (untracked) ou git mv (tracked)**

```powershell
$dest = "_BACKUPS/relocados-2026-05-10"
Move-Item -Path ".gitignore.backup-20260423-153153" -Destination $dest -Force
Move-Item -Path ".mcp.json.bak-20260508-234719" -Destination $dest -Force
Move-Item -Path "CLAUDE.md.bak.20260510_022119" -Destination $dest -Force
```

- [ ] **Step 4: Verificar que os arquivos não estão mais na raiz**

```powershell
Get-ChildItem -File | Where-Object { $_.Name -match "\.bak" } | Format-Table Name
```

Expected: vazio. Se aparecer algum, abortar.

- [ ] **Step 5: Verificar que estão no destino**

```powershell
Get-ChildItem "_BACKUPS/relocados-2026-05-10" | Format-Table Name
```

Expected: 3 arquivos listados.

- [ ] **Step 6: Não há commit aqui (arquivos eram untracked e `_BACKUPS/` continua untracked)**

Anotar em `_AUDITORIA_FISICA/RELATORIO.md` (Task 6) que os 3 arquivos foram relocados.

---

### Task 5: Apply — consolidar scripts `.py` soltos da raiz

**Files:**
- Move (canonical): `gera_notificacao_ses_script.py`, `gerar_dashboard.py`, `gerar_relatorio_docx.py`, `notificacao_simples.py`, `aplicar_renomeacao_inplace.py`, `baixar_lacunas_spcf.py`, `inventario_detran_externo.py`, `ocr_lote_sem_texto_externo.py`, `sincronizar_referencias.py`, `sincronizar_referencias_v2.py`, `insights_pasta_mae.py` → `scripts/`
- Move (ad hoc): `analisar_indefinidos.py`, `classificar_e_renomear_por_conteudo.py`, `limpar_suspeitos.py`, `profile_pasta_mae.py`, `reclassificar_por_path.py`, `triar_suspeitos.py` → `scripts/ad_hoc/`

**Risco:** se algum script faz import com path relativo à raiz, o move quebra o import. Mitigação: `git grep` antes do mv.

- [ ] **Step 1: Caçar imports dependentes na raiz dos scripts a mover**

```powershell
$scripts = @(
  "analisar_indefinidos","aplicar_renomeacao_inplace","baixar_lacunas_spcf",
  "classificar_e_renomear_por_conteudo","gera_notificacao_ses_script","gerar_dashboard",
  "gerar_relatorio_docx","insights_pasta_mae","inventario_detran_externo","limpar_suspeitos",
  "notificacao_simples","ocr_lote_sem_texto_externo","profile_pasta_mae","reclassificar_por_path",
  "sincronizar_referencias","sincronizar_referencias_v2","triar_suspeitos"
)
foreach ($s in $scripts) {
  Write-Output "=== imports de $s ==="
  git grep -n "from $s|import $s" -- "*.py" 2>$null
}
```

Expected: vazio. Se algum hit aparecer, anotar e mover **manualmente** (atualizar import OU pular o move desse script).

- [ ] **Step 2: Determinar tracked vs untracked para cada script**

```powershell
$scripts | ForEach-Object {
  $tracked = git ls-files --error-unmatch "$_.py" 2>$null
  if ($LASTEXITCODE -eq 0) { Write-Output "TRACKED:   $_.py" }
  else { Write-Output "UNTRACKED: $_.py" }
}
```

- [ ] **Step 3: Mover scripts canônicos para `scripts/`**

Usar `git mv` para tracked, `Move-Item` para untracked. Exemplo:

```powershell
$canonical = @(
  "gera_notificacao_ses_script.py","gerar_dashboard.py","gerar_relatorio_docx.py",
  "notificacao_simples.py","aplicar_renomeacao_inplace.py","baixar_lacunas_spcf.py",
  "inventario_detran_externo.py","ocr_lote_sem_texto_externo.py",
  "sincronizar_referencias.py","sincronizar_referencias_v2.py","insights_pasta_mae.py"
)
foreach ($f in $canonical) {
  if (-not (Test-Path $f)) { continue }
  git ls-files --error-unmatch $f *>$null
  if ($LASTEXITCODE -eq 0) { git mv $f "scripts/$f" }
  else { Move-Item $f "scripts/$f" -Force }
}
```

- [ ] **Step 4: Mover scripts ad-hoc para `scripts/ad_hoc/`**

```powershell
$adhoc = @(
  "analisar_indefinidos.py","classificar_e_renomear_por_conteudo.py","limpar_suspeitos.py",
  "profile_pasta_mae.py","reclassificar_por_path.py","triar_suspeitos.py"
)
foreach ($f in $adhoc) {
  if (-not (Test-Path $f)) { continue }
  git ls-files --error-unmatch $f *>$null
  if ($LASTEXITCODE -eq 0) { git mv $f "scripts/ad_hoc/$f" }
  else { Move-Item $f "scripts/ad_hoc/$f" -Force }
}
```

- [ ] **Step 5: Verificar que a raiz não tem mais `.py` solto**

```powershell
Get-ChildItem -File -Filter "*.py" | Format-Table Name
```

Expected: vazio (ou só `auto_update_claude_md.py` se for o caso — verificar; CLAUDE.md o lista em `scripts/`).

- [ ] **Step 6: Rodar testes**

```powershell
py -3.12 -m pytest tests/ -v
```

Expected: PASS.

- [ ] **Step 7: Commit (somente se algo foi tracked-moved)**

```bash
git add scripts/ scripts/ad_hoc/
git commit -m "chore(scripts): consolidar 17 scripts .py soltos da raiz em scripts/ e scripts/ad_hoc/"
```

---

### Task 6: Relatório executivo + selo final

**Files:**
- Create: `_AUDITORIA_FISICA/RELATORIO.md`

- [ ] **Step 1: Gerar relatório consolidado**

`_AUDITORIA_FISICA/RELATORIO.md`:

```markdown
# Auditoria Física PROJETO_PRODAM — Relatório

**Data:** 2026-05-10
**Branch:** main
**Commit base:** (ver `_AUDITORIA_FISICA/baseline_head.txt`)

## Sumário
- **Sweep:** N items inventariados
- **Classificação:** ver `_AUDITORIA_FISICA/classificacao.json`
- **Limpezas aplicadas:** 3 batches (gitignore, .bak relocados, scripts consolidados)

## Limpezas aplicadas

### Batch 1 — `.gitignore` endurecido
- Adicionadas regras: `node_modules/`, `*.bak`, `*.backup`, `*.backup-*`, `*.bak-*`, `*.bak.*`, `_AUDITORIA_FISICA/`
- Commit: <hash>

### Batch 2 — `.bak` da raiz relocados para `_BACKUPS/relocados-2026-05-10/`
- 3 arquivos (todos untracked, sem commit)
- ✅ Originais preservados, nenhum apagado.

### Batch 3 — 17 scripts `.py` soltos consolidados
- Canônicos → `scripts/` (11)
- Ad-hoc → `scripts/ad_hoc/` (6)
- Commit: <hash>

## Itens deixados para sessão futura (`NEEDS_HUMAN_DECISION`)
- 30 `CLAUDE.md` espalhados (política unificada)
- Triplicação `DOSSIES/`, `DOSSIES_MULTIFORMATO/`, `DOCUMENTOS_GERADOS/`
- Pastas legadas (`_ARQUIVO_*`, `_legado`, `_QUESTOES_CRITICAS`, etc.) — manter ou consolidar em `_ARCHIVE/<data>/`
- Untracked massivo em git status (decidir: gitignore vs commit vs delete)

## Reversibilidade
- `.gitignore`: `git restore .gitignore`
- `.bak` relocados: `Move-Item _BACKUPS/relocados-2026-05-10/* .`
- Scripts consolidados: `git revert <hash>` ou `git mv` reverso

## Próximos passos sugeridos
1. Revisar `NEEDS_HUMAN_DECISION` em sessão dedicada.
2. Resolver triplicação `DOSSIES*`/`DOCUMENTOS_GERADOS`.
3. Política para `CLAUDE.md` espalhados.
4. Decidir se `OCR_PESQUISAVEL_CONSOLIDADO/`, `SPCF_EXTRACAO/`, `DETRAN_AUDITORIA_COMPLETA/` devem sair do repo (LFS ou external storage).
```

- [ ] **Step 2: Preencher hashes reais e contagens reais**

Substituir `<hash>` pelos commits reais (`git log --oneline -5`) e `N items` pela contagem do `inventario.json`.

- [ ] **Step 3: Não commitar o relatório** (está em `_AUDITORIA_FISICA/` que agora é gitignored)

Apenas confirmar que o relatório existe:

```powershell
Test-Path _AUDITORIA_FISICA/RELATORIO.md
```

Expected: `True`.

- [ ] **Step 4: Verificação final**

```powershell
git status --short
```

Expected: tree limpo das mudanças desta sessão (somente untracked pré-existentes ou `_AUDITORIA_FISICA/` ignorado).

```powershell
git log --oneline -5
```

Expected: ver os 3-4 commits desta sessão (`scaffold`, `sweep`, `classify`, `gitignore`, `consolidar scripts`).

---

## Checklist de Self-Review (executor faz ao final)

- [ ] **Spec coverage:** todas as 3 limpezas seguras prometidas (gitignore, relocate-baks, move-scripts) têm task dedicada? ✅
- [ ] **Placeholder scan:** nenhum "TBD"/"TODO"/"implement later" no plano? ✅
- [ ] **Type consistency:** o nome do campo `label` é o mesmo em `classify.py`, nos testes e no consumo? ✅
- [ ] **Reversibilidade:** cada Task tem mecanismo de undo descrito? ✅
- [ ] **Gate humano em Task 2 Step 6:** sim, parada explícita antes das aplicações.
- [ ] **Escopo respeitado:** zero mutação automática em `PRODAM_DOCS/`, `OCR_*`, `SPCF_*`, `DETRAN_AUDITORIA_COMPLETA/`, `relatorios/`, `DOSSIES*`, `DOCUMENTOS_GERADOS/`, `profiles.json`, `prodam.db`. ✅

---

## Execução

Após aprovar este plano, escolher modo de execução:

1. **Subagent-Driven (recomendado)** — dispatch de subagent fresh por task, review entre tasks.
2. **Inline Execution** — executar tasks nesta sessão, com checkpoint humano em Task 2 Step 6 (gate de aprovação dos batches).

Qual modo?
