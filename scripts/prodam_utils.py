"""
prodam_utils.py — utilitários compartilhados do Projeto PRODAM.

Funções críticas usadas em múltiplos scripts:
  - brl(v): normaliza valor BRL para Decimal
  - fmt_brl(v): formata valor como "R$ 1.234,56"
  - norm(s): normaliza nome (uppercase + unidecode) — resolve órfãos
  - parse_br_date(s): "28/01/2019" → date
  - parse_comp(s): "05/2021" → date(2021, 5, 1)
  - is_metadata_key(k): detecta se uma chave do profiles.json é metadata
  - load_profiles(path=None): carrega profiles.json retornando só devedores
"""
from __future__ import annotations
import json, re
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import date, datetime, timedelta
from typing import Any, Iterable

try:
    from unidecode import unidecode
except ImportError:
    # Fallback simples se unidecode não estiver instalado
    def unidecode(s: str) -> str:
        import unicodedata
        nfkd = unicodedata.normalize("NFKD", s)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

# ============================================================
# VALORES MONETÁRIOS
# ============================================================

_MONEY_STRIP_RX = re.compile(r"[R$\s\xa0\ufeff\ufffd]")

def brl(s: Any) -> Decimal:
    """
    Normaliza valor BRL para Decimal.
    Aceita: None, int, float, str ("R$ 1.234,56", "1234.56", "1,56", etc.)
    """
    if s is None or s == "":
        return Decimal(0)
    if isinstance(s, (int, float)):
        return Decimal(str(s))
    s = str(s).strip()
    s = _MONEY_STRIP_RX.sub("", s).replace("\ufffd", "")
    if not s or s == "-":
        return Decimal(0)
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return Decimal(0)

def fmt_brl(v: Any) -> str:
    """Formata valor como 'R$ 1.234,56' (formato brasileiro).

    Strict-Decimal (Regra #16): nunca usa float(). Valores Decimal acima de
    15 dígitos significativos preservam precisão exata. Entradas None/inválidas
    viram Decimal(0) via brl().
    """
    d = v if isinstance(v, Decimal) else brl(v)
    return f"R$ {d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def pct_diff(a: Any, b: Any) -> Decimal:
    """Percent difference entre dois valores: abs(a-b)/max(a,b) * 100."""
    da = brl(a); db = brl(b)
    maior = max(abs(da), abs(db))
    if maior == 0:
        return Decimal(0)
    return abs(da - db) / maior * Decimal(100)

# ============================================================
# NORMALIZAÇÃO DE NOMES (resolve acentos + case)
# ============================================================

def norm(s: Any) -> str:
    """
    Normaliza nome: uppercase + unidecode + strip + colapsa espaços.
    Usa para matching entre fontes:
      norm('POLÍCIA CIVIL') == norm('Polícia Civil') == norm('POLICIA CIVIL') == 'POLICIA CIVIL'
    """
    if not s:
        return ""
    s = str(s).strip()
    s = unidecode(s).upper()
    s = re.sub(r"\s+", " ", s)
    return s

def norm_variants(s: Any) -> set[str]:
    """
    Gera variantes para matching flexível:
      'SES/SUSAM' → {'SES/SUSAM', 'SES', 'SUSAM'}
      'FUAM/FUHAM' → {'FUAM/FUHAM', 'FUAM', 'FUHAM'}
    """
    if not s:
        return set()
    base = norm(s)
    variantes = {base}
    if "/" in base:
        for part in base.split("/"):
            p = part.strip()
            if p: variantes.add(p)
    return variantes

def match_flex(alvo: str, candidatos: Iterable[str], limiar: float = 0.8) -> str | None:
    """
    Busca match flexível. Retorna o candidato que der melhor ratio, ou None se < limiar.
    """
    from difflib import SequenceMatcher
    alvo_n = norm(alvo)
    best = None
    for c in candidatos:
        c_n = norm(c)
        if not c_n: continue
        if alvo_n == c_n:
            return c
        r = SequenceMatcher(None, alvo_n, c_n).ratio()
        if r >= limiar and (best is None or r > best[1]):
            best = (c, r)
    return best[0] if best else None

# ============================================================
# DATAS
# ============================================================

def parse_br_date(s: Any) -> date | None:
    """'28/01/2019' → date(2019, 1, 28). Retorna None se inválido."""
    if not s or "/" not in str(s):
        return None
    try:
        return datetime.strptime(str(s).strip(), "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None

def parse_comp(s: Any) -> date | None:
    """'05/2021' (competência) → date(2021, 5, 1)."""
    if not s or "/" not in str(s):
        return None
    try:
        m, y = str(s).strip().split("/", 1)
        return date(int(y), int(m), 1)
    except (ValueError, TypeError):
        return None

def vencimento_30(emissao: Any) -> date | None:
    """Vencimento estimado = emissao + 30 dias."""
    d = parse_br_date(emissao)
    if not d: return None
    return d + timedelta(days=30)

def esta_prescrita(venc: date | None, hoje: date | None = None) -> bool:
    """
    Verifica se uma fatura está prescrita (> 5 anos desde vencimento).
    Se hoje é None, usa date.today().
    """
    if venc is None:
        return False
    if hoje is None:
        hoje = date.today()
    cutoff = hoje - timedelta(days=365 * 5)
    return venc < cutoff

# ============================================================
# PROFILES.JSON
# ============================================================

def is_metadata_key(k: str) -> bool:
    """Retorna True se a chave é metadata (ex: _metadata) e não um devedor."""
    return bool(k) and str(k).startswith("_")

def load_profiles(path: Any = None, include_metadata: bool = False) -> dict:
    """
    Carrega profiles.json retornando apenas devedores (pula _metadata por padrão).
    Se path é None, usa o caminho padrão do projeto.
    """
    if path is None:
        path = Path(__file__).parent.parent / "PRODAM_DOCS" / "profiles.json"
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if include_metadata:
        return data
    return {k: v for k, v in data.items() if not is_metadata_key(k)}

# ============================================================
# IDs
# ============================================================

def norm_id(x: Any) -> str:
    """Normaliza IDs numéricos: '161532' == '161532.0' == 161532."""
    if x is None:
        return ""
    s = str(x).strip()
    if not s:
        return ""
    if s.endswith(".0"):
        s = s[:-2]
    try:
        return str(int(float(s)))
    except (ValueError, TypeError):
        return s

def norm_contrato(c: Any) -> str:
    """Normaliza contrato: '018/2021' == 'C.18/2021' == ' 018/2021' == '18/2021'."""
    if not c:
        return ""
    s = str(c).strip().replace("C.", "").replace("c.", "")
    if "/" in s:
        a, b = s.split("/", 1)
        try:
            return f"{int(a)}/{b.strip()}"
        except ValueError:
            return s
    return s
