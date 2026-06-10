#!/usr/bin/env python3
"""Analyze all SPCF_MAR2026 data for dashboard integration."""
import json, csv, os, glob
from collections import defaultdict

DATA_DIR = "/home/ubuntu/spcf_data"

# 1. Load profiles.json
with open(f"{DATA_DIR}/profiles.json") as f:
    profiles = json.load(f)
print(f"=== PROFILES.JSON ===")
print(f"Total devedores: {len(profiles)}")

# Extract key fields from profiles (dict keyed by sigla)
profile_summary = []
for sigla, p in profiles.items():
    profile_summary.append({
        'sigla': sigla,
        'nome': p.get('nome_completo', p.get('nome','')),
        'tipo': p.get('tipo', p.get('natureza','')),
        'val_orig': p.get('val_orig', 0) or 0,
        'val_exig': p.get('val_exig', 0) or 0,
        'val_atualizado': p.get('val_atualizado', 0) or 0,
        'forca': p.get('forca_probatoria',''),
        'fase': p.get('fase_atual',''),
        'faturas': p.get('faturas_total', 0) or 0,
        'exigiveis': p.get('faturas_exigiveis', 0) or 0,
        'prescritas': p.get('faturas_prescritas', 0) or 0,
        'empenho_2026': p.get('emp_2026', 0) or 0,
        'nes_sem_cobertura': p.get('nes_sem_cobertura_qtd', 0) or 0,
        'score': p.get('score_composto', 0) or 0,
        'cprac': p.get('elegivel_cprac', ''),
        'prescricao': p.get('data_prescricao_proxima', ''),
        'prox_passo': p.get('proximo_passo', ''),
        'spcf_total_receber': p.get('spcf_total_receber', 0) or 0,
        'spcf_perdas': p.get('spcf_perdas', 0) or 0,
        'faturamento_total': p.get('faturamento_total_2019_2026', 0) or 0,
        'recebimento_total': p.get('recebimento_total_2019_2026', 0) or 0,
        'taxa_pagamento': p.get('taxa_pagamento_pct', 0) or 0,
        'padrao': p.get('padrao_inadimplencia', ''),
        'fat_canceladas_qtd': p.get('fat_canceladas_qtd', 0) or 0,
        'fat_canceladas_val': p.get('fat_canceladas_val_bruto', 0) or 0,
        'a_empenhar_2026': p.get('a_empenhar_2026', 0) or 0,
        'nes_sem_cob_valor': p.get('nes_sem_cobertura_valor', 0) or 0,
    })

# 2. Load BLOCO_B_SERIE_HISTORICA.json
with open(f"{DATA_DIR}/BLOCO_B_SERIE_HISTORICA.json") as f:
    serie_hist = json.load(f)
print(f"\n=== BLOCO_B_SERIE_HISTORICA ===")
print(f"Type: {type(serie_hist)}")
if isinstance(serie_hist, dict):
    print(f"Keys: {list(serie_hist.keys())[:10]}")
    # Get sparkline data for top devedores
    for dev in list(serie_hist.keys())[:3]:
        d = serie_hist[dev]
        if isinstance(d, dict):
            print(f"  {dev}: keys={list(d.keys())[:8]}")

# 3. Load DADOS_NOVOS_POR_DEVEDOR.json
with open(f"{DATA_DIR}/DADOS_NOVOS_POR_DEVEDOR.json") as f:
    dados_novos = json.load(f)
print(f"\n=== DADOS_NOVOS_POR_DEVEDOR ===")
print(f"Devedores: {len(dados_novos)}")
for dev in list(dados_novos.keys())[:3]:
    d = dados_novos[dev]
    if isinstance(d, dict):
        print(f"  {dev}: keys={list(d.keys())}")

# 4. Load BLOCO_D_EMPENHOS.json
with open(f"{DATA_DIR}/BLOCO_D_EMPENHOS.json") as f:
    empenhos = json.load(f)
print(f"\n=== BLOCO_D_EMPENHOS ===")
print(f"Type: {type(empenhos)}")
if isinstance(empenhos, dict):
    print(f"Keys: {list(empenhos.keys())[:10]}")
elif isinstance(empenhos, list):
    print(f"Count: {len(empenhos)}")
    if len(empenhos) > 0:
        print(f"First item keys: {list(empenhos[0].keys()) if isinstance(empenhos[0], dict) else 'not dict'}")

# 5. Load enriquecimento_stats.json
with open(f"{DATA_DIR}/enriquecimento_stats.json") as f:
    enriq_stats = json.load(f)
print(f"\n=== ENRIQUECIMENTO_STATS ===")
print(json.dumps(enriq_stats, indent=2)[:2000])

# 6. Analyze faturas cruzadas CSVs
print(f"\n=== FATURAS CRUZADAS ===")
faturas_dir = f"{DATA_DIR}/faturas"
total_faturas = 0
dev_faturas_summary = []
for csv_file in sorted(glob.glob(f"{faturas_dir}/*_FATURAS_CRUZADAS.csv")):
    devname = os.path.basename(csv_file).replace("_FATURAS_CRUZADAS.csv", "")
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            cols = reader.fieldnames or []
            
            vigentes = sum(1 for r in rows if r.get('status_prescricao','') == 'VIGENTE')
            prescritas = sum(1 for r in rows if r.get('status_prescricao','') == 'PRESCRITA')
            
            val_vigente = 0
            val_prescrito = 0
            val_corrigido = 0
            for r in rows:
                try:
                    v = float(r.get('valor_fatura','0').replace(',','.') if r.get('valor_fatura') else '0')
                except:
                    v = 0
                try:
                    vc = float(r.get('valor_corrigido_calc','0').replace(',','.') if r.get('valor_corrigido_calc') else '0')
                except:
                    vc = 0
                if r.get('status_prescricao','') == 'VIGENTE':
                    val_vigente += v
                else:
                    val_prescrito += v
                val_corrigido += vc
            
            # Count by acao_recomendada
            acoes = defaultdict(int)
            for r in rows:
                a = r.get('acao_recomendada', 'N/A')
                acoes[a] += 1
            
            # Count by forca_probatoria
            forcas = defaultdict(int)
            for r in rows:
                fp = r.get('forca_probatoria', 'N/A')
                forcas[fp] += 1
            
            dev_faturas_summary.append({
                'devedor': devname,
                'total': len(rows),
                'vigentes': vigentes,
                'prescritas': prescritas,
                'val_vigente': val_vigente,
                'val_prescrito': val_prescrito,
                'val_corrigido': val_corrigido,
                'acoes': dict(acoes),
                'forcas': dict(forcas),
                'cols': len(cols)
            })
            total_faturas += len(rows)
            print(f"  {devname}: {len(rows)} faturas, {vigentes} vigentes, {prescritas} prescritas, {len(cols)} cols, val_vig={val_vigente:,.2f}, val_corr={val_corrigido:,.2f}")
    except Exception as e:
        print(f"  {devname}: ERROR - {e}")

print(f"\nTotal faturas cruzadas: {total_faturas}")

# 7. Analyze OVERLAP file
print(f"\n=== OVERLAP PAGOS x DEVIDAS ===")
with open(f"{DATA_DIR}/OVERLAP_PAGOS_DEVIDAS_1643.csv", 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    overlap_rows = list(reader)
    print(f"Total overlap: {len(overlap_rows)}")
    if overlap_rows:
        print(f"Columns: {list(overlap_rows[0].keys())[:10]}")
        # Count by devedor
        overlap_by_dev = defaultdict(int)
        for r in overlap_rows:
            dev = r.get('cliente', r.get('devedor', 'N/A'))
            overlap_by_dev[dev] += 1
        print("Top overlap devedores:")
        for dev, cnt in sorted(overlap_by_dev.items(), key=lambda x: -x[1])[:10]:
            print(f"  {dev}: {cnt}")

# 8. Save consolidated analysis
analysis = {
    'profiles_count': len(profiles),
    'serie_historica_devedores': len(serie_hist) if isinstance(serie_hist, dict) else 0,
    'dados_novos_devedores': len(dados_novos),
    'total_faturas_cruzadas': total_faturas,
    'dev_faturas_summary': dev_faturas_summary,
    'overlap_total': len(overlap_rows),
    'enriquecimento': enriq_stats
}

with open('/home/ubuntu/spcf_analysis_result.json', 'w') as f:
    json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)

print("\n=== ANALYSIS SAVED ===")
print(f"Output: /home/ubuntu/spcf_analysis_result.json")
