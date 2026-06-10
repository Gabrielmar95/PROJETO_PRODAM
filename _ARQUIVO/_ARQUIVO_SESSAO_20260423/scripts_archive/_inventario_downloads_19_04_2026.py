"""
Inventario do que falta baixar (SPCF/SGTI) e do que precisa converter (HTML->PDF)
para completar o dossie da notificacao DETRAN. Read-only em todas as fontes.

Gera em _NOTIFICACAO_ASSINADA/:
  - INVENTARIO_DOWNLOADS_E_CONVERSOES.md   (relatorio)
  - LACUNAS_PARA_DOWNLOAD.csv              (para download em lote via SPCF/SGTI)
  - HTMLS_PARA_CONVERTER.csv               (para pipeline de conversao)
"""
from __future__ import annotations
import sqlite3, json, os, re, csv
from pathlib import Path
from decimal import Decimal
from datetime import datetime

DB = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\16_BANCOS_DADOS\prodam.db"
BASE = Path(r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA")
OUT_DIR = BASE / "_NOTIFICACAO_ASSINADA"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_MD = OUT_DIR / "INVENTARIO_DOWNLOADS_E_CONVERSOES.md"
OUT_CSV_DL = OUT_DIR / "LACUNAS_PARA_DOWNLOAD.csv"
OUT_CSV_HTML = OUT_DIR / "HTMLS_PARA_CONVERTER.csv"

# ============ UNIVERSO DA NOTIFICAO (18 contratos, 202 NFs) ============
CONTRATOS = [
    ("CT 010/2021",30),("CT 022/2014",12),("CT 296/2025",4),("CT 006/2021",79),
    ("CT 003/2026",3),("CT 004/2016",5),("CT 071/2022",2),("CT 012/2021",11),
    ("CT 017/2015",6),("CT 075/2022",2),("CT 025/2014",7),("CT 083/2022",7),
    ("CT 027/2014",15),("CT 060/2022",2),("CT 008/2021",12),("CT 179/2018",1),
    ("CT 023/2014",2),("CT 014/2019",2),
]
NFS_POR_CT = {
    "CT 010/2021": "129515,137916,137917,137918,165621,165622,165623,134316,134317,134318,162971,162973,135058,135059,135060,167282,167283,167284,136423,136424,136425,135862,135863,135864,166854,166855,166858,164004,164005,164006",
    "CT 022/2014": "128079,128080,128081,128086,128133,128134,128135,128146,128167,128168,128169,128170",
    "CT 296/2025": "165497,164621,163999,164000",
    "CT 006/2021": "137473,137474,137475,137476,137477,137478,137479,130271,165062,165063,165064,165065,165066,165067,165068,165137,165138,137569,137570,134800,134801,134802,134803,134804,134805,134806,135486,135487,135488,135489,135490,135491,135492,136191,136192,136193,136194,136195,136196,136197,136862,136863,136864,136865,136866,136867,136868,163820,167062,167063,167064,167065,167066,167067,167068,167158,167159,135063,135064,134418,134419,136421,136422,128770,129612,129613,135860,135861,137097,137098,166601,166602,166603,166604,166605,166606,166607,166852,166853",
    "CT 003/2026": "167160,166661,166089",
    "CT 004/2016": "132600,133362,131182,130540,131912",
    "CT 071/2022": "135065,134497",
    "CT 012/2021": "155538,165493,163822,167157,164797,135857,135858,138012,166851,163143,137296",
    "CT 017/2015": "128141,128144,128145,128163,128165,128166",
    "CT 075/2022": "167070,166609",
    "CT 025/2014": "128075,128138,128140,128159,128160,128162,128171",
    "CT 083/2022": "165071,165136,137571,167071,164300,166610,166276",
    "CT 027/2014": "127483,127484,127485,127754,127755,128076,128136,128137,128139,128142,128154,128155,128156,128157,128158",
    "CT 060/2022": "136505,137102",
    "CT 008/2021": "137480,155743,129365,129512,137915,165069,165619,167069,167285,137106,166608,166859",
    "CT 179/2018": "110654",
    "CT 023/2014": "128153,128164",
    "CT 014/2019": "128143,128161",
}
def norm(n: str) -> str:
    n = (n or "").upper().replace("CT","").replace("C.","").replace(" ","").replace(".","/").strip()
    m = re.match(r"0*(\d+)/(\d{4})$", n)
    return f"{m.group(1)}/{m.group(2)}" if m else n


# ============ LISTAR ARQUIVOS FISICOS ============
def listar(d: Path, ext: str) -> list[str]:
    return [p.name for p in d.iterdir() if p.is_file() and p.suffix.lower() == ext] if d.is_dir() else []

PDFS_CONTRATOS = listar(BASE / "01_CONTRATOS" / "PDF", ".pdf")
HTMLS_CONTRATOS = listar(BASE / "01_CONTRATOS" / "HTML", ".html")
PDFS_NE = listar(BASE / "02_NOTAS_EMPENHO" / "PDF", ".pdf")
HTMLS_NE = listar(BASE / "02_NOTAS_EMPENHO" / "HTML", ".html")
PDFS_FAT = listar(BASE / "04_FATURAS" / "PDF", ".pdf")
HTMLS_FAT = listar(BASE / "04_FATURAS" / "HTML", ".html")
PDFS_AC = listar(BASE / "05_ACEITES_TECNICOS" / "PDF", ".pdf")


def pdf_contrato(cn_norm: str) -> list[str]:
    num, ano = cn_norm.split("/")
    pats = [f"{num.zfill(3)}.{ano}", f"{num.zfill(3)}_{ano}", f"{num}.{ano}", f"{num}_{ano}", f"CT_{num.zfill(3)}_{ano}", f"CT_{num}_{ano}", f" {num}.{ano}", f" {num}/{ano}"]
    return sorted({p for p in PDFS_CONTRATOS if any(pat.lower() in p.lower() for pat in pats)})

def html_contrato(cn_norm: str) -> list[str]:
    num, ano = cn_norm.split("/")
    pats = [f"{num.zfill(3)}.{ano}", f"{num.zfill(3)}_{ano}", f"{num}.{ano}", f"{num}_{ano}", f"CT_{num.zfill(3)}_{ano}"]
    return sorted({p for p in HTMLS_CONTRATOS if any(pat.lower() in p.lower() for pat in pats)})

def pdf_fatura(nf: str) -> list[str]:
    return sorted({p for p in PDFS_FAT if nf in p})

def html_fatura(nf: str) -> list[str]:
    return sorted({p for p in HTMLS_FAT if nf in p})


# ============ CONSULTAR BANCO ============
conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()

# NEs
cur.execute("""
    SELECT numero, contrato_ref, valor, data_emissao, tem_pdf, pdf_path, cliente
    FROM spcf_empenhos WHERE UPPER(cliente) LIKE '%DETRAN%'
""")
nes = []
for r in cur.fetchall():
    nes.append({"numero": r[0], "contrato_ref": r[1], "valor": r[2], "data": r[3], "tem_pdf": r[4], "pdf_path": r[5]})
nes_por_ct = {}
for n in nes:
    cn = norm(n["contrato_ref"]) if n["contrato_ref"] else ""
    nes_por_ct.setdefault(cn, []).append(n)

# Faturas
cur.execute("""
    SELECT id, nf, contrato_num, valor_bruto, competencia, situacao, tem_pdf, fatura_parsed
    FROM spcf_faturas WHERE UPPER(cliente) LIKE '%DETRAN%'
""")
faturas = []
for r in cur.fetchall():
    try:
        fp = json.loads(r[7]) if r[7] else {}
    except Exception:
        fp = {}
    faturas.append({
        "id": r[0], "nf": str(r[1]), "contrato_num": r[2],
        "contrato_num_norm": norm(r[2]) if r[2] else "",
        "valor_bruto": r[3], "competencia": r[4], "situacao": r[5], "tem_pdf": r[6],
        "contrato_id_spcf": fp.get("contrato_id"),
    })
fat_por_nf = {f["nf"]: f for f in faturas}

# spcf_contratos (para pegar SPCF id)
cur.execute("SELECT id, numero FROM spcf_contratos WHERE UPPER(cliente) LIKE '%DETRAN%'")
ct_spcf_ids = {norm(r[1]): r[0] for r in cur.fetchall()}

conn.close()


# ============ CRUZAMENTO FATURAS DA NOTIFICACAO ============
inventario_nfs = []
for ct_raw, qtd in CONTRATOS:
    cn_norm = norm(ct_raw)
    nfs = NFS_POR_CT[ct_raw].split(",")
    for nf in nfs:
        nf = nf.strip()
        pdfs_loc = pdf_fatura(nf)
        htmls_loc = html_fatura(nf)
        fdb = fat_por_nf.get(nf)
        em_db = fdb is not None
        tem_pdf_db = bool(fdb and fdb["tem_pdf"])
        tem_pdf_fisico = len(pdfs_loc) > 0
        tem_html = len(htmls_loc) > 0
        # decisao de status
        if tem_pdf_fisico:
            status = "OK_PDF"
        elif tem_html and not tem_pdf_fisico:
            status = "CONVERTER_HTML"
        elif em_db and tem_pdf_db and not tem_pdf_fisico:
            # pdf no DB mas nao copiado para pasta
            status = "VERIFICAR_PDF_BANCO"
        else:
            status = "DOWNLOAD_SPCF"
        inventario_nfs.append({
            "contrato": ct_raw, "contrato_norm": cn_norm, "nf": nf,
            "em_db": em_db,
            "tem_pdf_banco": tem_pdf_db,
            "contrato_id_spcf": fdb["contrato_id_spcf"] if fdb else None,
            "pdfs_fisicos": ",".join(pdfs_loc[:3]),
            "qtd_pdfs_fisicos": len(pdfs_loc),
            "htmls_fisicos": ",".join(htmls_loc[:3]),
            "qtd_htmls_fisicos": len(htmls_loc),
            "status": status,
            "sugestao_endpoint_spcf": "/index.php/contratos/fatura/{fatura_id}" if status == "DOWNLOAD_SPCF" else "",
            "competencia": fdb["competencia"] if fdb else "",
            "valor_bruto": fdb["valor_bruto"] if fdb else "",
        })

status_nfs = {}
for it in inventario_nfs:
    status_nfs[it["status"]] = status_nfs.get(it["status"], 0) + 1


# ============ CRUZAMENTO CONTRATOS ============
inventario_cts = []
for ct_raw, qtd in CONTRATOS:
    cn = norm(ct_raw)
    pdfs = pdf_contrato(cn)
    htmls = html_contrato(cn)
    if pdfs:
        status = "OK_PDF"
    elif htmls:
        status = "CONVERTER_HTML"
    else:
        status = "DOWNLOAD_SPCF"
    spcf_id = ct_spcf_ids.get(cn)
    if isinstance(spcf_id, str) and spcf_id.startswith("PDF_"):
        spcf_id = None
    endpoint = ""
    if status == "DOWNLOAD_SPCF":
        if spcf_id:
            endpoint = f"/index.php/contratos/imprimir/{spcf_id} (ou /propostas/imprimir/{{proposta_id}})"
        else:
            endpoint = "buscar SPCF id em `spcf_contratos` ou acessar SGTI para contrato escaneado"
    inventario_cts.append({
        "contrato": ct_raw, "contrato_norm": cn, "qtd_nfs_notif": qtd,
        "qtd_pdfs": len(pdfs), "pdfs": ",".join(pdfs[:3]),
        "qtd_htmls": len(htmls), "htmls": ",".join(htmls[:3]),
        "spcf_id": spcf_id,
        "status": status,
        "endpoint_sugerido": endpoint,
    })


# ============ NEs SEM PDF NO BANCO ============
nes_sem_pdf_notif = []
for n in nes:
    if not n["tem_pdf"]:
        cn = norm(n["contrato_ref"]) if n["contrato_ref"] else ""
        if cn in {norm(c[0]) for c in CONTRATOS}:
            nes_sem_pdf_notif.append({
                "numero_ne": n["numero"], "contrato_ref": n["contrato_ref"],
                "contrato_norm": cn, "valor": n["valor"], "data": n["data"],
            })
nes_sem_pdf_outros = [n for n in nes if not n["tem_pdf"] and norm(n["contrato_ref"] or "") not in {norm(c[0]) for c in CONTRATOS}]


# ============ HTMLS PARA CONVERTER (global) ============
htmls_converter = []
for nm in HTMLS_CONTRATOS:
    htmls_converter.append({"categoria": "CONTRATO", "arquivo": nm, "pasta": "01_CONTRATOS/HTML"})
for nm in HTMLS_NE:
    htmls_converter.append({"categoria": "NE", "arquivo": nm, "pasta": "02_NOTAS_EMPENHO/HTML"})
for nm in HTMLS_FAT:
    htmls_converter.append({"categoria": "FATURA", "arquivo": nm, "pasta": "04_FATURAS/HTML"})


# ============ NLs — 03_NOTAS_LIQUIDACAO esta vazia ============
# Verificar se NLs aparecem em spcf_nfs.liquidacao para as NFs da notificacao
conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()
nls_por_nf = {}
for nf in {it["nf"] for it in inventario_nfs}:
    cur.execute("SELECT liquidacao FROM spcf_nfs WHERE numero_nf = ?", (nf,))
    r = cur.fetchone()
    if r and r[0]:
        # extrair codigos NL/OB/PD
        try:
            obj = json.loads(r[0])
        except Exception:
            obj = {}
        codigos = set()
        for v in (obj or {}).values():
            if isinstance(v, str):
                for m in re.finditer(r"(\d{4}(?:NL|OB|PD)\d+)", v):
                    codigos.add(m.group(1))
        if codigos:
            nls_por_nf[nf] = sorted(codigos)
conn.close()

nfs_com_nl = len(nls_por_nf)
nfs_sem_nl_em_spcfnfs = 202 - nfs_com_nl


# ============ GRAVAR CSVs ============
# DOWNLOAD CSV
with open(OUT_CSV_DL, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["categoria","contrato","contrato_norm","numero_documento","spcf_id","endpoint_sugerido","contexto","status"])
    # Contratos
    for c in inventario_cts:
        if c["status"] == "DOWNLOAD_SPCF":
            w.writerow(["CONTRATO", c["contrato"], c["contrato_norm"], "", c["spcf_id"] or "", c["endpoint_sugerido"], f"{c['qtd_nfs_notif']} NFs na notif", c["status"]])
    # NFs faltantes
    for it in inventario_nfs:
        if it["status"] == "DOWNLOAD_SPCF":
            w.writerow(["FATURA", it["contrato"], it["contrato_norm"], it["nf"], it["contrato_id_spcf"] or "", "/index.php/contratos/fatura/{fatura_id}", f"comp={it['competencia']} val={it['valor_bruto']}", it["status"]])
    # NEs sem PDF dos contratos da notif
    for n in nes_sem_pdf_notif:
        w.writerow(["NE", f"CT {n['contrato_norm']}", n['contrato_norm'], n["numero_ne"], "", "/index.php/empenhos/imprimir/{id} ou SGTI/AFI", f"data={n['data']} val={n['valor']}", "DOWNLOAD_SPCF"])

# HTML CSV
with open(OUT_CSV_HTML, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["categoria","pasta","arquivo"])
    for h in htmls_converter:
        w.writerow([h["categoria"], h["pasta"], h["arquivo"]])


# ============ RELATORIO MD ============
L = []
def out(s=""):
    L.append(s)

out("# INVENTÁRIO DE LACUNAS — Download (SPCF/SGTI) e Conversão (HTML→PDF)")
out("")
out(f"**Data:** 2026-04-19  |  **Escopo:** DETRAN (notificação 001/2026, 18 contratos × 202 NFs)")
out("")
out("---")
out("")
out("## RESUMO EXECUTIVO")
out("")
out("| Categoria | Cita | OK | Converter HTML | Download SPCF | Verificar |")
out("|---|---:|---:|---:|---:|---:|")
def cnt(items, st):
    return sum(1 for i in items if i["status"] == st)
out(f"| Contratos | 18 | {cnt(inventario_cts,'OK_PDF')} | {cnt(inventario_cts,'CONVERTER_HTML')} | {cnt(inventario_cts,'DOWNLOAD_SPCF')} | — |")
out(f"| Notas Fiscais | 202 | {status_nfs.get('OK_PDF',0)} | {status_nfs.get('CONVERTER_HTML',0)} | {status_nfs.get('DOWNLOAD_SPCF',0)} | {status_nfs.get('VERIFICAR_PDF_BANCO',0)} |")
out(f"| Notas de Empenho sem PDF | — | — | — | {len(nes_sem_pdf_notif)} (contratos da notif) + {len(nes_sem_pdf_outros)} (outros) | — |")
out(f"| Notas de Liquidação | 202 NFs | {nfs_com_nl} com NL em `spcf_nfs` | — | {nfs_sem_nl_em_spcfnfs} sem código NL | — |")
out(f"| Aceites Técnicos | ? | {len(PDFS_AC)} PDFs na pasta | 0 | faltam identificar por NF | — |")
out(f"| HTMLs globais p/ conversão | — | — | {len(htmls_converter)} | — | — |")
out("")
out("**Pastas físicas (contagens absolutas):**")
out("")
out(f"- `01_CONTRATOS/`: PDFs={len(PDFS_CONTRATOS)} · HTMLs={len(HTMLS_CONTRATOS)}")
out(f"- `02_NOTAS_EMPENHO/`: PDFs={len(PDFS_NE)} · HTMLs={len(HTMLS_NE)}")
out(f"- `03_NOTAS_LIQUIDACAO/`: **VAZIA** (0 PDFs, 0 HTMLs)")
out(f"- `04_FATURAS/`: PDFs={len(PDFS_FAT)} · HTMLs={len(HTMLS_FAT)}")
out(f"- `05_ACEITES_TECNICOS/`: PDFs={len(PDFS_AC)} · HTMLs=0")
out("")
out("---")
out("")

# --- Contratos ---
out("## 1 — CONTRATOS (18)")
out("")
out("| Contrato | Qtd NFs | PDFs | HTMLs | SPCF id | Status | Endpoint sugerido |")
out("|---|---:|---:|---:|---|---|---|")
for c in inventario_cts:
    st_icon = "🟢" if c["status"]=="OK_PDF" else "🟡" if c["status"]=="CONVERTER_HTML" else "🔴"
    out(f"| {c['contrato']} | {c['qtd_nfs_notif']} | {c['qtd_pdfs']} | {c['qtd_htmls']} | {c['spcf_id'] or '—'} | {st_icon} {c['status']} | {c['endpoint_sugerido']} |")
out("")
need_dl_ct = [c for c in inventario_cts if c["status"]=="DOWNLOAD_SPCF"]
if need_dl_ct:
    out(f"**Para download:** {len(need_dl_ct)} contrato(s) — {[c['contrato'] for c in need_dl_ct]}.")
    out("")
else:
    out("**Nenhum contrato precisa download** — todos têm PDF ou HTML em disco. ✅")
    out("")
need_conv_ct = [c for c in inventario_cts if c["status"]=="CONVERTER_HTML"]
if need_conv_ct:
    out(f"**Para converter HTML→PDF:** {len(need_conv_ct)} contrato(s) — {[c['contrato'] for c in need_conv_ct]}.")
    out("")

# --- NFs ---
out("---")
out("")
out("## 2 — NOTAS FISCAIS (202)")
out("")
out("Resumo por status:")
out("")
for st in ["OK_PDF","CONVERTER_HTML","VERIFICAR_PDF_BANCO","DOWNLOAD_SPCF"]:
    out(f"- **{st}**: {status_nfs.get(st,0)}")
out("")
out("### 2.1 NFs que precisam DOWNLOAD via SPCF")
out("")
faltantes = [it for it in inventario_nfs if it["status"] == "DOWNLOAD_SPCF"]
out(f"Total: **{len(faltantes)}** NFs. Endpoint sugerido: `/index.php/contratos/fatura/{{fatura_id}}` — o `fatura_id` equivale ao campo `id` em `spcf_faturas`. Para as NFs abaixo, o `id` ainda não está no banco; precisa autenticar no SPCF e navegar até a lista de faturas do contrato (POST `/index.php/contratos/relatorioFaturas`) para capturar o id antes de cada download.")
out("")
if faltantes:
    out("| Contrato | NF | SPCF contrato_id | Competência | Valor bruto |")
    out("|---|---|---|---|---:|")
    for it in faltantes[:100]:
        out(f"| {it['contrato']} | {it['nf']} | {it['contrato_id_spcf'] or '—'} | {it['competencia'] or '—'} | {it['valor_bruto'] or '—'} |")
    if len(faltantes) > 100:
        out(f"| ... (+{len(faltantes)-100} linhas no CSV) | | | | |")
else:
    out("Nenhuma NF precisa download. ✅")
out("")
out("### 2.2 NFs em HTML (converter)")
out("")
need_conv_nf = [it for it in inventario_nfs if it["status"] == "CONVERTER_HTML"]
out(f"Total: **{len(need_conv_nf)}** NFs.")
if need_conv_nf:
    out("")
    out("| Contrato | NF | Arquivo HTML |")
    out("|---|---|---|")
    for it in need_conv_nf[:50]:
        out(f"| {it['contrato']} | {it['nf']} | {it['htmls_fisicos']} |")
    if len(need_conv_nf) > 50:
        out(f"| ... (+{len(need_conv_nf)-50} linhas) | | |")
out("")
out("### 2.3 NFs com `tem_pdf=1` no banco mas sem PDF físico localizado")
out("")
verify = [it for it in inventario_nfs if it["status"] == "VERIFICAR_PDF_BANCO"]
out(f"Total: **{len(verify)}**. São NFs cujo PDF foi marcado no banco, mas a busca em `04_FATURAS/PDF/` não encontrou — pode ser nomenclatura diferente, ou PDF em outra subpasta.")
if verify:
    out("")
    out("| Contrato | NF | Competência |")
    out("|---|---|---|")
    for it in verify[:30]:
        out(f"| {it['contrato']} | {it['nf']} | {it['competencia']} |")
out("")

# --- NEs ---
out("---")
out("")
out("## 3 — NOTAS DE EMPENHO (NEs)")
out("")
out(f"- NEs DETRAN totais no banco: {len(nes)}")
out(f"- NEs com PDF: {sum(1 for n in nes if n['tem_pdf'])}")
out(f"- **NEs sem PDF:** {sum(1 for n in nes if not n['tem_pdf'])}")
out(f"  - Dentre os 18 contratos da notificação: **{len(nes_sem_pdf_notif)}**")
out(f"  - Outros contratos (fora da notif): {len(nes_sem_pdf_outros)}")
out("")
if nes_sem_pdf_notif:
    out("### NEs SEM PDF referentes aos 18 contratos da notificação")
    out("")
    out("| Contrato | NE | Data | Valor (R$) |")
    out("|---|---|---|---:|")
    for n in sorted(nes_sem_pdf_notif, key=lambda x: (x["contrato_norm"], x["data"] or "")):
        out(f"| CT {n['contrato_norm']} | {n['numero_ne']} | {n['data']} | {n['valor']} |")
    out("")
    out("**Origem do download:** SGTI/AFI (Sistema de Administração Financeira Integrada) — NEs estão no SIAFEM/AFI, não no SPCF. Alternativa: capturar via raspagem do SPCF `empenhos/imprimir/{id}` se o sistema expor.")
    out("")

# --- NLs ---
out("---")
out("")
out("## 4 — NOTAS DE LIQUIDAÇÃO (NLs)")
out("")
out(f"- Pasta `03_NOTAS_LIQUIDACAO/` está **VAZIA** (0 PDFs e 0 HTMLs).")
out(f"- Em `spcf_nfs`, {nfs_com_nl} das 202 NFs da notificação têm código NL/OB/PD registrado no campo `liquidacao`.")
out(f"- **{nfs_sem_nl_em_spcfnfs}** NFs da notificação não têm nenhuma NL identificada em `spcf_nfs` — pode significar: (a) a NF ainda não foi liquidada; (b) a NF foi liquidada mas a entrada ainda não foi raspada; (c) a NL está em outro sistema (SIAFEM).")
out("")
if nls_por_nf:
    out("**Exemplos de NFs com código NL identificado (primeiras 10):**")
    out("")
    out("| NF | Códigos (NL/OB/PD) |")
    out("|---|---|")
    for nf, cods in list(nls_por_nf.items())[:10]:
        out(f"| {nf} | {', '.join(cods)} |")
    out("")
out("**Observação:** NL é ato administrativo do DETRAN (Lei 4.320/64, Arts. 63-65). Não há necessariamente PDF autônomo — o registro já basta como prova quando extraído do spcf_nfs (como no caso da NF 110654 / 2021NL0001165). **Download de PDFs de NLs não é necessário**; basta comprovar via cópia do campo `liquidacao` exportada do banco, ou via consulta direta no SIAFEM por processo.")
out("")

# --- Aceites ---
out("---")
out("")
out("## 5 — ACEITES TÉCNICOS")
out("")
out(f"- Pasta `05_ACEITES_TECNICOS/PDF/` tem apenas **{len(PDFS_AC)} arquivos**.")
out(f"- Não há cruzamento direto no banco (nenhuma tabela `spcf_aceites`).")
out("")
out("**Recomendação:** para as 202 NFs da notificação, pedir à PRODAM por e-mail a lista de aceites técnicos assinados pelo fiscal do contrato DETRAN. Alternativa: capturar do SPCF via endpoint de detalhe da fatura (há vezes em que o aceite aparece embutido).")
out("")

# --- HTMLs ---
out("---")
out("")
out("## 6 — HTMLs PARA CONVERTER (global)")
out("")
out("| Categoria | Pasta | Qtd |")
out("|---|---|---:|")
out(f"| Contratos | `01_CONTRATOS/HTML/` | {len(HTMLS_CONTRATOS)} |")
out(f"| Notas de Empenho | `02_NOTAS_EMPENHO/HTML/` | {len(HTMLS_NE)} |")
out(f"| Faturas | `04_FATURAS/HTML/` | {len(HTMLS_FAT)} |")
out(f"| **Total** | — | **{len(htmls_converter)}** |")
out("")
out("**Pipeline de conversão recomendado:**")
out("")
out("1. **Chrome headless** (alta fidelidade visual, preserva CSS do SPCF):")
out("   ```powershell")
out("   & \"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\" --headless=new --disable-gpu --no-sandbox --print-to-pdf-no-header --print-to-pdf=\"saida.pdf\" \"file:///C:/caminho/para/arquivo.html\"")
out("   ```")
out("2. **WeasyPrint** (Python, preserva estrutura semântica — bom para docs com tabelas):")
out("   ```python")
out("   from weasyprint import HTML")
out("   HTML('arquivo.html').write_pdf('arquivo.pdf')")
out("   ```")
out("3. **pdfkit + wkhtmltopdf** (alternativa leve, instala via `pip install pdfkit` + binário `wkhtmltopdf`).")
out("")
out("**Boas práticas:**")
out("- Renomear o PDF gerado para incluir timestamp de captura (ex: `fatura_167285_SPCF_20260419.pdf`).")
out("- Arquivar o HTML original junto ao PDF gerado (NUNCA apagar — o HTML é a fonte primária).")
out("- Após conversão, atualizar `spcf_faturas.tem_pdf` e `pdf_path` via script de ingestão.")
out("")

# --- Endpoints ---
out("---")
out("")
out("## 7 — ENDPOINTS SPCF / SGTI PARA DOWNLOAD EM LOTE")
out("")
out("Referência do `CLAUDE.md §6`:")
out("")
out("| Recurso | Endpoint |")
out("|---|---|")
out("| Login | `POST /index.php/usuarios/login` com `data[Usuario][login]` e `data[Usuario][senha]` |")
out("| Estabelecer cookie SPCF | `GET /index.php/spcf` após login |")
out("| **Contrato (proposta)** | `GET /index.php/propostas/imprimir/{id_proposta}` |")
out("| **Contrato (detalhe)** | `GET /index.php/contratos/imprimir/{id_contrato}` |")
out("| **Fatura individual** | `GET /index.php/contratos/fatura/{id_fatura}` (renderiza RPS/NFS-e — usar Chrome CDP `Page.printToPDF`) |")
out("| **Relação de faturas do contrato** | `POST /index.php/contratos/relatorioFaturas` com `data[ContratoRelatorio][contrato_id]={id}` |")
out("")
out("**Autenticação:** use as variáveis de ambiente do `.env` (`SPCF_USER`, `SPCF_PASS`, `SPCF_URL`). Requer VPN PRODAM ativa (domínio resolve apenas na intranet 10.20.0.x).")
out("")
out("**Rate limit:** `time.sleep(1.5)` entre requisições (obrigatório — regra 5 do `CLAUDE.md`).")
out("")

# --- Arquivos gerados ---
out("---")
out("")
out("## ARQUIVOS GERADOS POR ESSA ANÁLISE")
out("")
out(f"- `_NOTIFICACAO_ASSINADA/INVENTARIO_DOWNLOADS_E_CONVERSOES.md` (este relatório)")
out(f"- `_NOTIFICACAO_ASSINADA/LACUNAS_PARA_DOWNLOAD.csv` — lista acionável para download via SPCF/SGTI (CSV `;`, UTF-8 BOM)")
out(f"- `_NOTIFICACAO_ASSINADA/HTMLS_PARA_CONVERTER.csv` — lista de HTMLs para pipeline de conversão")
out("")
out(f"_Gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — read-only em profiles.json, prodam.db e pastas físicas._")

OUT_MD.write_text("\n".join(L), encoding="utf-8")

# Sumário no stdout
print(f"MD:  {OUT_MD}  ({len(L)} linhas)")
print(f"CSV DL:  {OUT_CSV_DL}")
print(f"CSV HTML: {OUT_CSV_HTML}")
print(f"\nCONTRATOS: {len(inventario_cts)} total  |  OK={cnt(inventario_cts,'OK_PDF')}  HTML={cnt(inventario_cts,'CONVERTER_HTML')}  DL={cnt(inventario_cts,'DOWNLOAD_SPCF')}")
print(f"NFs:       {len(inventario_nfs)} total  |  OK={status_nfs.get('OK_PDF',0)}  HTML={status_nfs.get('CONVERTER_HTML',0)}  DL={status_nfs.get('DOWNLOAD_SPCF',0)}  VERIF={status_nfs.get('VERIFICAR_PDF_BANCO',0)}")
print(f"NEs s/ PDF notif:  {len(nes_sem_pdf_notif)}")
print(f"NEs s/ PDF outros: {len(nes_sem_pdf_outros)}")
print(f"HTMLs total:       {len(htmls_converter)}")
print(f"NLs: {nfs_com_nl}/202 NFs tem NL em spcf_nfs")
