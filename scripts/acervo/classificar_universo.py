#!/usr/bin/env python3
"""
classificar_universo.py — Classificacao em lote do universo de PDFs (portado do DETRAN).

Origem: DETRAN_AUDITORIA_COMPLETA/10_SCRIPTS_PYTHON/classificar_universo_v2.py
Mudancas no porte:
  - Paths hardcoded substituidos por argparse (--universo/--out/--orgao).
  - Sem filtro de pastas DETRAN-especifico: classifica TODO o universo informado
    (a coluna pasta_raiz do CSV continua servindo de hint para o classificador).
  - Removida a geracao de propostas de rename: a saida e um INDICE LATERAL.

REGRA: NUNCA renomeia/move/apaga arquivo. O CSV de saida e indice lateral —
rename em massa destroi naming canonico existente (licao DETRAN 23/04 tarde-2).

Uso (Windows):
  py -3.12 scripts\\acervo\\classificar_universo.py --universo <out>\\universo.csv ^
      --out <out>\\classificados_v2.csv --orgao SEDUC
  py -3.12 scripts\\acervo\\classificar_universo.py --universo ... --out ... --dry-run
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# classificador_v2 mora no mesmo diretorio (scripts/acervo/)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from classificador_v2 import classificar_pdf_v2  # noqa: E402

COLS = ["caminho", "pasta_raiz", "nome", "tipo", "numero", "orgao",
        "cnpj", "data", "valor", "confianca", "paginas_usadas",
        "alerta", "segundos"]


def classificar(p: Path, pasta_raiz: str, orgao_preferido: str | None) -> dict:
    t0 = time.time()
    try:
        import pdfplumber  # import tardio
        textos = []
        with pdfplumber.open(str(p)) as pdf:
            # Limita a 8 paginas (equilibrio velocidade/cobertura)
            for pg in pdf.pages[:8]:
                textos.append(pg.extract_text() or "")
        r = classificar_pdf_v2(textos, nome_arquivo=p.name, pasta_raiz=pasta_raiz,
                               orgao_preferido=orgao_preferido)
        r["caminho"] = str(p)
        r["pasta_raiz"] = pasta_raiz
        r["segundos"] = round(time.time() - t0, 1)
        return r
    except Exception as e:
        return {
            "caminho": str(p), "pasta_raiz": pasta_raiz,
            "tipo": "ERRO", "numero": None, "orgao": None,
            "cnpj": None, "data": None, "valor": None,
            "confianca": 0.0, "paginas_usadas": [],
            "candidatos_alternativos": [], "alerta": str(e)[:150],
            "segundos": round(time.time() - t0, 1),
        }


def carregar_alvos(universo_csv: Path, limit: int) -> list[tuple[Path, str]]:
    alvos: list[tuple[Path, str]] = []
    with open(universo_csv, encoding="utf-8-sig") as f:
        rd = csv.DictReader(f, delimiter=";")
        for row in rd:
            p = Path(row["caminho"])
            # se existe derivado .ocr.pdf (gerado por ocr_lote.py), classifica o derivado
            # (tem texto pesquisavel) mantendo a referencia ao original no nome
            if row.get("tem_texto") == "0":
                ocr = p.with_name(p.stem + ".ocr.pdf")
                if ocr.exists():
                    p = ocr
            alvos.append((p, row.get("pasta_raiz", "")))
    if limit > 0:
        alvos = alvos[:limit]
    return alvos


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Classifica PDFs do universo.csv com classificador_v2. Gera indice lateral; NUNCA renomeia.")
    ap.add_argument("--universo", required=True, help="universo.csv do inventario_pdfs.py")
    ap.add_argument("--out", required=True,
                    help="Arquivo CSV de saida (ex: classificados_v2.csv)")
    ap.add_argument("--orgao", default=None,
                    help="Devedor em foco (ex: SEDUC) — desempata extracao de orgao")
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    universo = Path(args.universo)
    out_csv = Path(args.out)

    if not universo.exists():
        if args.dry_run:
            print(f"[DRY-RUN] universo.csv inexistente neste ambiente: {universo}")
            print(f"[DRY-RUN] plano: classificar_pdf_v2 (8 pgs/pdf, orgao={args.orgao}) "
                  f"-> {out_csv} (';', utf-8-sig)")
            return 0
        print(f"ERRO: universo.csv nao existe: {universo}", file=sys.stderr)
        return 1

    alvos = carregar_alvos(universo, args.limit)
    existentes = [(p, pasta) for p, pasta in alvos if p.exists()]
    print(f"PDFs no universo: {len(alvos)} | existentes no disco: {len(existentes)}")

    if args.dry_run:
        for p, pasta in existentes[:10]:
            print(f"  [DRY-RUN] classificaria: [{pasta}] {p.name}")
        if len(existentes) > 10:
            print(f"  ... e mais {len(existentes) - 10}")
        print(f"[DRY-RUN] nada foi escrito. Saida seria: {out_csv}")
        return 0

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fh:
        csv.DictWriter(fh, fieldnames=COLS, delimiter=";").writeheader()

    tipos: Counter = Counter()
    confs: Counter = Counter()
    t_ini = time.time()
    with ThreadPoolExecutor(max_workers=max(1, args.threads)) as ex:
        futs = {ex.submit(classificar, p, pasta, args.orgao): (p, pasta)
                for p, pasta in existentes}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                r = f.result()
            except Exception as e:
                p, pasta = futs[f]
                r = {"caminho": str(p), "pasta_raiz": pasta, "tipo": "ERRO",
                     "numero": None, "orgao": None, "cnpj": None, "data": None,
                     "valor": None, "confianca": 0.0, "paginas_usadas": [],
                     "alerta": str(e)[:150], "segundos": 0.0}
            r["nome"] = Path(r["caminho"]).name
            r["paginas_usadas"] = str(r.get("paginas_usadas") or [])
            with open(out_csv, "a", newline="", encoding="utf-8-sig") as fh:
                csv.DictWriter(fh, fieldnames=COLS, delimiter=";",
                               extrasaction="ignore").writerow(r)
            tipos[r.get("tipo", "")] += 1
            c = r.get("confianca", 0.0)
            confs["alta" if c >= 0.8 else "media" if c >= 0.5 else "baixa"] += 1
            if i % 100 == 0:
                el = time.time() - t_ini
                rate = i / el if el > 0 else 0
                eta = (len(existentes) - i) / rate if rate > 0 else 0
                print(f"  {i}/{len(existentes)} ({rate:.1f} pdf/s) ETA {eta / 60:.1f}min",
                      flush=True)

    el = time.time() - t_ini
    print(f"\nClassificacao concluida em {el / 60:.1f}min")
    print(f"Tipos: {dict(tipos.most_common())}")
    print(f"Confianca: alta={confs['alta']} media={confs['media']} baixa={confs['baixa']}")
    print(f"Indice lateral gravado: {out_csv}")
    print("LEMBRETE: indice lateral — NAO use para rename em massa.")

    # Relatorio MD ao lado do CSV
    rel = out_csv.with_suffix(".relatorio.md")
    rel.write_text(
        "# Classificacao v2 (indice lateral)\n\n"
        f"**Data:** {datetime.now().isoformat(timespec='seconds')}\n"
        f"**Universo:** `{universo}`\n"
        f"**Orgao em foco:** {args.orgao or '(nenhum)'}\n"
        f"**PDFs classificados:** {len(existentes)} em {el / 60:.1f} min\n\n"
        f"## Confianca\n- Alta (>=0.8): {confs['alta']}\n- Media (>=0.5): {confs['media']}\n"
        f"- Baixa (<0.5): {confs['baixa']}\n\n## Tipos\n\n| Tipo | Qtd |\n|---|---:|\n"
        + "\n".join(f"| {t} | {n} |" for t, n in tipos.most_common())
        + "\n\n_Indice lateral: nunca renomear arquivos em massa a partir deste CSV._\n",
        encoding="utf-8")
    print(f"Relatorio: {rel}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
