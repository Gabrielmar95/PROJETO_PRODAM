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
