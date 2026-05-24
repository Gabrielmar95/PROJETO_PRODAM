"""Dry-run harness para auto_update_claude_md.py — gera preview SEM tocar no CLAUDE.md alvo."""
import sys
from pathlib import Path

BASE = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")
sys.path.insert(0, str(BASE / "scripts"))

import auto_update_claude_md as mod

# Bloqueia escrita acidental no CLAUDE.md real: redireciona OUTPUT
PREVIEW = BASE / "_QUESTOES_CRITICAS" / "CLAUDE.md.preview-20260511"
mod.OUTPUT = PREVIEW

# Reproduz main() exceto pelo destino
data = mod.load_profiles()
m = mod.compute_metrics(data)
content = mod.generate_claude_md(m)
PREVIEW.write_text(content, encoding="utf-8")

print(f"OK preview gerado em: {PREVIEW}")
print(f"Tamanho: {len(content)} bytes")
print(f"CLAUDE.md alvo NAO foi tocado: {mod.BASE / 'CLAUDE.md'}")
if m["prescricao_urgente"]:
    print(f"Prescricao urgente: {len(m['prescricao_urgente'])} devedor(es)")
