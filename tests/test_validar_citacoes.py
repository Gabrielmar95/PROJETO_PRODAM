"""
Testes unitários para scripts/validar_citacoes.py.

Cobertura: detecção de violação, salvaguardas (vencido/p_acórdão/José Delgado),
exclusão de diretórios, exit codes, repo real (não-regressão).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import validar_citacoes as vc  # noqa: E402


def _arquivo(tmp_path: Path, nome: str, conteudo: str) -> Path:
    p = tmp_path / nome
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(conteudo, encoding="utf-8")
    return p


# ============================================================
# varrer_arquivo — detecção e salvaguardas
# ============================================================

class TestVarrerArquivo:
    def test_arquivo_limpo(self, tmp_path):
        p = _arquivo(tmp_path, "limpo.md", "Texto normal sem citação.")
        assert vc.varrer_arquivo(p) == []

    def test_teori_sem_resp_passa(self, tmp_path):
        p = _arquivo(tmp_path, "ok.md",
                     "Min. Teori Zavascki votou em outro caso (TJ-AM).")
        assert vc.varrer_arquivo(p) == []

    def test_resp_sem_teori_passa(self, tmp_path):
        p = _arquivo(tmp_path, "ok2.md",
                     "REsp 793.969/RJ foi julgado em 2006 pelo STJ.")
        assert vc.varrer_arquivo(p) == []

    def test_teori_proximo_resp_sem_ressalva_REJEITA(self, tmp_path):
        p = _arquivo(tmp_path, "ruim.md",
                     "REsp 793.969/RJ, Min. Teori Zavascki, firmou entendimento.")
        v = vc.varrer_arquivo(p)
        assert len(v) == 1

    def test_salvaguarda_vencido_passa(self, tmp_path):
        p = _arquivo(tmp_path, "ok3.md",
                     "No REsp 793.969/RJ, o voto de Teori Zavascki foi vencido.")
        assert vc.varrer_arquivo(p) == []

    def test_salvaguarda_jose_delgado_passa(self, tmp_path):
        p = _arquivo(tmp_path, "ok4.md",
                     "REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; "
                     "Teori Zavascki vencido).")
        assert vc.varrer_arquivo(p) == []

    def test_salvaguarda_p_acordao_passa(self, tmp_path):
        p = _arquivo(tmp_path, "ok5.md",
                     "REsp 793.969/RJ, Rel. p/ acórdão Min. José Delgado "
                     "(Teori Zavascki).")
        assert vc.varrer_arquivo(p) == []

    def test_typo_zavascski_tambem_detecta(self, tmp_path):
        p = _arquivo(tmp_path, "ruim2.md",
                     "REsp 793.969, Min. Teori Zavascski, julgou.")
        v = vc.varrer_arquivo(p)
        assert len(v) == 1

    def test_resp_sem_ponto_detecta(self, tmp_path):
        p = _arquivo(tmp_path, "ruim3.md",
                     "REsp 793969, relator Min. Teori Zavascki.")
        v = vc.varrer_arquivo(p)
        assert len(v) == 1

    def test_janela_5_linhas_detecta(self, tmp_path):
        # Teori na linha 1, REsp na linha 4 (dentro da janela)
        conteudo = "Min. Teori Zavascki\nlinha 2\nlinha 3\nREsp 793.969\nfim"
        p = _arquivo(tmp_path, "ruim4.md", conteudo)
        v = vc.varrer_arquivo(p)
        assert len(v) == 1

    def test_fora_da_janela_passa(self, tmp_path):
        # 8 linhas de separação — fora da janela de 5
        conteudo = "Min. Teori Zavascki votou em outro caso\n" + ("linha vazia\n" * 8) + "REsp 793.969/RJ é caso separado"
        p = _arquivo(tmp_path, "ok6.md", conteudo)
        assert vc.varrer_arquivo(p) == []

    def test_nome_completo_albino_detecta(self, tmp_path):
        # Variante "Teori Albino Zavascki" (nome completo)
        p = _arquivo(tmp_path, "ruim5.md",
                     "REsp 793.969/RJ, relator Min. Teori Albino Zavascki.")
        v = vc.varrer_arquivo(p)
        assert len(v) == 1

    def test_arquivo_inexistente_retorna_vazio(self, tmp_path):
        assert vc.varrer_arquivo(tmp_path / "nao_existe.md") == []


# ============================================================
# _eh_excluido — diretórios excluídos
# ============================================================

class TestExclusao:
    def test_backups_excluido(self, monkeypatch, tmp_path):
        monkeypatch.setattr(vc, "ROOT", tmp_path)
        f = _arquivo(tmp_path, "_BACKUPS/x.md", "Teori Zavascki REsp 793.969")
        assert vc._eh_excluido(f) is True

    def test_arquivo_sessao_prefix_excluido(self, monkeypatch, tmp_path):
        monkeypatch.setattr(vc, "ROOT", tmp_path)
        f = _arquivo(tmp_path, "_ARQUIVO_SESSAO_20260423/x.md", "x")
        assert vc._eh_excluido(f) is True

    def test_teste_agent_excluido(self, monkeypatch, tmp_path):
        monkeypatch.setattr(vc, "ROOT", tmp_path)
        f = _arquivo(tmp_path, "DOCUMENTOS_GERADOS/_TESTE_AGENT/peca.md", "x")
        assert vc._eh_excluido(f) is True

    def test_arquivo_normal_nao_excluido(self, monkeypatch, tmp_path):
        monkeypatch.setattr(vc, "ROOT", tmp_path)
        f = _arquivo(tmp_path, "scripts/x.py", "y = 1")
        assert vc._eh_excluido(f) is False


# ============================================================
# CLI / main()
# ============================================================

class TestCli:
    def test_main_repo_limpo_retorna_0(self, tmp_path, capsys):
        _arquivo(tmp_path, "x.md", "Texto sem citação.")
        rc = vc.main([str(tmp_path)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "OK" in out

    def test_main_repo_com_violacao_retorna_1(self, tmp_path, capsys):
        _arquivo(tmp_path, "ruim.md",
                 "REsp 793.969/RJ, Min. Teori Zavascki, julgou.")
        rc = vc.main([str(tmp_path)])
        assert rc == 1
        out = capsys.readouterr().out
        assert "::error" in out
        assert "FALHA" in out

    def test_main_arquivo_especifico(self, tmp_path):
        f = _arquivo(tmp_path, "x.md",
                     "REsp 793.969/RJ, Teori Zavascki, julgou.")
        rc = vc.main([str(f)])
        assert rc == 1


# ============================================================
# Smoke test contra o repo real (garante não-regressão)
# ============================================================

class TestRepoReal:
    """O projeto inteiro precisa estar limpo (cascata aplicada em 12/05/2026)."""

    def test_projeto_inteiro_passa(self, capsys):
        rc = vc.main([])
        out = capsys.readouterr().out
        assert rc == 0, (
            f"Repo tem citação errônea de Teori no REsp 793.969 — "
            f"corrigir antes de mergear.\nOutput:\n{out}"
        )
