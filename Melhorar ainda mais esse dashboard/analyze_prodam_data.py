#!/usr/bin/env python3
"""
Comprehensive analysis of all PRODAM data files to extract key metrics
for the dashboard improvement.
"""
import json
import csv
import os
import glob
from collections import defaultdict

DATA_DIR = '/home/ubuntu/prodam_data'

# ============================================================
# 1. PROFILES.JSON - Full analysis
# ============================================================
print("=" * 80)
print("1. PROFILES.JSON - Análise Completa")
print("=" * 80)

with open(f'{DATA_DIR}/profiles.json', 'r', encoding='utf-8') as f:
    profiles = json.load(f)

print(f"\nTotal devedores: {len(profiles)}")

# Aggregate key metrics
total_val_exig = 0
total_val_orig = 0
total_val_atualizado = 0
total_faturas = 0
total_fat_exig = 0
total_fat_presc = 0
total_evidencias = 0
total_nes_sem_cob = 0
total_nes_sem_cob_val = 0
total_emp_2026 = 0
total_fat_canceladas_qtd = 0
total_fat_canceladas_val = 0
total_faturamento = 0
total_recebimento = 0
total_perdas = 0
total_spcf_devidas_val = 0
total_spcf_aberto_val = 0

forca_counts = defaultdict(int)
fase_counts = defaultdict(int)
tipo_counts = defaultdict(int)
prox_passo_counts = defaultdict(int)
padrao_inad_counts = defaultdict(int)
recon_status_counts = defaultdict(int)
modelo_counts = defaultdict(int)

devedores_prescritos = []
devedores_urgentes = []
devedores_cprac = []
devedores_com_titulo = []

for sigla, p in profiles.items():
    ve = float(p.get('val_exig', 0) or 0)
    vo = float(p.get('val_orig', 0) or 0)
    va = float(p.get('val_atualizado', 0) or 0)
    total_val_exig += ve
    total_val_orig += vo
    total_val_atualizado += va
    
    ft = int(p.get('faturas_total', 0) or 0)
    fe = int(p.get('faturas_exigiveis', 0) or 0)
    fp = int(p.get('faturas_prescritas', 0) or 0)
    total_faturas += ft
    total_fat_exig += fe
    total_fat_presc += fp
    
    ev = int(p.get('evidencias_reconhecimento', 0) or 0)
    total_evidencias += ev
    
    nsc = int(p.get('nes_sem_cobertura_qtd', 0) or 0)
    nscv = float(p.get('nes_sem_cobertura_valor', 0) or 0)
    total_nes_sem_cob += nsc
    total_nes_sem_cob_val += nscv
    
    e26 = float(p.get('emp_2026', 0) or 0)
    total_emp_2026 += e26
    
    fcq = int(p.get('fat_canceladas_qtd', 0) or 0)
    fcv = float(p.get('fat_canceladas_val_liquido', 0) or 0)
    total_fat_canceladas_qtd += fcq
    total_fat_canceladas_val += fcv
    
    fat_total = float(p.get('faturamento_total_2019_2026', 0) or 0)
    rec_total = float(p.get('recebimento_total_2019_2026', 0) or 0)
    total_faturamento += fat_total
    total_recebimento += rec_total
    
    perdas = float(p.get('spcf_perdas', 0) or 0)
    total_perdas += perdas
    
    spcf_dev = float(p.get('spcf_fat_devidas_val', 0) or 0)
    spcf_ab = float(p.get('spcf_fat_aberto_val', 0) or 0)
    total_spcf_devidas_val += spcf_dev
    total_spcf_aberto_val += spcf_ab
    
    forca = p.get('forca_probatoria', 'N/A')
    forca_counts[forca] += 1
    
    fase = p.get('fase_atual', 'N/A')
    fase_counts[fase] += 1
    
    tipo = p.get('tipo', 'N/A')
    tipo_counts[tipo] += 1
    
    prox = p.get('proximo_passo', 'N/A')
    prox_passo_counts[prox] += 1
    
    padrao = p.get('padrao_inadimplencia', 'N/A')
    padrao_inad_counts[padrao] += 1
    
    recon = p.get('reconciliacao_status', 'N/A')
    recon_status_counts[recon] += 1
    
    modelo = p.get('modelo_notificacao', 'N/A')
    modelo_counts[modelo] += 1
    
    # Prescrição
    dp = p.get('data_prescricao_proxima')
    if dp:
        from datetime import datetime, date
        try:
            d = datetime.strptime(dp, '%Y-%m-%d').date()
            today = date(2026, 4, 1)
            dias = (d - today).days
            if dias < 0:
                devedores_prescritos.append((sigla, ve, dias, dp))
            elif dias <= 90:
                devedores_urgentes.append((sigla, ve, dias, dp))
        except:
            pass
    
    if p.get('elegivel_cprac'):
        devedores_cprac.append((sigla, ve))
    
    if p.get('titulo_executivo'):
        devedores_com_titulo.append((sigla, ve))

print(f"\n--- TOTAIS FINANCEIROS ---")
print(f"Val Exigível: R$ {total_val_exig:,.2f}")
print(f"Val Original: R$ {total_val_orig:,.2f}")
print(f"Val Atualizado: R$ {total_val_atualizado:,.2f}")
print(f"Faturamento 2019-2026: R$ {total_faturamento:,.2f}")
print(f"Recebimento 2019-2026: R$ {total_recebimento:,.2f}")
print(f"Taxa Pgto Global: {(total_recebimento/total_faturamento*100) if total_faturamento else 0:.1f}%")
print(f"Empenhos 2026: R$ {total_emp_2026:,.2f}")
print(f"Perdas SPCF: R$ {total_perdas:,.2f}")
print(f"SPCF Fat Devidas: R$ {total_spcf_devidas_val:,.2f}")
print(f"SPCF Fat Aberto: R$ {total_spcf_aberto_val:,.2f}")
print(f"Fat Canceladas: {total_fat_canceladas_qtd} (R$ {total_fat_canceladas_val:,.2f})")
print(f"NEs sem Cobertura: {total_nes_sem_cob} (R$ {total_nes_sem_cob_val:,.2f})")

print(f"\n--- FATURAS ---")
print(f"Total: {total_faturas}")
print(f"Exigíveis: {total_fat_exig}")
print(f"Prescritas: {total_fat_presc}")
print(f"Evidências: {total_evidencias}")

print(f"\n--- DISTRIBUIÇÕES ---")
print(f"Força Probatória: {dict(forca_counts)}")
print(f"Fases: {dict(fase_counts)}")
print(f"Tipos: {dict(tipo_counts)}")
print(f"Próx. Passo: {dict(prox_passo_counts)}")
print(f"Padrão Inadimplência: {dict(padrao_inad_counts)}")
print(f"Reconciliação Status: {dict(recon_status_counts)}")
print(f"Modelo Notificação: {dict(modelo_counts)}")

print(f"\n--- PRESCRIÇÃO ---")
print(f"Prescritos: {len(devedores_prescritos)}")
for s, v, d, dp in sorted(devedores_prescritos, key=lambda x: x[2]):
    print(f"  {s}: R$ {v:,.2f} (D{d}, {dp})")

print(f"\nUrgentes (<90d): {len(devedores_urgentes)}")
for s, v, d, dp in sorted(devedores_urgentes, key=lambda x: x[2]):
    print(f"  {s}: R$ {v:,.2f} (D+{d}, {dp})")

print(f"\n--- CPRAC ---")
print(f"Elegíveis: {len(devedores_cprac)}")
val_cprac = sum(v for _, v in devedores_cprac)
print(f"Valor total CPRAC: R$ {val_cprac:,.2f}")

print(f"\n--- TÍTULO EXECUTIVO ---")
print(f"Com título: {len(devedores_com_titulo)}")

# ============================================================
# 2. FATURAS CRUZADAS - Analysis
# ============================================================
print("\n" + "=" * 80)
print("2. FATURAS CRUZADAS - Análise por Devedor")
print("=" * 80)

csv_files = glob.glob(f'{DATA_DIR}/*_FATURAS_CRUZADAS.csv')
grand_total = 0
grand_vigentes = 0
grand_prescritas = 0
grand_canceladas = 0
grand_val_vig = 0
grand_val_presc = 0
grand_val_corrigido = 0

devedor_stats = []

for csv_file in sorted(csv_files):
    devedor = os.path.basename(csv_file).replace('_FATURAS_CRUZADAS.csv', '')
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)
    
    total = len(rows)
    grand_total += total
    
    vigentes = 0
    prescritas = 0
    canceladas = 0
    val_vig = 0
    val_presc = 0
    val_corrigido = 0
    val_total_atualizado = 0
    com_empenho = 0
    com_ne_sem_cob = 0
    paga_em_devidas = 0
    
    forca_dist = defaultdict(int)
    acao_dist = defaultdict(int)
    
    for row in rows:
        status = row.get('status_prescricao', '')
        val_liq = float(row.get('valor_liquido', 0) or 0)
        
        if status == 'PRESCRITA':
            prescritas += 1
            grand_prescritas += 1
            val_presc += val_liq
            grand_val_presc += val_liq
        else:
            vigentes += 1
            grand_vigentes += 1
            val_vig += val_liq
            grand_val_vig += val_liq
        
        if row.get('cancelada', '').upper() == 'TRUE':
            canceladas += 1
            grand_canceladas += 1
        
        try:
            vc = float(row.get('valor_corrigido_calc', 0) or 0)
        except (ValueError, TypeError):
            vc = 0
        val_corrigido += vc
        grand_val_corrigido += vc
        
        try:
            vta = float(row.get('valor_total_atualizado', 0) or 0)
        except (ValueError, TypeError):
            vta = 0
        val_total_atualizado += vta
        
        if row.get('empenho_vinculado', ''):
            com_empenho += 1
        
        if row.get('empenho_sem_cobertura_flag', '').upper() == 'TRUE':
            com_ne_sem_cob += 1
        
        incon = row.get('tipo_inconsistencia', '')
        if 'PAGA_EM_DEVIDAS' in incon:
            paga_em_devidas += 1
        
        forca = row.get('forca_probatoria', 'N/A')
        forca_dist[forca] += 1
        
        acao = row.get('acao_recomendada', 'N/A')
        acao_dist[acao] += 1
    
    devedor_stats.append({
        'devedor': devedor,
        'total': total,
        'vigentes': vigentes,
        'prescritas': prescritas,
        'canceladas': canceladas,
        'val_vig': val_vig,
        'val_presc': val_presc,
        'val_corrigido': val_corrigido,
        'val_total_atualizado': val_total_atualizado,
        'com_empenho': com_empenho,
        'ne_sem_cob': com_ne_sem_cob,
        'paga_em_devidas': paga_em_devidas,
        'forca': dict(forca_dist),
        'acao': dict(acao_dist)
    })
    
    print(f"\n{devedor}:")
    print(f"  Total: {total} | Vigentes: {vigentes} | Prescritas: {prescritas} | Canceladas: {canceladas}")
    print(f"  Val Vigentes: R$ {val_vig:,.2f} | Val Prescritas: R$ {val_presc:,.2f}")
    print(f"  Val Corrigido: R$ {val_corrigido:,.2f} | Val Total Atualizado: R$ {val_total_atualizado:,.2f}")
    print(f"  Com Empenho: {com_empenho} | NE s/Cob: {com_ne_sem_cob} | PAGA_EM_DEVIDAS: {paga_em_devidas}")
    print(f"  Força: {dict(forca_dist)}")
    print(f"  Ação: {dict(acao_dist)}")

print(f"\n--- TOTAIS FATURAS CRUZADAS ---")
print(f"Total faturas: {grand_total}")
print(f"Vigentes: {grand_vigentes} ({grand_vigentes/grand_total*100:.1f}%)")
print(f"Prescritas: {grand_prescritas} ({grand_prescritas/grand_total*100:.1f}%)")
print(f"Canceladas: {grand_canceladas}")
print(f"Val Vigentes: R$ {grand_val_vig:,.2f}")
print(f"Val Prescritas: R$ {grand_val_presc:,.2f}")
print(f"Val Corrigido Total: R$ {grand_val_corrigido:,.2f}")

# ============================================================
# 3. DASHBOARD_DADOS_FINAIS.JSON
# ============================================================
print("\n" + "=" * 80)
print("3. DASHBOARD_DADOS_FINAIS.JSON")
print("=" * 80)

with open(f'{DATA_DIR}/DASHBOARD_DADOS_FINAIS.json', 'r', encoding='utf-8') as f:
    dash_data = json.load(f)

for key in dash_data:
    val = dash_data[key]
    if isinstance(val, dict):
        print(f"\n{key}: {json.dumps(val, indent=2, ensure_ascii=False)[:500]}")
    elif isinstance(val, list):
        print(f"\n{key}: [{len(val)} items]")
        if val and isinstance(val[0], dict):
            print(f"  Keys: {list(val[0].keys())}")
            for item in val[:3]:
                print(f"  {json.dumps(item, ensure_ascii=False)[:200]}")
    else:
        print(f"{key}: {val}")

# ============================================================
# 4. SAVE CONSOLIDATED DATA FOR DASHBOARD
# ============================================================
print("\n" + "=" * 80)
print("4. SAVING CONSOLIDATED DATA")
print("=" * 80)

consolidated = {
    'totais': {
        'val_exigivel': total_val_exig,
        'val_original': total_val_orig,
        'val_atualizado': total_val_atualizado,
        'faturamento_2019_2026': total_faturamento,
        'recebimento_2019_2026': total_recebimento,
        'taxa_pagamento_pct': (total_recebimento/total_faturamento*100) if total_faturamento else 0,
        'empenhos_2026': total_emp_2026,
        'perdas_spcf': total_perdas,
        'spcf_devidas': total_spcf_devidas_val,
        'spcf_aberto': total_spcf_aberto_val,
        'fat_canceladas_qtd': total_fat_canceladas_qtd,
        'fat_canceladas_val': total_fat_canceladas_val,
        'nes_sem_cobertura_qtd': total_nes_sem_cob,
        'nes_sem_cobertura_val': total_nes_sem_cob_val,
        'total_faturas': total_faturas,
        'faturas_exigiveis': total_fat_exig,
        'faturas_prescritas': total_fat_presc,
        'evidencias': total_evidencias,
        'devedores': len(profiles),
    },
    'distribuicoes': {
        'forca': dict(forca_counts),
        'fase': dict(fase_counts),
        'tipo': dict(tipo_counts),
        'prox_passo': dict(prox_passo_counts),
        'padrao_inadimplencia': dict(padrao_inad_counts),
        'reconciliacao_status': dict(recon_status_counts),
        'modelo_notificacao': dict(modelo_counts),
    },
    'faturas_cruzadas': {
        'total': grand_total,
        'vigentes': grand_vigentes,
        'prescritas': grand_prescritas,
        'canceladas': grand_canceladas,
        'val_vigentes': grand_val_vig,
        'val_prescritas': grand_val_presc,
        'val_corrigido': grand_val_corrigido,
        'por_devedor': devedor_stats
    },
    'prescritos': [{'sigla': s, 'val': v, 'dias': d, 'data': dp} for s, v, d, dp in devedores_prescritos],
    'urgentes': [{'sigla': s, 'val': v, 'dias': d, 'data': dp} for s, v, d, dp in devedores_urgentes],
}

with open('/home/ubuntu/prodam_consolidated.json', 'w', encoding='utf-8') as f:
    json.dump(consolidated, f, ensure_ascii=False, indent=2)

print("Consolidated data saved to /home/ubuntu/prodam_consolidated.json")
print("DONE!")
