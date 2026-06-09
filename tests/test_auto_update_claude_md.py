"""
Testes unitários para scripts/auto_update_claude_md.py (gerador do CLAUDE.md).

Cobre: validate_profiles (fail-fast), compute_metrics (Decimal, buckets de
prescrição urgente/vencida/sem-data, tie-break determinístico) e âncoras
críticas do CLAUDE.md gerado (bloco NUNCA, 13 regras, alerta de vencidas,
path corrigido do catálogo de precedentes). Nenhum teste escreve nos .md reais.
"""
from __future__ import annotations
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import auto_update_claude_md as g  # noqa: E402


def _dev(val="1000.00", cat="GOV_DIRETA", forca="FORTE", passo="ENVIAR_TRD",
         dp=None, fat=(10, 6, 4), va="2000.00"):
    d = {
        "val_exig": val, "val_orig": val, "val_atualizado": va,
        "categoria": cat, "forca_probatoria": forca, "proximo_passo": passo,
        "fase_atual": "F1",
        "faturas_total": fat[0], "faturas_exigiveis": fat[1],
        "faturas_prescritas": fat[2],
    }
    if dp is not None:
        d["data_prescricao_proxima"] = dp
    return d


def _base_data(n=55):
    data = {"_metadata": {"versao": "test"}}
    for i in range(n):
        data[f"DEV{i:02d}"] = _dev()
    return data


# ============================================================
# validate_profiles — fail-fast
# ============================================================

class TestValidateProfiles:
    def test_ok(self):
        assert g.validate_profiles(_base_data()) is True

    def test_nao_dict(self):
        with pytest.raises(g.ProfilesInvalidos):
            g.validate_profiles([1, 2, 3])

    def test_sem_metadata(self):
        d = _base_data()
        d.pop("_metadata")
        with pytest.raises(g.ProfilesInvalidos):
            g.validate_profiles(d)

    def test_truncado_menos_de_50(self):
        with pytest.raises(g.ProfilesInvalidos):
            g.validate_profiles(_base_data(10))

    def test_perfil_nao_dict(self):
        d = _base_data()
        d["DEV00"] = "string solta"
        with pytest.raises(g.ProfilesInvalidos):
            g.validate_profiles(d)

    def test_soma_exigivel_zero(self):
        d = {"_metadata": {}}
        for i in range(55):
            d[f"DEV{i:02d}"] = _dev(val="0")
        with pytest.raises(g.ProfilesInvalidos):
            g.validate_profiles(d)


# ============================================================
# compute_metrics — Decimal + buckets de prescrição
# ============================================================

class TestComputeMetrics:
    def test_somas_em_decimal_sem_erro_de_float(self):
        d = {"_metadata": {}, "A": _dev(val="0.10"), "B": _dev(val="0.20")}
        m = g.compute_metrics(d)
        assert isinstance(m["val_exig"], Decimal)
        assert m["val_exig"] == Decimal("0.30")  # float daria 0.30000000000000004

    def test_metadata_excluida_da_contagem(self):
        m = g.compute_metrics({"_metadata": {}, "A": _dev()})
        assert m["total"] == 1

    def test_bucket_urgente_futura(self):
        dp = (date.today() + timedelta(days=30)).isoformat()
        m = g.compute_metrics({"_metadata": {}, "A": _dev(dp=dp)})
        assert len(m["prescricao_urgente"]) == 1
        assert not m["prescricao_vencida"]

    def test_bucket_vencida_nao_some(self):
        # Regressão 2026-06-09: data no passado era descartada em silêncio
        # pelo filtro `0 < dias <= 90` (22 devedores invisíveis, incl. SEDUC).
        dp = (date.today() - timedelta(days=81)).isoformat()
        m = g.compute_metrics({"_metadata": {}, "A": _dev(dp=dp)})
        assert len(m["prescricao_vencida"]) == 1
        assert not m["prescricao_urgente"]

    def test_data_de_hoje_conta_como_vencida(self):
        m = g.compute_metrics(
            {"_metadata": {}, "A": _dev(dp=date.today().isoformat())})
        assert len(m["prescricao_vencida"]) == 1

    def test_sem_data_null_e_nao_parseavel(self):
        m = g.compute_metrics(
            {"_metadata": {}, "A": _dev(), "B": _dev(dp="N/A")})
        assert {s for s, _ in m["prescricao_sem_data"]} == {"A", "B"}

    def test_n_val_atualizado_ignora_null(self):
        d = {"_metadata": {}, "A": _dev(), "B": _dev(va=None)}
        m = g.compute_metrics(d)
        assert m["n_val_atualizado"] == 1

    def test_ordenacao_desc_com_tie_break_por_sigla(self):
        d = {"_metadata": {}, "B": _dev(val="100"), "A": _dev(val="100"),
             "C": _dev(val="200")}
        m = g.compute_metrics(d)
        assert [x[0] for x in m["top10"]] == ["C", "A", "B"]


# ============================================================
# generate_claude_md — âncoras críticas do output
# ============================================================

class TestGenerateClaudeMd:
    def _m(self, **kw):
        data = {"_metadata": {}}
        for i in range(3):
            data[f"DEV{i}"] = _dev()
        data.update(kw)
        return g.compute_metrics(data)

    def test_bloco_nunca_presente(self):
        out = g.generate_claude_md(self._m())
        assert "## 0. NUNCA" in out
        assert "ANTHROPIC_API_KEY" in out
        assert "FUHAM" in out and "FHAJ" in out

    def test_exatamente_13_regras(self):
        out = g.generate_claude_md(self._m())
        sec5 = out.split("## 5. REGRAS JURÍDICAS")[1].split("## 6.")[0]
        assert "\n13. Jurisprudência" in sec5
        assert "\n14. " not in sec5  # "Lei 14.905" não conta — exige nº de regra

    def test_alerta_vencida_aparece_no_claude_md(self):
        dp = (date.today() - timedelta(days=10)).isoformat()
        out = g.generate_claude_md(self._m(XISTO=_dev(val="999999.99", dp=dp)))
        assert "PASSADO/stale" in out
        assert "XISTO" in out  # maior exigível citado no agregado

    def test_path_precedentes_corrigido(self):
        out = g.generate_claude_md(self._m())
        assert "11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md" in out

    def test_arquivo_drift_removido(self):
        out = g.generate_claude_md(self._m())
        assert "_ARQUIVO_DRIFT" not in out

    def test_decreto_vigente_e_revogado(self):
        out = g.generate_claude_md(self._m())
        assert "53.464/2026" in out
        assert "revogou o 51.084/2025" in out

    def test_rpv_lei_correta(self):
        out = g.generate_claude_md(self._m())
        assert "Lei AM 2.748/2002" in out
        assert "teto **federal**" in out
