"""
Analisa drift entre scripts duplicados no projeto PRODAM.

Estratégia:
1. Procura scripts com o mesmo basename em múltiplas pastas (fora de _legado, _archive,
   _CONSOLIDADO, _DOSSIE).
2. Para cada grupo de duplicatas, compara md5, mtime, tamanho e número de linhas.
3. Identifica canonical (mais recente + maior) e classifica divergências:
   - IDENTICOS        → mesmos bytes (md5 igual) → deduplicar deletando cópias
   - DRIFT_LEVE       → diferença < 20% de linhas → merge manual
   - DRIFT_GRAVE      → diferença ≥ 20% de linhas → análise caso-a-caso
   - VERSIONADO       → sufixos v2/v3/v4 → arquivar versões antigas

Gera:
  - drift_scripts.json
  - drift_scripts.csv
  - 02_DRIFT_SCRIPTS.md
  - consolidar_scripts.ps1
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE = Path("/sessions/gallant-focused-brahmagupta/mnt/PROJETO_PRODAM")
OUT = Path("/sessions/gallant-focused-brahmagupta/mnt/outputs/_QUESTOES_CRITICAS")
OUT.mkdir(parents=True, exist_ok=True)

# Pastas que devem ser IGNORADAS (arquivo morto ou dados de devedor)
IGNORAR = {"_legado", "_archive", "_ARQUIVO_ORFA", "DETRAN_AUDITORIA"}
SUFFIX_IGNORAR = ("_CONSOLIDADO", "_DOSSIE")


def deve_ignorar(p: Path) -> bool:
    partes = p.parts
    for parte in partes:
        if parte in IGNORAR:
            return True
        for suf in SUFFIX_IGNORAR:
            if parte.endswith(suf):
                return True
    return False


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# --- 1. Coletar todos .py relevantes ---
scripts = []
for p in BASE.rglob("*.py"):
    if deve_ignorar(p):
        continue
    try:
        st = p.stat()
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            linhas = sum(1 for _ in f)
        scripts.append({
            "path": str(p),
            "rel": str(p.relative_to(BASE)),
            "basename": p.name,
            "size": st.st_size,
            "mtime": st.st_mtime,
            "mtime_iso": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            "lines": linhas,
            "md5": md5(p),
        })
    except (OSError, UnicodeDecodeError):
        continue

# --- 2. Agrupar por basename ---
grupos = defaultdict(list)
for s in scripts:
    grupos[s["basename"]].append(s)

# só drift se houver 2+
grupos = {k: v for k, v in grupos.items() if len(v) >= 2}


# --- 3. Classificar cada grupo ---
def classificar_grupo(versoes: list[dict]) -> dict:
    versoes = sorted(versoes, key=lambda x: x["mtime"], reverse=True)
    canonical = versoes[0]
    md5s = {v["md5"] for v in versoes}
    if len(md5s) == 1:
        tipo = "IDENTICOS"
    else:
        # calcular spread de linhas
        lmin = min(v["lines"] for v in versoes)
        lmax = max(v["lines"] for v in versoes)
        spread_pct = (lmax - lmin) / max(lmax, 1) * 100
        if spread_pct < 20:
            tipo = "DRIFT_LEVE"
        else:
            tipo = "DRIFT_GRAVE"
    return {
        "tipo": tipo,
        "canonical": canonical["rel"],
        "canonical_mtime": canonical["mtime_iso"],
        "versoes": versoes,
        "n_versoes": len(versoes),
    }


grupos_class = {k: classificar_grupo(v) for k, v in grupos.items()}

# --- 4. Estatísticas ---
stats = {
    "total_scripts_analisados": len(scripts),
    "grupos_duplicados": len(grupos),
    "por_tipo": {},
    "scripts_criticos_duplicados": [],  # os que aparecem no CLAUDE.md
}
for g in grupos_class.values():
    stats["por_tipo"][g["tipo"]] = stats["por_tipo"].get(g["tipo"], 0) + 1

# scripts listados no CLAUDE.md como canônicos
SCRIPTS_CLAUDE_MD = {
    "prodam_utils.py", "orgao_pipeline_completa.py", "sincronizar_prodam.py",
    "atualizar_db.py", "auditoria_completude_devedor.py",
    "dossie_multiformato_devedor.py", "reconciliar_orfaos_reversos.py",
    "consultas.py", "auto_update_claude_md.py",
}
for basename, info in grupos_class.items():
    if basename in SCRIPTS_CLAUDE_MD:
        stats["scripts_criticos_duplicados"].append({
            "nome": basename,
            "tipo": info["tipo"],
            "locais": [v["rel"] for v in info["versoes"]],
            "canonical": info["canonical"],
        })

# --- 5. JSON ---
payload = {
    "gerado_em": datetime.now().isoformat(timespec="seconds"),
    "estatisticas": stats,
    "grupos": grupos_class,
}
(OUT / "drift_scripts.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
)

# --- 6. CSV ---
linhas = ["basename;tipo;n_versoes;canonical;canonical_mtime;locais"]
for basename, info in sorted(grupos_class.items()):
    locais = "|".join(v["rel"] for v in info["versoes"])
    linhas.append(
        f'{basename};{info["tipo"]};{info["n_versoes"]};{info["canonical"]};'
        f'{info["canonical_mtime"]};"{locais}"'
    )
(OUT / "drift_scripts.csv").write_text("\n".join(linhas), encoding="utf-8")

# --- 7. Markdown ---
md = []
md.append("# Drift entre Scripts Duplicados — Diagnóstico\n")
md.append(f"_Gerado em {payload['gerado_em']}_\n")
md.append("## Visão geral\n")
md.append(f"- **Total de scripts `.py` analisados:** {stats['total_scripts_analisados']}")
md.append(f"- **Nomes duplicados (≥2 cópias):** {stats['grupos_duplicados']}")
md.append("")
md.append("### Distribuição por tipo de drift\n")
for tipo, n in sorted(stats["por_tipo"].items()):
    md.append(f"- **{tipo}**: {n} grupos")
md.append("")

md.append("## Por que isso importa\n")
md.append("Imagine que você tem três cópias do mesmo contrato em pastas diferentes. "
          "Se um cliente te pedir para corrigir uma cláusula e você alterar só uma das cópias, "
          "na próxima reunião alguém pode abrir outra e achar que você não fez o trabalho. "
          "É exatamente isso que acontece quando o mesmo script existe em vários lugares.\n")
md.append("- **IDENTICOS**: cópias idênticas — seguro deletar as duplicatas.")
md.append("- **DRIFT_LEVE**: diferenças pequenas (<20% de linhas) — provavelmente correções não propagadas.")
md.append("- **DRIFT_GRAVE**: diferenças grandes (≥20%) — são scripts diferentes que por coincidência têm o mesmo nome. Precisam renomear.\n")

# Scripts críticos primeiro
if stats["scripts_criticos_duplicados"]:
    md.append("## ⚠️ Scripts CRÍTICOS com duplicação\n")
    md.append("Estes scripts estão listados no `CLAUDE.md` como canônicos do projeto. "
              "Duplicação aqui é alto risco.\n")
    md.append("| Script | Tipo | Nº cópias | Canonical (mais recente) |")
    md.append("|--------|------|-----------|--------------------------|")
    for c in stats["scripts_criticos_duplicados"]:
        md.append(f"| `{c['nome']}` | {c['tipo']} | {len(c['locais'])} | `{c['canonical']}` |")
    md.append("")
    for c in stats["scripts_criticos_duplicados"]:
        md.append(f"### `{c['nome']}`\n")
        for local in c["locais"]:
            marca = " ← canonical" if local == c["canonical"] else ""
            md.append(f"- `{local}`{marca}")
        md.append("")

md.append("## Tabela completa de grupos\n")
md.append("| Script | Tipo | Cópias | Canonical |")
md.append("|--------|------|--------|-----------|")
for basename, info in sorted(grupos_class.items()):
    md.append(f"| `{basename}` | {info['tipo']} | {info['n_versoes']} | `{info['canonical']}` |")
md.append("")

md.append("## Próximos passos\n")
md.append("1. Revisar este relatório e `drift_scripts.csv`.")
md.append("2. Rodar `consolidar_scripts.ps1` (ele pergunta antes de cada ação).")
md.append("3. Para cada `IDENTICOS`, o script deleta as cópias e mantém só o canonical.")
md.append("4. Para cada `DRIFT_LEVE`/`DRIFT_GRAVE`, o script ARQUIVA as versões antigas "
          "em `_ARQUIVO_DRIFT/` — você depois abre o canonical e merge manual se necessário.")
md.append("5. Ao final, atualizar `CLAUDE.md` para apontar unicamente ao canonical.\n")

(OUT / "02_DRIFT_SCRIPTS.md").write_text("\n".join(md), encoding="utf-8")

# --- 8. PowerShell de consolidação ---
ps = []
ps.append("# ================================================================")
ps.append("# CONSOLIDACAO DE SCRIPTS DUPLICADOS - PROJETO PRODAM")
ps.append(f"# Gerado em: {payload['gerado_em']}")
ps.append("# ================================================================")
ps.append("# Estrategia:")
ps.append("#   IDENTICOS  -> deleta copias, mantem canonical")
ps.append("#   DRIFT_LEVE -> arquiva copias antigas em _ARQUIVO_DRIFT")
ps.append("#   DRIFT_GRAVE -> arquiva copias antigas, AVISA p/ revisao manual")
ps.append("# Cada acao pede confirmacao.")
ps.append("# ================================================================")
ps.append("")
ps.append("$ErrorActionPreference = 'Stop'")
ps.append("$BASE = 'C:\\Users\\gabri\\Desktop\\PROJETO_PRODAM'")
ps.append("$ARQUIVO_DRIFT = Join-Path $BASE '_ARQUIVO_DRIFT'")
ps.append("")
ps.append("function Confirmar($msg) {")
ps.append("    $r = Read-Host \"$msg [s/N]\"")
ps.append("    return $r -eq 's' -or $r -eq 'S'")
ps.append("}")
ps.append("")
ps.append("New-Item -ItemType Directory -Path $ARQUIVO_DRIFT -Force | Out-Null")
ps.append("")
ps.append("$total_deletados = 0")
ps.append("$total_arquivados = 0")
ps.append("")

for basename, info in sorted(grupos_class.items()):
    canonical = info["canonical"].replace("/", "\\")
    copias = [v["rel"].replace("/", "\\") for v in info["versoes"] if v["rel"] != info["canonical"]]
    ps.append(f"# ===== {basename} ({info['tipo']}, {info['n_versoes']} copias) =====")
    ps.append(f"# Canonical: {canonical}")
    if info["tipo"] == "IDENTICOS":
        ps.append(f"if (Confirmar 'DELETAR {len(copias)} copia(s) identica(s) de {basename}?') {{")
        for copia in copias:
            ps.append(f"    Remove-Item (Join-Path $BASE '{copia}') -Force")
            ps.append(f"    Write-Host '  deletado: {copia}' -ForegroundColor Yellow")
            ps.append(f"    $total_deletados++")
        ps.append("}")
    else:
        # DRIFT — arquivar
        ps.append(f"if (Confirmar 'ARQUIVAR {len(copias)} copia(s) com drift de {basename} em _ARQUIVO_DRIFT?') {{")
        for copia in copias:
            # slug para arquivo
            slug = copia.replace("\\", "_").replace("/", "_")
            ps.append(f"    Move-Item (Join-Path $BASE '{copia}') (Join-Path $ARQUIVO_DRIFT '{slug}') -Force")
            ps.append(f"    Write-Host '  arquivado: {copia}' -ForegroundColor Cyan")
            ps.append(f"    $total_arquivados++")
        if info["tipo"] == "DRIFT_GRAVE":
            ps.append(f"    Write-Warning 'DRIFT_GRAVE em {basename}: revisar manualmente o canonical.'")
        ps.append("}")
    ps.append("")

ps.append("Write-Host ''")
ps.append("Write-Host \"[OK] Deletados: $total_deletados | Arquivados: $total_arquivados\" -ForegroundColor Green")
ps.append("Write-Host 'Rode: py -3.12 sincronizar_prodam.py para validar.' -ForegroundColor Cyan")

(OUT / "consolidar_scripts.ps1").write_text("\n".join(ps), encoding="utf-8-sig")

print("=" * 60)
print("DRIFT DE SCRIPTS — CONCLUIDO")
print("=" * 60)
print(f"Scripts analisados: {stats['total_scripts_analisados']}")
print(f"Grupos duplicados:  {stats['grupos_duplicados']}")
print(f"Por tipo: {stats['por_tipo']}")
print(f"Criticos (CLAUDE.md): {len(stats['scripts_criticos_duplicados'])}")
for c in stats["scripts_criticos_duplicados"]:
    print(f"  - {c['nome']} ({c['tipo']}, {len(c['locais'])} copias)")
print(f"\nArquivos gerados em: {OUT}")
for f in sorted(OUT.iterdir()):
    print(f"  {f.name:<35} ({f.stat().st_size:>8,} bytes)")
