#!/usr/bin/env python3
"""
validar_citacoes.py — Validador de citações jurídicas (lint anti-alucinação).

Bloqueia citação errônea de Teori Zavascki como relator do REsp 793.969/RJ.

CONTEXTO: na cascata Teori→José Delgado (12/05/2026), descobriu-se que 8
arquivos do projeto citavam erroneamente Teori Zavascki como relator deste
REsp (correto: Min. José Delgado, p/ acórdão; Teori foi vencido).
Esse lint é o guardião que impede que nova citação errônea entre via PR.

CRITÉRIO:
  - Detecta "Teori Zavasck[is]i" próximo (mesma linha OU 5 linhas) de
    "REsp 793.969" ou "REsp 793969"
  - PASSA se houver salvaguarda na janela: "vencido", "venceu",
    "p/ acórdão", "José Delgado", "nunca citar", "não foi relator"
  - REJEITA se não houver salvaguarda

USO:
  python scripts/validar_citacoes.py                  # repo inteiro
  python scripts/validar_citacoes.py path/x.md ...    # arquivos específicos

EXIT CODES:
  0 = sem violações
  1 = pelo menos 1 citação errônea encontrada

ORIGEM: roadmap Janela 3, item 3.3.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTENSOES = (".md", ".py")

# Diretórios excluídos da varredura (são fixtures, backups, ou pastas históricas
# onde o erro é intencional ou meta-discurso)
EXCLUIR_DIRS = {
    "_BACKUPS",
    "_ARQUIVO_DRIFT",
    ".git",
    "PRODAM_DOCS",
    "node_modules",
}
EXCLUIR_PREFIXOS = ("_ARQUIVO_SESSAO_",)
EXCLUIR_PATHS = {
    # Pasta com peças sintéticas para o adversarial-meta-auditor — contém
    # furos intencionais (incluindo citação errônea de Teori como relator)
    "DOCUMENTOS_GERADOS/_TESTE_AGENT",
}

PADRAO_TEORI = re.compile(r"Teori\s+(?:Albino\s+)?Zavasc[sk]+i?", re.IGNORECASE)
PADRAO_RESP = re.compile(r"REsp\s*\.?\s*793[\.\s]?969", re.IGNORECASE)

SALVAGUARDAS = re.compile(
    r"(vencido|venceu|p/\s*ac[oó]rd[ãa]o|Jos[ée]\s+Delgado"
    r"|nunca\s+cit(?:ar|e)|n[ãa]o\s+foi\s+relator|viola\s+regra)",
    re.IGNORECASE,
)

JANELA = 5  # linhas antes/depois


def varrer_arquivo(path: Path) -> list[tuple[int, str, str]]:
    """Retorna [(linha_1based, contexto, razão)] para cada violação."""
    try:
        texto = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    linhas = texto.splitlines()
    violacoes: list[tuple[int, str, str]] = []
    for i, linha in enumerate(linhas):
        if not PADRAO_TEORI.search(linha):
            continue
        inicio = max(0, i - JANELA)
        fim = min(len(linhas), i + JANELA + 1)
        janela = "\n".join(linhas[inicio:fim])
        if not PADRAO_RESP.search(janela):
            continue
        if SALVAGUARDAS.search(janela):
            continue
        contexto = linha.strip()[:200]
        violacoes.append((i + 1, contexto,
                          "Teori citado proximo do REsp 793.969 sem ressalva 'vencido' "
                          "ou 'p/ acórdão Min. José Delgado'"))
    return violacoes


def _eh_excluido(path: Path) -> bool:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return False
    partes = set(rel.parts)
    if partes & EXCLUIR_DIRS:
        return True
    if any(p.startswith(EXCLUIR_PREFIXOS) for p in rel.parts):
        return True
    rel_str = str(rel).replace("\\", "/")
    if any(rel_str.startswith(ex) for ex in EXCLUIR_PATHS):
        return True
    return False


def iter_arquivos(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if root.is_file():
            if root.suffix in EXTENSOES and not _eh_excluido(root):
                out.append(root)
            continue
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix not in EXTENSOES:
                continue
            if _eh_excluido(p):
                continue
            out.append(p)
    return out


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if args:
        roots = [Path(a).resolve() for a in args]
    else:
        roots = [ROOT]

    arquivos = iter_arquivos(roots)
    total = 0
    for f in arquivos:
        # O próprio validador cita "Teori" no docstring/regex — auto-exclui
        if f.name in {"validar_citacoes.py", "test_validar_citacoes.py"}:
            continue
        violacoes = varrer_arquivo(f)
        for linha, contexto, razao in violacoes:
            total += 1
            try:
                rel = f.relative_to(ROOT)
            except ValueError:
                rel = f
            print(f"::error file={rel},line={linha}::CITACAO_ERRONEA: {razao}")
            print(f"  {rel}:{linha}: {contexto}")
    if total:
        print(f"\nFALHA: {total} violacao(oes) encontrada(s).")
        print("  Min. Jose Delgado e o relator do REsp 793.969/RJ "
              "(Teori Zavascki foi vencido).")
        print("  Padrao canonico: 'Rel. p/ acordao Min. Jose Delgado; "
              "Teori Zavascki vencido'.")
        return 1
    print(f"OK: {len(arquivos)} arquivo(s) escaneado(s), sem violacoes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
