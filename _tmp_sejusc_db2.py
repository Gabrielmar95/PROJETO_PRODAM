import sqlite3
import csv, calendar
from datetime import datetime
from collections import defaultdict

conn = sqlite3.connect('prodam.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Empenhos por ano (corrigindo substr para DD/MM/YYYY)
print('=== EMPENHOS SEJUSC POR ANO (data em DD/MM/YYYY) ===')
c.execute("""SELECT substr(data_emissao,7,4) as ano, COUNT(*) as n, SUM(CAST(valor AS REAL)) as v
              FROM spcf_empenhos WHERE cliente LIKE '%SEJUSC%'
              GROUP BY ano ORDER BY ano""")
for row in c.fetchall():
    print(f'  {row["ano"]}: {row["n"]} emp, R$ {row["v"] or 0:,.2f}')

# Empenhos 2021+ (potenciais marcos pós-vencimento das exigíveis 2021)
print('\n=== EMPENHOS SEJUSC 2021+ (marcos potenciais Art. 202 VI CC) ===')
c.execute("""SELECT numero, data_emissao, valor, contrato_ref
              FROM spcf_empenhos
              WHERE cliente LIKE '%SEJUSC%'
                AND substr(data_emissao,7,4) >= '2021'
              ORDER BY substr(data_emissao,7,4) DESC, substr(data_emissao,4,2) DESC, substr(data_emissao,1,2) DESC
              LIMIT 50""")
emp_2021_plus = c.fetchall()
print(f'Total 2021+: {len(emp_2021_plus)}\n')
for row in emp_2021_plus:
    print(f'  NE {row["numero"]:18s} data {row["data_emissao"]} ct {row["contrato_ref"]!r:25s} R$ {row["valor"]}')

# Empenhos sem contrato_ref (122 emp)
print('\n=== EMPENHOS SEM CONTRATO_REF (122 emp órfãos) ===')
c.execute("""SELECT substr(data_emissao,7,4) as ano, COUNT(*) as n, SUM(CAST(valor AS REAL)) as v
              FROM spcf_empenhos
              WHERE cliente LIKE '%SEJUSC%' AND (contrato_ref IS NULL OR contrato_ref = '')
              GROUP BY ano ORDER BY ano""")
for row in c.fetchall():
    print(f'  {row["ano"]}: {row["n"]} emp, R$ {row["v"] or 0:,.2f}')

# Contratos SEJUSC (descobrir schema correto)
print('\n=== SCHEMA spcf_contratos ===')
c.execute("PRAGMA table_info(spcf_contratos)")
for row in c.fetchall():
    print(f'  {row["name"]}: {row["type"]}')

# Contratos SEJUSC
print('\n=== CONTRATOS SEJUSC ===')
c.execute("SELECT * FROM spcf_contratos WHERE cliente LIKE '%SEJUSC%' LIMIT 10")
for row in c.fetchall():
    print(f'  {dict(row)}')

# v_fatura_completa SEJUSC com empenho
print('\n=== v_fatura_completa SEJUSC (com empenhos) ===')
try:
    c.execute("PRAGMA table_info(v_fatura_completa)")
    cols = [r["name"] for r in c.fetchall()]
    print(f'Colunas: {cols}')
    c.execute("SELECT * FROM v_fatura_completa WHERE cliente LIKE '%SEJUSC%' LIMIT 5")
    for row in c.fetchall():
        print(f'  {dict(row)}')
except Exception as e:
    print(f'erro: {e}')

# CRUZAMENTO: para cada contrato das 61 exigíveis no CSV, listar NEs com data DEPOIS do vencimento
print('\n=== CRUZAMENTO NE × FATURAS EXIGÍVEIS (marcos pós-vencimento) ===')

# Ler exigíveis do CSV
path = r'PRODAM_DOCS\_WORKFLOW_IMPORTADO\FATURAS_POR_DEVEDOR\SEJUSC_FATURAS_CRUZADAS.csv'
with open(path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f, delimiter=';'))

today = datetime(2026, 5, 12)

def venc_from_comp(comp):
    if not comp or '/' not in comp:
        return None
    m, y = comp.split('/')
    m, y = int(m), int(y)
    if m == 12:
        _, last = calendar.monthrange(y + 1, 1)
        return datetime(y + 1, 1, last)
    else:
        _, last = calendar.monthrange(y, m + 1)
        return datetime(y, m + 1, last)

# Normalizar contrato CSV → DB (C.7/2020 → 7/2020; P.252/2021 → 252/2021; 19/2021 → 19/2021)
def norm_ct(ct_csv):
    if not ct_csv:
        return None
    ct = ct_csv.strip()
    if ct.startswith('C.'):
        return ct[2:].lstrip('0')
    if ct.startswith('P.'):
        return ct[2:].lstrip('0')
    return ct.lstrip('0')

# Para cada exigível com valor > 0
exigiveis_data = []
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
    comp = r.get('competencia') or ''
    if not comp or '/' not in comp:
        continue
    try:
        venc = venc_from_comp(comp)
        prescr = venc.replace(year=venc.year + 5)
    except:
        continue
    if (prescr - today).days < 0:
        continue  # já prescrita
    ct = r.get('contrato', '')
    exigiveis_data.append({
        'nf': r.get('numero_fatura') or '?',
        'comp': comp, 'ct_csv': ct, 'ct_db': norm_ct(ct),
        'val': val, 'venc': venc, 'prescr': prescr,
        'd_plus': (prescr - today).days,
    })

# Agrupar por contrato
ct_groups = defaultdict(list)
for e in exigiveis_data:
    ct_groups[e['ct_db']].append(e)

print(f'\nExigiveis validas: {len(exigiveis_data)}')
print(f'Contratos das exigiveis (CSV -> DB): {sorted(set(e["ct_csv"] for e in exigiveis_data))}')

print('\n--- Para cada contrato exigivel: marcos NE pos-vencimento ---')
for ct_db, faturas in sorted(ct_groups.items()):
    earliest_venc = min(f['venc'] for f in faturas)
    qtd = len(faturas)
    val_tot = sum(f['val'] for f in faturas)
    print(f'\n  CT {ct_db!r} ({qtd} fat, R$ {val_tot:,.2f}, vencimento mais antigo: {earliest_venc.strftime("%Y-%m-%d")})')
    # NEs deste contrato
    c.execute("""SELECT numero, data_emissao, valor FROM spcf_empenhos
                  WHERE cliente LIKE '%SEJUSC%' AND contrato_ref = ?
                  ORDER BY substr(data_emissao,7,4) DESC, substr(data_emissao,4,2) DESC, substr(data_emissao,1,2) DESC""",
              (ct_db,))
    nes = c.fetchall()
    if not nes:
        print(f'    SEM NEs no DB para ct={ct_db}')
        continue
    # NEs APÓS o vencimento da fatura mais antiga
    nes_pos = []
    for n in nes:
        try:
            d_str = n['data_emissao']
            d_ne = datetime.strptime(d_str, '%d/%m/%Y')
            if d_ne >= earliest_venc:
                nes_pos.append((n, d_ne))
        except:
            continue
    print(f'    NEs total ct={ct_db}: {len(nes)} | NEs após venc {earliest_venc.strftime("%Y-%m-%d")}: {len(nes_pos)}')
    for n, d_ne in nes_pos[:5]:
        print(f'      NE {n["numero"]:18s} {d_ne.strftime("%Y-%m-%d")} R$ {n["valor"]}')

conn.close()
