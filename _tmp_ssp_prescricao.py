import csv, calendar
from datetime import datetime
from collections import Counter

path = r'PRODAM_DOCS\_WORKFLOW_IMPORTADO\FATURAS_POR_DEVEDOR\SSP_FATURAS_CRUZADAS.csv'
with open(path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f, delimiter=';'))

print(f'Total faturas CSV: {len(rows)}')

today = datetime(2026, 5, 12)
prescritas = []
exigiveis = []

for r in rows:
    comp = r['competencia']
    nf = r['pref']
    val_str = r.get('valor_servicos', '0').replace(',', '.')
    try:
        val = float(val_str)
    except:
        val = 0.0
    ct = r.get('contrato', '?')

    try:
        m, y = comp.split('/')
        m, y = int(m), int(y)
        if m == 12:
            _, last = calendar.monthrange(y + 1, 1)
            venc = datetime(y + 1, 1, last)
        else:
            _, last = calendar.monthrange(y, m + 1)
            venc = datetime(y, m + 1, last)
        prescr = venc.replace(year=venc.year + 5)
        d_plus = (prescr - today).days

        entry = {
            'nf': nf, 'comp': comp, 'ct': ct, 'val': val,
            'venc': venc.strftime('%Y-%m-%d'),
            'prescr': prescr.strftime('%Y-%m-%d'),
            'd_plus': d_plus,
        }

        if d_plus < 0:
            prescritas.append(entry)
        else:
            exigiveis.append(entry)
    except Exception as ex:
        print(f'  ERRO parsing comp={comp} nf={nf}: {ex}')

print(f'\nPrescritas: {len(prescritas)}')
print(f'Exigiveis: {len(exigiveis)}')

comp_prescr = Counter(e['comp'] for e in prescritas)
comp_exig = Counter(e['comp'] for e in exigiveis)

print(f'\n=== PRESCRITAS por competencia ===')
for c in sorted(comp_prescr.keys()):
    entries = [e for e in prescritas if e['comp'] == c]
    val_sum = sum(e['val'] for e in entries)
    print(f'  {c}: {comp_prescr[c]} fat, R$ {val_sum:,.2f}, prescr {entries[0]["prescr"]}')

print(f'\n=== EXIGIVEIS por competencia ===')
for c in sorted(comp_exig.keys(), key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0]))):
    entries = [e for e in exigiveis if e['comp'] == c]
    val_sum = sum(e['val'] for e in entries)
    d_plus = entries[0]['d_plus']
    print(f'  {c}: {len(entries)} fat, R$ {val_sum:,.2f}, prescr {entries[0]["prescr"]} (D+{d_plus})')

if exigiveis:
    earliest = min(exigiveis, key=lambda e: e['d_plus'])
    print(f'\n=== PRESCRICAO PROXIMA CORRETA ===')
    print(f'  NF {earliest["nf"]}, comp {earliest["comp"]}, ct {earliest["ct"]}')
    print(f'  prescr {earliest["prescr"]}, D+{earliest["d_plus"]}')

total_exig = sum(e['val'] for e in exigiveis)
total_prescr = sum(e['val'] for e in prescritas)
print(f'\nValor exigivel (CSV): R$ {total_exig:,.2f}')
print(f'Valor prescrito (CSV): R$ {total_prescr:,.2f}')
print(f'Total geral: R$ {total_exig + total_prescr:,.2f}')
