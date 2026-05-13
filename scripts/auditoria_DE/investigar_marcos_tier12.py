"""Investigação individual Tier 1+2: cruzar empenhos com faturas D- por contrato.
Art. 202 VI CC: empenho referenciando contrato = reconhecimento tácito.
Decreto 20.910/1932: Fazenda Pública reinicia em metade (2,5 anos).
Empresas privadas: reinicia em 5 anos (Art. 206 §5º I CC)."""
import sys
import sqlite3
import json
import calendar
from datetime import date
from decimal import Decimal
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

DB = r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_ANALISE\prodam.db"
PROFILES = r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\profiles.json"
HOJE = date(2026, 5, 12)

TIER_12 = ["SSP", "DETRAN", "SEAD", "IDAM", "FENIXSOFT", "FENIXSOFT2", "IKM DE LIMA-ME"]

GOV_DIRETAS = {"SSP", "SEAD", "IDAM"}
GOV_INDIRETAS = {"DETRAN"}
PRIVADAS = {"FENIXSOFT", "FENIXSOFT2", "IKM DE LIMA-ME"}


def parse_date_br(s: str) -> date | None:
    if not s:
        return None
    try:
        parts = s.strip().split("/")
        if len(parts) == 3:
            return date(int(parts[2]), int(parts[1]), int(parts[0]))
        if len(parts) == 2:
            m, y = int(parts[0]), int(parts[1])
            return date(y, m, calendar.monthrange(y, m)[1])
        return None
    except Exception:
        return None


def vencimento_de_comp(comp: str) -> date | None:
    try:
        parts = comp.strip().split("/")
        if len(parts) != 2:
            return None
        mes, ano = int(parts[0]), int(parts[1])
        mv = mes + 1
        av = ano
        if mv > 12:
            mv = 1
            av += 1
        return date(av, mv, calendar.monthrange(av, mv)[1])
    except Exception:
        return None


def safe_date_add_years(dt: date, years: float) -> date:
    if years == 2.5:
        m = dt.month + 6
        y = dt.year + 2
        if m > 12:
            m -= 12
            y += 1
        d = min(dt.day, calendar.monthrange(y, m)[1])
        return date(y, m, d)
    else:
        y = dt.year + int(years)
        try:
            return date(y, dt.month, dt.day)
        except ValueError:
            return date(y, dt.month, dt.day - 1)


def normalizar_contrato(c: str) -> str:
    if not c:
        return ""
    c = c.strip()
    if "/" in c:
        num, ano = c.split("/", 1)
        num_clean = "".join(ch for ch in num if ch.isdigit())
        if num_clean:
            return f"{int(num_clean)}/{ano.strip()}"
    return c


def main():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    with open(PROFILES, encoding="utf-8") as f:
        profiles = json.load(f)

    for cliente in TIER_12:
        print(f"\n{'='*80}")
        print(f"  {cliente}")
        print(f"{'='*80}")

        # Categoria
        if cliente in GOV_DIRETAS:
            cat, prazo_reinicio = "GOV_DIRETA", 2.5
        elif cliente in GOV_INDIRETAS:
            cat, prazo_reinicio = "GOV_INDIRETA", 2.5
        else:
            cat, prazo_reinicio = "PRIVADA", 5.0
        print(f"  Categoria: {cat} | Reinício pós-marco: {prazo_reinicio} anos")

        # Faturas D-
        faturas = db.execute("""
            SELECT id, nf, competencia, valor_bruto, contrato_num,
                   total_empenhos_vinculados
            FROM spcf_faturas
            WHERE cliente = ? AND situacao != 'Totalmente Paga'
              AND competencia IS NOT NULL AND competencia != ''
        """, (cliente,)).fetchall()

        fats_neg = []
        for f in faturas:
            venc = vencimento_de_comp(f["competencia"])
            if venc is None:
                continue
            presc = safe_date_add_years(venc, 5)
            d_plus = (presc - HOJE).days
            if d_plus < 0:
                fats_neg.append({
                    "id": f["id"],
                    "comp": f["competencia"],
                    "valor": Decimal(str(f["valor_bruto"])),
                    "contrato": normalizar_contrato(f["contrato_num"] or ""),
                    "empenhos_vinc": f["total_empenhos_vinculados"] or 0,
                    "vencimento": venc,
                    "presc_original": presc,
                    "d_plus_original": d_plus,
                })

        if not fats_neg:
            print("  Nenhuma fatura D- encontrada.")
            continue

        contratos_neg = set(f["contrato"] for f in fats_neg if f["contrato"])
        print(f"  Faturas D-: {len(fats_neg)} | Contratos envolvidos: {contratos_neg or 'N/A'}")
        print(f"  Valor total D- (bruto): R$ {sum(f['valor'] for f in fats_neg):,.2f}")

        # Empenhos do devedor
        empenhos = db.execute("""
            SELECT numero, contrato_ref, valor, data_emissao
            FROM spcf_empenhos
            WHERE cliente = ?
            ORDER BY data_emissao DESC
        """, (cliente,)).fetchall()

        if not empenhos:
            print(f"  EMPENHOS: ZERO no DB")
            print(f"  CONCLUSÃO: SEM MARCO INTERRUPTIVO VISÍVEL")
            print(f"  RISCO: ALTO — faturas possivelmente prescritas sem interrupção")
            for f in fats_neg:
                print(f"    NF {f['id']} | comp {f['comp']} | R$ {f['valor']:,.2f}"
                      f" | CT {f['contrato']} | D+ {f['d_plus_original']}")
            continue

        # Mapear empenhos por contrato normalizado
        emp_por_contrato: dict[str, list] = defaultdict(list)
        for e in empenhos:
            ct = normalizar_contrato(e["contrato_ref"] or "")
            dt = parse_date_br(e["data_emissao"])
            emp_por_contrato[ct].append({
                "numero": e["numero"],
                "valor": e["valor"],
                "data": dt,
                "data_raw": e["data_emissao"],
            })

        print(f"  Empenhos no DB: {len(empenhos)} | Contratos com empenho: {set(emp_por_contrato.keys())}")

        # Cruzar fatura D- com empenhos do mesmo contrato
        cobertas = 0
        descobertas = 0
        for f in fats_neg:
            emps_ct = emp_por_contrato.get(f["contrato"], [])
            emps_apos_venc = [e for e in emps_ct if e["data"] and e["data"] >= f["vencimento"]]
            if emps_apos_venc:
                ultimo = max(emps_apos_venc, key=lambda e: e["data"])
                nova_presc = safe_date_add_years(ultimo["data"], prazo_reinicio)
                novo_d_plus = (nova_presc - HOJE).days
                status = "COBERTA" if novo_d_plus > 0 else "PRESCRITA_MESMO_COM_MARCO"
                cobertas += 1 if novo_d_plus > 0 else 0
                descobertas += 0 if novo_d_plus > 0 else 1
                print(f"    NF {f['id']} | comp {f['comp']} | R$ {f['valor']:,.2f}"
                      f" | CT {f['contrato']} | D+orig {f['d_plus_original']}"
                      f" → Marco {ultimo['data_raw']} → Nova presc {nova_presc.isoformat()}"
                      f" → D+ {novo_d_plus} [{status}]")
            else:
                descobertas += 1
                print(f"    NF {f['id']} | comp {f['comp']} | R$ {f['valor']:,.2f}"
                      f" | CT {f['contrato']} | D+orig {f['d_plus_original']}"
                      f" → NENHUM empenho pós-vencimento encontrado [DESCOBERTA]")

        print(f"  RESULTADO: {cobertas} cobertas por marco | {descobertas} descobertas")
        if descobertas > 0:
            val_desc = sum(f["valor"] for f in fats_neg
                          if not any(e["data"] and e["data"] >= f["vencimento"]
                                     for e in emp_por_contrato.get(f["contrato"], [])))
            print(f"  VALOR DESCOBERTO: R$ {val_desc:,.2f}")

    db.close()


if __name__ == "__main__":
    main()
