"""
normalizador.py — Skill `normalizador-contratos-prodam` v1.1 (2026-04-23)

Normaliza numeros de contrato do Projeto PRODAM entre os 3 formatos que coexistem:
- Com zero a esquerda : '006/2021' (PDFs, spcf_contratos)
- Sem zero            : '6/2021'   (keys de profiles.json)
- Separador nao-barra : '6-2021', '6_2021', '006.2021' (filenames, CSVs, OCR)

Alem da normalizacao canonica, expoe:
- Deteccao de colisoes (contratos renumerados com 2 numeracoes — ex: CT 296/2025 = CT 3/2026)
- Mapas auxiliares por devedor: SPCF_ID, typos de filename, objeto do contrato, regime de correcao
- `parse_ct_num`: extrai (NNN, AAAA) zero-padded a partir de um filename

Retrocompatibilidade: toda API publica da v1.0 foi preservada.
"""
from __future__ import annotations

import re
from collections import defaultdict


# ---------------------------------------------------------------------------
# 1. NORMALIZACAO CANONICA (v1.0 — retrocompativel)
# ---------------------------------------------------------------------------
def normalizar_contrato(valor: str) -> str:
    """
    Normaliza '006/2021', '6/2021', '6-2021', '006.2021' -> '6/2021'.

    Retorna o valor original (trim) se nao casar com padrao conhecido.
    """
    if not valor:
        return ""
    m = re.match(r"0*(\d+)[/\-_.](\d{4})", valor.strip())
    if not m:
        return valor.strip()
    return f"{m.group(1)}/{m.group(2)}"


def mesmo_contrato(
    a: str,
    b: str,
    colisoes: list[list[str]] | None = None,
) -> bool:
    """Retorna True se a e b sao o mesmo contrato (normalizacao + mapa de colisoes)."""
    na = normalizar_contrato(a)
    nb = normalizar_contrato(b)
    if na == nb:
        return True
    if colisoes:
        for grupo in colisoes:
            grupo_norm = {normalizar_contrato(g) for g in grupo}
            if na in grupo_norm and nb in grupo_norm:
                return True
    return False


def detectar_colisoes_por_pdf(contratos: dict) -> list[tuple[str, list[str]]]:
    """
    contratos: {numero_normalizado: {"pdf": path}}
    Retorna lista de tuplas (pdf_path, [numeros_que_apontam]) com len > 1.
    """
    inv: dict[str, list[str]] = defaultdict(list)
    for num, meta in contratos.items():
        pdf = meta.get("pdf")
        if pdf:
            inv[pdf].append(num)
    return [(pdf, nums) for pdf, nums in inv.items() if len(nums) > 1]


# ---------------------------------------------------------------------------
# 2. MAPAS AUXILIARES (v1.1 — extraidos de rename_contratos_formal.py)
# ---------------------------------------------------------------------------

# Aliases de ID SPCF para (NNN, AAAA) — DETRAN
SPCF_ID_PARA_CT: dict[str, tuple[str, str]] = {
    "12086": ("003", "2026"),   # contrato_DETRAN_12086 = CT 003/2026 (prop 14421)
}

# Typos conhecidos no filesystem (filenames corrompidos) — DETRAN
FILENAME_TYPO_PARA_CT: dict[str, tuple[str, str]] = {
    "2762014": ("027", "2014"),  # "Contrato 2762014" -> 27/2014 (typo sem separador)
}

# Objeto de contrato-base por (NNN, AAAA) — DETRAN (CLAUDE.md §3.6)
# Convencao: ASCII puro, sem acento, palavras separadas por hifen.
OBJETO_CONTRATO_DETRAN: dict[tuple[str, str], str] = {
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
}

# Regime de correcao por (NNN, AAAA) — DETRAN (CLAUDE.md §1.2)
# Regimes canonicos: IGPM+1pct+2pct | Silente | Contratual | IGPM-via-4TA |
#                    IPCA | IPCA-via-5TA | SELIC-Lei-14905
REGIME_DETRAN: dict[tuple[str, str], str] = {
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
}


# Indice por devedor — extensivel
MAPAS_POR_DEVEDOR: dict[str, dict] = {
    "DETRAN": {
        "spcf_id": SPCF_ID_PARA_CT,
        "typos": FILENAME_TYPO_PARA_CT,
        "objeto": OBJETO_CONTRATO_DETRAN,
        "regime": REGIME_DETRAN,
    },
    "SES": {
        "spcf_id": {},
        "typos": {},
        "objeto": {},
        "regime": {},
    },
    "SSP": {
        "spcf_id": {},
        "typos": {},
        "objeto": {},
        "regime": {},
    },
}


def mapas_do_devedor(devedor: str) -> dict:
    """Retorna bloco de mapas para um devedor, ou blocos vazios se nao cadastrado."""
    return MAPAS_POR_DEVEDOR.get(devedor, {
        "spcf_id": {}, "typos": {}, "objeto": {}, "regime": {},
    })


# ---------------------------------------------------------------------------
# 3. PARSE_CT_NUM — extracao zero-padded (v1.1)
# ---------------------------------------------------------------------------
CT_NUM_RE = re.compile(
    r"(?:contrato|CT|ct)[\s_]*[Nn]?[ºo°\.]?[\s_]*0*(\d{1,3})[._\-/ ]+0*(\d{2,4})",
    re.IGNORECASE,
)
CT_NUM_SHORT_RE = re.compile(
    r"(?:^|[\s_])0*(\d{1,3})\.0*(\d{2,4})(?=[\s_\-.]|$)"
)  # "022.2014" / "22.14" / "83.22" -> (NNN, AAAA)
PROPOSTA_RE = re.compile(
    r"PROPOSTA[\s_]+0*(\d{1,3})[.\-/]0*(\d{2,4})",
    re.IGNORECASE,
)


def parse_ct_num(nome: str) -> tuple[str, str] | None:
    """
    Retorna (NNN, AAAA) zero-padded do contrato-base citado no filename.

    Ordem de cascata:
      1. SPCF_ID_PARA_CT  (IDs SPCF crus: 'contrato_DETRAN_12086')
      2. FILENAME_TYPO_PARA_CT  (typos conhecidos: '2762014' sem separador)
      3. CT_NUM_RE  (prefixo 'Contrato'/'CT')
      4. PROPOSTA_RE  (prefixo 'PROPOSTA')
      5. CT_NUM_SHORT_RE  (padrao curto standalone '022.2014') + sanity 2010-2030

    Expansao de ano 2 digitos: <80 -> '20xx'; >=80 -> '19xx'.

    Retorna None se nao bater nada ou se ano do short-form fugir do sanity.
    """
    # 1. IDs SPCF conhecidos
    for spcf_id, ct in SPCF_ID_PARA_CT.items():
        if spcf_id in nome:
            return ct
    # 2. Typos conhecidos
    for typo, ct in FILENAME_TYPO_PARA_CT.items():
        if typo in nome:
            return ct
    # 3. variantes explicitas com prefixo "Contrato" / "CT"
    m = CT_NUM_RE.search(nome)
    if m:
        num = m.group(1).zfill(3)
        ano = m.group(2)
        if len(ano) == 2:
            ano = ("20" if int(ano) < 80 else "19") + ano
        return num, ano
    # 4. proposta
    m = PROPOSTA_RE.search(nome)
    if m:
        num = m.group(1).zfill(3)
        ano = m.group(2)
        if len(ano) == 2:
            ano = ("20" if int(ano) < 80 else "19") + ano
        return num, ano
    # 5. padrao curto standalone (com sanity check de ano)
    m = CT_NUM_SHORT_RE.search(nome)
    if m:
        num, ano = m.group(1).zfill(3), m.group(2)
        if len(ano) == 2:
            ano = ("20" if int(ano) < 80 else "19") + ano
        if 2010 <= int(ano) <= 2030:
            return num, ano
    return None


# ---------------------------------------------------------------------------
# 4. TESTES INLINE
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # normalizar_contrato
    assert normalizar_contrato("006/2021") == "6/2021"
    assert normalizar_contrato("6/2021")   == "6/2021"
    assert normalizar_contrato("006-2021") == "6/2021"
    assert normalizar_contrato("022.2014") == "22/2014"
    assert normalizar_contrato("  3/2026 ") == "3/2026"
    assert normalizar_contrato("") == ""
    assert normalizar_contrato("nada-aqui") == "nada-aqui"

    # mesmo_contrato
    colisoes = [["296/2025", "3/2026"]]
    assert mesmo_contrato("006/2021", "6/2021", colisoes) is True
    assert mesmo_contrato("296/2025", "3/2026", colisoes) is True
    assert mesmo_contrato("75/2022", "83/2022", colisoes) is False
    assert mesmo_contrato("006/2021", "006/2021") is True

    # detectar_colisoes_por_pdf
    contratos = {
        "296/2025": {"pdf": "CT_003_2026_DETRAN.pdf"},
        "3/2026":   {"pdf": "CT_003_2026_DETRAN.pdf"},
        "75/2022":  {"pdf": "CT_075_2022_SIGMO.pdf"},
    }
    col = detectar_colisoes_por_pdf(contratos)
    assert len(col) == 1
    assert sorted(col[0][1]) == sorted(["296/2025", "3/2026"])

    # parse_ct_num
    assert parse_ct_num("contrato_DETRAN_12086.pdf") == ("003", "2026")
    assert parse_ct_num("Contrato 2762014 - Prazo.pdf") == ("027", "2014")
    assert parse_ct_num("CT 006_2021 MetroMao.pdf") == ("006", "2021")
    assert parse_ct_num("PROPOSTA 075.2022 SIGMO.pdf") == ("075", "2022")
    assert parse_ct_num("022.2014 - PRODAM - termo aditivo.pdf") == ("022", "2014")
    assert parse_ct_num("relatorio_anual_2023.pdf") is None

    # mapas_do_devedor
    d = mapas_do_devedor("DETRAN")
    assert d["objeto"][("006", "2021")] == "Rede-VPN-Firewall-MetroMao-Assessoria"
    assert d["regime"][("003", "2026")] == "SELIC-Lei-14905"
    assert mapas_do_devedor("INEXISTENTE") == {
        "spcf_id": {}, "typos": {}, "objeto": {}, "regime": {},
    }
    assert mapas_do_devedor("SES")["objeto"] == {}

    print("OK — todos os testes passaram")
