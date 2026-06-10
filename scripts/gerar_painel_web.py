# -*- coding: utf-8 -*-
"""
Gera o PAINEL PRODAM — um único arquivo HTML, 100% offline (sem CDN, sem
nenhuma chamada de rede), a partir de PRODAM_DOCS/profiles.json.

Como rodar (PowerShell, na raiz do projeto):
    py -3.12 scripts\\gerar_painel_web.py

Saida: PAINEL_PRODAM.html na raiz do projeto. Basta dar 2 cliques para abrir
no navegador. Nenhum dado de cliente sai do computador.

A agregacao (valor exigivel, forca, proximo passo, prescricao) replica
exatamente a logica de scripts/auto_update_claude_md.py, para os numeros do
painel baterem com o CLAUDE.md.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "PRODAM_DOCS" / "profiles.json"
OUTPUT = ROOT / "PAINEL_PRODAM.html"


def to_float(x) -> float:
    try:
        return float(str(x).strip() or 0)
    except (ValueError, TypeError):
        return 0.0


def to_int(x) -> int:
    try:
        return int(x or 0)
    except (ValueError, TypeError):
        return 0


def short_passo(pp: str) -> str:
    pp = pp or "N/A"
    pp = pp.split(" — ")[0] if " — " in pp else pp
    pp = pp.split(" -")[0] if " -" in pp else pp
    return pp.strip()


def build_records(data: dict) -> list[dict]:
    """Um registro enxuto por devedor, com os campos usados no painel."""
    recs = []
    for nome, d in data.items():
        if nome.startswith("_") or not isinstance(d, dict):
            continue
        recs.append({
            "nome": nome,
            "cnpj": d.get("cnpj") or "",
            "categoria": d.get("categoria") or "N/A",
            "forca": d.get("forca_probatoria") or "N/A",
            "val_orig": to_float(d.get("val_orig")),
            "val_exig": to_float(d.get("val_exig")),
            "val_atualizado": to_float(d.get("val_atualizado")),
            "faturas_total": to_int(d.get("faturas_total")),
            "faturas_exig": to_int(d.get("faturas_exigiveis")),
            "faturas_presc": to_int(d.get("faturas_prescritas")),
            "proximo_passo": short_passo(d.get("proximo_passo")),
            "proximo_passo_full": d.get("proximo_passo") or "N/A",
            "fase": d.get("fase_atual") or "N/A",
            "data_prescricao": d.get("data_prescricao_proxima") or "",
            "contratos_vigentes": to_int(d.get("contratos_vigentes")),
            "classificacao_reconhecimento": d.get("classificacao_reconhecimento") or "",
            "evidencias_reconhecimento": to_int(d.get("evidencias_reconhecimento")),
        })
    recs.sort(key=lambda r: r["val_exig"], reverse=True)
    return recs


def main() -> None:
    if not PROFILES.exists():
        raise SystemExit(f"profiles.json nao encontrado em {PROFILES}")
    data = json.loads(PROFILES.read_text(encoding="utf-8"))
    recs = build_records(data)
    gen_date = datetime.now().strftime("%d/%m/%Y %H:%M")

    payload = json.dumps(recs, ensure_ascii=False)
    html = (TEMPLATE
            .replace("__DATA_JSON__", payload)
            .replace("__GEN_DATE__", gen_date)
            .replace("__N_DEVEDORES__", str(len(recs))))
    OUTPUT.write_text(html, encoding="utf-8")

    total_exig = sum(r["val_exig"] for r in recs)
    print(f"OK -> {OUTPUT}")
    print(f"   {len(recs)} devedores | exigivel somado: R$ {total_exig:,.2f}"
          .replace(",", "X").replace(".", ",").replace("X", "."))
    print("   Abra com 2 cliques. Arquivo offline, nenhum dado sai do PC.")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Painel PRODAM — Recuperação de Créditos</title>
<style>
  :root{
    --azul:#1F3864; --azul2:#3a5fa0; --dourado:#B8963E; --carvao:#2D2D2D;
    --bg:#eef1f5; --card:#ffffff; --linha:#e3e7ee; --texto:#2D2D2D; --suave:#6b7280;
    --verde:#2e7d32; --ambar:#ed9b00; --cinza:#9aa0a6;
    --r:#c62828; --o:#ef6c00; --y:#f9a825;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:"Segoe UI",system-ui,-apple-system,Arial,sans-serif;
       background:var(--bg);color:var(--texto);font-size:14px;line-height:1.45}
  .wrap{max-width:1280px;margin:0 auto;padding:20px}
  header.top{background:linear-gradient(135deg,var(--azul),#16294a);color:#fff;
       border-radius:14px;padding:22px 26px;box-shadow:0 6px 18px rgba(31,56,100,.18)}
  header.top h1{margin:0;font-size:22px;letter-spacing:.3px}
  header.top .sub{opacity:.85;margin-top:4px;font-size:13px}
  .badges{margin-top:12px;display:flex;gap:10px;flex-wrap:wrap}
  .badge{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);
       padding:5px 11px;border-radius:999px;font-size:12px}
  .lock{background:rgba(184,150,62,.22);border-color:rgba(184,150,62,.5)}

  .grid-kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
       gap:14px;margin-top:18px}
  .kpi{background:var(--card);border:1px solid var(--linha);border-radius:12px;
       padding:16px 18px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
  .kpi .lab{color:var(--suave);font-size:12px;text-transform:uppercase;letter-spacing:.5px}
  .kpi .val{font-size:25px;font-weight:700;color:var(--azul);margin-top:6px}
  .kpi .det{font-size:12px;color:var(--suave);margin-top:6px}
  .kpi.gold{border-top:3px solid var(--dourado)}

  section.box{background:var(--card);border:1px solid var(--linha);border-radius:12px;
       padding:18px 20px;margin-top:18px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
  section.box h2{margin:0 0 14px;font-size:15px;color:var(--azul);
       text-transform:uppercase;letter-spacing:.6px;border-left:4px solid var(--dourado);
       padding-left:10px}

  /* Alertas prescricao */
  .alert-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
  .alert{border-radius:10px;padding:12px 14px;border:1px solid var(--linha);
       display:flex;flex-direction:column;gap:3px;cursor:pointer;transition:.12s}
  .alert:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.1)}
  .alert .nome{font-weight:700}
  .alert .meta{font-size:12px;color:var(--suave)}
  .alert .dias{font-weight:700;font-size:13px}
  .a-r{background:#fdecea;border-color:#f5c6c0}.a-r .dias{color:var(--r)}
  .a-o{background:#fff2e6;border-color:#ffd5ad}.a-o .dias{color:var(--o)}
  .a-y{background:#fff8e1;border-color:#fde9a8}.a-y .dias{color:#b8860b}
  .empty{color:var(--suave);font-style:italic}

  /* Charts */
  .charts{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media(max-width:820px){.charts{grid-template-columns:1fr}}
  .chart-card h3{margin:0 0 12px;font-size:13px;color:var(--carvao)}
  .donut-wrap{display:flex;align-items:center;gap:18px}
  .legend{display:flex;flex-direction:column;gap:7px;font-size:13px}
  .legend i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:7px;vertical-align:middle}
  .legend b{color:var(--azul)}
  .bar-row{display:grid;grid-template-columns:120px 1fr auto;align-items:center;gap:10px;margin-bottom:7px}
  .bar-label{font-size:12px;color:var(--carvao);text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .bar-track{background:#eef1f5;border-radius:6px;height:18px;overflow:hidden}
  .bar-fill{height:100%;border-radius:6px;min-width:2px;transition:width .4s}
  .bar-val{font-size:12px;color:var(--suave);font-variant-numeric:tabular-nums;white-space:nowrap}

  /* Filtros + tabela */
  .filters{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:6px}
  .filters input,.filters select{padding:8px 10px;border:1px solid var(--linha);
       border-radius:8px;font-size:13px;background:#fff;color:var(--texto)}
  .filters input{flex:1;min-width:200px}
  .filters .count{margin-left:auto;color:var(--suave);font-size:12px}
  .btn{background:var(--azul);color:#fff;border:none;border-radius:8px;padding:8px 14px;
       cursor:pointer;font-size:13px}
  .btn.ghost{background:#fff;color:var(--azul);border:1px solid var(--azul)}
  .tbl-wrap{overflow-x:auto;margin-top:8px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{padding:9px 11px;text-align:left;border-bottom:1px solid var(--linha);white-space:nowrap}
  th{background:#f6f8fb;color:var(--azul);cursor:pointer;user-select:none;position:sticky;top:0}
  th:hover{background:#eaf0f8}
  th .arr{color:var(--dourado);font-size:11px}
  tbody tr{cursor:pointer}
  tbody tr:hover{background:#f3f7ff}
  td.num{text-align:right;font-variant-numeric:tabular-nums}
  .pill{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11px;font-weight:600;color:#fff}
  .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle}

  /* Modal ficha */
  .overlay{position:fixed;inset:0;background:rgba(20,30,50,.55);display:none;
       align-items:flex-start;justify-content:center;padding:40px 16px;z-index:50;overflow:auto}
  .overlay.on{display:flex}
  .modal{background:#fff;border-radius:14px;max-width:680px;width:100%;
       box-shadow:0 20px 60px rgba(0,0,0,.3);overflow:hidden}
  .modal .mh{background:linear-gradient(135deg,var(--azul),#16294a);color:#fff;padding:18px 22px;position:relative}
  .modal .mh h3{margin:0;font-size:18px}
  .modal .mh .mc{opacity:.85;font-size:12px;margin-top:3px}
  .modal .close{position:absolute;top:14px;right:16px;background:rgba(255,255,255,.18);
       border:none;color:#fff;width:30px;height:30px;border-radius:50%;cursor:pointer;font-size:16px}
  .modal .mb{padding:20px 22px}
  .fgrid{display:grid;grid-template-columns:1fr 1fr;gap:12px 22px}
  .fitem .fl{font-size:11px;color:var(--suave);text-transform:uppercase;letter-spacing:.4px}
  .fitem .fv{font-size:15px;font-weight:600;color:var(--carvao);margin-top:2px}
  .fitem.full{grid-column:1/-1}
  footer{color:var(--suave);font-size:12px;text-align:center;margin:22px 0 6px}
  code{background:#eef1f5;padding:1px 6px;border-radius:5px;font-size:12px}
</style>
</head>
<body>
<div class="wrap">

  <header class="top">
    <h1>Painel PRODAM — Recuperação de Créditos</h1>
    <div class="sub">Contrato 002/2026 · PRODAM S.A. × Brandão Ozores Advogados</div>
    <div class="badges">
      <span class="badge">Atualizado em __GEN_DATE__</span>
      <span class="badge lock">🔒 Dados locais — nada sai do seu computador</span>
    </div>
  </header>

  <div class="grid-kpi" id="kpis"></div>

  <section class="box">
    <h2>Alertas de prescrição</h2>
    <div id="alertas"></div>
  </section>

  <section class="box">
    <h2>Visão por gráficos</h2>
    <div class="charts">
      <div class="chart-card">
        <h3>Devedores por categoria</h3>
        <div class="donut-wrap"><div id="donutCat"></div><div class="legend" id="legCat"></div></div>
      </div>
      <div class="chart-card">
        <h3>Devedores por força probatória</h3>
        <div class="donut-wrap"><div id="donutForca"></div><div class="legend" id="legForca"></div></div>
      </div>
      <div class="chart-card">
        <h3>Pipeline — próximo passo</h3>
        <div id="barPasso"></div>
      </div>
      <div class="chart-card">
        <h3>Top 10 devedores por valor exigível</h3>
        <div id="barTop"></div>
      </div>
    </div>
  </section>

  <section class="box">
    <h2>Devedores</h2>
    <div class="filters">
      <input id="q" type="text" placeholder="🔎 Buscar devedor por nome...">
      <select id="fCat"><option value="">Todas as categorias</option></select>
      <select id="fForca"><option value="">Todas as forças</option></select>
      <select id="fPasso"><option value="">Todos os próximos passos</option></select>
      <button class="btn ghost" id="limpar">Limpar</button>
      <span class="count" id="count"></span>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead><tr id="thead"></tr></thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
  </section>

  <footer>
    Painel gerado offline a partir de <code>PRODAM_DOCS/profiles.json</code>.
    Para atualizar os números, rode <code>py -3.12 scripts\gerar_painel_web.py</code> e abra de novo.
  </footer>
</div>

<div class="overlay" id="overlay"><div class="modal" id="modal"></div></div>

<script>
const DATA = __DATA_JSON__;

const CATLAB = {GOV_DIRETA:"Gov. Direta", GOV_INDIRETA:"Gov. Indireta", EMPRESA_PRIVADA:"Privada"};
const CATCOLOR = {GOV_DIRETA:"#1F3864", GOV_INDIRETA:"#3a5fa0", EMPRESA_PRIVADA:"#B8963E", "N/A":"#9aa0a6"};
const FORCACOLOR = {FORTE:"#2e7d32", "MÉDIA":"#ed9b00", FRACA:"#9aa0a6", "N/A":"#c5cad1"};

function fmtBRL(n){
  return "R$ " + (Number(n)||0).toLocaleString("pt-BR",{minimumFractionDigits:2,maximumFractionDigits:2});
}
function fmtCompact(n){
  n = Number(n)||0;
  if(n>=1e6) return "R$ "+(n/1e6).toLocaleString("pt-BR",{maximumFractionDigits:1})+" mi";
  if(n>=1e3) return "R$ "+(n/1e3).toLocaleString("pt-BR",{maximumFractionDigits:0})+" mil";
  return fmtBRL(n);
}
function fmtCNPJ(c){
  c = (c||"").replace(/\D/g,"");
  if(c.length!==14) return c||"—";
  return c.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,"$1.$2.$3/$4-$5");
}
function diasPrescricao(dstr){
  if(!dstr) return null;
  const d = new Date(dstr+"T00:00:00");
  if(isNaN(d)) return null;
  const hoje = new Date(); hoje.setHours(0,0,0,0);
  return Math.round((d - hoje)/86400000);
}
function nivelPrescricao(dias){
  if(dias===null) return null;
  if(dias<=0) return "venc";
  if(dias<=30) return "r";
  if(dias<=60) return "o";
  if(dias<=90) return "y";
  return null;
}

/* ---------- KPIs ---------- */
function renderKPIs(){
  const t = {exig:0, atual:0, ft:0, fe:0, fp:0, cat:{}, forca:{}};
  DATA.forEach(d=>{
    t.exig+=d.val_exig; t.atual+=d.val_atualizado;
    t.ft+=d.faturas_total; t.fe+=d.faturas_exig; t.fp+=d.faturas_presc;
    t.cat[d.categoria]=(t.cat[d.categoria]||0)+1;
    t.forca[d.forca]=(t.forca[d.forca]||0)+1;
  });
  const cat = c => t.cat[c]||0;
  const fo = f => t.forca[f]||0;
  document.getElementById("kpis").innerHTML = `
    <div class="kpi"><div class="lab">Devedores</div><div class="val">${DATA.length}</div>
      <div class="det">${cat("GOV_DIRETA")} Gov. Direta · ${cat("GOV_INDIRETA")} Gov. Indireta · ${cat("EMPRESA_PRIVADA")} Privadas</div></div>
    <div class="kpi gold"><div class="lab">Valor exigível</div><div class="val">${fmtCompact(t.exig)}</div>
      <div class="det">${fmtBRL(t.exig)}</div></div>
    <div class="kpi"><div class="lab">Valor atualizado</div><div class="val">${fmtCompact(t.atual)}</div>
      <div class="det">${fmtBRL(t.atual)}</div></div>
    <div class="kpi"><div class="lab">Faturas</div><div class="val">${t.ft.toLocaleString("pt-BR")}</div>
      <div class="det">${t.fe.toLocaleString("pt-BR")} exigíveis · ${t.fp.toLocaleString("pt-BR")} prescritas</div></div>
    <div class="kpi"><div class="lab">Força probatória</div>
      <div class="val" style="font-size:18px">
        <span class="dot" style="background:var(--verde)"></span>${fo("FORTE")} ·
        <span class="dot" style="background:var(--ambar)"></span>${fo("MÉDIA")} ·
        <span class="dot" style="background:var(--cinza)"></span>${fo("FRACA")}</div>
      <div class="det">Forte · Média · Fraca</div></div>`;
}

/* ---------- Alertas prescrição ---------- */
function renderAlertas(){
  const box = document.getElementById("alertas");
  const list = DATA.map(d=>({d, dias:diasPrescricao(d.data_prescricao)}))
                   .filter(x=>x.dias!==null && x.dias>0 && x.dias<=90)
                   .sort((a,b)=>a.dias-b.dias);
  if(!list.length){ box.innerHTML = '<div class="empty">Nenhum devedor com prescrição em até 90 dias na varredura atual.</div>'; return; }
  box.innerHTML = '<div class="alert-grid">' + list.map(({d,dias})=>{
    const cls = dias<=30?"a-r":dias<=60?"a-o":"a-y";
    const emoji = dias<=30?"🔴":dias<=60?"🟠":"🟡";
    return `<div class="alert ${cls}" onclick='abrirFicha(${JSON.stringify(d.nome)})'>
      <div class="nome">${emoji} ${d.nome}</div>
      <div class="dias">${dias} dias — prescreve em ${d.data_prescricao.split("-").reverse().join("/")}</div>
      <div class="meta">${fmtBRL(d.val_exig)} · ${d.forca}</div></div>`;
  }).join("") + '</div>';
}

/* ---------- Donut (SVG) ---------- */
function donut(elId, legId, slices){
  const total = slices.reduce((s,x)=>s+x.value,0)||1;
  const r=62,cx=80,cy=80,sw=26,C=2*Math.PI*r; let acc=0,segs="";
  slices.forEach(s=>{
    if(s.value<=0) return;
    const len=s.value/total*C;
    segs+=`<circle r="${r}" cx="${cx}" cy="${cy}" fill="none" stroke="${s.color}" stroke-width="${sw}"
      stroke-dasharray="${len.toFixed(2)} ${(C-len).toFixed(2)}" stroke-dashoffset="${(-acc).toFixed(2)}"
      transform="rotate(-90 ${cx} ${cy})"></circle>`;
    acc+=len;
  });
  document.getElementById(elId).innerHTML =
    `<svg width="160" height="160" viewBox="0 0 160 160">${segs}
      <text x="80" y="74" text-anchor="middle" font-size="26" font-weight="700" fill="#1F3864">${total}</text>
      <text x="80" y="94" text-anchor="middle" font-size="11" fill="#6b7280">devedores</text></svg>`;
  document.getElementById(legId).innerHTML = slices.map(s=>
    `<div><i style="background:${s.color}"></i>${s.label} <b>${s.value}</b></div>`).join("");
}

/* ---------- Barras horizontais ---------- */
function hbars(elId, rows, fmt){
  const max=Math.max(...rows.map(r=>r.value),1);
  document.getElementById(elId).innerHTML = rows.map(r=>
    `<div class="bar-row"><div class="bar-label" title="${r.label}">${r.label}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${(r.value/max*100).toFixed(1)}%;background:${r.color}"></div></div>
      <div class="bar-val">${fmt(r.value)}</div></div>`).join("");
}

function renderCharts(){
  const cc={}; DATA.forEach(d=>cc[d.categoria]=(cc[d.categoria]||0)+1);
  donut("donutCat","legCat",["GOV_DIRETA","GOV_INDIRETA","EMPRESA_PRIVADA"].filter(k=>cc[k])
    .map(k=>({label:CATLAB[k]||k,value:cc[k],color:CATCOLOR[k]})));

  const fc={}; DATA.forEach(d=>fc[d.forca]=(fc[d.forca]||0)+1);
  donut("donutForca","legForca",["FORTE","MÉDIA","FRACA"].filter(k=>fc[k])
    .map(k=>({label:k,value:fc[k],color:FORCACOLOR[k]})));

  const pc={}; DATA.forEach(d=>pc[d.proximo_passo]=(pc[d.proximo_passo]||0)+1);
  hbars("barPasso", Object.entries(pc).sort((a,b)=>b[1]-a[1])
    .map(([k,v])=>({label:k,value:v,color:"#3a5fa0"})), v=>v);

  hbars("barTop", DATA.slice(0,10).map(d=>({label:d.nome,value:d.val_exig,color:"#B8963E"})), fmtCompact);
}

/* ---------- Tabela ---------- */
const COLS = [
  {k:"nome", t:"Devedor"},
  {k:"categoria", t:"Categoria"},
  {k:"forca", t:"Força"},
  {k:"val_exig", t:"Exigível", num:true},
  {k:"val_atualizado", t:"Atualizado", num:true},
  {k:"faturas_exig", t:"Fat. exig.", num:true},
  {k:"proximo_passo", t:"Próximo passo"},
  {k:"dias", t:"Prescrição", num:true},
];
let sortKey="val_exig", sortDir=-1;

function valor(d,k){
  if(k==="dias") return diasPrescricao(d.data_prescricao);
  return d[k];
}
function pill(txt,color){return `<span class="pill" style="background:${color}">${txt}</span>`;}

function renderTable(){
  document.getElementById("thead").innerHTML = COLS.map(c=>{
    const arr = sortKey===c.k ? `<span class="arr">${sortDir<0?"▼":"▲"}</span>` : "";
    return `<th data-k="${c.k}">${c.t} ${arr}</th>`;
  }).join("");

  const q=document.getElementById("q").value.toLowerCase().trim();
  const fc=document.getElementById("fCat").value;
  const ff=document.getElementById("fForca").value;
  const fp=document.getElementById("fPasso").value;

  let rows = DATA.filter(d=>
    (!q || d.nome.toLowerCase().includes(q)) &&
    (!fc || d.categoria===fc) && (!ff || d.forca===ff) && (!fp || d.proximo_passo===fp));

  rows.sort((a,b)=>{
    let va=valor(a,sortKey), vb=valor(b,sortKey);
    if(va===null) va=Infinity; if(vb===null) vb=Infinity;
    if(typeof va==="string") return va.localeCompare(vb,"pt-BR")*sortDir;
    return (va-vb)*sortDir;
  });

  document.getElementById("count").textContent = `mostrando ${rows.length} de ${DATA.length}`;
  document.getElementById("tbody").innerHTML = rows.map(d=>{
    const dias=diasPrescricao(d.data_prescricao);
    const nv=nivelPrescricao(dias);
    const dcolor = nv==="r"?"var(--r)":nv==="o"?"var(--o)":nv==="y"?"#b8860b":nv==="venc"?"#7a1c1c":"var(--suave)";
    const dtxt = dias===null?"—":(dias<=0?`vencido (${dias})`:`${dias} d`);
    return `<tr onclick='abrirFicha(${JSON.stringify(d.nome)})'>
      <td><b>${d.nome}</b></td>
      <td>${pill(CATLAB[d.categoria]||d.categoria, CATCOLOR[d.categoria]||"#9aa0a6")}</td>
      <td><span class="dot" style="background:${FORCACOLOR[d.forca]||"#ccc"}"></span>${d.forca}</td>
      <td class="num">${fmtBRL(d.val_exig)}</td>
      <td class="num">${d.val_atualizado?fmtBRL(d.val_atualizado):"—"}</td>
      <td class="num">${d.faturas_exig}/${d.faturas_total}</td>
      <td>${d.proximo_passo}</td>
      <td class="num" style="color:${dcolor};font-weight:600">${dtxt}</td>
    </tr>`;
  }).join("");
}

/* ---------- Ficha (modal) ---------- */
function abrirFicha(nome){
  const d = DATA.find(x=>x.nome===nome); if(!d) return;
  const dias=diasPrescricao(d.data_prescricao);
  const presc = d.data_prescricao
     ? `${d.data_prescricao.split("-").reverse().join("/")}${dias!==null?` (${dias<=0?"vencido":dias+" dias"})`:""}`
     : "—";
  const it=(l,v,full)=>`<div class="fitem ${full?"full":""}"><div class="fl">${l}</div><div class="fv">${v}</div></div>`;
  document.getElementById("modal").innerHTML = `
    <div class="mh">
      <button class="close" onclick="fecharFicha()">×</button>
      <h3>${d.nome}</h3>
      <div class="mc">${CATLAB[d.categoria]||d.categoria} · CNPJ ${fmtCNPJ(d.cnpj)}</div>
    </div>
    <div class="mb"><div class="fgrid">
      ${it("Força probatória", `<span class="dot" style="background:${FORCACOLOR[d.forca]||"#ccc"}"></span>${d.forca}`)}
      ${it("Fase atual", d.fase)}
      ${it("Valor original", d.val_orig?fmtBRL(d.val_orig):"—")}
      ${it("Valor exigível", fmtBRL(d.val_exig))}
      ${it("Valor atualizado", d.val_atualizado?fmtBRL(d.val_atualizado):"—")}
      ${it("Contratos vigentes", d.contratos_vigentes||"—")}
      ${it("Faturas (exig. / total)", `${d.faturas_exig} / ${d.faturas_total}`)}
      ${it("Faturas prescritas", d.faturas_presc)}
      ${it("Próxima prescrição", presc)}
      ${it("Evidências de reconhecimento", d.evidencias_reconhecimento||"—")}
      ${it("Classificação do reconhecimento", d.classificacao_reconhecimento||"—", true)}
      ${it("Próximo passo", d.proximo_passo_full, true)}
    </div></div>`;
  document.getElementById("overlay").classList.add("on");
}
function fecharFicha(){document.getElementById("overlay").classList.remove("on");}

/* ---------- Init ---------- */
function popSelect(id, vals, lab){
  const s=document.getElementById(id);
  vals.forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=lab?(lab[v]||v):v;s.appendChild(o);});
}
function init(){
  renderKPIs(); renderAlertas(); renderCharts();
  popSelect("fCat",[...new Set(DATA.map(d=>d.categoria))].sort(),CATLAB);
  popSelect("fForca",["FORTE","MÉDIA","FRACA"].filter(f=>DATA.some(d=>d.forca===f)));
  popSelect("fPasso",[...new Set(DATA.map(d=>d.proximo_passo))].sort());
  renderTable();
  ["q","fCat","fForca","fPasso"].forEach(id=>document.getElementById(id).addEventListener("input",renderTable));
  document.getElementById("limpar").addEventListener("click",()=>{
    ["q","fCat","fForca","fPasso"].forEach(id=>document.getElementById(id).value="");renderTable();});
  document.getElementById("thead").addEventListener("click",e=>{
    const th=e.target.closest("th"); if(!th) return;
    const k=th.dataset.k;
    if(sortKey===k){sortDir*=-1;}else{sortKey=k;sortDir=(k==="nome"||k==="proximo_passo"||k==="categoria")?1:-1;}
    renderTable();
  });
  document.getElementById("overlay").addEventListener("click",e=>{if(e.target.id==="overlay")fecharFicha();});
  document.addEventListener("keydown",e=>{if(e.key==="Escape")fecharFicha();});
}
init();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
