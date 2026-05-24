"""
SEJUSC - Recalculo 2: NEs orfas (sem contrato_ref) x faturas exigiveis
dos mini-CTs P.252/P.287/P.322 + 8/2022.

Critério fuzzy:
  abs(NE.valor - fat.val) / fat.val <= 0.20  (20% tolerancia)
  AND NE.data BETWEEN (venc - 180 dias) AND (venc + 540 dias)

Veredito: MATCH_PROVAVEL (delta<=10% e delta_dias<=180)
          MATCH_FRACO (caso contrario dentro do bounding box)
          SEM_MATCH (nenhum candidato no bounding box)
"""
import sqlite3, csv, calendar
from datetime import datetime, timedelta

def venc_from_comp(comp):
    if not comp or '/' not in comp:
        return None
    m, y = comp.split('/')
    m, y = int(m), int(y)
    if m == 12:
        _, last = calendar.monthrange(y + 1, 1)
        return datetime(y + 1, 1, last)
    _, last = calendar.monthrange(y, m + 1)
    return datetime(y, m + 1, last)

# 1. Carregar NEs orfas SEJUSC 2021+ do DB
conn = sqlite3.connect('prodam.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("""SELECT numero, data_emissao, valor FROM spcf_empenhos
              WHERE cliente LIKE '%SEJUSC%'
                AND (contrato_ref IS NULL OR contrato_ref = '')
                AND substr(data_emissao,7,4) >= '2021'
              ORDER BY data_emissao""")
nes_orf = []
for r in c.fetchall():
    try:
        d = datetime.strptime(r['data_emissao'], '%d/%m/%Y')
        nes_orf.append({'num': r['numero'], 'data': d, 'val': float(r['valor'])})
    except:
        continue
print(f'NEs orfas SEJUSC 2021+: {len(nes_orf)}\n')

# 2. Carregar faturas exigiveis mini-CTs + 8/2022 do CSV
path = r'PRODAM_DOCS\_WORKFLOW_IMPORTADO\FATURAS_POR_DEVEDOR\SEJUSC_FATURAS_CRUZADAS.csv'
with open(path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f, delimiter=';'))

CTS_INTERESSE = {'P.252/2021', 'P.287/2021', 'P.322/2021', 'C.8/2022'}
faturas = []
for r in rows:
    val_str = (r.get('valor_liquido') or '0').replace(',', '.')
    try:
        val = float(val_str)
    except:
        val = 0.0
    if val <= 0:
        continue
    if (r.get('cancelada') or '').upper() == 'TRUE':
        continue
    if (r.get('em_perdas') or '').upper() == 'TRUE':
        continue
    ct_csv = (r.get('contrato') or '').strip()
    if ct_csv not in CTS_INTERESSE:
        continue
    comp = r.get('competencia') or ''
    if not comp or '/' not in comp:
        continue
    venc = venc_from_comp(comp)
    if not venc:
        continue
    faturas.append({
        'nf': r.get('numero_fatura') or '?',
        'ct': ct_csv,
        'comp': comp,
        'venc': venc,
        'val': val,
    })

print(f'Faturas exigiveis (mini-CTs + 8/2022): {len(faturas)}\n')

# 3. Matching fuzzy
print('=== MATCHING FUZZY (20% val, [-180d, +540d]) ===\n')
def fmt(d):
    return d.strftime('%Y-%m-%d') if d else '-'

for f in faturas:
    print(f'Fatura NF {f["nf"]} | ct {f["ct"]:11s} | comp {f["comp"]} | venc {fmt(f["venc"])} | val R$ {f["val"]:>10,.2f}')
    print('  ' + '-' * 90)
    janela_ini = f['venc'] - timedelta(days=180)
    janela_fim = f['venc'] + timedelta(days=540)
    candidatos = []
    for ne in nes_orf:
        if not (janela_ini <= ne['data'] <= janela_fim):
            continue
        if f['val'] == 0:
            continue
        delta_val_pct = abs(ne['val'] - f['val']) / f['val'] * 100
        if delta_val_pct > 20.0:
            continue
        delta_dias = (ne['data'] - f['venc']).days
        candidatos.append({
            **ne, 'delta_val_pct': delta_val_pct, 'delta_dias': delta_dias,
        })
    if not candidatos:
        print('  SEM_MATCH (nenhuma NE na janela com tolerancia <=20%)\n')
        continue
    # Ordenar por proximidade temporal
    candidatos.sort(key=lambda x: abs(x['delta_dias']))
    for ca in candidatos:
        veredito_local = 'MATCH_PROVAVEL' if ca['delta_val_pct'] <= 10 and abs(ca['delta_dias']) <= 180 else 'MATCH_FRACO'
        print(f'  NE {ca["num"]:18s} | data {fmt(ca["data"])} | val R$ {ca["val"]:>10,.2f} | '
              f'd_val {ca["delta_val_pct"]:>5.1f}% | d_dias {ca["delta_dias"]:>+5d} | {veredito_local}')
    # Veredito global = melhor candidato
    melhor = candidatos[0]
    if melhor['delta_val_pct'] <= 10 and abs(melhor['delta_dias']) <= 180:
        v = 'MATCH_PROVAVEL'
    else:
        v = 'MATCH_FRACO'
    print(f'  >> VEREDITO: {v}\n')

# 4. Resumo
print('=== RESUMO ORFAOS DISPONIVEIS ===')
print(f'Total NEs orfas 2021+: {len(nes_orf)}')
print(f'Faturas analisadas: {len(faturas)}')
print(f'\nValores das NEs orfas (todos):')
for ne in sorted(nes_orf, key=lambda x: x['data']):
    print(f'  NE {ne["num"]:18s} {fmt(ne["data"])} R$ {ne["val"]:>10,.2f}')

conn.close()
