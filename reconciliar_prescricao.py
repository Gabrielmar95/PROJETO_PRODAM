import json, csv
from datetime import datetime, date
from pathlib import Path
prof = json.loads(Path("PRODAM_DOCS/profiles.json").read_text(encoding="utf-8"))
today = date.today()
ssot = {}
for sigla, d in prof.items():
    if sigla.startswith("_"):          # pula _metadata
        continue
    dpp = d.get("data_prescricao_proxima")
    dias = None
    if dpp:
        try:
            dias = (datetime.strptime(dpp, "%Y-%m-%d").date() - today).days
        except (ValueError, TypeError):
            dias = None
    ssot[sigla] = {"dpp": dpp, "dias": dias,
                   "fat_presc": int(d.get("faturas_prescritas", 0) or 0),
                   "ve": float(d.get("val_exig", 0) or 0)}
csv_dplus = {}
p = Path("profiles_resumo.csv")
if p.exists():
    for r in csv.DictReader(p.open(encoding="utf-8-sig")):
        v = (r.get("d_plus") or "").strip()
        csv_dplus[r["sigla"]] = int(v) if v.lstrip("-").isdigit() else None
print(f"HOJE = {today}  |  devedores no SSOT = {len(ssot)}\n")
print(f"{'SIGLA':<16}{'SSOT dpp':<12}{'dias(vivo)':>11}{'CSV d_plus':>12}{'fat_presc':>10}  FLAG")
print("-"*80)
for sig in sorted(ssot, key=lambda s: (ssot[s]['dias'] is None, ssot[s]['dias'] or 0)):
    s = ssot[sig]; cd = csv_dplus.get(sig); sd = s['dias']
    flag = ""
    if sd is not None and cd is not None and ((sd < 0) != (cd < 0) or abs(sd - cd) > 7):
        flag = "<<< DIVERGE SSOT x CSV"
    print(f"{sig:<16}{(s['dpp'] or '(sem data)'):<12}"
          f"{('' if sd is None else sd):>11}{('' if cd is None else cd):>12}"
          f"{s['fat_presc']:>10}  {flag}")
risco = sorted([(k, v) for k, v in ssot.items() if v['dias'] is not None and v['dias'] <= 90],
               key=lambda x: x[1]['dias'])
print("\n=== SSOT ao vivo: prescricao em <=90 dias (inclui ja vencidas) ===")
for sig, s in risco:
    estado = "JA VENCIDA" if s['dias'] < 0 else f"{s['dias']}d"
    print(f"  {sig}: {s['dpp']}  ({estado})  ve=R$ {s['ve']:,.2f}")
print("  (nenhum)" if not risco else "")
