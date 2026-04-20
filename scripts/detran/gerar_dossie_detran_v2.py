"""
Gera dossie DETRAN consolidado cruzando:
  - prodam.db (SQLite, tabelas spcf_*)
  - C:/Users/gabri/Desktop/DETRAN_AUDITORIA_COMPLETA/ (DASHBOARD_DATA.json + subpastas)

Saidas (pasta DOSSIES_MULTIFORMATO/DETRAN/):
  dossie_v2.md | dossie_v2.html | dossie_v2.json | dossie_v2.xlsx | faturas_criticas.csv
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd

ROOT = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")
DB = ROOT / "prodam.db"
BASE = Path(r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA")
DASH = BASE / "DASHBOARD_DATA.json"
OUT = ROOT / "DOSSIES_MULTIFORMATO" / "DETRAN"
OUT.mkdir(parents=True, exist_ok=True)


def brl(v) -> str:
    try:
        v = float(v or 0)
    except (TypeError, ValueError):
        return "R$ 0,00"
    s = f"{v:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def contar_arquivos(pasta: Path) -> dict[str, int]:
    if not pasta.exists():
        return {}
    out: dict[str, int] = {}
    for p in pasta.rglob("*"):
        if p.is_file():
            ext = p.suffix.lower().lstrip(".")
            out[ext] = out.get(ext, 0) + 1
    return out


def coletar_inventario_pastas() -> dict[str, dict]:
    inv: dict[str, dict] = {}
    for sub in sorted(BASE.iterdir()):
        if sub.is_dir() and sub.name[:2].isdigit():
            inv[sub.name] = {
                "total_arquivos": sum(1 for _ in sub.rglob("*") if _.is_file()),
                "por_formato": contar_arquivos(sub),
            }
    return inv


def ler_db() -> dict:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    ctr = [dict(r) for r in c.execute(
        "SELECT id, numero, cliente, tem_tramite_pdf FROM spcf_contratos "
        "WHERE cliente LIKE '%DETRAN%' ORDER BY numero"
    )]
    emp_row = c.execute(
        "SELECT COUNT(*) n, COALESCE(SUM(valor),0) v FROM spcf_empenhos WHERE cliente LIKE '%DETRAN%'"
    ).fetchone()
    emp_por_sit = [dict(r) for r in c.execute(
        "SELECT situacao, COUNT(*) n, COALESCE(SUM(valor),0) v FROM spcf_empenhos "
        "WHERE cliente LIKE '%DETRAN%' GROUP BY situacao ORDER BY v DESC"
    )]
    fat_row = c.execute(
        "SELECT COUNT(*) n, COALESCE(SUM(valor_bruto),0) v FROM spcf_faturas WHERE cliente LIKE '%DETRAN%'"
    ).fetchone()
    fat_sit = [dict(r) for r in c.execute(
        "SELECT situacao, COUNT(*) n, COALESCE(SUM(valor_bruto),0) v FROM spcf_faturas "
        "WHERE cliente LIKE '%DETRAN%' GROUP BY situacao ORDER BY v DESC"
    )]
    fat_cadeia = [dict(r) for r in c.execute(
        "SELECT cadeia_completude, COUNT(*) n, COALESCE(SUM(valor_bruto),0) v "
        "FROM spcf_faturas WHERE cliente LIKE '%DETRAN%' GROUP BY cadeia_completude"
    )]
    fat_por_contrato = [dict(r) for r in c.execute(
        "SELECT contrato_num, COUNT(*) n, COALESCE(SUM(valor_bruto),0) v FROM spcf_faturas "
        "WHERE cliente LIKE '%DETRAN%' GROUP BY contrato_num ORDER BY v DESC"
    )]
    devedor = c.execute(
        "SELECT * FROM devedores WHERE sigla='DETRAN'"
    ).fetchone()
    conn.close()
    return {
        "devedor": dict(devedor) if devedor else {},
        "contratos": ctr,
        "empenhos_total": {"n": emp_row["n"], "v": emp_row["v"]},
        "empenhos_por_situacao": emp_por_sit,
        "faturas_total": {"n": fat_row["n"], "v": fat_row["v"]},
        "faturas_por_situacao": fat_sit,
        "faturas_por_cadeia": fat_cadeia,
        "faturas_por_contrato": fat_por_contrato,
    }


def ler_dashboard() -> dict:
    return json.loads(DASH.read_text(encoding="utf-8"))


def montar_markdown(db: dict, dash: dict, inv: dict) -> str:
    kpi = dash["kpis"]
    presc = dash["prescricao_distribuicao"]
    lines: list[str] = []
    A = lines.append
    A(f"# DOSSIE CONSOLIDADO - DETRAN/AM")
    A(f"_Gerado em {date.today().isoformat()} | fonte: prodam.db + DETRAN_AUDITORIA_COMPLETA_\n")
    A("## 1. IDENTIFICACAO\n")
    A(f"- **Devedor:** {dash['devedor']}")
    A(f"- **CNPJ:** {dash['cnpj']}")
    A(f"- **Ranking portfolio:** #{dash['ranking_portfolio']}")
    A(f"- **Score composto:** {dash['score_composto']:.4f} (A+)")
    A(f"- **Regime execucao:** `{dash['regime_execucao']}` (Tema 253/STF)")
    A(f"- **Blindagem pre-execucao:** {dash['blindagem_status']}\n")

    A("## 2. NUMEROS-CHAVE\n")
    A("| Metrica | prodam.db | DASHBOARD_DATA.json |")
    A("|---|---:|---:|")
    A(f"| Contratos | {len(db['contratos'])} | {kpi['total_contratos']} |")
    A(f"| Empenhos (NEs) | {db['empenhos_total']['n']} | {kpi['total_nes']} |")
    A(f"| Valor empenhos | {brl(db['empenhos_total']['v'])} | {brl(kpi['valor_nes_empenhado'])} |")
    A(f"| Faturas | {db['faturas_total']['n']} | {kpi['total_faturas']} |")
    A(f"| Valor faturas (bruto) | {brl(db['faturas_total']['v'])} | {brl(kpi['valor_bruto_total'])} |")
    A(f"| Valor atualizado | - | {brl(kpi['valor_atualizado_total'])} |")
    A(f"| Fator correcao medio | - | {kpi['fator_correcao_medio']:.4f}x |\n")

    A("## 3. PRESCRICAO (distribuicao)\n")
    A("| Status | Qtde |")
    A("|---|---:|")
    for k, v in presc.items():
        A(f"| {k} | {v} |")
    A("")

    A("## 4. CADEIA DOCUMENTAL 5 ELOS (prodam.db)\n")
    A("| Completude | Faturas | Valor bruto |")
    A("|---|---:|---:|")
    for r in db["faturas_por_cadeia"]:
        A(f"| {r['cadeia_completude']} | {r['n']} | {brl(r['v'])} |")
    A("")

    A("## 5. CONTRATOS (13 ativos/historicos)\n")
    A("| N | Numero | PDF | Indice (dashboard) |")
    A("|---:|---|:-:|---|")
    contratos_dash = dash.get("contratos", {})
    for i, c in enumerate(db["contratos"], 1):
        num = c["numero"]
        info = contratos_dash.get(num, {})
        idx = info.get("indice_correcao") or info.get("indice") or "-"
        pdf = "OK" if c.get("tem_tramite_pdf") else "-"
        A(f"| {i} | {num} | {pdf} | {idx} |")
    A("")

    A("## 6. FATURAS POR CONTRATO (top 10)\n")
    A("| Contrato | Faturas | Valor bruto |")
    A("|---|---:|---:|")
    for r in db["faturas_por_contrato"][:10]:
        A(f"| {r['contrato_num'] or '(sem)'} | {r['n']} | {brl(r['v'])} |")
    A("")

    criticas = dash.get("faturas_criticas_90d", [])
    atencao = dash.get("faturas_atencao_12m", [])
    A(f"## 7. ALERTAS DE PRESCRICAO\n")
    A(f"- Criticas (<90 dias): **{len(criticas)}**")
    A(f"- Atencao (<12 meses): **{len(atencao)}**\n")
    if atencao:
        A("### Top-6 em ATENCAO 12m\n")
        A("| ID | NF | Contrato | Vencimento | Dias | Bruto | Atualizado |")
        A("|---|---|---|---|---:|---:|---:|")
        for f in atencao[:6]:
            A(f"| {f['id']} | {f['nf']} | {f['contrato']} | "
              f"{f['data_vencimento_estimada']} | {f['dias_ate_prescricao']} | "
              f"{brl(f['valor_bruto'])} | {brl(f['valor_atualizado'])} |")
        A("")

    A("## 8. INVENTARIO DA PASTA `DETRAN_AUDITORIA_COMPLETA\\`\n")
    A("| Subpasta | Arquivos | Formatos (top) |")
    A("|---|---:|---|")
    for nome, dados in inv.items():
        fmts = sorted(dados["por_formato"].items(), key=lambda x: -x[1])[:5]
        fmt_str = ", ".join(f"{k}:{v}" for k, v in fmts)
        A(f"| {nome} | {dados['total_arquivos']} | {fmt_str} |")
    A("")

    A("## 9. BASES DE DADOS DE APOIO\n")
    A("- `prodam.db` (raiz PROJETO_PRODAM) - SSOT tabular (8 tabelas, 80k+ registros)")
    A("- `DASHBOARD_DATA.json` (DETRAN_AUDITORIA_COMPLETA) - camada curada p/ dashboard v7.0")
    A("- `01_CONTRATOS/JSON/*.json` - contratos por numero + TAs (LLM-ready)")
    A("- `04_FATURAS/JSON/*.json` - 149 faturas estruturadas")
    A("- `02_NOTAS_EMPENHO/JSON/*.json` - 470 NEs estruturadas\n")

    A("## 10. PROXIMOS PASSOS SUGERIDOS\n")
    A("1. **Distribuir execucao F5** (petition pronta) - regime penhora direta")
    A("2. **Atualizar IGPM BCB real** - re-rodar skill `atualizacao-monetaria-sob-demanda`")
    A("3. **Assinar TRD faltante** - unico gap critico da blindagem (nota 75/100)")
    A("4. **Monitorar 53 faturas em ATENCAO** - primeira prescricao 2026-10-27\n")

    A("---")
    A("_Dossie gerado por `scripts/detran/gerar_dossie_detran_v2.py`_")
    return "\n".join(lines)


def montar_html(md: str) -> str:
    # Converter tabelas MD -> HTML simples; fallback: envolver em <pre>
    try:
        import markdown  # type: ignore
        body = markdown.markdown(md, extensions=["tables"])
    except ImportError:
        body = "<pre>" + md.replace("<", "&lt;") + "</pre>"
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Dossie DETRAN - PRODAM</title>
<style>
body{{font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;max-width:980px;margin:2rem auto;padding:0 1rem;color:#111}}
h1{{border-bottom:3px solid #0a2e52;padding-bottom:.3rem;color:#0a2e52}}
h2{{margin-top:2rem;color:#0a2e52;border-bottom:1px solid #ddd;padding-bottom:.2rem}}
table{{border-collapse:collapse;width:100%;margin:.5rem 0;font-size:13px}}
th,td{{border:1px solid #ccc;padding:6px 10px;text-align:left}}
th{{background:#0a2e52;color:#fff}}
tr:nth-child(even){{background:#f6f8fb}}
code{{background:#eef;padding:2px 5px;border-radius:3px}}
</style></head><body>{body}</body></html>"""


def montar_xlsx(db: dict, dash: dict, path: Path) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        pd.DataFrame([{
            "devedor": dash["devedor"],
            "cnpj": dash["cnpj"],
            "ranking": dash["ranking_portfolio"],
            "score": dash["score_composto"],
            "regime": dash["regime_execucao"],
            "blindagem": dash["blindagem_status"],
            **dash["kpis"],
        }]).to_excel(xl, sheet_name="resumo", index=False)
        pd.DataFrame(db["contratos"]).to_excel(xl, sheet_name="contratos", index=False)
        pd.DataFrame(db["faturas_por_contrato"]).to_excel(xl, sheet_name="faturas_por_contrato", index=False)
        pd.DataFrame(db["faturas_por_cadeia"]).to_excel(xl, sheet_name="cadeia_5_elos", index=False)
        pd.DataFrame(db["empenhos_por_situacao"]).to_excel(xl, sheet_name="empenhos_situacao", index=False)
        pd.DataFrame(dash.get("faturas", [])).to_excel(xl, sheet_name="faturas_full", index=False)
        pd.DataFrame(dash.get("faturas_atencao_12m", [])).to_excel(xl, sheet_name="atencao_12m", index=False)


def main() -> None:
    print("[1/5] lendo prodam.db ...")
    db = ler_db()
    print("[2/5] lendo DASHBOARD_DATA.json ...")
    dash = ler_dashboard()
    print("[3/5] inventariando pasta DETRAN_AUDITORIA_COMPLETA ...")
    inv = coletar_inventario_pastas()

    print("[4/5] gerando arquivos ...")
    md = montar_markdown(db, dash, inv)
    (OUT / "dossie_v2.md").write_text(md, encoding="utf-8")
    (OUT / "dossie_v2.html").write_text(montar_html(md), encoding="utf-8")
    payload = {"gerado_em": date.today().isoformat(), "db": db, "dashboard": dash, "inventario": inv}
    (OUT / "dossie_v2.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    # CSV das faturas em atencao + criticas
    criticas = dash.get("faturas_criticas_90d", []) + dash.get("faturas_atencao_12m", [])
    if criticas:
        pd.DataFrame(criticas).to_csv(OUT / "faturas_criticas.csv", index=False, encoding="utf-8-sig")
    montar_xlsx(db, dash, OUT / "dossie_v2.xlsx")

    print("[5/5] OK. Arquivos em:", OUT)
    for p in sorted(OUT.glob("dossie_v2*")) + sorted(OUT.glob("faturas_criticas*")):
        print("  -", p.name, f"({p.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    sys.exit(main())
