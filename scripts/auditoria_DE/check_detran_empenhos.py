"""Verificar empenhos DETRAN nos contratos das faturas D-."""
import sys
import sqlite3
sys.stdout.reconfigure(encoding="utf-8")

DB = r"C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_ANALISE\prodam.db"
db = sqlite3.connect(DB)

for ct in ["22/2014", "25/2014", "27/2014"]:
    rows = db.execute(
        "SELECT numero, data_emissao, valor FROM spcf_empenhos "
        "WHERE cliente = 'DETRAN' AND contrato_ref = ? "
        "ORDER BY data_emissao DESC LIMIT 5", (ct,)
    ).fetchall()
    total = db.execute(
        "SELECT COUNT(*) FROM spcf_empenhos "
        "WHERE cliente = 'DETRAN' AND contrato_ref = ?", (ct,)
    ).fetchone()[0]
    print(f"CT {ct}: {total} empenhos total, top 5:")
    for r in rows:
        print(f"  {r[0]} | {r[1]} | R$ {r[2]}")

sem_ct = db.execute(
    "SELECT COUNT(*) FROM spcf_empenhos "
    "WHERE cliente = 'DETRAN' AND (contrato_ref IS NULL OR contrato_ref = '')"
).fetchone()[0]
print(f"\nEmpenhos DETRAN sem contrato_ref: {sem_ct}")

print("\nTop 5 empenhos DETRAN mais recentes (qualquer CT):")
tops = db.execute(
    "SELECT numero, contrato_ref, data_emissao FROM spcf_empenhos "
    "WHERE cliente = 'DETRAN' ORDER BY data_emissao DESC LIMIT 5"
).fetchall()
for t in tops:
    print(f"  {t[0]} CT {t[1]} | {t[2]}")

db.close()
