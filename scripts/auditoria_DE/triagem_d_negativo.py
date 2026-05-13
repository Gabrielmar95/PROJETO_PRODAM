"""Triagem: devedores com prescrição D+ negativo (faturas exigíveis cujo
competência + 5 anos < hoje). Read-only — não modifica nenhum dado.
Prescrição quinquenal: Art. 206 §5º I CC, contada do vencimento da fatura.
Vencimento presumido = último dia do mês seguinte à competência."""
import sqlite3
from datetime import date
from collections import defaultdict
import calendar

DB = r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_ANALISE\prodam.db"
HOJE = date(2026, 5, 12)


def vencimento_de_competencia(comp: str) -> date | None:
    """Competência 'MM/AAAA' → vencimento presumido (último dia mês seguinte)."""
    try:
        parts = comp.strip().split("/")
        if len(parts) == 2:
            mes, ano = int(parts[0]), int(parts[1])
        else:
            return None
        mes_venc = mes + 1
        ano_venc = ano
        if mes_venc > 12:
            mes_venc = 1
            ano_venc += 1
        ultimo_dia = calendar.monthrange(ano_venc, mes_venc)[1]
        return date(ano_venc, mes_venc, ultimo_dia)
    except Exception:
        return None


def main():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    rows = db.execute("""
        SELECT cliente, competencia, COUNT(*) as n
        FROM spcf_faturas
        WHERE situacao != 'Totalmente Paga'
          AND competencia IS NOT NULL
          AND competencia != ''
        GROUP BY cliente, competencia
    """).fetchall()

    dev: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for r in rows:
        venc = vencimento_de_competencia(r["competencia"])
        if venc is None:
            continue
        try:
            prescricao = date(venc.year + 5, venc.month, venc.day)
        except ValueError:
            prescricao = date(venc.year + 5, venc.month, venc.day - 1)
        d_plus = (prescricao - HOJE).days
        dev[r["cliente"]].append((d_plus, r["n"], r["competencia"]))

    negativos = []
    for cliente, faturas in dev.items():
        min_d = min(f[0] for f in faturas)
        n_neg = sum(f[1] for f in faturas if f[0] < 0)
        n_total = sum(f[1] for f in faturas)
        if n_neg > 0:
            negativos.append((cliente, min_d, n_neg, n_total))

    negativos.sort(key=lambda x: x[1])

    hdr = f"{'Devedor':<30} {'D+ min':>8} {'Fat D-':>7} {'Fat tot':>8}"
    print(f"TOTAL: {len(negativos)} devedores com D+ negativo")
    print(hdr)
    print("-" * len(hdr))
    for c, d, nn, nt in negativos:
        print(f"{c:<30} {d:>8} {nn:>7} {nt:>8}")

    db.close()


if __name__ == "__main__":
    main()
