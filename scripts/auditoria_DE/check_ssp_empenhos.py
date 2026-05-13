"""Verificar empenhos SSP mais recentes e timeline."""
import sys
import sqlite3
sys.stdout.reconfigure(encoding="utf-8")

DB = r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_ANALISE\prodam.db"
db = sqlite3.connect(DB)

print("=== TOP 15 empenhos SSP por data_emissao DESC ===")
rows = db.execute("""SELECT numero, contrato_ref, data_emissao, valor
    FROM spcf_empenhos WHERE cliente = 'SSP'
    ORDER BY data_emissao DESC LIMIT 15""").fetchall()
for r in rows:
    print(f"  {r[0]:<15} CT {str(r[1]):<12} {str(r[2]):<15} R$ {r[3]}")

total = db.execute("SELECT COUNT(*) FROM spcf_empenhos WHERE cliente = 'SSP'").fetchone()[0]
print(f"\nTotal empenhos SSP no DB: {total}")

print("\n=== Contratos distintos com empenho SSP ===")
cts = db.execute("""SELECT DISTINCT contrato_ref FROM spcf_empenhos
    WHERE cliente = 'SSP' AND contrato_ref IS NOT NULL AND contrato_ref != ''
    ORDER BY contrato_ref""").fetchall()
for c in cts:
    print(f"  {c[0]}")

print("\n=== Empenhos SSP 2020+ (marcos recentes?) ===")
recentes = db.execute("""SELECT numero, contrato_ref, data_emissao, valor
    FROM spcf_empenhos WHERE cliente = 'SSP'
    AND data_emissao > '01/01/2020'
    ORDER BY data_emissao DESC""").fetchall()
if recentes:
    for r in recentes:
        print(f"  {r[0]:<15} CT {str(r[1]):<12} {str(r[2]):<15} R$ {r[3]}")
else:
    print("  NENHUM empenho SSP após 01/01/2020")

db.close()
