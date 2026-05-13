"""
Reclassifica os PDFs DETRAN usando PATH como fonte primaria (filesystem ja
esta organizado por tipo) + overrides textuais quando o path for ambiguo.

O classificador generico (ocr-pdfs-prodam/classificador_conteudo.py) erra
sistematicamente porque NEs/NFs referenciam contratos no texto, disparando
match de CONTRATO/TA. Exemplo: empenho_10012_DETRAN.pdf classificado como
TA 03/2018 — absurdo.

Regra: PATH > filename > texto.

Le: _OUT_inventario_detran_externo_*/classificados.csv (o original errado)
Escreve: _OUT_reclassificacao_path_<ts>/classificados_reclass.csv
         + renomear_proposto_reclass.csv
         + relatorio_reclass.md
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
import traceback
from collections import Counter
from datetime import datetime
from pathlib import Path

RAIZ_PROJETO = Path(r"C:\Users\gabri\Desktop\PROJETO_PRODAM")


# -----------------------------------------------------------------------
# Regras de classificacao por PATH (prioridade maxima)
# -----------------------------------------------------------------------
# Cada tupla: (regex_path, tipo_canonico, fonte_extracao_numero)
REGRAS_PATH = [
    # DETRAN_CONSOLIDADO subpastas (estrutura canonica — prioridade maxima)
    (r"DETRAN_CONSOLIDADO[\\/]01_CONTRATOS[\\/]",       "CONTRATO_OU_TA", "texto"),
    (r"DETRAN_CONSOLIDADO[\\/]02_EMPENHOS[\\/]",        "NE",        "texto"),
    (r"DETRAN_CONSOLIDADO[\\/]03_FATURAS[\\/]",         "NF",        "texto"),
    (r"DETRAN_CONSOLIDADO[\\/]04_NOTAS_LIQUIDACAO[\\/]", "NL",       "texto"),
    (r"DETRAN_CONSOLIDADO[\\/]05_ACEITES[\\/]",         "ACEITE",    "texto"),
    (r"DETRAN_CONSOLIDADO[\\/]06_COBRANCAS[\\/]",       "COBRANCA",  "texto"),
    (r"DETRAN_CONSOLIDADO[\\/]07_SCRAPING_SPCF[\\/]",   "SPCF_CSV",  "texto"),
    (r"DETRAN_CONSOLIDADO[\\/]08_PDFS_ORIGINAIS[\\/]",  "CERTIDAO_OU_OUTRO", "texto"),
    (r"DETRAN_CONSOLIDADO[\\/]09_RELATORIOS[\\/]",      "RELATORIO", "texto"),
    # DETRAN raiz (so 1 arquivo)
    (r"PRODAM_DOCS[\\/]DETRAN[\\/]",                    "RELATORIO", "filename"),

    # SPCF_EXTRACAO subpastas de topo (estrutura original SPCF)
    (r"[\\/]SPCF_EXTRACAO[\\/]pdfs_empenhos[\\/]",     "NE",        "filename"),
    (r"[\\/]SPCF_EXTRACAO[\\/]pdfs_oficiais_SPCF[\\/]", "SPCF_OFICIAL", "filename"),
    (r"[\\/]SPCF_EXTRACAO[\\/]pdfs_convertidos[\\/]",   "SPCF_CONVERTIDO", "filename"),
    (r"[\\/]SPCF_EXTRACAO[\\/]htmls_brutos[\\/]",       "SPCF_HTML", "filename"),

    # Padroes genericos em qualquer profundidade (SPCF aninhado, pdfs_gerados, etc)
    # Ordem: mais especifico primeiro
    (r"[\\/]pdfs_empenhos[\\/]",        "NE",       "filename"),
    (r"[\\/]pdfs_gerados[\\/]empenhos[\\/]", "NE",  "filename"),
    (r"[\\/]pdfs_gerados[\\/]contratos[\\/]", "CONTRATO", "filename"),
    (r"[\\/]pdfs_gerados[\\/]faturas[\\/]",   "FATURA",   "filename"),
    (r"[\\/]pdfs_oficiais_SPCF[\\/]",    "SPCF_OFICIAL", "filename"),
    (r"[\\/]pdfs_convertidos[\\/]",      "SPCF_CONVERTIDO", "filename"),
    (r"[\\/]htmls_brutos[\\/]",          "SPCF_HTML", "filename"),
    (r"[\\/]empenhos[\\/]",              "NE",       "filename"),
    (r"[\\/]faturas[\\/]",               "FATURA",   "filename"),
    (r"[\\/]contratos[\\/]",             "CONTRATO", "filename"),
    (r"[\\/]cobrancas?[\\/]",            "COBRANCA", "filename"),
    (r"[\\/]aceites?[\\/]",              "ACEITE",   "filename"),
    (r"[\\/]certid[oõ]es?[\\/]",         "CERTIDAO", "filename"),
    (r"[\\/]notas?_liquidacao[\\/]",     "NL",       "filename"),
    # Fallback: qualquer pasta com "pdfs" e contendo DETRAN no path
    (r"[\\/]SPCF_EXTRACAO[\\/]pdfs[\\/]", "SPCF_DIVERSO", "filename"),
]


# -----------------------------------------------------------------------
# Fallback por FILENAME (quando path nao bate)
# -----------------------------------------------------------------------
REGRAS_FILENAME = [
    (re.compile(r"empenho[_\-\s]", re.IGNORECASE),    "NE"),
    (re.compile(r"^NE[_\-\s]?\d",  re.IGNORECASE),    "NE"),
    (re.compile(r"^fatura[_\-\s]", re.IGNORECASE),    "FATURA"),
    (re.compile(r"NFSe?[_\-\s\.]?n?[oº°\.]?[_\-\s]?\d", re.IGNORECASE), "NF"),
    (re.compile(r"^contrato[_\-\s]", re.IGNORECASE),  "CONTRATO"),
    (re.compile(r"^CT[_\-]\d",      re.IGNORECASE),   "CONTRATO"),
    (re.compile(r"termo.aditivo|\bTA[_\-\s]\d", re.IGNORECASE), "TA"),
    (re.compile(r"aceite|atesto",   re.IGNORECASE),   "ACEITE"),
    (re.compile(r"cobranca|cobrança|oficio.?cobr", re.IGNORECASE), "COBRANCA"),
    (re.compile(r"CND|certid[ãa]o|FGTS|trabalhista|fal[eê]ncia", re.IGNORECASE), "CERTIDAO"),
    (re.compile(r"liquidacao|\bNL\d|\d{4}NL\d", re.IGNORECASE), "NL"),
    (re.compile(r"proposta",        re.IGNORECASE),   "PROPOSTA"),
    (re.compile(r"relat[oó]rio|dashboard|auditoria", re.IGNORECASE), "RELATORIO"),
]


# -----------------------------------------------------------------------
# Regex para extrair numeros dos filenames SPCF
# -----------------------------------------------------------------------
RE_EMPENHO_FILENAME = re.compile(r"empenho_(\d+)_", re.IGNORECASE)
RE_FATURA_FILENAME = re.compile(r"fatura_(\d+)_", re.IGNORECASE)
RE_CONTRATO_FILENAME = re.compile(r"contrato_(?:DETRAN_)?(\d+)", re.IGNORECASE)
RE_NFSE_FILENAME = re.compile(r"NFSe?[\s_]?n?[oº°\.]?[\s_]?(\d+)", re.IGNORECASE)


# -----------------------------------------------------------------------
# Regex para conteudo (quando path e ambiguo)
# -----------------------------------------------------------------------
RE_NE_TEXTO = re.compile(r"(\d{4})NE(\d{5})")
RE_NL_TEXTO = re.compile(r"(\d{4})NL(\d{5})")
RE_NF_TEXTO = re.compile(r"NOTA\s+FISCAL|NFSe\b|NF\s*n?[ºo°\.]?\s*\d")
RE_CONTRATO_TEXTO = re.compile(r"CONTRATO\s+0*\d+[/.-]\d{2,4}", re.IGNORECASE)
RE_TA_TEXTO = re.compile(r"TERMO\s+ADITIVO|ADITIVO\s+CONTRATUAL|\d\s*[ºo°]?\s*TA", re.IGNORECASE)


def normalizar_path(p: str) -> str:
    """Substitui todos os separadores por / para uniformizar regex."""
    return p.replace("\\", "/")


def classificar_por_path(caminho: str) -> tuple[str, str]:
    """Retorna (tipo, fonte_numero) baseado no path.
    Se nao houver match, retorna ('INDETERMINADO', 'texto').
    """
    for padrao, tipo, fonte in REGRAS_PATH:
        if re.search(padrao, caminho, re.IGNORECASE):
            return tipo, fonte
    return "INDETERMINADO", "texto"


def classificar_por_filename(nome: str) -> str | None:
    """Fallback: usa filename quando path nao bate. Retorna None se nao resolver."""
    for regex, tipo in REGRAS_FILENAME:
        if regex.search(nome):
            return tipo
    return None


def extrair_numero_spcf(nome: str, tipo: str) -> str:
    """Extrai numero canonico de filenames SPCF."""
    if tipo == "NE":
        m = RE_EMPENHO_FILENAME.search(nome)
        if m:
            return m.group(1)
    elif tipo == "FATURA":
        m = RE_FATURA_FILENAME.search(nome)
        if m:
            return m.group(1)
    elif tipo == "CONTRATO":
        m = RE_CONTRATO_FILENAME.search(nome)
        if m:
            return m.group(1)
    elif tipo.startswith("SPCF_"):
        m = RE_EMPENHO_FILENAME.search(nome) or RE_FATURA_FILENAME.search(nome)
        if m:
            return m.group(1)
    return ""


def resolver_contrato_ou_ta(nome: str) -> str:
    """Decide entre CONTRATO e TA quando o path e ambiguo (01_CONTRATOS)."""
    n = nome.upper()
    if ("TERMO ADITIVO" in n or "ADITIVO" in n
            or re.search(r"\d\s*[ºo°]?\s*TA\b", n)
            or re.search(r"^\d+[ºo°]?\s*TA", n)):
        return "TA"
    if "PROPOSTA" in n and "TA" not in n:
        return "PROPOSTA"
    return "CONTRATO"


def resolver_certidao_ou_outro(nome: str) -> str:
    """Decide subtipo quando o path e 08_PDFS_ORIGINAIS (ambiguo)."""
    n = nome.upper()
    if any(t in n for t in ("CND", "CERTIDAO", "CERTIDÃO", "FGTS",
                            "TRABALHISTA", "FALENCIA", "FALÊNCIA",
                            "SEFAZ", "DEBITOS", "DÉBITOS")):
        return "CERTIDAO"
    return "OUTRO"


def hash6(nome: str, size: int) -> str:
    s = f"{nome}|{size}"
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:6]


def gerar_nome_canonico(row: dict) -> str:
    """Gera nome canonico baseado em tipo final + numero + orgao + data."""
    tipo = row["tipo_reclass"]
    num = row.get("numero_reclass", "")
    orgao = row.get("orgao", "DETRAN") or "DETRAN"
    data = row.get("data", "")
    try:
        size = int(row.get("size_bytes", 0) or 0)
    except ValueError:
        size = 0
    h = hash6(row["nome"], size)

    # NE em SPCF
    if tipo == "NE" and num:
        if data:
            return f"NE-{data[:4]}-ID{num}_{orgao}_{data}_{h}.pdf"
        return f"NE-ID{num}_{orgao}_{h}.pdf"

    # Fatura em SPCF
    if tipo == "FATURA" and num:
        if data:
            return f"FAT-ID{num}_{orgao}_{data}_{h}.pdf"
        return f"FAT-ID{num}_{orgao}_{h}.pdf"

    # Contrato do filesystem SPCF
    if tipo == "CONTRATO" and num:
        return f"CT-ID{num}_{orgao}_{h}.pdf"

    # SPCF oficial/convertido/HTML — categoria bruta, preservar ID original
    if tipo.startswith("SPCF_") and num:
        sub = tipo.replace("SPCF_", "")
        return f"SPCF-{sub}-ID{num}_{orgao}_{h}.pdf"

    # DETRAN_CONSOLIDADO — usar tipo + numero_texto (vindo do classificador)
    if tipo in ("NE", "NL", "NF", "ACEITE", "COBRANCA", "CONTRATO", "TA",
                "PROPOSTA", "CERTIDAO"):
        partes = [tipo]
        if num:
            partes.append(num.replace("/", "-").replace(".", "-"))
        if orgao and orgao != "DETRAN":
            partes.append(orgao)
        if data:
            partes.append(data)
        partes.append(h)
        return "_".join(partes) + ".pdf"

    # INDETERMINADO / RELATORIO / OUTRO
    return f"{tipo}_{h}.pdf"


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    saida = RAIZ_PROJETO / f"_OUT_reclassificacao_path_{ts}"
    saida.mkdir(parents=True, exist_ok=True)
    log_path = saida / "progresso.log"

    def log(msg):
        linha = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        print(linha, flush=True)

    log(f"Saida: {saida}")

    # Achar classificados.csv mais recente
    candidatos = sorted(
        RAIZ_PROJETO.glob("_OUT_inventario_detran_externo_*/classificados.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidatos:
        log("[ERRO] Nenhum classificados.csv encontrado.")
        return

    classif_csv = candidatos[0]
    universo_csv = classif_csv.parent / "universo.csv"
    log(f"Classificados original: {classif_csv}")

    # Ler universo (tem size_bytes, paginas, tem_texto)
    universo_map = {}
    if universo_csv.exists():
        with open(universo_csv, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                universo_map[row["caminho"]] = row

    # Ler classificados originais e reclassificar
    reclass_rows: list[dict] = []
    with open(classif_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            caminho = row["caminho"]
            nome = row["nome"]
            path_norm = normalizar_path(caminho)
            tipo_orig = row.get("tipo", "")
            confianca_orig = row.get("confianca", "0")

            # Classificar por path
            tipo_path, fonte = classificar_por_path(path_norm)

            # Fallback por filename quando path nao resolveu
            fonte_tipo = "path"
            if tipo_path == "INDETERMINADO":
                t_fn = classificar_por_filename(nome)
                if t_fn:
                    tipo_path = t_fn
                    fonte = "filename"
                    fonte_tipo = "filename"

            # Resolver ambiguidades
            tipo_final = tipo_path
            if tipo_path == "CONTRATO_OU_TA":
                tipo_final = resolver_contrato_ou_ta(nome)
            elif tipo_path == "CERTIDAO_OU_OUTRO":
                tipo_final = resolver_certidao_ou_outro(nome)

            # Extrair numero por filename (SPCF) ou manter numero do texto (DETRAN_CONSOLIDADO)
            if fonte == "filename":
                numero_reclass = extrair_numero_spcf(nome, tipo_final)
            else:
                numero_reclass = row.get("numero", "")

            # Tamanho do universo.csv
            u = universo_map.get(caminho, {})
            size_bytes = u.get("size_bytes", "0")

            reclass = {
                "caminho": caminho,
                "nome": nome,
                "raiz": row.get("raiz", ""),
                "tipo_original": tipo_orig,
                "confianca_original": confianca_orig,
                "tipo_reclass": tipo_final,
                "numero_reclass": numero_reclass,
                "orgao": row.get("orgao", "DETRAN"),
                "data": row.get("data", ""),
                "size_bytes": size_bytes,
                "mudou": int(tipo_orig != tipo_final),
                "fonte_tipo": fonte_tipo,
            }
            reclass_rows.append(reclass)

    # Tambem varrer PDFs sem texto (nao estavam em classificados.csv)
    sem_texto = 0
    if universo_csv.exists():
        ja_incluidos = {r["caminho"] for r in reclass_rows}
        with open(universo_csv, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                caminho = row["caminho"]
                if caminho in ja_incluidos:
                    continue
                if row.get("tem_texto") != "0":
                    continue
                nome = row["nome"]
                path_norm = normalizar_path(caminho)
                tipo_path, fonte = classificar_por_path(path_norm)
                fonte_tipo = "path_sem_texto"
                if tipo_path == "INDETERMINADO":
                    t_fn = classificar_por_filename(nome)
                    if t_fn:
                        tipo_path = t_fn
                        fonte = "filename"
                        fonte_tipo = "filename_sem_texto"
                tipo_final = tipo_path
                if tipo_path == "CONTRATO_OU_TA":
                    tipo_final = resolver_contrato_ou_ta(nome)
                elif tipo_path == "CERTIDAO_OU_OUTRO":
                    tipo_final = resolver_certidao_ou_outro(nome)
                numero_reclass = (extrair_numero_spcf(nome, tipo_final)
                                  if fonte == "filename" else "")
                reclass_rows.append({
                    "caminho": caminho,
                    "nome": nome,
                    "raiz": row.get("raiz", ""),
                    "tipo_original": "SEM_TEXTO",
                    "confianca_original": "0",
                    "tipo_reclass": tipo_final,
                    "numero_reclass": numero_reclass,
                    "orgao": "DETRAN",
                    "data": "",
                    "size_bytes": row.get("size_bytes", "0"),
                    "mudou": 1,
                    "fonte_tipo": fonte_tipo,
                })
                sem_texto += 1
    log(f"PDFs sem texto adicionados: {sem_texto}")

    # Gravar classificados reclass
    cols = ["caminho", "nome", "raiz", "tipo_original", "confianca_original",
            "tipo_reclass", "numero_reclass", "orgao", "data", "size_bytes",
            "mudou", "fonte_tipo"]
    out_class = saida / "classificados_reclass.csv"
    with open(out_class, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in reclass_rows:
            w.writerow(r)
    log(f"  gravado: {out_class}  ({len(reclass_rows)} linhas)")

    # Gerar propostas de renomeacao
    renomear_rows = []
    for r in reclass_rows:
        nome_novo = gerar_nome_canonico(r)
        if nome_novo == r["nome"]:
            continue
        if r["tipo_reclass"] == "INDETERMINADO":
            continue
        renomear_rows.append({
            "caminho_original": r["caminho"],
            "nome_original": r["nome"],
            "nome_proposto": nome_novo,
            "raiz": r["raiz"],
            "tipo_reclass": r["tipo_reclass"],
            "tipo_original": r["tipo_original"],
            "mudou_tipo": r["mudou"],
            "numero": r["numero_reclass"],
            "orgao": r["orgao"],
            "data": r["data"],
        })

    out_ren = saida / "renomear_proposto_reclass.csv"
    cols = ["caminho_original", "nome_original", "nome_proposto", "raiz",
            "tipo_reclass", "tipo_original", "mudou_tipo", "numero", "orgao", "data"]
    with open(out_ren, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in renomear_rows:
            w.writerow(r)
    log(f"  gravado: {out_ren}  ({len(renomear_rows)} propostas)")

    # Relatorio
    tipos_orig = Counter(r["tipo_original"] for r in reclass_rows)
    tipos_reclass = Counter(r["tipo_reclass"] for r in reclass_rows)
    mudancas = Counter(
        (r["tipo_original"], r["tipo_reclass"])
        for r in reclass_rows if r["mudou"]
    )

    linhas = [
        "# Reclassificacao por PATH — PDFs DETRAN externos",
        "",
        f"**Data:** {datetime.now().isoformat(timespec='seconds')}",
        f"**Input:** {classif_csv}",
        f"**PDFs reclassificados:** {len(reclass_rows)}",
        f"**Propostas de renomeacao:** {len(renomear_rows)}",
        f"**PDFs sem texto incluidos:** {sem_texto}",
        "",
        "## Comparacao: tipo_original vs tipo_reclass",
        "",
        "### Tipos originais (classificador generico)",
        "| Tipo | Qtd |",
        "|---|---:|",
    ]
    for t, n in tipos_orig.most_common():
        linhas.append(f"| {t} | {n} |")

    linhas += [
        "",
        "### Tipos reclass (PATH-based)",
        "| Tipo | Qtd |",
        "|---|---:|",
    ]
    for t, n in tipos_reclass.most_common():
        linhas.append(f"| {t} | {n} |")

    linhas += [
        "",
        "## Matriz de mudancas (top 20)",
        "| Original -> Reclass | Qtd |",
        "|---|---:|",
    ]
    for (orig, novo), n in mudancas.most_common(20):
        linhas.append(f"| {orig or '(vazio)'} -> {novo} | {n} |")

    linhas += [
        "",
        "## Proximos passos",
        "1. Revisar `renomear_proposto_reclass.csv`",
        "2. Se OK: rodar aplicador de renomeacao (renomeador-pdfs-prodam em modo --apply)",
        "3. Preservar log de mapeamento SHA-256 antes de aplicar in-place",
        "",
    ]
    out_rel = saida / "relatorio_reclass.md"
    with open(out_rel, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    log(f"  gravado: {out_rel}")

    log(f"\nTERMINOU. {len(reclass_rows)} PDFs reclassificados, {len(renomear_rows)} propostas.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
