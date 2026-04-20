import subprocess, shutil, sqlite3, sys, datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
PRODAM = ROOT / "PRODAM_DOCS"
BUILD = PRODAM / "build_sqlite.py"
DB_SRC = PRODAM / "_ANALISE" / "prodam.db"
DB_DST = ROOT / "prodam.db"

print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] Rebuilding prodam.db...")
r = subprocess.run([sys.executable, str(BUILD)], cwd=str(PRODAM), capture_output=True, text=True)
if r.returncode != 0:
    print("ERRO no build:", r.stderr[-500:])
    sys.exit(1)

shutil.copy2(DB_SRC, DB_DST)
size = DB_DST.stat().st_size / 1024 / 1024
db = sqlite3.connect(str(DB_DST))
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
total = sum(db.execute(f"SELECT COUNT(*) FROM [{t[0]}]").fetchone()[0] for t in tables)
db.close()

print(f"OK: prodam.db atualizado ({size:.1f} MB, {total:,} registros, {len(tables)} tabelas)")
print(f"Copiado para: {DB_DST}")
