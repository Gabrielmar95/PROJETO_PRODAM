"""
commit_sessao.py — orquestra commits correlacionados em PROJETO_PRODAM + PRODAM_DOCS.

Motivacao: toda feature que toca os dois repos do projeto (scripts/dados em
PROJETO_PRODAM e skills/documentos em PRODAM_DOCS) precisa de commits
correlacionados. Sem cross-link, perde rastreabilidade. Fazer manual e chato
(dois `git add`, dois `git commit`, copiar SHA, editar mensagem).

Este script automatiza:
    1. Lista o que esta staged em cada repo (aborta se vazio nos dois)
    2. Commita em PROJETO_PRODAM primeiro (repo "base", onde ficam os scripts
       que a skill documenta)
    3. Le o SHA do commit recem-criado
    4. Commita em PRODAM_DOCS com cross-ref automatica: o corpo da mensagem
       inclui "Ver tambem: PROJETO_PRODAM@<SHA>"
    5. Imprime ambos SHAs + lembrete de push manual

Nao faz:
    - git add (voce controla o que vai no commit)
    - git push (pela regra de seguranca do projeto, push e manual)
    - alteracoes destrutivas (amend, rebase, reset)

Uso:
    # Basico (titulo + body via CLI):
    py -3.12 scripts/commit_sessao.py \\
        --titulo "sessao: feature X" \\
        --body "Descricao detalhada em markdown..."

    # Body a partir de changelog:
    py -3.12 scripts/commit_sessao.py \\
        --titulo "sessao: feature X" \\
        --body-file relatorios/CHANGELOG_SESSAO_2026-04-23.md

    # Dry-run (imprime o que faria, sem commitar):
    py -3.12 scripts/commit_sessao.py --titulo "..." --body "..." --dry-run

Pre-requisito:
    - Arquivos ja devem estar em `git add` (staged) em cada repo que quer
      commitar. Se um dos dois repos nao tem nada staged, o script commita so
      no outro (com aviso).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

RAIZ_MAIN = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")
RAIZ_DOCS = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS")

CO_AUTHORED = "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"


def run_git(cwd: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Roda git no cwd indicado e devolve o CompletedProcess."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode != 0:
        print(f"[ERRO] git {' '.join(args)} em {cwd.name}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result


def listar_staged(cwd: Path) -> list[str]:
    """Retorna lista de arquivos staged. Vazia se nada staged."""
    r = run_git(cwd, ["diff", "--cached", "--name-only"])
    return [l for l in r.stdout.splitlines() if l.strip()]


def commitar(cwd: Path, titulo: str, body: str, dry_run: bool) -> str | None:
    """Commita com titulo + body. Retorna SHA curto, ou None se dry-run/sem-staged."""
    staged = listar_staged(cwd)
    if not staged:
        print(f"  {cwd.name}: nada staged, pulando.")
        return None

    print(f"  {cwd.name}: {len(staged)} arquivos staged")
    for f in staged[:10]:
        print(f"    - {f}")
    if len(staged) > 10:
        print(f"    ... (+{len(staged) - 10} outros)")

    mensagem_completa = f"{titulo}\n\n{body}\n\n{CO_AUTHORED}\n"

    if dry_run:
        print(f"  [dry-run] commitaria com mensagem:")
        print("  " + "-" * 60)
        for linha in mensagem_completa.splitlines():
            print(f"  | {linha}")
        print("  " + "-" * 60)
        return "DRY_RUN_SHA"

    # Usa --file=- (stdin) pra evitar problemas com newlines/escapes
    result = subprocess.run(
        ["git", "commit", "--file=-"],
        cwd=cwd,
        input=mensagem_completa,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"[ERRO] git commit falhou em {cwd.name}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    sha = run_git(cwd, ["rev-parse", "--short", "HEAD"]).stdout.strip()
    print(f"  [OK] {cwd.name} @ {sha}")
    return sha


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--titulo", required=True, help="Titulo do commit (1 linha)")
    grupo_body = ap.add_mutually_exclusive_group(required=True)
    grupo_body.add_argument("--body", help="Corpo do commit (texto)")
    grupo_body.add_argument(
        "--body-file",
        type=Path,
        help="Caminho de arquivo com o corpo do commit",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Imprime o que faria, sem commitar de verdade",
    )
    ap.add_argument(
        "--so-docs",
        action="store_true",
        help="Commita so em PRODAM_DOCS (pula o commit em PROJETO_PRODAM)",
    )
    ap.add_argument(
        "--so-main",
        action="store_true",
        help="Commita so em PROJETO_PRODAM (pula o commit em PRODAM_DOCS)",
    )
    args = ap.parse_args()

    if args.so_docs and args.so_main:
        ap.error("--so-docs e --so-main sao mutuamente exclusivos")

    body = args.body
    if args.body_file:
        if not args.body_file.exists():
            ap.error(f"arquivo nao existe: {args.body_file}")
        body = args.body_file.read_text(encoding="utf-8").strip()

    print(f"=== commit_sessao.py ({'DRY-RUN' if args.dry_run else 'APPLY'}) ===")
    print(f"Titulo: {args.titulo}")
    print(f"Body: {len(body)} chars")
    print()

    sha_main = None
    if not args.so_docs:
        print("[1/2] PROJETO_PRODAM")
        sha_main = commitar(RAIZ_MAIN, args.titulo, body, args.dry_run)
        print()

    if not args.so_main:
        print("[2/2] PRODAM_DOCS")
        body_docs = body
        if sha_main and sha_main != "DRY_RUN_SHA":
            body_docs = f"{body}\n\nVer tambem: PROJETO_PRODAM@{sha_main}"
        elif sha_main == "DRY_RUN_SHA":
            body_docs = f"{body}\n\nVer tambem: PROJETO_PRODAM@<SHA_DO_COMMIT_1>"
        sha_docs = commitar(RAIZ_DOCS, args.titulo, body_docs, args.dry_run)
        print()

    print("=== resumo ===")
    if sha_main:
        print(f"  PROJETO_PRODAM @ {sha_main}")
    if not args.so_main:
        sha_docs_final = sha_docs if 'sha_docs' in locals() else None
        if sha_docs_final:
            print(f"  PRODAM_DOCS    @ {sha_docs_final}")

    if args.dry_run:
        print("  (dry-run — nada foi commitado)")
    else:
        print()
        print("Push manual (regra de seguranca do projeto):")
        if sha_main:
            print(f"  cd {RAIZ_MAIN} && git push")
        if not args.so_main and 'sha_docs' in locals() and sha_docs:
            print(f"  cd {RAIZ_DOCS} && git push")


if __name__ == "__main__":
    main()
