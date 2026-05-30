"""
reconciliar_orfaos_reversos.py — Reconcilia devedores em profile.json sem faturas no DB.

Usa norm() para casar por similaridade com acentos+case. Para cada órfão reverso:
1. Identifica variantes no DB
2. Conta faturas e empenhos usando norm()
3. Popula val_exig / faturas_exigiveis se encontrar

Antes/depois gera relatório.
"""
from __future__ import annotations
import sys, json, sqlite3
from pathlib import Path
from decimal import Decimal
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from prodam_utils import norm, norm_variants, brl, fmt_brl, load_profiles

PROFILES_PATH = ROOT / "PRODAM_DOCS" / "profiles.json"
DB = sqlite3.connect(str(ROOT / "prodam.db"))

# Carrega profiles (inclui _metadata)
profiles_raw = json.load(open(PROFILES_PATH, encoding='utf-8'))
devedores = {k: v for k, v in profiles_raw.items() if not k.startswith("_")}

# Clientes distintos em spcf_faturas
clientes_db = [r[0] for r in DB.execute("SELECT DISTINCT cliente FROM spcf_faturas").fetchall() if r[0]]
# Clientes em spcf_empenhos
clientes_emp = [r[0] for r in DB.execute("SELECT DISTINCT cliente FROM spcf_empenhos").fetchall() if r[0]]

print(f"Profiles: {len(devedores)} devedores")
print(f"Clientes únicos em spcf_faturas: {len(clientes_db)}")
print(f"Clientes únicos em spcf_empenhos: {len(clientes_emp)}\n")

def buscar_matches(sigla: str, lista: list) -> list:
    """Retorna clientes da lista que casam com sigla via norm()."""
    variantes = norm_variants(sigla)
    return [c for c in lista if norm(c) in variantes or any(v in norm(c) for v in variantes)]

# Identifica órfãos reversos (sem faturas no DB) ANTES da correção
orfaos_antes = []
for sigla, pr in devedores.items():
    matches = buscar_matches(sigla, clientes_db)
    if not matches:
        orfaos_antes.append(sigla)

print(f"Órfãos reversos ANTES (sem matches via norm): {len(orfaos_antes)}")
print(orfaos_antes)

# Para cada devedor, tenta reconciliar
atualizados = []
for sigla, pr in devedores.items():
    matches_fat = buscar_matches(sigla, clientes_db)
    matches_emp = buscar_matches(sigla, clientes_emp)

    if not matches_fat and not matches_emp:
        continue

    # Se já tem valores corretos, pula (a menos que divergente)
    fat_exig_atual = pr.get("faturas_exigiveis") or 0
    val_exig_atual = brl(pr.get("val_exig"))

    # Conta faturas via clientes matched
    qtd_fat = 0
    val_fat = Decimal(0)
    if matches_fat:
        cond = " OR ".join("cliente = ?" for _ in matches_fat)
        r = DB.execute(f"SELECT COUNT(*), SUM(valor_bruto) FROM spcf_faturas WHERE {cond}", matches_fat).fetchone()
        qtd_fat = r[0] or 0
        val_fat = Decimal(str(r[1] or 0))

    # Conta empenhos via clientes matched
    qtd_emp = 0
    val_emp = Decimal(0)
    if matches_emp:
        cond = " OR ".join("cliente = ?" for _ in matches_emp)
        r = DB.execute(f"SELECT COUNT(*), SUM(valor) FROM spcf_empenhos WHERE {cond}", matches_emp).fetchone()
        qtd_emp = r[0] or 0
        val_emp = Decimal(str(r[1] or 0))

    # Detecta se precisa atualizar
    should_update = False
    motivo = []
    if fat_exig_atual == 0 and qtd_fat > 0:
        should_update = True
        motivo.append(f"faturas {fat_exig_atual}→{qtd_fat}")
    if val_exig_atual == 0 and val_fat > 0:
        should_update = True
        motivo.append(f"val_exig R$0→{fmt_brl(val_fat)}")

    if should_update:
        # Atualiza conservador (não sobrescreve valores não-zero)
        if fat_exig_atual == 0:
            pr["faturas_total"] = pr.get("faturas_total") or qtd_fat
            pr["faturas_exigiveis"] = qtd_fat
        if val_exig_atual == 0 and val_fat > 0:
            pr["val_exig"] = str(val_fat)
        pr["ultima_reconciliacao_orfao"] = "2026-04-14"
        pr["matches_db_fatura"] = matches_fat
        pr["matches_db_empenho"] = matches_emp
        atualizados.append({
            "sigla": sigla,
            "motivo": ", ".join(motivo),
            "qtd_fat_nova": qtd_fat,
            "qtd_emp_nova": qtd_emp,
            "val_fat_nova": str(val_fat),
            "matches_fat": matches_fat,
            "matches_emp": matches_emp,
        })
        print(f"✅ {sigla}: {', '.join(motivo)} | matches={matches_fat + matches_emp}")

# Salvar
if atualizados:
    json.dump(profiles_raw, open(PROFILES_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n✅ {len(atualizados)} devedores atualizados em profiles.json")

# Identifica órfãos reversos DEPOIS da correção
orfaos_depois = []
for sigla, pr in devedores.items():
    matches = buscar_matches(sigla, clientes_db)
    matches_emp = buscar_matches(sigla, clientes_emp)
    if not matches and not matches_emp:
        orfaos_depois.append(sigla)

print(f"\nÓrfãos reversos DEPOIS (sem matches em nenhum lugar): {len(orfaos_depois)}")
print(orfaos_depois)

# Salvar relatório
with open(ROOT / "RECONCILIACAO_ORFAOS_REVERSOS.json", "w", encoding="utf-8") as f:
    json.dump({
        "data": "2026-04-14",
        "orfaos_antes": orfaos_antes,
        "orfaos_depois": orfaos_depois,
        "atualizados": atualizados,
    }, f, ensure_ascii=False, indent=2)
print("\n✅ RECONCILIACAO_ORFAOS_REVERSOS.json gerado")
