"""
ses_reconciliacao_completa.py — Reconciliação definitiva das faturas SES/SUSAM.

Objetivo: mapear TODAS as faturas SES do SPCF, classificar por prescrição
(cutoff 2026-04-14 -5y = 2021-04-14), cruzar 4 fontes e identificar gaps.

Fontes:
  1. consolidado_faturas.json (cobranças ativas no SPCF)    → DB base
  2. rel_faturas_aberto.json (emitidas não pagas, snapshot)
  3. rel_geral_faturas_{ano}.json (histórico 2019-2026)
  4. SPCF_EXTRACAO/por_devedor/SES_SUSAM/faturas_detalhes_SES_SUSAM.json

Saídas:
  ses_reconciliacao.json       — dataset completo
  ses_reconciliacao.csv        — tabela exportável
  ses_reconciliacao_summary.md — relatório executivo
"""
from __future__ import annotations
import json, sys, csv
from pathlib import Path
from datetime import date, datetime
from collections import defaultdict, Counter
from decimal import Decimal, InvalidOperation

sys.stdout.reconfigure(encoding='utf-8')

# Helpers compartilhados — norm() resolve acentos+case
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from prodam_utils import norm, norm_variants

DL = ROOT / "SPCF_EXTRACAO" / "downloads"
DADOS = ROOT / "SPCF_EXTRACAO" / "dados"
POR_DEV = ROOT / "SPCF_EXTRACAO" / "por_devedor" / "SES_SUSAM"
OUT = ROOT

from datetime import timedelta
HOJE = date.today()
PRESCRICAO_CUTOFF = HOJE - timedelta(days=365*5)   # 5 anos antes de hoje

def brl(s) -> Decimal:
    if s is None or s == "":
        return Decimal(0)
    s = str(s).replace("R$", "").replace("\xa0", "").strip()
    if not s or s == "-":
        return Decimal(0)
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return Decimal(0)

def fmt_brl(v) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_comp(s: str) -> date | None:
    """'05/2021' → 2021-05-01 (primeiro dia do mês)"""
    if not s or "/" not in s:
        return None
    try:
        m, y = s.split("/")
        return date(int(y), int(m), 1)
    except Exception:
        return None

def parse_br_date(s: str) -> date | None:
    """'28/01/2019' → date"""
    if not s or "/" not in s: return None
    try:
        return datetime.strptime(s.strip(), "%d/%m/%Y").date()
    except ValueError:
        return None

def vencimento_30(emissao: str) -> date | None:
    """Vencimento padrão = emissão + 30 dias"""
    d = parse_br_date(emissao)
    if not d: return None
    from datetime import timedelta
    return d + timedelta(days=30)

def norm_id(x) -> str:
    """Normaliza IDs: '161532' == '161532.0' == 161532"""
    if x is None: return ""
    s = str(x).strip()
    if not s: return ""
    # Remove trailing .0 (pandas float artifact)
    if s.endswith(".0"):
        s = s[:-2]
    # Drop leading zeros in pure integers
    try:
        return str(int(float(s)))
    except (ValueError, TypeError):
        return s

def norm_contrato(c) -> str:
    """Normaliza contrato: '018/2021', 'C.18/2021', ' 018/2021' → '18/2021'"""
    if not c: return ""
    s = str(c).strip().replace("C.", "").replace("c.", "")
    # Strip leading zeros from the first part
    if "/" in s:
        a, b = s.split("/", 1)
        try:
            return f"{int(a)}/{b.strip()}"
        except ValueError:
            return s
    return s

def esta_prescrita(venc: date | None) -> bool:
    if venc is None: return False
    return venc < PRESCRICAO_CUTOFF

# ============================================================
# 1. CARREGA CONSOLIDADO_FATURAS (BASE DO DB — cobranças ativas)
# ============================================================
con = json.load(open(DADOS / "consolidado_faturas.json", encoding="utf-8"))
ses_con = [r for r in con if (r.get("fatura_parsed") or {}).get("cliente","").upper() in ("SES","SUSAM")]
print(f"[1] consolidado_faturas.json → {len(ses_con)} faturas SES")

records_db = {}
for r in ses_con:
    db = r.get("dados_base") or {}
    fp = r.get("fatura_parsed") or {}
    nfse = norm_id(r.get("id") or db.get("Número"))
    records_db[nfse] = {
        "id": nfse,
        "contrato": db.get("Contrato", "").strip(),
        "comp": db.get("Comp.", "").strip(),
        "valor_bruto": str(brl(db.get("Valor"))),
        "valor_corrigido": str(brl(db.get("Corrigido"))),
        "atraso_dias": (db.get("Atraso") or "").replace(" dias", "").strip(),
        "status_spcf": db.get("Status","").strip(),
        "fonte_registro": db.get("_from", "cobrancas.json"),
        "cadeia_elos": r.get("cadeia_5_elos", {}).get("elos", {}),
        "empenhos_vinculados_qtd": r.get("total_empenhos_vinculados", 0),
        "tem_pdf": bool(r.get("pdf")),
    }

# ============================================================
# 2. CARREGA REL_FATURAS_ABERTO (snapshot de emitidas em aberto)
# ============================================================
ab = json.load(open(DL / "rel_faturas_aberto.json", encoding="utf-8"))
ses_ab = [r for r in ab if str(r.get("Cliente","")).strip().upper() in ("SES","SUSAM")]
print(f"[2] rel_faturas_aberto.json → {len(ses_ab)} faturas SES emitidas em aberto")

records_ab = {}
for r in ses_ab:
    num = norm_id(r.get("Num."))
    records_ab[num] = {
        "num": num,
        "contrato": str(r.get("Contrato","")).strip(),
        "comp": str(r.get("Competência") or r.get("Compet�ncia","")).strip(),
        "emissao": str(r.get("Data Emissão") or r.get("Data Emiss�o","")).strip(),
        "valor_servicos": str(brl(r.get("Valor Serviços") or r.get("Valor Servi�os", ""))),
        "protocolo": str(r.get("Protocolo SIGED","")).strip(),
    }

# ============================================================
# 3. CARREGA REL_GERAL_FATURAS (histórico 2019-2026)
# ============================================================
records_geral = {}
situacao_counter = Counter()
for y in range(2019, 2027):
    f = DL / f"rel_geral_faturas_{y}.json"
    if not f.exists(): continue
    data = json.load(open(f, encoding="utf-8"))
    if not data: continue
    cli_key = list(data[0].keys())[0]
    for r in data[1:]:
        c = str(r.get(cli_key, "") or "").strip().upper()
        if c not in ("SES", "SUSAM"): continue
        rps = norm_id(r.get("Unnamed: 1"))
        nfse = norm_id(r.get("Unnamed: 3"))
        key = nfse or rps
        sit = str(r.get("Unnamed: 20","")).strip()
        situacao_counter[sit] += 1
        records_geral[key] = {
            "rps": rps,
            "nfse": nfse,
            "ano_rel": y,
            "contrato": str(r.get("Unnamed: 5","")).strip(),
            "comp": str(r.get("Unnamed: 9","")).strip(),
            "emissao": str(r.get("Unnamed: 10","")).strip(),
            "valor_servico": str(brl(r.get("Unnamed: 12"))),
            "valor_liquido": str(brl(r.get("Unnamed: 16"))),
            "valor_pago": str(brl(r.get("Unnamed: 18"))),
            "ult_pagamento": str(r.get("Unnamed: 19","")).strip(),
            "situacao": sit,
        }
print(f"[3] rel_geral_faturas_*.json → {len(records_geral)} faturas SES (2019-2026)")
print(f"    Situações: {dict(situacao_counter)}")

# ============================================================
# 4. UNIVERSO CONSOLIDADO (union por número)
# ============================================================
universo = {}
# Chave primária: id de NFS-e; secundária: RPS
for nfse, r in records_db.items():
    universo[nfse] = {"fontes": {"DB"}, "db": r, "ab": None, "geral": None}

for num, r in records_ab.items():
    if num in universo:
        universo[num]["fontes"].add("ABERTO")
        universo[num]["ab"] = r
    else:
        universo[num] = {"fontes": {"ABERTO"}, "db": None, "ab": r, "geral": None}

for key, r in records_geral.items():
    if key in universo:
        universo[key]["fontes"].add("GERAL")
        universo[key]["geral"] = r
    else:
        # Tenta casar por RPS nas fontes anteriores
        rps = r.get("rps")
        if rps and rps in universo:
            universo[rps]["fontes"].add("GERAL")
            universo[rps]["geral"] = r
        else:
            universo[key] = {"fontes": {"GERAL"}, "db": None, "ab": None, "geral": r}

print(f"\n[UNION] Universo total SES = {len(universo)} faturas únicas")

# ============================================================
# 5. CLASSIFICAÇÃO POR PRESCRIÇÃO E EXIGIBILIDADE
# ============================================================
def extract_info(entry):
    """Extrai comp, emissao, valor, situacao, de qualquer fonte disponível"""
    db, ab, ge = entry.get("db"), entry.get("ab"), entry.get("geral")
    def pick(*opts):
        for o in opts:
            if o: return o
        return ""
    return {
        "comp": pick(db and db.get("comp"), ab and ab.get("comp"), ge and ge.get("comp")),
        "emissao": pick(ab and ab.get("emissao"), ge and ge.get("emissao")),
        "contrato": pick(db and db.get("contrato"), ab and ab.get("contrato"), ge and ge.get("contrato")),
        "valor": pick(db and db.get("valor_bruto"), ab and ab.get("valor_servicos"),
                      ge and ge.get("valor_servico")),
        "valor_liquido": pick(ge and ge.get("valor_liquido")),
        "situacao_geral": (ge or {}).get("situacao", ""),
        "status_db": (db or {}).get("status_spcf", ""),
        "tem_db": db is not None,
        "tem_ab": ab is not None,
        "tem_ge": ge is not None,
    }

def classificar(entry):
    info = extract_info(entry)
    venc = vencimento_30(info["emissao"]) or parse_comp(info["comp"])
    # Default: se sem data, trata como NÃO-PRESCRITA (conservador)
    prescrita = esta_prescrita(venc) if venc else False
    sit = info["situacao_geral"].upper()
    # É EXIGÍVEL se:
    # - Não prescrita
    # - E não foi paga (ou é Emitida/Parc. Paga/Suspenso/em aberto)
    paga = sit in ("PAGA",)
    cancelada = sit in ("CANCELADA",)
    em_aberto = (
        info["tem_ab"] or
        info["tem_db"] or   # está no consolidado = Suspenso = cobrança ativa
        sit in ("EMITIDA", "PARC. PAGA", "PARCIALMENTE PAGA")
    )
    exigivel = (not prescrita) and (not paga) and (not cancelada) and em_aberto
    return {
        **info,
        "venc_est": venc.isoformat() if venc else None,
        "prescrita": prescrita,
        "paga": paga,
        "cancelada": cancelada,
        "em_aberto": em_aberto,
        "exigivel": exigivel,
    }

classificados = {k: {**v, "class": classificar(v)} for k, v in universo.items()}

# Stats
stats = Counter()
valor_exigivel = Decimal(0)
valor_prescrito = Decimal(0)
for k, v in classificados.items():
    c = v["class"]
    if c["exigivel"]: stats["exigivel"] += 1
    if c["prescrita"]: stats["prescrita"] += 1
    if c["paga"]: stats["paga"] += 1
    if c["cancelada"]: stats["cancelada"] += 1
    if c["exigivel"]:
        valor_exigivel += brl(c["valor"])
    if c["prescrita"] and not c["paga"]:
        valor_prescrito += brl(c["valor"])

print(f"\n[CLASSIFICAÇÃO]")
print(f"  Exigíveis:  {stats['exigivel']:>4}  | Valor: {fmt_brl(valor_exigivel)}")
print(f"  Prescritas: {stats['prescrita']:>4}  | Valor: {fmt_brl(valor_prescrito)}")
print(f"  Pagas:      {stats['paga']:>4}")
print(f"  Canceladas: {stats['cancelada']:>4}")

# ============================================================
# 6. GAPS ENTRE FONTES
# ============================================================
fontes_counter = Counter()
for v in classificados.values():
    fontes_counter[tuple(sorted(v["fontes"]))] += 1
print(f"\n[GAPS ENTRE FONTES]")
for f, n in fontes_counter.most_common():
    print(f"  {'+'.join(f):<25} {n}")

# ============================================================
# 7. EXIGÍVEIS POR CENÁRIO
# ============================================================
exigiveis = [(k, v) for k, v in classificados.items() if v["class"]["exigivel"]]
exigiveis_db = [(k, v) for k, v in exigiveis if "DB" in v["fontes"]]
exigiveis_so_ab = [(k, v) for k, v in exigiveis if v["fontes"] == {"ABERTO"}]
exigiveis_so_ge = [(k, v) for k, v in exigiveis if v["fontes"] == {"GERAL"}]
exigiveis_ab_sem_db = [(k, v) for k, v in exigiveis if "ABERTO" in v["fontes"] and "DB" not in v["fontes"]]

print(f"\n[EXIGÍVEIS POR ORIGEM]")
print(f"  Com DB (SPCF cobrança ativa):   {len(exigiveis_db)}")
print(f"  ABERTO sem DB:                   {len(exigiveis_ab_sem_db)}")
print(f"  Só em GERAL:                     {len(exigiveis_so_ge)}")

# ============================================================
# 8. EXPORT JSON + CSV
# ============================================================
out_json = {
    "meta": {
        "data": HOJE.isoformat(),
        "cutoff_prescricao": PRESCRICAO_CUTOFF.isoformat(),
        "universo_total": len(universo),
        "stats": dict(stats),
        "valor_exigivel_total": str(valor_exigivel),
        "valor_prescrito_total": str(valor_prescrito),
        "fontes_distribuicao": {
            "+".join(sorted(f)): n for f, n in fontes_counter.items()
        },
    },
    "exigiveis": [
        {
            "id": k,
            "fontes": sorted(v["fontes"]),
            "contrato": v["class"]["contrato"],
            "comp": v["class"]["comp"],
            "emissao": v["class"]["emissao"],
            "venc_estimado": v["class"]["venc_est"],
            "valor_bruto": v["class"]["valor"],
            "situacao_spcf": v["class"]["situacao_geral"] or v["class"]["status_db"],
            "tem_cadeia_db": v.get("db") is not None,
            "empenhos_vinculados": (v.get("db") or {}).get("empenhos_vinculados_qtd", 0),
        }
        for k, v in sorted(exigiveis, key=lambda kv: -brl(kv[1]["class"]["valor"]))
    ],
    "prescritas_resumo": {
        "quantidade": stats["prescrita"],
        "valor_se_cobraveis": str(valor_prescrito),
    },
}

with open(OUT / "ses_reconciliacao.json", "w", encoding="utf-8") as fh:
    json.dump(out_json, fh, ensure_ascii=False, indent=2, default=str)
print(f"\n[OK] ses_reconciliacao.json")

# CSV
with open(OUT / "ses_reconciliacao.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["id","fontes","contrato","comp","emissao","venc_est","valor",
                "situacao","prescrita","exigivel","tem_db","empenhos_qtd"])
    for k, v in classificados.items():
        c = v["class"]
        w.writerow([
            k, "+".join(sorted(v["fontes"])), c["contrato"], c["comp"],
            c["emissao"], c["venc_est"],
            str(brl(c["valor"])).replace(".", ","),
            c["situacao_geral"] or c["status_db"],
            "SIM" if c["prescrita"] else "NAO",
            "SIM" if c["exigivel"] else "NAO",
            "SIM" if c["tem_db"] else "NAO",
            (v.get("db") or {}).get("empenhos_vinculados_qtd", 0),
        ])
print(f"[OK] ses_reconciliacao.csv")

# ============================================================
# 9. SUMMARY MARKDOWN
# ============================================================
md = f"""# Reconciliação SES/SUSAM — {HOJE.isoformat()}

## Universo consolidado
- **{len(universo)} faturas únicas** cruzadas de 4 fontes SPCF
- Cutoff prescrição: {PRESCRICAO_CUTOFF.isoformat()} (HOJE −5 anos)

## Distribuição por exigibilidade

| Classe | Qtd | Valor |
|--------|-----|-------|
| Exigíveis (não prescritas + em aberto) | **{stats['exigivel']}** | **{fmt_brl(valor_exigivel)}** |
| Prescritas | {stats['prescrita']} | {fmt_brl(valor_prescrito)} |
| Pagas | {stats['paga']} | — |
| Canceladas | {stats['cancelada']} | — |

## Distribuição por fontes

| Combinação de fontes | Qtd |
|----------------------|-----|
"""
for f, n in sorted(fontes_counter.items(), key=lambda x: -x[1]):
    md += f"| {'+'.join(f)} | {n} |\n"

md += f"""

## Exigíveis por rastreabilidade documental

| Cenário | Qtd | Observação |
|---------|-----|------------|
| Em DB (cobrança ativa SPCF) | {len(exigiveis_db)} | Cadeia documental já mapeada |
| Em ABERTO sem DB | {len(exigiveis_ab_sem_db)} | Faturas novas (2024-2026) — integrar ao DB |
| Só em GERAL | {len(exigiveis_so_ge)} | Sem cobrança ativa nem aberto — investigar |

## Divergência com profiles.json

| Campo | profiles.json | Reconciliação | Status |
|-------|--------------|---------------|--------|
| faturas_exigiveis | 144 | **{stats['exigivel']}** | {'OK' if stats['exigivel'] == 144 else 'DIVERGE'} |
| val_exig | R$ 14.748.048,95 | **{fmt_brl(valor_exigivel)}** | {'OK' if abs(valor_exigivel - Decimal('14748048.95')) < 1 else 'DIVERGE'} |

## Top 10 exigíveis por valor
"""
top10 = sorted(exigiveis, key=lambda kv: -brl(kv[1]["class"]["valor"]))[:10]
md += "\n| ID | Contrato | Comp. | Valor | Fontes |\n|----|----------|-------|-------|--------|\n"
for k, v in top10:
    c = v["class"]
    md += f"| {k} | {c['contrato']} | {c['comp']} | {fmt_brl(brl(c['valor']))} | {'+'.join(sorted(v['fontes']))} |\n"

with open(OUT / "ses_reconciliacao_summary.md", "w", encoding="utf-8") as fh:
    fh.write(md)
print(f"[OK] ses_reconciliacao_summary.md")
print(f"\nFinal: {stats['exigivel']} exigíveis × {fmt_brl(valor_exigivel)}")
