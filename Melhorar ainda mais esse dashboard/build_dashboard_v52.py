#!/usr/bin/env python3
"""
Build Dashboard PRODAM v5.2 — integrating ALL real data from:
- profiles.json (71 devedores)
- DASHBOARD_DADOS_FINAIS.json (20 devedores detailed)
- 20 CSVs faturas cruzadas (1,735 faturas)
- Reconciliação SPCF data
"""
import json
import csv
import glob
import os

DATA_DIR = '/home/ubuntu/prodam_data'

# Load profiles
with open(f'{DATA_DIR}/profiles.json', 'r', encoding='utf-8') as f:
    profiles = json.load(f)

# Load dashboard dados finais
with open(f'{DATA_DIR}/DASHBOARD_DADOS_FINAIS.json', 'r', encoding='utf-8') as f:
    dash_final = json.load(f)

# Process faturas cruzadas CSVs
csv_files = glob.glob(f'{DATA_DIR}/*_FATURAS_CRUZADAS.csv')
faturas_by_dev = {}
for csv_file in sorted(csv_files):
    devedor = os.path.basename(csv_file).replace('_FATURAS_CRUZADAS.csv', '')
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)
    
    vigentes = sum(1 for r in rows if r.get('status_prescricao') != 'PRESCRITA')
    prescritas = sum(1 for r in rows if r.get('status_prescricao') == 'PRESCRITA')
    
    val_vig = sum(float(r.get('valor_liquido',0) or 0) for r in rows if r.get('status_prescricao') != 'PRESCRITA')
    val_presc = sum(float(r.get('valor_liquido',0) or 0) for r in rows if r.get('status_prescricao') == 'PRESCRITA')
    
    try:
        val_corrigido = sum(float(r.get('valor_corrigido_calc',0) or 0) for r in rows if r.get('valor_corrigido_calc','') not in ['','N/A — prescrita','N/A'])
    except:
        val_corrigido = 0
    
    try:
        val_atualizado = sum(float(r.get('valor_total_atualizado',0) or 0) for r in rows if r.get('valor_total_atualizado','') not in ['','N/A — prescrita','N/A'])
    except:
        val_atualizado = 0
    
    # Count actions
    acoes = {}
    for r in rows:
        a = r.get('acao_recomendada', 'N/A')
        acoes[a] = acoes.get(a, 0) + 1
    
    # Count forca
    forcas = {}
    for r in rows:
        f_val = r.get('forca_probatoria', 'N/A')
        forcas[f_val] = forcas.get(f_val, 0) + 1
    
    faturas_by_dev[devedor] = {
        'total': len(rows),
        'vigentes': vigentes,
        'prescritas': prescritas,
        'val_vig': val_vig,
        'val_presc': val_presc,
        'val_corrigido': val_corrigido,
        'val_atualizado': val_atualizado,
        'acoes': acoes,
        'forcas': forcas
    }

# Build the FATURAS_CRUZADAS JS data
fc_js_data = []
for dev, stats in sorted(faturas_by_dev.items(), key=lambda x: x[1]['val_vig'], reverse=True):
    fc_js_data.append({
        's': dev,
        't': stats['total'],
        'v': round(stats['vigentes']),
        'p': round(stats['prescritas']),
        'vv': round(stats['val_vig'], 2),
        'vp': round(stats['val_presc'], 2),
        'vc': round(stats['val_corrigido'], 2),
        'va': round(stats['val_atualizado'], 2),
    })

# Build urgencias JS data from DASHBOARD_DADOS_FINAIS
urgencias_js = json.dumps(dash_final.get('urgencias', []), ensure_ascii=False)

# Build prescricao_por_mes JS data
presc_mes_js = json.dumps(dash_final.get('prescricao_por_mes', []), ensure_ascii=False)

# Build cenarios JS data
cenarios_js = json.dumps(dash_final.get('cenarios_fee', {}), ensure_ascii=False)

# Build devedores detalhados from DASHBOARD_DADOS_FINAIS
dev_detalhados_js = json.dumps(dash_final.get('devedores', []), ensure_ascii=False)

# Build acao_distribuicao
acao_dist_js = json.dumps(dash_final.get('acao_distribuicao', []), ensure_ascii=False)

# Read the existing dashboard v5.1
with open('/home/ubuntu/DASHBOARD_PRODAM_v5.1_BRANDAO_OZORES.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# ADD NEW SECTIONS: Faturas Detalhadas + Correção Monetária + Urgências Reais
# ============================================================

# 1. Add new CSS for the new sections
new_css_v52 = """
/* ===== V5.2 NEW STYLES ===== */
.waterfall-container { position: relative; padding: 0 20px; }
.waterfall-bar { display: flex; align-items: center; margin-bottom: 8px; }
.waterfall-bar .wb-label { width: 100px; font-size: 11px; font-weight: 600; text-align: right; padding-right: 12px; flex-shrink: 0; }
.waterfall-bar .wb-bar { height: 28px; border-radius: 4px; display: flex; align-items: center; padding: 0 8px; font-size: 11px; font-weight: 700; color: white; min-width: 40px; transition: width 0.8s ease; }
.waterfall-bar .wb-bar.green { background: linear-gradient(90deg, #16A34A, #22C55E); }
.waterfall-bar .wb-bar.red { background: linear-gradient(90deg, #DC2626, #EF4444); }
.waterfall-bar .wb-bar.blue { background: linear-gradient(90deg, #2563EB, #3B82F6); }
.waterfall-bar .wb-bar.orange { background: linear-gradient(90deg, #D97706, #F59E0B); }
.waterfall-bar .wb-bar.purple { background: linear-gradient(90deg, #7C3AED, #8B5CF6); }
.waterfall-bar .wb-bar.gold { background: linear-gradient(90deg, #B8860B, #C9A84C); }

.correcao-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-top: 16px; }
.correcao-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 16px; text-align: center; }
.correcao-card .cc-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); font-weight: 600; }
.correcao-card .cc-value { font-size: 24px; font-weight: 800; font-family: var(--font-mono); margin: 4px 0; }
.correcao-card .cc-sub { font-size: 11px; color: var(--text-secondary); }
.correcao-card.positive .cc-value { color: var(--success); }
.correcao-card.negative .cc-value { color: var(--danger); }
.correcao-card.neutral .cc-value { color: var(--info); }

.urgencia-row { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border-light); transition: var(--transition); }
.urgencia-row:hover { background: var(--bg-alt); }
.urgencia-row .urg-dias { width: 60px; text-align: center; font-family: var(--font-mono); font-weight: 800; font-size: 18px; flex-shrink: 0; }
.urgencia-row .urg-dias.critico { color: var(--danger); }
.urgencia-row .urg-dias.urgente { color: var(--warn); }
.urgencia-row .urg-dias.normal { color: var(--info); }
.urgencia-row .urg-info { flex: 1; padding: 0 12px; }
.urgencia-row .urg-dev { font-weight: 700; font-size: 13px; }
.urgencia-row .urg-detail { font-size: 11px; color: var(--text-secondary); }
.urgencia-row .urg-valor { text-align: right; font-family: var(--font-mono); font-weight: 700; font-size: 13px; flex-shrink: 0; }
.urgencia-row .urg-acao { width: 120px; text-align: center; flex-shrink: 0; }
.urgencia-row .urg-badge { font-size: 10px; padding: 3px 8px; border-radius: 4px; font-weight: 700; }
.urg-badge.not5 { background: var(--danger-bg); color: var(--danger); }
.urg-badge.not15 { background: var(--warn-bg); color: var(--warn); }

.portfolio-flow { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; align-items: center; margin: 20px 0; }
.pf-box { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px; text-align: center; }
.pf-box .pf-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); font-weight: 600; }
.pf-box .pf-value { font-size: 18px; font-weight: 800; font-family: var(--font-mono); margin: 4px 0; }
.pf-arrow { text-align: center; font-size: 20px; color: var(--accent); font-weight: 700; }
"""

html = html.replace('/* ===== RECONCILIACAO STYLES ===== */', new_css_v52 + '\n/* ===== RECONCILIACAO STYLES ===== */')

# 2. Add new sidebar items
new_sidebar = """    <a href="#correcao"><span class="nav-icon">&#9733;</span> Correcao Monetaria</a>
    <a href="#faturas-det"><span class="nav-icon">&#9776;</span> Faturas Detalhadas</a>
    <a href="#urgencias-real"><span class="nav-icon">&#9200;</span> Urgencias Reais</a>
    <a href="#portfolio-flow"><span class="nav-icon">&#9654;</span> Fluxo Portfolio</a>
"""

html = html.replace(
    '    <div class="nav-section">Reconciliacao</div>',
    '    <div class="nav-section">Dados Reais</div>\n' + new_sidebar + '    <div class="nav-section">Reconciliacao</div>'
)

# 3. Add new HTML sections before reconciliation
new_sections_html = """
    <!-- ===== CORREÇÃO MONETÁRIA ===== -->
    <section id="correcao">
      <div class="section-header animate-in">
        <h2><span class="section-icon">&#9733;</span> Correcao Monetaria &amp; Valores Atualizados</h2>
        <span class="section-badge">SELIC + Juros + Multa</span>
      </div>

      <div class="correcao-grid animate-in">
        <div class="correcao-card neutral">
          <div class="cc-label">Val Original (Nominal)</div>
          <div class="cc-value">R$ 119,8M</div>
          <div class="cc-sub">Valor historico das faturas</div>
        </div>
        <div class="correcao-card neutral">
          <div class="cc-label">Val Exigivel</div>
          <div class="cc-value">R$ 121,5M</div>
          <div class="cc-sub">Faturas nao prescritas</div>
        </div>
        <div class="correcao-card positive">
          <div class="cc-label">Val Atualizado (SELIC)</div>
          <div class="cc-value">R$ 195,4M</div>
          <div class="cc-sub">Com correcao + juros + multa</div>
        </div>
        <div class="correcao-card positive">
          <div class="cc-label">Ganho Correcao</div>
          <div class="cc-value">+R$ 73,9M</div>
          <div class="cc-sub">+61,7% sobre nominal</div>
        </div>
        <div class="correcao-card neutral">
          <div class="cc-label">Val Corrigido (Cruzadas)</div>
          <div class="cc-value">R$ 101,9M</div>
          <div class="cc-sub">1.735 faturas com SELIC aplicada</div>
        </div>
        <div class="correcao-card negative">
          <div class="cc-label">Perdas SPCF</div>
          <div class="cc-value">R$ 32,5M</div>
          <div class="cc-sub">Baixadas como perdas</div>
        </div>
      </div>

      <div class="recon-charts-grid animate-in" style="margin-top:20px">
        <div class="recon-chart-panel">
          <h4>Composicao do Portfolio (R$ milhoes)</h4>
          <canvas id="chartPortfolio" height="300"></canvas>
        </div>
        <div class="recon-chart-panel">
          <h4>Faturamento vs Recebimento (Top 10)</h4>
          <canvas id="chartFatRecReal" height="300"></canvas>
        </div>
      </div>
    </section>

    <!-- ===== FATURAS DETALHADAS ===== -->
    <section id="faturas-det">
      <div class="section-header animate-in">
        <h2><span class="section-icon">&#9776;</span> Faturas Cruzadas &mdash; Dados Reais por Devedor</h2>
        <span class="section-badge">1.735 faturas &middot; 20 devedores &middot; 58 colunas</span>
      </div>

      <div class="recon-charts-grid animate-in">
        <div class="recon-chart-panel">
          <h4>Valor Vigente vs Prescrito por Devedor (R$)</h4>
          <canvas id="chartFatDetalhadas" height="400"></canvas>
        </div>
        <div class="recon-chart-panel">
          <h4>Valor Corrigido vs Original por Devedor (R$)</h4>
          <canvas id="chartCorrecaoDev" height="400"></canvas>
        </div>
      </div>

      <div class="panel animate-in" style="margin-top:20px;padding:0;overflow:hidden">
        <div class="tbl-wrap">
          <table class="recon-divergence-table" id="tblFatDet">
            <thead>
              <tr>
                <th>#</th>
                <th>Devedor</th>
                <th>Total Fat.</th>
                <th>Vigentes</th>
                <th>Prescritas</th>
                <th>Val Vigentes</th>
                <th>Val Prescritas</th>
                <th>Val Corrigido</th>
                <th>Val Atualizado</th>
                <th>Ganho Correcao</th>
              </tr>
            </thead>
            <tbody id="tblFatDetBody"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ===== URGÊNCIAS REAIS ===== -->
    <section id="urgencias-real">
      <div class="section-header animate-in">
        <h2><span class="section-icon">&#9200;</span> Urgencias Prescricao &mdash; Faturas Individuais</h2>
        <span class="section-badge">Dados reais dos CSVs</span>
      </div>

      <div class="panel animate-in" style="padding:0;overflow:hidden">
        <div id="urgenciasContainer"></div>
      </div>

      <div class="recon-charts-grid animate-in" style="margin-top:20px">
        <div class="recon-chart-panel">
          <h4>Prescricao por Mes &mdash; Faturas a Vencer</h4>
          <canvas id="chartPrescMes" height="300"></canvas>
        </div>
        <div class="recon-chart-panel">
          <h4>Acoes Recomendadas &mdash; Distribuicao Real</h4>
          <canvas id="chartAcaoReal" height="300"></canvas>
        </div>
      </div>
    </section>

    <!-- ===== FLUXO PORTFOLIO ===== -->
    <section id="portfolio-flow">
      <div class="section-header animate-in">
        <h2><span class="section-icon">&#9654;</span> Fluxo do Portfolio &mdash; De Faturamento a Recuperacao</h2>
        <span class="section-badge">2019-2026</span>
      </div>

      <div class="panel animate-in">
        <div class="portfolio-flow">
          <div class="pf-box">
            <div class="pf-label">Faturamento Total</div>
            <div class="pf-value" style="color:var(--info)">R$ 761,5M</div>
            <div style="font-size:10px;color:var(--text-secondary)">2019-2026</div>
          </div>
          <div class="pf-arrow">&#10140;</div>
          <div class="pf-box">
            <div class="pf-label">Recebido</div>
            <div class="pf-value" style="color:var(--success)">R$ 610,1M</div>
            <div style="font-size:10px;color:var(--text-secondary)">80,1% taxa pgto</div>
          </div>
          <div class="pf-arrow">&#10140;</div>
          <div class="pf-box">
            <div class="pf-label">Inadimplido</div>
            <div class="pf-value" style="color:var(--danger)">R$ 151,4M</div>
            <div style="font-size:10px;color:var(--text-secondary)">19,9% do total</div>
          </div>
        </div>
        <div class="portfolio-flow" style="margin-top:8px">
          <div class="pf-box">
            <div class="pf-label">Val Exigivel</div>
            <div class="pf-value" style="color:var(--warn)">R$ 121,5M</div>
            <div style="font-size:10px;color:var(--text-secondary)">Nao prescrito</div>
          </div>
          <div class="pf-arrow">&#10140;</div>
          <div class="pf-box">
            <div class="pf-label">Val Atualizado</div>
            <div class="pf-value" style="color:var(--success)">R$ 195,4M</div>
            <div style="font-size:10px;color:var(--text-secondary)">SELIC + juros + multa</div>
          </div>
          <div class="pf-arrow">&#10140;</div>
          <div class="pf-box">
            <div class="pf-label">Fee Estimado (20%)</div>
            <div class="pf-value" style="color:var(--accent)">R$ 8,6M</div>
            <div style="font-size:10px;color:var(--text-secondary)">Cenario base 40%</div>
          </div>
        </div>
        <div class="portfolio-flow" style="margin-top:8px">
          <div class="pf-box" style="border-color:var(--danger)">
            <div class="pf-label">Perdas SPCF</div>
            <div class="pf-value" style="color:var(--danger)">R$ 32,5M</div>
            <div style="font-size:10px;color:var(--text-secondary)">Baixadas</div>
          </div>
          <div class="pf-arrow" style="color:var(--danger)">&#10140;</div>
          <div class="pf-box" style="border-color:var(--danger)">
            <div class="pf-label">Fat Canceladas</div>
            <div class="pf-value" style="color:var(--danger)">R$ 54,5M</div>
            <div style="font-size:10px;color:var(--text-secondary)">770 faturas</div>
          </div>
          <div class="pf-arrow" style="color:var(--success)">&#10140;</div>
          <div class="pf-box" style="border-color:var(--success)">
            <div class="pf-label">Empenhos 2026</div>
            <div class="pf-value" style="color:var(--success)">R$ 39,0M</div>
            <div style="font-size:10px;color:var(--text-secondary)">Obrigacao futura</div>
          </div>
        </div>
      </div>

      <div class="recon-charts-grid animate-in" style="margin-top:20px">
        <div class="recon-chart-panel">
          <h4>Cenarios de Recuperacao &amp; Fee (R$ milhoes)</h4>
          <canvas id="chartCenariosReal" height="280"></canvas>
        </div>
        <div class="recon-chart-panel">
          <h4>Composicao: Canceladas vs Perdas vs Empenhos</h4>
          <canvas id="chartCancPerdas" height="280"></canvas>
        </div>
      </div>
    </section>

"""

html = html.replace(
    '    <!-- ===== RECONCILIACAO SPCF ===== -->',
    new_sections_html + '    <!-- ===== RECONCILIACAO SPCF ===== -->'
)

# 4. Add new JavaScript for the new charts
new_js = """

/* ===== V5.2 NEW CHARTS WITH REAL DATA ===== */

const FC_DATA = """ + json.dumps(fc_js_data, ensure_ascii=False) + """;

const URGENCIAS_REAL = """ + urgencias_js + """;

const PRESC_MES = """ + presc_mes_js + """;

const CENARIOS_REAL = """ + cenarios_js + """;

const ACAO_DIST = """ + acao_dist_js + """;

// Chart: Portfolio Composition (Doughnut)
(function(){
  const ctx=document.getElementById('chartPortfolio');
  if(!ctx) return;
  new Chart(ctx,{
    type:'doughnut',
    data:{
      labels:['Val Exigivel (R$ 121,5M)','Perdas SPCF (R$ 32,5M)','Fat Canceladas (R$ 54,5M)','NEs s/Cob (R$ 6,3M)'],
      datasets:[{
        data:[121.5,32.5,54.5,6.3],
        backgroundColor:['#2563EB','#DC2626','#D97706','#16A34A'],
        borderWidth:0,
        hoverOffset:8
      }]
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'bottom',labels:{font:{size:11,family:'Inter'},padding:12,usePointStyle:true,pointStyleWidth:8}},
        tooltip:{callbacks:{label:function(c){return c.label+' ('+((c.raw/214.8)*100).toFixed(1)+'%)'}}}
      },
      cutout:'60%'
    }
  });
})();

// Chart: Faturamento vs Recebimento Real
(function(){
  const ctx=document.getElementById('chartFatRecReal');
  if(!ctx) return;
  const devs=['SEDUC','DETRAN','SES','SSP','SEAD','SEJUSC','CETAM','SEDEL','SUHAB','SEAS'];
  const fat=[326.1,157.0,139.4,70.8,46.7,7.6,52.3,0,4.0,4.4];
  const rec=[535.1,195.7,267.2,118.3,82.2,9.2,51.0,0,10.6,6.3];
  new Chart(ctx,{
    type:'bar',
    data:{
      labels:devs,
      datasets:[
        {label:'Faturamento (R$ M)',data:fat.map(v=>v),backgroundColor:'rgba(37,99,235,0.6)',borderRadius:3},
        {label:'Recebimento (R$ M)',data:rec.map(v=>v),backgroundColor:'rgba(22,163,74,0.6)',borderRadius:3}
      ]
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'top',labels:{font:{size:11,family:'Inter'},usePointStyle:true,pointStyleWidth:8}},
        tooltip:{callbacks:{label:function(c){return c.dataset.label+': R$ '+c.raw.toFixed(1)+'M'}}}
      },
      scales:{
        x:{ticks:{font:{size:10},maxRotation:45},grid:{display:false}},
        y:{title:{display:true,text:'R$ Milhoes',font:{size:11}},ticks:{font:{size:10}},grid:{color:'rgba(0,0,0,0.05)'}}
      }
    }
  });
})();

// Chart: Faturas Detalhadas (Stacked Bar - Vigentes vs Prescritas)
(function(){
  const ctx=document.getElementById('chartFatDetalhadas');
  if(!ctx) return;
  const sorted=[...FC_DATA].sort((a,b)=>b.vv-a.vv);
  new Chart(ctx,{
    type:'bar',
    data:{
      labels:sorted.map(d=>d.s),
      datasets:[
        {label:'Vigentes (R$)',data:sorted.map(d=>d.vv/1e6),backgroundColor:'rgba(22,163,74,0.7)',borderRadius:2},
        {label:'Prescritas (R$)',data:sorted.map(d=>d.vp/1e6),backgroundColor:'rgba(220,38,38,0.5)',borderRadius:2}
      ]
    },
    options:{
      indexAxis:'y',
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'top',labels:{font:{size:11,family:'Inter'},usePointStyle:true,pointStyleWidth:8}},
        tooltip:{callbacks:{label:function(c){return c.dataset.label+': R$ '+(c.raw).toFixed(2)+'M'}}}
      },
      scales:{
        x:{stacked:true,title:{display:true,text:'R$ Milhoes',font:{size:11}},ticks:{font:{size:10}},grid:{color:'rgba(0,0,0,0.05)'}},
        y:{stacked:true,ticks:{font:{size:10,weight:'600'}},grid:{display:false}}
      }
    }
  });
})();

// Chart: Correção por Devedor
(function(){
  const ctx=document.getElementById('chartCorrecaoDev');
  if(!ctx) return;
  const sorted=[...FC_DATA].filter(d=>d.vc>0).sort((a,b)=>b.va-a.va);
  new Chart(ctx,{
    type:'bar',
    data:{
      labels:sorted.map(d=>d.s),
      datasets:[
        {label:'Val Original (R$)',data:sorted.map(d=>d.vv/1e6),backgroundColor:'rgba(37,99,235,0.5)',borderRadius:2},
        {label:'Val Corrigido SELIC (R$)',data:sorted.map(d=>d.vc/1e6),backgroundColor:'rgba(22,163,74,0.7)',borderRadius:2}
      ]
    },
    options:{
      indexAxis:'y',
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'top',labels:{font:{size:11,family:'Inter'},usePointStyle:true,pointStyleWidth:8}},
        tooltip:{callbacks:{label:function(c){return c.dataset.label+': R$ '+(c.raw).toFixed(2)+'M'}}}
      },
      scales:{
        x:{title:{display:true,text:'R$ Milhoes',font:{size:11}},ticks:{font:{size:10}},grid:{color:'rgba(0,0,0,0.05)'}},
        y:{ticks:{font:{size:10,weight:'600'}},grid:{display:false}}
      }
    }
  });
})();

// Populate faturas detalhadas table
(function(){
  const tbody=document.getElementById('tblFatDetBody');
  if(!tbody) return;
  const sorted=[...FC_DATA].sort((a,b)=>b.vv-a.vv);
  sorted.forEach((d,i)=>{
    const ganho=d.vc>0?((d.vc-d.vv)/d.vv*100):0;
    const ganhoClass=ganho>0?'val-pos':'val-neg';
    const tr=document.createElement('tr');
    tr.innerHTML='<td>'+(i+1)+'</td><td style="font-weight:600">'+d.s+'</td><td>'+d.t+'</td><td style="color:var(--success);font-weight:600">'+d.v+'</td><td style="color:var(--danger)">'+d.p+'</td><td style="font-family:var(--font-mono);font-size:11px">R$ '+(d.vv/1e6).toFixed(2)+'M</td><td style="font-family:var(--font-mono);font-size:11px;color:var(--danger)">R$ '+(d.vp/1e6).toFixed(2)+'M</td><td style="font-family:var(--font-mono);font-size:11px">R$ '+(d.vc/1e6).toFixed(2)+'M</td><td style="font-family:var(--font-mono);font-size:11px;font-weight:700">R$ '+(d.va/1e6).toFixed(2)+'M</td><td class="'+ganhoClass+'" style="font-weight:600">'+(ganho>0?'+':'')+ganho.toFixed(1)+'%</td>';
    tbody.appendChild(tr);
  });
})();

// Populate urgencias container
(function(){
  const container=document.getElementById('urgenciasContainer');
  if(!container) return;
  URGENCIAS_REAL.sort((a,b)=>a.dias-b.dias).forEach(u=>{
    const diasClass=u.dias<=30?'critico':u.dias<=90?'urgente':'normal';
    const badgeClass=u.acao.includes('5D')?'not5':'not15';
    const div=document.createElement('div');
    div.className='urgencia-row';
    div.innerHTML='<div class="urg-dias '+diasClass+'">D+'+u.dias+'</div><div class="urg-info"><div class="urg-dev">'+u.devedor+'</div><div class="urg-detail">'+u.faturas+' faturas &middot; Prescreve em '+u.prescreve_em+'</div></div><div class="urg-valor">R$ '+(u.valor/1e3).toFixed(1)+'K</div><div class="urg-acao"><span class="urg-badge '+badgeClass+'">'+u.acao+'</span></div>';
    container.appendChild(div);
  });
})();

// Chart: Prescrição por Mês
(function(){
  const ctx=document.getElementById('chartPrescMes');
  if(!ctx) return;
  const sorted=[...PRESC_MES].sort((a,b)=>{
    const [ma,ya]=a.mes.split('/');const [mb,yb]=b.mes.split('/');
    return (parseInt(ya)*100+parseInt(ma))-(parseInt(yb)*100+parseInt(mb));
  });
  new Chart(ctx,{
    type:'bar',
    data:{
      labels:sorted.map(d=>d.mes),
      datasets:[{
        label:'Faturas',
        data:sorted.map(d=>d.faturas),
        backgroundColor:sorted.map(d=>d.faturas>30?'rgba(220,38,38,0.7)':d.faturas>10?'rgba(217,119,6,0.7)':'rgba(37,99,235,0.7)'),
        borderRadius:4,
        yAxisID:'y'
      },{
        label:'Valor (R$ M)',
        data:sorted.map(d=>d.valor/1e6),
        type:'line',
        borderColor:'#C9A84C',
        backgroundColor:'rgba(201,168,76,0.1)',
        pointBackgroundColor:'#C9A84C',
        pointRadius:4,
        borderWidth:2,
        fill:true,
        yAxisID:'y1'
      }]
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'top',labels:{font:{size:11,family:'Inter'},usePointStyle:true,pointStyleWidth:8}},
        tooltip:{mode:'index',intersect:false}
      },
      scales:{
        x:{ticks:{font:{size:10}},grid:{display:false}},
        y:{position:'left',title:{display:true,text:'Faturas',font:{size:11}},ticks:{font:{size:10}},grid:{color:'rgba(0,0,0,0.05)'}},
        y1:{position:'right',title:{display:true,text:'R$ Milhoes',font:{size:11}},ticks:{font:{size:10}},grid:{display:false}}
      }
    }
  });
})();

// Chart: Ações Recomendadas Real
(function(){
  const ctx=document.getElementById('chartAcaoReal');
  if(!ctx) return;
  const colors={'DESCARTAR':'#94A3B8','EXECUTAR':'#16A34A','MONITORAR':'#2563EB','NOTIFICAR_IMEDIATO':'#DC2626','TRD':'#D97706'};
  new Chart(ctx,{
    type:'doughnut',
    data:{
      labels:ACAO_DIST.map(a=>a.acao+' ('+a.faturas+')'),
      datasets:[{
        data:ACAO_DIST.map(a=>a.faturas),
        backgroundColor:ACAO_DIST.map(a=>colors[a.acao]||'#64748B'),
        borderWidth:0,
        hoverOffset:8
      }]
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'bottom',labels:{font:{size:11,family:'Inter'},padding:12,usePointStyle:true,pointStyleWidth:8}},
        tooltip:{callbacks:{label:function(c){const a=ACAO_DIST[c.dataIndex];return a.acao+': '+a.faturas+' faturas (R$ '+(a.valor/1e6).toFixed(1)+'M)'}}}
      },
      cutout:'60%'
    }
  });
})();

// Chart: Cenários de Recuperação Real
(function(){
  const ctx=document.getElementById('chartCenariosReal');
  if(!ctx) return;
  new Chart(ctx,{
    type:'bar',
    data:{
      labels:['Conservador (20%)','Base (40%)','Otimista (70%)'],
      datasets:[
        {label:'Recuperado',data:[CENARIOS_REAL.conservador_20pct.recuperado/1e6,CENARIOS_REAL.base_40pct.recuperado/1e6,CENARIOS_REAL.otimista_70pct.recuperado/1e6],backgroundColor:['rgba(37,99,235,0.5)','rgba(37,99,235,0.7)','rgba(37,99,235,0.9)'],borderRadius:4},
        {label:'Fee 20%',data:[CENARIOS_REAL.conservador_20pct.fee_20pct/1e6,CENARIOS_REAL.base_40pct.fee_20pct/1e6,CENARIOS_REAL.otimista_70pct.fee_20pct/1e6],backgroundColor:['rgba(201,168,76,0.5)','rgba(201,168,76,0.7)','rgba(201,168,76,0.9)'],borderRadius:4}
      ]
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'top',labels:{font:{size:11,family:'Inter'},usePointStyle:true,pointStyleWidth:8}},
        tooltip:{callbacks:{label:function(c){return c.dataset.label+': R$ '+c.raw.toFixed(1)+'M'}}}
      },
      scales:{
        x:{ticks:{font:{size:11}},grid:{display:false}},
        y:{title:{display:true,text:'R$ Milhoes',font:{size:11}},ticks:{font:{size:10}},grid:{color:'rgba(0,0,0,0.05)'}}
      }
    }
  });
})();

// Chart: Canceladas vs Perdas vs Empenhos
(function(){
  const ctx=document.getElementById('chartCancPerdas');
  if(!ctx) return;
  new Chart(ctx,{
    type:'bar',
    data:{
      labels:['Fat Canceladas','Perdas SPCF','Empenhos 2026','NEs s/Cobertura','SPCF Devidas','SPCF Aberto'],
      datasets:[{
        label:'R$ Milhoes',
        data:[54.5,32.5,39.0,6.3,112.8,108.8],
        backgroundColor:['#DC2626','#EF4444','#16A34A','#22C55E','#2563EB','#3B82F6'],
        borderRadius:4
      }]
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{display:false},
        tooltip:{callbacks:{label:function(c){return 'R$ '+c.raw.toFixed(1)+'M'}}}
      },
      scales:{
        x:{ticks:{font:{size:10},maxRotation:45},grid:{display:false}},
        y:{title:{display:true,text:'R$ Milhoes',font:{size:11}},ticks:{font:{size:10}},grid:{color:'rgba(0,0,0,0.05)'}}
      }
    }
  });
})();

"""

# Insert before closing </script>
html = html.replace('</script>\n</body>', new_js + '</script>\n</body>')

# Update version
html = html.replace('Dashboard v5.1', 'Dashboard v5.2')
html = html.replace('v5.1</title>', 'v5.2</title>')
html = html.replace(
    'profiles.json v71 + SPCF Mar/2026 (247 CSVs, 900K+ linhas) + Reconciliacao Exaustiva (1.779 faturas cruzadas)',
    'profiles.json v71 + SPCF Mar/2026 (247 CSVs, 900K+ linhas) + 1.735 faturas cruzadas + Correcao SELIC + Reconciliacao Exaustiva'
)

# Write output
output_path = '/home/ubuntu/DASHBOARD_PRODAM_v5.2_BRANDAO_OZORES.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Dashboard v5.2 saved to {output_path}")
print(f"File size: {len(html):,} bytes ({len(html)/1024:.1f} KB)")
