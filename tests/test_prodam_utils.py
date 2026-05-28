"""
Testes unitários para prodam_utils — funções monetárias e de normalização críticas.

Uso:
  cd C:\\Users\\gabri\\Desktop\\PROJETO_PRODAM
  py -3.12 -m pytest tests/ -v

Se pytest não instalado:
  py -3.12 -m pip install pytest
"""
from __future__ import annotations
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from prodam_utils import (
    brl, fmt_brl, pct_diff,
    norm, norm_variants, match_flex,
    parse_br_date, parse_comp, vencimento_30, esta_prescrita,
    is_metadata_key, norm_id, norm_contrato,
)

# ============================================================
# VALORES MONETÁRIOS
# ============================================================

class TestBrl:
    def test_none(self):
        assert brl(None) == Decimal(0)
        assert brl("") == Decimal(0)
        assert brl("-") == Decimal(0)

    def test_numero_simples(self):
        assert brl(123) == Decimal("123")
        assert brl(123.45) == Decimal("123.45")

    def test_brl_padrao(self):
        assert brl("R$ 1.234,56") == Decimal("1234.56")
        assert brl("R$1.234,56") == Decimal("1234.56")
        assert brl(" 1.234,56 ") == Decimal("1234.56")

    def test_decimal_sem_virgula(self):
        assert brl("1234.56") == Decimal("1234.56")
        assert brl("1234") == Decimal("1234")

    def test_valor_grande(self):
        assert brl("R$ 1.234.567,89") == Decimal("1234567.89")

    def test_valor_invalido_retorna_zero(self):
        assert brl("ABC") == Decimal(0)
        assert brl("R$") == Decimal(0)

    def test_nbsp_e_caracteres_especiais(self):
        # NBSP (\xa0) aparece no SPCF
        assert brl("R$\xa01.234,56") == Decimal("1234.56")

    def test_aceita_resultado_sql_sum(self):
        # SQLite SUM() retorna int, float ou None.
        # auditoria_completude_devedor.py:250,252 alimenta brl() com isso pós-fix
        # do bug D1 (float → Decimal). brl() precisa lidar com os 3.
        assert brl(None) == Decimal(0)
        assert brl(0) == Decimal(0)
        assert brl(1234567) == Decimal("1234567")
        assert brl(1234.56) == Decimal("1234.56")

class TestFmtBrl:
    def test_inteiro(self):
        assert fmt_brl(1234) == "R$ 1.234,00"

    def test_decimal(self):
        assert fmt_brl(1234.56) == "R$ 1.234,56"

    def test_grande(self):
        assert fmt_brl(1234567.89) == "R$ 1.234.567,89"

    def test_zero(self):
        assert fmt_brl(0) == "R$ 0,00"

    def test_invalido(self):
        assert fmt_brl("abc") == "R$ 0,00"
        assert fmt_brl(None) == "R$ 0,00"

    def test_aceita_decimal(self):
        # Pós-fix D1, auditoria_completude_devedor.py passa Decimal a fmt_brl
        # (via "empenhos_valor": brl(...)). fmt_brl precisa formatá-lo sem erro.
        assert fmt_brl(Decimal("1234.56")) == "R$ 1.234,56"
        assert fmt_brl(Decimal("0")) == "R$ 0,00"
        assert fmt_brl(Decimal("10463698.62")) == "R$ 10.463.698,62"

class TestPctDiff:
    def test_iguais(self):
        assert pct_diff(100, 100) == 0

    def test_metade(self):
        # pct = abs(100-50)/100 * 100 = 50%
        assert pct_diff(100, 50) == Decimal(50)

    def test_zero(self):
        assert pct_diff(0, 0) == 0

    def test_um_lado_zero(self):
        # max(100,0)=100, abs(100-0)/100 = 100%
        assert pct_diff(100, 0) == Decimal(100)

# ============================================================
# NORMALIZAÇÃO DE NOMES (core do fix unidecode)
# ============================================================

class TestNorm:
    def test_acentos(self):
        assert norm("POLÍCIA CIVIL") == "POLICIA CIVIL"
        assert norm("Polícia Civil") == "POLICIA CIVIL"
        assert norm("POLICIA CIVIL") == "POLICIA CIVIL"

    def test_case(self):
        assert norm("sedUc") == "SEDUC"

    def test_espacos(self):
        assert norm("  SEDUC   AM  ") == "SEDUC AM"

    def test_none_vazio(self):
        assert norm(None) == ""
        assert norm("") == ""

    def test_caracteres_especiais(self):
        assert norm("FUAM/FUHAM") == "FUAM/FUHAM"
        assert norm("AÇÃO") == "ACAO"
        assert norm("INFORMATIZAÇÃO") == "INFORMATIZACAO"

class TestNormVariants:
    def test_sem_slash(self):
        assert norm_variants("SEDUC") == {"SEDUC"}

    def test_com_slash(self):
        vs = norm_variants("SES/SUSAM")
        assert "SES/SUSAM" in vs
        assert "SES" in vs
        assert "SUSAM" in vs

    def test_fuam(self):
        vs = norm_variants("FUAM/FUHAM")
        assert vs == {"FUAM/FUHAM", "FUAM", "FUHAM"}

class TestMatchFlex:
    def test_match_exato(self):
        assert match_flex("SEDUC", ["SEDUC", "SES"]) == "SEDUC"

    def test_match_case_acento(self):
        assert match_flex("POLÍCIA CIVIL", ["POLICIA CIVIL"]) == "POLICIA CIVIL"

    def test_sem_match(self):
        assert match_flex("XPTO", ["SEDUC", "SES"]) is None

# ============================================================
# DATAS
# ============================================================

class TestParseBrDate:
    def test_valido(self):
        assert parse_br_date("28/01/2019") == date(2019, 1, 28)

    def test_invalido(self):
        assert parse_br_date(None) is None
        assert parse_br_date("") is None
        assert parse_br_date("abc") is None
        assert parse_br_date("30/02/2019") is None  # dia inválido

    def test_com_espacos(self):
        assert parse_br_date(" 28/01/2019 ") == date(2019, 1, 28)

class TestParseComp:
    def test_valido(self):
        assert parse_comp("05/2021") == date(2021, 5, 1)

    def test_invalido(self):
        assert parse_comp(None) is None
        assert parse_comp("2021") is None

class TestVencimento30:
    def test_basico(self):
        assert vencimento_30("01/01/2021") == date(2021, 1, 31)

    def test_invalido(self):
        assert vencimento_30(None) is None

class TestEstaPrescrita:
    def test_prescrita(self):
        # Vencimento há 10 anos → prescrita
        hoje = date(2026, 4, 14)
        assert esta_prescrita(date(2016, 1, 1), hoje=hoje) is True

    def test_nao_prescrita(self):
        hoje = date(2026, 4, 14)
        assert esta_prescrita(date(2025, 1, 1), hoje=hoje) is False

    def test_borderline(self):
        # Exatamente no cutoff (5 anos -1 dia)
        hoje = date(2026, 4, 14)
        from datetime import timedelta
        cutoff = hoje - timedelta(days=365*5)
        assert esta_prescrita(cutoff - timedelta(days=1), hoje=hoje) is True
        assert esta_prescrita(cutoff + timedelta(days=1), hoje=hoje) is False

    def test_none(self):
        assert esta_prescrita(None) is False

# ============================================================
# METADATA E IDS
# ============================================================

class TestIsMetadataKey:
    def test_metadata(self):
        assert is_metadata_key("_metadata") is True
        assert is_metadata_key("_internal") is True

    def test_devedor(self):
        assert is_metadata_key("SEDUC") is False
        assert is_metadata_key("SES/SUSAM") is False

    def test_edge(self):
        assert is_metadata_key(None) is False
        assert is_metadata_key("") is False

class TestNormId:
    def test_inteiro_string(self):
        assert norm_id("161532") == "161532"

    def test_float_artifact(self):
        assert norm_id("161532.0") == "161532"
        assert norm_id(161532.0) == "161532"

    def test_int(self):
        assert norm_id(161532) == "161532"

    def test_string_nao_numerica(self):
        assert norm_id("ABC") == "ABC"

    def test_vazio(self):
        assert norm_id(None) == ""
        assert norm_id("") == ""

class TestNormContrato:
    def test_basico(self):
        assert norm_contrato("018/2021") == "18/2021"
        assert norm_contrato("C.18/2021") == "18/2021"
        assert norm_contrato(" 018/2021 ") == "18/2021"

    def test_sem_barra(self):
        assert norm_contrato("2021") == "2021"

    def test_vazio(self):
        assert norm_contrato(None) == ""
        assert norm_contrato("") == ""


if __name__ == "__main__":
    # Execução standalone sem pytest
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    import inspect
    ok = 0
    fail = 0
    for name, cls in list(globals().items()):
        if inspect.isclass(cls) and name.startswith("Test"):
            inst = cls()
            for mname in dir(inst):
                if mname.startswith("test_"):
                    try:
                        getattr(inst, mname)()
                        print(f"  [OK] {name}.{mname}")
                        ok += 1
                    except AssertionError as e:
                        print(f"  [FAIL] {name}.{mname}: assertion")
                        fail += 1
                    except Exception as e:
                        print(f"  [ERR ] {name}.{mname}: {type(e).__name__}: {e}")
                        fail += 1
    print(f"\n{ok} passou / {fail} falhou")
    sys.exit(0 if fail == 0 else 1)
