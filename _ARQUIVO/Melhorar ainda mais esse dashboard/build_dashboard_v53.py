#!/usr/bin/env python3
"""Build Dashboard PRODAM v5.3 from SPCF_MAR2026 data - comprehensive standalone HTML."""
import json, csv, os, glob
from collections import defaultdict
from datetime import datetime, timedelta

DATA_DIR = "/home/ubuntu/spcf_data"

# ============================================================
# 1. LOAD ALL DATA SOURCES
# ============================================================

# profiles.json (71 devedores)
with open(f"{DATA_DIR}/profiles.json") as f:
    profiles_raw = json.load(f)

# DASHBOARD_DADOS_FINAIS.json
with open(f"{DATA_DIR}/DASHBOARD_DADOS_FINAIS.json") as f:
    dash_dados = json.load(f)

# BLOCO_B_SERIE_HISTORICA.json
with open(f"{DATA_DIR}/BLOCO_B_SERIE_HISTORICA.json") as f:
    serie_hist = json.load(f)

# DADOS_NOVOS_POR_DEVEDOR.json
with open(f"{DATA_DIR}/DADOS_NOVOS_POR_DEVEDOR.json") as f:
    dados_novos_raw = json.load(f)
dados_novos = dados_novos_raw.get('devedores', dados_novos_raw)

# BLOCO_D_EMPENHOS.json
with open(f"{DATA_DIR}/BLOCO_D_EMPENHOS.json") as f:
    empenhos_data = json.load(f)

# Faturas cruzadas CSVs
faturas_by_dev = {}
faturas_dir = f"{DATA_DIR}/faturas"
total_faturas_cruzadas = 0
for csv_file in sorted(glob.glob(f"{faturas_dir}/*_FATURAS_CRUZADAS.csv")):
    devname = os.path.basename(csv_file).replace("_FATURAS_CRUZADAS.csv", "")
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            rows = list(reader)
            faturas_by_dev[devname] = rows
            total_faturas_cruzadas += len(rows)
    except:
        pass

# ============================================================
# 2. PROCESS PROFILES INTO TABLE DATA
# ============================================================
devs = []
for sigla, p in profiles_raw.items():
    d = {
        'sigla': sigla,
        'nome': p.get('nome_completo', p.get('nome', sigla)),
        'tipo': p.get('tipo', p.get('natureza', '')),
        'val_orig': float(p.get('val_orig', 0) or 0),
        'val_exig': float(p.get('val_exig', 0) or 0),
        'val_atualizado': float(p.get('val_atualizado', 0) or 0),
        'forca': p.get('forca_probatoria', ''),
        'fase': p.get('fase_atual', ''),
        'faturas': int(p.get('faturas_total', 0) or 0),
        'exigiveis': int(p.get('faturas_exigiveis', 0) or 0),
        'prescritas': int(p.get('faturas_prescritas', 0) or 0),
        'emp_2026': float(p.get('emp_2026', 0) or 0),
        'nes_sem_cob': int(p.get('nes_sem_cobertura_qtd', 0) or 0),
        'evidencias': int(p.get('evidencias_reconhecimento', 0) or 0) if isinstance(p.get('evidencias_reconhecimento'), (int, float)) else len(p.get('evidencias_reconhecimento', [])) if isinstance(p.get('evidencias_reconhecimento'), list) else 0,
        'score': float(p.get('score_composto', 0) or 0),
        'cprac': 'Sim' if p.get('elegivel_cprac') else '',
        'blindagem': p.get('blindagem_resultado', ''),
        'prescricao': p.get('data_prescricao_proxima', ''),
        'prox_passo': p.get('proximo_passo', ''),
        'spcf_total': float(p.get('spcf_total_receber', 0) or 0),
        'spcf_perdas': float(p.get('spcf_perdas', 0) or 0),
        'fat_total_hist': float(p.get('faturamento_total_2019_2026', 0) or 0),
        'rec_total_hist': float(p.get('recebimento_total_2019_2026', 0) or 0),
        'taxa_pgto': float(p.get('taxa_pagamento_pct', 0) or 0),
        'padrao': p.get('padrao_inadimplencia', ''),
        'fat_cancel_qtd': int(p.get('fat_canceladas_qtd', 0) or 0),
        'fat_cancel_val': float(p.get('fat_canceladas_val_bruto', 0) or 0),
        'a_empenhar': float(p.get('a_empenhar_2026', 0) or 0),
        'nes_sem_cob_val': float(p.get('nes_sem_cobertura_valor', 0) or 0),
        'contratos': int(p.get('n_contratos', 0) or 0),
    }
    devs.append(d)

# Sort by val_exig descending
devs.sort(key=lambda x: -x['val_exig'])

# ============================================================
# 3. COMPUTE AGGREGATES
# ============================================================
total_val_exig = sum(d['val_exig'] for d in devs)
total_val_orig = sum(d['val_orig'] for d in devs)
total_val_atual = sum(d['val_atualizado'] for d in devs)
total_faturas = sum(d['faturas'] for d in devs)
total_exigiveis = sum(d['exigiveis'] for d in devs)
total_prescritas = sum(d['prescritas'] for d in devs)
total_emp_2026 = sum(d['emp_2026'] for d in devs)
total_nes_sem_cob = sum(d['nes_sem_cob'] for d in devs)
total_evidencias = sum(d['evidencias'] for d in devs)
total_spcf = sum(d['spcf_total'] for d in devs)
total_spcf_perdas = sum(d['spcf_perdas'] for d in devs)
total_fat_hist = sum(d['fat_total_hist'] for d in devs)
total_rec_hist = sum(d['rec_total_hist'] for d in devs)
total_fat_cancel = sum(d['fat_cancel_val'] for d in devs)
total_a_empenhar = sum(d['a_empenhar'] for d in devs)

# Count by forca
forca_counts = defaultdict(int)
forca_vals = defaultdict(float)
for d in devs:
    f = d['forca'] or 'Sem evidencia'
    forca_counts[f] += 1
    forca_vals[f] += d['val_exig']

# Count by fase
fase_counts = defaultdict(int)
for d in devs:
    f = d['fase'] or 'N/A'
    fase_counts[f] += 1

# Count prescritos
prescritos_count = sum(1 for d in devs if d['prescritas'] > 0 and d['exigiveis'] == 0)
prescritos_val = sum(d['val_orig'] for d in devs if d['prescritas'] > 0 and d['exigiveis'] == 0)

# Padrão inadimplência
padrao_counts = defaultdict(int)
for d in devs:
    p = d['padrao'] or 'N/A'
    padrao_counts[p] += 1

# Faturas cruzadas summary
fat_cruzadas_summary = []
for devname, rows in faturas_by_dev.items():
    vigentes = sum(1 for r in rows if r.get('status_prescricao','') == 'VIGENTE')
    prescritas = sum(1 for r in rows if r.get('status_prescricao','') == 'PRESCRITA')
    val_vig = 0
    val_presc = 0
    val_corr = 0
    for r in rows:
        try: v = float(r.get('valor_servicos','0').replace(',','.'))
        except: v = 0
        try: vc = float(r.get('valor_corrigido','0').replace(',','.'))
        except: vc = 0
        if r.get('status_prescricao','') == 'VIGENTE':
            val_vig += v
        else:
            val_presc += v
        val_corr += vc
    
    acoes = defaultdict(int)
    forcas = defaultdict(int)
    for r in rows:
        acoes[r.get('acao_recomendada','N/A')] += 1
        forcas[r.get('forca_probatoria','N/A')] += 1
    
    fat_cruzadas_summary.append({
        'devedor': devname,
        'total': len(rows),
        'vigentes': vigentes,
        'prescritas': prescritas,
        'val_vigente': val_vig,
        'val_prescrito': val_presc,
        'val_corrigido': val_corr,
        'acoes': dict(acoes),
        'forcas': dict(forcas),
    })

fat_cruzadas_summary.sort(key=lambda x: -x['val_vigente'])

# Serie historica - top devedores
serie_top = []
if isinstance(serie_hist, dict):
    for dev, data in serie_hist.items():
        if isinstance(data, dict):
            fat = data.get('faturamento_total', data.get('total_faturamento', 0))
            rec = data.get('recebimento_total', data.get('total_recebimento', 0))
            taxa = data.get('taxa_pagamento', 0)
            padrao = data.get('padrao', data.get('classificacao', ''))
            serie_top.append({'dev': dev, 'fat': fat, 'rec': rec, 'taxa': taxa, 'padrao': padrao})
    serie_top.sort(key=lambda x: -(x['fat'] if isinstance(x['fat'], (int,float)) else 0))

# ============================================================
# 4. URGENCIAS from DASHBOARD_DADOS_FINAIS
# ============================================================
urgencias = dash_dados.get('urgencias', [])

# ============================================================
# 5. CENARIOS FEE
# ============================================================
cenarios = dash_dados.get('cenarios_fee', {})

# ============================================================
# 6. BUILD HTML
# ============================================================

def fmt(v):
    """Format number as Brazilian currency."""
    if v is None or v == 0:
        return '—'
    if abs(v) >= 1e9:
        return f'R$ {v/1e6:,.1f}M'
    if abs(v) >= 1e6:
        return f'R$ {v/1e6:,.1f}M'
    if abs(v) >= 1e3:
        return f'R$ {v:,.2f}'
    return f'R$ {v:,.2f}'

def fmtN(v):
    """Format number without R$."""
    if v is None or v == 0:
        return '0'
    return f'{v:,.2f}'

# DEVS JS array for table
devs_js_rows = []
for i, d in enumerate(devs):
    row = {
        'n': i+1,
        'sigla': d['sigla'],
        'tipo': 'GOV' if d['tipo'] in ['Governo','GOV','governo','Autarquia','Fundação','Secretaria'] else 'PRIV',
        'val_exig': d['val_exig'],
        'val_atual': d['val_atualizado'],
        'forca': d['forca'],
        'fase': d['fase'],
        'faturas': d['faturas'],
        'exig': d['exigiveis'],
        'presc': d['prescritas'],
        'emp26': d['emp_2026'],
        'nes': d['nes_sem_cob'],
        'evid': d['evidencias'],
        'score': round(d['score']*100) if d['score'] < 1 else round(d['score']),
        'cprac': d['cprac'],
        'blind': d['blindagem'],
        'prescricao': d['prescricao'],
        'prox': d['prox_passo'],
        'spcf': d['spcf_total'],
        'perdas': d['spcf_perdas'],
        'padrao': d['padrao'],
        'taxa': d['taxa_pgto'],
    }
    devs_js_rows.append(row)

devs_json = json.dumps(devs_js_rows, ensure_ascii=False)

# Serie historica JS
serie_js_data = []
for s in serie_top[:15]:
    serie_js_data.append({
        'dev': s['dev'],
        'fat': s['fat'] if isinstance(s['fat'], (int,float)) else 0,
        'rec': s['rec'] if isinstance(s['rec'], (int,float)) else 0,
        'taxa': s['taxa'] if isinstance(s['taxa'], (int,float)) else 0,
        'padrao': s['padrao']
    })
serie_json = json.dumps(serie_js_data, ensure_ascii=False)

# Faturas cruzadas JS
fat_cruz_js = json.dumps(fat_cruzadas_summary[:20], ensure_ascii=False, default=str)

# Urgencias JS
urg_js = json.dumps(urgencias, ensure_ascii=False)

# Cenarios JS
cen_js = json.dumps(cenarios, ensure_ascii=False)

# Forca counts JS
forca_js = json.dumps({
    'labels': list(forca_counts.keys()),
    'counts': list(forca_counts.values()),
    'vals': [round(v,2) for v in forca_vals.values()]
}, ensure_ascii=False)

# Fase counts JS
fase_js = json.dumps({
    'labels': list(fase_counts.keys()),
    'counts': list(fase_counts.values())
}, ensure_ascii=False)

# Padrao counts JS
padrao_js = json.dumps({
    'labels': list(padrao_counts.keys()),
    'counts': list(padrao_counts.values())
}, ensure_ascii=False)

# Key metrics for SPCF_MAR2026 visao consolidada
spcf_metrics = {
    'devedores_unicos': 543,
    'devedores_portfolio': 34,
    'devedores_fora': 346,
    'total_receber': 127571242.99,
    'fat_devidas': 4620,
    'fat_devidas_val': 140359863.56,
    'fat_aberto': 2414,
    'fat_aberto_val': 135790715.30,
    'perdas_total': 60281125.60,
    'empenhos_2026_nes': 214,
    'empenhos_2026_val': 41080121.61,
    'canceladas_total': 2097,
    'cancel_x_devidas': 11,
    'cancel_x_aberto': 6,
    'cancel_x_perdas': 47,
    'cancel_val_portfolio': 57553377.64,
    'dupla_baixa_val': 86770322.76,
    'cobranca_indevida': 2362094.52,
    'overlap_pagos_devidas': 1643,
    'empenho_bloco2_val': 52459964.77,
    'a_empenhar_2026': 65830919.47,
    'nes_sem_cobertura': 60,
    'nes_sem_cob_val': 14936371.70,
    'bloco0_nes': 9870,
    'bloco0_val': 1072470794.06,
}
spcf_js = json.dumps(spcf_metrics, ensure_ascii=False)

# ============================================================
# 7. WRITE THE HTML FILE
# ============================================================

html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Dashboard PRODAM — Recuperacao de Creditos v5.3</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #f8f9fc; --bg2: #ffffff; --bg3: #f0f2f8; --text: #1a1d29; --text2: #5a5f7a;
  --accent: #0f1b3d; --accent2: #c8a84e; --accent3: #1e3a6e; --border: #e2e5f0;
  --green: #10b981; --red: #ef4444; --orange: #f59e0b; --blue: #3b82f6;
  --purple: #8b5cf6; --teal: #14b8a6; --pink: #ec4899;
  --shadow: 0 2px 12px rgba(15,27,61,.08); --shadow2: 0 8px 32px rgba(15,27,61,.12);
  --radius: 12px; --radius2: 16px;
}}
[data-theme="dark"] {{
  --bg: #0d1117; --bg2: #161b22; --bg3: #1c2333; --text: #e6edf3; --text2: #8b949e;
  --accent: #1e3a6e; --accent2: #c8a84e; --accent3: #2d5aa0; --border: #30363d;
  --shadow: 0 2px 12px rgba(0,0,0,.3); --shadow2: 0 8px 32px rgba(0,0,0,.4);
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',system-ui,sans-serif; background:var(--bg); color:var(--text); line-height:1.5; }}

/* SIDEBAR */
.sidebar {{ position:fixed; left:0; top:0; bottom:0; width:220px; background:var(--accent); color:#fff;
  overflow-y:auto; z-index:100; padding:16px 0; transition:transform .3s; }}
.sidebar h2 {{ font-size:14px; font-weight:800; text-transform:uppercase; letter-spacing:1.5px;
  padding:8px 16px; color:var(--accent2); margin-bottom:4px; }}
.sidebar .brand {{ padding:12px 16px 16px; border-bottom:1px solid rgba(255,255,255,.1); margin-bottom:8px; }}
.sidebar .brand h1 {{ font-size:15px; font-weight:800; color:#fff; letter-spacing:1px; }}
.sidebar .brand p {{ font-size:10px; color:rgba(255,255,255,.5); margin-top:2px; }}
.sidebar a {{ display:block; padding:6px 16px; color:rgba(255,255,255,.7); text-decoration:none;
  font-size:11px; transition:all .2s; border-left:3px solid transparent; }}
.sidebar a:hover,.sidebar a.active {{ color:#fff; background:rgba(255,255,255,.08); border-left-color:var(--accent2); }}
.sidebar .cat {{ font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px;
  color:rgba(255,255,255,.35); padding:12px 16px 4px; }}

/* MAIN */
.main {{ margin-left:220px; padding:20px 28px 60px; max-width:1400px; }}

/* HEADER */
.header {{ display:flex; align-items:center; justify-content:space-between; padding:10px 20px;
  background:var(--bg2); border-radius:var(--radius); box-shadow:var(--shadow); margin-bottom:20px; flex-wrap:wrap; gap:8px; }}
.header .breadcrumb {{ font-size:12px; color:var(--text2); }}
.header .badges {{ display:flex; gap:8px; flex-wrap:wrap; }}
.header .badge {{ font-size:11px; padding:3px 10px; border-radius:20px; font-weight:600; }}
.badge-blue {{ background:#dbeafe; color:#1e40af; }}
.badge-red {{ background:#fecaca; color:#991b1b; }}
.badge-green {{ background:#d1fae5; color:#065f46; }}
.badge-gold {{ background:#fef3c7; color:#92400e; }}
[data-theme="dark"] .badge-blue {{ background:#1e3a5f; color:#93c5fd; }}
[data-theme="dark"] .badge-red {{ background:#5f1a1a; color:#fca5a5; }}
[data-theme="dark"] .badge-green {{ background:#064e3b; color:#6ee7b7; }}
[data-theme="dark"] .badge-gold {{ background:#78350f; color:#fcd34d; }}
.header .actions {{ display:flex; gap:8px; }}
.header .actions button {{ padding:6px 14px; border:none; border-radius:8px; font-size:12px; font-weight:600;
  cursor:pointer; transition:all .2s; }}
#themeToggle {{ background:var(--bg3); color:var(--text); }}
#exportBtn {{ background:var(--accent2); color:#fff; }}

/* SECTIONS */
section {{ margin-bottom:28px; animation:fadeIn .6s ease-out; }}
@keyframes fadeIn {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:translateY(0); }} }}
.section-title {{ font-size:18px; font-weight:800; color:var(--text); margin-bottom:16px;
  padding-bottom:8px; border-bottom:2px solid var(--accent2); display:flex; align-items:center; gap:8px; }}
.section-subtitle {{ font-size:13px; color:var(--text2); margin-left:auto; font-weight:400; }}

/* CARDS GRID */
.kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin-bottom:20px; }}
.kpi {{ background:var(--bg2); border-radius:var(--radius); padding:16px; box-shadow:var(--shadow);
  border-left:4px solid var(--accent2); transition:transform .2s; }}
.kpi:hover {{ transform:translateY(-2px); box-shadow:var(--shadow2); }}
.kpi .label {{ font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--text2); }}
.kpi .value {{ font-size:24px; font-weight:800; color:var(--accent2); margin:4px 0; }}
.kpi .sub {{ font-size:11px; color:var(--text2); }}
.kpi.red {{ border-left-color:var(--red); }}
.kpi.red .value {{ color:var(--red); }}
.kpi.green {{ border-left-color:var(--green); }}
.kpi.green .value {{ color:var(--green); }}
.kpi.blue {{ border-left-color:var(--blue); }}
.kpi.blue .value {{ color:var(--blue); }}
.kpi.purple {{ border-left-color:var(--purple); }}
.kpi.purple .value {{ color:var(--purple); }}

/* ALERT BOX */
.alert-box {{ background:linear-gradient(135deg,#1a0a0a,#2d1515); color:#fca5a5; border-radius:var(--radius2);
  padding:20px; margin-bottom:20px; border:1px solid rgba(239,68,68,.3); }}
[data-theme="dark"] .alert-box {{ background:linear-gradient(135deg,#1a0505,#2d0f0f); }}
.alert-box h3 {{ color:#f87171; font-size:16px; margin-bottom:10px; }}
.alert-box .alert-item {{ padding:6px 0; font-size:13px; border-bottom:1px solid rgba(255,255,255,.05); }}
.alert-box .alert-item:last-child {{ border:none; }}
.alert-badge {{ display:inline-block; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:700; margin:0 4px; }}
.alert-badge.bloq {{ background:#dc2626; color:#fff; }}
.alert-badge.urg {{ background:#f59e0b; color:#000; }}
.alert-badge.d {{ background:#6366f1; color:#fff; }}

/* CHARTS */
.charts-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(420px,1fr)); gap:16px; margin-bottom:20px; }}
.chart-box {{ background:var(--bg2); border-radius:var(--radius); padding:16px; box-shadow:var(--shadow); }}
.chart-box h4 {{ font-size:13px; font-weight:700; margin-bottom:10px; color:var(--text); }}
.chart-wrap {{ position:relative; height:320px; }}

/* TIMELINE */
.timeline {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:20px; }}
.tl-item {{ background:var(--bg2); border-radius:var(--radius); padding:12px 16px; box-shadow:var(--shadow);
  border-left:4px solid var(--red); min-width:200px; flex:1; }}
.tl-item.warn {{ border-left-color:var(--orange); }}
.tl-item .tl-badge {{ font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px;
  background:var(--red); color:#fff; display:inline-block; margin-bottom:4px; }}
.tl-item.warn .tl-badge {{ background:var(--orange); color:#000; }}
.tl-item .tl-dev {{ font-size:13px; font-weight:700; }}
.tl-item .tl-val {{ font-size:15px; font-weight:800; color:var(--accent2); }}

/* HEATMAP */
.heatmap {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:20px; }}
.hm-cell {{ padding:8px 10px; border-radius:8px; font-size:11px; font-weight:700; color:#fff;
  text-align:center; min-width:80px; transition:transform .2s; cursor:default; }}
.hm-cell:hover {{ transform:scale(1.05); }}
.hm-cell .hm-score {{ font-size:14px; display:block; }}

/* FLOW */
.flow-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:10px; margin-bottom:20px; }}
.flow-card {{ background:var(--bg2); border-radius:var(--radius); padding:14px; text-align:center;
  box-shadow:var(--shadow); position:relative; }}
.flow-card .flow-label {{ font-size:10px; font-weight:700; text-transform:uppercase; color:var(--text2); }}
.flow-card .flow-val {{ font-size:20px; font-weight:800; color:var(--accent2); margin:4px 0; }}
.flow-card .flow-sub {{ font-size:10px; color:var(--text2); }}
.flow-arrow {{ position:absolute; right:-14px; top:50%; transform:translateY(-50%); font-size:18px; color:var(--accent2); }}

/* INSIGHTS */
.insights-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(350px,1fr)); gap:14px; margin-bottom:20px; }}
.insight-card {{ background:var(--bg2); border-radius:var(--radius); padding:16px; box-shadow:var(--shadow);
  border-top:3px solid var(--accent2); }}
.insight-card.critical {{ border-top-color:var(--red); }}
.insight-card h4 {{ font-size:14px; font-weight:700; color:var(--text); margin-bottom:6px; }}
.insight-card p {{ font-size:12px; color:var(--text2); line-height:1.6; }}
.insight-tags {{ display:flex; gap:6px; margin-top:8px; flex-wrap:wrap; }}
.insight-tag {{ font-size:10px; padding:2px 8px; border-radius:4px; background:var(--bg3); color:var(--text2); font-weight:600; }}

/* SPCF METRICS */
.spcf-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-bottom:20px; }}
.spcf-card {{ background:var(--bg2); border-radius:var(--radius); padding:14px; box-shadow:var(--shadow); text-align:center; }}
.spcf-card .spcf-label {{ font-size:10px; font-weight:700; text-transform:uppercase; color:var(--text2); }}
.spcf-card .spcf-val {{ font-size:22px; font-weight:800; margin:4px 0; }}
.spcf-card .spcf-sub {{ font-size:10px; color:var(--text2); }}

/* TABLE */
.table-container {{ background:var(--bg2); border-radius:var(--radius); box-shadow:var(--shadow);
  overflow-x:auto; margin-bottom:20px; }}
.filters {{ display:flex; gap:10px; padding:12px 16px; flex-wrap:wrap; align-items:center; background:var(--bg3);
  border-radius:var(--radius) var(--radius) 0 0; }}
.filters select,.filters input {{ padding:6px 10px; border:1px solid var(--border); border-radius:6px;
  font-size:12px; background:var(--bg2); color:var(--text); }}
.filters button {{ padding:6px 12px; border:1px solid var(--border); border-radius:6px; background:var(--bg2);
  color:var(--text); cursor:pointer; font-size:12px; }}
table {{ width:100%; border-collapse:collapse; font-size:11px; }}
th {{ background:var(--accent); color:#fff; padding:8px 6px; text-align:left; cursor:pointer;
  font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; white-space:nowrap; position:sticky; top:0; }}
th:hover {{ background:var(--accent3); }}
td {{ padding:6px; border-bottom:1px solid var(--border); white-space:nowrap; }}
tr:hover {{ background:var(--bg3); }}
.tag {{ display:inline-block; padding:1px 6px; border-radius:4px; font-size:9px; font-weight:700; }}
.tag-forte {{ background:#d1fae5; color:#065f46; }}
.tag-media {{ background:#fef3c7; color:#92400e; }}
.tag-fraca {{ background:#fecaca; color:#991b1b; }}
.tag-f0 {{ background:#e0e7ff; color:#3730a3; }}
.tag-f3 {{ background:#fef3c7; color:#92400e; }}
.tag-f5 {{ background:#d1fae5; color:#065f46; }}
[data-theme="dark"] .tag-forte {{ background:#064e3b; color:#6ee7b7; }}
[data-theme="dark"] .tag-media {{ background:#78350f; color:#fcd34d; }}
[data-theme="dark"] .tag-fraca {{ background:#7f1d1d; color:#fca5a5; }}

/* FOOTER */
.footer {{ text-align:center; padding:20px; font-size:11px; color:var(--text2); border-top:1px solid var(--border); }}

/* RESPONSIVE */
@media(max-width:768px) {{
  .sidebar {{ transform:translateX(-100%); }}
  .main {{ margin-left:0; padding:12px; }}
  .charts-grid {{ grid-template-columns:1fr; }}
  .kpi-grid {{ grid-template-columns:repeat(2,1fr); }}
}}
</style>
</head>
<body>

<!-- SIDEBAR -->
<nav class="sidebar">
  <div class="brand">
    <h1>RECUPERACAO DE CREDITOS</h1>
    <p>PRODAM S.A. &middot; Contrato 002/2026</p>
  </div>
  <div class="cat">VISAO GERAL</div>
  <a href="#alertas">&#9888; Alertas Criticos</a>
  <a href="#kpis">&#9632; Indicadores-Chave</a>
  <a href="#timeline">&#9200; Timeline Prescricoes</a>
  <div class="cat">ANALISE</div>
  <a href="#ranking">&#9650; Ranking Top 15</a>
  <a href="#forca">&#9673; Forca Probatoria</a>
  <a href="#pipeline">&#9654; Pipeline Fases</a>
  <a href="#prescricao">&#9675; Mapa Prescricao</a>
  <div class="cat">FINANCEIRO</div>
  <a href="#faturamento">&#9638; Faturamento</a>
  <a href="#empenhos">&#9670; Empenhos 2026</a>
  <a href="#cenarios">&#9733; Cenarios</a>
  <div class="cat">SPCF MAR/2026</div>
  <a href="#spcf-visao">&#8660; Visao SPCF</a>
  <a href="#spcf-canceladas">&#9888; Canceladas &amp; Inconsist.</a>
  <a href="#spcf-empenhos">&#9670; Empenhos Detalhados</a>
  <a href="#spcf-serie">&#9632; Serie Historica</a>
  <div class="cat">OPERACIONAL</div>
  <a href="#vias">&#9656; Vias Processuais</a>
  <a href="#heatmap">&#9618; Mapa de Risco</a>
  <a href="#tabela">&#9776; Tabela Completa</a>
  <div class="cat">DADOS REAIS</div>
  <a href="#fat-cruzadas">&#9776; Faturas Cruzadas</a>
  <a href="#fluxo">&#9654; Fluxo Portfolio</a>
  <a href="#insights">&#9733; Insights &amp; Acoes</a>
</nav>

<!-- MAIN -->
<div class="main">

<!-- HEADER -->
<div class="header">
  <span class="breadcrumb">PRODAM &rsaquo; Recuperacao de Creditos &rsaquo; <strong>Dashboard v5.3</strong></span>
  <div class="badges">
    <span class="badge badge-blue">{len(devs)} devedores</span>
    <span class="badge badge-red">&bull; {sum(1 for d in devs if d["prescritas"]>0)} com prescricao</span>
    <span class="badge badge-green">&bull; SPCF Mar/2026</span>
    <span class="badge badge-gold">&bull; {total_faturas_cruzadas} faturas cruzadas</span>
  </div>
  <div class="actions">
    <button id="themeToggle" title="Alternar tema">&#9790; Tema</button>
    <button id="exportBtn" title="Exportar CSV">&#8681; Exportar</button>
  </div>
</div>

<!-- ALERTAS -->
<section id="alertas">
<div class="alert-box">
  <h3>&#9888; ALERTAS CRITICOS</h3>
  <div class="alert-item">&bull; <strong>PROCURACAO PENDENTE</strong> — Bloqueador #1 para todas as notificacoes e atos formais. <span class="alert-badge bloq">BLOQUEADOR</span></div>
  <div class="alert-item">&bull; <strong>{sum(1 for d in devs if d['prescritas']>0 and d['exigiveis']==0)} devedores com prescricao VENCIDA</strong> (cutoff 20/03) — R$ {prescritos_val/1e6:,.1f}M em risco</div>
  <div class="alert-item">&bull; <strong>SES/SUSAM</strong> — Of.129/2021 prescreve ~13/05/2026 <span class="alert-badge d">D+42</span> — R$ 14,7M + 60 NEs sem cobertura contratual (R$ 14,9M)</div>
  <div class="alert-item">&bull; <strong>Acordo SEFAZ/SES</strong> — deadline 15/04/2026 <span class="alert-badge d">D+14</span> — R$ 30M</div>
  <div class="alert-item">&bull; <strong>Overlap PAGA&times;DEVIDAS</strong>: 1.643 faturas em ambas as listas — depuracao obrigatoria antes de notificacao</div>
  <div class="alert-item">&bull; <strong>Dupla Baixa Contabil</strong>: 47 faturas canceladas &times; perdas = R$ {spcf_metrics['dupla_baixa_val']/1e6:,.1f}M — auditoria necessaria</div>
  <div class="alert-item">&bull; <strong>ADS</strong> — prescreve em 12/04/2026 <span class="alert-badge d">D+11</span> — 18 faturas, R$ 61K — NOTIFICAR 48H</div>
</div>
</section>

<!-- KPIs -->
<section id="kpis">
<div class="section-title">&#9632; Indicadores-Chave de Performance <span class="section-subtitle">Atualizado 01/04/2026</span></div>
<div class="kpi-grid">
  <div class="kpi"><div class="label">Valor Exigivel Total</div><div class="value">R$ {total_val_exig/1e6:,.1f}M</div><div class="sub">{len(devs)} devedores ativos</div></div>
  <div class="kpi blue"><div class="label">Valor Atualizado</div><div class="value">R$ {total_val_atual/1e6:,.1f}M</div><div class="sub">Com correcao monetaria + juros</div></div>
  <div class="kpi green"><div class="label">Fee Estimado (20%)</div><div class="value">R$ {cenarios.get('base_40pct',{}).get('fee_20pct',0)/1e6:,.1f}M</div><div class="sub">Cenario base (40% recuperacao)</div></div>
  <div class="kpi red"><div class="label">Prescricao Vencida</div><div class="value">{sum(1 for d in devs if d["prescritas"]>0 and d["exigiveis"]==0)}</div><div class="sub">R$ {prescritos_val/1e6:,.1f}M em risco imediato</div></div>
  <div class="kpi"><div class="label">Forca Forte</div><div class="value">{forca_counts.get("FORTE",0)}</div><div class="sub">R$ {forca_vals.get("FORTE",0)/1e6:,.1f}M ({forca_vals.get("FORTE",0)/total_val_exig*100:.0f}% do valor)</div></div>
  <div class="kpi purple"><div class="label">NEs sem Cobertura</div><div class="value">{total_nes_sem_cob}</div><div class="sub">R$ {sum(d['nes_sem_cob_val'] for d in devs)/1e6:,.1f}M expostos</div></div>
  <div class="kpi blue"><div class="label">Total Faturas</div><div class="value">{total_faturas:,}</div><div class="sub">{total_exigiveis} exigiveis + {total_prescritas} prescritas</div></div>
  <div class="kpi"><div class="label">SPCF Total a Receber</div><div class="value">R$ {spcf_metrics['total_receber']/1e6:,.1f}M</div><div class="sub">{spcf_metrics['fat_devidas']} faturas devidas</div></div>
  <div class="kpi red"><div class="label">Perdas SPCF</div><div class="value">R$ {spcf_metrics['perdas_total']/1e6:,.1f}M</div><div class="sub">Baixadas como perdas</div></div>
  <div class="kpi green"><div class="label">Empenhos 2026</div><div class="value">R$ {spcf_metrics['empenhos_2026_val']/1e6:,.1f}M</div><div class="sub">{spcf_metrics['empenhos_2026_nes']} NEs — reconhecimento tacito</div></div>
</div>
</section>

<!-- TIMELINE -->
<section id="timeline">
<div class="section-title">&#9200; Timeline de Prescricoes Criticas</div>
<div class="timeline">'''

# Add urgencias to timeline
for u in urgencias:
    cls = '' if u.get('dias',0) < 30 else ' warn'
    html += f'''
  <div class="tl-item{cls}">
    <span class="tl-badge">D+{u.get("dias",0)} ({u.get("prescreve_em","")})</span>
    <div class="tl-dev">{u.get("devedor","")}</div>
    <div>{u.get("faturas",0)} faturas</div>
    <div class="tl-val">R$ {u.get("valor",0)/1e6:,.1f}M</div>
    <div style="font-size:10px;color:var(--text2)">{u.get("acao","")}</div>
  </div>'''

# Add more timeline items from profiles with prescricao data
for d in devs:
    if d['prescricao'] and d['sigla'] not in [u.get('devedor','') for u in urgencias]:
        try:
            pdate = datetime.strptime(d['prescricao'], '%Y-%m-%d')
            days = (pdate - datetime(2026,4,1)).days
            if 0 < days < 365:
                html += f'''
  <div class="tl-item warn">
    <span class="tl-badge">D+{days} ({d["prescricao"]})</span>
    <div class="tl-dev">{d["sigla"]}</div>
    <div>{d["exigiveis"]} faturas exigiveis</div>
    <div class="tl-val">R$ {d["val_exig"]/1e6:,.1f}M</div>
  </div>'''
        except:
            pass

html += f'''
</div>
</section>

<!-- RANKING & FORCA -->
<section id="ranking">
<div class="section-title">&#9650; Ranking &amp; Forca Probatoria</div>
<div class="charts-grid">
  <div class="chart-box"><h4>Top 15 Devedores por Valor Exigivel</h4><div class="chart-wrap"><canvas id="chartRanking"></canvas></div></div>
  <div class="chart-box"><h4>Distribuicao por Forca Probatoria</h4><div class="chart-wrap"><canvas id="chartForca"></canvas></div></div>
</div>
</section>

<section id="forca"></section>

<!-- PIPELINE -->
<section id="pipeline">
<div class="charts-grid">
  <div class="chart-box"><h4>Pipeline de Fases</h4><div class="chart-wrap"><canvas id="chartPipeline"></canvas></div></div>
  <div class="chart-box" id="prescricao"><h4>Mapa de Prescricao (Bubble)</h4><div class="chart-wrap"><canvas id="chartPresc"></canvas></div></div>
</div>
</section>

<!-- FATURAMENTO -->
<section id="faturamento">
<div class="section-title">&#9638; Analise Financeira</div>
<div class="charts-grid">
  <div class="chart-box"><h4>Faturamento vs Recebimento (Top 10)</h4><div class="chart-wrap"><canvas id="chartFatRec"></canvas></div></div>
  <div class="chart-box" id="empenhos"><h4>Empenhos 2026 + NEs sem Cobertura</h4><div class="chart-wrap"><canvas id="chartEmp"></canvas></div></div>
</div>
</section>

<!-- CENARIOS -->
<section id="cenarios">
<div class="charts-grid">
  <div class="chart-box"><h4>Cenarios de Recuperacao &amp; Fee</h4><div class="chart-wrap"><canvas id="chartCenarios"></canvas></div></div>
  <div class="chart-box"><h4>Padrao de Inadimplencia</h4><div class="chart-wrap"><canvas id="chartPadrao"></canvas></div></div>
</div>
</section>

<!-- SPCF VISAO -->
<section id="spcf-visao">
<div class="section-title">&#8660; Visao Consolidada SPCF Mar/2026 <span class="section-subtitle">Snapshot 29/03/2026 — 6 Blocos + Extraido</span></div>
<div class="spcf-grid">
  <div class="spcf-card"><div class="spcf-label">Devedores Unicos</div><div class="spcf-val" style="color:var(--blue)">543</div><div class="spcf-sub">Todos no SPCF</div></div>
  <div class="spcf-card"><div class="spcf-label">Portfolio Mapeado</div><div class="spcf-val" style="color:var(--green)">34</div><div class="spcf-sub">De 71 no profiles.json</div></div>
  <div class="spcf-card"><div class="spcf-label">Fora do Portfolio</div><div class="spcf-val" style="color:var(--orange)">346</div><div class="spcf-sub">R$ 24,8M em dividas</div></div>
  <div class="spcf-card"><div class="spcf-label">Total a Receber</div><div class="spcf-val" style="color:var(--accent2)">R$ 127,6M</div><div class="spcf-sub">B1-03 Geral</div></div>
  <div class="spcf-card"><div class="spcf-label">Faturas Devidas</div><div class="spcf-val" style="color:var(--red)">4.620</div><div class="spcf-sub">R$ 140,4M (B1-05)</div></div>
  <div class="spcf-card"><div class="spcf-label">Faturas em Aberto</div><div class="spcf-val" style="color:var(--blue)">2.414</div><div class="spcf-sub">R$ 135,8M (B2-05)</div></div>
  <div class="spcf-card"><div class="spcf-label">Perdas Totais</div><div class="spcf-val" style="color:var(--red)">R$ 60,3M</div><div class="spcf-sub">B1-01 + B3-06</div></div>
  <div class="spcf-card"><div class="spcf-label">Empenhos 2026</div><div class="spcf-val" style="color:var(--green)">R$ 41,1M</div><div class="spcf-sub">214 NEs</div></div>
  <div class="spcf-card"><div class="spcf-label">A Empenhar 2026</div><div class="spcf-val" style="color:var(--purple)">R$ 65,8M</div><div class="spcf-sub">Obrigacao futura</div></div>
  <div class="spcf-card"><div class="spcf-label">Bloco 0 NEs</div><div class="spcf-val" style="color:var(--teal)">9.870</div><div class="spcf-sub">R$ 1,07B operacional</div></div>
</div>
<div class="charts-grid">
  <div class="chart-box"><h4>SPCF: Portfolio vs Fora do Portfolio</h4><div class="chart-wrap"><canvas id="chartSpcfPortfolio"></canvas></div></div>
  <div class="chart-box"><h4>SPCF: Faturas por Status</h4><div class="chart-wrap"><canvas id="chartSpcfFaturas"></canvas></div></div>
</div>
</section>

<!-- SPCF CANCELADAS -->
<section id="spcf-canceladas">
<div class="section-title">&#9888; Canceladas &amp; Inconsistencias SPCF</div>
<div class="kpi-grid">
  <div class="kpi red"><div class="label">Faturas Canceladas</div><div class="value">2.097</div><div class="sub">Total no sistema</div></div>
  <div class="kpi red"><div class="label">Cancel. x Devidas</div><div class="value">11</div><div class="sub">GRAVE — em cobranca mas cancelada</div></div>
  <div class="kpi red"><div class="label">Cancel. x Perdas</div><div class="value">47</div><div class="sub">CRITICA — dupla baixa contabil</div></div>
  <div class="kpi"><div class="label">Val. Cancelado (Portf.)</div><div class="value">R$ 57,6M</div><div class="sub">1.015 faturas do portfolio</div></div>
  <div class="kpi red"><div class="label">Dupla Baixa</div><div class="value">R$ 86,8M</div><div class="sub">Cruzamento D impacto</div></div>
  <div class="kpi"><div class="label">Overlap Paga x Devida</div><div class="value">1.643</div><div class="sub">Depuracao obrigatoria</div></div>
</div>
<div class="charts-grid">
  <div class="chart-box"><h4>Inconsistencias por Tipo de Cruzamento</h4><div class="chart-wrap"><canvas id="chartInconsist"></canvas></div></div>
  <div class="chart-box"><h4>Top Devedores com Canceladas em Perdas</h4><div class="chart-wrap"><canvas id="chartCancelPerdas"></canvas></div></div>
</div>
</section>

<!-- SPCF EMPENHOS -->
<section id="spcf-empenhos">
<div class="section-title">&#9670; Empenhos Detalhados — Bloco 0 vs Bloco 2</div>
<div class="kpi-grid">
  <div class="kpi"><div class="label">Bloco 2 Contratos</div><div class="value">248</div><div class="sub">96 clientes, R$ 259,7M global</div></div>
  <div class="kpi blue"><div class="label">Bloco 0 NEs</div><div class="value">9.870</div><div class="sub">110 clientes, R$ 1,07B</div></div>
  <div class="kpi green"><div class="label">Empenho 2026</div><div class="value">R$ 52,5M</div><div class="sub">Bloco 2 gerencial</div></div>
  <div class="kpi purple"><div class="label">A Empenhar 2026</div><div class="value">R$ 65,8M</div><div class="sub">Reconhecimento futuro</div></div>
  <div class="kpi red"><div class="label">NEs SEM COBERTURA</div><div class="value">60</div><div class="sub">R$ 14,9M — Art. 202 VI CC</div></div>
</div>
<div class="charts-grid">
  <div class="chart-box"><h4>Top 10 Devedores — Empenho Operacional (Bloco 0)</h4><div class="chart-wrap"><canvas id="chartEmpBloco0"></canvas></div></div>
  <div class="chart-box"><h4>Top 10 Devedores — Empenho 2026 (NEs)</h4><div class="chart-wrap"><canvas id="chartEmp2026"></canvas></div></div>
</div>
</section>

<!-- SERIE HISTORICA -->
<section id="spcf-serie">
<div class="section-title">&#9632; Serie Historica — Faturamento vs Recebimento (87 meses)</div>
<div class="charts-grid">
  <div class="chart-box"><h4>Top 15 — Faturamento Total (Jan/2019 a Mar/2026)</h4><div class="chart-wrap"><canvas id="chartSerieHist"></canvas></div></div>
  <div class="chart-box"><h4>Taxa de Pagamento por Devedor (%)</h4><div class="chart-wrap"><canvas id="chartTaxaPgto"></canvas></div></div>
</div>
</section>

<!-- VIAS PROCESSUAIS -->
<section id="vias">
<div class="section-title">&#9656; Vias Processuais &amp; Padrao</div>
<div class="charts-grid">
  <div class="chart-box"><h4>Vias Processuais Recomendadas</h4><div class="chart-wrap"><canvas id="chartVias"></canvas></div></div>
  <div class="chart-box"><h4>NEs sem Cobertura Contratual</h4><div class="chart-wrap"><canvas id="chartNSC"></canvas></div></div>
</div>
</section>

<!-- HEATMAP -->
<section id="heatmap">
<div class="section-title">&#9618; Mapa de Calor — Score de Risco</div>
<div class="heatmap" id="heatmapContainer"></div>
</section>

<!-- TABELA -->
<section id="tabela">
<div class="section-title">&#9776; Tabela Completa — {len(devs)} Devedores <span class="section-subtitle" id="tableCount">{len(devs)} registros</span></div>
<div class="table-container">
  <div class="filters">
    <select id="fTipo"><option value="">Todos</option><option value="GOV">Governo</option><option value="PRIV">Privada</option></select>
    <select id="fForca"><option value="">Todas</option><option value="FORTE">Forte</option><option value="MEDIA">Media</option><option value="FRACA">Fraca</option><option value="Sem evidencia">Sem evidencia</option></select>
    <select id="fFase"><option value="">Todas</option><option value="F0">F0</option><option value="F0 Diagnostico">F0 Diagnostico</option><option value="F3">F3</option><option value="F5">F5</option></select>
    <select id="fPresc"><option value="">Todas</option><option value="vencida">Vencida</option><option value="urgente">Urgente (&lt;90d)</option></select>
    <select id="fCprac"><option value="">Todos</option><option value="Sim">Elegivel</option></select>
    <input id="fBusca" type="text" placeholder="Nome ou sigla...">
    <button id="filterReset">&#8634; Limpar</button>
  </div>
  <div style="max-height:600px;overflow-y:auto">
  <table id="mainTable">
    <thead><tr>
      <th data-col="n"># &#9650;</th>
      <th data-col="sigla">DEVEDOR &#9650;</th>
      <th data-col="tipo">TIPO &#9650;</th>
      <th data-col="val_exig">VAL.EXIGIVEL &#9660;</th>
      <th data-col="val_atual">VAL.ATUALIZADO &#9650;</th>
      <th data-col="forca">FORCA &#9650;</th>
      <th data-col="fase">FASE &#9650;</th>
      <th data-col="faturas">FATURAS &#9650;</th>
      <th data-col="exig">EXIG. &#9650;</th>
      <th data-col="presc">PRESC. &#9650;</th>
      <th data-col="emp26">EMP.2026 &#9650;</th>
      <th data-col="nes">NES S/COB &#9650;</th>
      <th data-col="score">SCORE &#9650;</th>
      <th data-col="cprac">CPRAC &#9650;</th>
      <th data-col="spcf">SPCF RECEBER &#9650;</th>
      <th data-col="perdas">PERDAS &#9650;</th>
      <th data-col="padrao">PADRAO &#9650;</th>
      <th data-col="taxa">TAXA% &#9650;</th>
      <th data-col="prox">PROX.PASSO &#9650;</th>
    </tr></thead>
    <tbody id="tableBody"></tbody>
  </table>
  </div>
</div>
</section>

<!-- FATURAS CRUZADAS -->
<section id="fat-cruzadas">
<div class="section-title">&#9776; Faturas Cruzadas — Dados Reais por Devedor <span class="section-subtitle">{total_faturas_cruzadas} faturas &middot; 19 devedores &middot; 58 colunas</span></div>
<div class="charts-grid">
  <div class="chart-box"><h4>Valor Vigente vs Prescrito por Devedor</h4><div class="chart-wrap"><canvas id="chartFatCruz1"></canvas></div></div>
  <div class="chart-box"><h4>Valor Corrigido vs Original por Devedor</h4><div class="chart-wrap"><canvas id="chartFatCruz2"></canvas></div></div>
</div>
</section>

<!-- FLUXO -->
<section id="fluxo">
<div class="section-title">&#9654; Fluxo do Portfolio — De Faturamento a Recuperacao</div>
<div class="flow-grid">
  <div class="flow-card"><div class="flow-label">Faturamento Total</div><div class="flow-val">R$ {total_fat_hist/1e6:,.0f}M</div><div class="flow-sub">2019-2026</div><span class="flow-arrow">&#10140;</span></div>
  <div class="flow-card"><div class="flow-label">Recebido</div><div class="flow-val">R$ {total_rec_hist/1e6:,.0f}M</div><div class="flow-sub">{total_rec_hist/total_fat_hist*100:.1f}% taxa pgto</div><span class="flow-arrow">&#10140;</span></div>
  <div class="flow-card"><div class="flow-label">Inadimplido</div><div class="flow-val">R$ {(total_fat_hist-total_rec_hist)/1e6:,.0f}M</div><div class="flow-sub">{(total_fat_hist-total_rec_hist)/total_fat_hist*100:.1f}% do total</div><span class="flow-arrow">&#10140;</span></div>
  <div class="flow-card"><div class="flow-label">Val Exigivel</div><div class="flow-val">R$ {total_val_exig/1e6:,.0f}M</div><div class="flow-sub">Nao prescrito</div><span class="flow-arrow">&#10140;</span></div>
  <div class="flow-card"><div class="flow-label">Val Atualizado</div><div class="flow-val">R$ {total_val_atual/1e6:,.0f}M</div><div class="flow-sub">SELIC + juros + multa</div><span class="flow-arrow">&#10140;</span></div>
  <div class="flow-card"><div class="flow-label">Fee Estimado</div><div class="flow-val">R$ {cenarios.get('base_40pct',{}).get('fee_20pct',0)/1e6:,.1f}M</div><div class="flow-sub">Base 40% &times; 20%</div></div>
</div>
<div class="flow-grid">
  <div class="flow-card"><div class="flow-label">Perdas SPCF</div><div class="flow-val" style="color:var(--red)">R$ {spcf_metrics['perdas_total']/1e6:,.1f}M</div><div class="flow-sub">Baixadas</div></div>
  <div class="flow-card"><div class="flow-label">Fat. Canceladas</div><div class="flow-val" style="color:var(--orange)">R$ {total_fat_cancel/1e6:,.1f}M</div><div class="flow-sub">{sum(d['fat_cancel_qtd'] for d in devs)} faturas</div></div>
  <div class="flow-card"><div class="flow-label">Empenhos 2026</div><div class="flow-val" style="color:var(--green)">R$ {spcf_metrics['empenhos_2026_val']/1e6:,.1f}M</div><div class="flow-sub">Obrigacao futura</div></div>
  <div class="flow-card"><div class="flow-label">A Empenhar 2026</div><div class="flow-val" style="color:var(--purple)">R$ {spcf_metrics['a_empenhar_2026']/1e6:,.1f}M</div><div class="flow-sub">Reconhecimento futuro</div></div>
</div>
</section>

<!-- INSIGHTS -->
<section id="insights">
<div class="section-title">&#9733; Insights Estrategicos &amp; Acoes Recomendadas</div>
<div class="insights-grid">
  <div class="insight-card critical">
    <h4>RISCO PRESCRICIONAL CRITICO</h4>
    <p>ADS prescreve em 12/04/2026 (D+11). SES/SUSAM prescreve em 13/05/2026 (D+42) com R$ 14,7M + 60 NEs sem cobertura. Acao imediata necessaria para interromper prescricao.</p>
    <div class="insight-tags"><span class="insight-tag">URGENTE</span><span class="insight-tag">R$ 18,2M</span><span class="insight-tag">NOTIFICAR 48H</span></div>
  </div>
  <div class="insight-card critical">
    <h4>PROCURACAO — BLOQUEADOR PRINCIPAL</h4>
    <p>A ausencia de procuracao impede qualquer ato formal. Este e o gargalo #1 do projeto. Recomenda-se obtencao imediata junto a PRODAM.</p>
    <div class="insight-tags"><span class="insight-tag">BLOQUEADOR #1</span><span class="insight-tag">{len(devs)} devedores afetados</span></div>
  </div>
  <div class="insight-card">
    <h4>CONCENTRACAO DE VALOR</h4>
    <p>Os 5 maiores devedores (SEDUC, DETRAN, SES/SUSAM, SSP, SEAD) concentram {sum(d["val_exig"] for d in devs[:5])/total_val_exig*100:.0f}% do valor exigivel total. Estrategia de recuperacao deve priorizar estes orgaos.</p>
    <div class="insight-tags"><span class="insight-tag">Top 5 = {sum(d["val_exig"] for d in devs[:5])/total_val_exig*100:.0f}%</span><span class="insight-tag">R$ {sum(d["val_exig"] for d in devs[:5])/1e6:,.0f}M</span></div>
  </div>
  <div class="insight-card">
    <h4>DUPLA BAIXA CONTABIL</h4>
    <p>47 faturas aparecem simultaneamente como canceladas E em perdas. Impacto financeiro de R$ 86,8M. Auditoria contabil obrigatoria antes de qualquer notificacao.</p>
    <div class="insight-tags"><span class="insight-tag">AUDITORIA</span><span class="insight-tag">R$ 86,8M</span><span class="insight-tag">47 faturas</span></div>
  </div>
  <div class="insight-card">
    <h4>OVERLAP PAGA x DEVIDAS</h4>
    <p>1.643 faturas aparecem em ambas as listas de pagas e devidas. Depuracao obrigatoria antes de qualquer notificacao para evitar contestacao e dano reputacional.</p>
    <div class="insight-tags"><span class="insight-tag">DEPURACAO</span><span class="insight-tag">1.643 faturas</span></div>
  </div>
  <div class="insight-card">
    <h4>EMPENHOS SEM COBERTURA — ARMA JURIDICA</h4>
    <p>60 NEs emitidas SEM COBERTURA CONTRATUAL (R$ 14,9M) constituem reconhecimento tacito de divida (Art. 202 VI CC). Argumento nuclear para SES/SUSAM.</p>
    <div class="insight-tags"><span class="insight-tag">Art. 202 VI CC</span><span class="insight-tag">60 NEs</span><span class="insight-tag">R$ 14,9M</span></div>
  </div>
</div>
</section>

<!-- FOOTER -->
<div class="footer">
  <strong>Brandao Ozores Advogados</strong> &middot; Dashboard PRODAM v5.3 &middot; Gerado em 01/04/2026<br>
  Dados: profiles.json (71 dev) + SPCF_MAR2026 (6 Blocos, 543 clientes) + {total_faturas_cruzadas} faturas cruzadas (19 CSVs) + Serie Historica (87 meses)<br>
  Confidencial — Uso exclusivo da equipe juridica
</div>

</div><!-- /main -->

<script>
// ============================================================
// DATA
// ============================================================
const DEVS = {devs_json};
const SERIE = {serie_json};
const FAT_CRUZ = {fat_cruz_js};
const FORCA = {forca_js};
const FASE = {fase_js};
const PADRAO = {padrao_js};
const SPCF = {spcf_js};

// ============================================================
// THEME
// ============================================================
const themeBtn = document.getElementById('themeToggle');
themeBtn.onclick = () => {{
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  document.documentElement.setAttribute('data-theme', isDark ? '' : 'dark');
  themeBtn.textContent = isDark ? '\\u263E Tema' : '\\u2600 Tema';
  // Update chart colors
  Chart.helpers.each(Chart.instances, c => {{
    c.options.plugins.legend.labels.color = isDark ? '#1a1d29' : '#e6edf3';
    c.options.scales && Object.values(c.options.scales).forEach(s => {{
      if(s.ticks) s.ticks.color = isDark ? '#1a1d29' : '#8b949e';
      if(s.grid) s.grid.color = isDark ? '#e2e5f0' : '#30363d';
    }});
    c.update('none');
  }});
}};

// ============================================================
// EXPORT CSV
// ============================================================
document.getElementById('exportBtn').onclick = () => {{
  const headers = ['#','Devedor','Tipo','Val.Exigivel','Val.Atualizado','Forca','Fase','Faturas','Exig','Presc','Emp2026','NEs','Score','CPRAC','SPCF Receber','Perdas','Padrao','Taxa%','Prox.Passo'];
  let csv = headers.join(';') + '\\n';
  DEVS.forEach(d => {{
    csv += [d.n,d.sigla,d.tipo,d.val_exig.toFixed(2),d.val_atual.toFixed(2),d.forca,d.fase,d.faturas,d.exig,d.presc,d.emp26.toFixed(2),d.nes,d.score,d.cprac,d.spcf.toFixed(2),d.perdas.toFixed(2),d.padrao,d.taxa,d.prox].join(';') + '\\n';
  }});
  const blob = new Blob([csv], {{type:'text/csv;charset=utf-8;'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'PRODAM_v53_export.csv';
  a.click();
}};

// ============================================================
// TABLE
// ============================================================
const tbody = document.getElementById('tableBody');
let sortCol = 'val_exig', sortAsc = false;
let filtered = [...DEVS];

function fmtBR(v) {{ return v ? 'R$ ' + v.toLocaleString('pt-BR', {{minimumFractionDigits:2, maximumFractionDigits:2}}) : '—'; }}
function forcaTag(f) {{
  const cls = f === 'FORTE' ? 'tag-forte' : f === 'MEDIA' ? 'tag-media' : 'tag-fraca';
  return '<span class="tag ' + cls + '">' + (f||'—') + '</span>';
}}
function faseTag(f) {{
  const cls = f && f.includes('F5') ? 'tag-f5' : f && f.includes('F3') ? 'tag-f3' : 'tag-f0';
  return '<span class="tag ' + cls + '">' + (f||'—') + '</span>';
}}

function renderTable() {{
  tbody.innerHTML = '';
  filtered.forEach((d,i) => {{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${{i+1}}</td><td><strong>${{d.sigla}}</strong></td><td>${{d.tipo}}</td>
      <td>${{fmtBR(d.val_exig)}}</td><td>${{fmtBR(d.val_atual)}}</td>
      <td>${{forcaTag(d.forca)}}</td><td>${{faseTag(d.fase)}}</td>
      <td>${{d.faturas}}</td><td>${{d.exig}}</td><td>${{d.presc}}</td>
      <td>${{fmtBR(d.emp26)}}</td><td>${{d.nes||'—'}}</td><td>${{d.score}}%</td>
      <td>${{d.cprac||'—'}}</td><td>${{fmtBR(d.spcf)}}</td><td>${{fmtBR(d.perdas)}}</td>
      <td>${{d.padrao||'—'}}</td><td>${{d.taxa ? d.taxa.toFixed(1)+'%' : '—'}}</td>
      <td style="max-width:120px;overflow:hidden;text-overflow:ellipsis">${{d.prox||'—'}}</td>`;
    tbody.appendChild(tr);
  }});
  document.getElementById('tableCount').textContent = filtered.length + ' registros';
}}

// Sort
document.querySelectorAll('#mainTable th').forEach(th => {{
  th.onclick = () => {{
    const col = th.dataset.col;
    if(sortCol === col) sortAsc = !sortAsc; else {{ sortCol = col; sortAsc = true; }}
    filtered.sort((a,b) => {{
      let va = a[col], vb = b[col];
      if(typeof va === 'string') return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
      return sortAsc ? va - vb : vb - va;
    }});
    renderTable();
  }};
}});

// Filters
function applyFilters() {{
  const tipo = document.getElementById('fTipo').value;
  const forca = document.getElementById('fForca').value;
  const fase = document.getElementById('fFase').value;
  const presc = document.getElementById('fPresc').value;
  const cprac = document.getElementById('fCprac').value;
  const busca = document.getElementById('fBusca').value.toLowerCase();
  filtered = DEVS.filter(d => {{
    if(tipo && d.tipo !== tipo) return false;
    if(forca && d.forca !== forca) return false;
    if(fase && d.fase !== fase) return false;
    if(presc === 'vencida' && d.exig > 0) return false;
    if(presc === 'urgente' && d.presc === 0) return false;
    if(cprac && d.cprac !== cprac) return false;
    if(busca && !d.sigla.toLowerCase().includes(busca)) return false;
    return true;
  }});
  renderTable();
}}
['fTipo','fForca','fFase','fPresc','fCprac'].forEach(id => document.getElementById(id).onchange = applyFilters);
document.getElementById('fBusca').oninput = applyFilters;
document.getElementById('filterReset').onclick = () => {{
  ['fTipo','fForca','fFase','fPresc','fCprac'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('fBusca').value = '';
  filtered = [...DEVS];
  renderTable();
}};
renderTable();

// ============================================================
// HEATMAP
// ============================================================
const hmContainer = document.getElementById('heatmapContainer');
DEVS.filter(d => d.score > 0).sort((a,b) => b.score - a.score).forEach(d => {{
  const pct = d.score;
  const r = Math.round(220 * pct / 100 + 35);
  const g = Math.round(220 * (100 - pct) / 100 + 35);
  const cell = document.createElement('div');
  cell.className = 'hm-cell';
  cell.style.background = `rgb(${{r}},${{g}},60)`;
  cell.innerHTML = `${{d.sigla}}<span class="hm-score">${{pct}}%</span>`;
  cell.title = `${{d.sigla}}: Score ${{pct}}%, Val.Exig R$ ${{(d.val_exig/1e6).toFixed(1)}}M`;
  hmContainer.appendChild(cell);
}});

// ============================================================
// CHARTS
// ============================================================
const COLORS = ['#c8a84e','#3b82f6','#10b981','#ef4444','#8b5cf6','#f59e0b','#ec4899','#14b8a6','#6366f1','#f97316','#06b6d4','#84cc16','#e11d48','#a855f7','#0ea5e9'];

// Ranking Top 15
new Chart(document.getElementById('chartRanking'), {{
  type: 'bar',
  data: {{
    labels: DEVS.slice(0,15).map(d => d.sigla),
    datasets: [{{
      label: 'Val. Exigivel (R$)',
      data: DEVS.slice(0,15).map(d => d.val_exig),
      backgroundColor: COLORS.slice(0,15),
      borderRadius: 4
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: ctx => 'R$ ' + (ctx.raw/1e6).toFixed(2) + 'M' }} }} }},
    scales: {{ x: {{ ticks: {{ callback: v => 'R$ ' + (v/1e6).toFixed(0) + 'M' }} }} }}
  }}
}});

// Forca
new Chart(document.getElementById('chartForca'), {{
  type: 'doughnut',
  data: {{
    labels: FORCA.labels,
    datasets: [{{ data: FORCA.counts, backgroundColor: ['#10b981','#f59e0b','#ef4444','#6b7280','#8b5cf6'] }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'bottom' }} }} }}
}});

// Pipeline
new Chart(document.getElementById('chartPipeline'), {{
  type: 'bar',
  data: {{
    labels: FASE.labels,
    datasets: [{{ label: 'Devedores', data: FASE.counts, backgroundColor: ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6'] }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// Prescricao Bubble
new Chart(document.getElementById('chartPresc'), {{
  type: 'bubble',
  data: {{
    datasets: DEVS.filter(d => d.presc > 0).slice(0,20).map((d,i) => ({{
      label: d.sigla,
      data: [{{ x: d.presc, y: d.val_exig/1e6, r: Math.max(4, Math.min(25, d.faturas/5)) }}],
      backgroundColor: COLORS[i % COLORS.length] + '80'
    }}))
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    scales: {{ x: {{ title: {{ display: true, text: 'Faturas Prescritas' }} }},
              y: {{ title: {{ display: true, text: 'Val. Exigivel (R$ M)' }} }} }},
    plugins: {{ legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': R$ ' + ctx.raw.y.toFixed(1) + 'M, ' + ctx.raw.x + ' prescritas' }} }} }}
  }}
}});

// Faturamento vs Recebimento
const fatTop = DEVS.filter(d => d.spcf > 0).slice(0,10);
new Chart(document.getElementById('chartFatRec'), {{
  type: 'bar',
  data: {{
    labels: fatTop.map(d => d.sigla),
    datasets: [
      {{ label: 'Val. Exigivel', data: fatTop.map(d => d.val_exig), backgroundColor: '#3b82f6', borderRadius: 4 }},
      {{ label: 'SPCF a Receber', data: fatTop.map(d => d.spcf), backgroundColor: '#10b981', borderRadius: 4 }},
      {{ label: 'Perdas', data: fatTop.map(d => d.perdas), backgroundColor: '#ef4444', borderRadius: 4 }}
    ]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': R$ ' + (ctx.raw/1e6).toFixed(2) + 'M' }} }} }},
    scales: {{ x: {{ stacked: false }}, y: {{ ticks: {{ callback: v => 'R$ ' + (v/1e6).toFixed(0) + 'M' }} }} }}
  }}
}});

// Empenhos
const empTop = DEVS.filter(d => d.emp26 > 0).sort((a,b) => b.emp26 - a.emp26).slice(0,10);
new Chart(document.getElementById('chartEmp'), {{
  type: 'bar',
  data: {{
    labels: empTop.map(d => d.sigla),
    datasets: [
      {{ label: 'Empenho 2026', data: empTop.map(d => d.emp26), backgroundColor: '#10b981', borderRadius: 4 }},
      {{ label: 'NEs s/ Cobertura', data: empTop.map(d => d.nes > 0 ? d.val_exig * 0.1 : 0), backgroundColor: '#ef4444', borderRadius: 4 }}
    ]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    scales: {{ y: {{ ticks: {{ callback: v => 'R$ ' + (v/1e6).toFixed(1) + 'M' }} }} }} }}
}});

// Cenarios
new Chart(document.getElementById('chartCenarios'), {{
  type: 'bar',
  data: {{
    labels: ['Conservador (20%)', 'Base (40%)', 'Otimista (70%)'],
    datasets: [
      {{ label: 'Recuperado', data: [{cenarios.get("conservador_20pct",{}).get("recuperado",0)}, {cenarios.get("base_40pct",{}).get("recuperado",0)}, {cenarios.get("otimista_70pct",{}).get("recuperado",0)}], backgroundColor: '#3b82f6', borderRadius: 4 }},
      {{ label: 'Fee 20%', data: [{cenarios.get("conservador_20pct",{}).get("fee_20pct",0)}, {cenarios.get("base_40pct",{}).get("fee_20pct",0)}, {cenarios.get("otimista_70pct",{}).get("fee_20pct",0)}], backgroundColor: '#c8a84e', borderRadius: 4 }}
    ]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    scales: {{ y: {{ ticks: {{ callback: v => 'R$ ' + (v/1e6).toFixed(0) + 'M' }} }} }} }}
}});

// Padrao
new Chart(document.getElementById('chartPadrao'), {{
  type: 'doughnut',
  data: {{
    labels: PADRAO.labels,
    datasets: [{{ data: PADRAO.counts, backgroundColor: ['#ef4444','#f59e0b','#3b82f6','#10b981','#8b5cf6','#6b7280'] }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom' }} }} }}
}});

// SPCF Portfolio
new Chart(document.getElementById('chartSpcfPortfolio'), {{
  type: 'doughnut',
  data: {{
    labels: ['Portfolio (34 dev)', 'Fora Portfolio (346 dev)', 'Sem divida (163)'],
    datasets: [{{ data: [101310196, 24821731, 1439315], backgroundColor: ['#3b82f6','#f59e0b','#6b7280'] }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'bottom' }},
      tooltip: {{ callbacks: {{ label: ctx => ctx.label + ': R$ ' + (ctx.raw/1e6).toFixed(1) + 'M' }} }} }} }}
}});

// SPCF Faturas
new Chart(document.getElementById('chartSpcfFaturas'), {{
  type: 'bar',
  data: {{
    labels: ['Devidas', 'Em Aberto', 'Canceladas', 'Perdas', 'Overlap'],
    datasets: [
      {{ label: 'Quantidade', data: [4620, 2414, 2097, 2442, 1643], backgroundColor: ['#ef4444','#f59e0b','#8b5cf6','#6b7280','#ec4899'] }}
    ]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// Inconsistencias
new Chart(document.getElementById('chartInconsist'), {{
  type: 'bar',
  data: {{
    labels: ['Cancel. x Devidas', 'Cancel. x Aberto', 'Cancel. x Pagas', 'Cancel. x Perdas'],
    datasets: [{{ label: 'Inconsistencias', data: [11, 6, 0, 47], backgroundColor: ['#ef4444','#f59e0b','#10b981','#8b5cf6'] }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// Cancel x Perdas top devedores
new Chart(document.getElementById('chartCancelPerdas'), {{
  type: 'bar',
  data: {{
    labels: ['SEDUC','DETRAN','SES','SEAD','CETAM','PGE','POLICIA CIVIL','SEC','SEJUSC','UEA'],
    datasets: [{{ label: 'Val. Cancelado (R$)', data: [13227925,8995685,4814910,3132247,1245802,602066,590523,197818,246955,549808], backgroundColor: '#ef4444', borderRadius: 4 }}]
  }},
  options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: ctx => 'R$ ' + (ctx.raw/1e6).toFixed(2) + 'M' }} }} }},
    scales: {{ x: {{ ticks: {{ callback: v => 'R$ ' + (v/1e6).toFixed(0) + 'M' }} }} }} }}
}});

// Empenhos Bloco 0
new Chart(document.getElementById('chartEmpBloco0'), {{
  type: 'bar',
  data: {{
    labels: ['SEDUC','DETRAN','SES','SSP','SEAD','CETAM','AMAZONPREV','POL.CIVIL','CASA CIVIL','SEAS'],
    datasets: [{{ label: 'Valor (R$)', data: [383664365,119600700,83257855,61905752,40924402,31749714,16563334,8205443,7648104,6642249], backgroundColor: '#3b82f6', borderRadius: 4 }}]
  }},
  options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: ctx => 'R$ ' + (ctx.raw/1e6).toFixed(1) + 'M' }} }} }},
    scales: {{ x: {{ ticks: {{ callback: v => 'R$ ' + (v/1e6).toFixed(0) + 'M' }} }} }} }}
}});

// Empenhos 2026
new Chart(document.getElementById('chartEmp2026'), {{
  type: 'bar',
  data: {{
    labels: ['SEDUC','SUSAM','DETRAN','UEA','TCE','SEDECTI','UGPI','SEAS','SEMIG','SEAD'],
    datasets: [
      {{ label: 'Empenho 2026', data: [24998189,9468164,1551010,995466,552739,303126,302249,280460,277175,254276], backgroundColor: '#10b981', borderRadius: 4 }},
      {{ label: 'SEM COBERTURA', data: [0,964826,0,0,0,0,0,0,0,0], backgroundColor: '#ef4444', borderRadius: 4 }}
    ]
  }},
  options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false,
    plugins: {{ tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': R$ ' + (ctx.raw/1e6).toFixed(2) + 'M' }} }} }},
    scales: {{ x: {{ stacked: true, ticks: {{ callback: v => 'R$ ' + (v/1e6).toFixed(0) + 'M' }} }}, y: {{ stacked: true }} }} }}
}});

// Serie Historica
new Chart(document.getElementById('chartSerieHist'), {{
  type: 'bar',
  data: {{
    labels: SERIE.map(s => s.dev),
    datasets: [
      {{ label: 'Faturamento', data: SERIE.map(s => s.fat), backgroundColor: '#3b82f6', borderRadius: 4 }},
      {{ label: 'Recebimento', data: SERIE.map(s => s.rec), backgroundColor: '#10b981', borderRadius: 4 }}
    ]
  }},
  options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false,
    plugins: {{ tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': R$ ' + (ctx.raw/1e6).toFixed(1) + 'M' }} }} }},
    scales: {{ x: {{ ticks: {{ callback: v => 'R$ ' + (v/1e6).toFixed(0) + 'M' }} }} }} }}
}});

// Taxa Pagamento
new Chart(document.getElementById('chartTaxaPgto'), {{
  type: 'bar',
  data: {{
    labels: SERIE.map(s => s.dev),
    datasets: [{{ label: 'Taxa %', data: SERIE.map(s => s.taxa), backgroundColor: SERIE.map(s => s.taxa > 90 ? '#10b981' : s.taxa > 70 ? '#f59e0b' : '#ef4444'), borderRadius: 4 }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ y: {{ max: 105, ticks: {{ callback: v => v + '%' }} }} }} }}
}});

// Vias Processuais
const viasData = {{}};
DEVS.forEach(d => {{ const v = d.prox || 'Diagnostico'; viasData[v] = (viasData[v]||0) + 1; }});
new Chart(document.getElementById('chartVias'), {{
  type: 'doughnut',
  data: {{
    labels: Object.keys(viasData).slice(0,8),
    datasets: [{{ data: Object.values(viasData).slice(0,8), backgroundColor: COLORS }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }} }} }} }} }}
}});

// NEs sem Cobertura
const nscDevs = DEVS.filter(d => d.nes > 0).sort((a,b) => b.nes - a.nes);
new Chart(document.getElementById('chartNSC'), {{
  type: 'bar',
  data: {{
    labels: nscDevs.map(d => d.sigla),
    datasets: [{{ label: 'NEs sem Cobertura', data: nscDevs.map(d => d.nes), backgroundColor: '#ef4444', borderRadius: 4 }}]
  }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ beginAtZero: true }} }} }}
}});

// Faturas Cruzadas 1 - Vigente vs Prescrito
const fc = FAT_CRUZ.filter(f => f.val_vigente > 0 || f.val_prescrito > 0).slice(0,15);
new Chart(document.getElementById('chartFatCruz1'), {{
  type: 'bar',
  data: {{
    labels: fc.map(f => f.devedor),
    datasets: [
      {{ label: 'Vigente', data: fc.map(f => f.val_vigente), backgroundColor: '#10b981', borderRadius: 4 }},
      {{ label: 'Prescrito', data: fc.map(f => f.val_prescrito), backgroundColor: '#ef4444', borderRadius: 4 }}
    ]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': R$ ' + (ctx.raw/1e6).toFixed(2) + 'M' }} }} }},
    scales: {{ x: {{ stacked: true }}, y: {{ stacked: true, ticks: {{ callback: v => 'R$ ' + (v/1e6).toFixed(0) + 'M' }} }} }} }}
}});

// Faturas Cruzadas 2 - Corrigido vs Original
new Chart(document.getElementById('chartFatCruz2'), {{
  type: 'bar',
  data: {{
    labels: fc.map(f => f.devedor),
    datasets: [
      {{ label: 'Val. Original', data: fc.map(f => f.val_vigente + f.val_prescrito), backgroundColor: '#3b82f6', borderRadius: 4 }},
      {{ label: 'Val. Corrigido', data: fc.map(f => f.val_corrigido), backgroundColor: '#c8a84e', borderRadius: 4 }}
    ]
  }},
  options: {{ responsive: true, maintainAspectRatio: false,
    plugins: {{ tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': R$ ' + (ctx.raw/1e6).toFixed(2) + 'M' }} }} }},
    scales: {{ y: {{ ticks: {{ callback: v => 'R$ ' + (v/1e6).toFixed(0) + 'M' }} }} }} }}
}});

</script>
</body>
</html>'''

# Write the file
output_path = "/home/ubuntu/DASHBOARD_PRODAM_v5.3_BRANDAO_OZORES.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

file_size = os.path.getsize(output_path)
print(f"Dashboard v5.3 generated: {output_path}")
print(f"Size: {file_size/1024:.1f} KB")
print(f"Devedores: {len(devs)}")
print(f"Charts: 20+")
print(f"Sections: 18")
