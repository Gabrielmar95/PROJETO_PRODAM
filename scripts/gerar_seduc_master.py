"""gerar_seduc_master.py — Consolidador SEDUC → SEDUC_MASTER_v1.json

Porta do padrão DETRAN v10 (gerar_v10_master.py) com:
  - paths relativos ao repo (sem hardcode Windows);
  - CLI argparse (--orgao SEDUC --out DIR);
  - Decimal em TODA agregação monetária (NUNCA-2) — serializado como string decimal.

Fontes (somente leitura):
  1. _ARQUIVO/Melhorar ainda mais esse dashboard/profiles.json → chave SEDUC (SSOT histórico)
  2. DOSSIES_MULTIFORMATO/SEDUC/dossie.json → universo recente SPCF (106 faturas, 286 empenhos)

Os DOIS universos são declarados separadamente no master — nunca somados nem misturados.

Uso:
  py -3.12 scripts\gerar_seduc_master.py --orgao SEDUC --out DOCUMENTOS_GERADOS/SEDUC
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prodam_utils import brl, fmt_brl, parse_comp  # noqa: E402

PROFILES_PADRAO = ROOT / "_ARQUIVO" / "Melhorar ainda mais esse dashboard" / "profiles.json"
DOSSIE_PADRAO = ROOT / "DOSSIES_MULTIFORMATO" / "SEDUC" / "dossie.json"


def dec_str(v) -> str:
    """Decimal → string decimal canônica para serialização JSON (SSOT sem float)."""
    d = v if isinstance(v, Decimal) else brl(v)
    return f"{d:.2f}"


def carregar_json(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def comp_key(comp: str):
    """'05/2023' → date(2023,5,1) para ordenação cronológica."""
    d = parse_comp(comp)
    return d or date(1900, 1, 1)


def construir_master(orgao: str, profiles_path: Path, dossie_path: Path) -> dict:
    profiles = carregar_json(profiles_path)
    if orgao not in profiles:
        raise SystemExit(f"ERRO: órgão {orgao!r} não encontrado em {profiles_path}")
    profile = profiles[orgao]
    dossie = carregar_json(dossie_path)
    stats = dossie.get("stats", {})

    # ===== Universo recente SPCF (dossie.json) — agregação 100% Decimal =====
    faturas_raw = dossie.get("faturas", [])
    faturas_out = []
    total_spcf = Decimal(0)
    por_contrato: dict[str, dict] = defaultdict(lambda: {"qtd": 0, "valor": Decimal(0)})
    por_competencia: dict[str, dict] = defaultdict(lambda: {"qtd": 0, "valor": Decimal(0)})
    por_situacao: dict[str, int] = defaultdict(int)
    por_cadeia: dict[str, int] = defaultdict(int)
    for f in faturas_raw:
        valor = brl(f.get("valor_bruto"))
        total_spcf += valor
        ct = f.get("contrato") or "(sem contrato)"
        comp = f.get("competencia") or "—"
        sit = f.get("situacao") or "—"
        por_contrato[ct]["qtd"] += 1
        por_contrato[ct]["valor"] += valor
        por_competencia[comp]["qtd"] += 1
        por_competencia[comp]["valor"] += valor
        por_situacao[sit] += 1
        por_cadeia[f.get("cadeia") or "—"] += 1
        faturas_out.append({
            "id": f.get("id"),
            "nf": f.get("nf"),
            "contrato": ct,
            "competencia": comp,
            "valor_bruto": dec_str(valor),
            "situacao": sit,
            "cadeia": f.get("cadeia"),
            "empenhos_vinc": f.get("empenhos_vinc"),
        })

    # Sanidade contra stats do dossiê (sem alterar nada — só alerta)
    stats_fat = brl(stats.get("faturas", {}).get("valor_total"))
    if stats_fat and stats_fat != total_spcf:
        print(f"  ! AVISO: soma Decimal {fmt_brl(total_spcf)} difere de stats.faturas "
              f"{fmt_brl(stats_fat)}")

    contratos_out = [
        {
            "numero": ct,
            "num_faturas": agg["qtd"],
            "valor_bruto": dec_str(agg["valor"]),
            "valor_bruto_fmt": fmt_brl(agg["valor"]),
            "pdf_contrato": False,  # 0 contratos PDF no acervo — cláusula econômica pendente
            "clausula_economica": "PENDENTE",
        }
        for ct, agg in sorted(por_contrato.items(), key=lambda kv: -kv[1]["valor"])
    ]

    competencias_out = [
        {"competencia": comp, "qtd": agg["qtd"], "valor": dec_str(agg["valor"])}
        for comp, agg in sorted(por_competencia.items(), key=lambda kv: comp_key(kv[0]))
    ]

    # ===== Empenhos por ano (stats.empenhos.por_ano) =====
    emp_stats = stats.get("empenhos", {})
    empenhos_por_ano = {
        ano: {"qtd": v.get("qtd", 0), "valor": dec_str(brl(v.get("valor")))}
        for ano, v in sorted(emp_stats.get("por_ano", {}).items())
    }
    empenhos_total = brl(emp_stats.get("valor_total"))

    cobr_stats = stats.get("cobrancas", {})

    # ===== Universos declarados (NUNCA somar/misturar) =====
    val_exig = brl(profile.get("val_exig"))
    val_atualizado = brl(profile.get("val_atualizado"))
    universos = {
        "nota": ("Dois universos coexistem e NÃO devem ser somados nem misturados num "
                 "mesmo gráfico: (a) universo recente SPCF do dossiê (competências ≥ 05/2023) "
                 "e (b) universo SSOT histórico do profiles.json (base da cobrança)."),
        "spcf_recente": {
            "fonte": "DOSSIES_MULTIFORMATO/SEDUC/dossie.json",
            "faturas": len(faturas_out),
            "valor_bruto": dec_str(total_spcf),
            "valor_bruto_fmt": fmt_brl(total_spcf),
            "descricao": (f"Universo recente SPCF: {len(faturas_out)} faturas · "
                          f"{fmt_brl(total_spcf)} (todas com competência ≥ 05/2023)"),
            "situacoes": dict(por_situacao),
            "cadeia": dict(por_cadeia),
        },
        "ssot_historico": {
            "fonte": "profiles.json → SEDUC (SSOT)",
            "faturas": profile.get("faturas_total", 84),
            "faturas_exigiveis": profile.get("faturas_exigiveis", 76),
            "faturas_prescritas": profile.get("faturas_prescritas", 8),
            "valor_exigivel": dec_str(val_exig),
            "valor_exigivel_fmt": fmt_brl(val_exig),
            "valor_atualizado": dec_str(val_atualizado),
            "valor_atualizado_fmt": fmt_brl(val_atualizado),
            "descricao": (f"Universo SSOT histórico: {profile.get('faturas_total', 84)} faturas · "
                          f"{fmt_brl(val_exig)} exigível / {fmt_brl(val_atualizado)} atualizado"),
        },
    }

    # ===== Hero =====
    blindagem = profile.get("blindagem_resultado", {}) or {}
    score = brl(profile.get("score_composto"))  # 0.8005
    hero = {
        "valor_exigivel": dec_str(val_exig),
        "valor_exigivel_fmt": fmt_brl(val_exig),
        "valor_atualizado": dec_str(val_atualizado),
        "valor_atualizado_fmt": fmt_brl(val_atualizado),
        "score_100": dec_str(score * 100),       # "80.05"
        "score_label": "80/100",
        "conceito": "B+",
        "ev_valor_esperado": dec_str(brl(profile.get("ev_valor_esperado"))),
        "ev_honorarios": dec_str(brl(profile.get("ev_honorarios"))),
        "monte_carlo_p50": dec_str(brl(profile.get("cenario_monte_carlo_p50"))),
        "p_recuperacao": str(profile.get("p_recuperacao", 0.7)),
        "recomendacao": blindagem.get("recomendacao", "MONITORIA"),
        "blindagem_ok": blindagem.get("total_ok", 20),
        "blindagem_total": blindagem.get("total_items", 22),
        "blindagem_blocos": blindagem.get("blocos", {}),
        "blindagem_ressalvas": blindagem.get("ressalvas", []),
        "forca_probatoria": profile.get("forca_probatoria", "FORTE"),
        "proximo_passo": profile.get("proximo_passo", "ANALISAR_DOCUMENTACAO"),
        "prioridade_rank": profile.get("prioridade_rank", 2),
        "status": profile.get("status", ""),
        "fase_atual": profile.get("fase_atual", "F0"),
    }

    # ===== Riscos & blindagem (catálogo verificado — Regra 13) =====
    riscos = [
        {"severidade": "critica", "titulo": "Recomendação: MONITORIA",
         "descricao": (f"Blindagem {hero['blindagem_ok']}/{hero['blindagem_total']} — sem título "
                       "executivo formado. Ação monitória (ou TRD prévio) antes de execução.")},
        {"severidade": "critica", "titulo": "Negativa expressa — Of. 316/2020-GS/SEDUC",
         "descricao": ("Devedor registrou negativa expressa de cobrança. Exige prova documental "
                       "robusta; silêncio/gestão não suprem (Tema 1.109/STJ: gestor público não "
                       "renuncia tacitamente à prescrição).")},
        {"severidade": "alta", "titulo": "Decreto Estadual AM nº 53.464/2026",
         "descricao": ("Verificar as 4 exceções (art. 1º §§1º-4º) antes de qualquer ação contra "
                       "o Governo do AM — SEDUC é Administração Direta (precatório/RPV, "
                       "Art. 100 CF).")},
        {"severidade": "alta", "titulo": "Cadeia REsp 793.969/RJ incompleta",
         "descricao": ("Título executivo exige Contrato + NE + NF + Atesto. Hoje: 0 contratos em "
                       "PDF no acervo → cláusula econômica pendente e composição documental "
                       "incompleta.")},
        {"severidade": "media", "titulo": "Prescrição por fatura individual",
         "descricao": ("Art. 189 + 206 §5º I CC, contada do vencimento. NE = reconhecimento "
                       "tácito (Art. 202 VI CC) interrompe; NF emitida pelo credor não. "
                       "Empenhos 2025/2026 são potenciais marcos a documentar.")},
        {"severidade": "media", "titulo": "Reconciliação CRITICAL entre fontes",
         "descricao": ("profiles.json registra divergência de 44,79% entre fontes SPCF/SSOT "
                       "(reconciliacao_status=CRITICAL) — manter os dois universos separados "
                       "até auditoria documental concluir.")},
    ]

    proximos_passos = [
        {"ordem": 1, "acao": "Auditar acervo DPCON (share SPCON/CLIENTES/SEDUC)",
         "detalhe": "Mesma pipeline validada no DETRAN: OCR cascata + classificação + naming formal.",
         "impacto": "Contratos-base + cláusula econômica"},
        {"ordem": 2, "acao": "Auditar pendrive / acervo físico digitalizado",
         "detalhe": "Buscar os 6 contratos (14/2018, 20/2022, 23/2021, 2/2021, 54/2017, 21/2026) e atestos.",
         "impacto": "Cadeia REsp 793.969 completa"},
        {"ordem": 3, "acao": "Reimportar snapshot SPCF e reconciliar universos",
         "detalhe": "Fechar a divergência 84×106 faturas (SSOT × SPCF recente) fatura a fatura.",
         "impacto": "Valor canônico único"},
        {"ordem": 4, "acao": "Mapear marcos interruptivos nos empenhos 2025/2026",
         "detalhe": "38 NEs em 2025-2026 — candidatos a reconhecimento tácito (Art. 202 VI CC).",
         "impacto": "Proteção prescricional"},
        {"ordem": 5, "acao": "Preparar memorial de cálculo preliminar e minuta de monitória/TRD",
         "detalhe": "Após cláusula econômica confirmada (índice por contrato; SELIC default Lei 14.905/2024).",
         "impacto": "F0 → F2"},
    ]

    master = {
        "metadata": {
            "gerado_em": date.today().isoformat(),
            "versao": "v1",
            "edicao": "Editorial Noir · SEDUC",
            "devedor": profile.get("nome_completo", "Secretaria de Educação do Amazonas"),
            "sigla": orgao,
            "cnpj": profile.get("cnpj", "04.312.419/0001-30"),
            "categoria": profile.get("categoria", "GOV_DIRETA"),
            "natureza": profile.get("natureza", "Secretaria de Estado"),
            "regime_execucao": profile.get("regime_execucao", "precatorio_rpv"),
            "fontes": [str(profiles_path.relative_to(ROOT)), str(dossie_path.relative_to(ROOT))],
            "nota_monetaria": "Valores serializados como string decimal (agregação em Decimal — NUNCA-2).",
        },
        "hero": hero,
        "universos": universos,
        "contratos": contratos_out,
        "contratos_aviso": "0 contratos PDF — cláusula econômica pendente",
        "faturas": faturas_out,
        "faturas_por_competencia": competencias_out,
        "faturas_por_contrato": [
            {"contrato": c["numero"], "qtd": c["num_faturas"], "valor": c["valor_bruto"]}
            for c in contratos_out
        ],
        "empenhos_por_ano": empenhos_por_ano,
        "empenhos_total": {"qtd": emp_stats.get("qtd", 0), "valor": dec_str(empenhos_total),
                           "valor_fmt": fmt_brl(empenhos_total)},
        "cobrancas_total": {"qtd": cobr_stats.get("qtd", 0),
                            "valor": dec_str(brl(cobr_stats.get("valor_total")))},
        "riscos": riscos,
        "proximos_passos": proximos_passos,
    }
    return master


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gera SEDUC_MASTER_v1.json (consolidador Editorial Noir)")
    ap.add_argument("--orgao", default="SEDUC", help="Sigla do órgão (suportado: SEDUC)")
    ap.add_argument("--out", default=str(ROOT / "DOCUMENTOS_GERADOS" / "SEDUC"),
                    help="Diretório de saída")
    ap.add_argument("--profiles", default=str(PROFILES_PADRAO), help="Caminho do profiles.json")
    ap.add_argument("--dossie", default=str(DOSSIE_PADRAO), help="Caminho do dossie.json")
    args = ap.parse_args(argv)

    if args.orgao.upper() != "SEDUC":
        raise SystemExit("ERRO: este consolidador v1 suporta apenas --orgao SEDUC")

    master = construir_master(args.orgao.upper(), Path(args.profiles), Path(args.dossie))

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.orgao.upper()}_MASTER_v1.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(master, fh, ensure_ascii=False, indent=None, separators=(",", ":"))

    print(f"OK {out_path}  ({out_path.stat().st_size:,} bytes)")
    print(f"  faturas SPCF recente : {len(master['faturas'])} · "
          f"{master['universos']['spcf_recente']['valor_bruto_fmt']}")
    print(f"  SSOT historico       : {master['universos']['ssot_historico']['faturas']} faturas · "
          f"{master['universos']['ssot_historico']['valor_exigivel_fmt']} exigivel")
    print(f"  contratos            : {len(master['contratos'])} ({master['contratos_aviso']})")
    print(f"  empenhos por ano     : {len(master['empenhos_por_ano'])} anos · "
          f"{master['empenhos_total']['valor_fmt']}")
    return out_path


if __name__ == "__main__":
    main()
