"""
SEJUSC - Recalculo 1: Prescricao com Sumula 383/STF para CT C.7/2020 (detalhado).
Regra:
  venc_original     = ultimo dia do mes seguinte a competencia
  quinquenio_natural = venc_original + 5 anos
  primeira_metade_fim = venc_original + 2,5 anos (913 dias)

  Marco efetivo = NE mais recente com data >= venc, ct_ref correspondente
  Se data_marco <= primeira_metade_fim: prescr = max(marco + 2,5a, quinq_nat)
  Senao (2a metade): prescr = marco + 2,5a
  Sem marco: prescr = quinq_nat
"""
import sqlite3, csv, calendar
from datetime import datetime, timedelta

today = datetime(2026, 5, 12)
DOIS_E_MEIO_DIAS = 913

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

def add_years(d, n):
    try:
        return d.replace(year=d.year + n)
    except ValueError:
        return d.replace(month=2, day=28, year=d.year + n)

# 1. Carregar NEs SEJUSC CT C.7/2020 do DB
conn = sqlite3.connect('prodam.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("""SELECT numero, data_emissao, valor, contrato_ref FROM spcf_empenhos
              WHERE cliente LIKE '%SEJUSC%'
                AND contrato_ref IN ('7/2020', '07/2020', 'C.7/2020')
              ORDER BY data_emissao""")
nes_ct = []
for r in c.fetchall():
    try:
        d = datetime.strptime(r['data_emissao'], '%d/%m/%Y')
        nes_ct.append({'num': r['numero'], 'data': d, 'val': r['valor'], 'ct_ref': r['contrato_ref']})
    except:
        continue
print(f'NEs SEJUSC CT 7/2020 (variantes): {len(nes_ct)}')
print(f'Variantes ct_ref distintas: {sorted(set(n["ct_ref"] for n in nes_ct))}')
print()

# 2. Carregar faturas exigiveis CT C.7/2020 do CSV
path = r'PRODAM_DOCS\_WORKFLOW_IMPORTADO\FATURAS_POR_DEVEDOR\SEJUSC_FATURAS_CRUZADAS.csv'
with open(path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f, delimiter=';'))

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
    if ct_csv not in ('C.7/2020', '7/2020', '07/2020'):
        continue
    comp = r.get('competencia') or ''
    if not comp or '/' not in comp:
        continue
    venc = venc_from_comp(comp)
    if not venc:
        continue
    faturas.append({
        'nf': r.get('numero_fatura') or '?',
        'comp': comp,
        'ct_csv': ct_csv,
        'val': val,
        'venc': venc,
        'quinq_nat': add_years(venc, 5),
        'meia_fim': venc + timedelta(days=DOIS_E_MEIO_DIAS),
    })

print(f'Faturas exigiveis CT C.7/2020 (CSV, nao cancel, nao perda, val>0): {len(faturas)}\n')

# 3. Para cada fatura, identificar marco efetivo (NE mais recente com data >= venc)
def fmt(d):
    return d.strftime('%Y-%m-%d') if d else '-'

print('=== TABELA POR FATURA CT C.7/2020 ===\n')
hdr = f'{"NF":>7} | {"comp":>7} | {"venc":>10} | {"quinq_nat":>10} | {"1a_meia":>10} | {"NE_marco":>17} | {"data_marco":>10} | {"cenario":>22} | {"prescr_final":>12} | {"D+":>6} | {"val":>12}'
print(hdr)
print('-' * len(hdr))

resultados = []
for f in faturas:
    nes_pos = [n for n in nes_ct if n['data'] >= f['venc']]
    if not nes_pos:
        marco = None
        cenario = 'sem_marco'
        prescr = f['quinq_nat']
    else:
        marco = max(nes_pos, key=lambda n: n['data'])
        if marco['data'] <= f['meia_fim']:
            cand = marco['data'] + timedelta(days=DOIS_E_MEIO_DIAS)
            if cand > f['quinq_nat']:
                prescr = cand
                cenario = '1a_metade_marco+2.5y'
            else:
                prescr = f['quinq_nat']
                cenario = '1a_metade_quinq_nat(S383)'
        else:
            prescr = marco['data'] + timedelta(days=DOIS_E_MEIO_DIAS)
            cenario = '2a_metade_marco+2.5y'

    d_plus = (prescr - today).days
    resultados.append({**f, 'marco': marco, 'cenario': cenario, 'prescr': prescr, 'd_plus': d_plus})

resultados.sort(key=lambda r: (r['venc'], r['nf']))
for r in resultados:
    ne_num = r['marco']['num'] if r['marco'] else '-'
    ne_data = fmt(r['marco']['data']) if r['marco'] else '-'
    print(f'{r["nf"]:>7} | {r["comp"]:>7} | {fmt(r["venc"]):>10} | {fmt(r["quinq_nat"]):>10} | '
          f'{fmt(r["meia_fim"]):>10} | {ne_num:>17} | {ne_data:>10} | {r["cenario"]:>22} | '
          f'{fmt(r["prescr"]):>12} | {r["d_plus"]:>6} | {r["val"]:>12,.2f}')

# 4. Sumario
print('\n=== SUMARIO CT C.7/2020 ===')
print(f'Total faturas: {len(resultados)}')
prescr_min = min(resultados, key=lambda r: r['d_plus'])
print(f'Prescricao mais proxima: {fmt(prescr_min["prescr"])} (D+{prescr_min["d_plus"]}) - NF {prescr_min["nf"]} comp {prescr_min["comp"]}')
val_total = sum(r['val'] for r in resultados)
print(f'Valor exigivel total CT C.7/2020 (regra S383): R$ {val_total:,.2f}')

# Distribuicao cenarios
from collections import Counter
cen_count = Counter(r['cenario'] for r in resultados)
print('\nDistribuicao cenarios:')
for cen, n in cen_count.most_common():
    val_c = sum(r['val'] for r in resultados if r['cenario'] == cen)
    print(f'  {cen}: {n} fat, R$ {val_c:,.2f}')

conn.close()
