#!/usr/bin/env python3
"""
Inject Reconciliação SPCF sections into Dashboard PRODAM v5.0
"""

import re

# Read the current dashboard
with open('/home/ubuntu/DASHBOARD_PRODAM_v5.0_BRANDAO_OZORES.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# 1. ADD NEW CSS STYLES
# ============================================================
new_css = """
/* ===== RECONCILIACAO STYLES ===== */
.recon-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.recon-stat-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 20px;
  text-align: center;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}
.recon-stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.recon-stat-card .stat-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); margin-bottom: 6px; font-weight: 600; }
.recon-stat-card .stat-value { font-size: 28px; font-weight: 800; font-family: var(--font-mono); }
.recon-stat-card .stat-sub { font-size: 11px; color: var(--text-secondary); margin-top: 4px; }
.recon-stat-card.match .stat-value { color: var(--success); }
.recon-stat-card.diverge .stat-value { color: var(--warn); }
.recon-stat-card.critical .stat-value { color: var(--danger); }
.recon-stat-card.info .stat-value { color: var(--info); }
.recon-stat-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
}
.recon-stat-card.match::after { background: var(--success); }
.recon-stat-card.diverge::after { background: var(--warn); }
.recon-stat-card.critical::after { background: var(--danger); }
.recon-stat-card.info::after { background: var(--info); }

.recon-divergence-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 12px;
}
.recon-divergence-table th {
  background: var(--bg-alt);
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: var(--muted);
  border-bottom: 2px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 2;
}
.recon-divergence-table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-light);
  vertical-align: middle;
}
.recon-divergence-table tr:hover td { background: var(--bg-alt); }
.recon-divergence-table .val-pos { color: var(--success); font-weight: 600; }
.recon-divergence-table .val-neg { color: var(--danger); font-weight: 600; }
.recon-divergence-table .status-ok { background: var(--success-bg); color: var(--success); padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.recon-divergence-table .status-minor { background: var(--info-bg); color: var(--info); padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.recon-divergence-table .status-major { background: var(--warn-bg); color: var(--warn); padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.recon-divergence-table .status-critical { background: var(--danger-bg); color: var(--danger); padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }

.recon-charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;
}
.recon-chart-panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
}
.recon-chart-panel h4 {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--text);
}

.inconsistency-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 16px;
}
.inconsistency-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 18px;
  border-left: 4px solid var(--danger);
}
.inconsistency-card.warn { border-left-color: var(--warn); }
.inconsistency-card.info { border-left-color: var(--info); }
.inconsistency-card h5 { font-size: 13px; font-weight: 700; margin-bottom: 6px; }
.inconsistency-card .inc-value { font-size: 22px; font-weight: 800; font-family: var(--font-mono); color: var(--danger); }
.inconsistency-card.warn .inc-value { color: var(--warn); }
.inconsistency-card.info .inc-value { color: var(--info); }
.inconsistency-card .inc-desc { font-size: 11px; color: var(--text-secondary); margin-top: 4px; }

.enrichment-timeline {
  position: relative;
  padding-left: 30px;
  margin-top: 20px;
}
.enrichment-timeline::before {
  content: '';
  position: absolute;
  left: 12px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border);
}
.enrichment-step {
  position: relative;
  margin-bottom: 20px;
  padding: 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
}
.enrichment-step::before {
  content: '';
  position: absolute;
  left: -24px;
  top: 20px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--card);
  box-shadow: 0 0 0 2px var(--accent);
}
.enrichment-step .step-date { font-size: 11px; color: var(--muted); font-weight: 600; text-transform: uppercase; }
.enrichment-step .step-title { font-size: 14px; font-weight: 700; margin: 4px 0; }
.enrichment-step .step-detail { font-size: 12px; color: var(--text-secondary); }
.enrichment-step .step-badges { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.enrichment-step .step-badge { font-size: 10px; padding: 2px 8px; border-radius: 4px; font-weight: 600; background: var(--accent-glow); color: var(--accent); }
.enrichment-step .step-badge.green { background: var(--success-bg); color: var(--success); }
.enrichment-step .step-badge.red { background: var(--danger-bg); color: var(--danger); }

.faturas-cruzadas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-top: 16px;
}
.fc-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 14px;
  text-align: center;
}
.fc-card .fc-dev { font-size: 12px; font-weight: 700; margin-bottom: 4px; }
.fc-card .fc-fat { font-size: 18px; font-weight: 800; font-family: var(--font-mono); color: var(--accent); }
.fc-card .fc-sub { font-size: 10px; color: var(--text-secondary); margin-top: 2px; }
.fc-card .fc-bar { height: 4px; border-radius: 2px; background: var(--border); margin-top: 8px; overflow: hidden; }
.fc-card .fc-bar-fill { height: 100%; border-radius: 2px; }
.fc-bar-fill.green { background: var(--success); }
.fc-bar-fill.red { background: var(--danger); }
.fc-bar-fill.orange { background: var(--warn); }
"""

# Insert new CSS before the closing </style> tag
html = html.replace('</style>', new_css + '\n</style>', 1)

# ============================================================
# 2. ADD SIDEBAR NAVIGATION ITEMS
# ============================================================
# Add "Reconciliacao" section to sidebar before "Estrategia"
sidebar_addition = """    <div class="nav-section">Reconciliacao</div>
    <a href="#recon-overview"><span class="nav-icon">&#8644;</span> Visao SPCF</a>
    <a href="#recon-divergencias"><span class="nav-icon">&#9888;</span> Divergencias</a>
    <a href="#recon-inconsistencias"><span class="nav-icon">&#9888;</span> Inconsistencias</a>
    <a href="#recon-faturas"><span class="nav-icon">&#9776;</span> Faturas Cruzadas</a>
    <a href="#recon-enriquecimento"><span class="nav-icon">&#9650;</span> Enriquecimento</a>
"""

html = html.replace(
    '    <div class="nav-section">Estrategia</div>',
    sidebar_addition + '    <div class="nav-section">Estrategia</div>'
)

# ============================================================
# 3. ADD RECONCILIATION HTML SECTIONS
# ============================================================
# Insert before the Insights section
recon_html = """
    <!-- ===== RECONCILIACAO SPCF ===== -->
    <section id="recon-overview">
      <div class="section-header animate-in">
        <h2><span class="section-icon">&#8644;</span> Reconciliacao SPCF Mar/2026</h2>
        <span class="section-badge">01/04/2026</span>
      </div>

      <!-- Summary Stats -->
      <div class="recon-summary-grid animate-in">
        <div class="recon-stat-card info">
          <div class="stat-label">Clientes SPCF</div>
          <div class="stat-value">333</div>
          <div class="stat-sub">4.040 faturas no sistema</div>
        </div>
        <div class="recon-stat-card info">
          <div class="stat-label">Devedores Mapeados</div>
          <div class="stat-value">65</div>
          <div class="stat-sub">de 71 no profiles.json</div>
        </div>
        <div class="recon-stat-card match">
          <div class="stat-label">Matches (&lt;1%)</div>
          <div class="stat-value">12</div>
          <div class="stat-sub">Valores conferem</div>
        </div>
        <div class="recon-stat-card diverge">
          <div class="stat-label">Divergentes (&gt;1%)</div>
          <div class="stat-value">53</div>
          <div class="stat-sub">Requerem analise</div>
        </div>
        <div class="recon-stat-card critical">
          <div class="stat-label">Nao Mapeados</div>
          <div class="stat-value">264</div>
          <div class="stat-sub">Clientes SPCF sem match</div>
        </div>
      </div>

      <!-- Totals comparison -->
      <div class="panel animate-in" style="margin-bottom:20px">
        <h4 style="margin-bottom:12px;font-size:14px;font-weight:700">Comparacao de Totais &mdash; SPCF vs profiles.json</h4>
        <div class="recon-summary-grid">
          <div class="recon-stat-card info">
            <div class="stat-label">SPCF Val. Servicos (Todos)</div>
            <div class="stat-value" style="font-size:20px">R$ 152,4M</div>
            <div class="stat-sub">333 clientes</div>
          </div>
          <div class="recon-stat-card info">
            <div class="stat-label">SPCF Val. Liquido (Mapeados)</div>
            <div class="stat-value" style="font-size:20px">R$ 122,4M</div>
            <div class="stat-sub">65 devedores mapeados</div>
          </div>
          <div class="recon-stat-card diverge">
            <div class="stat-label">Profiles val_orig (Mapeados)</div>
            <div class="stat-value" style="font-size:20px">R$ 118,7M</div>
            <div class="stat-sub">Valor nominal original</div>
          </div>
          <div class="recon-stat-card match">
            <div class="stat-label">Profiles val_exig (Mapeados)</div>
            <div class="stat-value" style="font-size:20px">R$ 120,6M</div>
            <div class="stat-sub">Com correcao monetaria</div>
          </div>
        </div>
      </div>

      <!-- Charts: Divergence distribution + Match status -->
      <div class="recon-charts-grid animate-in">
        <div class="recon-chart-panel">
          <h4>Distribuicao de Status de Reconciliacao</h4>
          <canvas id="chartReconStatus" height="280"></canvas>
        </div>
        <div class="recon-chart-panel">
          <h4>Top 15 Divergencias por Valor Absoluto</h4>
          <canvas id="chartReconDiverg" height="280"></canvas>
        </div>
      </div>
    </section>

    <!-- ===== DIVERGENCIAS DETALHADAS ===== -->
    <section id="recon-divergencias">
      <div class="section-header animate-in">
        <h2><span class="section-icon">&#9888;</span> Tabela de Divergencias SPCF vs profiles.json</h2>
        <span class="section-badge">65 devedores comparados</span>
      </div>
      <div class="panel animate-in" style="padding:0;overflow:hidden">
        <div class="tbl-wrap">
          <table class="recon-divergence-table" id="tblRecon">
            <thead>
              <tr>
                <th>#</th>
                <th>Devedor</th>
                <th>Fat SPCF</th>
                <th>Val Liq SPCF</th>
                <th>Val Orig Profiles</th>
                <th>Divergencia</th>
                <th>%</th>
                <th>Status</th>
                <th>Nota</th>
              </tr>
            </thead>
            <tbody id="tblReconBody"></tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ===== INCONSISTENCIAS ===== -->
    <section id="recon-inconsistencias">
      <div class="section-header animate-in">
        <h2><span class="section-icon">&#9888;</span> Inconsistencias &amp; Achados Criticos</h2>
        <span class="section-badge">938 inconsistencias</span>
      </div>

      <div class="inconsistency-grid animate-in">
        <div class="inconsistency-card">
          <h5>PAGA_EM_DEVIDAS</h5>
          <div class="inc-value">874</div>
          <div class="inc-desc">Faturas pagas mas constam como devidas no portfolio. SEJUSC (101), SSP (99), ADS (99), SUHAB (89) lideram.</div>
        </div>
        <div class="inconsistency-card warn">
          <h5>Canceladas x Perdas</h5>
          <div class="inc-value">47</div>
          <div class="inc-desc">Dupla baixa contabil &mdash; faturas canceladas E em perdas. Superavaliacao potencial de ate R$ 34,7M.</div>
        </div>
        <div class="inconsistency-card">
          <h5>Canceladas x Devidas</h5>
          <div class="inc-value">11</div>
          <div class="inc-desc">Cobranca indevida &mdash; faturas canceladas mas ainda em cobranca. Risco reputacional alto.</div>
        </div>
        <div class="inconsistency-card warn">
          <h5>Canceladas x Aberto</h5>
          <div class="inc-value">6</div>
          <div class="inc-desc">Faturas canceladas mas em aberto no SPCF. Depuracao obrigatoria antes de notificacao.</div>
        </div>
        <div class="inconsistency-card info">
          <h5>NEs SEM COBERTURA</h5>
          <div class="inc-value">60</div>
          <div class="inc-desc">SES (32 NEs, R$ 6,28M) + FHEMOAM (28 NEs, R$ 1,33M). Reconhecimento tacito atualissimo &mdash; argumento nuclear.</div>
        </div>
        <div class="inconsistency-card info">
          <h5>BMC &mdash; Cronico</h5>
          <div class="inc-value">0%</div>
          <div class="inc-desc">Zero pagamento em 87 meses de faturamento. Unico devedor CRONICO. Candidato a execucao judicial direta.</div>
        </div>
      </div>

      <div class="recon-charts-grid animate-in" style="margin-top:20px">
        <div class="recon-chart-panel">
          <h4>Inconsistencias por Devedor (Top 10)</h4>
          <canvas id="chartInconsist" height="280"></canvas>
        </div>
        <div class="recon-chart-panel">
          <h4>Padrao de Inadimplencia &mdash; Classificacao</h4>
          <canvas id="chartPadraoRecon" height="280"></canvas>
        </div>
      </div>
    </section>

    <!-- ===== FATURAS CRUZADAS ===== -->
    <section id="recon-faturas">
      <div class="section-header animate-in">
        <h2><span class="section-icon">&#9776;</span> Faturas Cruzadas &mdash; Top 20 Devedores</h2>
        <span class="section-badge">1.779 faturas &middot; 58 colunas &middot; 14 fontes</span>
      </div>

      <div class="recon-summary-grid animate-in">
        <div class="recon-stat-card info">
          <div class="stat-label">Total Faturas</div>
          <div class="stat-value">1.779</div>
          <div class="stat-sub">20 devedores processados</div>
        </div>
        <div class="recon-stat-card match">
          <div class="stat-label">Vigentes</div>
          <div class="stat-value">1.208</div>
          <div class="stat-sub">67,9% do total</div>
        </div>
        <div class="recon-stat-card critical">
          <div class="stat-label">Prescritas</div>
          <div class="stat-value">571</div>
          <div class="stat-sub">32,1% do total</div>
        </div>
        <div class="recon-stat-card diverge">
          <div class="stat-label">Criticas &lt;90d</div>
          <div class="stat-value">34</div>
          <div class="stat-sub">24 com &lt;45 dias</div>
        </div>
        <div class="recon-stat-card match">
          <div class="stat-label">Forca FORTE+</div>
          <div class="stat-value">729</div>
          <div class="stat-sub">40,9% &mdash; posicao processual excelente</div>
        </div>
        <div class="recon-stat-card info">
          <div class="stat-label">Com Empenho</div>
          <div class="stat-value">1.476</div>
          <div class="stat-sub">83,0% &mdash; reconhecimento tacito</div>
        </div>
      </div>

      <div class="recon-charts-grid animate-in">
        <div class="recon-chart-panel">
          <h4>Faturas por Devedor &mdash; Vigentes vs Prescritas</h4>
          <canvas id="chartFatCruzadas" height="350"></canvas>
        </div>
        <div class="recon-chart-panel">
          <h4>Acao Recomendada &mdash; Distribuicao</h4>
          <canvas id="chartAcaoRecom" height="350"></canvas>
        </div>
      </div>

      <div class="panel animate-in" style="margin-top:20px">
        <h4 style="margin-bottom:12px;font-size:14px;font-weight:700">Faturas Criticas &lt;45 dias &mdash; NOTIFICAR IMEDIATO</h4>
        <div class="tbl-wrap">
          <table class="recon-divergence-table">
            <thead>
              <tr>
                <th>Seq</th>
                <th>Devedor</th>
                <th>NF</th>
                <th>Valor (R$)</th>
                <th>Dias ate Prescr.</th>
                <th>Data Limite</th>
                <th>Acao</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>1-18</td><td>ADS</td><td>18 faturas</td><td style="font-weight:700">R$ 30.427,70</td><td style="color:var(--danger);font-weight:700">11</td><td>12/04/2026</td><td><span class="status-critical">NOTIFICAR_IMEDIATO</span></td></tr>
              <tr><td>19-21</td><td>SUHAB</td><td>3 faturas</td><td style="font-weight:700">R$ 3.597,97</td><td style="color:var(--danger);font-weight:700">22</td><td>23/04/2026</td><td><span class="status-critical">NOTIFICAR_IMEDIATO</span></td></tr>
              <tr><td>22-23</td><td>SUHAB</td><td>2 faturas</td><td style="font-weight:700">R$ 40.925,56</td><td style="color:var(--warn);font-weight:700">26</td><td>27/04/2026</td><td><span class="status-critical">NOTIFICAR_IMEDIATO</span></td></tr>
              <tr><td>24</td><td>SEPROR</td><td>123942</td><td style="font-weight:700">R$ 623,75</td><td style="color:var(--warn);font-weight:700">29</td><td>30/04/2026</td><td><span class="status-critical">NOTIFICAR_IMEDIATO</span></td></tr>
              <tr style="background:var(--danger-bg);font-weight:700"><td colspan="2">SES/SUSAM</td><td>Of.129/2021</td><td>R$ 11.877.977,07</td><td style="color:var(--danger)">42</td><td>13/05/2026</td><td><span class="status-critical">CPRAC/PGE-AM IMEDIATO</span></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ===== ENRIQUECIMENTO ===== -->
    <section id="recon-enriquecimento">
      <div class="section-header animate-in">
        <h2><span class="section-icon">&#9650;</span> Timeline de Enriquecimento de Dados</h2>
        <span class="section-badge">900.537+ registros processados</span>
      </div>

      <div class="enrichment-timeline animate-in">
        <div class="enrichment-step">
          <div class="step-date">30/03/2026 &mdash; Snapshot Inicial</div>
          <div class="step-title">Reconciliacao v0.1 &mdash; Primeira Comparacao</div>
          <div class="step-detail">52 devedores em profiles.json vs 333 clientes SPCF. Apenas 4 matches (&lt;1%). Identificadas divergencias massivas em SEDUC (+55%), SES/SUSAM (-63%), SEAD (+97%).</div>
          <div class="step-badges">
            <span class="step-badge">52 devedores</span>
            <span class="step-badge red">4 matches</span>
            <span class="step-badge red">41 divergentes</span>
          </div>
        </div>
        <div class="enrichment-step">
          <div class="step-date">31/03/2026 &mdash; Integracao SPCF</div>
          <div class="step-title">Changelog: 35 atualizados + 11 novos devedores</div>
          <div class="step-detail">Adicionados 11 campos SPCF por devedor (spcf_total_receber, fat_devidas, fat_aberto, perdas, emp_2026, contratos_vigentes). Total: 62 devedores.</div>
          <div class="step-badges">
            <span class="step-badge green">+35 atualizados</span>
            <span class="step-badge green">+11 novos</span>
            <span class="step-badge">62 devedores</span>
          </div>
        </div>
        <div class="enrichment-step">
          <div class="step-date">01/04/2026 02:24 &mdash; Integracao Exaustiva</div>
          <div class="step-title">715 campos em 41 devedores + 8 novos devedores</div>
          <div class="step-detail">Processados 247 CSVs (900K+ linhas) dos 7 blocos SPCF. Novos: CASA CIVIL, COSAMA, CASA MILITAR, BANCO DAYCOVAL, IMPRENSA OFICIAL, JUCEA, AFEAM, CIAMA. Zero inconsistencias em val_orig/val_exig.</div>
          <div class="step-badges">
            <span class="step-badge green">+715 campos</span>
            <span class="step-badge green">+8 novos</span>
            <span class="step-badge">70 devedores</span>
            <span class="step-badge green">0 inconsistencias</span>
          </div>
        </div>
        <div class="enrichment-step">
          <div class="step-date">01/04/2026 06:09 &mdash; Reconciliacao Final</div>
          <div class="step-title">65 mapeados, 12 matches, 53 divergentes</div>
          <div class="step-detail">Reconciliacao v1.0 completa com Val Liquido SPCF. Melhoria de 4 para 12 matches. Identificados merges (FENIXSOFT 2x, FAAR/SEDEL 2x, PGE 2x, SECT 2x). 71 devedores finais.</div>
          <div class="step-badges">
            <span class="step-badge green">12 matches</span>
            <span class="step-badge">53 divergentes</span>
            <span class="step-badge">71 devedores</span>
            <span class="step-badge green">100% cobertura</span>
          </div>
        </div>
      </div>

      <div class="panel animate-in" style="margin-top:20px">
        <h4 style="margin-bottom:12px;font-size:14px;font-weight:700">Achados que Alteram o Portfolio</h4>
        <div class="tbl-wrap">
          <table class="recon-divergence-table">
            <thead>
              <tr>
                <th>Fator</th>
                <th>Impacto Potencial</th>
                <th>Direcao</th>
                <th>Validacao</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Faturas canceladas (R$ 55M liq. total)</td><td style="font-weight:700">Ate -R$ 55M</td><td class="val-neg">&#9660; REDUZ</td><td>Confirmar se sao baixa definitiva</td></tr>
              <tr><td>Dupla-baixa canceladas x perdas</td><td style="font-weight:700">Ate -R$ 34,7M superavaliacao</td><td class="val-neg">&#9660; REDUZ</td><td>Auditoria contabil PRODAM</td></tr>
              <tr><td>"A Empenhar 2026" R$ 65,8M</td><td style="font-weight:700">+R$ 65,8M obrigacao futura</td><td class="val-pos">&#9650; REFORCA</td><td>Confirmado no SPCF</td></tr>
              <tr><td>NEs SEM COBERTURA R$ 6,28M</td><td style="font-weight:700">+R$ 6,28M reconhecimento tacito</td><td class="val-pos">&#9650; REFORCA</td><td>Confirmado: 60 NEs</td></tr>
              <tr style="font-weight:700;background:var(--bg-alt)"><td>Saldo Liquido</td><td>Portfolio R$ 127,6M permanece, composicao muda</td><td>&mdash;</td><td>Validar com PRODAM</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

"""

# Insert before the insights section
html = html.replace(
    '    <!-- ===== INSIGHTS ===== -->',
    recon_html + '    <!-- ===== INSIGHTS ===== -->'
)

# ============================================================
# 4. ADD RECONCILIATION JAVASCRIPT
# ============================================================
recon_js = """

/* ===== RECONCILIACAO CHARTS ===== */

// Reconciliation data
const RECON_DATA = [
  {dev:"SEDUC",fat:128,spcf:56040239.62,prof:38705633.18,div:44.8,st:"CRITICAL"},
  {dev:"DETRAN",fat:202,spcf:20848440.34,prof:22745276.48,div:8.3,st:"MAJOR"},
  {dev:"SES/SUSAM",fat:215,spcf:11877761.92,prof:22406424.64,div:47.0,st:"CRITICAL"},
  {dev:"SSP",fat:181,spcf:10725242.83,prof:12532319.38,div:14.4,st:"MAJOR"},
  {dev:"SEAD",fat:97,spcf:5293077.30,prof:2772731.09,div:90.9,st:"CRITICAL"},
  {dev:"SEJUSC",fat:158,spcf:2671397.51,prof:3025777.73,div:11.7,st:"MAJOR"},
  {dev:"SEDECTI",fat:145,spcf:1931906.33,prof:2012035.99,div:4.0,st:"MINOR"},
  {dev:"PGE",fat:55,spcf:1396512.22,prof:849643.14,div:64.4,st:"CRITICAL"},
  {dev:"CETAM",fat:15,spcf:1256564.27,prof:1256564.28,div:0.0,st:"MATCH"},
  {dev:"CAIXA",fat:71,spcf:988460.57,prof:844328.88,div:17.1,st:"MAJOR"},
  {dev:"BANCO MASTER",fat:57,spcf:967386.73,prof:889270.87,div:8.8,st:"MAJOR"},
  {dev:"FENIXSOFT",fat:14,spcf:934800.00,prof:888250.00,div:5.2,st:"MAJOR"},
  {dev:"POL.CIVIL",fat:50,spcf:742177.44,prof:1066717.79,div:30.4,st:"CRITICAL"},
  {dev:"SUHAB",fat:107,spcf:636026.33,prof:710644.00,div:10.5,st:"MAJOR"},
  {dev:"PROVER",fat:52,spcf:614024.90,prof:549105.70,div:11.8,st:"MAJOR"},
  {dev:"FAAR/SEDEL",fat:118,spcf:525860.25,prof:877764.20,div:40.1,st:"CRITICAL"},
  {dev:"SETRAB",fat:75,spcf:505899.62,prof:505961.79,div:0.0,st:"MATCH"},
  {dev:"SEAS",fat:47,spcf:391239.28,prof:474659.77,div:17.6,st:"MAJOR"},
  {dev:"AMAZONPREV",fat:9,spcf:366572.61,prof:777884.59,div:52.9,st:"CRITICAL"},
  {dev:"SEMIG",fat:37,spcf:337858.93,prof:0,div:100.0,st:"CRITICAL"},
  {dev:"IDAM",fat:17,spcf:315872.02,prof:505375.17,div:37.5,st:"CRITICAL"},
  {dev:"IPAAM",fat:27,spcf:273039.16,prof:465482.72,div:41.3,st:"CRITICAL"},
  {dev:"FHAJ",fat:65,spcf:221017.27,prof:304898.42,div:27.5,st:"CRITICAL"},
  {dev:"FCECON",fat:33,spcf:220905.77,prof:581141.44,div:62.0,st:"CRITICAL"},
  {dev:"ADS",fat:108,spcf:211657.45,prof:211657.47,div:0.0,st:"MATCH"},
  {dev:"SEC",fat:20,spcf:189021.90,prof:152126.16,div:24.2,st:"CRITICAL"},
  {dev:"IKM DE",fat:19,spcf:183622.37,prof:116263.60,div:57.9,st:"CRITICAL"},
  {dev:"CPA",fat:6,spcf:165830.96,prof:165830.96,div:0.0,st:"MATCH"},
  {dev:"ANOREG",fat:18,spcf:153232.43,prof:102267.91,div:49.8,st:"CRITICAL"},
  {dev:"ADAF",fat:40,spcf:149600.91,prof:149600.91,div:0.0,st:"MATCH"},
  {dev:"SEINFRA",fat:20,spcf:140474.81,prof:294139.13,div:52.2,st:"CRITICAL"},
  {dev:"CASA CIVIL",fat:28,spcf:93859.53,prof:0,div:100.0,st:"CRITICAL"},
  {dev:"SEPROR",fat:21,spcf:87687.72,prof:103810.40,div:15.5,st:"MAJOR"},
  {dev:"SECT",fat:21,spcf:80571.09,prof:222910.14,div:63.9,st:"CRITICAL"},
  {dev:"FVS",fat:11,spcf:78304.05,prof:253753.07,div:69.1,st:"CRITICAL"},
  {dev:"BANCO BMG",fat:16,spcf:69731.50,prof:39242.00,div:77.7,st:"CRITICAL"},
  {dev:"FUAM/FUHAM",fat:9,spcf:63306.61,prof:368561.63,div:82.8,st:"CRITICAL"},
  {dev:"BMC",fat:6,spcf:58142.00,prof:58142.00,div:0.0,st:"MATCH"},
  {dev:"AADESAM",fat:25,spcf:49045.38,prof:125682.90,div:61.0,st:"CRITICAL"},
  {dev:"ITRANSITO",fat:13,spcf:48750.39,prof:38360.67,div:27.1,st:"CRITICAL"},
  {dev:"SNPH",fat:29,spcf:46521.21,prof:17526.63,div:165.4,st:"CRITICAL"},
  {dev:"SEFAZ",fat:8,spcf:39087.87,prof:188362.64,div:79.2,st:"CRITICAL"},
  {dev:"ARSEPAM",fat:26,spcf:39082.71,prof:35923.02,div:8.8,st:"MAJOR"},
  {dev:"FUNTEA",fat:17,spcf:36302.38,prof:23998.67,div:51.3,st:"CRITICAL"},
  {dev:"ASSOC.GESTAO",fat:6,spcf:34760.79,prof:34760.79,div:0.0,st:"MATCH"},
  {dev:"BANCO SICOOB",fat:22,spcf:33732.00,prof:30290.00,div:11.4,st:"MAJOR"},
  {dev:"SEMA",fat:14,spcf:32656.40,prof:35326.64,div:7.6,st:"MAJOR"},
  {dev:"DPE",fat:6,spcf:28060.04,prof:28060.05,div:0.0,st:"MATCH"},
  {dev:"FMPES",fat:2,spcf:27264.57,prof:27264.57,div:0.0,st:"MATCH"},
  {dev:"CGE",fat:8,spcf:25693.34,prof:25693.37,div:0.0,st:"MATCH"},
  {dev:"CBMAM",fat:23,spcf:24824.72,prof:27570.74,div:10.0,st:"MAJOR"},
  {dev:"PSA TECH",fat:1,spcf:21007.21,prof:21007.21,div:0.0,st:"MATCH"},
  {dev:"BANCO SAFRA",fat:11,spcf:20994.00,prof:9310.00,div:125.5,st:"CRITICAL"},
  {dev:"SUL AMERICA",fat:21,spcf:19758.00,prof:18196.00,div:8.6,st:"MAJOR"},
  {dev:"PMAM",fat:13,spcf:17759.11,prof:24351.49,div:27.1,st:"CRITICAL"},
  {dev:"JUCEA",fat:6,spcf:16154.45,prof:0,div:100.0,st:"CRITICAL"},
  {dev:"B23 TECH",fat:3,spcf:11892.24,prof:11892.24,div:0.0,st:"MATCH"},
  {dev:"EASYTECH",fat:12,spcf:9558.34,prof:6927.16,div:38.0,st:"CRITICAL"},
  {dev:"COSAMA",fat:5,spcf:9172.72,prof:0,div:100.0,st:"CRITICAL"},
  {dev:"ODONTOMED",fat:18,spcf:9044.00,prof:7541.10,div:19.9,st:"MAJOR"},
  {dev:"FHEMOAM",fat:8,spcf:3726.51,prof:7743.77,div:51.9,st:"CRITICAL"},
  {dev:"IMPR.OFICIAL",fat:1,spcf:3104.96,prof:0,div:100.0,st:"CRITICAL"},
  {dev:"AFEAM",fat:1,spcf:2973.25,prof:0,div:100.0,st:"CRITICAL"},
  {dev:"CASA MILITAR",fat:1,spcf:2784.24,prof:0,div:100.0,st:"CRITICAL"},
  {dev:"CIAMA",fat:1,spcf:2784.24,prof:0,div:100.0,st:"CRITICAL"}
];

// Populate reconciliation table
(function(){
  const tbody=document.getElementById('tblReconBody');
  if(!tbody) return;
  RECON_DATA.forEach((r,i)=>{
    const diff=r.spcf-r.prof;
    const diffClass=diff>=0?'val-pos':'val-neg';
    const arrow=diff>=0?'\\u25B2':'\\u25BC';
    const stMap={MATCH:'status-ok',MINOR:'status-minor',MAJOR:'status-major',CRITICAL:'status-critical'};
    const stLabel={MATCH:'OK',MINOR:'MINOR',MAJOR:'MAJOR',CRITICAL:'CRITICAL'};
    const nota=r.st==='MATCH'?'Valores conferem':Math.abs(diff)>1000000?'Investigar divergencia':'Verificar';
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${i+1}</td><td style="font-weight:600">${r.dev}</td><td>${r.fat}</td><td style="font-family:var(--font-mono);font-size:11px">R$ ${r.spcf.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td><td style="font-family:var(--font-mono);font-size:11px">R$ ${r.prof.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td><td class="${diffClass}" style="font-family:var(--font-mono);font-size:11px">${arrow} R$ ${Math.abs(diff).toLocaleString('pt-BR',{minimumFractionDigits:2})}</td><td style="font-weight:600">${r.div.toFixed(1)}%</td><td><span class="${stMap[r.st]||'status-major'}">${stLabel[r.st]||r.st}</span></td><td style="font-size:11px;color:var(--text-secondary)">${nota}</td>`;
    tbody.appendChild(tr);
  });
})();

// Chart: Reconciliation Status (Doughnut)
(function(){
  const ctx=document.getElementById('chartReconStatus');
  if(!ctx) return;
  const counts={MATCH:0,MINOR:0,MAJOR:0,CRITICAL:0};
  RECON_DATA.forEach(r=>counts[r.st]=(counts[r.st]||0)+1);
  new Chart(ctx,{
    type:'doughnut',
    data:{
      labels:['Match (<1%)','Minor (1-5%)','Major (5-20%)','Critical (>20%)'],
      datasets:[{
        data:[counts.MATCH,counts.MINOR,counts.MAJOR,counts.CRITICAL],
        backgroundColor:['#16A34A','#2563EB','#D97706','#DC2626'],
        borderWidth:0,
        hoverOffset:8
      }]
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'bottom',labels:{font:{size:11,family:'Inter'},padding:12,usePointStyle:true,pointStyleWidth:8}},
        tooltip:{callbacks:{label:function(c){return c.label+': '+c.raw+' devedores ('+((c.raw/RECON_DATA.length)*100).toFixed(0)+'%)'}}}
      },
      cutout:'65%'
    }
  });
})();

// Chart: Top 15 Divergences (Horizontal Bar)
(function(){
  const ctx=document.getElementById('chartReconDiverg');
  if(!ctx) return;
  const sorted=[...RECON_DATA].sort((a,b)=>Math.abs(b.spcf-b.prof)-Math.abs(a.spcf-a.prof)).slice(0,15);
  new Chart(ctx,{
    type:'bar',
    data:{
      labels:sorted.map(r=>r.dev),
      datasets:[{
        label:'SPCF > Profiles',
        data:sorted.map(r=>r.spcf>r.prof?(r.spcf-r.prof)/1e6:0),
        backgroundColor:'rgba(22,163,74,0.7)',
        borderRadius:4
      },{
        label:'Profiles > SPCF',
        data:sorted.map(r=>r.prof>r.spcf?(r.prof-r.spcf)/1e6:0),
        backgroundColor:'rgba(220,38,38,0.7)',
        borderRadius:4
      }]
    },
    options:{
      indexAxis:'y',
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'top',labels:{font:{size:11,family:'Inter'},usePointStyle:true,pointStyleWidth:8}},
        tooltip:{callbacks:{label:function(c){return c.dataset.label+': R$ '+c.raw.toFixed(2)+'M'}}}
      },
      scales:{
        x:{title:{display:true,text:'Divergencia (R$ milhoes)',font:{size:11}},ticks:{font:{size:10}},grid:{color:'rgba(0,0,0,0.05)'}},
        y:{ticks:{font:{size:10,weight:'600'}},grid:{display:false}}
      }
    }
  });
})();

// Chart: Inconsistencies by Debtor
(function(){
  const ctx=document.getElementById('chartInconsist');
  if(!ctx) return;
  const data=[
    {dev:'SEJUSC',val:101},{dev:'SSP',val:99},{dev:'ADS',val:99},{dev:'SUHAB',val:89},
    {dev:'SEJEL',val:87},{dev:'SES',val:78},{dev:'SETRAB',val:75},{dev:'DETRAN',val:53},
    {dev:'POL.CIVIL',val:36},{dev:'SEAD',val:35}
  ];
  new Chart(ctx,{
    type:'bar',
    data:{
      labels:data.map(d=>d.dev),
      datasets:[{
        label:'PAGA_EM_DEVIDAS',
        data:data.map(d=>d.val),
        backgroundColor:data.map(d=>d.val>90?'rgba(220,38,38,0.7)':d.val>60?'rgba(217,119,6,0.7)':'rgba(37,99,235,0.7)'),
        borderRadius:4
      }]
    },
    options:{
      indexAxis:'y',
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{display:false},
        tooltip:{callbacks:{label:function(c){return c.raw+' faturas inconsistentes'}}}
      },
      scales:{
        x:{title:{display:true,text:'Faturas PAGA_EM_DEVIDAS',font:{size:11}},ticks:{font:{size:10}},grid:{color:'rgba(0,0,0,0.05)'}},
        y:{ticks:{font:{size:10,weight:'600'}},grid:{display:false}}
      }
    }
  });
})();

// Chart: Inadimplência Pattern
(function(){
  const ctx=document.getElementById('chartPadraoRecon');
  if(!ctx) return;
  new Chart(ctx,{
    type:'doughnut',
    data:{
      labels:['PONTUAL (>80%)','INTERMITENTE (<80%)','RECENTE (<50%)','CRONICO (0%)'],
      datasets:[{
        data:[31,4,1,1],
        backgroundColor:['#16A34A','#D97706','#DC2626','#7C3AED'],
        borderWidth:0,
        hoverOffset:8
      }]
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'bottom',labels:{font:{size:11,family:'Inter'},padding:12,usePointStyle:true,pointStyleWidth:8}},
        tooltip:{callbacks:{label:function(c){return c.label+': '+c.raw+' devedores'}}}
      },
      cutout:'60%'
    }
  });
})();

// Chart: Faturas Cruzadas (Stacked Bar)
(function(){
  const ctx=document.getElementById('chartFatCruzadas');
  if(!ctx) return;
  const data=[
    {dev:'SEDUC',vig:121,presc:7,crit:0},
    {dev:'DETRAN',vig:158,presc:45,crit:0},
    {dev:'SES',vig:170,presc:46,crit:0},
    {dev:'SSP',vig:66,presc:115,crit:0},
    {dev:'SEAD',vig:85,presc:13,crit:0},
    {dev:'SEJUSC',vig:81,presc:83,crit:0},
    {dev:'CETAM',vig:15,presc:0,crit:0},
    {dev:'POL.CIVIL',vig:42,presc:9,crit:0},
    {dev:'SUHAB',vig:71,presc:37,crit:13},
    {dev:'SEDEL',vig:119,presc:0,crit:0},
    {dev:'SETRAB',vig:27,presc:48,crit:0},
    {dev:'SEAS',vig:47,presc:0,crit:0},
    {dev:'UGPI',vig:16,presc:0,crit:0},
    {dev:'SEC',vig:43,presc:6,crit:0},
    {dev:'SEJEL',vig:22,presc:67,crit:0},
    {dev:'ADS',vig:50,presc:61,crit:18},
    {dev:'ADAF',vig:40,presc:0,crit:0},
    {dev:'AADESAM',vig:8,presc:23,crit:0},
    {dev:'FMT',vig:11,presc:6,crit:0},
    {dev:'SEPROR',vig:16,presc:5,crit:3}
  ];
  new Chart(ctx,{
    type:'bar',
    data:{
      labels:data.map(d=>d.dev),
      datasets:[
        {label:'Vigentes',data:data.map(d=>d.vig),backgroundColor:'rgba(22,163,74,0.7)',borderRadius:2},
        {label:'Prescritas',data:data.map(d=>d.presc),backgroundColor:'rgba(220,38,38,0.5)',borderRadius:2},
        {label:'Criticas <90d',data:data.map(d=>d.crit),backgroundColor:'rgba(217,119,6,0.8)',borderRadius:2}
      ]
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{position:'top',labels:{font:{size:11,family:'Inter'},usePointStyle:true,pointStyleWidth:8}},
        tooltip:{mode:'index',intersect:false}
      },
      scales:{
        x:{stacked:true,ticks:{font:{size:9},maxRotation:45},grid:{display:false}},
        y:{stacked:true,title:{display:true,text:'Faturas',font:{size:11}},ticks:{font:{size:10}},grid:{color:'rgba(0,0,0,0.05)'}}
      }
    }
  });
})();

// Chart: Acao Recomendada
(function(){
  const ctx=document.getElementById('chartAcaoRecom');
  if(!ctx) return;
  const data=[
    {acao:'EXECUTAR_TRD',qtd:442,pct:24.8},
    {acao:'NOTIFICAR_TRD',qtd:427,pct:24.0},
    {acao:'OBRIG.NAT.INVEST.',qtd:250,pct:14.1},
    {acao:'HABILITACAO_LIQ.',qtd:195,pct:11.0},
    {acao:'EXECUTAR',qtd:184,pct:10.3},
    {acao:'OBRIG.NATURAL',qtd:101,pct:5.7},
    {acao:'DESCARTAR',qtd:82,pct:4.6},
    {acao:'MONITORAR',qtd:74,pct:4.2},
    {acao:'NOTIF.IMEDIATO',qtd:24,pct:1.3}
  ];
  new Chart(ctx,{
    type:'bar',
    data:{
      labels:data.map(d=>d.acao),
      datasets:[{
        label:'Faturas',
        data:data.map(d=>d.qtd),
        backgroundColor:['#16A34A','#059669','#2563EB','#7C3AED','#0EA5E9','#6366F1','#94A3B8','#D97706','#DC2626'],
        borderRadius:4
      }]
    },
    options:{
      indexAxis:'y',
      responsive:true,
      maintainAspectRatio:false,
      plugins:{
        legend:{display:false},
        tooltip:{callbacks:{label:function(c){return c.raw+' faturas ('+data[c.dataIndex].pct+'%)'}}}
      },
      scales:{
        x:{title:{display:true,text:'Quantidade de Faturas',font:{size:11}},ticks:{font:{size:10}},grid:{color:'rgba(0,0,0,0.05)'}},
        y:{ticks:{font:{size:10,weight:'600'}},grid:{display:false}}
      }
    }
  });
})();

"""

# Insert before the closing </script> tag
html = html.replace('</script>\n</body>', recon_js + '</script>\n</body>')

# ============================================================
# 5. UPDATE VERSION AND FOOTER
# ============================================================
html = html.replace('Dashboard v5.0', 'Dashboard v5.1')
html = html.replace('Dashboard PRODAM &mdash; Recuperacao de Creditos v5.0', 'Dashboard PRODAM &mdash; Recuperacao de Creditos v5.1')
html = html.replace('<title>Dashboard PRODAM — Recuperacao de Creditos v5.0</title>', '<title>Dashboard PRODAM — Recuperacao de Creditos v5.1</title>')
html = html.replace(
    'Gerado em 01/04/2026 &middot; profiles.json v71 + SPCF Mar/2026 (122 Excels, 359K linhas) + Analise Massiva (4.097 arq, 10.55 GB)',
    'Gerado em 01/04/2026 &middot; profiles.json v71 + SPCF Mar/2026 (247 CSVs, 900K+ linhas) + Reconciliacao Exaustiva (1.779 faturas cruzadas)'
)
html = html.replace(
    'Fontes cruzadas: profiles.json | SPCF Blocos 0-6 | Bloco D Empenhos | Analise Massiva v3.6 | Pesquisas Mar/2026',
    'Fontes cruzadas: profiles.json | SPCF Blocos 0-6 | Bloco D Empenhos | Reconciliacao SPCF v1.0 | Faturas Cruzadas (14 fontes) | Analise Massiva v3.6'
)

# Write the updated dashboard
output_path = '/home/ubuntu/DASHBOARD_PRODAM_v5.1_BRANDAO_OZORES.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Dashboard v5.1 saved to {output_path}")
print(f"File size: {len(html):,} bytes")
