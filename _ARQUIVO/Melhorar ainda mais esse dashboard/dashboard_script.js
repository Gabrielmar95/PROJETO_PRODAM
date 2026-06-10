
/* ===== CHART PALETTE ===== */
const PAL = {
  primary: '#0F172A', secondary: '#334155', muted: '#64748B', light: '#94A3B8',
  accent: '#C9A84C', accentLight: '#E2C97E',
  danger: '#DC2626', success: '#16A34A', warn: '#D97706', info: '#2563EB',
};

/* ===== Chart.js global defaults ===== */
Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#64748B';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyle = 'circle';
Chart.defaults.plugins.legend.labels.padding = 16;
Chart.defaults.plugins.tooltip.backgroundColor = '#0F172A';
Chart.defaults.plugins.tooltip.titleFont = {weight:'700',size:13};
Chart.defaults.plugins.tooltip.bodyFont = {size:12};
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.displayColors = true;
Chart.defaults.plugins.tooltip.boxPadding = 4;
Chart.defaults.elements.bar.borderRadius = 6;
Chart.defaults.elements.bar.borderSkipped = false;

/* ===== HELPERS ===== */
function fmtBRL(v){return 'R$ '+(v||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2})}
function fmtM(v){if(Math.abs(v)>=1e6)return 'R$ '+(v/1e6).toFixed(1)+'M';if(Math.abs(v)>=1e3)return 'R$ '+(v/1e3).toFixed(0)+'K';return 'R$ '+v.toFixed(0)}
function fTag(f){
  const cls=f==='FORTE'?'tag-forte':f==='MEDIA'||f==='MÉDIA'?'tag-media':f==='FRACA'?'tag-fraca':'tag-sem';
  return '<span class="tag '+cls+'">'+f+'</span>';
}
function phTag(f){
  const cls=f==='F0'?'tag-f0':f==='F0_DIAGNOSTICO'?'tag-f0d':f==='F3'?'tag-f3':f==='F5'?'tag-f5':'tag-f0';
  const label=f==='F0_DIAGNOSTICO'?'F0D':f;
  return '<span class="tag '+cls+'">'+label+'</span>';
}

/* ===== ANIMATED COUNTER ===== */
function animateValue(el,start,end,duration,formatter){
  let startTs=null;
  const step=(ts)=>{
    if(!startTs)startTs=ts;
    const p=Math.min((ts-startTs)/duration,1);
    const e=1-Math.pow(1-p,3);
    const cur=start+(end-start)*e;
    el.textContent=formatter?formatter(cur):Math.floor(cur).toLocaleString('pt-BR');
    if(p<1)window.requestAnimationFrame(step);
  };
  window.requestAnimationFrame(step);
}

/* ===== KPI VALUES ===== */
const totalVE=DEVS.reduce((s,d)=>s+d.ve,0);
const totalVA=DEVS.reduce((s,d)=>s+d.va,0);
const totalFat=DEVS.reduce((s,d)=>s+d.ft,0);
const totalEvid=DEVS.reduce((s,d)=>s+d.evid,0);
const totalNSC=DEVS.reduce((s,d)=>s+d.nsc,0);
const totalNSCv=DEVS.reduce((s,d)=>s+d.nscv,0);

setTimeout(()=>{
  animateValue(document.getElementById('kpiVE'),0,totalVE,1500,fmtBRL);
  animateValue(document.getElementById('kpiVA'),0,totalVA,1500,fmtBRL);
  animateValue(document.getElementById('kpiFee'),0,totalVE*0.40*0.20,1500,fmtBRL);
  animateValue(document.getElementById('kpiFaturas'),0,totalFat,1200,v=>Math.floor(v).toLocaleString('pt-BR'));
  animateValue(document.getElementById('kpiEvid'),0,totalEvid,1200,v=>Math.floor(v).toLocaleString('pt-BR'));
},300);
document.getElementById('kpiNSC').textContent=totalNSC;
document.getElementById('kpiNSCval').textContent=fmtM(totalNSCv)+' expostos';
document.getElementById('kpiFatDet').textContent=DEVS.reduce((s,d)=>s+d.fe,0)+' exigiveis + '+DEVS.reduce((s,d)=>s+d.fp,0)+' prescritas';

/* ===== SIDEBAR NAVIGATION ===== */
document.getElementById('menuToggle').addEventListener('click',()=>{
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebarOverlay').classList.toggle('active');
});
document.getElementById('sidebarOverlay').addEventListener('click',()=>{
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').classList.remove('active');
});
const sections=document.querySelectorAll('section[id]');
const navLinks=document.querySelectorAll('.sidebar-nav a');
window.addEventListener('scroll',()=>{
  let current='';
  sections.forEach(s=>{if(window.scrollY>=s.offsetTop-100)current=s.getAttribute('id')});
  navLinks.forEach(l=>{l.classList.remove('active');if(l.getAttribute('href')==='#'+current)l.classList.add('active')});
});

/* ===== THEME TOGGLE ===== */
document.getElementById('themeToggle').addEventListener('click',()=>{
  const h=document.documentElement;
  const isDark=h.getAttribute('data-theme')==='dark';
  h.setAttribute('data-theme',isDark?'light':'dark');
  document.getElementById('themeToggle').innerHTML=isDark?'&#9790; Tema':'&#9788; Tema';
});

/* ===== ALERT TOGGLE ===== */
document.getElementById('alertToggle').addEventListener('click',()=>{
  const items=document.getElementById('alertItems');
  const btn=document.getElementById('alertToggle');
  if(items.style.display==='none'){items.style.display='flex';btn.textContent='Recolher'}
  else{items.style.display='none';btn.textContent='Expandir'}
});

/* ===== EXPORT CSV ===== */
document.getElementById('exportBtn').addEventListener('click',()=>{
  const headers=['Sigla','Nome','CNPJ','Tipo','Val.Exigivel','Val.Atualizado','Forca','Fase','Faturas','Exigiveis','Prescritas','Score','CPRAC','Prescricao','Prox.Passo'];
  let csv=headers.join(';')+'\n';
  DEVS.forEach(d=>{csv+=[d.s,d.n,d.c,d.tr,d.ve.toFixed(2),d.va.toFixed(2),d.f,d.fs,d.ft,d.fe,d.fp,(d.sc*100).toFixed(0)+'%',d.cprac?'SIM':'NAO',d.pd||'',d.pr].join(';')+'\n'});
  const blob=new Blob([csv],{type:'text/csv;charset=utf-8;'});
  const link=document.createElement('a');
  link.href=URL.createObjectURL(blob);
  link.download='PRODAM_Devedores_v5.0.csv';
  link.click();
});

/* ===== FILTER RESET ===== */
document.getElementById('filterReset').addEventListener('click',()=>{
  document.querySelectorAll('#filters select').forEach(s=>s.value='');
  document.getElementById('fBusca').value='';
  render();
});

/* ===== TIMELINE ===== */
(function buildTimeline(){
  const urgent=DEVS.filter(d=>d.pdi!==null&&d.pdi>-60&&d.pdi<200&&d.ve>0).sort((a,b)=>a.pdi-b.pdi).slice(0,12);
  const container=document.getElementById('prescTimeline');
  let html='';
  urgent.forEach(d=>{
    const isU=d.pdi<0||d.pdi<=45;
    html+='<div class="timeline-item'+(isU?' urgent':'')+'">';
    html+='<div class="tl-date">'+(d.pdi<0?'VENCIDA D'+d.pdi:'D+'+d.pdi)+(d.pd?' ('+d.pd+')':'')+'</div>';
    html+='<div class="tl-content"><strong>'+d.s+'</strong> &mdash; '+d.n+'</div>';
    html+='<div class="tl-value">'+fmtM(d.ve)+'</div>';
    html+='</div>';
  });
  container.innerHTML=html;
})();

/* ===== HEATMAP ===== */
(function buildHeatmap(){
  const scored=DEVS.filter(d=>d.sc>0).sort((a,b)=>b.sc-a.sc);
  const container=document.getElementById('riskHeatmap');
  let html='';
  scored.forEach(d=>{
    const score=d.sc;
    let bg,color;
    if(score>=0.8){bg='#0F172A';color='#C9A84C'}
    else if(score>=0.6){bg='#334155';color='#E2E8F0'}
    else if(score>=0.4){bg='#64748B';color='#F1F5F9'}
    else if(score>=0.2){bg='#CBD5E1';color='#334155'}
    else{bg='#F1F5F9';color='#94A3B8'}
    html+='<div class="heatmap-cell" style="background:'+bg+';color:'+color+'" title="'+d.n+' — Score: '+(score*100).toFixed(0)+'% — '+fmtM(d.ve)+'">';
    html+='<div class="hm-name">'+d.s+'</div>';
    html+='<div class="hm-val">'+(score*100).toFixed(0)+'%</div>';
    html+='</div>';
  });
  container.innerHTML=html;
})();

/* ===== TABLE LOGIC ===== */
let sortCol=3,sortAsc=false;
function getFiltered(){
  const fT=document.getElementById('fTipo').value;
  const fF=document.getElementById('fForca').value;
  const fFs=document.getElementById('fFase').value;
  const fP=document.getElementById('fPresc').value;
  const fC=document.getElementById('fCprac').value;
  const fB=document.getElementById('fBusca').value.toLowerCase();
  return DEVS.filter(d=>{
    if(fT&&!d.t.includes(fT))return false;
    if(fF==='FORTE'&&d.f!=='FORTE')return false;
    if(fF==='MEDIA'&&d.f!=='MÉDIA')return false;
    if(fF==='FRACA'&&d.f!=='FRACA')return false;
    if(fF==='SEM'&&['FORTE','MÉDIA','FRACA'].includes(d.f))return false;
    if(fFs&&d.fs!==fFs)return false;
    if(fP==='venc'&&(d.pdi===null||d.pdi>=0))return false;
    if(fP==='urg'&&(d.pdi===null||d.pdi<0||d.pdi>90))return false;
    if(fC==='sim'&&!d.cprac)return false;
    if(fB&&!d.s.toLowerCase().includes(fB)&&!d.n.toLowerCase().includes(fB))return false;
    return true;
  });
}
function sortData(){
  const data=getFiltered();
  data.sort((a,b)=>{
    let va2,vb2;
    switch(sortCol){
      case 0:va2=DEVS.indexOf(a);vb2=DEVS.indexOf(b);break;
      case 1:va2=a.s;vb2=b.s;break;
      case 3:va2=a.ve;vb2=b.ve;break;
      case 4:va2=a.va;vb2=b.va;break;
      case 7:va2=a.ft;vb2=b.ft;break;
      case 10:va2=a.b2e26;vb2=b.b2e26;break;
      case 11:va2=a.nsc;vb2=b.nsc;break;
      case 12:va2=a.evid;vb2=b.evid;break;
      case 13:va2=a.sc;vb2=b.sc;break;
      case 16:va2=a.pdi!==null?a.pdi:9999;vb2=b.pdi!==null?b.pdi:9999;break;
      default:va2=a.ve;vb2=b.ve;
    }
    if(typeof va2==='string')return sortAsc?va2.localeCompare(vb2):vb2.localeCompare(va2);
    return sortAsc?va2-vb2:vb2-va2;
  });
  return data;
}
function render(){
  const data=sortData();
  const tbody=document.getElementById('tblBody');
  let html='',totVE=0,totVA=0;
  data.forEach((d,i)=>{
    const prescTxt=d.pdi!==null?(d.pdi<0?'D'+d.pdi:'D+'+d.pdi)+(d.pd?' ('+d.pd+')':''):'&mdash;';
    const al=d.pdi===null?'':'<span class="alerta '+(d.pdi<0?'alerta-red':d.pdi<=90?'alerta-orange':d.pdi<=180?'alerta-yellow':'alerta-green')+'"></span>';
    const blTxt=d.bltot>0?d.blok+'/'+d.bltot:'&mdash;';
    totVE+=d.ve;totVA+=d.va;
    html+='<tr>'
      +'<td>'+(i+1)+'</td>'
      +'<td title="'+d.n+'"><strong>'+d.s+'</strong></td>'
      +'<td>'+d.tr+'</td>'
      +'<td style="text-align:right;font-family:var(--font-mono);font-size:11px">'+fmtBRL(d.ve)+'</td>'
      +'<td style="text-align:right;font-family:var(--font-mono);font-size:11px">'+fmtBRL(d.va)+'</td>'
      +'<td>'+fTag(d.f)+'</td>'
      +'<td>'+phTag(d.fs)+'</td>'
      +'<td style="text-align:center">'+d.ft+'</td>'
      +'<td style="text-align:center">'+d.fe+'</td>'
      +'<td style="text-align:center">'+d.fp+'</td>'
      +'<td style="text-align:right;font-family:var(--font-mono);font-size:11px">'+(d.b2e26>0?fmtBRL(d.b2e26):'&mdash;')+'</td>'
      +'<td style="text-align:center;color:'+(d.nsc>0?'var(--danger)':'inherit')+';font-weight:'+(d.nsc>0?'700':'400')+'">'+d.nsc+'</td>'
      +'<td style="text-align:center">'+d.evid+'</td>'
      +'<td style="text-align:center">'+(d.sc>0?'<span style="font-family:var(--font-mono)">'+(d.sc*100).toFixed(0)+'%</span>':'&mdash;')+'</td>'
      +'<td style="text-align:center">'+(d.cprac?'<span class="tag tag-cprac">SIM</span>':'&mdash;')+'</td>'
      +'<td style="text-align:center">'+blTxt+'</td>'
      +'<td style="font-family:var(--font-mono);font-size:11px">'+prescTxt+'</td>'
      +'<td style="text-align:center">'+al+'</td>'
      +'<td style="font-size:11px;max-width:140px;overflow:hidden;text-overflow:ellipsis" title="'+(d.pr||'')+'">'+(d.pr||'&mdash;')+'</td>'
      +'</tr>';
  });
  html+='<tr class="total"><td></td><td><strong>TOTAL ('+data.length+')</strong></td><td></td>'
    +'<td style="text-align:right;font-family:var(--font-mono)">'+fmtBRL(totVE)+'</td>'
    +'<td style="text-align:right;font-family:var(--font-mono)">'+fmtBRL(totVA)+'</td>'
    +'<td colspan="14"></td></tr>';
  tbody.innerHTML=html;
  document.getElementById('tblCount').textContent=data.length+' registros';
}
document.querySelectorAll('#filters select, #filters input').forEach(el=>el.addEventListener(el.tagName==='INPUT'?'input':'change',render));
document.querySelectorAll('th[data-col]').forEach(th=>th.addEventListener('click',()=>{
  const col=parseInt(th.dataset.col);
  document.querySelectorAll('th').forEach(t=>t.classList.remove('sorted'));
  th.classList.add('sorted');
  if(col===sortCol)sortAsc=!sortAsc;else{sortCol=col;sortAsc=false}
  th.querySelector('.sort-arrow').innerHTML=sortAsc?'&#9650;':'&#9660;';
  render();
}));
render();

/* ===== CHARTS ===== */

// 1. Top 15 Ranking
const top15=[...DEVS].sort((a,b)=>b.ve-a.ve).slice(0,15);
new Chart(document.getElementById('chartRanking'),{
  type:'bar',
  data:{labels:top15.map(d=>d.s),datasets:[
    {label:'Val. Exigivel',data:top15.map(d=>d.ve),backgroundColor:top15.map((d,i)=>`rgba(15,23,42,${1-i*0.04})`),borderRadius:6},
    {label:'Val. Atualizado',data:top15.map(d=>d.va),backgroundColor:top15.map((d,i)=>`rgba(201,168,76,${0.6-i*0.02})`),borderRadius:6}
  ]},
  options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',
    plugins:{tooltip:{callbacks:{label:ctx=>ctx.dataset.label+': '+fmtBRL(ctx.raw)}},legend:{position:'top'}},
    scales:{x:{ticks:{callback:v=>fmtM(v)},grid:{color:'rgba(0,0,0,0.04)'}},y:{grid:{display:false}}}
  }
});

// 2. Forca probatoria
const fqData=[12,15,35,9];
const fqLabels=['FORTE (12)','MEDIA (15)','FRACA (35)','Sem (9)'];
const fqCores=[PAL.primary,PAL.muted,PAL.light,'#E2E8F0'];
const fvData=[104556870,8958896,7996732,0];
new Chart(document.getElementById('chartForcaQtd'),{type:'doughnut',data:{labels:fqLabels,datasets:[{data:fqData,backgroundColor:fqCores,borderWidth:3,borderColor:'#fff',hoverOffset:8}]},options:{responsive:true,maintainAspectRatio:false,cutout:'65%',plugins:{legend:{position:'bottom',labels:{font:{size:11},padding:12}},title:{display:true,text:'Por Quantidade',font:{size:13,weight:'600'},padding:{bottom:8}}}}});
new Chart(document.getElementById('chartForcaVal'),{type:'doughnut',data:{labels:fqLabels,datasets:[{data:fvData,backgroundColor:fqCores,borderWidth:3,borderColor:'#fff',hoverOffset:8}]},options:{responsive:true,maintainAspectRatio:false,cutout:'65%',plugins:{legend:{position:'bottom',labels:{font:{size:11},padding:12}},tooltip:{callbacks:{label:ctx=>fmtBRL(ctx.raw)}},title:{display:true,text:'Por Valor',font:{size:13,weight:'600'},padding:{bottom:8}}}}});

// 3. Pipeline
const fLabels=["F0","F0_DIAGNOSTICO","F3","F5"];
const fDescs={"F0":"(49 devs)","F0_DIAGNOSTICO":"(8 devs)","F3":"(9 devs)","F5":"(5 devs)"};
const fCores={'F0':'#CBD5E1','F0_DIAGNOSTICO':'#FCD34D','F3':PAL.accent,'F5':PAL.primary};
new Chart(document.getElementById('chartPipeline'),{type:'bar',data:{labels:fLabels.map(f=>f+(fDescs[f]?' '+fDescs[f]:'')),datasets:[
  {label:'Devedores',data:fLabels.map(f=>FASES[f]?.c||0),backgroundColor:fLabels.map(f=>fCores[f]||'#ccc'),borderRadius:6,yAxisID:'y'},
  {label:'Valor Exigivel',data:fLabels.map(f=>FASES[f]?.v||0),type:'line',borderColor:PAL.accent,backgroundColor:PAL.accent+'22',pointRadius:7,pointBackgroundColor:PAL.accent,pointBorderColor:'#fff',pointBorderWidth:2,yAxisID:'y1',tension:0.4,fill:true}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{tooltip:{callbacks:{label:ctx=>ctx.datasetIndex===1?fmtM(ctx.raw):ctx.raw+' devedores'}}},scales:{y:{beginAtZero:true,position:'left',title:{display:true,text:'Devedores'},grid:{color:'rgba(0,0,0,0.04)'}},y1:{beginAtZero:true,position:'right',grid:{drawOnChartArea:false},ticks:{callback:v=>fmtM(v)},title:{display:true,text:'Valor'}}}}});

// 4. Prescricao bubble
const prescData=DEVS.filter(d=>d.pdi!==null&&d.pdi>-60&&d.pdi<1400&&d.ve>0).map(d=>({x:d.pdi,y:d.ve,label:d.s,r:Math.max(5,Math.min(25,Math.sqrt(d.ve/60000)))}));
new Chart(document.getElementById('chartPresc'),{type:'bubble',data:{datasets:[{label:'Devedores',data:prescData,backgroundColor:prescData.map(p=>p.x<0?'rgba(220,38,38,0.5)':p.x<=90?'rgba(217,119,6,0.5)':p.x<=180?'rgba(201,168,76,0.5)':'rgba(22,163,74,0.5)'),borderColor:prescData.map(p=>p.x<0?PAL.danger:p.x<=90?PAL.warn:p.x<=180?PAL.accent:PAL.success),borderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>{const d=ctx.raw;return d.label+': '+fmtM(d.y)+' ('+(d.x<0?'VENCIDA D'+d.x:'D+'+d.x)+')'}}}},scales:{x:{title:{display:true,text:'Dias ate prescricao (negativo = vencida)',font:{weight:'600'}},grid:{color:ctx=>ctx.tick&&ctx.tick.value===0?PAL.danger:'rgba(0,0,0,0.04)',lineWidth:ctx=>ctx.tick&&ctx.tick.value===0?2:1}},y:{title:{display:true,text:'Valor exigivel',font:{weight:'600'}},ticks:{callback:v=>fmtM(v)},grid:{color:'rgba(0,0,0,0.04)'}}}}});

// 5. Faturamento x Recebimento
const topFat=[...DEVS].filter(d=>d.fat>0).sort((a,b)=>b.fat-a.fat).slice(0,10);
new Chart(document.getElementById('chartFatRec'),{type:'bar',data:{labels:topFat.map(d=>d.s),datasets:[
  {label:'Faturamento',data:topFat.map(d=>d.fat),backgroundColor:PAL.primary+'cc',borderRadius:6},
  {label:'Recebimento',data:topFat.map(d=>d.rec),backgroundColor:PAL.success+'aa',borderRadius:6}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{tooltip:{callbacks:{label:ctx=>ctx.dataset.label+': '+fmtM(ctx.raw)+' ('+topFat[ctx.dataIndex].tp+'%)'}}},scales:{y:{ticks:{callback:v=>fmtM(v)},grid:{color:'rgba(0,0,0,0.04)'}},x:{grid:{display:false}}}}});

// 6. Empenhos 2026
const topEmp=[...DEVS].filter(d=>d.b2e26>0).sort((a,b)=>b.b2e26-a.b2e26).slice(0,12);
new Chart(document.getElementById('chartEmp26'),{type:'bar',data:{labels:topEmp.map(d=>d.s),datasets:[
  {label:'Empenhado 2026',data:topEmp.map(d=>d.b2e26),backgroundColor:PAL.muted+'cc',borderRadius:6},
  {label:'NE s/ Cobertura',data:topEmp.map(d=>d.nscv),backgroundColor:PAL.danger+'aa',borderRadius:6}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{tooltip:{callbacks:{label:ctx=>ctx.dataset.label+': '+fmtBRL(ctx.raw)}}},scales:{y:{ticks:{callback:v=>fmtM(v)},grid:{color:'rgba(0,0,0,0.04)'}},x:{grid:{display:false}}}}});

// 7. Cenarios
new Chart(document.getElementById('chartCenarios'),{type:'bar',data:{labels:['Conservador (20%)','Base (40%)','Otimista (70%)'],datasets:[
  {label:'Recuperado',data:[CENARIOS.conservador.rec,CENARIOS.base.rec,CENARIOS.otimista.rec],backgroundColor:[PAL.light,PAL.muted,PAL.primary],borderRadius:6},
  {label:'Fee (20%)',data:[CENARIOS.conservador.fee,CENARIOS.base.fee,CENARIOS.otimista.fee],backgroundColor:PAL.accent,borderRadius:6}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{tooltip:{callbacks:{label:ctx=>ctx.dataset.label+': '+fmtBRL(ctx.raw)}}},scales:{y:{ticks:{callback:v=>fmtM(v)},grid:{color:'rgba(0,0,0,0.04)'}},x:{grid:{display:false}}}}});

// 8. NEs sem cobertura
const nscDevs=[...DEVS].filter(d=>d.nsc>0).sort((a,b)=>b.nscv-a.nscv);
new Chart(document.getElementById('chartNSC'),{type:'bar',data:{labels:nscDevs.map(d=>d.s+' ('+d.nsc+' NEs)'),datasets:[{label:'Valor NEs s/ Cobertura',data:nscDevs.map(d=>d.nscv),backgroundColor:PAL.danger+'bb',borderRadius:6,borderColor:PAL.danger,borderWidth:1}]},options:{responsive:true,maintainAspectRatio:false,plugins:{tooltip:{callbacks:{label:ctx=>fmtBRL(ctx.raw)}}},scales:{y:{ticks:{callback:v=>fmtM(v)},grid:{color:'rgba(0,0,0,0.04)'}},x:{grid:{display:false}}}}});

// 9. Vias processuais
const viasData={'CPRAC Elegivel':DEVS.filter(d=>d.cprac).length,'Transacao Referendada':DEVS.filter(d=>d.transacao).length,'Peticao (F5)':DEVS.filter(d=>d.fs==='F5').length,'TRD (F3)':DEVS.filter(d=>d.fs==='F3').length,'Diagnostico':DEVS.filter(d=>d.fs==='F0_DIAGNOSTICO').length,'Triagem (F0)':DEVS.filter(d=>d.fs==='F0').length};
new Chart(document.getElementById('chartVias'),{type:'bar',data:{labels:Object.keys(viasData),datasets:[{label:'Devedores',data:Object.values(viasData),backgroundColor:[PAL.accent,'#92400E',PAL.primary,PAL.muted,'#FCD34D','#CBD5E1'],borderRadius:6}]},options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{beginAtZero:true,grid:{color:'rgba(0,0,0,0.04)'}},y:{grid:{display:false}}}}});

// 10. Padrao inadimplencia
const padData=DEVS.reduce((acc,d)=>{if(d.pi&&d.pi!=='—'){if(!acc[d.pi])acc[d.pi]={count:0,val:0};acc[d.pi].count++;acc[d.pi].val+=d.ve}return acc},{});
const padLabels=Object.keys(padData);
const padCores={'CRONICO':PAL.danger,'INTERMITENTE':PAL.warn,'RECENTE':PAL.accent,'PONTUAL':PAL.success};
new Chart(document.getElementById('chartPadrao'),{type:'bar',data:{labels:padLabels.map(p=>p+' ('+padData[p].count+')'),datasets:[
  {label:'Devedores',data:padLabels.map(p=>padData[p].count),backgroundColor:padLabels.map(p=>padCores[p]||PAL.light),borderRadius:6,yAxisID:'y'},
  {label:'Valor Exigivel',data:padLabels.map(p=>padData[p].val),type:'line',borderColor:PAL.primary,pointRadius:7,pointBackgroundColor:PAL.primary,pointBorderColor:'#fff',pointBorderWidth:2,yAxisID:'y1',tension:0.4}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{tooltip:{callbacks:{label:ctx=>ctx.datasetIndex===1?fmtM(ctx.raw):ctx.raw+' devedores'}}},scales:{y:{beginAtZero:true,position:'left',title:{display:true,text:'Devedores'},grid:{color:'rgba(0,0,0,0.04)'}},y1:{beginAtZero:true,position:'right',grid:{drawOnChartArea:false},ticks:{callback:v=>fmtM(v)},title:{display:true,text:'Valor'}}}}});

/* ===== INTERSECTION OBSERVER ===== */
const observer=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting){e.target.style.opacity='1';e.target.style.transform='translateY(0)'}})},{threshold:0.1});
document.querySelectorAll('.animate-in').forEach(el=>observer.observe(el));

/* ===== SMOOTH SCROLL ===== */
document.querySelectorAll('.sidebar-nav a').forEach(link=>{
  link.addEventListener('click',e=>{
    e.preventDefault();
    const target=document.querySelector(link.getAttribute('href'));
    if(target){target.scrollIntoView({behavior:'smooth',block:'start'});document.getElementById('sidebar').classList.remove('open');document.getElementById('sidebarOverlay').classList.remove('active')}
  });
});
