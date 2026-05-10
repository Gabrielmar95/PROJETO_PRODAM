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
