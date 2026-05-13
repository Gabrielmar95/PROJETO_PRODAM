"""
Gera dashboard HTML interativo (auto-contido) da pasta-mãe PROJETO_PRODAM.
Usa Chart.js via CDN e dados embutidos (sem necessidade de servidor).
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path("/sessions/gallant-focused-brahmagupta/mnt/PROJETO_PRODAM/DIAGNOSTICO_PASTA_MAE.html")
PROFILE = Path("/sessions/gallant-focused-brahmagupta/mnt/outputs/profile_pasta_mae.json")
INSIGHTS = Path("/sessions/gallant-focused-brahmagupta/mnt/outputs/insights_consolidados.json")

data = json.loads(PROFILE.read_text(encoding="utf-8"))
insights = json.loads(INSIGHTS.read_text(encoding="utf-8"))

cobertura = data["cobertura_consolidado"]
dossie = data["cobertura_dossie"]
pf = data["profiles_json"]

# Montar dataset enxuto para o front
devedores_js = []
for nome in data["devedores"]:
    c = cobertura.get(nome, {})
    d = dossie.get(nome, {})
    sub_cov = {}
    for sub, s_info in c.get("subpastas", {}).items():
        sub_cov[sub] = s_info.get("files", 0)
    devedores_js.append({
        "nome": nome,
        "arquivos": c.get("total_arquivos", 0),
        "cobertura": c.get("cobertura_pct", 0),
        "dossie_cobertura": d.get("cobertura_pct", 0) if d.get("existe") else 0,
        "subpastas": sub_cov,
    })

# KPIs
kpis = {
    "n_devedores_pastas": data["n_devedores_pastas"],
    "n_devedores_profiles": pf.get("n_devedores", 0),
    "valor_exigivel": 93632770.88,
    "valor_atualizado": 160936948.41,
    "valor_original": 123225824.59,
    "fat_total": 3497,
    "fat_exigiveis": 2412,
    "fat_prescritas": 1085,
    "pct_prescritas": 31.0,
    "db_mb": data["prodam_db"]["tamanho_mb"],
    "db_registros": sum(t.get("count", 0) or 0 for t in data["prodam_db"]["tabelas"].values()),
    "n_forte": 12,
    "n_media": 15,
    "n_fraca": 42,
    "gap_por_sub": insights["gap_por_subpasta"],
    "bins_cobertura": insights["bins_cobertura"],
    "detran_arqs": cobertura.get("DETRAN", {}).get("total_arquivos", 0),
    "detran_cov": cobertura.get("DETRAN", {}).get("cobertura_pct", 0),
}

# Tabelas do banco
tabelas = []
for nome, info in data["prodam_db"]["tabelas"].items():
    if nome == "sqlite_sequence":
        continue
    tabelas.append({"nome": nome, "registros": info.get("count", 0) or 0})

payload = {
    "kpis": kpis,
    "devedores": devedores_js,
    "tabelas_db": tabelas,
    "gerado_em": data["gerado_em"],
}

PAYLOAD_JSON = json.dumps(payload, ensure_ascii=False)

html = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Diagnóstico Pasta-Mãe PROJETO_PRODAM</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {
    --azul: #1F3864;
    --azul-claro: #2E5090;
    --dourado: #B8963E;
    --carvao: #2D2D2D;
    --cinza: #777777;
    --cinza-claro: #F2F2F2;
    --vermelho: #C0392B;
    --verde: #27AE60;
    --laranja: #E67E22;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: #FAFAFA;
    color: var(--carvao);
    line-height: 1.5;
  }
  header {
    background: linear-gradient(135deg, var(--azul), var(--azul-claro));
    color: white;
    padding: 30px 40px;
    border-bottom: 4px solid var(--dourado);
  }
  header h1 {
    font-size: 26px;
    margin-bottom: 6px;
  }
  header .sub {
    font-size: 13px;
    opacity: 0.85;
    letter-spacing: 1px;
    text-transform: uppercase;
  }
  header .meta {
    margin-top: 10px;
    font-size: 11px;
    opacity: 0.7;
  }
  .container { max-width: 1400px; margin: 0 auto; padding: 30px; }
  section { margin-bottom: 40px; }
  h2 {
    color: var(--azul);
    font-size: 20px;
    border-bottom: 2px solid var(--dourado);
    padding-bottom: 8px;
    margin-bottom: 20px;
  }
  h3 { color: var(--azul); font-size: 15px; margin-bottom: 10px; }
  .grid-kpi {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 16px;
  }
  .kpi {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    border-left: 5px solid var(--azul);
  }
  .kpi.dourado { border-left-color: var(--dourado); }
  .kpi.verde { border-left-color: var(--verde); }
  .kpi.vermelho { border-left-color: var(--vermelho); }
  .kpi.laranja { border-left-color: var(--laranja); }
  .kpi .label { font-size: 11px; color: var(--cinza); text-transform: uppercase; letter-spacing: 1px; }
  .kpi .valor { font-size: 26px; font-weight: bold; color: var(--azul); margin-top: 4px; }
  .kpi .extra { font-size: 11px; color: var(--cinza); margin-top: 4px; }
  .charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
  .chart-box {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.07);
  }
  .chart-box canvas { max-height: 300px; }
  @media (max-width: 900px) { .charts-grid { grid-template-columns: 1fr; } }
  .tabela-wrap {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    overflow-x: auto;
  }
  table { width: 100%; border-collapse: collapse; }
  thead th {
    background: var(--azul);
    color: white;
    padding: 10px 8px;
    text-align: left;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  tbody td { padding: 8px; border-bottom: 1px solid var(--cinza-claro); font-size: 13px; }
  tbody tr:nth-child(even) { background: #FAFAFA; }
  tbody tr:hover { background: #FFF8E5; }
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
  }
  .b-forte { background: #D4EDDA; color: #1E6B2E; }
  .b-media { background: #FFF3CD; color: #7A5C00; }
  .b-fraca { background: #F8D7DA; color: #7A1E25; }
  .b-zero  { background: #EEE; color: #666; }
  .filtros { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
  .filtros input, .filtros select {
    padding: 8px 12px;
    border: 1px solid #DDD;
    border-radius: 6px;
    font-size: 13px;
    font-family: inherit;
  }
  .filtros input { flex: 1; min-width: 200px; }
  .heatmap-cell {
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: white;
    padding: 4px;
    min-width: 40px;
  }
  .legenda {
    font-size: 11px;
    color: var(--cinza);
    margin-top: 10px;
    font-style: italic;
  }
  footer {
    text-align: center;
    padding: 20px;
    font-size: 12px;
    color: var(--cinza);
    border-top: 1px solid #DDD;
    margin-top: 40px;
  }
</style>
</head>
<body>
<header>
  <h1>Diagnóstico Técnico — Pasta-Mãe PROJETO_PRODAM</h1>
  <div class="sub">Análise de cientista de dados | Contrato 002/2026</div>
  <div class="meta">Gabriel Mar Sociedade Individual de Advocacia | OAB/AM 15.697 | Gerado em <span id="data-ger"></span></div>
</header>

<div class="container">

  <section>
    <h2>Visão geral — KPIs</h2>
    <div class="grid-kpi" id="kpis"></div>
  </section>

  <section>
    <h2>Distribuição de cobertura documental</h2>
    <div class="charts-grid">
      <div class="chart-box"><h3>Cobertura dos devedores (_CONSOLIDADO)</h3><canvas id="chartCobertura"></canvas></div>
      <div class="chart-box"><h3>Subpastas com maiores lacunas</h3><canvas id="chartGaps"></canvas></div>
      <div class="chart-box"><h3>Força probatória do portfólio</h3><canvas id="chartForca"></canvas></div>
      <div class="chart-box"><h3>Faturas: exigíveis × prescritas</h3><canvas id="chartFaturas"></canvas></div>
    </div>
  </section>

  <section>
    <h2>Benchmark DETRAN × Top-10 devedores</h2>
    <div class="chart-box"><canvas id="chartBenchmark" style="max-height:380px"></canvas></div>
    <div class="legenda">DETRAN é a única pasta-filha com cobertura ≥80% (score 94/100 A+). Os demais precisam de execução da pipeline orgao_pipeline_completa.py.</div>
  </section>

  <section>
    <h2>Heatmap de cobertura por subpasta (todos os 78 devedores)</h2>
    <div class="tabela-wrap" id="heatmap-wrap"></div>
    <div class="legenda">Verde = tem arquivos; cinza = vazio. Ler linhas esquerda→direita: 01_CONTRATOS, 02_EMPENHOS, ..., 09_RELATORIOS.</div>
  </section>

  <section>
    <h2>Tabela completa de devedores (filtre e ordene)</h2>
    <div class="filtros">
      <input id="busca" placeholder="🔍  Busca por nome...">
      <select id="ordenar">
        <option value="arquivos">Ordenar por: arquivos ↓</option>
        <option value="cobertura">Ordenar por: cobertura ↓</option>
        <option value="nome">Ordenar por: nome A→Z</option>
      </select>
    </div>
    <div class="tabela-wrap"><table><thead><tr>
      <th>#</th><th>Devedor</th><th>Arquivos</th><th>Cobertura</th><th>Dossiê</th><th>Status</th>
    </tr></thead><tbody id="tabela-dev"></tbody></table></div>
  </section>

  <section>
    <h2>Tabelas da base prodam.db</h2>
    <div class="tabela-wrap"><table><thead><tr>
      <th>Tabela</th><th>Registros</th>
    </tr></thead><tbody id="tabela-db"></tbody></table></div>
  </section>

</div>

<footer>
  Relatório gerado automaticamente a partir de profile_pasta_mae.py.<br>
  Para regenerar: <code>python3 profile_pasta_mae.py &amp;&amp; python3 gerar_dashboard.py</code>
</footer>

<script>
const DATA = __PAYLOAD__;

// Helpers
const brl = v => 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmt = n => n.toLocaleString('pt-BR');

// Data
document.getElementById('data-ger').textContent = DATA.gerado_em;

// KPIs
const kpi = DATA.kpis;
const kpiConfigs = [
  { label: 'Devedores (pastas)', valor: kpi.n_devedores_pastas, extra: kpi.n_devedores_profiles + ' no profiles.json', cls: '' },
  { label: 'Valor exigível', valor: brl(kpi.valor_exigivel), extra: 'Original: ' + brl(kpi.valor_original), cls: 'dourado' },
  { label: 'Valor atualizado', valor: brl(kpi.valor_atualizado), extra: '+72% vs exigível', cls: 'dourado' },
  { label: 'Faturas totais', valor: fmt(kpi.fat_total), extra: fmt(kpi.fat_exigiveis) + ' exigíveis | ' + fmt(kpi.fat_prescritas) + ' prescritas', cls: '' },
  { label: 'Prescrição', valor: kpi.pct_prescritas.toFixed(1) + '%', extra: fmt(kpi.fat_prescritas) + ' faturas perdidas', cls: 'vermelho' },
  { label: 'prodam.db', valor: kpi.db_mb + ' MB', extra: fmt(kpi.db_registros) + ' registros em 8 tabelas', cls: '' },
  { label: 'Benchmark DETRAN', valor: kpi.detran_cov + '%', extra: fmt(kpi.detran_arqs) + ' arquivos | A+ 94/100', cls: 'verde' },
  { label: 'Força FORTE', valor: kpi.n_forte, extra: kpi.n_media + ' MÉDIA | ' + kpi.n_fraca + ' FRACA', cls: 'laranja' },
];
document.getElementById('kpis').innerHTML = kpiConfigs.map(k =>
  `<div class="kpi ${k.cls}"><div class="label">${k.label}</div><div class="valor">${k.valor}</div><div class="extra">${k.extra}</div></div>`
).join('');

// Chart colors
const C_AZUL = '#1F3864';
const C_DOURADO = '#B8963E';
const C_VERDE = '#27AE60';
const C_VERMELHO = '#C0392B';
const C_LARANJA = '#E67E22';

// Cobertura bins
new Chart(document.getElementById('chartCobertura'), {
  type: 'doughnut',
  data: {
    labels: Object.keys(kpi.bins_cobertura),
    datasets: [{
      data: Object.values(kpi.bins_cobertura),
      backgroundColor: [C_VERDE, '#7FB77E', C_LARANJA, '#E88C56', C_VERMELHO],
      borderWidth: 2, borderColor: '#fff'
    }]
  },
  options: { responsive: true, plugins: { legend: { position: 'right' } } }
});

// Gaps
const gapsEntries = Object.entries(kpi.gap_por_sub).sort((a,b) => b[1]-a[1]);
new Chart(document.getElementById('chartGaps'), {
  type: 'bar',
  data: {
    labels: gapsEntries.map(e => e[0]),
    datasets: [{
      label: 'Devedores sem arquivos',
      data: gapsEntries.map(e => e[1]),
      backgroundColor: C_VERMELHO,
      borderRadius: 4
    }]
  },
  options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } } }
});

// Força
new Chart(document.getElementById('chartForca'), {
  type: 'pie',
  data: {
    labels: ['FORTE (execução)', 'MÉDIA (monitória)', 'FRACA (cobrança)'],
    datasets: [{
      data: [kpi.n_forte, kpi.n_media, kpi.n_fraca],
      backgroundColor: [C_VERDE, C_LARANJA, C_VERMELHO],
      borderWidth: 2, borderColor: '#fff'
    }]
  },
  options: { responsive: true, plugins: { legend: { position: 'right' } } }
});

// Faturas
new Chart(document.getElementById('chartFaturas'), {
  type: 'doughnut',
  data: {
    labels: ['Exigíveis', 'Prescritas'],
    datasets: [{
      data: [kpi.fat_exigiveis, kpi.fat_prescritas],
      backgroundColor: [C_VERDE, C_VERMELHO],
      borderWidth: 2, borderColor: '#fff'
    }]
  },
  options: { responsive: true, plugins: { legend: { position: 'right' } } }
});

// Benchmark
const topNomes = ['DETRAN','SSP','SEDECTI','SES','FAAR','SEDUC','SEAD','SEC','POLICIA_CIVIL','SEJUSC','IPAAM'];
const topArqs = topNomes.map(n => {
  const d = DATA.devedores.find(x => x.nome === n);
  return d ? d.arquivos : 0;
});
const topCov = topNomes.map(n => {
  const d = DATA.devedores.find(x => x.nome === n);
  return d ? d.cobertura : 0;
});
new Chart(document.getElementById('chartBenchmark'), {
  type: 'bar',
  data: {
    labels: topNomes,
    datasets: [
      { label: 'Arquivos', data: topArqs, backgroundColor: C_AZUL, borderRadius: 4, yAxisID: 'y' },
      { label: 'Cobertura %', data: topCov, backgroundColor: C_DOURADO, borderRadius: 4, yAxisID: 'y1', type: 'line', tension: 0.3 },
    ]
  },
  options: {
    responsive: true,
    scales: {
      y: { position: 'left', title: { display: true, text: 'Arquivos' } },
      y1: { position: 'right', title: { display: true, text: 'Cobertura %' }, min: 0, max: 100, grid: { display: false } }
    }
  }
});

// Heatmap
const subs = ['01_CONTRATOS','02_EMPENHOS','03_FATURAS','04_NOTAS_LIQUIDACAO','05_ACEITES','06_COBRANCAS','07_SCRAPING_SPCF','08_PDFS_ORIGINAIS','09_RELATORIOS'];
function heatColor(files) {
  if (files === 0) return '#EEE';
  if (files < 5) return '#F5B041';
  if (files < 20) return '#F4D03F';
  if (files < 50) return '#82E0AA';
  return '#27AE60';
}
let heatHTML = '<table><thead><tr><th>Devedor</th>';
subs.forEach(s => { heatHTML += `<th style="font-size:9px">${s.slice(0,7)}</th>`; });
heatHTML += '<th>Total</th></tr></thead><tbody>';
[...DATA.devedores].sort((a,b)=>b.arquivos-a.arquivos).forEach(d => {
  heatHTML += `<tr><td style="font-weight:600">${d.nome}</td>`;
  subs.forEach(s => {
    const v = d.subpastas[s] || 0;
    heatHTML += `<td class="heatmap-cell" style="background:${heatColor(v)}; color:${v===0?'#999':'#000'}">${v || '—'}</td>`;
  });
  heatHTML += `<td style="font-weight:600">${d.arquivos}</td></tr>`;
});
heatHTML += '</tbody></table>';
document.getElementById('heatmap-wrap').innerHTML = heatHTML;

// Tabela devedores
function renderTabela() {
  const q = document.getElementById('busca').value.toLowerCase();
  const ord = document.getElementById('ordenar').value;
  let lista = DATA.devedores.filter(d => d.nome.toLowerCase().includes(q));
  if (ord === 'arquivos') lista.sort((a,b)=>b.arquivos-a.arquivos);
  else if (ord === 'cobertura') lista.sort((a,b)=>b.cobertura-a.cobertura);
  else lista.sort((a,b)=>a.nome.localeCompare(b.nome));
  const html = lista.map((d,i) => {
    let status = '<span class="badge b-zero">0-19%</span>';
    if (d.cobertura >= 80) status = '<span class="badge b-forte">80-100%</span>';
    else if (d.cobertura >= 50) status = '<span class="badge b-media">50-79%</span>';
    else if (d.cobertura >= 20) status = '<span class="badge b-fraca">20-49%</span>';
    return `<tr><td>${i+1}</td><td><strong>${d.nome}</strong></td><td>${fmt(d.arquivos)}</td><td>${d.cobertura}%</td><td>${d.dossie_cobertura}%</td><td>${status}</td></tr>`;
  }).join('');
  document.getElementById('tabela-dev').innerHTML = html;
}
document.getElementById('busca').oninput = renderTabela;
document.getElementById('ordenar').onchange = renderTabela;
renderTabela();

// Tabela DB
document.getElementById('tabela-db').innerHTML = DATA.tabelas_db
  .sort((a,b)=>b.registros-a.registros)
  .map(t => `<tr><td><strong>${t.nome}</strong></td><td>${fmt(t.registros)}</td></tr>`)
  .join('');
</script>
</body>
</html>
"""

html = html.replace("__PAYLOAD__", PAYLOAD_JSON)
OUT.write_text(html, encoding="utf-8")
print(f"[OK] Dashboard salvo em: {OUT}")
print(f"Tamanho: {OUT.stat().st_size / 1024:.1f} KB")
