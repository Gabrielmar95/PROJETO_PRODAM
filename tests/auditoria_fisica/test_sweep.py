"""Smoke test: sweep gera JSON com kinds esperados, contra fixture sintética em tmp_path.

A versão anterior rodava sweep contra o repo_root real e dependia da existência de
loose scripts na raiz. Após Task 5 da auditoria física limpar a raiz (commit 99f9ee7),
o teste passou a falhar — a própria limpeza que o sweep deveria detectar tornava o
teste self-defeating. Agora o teste constrói uma estrutura controlada em tmp_path.
"""
import json
import subprocess
import sys
from pathlib import Path

SWEEP_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts" / "auditoria_fisica" / "sweep.py"
)


def _build_fake_repo(root: Path) -> dict[str, list[str]]:
    """Planta estrutura sintética e devolve o que foi plantado por kind."""
    # 2 loose root scripts (devem ser detectados)
    (root / "gerar_relatorio.py").write_text("# fixture\n", encoding="utf-8")
    (root / "sincronizar_dados.py").write_text("# fixture\n", encoding="utf-8")

    # 1 .bak na raiz
    (root / "config.json.bak").write_text("{}", encoding="utf-8")

    # 1 CLAUDE.md em subpasta (deve aparecer em scattered_claude_md)
    (root / "subpasta").mkdir()
    (root / "subpasta" / "CLAUDE.md").write_text("# fixture\n", encoding="utf-8")

    # Controle negativo: script DENTRO de scripts/ NÃO deve ser detectado
    # como loose_root_script (sweep só olha root.iterdir() para essa categoria).
    (root / "scripts").mkdir()
    (root / "scripts" / "deve_ser_ignorado.py").write_text("# fixture\n", encoding="utf-8")

    # 1 pasta legacy (sanity: estrutura de pastas legadas é reconhecida)
    (root / "_ARQUIVO_FIXTURE").mkdir()

    return {
        "loose_root_script": ["gerar_relatorio.py", "sincronizar_dados.py"],
        "root_bak_file": ["config.json.bak"],
        "scattered_claude_md": ["subpasta/CLAUDE.md"],
        "legacy_top_dir": ["_ARQUIVO_FIXTURE"],
        "negative_control_loose": "scripts/deve_ser_ignorado.py",
    }


def _by_kind(items: list[dict]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for item in items:
        out.setdefault(item["kind"], []).append(item["path"])
    return out


def test_sweep_produces_inventario_with_required_keys(tmp_path):
    fake_repo = tmp_path / "fake_repo"
    fake_repo.mkdir()
    expected = _build_fake_repo(fake_repo)

    out_path = tmp_path / "inventario.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SWEEP_SCRIPT),
            "--root",
            str(fake_repo),
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

    by_kind = _by_kind(data["items"])

    # loose_root_script: contagem e nomes exatos batem com o plantado
    loose = sorted(by_kind.get("loose_root_script", []))
    assert len(loose) == 2
    assert loose == sorted(expected["loose_root_script"])

    # Controle negativo: script dentro de scripts/ NÃO deve aparecer como loose
    assert expected["negative_control_loose"] not in loose
    assert "deve_ser_ignorado.py" not in loose

    # root_bak_file: 1 arquivo, nome bate
    assert by_kind.get("root_bak_file", []) == expected["root_bak_file"]

    # scattered_claude_md: 1 ocorrência, path bate
    assert by_kind.get("scattered_claude_md", []) == expected["scattered_claude_md"]

    # legacy_top_dir: 1 pasta, nome bate
    assert by_kind.get("legacy_top_dir", []) == expected["legacy_top_dir"]
