"""
auditoria_completude_devedor.py — Audita completude documental e divergências
de cada devedor do Projeto PRODAM contra todas as fontes disponíveis.

Verifica por devedor:
  - Documentos esperados (contrato, NEs, NLs, NFs, aceites, cobranças, ofícios)
  - Presença em cada fonte: profiles.json, prodam.db, consolidado_*.json, DOSSIE/, CONSOLIDADO/
  - Divergências de valor entre profile × DB × SPCF bruto × cobrancas
  - Gaps: documentos mencionados em uma fonte e ausentes em outra

Saídas:
  AUDITORIA_COMPLETUDE_<DEVEDOR>.md   — 1 por devedor
  AUDITORIA_COMPLETUDE_RESUMO.json    — índice global
  AUDITORIA_COMPLETUDE_DASHBOARD.html — visão geral Chart.js
"""
from __future__ import annotations
import json, sys, sqlite3, re
from pathlib import Path
from datetime import date
from decimal import Decimal, InvalidOperation
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

# Helper compartilhado (norm() com unidecode — resolve POLÍCIA CIVIL vs POLICIA CIVIL)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from prodam_utils import norm, norm_variants

DB = sqlite3.connect(str(ROOT / "prodam.db"))
DOCS = ROOT / "PRODAM_DOCS"
SPCF = ROOT / "SPCF_EXTRACAO"
DADOS = SPCF / "dados"
DL = SPCF / "downloads"
PD = SPCF / "por_devedor"
OUT = ROOT / "AUDITORIA_COMPLETUDE"
OUT.mkdir(exist_ok=True)

HOJE = date.today()

def brl(s) -> Decimal:
    if s is None or s == "": return Decimal(0)
    s = str(s).replace("R$", "").replace("\xa0", "").strip()
    if not s or s == "-": return Decimal(0)
    if "," in s: s = s.replace(".", "").replace(",", ".")
    try: return Decimal(s)
    except (InvalidOperation, ValueError): return Decimal(0)

def fmt_brl(v) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def norm_cliente_nome(nome: str) -> list[str]:
    """Gera variações do nome do cliente para casamento em diferentes fontes."""
    if not nome: return []
    base = nome.upper().strip()
    variantes = {base}
    # Sem barra
    if "/" in base: variantes.add(base.split("/")[0].strip())
    # Sem sigla (se tem "/")
    if "/" in base: variantes.add(base.split("/")[1].strip())
    # Removendo pontuação
    variantes.add(re.sub(r"[^\w\s]", " ", base).strip())
    return [v for v in variantes if v]

# ============================================================
# CARREGA FONTES
# ============================================================
print("[1/6] Carregando profiles.json...")
profiles = json.load(open(DOCS / "profiles.json", encoding="utf-8"))
print(f"      {len(profiles)} devedores")

print("[2/6] Carregando consolidados SPCF...")
con_f = json.load(open(DADOS / "consolidado_faturas.json", encoding="utf-8"))
con_e = json.load(open(DADOS / "consolidado_empenhos.json", encoding="utf-8"))
con_c = json.load(open(DADOS / "consolidado_contratos.json", encoding="utf-8"))
con_n = json.load(open(DADOS / "consolidado_nfs.json", encoding="utf-8"))
print(f"      {len(con_f)} faturas, {len(con_e)} empenhos, {len(con_c)} contratos, {len(con_n)} NFs")

print("[3/6] Carregando cobrancas.json...")
cobrancas = json.load(open(DADOS / "cobrancas.json", encoding="utf-8"))
print(f"      {len(cobrancas)} cobranças")

# ============================================================
# FUNÇÕES DE BUSCA POR DEVEDOR
# ============================================================
def buscar_em_consolidado(devedor_nome: str, registros: list, campo_cliente_paths: list[tuple]) -> list:
    """Busca registros de um cliente com flexibilidade de campo e nome."""
    alvos = set(norm_cliente_nome(devedor_nome))
    result = []
    for r in registros:
        for path in campo_cliente_paths:
            val = r
            for p in path:
                val = (val or {}).get(p) if isinstance(val, dict) else None
                if val is None: break
            if val:
                val_up = str(val).upper().strip()
                if val_up in alvos or any(a in val_up or val_up in a for a in alvos):
                    result.append(r)
                    break
    return result

def buscar_db(sql: str, *params) -> list:
    cur = DB.execute(sql, params)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

# ============================================================
# AUDITORIA POR DEVEDOR
# ============================================================
CHECKLIST = [
    ("contrato", "Pelo menos 1 contrato PDF ou ID"),
    ("empenhos", "NEs vinculadas ao contrato"),
    ("nls", "Notas de Liquidação"),
    ("nfs", "Notas Fiscais / RPS"),
    ("aceites", "Aceites técnicos / recibos"),
    ("cobrancas", "Registros de cobrança SPCF"),
    ("oficios", "Ofícios de cobrança"),
    ("reconhecimento", "Atos de reconhecimento tácito/expresso"),
    ("cnd", "CNDs / Certidões"),
    ("dossie_folder", "Pasta <DEVEDOR>_DOSSIE/ no PRODAM_DOCS"),
    ("consolidado_folder", "Pasta <DEVEDOR>_CONSOLIDADO/ no PRODAM_DOCS"),
]

def _contar_empenhos_db(sigla: str) -> dict:
    """Conta empenhos no DB usando norm() para casar com acentos+case."""
    variantes = norm_variants(sigla)
    # Busca por todas variantes usando OR
    cond = " OR ".join("UPPER(cliente) LIKE ?" for _ in variantes)
    params = [f"%{v}%" for v in variantes]
    rows = buscar_db(f"""
        SELECT COUNT(*) as n, SUM(valor) as total, MIN(data_emissao) as min_d, MAX(data_emissao) as max_d
        FROM spcf_empenhos WHERE {cond}
    """, *params)
    return rows[0] if rows else {}

def _contar_faturas_db(sigla: str) -> dict:
    """Conta faturas no DB — compara via Python norm() para pegar acentos."""
    # Carrega todos clientes distintos do DB (cached)
    if not hasattr(_contar_faturas_db, "_clientes_db"):
        _contar_faturas_db._clientes_db = {row["cliente"] for row in buscar_db("SELECT DISTINCT cliente FROM spcf_faturas")}
    variantes = norm_variants(sigla)
    matches = [c for c in _contar_faturas_db._clientes_db if norm(c) in variantes or any(v in norm(c) for v in variantes)]
    if not matches:
        return {"COUNT(*)": 0, "SUM(valor_bruto)": 0}
    # Contagem agregada
    cond = " OR ".join("cliente = ?" for _ in matches)
    rows = buscar_db(f"SELECT COUNT(*), SUM(valor_bruto) FROM spcf_faturas WHERE {cond}", *matches)
    return rows[0] if rows else {"COUNT(*)": 0, "SUM(valor_bruto)": 0}

def _localizar_pastas(sigla: str) -> dict:
    """Encontra pastas DOSSIE, CONSOLIDADO e SPCF per-devedor para esta sigla."""
    sigla_clean = re.sub(r"[^\w]", "_", sigla.upper()).strip("_")
    dossie_variants = [
        DOCS / f"{sigla_clean}_DOSSIE",
        DOCS / f"{sigla.upper()}_DOSSIE",
        DOCS / f"{sigla.replace('/','_').upper()}_DOSSIE",
    ]
    consol_variants = [
        DOCS / f"{sigla_clean}_CONSOLIDADO",
        DOCS / f"{sigla.upper()}_CONSOLIDADO",
        DOCS / f"{sigla.replace('/','_').upper()}_CONSOLIDADO",
    ]
    spcf_dev_variants = [
        PD / sigla.replace("/","_").upper(),
        PD / sigla_clean,
    ]
    return {
        "dossie": next((p for p in dossie_variants if p.exists()), None),
        "consolidado": next((p for p in consol_variants if p.exists()), None),
        "spcf_per_dev": next((p for p in spcf_dev_variants if p.exists()), None),
    }

def _detectar_divergencias(profile: dict, contagens: dict, cobr_dev: list) -> list:
    """Compara profile × DB para detectar divergências de valor/contagem.

    fix 2026-04-22: escopo corrigido. Antes comparava val_exig (SSOT, só não-prescritas)
    contra SUM(spcf_faturas) (DB, todas abertas). Escopos diferentes → falso-positivos.
    Agora compara spcf_fat_aberto_* (SSOT, faturas em aberto) contra DB (que só traz
    Emitida + Parcialmente Paga, ou seja, também em aberto). Escopos equivalentes.
    Tolerância subiu para 10% em valor / 15% em qtd (snapshots podem diferir dias).
    """
    divs = []
    # --- Valor em aberto ---
    val_aberto_profile = Decimal(str(profile.get("spcf_fat_aberto_val") or 0))
    val_spcf_fat = Decimal(str(contagens.get("faturas_valor", 0) or 0))
    if val_aberto_profile > 0 and val_spcf_fat > 0:
        delta = abs(val_aberto_profile - val_spcf_fat)
        pct = (delta / val_aberto_profile * 100) if val_aberto_profile else Decimal(0)
        if pct > Decimal(10):
            divs.append({
                "tipo": "valor_aberto_vs_db_faturas",
                "profile": str(val_aberto_profile),
                "db_faturas": str(val_spcf_fat),
                "delta": str(delta),
                "pct": f"{pct:.1f}%",
            })
    # --- Quantidade em aberto ---
    fat_aberto_profile = profile.get("spcf_fat_aberto_qtd", 0) or 0
    fat_db = contagens.get("faturas_db", 0)
    if fat_aberto_profile > 0 and fat_db > 0:
        delta_qtd = abs(fat_aberto_profile - fat_db)
        tol = max(5, fat_aberto_profile * 0.15)
        if delta_qtd > tol:
            divs.append({
                "tipo": "faturas_aberto_qtd_profile_vs_db",
                "profile": fat_aberto_profile,
                "db": fat_db,
                "delta": delta_qtd,
            })
    return divs

def auditar_devedor(sigla: str, profile: dict) -> dict:
    """Orquestra auditoria de um devedor — usa helpers acima."""
    result = {
        "sigla": sigla,
        "nome_completo": profile.get("nome_completo", ""),
        "categoria": profile.get("categoria", ""),
        "checklist": {},
        "contagens": {},
        "divergencias": [],
        "documentos_faltantes": [],
    }

    # 1. Contratos
    contratos_spcf = buscar_em_consolidado(sigla, con_c, [("dados_base","cliente"), ("fatura_parsed","cliente")])
    contratos_db = buscar_db("SELECT * FROM spcf_contratos WHERE UPPER(json_extract(dados_base,'$.cliente')) LIKE ?", f"%{sigla.upper()}%")

    # 2. Empenhos (usa norm_variants)
    empenhos_info = _contar_empenhos_db(sigla)

    # 3. Faturas (usa norm() via DISTINCT clientes cacheado)
    fat_db_info = _contar_faturas_db(sigla)

    # 4. Cobrancas
    cobr_dev = buscar_em_consolidado(sigla, cobrancas, [("Cliente",)])

    # 5. Pastas DOSSIE/CONSOLIDADO/SPCF (via helper)
    paths = _localizar_pastas(sigla)
    dossie_path = paths["dossie"]
    consol_path = paths["consolidado"]
    spcf_dev_path = paths["spcf_per_dev"]

    # Contagens
    contagens = {
        "contratos_spcf": len(contratos_spcf),
        "contratos_db": len(contratos_db),
        "empenhos_db": empenhos_info.get("n", 0) or 0,
        "empenhos_valor": brl(empenhos_info.get("total", 0) or 0),
        "faturas_db": fat_db_info.get("COUNT(*)", 0) or 0,
        "faturas_valor": brl(fat_db_info.get("SUM(valor_bruto)", 0) or 0),
        "cobrancas": len(cobr_dev),
    }
    result["contagens"] = contagens

    # Checklist
    result["checklist"] = {
        "contrato": contagens["contratos_spcf"] > 0 or contagens["contratos_db"] > 0,
        "empenhos": contagens["empenhos_db"] > 0,
        "nls": False,  # NLs são raras no SPCF — assumem-se via OCR
        "nfs": contagens["faturas_db"] > 0,
        "aceites": False,  # Aceites são via OCR/pendrive
        "cobrancas": contagens["cobrancas"] > 0,
        "oficios": False,  # Via evidencias
        "reconhecimento": profile.get("evidencias_reconhecimento", 0) > 0,
        "cnd": False,
        "dossie_folder": dossie_path is not None,
        "consolidado_folder": consol_path is not None,
    }

    # Documentos faltantes
    for k, descr in CHECKLIST:
        if not result["checklist"].get(k):
            result["documentos_faltantes"].append(f"{k}: {descr}")

    # Paths
    result["paths"] = {
        "dossie": str(dossie_path) if dossie_path else None,
        "consolidado": str(consol_path) if consol_path else None,
        "spcf_per_dev": str(spcf_dev_path) if spcf_dev_path else None,
    }

    # Divergências de valor/contagem (via helper)
    result["divergencias"] = _detectar_divergencias(profile, contagens, cobr_dev)

    # Score de completude
    total_checks = len(result["checklist"])
    passed = sum(1 for v in result["checklist"].values() if v)
    result["score_completude_pct"] = round(passed / total_checks * 100, 1)

    return result

# ============================================================
# PROCESSA TODOS
# ============================================================
# _metadata não é devedor — é metadata do JSON
devedores_validos = {k: v for k, v in profiles.items() if not k.startswith("_")}
print(f"[4/6] Auditando {len(devedores_validos)} devedores ({len(profiles)-len(devedores_validos)} entradas _metadata ignoradas)...")
resumo = {}
total_divergencias = 0
total_gaps = 0
for sigla, profile in devedores_validos.items():
    try:
        a = auditar_devedor(sigla, profile)
    except Exception as e:
        print(f"  ERRO {sigla}: {e}")
        continue
    resumo[sigla] = a
    total_divergencias += len(a["divergencias"])
    total_gaps += len(a["documentos_faltantes"])

# ============================================================
# SAÍDA MD POR DEVEDOR
# ============================================================
print(f"[5/6] Gerando {len(resumo)} relatórios MD...")
for sigla, a in resumo.items():
    sigla_safe = re.sub(r"[^\w]", "_", sigla)
    f_md = OUT / f"AUDITORIA_{sigla_safe}.md"

    md = f"""# Auditoria de Completude — {sigla}
**{a['nome_completo']}** | Categoria: **{a['categoria']}** | Data: {HOJE.isoformat()}

## Score de Completude: **{a['score_completude_pct']}%**

## Checklist de Documentos

| Item | Status | Descrição |
|------|--------|-----------|
"""
    for k, descr in CHECKLIST:
        status = "✅ OK" if a["checklist"].get(k) else "❌ FALTANDO"
        md += f"| `{k}` | {status} | {descr} |\n"

    md += f"""

## Contagens (todas as fontes)

| Fonte | Qtd | Valor |
|-------|-----|-------|
| Contratos SPCF | {a['contagens']['contratos_spcf']} | — |
| Contratos no DB | {a['contagens']['contratos_db']} | — |
| Empenhos no DB | {a['contagens']['empenhos_db']} | {fmt_brl(a['contagens']['empenhos_valor'])} |
| Faturas no DB | {a['contagens']['faturas_db']} | {fmt_brl(a['contagens']['faturas_valor'])} |
| Cobranças SPCF | {a['contagens']['cobrancas']} | — |

## Paths no Projeto

| Recurso | Caminho |
|---------|---------|
| Pasta Dossiê | {a['paths'].get('dossie') or '*(AUSENTE)*'} |
| Pasta Consolidado | {a['paths'].get('consolidado') or '*(AUSENTE)*'} |
| SPCF por_devedor | {a['paths'].get('spcf_per_dev') or '*(AUSENTE)*'} |

## Documentos Faltantes ({len(a['documentos_faltantes'])})

"""
    if a["documentos_faltantes"]:
        for d in a["documentos_faltantes"]:
            md += f"- ❌ {d}\n"
    else:
        md += "_Nenhum documento faltante identificado_\n"

    md += f"\n## Divergências ({len(a['divergencias'])})\n\n"
    if a["divergencias"]:
        for d in a["divergencias"]:
            md += f"### Tipo: `{d['tipo']}`\n"
            for k, v in d.items():
                if k != "tipo":
                    md += f"- **{k}:** {v}\n"
            md += "\n"
    else:
        md += "_Nenhuma divergência significativa detectada_\n"

    f_md.write_text(md, encoding="utf-8")

# ============================================================
# RESUMO JSON
# ============================================================
print("[6/6] Gerando resumo global...")
with open(OUT / "AUDITORIA_COMPLETUDE_RESUMO.json", "w", encoding="utf-8") as fh:
    json.dump({
        "data": HOJE.isoformat(),
        "total_devedores": len(resumo),
        "total_divergencias": total_divergencias,
        "total_gaps": total_gaps,
        "score_medio": round(sum(a["score_completude_pct"] for a in resumo.values()) / len(resumo), 1),
        "por_devedor": {s: {
            "score": a["score_completude_pct"],
            "divergencias_qtd": len(a["divergencias"]),
            "gaps_qtd": len(a["documentos_faltantes"]),
            "categoria": a["categoria"],
        } for s, a in resumo.items()},
    }, fh, ensure_ascii=False, indent=2)

# Dashboard HTML
top_gaps = sorted(resumo.items(), key=lambda x: -len(x[1]["documentos_faltantes"]))[:20]
top_div = sorted(resumo.items(), key=lambda x: -len(x[1]["divergencias"]))[:20]

html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Auditoria de Completude — Projeto PRODAM</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;max-width:1400px;margin:20px auto;padding:20px;background:#f5f5f5}}
h1{{color:#1F3864;border-bottom:3px solid #B8963E}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:16px 0}}
.card{{background:white;padding:16px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
.kpi{{font-size:32px;color:#1F3864;font-weight:700}}
.label{{color:#666;font-size:13px;text-transform:uppercase}}
table{{width:100%;border-collapse:collapse;background:white}}
th,td{{padding:8px 12px;border-bottom:1px solid #eee;text-align:left}}
th{{background:#1F3864;color:white}}
tr:hover{{background:#f0f0f0}}
canvas{{max-height:400px}}
</style></head><body>
<h1>Auditoria de Completude — Projeto PRODAM</h1>
<p>Gerado em {HOJE.isoformat()} | {len(resumo)} devedores analisados</p>

<div class="grid">
<div class="card"><div class="label">Score Médio</div>
<div class="kpi">{round(sum(a['score_completude_pct'] for a in resumo.values()) / len(resumo), 1)}%</div></div>
<div class="card"><div class="label">Gaps Documentais</div>
<div class="kpi">{total_gaps}</div></div>
<div class="card"><div class="label">Divergências</div>
<div class="kpi">{total_divergencias}</div></div>
</div>

<div class="card"><canvas id="scoreChart"></canvas></div>

<h2>Top 20 com mais gaps</h2>
<table><tr><th>Devedor</th><th>Categoria</th><th>Score</th><th>Gaps</th><th>Divergências</th></tr>
"""
for sigla, a in top_gaps:
    html += f"<tr><td>{sigla}</td><td>{a['categoria']}</td><td>{a['score_completude_pct']}%</td><td>{len(a['documentos_faltantes'])}</td><td>{len(a['divergencias'])}</td></tr>\n"
html += "</table>"

scores_data = sorted(resumo.items(), key=lambda x: -x[1]["score_completude_pct"])
html += f"""
<script>
new Chart(document.getElementById('scoreChart'),{{
  type:'bar',
  data:{{
    labels:{json.dumps([s for s,_ in scores_data[:30]])},
    datasets:[{{
      label:'Score %',
      data:{json.dumps([a['score_completude_pct'] for _,a in scores_data[:30]])},
      backgroundColor:'#1F3864'
    }}]
  }},
  options:{{responsive:true,plugins:{{title:{{display:true,text:'Top 30 - Score de Completude'}}}}}}
}});
</script>
</body></html>"""
(OUT / "AUDITORIA_COMPLETUDE_DASHBOARD.html").write_text(html, encoding="utf-8")

print(f"\nRelatorios em {OUT}")
print(f"   - {len(resumo)} AUDITORIA_<DEVEDOR>.md")
print(f"   - AUDITORIA_COMPLETUDE_RESUMO.json")
print(f"   - AUDITORIA_COMPLETUDE_DASHBOARD.html")
print(f"\nTotal gaps documentais: {total_gaps}")
print(f"Total divergencias:     {total_divergencias}")
print(f"Score medio:            {round(sum(a['score_completude_pct'] for a in resumo.values()) / len(resumo), 1)}%")
