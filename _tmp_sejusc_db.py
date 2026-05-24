import sqlite3
from collections import Counter

conn = sqlite3.connect('prodam.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

print('=== SEJUSC NO DB ===\n')

# 1) Faturas SEJUSC
c.execute("SELECT COUNT(*) as n, SUM(CAST(valor_bruto AS REAL)) as v FROM spcf_faturas WHERE cliente LIKE '%SEJUSC%'")
r = c.fetchone()
print(f'spcf_faturas WHERE cliente LIKE SEJUSC: {r["n"]} fat, R$ {r["v"] or 0:,.2f}')

# Variações de nome
c.execute("SELECT DISTINCT cliente FROM spcf_faturas WHERE cliente LIKE '%SEJUSC%' OR cliente LIKE '%JUSTI%' LIMIT 20")
print('Variações de cliente:')
for row in c.fetchall():
    print(f'  {row["cliente"]!r}')

# 2) Empenhos SEJUSC
print('\n--- EMPENHOS ---')
c.execute("SELECT COUNT(*) as n, SUM(CAST(valor AS REAL)) as v FROM spcf_empenhos WHERE cliente LIKE '%SEJUSC%'")
r = c.fetchone()
print(f'spcf_empenhos WHERE cliente LIKE SEJUSC: {r["n"]} emp, R$ {r["v"] or 0:,.2f}')

c.execute("SELECT DISTINCT cliente FROM spcf_empenhos WHERE cliente LIKE '%SEJUSC%' OR cliente LIKE '%JUSTI%' LIMIT 20")
print('Variações cliente em empenhos:')
for row in c.fetchall():
    print(f'  {row["cliente"]!r}')

# 3) Datas dos empenhos SEJUSC (para análise marcos interruptivos)
print('\n--- EMPENHOS SEJUSC POR ANO ---')
c.execute("""SELECT substr(data_emissao,1,4) as ano, COUNT(*) as n, SUM(CAST(valor AS REAL)) as v
              FROM spcf_empenhos WHERE cliente LIKE '%SEJUSC%'
              GROUP BY ano ORDER BY ano""")
for row in c.fetchall():
    print(f'  {row["ano"]}: {row["n"]} emp, R$ {row["v"] or 0:,.2f}')

# 4) Empenhos por contrato (para cruzar com mini-CTs P.252/P.287/P.322/C.7)
print('\n--- EMPENHOS POR CONTRATO ---')
c.execute("""SELECT contrato_ref, COUNT(*) as n FROM spcf_empenhos
              WHERE cliente LIKE '%SEJUSC%' GROUP BY contrato_ref ORDER BY n DESC LIMIT 20""")
for row in c.fetchall():
    print(f'  ct={row["contrato_ref"]!r}: {row["n"]} emp')

# 5) Empenhos mais recentes (potenciais marcos pós-vencimento das 61 exigíveis)
print('\n--- EMPENHOS SEJUSC 2024-2026 (potenciais marcos recentes) ---')
c.execute("""SELECT numero, data_emissao, valor, contrato_ref FROM spcf_empenhos
              WHERE cliente LIKE '%SEJUSC%' AND substr(data_emissao,1,4) >= '2024'
              ORDER BY data_emissao DESC LIMIT 30""")
for row in c.fetchall():
    print(f'  NE {row["numero"]:15s} data {row["data_emissao"]} ct {row["contrato_ref"]!r:25s} R$ {row["valor"]}')

# 6) Faturas SEJUSC com empenho vinculado (vw_fatura_completa se existir)
print('\n--- v_fatura_completa SEJUSC ---')
try:
    c.execute("SELECT COUNT(*) FROM v_fatura_completa WHERE cliente LIKE '%SEJUSC%'")
    print(f'v_fatura_completa SEJUSC: {c.fetchone()[0]}')
except Exception as e:
    print(f'Sem view: {e}')

# 7) Contratos SEJUSC
print('\n--- CONTRATOS ---')
c.execute("SELECT numero, valor_global, status, fim_vigencia FROM spcf_contratos WHERE cliente LIKE '%SEJUSC%' ORDER BY numero")
for row in c.fetchall():
    print(f'  CT {row["numero"]} val {row["valor_global"]} st {row["status"]} fim {row["fim_vigencia"]}')

conn.close()
