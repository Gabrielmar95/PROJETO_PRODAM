"""S1.1 — Triagem prescricional completa dos devedores com D+ negativo.
Cruza competência de faturas com marcos interruptivos (empenhos = Art. 202 VI CC).
Read-only — não modifica dados. Gera relatório para gate humano."""
import sqlite3
import json
import calendar
from datetime import date
from collections import defaultdict
from decimal import Decimal

DB = r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_ANALISE\prodam.db"
PROFILES = r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\profiles.json"
HOJE = date(2026, 5, 12)

FORA_ESCOPO = {
    "PREF DE MANACAPURU", "PREF DE IRANDUBA", "SEMAD-MANAUS",
    "SEMED-MANAUS", "MANAUSPREV", "PREF DE COARI",
    "SEAP", "IMMU", "UEA",
}


def vencimento_de_competencia(comp: str) -> date | None:
    try:
        parts = comp.strip().split("/")
        if len(parts) != 2:
            return None
        mes, ano = int(parts[0]), int(parts[1])
        mes_venc = mes + 1
        ano_venc = ano
        if mes_venc > 12:
            mes_venc = 1
            ano_venc += 1
        ultimo_dia = calendar.monthrange(ano_venc, mes_venc)[1]
        return date(ano_venc, mes_venc, ultimo_dia)
    except Exception:
        return None


def prescricao_de_vencimento(venc: date) -> date:
    try:
        return date(venc.year + 5, venc.month, venc.day)
    except ValueError:
        return date(venc.year + 5, venc.month, venc.day - 1)


def main():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    with open(PROFILES, encoding="utf-8") as f:
        profiles = json.load(f)

    # 1. Faturas não-pagas agrupadas por cliente
    faturas = db.execute("""
        SELECT id, nf, cliente, competencia, valor_bruto, contrato_num,
               total_empenhos_vinculados, situacao
        FROM spcf_faturas
        WHERE situacao != 'Totalmente Paga'
          AND competencia IS NOT NULL AND competencia != ''
    """).fetchall()

    dev_faturas: dict[str, list] = defaultdict(list)
    for f in faturas:
        venc = vencimento_de_competencia(f["competencia"])
        if venc is None:
            continue
        presc = prescricao_de_vencimento(venc)
        d_plus = (presc - HOJE).days
        dev_faturas[f["cliente"]].append({
            "id": f["id"],
            "nf": f["nf"],
            "competencia": f["competencia"],
            "valor_bruto": f["valor_bruto"],
            "contrato": f["contrato_num"],
            "empenhos_vinc": f["total_empenhos_vinculados"] or 0,
            "d_plus": d_plus,
            "vencimento": venc.isoformat(),
            "prescricao": presc.isoformat(),
        })

    # 2. Empenhos por cliente (marco interruptivo mais recente)
    empenhos = db.execute("""
        SELECT cliente, MAX(data_emissao) as ult_emissao, COUNT(*) as total
        FROM spcf_empenhos
        WHERE cliente IS NOT NULL
        GROUP BY cliente
    """).fetchall()
    marcos_empenho = {}
    for e in empenhos:
        marcos_empenho[e["cliente"]] = {
            "total_empenhos": e["total"],
            "ult_competencia": e["ult_emissao"] or "N/A",
        }

    # 3. Montar relatório
    resultados = []
    for cliente, fats in dev_faturas.items():
        if cliente in FORA_ESCOPO:
            continue
        fats_neg = [f for f in fats if f["d_plus"] < 0]
        if not fats_neg:
            continue

        min_d = min(f["d_plus"] for f in fats_neg)
        n_neg = len(fats_neg)
        n_total = len(fats)
        val_neg = sum(Decimal(str(f["valor_bruto"])) for f in fats_neg)
        val_total = sum(Decimal(str(f["valor_bruto"])) for f in fats)
        tem_empenho_vinc = any(f["empenhos_vinc"] > 0 for f in fats_neg)

        marco = marcos_empenho.get(cliente, {})
        total_empenhos_db = marco.get("total_empenhos", 0)
        ult_comp_empenho = marco.get("ult_competencia", "N/A")

        # Dados do profiles.json
        prof = profiles.get(cliente, {})
        fase = prof.get("proximo_passo", "N/A")
        forca = prof.get("forca_probatoria", "N/A")
        evidencias = prof.get("evidencias_reconhecimento", 0)
        obs = prof.get("observacoes", "")

        # Classificação preliminar
        if total_empenhos_db > 0 or tem_empenho_vinc or evidencias > 10:
            classificacao = "INVESTIGAR"
            fundamento = "Marcos interruptivos potenciais (empenhos/evidências)"
        elif n_neg == n_total:
            classificacao = "INCLUIR"
            fundamento = "100% faturas com D- e sem marcos visíveis"
        else:
            classificacao = "INVESTIGAR"
            fundamento = "Mix de faturas D+/D- — análise individual necessária"

        resultados.append({
            "cliente": cliente,
            "d_plus_min": min_d,
            "fat_d_neg": n_neg,
            "fat_total": n_total,
            "val_d_neg": val_neg,
            "val_total": val_total,
            "tem_empenho_vinc": tem_empenho_vinc,
            "total_empenhos_db": total_empenhos_db,
            "ult_comp_empenho": ult_comp_empenho,
            "fase": fase,
            "forca": forca,
            "evidencias": evidencias,
            "classificacao": classificacao,
            "fundamento": fundamento,
            "obs_profiles": obs[:120] if obs else "",
        })

    resultados.sort(key=lambda x: x["d_plus_min"])

    # 4. Imprimir relatório
    print(f"TRIAGEM PRESCRICIONAL — {HOJE.isoformat()}")
    print(f"Devedores em-escopo com D+ negativo: {len(resultados)}")
    print(f"{'='*120}")
    print()

    for r in resultados:
        print(f"--- {r['cliente']} ---")
        print(f"  D+ min: {r['d_plus_min']:>6}d | Faturas D-: {r['fat_d_neg']}/{r['fat_total']}"
              f" | Valor D-: R$ {r['val_d_neg']:,.2f}")
        print(f"  Fase: {r['fase']} | Força: {r['forca']}"
              f" | Evidências reconhecimento: {r['evidencias']}")
        print(f"  Empenhos DB: {r['total_empenhos_db']}"
              f" | Últ. competência empenho: {r['ult_comp_empenho']}"
              f" | Vinculado a fatura D-: {'SIM' if r['tem_empenho_vinc'] else 'NÃO'}")
        print(f"  CLASSIFICAÇÃO: {r['classificacao']} — {r['fundamento']}")
        if r["obs_profiles"]:
            print(f"  Obs profiles: {r['obs_profiles']}...")
        print()

    # 5. Resumo
    incluir = [r for r in resultados if r["classificacao"] == "INCLUIR"]
    investigar = [r for r in resultados if r["classificacao"] == "INVESTIGAR"]
    print(f"{'='*120}")
    print(f"RESUMO: {len(incluir)} INCLUIR | {len(investigar)} INVESTIGAR")
    print(f"Valor total D- (bruto): R$ {sum(r['val_d_neg'] for r in resultados):,.2f}")

    db.close()
    return resultados


if __name__ == "__main__":
    main()
