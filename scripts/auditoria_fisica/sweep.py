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
