import sqlite3
conn = sqlite3.connect('prodam.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Verificar empenhos orfaos sem contrato_ref — podem ser os P.252/P.287/P.322
print('=== EMPENHOS SEM CONTRATO_REF 2021+ ===')
c.execute("""SELECT numero, data_emissao, valor FROM spcf_empenhos
              WHERE cliente LIKE '%SEJUSC%' AND (contrato_ref IS NULL OR contrato_ref = '')
                AND substr(data_emissao,7,4) >= '2021'
              ORDER BY substr(data_emissao,7,4) DESC, substr(data_emissao,4,2) DESC""")
for r in c.fetchall():
    cols = dict(r)
    print(f'  NE {cols["numero"]:18s} {cols["data_emissao"]} R$ {cols["valor"]}')

# Schema spcf_empenhos
print('\n=== SCHEMA spcf_empenhos ===')
c.execute("PRAGMA table_info(spcf_empenhos)")
for r in c.fetchall():
    print(f'  {r["name"]}: {r["type"]}')

# Reconciliacao faturas: CSV 160 vs DB 58
# Listar as 58 do DB e ver quais comp/contratos
print('\n=== FATURAS SEJUSC NO DB POR ANO E CONTRATO ===')
c.execute("""SELECT substr(competencia,4,4) as ano,
                    contrato_num,
                    COUNT(*) as n,
                    SUM(CAST(valor_bruto AS REAL)) as v
              FROM v_fatura_completa
              WHERE cliente LIKE '%SEJUSC%'
              GROUP BY ano, contrato_num ORDER BY ano, contrato_num""")
for r in c.fetchall():
    print(f'  {r["ano"]} ct {r["contrato_num"]:15s} {r["n"]:3d} fat R$ {r["v"]:,.2f}')

# Faturas DB com cadeia COMPLETA (cinco elos)
print('\n=== CADEIA DOS 58 ===')
c.execute("""SELECT cadeia_completude, COUNT(*) as n FROM v_fatura_completa
              WHERE cliente LIKE '%SEJUSC%' GROUP BY cadeia_completude""")
for r in c.fetchall():
    print(f'  {r["cadeia_completude"]}: {r["n"]}')

# Quais 58 sao exigiveis (Emitida)
print('\n=== SITUACAO DAS 58 ===')
c.execute("""SELECT situacao, COUNT(*) as n FROM v_fatura_completa
              WHERE cliente LIKE '%SEJUSC%' GROUP BY situacao""")
for r in c.fetchall():
    print(f'  {r["situacao"]}: {r["n"]}')

conn.close()
