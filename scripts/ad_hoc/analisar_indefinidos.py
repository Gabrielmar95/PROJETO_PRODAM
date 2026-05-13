"""
Analisa os 525 PDFs classificados como 'Indefinido' apos v5 + renomeacao.

Categoriza por:
  - Tamanho de texto (vazio / menu SPCF curto / texto substancial)
  - Pasta de origem (SPCF_EXTRACAO vs DETRAN_CONSOLIDADO vs ...)
  - Numero de paginas
  - Amostra textual (primeiros 200 chars)

Output: _OUT_analise_indefinidos_<ts>/
  - relatorio_indefinidos.md (categorias + top pastas + amostras)
  - indefinidos_detalhado.csv
"""
from __future__ import annotations
import csv
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pdfplumber  # type: ignore

RAIZ = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")


def acha_log_rename() -> Path:
    cand = sorted(
        RAIZ.glob("_OUT_rename_inplace_*/log_renomeacao.csv"),
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    if not cand:
        print("[ERRO] log_renomeacao.csv nao encontrado")
        sys.exit(1)
    return cand[0]


def classifica_tamanho(chars: int) -> str:
    if chars < 100:
        return "VAZIO"
    if chars < 1000:
        return "CURTO_MENU_OU_CABECALHO"
    if chars < 5000:
        return "MEDIO_COM_CONTEUDO"
    return "GRANDE_DOCUMENTO"


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    saida = RAIZ / f"_OUT_analise_indefinidos_{ts}"
    saida.mkdir(parents=True, exist_ok=True)

    log = acha_log_rename()
    print(f"[INFO] Lendo: {log}")

    # Carrega log, filtra Indefinido
    indefs = []
    with open(log, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f, delimiter=";"):
            if row.get("tipo_final") == "Indefinido":
                indefs.append(row)
    print(f"[INFO] Total Indefinidos no log: {len(indefs)}")

    # Pra cada, abre PDF, mede tamanho texto, extrai amostra
    detalhes = []
    for i, row in enumerate(indefs, 1):
        if i % 100 == 0:
            print(f"  analisando {i}/{len(indefs)}")
        p = Path(row["caminho_novo"])
        raiz_pasta = "OUTRO"
        for r in ("SPCF_EXTRACAO", "DETRAN_CONSOLIDADO", "PRODAM_DOCS"):
            if r in str(p):
                raiz_pasta = r
                break

        chars = 0
        n_pag = 0
        amostra = ""
        if p.exists():
            try:
                with pdfplumber.open(str(p)) as pdf:
                    n_pag = len(pdf.pages)
                    t = "\n".join((pg.extract_text() or "") for pg in pdf.pages[:3])
                    chars = len(t.strip())
                    amostra = re.sub(r"\s+", " ", t[:300]).strip()
            except Exception:
                pass

        detalhes.append({
            "nome_novo": row["nome_novo"],
            "nome_original": row["nome_original"],
            "raiz": raiz_pasta,
            "paginas": n_pag,
            "chars_texto": chars,
            "categoria_tamanho": classifica_tamanho(chars),
            "amostra_texto": amostra,
            "caminho_novo": row["caminho_novo"],
        })

    # Grava detalhes
    out_csv = saida / "indefinidos_detalhado.csv"
    cols = ["nome_novo", "nome_original", "raiz", "paginas",
            "chars_texto", "categoria_tamanho", "amostra_texto", "caminho_novo"]
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for d in detalhes:
            w.writerow(d)

    # Agregados
    cat = Counter(d["categoria_tamanho"] for d in detalhes)
    por_raiz = Counter(d["raiz"] for d in detalhes)
    cat_por_raiz = defaultdict(Counter)
    for d in detalhes:
        cat_por_raiz[d["raiz"]][d["categoria_tamanho"]] += 1

    # Amostras por categoria (5 cada)
    amostras_cat = defaultdict(list)
    for d in detalhes:
        amostras_cat[d["categoria_tamanho"]].append(d)

    relatorio = [
        f"# Analise dos {len(indefs)} Indefinidos — {ts}",
        "",
        f"**Input:** `{log}`",
        "",
        "## Distribuicao por categoria de tamanho de texto",
        "",
        "| Categoria | Qtd | O que provavelmente e |",
        "|---|---:|---|",
        f"| VAZIO (<100 chars) | {cat['VAZIO']} | Menu SPCF 1 pagina ou PDF imagem sem OCR util |",
        f"| CURTO_MENU_OU_CABECALHO (100-999) | {cat['CURTO_MENU_OU_CABECALHO']} | Cabecalho SPCF / pagina unica de sistema |",
        f"| MEDIO_COM_CONTEUDO (1000-4999) | {cat['MEDIO_COM_CONTEUDO']} | Documento curto — pode ser empenho/recibo nao classificado |",
        f"| GRANDE_DOCUMENTO (>=5000) | {cat['GRANDE_DOCUMENTO']} | Documento substancial — **possivelmente valioso, regex falhou** |",
        "",
        "## Por raiz",
        "| Raiz | Qtd |",
        "|---|---:|",
    ]
    for r, n in por_raiz.most_common():
        relatorio.append(f"| {r} | {n} |")

    relatorio += [
        "",
        "## Cruzamento raiz × tamanho",
        "",
    ]
    for raiz in por_raiz:
        relatorio.append(f"### {raiz}")
        relatorio.append("| Categoria | Qtd |")
        relatorio.append("|---|---:|")
        for cat_nome, n in cat_por_raiz[raiz].most_common():
            relatorio.append(f"| {cat_nome} | {n} |")
        relatorio.append("")

    # Amostras
    relatorio.append("## Amostras por categoria (5 cada)")
    for cat_nome in ["GRANDE_DOCUMENTO", "MEDIO_COM_CONTEUDO",
                     "CURTO_MENU_OU_CABECALHO", "VAZIO"]:
        lst = amostras_cat.get(cat_nome, [])[:5]
        relatorio.append(f"\n### {cat_nome}")
        for d in lst:
            relatorio.append(f"- **{d['nome_novo'][:70]}**")
            relatorio.append(f"  - Original: `{d['nome_original'][:50]}`")
            relatorio.append(f"  - Raiz: {d['raiz']} | Pgs: {d['paginas']} | Chars: {d['chars_texto']}")
            if d["amostra_texto"]:
                relatorio.append(f"  - Amostra: `{d['amostra_texto'][:150]}`")
            relatorio.append("")

    # Sugestoes
    relatorio += [
        "## Sugestoes de acao",
        "",
        f"1. **VAZIO e CURTO**: descartaveis ou merecem OCR agressivo (cascata estagio 3). Total: {cat['VAZIO'] + cat['CURTO_MENU_OU_CABECALHO']}",
        f"2. **MEDIO e GRANDE**: potencialmente documentos valiosos que escaparam dos regex. Total: {cat['MEDIO_COM_CONTEUDO'] + cat['GRANDE_DOCUMENTO']}",
        "   - Vale abrir amostra manual dos maiores (>5000 chars) pra ver se sao: empenhos em formato novo, notificacoes, ofícios internos, etc",
        "   - Pode valer estender os regex de `parse_tipo_doc` da skill `renomeador-pdfs-prodam`",
        "",
    ]

    out_md = saida / "relatorio_indefinidos.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(relatorio))
    print(f"[OK] Gravado: {out_csv}")
    print(f"[OK] Gravado: {out_md}")


if __name__ == "__main__":
    main()
