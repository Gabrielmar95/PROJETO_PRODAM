"""
Extrai insights a partir do profile_pasta_mae.json e imprime relatório texto.
Também gera dados consolidados para o dashboard e o .docx.
"""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path("/sessions/gallant-focused-brahmagupta/mnt/outputs")
SRC = BASE / "profile_pasta_mae.json"
OUT_CSV = BASE / "insights_devedores.csv"
OUT_INSIGHTS = BASE / "insights_consolidados.json"

data = json.loads(SRC.read_text(encoding="utf-8"))

# --- 1. Overview ---
print("=" * 70)
print("DIAGNÓSTICO — Pasta-mãe PROJETO_PRODAM")
print(f"Gerado em: {data['gerado_em']}")
print("=" * 70)

print(f"\nDevedores com pasta _CONSOLIDADO: {data['n_devedores_pastas']}")

# --- 2. Top-level ---
print("\n--- PASTAS DO TOPO ---")
for nome, info in data["pastas_topo"].items():
    f = info.get("files", 0)
    mb = info.get("size_mb", 0)
    top_ext = ", ".join(f"{k}={v}" for k, v in list(info.get("ext_top10", {}).items())[:3])
    print(f"  {nome:<28} {f:>6} arqs | {mb:>10.2f} MB | {top_ext}")

# --- 3. prodam.db ---
db = data["prodam_db"]
print(f"\n--- prodam.db ({db['tamanho_mb']} MB) ---")
for nome, info in db["tabelas"].items():
    print(f"  {nome:<30} {info['count']:>8} registros | {info['cols']:>3} colunas")
print(f"\n  Views: {', '.join(db['views'])}")

# --- 4. profiles.json ---
pf = data["profiles_json"]
print(f"\n--- profiles.json ({pf.get('n_devedores', 0)} devedores) ---")
print(f"  Regimes: {pf.get('regimes', {})}")
print(f"  Forca probatoria: {pf.get('forca_probatoria', {})}")
print(f"  R$ exigivel total: R$ {pf.get('valor_exigivel_total', 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
print(f"  R$ atualizado total: R$ {pf.get('valor_atualizado_total', 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
print(f"  Campos faltantes: {pf.get('campos_faltantes', {})}")

# --- 5. Cobertura por devedor ---
cons = data["cobertura_consolidado"]
dossie = data["cobertura_dossie"]

# Distribuição de cobertura
bins_cons = {"100%": 0, "80-99%": 0, "50-79%": 0, "20-49%": 0, "0-19%": 0}
for nome, info in cons.items():
    p = info.get("cobertura_pct", 0)
    if p == 100:
        bins_cons["100%"] += 1
    elif p >= 80:
        bins_cons["80-99%"] += 1
    elif p >= 50:
        bins_cons["50-79%"] += 1
    elif p >= 20:
        bins_cons["20-49%"] += 1
    else:
        bins_cons["0-19%"] += 1

print("\n--- COBERTURA DOCUMENTAL (_CONSOLIDADO, 9 subpastas) ---")
for bucket, n in bins_cons.items():
    pct = n / len(cons) * 100 if cons else 0
    print(f"  {bucket:<10} {n:>3} devedores ({pct:.1f}%)")

# Top 10 por arquivos
ranking = sorted(cons.items(), key=lambda x: x[1].get("total_arquivos", 0), reverse=True)
print("\n--- TOP 15 DEVEDORES POR VOLUME DE ARQUIVOS ---")
print(f"  {'Devedor':<22} {'Arquivos':>8} {'Cobertura':>10}")
for nome, info in ranking[:15]:
    print(f"  {nome:<22} {info.get('total_arquivos', 0):>8} {info.get('cobertura_pct', 0):>9.1f}%")

# Bottom 10
print("\n--- BOTTOM 15 DEVEDORES (menor volume) ---")
for nome, info in ranking[-15:]:
    print(f"  {nome:<22} {info.get('total_arquivos', 0):>8} {info.get('cobertura_pct', 0):>9.1f}%")

# Subpastas com maior taxa de lacuna
print("\n--- SUBPASTAS COM MAIORES LACUNAS ---")
gap_por_sub = {sub: 0 for sub in [
    "01_CONTRATOS", "02_EMPENHOS", "03_FATURAS", "04_NOTAS_LIQUIDACAO",
    "05_ACEITES", "06_COBRANCAS", "07_SCRAPING_SPCF", "08_PDFS_ORIGINAIS", "09_RELATORIOS",
]}
for nome, info in cons.items():
    for sub, s_info in info.get("subpastas", {}).items():
        if s_info.get("files", 0) == 0:
            gap_por_sub[sub] += 1
for sub in sorted(gap_por_sub, key=lambda k: gap_por_sub[k], reverse=True):
    n = gap_por_sub[sub]
    pct = n / len(cons) * 100 if cons else 0
    print(f"  {sub:<25} {n:>3} devedores sem arquivos ({pct:.1f}%)")

# DOSSIES
cobertura_dossie_pct = [info.get("cobertura_pct", 0) for info in dossie.values() if info.get("existe")]
tem_dashboard = sum(1 for info in dossie.values() if info.get("existe") and info.get("artefatos", {}).get("dashboard.html"))
tem_auditoria = sum(1 for info in dossie.values() if info.get("existe") and info.get("artefatos", {}).get("AUDITORIA.md"))
tem_llm = sum(1 for info in dossie.values() if info.get("existe") and info.get("artefatos", {}).get("llm"))
print(f"\n--- DOSSIES (artefatos gerados) ---")
print(f"  Devedores com _DOSSIE: {sum(1 for i in dossie.values() if i.get('existe'))}/{len(dossie)}")
print(f"  Com dashboard.html:  {tem_dashboard}")
print(f"  Com AUDITORIA.md:    {tem_auditoria}")
print(f"  Com pasta llm/:      {tem_llm}")
if cobertura_dossie_pct:
    media = sum(cobertura_dossie_pct) / len(cobertura_dossie_pct)
    print(f"  Cobertura media de artefatos: {media:.1f}%")

# --- 6. Gerar CSV com resumo por devedor ---
linhas = ["devedor,arquivos_consolidado,cobertura_consolidado_pct,dossie_existe,dossie_cobertura_pct"]
for nome in data["devedores"]:
    c = cons.get(nome, {})
    d = dossie.get(nome, {})
    linhas.append(
        f"{nome},{c.get('total_arquivos', 0)},{c.get('cobertura_pct', 0)},"
        f"{d.get('existe', False)},{d.get('cobertura_pct', 0) if d.get('existe') else 0}"
    )
OUT_CSV.write_text("\n".join(linhas), encoding="utf-8")
print(f"\n[OK] CSV salvo: {OUT_CSV}")

# --- 7. Benchmark DETRAN ---
print("\n--- BENCHMARK DETRAN (pasta-filha A+) ---")
detran_cons = cons.get("DETRAN", {})
detran_dossie = dossie.get("DETRAN", {})
print(f"  _CONSOLIDADO: {detran_cons.get('total_arquivos', 0)} arqs | cobertura {detran_cons.get('cobertura_pct', 0)}%")
print(f"  _DOSSIE: {detran_dossie.get('total_arquivos', 0)} arqs | cobertura {detran_dossie.get('cobertura_pct', 0)}%")
print("  Subpastas DETRAN:")
for sub, info in detran_cons.get("subpastas", {}).items():
    print(f"    {sub:<25} {info.get('files', 0):>5} arqs | {info.get('size_mb', 0):>8.2f} MB")

# --- 8. Dump insights ---
insights = {
    "bins_cobertura": bins_cons,
    "gap_por_subpasta": gap_por_sub,
    "ranking_arquivos": [{"devedor": n, "arquivos": i.get("total_arquivos", 0), "cobertura": i.get("cobertura_pct", 0)} for n, i in ranking],
    "dossies": {
        "total": sum(1 for i in dossie.values() if i.get("existe")),
        "com_dashboard": tem_dashboard,
        "com_auditoria": tem_auditoria,
        "com_llm": tem_llm,
    },
}
OUT_INSIGHTS.write_text(json.dumps(insights, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n[OK] Insights salvos: {OUT_INSIGHTS}")
