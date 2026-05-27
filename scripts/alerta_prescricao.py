"""
alerta_prescricao.py — Alerta diário de prescrição (job de cron CI).

Lê `profiles_resumo.csv` e identifica devedores em risco prescricional, gerando:
  - Saída humana (Markdown) para corpo de issue / e-mail
  - Saída estruturada (JSON) para automação downstream
  - Exit code != 0 quando há alertas (útil para gating em CI)

CRITÉRIOS DE ALERTA (qualquer um dispara):
  1. `d_plus < 0`  → PRESCRITA (perda corrente — incide multa contratual 10%)
  2. `0 <= d_plus <= 30`  → CRITICA_IMINENTE (próximas 4 semanas)
  3. `urg_presc` ∈ {CRITICA_IMINENTE, URGENTE, PRESCRITA} → flag explícita no CSV
     (PROTEGIDA_ART202_VI NÃO dispara — está blindada por marco interruptivo)

USO:
  python scripts/alerta_prescricao.py                  # markdown no stdout
  python scripts/alerta_prescricao.py --json           # JSON estruturado
  python scripts/alerta_prescricao.py --check          # silencioso; exit 0/1
  python scripts/alerta_prescricao.py --csv path/x.csv # CSV custom

EXIT CODES:
  0 = sem alertas
  1 = há alertas (devedores em risco)
  2 = erro (CSV não encontrado, formato inválido)

ORIGEM: roadmap Janela 3, item 3.1 (ADS escapou por 14 dias sem ninguém olhar o CSV).
"""
from __future__ import annotations
import csv
import json
import sys
import argparse
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

# Set de urg_presc que dispara alerta (PROTEGIDA_ART202_VI excluída — está blindada)
URG_ALERTA = {"CRITICA_IMINENTE", "URGENTE", "PRESCRITA"}

# Janela d_plus considerada "iminente" (em dias)
JANELA_IMINENTE = 30


def _to_dec(s: Any) -> Decimal:
    if s is None or str(s).strip() == "":
        return Decimal(0)
    try:
        return Decimal(str(s))
    except Exception:
        return Decimal(0)


def _fmt_brl(v: Any) -> str:
    n = _to_dec(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"R$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _d_plus_int(r: dict) -> int | None:
    v = r.get("d_plus", "")
    if v is None or str(v).strip() == "":
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def carregar_csv(csv_path: Path) -> list[dict]:
    """Carrega CSV e retorna lista de devedores (pula linhas _metadata)."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV não encontrado: {csv_path}")
    with open(csv_path, encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if not r["sigla"].startswith("_")]


def classificar(rows: list[dict]) -> dict:
    """
    Classifica devedores em buckets de risco. Cada devedor cai em EXATAMENTE um
    bucket (precedência: PRESCRITA > CRITICA_IMINENTE > URGENTE_FLAG > sem alerta).
    """
    prescritos: list[dict] = []
    criticos: list[dict] = []
    urgentes_flag: list[dict] = []
    sem_alerta: list[dict] = []

    for r in rows:
        dp = _d_plus_int(r)
        urg = (r.get("urg_presc") or "").strip()

        if dp is not None and dp < 0:
            prescritos.append(r)
        elif dp is not None and 0 <= dp <= JANELA_IMINENTE:
            criticos.append(r)
        elif urg in URG_ALERTA:
            urgentes_flag.append(r)
        else:
            sem_alerta.append(r)

    return {
        "prescritos": prescritos,
        "criticos_iminentes": criticos,
        "urgentes_flag": urgentes_flag,
        "sem_alerta": sem_alerta,
    }


def gerar_json(buckets: dict) -> dict:
    """Serializa buckets + agregados em estrutura JSON-safe."""
    def _serialize(rows: list[dict]) -> list[dict]:
        out = []
        for r in rows:
            out.append({
                "sigla": r["sigla"],
                "categoria": r.get("categoria", ""),
                "forca": r.get("forca", ""),
                "val_exig": str(_to_dec(r.get("val_exig"))),
                "val_atualizado": str(_to_dec(r.get("val_atualizado"))),
                "proximo_passo": r.get("proximo_passo", ""),
                "urg_presc": r.get("urg_presc", ""),
                "d_plus": _d_plus_int(r),
            })
        return out

    soma_atu_prescritos = sum(_to_dec(r["val_atualizado"]) for r in buckets["prescritos"])
    soma_atu_criticos = sum(_to_dec(r["val_atualizado"]) for r in buckets["criticos_iminentes"])

    n_alertas = (len(buckets["prescritos"])
                 + len(buckets["criticos_iminentes"])
                 + len(buckets["urgentes_flag"]))

    return {
        "gerado_em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data_base": date.today().isoformat(),
        "tem_alertas": n_alertas > 0,
        "n_alertas": n_alertas,
        "totais": {
            "prescritos_n": len(buckets["prescritos"]),
            "prescritos_val_atualizado": str(soma_atu_prescritos),
            "prescritos_multa_10pct": str((soma_atu_prescritos * Decimal("0.10"))
                                           .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "criticos_iminentes_n": len(buckets["criticos_iminentes"]),
            "criticos_iminentes_val_atualizado": str(soma_atu_criticos),
            "urgentes_flag_n": len(buckets["urgentes_flag"]),
        },
        "prescritos": _serialize(buckets["prescritos"]),
        "criticos_iminentes": _serialize(buckets["criticos_iminentes"]),
        "urgentes_flag": _serialize(buckets["urgentes_flag"]),
    }


def gerar_markdown(buckets: dict) -> str:
    """Gera corpo Markdown human-readable (para issue do GitHub / e-mail)."""
    soma_atu_prescritos = sum(_to_dec(r["val_atualizado"]) for r in buckets["prescritos"])
    soma_atu_criticos = sum(_to_dec(r["val_atualizado"]) for r in buckets["criticos_iminentes"])
    multa_prescritos = (soma_atu_prescritos * Decimal("0.10")).quantize(Decimal("0.01"),
                                                                          rounding=ROUND_HALF_UP)
    n_alertas = (len(buckets["prescritos"])
                 + len(buckets["criticos_iminentes"])
                 + len(buckets["urgentes_flag"]))

    L = []
    L.append(f"# Alerta de Prescrição — {date.today().isoformat()}")
    L.append("")
    L.append(f"> Gerado por `.github/workflows/alerta_prescricao.yml` em "
             f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    L.append("")

    if n_alertas == 0:
        L.append("## ✅ Sem alertas hoje")
        L.append("")
        L.append("Nenhum devedor com `d_plus <= 30` ou `urg_presc ∈ "
                 "{CRITICA_IMINENTE, URGENTE, PRESCRITA}`.")
        return "\n".join(L)

    L.append(f"## ⚠️ {n_alertas} devedor(es) em risco prescricional")
    L.append("")
    L.append(f"- **{len(buckets['prescritos'])} já prescritos** (`d_plus < 0`) — "
             f"{_fmt_brl(soma_atu_prescritos)} atualizado · "
             f"multa contratual 10% incidente: **{_fmt_brl(multa_prescritos)}**")
    L.append(f"- **{len(buckets['criticos_iminentes'])} críticos em ≤ 30 dias** "
             f"(`0 <= d_plus <= 30`) — {_fmt_brl(soma_atu_criticos)} atualizado")
    L.append(f"- **{len(buckets['urgentes_flag'])} urgentes por flag** "
             f"(`urg_presc` ∈ {sorted(URG_ALERTA)} sem `d_plus` numérico)")
    L.append("")

    if buckets["prescritos"]:
        L.append("### 🔴 PRESCRITOS (perda corrente)")
        L.append("")
        L.append("| Sigla | Categoria | Força | d_plus | val_exig | val_atualizado | Próximo passo |")
        L.append("|---|---|---|---:|---:|---:|---|")
        for r in sorted(buckets["prescritos"], key=lambda r: _d_plus_int(r) or 0):
            L.append(f"| {r['sigla']} | {r.get('categoria', '')} | {r.get('forca', '')} | "
                     f"{_d_plus_int(r)} | {_fmt_brl(r.get('val_exig'))} | "
                     f"{_fmt_brl(r.get('val_atualizado'))} | {r.get('proximo_passo', '')} |")
        L.append("")

    if buckets["criticos_iminentes"]:
        L.append("### 🟠 CRÍTICOS IMINENTES (≤ 30 dias)")
        L.append("")
        L.append("| Sigla | Categoria | Força | d_plus | val_exig | val_atualizado | Próximo passo |")
        L.append("|---|---|---|---:|---:|---:|---|")
        for r in sorted(buckets["criticos_iminentes"], key=lambda r: _d_plus_int(r) or 0):
            L.append(f"| {r['sigla']} | {r.get('categoria', '')} | {r.get('forca', '')} | "
                     f"{_d_plus_int(r)} | {_fmt_brl(r.get('val_exig'))} | "
                     f"{_fmt_brl(r.get('val_atualizado'))} | {r.get('proximo_passo', '')} |")
        L.append("")

    if buckets["urgentes_flag"]:
        L.append("### 🟡 URGENTES por flag (sem d_plus numérico)")
        L.append("")
        L.append("| Sigla | Categoria | Força | urg_presc | val_exig | val_atualizado |")
        L.append("|---|---|---|---|---:|---:|")
        for r in sorted(buckets["urgentes_flag"], key=lambda r: r["sigla"]):
            L.append(f"| {r['sigla']} | {r.get('categoria', '')} | {r.get('forca', '')} | "
                     f"{r.get('urg_presc', '')} | {_fmt_brl(r.get('val_exig'))} | "
                     f"{_fmt_brl(r.get('val_atualizado'))} |")
        L.append("")

    L.append("---")
    L.append("")
    L.append("**Ações recomendadas:**")
    L.append("")
    L.append("- Para PRESCRITOS: consultar `_QUESTOES_CRITICAS/09_TRIAGEM_PRESCRITOS_20D.md` "
             "(plano em 5 grupos) e `_QUESTOES_CRITICAS/08_EXPOSICAO_CONTRATUAL.md` "
             "(memorando exposição).")
    L.append("- Para CRÍTICOS: notificação extrajudicial via AR ANTES da prescrição efetiva.")
    L.append("- Cada peça gerada deve passar pelo gate `adversarial-meta-auditor` "
             "antes do envio.")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", type=Path,
                        default=Path(__file__).resolve().parent.parent / "profiles_resumo.csv",
                        help="caminho do profiles_resumo.csv (default: raiz do projeto)")
    fmt = parser.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_true", help="saída JSON estruturada")
    fmt.add_argument("--md", action="store_true", help="saída Markdown (default)")
    fmt.add_argument("--check", action="store_true",
                     help="silencioso; só exit code (0=sem alerta, 1=com alerta)")
    args = parser.parse_args(argv)

    try:
        rows = carregar_csv(args.csv)
    except FileNotFoundError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2

    buckets = classificar(rows)
    n_alertas = (len(buckets["prescritos"])
                 + len(buckets["criticos_iminentes"])
                 + len(buckets["urgentes_flag"]))

    if args.check:
        return 1 if n_alertas > 0 else 0

    if args.json:
        print(json.dumps(gerar_json(buckets), ensure_ascii=False, indent=2))
    else:
        print(gerar_markdown(buckets))

    return 1 if n_alertas > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
