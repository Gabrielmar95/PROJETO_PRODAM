"""
Testes de regressão estrutural — Janela 2, item 2.4 (Bugs D1 + DRY).

Esses testes são "lints": verificam o TEXTO dos scripts, não rodam o código
(os scripts têm top-level DB/JSON connect que requer PRODAM_DOCS/profiles.json
e prodam.db locais, indisponíveis em CI).

Garantem que:
  - auditoria_completude_devedor.py usa brl() (Decimal) em empenhos_valor/faturas_valor
  - dossie_multiformato_devedor.py importa brl/fmt_brl de prodam_utils (DRY)
  - dossie_multiformato_devedor.py NÃO tem helpers brl/fmt_brl locais (DRY)
  - dossie_multiformato_devedor.py NÃO tem `except:` nu (bug D3)
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def _read(rel: str) -> str:
    return (SCRIPTS / rel).read_text(encoding="utf-8")


class TestAuditoriaCompletudeUsaDecimal:
    def test_empenhos_valor_usa_brl(self):
        texto = _read("auditoria_completude_devedor.py")
        m = re.search(r'"empenhos_valor":\s*([^,\n]+)', texto)
        assert m, "campo empenhos_valor não encontrado em auditoria_completude_devedor.py"
        expr = m.group(1)
        assert "brl(" in expr, (
            f"empenhos_valor deve usar brl() (Regra #16 Decimal). "
            f"Encontrado: {expr!r}"
        )
        assert "float(" not in expr, (
            f"empenhos_valor NÃO pode usar float() (Regra #16 Decimal). "
            f"Encontrado: {expr!r}"
        )

    def test_faturas_valor_usa_brl(self):
        texto = _read("auditoria_completude_devedor.py")
        m = re.search(r'"faturas_valor":\s*([^,\n]+)', texto)
        assert m, "campo faturas_valor não encontrado em auditoria_completude_devedor.py"
        expr = m.group(1)
        assert "brl(" in expr, (
            f"faturas_valor deve usar brl() (Regra #16 Decimal). "
            f"Encontrado: {expr!r}"
        )
        assert "float(" not in expr, (
            f"faturas_valor NÃO pode usar float() (Regra #16 Decimal). "
            f"Encontrado: {expr!r}"
        )


class TestDossieMultiformatoUsaProdamUtils:
    def test_importa_brl_e_fmt_brl_de_prodam_utils(self):
        texto = _read("dossie_multiformato_devedor.py")
        m = re.search(r'from\s+prodam_utils\s+import\s+([^\n]+)', texto)
        assert m, "import de prodam_utils não encontrado"
        importados = {x.strip() for x in m.group(1).split(",")}
        assert "brl" in importados, (
            f"dossie_multiformato_devedor.py deve importar brl de prodam_utils (DRY). "
            f"Encontrado: {importados}"
        )
        assert "fmt_brl" in importados, (
            f"dossie_multiformato_devedor.py deve importar fmt_brl de prodam_utils (DRY). "
            f"Encontrado: {importados}"
        )

    def test_nao_tem_helper_brl_local(self):
        texto = _read("dossie_multiformato_devedor.py")
        m = re.search(r'^def\s+brl\s*\(', texto, re.MULTILINE)
        assert m is None, (
            "dossie_multiformato_devedor.py NÃO pode ter helper brl() local "
            "(DRY: deve usar prodam_utils.brl)"
        )

    def test_nao_tem_helper_fmt_brl_local(self):
        texto = _read("dossie_multiformato_devedor.py")
        m = re.search(r'^def\s+fmt_brl\s*\(', texto, re.MULTILINE)
        assert m is None, (
            "dossie_multiformato_devedor.py NÃO pode ter helper fmt_brl() local "
            "(DRY: deve usar prodam_utils.fmt_brl)"
        )

    def test_nao_tem_except_nu(self):
        # Bug D3: except: nu engole erros silenciosos.
        texto = _read("dossie_multiformato_devedor.py")
        m = re.search(r'^\s*except\s*:\s*$', texto, re.MULTILINE)
        assert m is None, (
            "dossie_multiformato_devedor.py NÃO pode ter `except:` nu (bug D3). "
            "Use `except Exception as e:` com log."
        )
