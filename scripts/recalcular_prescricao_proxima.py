#!/usr/bin/env python3
"""
recalcular_prescricao_proxima.py — Recalcula `data_prescricao_proxima` dos devedores
com data VENCIDA/stale ou AUSENTE em PRODAM_DOCS/profiles.json, a partir do universo
de faturas EM ABERTO do SPCF (SPCF_EXTRACAO/downloads/rel_faturas_aberto.csv).

Metodologia (a mesma registrada na revisão humana do SES/SUSAM —
`data_prescricao_proxima_metodologia`):
    prescricao(fatura) = último dia de (competência + 1 mês) + 5 anos
    (Art. 189 + 206 §5º I CC; vencimento presumido = fim do mês seguinte à competência)

LIMITAÇÕES DECLARADAS (constam do relatório e do campo de metodologia gravado):
    - NÃO considera marcos interruptivos não registrados (Art. 202 CC): as datas são
      o cenário CONSERVADOR (sem marco). Marco registrado prevalece — por isso
      devedores PROTEGIDA_ART202_VI são intocados.
    - Universo = snapshot de rel_faturas_aberto.csv (data no relatório).

POLÍTICA DE ESCRITA (--apply):
    INTOCADOS  : (a) revisão humana recente com data futura (ex.: SSP, SEJUSC,
                 FENIXSOFT — `ultima_revisao_prescricao`), (b) SES/SUSAM
                 (metodologia própria registrada), (c) urgencia PROTEGIDA_ART202_VI
                 (DETRAN — recebe apenas anotação, nunca data), (d) datas futuras
                 existentes (lotes 2027/2029 ficam para auditoria própria).
    ATUALIZA   : data no passado/'N/A'/ausente E fonte no rel_aberto →
                 nova data = menor prescrição FUTURA entre faturas em aberto;
                 se todas estouradas, menor estourada (fica visível no 🔥 do
                 CLAUDE.md). Antiga preservada em *_anterior_recalc20260609.
    SEM_FONTE  : intocado, listado no relatório.

GATE DE SANIDADE (documentado; motivo de revisados serem intocados): o método
reproduz SES/SUSAM (2026-09-30 ✓) mas DIVERGE de SSP (rel_aberto→2028-01-31 vs
revisão 2026-06-30) e SEJUSC (2026-11-30 vs 2026-08-31) — universos distintos
(rel_aberto financeiro 2026-04-12 × CSV cruzado jurídico da revisão 2026-05-12).
Divergência reportada para decisão humana; este script NÃO arbitra entre fontes.

Uso:
    py -3.12 scripts\\recalcular_prescricao_proxima.py            # dry-run + relatórios
    py -3.12 scripts\\recalcular_prescricao_proxima.py --apply    # grava com backup
"""
from __future__ import annotations

import argparse
import calendar
import csv
import json
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
if BASE.name == "scripts":
    BASE = BASE.parent
PROFILES = BASE / "PRODAM_DOCS" / "profiles.json"
REL_ABERTO = BASE / "SPCF_EXTRACAO" / "downloads" / "rel_faturas_aberto.csv"
REL_DIR = BASE / "relatorios"

HOJE = date.today()
TAG = "recalc20260609"
METODOLOGIA = (
    "Recalculado {dt} via scripts/recalcular_prescricao_proxima.py: menor prescrição "
    "entre faturas EM ABERTO (rel_faturas_aberto.csv@{snap}); prescrição por fatura = "
    "fim do mês (competência+1) + 5 anos (Art. 189 + 206 §5º I CC). Cenário conservador: "
    "NÃO considera marcos interruptivos não registrados (Art. 202 CC)."
)

# Aliases Cliente(rel_aberto) -> sigla(profiles) que o match normalizado não resolve.
ALIASES = {
    "FMT-HVD": "FMT",
    "POLICIA CIVIL": "POLÍCIA CIVIL",
    "SES": "SES/SUSAM",
    "FAAR - EXTINTA LEI 6.225 INCP PELA SEDEL": "FAAR/SEDEL",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def presc_date(comp: str) -> date | None:
    """MM/YYYY -> último dia de (mês+1) + 5 anos. None se não parseável."""
    m = re.match(r"^(\d{2})/(\d{4})$", (comp or "").strip())
    if not m:
        return None
    mes, ano = int(m.group(1)), int(m.group(2))
    mes2, ano2 = (mes + 1, ano) if mes < 12 else (1, ano + 1)
    ano5 = ano2 + 5
    return date(ano5, mes2, calendar.monthrange(ano5, mes2)[1])


def carregar_rel_aberto():
    """-> dict cliente_normalizado -> {"cliente": nome_csv, "prescs": [date, ...]}"""
    if not REL_ABERTO.exists():
        print(f"ERRO: {REL_ABERTO} não encontrado.")
        sys.exit(2)
    snap = datetime.fromtimestamp(REL_ABERTO.stat().st_mtime).date().isoformat()
    agg: dict[str, dict] = {}
    with open(REL_ABERTO, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            cli = (r.get("Cliente") or "").strip()
            if not cli:
                continue
            d = presc_date(r.get("Competência", ""))
            if d is None:
                continue
            k = norm(ALIASES.get(cli, cli))
            agg.setdefault(k, {"cliente": cli, "prescs": []})["prescs"].append(d)
    for v in agg.values():
        v["prescs"].sort()
    return agg, snap


def achar_fonte(sigla: str, rel: dict):
    """Match sigla do profiles -> entrada do rel_aberto (exato normalizado;
    senão prefixo inequívoco). None se sem fonte ou ambíguo."""
    alvo = norm(ALIASES.get(sigla, sigla))
    if alvo in rel:
        return rel[alvo]
    # sigla composta tipo FAAR/SEDEL: tenta cada parte
    partes = [norm(p) for p in re.split(r"[/+]", sigla) if p.strip()]
    hits = [rel[p] for p in partes if p in rel]
    if len(hits) == 1:
        return hits[0]
    # prefixo inequívoco (>=4 chars p/ evitar colisão)
    cands = [v for k, v in rel.items() if len(alvo) >= 4 and k.startswith(alvo)]
    return cands[0] if len(cands) == 1 else None


def classifica(sigla: str, d: dict, rel: dict):
    """-> dict linha do relatório com decisão por devedor."""
    dp_raw = d.get("data_prescricao_proxima")
    urg = d.get("urgencia_prescricao") or ""
    revisao = d.get("ultima_revisao_prescricao")
    dp = None
    if dp_raw and dp_raw != "N/A":
        try:
            dp = datetime.strptime(dp_raw, "%Y-%m-%d").date()
        except ValueError:
            dp = None

    fonte = achar_fonte(sigla, rel)
    prescs = fonte["prescs"] if fonte else []
    fut = [x for x in prescs if x > HOJE]
    venc = [x for x in prescs if x <= HOJE]
    nova = (fut[0] if fut else (venc[0] if venc else None))

    linha = {
        "sigla": sigla,
        "data_atual": dp_raw or "—",
        "urgencia": urg or "—",
        "fonte_cliente": fonte["cliente"] if fonte else "—",
        "n_abertas": len(prescs),
        "n_estouradas": len(venc),
        "primeira_estourada": venc[0].isoformat() if venc else "—",
        "proxima_futura": fut[0].isoformat() if fut else "—",
        "data_nova": nova.isoformat() if nova else "—",
    }

    if urg == "PROTEGIDA_ART202_VI":
        linha["decisao"] = "INTOCADO_PROTEGIDO (marcos Art. 202 VI prevalecem; anotação)"
        linha["acao"] = "anota"
    elif revisao or sigla == "SES/SUSAM":
        linha["decisao"] = "INTOCADO_REVISADO (revisão humana prevalece)"
        linha["acao"] = "nada"
        if fonte and fut and dp and fut[0] != dp:
            linha["decisao"] += f" — DIVERGÊNCIA fonte×revisão: rel_aberto→{fut[0]}"
    elif dp and dp > HOJE:
        linha["decisao"] = "INTOCADO_FUTURA (fora do escopo; auditar lote em sessão própria)"
        linha["acao"] = "nada"
    elif fonte is None or not prescs:
        linha["decisao"] = "SEM_FONTE (sem linhas no rel_aberto — revisão manual)"
        linha["acao"] = "nada"
    else:
        motivo = "stale/vencida" if dp else "sem data"
        destino = "futura" if fut else "todas estouradas → menor estourada (visível no 🔥)"
        linha["decisao"] = f"ATUALIZA ({motivo} → {destino})"
        linha["acao"] = "grava"
    return linha


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="grava no profiles.json (com backup)")
    args = ap.parse_args(argv)

    data = json.load(open(PROFILES, encoding="utf-8"))
    rel, snap = carregar_rel_aberto()

    linhas = []
    for sigla, d in data.items():
        if sigla.startswith("_") or not isinstance(d, dict):
            continue
        linhas.append(classifica(sigla, d, rel))

    muda = [x for x in linhas if x["acao"] == "grava"]
    anota = [x for x in linhas if x["acao"] == "anota"]
    sem_fonte = [x for x in linhas if "SEM_FONTE" in x["decisao"]]
    diverg = [x for x in linhas if "DIVERGÊNCIA" in x["decisao"]]

    REL_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = REL_DIR / f"RECALCULO_PRESCRICAO_{ts}"

    # CSV (; + BOM) — todas as linhas
    cols = ["sigla", "data_atual", "data_nova", "decisao", "urgencia", "fonte_cliente",
            "n_abertas", "n_estouradas", "primeira_estourada", "proxima_futura"]
    with open(f"{stem}.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for x in sorted(linhas, key=lambda r: (r["acao"] != "grava", r["sigla"])):
            w.writerow(x)

    # JSON (SSOT do relatório)
    json.dump({"gerado_em": ts, "snapshot_rel_aberto": snap, "hoje": HOJE.isoformat(),
               "linhas": linhas}, open(f"{stem}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # MD resumo
    md = [f"# Recálculo de data_prescricao_proxima — {ts}",
          f"_Fonte: rel_faturas_aberto.csv (snapshot {snap}) · hoje {HOJE} · "
          f"metodologia conservadora sem marcos não registrados._", "",
          f"**ATUALIZA: {len(muda)}** · anotação (protegido): {len(anota)} · "
          f"sem fonte: {len(sem_fonte)} · divergências fonte×revisão: {len(diverg)}", "",
          "| Sigla | Atual | Nova | Estouradas | Decisão |", "|---|---|---|---:|---|"]
    for x in sorted(linhas, key=lambda r: (r["acao"] != "grava", r["sigla"])):
        md.append(f"| {x['sigla']} | {x['data_atual']} | {x['data_nova']} | "
                  f"{x['n_estouradas']} | {x['decisao']} |")
    Path(f"{stem}.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Relatórios: {stem}.md/.csv/.json")
    print(f"ATUALIZA={len(muda)} ANOTA={len(anota)} SEM_FONTE={len(sem_fonte)} "
          f"DIVERGENCIA={len(diverg)}")

    if not args.apply:
        print("(dry-run — nada gravado; use --apply para gravar com backup)")
        return 0

    # ===== APPLY =====
    bkp = PROFILES.with_name(f"profiles_BACKUP_ANTES_{TAG}_{ts}.json")
    bkp.write_bytes(PROFILES.read_bytes())
    print(f"Backup: {bkp}")

    met = METODOLOGIA.format(dt=HOJE.isoformat(), snap=snap)
    for x in muda:
        d = data[x["sigla"]]
        d[f"data_prescricao_proxima_anterior_{TAG}"] = d.get("data_prescricao_proxima")
        d["data_prescricao_proxima"] = x["data_nova"]
        d[f"data_prescricao_metodologia_{TAG}"] = met
        d[f"faturas_abertas_presc_estourada_{TAG}"] = {
            "n": x["n_estouradas"], "primeira": x["primeira_estourada"],
            "fonte": f"rel_faturas_aberto.csv@{snap}",
        }
    for x in anota:
        d = data[x["sigla"]]
        d[f"faturas_abertas_presc_estourada_{TAG}"] = {
            "n": x["n_estouradas"], "primeira": x["primeira_estourada"],
            "fonte": f"rel_faturas_aberto.csv@{snap}",
            "nota": "PROTEGIDA_ART202_VI — marcos prevalecem; data_prescricao_proxima NÃO alterada",
        }

    with open(PROFILES, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print(f"profiles.json atualizado: {len(muda)} devedores + {len(anota)} anotações.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
