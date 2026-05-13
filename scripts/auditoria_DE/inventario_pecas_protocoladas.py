"""Inventariar quais devedores têm data_protocolo preenchida em profiles.json
e cruzar com peças disponíveis em _DOCUMENTOS_JURIDICOS/."""
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")
PROFILES = ROOT / "PRODAM_DOCS" / "profiles.json"
DOCS = ROOT / "PRODAM_DOCS" / "_DOCUMENTOS_JURIDICOS"

with open(PROFILES, encoding="utf-8") as f:
    profiles = json.load(f)

# Devedores com data_protocolo preenchida
protocoladas = []
for nome, dados in profiles.items():
    if nome.startswith("_"):
        continue
    if not isinstance(dados, dict):
        continue
    dp = dados.get("data_protocolo")
    if dp and dp != "" and dp != "null":
        protocoladas.append((nome, dp, dados.get("status"), dados.get("fase_atual")))

print(f"Devedores com data_protocolo preenchida: {len(protocoladas)}")
for nome, dp, status, fase in protocoladas:
    print(f"  {nome:<25} | protocolo: {dp} | status: {status} | fase: {fase}")

# Top devedores por fase F4-F5 (pré-execução / executando)
print("\nDevedores em F4 ou F5 (pre-execucao ou executando):")
f45 = []
for nome, dados in profiles.items():
    if nome.startswith("_"):
        continue
    if not isinstance(dados, dict):
        continue
    fase = dados.get("fase_atual")
    if fase in ("F4", "F5"):
        f45.append((nome, fase, dados.get("status"), dados.get("val_exig")))

for nome, fase, status, val in f45:
    print(f"  {nome:<25} | {fase} | {status} | val_exig: {val}")
