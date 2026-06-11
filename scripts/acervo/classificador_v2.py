#!/usr/bin/env python3
"""
Classificador de conteudo v2 — PRODAM (portado de DETRAN_AUDITORIA_COMPLETA).

Origem: DETRAN_AUDITORIA_COMPLETA/10_SCRIPTS_PYTHON/classificador_v2.py
Mudancas no porte:
  - Lista de orgaos virou parametro (`orgaos=`) com default ORGAOS_DEFAULT
    (lista original do DETRAN; SEDUC ja constava e permanece).
  - Nenhuma outra alteracao funcional — puro Python/regex, sem I/O.

Melhorias sobre o v1 da skill ocr-pdfs-prodam:
1. Detecta "pagina de assinatura e-Doc Amazonas" (primeira pagina que e so
   carimbo digital) e usa a proxima pagina com conteudo real.
2. 16 tipos de documento, com padroes de CABECALHO especificos
   (nao apenas mencao interna).
3. Extrai numero canonico por tipo (NE=YYYYNEnnnn, Carta=NN-GECOB, Oficio=NN/AAAA).
4. Usa pasta como hint forte (06_COBRANCAS_OFICIOS sugere CARTA/OFICIO;
   02_NOTAS_EMPENHO sugere NE; 04_FATURAS sugere NF).
5. Tolerante a encoding corrompido (OF[IÍ�]CIO casa acentos quebrados).
6. Retorna paginas_usadas (para auditoria).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional


# ------------------------------------------------------------
# Orgaos (default = lista original DETRAN; SEDUC ja incluso)
# ------------------------------------------------------------
ORGAOS_DEFAULT = [
    "DETRAN", "PRODAM", "SES", "SUSAM", "SSP", "SEAP", "SEAD", "SEDUC",
    "SEFAZ", "SEJUSC", "SEIC", "SEMA", "SEC", "SEPLAN", "SEJEL",
    "FVS", "FHAJ", "FUHAM", "FUSEAM", "FCECON", "SUHAB", "SUFRAMA",
    "IPAAM", "IDAM", "AGEMS", "AFEAM", "AMAZONPREV",
    "TJ-AM", "TJAM", "TCE-AM", "TCEAM", "PGE-AM", "DPE-AM", "MP-AM",
    "CBMAM", "PCAM", "PMM", "ALE-AM", "PMAM", "HPS", "UEA", "FAPEAM", "ADS",
]


def compilar_re_orgaos(orgaos: Optional[list[str]] = None) -> re.Pattern:
    """Compila o regex de orgaos a partir da lista informada (default ORGAOS_DEFAULT)."""
    lista = list(orgaos) if orgaos else list(ORGAOS_DEFAULT)
    return re.compile(r"\b(" + "|".join(re.escape(o) for o in lista) + r")\b", re.IGNORECASE)


RE_ORGAO = compilar_re_orgaos()


# ------------------------------------------------------------
# Detector de pagina de assinatura e-Doc Amazonas
# ------------------------------------------------------------
RE_EDOC_HINTS = [
    re.compile(r"autenticidade\s+deste\s+documento", re.IGNORECASE),
    re.compile(r"c[ó�o]digo\s+verificador", re.IGNORECASE),
    re.compile(r"edoc\.amazonas\.am\.gov\.br"),
    re.compile(r"CRC:\s*[0-9A-F]{8}"),
    # Texto invertido por pdfplumber (palavras viradas ao contrario):
    re.compile(r"\brodacifireV\b"),        # "Verificador"
    re.compile(r"\bemrofnoc\b"),           # "conforme"
    re.compile(r"\bodanissA\b"),           # "Assinado"
    re.compile(r"\betnemlatigid\b"),       # "digitalmente"
    re.compile(r"\.1002/80/42ed"),         # fragmento da MP 2.200-2 invertido
    # Assinatura MP 2.200-2 em formato padrao Brasil
    re.compile(r"MP\s*2\.?200-?2\s+de\s+24/08/2001", re.IGNORECASE),
    re.compile(r"conforme\s+MP\s*n[oº°].?\s*2\.?200-?2", re.IGNORECASE),
]


PALAVRAS_CHAVE_DOCUMENTO = [
    r"Ao Senhor", r"Ao Senhora", r"Senhor Diretor", r"A Vossa", r"A V\.?Sa",
    r"\bsolicita\b", r"SOLICITAMOS", r"OF[IÍ�]CIO", r"NOTIFICA",
    r"Nota de Empenho", r"Nota de Liquida", r"NOTA FISCAL",
    r"Carta Cobran", r"Carta Circular", r"\bCONTRATO\b", r"TERMO ADITIVO",
    r"TERMO DE RECONHECIMENTO", r"PROPOSTA COMERCIAL", r"ACEITE\s+T[EÉ�]CNICO",
    r"ATESTO\s+T[EÉ�]CNICO", r"CERTID[AÃ�]O",
    r"Processo\s+n[º°o]\s*\d", r"Secretaria", r"PREFEITURA",
    r"GOVERNO DO ESTADO", r"REQUERIMENTO", r"RELAT[ÓO�]RIO",
    r"RECIBO", r"DEMONSTRATIVO", r"DANFE", r"NFS-?e",
    # Citacoes formais
    r"CNPJ\s*(?:sob\s+)?(?:o\s+)?n[º°o]", r"Inscri[cç�]",
]
RE_PALAVRAS_DOC = re.compile("|".join(PALAVRAS_CHAVE_DOCUMENTO), re.IGNORECASE)


def is_pagina_assinatura(txt: str) -> bool:
    """True se a pagina e SO carimbo e-Doc, sem conteudo real.

    Estrategia v2.2:
      1. Vazia ou muito curta (< 80 chars) -> assinatura.
      2. Tem hints e-Doc (2+) E nao tem palavras-chave documentais -> assinatura.
      3. Tem palavra-chave documental forte -> NAO e assinatura (regardless of size).
      4. Ratio embaralhamento alto E poucos chars uteis -> assinatura.
    """
    if not txt or len(txt.strip()) < 80:
        return True

    linhas = [l for l in txt.split("\n") if l.strip()]
    embaralhadas = sum(
        1 for l in linhas
        if re.match(r"^[.\d/\-:a-z]{15,}$", l.strip().lower())
        or re.match(r"^[A-Za-z]{2,3}[.]\d{4}[.]\w{4}[.]\w{4}[.]\w{4}$", l.strip())
        or l.strip().startswith("Aautenticidadedestedocumento")
        or re.match(r"^C[ó�o]digoverificador", l.strip())
    )
    chars_uteis = sum(
        len(l) for l in linhas
        if not re.match(r"^[.\d/\-:a-z]{15,}$", l.strip().lower())
        and not l.strip().startswith("Aautenticidadedestedocumento")
        and not re.match(r"^[A-Za-z]{2,3}[.]\d{4}[.]\w{4}[.]\w{4}[.]\w{4}$", l.strip())
    )

    hits_edoc = sum(1 for r in RE_EDOC_HINTS if r.search(txt))
    tem_palavra_chave = bool(RE_PALAVRAS_DOC.search(txt))

    # Regra 3: palavra-chave forte presente
    if tem_palavra_chave:
        # Se ha palavra-chave MAS o restante e dominado por assinatura E chars_uteis sao baixos,
        # ainda pode ser so um rodape com palavra-chave (ex: "Folha:" que esta em PALAVRAS_CHAVE)
        if hits_edoc >= 3 and chars_uteis < 200:
            return True
        return False

    # Regra 2: hints e-Doc sem palavra-chave
    if hits_edoc >= 2:
        return True

    # Regra 4: ratio de embaralhamento
    if linhas and embaralhadas / len(linhas) > 0.5:
        return True

    return False


# ------------------------------------------------------------
# Catalogo de TIPOS — ordem importa (mais especifico primeiro)
# ------------------------------------------------------------
# Cada entrada: (tipo, regex_cabecalho, regex_numero_opcional)
PADROES_TIPO = [
    # --- NE Crystal Reports (SIAFE): "Nota de Empenho" como titulo
    (
        "NE",
        re.compile(
            r"(?:ADMINISTRA[CÇ�]\w+\s+FINANCEIRA\s+INTEGRADA[\s\S]{0,50})?"
            r"Nota\s+de\s+Empenho\b",
            re.IGNORECASE,
        ),
        re.compile(r"(\d{4}NE\d{4,7})"),
    ),
    # --- NL
    (
        "NL",
        re.compile(r"Nota\s+de\s+Liquida[cç�]", re.IGNORECASE),
        re.compile(r"(\d{4}NL\d{4,7})"),
    ),
    # --- Carta Cobranca / Solicitacao de Pagamento / Aviso de Cobranca
    (
        "CARTA_COBRANCA",
        re.compile(
            r"Carta\s+Cobran[cç�]a?|"
            r"Aviso\s+de\s+Cobran[cç�]a?|"
            r"PRODAM.{0,200}solicita.{0,50}pagamento|"
            r"solicita\s+(?:a\s*\(o\)\s*)?V\.?\s*Sa\.?\s+o\s+pagamento|"
            r"pend[eê�]ncias?\s+de\s+pagamento|"
            r"Inadimpl[eê�]ncia\s+do\s+Cliente",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(
            r"Carta\s+Cobran[cç�]a?\s*(?:n[º°o]?\s*)?(\d+[\-/]?[A-Za-z-]*)|"
            r"PRESI/(\d+[\-\-]?\d*)",
            re.IGNORECASE,
        ),
    ),
    # --- Recibo (R E C I B O no topo + valor)
    (
        "RECIBO",
        re.compile(r"^\s*R\s*E\s*C\s*I\s*B\s*O\s*$|Recebemos\s+d[ao]?\s", re.IGNORECASE | re.MULTILINE),
        None,
    ),
    # --- Carta Circular
    (
        "CARTA_CIRCULAR",
        re.compile(r"Carta\s+Circular\s*(?:n[º°o]?\s*)?\d*[/\-]?\d*", re.IGNORECASE),
        re.compile(r"Carta\s+Circular\s*(?:n[º°o]?\s*)?(\d+[/\-]?\d*[\s\-]?\w*)", re.IGNORECASE),
    ),
    # --- Oficio (OFICIO Nº)
    (
        "OFICIO",
        re.compile(r"OF[IÍ�]CIO\s*(?:N[º°O]|Nr|n[uú]mero)", re.IGNORECASE),
        re.compile(r"OF[IÍ�]CIO\s*(?:N[º°O]|Nr)?\s*[:\-]?\s*(\d+[/\-]\d+|\d+)", re.IGNORECASE),
    ),
    # --- Notificacao Extrajudicial
    (
        "NOTIFICACAO",
        re.compile(r"NOTIFICA[CÇ�][AÃ�]O\s+EXTRAJUDICIAL", re.IGNORECASE),
        re.compile(r"NOTIFICA[CÇ�][AÃ�]O\s+EXTRAJUDICIAL\s*(?:n[º°o]?\s*)?(\d+[/\-]?\d*)", re.IGNORECASE),
    ),
    # --- Termo de Reconhecimento de Divida (TRD)
    (
        "TRD",
        re.compile(r"TERMO\s+DE\s+RECONHECIMENTO\s+(?:E\s+)?CONFISS[AÃ�]O\s+DE\s+D[IÍ�]VIDA|\bTRD\b",
                   re.IGNORECASE),
        None,
    ),
    # --- Termo Aditivo
    (
        "TA",
        re.compile(r"(?:^|\n)\s*(?:PRIMEIRO|SEGUNDO|TERCEIRO|QUARTO|QUINTO|SEXTO|S[ÉE�]TIMO|OITAVO|NONO|D[ÉE�]CIMO|\d+[ºo])"
                   r"\s+TERMO\s+ADITIVO|^TERMO\s+ADITIVO", re.IGNORECASE | re.MULTILINE),
        re.compile(r"(?:Contrato|CT)\s*(?:n[º°o]?\s*)?(\d{1,4}[/\-\.]\d{4})", re.IGNORECASE),
    ),
    # --- Contrato (CONTRATO DE PRESTACAO DE SERVICOS, CLAUSULA PRIMEIRA, etc.)
    (
        "CONTRATO",
        re.compile(r"CONTRATO\s+(?:DE\s+PRESTA[CÇ�][AÃ�]O\s+DE\s+SERVI[CÇ�]OS|N[º°O]\s*\d)|"
                   r"CL[AÁ�]USULA\s+PRIMEIRA",
                   re.IGNORECASE),
        re.compile(r"(?:CONTRATO|CT)\s*(?:n[º°o]?\s*)?(\d{1,4}[/\-\.]\d{4})", re.IGNORECASE),
    ),
    # --- Proposta Comercial
    (
        "PROPOSTA",
        re.compile(r"PROPOSTA\s+(?:COMERCIAL|DE\s+PRE[CÇ�]OS?|T[EÉ�]CNICA)|"
                   r"(?:^|\n)\s*PROPOSTA\b", re.IGNORECASE),
        None,
    ),
    # --- Nota Fiscal (NFS-e, DANFE)
    (
        "NF",
        re.compile(r"NOTA\s+FISCAL(?:\s+DE\s+SERVI[CÇ�]OS?\s+ELETR[OÔ�]NICA)?|\bNFS-?e\b|\bDANFE\b",
                   re.IGNORECASE),
        re.compile(r"(?:N[Ff]S?-?e?|Nota\s+Fiscal)\s*(?:n[º°o]?\s*)?(\d{3,9})", re.IGNORECASE),
    ),
    # --- Aceite Tecnico / Atesto
    (
        "ACEITE",
        re.compile(r"ACEITE\s+T[EÉ�]CNICO|ATESTO\s+T[EÉ�]CNICO|ATESTADO\s+DE\s+EXECU[CÇ�]",
                   re.IGNORECASE),
        None,
    ),
    # --- Certidao (CND, CPEN, CAUC, etc.)
    (
        "CERTIDAO",
        re.compile(r"CERTID[AÃ�]O\s+(?:NEGATIVA|POSITIVA|DE\s+REGULARIDADE)|"
                   r"CND|CPEN|CAUC", re.IGNORECASE),
        None,
    ),
    # --- Processo administrativo (SEI, e-Doc)
    (
        "PROCESSO",
        re.compile(r"Processo\s+(?:n[º°o]|administrativo)\s*[:\-]?\s*\d", re.IGNORECASE),
        re.compile(r"Processo\s*(?:n[º°o])?\s*[:\-]?\s*([\d.]+/\d{4}[\-\d]*)", re.IGNORECASE),
    ),
    # --- Relatorio SPCF
    (
        "RELATORIO_SPCF",
        re.compile(r"^(?:SPCF|Rela[cç�]{0,1}[aã�]?o\s+(?:de\s+)?Faturas)", re.IGNORECASE | re.MULTILINE),
        None,
    ),
    # --- Extrato / Demonstrativo
    (
        "EXTRATO",
        re.compile(r"EXTRATO\s+(?:DE|DOS|DA)|DEMONSTRATIVO\s+DE", re.IGNORECASE),
        None,
    ),
]


# ------------------------------------------------------------
# Hints por pasta (peso: adiciona confianca se tipo bate com pasta)
# ------------------------------------------------------------
HINTS_PASTA: dict[str, list[str]] = {
    "06_COBRANCAS_OFICIOS": ["CARTA_COBRANCA", "CARTA_CIRCULAR", "OFICIO", "PROCESSO", "RELATORIO_SPCF", "NE"],
    "02_NOTAS_EMPENHO":     ["NE"],
    "03_NOTAS_LIQUIDACAO":  ["NL"],
    "04_FATURAS":           ["NF"],
    "05_ACEITES_TECNICOS":  ["ACEITE"],
    "07_CERTIDOES":         ["CERTIDAO"],
    "01_CONTRATOS":         ["CONTRATO", "TA", "PROPOSTA"],
    "13_PECAS_JURIDICAS":   ["NOTIFICACAO", "TRD", "OFICIO"],
    "09_RELATORIOS_AUDITORIAS": ["RELATORIO_SPCF", "EXTRATO", "PROCESSO"],
    "17_FATURAS_HTML":      ["NF"],
    "20_OCR_OUTPUT":        [],  # pasta mista, sem hint
}


# ------------------------------------------------------------
# Datas, CNPJ, valores
# ------------------------------------------------------------
RE_DATA_BR   = re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b")
RE_DATA_ISO  = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
RE_DATA_EXT  = re.compile(
    r"\b(\d{1,2})\s+de\s+"
    r"(janeiro|fevereiro|mar[cç�]o|abril|maio|junho|julho|agosto|"
    r"setembro|outubro|novembro|dezembro)\s+de\s+(\d{4})",
    re.IGNORECASE,
)
MESES_EXT = {"janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "mar�o": 3,
             "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
             "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}

RE_CNPJ = re.compile(r"(\d{2}[.\-]?\d{3}[.\-]?\d{3}[/\-]?\d{4}[.\-]?\d{2})")
RE_VALOR = re.compile(
    r"R\$\s*([\d]{1,3}(?:\.\d{3})*,\d{2}|[\d]+,\d{2}|[\d]+\.\d{2})"
)


def extrair_data(texto: str) -> Optional[str]:
    """Retorna data em YYYY-MM-DD ou None."""
    m = RE_DATA_BR.search(texto)
    if m:
        d, mes, y = m.groups()
        try:
            return f"{y}-{int(mes):02d}-{int(d):02d}"
        except Exception:
            pass
    m = RE_DATA_ISO.search(texto)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = RE_DATA_EXT.search(texto)
    if m:
        d, mes, y = m.groups()
        mes_norm = mes.lower().replace("ç", "c").replace("�", "c")
        mn = MESES_EXT.get(mes.lower()) or MESES_EXT.get(mes_norm)
        if mn:
            try:
                return f"{y}-{mn:02d}-{int(d):02d}"
            except Exception:
                pass
    return None


def extrair_cnpj(texto: str) -> Optional[str]:
    m = RE_CNPJ.search(texto)
    if m:
        # Normaliza para so digitos
        return re.sub(r"[^\d]", "", m.group(1))
    return None


def extrair_valor(texto: str) -> Optional[str]:
    m = RE_VALOR.search(texto)
    if not m:
        return None
    raw = m.group(1)
    try:
        s = raw.replace(".", "").replace(",", ".")
        v = Decimal(s)
        return f"{v:.2f}"
    except (InvalidOperation, ValueError):
        return None


def extrair_orgao(texto: str, preferencia_pasta: Optional[str] = None,
                  orgaos: Optional[list[str]] = None) -> Optional[str]:
    """Extrai orgao mais citado no texto (lista parametrizavel; default ORGAOS_DEFAULT)."""
    re_orgao = RE_ORGAO if not orgaos else compilar_re_orgaos(orgaos)
    hits = [m.group(1).upper() for m in re_orgao.finditer(texto)]
    if not hits:
        return None
    # Ordena por frequencia desc; desempate: preferencia
    from collections import Counter
    c = Counter(hits)
    # Normaliza variantes (TJAM -> TJ-AM, etc.)
    norm = {"TJAM": "TJ-AM", "TCEAM": "TCE-AM"}
    mais_comum = c.most_common()
    for orgao, _ in mais_comum:
        o = norm.get(orgao, orgao)
        if preferencia_pasta and preferencia_pasta.upper() in o:
            return o
    return norm.get(mais_comum[0][0], mais_comum[0][0])


# ------------------------------------------------------------
# Classificador principal
# ------------------------------------------------------------
@dataclass
class ResultadoClassificacao:
    tipo: str = "OUTRO"
    numero: Optional[str] = None
    orgao: Optional[str] = None
    cnpj: Optional[str] = None
    data: Optional[str] = None
    valor: Optional[str] = None
    confianca: float = 0.0
    paginas_usadas: list[int] = field(default_factory=list)
    candidatos_alternativos: list[tuple[str, float]] = field(default_factory=list)
    alerta: str = ""


def escolher_pagina_conteudo(textos_paginas: list[str]) -> tuple[str, list[int]]:
    """Retorna (texto_concatenado, lista_paginas_usadas_1indexed).
    Pula paginas de assinatura e-Doc; usa as 3 primeiras paginas de conteudo real.
    """
    usadas = []
    chunks = []
    for i, t in enumerate(textos_paginas):
        if is_pagina_assinatura(t):
            continue
        usadas.append(i + 1)
        chunks.append(t)
        if len(usadas) >= 3:
            break
    if not chunks:
        # Nenhuma pagina "util" — usa o que tem
        usadas = [1]
        chunks = textos_paginas[:1]
    return "\n\n".join(chunks), usadas


def classificar_pdf_v2(
    textos_paginas: list[str],
    nome_arquivo: str = "",
    pasta_raiz: str = "",
    orgaos: Optional[list[str]] = None,
    orgao_preferido: Optional[str] = None,
) -> dict:
    """
    Classifica um PDF.

    Args:
        textos_paginas: lista de strings, 1 por pagina (ordem).
        nome_arquivo: basename do arquivo (opcional hint).
        pasta_raiz: nome da pasta raiz (ex: "06_COBRANCAS_OFICIOS") — hint forte.
        orgaos: lista de orgaos reconheciveis (default ORGAOS_DEFAULT).
        orgao_preferido: devedor em foco (ex: "SEDUC") — desempata extracao de orgao.

    Returns:
        dict com tipo, numero, orgao, cnpj, data, valor, confianca, paginas_usadas,
        candidatos_alternativos (outros tipos com score), alerta.
    """
    r = ResultadoClassificacao()

    # Primeira pagina de conteudo real (nao assinatura) -> usada para DETECTAR TIPO
    pagina_tipo = None
    for t in textos_paginas:
        if not is_pagina_assinatura(t):
            pagina_tipo = t
            break
    if pagina_tipo is None:
        pagina_tipo = textos_paginas[0] if textos_paginas else ""

    # Texto concatenado de ate 3 paginas de conteudo -> usado para extrair METADADOS
    texto_todo, paginas_usadas = escolher_pagina_conteudo(textos_paginas)
    r.paginas_usadas = paginas_usadas

    # Cabecalho = primeiros 1000 chars da PRIMEIRA pagina de conteudo
    # (Critico: evita capturar NF anexa quando o PDF e carta + NF)
    cabecalho = pagina_tipo[:1000]
    # Para extracao de metadados, usamos texto_todo
    texto = texto_todo

    # Avalia cada tipo
    hints_pasta = HINTS_PASTA.get(pasta_raiz, [])
    scores: dict[str, float] = {}
    numeros_por_tipo: dict[str, Optional[str]] = {}

    for tipo, re_cab, re_num in PADROES_TIPO:
        m = re_cab.search(cabecalho)
        if not m:
            continue
        score = 0.6  # bateu no cabecalho
        # Hint de pasta reforca
        if tipo in hints_pasta:
            score += 0.2
        # Hint do nome de arquivo (se tipo aparece nele)
        nm_up = nome_arquivo.upper()
        if tipo in nm_up or (tipo == "NE" and re.search(r"^NE[\s_\-]|\d{4}NE\d", nm_up)):
            score += 0.1
        # Extrai numero
        num = None
        if re_num:
            mn = re_num.search(texto)
            if mn:
                num = mn.group(1)
                score += 0.1
        scores[tipo] = min(1.0, round(score, 2))
        numeros_por_tipo[tipo] = num

    if not scores:
        # Nao bateu em nada — tenta CONTRATO/OUTRO com base no nome
        r.tipo = "OUTRO"
        r.confianca = 0.1
        r.alerta = "nenhum padrao de cabecalho reconhecido"
    else:
        # Escolhe o tipo de maior score; empate -> hint de pasta
        ordenado = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        r.tipo = ordenado[0][0]
        r.confianca = ordenado[0][1]
        r.numero = numeros_por_tipo.get(r.tipo)
        # Alternativos (score >= 0.5)
        r.candidatos_alternativos = [(t, s) for t, s in ordenado[1:] if s >= 0.5][:3]

    # Metadados gerais
    r.data = extrair_data(texto)
    r.cnpj = extrair_cnpj(texto)
    r.valor = extrair_valor(texto)
    # Para orgao, priorizar o devedor (nao PRODAM que e o credor)
    preferencia = None
    candidatos_pref = [orgao_preferido] if orgao_preferido else []
    candidatos_pref += ["DETRAN", "SES", "SUSAM", "SSP", "SEDUC", "SEAP"]
    for o in candidatos_pref:
        if o and o.upper() in texto.upper():
            preferencia = o.upper()
            break
    r.orgao = extrair_orgao(texto, preferencia_pasta=preferencia, orgaos=orgaos)

    return asdict(r)


# ------------------------------------------------------------
# CLI de teste
# ------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Uso: classificador_v2.py <pdf1> [pdf2] ...")
        print("Modulo de biblioteca — para lote use classificar_universo.py")
        sys.exit(0)

    import pdfplumber  # import tardio — so o CLI de teste precisa

    for pdf_path in sys.argv[1:]:
        p = Path(pdf_path)
        if not p.exists():
            print(f"[MISS] {pdf_path}")
            continue
        textos = []
        try:
            with pdfplumber.open(str(p)) as pdf:
                for pg in pdf.pages[:10]:  # le ate 10 paginas para achar conteudo
                    textos.append(pg.extract_text() or "")
        except Exception as e:
            print(f"[ERRO] {p.name}: {e}")
            continue
        # Pasta raiz (2 niveis acima do arquivo se possivel)
        pasta_raiz = p.parts[-3] if len(p.parts) >= 3 else ""
        r = classificar_pdf_v2(textos, nome_arquivo=p.name, pasta_raiz=pasta_raiz)
        print(f"\n{p.name}")
        print(f"  tipo={r['tipo']:<16} conf={r['confianca']}  pgs={r['paginas_usadas']}")
        print(f"  numero={r['numero']!r}  orgao={r['orgao']!r}  data={r['data']!r}  valor={r['valor']!r}")
        if r["candidatos_alternativos"]:
            print(f"  alternativos: {r['candidatos_alternativos']}")
        if r["alerta"]:
            print(f"  ALERTA: {r['alerta']}")
