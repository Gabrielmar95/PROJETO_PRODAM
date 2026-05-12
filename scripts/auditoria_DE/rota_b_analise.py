"""Rota B — análise cruzada SSP + FENIXSOFT/FENIXSOFT2 + DETRAN + Tier3.

Produz relatório stdout para cada devedor:
  - Faturas D- (prescritas >5a do vencimento calculado)
  - Empenhos disponíveis (com contrato extraído do JSON dados_base)
  - Cruzamento empenho × fatura por contrato normalizado
  - Veredicto: COBERTA / DESCOBERTA / INVESTIGAR_MANUAL
"""
import sqlite3
import json
import datetime as dt
import sys
import re
from decimal import Decimal
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DB = Path(__file__).resolve().parent.parent.parent / "PRODAM_DOCS" / "_ANALISE" / "prodam.db"
HOJE = dt.date.today()
CUTOFF_5A = HOJE - dt.timedelta(days=1826)
CUTOFF_2_5A_GOVT = dt.timedelta(days=913)  # Decreto 20.910/1932


def norm_ct(raw: str) -> str:
    """Normaliza contrato: '006/2021' → '6/2021', '67/2012' → '67/2012'."""
    if not raw:
        return ""
    m = re.search(r"(\d+)\s*/\s*(\d{4})", raw)
    if m:
        return f"{int(m.group(1))}/{m.group(2)}"
    return raw.strip()


def parse_date_br(d: str) -> dt.date | None:
    """DD/MM/AAAA → date."""
    if not d:
        return None
    try:
        parts = d.strip().split("/")
        if len(parts) == 3:
            return dt.date(int(parts[2]), int(parts[1]), int(parts[0]))
    except (ValueError, IndexError):
        pass
    return None


def vencimento_de_competencia(comp: str) -> dt.date | None:
    """MM/AAAA → último dia do mês seguinte (vencimento)."""
    if not comp or "/" not in comp:
        return None
    try:
        m, a = comp.split("/")
        mi, ai = int(m), int(a)
        prox_m = mi % 12 + 1
        prox_a = ai + (1 if mi == 12 else 0)
        if prox_m == 2:
            dia = 28
        elif prox_m in (4, 6, 9, 11):
            dia = 30
        else:
            dia = 31
        return dt.date(prox_a, prox_m, dia)
    except (ValueError, IndexError):
        return None


def extrair_contrato_de_json(dados_base_str: str) -> str:
    """Extrai campo 'Contrato' do JSON dados_base de spcf_empenhos."""
    if not dados_base_str:
        return ""
    try:
        d = json.loads(dados_base_str)
        return norm_ct(d.get("Contrato", ""))
    except (json.JSONDecodeError, TypeError):
        return ""


def extrair_descricao_de_json(dados_base_str: str) -> str:
    if not dados_base_str:
        return ""
    try:
        d = json.loads(dados_base_str)
        return d.get("Descrição", d.get("Descricao", ""))
    except (json.JSONDecodeError, TypeError):
        return ""


def analisar_devedor(conn, cliente_like: str, nome: str, is_govt: bool = True):
    """Análise completa de um devedor."""
    print(f"\n{'='*70}")
    print(f"  {nome}")
    print(f"{'='*70}")

    # 1. Faturas
    faturas = conn.execute(
        "SELECT id, nf, competencia, valor_bruto, contrato_num, situacao "
        "FROM spcf_faturas WHERE cliente LIKE ? ORDER BY competencia",
        (cliente_like,),
    ).fetchall()

    d_neg = []
    d_pos = []
    for f in faturas:
        fid, nf, comp, val, ct, sit = f
        venc = vencimento_de_competencia(comp)
        if not venc:
            continue
        dias = (HOJE - venc).days
        ct_norm = norm_ct(ct or "")
        rec = {
            "id": fid, "nf": nf, "comp": comp, "val": val,
            "ct": ct_norm, "sit": sit, "venc": venc, "dias": dias,
        }
        if dias > 1826:
            d_neg.append(rec)
        else:
            d_pos.append(rec)

    print(f"\nFaturas: {len(faturas)} total | {len(d_neg)} D- (>5a) | {len(d_pos)} D+ (<5a)")
    val_dneg = sum(Decimal(str(f["val"] or 0)) for f in d_neg)
    val_dpos = sum(Decimal(str(f["val"] or 0)) for f in d_pos)
    print(f"Valor D-: R$ {val_dneg:,.2f} | Valor D+: R$ {val_dpos:,.2f}")

    # Contratos das faturas D-
    cts_dneg = sorted(set(f["ct"] for f in d_neg if f["ct"]))
    print(f"Contratos com faturas D-: {cts_dneg or '(nenhum)'}")

    # 2. Empenhos
    empenhos = conn.execute(
        "SELECT id, numero, contrato_ref, valor, data_emissao, dados_base "
        "FROM spcf_empenhos WHERE cliente LIKE ? ORDER BY data_emissao",
        (cliente_like,),
    ).fetchall()

    print(f"\nEmpenhos no DB: {len(empenhos)}")

    # Extrair contrato do JSON quando contrato_ref está vazio
    empenhos_parsed = []
    for e in empenhos:
        eid, num, ct_ref, val, data_em, dados_base = e
        ct_db = norm_ct(ct_ref or "")
        ct_json = extrair_contrato_de_json(dados_base)
        ct_final = ct_db or ct_json
        data = parse_date_br(data_em)
        desc = extrair_descricao_de_json(dados_base)
        is_anulacao = "anula" in desc.lower() if desc else False
        empenhos_parsed.append({
            "id": eid, "num": num, "ct": ct_final,
            "val": val, "data": data, "data_str": data_em,
            "desc_curta": desc[:80] if desc else "",
            "is_anulacao": is_anulacao,
        })

    # Empenhos com contrato vs sem
    com_ct = [e for e in empenhos_parsed if e["ct"]]
    sem_ct = [e for e in empenhos_parsed if not e["ct"]]
    print(f"  Com contrato: {len(com_ct)} | Sem contrato: {len(sem_ct)}")

    cts_empenho = sorted(set(e["ct"] for e in com_ct))
    print(f"  Contratos nos empenhos: {cts_empenho or '(nenhum)'}")

    # 3. Cruzamento: para cada fatura D-, buscar empenho no mesmo contrato
    print(f"\n--- Cruzamento Fatura D- × Empenho (marco interruptivo) ---")
    cobertas = []
    descobertas = []

    for f in d_neg:
        ct_fat = f["ct"]
        if not ct_fat:
            descobertas.append(f)
            continue

        # Buscar empenhos no mesmo contrato, não-anulação, pós-vencimento
        marcos = [
            e for e in empenhos_parsed
            if e["ct"] == ct_fat
            and not e["is_anulacao"]
            and e["data"]
            and e["data"] >= f["venc"]
        ]

        if marcos:
            marco_mais_recente = max(marcos, key=lambda e: e["data"])
            # Calcular nova prescrição
            if is_govt:
                nova_presc = marco_mais_recente["data"] + CUTOFF_2_5A_GOVT
            else:
                nova_presc = marco_mais_recente["data"] + dt.timedelta(days=1826)

            status = "EXIGÍVEL" if nova_presc >= HOJE else "PRESCRITA_COM_MARCO"
            cobertas.append({
                **f,
                "marco": marco_mais_recente,
                "nova_presc": nova_presc,
                "status": status,
            })
        else:
            descobertas.append(f)

    print(f"\nCobertas (marco encontrado): {len(cobertas)}")
    for c in cobertas:
        m = c["marco"]
        print(f"  NF {c['nf']} CT={c['ct']} comp={c['comp']} "
              f"R$ {c['val']:,.2f} → marco {m['num']} em {m['data_str']} "
              f"→ nova presc {c['nova_presc']} → {c['status']}")

    print(f"\nDescobertas (sem marco): {len(descobertas)}")
    val_desc = Decimal(0)
    for d in descobertas:
        val_desc += Decimal(str(d["val"] or 0))
        print(f"  NF {d['nf']} CT={d['ct'] or '???'} comp={d['comp']} "
              f"R$ {d['val']:,.2f} dias={d['dias']}")
    print(f"  Total descobertas: R$ {val_desc:,.2f}")

    # 4. Empenhos sem contrato que podem ser marcos potenciais
    ne_sem_ct = [e for e in empenhos_parsed if not e["ct"] and not e["is_anulacao"]]
    if ne_sem_ct and descobertas:
        print(f"\n⚠️  {len(ne_sem_ct)} empenhos SEM contrato (potenciais marcos não cruzados):")
        for e in ne_sem_ct[:10]:
            print(f"  NE {e['num']} data={e['data_str']} R$ {e['val']:,.2f} "
                  f"| {e['desc_curta']}")
        if len(ne_sem_ct) > 10:
            print(f"  ... e mais {len(ne_sem_ct) - 10}")

    # 5. Veredicto — distinguir EXIGÍVEL vs PRESCRITA_COM_MARCO
    exigiveis = [c for c in cobertas if c["status"] == "EXIGÍVEL"]
    prescritas_com_marco = [c for c in cobertas if c["status"] == "PRESCRITA_COM_MARCO"]
    val_exig = sum(Decimal(str(c["val"] or 0)) for c in exigiveis)
    val_presc_marco = sum(Decimal(str(c["val"] or 0)) for c in prescritas_com_marco)

    if exigiveis:
        print(f"\n  ✅ Exigíveis (marco válido): {len(exigiveis)} — R$ {val_exig:,.2f}")
    if prescritas_com_marco:
        print(f"\n  ⛔ Prescritas COM marco (expirado): {len(prescritas_com_marco)} — R$ {val_presc_marco:,.2f}")

    print(f"\n>>> VEREDICTO {nome}: ", end="")
    if not d_neg:
        print("SEM FATURAS D- — nada a investigar")
    elif not descobertas and not prescritas_com_marco:
        print(f"TODAS EXIGÍVEIS — {len(exigiveis)} faturas cobertas por marco válido")
    elif not descobertas and prescritas_com_marco and not exigiveis:
        print(f"PRESCRITA — {len(prescritas_com_marco)} faturas com marco EXPIRADO "
              f"(R$ {val_presc_marco:,.2f}). Unicidade Art. 202 CC impede 2ª interrupção")
    elif not descobertas and prescritas_com_marco and exigiveis:
        print(f"MISTA — {len(exigiveis)} exigíveis (R$ {val_exig:,.2f}) + "
              f"{len(prescritas_com_marco)} prescritas com marco expirado (R$ {val_presc_marco:,.2f})")
    elif ne_sem_ct and len(ne_sem_ct) >= len(descobertas):
        print(f"INVESTIGAR_MANUAL — {len(descobertas)} descobertas mas "
              f"{len(ne_sem_ct)} empenhos sem contrato podem cobrir")
    else:
        print(f"DESCOBERTA — R$ {val_desc:,.2f} sem marco interruptivo")

    total_risco_devedor = val_desc + val_presc_marco
    return {
        "nome": nome,
        "d_neg": len(d_neg),
        "val_dneg": val_dneg,
        "cobertas": len(cobertas),
        "exigiveis": len(exigiveis),
        "val_exigiveis": val_exig,
        "prescritas_com_marco": len(prescritas_com_marco),
        "val_presc_marco": val_presc_marco,
        "descobertas": len(descobertas),
        "val_descobertas": val_desc,
        "ne_sem_ct": len(ne_sem_ct),
        "total_risco": total_risco_devedor,
    }


def main():
    conn = sqlite3.connect(str(DB))

    resultados = []

    # SSP (Governo — Decreto 20.910: 2.5 anos)
    r = analisar_devedor(conn, "%SSP%", "SSP — Secretaria de Segurança Pública", is_govt=True)
    resultados.append(r)

    # FENIXSOFT2 (Privada — 5 anos)
    r = analisar_devedor(conn, "FENIXSOFT2", "FENIXSOFT2 (empresa privada)", is_govt=False)
    resultados.append(r)

    # FENIXSOFT (Privada — 5 anos)
    r = analisar_devedor(conn, "FENIXSOFT", "FENIXSOFT (empresa privada)", is_govt=False)
    resultados.append(r)

    # DETRAN
    r = analisar_devedor(conn, "%DETRAN%", "DETRAN — Departamento de Trânsito", is_govt=True)
    resultados.append(r)

    # Tier 3 — análise individual de todos os devedores com faturas D-
    print(f"\n{'='*70}")
    print(f"  TIER 3 — ANÁLISE INDIVIDUAL DE TODOS OS DEVEDORES COM FATURAS D-")
    print(f"{'='*70}")

    PRIVADAS = {
        "IKM DE LIMA-ME", "BRADESCO", "SALUX", "CETAM", "AADESAM",
        "DPCON", "MULTI INFORMATICA", "LINK CARD", "PROCESSAMENTO DE DADOS",
    }

    clientes = [r[0] for r in conn.execute(
        "SELECT DISTINCT cliente FROM spcf_faturas ORDER BY cliente"
    ).fetchall()]

    ja_analisados = {"SSP", "FENIXSOFT", "FENIXSOFT2", "DETRAN"}
    tier3_candidatos = []

    for cli in clientes:
        if cli in ja_analisados:
            continue
        faturas = conn.execute(
            "SELECT competencia, valor_bruto FROM spcf_faturas WHERE cliente = ?",
            (cli,),
        ).fetchall()
        dneg_count = 0
        val_dneg = Decimal(0)
        for comp, val in faturas:
            venc = vencimento_de_competencia(comp)
            if venc and (HOJE - venc).days > 1826:
                dneg_count += 1
                val_dneg += Decimal(str(val or 0))
        if dneg_count > 0:
            tier3_candidatos.append((cli, dneg_count, val_dneg))

    tier3_candidatos.sort(key=lambda x: x[2], reverse=True)
    print(f"\n{len(tier3_candidatos)} devedores com faturas D-. Analisando individualmente...\n")

    tier3_resultados = []
    for cli, _, _ in tier3_candidatos:
        is_govt = cli not in PRIVADAS
        r = analisar_devedor(conn, cli, cli, is_govt=is_govt)
        tier3_resultados.append(r)

    print(f"\n{'='*70}")
    print(f"  RESUMO TIER 3")
    print(f"{'='*70}")
    total_t3_risco = Decimal(0)
    for r in tier3_resultados:
        total_t3_risco += r["total_risco"]
        tag = ""
        if r["exigiveis"] and not r["descobertas"] and not r["prescritas_com_marco"]:
            tag = "✅ EXIGÍVEL"
        elif r["total_risco"] > 0:
            tag = f"⛔ RISCO R$ {r['total_risco']:,.2f}"
        else:
            tag = "—"
        print(f"  {r['nome']:25s} D-={r['d_neg']:3d}  exig={r['exigiveis']:3d}  "
              f"presc_marco={r['prescritas_com_marco']:3d}  desc={r['descobertas']:3d}  {tag}")
    print(f"\n  TOTAL TIER 3 EM RISCO: R$ {total_t3_risco:,.2f}")

    # Resumo final
    print(f"\n{'='*70}")
    print(f"  RESUMO CONSOLIDADO ROTA B")
    print(f"{'='*70}")
    total_risco_principal = Decimal(0)
    print(f"  {'Devedor':45s} {'D-':>3s}  {'Exig':>4s}  {'PcM':>4s}  {'Desc':>4s}  "
          f"{'Risco':>14s}  {'NE?':>6s}")
    print(f"  {'-'*90}")
    for r in resultados:
        print(f"  {r['nome']:45s} {r['d_neg']:3d}  {r['exigiveis']:4d}  "
              f"{r['prescritas_com_marco']:4d}  {r['descobertas']:4d}  "
              f"R$ {r['total_risco']:>12,.2f}  {r['ne_sem_ct']:4d}")
        total_risco_principal += r["total_risco"]

    print(f"\n  Total principal (SSP+FENIX+DETRAN): R$ {total_risco_principal:,.2f}")
    print(f"  Total Tier 3:                        R$ {total_t3_risco:,.2f}")
    print(f"  TOTAL GERAL EM RISCO:                R$ {total_risco_principal + total_t3_risco:,.2f}")
    print(f"\n  Legenda: Exig=exigíveis (marco válido), PcM=prescritas com marco expirado,")
    print(f"           Desc=descobertas (sem marco), NE?=empenhos sem contrato_ref")

    conn.close()


if __name__ == "__main__":
    main()
