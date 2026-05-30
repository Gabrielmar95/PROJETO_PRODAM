"""
Testes de regressão estrutural — Janela 2, item 2.4 (Bugs D1 + DRY).

Esses testes verificam o TEXTO/AST dos scripts, não rodam o código
(os scripts têm top-level DB/JSON connect que requer PRODAM_DOCS/profiles.json
e prodam.db locais, indisponíveis em CI).

Garantem que:
  - auditoria_completude_devedor.py usa brl() (Decimal) em empenhos_valor/faturas_valor
  - dossie_multiformato_devedor.py importa brl/fmt_brl de prodam_utils (DRY)
  - dossie_multiformato_devedor.py NÃO tem helpers brl/fmt_brl locais (DRY)
  - dossie_multiformato_devedor.py NÃO tem `except:` nu (bug D3)

Imports e helpers são detectados via AST para tolerar refatoração inocente
(imports multi-linha parentetizados, helpers indentados, `except:` com comentário).
"""
from __future__ import annotations
import ast
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def _read(rel: str) -> str:
    return (SCRIPTS / rel).read_text(encoding="utf-8")


def _parse(rel: str) -> ast.Module:
    return ast.parse(_read(rel))


class TestAuditoriaCompletudeUsaDecimal:
    @pytest.mark.parametrize("campo", ["empenhos_valor", "faturas_valor"])
    def test_campo_usa_brl(self, campo):
        # Captura a linha inteira pós-':' (não trunca em vírgula interna do .get).
        texto = _read("auditoria_completude_devedor.py")
        m = re.search(rf'"{campo}":\s*([^\n]+)', texto)
        assert m, f"campo {campo} não encontrado em auditoria_completude_devedor.py"
        expr = m.group(1)
        assert "brl(" in expr, (
            f"{campo} deve usar brl() (Regra #16 Decimal). Encontrado: {expr!r}"
        )
        assert "float(" not in expr, (
            f"{campo} NÃO pode usar float() (Regra #16 Decimal). Encontrado: {expr!r}"
        )


class TestDossieMultiformatoUsaProdamUtils:
    def test_importa_brl_e_fmt_brl_de_prodam_utils(self):
        # AST tolera imports parentetizados multi-linha (PEP8).
        tree = _parse("dossie_multiformato_devedor.py")
        importados: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "prodam_utils":
                importados.update(alias.name for alias in node.names)
        assert "brl" in importados, (
            f"dossie deve importar brl de prodam_utils (DRY). Encontrado: {sorted(importados)}"
        )
        assert "fmt_brl" in importados, (
            f"dossie deve importar fmt_brl de prodam_utils (DRY). Encontrado: {sorted(importados)}"
        )

    @pytest.mark.parametrize("helper", ["brl", "fmt_brl"])
    def test_nao_tem_helper_local(self, helper):
        # AST: pega função em qualquer nível (top-level, indentada em try/except shadow).
        tree = _parse("dossie_multiformato_devedor.py")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == helper:
                pytest.fail(
                    f"dossie NÃO pode ter helper {helper}() local em qualquer nível "
                    f"(DRY: deve usar prodam_utils.{helper}). Definido na linha {node.lineno}."
                )

    def test_nao_tem_except_nu(self):
        # Bug D3: except: nu engole erros silenciosos.
        # AST detecta em qualquer formatação: `except:`, `except: pass`, `except: # comentário`.
        tree = _parse("dossie_multiformato_devedor.py")
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                pytest.fail(
                    f"dossie NÃO pode ter `except:` nu (bug D3) em linha {node.lineno}. "
                    f"Use `except Exception as e:` com log."
                )


class TestIssue11CatADRY:
    """Issue 11 Cat A: 4 scripts consolidam os helpers brl/fmt_brl locais → prodam_utils.

    AST-based (não roda os scripts — todos carregam profiles.json/prodam.db ou
    regeneram CLAUDE.md no import). `alias.name` ignora o `as` (ex.: `fmt_brl as brl`
    conta como import de fmt_brl).
    """

    CAT_A = [
        "ses_reconciliacao_completa.py",
        "auto_update_claude_md.py",
        "gerar_relatorio_docx.py",
        "detalhamento_faturas.py",
    ]

    @pytest.mark.parametrize("script", CAT_A)
    def test_nao_tem_helper_brl_local(self, script):
        # AST: pega def em qualquer nível (top-level OU aninhada em função).
        tree = _parse(script)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in ("brl", "fmt_brl"):
                pytest.fail(
                    f"{script}: helper {node.name}() local na linha {node.lineno} "
                    f"(DRY Issue 11 Cat A: usar prodam_utils)."
                )

    @pytest.mark.parametrize("script", CAT_A)
    def test_importa_helper_de_prodam_utils(self, script):
        tree = _parse(script)
        importados: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "prodam_utils":
                importados.update(a.name for a in node.names)  # nome ORIGINAL (ignora 'as')
        assert importados & {"brl", "fmt_brl"}, (
            f"{script}: deve importar brl e/ou fmt_brl de prodam_utils (DRY). "
            f"Importados de prodam_utils: {sorted(importados)}"
        )


class TestReconciliarOrfaosReversosDecimal:
    """Issue 12 Tier 1: `reconciliar_orfaos_reversos.py` escrevia `float(val_fat)` no
    profiles.json (SSOT) — causa-raiz plausível da deriva da Issue 03. Fix: `str(val_fat)`
    preserva precisão Decimal; consumidores (auto_update/dossie/notificacao/reconciliacao_4f/
    alerta_prescricao) já toleram string. Trava por AST porque o script tem top-level
    DB/JSON connect e muta SSOT (não roda em cloud sem PRODAM_DOCS)."""

    SCRIPT = "reconciliar_orfaos_reversos.py"

    def test_grava_val_exig_sem_float(self):
        # AST: para todo Assign cujo target é Subscript(pr, "val_exig"),
        # o valor NÃO pode ser uma Call de float() (Regra #16: nunca float em moeda).
        tree = _parse(self.SCRIPT)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for tgt in node.targets:
                if not isinstance(tgt, ast.Subscript):
                    continue
                slc = tgt.slice
                key = slc.value if isinstance(slc, ast.Constant) else None
                if key != "val_exig":
                    continue
                val = node.value
                if isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and val.func.id == "float":
                    pytest.fail(
                        f"{self.SCRIPT}: linha {node.lineno} escreve pr['val_exig'] via "
                        f"float() — viola Regra #16 (Issue 12 Tier 1). Use str(val_fat)."
                    )

    def test_nao_tem_except_nu(self):
        # Bug D3 também ocorria aqui (linha 67 original). Fix consolidou via brl().
        tree = _parse(self.SCRIPT)
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                pytest.fail(
                    f"{self.SCRIPT}: `except:` nu na linha {node.lineno} (bug D3). "
                    f"Use brl() para parse Decimal-aware ou `except Exception as e:`."
                )

    def test_importa_brl_de_prodam_utils(self):
        # brl() é o helper Decimal-aware que substituiu o bloco isinstance/float/except nu.
        tree = _parse(self.SCRIPT)
        importados: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "prodam_utils":
                importados.update(a.name for a in node.names)
        assert "brl" in importados, (
            f"{self.SCRIPT}: deve importar brl de prodam_utils (Issue 12 Tier 1). "
            f"Importados: {sorted(importados)}"
        )


if __name__ == "__main__":
    # Paridade com tests/test_prodam_utils.py: permite rodar standalone.
    sys.exit(pytest.main([__file__, "-v"]))
