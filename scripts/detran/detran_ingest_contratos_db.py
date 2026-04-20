"""
detran_ingest_contratos_db.py — Ingere contratos DETRAN (PDF→JSON) no spcf_contratos.

Problema: 228 contratos DETRAN históricos existem em PDF mas apenas 1 no DB
(o atual C.3/2026). O scraper SPCF só pega vigentes.

Solução: ingerir os 12 contratos únicos (+ aditivos) identificados na pipeline
PDF→JSON em `DETRAN_CONSOLIDADO_JSON/01_CONTRATOS/`, criando registros em
spcf_contratos com id prefixado (PDF_DETRAN_) para não conflitar.

Dados agregados por contrato (usando o principal + metadados dos aditivos):
  - número, ano
  - índice correção (IGPM/IPCA/INDETERMINADO)
  - valor global estimado (soma valores_brl do principal)
  - número de aditivos
  - páginas total
  - status: ENCERRADO_ARQUIVADO (todos menos 3/2026) / VIGENTE (3/2026)

Esquema compatível com spcf_contratos:
  id (PDF_DETRAN_XXX_YYYY)
  numero (022/2014)
  cliente (DETRAN)
  dados_base (JSON: Cliente, N°, Status, Valor, Descrição, Fim da vigência, Origem)
  detalhes (JSON: referência aos JSONs-fonte)
  tramite_pdf (null — não há tramite web)
"""
from __future__ import annotations
import sys, json, sqlite3, re
from pathlib import Path
from datetime import date
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).parent.parent.parent

DB_PATH = ROOT / "prodam.db"
JSON_DIR = ROOT / "DETRAN_CONSOLIDADO_JSON" / "01_CONTRATOS"
INDICES_FILE = ROOT / "DETRAN_CONSOLIDADO_JSON" / "ANALISE_INDICES_CORRECAO.json"

# ============================================================
# Carrega análise de índices
# ============================================================
indices_data = json.load(open(INDICES_FILE, encoding='utf-8'))
indices_por_contrato = indices_data["por_contrato"]

# ============================================================
# Agrega JSONs por contrato
# ============================================================
agregado = defaultdict(lambda: {
    "arquivos": [], "paginas_total": 0, "valores": set(), "cnpjs": set(),
    "datas": set(), "reajustes_pct": [], "nes_refs": set(),
    "textos_clausulas_11": [], "principal_texto_preview": "",
})

for jf in JSON_DIR.glob("*.json"):
    try:
        d = json.loads(jf.read_text(encoding='utf-8'))
    except Exception:
        continue

    fn = d.get("filename", "")
    m = re.search(r"\b(\d{2,3})[.\s](\d{2,4})\b", fn)
    if not m:
        continue
    num, ano = m.groups()
    if len(ano) == 2:
        ano = "20" + ano
    ref = f"{int(num):03d}/{ano}"

    info = agregado[ref]
    info["arquivos"].append(fn)
    info["paginas_total"] += d.get("pdf_meta", {}).get("paginas", 0)

    campos = d.get("campos_estruturados") or {}
    if campos.get("valores_brl"):
        for v in campos["valores_brl"][:10]:
            info["valores"].add(v)
    if campos.get("cnpjs"):
        for c in campos["cnpjs"]:
            info["cnpjs"].add(c)
    if campos.get("datas_encontradas"):
        for dt in campos["datas_encontradas"]:
            info["datas"].add(dt)
    if campos.get("reajustes_pct"):
        info["reajustes_pct"].extend(campos["reajustes_pct"])
    if campos.get("nes_referenciadas"):
        for ne in campos["nes_referenciadas"]:
            info["nes_refs"].add(ne)
    if campos.get("clausula_11"):
        info["textos_clausulas_11"].append(campos["clausula_11"])
    # Preview do principal (se for CONTRATO_PRINCIPAL)
    if campos.get("tipo_doc") == "CONTRATO_PRINCIPAL" and not info["principal_texto_preview"]:
        info["principal_texto_preview"] = (d.get("texto_preview") or "")[:600]

print(f"Contratos únicos identificados: {len(agregado)}")

# Remove 'DESCONHECIDO' se existir
agregado.pop("DESCONHECIDO", None)

# ============================================================
# Conecta DB e verifica quais já existem
# ============================================================
conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

# Já existentes: C.3/2026 do SPCF + verificar outros
cur.execute("""
    SELECT json_extract(dados_base, '$.N° do contrato'), id
    FROM spcf_contratos
    WHERE UPPER(json_extract(dados_base, '$.Cliente')) LIKE '%DETRAN%'
""")
existentes = {row[0]: row[1] for row in cur.fetchall() if row[0]}
print(f"Já no DB: {existentes}")

# Normaliza existentes para formato 003/2026
existentes_normalizados = set()
for num in existentes.keys():
    m = re.search(r"(\d{1,3})/(\d{2,4})", num or "")
    if m:
        n, a = m.groups()
        if len(a) == 2: a = "20" + a
        existentes_normalizados.add(f"{int(n):03d}/{a}")

# ============================================================
# Prepara inserts
# ============================================================
inseridos = 0
atualizados = 0
pulados = 0

for ref, info in sorted(agregado.items()):
    if ref in existentes_normalizados:
        pulados += 1
        print(f"  [SKIP] {ref} já existe no DB")
        continue

    pk = f"PDF_DETRAN_{ref.replace('/','_')}"

    # Dados do índice
    idx_info = indices_por_contrato.get(ref, {})
    indice_dom = idx_info.get("indice_dominante", "INDETERMINADO")

    # Valor global: pega maior valor em `valores` (provável valor contratual global)
    valores_num = []
    for v in info["valores"]:
        try:
            vn = float(str(v).replace(".","").replace(",","."))
            if 10_000 <= vn <= 100_000_000:  # filtro sanity
                valores_num.append(vn)
        except: pass
    valor_max = max(valores_num) if valores_num else None

    # Datas
    datas_list = sorted(info["datas"])
    data_inicial = datas_list[0] if datas_list else None
    data_final = datas_list[-1] if datas_list else None

    # CNPJs
    cnpjs_list = sorted(info["cnpjs"])

    # Status
    status = "ENCERRADO_ARQUIVADO"  # Assumido para todos menos vigentes

    # Descrição baseada no texto do principal
    desc = info["principal_texto_preview"][:300] or f"Contrato DETRAN {ref} - {len(info['arquivos'])} documentos"

    # dados_base compatível com schema SPCF
    dados_base = {
        "Cliente": "DETRAN",
        "N° do contrato": ref,
        "Valor(R$)": f"{valor_max:,.2f}" if valor_max else "",
        "Tramitando": "0 dia",
        "Fim da vigência": data_final,
        "Descrição": desc,
        "Status": status,
        "Origem": "PDF_INGESTAO_14_04_2026",
        "Arquivos_fonte": len(info["arquivos"]),
        "Paginas_total": info["paginas_total"],
        "Indice_correcao": indice_dom,
        "Reajustes_aplicados": list(info["reajustes_pct"]),
        "CNPJs_detectados": cnpjs_list,
        "NEs_referenciadas": list(info["nes_refs"])[:30],
    }

    detalhes = {
        "url": None,
        "title": f"Contrato DETRAN {ref} (reconstituído de PDFs)",
        "arquivos": info["arquivos"],
        "fontes_json": f"DETRAN_CONSOLIDADO_JSON/01_CONTRATOS/ ({len(info['arquivos'])} JSONs)",
        "num_aditivos": sum(1 for f in info["arquivos"] if re.search(r"TA|aditivo", f, re.IGNORECASE)),
        "tem_principal": any(re.search(r"^(\d{2,3}\.\d{2,4}|Contrato \d|Comprimido)", f) for f in info["arquivos"]),
        "num_clausulas_11": len(info["textos_clausulas_11"]),
    }

    try:
        cur.execute("""
            INSERT OR REPLACE INTO spcf_contratos (id, numero, cliente, dados_base, detalhes, tem_tramite_pdf)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            pk,
            ref,
            "DETRAN",
            json.dumps(dados_base, ensure_ascii=False, default=str),
            json.dumps(detalhes, ensure_ascii=False, default=str),
            0,
        ))
        inseridos += 1
        print(f"  [INS] {pk}: {ref} | {indice_dom} | R$ {valor_max or 0:,.2f} | {len(info['arquivos'])} docs")
    except Exception as e:
        print(f"  [ERR] {pk}: {e}")

conn.commit()

# Stats finais
total_detran_db = cur.execute("""
    SELECT COUNT(*) FROM spcf_contratos
    WHERE UPPER(json_extract(dados_base, '$.Cliente')) LIKE '%DETRAN%'
""").fetchone()[0]

print(f"\n{'='*60}")
print(f"Inseridos: {inseridos}")
print(f"Já existentes (skip): {pulados}")
print(f"Total contratos DETRAN no DB agora: {total_detran_db}")
print(f"{'='*60}")

conn.close()
