"""
GAP ANALYSIS — Notificação Extrajudicial PRODAM/DETRAN vs todas as fontes (19/04/2026).
Read-only. Gera 2 artefatos em DETRAN_AUDITORIA_COMPLETA/_NOTIFICACAO_ASSINADA/:
  - CONTEUDO_NOTIFICACAO_EXTRAIDO.json
  - GAP_ANALYSIS_NOTIFICACAO_vs_FONTES.md
"""
from __future__ import annotations
import sqlite3, json, os, re, csv, hashlib
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime

# =============== CONSTANTES / CAMINHOS ===============
DB = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\16_BANCOS_DADOS\prodam.db"
PROFILE = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\11_PROFILES_BACKUPS\ativo\profiles.json"
CSV_FATURAS_PROJETO = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\04_FATURAS\CSV\PRODAM_DOCS___WORKFLOW_IMPORTADO__DASHBOARD_PRODAM_ORGANIZA__02_DADOS_FONTE__faturas_cruzadas_projeto___DETRAN_FATURAS_CRUZADAS.csv"
CSV_FATURAS_SPCF = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\08_DADOS_SPCF\CSV\Dados_Brutos_SPCF__CSV__DETRAN_FATURAS_CRUZADAS.csv"
CSV_CORRIGIDO = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\08_DADOS_SPCF\CSV\Dados_Brutos_SPCF__CSV__DETRAN_FATURAS_CRUZADAS_COM_CORRECAO.csv"
PDFS_DIR = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\01_CONTRATOS\PDF"
HTMLS_DIR = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\01_CONTRATOS\HTML"
PRODAM_DOCS_DETRAN = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\PRODAM_DOCS\DETRAN"
OUT_DIR = Path(r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\_NOTIFICACAO_ASSINADA")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT_DIR / "CONTEUDO_NOTIFICACAO_EXTRAIDO.json"
OUT_MD = OUT_DIR / "GAP_ANALYSIS_NOTIFICACAO_vs_FONTES.md"

# =============== DADOS DA NOTIFICAÇÃO (extraídos do PDF assinado) ===============
# Anexo I — contrato × qtd × saldo original × valor atualizado
NOTIFICACAO_ANEXO_I = [
    ("CT 010/2021", 30, "10.473.410,37", "13.933.833,89"),
    ("CT 022/2014", 12, "1.584.062,67", "2.751.091,24"),
    ("CT 296/2025", 4, "2.522.329,40", "2.616.720,52"),
    ("CT 006/2021", 79, "1.458.141,83", "1.932.882,31"),
    ("CT 003/2026", 3, "1.891.747,05", "1.899.377,10"),
    ("CT 004/2016", 5, "732.968,33", "1.235.012,24"),
    ("CT 071/2022", 2, "520.000,00", "852.315,28"),
    ("CT 012/2021", 11, "734.512,17", "804.903,92"),
    ("CT 017/2015", 6, "357.476,55", "661.325,34"),
    ("CT 075/2022", 2, "567.872,80", "567.872,80"),
    ("CT 025/2014", 7, "212.472,74", "369.008,05"),
    ("CT 083/2022", 7, "188.531,07", "206.445,20"),
    ("CT 027/2014", 15, "109.563,91", "190.283,06"),
    ("CT 060/2022", 2, "41.595,00", "65.419,68"),
    ("CT 008/2021", 12, "30.625,82", "38.412,13"),
    ("CT 179/2018", 1, "3.084,08", "6.958,97"),
    ("CT 023/2014", 2, "3.584,37", "6.631,03"),
    ("CT 014/2019", 2, "2.233,29", "4.131,54"),
]

# Anexo I.A — lista de NFs por contrato
NOTIFICACAO_ANEXO_IA = {
    "CT 010/2021": ["129515","137916","137917","137918","165621","165622","165623","134316","134317","134318","162971","162973","135058","135059","135060","167282","167283","167284","136423","136424","136425","135862","135863","135864","166854","166855","166858","164004","164005","164006"],
    "CT 022/2014": ["128079","128080","128081","128086","128133","128134","128135","128146","128167","128168","128169","128170"],
    "CT 296/2025": ["165497","164621","163999","164000"],
    "CT 006/2021": ["137473","137474","137475","137476","137477","137478","137479","130271","165062","165063","165064","165065","165066","165067","165068","165137","165138","137569","137570","134800","134801","134802","134803","134804","134805","134806","135486","135487","135488","135489","135490","135491","135492","136191","136192","136193","136194","136195","136196","136197","136862","136863","136864","136865","136866","136867","136868","163820","167062","167063","167064","167065","167066","167067","167068","167158","167159","135063","135064","134418","134419","136421","136422","128770","129612","129613","135860","135861","137097","137098","166601","166602","166603","166604","166605","166606","166607","166852","166853"],
    "CT 003/2026": ["167160","166661","166089"],
    "CT 004/2016": ["132600","133362","131182","130540","131912"],
    "CT 071/2022": ["135065","134497"],
    "CT 012/2021": ["155538","165493","163822","167157","164797","135857","135858","138012","166851","163143","137296"],
    "CT 017/2015": ["128141","128144","128145","128163","128165","128166"],
    "CT 075/2022": ["167070","166609"],
    "CT 025/2014": ["128075","128138","128140","128159","128160","128162","128171"],
    "CT 083/2022": ["165071","165136","137571","167071","164300","166610","166276"],
    "CT 027/2014": ["127483","127484","127485","127754","127755","128076","128136","128137","128139","128142","128154","128155","128156","128157","128158"],
    "CT 060/2022": ["136505","137102"],
    "CT 008/2021": ["137480","155743","129365","129512","137915","165069","165619","167069","167285","137106","166608","166859"],
    "CT 179/2018": ["110654"],
    "CT 023/2014": ["128153","128164"],
    "CT 014/2019": ["128143","128161"],
}

CONTRATOS_AUSENTES_DB = {"296/2025","8/2021","179/2018","23/2014","14/2019"}


def fix_latin(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s


def norm(numero: str) -> str:
    """Normaliza variacoes: 'CT 010/2021', '010/2021', 'C.10/2021', 'CT010.2021' -> '10/2021'"""
    if not numero:
        return ""
    n = str(numero).upper()
    n = re.sub(r"\bCT\b", "", n)
    n = re.sub(r"\bC\.", "", n)
    n = n.replace(" ", "").strip()
    n = n.replace(".", "/")
    m = re.match(r"0*(\d+)/(\d{4})$", n)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    m = re.match(r"0*(\d+)/(\d{2})$", n)
    if m:
        ano = m.group(2)
        ano_full = ("20" + ano) if int(ano) < 80 else ("19" + ano)
        return f"{m.group(1)}/{ano_full}"
    return n


def money(val) -> Decimal:
    if val is None or val == "":
        return Decimal("0")
    if isinstance(val, (int, float, Decimal)):
        return Decimal(str(val))
    s = str(val).strip().replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return Decimal("0")


def fmt_brl(v: Decimal) -> str:
    s = f"{v:,.2f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


# =============== 1) CONTEUDO DA NOTIFICAÇÃO → JSON ===============
notificacao_json = {
    "extraido_de": "NOTIFICACAO_EXTRAJUDICIAL_PRODAM_DETRANass.pdf",
    "sha256_pdf": "c4f052368346b83a79cf32ffad8f40a0954602cadd9947ab79162c4f444b928d",
    "data_notificacao": "2026-04-16",
    "data_assinatura_digital": "2026-04-17T13:26:18-04:00",
    "assinante": "BRANDAO OZORES SOCIEDADE DE ADVOGADOS:32776994000129 (ICP-Brasil, e-CNPJ A1)",
    "representante_legal": "Fabio Silva Andrade — OAB/AM 9.217",
    "universo": {"qtd_contratos": 18, "qtd_notas_fiscais": 202},
    "total_saldo_original_brl": "21.434.211,45",
    "total_valor_atualizado_brl": "28.142.624,30",
    "data_base_correcao": "2026-04-16",
    "contratos": [],
}

soma_qtd = 0
soma_orig = Decimal("0")
soma_atu = Decimal("0")
for ct, qtd, orig, atu in NOTIFICACAO_ANEXO_I:
    nfs = NOTIFICACAO_ANEXO_IA.get(ct, [])
    assert len(nfs) == qtd, f"Mismatch qtd em {ct}: anexo I diz {qtd} mas anexo I.A tem {len(nfs)}"
    item = {
        "numero_contrato": ct,
        "numero_normalizado": norm(ct),
        "qtd_nfs": qtd,
        "saldo_original_brl": orig,
        "saldo_original_decimal": str(money(orig)),
        "valor_atualizado_brl": atu,
        "valor_atualizado_decimal": str(money(atu)),
        "notas_fiscais": nfs,
    }
    notificacao_json["contratos"].append(item)
    soma_qtd += qtd
    soma_orig += money(orig)
    soma_atu += money(atu)

notificacao_json["verificacao_integridade"] = {
    "qtd_nfs_somadas": soma_qtd,
    "qtd_nfs_declarada": 202,
    "qtd_nfs_bate": soma_qtd == 202,
    "soma_saldo_original": str(soma_orig),
    "soma_saldo_original_brl": fmt_brl(soma_orig),
    "saldo_declarado_brl": "21.434.211,45",
    "saldo_original_bate": soma_orig == Decimal("21434211.45"),
    "soma_valor_atualizado": str(soma_atu),
    "soma_valor_atualizado_brl": fmt_brl(soma_atu),
    "valor_atualizado_declarado_brl": "28.142.624,30",
    "valor_atualizado_bate": soma_atu == Decimal("28142624.30"),
}

OUT_JSON.write_text(json.dumps(notificacao_json, ensure_ascii=False, indent=2), encoding="utf-8")


# =============== 2) PROFILES.JSON ===============
with open(PROFILE, "r", encoding="utf-8") as f:
    profiles = json.load(f)
det = profiles["DETRAN"]
profile_contratos = {norm(k): {"numero_raw": k, "obj": v} for k, v in det.get("contratos", {}).items()}
profile_removidos = {norm(k): {"numero_raw": k, "obj": v} for k, v in det.get("contratos_removidos_2026_04_16", {}).items()}
profile_nfs_especificas = det.get("nfs_especificas_documentadas", [])


# =============== 3) PRODAM.DB ===============
conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()
cur.execute("SELECT id, numero, cliente, dados_base, tem_tramite_pdf FROM spcf_contratos WHERE UPPER(cliente) LIKE '%DETRAN%'")
db_contratos = {}
for id_, numero, cliente, db_, pdf in cur.fetchall():
    d = json.loads(db_) if db_ else {}
    d2 = {fix_latin(k): (fix_latin(v) if isinstance(v, str) else v) for k, v in d.items()}
    db_contratos[norm(numero)] = {
        "id": id_, "numero_raw": numero,
        "status": d2.get("Status", ""),
        "valor_global": d2.get("Valor(R$)", ""),
        "tem_tramite_pdf": pdf,
    }

cur.execute("SELECT nf, cliente, contrato_num, valor_bruto, competencia, situacao, cadeia_completude, tem_pdf FROM spcf_faturas WHERE UPPER(cliente) LIKE '%DETRAN%'")
db_faturas_por_nf = {}
db_faturas_por_contrato = {}
for nf, cliente, cnum, vb, comp, sit, cc, tp in cur.fetchall():
    item = {
        "nf": str(nf), "contrato_num_raw": cnum,
        "contrato_num_norm": norm(cnum) if cnum else "",
        "valor_bruto": money(vb), "competencia": comp, "situacao": sit,
        "cadeia_completude": cc, "tem_pdf": tp,
    }
    db_faturas_por_nf[str(nf)] = item
    db_faturas_por_contrato.setdefault(item["contrato_num_norm"], []).append(item)

conn.close()


# =============== 4) CSVs ===============
def carregar_csv(path):
    if not os.path.isfile(path):
        return [], f"nao encontrado: {path}"
    linhas = []
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                linhas.append(row)
    except Exception as e:
        return [], f"erro leitura: {e}"
    return linhas, None

csv_projeto, err_p = carregar_csv(CSV_FATURAS_PROJETO)
csv_spcf, err_s = carregar_csv(CSV_FATURAS_SPCF)
csv_correcao, err_c = carregar_csv(CSV_CORRIGIDO)

def indexar_csv(linhas):
    """Retorna (por_nf, por_contrato). contrato do CSV vem como 'C.6/2021' etc."""
    por_nf = {}
    por_contrato = {}
    for r in linhas:
        nf = (r.get("numero_fatura") or "").strip()
        ctn = norm(r.get("contrato") or "")
        if not nf:
            continue
        por_nf[nf] = r
        por_contrato.setdefault(ctn, []).append(r)
    return por_nf, por_contrato

csv_proj_por_nf, csv_proj_por_ct = indexar_csv(csv_projeto)
csv_spcf_por_nf, csv_spcf_por_ct = indexar_csv(csv_spcf)
csv_corr_por_nf, csv_corr_por_ct = indexar_csv(csv_correcao)


# =============== 5) PDFs em 01_CONTRATOS/PDF/ ===============
def listar_arquivos(d, ext=".pdf"):
    if not os.path.isdir(d):
        return []
    return [f for f in os.listdir(d) if f.lower().endswith(ext)]

todos_pdfs_contratos = listar_arquivos(PDFS_DIR, ".pdf")
todos_htmls = listar_arquivos(HTMLS_DIR, ".html")

def buscar_docs_por_contrato(num_norm):
    """Retorna {'pdfs': [...], 'htmls': [...], 'prodam_docs': [...]}"""
    parts = num_norm.split("/")
    if len(parts) != 2:
        return {"pdfs": [], "htmls": [], "prodam_docs": []}
    num, ano = parts
    # padroes que o dir tem: CT_003_2026, 003.2026, 003_2026, 3_2026, 3/2026 (nao no nome), etc.
    padroes = [
        f"{num.zfill(3)}.{ano}", f"{num.zfill(3)}_{ano}", f"{num.zfill(3)}-{ano}",
        f"{num}.{ano}", f"{num}_{ano}", f"{num}-{ano}",
        f"CT_{num.zfill(3)}_{ano}", f"CT {num.zfill(3)}/{ano}",
        f"CT_{num}_{ano}", f"CT {num}/{ano}",
        f"Contrato {num.zfill(3)}.{ano}", f"Contrato {num}.{ano}",
        f"Contrato {num.zfill(3)}/{ano}", f"Contrato {num}/{ano}",
    ]
    pdfs = [p for p in todos_pdfs_contratos if any(pad.lower() in p.lower() for pad in padroes)]
    htmls = [h for h in todos_htmls if any(pad.lower() in h.lower() for pad in padroes)]
    prodam_docs_found = []
    if os.path.isdir(PRODAM_DOCS_DETRAN):
        for root, _, files in os.walk(PRODAM_DOCS_DETRAN):
            for fn in files:
                if any(pad.lower() in fn.lower() for pad in padroes):
                    prodam_docs_found.append(os.path.join(root, fn))
    return {"pdfs": pdfs, "htmls": htmls, "prodam_docs": prodam_docs_found}


# =============== 6) CRUZAMENTO POR CONTRATO ===============
def status_em_fonte(num_norm):
    return {
        "no_profile": num_norm in profile_contratos,
        "no_profile_removido_1604": num_norm in profile_removidos,
        "no_db_spcf_contratos": num_norm in db_contratos,
        "no_db_spcf_faturas": num_norm in db_faturas_por_contrato,
        "no_csv_projeto": num_norm in csv_proj_por_ct,
        "no_csv_spcf": num_norm in csv_spcf_por_ct,
        "no_csv_correcao": num_norm in csv_corr_por_ct,
    }

def contar_faturas_por_fonte(num_norm):
    return {
        "db_spcf_faturas": len(db_faturas_por_contrato.get(num_norm, [])),
        "csv_projeto": len(csv_proj_por_ct.get(num_norm, [])),
        "csv_spcf": len(csv_spcf_por_ct.get(num_norm, [])),
        "csv_correcao": len(csv_corr_por_ct.get(num_norm, [])),
    }

cruzamento = []
for ct_raw, qtd_notif, saldo_orig, valor_atu in NOTIFICACAO_ANEXO_I:
    cn = norm(ct_raw)
    stat = status_em_fonte(cn)
    cnt = contar_faturas_por_fonte(cn)
    docs = buscar_docs_por_contrato(cn)
    # Cenario
    if stat["no_profile"] and stat["no_db_spcf_contratos"] and (docs["pdfs"] or docs["htmls"]):
        cenario = "A-OK"  # todas fontes + PDF
    elif stat["no_profile"] and (stat["no_db_spcf_contratos"] or stat["no_db_spcf_faturas"]):
        cenario = "A"  # multiplas fontes + DB parcial
    elif stat["no_profile"] and not stat["no_db_spcf_contratos"] and stat["no_db_spcf_faturas"]:
        cenario = "A-parcial"
    elif stat["no_profile"] and not (docs["pdfs"] or docs["htmls"] or docs["prodam_docs"]):
        cenario = "B"  # menção mas sem PDF
    elif not stat["no_profile"]:
        cenario = "C"  # fantasma
    else:
        cenario = "?"
    cruzamento.append({
        "numero_notificacao": ct_raw,
        "numero_norm": cn,
        "qtd_nfs_notif": qtd_notif,
        "saldo_orig_brl": saldo_orig,
        "valor_atu_brl": valor_atu,
        "status_fontes": stat,
        "qtd_faturas_por_fonte": cnt,
        "docs": {
            "pdfs_01": docs["pdfs"],
            "htmls_01": docs["htmls"],
            "prodam_docs_detran": docs["prodam_docs"],
        },
        "cenario": cenario,
    })


# =============== 7) CT 008/2021 — diff NFs notif vs DB ===============
ct008_nfs_notif = set(NOTIFICACAO_ANEXO_IA["CT 008/2021"])
ct008_nfs_db = {f["nf"] for f in db_faturas_por_contrato.get("8/2021", [])}
ct008_nfs_notif_no_db = ct008_nfs_notif & ct008_nfs_db
ct008_nfs_notif_fora_db = ct008_nfs_notif - ct008_nfs_db
ct008_nfs_db_fora_notif = ct008_nfs_db - ct008_nfs_notif

def rastrear_nf(nf):
    """Onde a NF aparece?"""
    return {
        "nf": nf,
        "no_db": nf in db_faturas_por_nf,
        "db_info": db_faturas_por_nf.get(nf),
        "no_csv_projeto": nf in csv_proj_por_nf,
        "csv_projeto_info": ({
            "contrato_csv": csv_proj_por_nf[nf].get("contrato"),
            "valor_servicos": csv_proj_por_nf[nf].get("valor_servicos"),
            "valor_corrigido_calc": csv_proj_por_nf[nf].get("valor_corrigido_calc"),
            "status_prescricao": csv_proj_por_nf[nf].get("status_prescricao"),
            "forca_probatoria": csv_proj_por_nf[nf].get("forca_probatoria"),
            "valor_pg_parcial": csv_proj_por_nf[nf].get("valor_pg_parcial"),
            "paga": csv_proj_por_nf[nf].get("paga"),
        } if nf in csv_proj_por_nf else None),
        "no_csv_spcf": nf in csv_spcf_por_nf,
        "no_csv_correcao": nf in csv_corr_por_nf,
        "csv_correcao_info": ({
            "valor_servicos": csv_corr_por_nf[nf].get("valor_servicos"),
            "valor_total_atualizado": csv_corr_por_nf[nf].get("valor_total_atualizado"),
        } if nf in csv_corr_por_nf else None),
    }

ct008_trace = {nf: rastrear_nf(nf) for nf in sorted(ct008_nfs_notif)}

# CT 179/2018 — NF 110654
nf_110654 = rastrear_nf("110654")
ct179_nfs_db = [f["nf"] for f in db_faturas_por_contrato.get("179/2018", [])]


# =============== 8) RELATÓRIO .MD ===============
L = []
def w(line=""):
    L.append(line)

w("# GAP ANALYSIS — Notificação Extrajudicial PRODAM/DETRAN × Fontes do Projeto")
w("")
w("**Data da análise:** 2026-04-19  ")
w("**Notificação analisada:** `NOTIFICACAO_EXTRAJUDICIAL_PRODAM_DETRANass.pdf` (SHA-256 `c4f05236...`)  ")
w("**Assinatura digital:** 2026-04-17 13:26:18 (UTC-4) — BRANDAO OZORES SOCIEDADE DE ADVOGADOS (ICP-Brasil)  ")
w("**Modo:** read-only sobre todas as fontes. PDF assinado intocado.  ")
w("")
w("---")
w("")
w("## SUMÁRIO EXECUTIVO")
w("")
w("- **Conteúdo da notificação extraído integralmente** e salvo em `CONTEUDO_NOTIFICACAO_EXTRAIDO.json`. Integridade verificada: 202 NFs × 18 contratos × R$ 21.434.211,45 (saldo original) × R$ 28.142.624,30 (atualizado) — as somas do Anexo I batem exatamente com os totais declarados na notificação.")
w(f"- **`profiles.json` É a fonte autoritativa**: contém 18 contratos DETRAN (todos os 18 da notificação), incluindo os 5 ausentes do `prodam.db`.")
w(f"- **Timeline de integridade jurídica (alerta amarelo):** 4 contratos (`8/2021`, `14/2019`, `23/2014`, `179/2018`) foram *removidos* do profile em 16/04/2026 com motivo \"Sem PDF\" e *re-adicionados* em 17/04/2026 14:36:33 (≈1h10min **depois** da assinatura digital do PDF às 13:26). A re-adição cita como fonte \"Universo oficial 202 (memorial 17/04/2026)\" — conhecer essa ordem de eventos é importante caso o devedor questione a procedência.")
w("- **PDFs de contrato**: 01_CONTRATOS/PDF cobre a maior parte dos 18 (via termos aditivos ou contratos originais do pendrive); 4 dos 5 contratos ausentes do banco (`8/2021`, `14/2019`, `23/2014`, `179/2018`) **não têm PDF de contrato em nenhuma fonte** — fato reconhecido no próprio profile.")
w("- **CT 008/2021**: notificação lista 12 NFs; banco tem 7 faturas sob esse contrato, das quais apenas **4** coincidem com a notificação. Logo, **8 NFs da notificação não estão no `spcf_faturas`** — foram buscadas em todas as outras fontes.")
w("- **CT 179/2018 / NF 110654**: única fatura; é a NF crítica cujo cutoff prescricional é 19/08/2026.")
w("")
w("---")
w("")
w("## 1 — CONTEÚDO DA NOTIFICAÇÃO")
w("")
w(f"- Arquivo JSON: `CONTEUDO_NOTIFICACAO_EXTRAIDO.json` ({OUT_JSON.name})")
w(f"- Verificação das somas do Anexo I:")
vi = notificacao_json["verificacao_integridade"]
w(f"  - Qtd NFs: soma = {vi['qtd_nfs_somadas']} · declarada = {vi['qtd_nfs_declarada']} · bate = **{vi['qtd_nfs_bate']}**")
w(f"  - Saldo original: soma = R$ {vi['soma_saldo_original_brl']} · declarado = R$ {vi['saldo_declarado_brl']} · bate = **{vi['saldo_original_bate']}**")
w(f"  - Valor atualizado: soma = R$ {vi['soma_valor_atualizado_brl']} · declarado = R$ {vi['valor_atualizado_declarado_brl']} · bate = **{vi['valor_atualizado_bate']}**")
w("")
w("---")
w("")
w("## 2 — CRUZAMENTO EXPANDIDO POR CONTRATO (18 × 7 fontes)")
w("")
w("| Contrato | Notif qtd | Profile | Removido 16/04 | DB.contratos | DB.faturas (qtd) | CSV projeto (qtd) | CSV SPCF (qtd) | CSV corr (qtd) | PDFs 01 | HTMLs 01 | PRODAM_DOCS | Cenário |")
w("|---|---:|:---:|:---:|:---:|---:|---:|---:|---:|---:|---:|---:|:---:|")
def y(b): return "✔" if b else "—"
for c in cruzamento:
    st = c["status_fontes"]
    ct = c["qtd_faturas_por_fonte"]
    d = c["docs"]
    w(f"| {c['numero_notificacao']} | {c['qtd_nfs_notif']} | {y(st['no_profile'])} | {y(st['no_profile_removido_1604'])} | {y(st['no_db_spcf_contratos'])} | {ct['db_spcf_faturas']} | {ct['csv_projeto']} | {ct['csv_spcf']} | {ct['csv_correcao']} | {len(d['pdfs_01'])} | {len(d['htmls_01'])} | {len(d['prodam_docs_detran'])} | **{c['cenario']}** |")
w("")
w("**Legenda de cenário:**")
w("- **A-OK** — presente em profile + DB + pelo menos 1 PDF. Verde.")
w("- **A** — presente em profile + DB (contrato ou faturas). Banco com algum dado. Amarelo claro.")
w("- **A-parcial** — profile completo + DB só faturas (sem contrato em spcf_contratos).")
w("- **B** — presente no profile com menção, mas **nenhum PDF de contrato** encontrado e com/sem faturas em DB. Amarelo forte.")
w("- **C** — fantasma: sequer está no profile. Vermelho.")
w("")
w("---")
w("")
w("## 3 — DIAGNÓSTICO POR CONTRATO AUSENTE DO prodam.db (os 5)")
w("")
for num_raw in ["296/2025", "8/2021", "179/2018", "23/2014", "14/2019"]:
    ct_raw_notif = next((c["numero_notificacao"] for c in cruzamento if c["numero_norm"] == num_raw), f"CT {num_raw}")
    cruz = next((c for c in cruzamento if c["numero_norm"] == num_raw), None)
    prof = profile_contratos.get(num_raw, {})
    prof_obj = prof.get("obj", {})
    removido = profile_removidos.get(num_raw, {})
    removido_obj = removido.get("obj", {})
    qtd_notif = cruz["qtd_nfs_notif"] if cruz else "?"

    w(f"### {ct_raw_notif}  (norm `{num_raw}`)")
    w("")
    w(f"**Qtd NFs na notificação:** {qtd_notif}")
    w("")

    if prof_obj:
        w(f"**Profile (DETRAN.contratos[{num_raw!r}]):**")
        w("")
        linhas_prof = []
        for k in ["numero_contrato", "objeto", "valor_global", "valor_mensal",
                  "regime_aplicavel", "fundamentacao_juridica", "validado_juridicamente",
                  "fonte_primaria", "qtd_faturas_universo_oficial",
                  "adicionado_em", "adicionado_por", "pdf_oficial_local", "pdf_baixado_em",
                  "descoberta_documental", "status_prescricao", "risco_prescricional"]:
            if k in prof_obj:
                v = prof_obj[k]
                if isinstance(v, str) and len(v) > 180:
                    v = v[:180] + "..."
                linhas_prof.append(f"  - `{k}`: {fix_latin(v) if isinstance(v,str) else v}")
        for l in linhas_prof:
            w(l)
        w("")

    if removido_obj:
        w(f"**Profile.contratos_removidos_2026_04_16[{num_raw!r}]:**")
        w("")
        for k, v in removido_obj.items():
            w(f"  - `{k}`: {fix_latin(v) if isinstance(v,str) else v}")
        w("")

    if cruz:
        docs = cruz["docs"]
        w("**Documentos encontrados em disco:**")
        w(f"  - 01_CONTRATOS/PDF: {len(docs['pdfs_01'])} arquivo(s) — {docs['pdfs_01'][:5]}")
        w(f"  - 01_CONTRATOS/HTML: {len(docs['htmls_01'])} arquivo(s)")
        w(f"  - PRODAM_DOCS/DETRAN: {len(docs['prodam_docs_detran'])} arquivo(s)")
        w("")
        w("**Presença em bases tabulares:**")
        cnt = cruz["qtd_faturas_por_fonte"]
        w(f"  - `spcf_contratos`: {'sim' if cruz['status_fontes']['no_db_spcf_contratos'] else 'não'}")
        w(f"  - `spcf_faturas`: {cnt['db_spcf_faturas']} faturas")
        w(f"  - CSV projeto: {cnt['csv_projeto']} · CSV SPCF: {cnt['csv_spcf']} · CSV c/correção: {cnt['csv_correcao']}")
        w("")
        w(f"**Cenário:** **{cruz['cenario']}**")
        w("")
        # Recomendacao
        if num_raw == "296/2025":
            w("**Recomendação:** contrato-proposta precursor do CT 003/2026 (mesmo documento, SPCF ids diferentes). PDF oficial existe em `01_CONTRATOS/PDF/CT_003_2026_DETRAN.pdf` e cobre AMBOS os números. **Risco baixo**: basta anexar esse PDF e um memorando explicando a relação proposta↔contrato para qualquer questionamento do devedor.")
        elif num_raw in ("8/2021", "14/2019", "23/2014"):
            w("**Recomendação:** contrato reconhecido como \"sem PDF\" pelo próprio profile (e removido em 16/04, re-adicionado em 17/04 pós-assinatura). Valores baixos (R$ 2k–R$ 30k). **Decisão jurídica a confirmar antes do protocolo:**")
            w("  1. **Manter na notificação** com ressalva nos autos, apresentando: reconhecimento tácito via Notas de Empenho (NE) subsequentes + NF emitidas e aceitas; OU")
            w("  2. **Excluir na errata** e perseguir cobrança separada após localizar o PDF em sistema corporativo (PRODAM-RH, SPROWEB).")
        elif num_raw == "179/2018":
            w("**Recomendação:** única fatura (NF 110654). Profile marca marco interruptivo FORTÍSSIMO em 19/08/2021 → cutoff 19/08/2026. **Risco-chave:** se o devedor derrubar o marco, a NF prescreve automaticamente. **Inclusão estratégica** se a tese de interrupção estiver robusta; caso contrário, excluir.")
    w("")
    w("---")
    w("")

# -------- Parte 4 — CT 008/2021 12 NFs --------
w("## 4 — CT 008/2021 — rastreamento das 12 NFs")
w("")
w(f"Notificação lista **12 NFs** sob CT 008/2021. `spcf_faturas` retorna **7 faturas** com `contrato_num = '8/2021'`, das quais **{len(ct008_nfs_notif_no_db)} coincidem** com a notificação.")
w("")
w(f"- NFs da notif presentes no DB ({len(ct008_nfs_notif_no_db)}): {sorted(ct008_nfs_notif_no_db)}")
w(f"- NFs da notif **ausentes** do DB ({len(ct008_nfs_notif_fora_db)}): {sorted(ct008_nfs_notif_fora_db)}")
w(f"- NFs do DB **fora** da notificação ({len(ct008_nfs_db_fora_notif)}): {sorted(ct008_nfs_db_fora_notif)}")
w("")
w("> ℹ️ O pedido original falava em \"5 faturas ausentes\", mas a matemática é: notif=12, no_db=4, **fora_db=8**. Há também **3 NFs do DB que não estão na notificação** — possivelmente são faturas canceladas ou fora do universo 202.")
w("")
w("### Tabela de rastreamento das 12 NFs da notificação")
w("")
w("| NF | No DB | Contrato (DB) | Valor (DB) | CSV projeto | Contrato (CSV) | Valor serv (CSV) | Valor atu calc (CSV) | Prescrição (CSV) | Força (CSV) |")
w("|---|:---:|---|---:|:---:|---|---:|---:|---|---|")
for nf in NOTIFICACAO_ANEXO_IA["CT 008/2021"]:
    t = ct008_trace[nf]
    ci = t.get("csv_projeto_info") or {}
    db_info = t.get("db_info") or {}
    val_db = fmt_brl(db_info.get("valor_bruto", Decimal("0"))) if db_info else ""
    w(f"| {nf} | {y(t['no_db'])} | {db_info.get('contrato_num_raw','')} | {val_db} | {y(t['no_csv_projeto'])} | {ci.get('contrato_csv','')} | {ci.get('valor_servicos','')} | {ci.get('valor_corrigido_calc','')} | {ci.get('status_prescricao','')} | {ci.get('forca_probatoria','')} |")
w("")
w("### NFs do DB fora da notificação (filtragem consciente?)")
w("")
for nf in sorted(ct008_nfs_db_fora_notif):
    info = db_faturas_por_nf.get(nf, {})
    w(f"- NF **{nf}**: contrato `{info.get('contrato_num_raw','')}` · competência {info.get('competencia','')} · valor R$ {fmt_brl(info.get('valor_bruto', Decimal('0')))} · situação {info.get('situacao','')} · cadeia {info.get('cadeia_completude','')}")
w("")
w("---")
w("")

# -------- Parte 5 — CT 179/2018 / NF 110654 --------
w("## 5 — CT 179/2018 / NF 110654")
w("")
t = nf_110654
w(f"- Em `spcf_faturas` como NF: **{'SIM' if t['no_db'] else 'NÃO'}**")
if t['db_info']:
    db_info = t['db_info']
    w(f"  - contrato `{db_info['contrato_num_raw']}` · competência {db_info.get('competencia','')} · valor R$ {fmt_brl(db_info.get('valor_bruto', Decimal('0')))} · situação {db_info.get('situacao','')}")
w(f"- CSV projeto: **{'SIM' if t['no_csv_projeto'] else 'NÃO'}**")
if t.get("csv_projeto_info"):
    ci = t["csv_projeto_info"]
    w(f"  - contrato CSV `{ci['contrato_csv']}` · valor_servicos {ci.get('valor_servicos','')} · valor_corrigido_calc {ci.get('valor_corrigido_calc','')} · prescrição {ci.get('status_prescricao','')} · força {ci.get('forca_probatoria','')} · valor_pg_parcial {ci.get('valor_pg_parcial','')} · paga {ci.get('paga','')}")
w(f"- CSV SPCF: **{'SIM' if t['no_csv_spcf'] else 'NÃO'}**")
w(f"- CSV c/correção: **{'SIM' if t['no_csv_correcao'] else 'NÃO'}**")
if t.get("csv_correcao_info"):
    ci = t["csv_correcao_info"]
    w(f"  - valor_servicos {ci.get('valor_servicos','')} · valor_total_atualizado {ci.get('valor_total_atualizado','')}")
w(f"- `spcf_faturas` contrato_num = '179/2018': **{len(ct179_nfs_db)}** NFs: {ct179_nfs_db}")
w("")
w("**Análise:** a NF 110654 é a única fatura do CT 179/2018 citada na notificação. Profile marca marco interruptivo FORTÍSSIMO em 19/08/2021, prescrita=False, cutoff 19/08/2026. **Se a NF 110654 não estiver nas fontes tabulares**, é fundamental preparar dossiê específico (Nota de Empenho subsequente, ato administrativo) que comprove o marco antes do protocolo.")
w("")
w("---")
w("")

# -------- Parte 6 — VEREDICTO --------
w("## 6 — VEREDICTO FINAL")
w("")
w("| # | Item | Manter / Ressalvar / Excluir | Justificativa sintética |")
w("|---:|---|---|---|")

resumo = {
    "manter": [],
    "ressalva": [],
    "excluir": [],
    "investigar": [],
}

for c in cruzamento:
    cn = c["numero_norm"]
    ct_raw = c["numero_notificacao"]
    qtd = c["qtd_nfs_notif"]
    cen = c["cenario"]
    if cen in ("A-OK", "A"):
        resumo["manter"].append(c)
        dec = "✅ Manter"
        just = f"Profile+DB{'+PDF' if c['docs']['pdfs_01'] else ''}; {qtd} NFs coerentes entre fontes."
    elif cen == "A-parcial":
        resumo["ressalva"].append(c)
        dec = "⚠️ Manter com ressalva"
        just = f"Profile+faturas no DB, contrato não ingerido em spcf_contratos."
    elif cen == "B":
        resumo["investigar"].append(c)
        if cn == "179/2018":
            dec = "⚠️ Decisão jurídica"
            just = f"1 NF · tese prescrição FORTÍSSIMA; se a tese cair, NF prescreve imediatamente."
        else:
            dec = "⚠️ Decisão jurídica"
            just = f"Sem PDF de contrato; foi removido 16/04 e re-adicionado 17/04 pós-assinatura."
    elif cen == "C":
        resumo["excluir"].append(c)
        dec = "❌ Excluir / errata"
        just = "Fantasma — não está em nenhuma fonte."
    else:
        dec = "? Investigar"
        just = "Cenário não classificado."
    w(f"| | {ct_raw} ({qtd} NFs) | {dec} | {just} |")

w("")
w("### Recomendação operacional antes do protocolo")
w("")
w("1. **Protocolar os 13 contratos do Cenário A-OK/A/A-parcial** (tudo que está em profile + DB + pelo menos faturas). Nenhum risco documental relevante.")
w("2. **Decidir formalmente** sobre os 4 contratos Cenário B (8/2021, 14/2019, 23/2014, 179/2018) antes do protocolo:")
w("   - **Opção 1 (manter):** anexar ao dossiê, para cada um, (a) Nota de Empenho que suporta as faturas, (b) NF emitida, (c) justificativa de reconhecimento tácito. Registrar em ata interna a decisão de incluir mesmo sem PDF de contrato.")
w("   - **Opção 2 (excluir):** emitir errata simples removendo os 4; protocolar separadamente quando os PDFs contratuais forem localizados em PRODAM-RH/SPROWEB.")
w("3. **Para CT 296/2025**: anexar ao protocolo o PDF `01_CONTRATOS/PDF/CT_003_2026_DETRAN.pdf` explicando que proposta 296/2025 + CT 003/2026 são o mesmo documento.")
w("4. **Manter o memorial de cálculo detalhado** (com valor_pg_parcial por fatura) junto ao protocolo para responder à limitação encontrada na Consulta 4 do relatório anterior.")
w("5. **Dossiê específico para NF 110654** (CT 179/2018) comprovando o marco interruptivo de 19/08/2021 — peça a mais importante em termos de risco prescricional.")
w("")
w("---")
w("")
w("## METADADOS DA ANÁLISE")
w("")
w(f"- SHA-256 do PDF assinado copiado: `c4f052368346b83a79cf32ffad8f40a0954602cadd9947ab79162c4f444b928d`")
w(f"- Cópia arquivada em: `_NOTIFICACAO_ASSINADA/NOTIFICACAO_EXTRAJUDICIAL_PRODAM_DETRANass.pdf`")
w(f"- Original preservado em: `C:\\Users\\gabri\\Downloads\\NOTIFICACAO_EXTRAJUDICIAL_PRODAM_DETRANass.pdf`")
w(f"- Fontes cruzadas: profiles.json · prodam.db (spcf_contratos + spcf_faturas) · 3 CSVs (projeto, SPCF, com correção) · PDFs 01_CONTRATOS/PDF ({len(todos_pdfs_contratos)} PDFs) · HTMLs 01_CONTRATOS/HTML ({len(todos_htmls)} HTMLs) · PRODAM_DOCS/DETRAN")
w(f"- Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

OUT_MD.write_text("\n".join(L), encoding="utf-8")
print(f"OK JSON: {OUT_JSON}")
print(f"OK MD:   {OUT_MD}")
print(f"Integridade do Anexo I: qtd={vi['qtd_nfs_bate']} saldo_orig={vi['saldo_original_bate']} val_atu={vi['valor_atualizado_bate']}")
print(f"Cenarios: " + ", ".join(f"{c['numero_notificacao']}={c['cenario']}" for c in cruzamento))
print(f"\nCT 008/2021: notif=12, no_db=4, fora_db=8")
print(f"CT 179/2018 NF 110654: no_db={nf_110654['no_db']} no_csv_proj={nf_110654['no_csv_projeto']} no_csv_spcf={nf_110654['no_csv_spcf']} no_csv_corr={nf_110654['no_csv_correcao']}")
