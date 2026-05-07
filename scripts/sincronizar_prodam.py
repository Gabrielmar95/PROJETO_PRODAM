"""
sincronizar_prodam.py — COMANDO MESTRE de sincronização do Projeto PRODAM.

Executa em sequência:
  1. Rebuild prodam.db via atualizar_db.py
  2. Auditoria de completude por devedor (gaps + divergências)
  3. Dossiê multi-formato por devedor (.md, .html, .xlsx, .csv, .json)
  4. Validação de skills com paths hardcoded desatualizados
  5. Atualiza CLAUDE.md (se auto_update_claude_md.py existir)

Uso:
  py -3.12 sincronizar_prodam.py              # tudo
  py -3.12 sincronizar_prodam.py --so-db      # só etapa 1
  py -3.12 sincronizar_prodam.py --so-audit   # só etapa 2
  py -3.12 sincronizar_prodam.py --so-dossie  # só etapa 3
  py -3.12 sincronizar_prodam.py --pular-dossie  # tudo exceto etapa 3 (lenta)
"""
from __future__ import annotations
import subprocess, sys, argparse, re
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent  # fix 2026-04-22: scripts agora vivem em scripts/

ETAPAS = {
    "db":       ("atualizar_db.py",                 "Rebuild prodam.db"),
    "audit":    ("auditoria_completude_devedor.py", "Auditoria de completude"),
    "dossie":   ("dossie_multiformato_devedor.py",  "Dossiês multi-formato"),
    "claude":   ("auto_update_claude_md.py",        "Atualizar CLAUDE.md"),
}

def run_etapa(nome: str, script: str, descr: str, extra_args: list = None) -> bool:
    print(f"\n{'='*70}")
    print(f"  [{nome.upper()}] {descr}")
    print(f"  Script: {script}")
    print(f"{'='*70}")
    # fix 2026-04-22: procura primeiro em scripts/, depois no ROOT (fallback legado)
    path = SCRIPTS_DIR / script
    if not path.exists():
        path = ROOT / script
    if not path.exists():
        print(f"  ⚠️  {script} não encontrado — pulando.")
        return False
    cmd = [sys.executable, str(path)] + (extra_args or [])
    r = subprocess.run(cmd, cwd=str(ROOT))
    sucesso = r.returncode == 0
    print(f"  {'✅ OK' if sucesso else '❌ FALHOU'}")
    return sucesso

def validar_skills_paths() -> list[dict]:
    """Varre skills do projeto procurando paths antigos hardcoded."""
    PADROES_ANTIGOS = [
        r"C:\\Users\\gabri\\Desktop\\PRODAM_DOCS",      # antigo root
        r"C:\\Users\\gabri\\Desktop\\SPCF_EXTRACAO",    # antigo SPCF root
        r"C:\\Users\\gabri\\PRODAM_DOCS",               # antigo clone
        r"C:\\Users\\gabri\\Desktop\\01_PRODAM",        # arquivado
        r"C:\\Users\\gabri\\Desktop\\Prodam_V2_Recuperacao",
        r"C:\\Users\\gabri\\Desktop\\Projeto_PRODAM",
    ]
    issues = []
    skills_dir = ROOT / "PRODAM_DOCS" / "_SKILLS"
    if not skills_dir.exists():
        return []
    for f in skills_dir.rglob("*"):
        if not f.is_file(): continue
        if f.suffix.lower() not in {".md", ".py", ".json", ".txt", ".skill"}:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for padrao in PADROES_ANTIGOS:
            if padrao in content or padrao.replace("\\\\","\\") in content:
                # Contar ocorrências
                matches = [m.start() for m in re.finditer(re.escape(padrao.replace("\\\\","\\")), content)]
                issues.append({
                    "skill": str(f.relative_to(ROOT)),
                    "padrao_antigo": padrao.replace("\\\\","\\"),
                    "ocorrencias": len(matches),
                    "novo_sugerido": padrao.replace("\\\\","\\")
                        .replace("C:\\Users\\gabri\\Desktop", "C:\\Users\\gabri\\Desktop\\PROJETO_PRODAM")
                        .replace("C:\\Users\\gabri\\PRODAM_DOCS",
                                 "C:\\Users\\gabri\\Desktop\\PROJETO_PRODAM\\PRODAM_DOCS")
                })
                break
    return issues

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-db", action="store_true")
    ap.add_argument("--so-audit", action="store_true")
    ap.add_argument("--so-dossie", action="store_true")
    ap.add_argument("--pular-dossie", action="store_true")
    ap.add_argument("--devedor", help="Gera dossiê só do devedor especificado")
    args = ap.parse_args()

    t0 = datetime.now()
    print(f"\n🔄 SINCRONIZAÇÃO PROJETO PRODAM — início {t0:%H:%M:%S}\n")

    resultados = {}

    so_algum = args.so_db or args.so_audit or args.so_dossie

    if args.so_db or not so_algum:
        resultados["db"] = run_etapa("db", *ETAPAS["db"])

    if args.so_audit or (not so_algum):
        resultados["audit"] = run_etapa("audit", *ETAPAS["audit"])

    if args.so_dossie or (not so_algum and not args.pular_dossie):
        extra = ["--devedor", args.devedor] if args.devedor else []
        resultados["dossie"] = run_etapa("dossie", *ETAPAS["dossie"], extra_args=extra)

    if not so_algum:
        resultados["claude"] = run_etapa("claude", *ETAPAS["claude"])

    # Validação de skills sempre
    print(f"\n{'='*70}\n  [SKILLS] Validando paths em skills do projeto\n{'='*70}")
    issues = validar_skills_paths()
    if issues:
        print(f"  ⚠️  {len(issues)} arquivos de skill com paths desatualizados:")
        for i in issues[:10]:
            print(f"     {i['skill']:<50} {i['padrao_antigo']} ({i['ocorrencias']}×)")
        if len(issues) > 10:
            print(f"     ... (+{len(issues)-10} outros)")
        # Salva relatório
        out = ROOT / "SKILLS_PATHS_DESATUALIZADOS.md"
        lines = ["# Skills com paths desatualizados\n\n",
                 f"Gerado em {datetime.now():%Y-%m-%d %H:%M:%S}\n\n",
                 f"**Total: {len(issues)} arquivos**\n\n",
                 "| Skill | Padrão antigo | Ocorrências | Novo sugerido |\n",
                 "|-------|---------------|-------------|----------------|\n"]
        for i in issues:
            lines.append(f"| `{i['skill']}` | `{i['padrao_antigo']}` | {i['ocorrencias']} | `{i['novo_sugerido']}` |\n")
        out.write_text("".join(lines), encoding="utf-8")
        print(f"  📄 Relatório completo: {out.name}")
    else:
        print(f"  ✅ Todos os paths estão atualizados.")


    # Resumo final
    dt = datetime.now() - t0
    print(f"\n{'='*70}")
    print(f"SINCRONIZACAO COMPLETA em {dt.total_seconds():.0f}s")
    print(f"{'='*70}")
    for etapa, ok in resultados.items():
        print(f"  {'[OK]' if ok else '[X]'} {etapa}")
    print(f"\nSkills com paths desatualizados: {len(issues)}")

if __name__ == "__main__":
    main()
