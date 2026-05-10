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
