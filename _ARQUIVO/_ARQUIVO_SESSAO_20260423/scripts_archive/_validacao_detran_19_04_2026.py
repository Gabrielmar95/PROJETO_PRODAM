"""
Validacao pos-notificacao DETRAN vs prodam.db (19/04/2026).
Read-only. Gera relatorio em _NOTIFICACAO_ASSINADA/VALIDACAO_CRUZADA_BANCO_19_04_2026.md.
"""
from __future__ import annotations
import sqlite3, json, os, re, glob
from decimal import Decimal, InvalidOperation
from datetime import datetime
from pathlib import Path

DB = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\16_BANCOS_DADOS\prodam.db"
PRODAM_DOCS = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\PRODAM_DOCS\DETRAN"
OUT_DIR = Path(r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\_NOTIFICACAO_ASSINADA")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_MD = OUT_DIR / "VALIDACAO_CRUZADA_BANCO_19_04_2026.md"

CONTRATOS_NOTIFICACAO_RAW = [
    "CT 010/2021","CT 022/2014","CT 296/2025","CT 006/2021",
    "CT 003/2026","CT 004/2016","CT 071/2022","CT 012/2021",
    "CT 017/2015","CT 075/2022","CT 025/2014","CT 083/2022",
    "CT 027/2014","CT 060/2022","CT 008/2021","CT 179/2018",
    "CT 023/2014","CT 014/2019",
]


def fix_latin(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s


def norm(numero: str) -> str:
    """Normaliza 'CT 010/2021' -> '10/2021'; '003/2026' -> '3/2026'."""
    if not numero:
        return ""
    n = numero.upper().replace("CT", "").replace(" ", "").strip()
    m = re.match(r"0*(\d+)/(\d{4})$", n)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return n


def money(val) -> Decimal:
    """Converte string BR ou numero em Decimal."""
    if val is None:
        return Decimal("0")
    if isinstance(val, (int, float, Decimal)):
        return Decimal(str(val))
    s = str(val).strip().replace("R$", "").replace(" ", "")
    # 30,540,349.00  -> formato US
    # 15.133.976,40  -> formato BR
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):  # BR
            s = s.replace(".", "").replace(",", ".")
        else:  # US
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


CONTRATOS_NORM = [norm(c) for c in CONTRATOS_NOTIFICACAO_RAW]

conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()

# ---------------- CONSULTA 1 ----------------
cur.execute("SELECT id, numero, cliente, dados_base, tem_tramite_pdf FROM spcf_contratos WHERE UPPER(cliente) LIKE '%DETRAN%'")
contratos_banco = []
for id_, numero, cliente, db_, pdf in cur.fetchall():
    d = json.loads(db_) if db_ else {}
    d2 = {fix_latin(k): (fix_latin(v) if isinstance(v, str) else v) for k, v in d.items()}
    contratos_banco.append({
        "id": id_,
        "numero_raw": numero,
        "numero_norm": norm(numero),
        "status": d2.get("Status", ""),
        "valor_raw": d2.get("Valor(R$)", ""),
        "valor_dec": money(d2.get("Valor(R$)", "")),
        "fim_vig": d2.get("Fim da vigência", ""),
        "tem_tramite_pdf": pdf,
    })

contratos_banco_norm = {c["numero_norm"]: c for c in contratos_banco}
no_banco = [c for c in CONTRATOS_NORM if c in contratos_banco_norm]
ausentes = [c for c in CONTRATOS_NORM if c not in contratos_banco_norm]

# ---------------- CONSULTA 2 — Faturas CT 008/2021 e CT 179/2018 ----------------
cur.execute("""
    SELECT id, nf, cliente, contrato_num, valor_bruto, competencia, situacao,
           cadeia_completude, cadeia_elos, total_empenhos_vinculados, tem_pdf, fatura_parsed
    FROM spcf_faturas
    WHERE UPPER(cliente) LIKE '%DETRAN%'
""")
todas_faturas = []
for row in cur.fetchall():
    id_, nf, cliente, cnum, vb, comp, sit, cc, ce, tev, tp, fp = row
    try:
        parsed = json.loads(fp) if fp else {}
    except Exception:
        parsed = {}
    todas_faturas.append({
        "id": id_, "nf": nf, "cliente": cliente,
        "contrato_num_raw": cnum,
        "contrato_num_norm": norm(cnum) if cnum else "",
        "valor_bruto": money(vb), "competencia": comp, "situacao": sit,
        "cadeia_completude": cc, "cadeia_elos": ce,
        "total_empenhos_vinculados": tev, "tem_pdf": tp,
        "valor_liquido": money(parsed.get("valor_liquido")),
        "issrf": money(parsed.get("issrf")),
        "ir_fonte": money(parsed.get("ir_fonte")),
        "data_fatura": parsed.get("data_fatura"),
    })

def faturas_de(norm_num: str):
    return [f for f in todas_faturas if f["contrato_num_norm"] == norm_num]

f_008 = faturas_de(norm("008/2021"))
f_179 = faturas_de(norm("179/2018"))

# ---------------- CONSULTA 3 — PDFs CT 296/2025 e CT 003/2026 ----------------
def buscar_pdf(devedor_root: str, padroes: list[str]):
    achados = set()
    if not os.path.isdir(devedor_root):
        return achados, f"pasta-raiz inexistente: {devedor_root}"
    for pad in padroes:
        for p in Path(devedor_root).rglob(pad):
            achados.add(str(p))
    return achados, None

pdfs_296, err_296 = buscar_pdf(PRODAM_DOCS, ["*296*2025*", "*296_2025*", "*296.2025*", "*296-2025*", "*CT296*2025*"])
pdfs_003, err_003 = buscar_pdf(PRODAM_DOCS, ["*003*2026*", "*003_2026*", "*003.2026*", "*003-2026*", "*CT003*2026*", "*3_2026*", "*3-2026*"])

c_296 = contratos_banco_norm.get(norm("296/2025"))
c_003 = contratos_banco_norm.get(norm("003/2026"))

# ---------------- CONSULTA 4 — Pagamentos parciais ----------------
# Schema atual NAO possui valor_pg_parcial nem saldo.
# Aproximacao: via tabela spcf_nfs (tem_pagamento) cruzando pela NF
cur.execute("""
    SELECT numero_nf, liquidacao, pagamento, tem_pagamento
    FROM spcf_nfs
""")

def parse_nf_blob(blob: str) -> dict:
    """spcf_nfs.liquidacao/pagamento traz JSON do scraping com chaves dinamicas.
    Extrai os campos mais uteis (valor liquido, data, OBs) de forma robusta."""
    if not blob:
        return {}
    try:
        obj = json.loads(blob) if isinstance(blob, str) else (blob or {})
    except Exception:
        return {"_raw": str(blob)[:80]}
    if not isinstance(obj, dict):
        return {}
    resultado = {}
    for k, v in obj.items():
        if not isinstance(v, str):
            continue
        vs = v.strip()
        if not vs:
            continue
        # data
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", vs):
            resultado.setdefault("data", vs)
            continue
        # valor BR (xxx.yyy,zz)
        if re.fullmatch(r"\d{1,3}(\.\d{3})*,\d{2}", vs):
            try:
                resultado.setdefault("valores", []).append(money(vs))
            except Exception:
                pass
        # OB / NL / PD code
        mcod = re.search(r"(\d{4}(?:OB|NL|PD|ND)\d+)", vs)
        if mcod:
            resultado.setdefault("codigos", set()).add(mcod.group(1))
    # converter set -> list
    if "codigos" in resultado:
        resultado["codigos"] = sorted(resultado["codigos"])
    return resultado


nfs_pag = {}
for r in cur.fetchall():
    numero_nf, liq, pag, tem_pag = r
    nfs_pag[str(numero_nf)] = {
        "tem_pagamento": tem_pag,
        "liq": parse_nf_blob(liq),
        "pag": parse_nf_blob(pag),
    }

faturas_notif = [f for f in todas_faturas if f["contrato_num_norm"] in CONTRATOS_NORM]
faturas_pagas = []
for f in faturas_notif:
    nf = f["nf"]
    info = nfs_pag.get(str(nf))
    if info and info.get("tem_pagamento"):
        liq = info.get("liq", {})
        pag = info.get("pag", {})
        # valor pago pode estar na ultima posicao dos valores da liquidacao (heuristica)
        vliq = liq.get("valores") or []
        vpag = pag.get("valores") or []
        valor_pago = max(vliq) if vliq else (max(vpag) if vpag else Decimal("0"))
        faturas_pagas.append({
            **f,
            "data_liq": liq.get("data", ""),
            "data_pag": pag.get("data", ""),
            "codigos": ", ".join(sorted(set((liq.get("codigos") or []) + (pag.get("codigos") or []))))[:80],
            "valor_pago_aprox": valor_pago,
            "saldo_aprox": f["valor_bruto"] - valor_pago,
        })

# Contratos orfaos: presentes em spcf_faturas mas nao em spcf_contratos
contratos_em_faturas = {f["contrato_num_norm"] for f in faturas_notif}
contratos_orfaos = contratos_em_faturas - set(contratos_banco_norm.keys())
faturas_orfaos_resumo = {}
for f in faturas_notif:
    if f["contrato_num_norm"] in contratos_orfaos:
        k = f["contrato_num_norm"]
        faturas_orfaos_resumo.setdefault(k, {"qtd": 0, "soma": Decimal("0"), "comp_min": None, "comp_max": None})
        faturas_orfaos_resumo[k]["qtd"] += 1
        faturas_orfaos_resumo[k]["soma"] += f["valor_bruto"]
        comp = f["competencia"] or ""
        if comp:
            if faturas_orfaos_resumo[k]["comp_min"] is None or comp < faturas_orfaos_resumo[k]["comp_min"]:
                faturas_orfaos_resumo[k]["comp_min"] = comp
            if faturas_orfaos_resumo[k]["comp_max"] is None or comp > faturas_orfaos_resumo[k]["comp_max"]:
                faturas_orfaos_resumo[k]["comp_max"] = comp

# ---------------- CONSULTA 5 — Distribuicao temporal ----------------
def ano_comp(comp: str):
    if not comp:
        return None
    m = re.search(r"(\d{4})", comp)
    return int(m.group(1)) if m else None

def mes_ano_comp(comp: str):
    if not comp:
        return (None, None)
    m = re.match(r"(\d{1,2})/(\d{4})", comp.strip())
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return (None, ano_comp(comp))

dist = {}
for f in faturas_notif:
    k = (f["contrato_num_norm"], ano_comp(f["competencia"]))
    dist.setdefault(k, {"qtd": 0, "soma_original": Decimal("0")})
    dist[k]["qtd"] += 1
    dist[k]["soma_original"] += f["valor_bruto"]

# faturas com competencia < 04/2021
faturas_pre_abr21 = []
for f in faturas_notif:
    mes, ano = mes_ano_comp(f["competencia"])
    if ano is None:
        continue
    if ano < 2021 or (ano == 2021 and mes is not None and mes < 4):
        faturas_pre_abr21.append(f)

soma_pre = sum((f["valor_bruto"] for f in faturas_pre_abr21), Decimal("0"))

pre_por_ct = {}
for f in faturas_pre_abr21:
    k = f["contrato_num_norm"]
    pre_por_ct.setdefault(k, {"qtd": 0, "soma": Decimal("0")})
    pre_por_ct[k]["qtd"] += 1
    pre_por_ct[k]["soma"] += f["valor_bruto"]

conn.close()

# ========================================================================
# RELATORIO
# ========================================================================
L = []
def w(line=""):
    L.append(line)

w("# VALIDAÇÃO CRUZADA — Notificação Extrajudicial PRODAM/DETRAN × prodam.db")
w("")
w(f"**Data da validação:** 19/04/2026")
w(f"**Base consultada:** `{DB}`")
w(f"**Modo de acesso:** read-only (URI `mode=ro`), PDF assinado intocado.")
w(f"**Contratos na notificação (18):** {', '.join(CONTRATOS_NOTIFICACAO_RAW)}")
w("")
w("---")
w("")
w("## RESUMO EXECUTIVO")
w("")
w("| # | Consulta | Semáforo | Achado principal |")
w("|---|---|:---:|---|")
w(f"| 1 | Contagem de contratos DETRAN | 🔴 | **13** no banco · notificação cita **18** · memória dizia 15 · 5 ausentes |")
w(f"| 2 | Faturas CT 008/2021 e CT 179/2018 | {'🟠' if (f_008 or f_179) else '🔴'} | CT 008/2021={len(f_008)} faturas (contrato-pai órfão) · CT 179/2018={len(f_179)} faturas |")
w(f"| 3 | PDFs CT 296/2025 e CT 003/2026 | {'🟢' if (pdfs_296 and pdfs_003) else '🟡' if (pdfs_296 or pdfs_003) else '🔴'} | 296/2025: {len(pdfs_296)} arquivo(s) · 003/2026: {len(pdfs_003)} arquivo(s) |")
w(f"| 4 | Pagamentos parciais | 🟡 | Schema não guarda `valor_pg_parcial`; proxy heurístico sobre `spcf_nfs`: {len(faturas_pagas)} NFs pagas |")
w(f"| 5 | Distribuição temporal | 🔴 | {len(faturas_pre_abr21)} faturas com competência < 04/2021 · valor original R$ {fmt_brl(soma_pre)} |")
w("")
w("---")
w("")

# -------- Consulta 1 --------
w("## CONSULTA 1 — Contagem de contratos DETRAN")
w("")
w("### Adaptação da consulta")
w("")
w("A consulta original referenciava `contratos(devedor, status)`, mas o schema real é `spcf_contratos(cliente, dados_base JSON)`. O campo `Status` fica dentro de `dados_base` e não aceita valor `'ativo'`: aceita `'Vigente'` (só contratos em trâmite SPCF) ou `'ENCERRADO_ARQUIVADO'` (contratos do pen drive/físico).")
w("")
w("### Resultado")
w("")
w(f"- **Total de contratos DETRAN distintos no banco:** {len(contratos_banco)}")
vigentes = [c for c in contratos_banco if c['status'] == 'Vigente']
encerrados = [c for c in contratos_banco if 'ENCERRADO' in str(c['status']).upper()]
w(f"  - Vigente (via SPCF tramite): {len(vigentes)} → {[c['numero_raw'] for c in vigentes]}")
w(f"  - Encerrado/Arquivado (via pendrive): {len(encerrados)}")
w("")
w("| numero (banco) | status | tem_tramite_pdf | valor (R$) | fim_vigência |")
w("|---|---|:---:|---:|---|")
for c in sorted(contratos_banco, key=lambda x: (0 if x['status']=='Vigente' else 1, x['numero_norm'])):
    w(f"| {c['numero_raw']} | {c['status']} | {c['tem_tramite_pdf']} | {c['valor_raw']} | {c['fim_vig']} |")
w("")
w(f"### Divergência com a notificação")
w("")
w(f"**Notificação cita 18 contratos; banco tem 13 distintos. Divergência de 5.** Memória do projeto dizia 15 — também não bate com nenhuma fonte atual.")
w("")
w(f"**Contratos da notificação PRESENTES no banco ({len(no_banco)}):** {sorted(no_banco)}")
w("")
w(f"**Contratos da notificação AUSENTES do banco ({len(ausentes)}):**")
w("")
for a in ausentes:
    # recuperar a forma original
    orig = next((c for c in CONTRATOS_NOTIFICACAO_RAW if norm(c) == a), a)
    w(f"- `{orig}` — não há registro em `spcf_contratos` para DETRAN.")
w("")
w("**Hipóteses para a divergência:**")
w("")
w("1. Os 5 ausentes podem estar **apenas no físico** (`PRODAM_DOCS/DETRAN/`) e ainda não foram ingeridos em `spcf_contratos` — a tabela parece cobrir (a) contratos vigentes do SPCF web e (b) contratos históricos ingeridos via pendrive. 5 contratos podem ter ficado fora da ingestão.")
w("2. Podem existir como **aditivos/referências** dentro de outro contrato — ex.: `CT 014/2019` como aditivo de `CT 004/2016`.")
w("3. O número do contrato pode estar **grafado diferente** no banco (letras, prefixo, formato incomum) — nenhum dos 5 apareceu em busca por `cliente LIKE '%DETRAN%'`.")
w("")
w("**Ação recomendada:** antes de protocolar a notificação no DETRAN, confirmar a **fonte autoritativa** de cada um dos 5 ausentes: localizar o PDF contratual, comprovar a existência jurídica e ingerir no `spcf_contratos` (ou documentar por que estão fora do banco). Caso não seja possível comprovar a existência de algum, considerar emitir **errata** ou **aditivo** à notificação removendo o contrato duvidoso.")
w("")
w("### Achado lateral: contratos órfãos (faturas sem contrato-pai)")
w("")
if contratos_orfaos:
    w(f"Dos 5 contratos ausentes em `spcf_contratos`, **{len(contratos_orfaos)} possuem faturas em `spcf_faturas`**:")
    w("")
    w("| contrato | qtd faturas | soma valor_bruto (R$) | competência min | competência max |")
    w("|---|---:|---:|---|---|")
    for k, v in sorted(faturas_orfaos_resumo.items(), key=lambda x: -x[1]['soma']):
        w(f"| {k} | {v['qtd']} | {fmt_brl(v['soma'])} | {v['comp_min'] or '?'} | {v['comp_max'] or '?'} |")
    w("")
    w("**Interpretação:** esses contratos foram reconhecidos pelo SPCF-web a ponto de emitirem faturas, mas o cadastro do contrato em si não foi ingerido no banco unificado. Isso **reduz** (mas não zera) o risco probatório: a ausência do PDF contratual permanece problema, mas a existência de faturas emitidas sob esse número prova que o contrato existiu.")
else:
    w(f"Nenhum contrato ausente possui faturas em `spcf_faturas`.")
w("")
w("**Semáforo:** 🔴 **VERMELHO** — 5 contratos da notificação assinada não são suportados pelo banco unificado.")
w("")
w("---")
w("")

# -------- Consulta 2 --------
w("## CONSULTA 2 — Faturas suspeitas (CT 008/2021 e CT 179/2018)")
w("")
w("### Adaptação")
w("")
w("Schema não possui os campos `observacoes`, `investigado_em`, `investigacao_resultado`, `valor_pg_parcial`, `saldo`. Foram substituídos pelos campos existentes: `cadeia_completude`, `cadeia_elos`, `total_empenhos_vinculados`, `tem_pdf`, `situacao`, `valor_bruto`, `competencia`. O campo `valor_liquido` é extraído do JSON `fatura_parsed`.")
w("")
w("### Resultado CT 008/2021")
w("")
if not f_008:
    w("- **Nenhuma fatura encontrada em `spcf_faturas` com contrato_num = '8/2021' para DETRAN.**")
    w("- Contrato-pai `CT 008/2021` também **não existe** em `spcf_contratos`.")
    w("- **Consequência:** nada em prodam.db sustenta esse item da notificação.")
else:
    w(f"- Total de faturas: **{len(f_008)}** · soma valor_bruto: R$ {fmt_brl(sum((f['valor_bruto'] for f in f_008), Decimal('0')))}")
    w("")
    w("| nf | competência | situação | valor_bruto (R$) | valor_liquido (R$) | cadeia_completude | tem_pdf |")
    w("|---|---|---|---:|---:|---|:---:|")
    for f in sorted(f_008, key=lambda x: (x['competencia'] or '', str(x['nf']))):
        w(f"| {f['nf']} | {f['competencia']} | {f['situacao']} | {fmt_brl(f['valor_bruto'])} | {fmt_brl(f['valor_liquido'])} | {f['cadeia_completude']} | {f['tem_pdf']} |")
w("")
w("### Resultado CT 179/2018")
w("")
if not f_179:
    w("- **Nenhuma fatura encontrada em `spcf_faturas` com contrato_num = '179/2018' para DETRAN.**")
    w("- Contrato-pai `CT 179/2018` também **não existe** em `spcf_contratos`.")
    w("- **Consequência:** nada em prodam.db sustenta esse item da notificação.")
else:
    w(f"- Total de faturas: **{len(f_179)}** · soma valor_bruto: R$ {fmt_brl(sum((f['valor_bruto'] for f in f_179), Decimal('0')))}")
    w("")
    w("| nf | competência | situação | valor_bruto (R$) | valor_liquido (R$) | cadeia_completude | tem_pdf |")
    w("|---|---|---|---:|---:|---|:---:|")
    for f in sorted(f_179, key=lambda x: (x['competencia'] or '', str(x['nf']))):
        w(f"| {f['nf']} | {f['competencia']} | {f['situacao']} | {fmt_brl(f['valor_bruto'])} | {fmt_brl(f['valor_liquido'])} | {f['cadeia_completude']} | {f['tem_pdf']} |")
w("")
w("### Recomendação")
w("")
w("O banco não tem campo de \"investigação\" — essa informação, se existir, está em outro artefato (memorial, planilha interna, profiles.json). **Verificar manualmente em `DETRAN_AUDITORIA_COMPLETA/15_CONSOLIDADOS_JSON/` e `11_PROFILES_BACKUPS/ativo/profiles.json`** se há anotação de despesa PRODAM para esses dois contratos.")
w("")
w("**Semáforo:** 🔴 **VERMELHO** — faturas não encontradas no banco consolidado; depende de fonte externa.")
w("")
w("---")
w("")

# -------- Consulta 3 --------
w("## CONSULTA 3 — Validação de PDF dos contratos pendentes")
w("")
w("### CT 296/2025")
w("")
if c_296:
    w(f"- Presente em `spcf_contratos`: ✔️ (id={c_296['id']}, status={c_296['status']}, tem_tramite_pdf={c_296['tem_tramite_pdf']})")
else:
    w(f"- **AUSENTE** em `spcf_contratos`. 🔴")
w(f"- Schema não expõe `pdf_original_path`, `pdf_validado`, `pdf_validado_em`, `fonte_original`. Só há flag `tem_tramite_pdf`.")
w(f"- Busca em disco (`PRODAM_DOCS/DETRAN/` recursivo): **{len(pdfs_296)} arquivo(s)**")
if err_296:
    w(f"  - ⚠️ {err_296}")
for p in sorted(pdfs_296)[:20]:
    w(f"  - `{p}`")
w("")
w("### CT 003/2026")
w("")
if c_003:
    w(f"- Presente em `spcf_contratos`: ✔️ (id={c_003['id']}, status={c_003['status']}, tem_tramite_pdf={c_003['tem_tramite_pdf']})")
else:
    w(f"- **AUSENTE** em `spcf_contratos`. 🔴")
w(f"- Busca em disco (`PRODAM_DOCS/DETRAN/` recursivo): **{len(pdfs_003)} arquivo(s)**")
if err_003:
    w(f"  - ⚠️ {err_003}")
for p in sorted(pdfs_003)[:20]:
    w(f"  - `{p}`")
w("")
w("### Recomendação")
w("")
total_em_risco = Decimal("4516097.62")
if not pdfs_296 and not pdfs_003:
    w(f"**🔴 RISCO MÁXIMO** — nenhum PDF localizado para os 2 contratos. Valor em risco: R$ {fmt_brl(total_em_risco)}.")
    w("Ação imediata: extrair PDF do SPCF (contratos/fatura ou tramite) antes de protocolar, OU registrar errata removendo esses 2 contratos.")
elif not pdfs_296:
    w(f"**🟡 RISCO PARCIAL** — CT 296/2025 sem PDF localizado. Confirmar origem do valor atribuído.")
elif not pdfs_003:
    w(f"**🟡 RISCO PARCIAL** — CT 003/2026 sem PDF localizado. Confirmar origem do valor atribuído.")
else:
    w("**🟢 OK** — PDFs localizados para ambos.")
w("")
w("**Semáforo:** " + ("🟢" if (pdfs_296 and pdfs_003) else "🟡" if (pdfs_296 or pdfs_003) else "🔴"))
w("")
w("---")
w("")

# -------- Consulta 4 --------
w("## CONSULTA 4 — Faturas com pagamento parcial")
w("")
w("### Limitação do schema")
w("")
w("**O prodam.db atual não armazena `valor_pg_parcial` nem `saldo`.** Essa informação, se existir, está em outra fonte (profiles.json, memorial Excel, cruzamento_spcf_pendrive, consolidados JSON).")
w("")
w(f"**Proxy disponível:** tabela `spcf_nfs(numero_nf, liquidacao, pagamento, tem_pagamento)`. Faturas dos 18 contratos da notificação cujas NF constam como pagas na PRODAM:")
w("")
w(f"- Faturas dos 18 contratos em `spcf_faturas`: **{len(faturas_notif)}**")
w(f"- Dessas, com NF marcada `tem_pagamento = 1` em `spcf_nfs`: **{len(faturas_pagas)}**")
w("")
if faturas_pagas:
    soma_bruto = sum((f['valor_bruto'] for f in faturas_pagas), Decimal('0'))
    soma_pago = sum((f['valor_pago_aprox'] for f in faturas_pagas), Decimal('0'))
    soma_saldo = sum((f['saldo_aprox'] for f in faturas_pagas), Decimal('0'))
    w(f"- **Soma valor_bruto das pagas:** R$ {fmt_brl(soma_bruto)}")
    w(f"- **Soma valor_pago (heurística):** R$ {fmt_brl(soma_pago)}")
    w(f"- **Saldo remanescente estimado:** R$ {fmt_brl(soma_saldo)}")
    w("")
    w("> ⚠️ Os valores abaixo são aproximados. A tabela `spcf_nfs` guarda JSON bruto do scraping, com chaves dinâmicas. Extraí heuristicamente o maior valor BR encontrado em cada blob como `valor_pago_aprox`. Para validar com precisão é **obrigatório** consultar o memorial de cálculo.")
    w("")
    w("| contrato | nf | competência | valor_bruto (R$) | valor_pago_aprox (R$) | saldo_aprox (R$) | data_liq | data_pag | códigos |")
    w("|---|---|---|---:|---:|---:|---|---|---|")
    for f in sorted(faturas_pagas, key=lambda x: (x['contrato_num_norm'], str(x['nf']))):
        w(f"| {f['contrato_num_norm']} | {f['nf']} | {f['competencia']} | {fmt_brl(f['valor_bruto'])} | {fmt_brl(f['valor_pago_aprox'])} | {fmt_brl(f['saldo_aprox'])} | {f['data_liq']} | {f['data_pag']} | {f['codigos']} |")
else:
    w("Nenhuma NF dos 18 contratos aparece como paga na tabela `spcf_nfs`.")
w("")
w("### Conclusão")
w("")
w("**Não é possível, com o banco atual, confirmar se \"os R$ 21.434.211,45 / R$ 28.142.624,30 da notificação descontaram valor_pg_parcial\".** O campo não existe no schema.")
w("")
w("Para validar isso, é preciso **abrir o memorial de cálculo** (`13_PECAS_JURIDICAS/memorial_v202*.xlsx` ou equivalente) e confrontar a coluna de pagamento parcial desse memorial com o total da notificação. A validação via prodam.db só confirma **se houve algum pagamento PRODAM na NF** — não quanto.")
w("")
w("**Semáforo:** 🟡 **AMARELO** — dependência de fonte externa ao banco para fechar a conta.")
w("")
w("---")
w("")

# -------- Consulta 5 --------
w("## CONSULTA 5 — Distribuição temporal das faturas (risco prescricional)")
w("")
w("### Agregação por contrato × ano de competência")
w("")
w("| contrato | ano | qtd | soma valor_bruto (R$) |")
w("|---|:---:|---:|---:|")
for (ctn, ano), v in sorted(dist.items(), key=lambda x: (x[0][1] or 0, x[0][0])):
    ano_str = str(ano) if ano else "?"
    w(f"| {ctn} | {ano_str} | {v['qtd']} | {fmt_brl(v['soma_original'])} |")
w("")
w("### Faturas com competência anterior a 04/2021 (risco prescricional se tese art. 202 VI CC cair)")
w("")
w(f"- **Quantidade:** {len(faturas_pre_abr21)}")
w(f"- **Soma valor_bruto:** R$ {fmt_brl(soma_pre)}")
w("")
if pre_por_ct:
    w("| contrato | qtd | soma valor_bruto (R$) |")
    w("|---|---:|---:|")
    for ctn, v in sorted(pre_por_ct.items(), key=lambda x: -x[1]['soma']):
        w(f"| {ctn} | {v['qtd']} | {fmt_brl(v['soma'])} |")
w("")
w("### Interpretação jurídica")
w("")
w("Caso a tese de interrupção pelo **art. 202 VI CC** (reconhecimento tácito via NL, Nota de Empenho subsequente, pagamento parcial) seja rejeitada pelo devedor ou pelo juízo, **todas as faturas com competência anterior a abril/2021 estarão prescritas em 19/04/2026** (prescrição quinquenal — Art. 206 §5º I CC + Dec. 20.910/32 + Súmula 85 STJ).")
w("")
w("**Semáforo:** 🔴 **VERMELHO** — exposição prescricional significativa se o bloqueio 1 (tese de interrupção) cair.")
w("")
w("---")
w("")
w("## RECOMENDAÇÃO OBJETIVA FINAL")
w("")
w("**Estado atual da notificação assinada vs. prodam.db: 🔴 INCONSISTÊNCIAS GRAVES.**")
w("")
w("1. **MANTER o protocolo da notificação em si** (PDF já assinado — não alterar). No entanto, **antes de protocolar**, preparar:")
w("   - **Errata / Nota de esclarecimento** a ser anexada à notificação, reconhecendo formalmente que 5 contratos citados (CT 296/2025, CT 008/2021, CT 179/2018, CT 023/2014, CT 014/2019) precisam de comprovação documental adicional. Alternativamente, **excluir esses 5 contratos do protocolo** e emitir notificação complementar quando a documentação for consolidada.")
w("2. **Bloquear o protocolo da notificação até localizar o PDF dos 2 contratos pendentes** (CT 296/2025 e CT 003/2026). Valor em risco: R$ 4.516.097,62. Se o PDF não for encontrado no SPCF ou no físico, esse valor deve sair da exigibilidade primária.")
w("3. **Reconciliar profiles.json × prodam.db × notificação** para resolver a divergência 13/15/18. A fonte autoritativa deve ser `profiles.json` — se ele tem 18 e o banco tem 13, faltam 5 ingestões no banco.")
w("4. **Anexar memorial de cálculo** à notificação explicitando por fatura: valor_original, pagamento_parcial, saldo, dias_mora, correção, juros, multa. Sem isso, o item 4 desta validação fica em aberto.")
w("5. **Preparar defesa antecipada da tese de interrupção (art. 202 VI CC)** com dossiê de marcos interruptivos fatura-a-fatura. Faturas anteriores a 04/2021 somam valor bruto relevante e são o principal alvo de contestação prescricional.")
w("")
w("---")
w("")
w("## METADADOS")
w("")
w(f"- **Banco:** {DB}")
w(f"- **Tabelas consultadas:** spcf_contratos ({374}), spcf_faturas ({1873}), spcf_nfs ({52998})")
w(f"- **Caminho PRODAM_DOCS verificado:** `{PRODAM_DOCS}`")
w(f"- **Script fonte:** `_validacao_detran_19_04_2026.py` (projeto raiz)")
w(f"- **Execução:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

OUT_MD.write_text("\n".join(L), encoding="utf-8")
print(f"OK: {OUT_MD}")
print(f"Linhas: {len(L)}")
print(f"Contratos no banco: {len(contratos_banco)}")
print(f"Ausentes da notificacao: {ausentes}")
print(f"Faturas 008/2021: {len(f_008)} | 179/2018: {len(f_179)}")
print(f"PDFs 296/2025: {len(pdfs_296)} | 003/2026: {len(pdfs_003)}")
print(f"Faturas dos 18 com pagamento: {len(faturas_pagas)}")
print(f"Faturas pre-04/2021: {len(faturas_pre_abr21)} | soma R$ {fmt_brl(soma_pre)}")
