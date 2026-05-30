#!/usr/bin/env python3
"""PreCompact hook — snapshot factual da sessao em .remember/remember.md.

Roda ANTES de cada /compact (manual ou auto). Como hooks PreCompact so aceitam
`type: command` (nao `prompt`/`agent`), este script NAO "raciocina" um handoff —
ele captura o ESQUELETO FACTUAL que a proxima sessao (ou o /compact) usa para se
reorientar:

  - estado git (branch, ahead/behind, ultimos commits, working tree)
  - issues abertas em _QUESTOES_CRITICAS/
  - as ultimas mensagens do assistant no transcript (texto literal, sem LLM)

A camada semantica (decisoes, proximos passos, constraints) continua sendo
reconstruida por quem ler este arquivo + o transcript. Honestamente: e' um
"snapshot automatico", nao um handoff inteligente.

Invariantes (espelham .claude/hooks/session-start.sh):
  - SEMPRE sai 0. Um hook nunca pode derrubar/atrasar a sessao nem abortar o /compact.
  - Defensivo em tudo: cada coleta e' guardada; falha vira "?" em vez de excecao.
  - Multiplataforma: usa sys.executable e subprocess; sem dependencia de shell.
  - Sem libs externas (so stdlib) — roda igual no Windows (py -3.12) e cloud (python3).

Contrato de entrada (stdin JSON do PreCompact):
  { "session_id", "transcript_path", "cwd"?, "trigger": "manual"|"auto",
    "custom_instructions"? }

Caveat supply-chain: este hook e' commitado; quem tem push controla o que roda no
/compact. Mantenha minimo, legivel, revisado.
"""
from __future__ import annotations

import datetime as _dt
import json
import subprocess
import sys
from pathlib import Path

# Quantas das ultimas mensagens do assistant preservar no snapshot.
_TAIL_ASSISTANT_MSGS = 6
# Teto de caracteres por mensagem preservada (evita arquivo gigante).
_MSG_CHAR_CAP = 1200


def _read_stdin_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _git(args: list[str], cwd: Path) -> str:
    """Roda um comando git read-only; devolve stdout strip ou '?' em falha."""
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return out.stdout.strip() if out.returncode == 0 else "?"
    except Exception:
        return "?"


def _git_state(cwd: Path) -> dict:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    ab = _git(["rev-list", "--left-right", "--count", "origin/main...HEAD"], cwd)
    ab = ab.replace("\t", "/") if ab != "?" else "?/?"
    commits = _git(["log", "-5", "--oneline"], cwd)
    status = _git(["status", "--short"], cwd)
    return {
        "branch": branch,
        "ahead_behind": ab,  # formato: behind/ahead vs origin/main
        "commits": commits,
        "status": status if status else "(working tree limpa)",
    }


def _open_issues(cwd: Path) -> list[str]:
    try:
        d = cwd / "_QUESTOES_CRITICAS"
        if not d.is_dir():
            return []
        # NN_*.md numerados (mesmo criterio do session-start.sh: [0-9]*.md)
        names = sorted(p.name for p in d.glob("[0-9]*.md"))
        return names
    except Exception:
        return []


def _content_to_text(content) -> str:
    """Extrai texto de .message.content (string OU lista de blocos)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(p for p in parts if p)
    return ""


def _tail_assistant_messages(transcript_path: str) -> list[str]:
    """Le o .jsonl e devolve as ultimas N mensagens de texto do assistant."""
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return []
        texts: list[str] = []
        with p.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("type") != "assistant":
                    continue
                msg = rec.get("message") or {}
                txt = _content_to_text(msg.get("content")).strip()
                if txt:
                    texts.append(txt)
        tail = texts[-_TAIL_ASSISTANT_MSGS:]
        # cap por mensagem
        capped = []
        for t in tail:
            if len(t) > _MSG_CHAR_CAP:
                t = t[:_MSG_CHAR_CAP].rstrip() + " […truncado]"
            capped.append(t)
        return capped
    except Exception:
        return []


def _render(payload: dict, cwd: Path) -> str:
    now = _dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    trigger = payload.get("trigger", "?")
    session_id = payload.get("session_id", "?")
    custom = (payload.get("custom_instructions") or "").strip()
    git = _git_state(cwd)
    issues = _open_issues(cwd)
    msgs = _tail_assistant_messages(payload.get("transcript_path", ""))

    lines: list[str] = []
    lines.append("# .remember — snapshot automatico pre-/compact")
    lines.append("")
    lines.append("> ⚙️ Gerado pelo hook PreCompact `.claude/hooks/precompact-handoff.py`.")
    lines.append("> NAO e' handoff curado — e' o esqueleto factual. Releia + o transcript.")
    lines.append("> Sobrescrito a cada /compact; nao versionado (`.gitignore`).")
    lines.append("")
    lines.append(f"- **Gerado em:** {now}")
    lines.append(f"- **Trigger:** {trigger} (manual = voce pediu /compact; auto = janela cheia)")
    lines.append(f"- **Session:** `{session_id}`")
    if custom:
        lines.append(f"- **Instrucoes do /compact manual:** {custom}")
    lines.append("")
    lines.append("## Estado git")
    lines.append("")
    lines.append(f"- **Branch:** `{git['branch']}`")
    lines.append(f"- **behind/ahead vs origin/main:** `{git['ahead_behind']}`")
    lines.append("- **Ultimos 5 commits:**")
    lines.append("```")
    lines.append(git["commits"])
    lines.append("```")
    lines.append("- **Working tree:**")
    lines.append("```")
    lines.append(git["status"])
    lines.append("```")
    lines.append("")
    lines.append(f"## Issues abertas em _QUESTOES_CRITICAS/ ({len(issues)})")
    lines.append("")
    if issues:
        for n in issues:
            lines.append(f"- {n}")
    else:
        lines.append("- (nenhuma encontrada)")
    lines.append("")
    lines.append(f"## Ultimas {len(msgs)} mensagens do assistant (texto literal)")
    lines.append("")
    if msgs:
        for i, t in enumerate(msgs, 1):
            lines.append(f"### [-{len(msgs) - i + 1}]")
            lines.append("")
            lines.append(t)
            lines.append("")
    else:
        lines.append("- (transcript indisponivel ou sem mensagens de texto)")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    payload = _read_stdin_payload()
    # cwd: preferir o do payload; cair pro CLAUDE_PROJECT_DIR; por fim cwd do processo.
    cwd_str = payload.get("cwd") or _env_project_dir() or "."
    cwd = Path(cwd_str)

    try:
        out_dir = cwd / ".remember"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "remember.md"
        out_file.write_text(_render(payload, cwd), encoding="utf-8")
        # systemMessage aparece pro usuario; suppressOutput tira o stdout do transcript.
        print(json.dumps({
            "systemMessage": f"📝 Snapshot pre-compact salvo em .remember/remember.md",
            "suppressOutput": True,
        }))
    except Exception as exc:  # nunca aborta o /compact
        # Mesmo em falha, sai 0 com aviso leve.
        try:
            print(json.dumps({
                "systemMessage": f"[precompact-handoff] aviso: {exc!r}",
                "suppressOutput": True,
            }))
        except Exception:
            pass
    return 0


def _env_project_dir():
    import os
    return os.environ.get("CLAUDE_PROJECT_DIR")


if __name__ == "__main__":
    sys.exit(main())
