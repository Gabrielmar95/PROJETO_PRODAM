"""
Testes unitários para scripts/alerta_prescricao.py.

Cobre: classificação por bucket, agregados, JSON estruturado, exit codes,
CSV inexistente, casos-limite (sem alerta, só PROTEGIDA_ART202_VI, etc.).
"""
from __future__ import annotations
import json
import sys
import csv
from pathlib import Path

import pytest

# Adiciona scripts/ ao path para importar alerta_prescricao como módulo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import alerta_prescricao as ap  # noqa: E402


HEADERS = ["sigla", "categoria", "forca", "val_exig", "val_atualizado",
           "proximo_passo", "fat_exig", "fat_presc", "urg_presc", "d_plus", "p_rec"]


def _write_csv(tmp_path: Path, rows: list[dict]) -> Path:
    """Escreve CSV temporário com as linhas dadas."""
    csv_path = tmp_path / "profiles_resumo.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADERS)
        writer.writeheader()
        for r in rows:
            full = {h: r.get(h, "") for h in HEADERS}
            writer.writerow(full)
    return csv_path


# ============================================================
# carregar_csv
# ============================================================

class TestCarregarCsv:
    def test_csv_inexistente_levanta(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ap.carregar_csv(tmp_path / "nao_existe.csv")

    def test_pula_metadata(self, tmp_path):
        csv_p = _write_csv(tmp_path, [
            {"sigla": "_metadata"},
            {"sigla": "FOO", "val_exig": "100.00", "d_plus": "5"},
        ])
        rows = ap.carregar_csv(csv_p)
        assert len(rows) == 1
        assert rows[0]["sigla"] == "FOO"


# ============================================================
# classificar
# ============================================================

class TestClassificar:
    def test_d_plus_negativo_vai_para_prescritos(self):
        rows = [{"sigla": "X", "d_plus": "-5", "urg_presc": "PRESCRITA"}]
        b = ap.classificar(rows)
        assert len(b["prescritos"]) == 1
        assert len(b["criticos_iminentes"]) == 0

    def test_d_plus_zero_a_30_vai_para_criticos(self):
        rows = [
            {"sigla": "A", "d_plus": "0", "urg_presc": ""},
            {"sigla": "B", "d_plus": "15", "urg_presc": ""},
            {"sigla": "C", "d_plus": "30", "urg_presc": ""},
        ]
        b = ap.classificar(rows)
        assert len(b["criticos_iminentes"]) == 3
        assert len(b["prescritos"]) == 0

    def test_d_plus_31_nao_dispara(self):
        rows = [{"sigla": "X", "d_plus": "31", "urg_presc": ""}]
        b = ap.classificar(rows)
        assert len(b["criticos_iminentes"]) == 0
        assert len(b["sem_alerta"]) == 1

    def test_urg_presc_sem_d_plus_dispara_flag(self):
        rows = [{"sigla": "X", "d_plus": "", "urg_presc": "URGENTE"}]
        b = ap.classificar(rows)
        assert len(b["urgentes_flag"]) == 1

    def test_protegida_art202_nao_dispara(self):
        rows = [{"sigla": "DETRAN", "d_plus": "", "urg_presc": "PROTEGIDA_ART202_VI"}]
        b = ap.classificar(rows)
        assert len(b["prescritos"]) == 0
        assert len(b["criticos_iminentes"]) == 0
        assert len(b["urgentes_flag"]) == 0
        assert len(b["sem_alerta"]) == 1

    def test_precedencia_prescrita_sobre_urg_flag(self):
        # devedor com d_plus=-5 E urg_presc=URGENTE → cai só em prescritos
        rows = [{"sigla": "X", "d_plus": "-5", "urg_presc": "URGENTE"}]
        b = ap.classificar(rows)
        assert len(b["prescritos"]) == 1
        assert len(b["urgentes_flag"]) == 0

    def test_normal_nao_dispara(self):
        rows = [{"sigla": "X", "d_plus": "1271", "urg_presc": "NORMAL"}]
        b = ap.classificar(rows)
        assert len(b["sem_alerta"]) == 1


# ============================================================
# gerar_json
# ============================================================

class TestGerarJson:
    def test_estrutura_completa(self):
        rows = [
            {"sigla": "A", "categoria": "GOV_DIRETA", "forca": "FORTE",
             "val_exig": "100.00", "val_atualizado": "200.00",
             "d_plus": "-10", "urg_presc": "PRESCRITA", "proximo_passo": "X"},
            {"sigla": "B", "categoria": "GOV_INDIRETA", "forca": "FRACA",
             "val_exig": "50.00", "val_atualizado": "50.00",
             "d_plus": "5", "urg_presc": "CRITICA_IMINENTE", "proximo_passo": "Y"},
        ]
        b = ap.classificar(rows)
        j = ap.gerar_json(b)

        assert j["tem_alertas"] is True
        assert j["n_alertas"] == 2
        assert j["totais"]["prescritos_n"] == 1
        assert j["totais"]["criticos_iminentes_n"] == 1
        assert j["totais"]["prescritos_val_atualizado"] == "200.00"
        # multa 10% sobre 200 = 20
        assert j["totais"]["prescritos_multa_10pct"] == "20.00"
        assert j["prescritos"][0]["sigla"] == "A"
        assert j["prescritos"][0]["d_plus"] == -10

    def test_sem_alertas(self):
        rows = [{"sigla": "X", "d_plus": "1271", "urg_presc": "NORMAL"}]
        b = ap.classificar(rows)
        j = ap.gerar_json(b)
        assert j["tem_alertas"] is False
        assert j["n_alertas"] == 0

    def test_serializa_decimal_como_string(self):
        # Decimal não é JSON-safe; garantir que vira string preservando precisão
        rows = [{"sigla": "X", "d_plus": "-1",
                 "val_atualizado": "1234567.89", "val_exig": "1234567.89"}]
        b = ap.classificar(rows)
        j = ap.gerar_json(b)
        s = json.dumps(j)  # não deve levantar
        assert "1234567.89" in s

    def test_gerado_em_formato_RFC3339_Z(self):
        # Garante que migração de datetime.utcnow() → datetime.now(timezone.utc)
        # preservou o sufixo Z (RFC 3339), sem introduzir "+00:00".
        rows = [{"sigla": "X", "d_plus": "-1",
                 "val_exig": "100.00", "val_atualizado": "100.00"}]
        b = ap.classificar(rows)
        j = ap.gerar_json(b)
        assert j["gerado_em"].endswith("Z"), f"esperado terminar com Z: {j['gerado_em']}"
        assert "+00:00" not in j["gerado_em"], "não deve ter offset numérico"
        # Formato: YYYY-MM-DDTHH:MM:SSZ (20 chars)
        assert len(j["gerado_em"]) == 20


# ============================================================
# gerar_markdown
# ============================================================

class TestGerarMarkdown:
    def test_sem_alertas_mostra_ok(self):
        b = ap.classificar([{"sigla": "X", "d_plus": "1271", "urg_presc": "NORMAL"}])
        md = ap.gerar_markdown(b)
        assert "Sem alertas hoje" in md
        assert "✅" in md

    def test_com_prescritos_mostra_tabela(self):
        b = ap.classificar([
            {"sigla": "FOO", "categoria": "GOV_DIRETA", "forca": "FORTE",
             "val_exig": "100.00", "val_atualizado": "200.00",
             "d_plus": "-10", "urg_presc": "PRESCRITA"},
        ])
        md = ap.gerar_markdown(b)
        assert "PRESCRITOS" in md
        assert "FOO" in md
        assert "R$ 200,00" in md  # formato BRL
        assert "R$ 20,00" in md   # multa 10%

    def test_inclui_ads_critica_iminente(self):
        b = ap.classificar([
            {"sigla": "ADS", "categoria": "GOV_INDIRETA", "forca": "FRACA",
             "val_exig": "211657.47", "val_atualizado": "211657.47",
             "d_plus": "3", "urg_presc": "CRITICA_IMINENTE"},
        ])
        md = ap.gerar_markdown(b)
        assert "CRÍTICOS IMINENTES" in md
        assert "ADS" in md


# ============================================================
# CLI / exit codes
# ============================================================

class TestCli:
    def test_check_sem_alertas_exit_0(self, tmp_path):
        csv_p = _write_csv(tmp_path, [
            {"sigla": "X", "d_plus": "1271", "urg_presc": "NORMAL"},
        ])
        rc = ap.main(["--csv", str(csv_p), "--check"])
        assert rc == 0

    def test_check_com_alertas_exit_1(self, tmp_path):
        csv_p = _write_csv(tmp_path, [
            {"sigla": "X", "d_plus": "-10", "urg_presc": "PRESCRITA"},
        ])
        rc = ap.main(["--csv", str(csv_p), "--check"])
        assert rc == 1

    def test_csv_inexistente_exit_2(self):
        rc = ap.main(["--csv", "/tmp/nao_existe_99887766.csv", "--check"])
        assert rc == 2

    def test_md_default_emite_markdown(self, tmp_path, capsys):
        csv_p = _write_csv(tmp_path, [
            {"sigla": "X", "d_plus": "1271", "urg_presc": "NORMAL"},
        ])
        ap.main(["--csv", str(csv_p)])
        out = capsys.readouterr().out
        assert "# Alerta de Prescrição" in out

    def test_json_emite_json_valido(self, tmp_path, capsys):
        csv_p = _write_csv(tmp_path, [
            {"sigla": "X", "d_plus": "-5", "urg_presc": "PRESCRITA",
             "val_atualizado": "100.00", "val_exig": "100.00"},
        ])
        ap.main(["--csv", str(csv_p), "--json"])
        out = capsys.readouterr().out
        data = json.loads(out)  # não deve levantar
        assert data["n_alertas"] == 1


# ============================================================
# Smoke test contra CSV real
# ============================================================

class TestCsvReal:
    """Garantia de não-regressão contra o profiles_resumo.csv versionado."""

    @pytest.fixture
    def csv_path(self):
        p = Path(__file__).resolve().parent.parent / "profiles_resumo.csv"
        if not p.exists():
            pytest.skip("profiles_resumo.csv ausente no checkout")
        return p

    def test_carrega_69_devedores(self, csv_path):
        rows = ap.carregar_csv(csv_path)
        # ~69-72 esperados; sem hard-coding excessivo
        assert 60 <= len(rows) <= 100

    def test_ads_classificada_como_critica_iminente(self, csv_path):
        rows = ap.carregar_csv(csv_path)
        b = ap.classificar(rows)
        siglas_crit = {r["sigla"] for r in b["criticos_iminentes"]}
        assert "ADS" in siglas_crit, "ADS deveria estar em CRITICA_IMINENTE (d_plus=3)"

    def test_detran_protegida_nao_dispara(self, csv_path):
        rows = ap.carregar_csv(csv_path)
        b = ap.classificar(rows)
        todos_alerta = ({r["sigla"] for r in b["prescritos"]}
                        | {r["sigla"] for r in b["criticos_iminentes"]}
                        | {r["sigla"] for r in b["urgentes_flag"]})
        assert "DETRAN" not in todos_alerta, "DETRAN (PROTEGIDA_ART202_VI) não deve disparar"

    def test_consistencia_multa_com_doc_08(self, csv_path):
        """
        Cross-check: o agregado prescritos × 10% deve bater com o documento
        _QUESTOES_CRITICAS/08_EXPOSICAO_CONTRATUAL.md (R$ 10.463.698,62).
        """
        rows = ap.carregar_csv(csv_path)
        b = ap.classificar(rows)
        j = ap.gerar_json(b)
        assert j["totais"]["prescritos_multa_10pct"] == "10463698.62", \
            f"Multa inconsistente com doc 08: {j['totais']['prescritos_multa_10pct']}"
