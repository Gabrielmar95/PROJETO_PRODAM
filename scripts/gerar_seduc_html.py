"""gerar_seduc_html.py — DASHBOARD_SEDUC_v1.html · Editorial Noir (port do DETRAN v10)

Renderiza dashboard HTML standalone da SEDUC a partir de SEDUC_MASTER_v1.json.
  - Design Editorial Noir: Fraunces / Instrument Sans / Instrument Serif / JetBrains Mono;
  - acentos institucionais Brandão Ozores: azul #1F3864 + dourado #B8963E;
  - ECharts 5.5.0 via CDN (único request externo permitido);
  - dois universos DECLARADOS separadamente (SPCF recente × SSOT histórico) — nunca somados;
  - placeholder de injeção do memorial (id="memorial-section" + <!-- MEMORIAL_INJECT -->).

Uso:
  py -3.12 scripts\gerar_seduc_html.py --orgao SEDUC --out DOCUMENTOS_GERADOS/SEDUC

Injeção posterior do memorial (rodada por outro processo):
  from gerar_seduc_html import injetar_memorial
  injetar_memorial(html_path, memorial_json_path)
"""
from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prodam_utils import brl, fmt_brl  # noqa: E402

MEMORIAL_PLACEHOLDER = "<!-- MEMORIAL_INJECT -->"
MEMORIAL_AVISO = ("Memorial de cálculo preliminar em produção — "
                  "ver MEMORIAL_PRELIMINAR_SEDUC_2026-06-11.md")
MEMORIAL_JSON_PADRAO = ROOT / "DOCUMENTOS_GERADOS" / "SEDUC" / "MEMORIAL_PRELIMINAR_SEDUC_2026-06-11.json"

HTML = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Dossiê SEDUC/AM · Dashboard v1 · PRODAM</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --ink:#0C0C0E; --ink-2:#161618; --ink-3:#1E1E22; --ink-4:#28282D;
  --paper:#F5F1E8; --paper-dim:#E8E4D7; --paper-mute:#9C9786; --paper-faint:rgba(232,228,215,0.55);
  --rule:rgba(232,228,215,0.14); --rule-hi:rgba(232,228,215,0.28); --rule-max:rgba(232,228,215,0.5);
  --stamp:#D94F2E; --stamp-ink:#A83616; --amber:#C89B3C; --ok:#6B8E5A; --warn:#D9A44E;
  --inst-azul:#1F3864; --inst-azul-hi:#3A5A94; --inst-ouro:#B8963E;
  --display:"Fraunces",Georgia,serif; --body:"Instrument Sans",-apple-system,system-ui,sans-serif;
  --serif:"Instrument Serif",Georgia,serif; --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
html{background:var(--ink);scroll-behavior:smooth}
body{font-family:var(--body);font-size:14px;line-height:1.55;color:var(--paper-dim);background:var(--ink);min-height:100vh;
  font-feature-settings:"ss01","ss02","cv11";-webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:100;opacity:0.035;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/></svg>")}

.container{max-width:1480px;margin:0 auto;padding:56px 64px 120px;position:relative}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
.serif{font-family:var(--serif)}

/* ===== A11Y / MOTION / PRINT (skill ui-ux-pro-max) ===== */
.skip{position:absolute;left:-9999px;z-index:1000;background:var(--inst-ouro);color:var(--ink);padding:10px 16px;font-family:var(--mono);font-size:12px;letter-spacing:.08em}
.skip:focus{left:0;top:0}
:focus-visible{outline:2px solid var(--inst-ouro);outline-offset:3px}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{transition:none!important;animation:none!important}
}
@media print{
  :root{--ink:#fff;--ink-2:#f7f7f4;--ink-3:#efefec;--ink-4:#e7e7e2;
        --paper:#111;--paper-dim:#222;--paper-mute:#555;--paper-faint:rgba(17,17,17,0.6);
        --rule:rgba(17,17,17,0.18);--rule-hi:rgba(17,17,17,0.3);--rule-max:rgba(17,17,17,0.5)}
  body::before,.toc,.tbl-ctrl,.tbl-pager,.chart,.chart-tall,.skip{display:none!important}
  body{background:#fff}
  .section,.hero{break-inside:avoid-page;margin-bottom:40px}
  .chart-wrap .cap::after{content:" (gráfico omitido na impressão — dados na tabela)"}
}

/* ===== MASTHEAD ===== */
.masthead{border-bottom:2px solid var(--paper-dim);padding-bottom:28px;margin-bottom:32px;display:grid;grid-template-columns:auto 1fr auto;align-items:end;gap:40px}
.mast-left{display:flex;flex-direction:column;gap:6px}
.mast-super{font-family:var(--mono);font-size:10px;letter-spacing:0.28em;text-transform:uppercase;color:var(--paper-mute)}
.mast-title{font-family:var(--display);font-weight:500;font-size:64px;line-height:0.92;letter-spacing:-0.035em;color:var(--paper)}
.mast-title em{font-style:italic;color:var(--inst-ouro)}
.mast-center{text-align:center;font-family:var(--serif);font-size:13px;font-style:italic;color:var(--paper-mute);line-height:1.5;justify-self:center;border-left:1px solid var(--rule);border-right:1px solid var(--rule);padding:0 28px}
.mast-right{font-family:var(--mono);font-size:11px;color:var(--paper-mute);text-align:right;line-height:1.9;letter-spacing:0.05em}
.mast-right .k{color:var(--paper-faint);display:inline-block;min-width:72px;text-align:left}
.mast-right .v{color:var(--paper-dim)}

.dossie-bar{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:24px;padding:14px 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);margin-bottom:48px;font-family:var(--mono);font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:var(--paper-mute)}
.dossie-num{color:var(--inst-ouro);font-weight:500}

/* ===== STICKY NAV ===== */
.toc{position:sticky;top:0;z-index:50;background:rgba(12,12,14,0.92);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--rule);margin:0 -64px 64px;padding:14px 64px;display:flex;align-items:center;gap:28px;overflow-x:auto;scrollbar-width:none}
.toc::-webkit-scrollbar{display:none}
.toc a{color:var(--paper-mute);text-decoration:none;font-family:var(--mono);font-size:11px;letter-spacing:0.14em;text-transform:uppercase;white-space:nowrap;padding:6px 0;border-bottom:1px solid transparent;transition:all .25s}
.toc a:hover,.toc a.active{color:var(--paper);border-bottom-color:var(--inst-ouro)}
.toc-lead{font-family:var(--serif);font-style:italic;color:var(--inst-ouro);font-size:13px;margin-right:10px}

/* ===== HERO ===== */
.hero{display:grid;grid-template-columns:13fr 8fr;gap:56px;margin-bottom:96px;align-items:flex-start;position:relative}
.hero-kicker{font-family:var(--mono);font-size:11px;letter-spacing:0.2em;text-transform:uppercase;color:var(--paper-mute);margin-bottom:20px;padding-left:32px;position:relative}
.hero-kicker::before{content:"";position:absolute;left:0;top:6px;width:22px;height:1px;background:var(--inst-ouro)}
.hero-number{font-family:var(--display);font-weight:500;font-size:clamp(72px,9vw,150px);line-height:0.85;letter-spacing:-0.05em;color:var(--paper);font-variant-numeric:tabular-nums lining-nums;margin-bottom:20px;white-space:nowrap}
.hero-currency{font-family:var(--serif);font-style:italic;font-size:0.3em;vertical-align:0.7em;color:var(--paper-mute);margin-right:12px}
.hero-sub{font-family:var(--serif);font-size:19px;font-style:italic;line-height:1.5;color:var(--paper-dim);max-width:560px;padding-top:16px;border-top:1px solid var(--rule)}
.hero-sub strong{font-style:normal;color:var(--ink);font-family:var(--body);font-weight:500;background:var(--paper-dim);padding:2px 7px;text-transform:uppercase;font-size:11px;letter-spacing:0.1em;vertical-align:2px}
.stamp{position:absolute;top:-20px;right:-10px;transform:rotate(-8deg);border:3px double var(--stamp);color:var(--stamp);padding:10px 18px 8px;font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:0.26em;text-transform:uppercase;line-height:1.3;text-align:center;background:rgba(217,79,46,0.04);box-shadow:0 0 0 1px rgba(217,79,46,0.2);opacity:0.88}
.stamp b{display:block;font-family:var(--display);font-size:22px;font-weight:700;letter-spacing:0.04em;margin:2px 0}
.stamp i{display:block;font-style:normal;font-size:9px;letter-spacing:0.22em;color:var(--stamp-ink)}
.hero-right{padding-top:60px}
.score-card{border-left:1px solid var(--inst-ouro);padding-left:28px;margin-bottom:40px}
.score-label{font-family:var(--mono);font-size:10px;letter-spacing:0.24em;text-transform:uppercase;color:var(--paper-mute);margin-bottom:8px}
.score-value{font-family:var(--display);font-weight:400;font-size:96px;line-height:0.9;color:var(--paper);letter-spacing:-0.04em;font-variant-numeric:tabular-nums}
.score-value small{font-size:0.36em;color:var(--paper-mute)}
.score-grade{font-family:var(--serif);font-style:italic;font-size:28px;color:var(--inst-ouro);margin-top:6px}
.mini-grid{display:grid;grid-template-columns:1fr 1fr;gap:0;border-top:1px solid var(--rule);border-left:1px solid var(--rule)}
.mini-cell{padding:16px 18px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.mini-cell .l{font-family:var(--mono);font-size:9px;letter-spacing:0.2em;text-transform:uppercase;color:var(--paper-mute);margin-bottom:8px}
.mini-cell .v{font-family:var(--display);font-size:26px;font-weight:500;color:var(--paper);line-height:1;letter-spacing:-0.02em;font-variant-numeric:tabular-nums}
.mini-cell .n{font-family:var(--serif);font-style:italic;font-size:12px;color:var(--paper-mute);margin-top:6px;line-height:1.4}

/* ===== SECTION ===== */
.section{margin-bottom:100px;position:relative;scroll-margin-top:80px}
.section-head{display:grid;grid-template-columns:120px 1fr auto;align-items:baseline;gap:32px;margin-bottom:36px;padding-bottom:18px;border-bottom:1px solid var(--paper-dim)}
.section-num{font-family:var(--display);font-weight:400;font-style:italic;font-size:72px;line-height:0.8;color:var(--inst-ouro);letter-spacing:-0.04em}
.section-title{font-family:var(--display);font-weight:500;font-size:38px;line-height:1;letter-spacing:-0.03em;color:var(--paper)}
.section-title em{font-family:var(--serif);font-weight:400;font-size:0.7em}
.section-meta{font-family:var(--mono);font-size:10px;letter-spacing:0.2em;text-transform:uppercase;color:var(--paper-mute);text-align:right}
.section-meta .lead{color:var(--inst-ouro);display:block;margin-bottom:3px}

/* ===== UNIVERSOS ===== */
.universos{display:grid;grid-template-columns:1fr 1fr;gap:0;border:1px solid var(--paper-dim)}
.universo{padding:32px 36px;position:relative}
.universo+.universo{border-left:1px solid var(--paper-dim)}
.universo::before{content:"";position:absolute;top:0;left:0;width:100%;height:4px}
.universo.u-spcf::before{background:var(--inst-azul-hi)}
.universo.u-ssot::before{background:var(--inst-ouro)}
.universo .u-tag{font-family:var(--mono);font-size:10px;letter-spacing:0.22em;text-transform:uppercase;margin-bottom:16px}
.universo.u-spcf .u-tag{color:var(--inst-azul-hi)}
.universo.u-ssot .u-tag{color:var(--inst-ouro)}
.universo .u-big{font-family:var(--display);font-size:40px;font-weight:500;color:var(--paper);line-height:1.05;letter-spacing:-0.03em;font-variant-numeric:tabular-nums}
.universo .u-sub{font-family:var(--serif);font-style:italic;font-size:14px;color:var(--paper-mute);margin-top:12px;line-height:1.55}
.universo .u-meta{font-family:var(--mono);font-size:11px;color:var(--paper-dim);margin-top:18px;line-height:2;letter-spacing:0.05em}
.nota-universos{margin-top:22px;padding:18px 24px;border-left:3px solid var(--inst-ouro);background:var(--ink-2);font-family:var(--serif);font-style:italic;font-size:14px;color:var(--paper-dim);line-height:1.6}
.nota-universos b{font-family:var(--body);font-style:normal;color:var(--inst-ouro);text-transform:uppercase;font-size:11px;letter-spacing:0.12em}

/* ===== ALERT ===== */
.aviso{margin-bottom:22px;padding:14px 20px;border:1px dashed var(--stamp);color:var(--stamp);font-family:var(--mono);font-size:11px;letter-spacing:0.1em;text-transform:uppercase;background:rgba(217,79,46,0.05)}

/* ===== CHART ===== */
.two-col-even{display:grid;grid-template-columns:1fr 1fr;gap:48px}
.chart-wrap h3{font-family:var(--display);font-weight:500;font-size:22px;letter-spacing:-0.02em;margin-bottom:6px;color:var(--paper)}
.chart-wrap .cap{font-family:var(--serif);font-style:italic;font-size:13px;color:var(--paper-mute);margin-bottom:20px;padding-bottom:14px;border-bottom:1px solid var(--rule)}
.chart{width:100%;height:360px}
.chart-tall{height:440px}

/* ===== TABLE ===== */
.tbl-ctrl{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:16px;flex-wrap:wrap}
.tbl-search{flex:1;max-width:420px;background:var(--ink-2);border:1px solid var(--rule);padding:11px 16px;font-family:var(--mono);font-size:12px;color:var(--paper);letter-spacing:0.04em}
.tbl-search:focus{border-color:var(--inst-ouro);outline:2px solid var(--inst-ouro);outline-offset:1px}
.tbl-search::placeholder{color:var(--paper-mute);font-style:italic;font-family:var(--serif)}
.tbl-filter{display:flex;gap:8px;flex-wrap:wrap}
.chip-filter{font-family:var(--mono);font-size:10px;letter-spacing:0.12em;text-transform:uppercase;padding:10px 14px;border:1px solid var(--rule-hi);color:var(--paper-mute);cursor:pointer;transition:all .2s;user-select:none;background:transparent}
.chip-filter.active,.chip-filter:hover{color:var(--paper);border-color:var(--inst-ouro);background:var(--ink-3)}
.tbl-wrap{overflow-x:auto;border:1px solid var(--rule)}
.tbl{width:100%;border-collapse:collapse;font-size:13px;min-width:780px}
.tbl thead th{font-family:var(--mono);font-size:10px;letter-spacing:0.18em;text-transform:uppercase;color:var(--paper-mute);text-align:left;padding:14px 16px;border-bottom:2px solid var(--paper-dim);font-weight:400;cursor:pointer;user-select:none;white-space:nowrap;background:var(--ink)}
.tbl thead th:hover{color:var(--paper)}
.tbl thead th.num{text-align:right}
.tbl thead th.sort-asc::after{content:"▲";margin-left:6px;color:var(--inst-ouro)}
.tbl thead th.sort-desc::after{content:"▼";margin-left:6px;color:var(--inst-ouro)}
.tbl td{padding:12px 16px;border-bottom:1px solid var(--rule);font-family:var(--body);color:var(--paper-dim);vertical-align:top}
.tbl tr:hover td{background:var(--ink-2);color:var(--paper)}
.tbl td.mono,.tbl td.num{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:12px}
.tbl td.num{text-align:right}
.tbl td.ref{color:var(--inst-ouro)}
.pill{display:inline-block;font-family:var(--mono);font-size:10px;letter-spacing:0.1em;padding:2px 7px;border:1px solid var(--rule-hi)}
.pill-ok{color:var(--ok);border-color:rgba(107,142,90,0.4)}
.pill-warn{color:var(--amber);border-color:rgba(200,155,60,0.4)}
.pill-danger{color:var(--stamp);border-color:rgba(217,79,46,0.4)}
.pill-azul{color:var(--inst-azul-hi);border-color:rgba(58,90,148,0.55)}
.tbl-pager{display:flex;justify-content:space-between;align-items:center;margin-top:14px;padding:12px 0;font-family:var(--mono);font-size:11px;color:var(--paper-mute);letter-spacing:0.08em}
.pager-btns{display:flex;gap:6px}
.pager-btn{background:transparent;border:1px solid var(--rule-hi);color:var(--paper-mute);padding:5px 11px;font-family:var(--mono);font-size:11px;cursor:pointer;letter-spacing:0.08em}
.pager-btn:hover:not(:disabled){color:var(--paper);border-color:var(--paper-dim)}
.pager-btn:disabled{opacity:0.3;cursor:not-allowed}
.pager-btn.active{color:var(--inst-ouro);border-color:var(--inst-ouro)}

/* ===== RISCOS / PASSOS ===== */
.gaps-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-top:1px solid var(--paper-dim);border-left:1px solid var(--paper-dim)}
.gap{padding:28px;border-right:1px solid var(--paper-dim);border-bottom:1px solid var(--paper-dim);position:relative}
.gap::before{content:"";position:absolute;top:0;left:0;width:4px;height:100%}
.gap.critica::before{background:var(--stamp)}
.gap.alta::before{background:var(--amber)}
.gap.media::before{background:var(--inst-azul-hi)}
.gap .sev{font-family:var(--mono);font-size:10px;letter-spacing:0.22em;text-transform:uppercase;color:var(--paper-mute);margin-bottom:14px}
.gap.critica .sev{color:var(--stamp)}
.gap.alta .sev{color:var(--amber)}
.gap.media .sev{color:var(--inst-azul-hi)}
.gap h4{font-family:var(--display);font-weight:500;font-size:22px;line-height:1.15;color:var(--paper);margin-bottom:10px}
.gap p{font-family:var(--serif);font-style:italic;font-size:14px;color:var(--paper-dim);line-height:1.5}
.plano-list{border-top:1px solid var(--paper-dim)}
.plano-item{display:grid;grid-template-columns:80px 1fr auto;gap:32px;align-items:center;padding:28px 0;border-bottom:1px solid var(--rule);transition:all .4s}
.plano-item:hover{padding-left:20px;border-bottom-color:var(--paper-dim)}
.plano-item .n{font-family:var(--display);font-size:56px;font-weight:400;font-style:italic;color:var(--inst-ouro);letter-spacing:-0.04em;line-height:0.85}
.plano-item .t{font-family:var(--display);font-size:22px;font-weight:500;color:var(--paper);letter-spacing:-0.015em;line-height:1.3}
.plano-item .sub{display:block;font-family:var(--serif);font-style:italic;font-size:13px;color:var(--paper-mute);margin-top:6px;font-weight:400}
.plano-item .imp{font-family:var(--mono);font-size:11px;letter-spacing:0.1em;color:var(--ok);padding:8px 14px;border:1px solid var(--ok);text-transform:uppercase;white-space:nowrap}

/* ===== MEMORIAL ===== */
.memorial-box{border:1px solid var(--paper-dim);padding:36px 40px;background:var(--ink-2)}
.memorial-box .m-aviso{font-family:var(--serif);font-style:italic;font-size:16px;color:var(--paper-mute);line-height:1.6}
.memorial-box .m-aviso::before{content:"※ ";color:var(--inst-ouro);font-style:normal}
.mem-tbl{width:100%;border-collapse:collapse;font-size:13px;margin-top:18px}
.mem-tbl caption{font-family:var(--display);font-size:20px;font-weight:500;color:var(--paper);text-align:left;margin-bottom:12px}
.mem-tbl th{font-family:var(--mono);font-size:10px;letter-spacing:0.16em;text-transform:uppercase;color:var(--paper-mute);text-align:left;padding:10px 14px;border-bottom:2px solid var(--inst-ouro);font-weight:400}
.mem-tbl td{padding:10px 14px;border-bottom:1px solid var(--rule);font-family:var(--mono);font-variant-numeric:tabular-nums;color:var(--paper-dim)}
.mem-tbl td:first-child{font-family:var(--body);color:var(--paper)}

/* ===== COLOPHON ===== */
.colophon{margin-top:120px;padding-top:40px;border-top:2px solid var(--paper-dim)}
.colophon-top{display:grid;grid-template-columns:1fr auto;align-items:baseline;margin-bottom:24px}
.colophon-mark{font-family:var(--display);font-weight:500;font-size:32px;letter-spacing:-0.02em;color:var(--paper)}
.colophon-mark em{color:var(--inst-ouro);font-style:italic}
.colophon-date{font-family:var(--mono);font-size:11px;letter-spacing:0.16em;color:var(--paper-mute);text-transform:uppercase}
.colophon-body{font-family:var(--serif);font-style:italic;font-size:13px;color:var(--paper-mute);line-height:1.75;max-width:920px}
.colophon-body .src{font-family:var(--mono);font-style:normal;font-size:10px;color:var(--paper-faint);letter-spacing:0.04em;margin-top:14px;display:block}

@media (max-width:1100px){
  .container{padding:32px 20px 60px}
  .hero,.two-col-even,.universos{grid-template-columns:1fr}
  .universo+.universo{border-left:none;border-top:1px solid var(--paper-dim)}
  .gaps-grid{grid-template-columns:1fr}
  .masthead{grid-template-columns:1fr}
  .mast-center{display:none}
  .section-head{grid-template-columns:60px 1fr}
  .section-num{font-size:48px}
  .section-title{font-size:28px}
  .section-meta{display:none}
  .hero-number{font-size:52px;white-space:normal}
  .plano-item{grid-template-columns:50px 1fr}
  .plano-item .imp{display:none}
  .toc{margin:0 -20px 32px;padding:12px 20px}
}
</style>
</head>
<body>
<a class="skip" href="#s1">Pular para o conteúdo</a>
<main class="container">

  <header class="masthead">
    <div class="mast-left">
      <div class="mast-super">Dossiê de Recuperação de Crédito · Devedor nº 1 do portfólio</div>
      <div class="mast-title">SEDUC<em>/</em>AM</div>
    </div>
    <div class="mast-center">
      Secretaria de Educação do Amazonas.<br>
      Administração Direta &mdash; categoria GOV_DIRETA.<br>
      Regime: precatório/RPV (Art. 100 CF) · Índice SELIC.
    </div>
    <div class="mast-right">
      <div><span class="k">CNPJ</span> <span class="v" id="m-cnpj">—</span></div>
      <div><span class="k">Edição</span> <span class="v">v1.0 · Editorial Noir</span></div>
      <div><span class="k">Data</span> <span class="v" id="m-data">—</span></div>
      <div><span class="k">Fase</span> <span class="v" id="m-fase">—</span></div>
    </div>
  </header>

  <div class="dossie-bar">
    <span>Dossiê Nº <span class="dossie-num">02</span></span>
    <span style="text-align:center;letter-spacing:0.4em">· · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·</span>
    <span id="bar-resumo">—</span>
  </div>

  <nav class="toc">
    <span class="toc-lead">Índice &mdash;</span>
    <a href="#s1">I. Balanço</a>
    <a href="#s2">II. Universos</a>
    <a href="#s3">III. Contratos</a>
    <a href="#s4">IV. Faturas</a>
    <a href="#s5">V. Empenhos</a>
    <a href="#s6">VI. Riscos</a>
    <a href="#memorial-section">VII. Memorial</a>
    <a href="#s8">VIII. Próximos passos</a>
  </nav>

  <!-- 1. HERO -->
  <section class="hero" id="s1">
    <div class="hero-left">
      <div class="hero-kicker">Ativo nº 02 · Valor exigível SSOT (profiles.json)</div>
      <div class="hero-number"><span class="hero-currency">R$</span><span id="h-exig">—</span></div>
      <div class="hero-sub">
        Atualizado a <strong id="h-atual">—</strong>.
        Administração Direta — precatório/RPV (Art. 100 CF).
        Negativa expressa registrada (Of. 316/2020-GS/SEDUC).
        Probabilidade de recuperação <strong id="h-prec">70%</strong>.
      </div>
      <div class="stamp">Recomendação<b id="h-recom">MONITORIA</b><i>Blindagem <span id="h-blind">20/22</span> · PRODAM 2026</i></div>
    </div>
    <aside class="hero-right">
      <div class="score-card">
        <div class="score-label">Score composto</div>
        <div class="score-value"><span id="h-score">80</span><small>/100</small></div>
        <div class="score-grade" id="h-conc">B+ (Forte)</div>
      </div>
      <div class="mini-grid">
        <div class="mini-cell"><div class="l">EV · valor esperado</div><div class="v" id="h-ev">—</div><div class="n">p = 0,70 sobre exigível</div></div>
        <div class="mini-cell"><div class="l">Honorários 20%</div><div class="v" id="h-hon">—</div><div class="n">sobre o EV</div></div>
        <div class="mini-cell"><div class="l">Monte Carlo P50</div><div class="v" id="h-p50">—</div><div class="n">cenário conservador</div></div>
        <div class="mini-cell"><div class="l">Recomendação</div><div class="v" style="color:var(--inst-ouro)" id="h-recom2">MONITORIA</div><div class="n">sem título executivo — ação monitória</div></div>
      </div>
    </aside>
  </section>

  <!-- 2. UNIVERSOS -->
  <section class="section" id="s2">
    <header class="section-head">
      <div class="section-num serif">II.</div>
      <div class="section-title">Dois universos de faturas <em>— declarados, nunca somados</em></div>
      <div class="section-meta"><span class="lead">Quadro A</span>SPCF × SSOT</div>
    </header>
    <div class="universos">
      <div class="universo u-spcf">
        <div class="u-tag">Universo recente SPCF · dossie.json</div>
        <div class="u-big" id="u-spcf-big">—</div>
        <div class="u-sub" id="u-spcf-desc">—</div>
        <div class="u-meta" id="u-spcf-meta">—</div>
      </div>
      <div class="universo u-ssot">
        <div class="u-tag">Universo SSOT histórico · profiles.json</div>
        <div class="u-big" id="u-ssot-big">—</div>
        <div class="u-sub" id="u-ssot-desc">—</div>
        <div class="u-meta" id="u-ssot-meta">—</div>
      </div>
    </div>
    <div class="nota-universos"><b>Nota metodológica —</b> <span id="u-nota">—</span></div>
  </section>

  <!-- 3. CONTRATOS -->
  <section class="section" id="s3">
    <header class="section-head">
      <div class="section-num serif">III.</div>
      <div class="section-title">Portfólio contratual <em>— 6 instrumentos no universo SPCF</em></div>
      <div class="section-meta"><span class="lead">Tab. I</span>universo SPCF recente</div>
    </header>
    <div class="aviso" id="ct-aviso">—</div>
    <div class="tbl-wrap">
      <table class="tbl" id="tbl-contratos">
        <thead><tr>
          <th data-sort="numero">Contrato</th>
          <th data-sort="num_faturas" class="num">Faturas</th>
          <th data-sort="valor_num" class="num">Valor bruto (SPCF)</th>
          <th data-sort="pct" class="num">% do universo</th>
          <th>PDF do contrato</th>
          <th>Cláusula econômica</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <div class="tbl-pager" id="ct-pager"></div>
  </section>

  <!-- 4. FATURAS -->
  <section class="section" id="s4">
    <header class="section-head">
      <div class="section-num serif">IV.</div>
      <div class="section-title">Faturas do universo SPCF <em id="fat-sub">— detalhamento</em></div>
      <div class="section-meta"><span class="lead">Tab. II + Figs. 1–2</span>competência ≥ 05/2023</div>
    </header>
    <div class="two-col-even" style="margin-bottom:48px">
      <div class="chart-wrap">
        <h3>Fig. 1 — Faturas por competência</h3>
        <div class="cap">Universo SPCF recente. Barras = valor bruto (R$ Mi); linha = quantidade de faturas.</div>
        <div id="chart-competencia" class="chart" role="img" aria-label="Gráfico de barras e linha: valor bruto (R$ milhões) e quantidade de faturas por competência, de 05/2023 a 03/2026 — 2025 concentra 90 das 106 faturas. Valores exatos na Tabela II abaixo."></div>
      </div>
      <div class="chart-wrap">
        <h3>Fig. 2 — Faturas por contrato</h3>
        <div class="cap">CT 14/2018 concentra a maior parte do universo SPCF recente.</div>
        <div id="chart-contrato" class="chart" role="img" aria-label="Gráfico de barras horizontais: valor bruto por contrato — CT 20/2022 (R$ 22,5 milhões), CT 14/2018 (R$ 19,9 milhões, 73 faturas), CT 23/2021 (R$ 11,6 milhões) e demais. Valores exatos na Tabela I."></div>
      </div>
    </div>
    <div class="tbl-ctrl">
      <input type="search" class="tbl-search" id="fat-search" aria-label="Buscar fatura por ID, NF, contrato, competência, situação ou cadeia" placeholder="Buscar fatura, NF, contrato, competência...">
      <div class="tbl-filter" id="fat-filters" role="group" aria-label="Filtrar faturas">
        <button type="button" class="chip-filter active" aria-pressed="true" data-filter="all">Todas</button>
        <button type="button" class="chip-filter" aria-pressed="false" data-filter="Emitida">Emitidas</button>
        <button type="button" class="chip-filter" aria-pressed="false" data-filter="Parcialmente Paga">Parc. pagas</button>
        <button type="button" class="chip-filter" aria-pressed="false" data-filter="COMPLETA">Cadeia completa</button>
        <button type="button" class="chip-filter" aria-pressed="false" data-filter="FORTE">Cadeia forte</button>
      </div>
    </div>
    <div class="tbl-wrap">
      <table class="tbl" id="tbl-faturas">
        <thead><tr>
          <th data-sort="id">ID SPCF</th>
          <th data-sort="nf">NF</th>
          <th data-sort="contrato">Contrato</th>
          <th data-sort="comp_ord">Comp.</th>
          <th data-sort="valor_num" class="num">Valor bruto</th>
          <th data-sort="situacao">Situação</th>
          <th data-sort="cadeia">Cadeia</th>
          <th data-sort="empenhos_vinc" class="num">NEs vinc.</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <div class="tbl-pager" id="fat-pager"></div>
  </section>

  <!-- 5. EMPENHOS -->
  <section class="section" id="s5">
    <header class="section-head">
      <div class="section-num serif">V.</div>
      <div class="section-title">Empenhos por ano <em id="emp-sub">— histórico SPCF</em></div>
      <div class="section-meta"><span class="lead">Fig. 3</span>Art. 202 VI CC</div>
    </header>
    <div class="chart-wrap">
      <h3>Fig. 3 — Notas de Empenho SEDUC por ano de emissão</h3>
      <div class="cap">Barras douradas: <b style="color:var(--inst-ouro)">2025 e 2026</b> — empenhos recentes são potenciais marcos interruptivos
        (NE = reconhecimento tácito, Art. 202 VI CC). Linha = quantidade de NEs.</div>
      <div id="chart-empenhos" class="chart chart-tall" role="img" aria-label="Gráfico de barras: valor empenhado por ano, 2014 a 2026 — 286 notas de empenho ativas somando R$ 482,7 milhões; destaque para 38 NEs em 2025-2026 (R$ 62,1 milhões), potenciais marcos do Art. 202 VI do Código Civil."></div>
    </div>
  </section>

  <!-- 6. RISCOS -->
  <section class="section" id="s6">
    <header class="section-head">
      <div class="section-num serif">VI.</div>
      <div class="section-title">Riscos <em>& blindagem</em></div>
      <div class="section-meta"><span class="lead">Quadro B</span><span id="riscos-meta">—</span></div>
    </header>
    <div class="gaps-grid" id="gaps-grid"></div>
  </section>

  <!-- 7. MEMORIAL (placeholder de injeção) -->
  <section class="section" id="memorial-section">
    <header class="section-head">
      <div class="section-num serif">VII.</div>
      <div class="section-title">Memorial de cálculo <em>— preliminar</em></div>
      <div class="section-meta"><span class="lead">Anexo</span>injeção posterior</div>
    </header>
    <div class="memorial-box">
<!-- MEMORIAL_INJECT -->
      <p class="m-aviso">Memorial de cálculo preliminar em produção — ver MEMORIAL_PRELIMINAR_SEDUC_2026-06-11.md</p>
    </div>
  </section>

  <!-- 8. PRÓXIMOS PASSOS -->
  <section class="section" id="s8">
    <header class="section-head">
      <div class="section-num serif">VIII.</div>
      <div class="section-title">Próximos passos <em>— auditoria do acervo</em></div>
      <div class="section-meta"><span class="lead">Plano</span>DPCON · pendrive · SPCF</div>
    </header>
    <div class="plano-list" id="plano-list"></div>
  </section>

  <footer class="colophon">
    <div class="colophon-top">
      <div class="colophon-mark">SEDUC<em>/</em>AM &mdash; <span class="serif" style="font-style:italic;font-weight:400;color:var(--paper-mute)">Dossiê de Recuperação</span></div>
      <div class="colophon-date">Edição v1.0 · <span id="ft-date"></span> · Editorial Noir</div>
    </div>
    <div class="colophon-body">
      Dashboard consolidado pela equipe PRODAM a partir de duas fontes primárias mantidas separadas por
      metodologia: o universo recente SPCF (dossiê multiformato, faturas com competência a partir de 05/2023)
      e o universo SSOT histórico (profiles.json — base jurídica da cobrança). Agregação monetária integralmente
      em Decimal; valores serializados como string decimal no JSON master. Contrato-matriz 002/2026
      (Brandão Ozores Advogados × PRODAM S.A.). Gerado por scripts/gerar_seduc_master.py + scripts/gerar_seduc_html.py.
      <span class="src" id="ft-fontes">Fontes: —</span>
    </div>
  </footer>
</main>

<script id="dataset" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('dataset').textContent);
const N = v=>parseFloat(v||0);
const BRL = v=>'R$ '+N(v).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
const BRLc = v=>{const n=N(v);if(n>=1e6) return 'R$ '+(n/1e6).toFixed(2).replace('.',',')+'M';if(n>=1e3) return 'R$ '+(n/1e3).toFixed(1).replace('.',',')+'k';return 'R$ '+n.toFixed(0)};
const FMT = v=>(v||0).toLocaleString('pt-BR');
const compOrd = c=>{const p=(c||'').split('/');return p.length===2?p[1]+'-'+p[0]:'0000-00'};

// ===== MASTHEAD / HERO =====
const H = D.hero, U = D.universos;
document.getElementById('m-cnpj').textContent = D.metadata.cnpj;
document.getElementById('m-data').textContent = D.metadata.gerado_em;
document.getElementById('m-fase').textContent = H.fase_atual+' · '+H.proximo_passo.replace(/_/g,' ');
document.getElementById('ft-date').textContent = D.metadata.gerado_em;
document.getElementById('ft-fontes').textContent = 'Fontes: '+D.metadata.fontes.join(' · ');
document.getElementById('bar-resumo').textContent =
  U.spcf_recente.faturas+' faturas SPCF · '+D.contratos.length+' contratos · '+
  D.empenhos_total.qtd+' empenhos · força '+H.forca_probatoria+' · rank #'+H.prioridade_rank;

document.getElementById('h-exig').textContent = N(H.valor_exigivel).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
document.getElementById('h-atual').textContent = H.valor_atualizado_fmt;
document.getElementById('h-prec').textContent = (N(H.p_recuperacao)*100).toFixed(0)+'%';
document.getElementById('h-score').textContent = Math.round(N(H.score_100));
document.getElementById('h-conc').textContent = H.conceito+' (Forte)';
document.getElementById('h-ev').textContent = BRLc(H.ev_valor_esperado);
document.getElementById('h-hon').textContent = BRLc(H.ev_honorarios);
document.getElementById('h-p50').textContent = BRLc(H.monte_carlo_p50);
document.getElementById('h-recom').textContent = H.recomendacao;
document.getElementById('h-recom2').textContent = H.recomendacao;
document.getElementById('h-blind').textContent = H.blindagem_ok+'/'+H.blindagem_total;
document.getElementById('riscos-meta').textContent = D.riscos.length+' riscos · blindagem '+H.blindagem_ok+'/'+H.blindagem_total;

// ===== UNIVERSOS =====
{
  const s = U.spcf_recente, h = U.ssot_historico;
  document.getElementById('u-spcf-big').textContent = s.faturas+' faturas · '+s.valor_bruto_fmt;
  document.getElementById('u-spcf-desc').textContent = s.descricao;
  document.getElementById('u-spcf-meta').innerHTML =
    'Situação: '+Object.entries(s.situacoes).map(([k,v])=>v+' '+k).join(' · ')+'<br>'+
    'Cadeia documental: '+Object.entries(s.cadeia).map(([k,v])=>v+' '+k).join(' · ');
  document.getElementById('u-ssot-big').textContent = h.faturas+' faturas · '+h.valor_exigivel_fmt;
  document.getElementById('u-ssot-desc').textContent = h.descricao;
  document.getElementById('u-ssot-meta').innerHTML =
    h.faturas_exigiveis+' exigíveis · '+h.faturas_prescritas+' prescritas<br>'+
    'Atualizado: '+h.valor_atualizado_fmt;
  document.getElementById('u-nota').textContent = U.nota;
}

// ===== ECHARTS theme (Editorial Noir + acentos institucionais) =====
const NC = {paper:'#E8E4D7',mute:'#9C9786',rule:'rgba(232,228,215,0.14)',stamp:'#D94F2E',amber:'#C89B3C',ok:'#6B8E5A',azul:'#3A5A94',azulFundo:'#1F3864',ouro:'#B8963E'};
const REDUZ_MOTION = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const theme = {
  animation: !REDUZ_MOTION,
  textStyle:{color:NC.paper,fontFamily:'Instrument Sans',fontSize:12},
  tooltip:{backgroundColor:'#0C0C0E',borderColor:'#E8E4D7',borderWidth:1,textStyle:{color:NC.paper,fontFamily:'JetBrains Mono',fontSize:11},padding:[10,14]},
  grid:{left:'4%',right:'4%',bottom:'10%',top:'14%',containLabel:true},
};

// Fig 1 — faturas por competência (universo SPCF apenas)
{
  const rows = D.faturas_por_competencia;
  echarts.init(document.getElementById('chart-competencia')).setOption({...theme,
    tooltip:{...theme.tooltip,trigger:'axis'},
    legend:{data:['Valor (R$ Mi)','Qtd. faturas'],textStyle:{color:NC.paper,fontFamily:'JetBrains Mono',fontSize:10},top:0,right:0,itemWidth:14,itemHeight:2},
    xAxis:{type:'category',data:rows.map(r=>r.competencia),axisLine:{lineStyle:{color:NC.paper}},axisLabel:{color:NC.paper,fontFamily:'JetBrains Mono',fontSize:9,rotate:45}},
    yAxis:[
      {type:'value',axisLine:{show:false},axisLabel:{color:NC.mute,fontFamily:'JetBrains Mono',fontSize:10,formatter:'{value}M'},splitLine:{lineStyle:{color:NC.rule,type:'dotted'}}},
      {type:'value',axisLine:{show:false},axisLabel:{color:NC.mute,fontFamily:'JetBrains Mono',fontSize:10},splitLine:{show:false}}
    ],
    series:[
      {name:'Valor (R$ Mi)',type:'bar',data:rows.map(r=>+(N(r.valor)/1e6).toFixed(2)),barWidth:'55%',itemStyle:{color:NC.azul}},
      {name:'Qtd. faturas',type:'line',yAxisIndex:1,data:rows.map(r=>r.qtd),symbol:'emptyCircle',symbolSize:6,lineStyle:{color:NC.ouro,width:1.6},itemStyle:{color:NC.ouro}},
    ]
  });
}
// Fig 2 — faturas por contrato (universo SPCF apenas)
{
  const rows = [...D.faturas_por_contrato].sort((a,b)=>N(a.valor)-N(b.valor));
  echarts.init(document.getElementById('chart-contrato')).setOption({...theme,
    tooltip:{...theme.tooltip,trigger:'axis',formatter:p=>{const r=rows[p[0].dataIndex];return 'CT '+r.contrato+'<br>'+r.qtd+' faturas · '+BRL(r.valor)}},
    grid:{left:'14%',right:'12%',top:'6%',bottom:'8%'},
    xAxis:{type:'value',axisLabel:{color:NC.mute,fontFamily:'JetBrains Mono',fontSize:10,formatter:'{value}M'},splitLine:{lineStyle:{color:NC.rule,type:'dotted'}},axisLine:{show:false}},
    yAxis:{type:'category',data:rows.map(r=>'CT '+r.contrato),axisLabel:{color:NC.paper,fontFamily:'Fraunces',fontSize:14},axisTick:{show:false}},
    series:[{type:'bar',data:rows.map(r=>+(N(r.valor)/1e6).toFixed(2)),barWidth:18,itemStyle:{color:NC.azul},
      label:{show:true,position:'right',color:NC.paper,fontFamily:'JetBrains Mono',fontSize:11,formatter:p=>rows[p.dataIndex].qtd+' fat.'}}]
  });
}
// Fig 3 — empenhos por ano (destaque 2025/2026 = potenciais marcos Art. 202 VI)
{
  const anos = Object.keys(D.empenhos_por_ano).sort();
  const vals = anos.map(a=>+(N(D.empenhos_por_ano[a].valor)/1e6).toFixed(2));
  const qtds = anos.map(a=>D.empenhos_por_ano[a].qtd);
  echarts.init(document.getElementById('chart-empenhos')).setOption({...theme,
    tooltip:{...theme.tooltip,trigger:'axis'},
    legend:{data:['Valor empenhado (R$ Mi)','Qtd. NEs'],textStyle:{color:NC.paper,fontFamily:'JetBrains Mono',fontSize:10},top:0,right:0,itemWidth:14,itemHeight:2},
    xAxis:{type:'category',data:anos,axisLine:{lineStyle:{color:NC.paper}},axisLabel:{color:NC.paper,fontFamily:'JetBrains Mono',fontSize:11}},
    yAxis:[
      {type:'value',axisLine:{show:false},axisLabel:{color:NC.mute,fontFamily:'JetBrains Mono',fontSize:10,formatter:'{value}M'},splitLine:{lineStyle:{color:NC.rule,type:'dotted'}}},
      {type:'value',axisLine:{show:false},axisLabel:{color:NC.mute,fontFamily:'JetBrains Mono',fontSize:10},splitLine:{show:false}}
    ],
    series:[
      {name:'Valor empenhado (R$ Mi)',type:'bar',barWidth:'55%',
       data:anos.map((a,i)=>({value:vals[i],itemStyle:{color:(a==='2025'||a==='2026')?NC.ouro:NC.azul}})),
       label:{show:true,position:'top',color:NC.mute,fontFamily:'JetBrains Mono',fontSize:9,formatter:p=>(a=>(a==='2025'||a==='2026')?'★ marco?':'')(anos[p.dataIndex])}},
      {name:'Qtd. NEs',type:'line',yAxisIndex:1,data:qtds,symbol:'emptyCircle',symbolSize:6,lineStyle:{color:NC.stamp,width:1.4},itemStyle:{color:NC.stamp}},
    ]
  });
}

// ===== SORTABLE / FILTERABLE TABLES =====
function makeTable({tbodySel,data,render,pagerSel,searchInputId,filterChipSel,perPage=30,searchFields,filterFn}){
  const tbody = document.querySelector(tbodySel);
  const pager = document.querySelector(pagerSel);
  let state = {sort:null,dir:1,page:1,q:'',filter:'all'};
  function apply(){
    let rows = data.slice();
    if(state.q){
      const q=state.q.toLowerCase();
      rows = rows.filter(r=>searchFields.some(f=>(String(r[f]||'')).toLowerCase().includes(q)));
    }
    if(state.filter!=='all' && filterFn) rows = rows.filter(r=>filterFn(r,state.filter));
    if(state.sort){
      rows.sort((a,b)=>{
        const av=a[state.sort],bv=b[state.sort];
        if(typeof av==='number'&&typeof bv==='number') return (av-bv)*state.dir;
        return String(av||'').localeCompare(String(bv||''),'pt-BR')*state.dir;
      });
    }
    const total=rows.length,pages=Math.max(1,Math.ceil(total/perPage));
    if(state.page>pages) state.page=pages;
    const start=(state.page-1)*perPage;
    tbody.innerHTML = rows.slice(start,start+perPage).map(render).join('') ||
      '<tr><td colspan="20" style="text-align:center;padding:30px;color:var(--paper-mute);font-style:italic">Nenhum resultado</td></tr>';
    let btns='';
    if(pages>1){
      btns = `<button class="pager-btn" ${state.page<=1?'disabled':''} data-p="prev">◂ Ant</button>`;
      const range=[];
      for(let i=1;i<=pages;i++){
        if(i===1||i===pages||Math.abs(i-state.page)<=2) range.push(i);
        else if(range[range.length-1]!=='...') range.push('...');
      }
      range.forEach(i=>{btns+=i==='...'?'<span style="padding:5px">…</span>':`<button class="pager-btn${i===state.page?' active':''}" data-p="${i}">${i}</button>`;});
      btns+=`<button class="pager-btn" ${state.page>=pages?'disabled':''} data-p="next">Prox ▸</button>`;
    }
    pager.innerHTML = `<span>${total} registros · página ${state.page}/${pages}</span><div class="pager-btns">${btns}</div>`;
    pager.querySelectorAll('.pager-btn').forEach(b=>b.addEventListener('click',()=>{
      const p=b.dataset.p;
      if(p==='prev') state.page--; else if(p==='next') state.page++; else state.page=+p;
      apply();
    }));
  }
  const table = tbody.closest('table');
  table.querySelectorAll('thead th[data-sort]').forEach(th=>{
    th.setAttribute('tabindex','0');
    th.setAttribute('role','columnheader');
    th.setAttribute('aria-sort','none');
    const ordenar = ()=>{
      const k=th.dataset.sort;
      if(state.sort===k) state.dir=-state.dir; else {state.sort=k;state.dir=1;}
      table.querySelectorAll('thead th').forEach(x=>{x.classList.remove('sort-asc','sort-desc');x.setAttribute('aria-sort','none');});
      th.classList.add(state.dir>0?'sort-asc':'sort-desc');
      th.setAttribute('aria-sort',state.dir>0?'ascending':'descending');
      apply();
    };
    th.addEventListener('click',ordenar);
    th.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();ordenar();}});
  });
  if(searchInputId) document.getElementById(searchInputId).addEventListener('input',e=>{state.q=e.target.value;state.page=1;apply();});
  if(filterChipSel){
    document.querySelectorAll(filterChipSel+' .chip-filter').forEach(c=>{
      c.addEventListener('click',()=>{
        document.querySelectorAll(filterChipSel+' .chip-filter').forEach(x=>{x.classList.remove('active');x.setAttribute('aria-pressed','false');});
        c.classList.add('active');
        c.setAttribute('aria-pressed','true');
        state.filter=c.dataset.filter; state.page=1; apply();
      });
    });
  }
  apply();
}

// Tab. I — Contratos
{
  document.getElementById('ct-aviso').textContent = '⚠ '+D.contratos_aviso+' — confirmar índice (SELIC/IGPM/IPCA) na cláusula econômica antes de atualizar valores.';
  const totalU = N(U.spcf_recente.valor_bruto);
  makeTable({
    tbodySel:'#tbl-contratos tbody', pagerSel:'#ct-pager', perPage:10,
    data: D.contratos.map(c=>({...c, valor_num:N(c.valor_bruto), pct:totalU?100*N(c.valor_bruto)/totalU:0})),
    searchFields:['numero'],
    render:c=>`<tr>
      <td class="mono ref">CT ${c.numero}</td>
      <td class="num">${c.num_faturas}</td>
      <td class="num">${BRL(c.valor_bruto)}</td>
      <td class="num">${c.pct.toFixed(1).replace('.',',')}%</td>
      <td><span class="pill pill-danger">${c.pdf_contrato?'OK':'AUSENTE'}</span></td>
      <td><span class="pill pill-warn">${c.clausula_economica}</span></td>
    </tr>`
  });
}

// Tab. II — Faturas (106 · universo SPCF)
{
  document.getElementById('fat-sub').textContent = '— '+D.faturas.length+' registros';
  makeTable({
    tbodySel:'#tbl-faturas tbody', pagerSel:'#fat-pager', perPage:25,
    searchInputId:'fat-search', filterChipSel:'#fat-filters',
    data: D.faturas.map(f=>({...f, valor_num:N(f.valor_bruto), comp_ord:compOrd(f.competencia)})),
    searchFields:['id','nf','contrato','competencia','situacao','cadeia'],
    filterFn:(r,f)=>{
      if(['Emitida','Parcialmente Paga'].includes(f)) return r.situacao===f;
      if(['COMPLETA','FORTE'].includes(f)) return r.cadeia===f;
      return true;
    },
    render:f=>`<tr>
      <td class="mono ref">${f.id}</td>
      <td class="mono">${f.nf||'—'}</td>
      <td class="mono">${f.contrato}</td>
      <td class="mono">${f.competencia}</td>
      <td class="num">${BRL(f.valor_bruto)}</td>
      <td><span class="pill ${f.situacao==='Emitida'?'pill-azul':'pill-warn'}">${f.situacao}</span></td>
      <td><span class="pill ${f.cadeia==='COMPLETA'?'pill-ok':'pill-warn'}">${f.cadeia||'—'}</span></td>
      <td class="num">${f.empenhos_vinc!=null?f.empenhos_vinc:'—'}</td>
    </tr>`
  });
}

// Empenhos subtítulo
document.getElementById('emp-sub').textContent =
  '— '+D.empenhos_total.qtd+' NEs · '+D.empenhos_total.valor_fmt+' (2014–2026)';

// Quadro B — Riscos
document.getElementById('gaps-grid').innerHTML = D.riscos.map(g=>`
  <div class="gap ${g.severidade}">
    <div class="sev">${g.severidade==='critica'?'Crítico':g.severidade==='alta'?'Alta':'Média'}</div>
    <h4>${g.titulo}</h4>
    <p>${g.descricao}</p>
  </div>`).join('');

// Plano — Próximos passos
{
  const roman=['I','II','III','IV','V','VI','VII','VIII'];
  document.getElementById('plano-list').innerHTML = D.proximos_passos.map((p,i)=>`
    <div class="plano-item">
      <div class="n">${roman[i]||(i+1)}.</div>
      <div class="t">${p.acao}<span class="sub">${p.detalhe}</span></div>
      <div class="imp">${p.impacto}</div>
    </div>`).join('');
}

// TOC active highlight
const tocLinks = document.querySelectorAll('.toc a');
const sections = [...document.querySelectorAll('.section'), document.querySelector('.hero')];
const io = new IntersectionObserver(entries=>{
  entries.forEach(e=>{
    if(e.isIntersecting) tocLinks.forEach(l=>l.classList.toggle('active', l.getAttribute('href')==='#'+e.target.id));
  });
},{rootMargin:'-30% 0px -60% 0px'});
sections.forEach(s=>{ if(s) io.observe(s); });

// Resize
window.addEventListener('resize',()=>{
  document.querySelectorAll('.chart,.chart-tall').forEach(el=>{const i=echarts.getInstanceByDom(el);if(i)i.resize()});
});
</script>
</body>
</html>
'''


# ============================================================
# INJEÇÃO POSTERIOR DO MEMORIAL (rodada por outro processo)
# ============================================================

def _fmt_celula(v) -> str:
    """Formata célula do memorial: número/str-decimal → R$ pt-BR; resto → texto escapado."""
    if isinstance(v, bool) or v is None:
        return escape(str(v))
    if isinstance(v, (int, float)) or (
        isinstance(v, str) and v.replace(".", "", 1).replace("-", "", 1).isdigit()
    ):
        try:
            return fmt_brl(brl(v))
        except Exception:
            return escape(str(v))
    return escape(str(v))


def _render_memorial_html(data: dict) -> str:
    """Renderiza o bloco HTML do memorial (tabelas de totais e cenários)."""
    partes = ['<div class="memorial-injetado">']
    fonte = data.get("fonte") or data.get("arquivo") or ""
    gerado = data.get("gerado_em") or data.get("data") or ""
    rotulo = " · ".join(x for x in (str(gerado), str(fonte)) if x)
    if rotulo:
        partes.append(
            f'<p style="font-family:var(--mono);font-size:10px;letter-spacing:0.16em;'
            f'text-transform:uppercase;color:var(--paper-mute);margin-bottom:8px">'
            f'Memorial injetado — {escape(rotulo)}</p>'
        )

    totais = data.get("totais")
    if isinstance(totais, dict) and totais:
        linhas = "".join(
            f"<tr><td>{escape(str(k))}</td><td>{_fmt_celula(v)}</td></tr>"
            for k, v in totais.items()
        )
        partes.append(
            '<table class="mem-tbl"><caption>Totais do memorial</caption>'
            "<thead><tr><th>Rubrica</th><th>Valor</th></tr></thead>"
            f"<tbody>{linhas}</tbody></table>"
        )

    cenarios = data.get("cenarios")
    if isinstance(cenarios, dict):
        cenarios = [{"cenario": k, **(v if isinstance(v, dict) else {"valor": v})}
                    for k, v in cenarios.items()]
    if isinstance(cenarios, list) and cenarios:
        colunas: list[str] = []
        for c in cenarios:
            for k in c:
                if k not in colunas:
                    colunas.append(k)
        head = "".join(f"<th>{escape(str(c))}</th>" for c in colunas)
        corpo = "".join(
            "<tr>" + "".join(f"<td>{_fmt_celula(c.get(col, '—'))}</td>" for col in colunas) + "</tr>"
            for c in cenarios
        )
        partes.append(
            '<table class="mem-tbl"><caption>Cenários</caption>'
            f"<thead><tr>{head}</tr></thead><tbody>{corpo}</tbody></table>"
        )

    if len(partes) == 1:  # JSON sem totais/cenarios reconhecíveis → dump plano
        linhas = "".join(
            f"<tr><td>{escape(str(k))}</td><td>{_fmt_celula(v)}</td></tr>"
            for k, v in data.items() if not isinstance(v, (dict, list))
        )
        partes.append(
            '<table class="mem-tbl"><caption>Memorial (resumo)</caption>'
            "<thead><tr><th>Campo</th><th>Valor</th></tr></thead>"
            f"<tbody>{linhas}</tbody></table>"
        )
    partes.append("</div>")
    return "\n".join(partes)


def injetar_memorial(html_path, memorial_json_path) -> bool:
    """Injeta o memorial de cálculo no dashboard, SE o JSON do memorial existir.

    Args:
        html_path: caminho do DASHBOARD_SEDUC_v1.html já gerado.
        memorial_json_path: caminho do MEMORIAL_PRELIMINAR_SEDUC_2026-06-11.json.

    Returna True se injetou; False se o JSON do memorial ainda não existe.
    Levanta ValueError se o placeholder não estiver presente no HTML
    (ex.: memorial já injetado anteriormente).
    """
    html_path = Path(html_path)
    memorial_json_path = Path(memorial_json_path)
    if not memorial_json_path.exists():
        return False
    with open(memorial_json_path, encoding="utf-8") as fh:
        data = json.load(fh)
    html = html_path.read_text(encoding="utf-8")
    if MEMORIAL_PLACEHOLDER not in html:
        raise ValueError(f"Placeholder {MEMORIAL_PLACEHOLDER!r} não encontrado em {html_path}")
    bloco = _render_memorial_html(data if isinstance(data, dict) else {"totais": {"conteudo": str(data)}})
    html = html.replace(MEMORIAL_PLACEHOLDER, bloco, 1)
    # remove o aviso "em produção" (mantém layout limpo pós-injeção)
    html = html.replace(f'<p class="m-aviso">{MEMORIAL_AVISO}</p>', "", 1)
    html_path.write_text(html, encoding="utf-8")
    return True


# ============================================================
# GERAÇÃO
# ============================================================

def gerar(orgao: str, out_dir: Path) -> Path:
    master_path = out_dir / f"{orgao}_MASTER_v1.json"
    if not master_path.exists():
        raise SystemExit(f"ERRO: {master_path} não existe — rode antes "
                         f"scripts/gerar_seduc_master.py --orgao {orgao} --out {out_dir}")
    with open(master_path, encoding="utf-8") as fh:
        data = json.load(fh)
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")) \
        .replace("</", "<\\/")  # evita fechar o <script> do dataset
    html = HTML.replace("__DATA__", data_json)
    out_path = out_dir / f"DASHBOARD_{orgao}_v1.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"OK {out_path}  ({out_path.stat().st_size:,} bytes)")
    return out_path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Renderiza DASHBOARD_SEDUC_v1.html (Editorial Noir)")
    ap.add_argument("--orgao", default="SEDUC", help="Sigla do órgão (suportado: SEDUC)")
    ap.add_argument("--out", default=str(ROOT / "DOCUMENTOS_GERADOS" / "SEDUC"),
                    help="Diretório com o MASTER e destino do HTML")
    ap.add_argument("--memorial-json", default=None,
                    help="(opcional) injeta memorial após gerar, se o JSON existir")
    args = ap.parse_args(argv)

    if args.orgao.upper() != "SEDUC":
        raise SystemExit("ERRO: este renderizador v1 suporta apenas --orgao SEDUC")

    out_dir = Path(args.out)
    out_path = gerar(args.orgao.upper(), out_dir)

    if args.memorial_json:
        if injetar_memorial(out_path, args.memorial_json):
            print(f"OK memorial injetado de {args.memorial_json}")
        else:
            print(f"-- memorial ainda não existe ({args.memorial_json}) — placeholder mantido")
    return out_path


if __name__ == "__main__":
    main()
