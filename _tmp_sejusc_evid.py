"""
SEJUSC - Recalculo 3: evidencias_reconhecimento (criterio estrito).

Criterio:
  Uma NE conta como evidencia de reconhecimento APENAS SE:
    1. cliente LIKE '%SEJUSC%'
    2. contrato_ref NAO vazio
    3. contrato_ref corresponde a algum contrato com PELO MENOS UMA fatura em
       aberto (valor_liquido > 0, nao cancel, nao em perdas) no CSV cruzado
    4. data_emissao da NE >= venc_original da fatura mais antiga em aberto
       daquele contrato (marco pos-vencimento)
"""
import sqlite3, csv, calendar
from datetime import datetime, timedelta
from collections import defaultdict

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

def norm_ct(ct_csv):
    if not ct_csv:
        return None
    ct = ct_csv.strip()
    if ct.startswith('C.') or ct.startswith('P.'):
        return ct[2:].lstrip('0')
    return ct.lstrip('0')

def fmt(d):
    return d.strftime('%Y-%m-%d') if d else '-'

# 1. Faturas em aberto agrupadas por contrato normalizado
path = r'PRODAM_DOCS\_WORKFLOW_IMPORTADO\FATURAS_POR_DEVEDOR\SEJUSC_FATURAS_CRUZADAS.csv'
with open(path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f, delimiter=';'))

cts_aberto = defaultdict(list)  # ct_db_norm -> list[fat]
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
    ct_norm = norm_ct(ct_csv)
    if not ct_norm:
        continue
    comp = r.get('competencia') or ''
    venc = venc_from_comp(comp)
    if not venc:
        continue
    cts_aberto[ct_norm].append({
        'nf': r.get('numero_fatura'), 'ct_csv': ct_csv, 'comp': comp,
        'venc': venc, 'val': val,
    })

# 2. Para cada contrato aberto, buscar NEs SEJUSC com data >= venc mais antigo
conn = sqlite3.connect('prodam.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print('=== EVIDENCIAS DE RECONHECIMENTO (CRITERIO ESTRITO) ===\n')
hdr = f'{"contrato":>10} | {"qtd_fat":>7} | {"venc_min":>10} | {"NEs>=venc":>10} | {"val_NEs":>15}'
print(hdr)
print('-' * len(hdr))

total_nes_estrito = 0
total_val_nes = 0.0
nes_unique = set()
detalhes_por_ct = {}

for ct_norm, fats in sorted(cts_aberto.items()):
    venc_min = min(f['venc'] for f in fats)
    c.execute("""SELECT numero, data_emissao, valor FROM spcf_empenhos
                  WHERE cliente LIKE '%SEJUSC%' AND contrato_ref = ?
                  ORDER BY data_emissao""", (ct_norm,))
    nes_pos = []
    for r in c.fetchall():
        try:
            d = datetime.strptime(r['data_emissao'], '%d/%m/%Y')
            if d >= venc_min:
                nes_pos.append({'num': r['numero'], 'data': d, 'val': float(r['valor'])})
        except:
            continue
    val_nes = sum(n['val'] for n in nes_pos)
    print(f'{ct_norm:>10} | {len(fats):>7} | {fmt(venc_min):>10} | {len(nes_pos):>10} | {val_nes:>15,.2f}')
    detalhes_por_ct[ct_norm] = nes_pos
    for n in nes_pos:
        nes_unique.add(n['num'])
    total_nes_estrito += len(nes_pos)
    total_val_nes += val_nes

print('-' * len(hdr))
print(f'\nTOTAL evidencias_reconhecimento (criterio estrito): {total_nes_estrito}')
print(f'NEs distintas (numero unico): {len(nes_unique)}')
print(f'Valor total NEs marco: R$ {total_val_nes:,.2f}')

# Listar NEs por contrato
print('\n=== DETALHE NEs POR CONTRATO ===')
for ct_norm, nes in sorted(detalhes_por_ct.items()):
    if not nes:
        continue
    print(f'\n  CT {ct_norm} ({len(nes)} NEs marco):')
    for n in sorted(nes, key=lambda x: x['data']):
        print(f'    NE {n["num"]:18s} {fmt(n["data"])} R$ {n["val"]:>10,.2f}')

# Profile diz 37 ("E": 37)
print(f'\n=== COMPARACAO ===')
print(f'profile.evidencias_reconhecimento.por_tipo.E: 37')
print(f'criterio estrito (calculado): {total_nes_estrito}')
print(f'delta: {total_nes_estrito - 37}')

conn.close()
