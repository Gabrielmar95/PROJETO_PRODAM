"""
padroes.py — Regex, mapas canônicos e parsers para a skill `renomeador-pdfs-prodam`.

Generalização do script `rename_contratos_formal.py` (DETRAN, testado em 89 PDFs) para
cobrir os 10 tipos de documento do Projeto PRODAM:

    Contrato-Base | TA | Proposta | NE | NL | NF | Fatura | Aceite | Cobrança | Certidão

Princípios:
- Nenhum regex aceita ambiguidade: o parser preserva (NNN, AAAA) com zfill(3).
- Mapas por devedor ficam em `MAPAS_POR_DEVEDOR[<ORGAO>]` e DEVEM ser populados
  antes de rodar para um novo devedor. DETRAN já vem populado (ground-truth).
- Nomes canônicos são **ASCII puro**: sem acentos, sem espaços, sem `/` (vira `.`).
- `Decimal` para qualquer valor monetário parseado. Nunca `float`.

Referências:
- `REFERENCIA_JURIDICA/` na SSOT do projeto
- CLAUDE.md §DETRAN (benchmark A+)
- Skills irmãs:
    * `normalizador-contratos-prodam` (forma canônica 6/2021 → CT-006.2021)
    * `ocr-pdfs-prodam/scripts/classificador_conteudo.py` (tipo detectado por conteúdo)
    * `nota-empenho-classificador`, `nota-liquidacao-extrator`

Compatível com Python 3.12+.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Optional

# ============================================================================
# 1. CONSTANTES E ENUMERAÇÕES
# ============================================================================

#: Tipos de documento em ordem de precedência (DIRAF > SPCF-Extração > NE > ...).
#: A ordem aqui espelha a cascata de `parse_tipo_doc`.
TIPOS_DOCUMENTO = (
    "Oficio-DIRAF",     # oficios internos PRODAM (fora de escopo contratual)
    "Extracao-SPCF",    # variantes extraídas do scraper SPCF
    "NE",               # nota de empenho
    "NL",               # nota de liquidação
    "NF",               # nota fiscal
    "Fatura",           # fatura/boleto/DV
    "Aceite",           # aceite técnico / atesto fiscal
    "Cobranca",         # carta de cobrança / ofício de cobrança
    "Certidao",         # CND, FGTS, Trabalhista, Falência
    "Proposta",         # proposta comercial anexa a CT
    "TA",               # termo aditivo
    "Contrato-Base",    # contrato-base (numeração principal)
    "Indefinido",       # fallback
)

#: Map de palavras-ordinais → ordinal numérico zero-padded (usado em TAs).
ORDINAL_WORD: dict[str, str] = {
    "1": "01", "2": "02", "3": "03", "4": "04",
    "5": "05", "6": "06", "7": "07", "8": "08", "9": "09",
    "primeiro": "01", "segundo": "02", "terceiro": "03",
    "quarto": "04", "quinto": "05", "sexto": "06", "setimo": "07",
    "oitavo": "08", "nono": "09", "decimo": "10",
}

# ============================================================================
# 2. REGEX (COMPILADOS, NOMEADOS)
# ============================================================================

# ---- 2.1 Contratos e TAs (herdados de rename_contratos_formal.py) -----------

#: "Contrato NNN/AAAA" ou "CT-006.2021" ou "CT 22/2014" (com prefixo explícito).
#: Aceita hífens entre prefixo e número (generalização do DETRAN original).
CT_NUM_RE = re.compile(
    r"(?:contrato|CT|ct)[\s_\-]*[Nn]?[ºo°\.]?[\s_\-]*0*(\d{1,3})[._\-/ ]+0*(\d{2,4})",
    re.IGNORECASE,
)

#: Padrão curto sem prefixo: "022.2014", "22.14", "83.22" → (NNN, AAAA).
#: Exige lookahead/lookbehind para não pegar valores monetários ou datas.
CT_NUM_SHORT_RE = re.compile(
    r"(?:^|[\s_])0*(\d{1,3})\.0*(\d{2,4})(?=[\s_\-.]|$)"
)

#: Typo conhecido: "Contrato 2762014" (sem separador) → 27/2014.
CT_NUM_TYPO_RE = re.compile(
    r"\b0*(\d{1,3})\s*-?\s*(\d{4})\s*-\s*Prazo", re.IGNORECASE
)

#: "1º TA", "2o TA", "3 TA".
TA_ORDINAL_RE = re.compile(
    r"(?:^|[\s_])(\d)\s*[ºo°]?\s*TA(?:[\s_]|$)", re.IGNORECASE
)

#: "PRIMEIRO TERMO ADITIVO", "SEGUNDO TERMO ADITIVO", etc.
TA_ALT_RE = re.compile(
    r"(?:^|[\s_])(primeiro|segundo|terceiro|quarto|quinto|sexto|setimo|s[eé]timo|oitavo|nono|d[eé]cimo)\s+TERMO\s+ADITIVO",
    re.IGNORECASE,
)

#: "PROPOSTA 060/2022".
PROPOSTA_RE = re.compile(
    r"PROPOSTA[\s_]+0*(\d{1,3})[.\-/]0*(\d{2,4})", re.IGNORECASE
)

# ---- 2.2 Notas de empenho, liquidação, fiscal -------------------------------

#: "NE 471", "NE_471", "2024NE00471", "NOTA DE EMPENHO Nº 00471/2024".
NE_RE = re.compile(
    r"(?:^|[\s_])(?:NE|nota\s+de\s+empenho|n[ºo°]?\s*empenho)[\s_:No°\.]*0*(\d{3,7})(?:[.\-/]?(\d{2,4}))?",
    re.IGNORECASE,
)

#: "2024NE00471" (formato SPCF concatenado).
NE_SPCF_RE = re.compile(r"(\d{4})\s*NE\s*(\d{5,7})", re.IGNORECASE)

#: "NL 1234", "2024NL00123", "NOTA DE LIQUIDACAO".
NL_RE = re.compile(
    r"(?:^|[\s_])(?:NL|nota\s+de\s+liquida[çc][ãa]o)[\s_:No°\.]*0*(\d{3,7})(?:[.\-/]?(\d{2,4}))?",
    re.IGNORECASE,
)

#: "2024NL00123" (formato SPCF concatenado).
NL_SPCF_RE = re.compile(r"(\d{4})\s*NL\s*(\d{5,7})", re.IGNORECASE)

#: NF com número isolado: "NF 12345", "NF-e 000012345", "Nota Fiscal 12345".
NF_RE = re.compile(
    r"(?:^|[\s_])(?:NF[\s_\-]?e?|nota\s+fiscal)[\s_:No°\.]*0*(\d{3,9})",
    re.IGNORECASE,
)

#: "Referências: 2024NE00471 + 2024NE00480" (NL referencia NEs).
NL_REFS_RE = re.compile(
    r"(?:refer[êe]ncias?|refs?)[\s:]*((?:\d{4}NE\d{5,7}[,+ ]*)+)",
    re.IGNORECASE,
)

# ---- 2.3 Faturas e aceites --------------------------------------------------

#: "FAT 123/2024", "FATURA 000123-2024", "Fatura n. 123/2024".
FATURA_RE = re.compile(
    r"(?:^|[\s_])(?:FAT|FATURA)[\s_:No°\.]*0*(\d{1,5})[.\-/](\d{2,4})",
    re.IGNORECASE,
)

#: Aceite técnico referenciando NF: "ACEITE NF 12345", "Atesto NF-e 000012345".
ACEITE_NF_RE = re.compile(
    r"(?:aceite|atesto|atestado)[\s_:]*(?:t[eé]cnico)?[\s_]*(?:NF[\s_\-]?e?)?[\s_:No°\.]*0*(\d{3,9})",
    re.IGNORECASE,
)

# ---- 2.4 Competência, datas, valores ---------------------------------------

#: "Competência: 09/2024", "Comp. 2024-09", "referente a 09/2024".
COMPETENCIA_RE = re.compile(
    r"(?:compet[êe]ncia|comp\.?|refer[êe]ncia|ref\.?|m[êe]s\s+de\s+refer[êe]ncia)"
    r"[\s:]*(\d{1,2})[/\-](\d{4})",
    re.IGNORECASE,
)

#: "Competência: 2024-09" (formato ISO).
COMPETENCIA_ISO_RE = re.compile(
    r"(?:compet[êe]ncia|comp\.?)[\s:]*(\d{4})[/\-](\d{1,2})", re.IGNORECASE
)

#: Data DD/MM/AAAA.
DATA_BR_RE = re.compile(r"(\d{2})[/\-.](\d{2})[/\-.](\d{4})")

#: Data AAAA-MM-DD (ISO).
DATA_ISO_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

#: Valor BRL: "R$ 1.234,56", "R$ 123,45", "123456,78".
VALOR_BRL_RE = re.compile(
    r"R\$\s*([\d]{1,3}(?:\.\d{3})*,\d{2}|[\d]+,\d{2})"
)

# ---- 2.5 Cobranças e certidões ---------------------------------------------

#: "Ofício 337/2021", "Of. n. 337-2021".
OFICIO_RE = re.compile(
    r"(?:of[íi]cio|of\.?|carta\s+de\s+cobran[çc]a)[\s_:No°\.]*0*(\d{1,5})[.\-/](\d{2,4})",
    re.IGNORECASE,
)

#: CND: "Certidão Negativa de Débitos", "CND Federal", "CPEN", "CNDT".
CERTIDAO_TIPO_RE = re.compile(
    r"(CND(?:T)?|CPEN|certid[ãa]o\s+(?:negativa|positiva|de\s+regularidade)|FGTS|falencia|trabalhista|federal|municipal|estadual)",
    re.IGNORECASE,
)

# ---- 2.6 Filtros de "nome suspeito" (mesmo critério da skill irmã) ---------

#: Nomes genéricos de scanner/câmera que merecem renomeação.
NOME_SUSPEITO_RE = re.compile(
    r"^(scan_\d+|img_\d+|image\s*\(\d+\)|document(\s*\(\d+\))?|documento\s*\(\d+\)"
    r"|untitled|\d{6,}|[a-f0-9]{16,})\.pdf$",
    re.IGNORECASE,
)

# ============================================================================
# 3. MAPAS POR DEVEDOR
# ============================================================================


@dataclass(frozen=True)
class MapaDevedor:
    """Estrutura dos mapas canônicos por devedor."""
    nome: str                                       # p.ex. "DETRAN"
    spcf_id_para_ct: dict[str, tuple[str, str]]     # "12086" → ("003", "2026")
    filename_typo_para_ct: dict[str, tuple[str, str]]  # "2762014" → ("027", "2014")
    objeto_contrato: dict[tuple[str, str], str]     # ("022","2014") → "Sistema-SCIT..."
    regime: dict[tuple[str, str], str]              # ("006","2021") → "IGPM-via-4TA"


#: DETRAN — populado com valores validados em CLAUDE.md §3.6 e §1.2 do DETRAN.
MAPA_DETRAN = MapaDevedor(
    nome="DETRAN",
    spcf_id_para_ct={
        "12086": ("003", "2026"),  # contrato_DETRAN_12086 = CT 003/2026 (prop 14421)
    },
    filename_typo_para_ct={
        "2762014": ("027", "2014"),  # "Contrato 2762014" → 27/2014 (typo sem separador)
    },
    objeto_contrato={
        ("022", "2014"): "Sistema-SCIT-Processamento-Diario",
        ("025", "2014"): "Manutencao-de-Sistema",
        ("027", "2014"): "Servico-de-Rede",
        ("017", "2015"): "Data-Center",
        ("004", "2016"): "Sistema-de-Biometria",
        ("006", "2021"): "Rede-VPN-Firewall-MetroMao-Assessoria",
        ("010", "2021"): "SW-Gestao-de-Transito",
        ("012", "2021"): "Desenvolvimento-de-Sistemas",
        ("075", "2022"): "Sistema-SIGMO",
        ("083", "2022"): "Licenca-Talao-Eletronico",
        ("060", "2022"): "Proposta-Comercial",
        ("071", "2022"): "Proposta-Comercial",
        ("003", "2026"): "Assessoria-Tecnica-Prop-14421",
        ("296", "2025"): "Assessoria-Tecnica-Prop-14421",
    },
    regime={
        ("022", "2014"): "IGPM+1pct+2pct",
        ("025", "2014"): "IGPM+1pct+2pct",
        ("027", "2014"): "IGPM+1pct+2pct",
        ("017", "2015"): "Silente",
        ("004", "2016"): "Contratual",
        ("006", "2021"): "IGPM-via-4TA",
        ("010", "2021"): "Silente",
        ("012", "2021"): "IPCA-via-5TA",
        ("075", "2022"): "IPCA",
        ("083", "2022"): "IPCA",
        ("060", "2022"): "Silente",
        ("071", "2022"): "Silente",
        ("003", "2026"): "SELIC-Lei-14905",
        ("296", "2025"): "SELIC-Lei-14905",
    },
)

#: Template vazio — copiar e popular por devedor antes do primeiro uso.
MAPA_SES_TEMPLATE = MapaDevedor(
    nome="SES",
    spcf_id_para_ct={},
    filename_typo_para_ct={},
    objeto_contrato={},
    regime={},
)

MAPA_SSP_TEMPLATE = MapaDevedor(
    nome="SSP",
    spcf_id_para_ct={},
    filename_typo_para_ct={},
    objeto_contrato={},
    regime={},
)

#: Registry central: usado por `Renomeador(mapas_devedor=...)`.
MAPAS_POR_DEVEDOR: dict[str, MapaDevedor] = {
    "DETRAN": MAPA_DETRAN,
    "SES": MAPA_SES_TEMPLATE,
    "SSP": MAPA_SSP_TEMPLATE,
}

# ============================================================================
# 4. PARSERS
# ============================================================================


def asciificar(s: str) -> str:
    """Remove acentos e caracteres não-ASCII. Preserva alfanuméricos e `._-+`.

    >>> asciificar("Supressão Contratual")
    'Supressao-Contratual'
    >>> asciificar("Décimo Termo Aditivo")
    'Decimo-Termo-Aditivo'
    """
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    # substitui espaços por hífen e remove chars proibidos
    limpo = re.sub(r"\s+", "-", sem_acento)
    limpo = re.sub(r"[^A-Za-z0-9._\-+]", "-", limpo)
    # colapsa hífens duplicados
    limpo = re.sub(r"-{2,}", "-", limpo)
    return limpo.strip("-")


def parse_ct_num(
    nome: str, mapa: Optional[MapaDevedor] = None
) -> Optional[tuple[str, str]]:
    """Extrai (NNN, AAAA) do contrato-base citado no nome do arquivo.

    Usa cascata em 5 etapas; retorna no primeiro match.

    Args:
        nome: nome do arquivo (pode incluir extensão).
        mapa: `MapaDevedor` opcional — habilita SPCF_IDs e typos conhecidos.

    Returns:
        Tupla (numero_zfill_3, ano_4_digitos) ou None se não parseável.
    """
    # 1. IDs SPCF conhecidos do devedor (ex: contrato_DETRAN_12086 → 003/2026)
    if mapa:
        for spcf_id, ct in mapa.spcf_id_para_ct.items():
            if spcf_id in nome:
                return ct
        # 2. Typos conhecidos (ex: "2762014" sem separador → 27/2014)
        for typo, ct in mapa.filename_typo_para_ct.items():
            if typo in nome:
                return ct

    # 3. Variantes explícitas com prefixo "Contrato" / "CT"
    m = CT_NUM_RE.search(nome)
    if m:
        return _normalizar_par(m.group(1), m.group(2))

    # 4. Proposta
    m = PROPOSTA_RE.search(nome)
    if m:
        return _normalizar_par(m.group(1), m.group(2))

    # 5. Padrão curto standalone tipo "075.2022 - PRODAM -" ou "22.14"
    m = CT_NUM_SHORT_RE.search(nome)
    if m:
        num, ano = m.group(1).zfill(3), m.group(2)
        if len(ano) == 2:
            ano = ("20" if int(ano) < 80 else "19") + ano
        # Sanity: ano entre 2010 e 2030 (evita falso positivo em datas/valores)
        if 2010 <= int(ano) <= 2030:
            return num, ano

    return None


def _normalizar_par(num_raw: str, ano_raw: str) -> tuple[str, str]:
    """Normaliza (num, ano) — zfill e converte AA → AAAA."""
    num = num_raw.zfill(3)
    ano = ano_raw
    if len(ano) == 2:
        ano = ("20" if int(ano) < 80 else "19") + ano
    return num, ano


def parse_ta_ordinal(nome: str) -> Optional[str]:
    """Retorna ordinal do TA zero-padded ('01', '02', ...) ou None."""
    m = TA_ORDINAL_RE.search(nome)
    if m:
        return m.group(1).zfill(2)
    m = TA_ALT_RE.search(nome)
    if m:
        key = asciificar(m.group(1).lower()).replace("-", "")
        return ORDINAL_WORD.get(key)
    return None


def parse_tipo_doc(nome: str, texto_ocr: str = "") -> str:
    """Classifica tipo do documento em CASCATA DE 13 REGRAS.

    Ordem taxativa (parar no primeiro match):

        1. DIRAF          → Oficio-DIRAF (ofício interno PRODAM)
        2. tags-SPCF      → Extracao-SPCF (scraping duplicado)
        3. Aceite         → aceite técnico / atesto (antes de NF — o aceite
                            referencia uma NF mas NÃO é NF)
        4. NL             → nota de liquidação (antes de NE — uma NL costuma
                            referenciar NEs no nome)
        5. NE             → nota de empenho
        6. NF             → nota fiscal
        7. Fatura         → fatura/boleto (só se NÃO for NF)
        8. Cobranca       → ofício de cobrança
        9. Certidao       → CND / FGTS / etc
        10. Proposta      → proposta comercial (antes de TA/Contrato)
        11. TA            → termo aditivo
        12. Contrato-Base → contrato-base
        13. Indefinido    → fallback

    Args:
        nome: nome do arquivo (sem path, com extensão).
        texto_ocr: conteúdo OCR das primeiras páginas (opcional; reforça decisão).

    Returns:
        String do enum `TIPOS_DOCUMENTO`.
    """
    n = nome.upper()
    t = (texto_ocr or "").upper()

    # 1. DIRAF tem prioridade (ofício, não contrato)
    if "DIRAF" in n:
        return "Oficio-DIRAF"

    # 2. Extrações SPCF — marcam-se por prefixo da cascata de extração
    if any(tag in nome for tag in (
        "htmls_brutos", "pdfs_convertidos",
        "pdfs_oficiais_SPCF", "pdfs_spcf_reais",
        "HIST__Auditoria", "Documentacao_Contratos",
    )):
        return "Extracao-SPCF"

    # 3. Aceite / Atesto (ANTES de NF — "ACEITE TECNICO NF 12345" é Aceite,
    #    não NF; o documento é o aceite que *referencia* a NF).
    if re.search(r"ACEITE|ATESTO|ATESTADO", n) or re.search(r"ACEITE\s+T[ÉE]CNICO", t):
        return "Aceite"

    # 4. NL: "NL 123", "NOTA DE LIQUIDACAO" (antes de NE — uma NL costuma
    #    referenciar NEs no nome; se deixássemos NE primeiro, perderíamos a NL).
    if (re.search(r"(?:^|[\s_])NL\s*\d", n)
            or "NOTA DE LIQUIDACAO" in n
            or "NOTA DE LIQUIDA" in t
            or re.search(r"\d{4}NL\d{5,7}", n)):
        return "NL"

    # 5. NE: "NE 471", "NOTA DE EMPENHO", com lookbehind de separador
    if (re.search(r"(?:^|[\s_])NE\s*\d", n)
            or "NOTA DE EMPENHO" in n
            or "NOTA DE EMPENHO" in t
            or re.search(r"\d{4}NE\d{5,7}", n)):
        return "NE"

    # 6. NF (antes de Fatura pois toda NF é também "fatura" no sentido amplo)
    # Usa [Ee] para aceitar tanto "NF-e" quanto "NF-E" (n já está em upper, mas
    # preservamos ambas variantes para robustez contra mudanças futuras).
    if (re.search(r"(?:^|[\s_])NF[\s_\-]?[Ee]?[\s_]*\d", n)
            or "NOTA FISCAL" in n
            or "NOTA FISCAL" in t):
        return "NF"

    # 7. Fatura (boleto, DV, duplicata; só se NÃO for NF)
    if ("FATURA" in n or "BOLETO" in n or "DUPLICATA" in n) and "NOTA FISCAL" not in n:
        return "Fatura"

    # 8. Cobrança (carta/ofício de cobrança)
    if ("COBRANCA" in n or "COBRAN" in n
            or "CARTA DE COBRANCA" in t or "CARTA DE COBRAN" in t):
        return "Cobranca"

    # 9. Certidão (CND, FGTS, CPEN, CNDT)
    if re.search(r"CERTIDAO|CND|CPEN|FGTS|CNDT", n) or CERTIDAO_TIPO_RE.search(t or ""):
        return "Certidao"

    # 10. Proposta (sem TA)
    if "PROPOSTA" in n and not re.search(r"(?:^|[\s_])TA(?:[\s_]|$)", n):
        return "Proposta"

    # 11. TA: "TERMO ADITIVO", "Nº TA", ou " TA " standalone
    if ("TERMO ADITIVO" in n
            or re.search(r"\d\s*[ºo°]\s*TA", n)
            or re.search(r"(?:^|[\s_])TA(?:[\s_]|$)", n)):
        return "TA"

    # 12. Contrato-Base: "CONTRATO NNN/AAAA" ou "CT_NNN..." ou "CT-NNN"
    if "CONTRATO" in n or re.search(r"(?:^|[\s_])CT[_\-\s]\d", n):
        return "Contrato-Base"

    return "Indefinido"


def objeto_ta(nome: str) -> str:
    """Extrai o objeto do TA (reajuste, supressão, suplementação, prazo, etc.).

    Retorna string ASCII pura separada por `-`, ou `Sem-Especificacao` se nada bater.
    """
    n = nome.lower()
    partes: list[str] = []

    # Reajustes (IGPM/IPCA/SELIC × percentual)
    m = re.search(r"reajuste\s+([\d,]+)\s*%\s*(igpm|ipca|selic)", n)
    if m:
        pct = m.group(1).replace(",", ".")
        idx = m.group(2).upper()
        partes.append(f"Reajuste-{idx}-{pct}pct")

    # Supressão contratual
    if "supressao" in n or "supress" in n:
        partes.append("Supressao-Contratual")

    # Suplementação
    m = re.search(r"suplem\w*\s+(\d+)\s*%", n)
    if m:
        partes.append(f"Suplementacao-{m.group(1)}pct")
    elif "suplem" in n:
        partes.append("Suplementacao-Contratual")

    # Redução por decreto
    m = re.search(r"redu\w*\s+(?:de\s+)?(\d+)\s*%", n)
    if m:
        partes.append(f"Reducao-{m.group(1)}pct-Decreto")

    # Prazo
    if "prazo" in n:
        m = re.search(r"prazo\s+(\d+)\s*meses", n)
        if m:
            partes.append(f"Prorrogacao-{m.group(1)}meses")
        else:
            partes.append("Prorrogacao-Prazo")

    # Realinhamento de preços
    if "realinham" in n:
        partes.append("Realinhamento")

    # Ofício citado (ex: "Of. 337/2021")
    m = re.search(r"of\.?\s*(\d{3,4})[.\-/]?(\d{2})?", n)
    if m:
        of_num = m.group(1)
        of_ano = m.group(2) or ""
        partes.append(f"Of-{of_num}" + (f"-{of_ano}" if of_ano else ""))

    # Status de assinatura
    if "assinad" in n and "doe" not in n:
        partes.append("Assinado")
    if "doe" in n:
        partes.append("DOE")
    if "para assinatura" in n:
        partes.append("Pre-Assinatura")
    if "comprimido" in n:
        partes.append("Comprimido")

    return "-".join(partes) if partes else "Sem-Especificacao"


def parse_ne_num(nome: str) -> Optional[tuple[str, str]]:
    """Extrai (ano_4, numero_5) da NE. Retorna None se não parseável.

    Reconhece formatos:
        - "2024NE00471"     → ("2024", "00471")
        - "NE 471/2024"     → ("2024", "00471")
        - "NE_00471"        → ("", "00471") — sem ano
    """
    m = NE_SPCF_RE.search(nome)
    if m:
        return m.group(1), m.group(2).zfill(5)
    m = NE_RE.search(nome)
    if m:
        num = m.group(1).zfill(5)
        ano = m.group(2) or ""
        if ano and len(ano) == 2:
            ano = ("20" if int(ano) < 80 else "19") + ano
        return ano, num
    return None


def parse_nl_num(nome: str) -> Optional[tuple[str, str]]:
    """Extrai (ano_4, numero_5) da NL. Mesmo formato de `parse_ne_num`."""
    m = NL_SPCF_RE.search(nome)
    if m:
        return m.group(1), m.group(2).zfill(5)
    m = NL_RE.search(nome)
    if m:
        num = m.group(1).zfill(5)
        ano = m.group(2) or ""
        if ano and len(ano) == 2:
            ano = ("20" if int(ano) < 80 else "19") + ano
        return ano, num
    return None


def parse_nf_num(nome: str) -> Optional[str]:
    """Extrai número da NF (sem ano, zfill(5)). Retorna None se não parseável."""
    m = NF_RE.search(nome)
    if m:
        return m.group(1).zfill(5)
    return None


def parse_competencia(nome: str, texto_ocr: str = "") -> Optional[str]:
    """Extrai competência em formato canônico 'AAAA-MM'.

    Tenta no nome primeiro, depois no texto OCR. Retorna None se não parseável.

    Args:
        nome: nome do arquivo.
        texto_ocr: texto OCR (reforço).
    """
    # 1. AAAA-MM no nome
    m = COMPETENCIA_ISO_RE.search(nome)
    if m:
        ano, mes = m.group(1), m.group(2).zfill(2)
        if _competencia_valida(ano, mes):
            return f"{ano}-{mes}"

    # 2. MM/AAAA no nome
    m = COMPETENCIA_RE.search(nome)
    if m:
        mes, ano = m.group(1).zfill(2), m.group(2)
        if _competencia_valida(ano, mes):
            return f"{ano}-{mes}"

    # 3. Busca no texto OCR
    if texto_ocr:
        m = COMPETENCIA_ISO_RE.search(texto_ocr)
        if m and _competencia_valida(m.group(1), m.group(2).zfill(2)):
            return f"{m.group(1)}-{m.group(2).zfill(2)}"
        m = COMPETENCIA_RE.search(texto_ocr)
        if m and _competencia_valida(m.group(2), m.group(1).zfill(2)):
            return f"{m.group(2)}-{m.group(1).zfill(2)}"

    return None


def _competencia_valida(ano: str, mes: str) -> bool:
    """Sanity: ano entre 2010-2030 e mês entre 01-12."""
    try:
        a, m = int(ano), int(mes)
        return 2010 <= a <= 2030 and 1 <= m <= 12
    except (TypeError, ValueError):
        return False


def parse_valor_brl(texto: str) -> Optional[Decimal]:
    """Extrai primeiro valor BRL de um texto. Retorna Decimal ou None.

    >>> parse_valor_brl("Valor R$ 1.234,56 líquido")
    Decimal('1234.56')
    >>> parse_valor_brl("123,45")
    Decimal('123.45')

    NOTA: regra global CLAUDE.md — valores monetários sempre Decimal, nunca float.
    """
    m = VALOR_BRL_RE.search(texto or "")
    if not m:
        return None
    raw = m.group(1)
    # '1.234,56' → '1234.56'
    normalizado = raw.replace(".", "").replace(",", ".")
    try:
        return Decimal(normalizado)
    except InvalidOperation:
        return None


def parse_data_br(texto: str) -> Optional[str]:
    """Extrai primeira data (DD/MM/AAAA ou AAAA-MM-DD) e retorna ISO 'AAAA-MM-DD'.

    Aceita separadores /, -, . na forma BR e - na forma ISO.
    """
    m = DATA_ISO_RE.search(texto or "")
    if m and _data_valida(m.group(1), m.group(2), m.group(3)):
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = DATA_BR_RE.search(texto or "")
    if m and _data_valida(m.group(3), m.group(2), m.group(1)):
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return None


def _data_valida(a: str, m: str, d: str) -> bool:
    try:
        ai, mi, di = int(a), int(m), int(d)
        return 1990 <= ai <= 2099 and 1 <= mi <= 12 and 1 <= di <= 31
    except (TypeError, ValueError):
        return False


def parse_oficio_cobranca(nome: str) -> Optional[tuple[str, str]]:
    """Extrai (numero, ano) de ofício de cobrança. Retorna None se não parseável."""
    m = OFICIO_RE.search(nome)
    if m:
        num = m.group(1).zfill(3)
        ano = m.group(2)
        if len(ano) == 2:
            ano = ("20" if int(ano) < 80 else "19") + ano
        return num, ano
    return None


def tipo_certidao(nome: str, texto_ocr: str = "") -> str:
    """Classifica subtipo de certidão: CND-Federal, FGTS, Trabalhista, Falencia, Outro."""
    conteudo = f"{nome} {texto_ocr}".upper()
    if "FGTS" in conteudo:
        return "FGTS"
    if "TRABALHISTA" in conteudo or "CNDT" in conteudo:
        return "Trabalhista"
    if "FALENCIA" in conteudo or "FALÊNCIA" in conteudo or "FALENCIA" in conteudo:
        return "Falencia"
    if "FEDERAL" in conteudo or "RFB" in conteudo or "RECEITA FEDERAL" in conteudo:
        return "CND-Federal"
    if "MUNICIPAL" in conteudo:
        return "CND-Municipal"
    if "ESTADUAL" in conteudo:
        return "CND-Estadual"
    return "Outra"


def subtipo_extracao_spcf(nome: str) -> str:
    """Categoriza as 7 variantes de extração SPCF (HIST-V3, V2, V1, HTML, PDF, etc)."""
    partes: list[str] = []
    if "HIST__" in nome:
        partes.append("HIST-V3")
    elif "_V2__" in nome:
        partes.append("V2")
    elif "Documentacao_Contratos__" in nome:
        partes.append("V1")
    if "htmls_brutos" in nome:
        partes.append("HTML-Bruto")
    elif "pdfs_convertidos" in nome:
        partes.append("PDF-Convertido")
    elif "pdfs_oficiais_SPCF" in nome or "pdfs_spcf_reais" in nome:
        partes.append("PDF-Oficial-SPCF")
    if "DETRAN_REAL" in nome:
        partes.append("DETRAN-REAL")
    if "detalhe" in nome:
        partes.append("Detalhe-Pagina")
    elif "proposta" in nome.lower():
        partes.append("Proposta-Pagina")
    elif "tramite" in nome:
        partes.append("Tramite")
    return "-".join(partes) if partes else "Extracao-Indefinida"


# ============================================================================
# 5. Sanity-check (quando rodar como script)
# ============================================================================

if __name__ == "__main__":
    # Bateria mínima — não substitui testes pytest, mas sinaliza regressões grosseiras.
    assert parse_ct_num("Contrato 006/2021") == ("006", "2021"), "CT_NUM básico"
    assert parse_ct_num("CT-022.2014") == ("022", "2014"), "CT com hífen+ponto"
    assert parse_ct_num("075.2022 - PRODAM") == ("075", "2022"), "padrão curto"
    assert parse_ct_num("contrato_DETRAN_12086.pdf", MAPA_DETRAN) == ("003", "2026"), "SPCF_ID"
    assert parse_ct_num("Contrato 2762014 - Prazo.pdf", MAPA_DETRAN) == ("027", "2014"), "typo"
    assert parse_ta_ordinal("1º TA_Supressao.pdf") == "01", "TA ordinal numérico"
    assert parse_ta_ordinal("QUARTO TERMO ADITIVO.pdf") == "04", "TA ordinal palavra"
    assert parse_tipo_doc("Contrato 006_2021.pdf") == "Contrato-Base", "tipo contrato"
    assert parse_tipo_doc("NE 471 Cobertura.pdf") == "NE", "tipo NE"
    assert parse_tipo_doc("2024NL00123_extrato.pdf") == "NL", "tipo NL"
    assert parse_tipo_doc("NF-e 000012345.pdf") == "NF", "tipo NF"
    assert parse_tipo_doc("ACEITE TECNICO NF 12345.pdf") == "Aceite", "tipo Aceite"
    assert parse_tipo_doc("Certidao CND Federal.pdf") == "Certidao", "tipo Certidao"
    assert asciificar("Supressão Contratual") == "Supressao-Contratual", "asciificar"
    assert parse_competencia("FAT_09-2024_detalhe.pdf", "Competência: 09/2024") == "2024-09", "comp OCR"
    assert parse_valor_brl("R$ 1.234,56") == Decimal("1234.56"), "valor BRL"
    assert parse_ne_num("2024NE00471") == ("2024", "00471"), "NE SPCF"
    assert parse_ne_num("NE 471/2024") == ("2024", "00471"), "NE com ano"
    assert parse_data_br("Assinado em 15/03/2024.") == "2024-03-15", "data BR"
    print("OK — sanity-check passou.")
