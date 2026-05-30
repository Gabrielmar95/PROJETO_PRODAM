#!/usr/bin/env bash
# SessionStart hook — SOMENTE em sessoes remotas (Claude Code na web).
#
# O que faz (so no cloud): instala as dev-deps para que pytest/ruff funcionem e
# injeta um banner de contexto (branch, issues abertas, risco de prescricao).
#
# Invariantes de seguranca:
#   - SEMPRE termina com exit 0: um hook nunca pode derrubar/atrasar a sessao.
#   - SEM `set -e`: `alerta_prescricao.py --check` sai 1 quando ha alerta (esperado);
#     toda chamada de script do projeto e' guardada (|| ... / 2>/dev/null).
#   - No-op instantaneo fora do cloud (gate $CLAUDE_CODE_REMOTE na 1a linha) — assim
#     nao gera ruido nas sessoes LOCAIS (Windows/PowerShell, dev primario do projeto).
#
# Caveat de supply-chain: este hook e' commitado; quem tem push no repo controla o
# comando que roda no boot da sessao. Mantenha-o minimo, legivel e revisado.
set -uo pipefail

# Gate remoto: idioma oficial do Claude Code na web. No-op em qualquer outro ambiente.
[ "${CLAUDE_CODE_REMOTE:-}" != "true" ] && exit 0

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

# --- Acao critica: instalar deps de teste (best-effort, nunca aborta) ---
# Pula se pytest ja importavel (resume/clear ficam instantaneos); so instala em
# container novo. --timeout limita espera sob politica de rede restrita.
if ! python3 -c "import pytest" >/dev/null 2>&1; then
  python3 -m pip install -q --disable-pip-version-check --timeout 60 -r requirements-dev.txt \
    >/tmp/prodam_pip.log 2>&1 \
    || echo "[session-start] pip install com avisos (ver /tmp/prodam_pip.log)" >&2
fi

# --- Banner best-effort (cada sub-comando guardado) ---
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
AB="$(git rev-list --left-right --count origin/main...HEAD 2>/dev/null | tr '\t' '/' || echo '?/?')"
PRESC="$(python3 scripts/alerta_prescricao.py --check 2>/dev/null; echo "exit $?")"
ISSUES="$(ls _QUESTOES_CRITICAS/[0-9]*.md 2>/dev/null | wc -l | tr -d ' ')"

BANNER="PRODAM cloud pronta. Branch ${BRANCH} | ahead/behind origin/main: ${AB}
Issues abertas (arquivos): ${ISSUES} em _QUESTOES_CRITICAS/ | prescricao --check: ${PRESC}
PRODAM_DOCS/prodam.db AUSENTE no cloud; artefato juridico exige gate manual.
Testes on-demand: python3 -m pytest tests/ -q"

# Injeta no contexto via o contrato documentado do SessionStart (additionalContext).
python3 - "$BANNER" <<'PY'
import json, sys
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": sys.argv[1],
    }
}))
PY

exit 0
