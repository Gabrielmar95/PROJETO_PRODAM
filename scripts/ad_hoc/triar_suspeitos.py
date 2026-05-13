"""
Triagem dos 184 PDFs marcados como `-SUSPEITO` no nome canonico.

Pra cada contrato suspeito distinto (ex: CT-011.2016, CT-028.2012),
pega 1 PDF amostra, extrai texto, mostra contexto ao redor do match
para decidir: contrato real (adicionar ao whitelist) OU ruido do regex.

Input: log_renomeacao.csv (mais recente)
Output: _OUT_triagem_suspeitos_<ts>/
  - relatorio_suspeitos.md (tabela + contexto textual de amostra)
  - suspeitos_por_contrato.csv (todos, agrupados)
"""
from __future__ import annotations
import csv
import re
import sys
from collections import defaultdict, Counter
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


def extrair_contexto(texto: str, alvo: str, raio: int = 80) -> list[str]:
    """Retorna trechos de texto ao redor de cada ocorrencia de `alvo`."""
    hits = []
    for m in re.finditer(re.escape(alvo), texto, re.IGNORECASE):
        ini = max(0, m.start() - raio)
        fim = min(len(texto), m.end() + raio)
        trecho = texto[ini:fim].replace("\n", " ")
        trecho = re.sub(r"\s+", " ", trecho).strip()
        hits.append(trecho)
    return hits[:3]  # no maximo 3


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    saida = RAIZ / f"_OUT_triagem_suspeitos_{ts}"
    saida.mkdir(parents=True, exist_ok=True)

    log = acha_log_rename()
    print(f"[INFO] Lendo: {log}")

    # Carrega log, filtra SUSPEITOs
    suspeitos = []
    with open(log, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f, delimiter=";"):
            nome_novo = row.get("nome_novo", "")
            m = re.search(r"CT-([\d.]+)-SUSPEITO", nome_novo)
            if m:
                suspeitos.append({
                    "contrato_suspeito": m.group(1),
                    "caminho_novo": row["caminho_novo"],
                    "nome_novo": nome_novo,
                    "nome_original": row.get("nome_original", ""),
                    "tipo_final": row.get("tipo_final", ""),
                })
    print(f"[INFO] Total suspeitos no log: {len(suspeitos)}")

    # Agrupa por contrato
    por_ct = defaultdict(list)
    for s in suspeitos:
        por_ct[s["contrato_suspeito"]].append(s)

    print(f"[INFO] Contratos suspeitos distintos: {len(por_ct)}")

    # Grava CSV agrupado
    out_csv = saida / "suspeitos_por_contrato.csv"
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["contrato_suspeito", "qtd", "nomes_novos"])
        for ct, lst in sorted(por_ct.items(), key=lambda x: -len(x[1])):
            nomes = "|".join(s["nome_novo"] for s in lst[:5])
            w.writerow([ct, len(lst), nomes])

    # Pra cada contrato, abre 1 amostra e extrai contexto
    relatorio = [
        f"# Triagem SUSPEITOS — {ts}",
        "",
        f"**Input:** `{log}`",
        f"**Total PDFs suspeitos:** {len(suspeitos)}",
        f"**Contratos distintos:** {len(por_ct)}",
        "",
        "## Contratos SUSPEITOS (ordenados por frequência)",
        "",
        "Para cada, amostra de contexto textual onde o contrato apareceu.",
        "Decisao humana: adicionar ao whitelist (contrato real) ou manter como ruido do regex.",
        "",
    ]

    for ct, lst in sorted(por_ct.items(), key=lambda x: -len(x[1])):
        relatorio.append(f"### CT-{ct} ({len(lst)} PDFs)\n")
        amostra = lst[0]
        pdf_path = Path(amostra["caminho_novo"])
        contexto = []
        if pdf_path.exists():
            try:
                with pdfplumber.open(str(pdf_path)) as pdf:
                    texto = "\n".join((p.extract_text() or "") for p in pdf.pages[:3])
                # tenta com e sem zero-padding
                num = ct.split(".")[0].lstrip("0")
                ano = ct.split(".")[1]
                alvos = [f"{ct.replace('.', '/')}", f"{num}/{ano}",
                         ct, f"{num}.{ano}"]
                for alvo in alvos:
                    ctx = extrair_contexto(texto, alvo)
                    if ctx:
                        contexto = [f'"{c}"' for c in ctx]
                        break
            except Exception as e:
                contexto = [f"(erro ao ler PDF: {e})"]
        else:
            contexto = ["(arquivo nao existe)"]

        relatorio.append(f"- Amostra: `{amostra['nome_novo']}`")
        relatorio.append(f"- Tipo: `{amostra['tipo_final']}`")
        if contexto:
            relatorio.append(f"- Contexto textual (3 primeiras ocorrencias):")
            for c in contexto:
                relatorio.append(f"  - {c[:200]}")
        else:
            relatorio.append(f"- Contexto: (match nao encontrado no texto — pode ser typo do regex)")
        relatorio.append("")

    out_md = saida / "relatorio_suspeitos.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(relatorio))
    print(f"[OK] Gravado: {out_csv}")
    print(f"[OK] Gravado: {out_md}")


if __name__ == "__main__":
    main()
