"""
Profiling completo da pasta mãe PROJETO_PRODAM.

Gera um JSON consolidado com:
- Inventário por pasta (contagem, tamanho, formato)
- Cobertura por devedor (estrutura _CONSOLIDADO)
- Comparação com benchmark DETRAN
- Qualidade de prodam.db e profiles.json
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path("/sessions/gallant-focused-brahmagupta/mnt/PROJETO_PRODAM")
OUT = Path("/sessions/gallant-focused-brahmagupta/mnt/outputs/profile_pasta_mae.json")

SUBPASTAS_CONSOLIDADO_ESPERADAS = [
    "01_CONTRATOS",
    "02_EMPENHOS",
    "03_FATURAS",
    "04_NOTAS_LIQUIDACAO",
    "05_ACEITES",
    "06_COBRANCAS",
    "07_SCRAPING_SPCF",
    "08_PDFS_ORIGINAIS",
    "09_RELATORIOS",
]


def stat_dir(p: Path, max_files: int | None = None) -> dict:
    total_files = 0
    total_size = 0
    ext_counter: Counter = Counter()
    t0 = time.time()
    try:
        for root, _, files in os.walk(p):
            for f in files:
                total_files += 1
                ext = os.path.splitext(f)[1].lower() or "(sem_ext)"
                ext_counter[ext] += 1
                try:
                    total_size += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
                if max_files is not None and total_files >= max_files:
                    break
            if max_files is not None and total_files >= max_files:
                break
    except Exception as exc:
        return {"erro": str(exc)}
    return {
        "files": total_files,
        "size_mb": round(total_size / 1024 / 1024, 2),
        "ext_top10": dict(ext_counter.most_common(10)),
        "walk_sec": round(time.time() - t0, 2),
    }


def profile_devedor_consolidado(nome: str) -> dict:
    pasta = BASE / "PRODAM_DOCS" / f"{nome}_CONSOLIDADO"
    if not pasta.exists():
        return {"existe": False}
    resultado = {
        "existe": True,
        "subpastas": {},
        "cobertura_pct": 0.0,
        "total_arquivos": 0,
    }
    presentes = 0
    for sub in SUBPASTAS_CONSOLIDADO_ESPERADAS:
        p = pasta / sub
        if p.exists():
            info = stat_dir(p)
            if info.get("files", 0) > 0:
                presentes += 1
                resultado["total_arquivos"] += info["files"]
            resultado["subpastas"][sub] = info
        else:
            resultado["subpastas"][sub] = {"files": 0, "missing": True}
    resultado["cobertura_pct"] = round(presentes / len(SUBPASTAS_CONSOLIDADO_ESPERADAS) * 100, 1)
    return resultado


def profile_devedor_dossie(nome: str) -> dict:
    pasta = BASE / "PRODAM_DOCS" / f"{nome}_DOSSIE"
    if not pasta.exists():
        return {"existe": False}
    artefatos_esperados = [
        "AUDITORIA.md",
        "AUDITORIA.html",
        "dados_completos.json",
        "dashboard.html",
        "INVENTARIO.xlsx",
        "README.md",
        "RESUMO_EXECUTIVO.md",
        "csv",
        "llm",
    ]
    encontrados = {}
    for a in artefatos_esperados:
        p = pasta / a
        encontrados[a] = p.exists()
    total_arquivos = stat_dir(pasta).get("files", 0)
    cobertura = sum(encontrados.values()) / len(artefatos_esperados) * 100
    return {
        "existe": True,
        "artefatos": encontrados,
        "cobertura_pct": round(cobertura, 1),
        "total_arquivos": total_arquivos,
    }


def profile_prodam_db() -> dict:
    db = BASE / "prodam.db"
    if not db.exists():
        return {"erro": "arquivo_nao_existe"}
    con = sqlite3.connect(str(db))
    cur = con.cursor()
    cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view')")
    objs = cur.fetchall()
    resultado: dict = {
        "tamanho_mb": round(os.path.getsize(db) / 1024 / 1024, 2),
        "tabelas": {},
        "views": [],
    }
    for nome, tipo in objs:
        if tipo == "view":
            resultado["views"].append(nome)
            continue
        try:
            cur.execute(f"SELECT COUNT(*) FROM '{nome}'")
            count = cur.fetchone()[0]
        except Exception:
            count = None
        try:
            cur.execute(f"PRAGMA table_info('{nome}')")
            cols = [{"col": r[1], "tipo": r[2], "pk": bool(r[5])} for r in cur.fetchall()]
        except Exception:
            cols = []
        resultado["tabelas"][nome] = {"count": count, "cols": len(cols), "schema": cols}
    con.close()
    return resultado


def profile_profiles_json() -> dict:
    p = BASE / "PRODAM_DOCS" / "profiles.json"
    if not p.exists():
        return {"erro": "arquivo_nao_existe"}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"erro": str(exc)}
    if isinstance(data, dict):
        itens = list(data.values())
    elif isinstance(data, list):
        itens = data
    else:
        itens = []
    if not itens:
        return {"n_devedores": 0}
    sample = itens[0] if itens else {}
    regimes = Counter()
    forcas = Counter()
    proximo_passo = Counter()
    campos_faltantes = defaultdict(int)
    valor_exigivel_total = 0.0
    valor_atualizado_total = 0.0
    for d in itens:
        if not isinstance(d, dict):
            continue
        regimes[d.get("regime", "")] += 1
        forcas[d.get("forca_probatoria", "")] += 1
        proximo_passo[d.get("proximo_passo", "")] += 1
        for campo in ("cnpj", "regime", "forca_probatoria", "valor_exigivel", "valor_atualizado", "proximo_passo"):
            if not d.get(campo):
                campos_faltantes[campo] += 1
        try:
            valor_exigivel_total += float(d.get("valor_exigivel") or 0)
        except (TypeError, ValueError):
            pass
        try:
            valor_atualizado_total += float(d.get("valor_atualizado") or 0)
        except (TypeError, ValueError):
            pass
    return {
        "n_devedores": len(itens),
        "campos_sample": list(sample.keys()) if isinstance(sample, dict) else [],
        "regimes": dict(regimes.most_common()),
        "forca_probatoria": dict(forcas.most_common()),
        "proximo_passo": dict(proximo_passo.most_common()),
        "campos_faltantes": dict(campos_faltantes),
        "valor_exigivel_total": round(valor_exigivel_total, 2),
        "valor_atualizado_total": round(valor_atualizado_total, 2),
    }


def main():
    print("[1/6] Listando devedores...", flush=True)
    prodam_docs = BASE / "PRODAM_DOCS"
    devedores = sorted({d.name.replace("_CONSOLIDADO", "") for d in prodam_docs.iterdir() if d.is_dir() and d.name.endswith("_CONSOLIDADO")})
    print(f"  {len(devedores)} devedores encontrados", flush=True)

    resultado = {
        "gerado_em": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pasta_raiz": str(BASE),
        "n_devedores_pastas": len(devedores),
        "devedores": devedores,
    }

    print("[2/6] Perfil da pasta mae (topo)...", flush=True)
    topo = {}
    subdirs_topo = ["AUDITORIA_COMPLETUDE", "DETRAN_AUDITORIA", "DETRAN_CONSOLIDADO_JSON",
                    "DETRAN_CONTRATOS_JSON", "DOSSIES", "DOSSIES_MULTIFORMATO",
                    "_legado", "dados", "relatorios", "scripts", "tests"]
    for d in subdirs_topo:
        p = BASE / d
        if p.exists():
            topo[d] = stat_dir(p)
    resultado["pastas_topo"] = topo

    print("[3/6] Perfil prodam.db...", flush=True)
    resultado["prodam_db"] = profile_prodam_db()

    print("[4/6] Perfil profiles.json...", flush=True)
    resultado["profiles_json"] = profile_profiles_json()

    print("[5/6] Cobertura por devedor (_CONSOLIDADO)...", flush=True)
    cobertura_consolidado = {}
    for i, nome in enumerate(devedores, 1):
        if i % 10 == 0:
            print(f"  [{i}/{len(devedores)}] {nome}", flush=True)
        cobertura_consolidado[nome] = profile_devedor_consolidado(nome)
    resultado["cobertura_consolidado"] = cobertura_consolidado

    print("[6/6] Cobertura por devedor (_DOSSIE)...", flush=True)
    cobertura_dossie = {}
    for i, nome in enumerate(devedores, 1):
        if i % 10 == 0:
            print(f"  [{i}/{len(devedores)}] {nome}", flush=True)
        cobertura_dossie[nome] = profile_devedor_dossie(nome)
    resultado["cobertura_dossie"] = cobertura_dossie

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nPronto: {OUT}", flush=True)
    print(f"Tamanho do JSON: {OUT.stat().st_size / 1024:.1f} KB", flush=True)


if __name__ == "__main__":
    main()
