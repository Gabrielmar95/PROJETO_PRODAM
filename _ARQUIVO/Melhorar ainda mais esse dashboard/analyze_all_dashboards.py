#!/usr/bin/env python3
"""
Análise forense automatizada de TODOS os dashboards PRODAM.
Extrai: título, seções, gráficos, KPIs, fontes de dados, campos DEVS, métricas hardcoded.
"""
import re, os, json, html
from collections import OrderedDict

DASH_DIR = "/home/ubuntu/all_dashboards"
EXISTING = [
    "/home/ubuntu/upload/pasted_file_nudVmu_DASHBOARD_PRODAM_v4.1_BRANDAO_OZORES.html",
    "/home/ubuntu/DASHBOARD_PRODAM_v5.0_BRANDAO_OZORES.html",
    "/home/ubuntu/DASHBOARD_PRODAM_v5.1_BRANDAO_OZORES.html",
    "/home/ubuntu/DASHBOARD_PRODAM_v5.2_BRANDAO_OZORES.html",
    "/home/ubuntu/DASHBOARD_PRODAM_v5.3_BRANDAO_OZORES.html",
]

results = OrderedDict()

def analyze_dashboard(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    info = {}
    info['arquivo'] = os.path.basename(filepath)
    info['tamanho_kb'] = round(os.path.getsize(filepath) / 1024, 1)
    info['linhas'] = content.count('\n') + 1
    
    # Título
    m = re.search(r'<title>([^<]+)</title>', content)
    info['titulo'] = m.group(1).strip() if m else 'Sem título'
    
    # Versão
    vm = re.search(r'v(\d+\.?\d*)', info['arquivo'])
    info['versao'] = vm.group(0) if vm else info['arquivo'].replace('.html','')
    
    # Seções
    sections = re.findall(r'(?:section id|id)="([^"]+)"', content)
    info['secoes'] = list(dict.fromkeys(sections))  # unique, preserve order
    info['num_secoes'] = len(info['secoes'])
    
    # Gráficos (canvas)
    charts = re.findall(r'canvas id="([^"]+)"', content)
    info['graficos'] = charts
    info['num_graficos'] = len(charts)
    
    # KPIs - valores R$ visíveis
    kpis = re.findall(r'R\$\s*[\d.,]+\s*[MKB]', content)
    info['kpis_visiveis'] = list(dict.fromkeys(kpis))[:30]
    
    # Fontes de dados mencionadas
    sources = set()
    for pattern in ['profiles\\.json', 'SPCF', 'BLOCO_[A-Z0-9]', 'FATURAS_CRUZADAS', 
                     'DASHBOARD_DADOS_FINAIS', 'MEMORIAL', 'SERIE_HISTORICA', 'EMPENHOS',
                     'RECONCILIACAO', 'DADOS_NOVOS', 'OCR', 'pendrive', 'Excel']:
        if re.search(pattern, content, re.IGNORECASE):
            sources.add(pattern.replace('\\', ''))
    info['fontes_mencionadas'] = sorted(sources)
    
    # Campos do array DEVS
    devs_fields = re.findall(r'"([a-z_]{1,10})":', content[:5000])
    info['campos_devs'] = sorted(set(devs_fields))
    
    # Contagem de devedores
    devs_count = content.count('"s":') or content.count('"sigla":')
    info['num_devedores_aprox'] = devs_count
    
    # Constantes/dados hardcoded
    consts = re.findall(r'const\s+([A-Z_]+)\s*=', content)
    info['constantes_js'] = consts
    
    # Funcionalidades
    features = []
    if 'data-theme' in content or 'themeToggle' in content:
        features.append('Tema escuro/claro')
    if 'exportBtn' in content or 'exportCSV' in content or 'Exportar' in content:
        features.append('Exportação CSV')
    if 'sidebar' in content:
        features.append('Sidebar navegação')
    if 'filter' in content.lower() or 'fTipo' in content:
        features.append('Filtros interativos')
    if 'sort' in content.lower():
        features.append('Ordenação tabela')
    if 'heatmap' in content.lower():
        features.append('Mapa de calor')
    if 'timeline' in content.lower():
        features.append('Timeline prescrições')
    if 'bubble' in content.lower():
        features.append('Bubble chart')
    if 'animate' in content.lower() or 'fadeIn' in content:
        features.append('Animações')
    if 'responsive' in content.lower() or '@media' in content:
        features.append('Responsivo')
    if 'tab-btn' in content or 'tabContent' in content:
        features.append('Abas/Tabs')
    if 'modal' in content.lower():
        features.append('Modais')
    if 'search' in content.lower() or 'fBusca' in content:
        features.append('Busca textual')
    info['funcionalidades'] = features
    
    # Métricas numéricas hardcoded
    metrics = {}
    for pattern, name in [
        (r'(?:totalVE|total_val_exig|val_exig_total)[^=]*=\s*([\d.]+)', 'val_exigivel_total'),
        (r'(?:totalVA|total_val_atual)[^=]*=\s*([\d.]+)', 'val_atualizado_total'),
        (r'devedores_unicos["\s:]+(\d+)', 'spcf_devedores_unicos'),
        (r'fat_devidas["\s:]+(\d+)', 'spcf_faturas_devidas'),
        (r'perdas_total["\s:]+(\d+[\d.]*)', 'spcf_perdas'),
    ]:
        m = re.search(pattern, content)
        if m:
            metrics[name] = m.group(1)
    info['metricas_hardcoded'] = metrics
    
    # CSS framework/font
    fonts = re.findall(r"font-family:\s*'([^']+)'", content)
    info['fontes_tipograficas'] = list(set(fonts))[:5]
    
    # Chart.js version
    cjs = re.search(r'chart\.js[/@]?([\d.]+)', content, re.IGNORECASE)
    info['chartjs_version'] = cjs.group(1) if cjs else 'N/A'
    
    return info

# Analyze all dashboards
all_files = []
for f in EXISTING:
    if os.path.exists(f):
        all_files.append(f)
for f in sorted(os.listdir(DASH_DIR)):
    fp = os.path.join(DASH_DIR, f)
    if fp.endswith('.html'):
        # Skip duplicates
        basename = os.path.basename(fp)
        if not any(basename == os.path.basename(x) for x in all_files):
            all_files.append(fp)

print(f"Analisando {len(all_files)} dashboards...\n")

for filepath in all_files:
    try:
        info = analyze_dashboard(filepath)
        key = info['versao']
        results[key] = info
        print(f"✓ {info['arquivo']}: {info['versao']} | {info['tamanho_kb']}KB | {info['num_secoes']} seções | {info['num_graficos']} gráficos | {info['num_devedores_aprox']} devs")
    except Exception as e:
        print(f"✗ {os.path.basename(filepath)}: ERRO - {e}")

# Save results
with open('/home/ubuntu/all_dashboards_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nAnálise salva em all_dashboards_analysis.json")
print(f"Total: {len(results)} dashboards únicos analisados")
