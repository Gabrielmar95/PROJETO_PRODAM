"""Regressao das guardas anti-data do organizador (v2.1.1).

Autor: Gabriel Mar (OAB/AM 15.697) — Contrato 002/2026 PRODAM
O modulo testado vive em PRODAM_DOCS/ (fora do repo); em CI o teste e pulado.

Bugs cobertos (confirmados por verificacao adversarial em 11/06/2026):
- par direto: 'DD MM AAAA' no nome virava contrato MM/AAAA (ex.: 16-03-2026 -> 3/2026);
- colado: 'MMAAAA' colado com data ISO no nome virava contrato (ex.: TA_042020_
  PRODAM_2020-04-30 -> contrato 4/2020 do SEAD; 34 misatribuicoes no manifesto).
"""
import importlib.util
from pathlib import Path

import pytest

SRC = (Path(__file__).resolve().parent.parent / "PRODAM_DOCS" / "_SKILLS"
       / "organizador-arquivos-prodam" / "scripts" / "planejar_organizacao.py")

pytestmark = pytest.mark.skipif(
    not SRC.exists(), reason="PRODAM_DOCS ausente (CI) — modulo fora do repo")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("plan_org", SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PARES = {("3", "2026"): "DETRAN", ("22", "2014"): "DETRAN"}
COLADOS = {"0222014": "DETRAN", "042020": "SEAD", "072020": "SEAD",
           "52020": "SEAD"}
IDX_CT = (PARES, COLADOS)

CASOS = [
    # (nome, partes_rel, esperado, descricao)
    ("CONTRATO_122007_PRODAM_2026-03-16_ASS.pdf", [], "",
     "data ISO nao vira contrato 3/2026 (branco invertido removido)"),
    ("CONTRATO 16-03-2026 relatorio.pdf", [], "",
     "data DD-MM-AAAA barrada pela guarda do par direto"),
    ("CONTRATO 022 2014 ANEXO.pdf", [], "DETRAN", "par direto legitimo"),
    ("TA_0222014_FVS.pdf", [], "DETRAN", "colado legitimo NNN+AAAA"),
    ("CONTRATO_002-2026_BRANDAO (3).pdf", [], "",
     "sufixo de copia (3)+2026 nao vira contrato 3/2026"),
    ("022 2014 avulso.pdf", ["pasta_qualquer"], "",
     "sem contexto contratual a funcao nao atua"),
    ("relatorio CT 03 2026.pdf", [], "DETRAN",
     "MM AAAA sem dia antes = contrato valido 3/2026"),
    ("TA_042020_PRODAM_2020-04-30_dd955c.pdf", [], "",
     "colado 042020 + data ISO 2020-04 no nome = data, nao contrato"),
    ("TA_072020_PRODAM_2020-07-23_abc123.pdf", [], "",
     "colado 072020 + data ISO 2020-07 no nome = data, nao contrato"),
    ("TA_042020_FAPEAM_2020-04-07_590e2c.pdf", [], "",
     "colado-data com orgao terceiro no nome"),
    ("TA_042020_SEAD_ANEXO.pdf", [], "SEAD",
     "colado 042020 SEM data ISO no nome = contrato valido"),
    ("CT_52020_SEAD_2021-01-15_x.pdf", [], "SEAD",
     "colado 5 digitos com data de outro mes/ano = contrato valido"),
    ("CT_52020_SEAD_2020-05-04_x.pdf", [], "",
     "colado 5 digitos 5+2020 + data ISO 2020-05 = data"),
]


@pytest.mark.parametrize("nome,partes,esperado,desc",
                         CASOS, ids=[c[3] for c in CASOS])
def test_devedor_por_contrato_anti_data(mod, nome, partes, esperado, desc):
    assert mod._devedor_por_contrato(nome, partes, IDX_CT) == esperado


def test_versao_minima(mod):
    # guardas existem a partir da 2.1.1
    assert tuple(int(x) for x in mod.__version__.split(".")) >= (2, 1, 1)
