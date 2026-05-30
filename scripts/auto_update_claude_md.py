#!/usr/bin/env python3
"""
Auto-update CLAUDE.md from profiles.json + prodam.db.
Roda no inicio de cada sessao Cowork para manter CLAUDE.md sincronizado.
Gera metricas atualizadas automaticamente.
"""
import json
import re
import sqlite3
import os
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path

# fix 2026-04-22: script movido para scripts/, BASE precisa subir 1 nivel se necessario
BASE = Path(__file__).resolve().parent
if BASE.name == "scripts":
    BASE = BASE.parent
PROFILES = BASE / "PRODAM_DOCS" / "profiles.json"
DB = BASE / "prodam.db"
OUTPUT = BASE / "CLAUDE.md"

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prodam_utils import fmt_brl  # SSOT (Regra #16, Issue 11 Cat A)

def load_profiles():
    with open(PROFILES, "r", encoding="utf-8") as f:
        return json.load(f)

def query_db(sql):
    if not DB.exists():
        return []
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql).fetchall()]
    finally:
        conn.close()


def _query_db_counts():
    """Lê contagens vivas do prodam.db. Retorna dict com ok=True/False + conteúdo ou reason.
    Fallback robusto para que /sincronizar-prodam nunca quebre se o DB estiver lockado/ausente."""
    if not DB.exists():
        return {"ok": False, "reason": "DB nao encontrado"}
    try:
        conn = sqlite3.connect(str(DB), timeout=2.0)
        try:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
            views = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name"
            ).fetchall()
            parts = []
            for (name,) in tables:
                try:
                    n = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
                    parts.append(f"{name} ({n:,})".replace(",", "."))
                except sqlite3.Error:
                    parts.append(f"{name} (?)")
            return {
                "ok": True,
                "tables": ", ".join(parts),
                "views": ", ".join(v[0] for v in views) or "(nenhuma)",
            }
        finally:
            conn.close()
    except sqlite3.Error as e:
        return {"ok": False, "reason": f"sqlite3.Error: {e}"}


SKILLS_SRC = None  # PRODAM_DOCS/_SKILLS/ (onde moram as skills)
SKILLS_INDEX = None  # .claude/skills/INDEX.md (versionado)


def generate_skills_index():
    """Varre PRODAM_DOCS/_SKILLS/ em 2 padroes (*_SKILL.md flat + */SKILL.md em pasta),
    extrai nome + 1a frase de description, escreve .claude/skills/INDEX.md.
    INDEX.md fica versionado no git (rastreia *quais* skills existem); fontes sao privadas."""
    global SKILLS_SRC, SKILLS_INDEX
    if SKILLS_SRC is None:
        SKILLS_SRC = BASE / "PRODAM_DOCS" / "_SKILLS"
        SKILLS_INDEX = BASE / ".claude" / "skills" / "INDEX.md"
    if not SKILLS_SRC.exists():
        return 0
    SKILLS_INDEX.parent.mkdir(parents=True, exist_ok=True)

    entries = []
    seen_names = set()

    # Padrao 1: pasta com SKILL.md dentro (formato novo)
    for skill_md in sorted(SKILLS_SRC.glob("*/SKILL.md")):
        name = skill_md.parent.name
        if name in seen_names or re.search(r"\s*\(\d+\)$", name):
            continue
        seen_names.add(name)
        entries.append(_parse_skill(skill_md, name))

    # Padrao 2: arquivo *_SKILL.md flat na raiz (formato legado)
    for skill_md in sorted(SKILLS_SRC.glob("*_SKILL.md")):
        name = skill_md.stem.removesuffix("_SKILL")
        if name in seen_names or re.search(r"\s*\(\d+\)$", name):
            continue
        seen_names.add(name)
        entries.append(_parse_skill(skill_md, name))

    entries.sort(key=lambda x: x[0])
    if not entries:
        return 0

    out = ["# Índice de Skills do Projeto (`PRODAM_DOCS/_SKILLS/`)", ""]
    out.append("_Gerado por `scripts/auto_update_claude_md.py` — não editar manualmente._")
    out.append("")
    out.append("_Skills moram em `PRODAM_DOCS/_SKILLS/` (não versionado). Este índice é versionado para rastrear quais skills existem ao longo do tempo._")
    out.append("")
    out.append("| Skill | Descrição curta |")
    out.append("|-------|------------------|")
    for name, desc in entries:
        out.append(f"| `{name}` | {desc or '_(sem description)_'} |")
    SKILLS_INDEX.write_text("\n".join(out) + "\n", encoding="utf-8")
    return len(entries)


def _parse_skill(skill_md, name):
    """Le frontmatter YAML de um SKILL.md, extrai 1a frase de description.
    Cobre 2 formatos:
      - inline:        'description: Foo bar.'
      - folded/literal: 'description: >' (ou |, >-, |-, >+, |+, '> # comment')
                        seguido de bloco indentado, com linhas vazias virando
                        separadores de paragrafo (nao terminam o bloco).
    Bloco termina por: (a) linha nao-vazia com indent < base, (b) linha '---',
    (c) outra chave YAML top-level (indent 0 matching r'^[A-Za-z_][\\w-]*:').
    Retorna (name, desc)."""
    try:
        lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return (name, "(erro ao ler SKILL.md)")

    yaml_key_re = re.compile(r"^[A-Za-z_][\w-]*:")
    desc = ""
    in_fm = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if i == 0 and line.strip() == "---":
            in_fm = True
            i += 1
            continue
        if in_fm and line.strip() == "---":
            break
        if in_fm and line.startswith("description:"):
            rest = line.split(":", 1)[1].strip()
            if rest.startswith((">", "|")):
                block = []
                base_indent = None
                j = i + 1
                while j < len(lines):
                    nxt = lines[j]
                    if nxt.strip() == "":
                        if block:
                            block.append("")
                        j += 1
                        continue
                    if nxt.strip() == "---":
                        break
                    cur_indent = len(nxt) - len(nxt.lstrip())
                    if base_indent is None:
                        base_indent = cur_indent
                    if cur_indent < base_indent:
                        break
                    if cur_indent == 0 and yaml_key_re.match(nxt.strip()):
                        break
                    block.append(nxt.strip())
                    j += 1
                desc = " ".join(b for b in block if b).strip()
            else:
                desc = rest.strip('"').strip("'")
            break
        i += 1

    if desc:
        for sep in [". ", ".\n", " — ", " - "]:
            if sep in desc:
                desc = desc.split(sep, 1)[0] + ("." if sep.startswith(".") else "")
                break
        desc = desc[:200]
    return (name, desc)

def compute_metrics(data):
    m = {
        "total": len(data),
        "val_exig": 0, "val_orig": 0, "val_atualizado": 0,
        "faturas_total": 0, "faturas_exig": 0, "faturas_presc": 0,
        "categorias": {}, "forcas": {}, "proximos": {},
        "top10": [], "prescricao_urgente": [], "fase_counts": {},
    }
    items = []
    for sigla, d in data.items():
        ve = float(d.get("val_exig", 0) or 0)
        vo = float(d.get("val_orig", 0) or 0)
        va = float(d.get("val_atualizado", 0) or 0)
        m["val_exig"] += ve
        m["val_orig"] += vo
        m["val_atualizado"] += va
        m["faturas_total"] += int(d.get("faturas_total", 0) or 0)
        m["faturas_exig"] += int(d.get("faturas_exigiveis", 0) or 0)
        m["faturas_presc"] += int(d.get("faturas_prescritas", 0) or 0)
        
        cat = d.get("categoria", "N/A")
        m["categorias"][cat] = m["categorias"].get(cat, 0) + 1
        fp = d.get("forca_probatoria", "N/A")
        m["forcas"][fp] = m["forcas"].get(fp, 0) + 1
        
        pp = d.get("proximo_passo", "N/A")
        # Normalizar proximo_passo longo
        pp_short = pp.split(" — ")[0] if " — " in pp else pp
        pp_short = pp_short.split(" -")[0] if " -" in pp_short else pp_short
        m["proximos"][pp_short] = m["proximos"].get(pp_short, 0) + 1
        
        items.append((sigla, ve, fp, pp_short, d))
        
        # Prescricao urgente
        dp = d.get("data_prescricao_proxima")
        if dp:
            try:
                dt = datetime.strptime(dp, "%Y-%m-%d").date()
                dias = (dt - date.today()).days
                if 0 < dias <= 90:
                    m["prescricao_urgente"].append((sigla, dp, dias, ve))
            except:
                pass
    
    items.sort(key=lambda x: x[1], reverse=True)
    m["top10"] = items[:10]
    m["prescricao_urgente"].sort(key=lambda x: x[2])
    return m

def generate_claude_md(m):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    lines = []
    lines.append("# PROJETO PRODAM — Recuperação de Créditos")
    lines.append(f"## Contrato 002/2026 — PRODAM S.A. × Brandão Ozores Advogados")
    lines.append(f"**Atualizado automaticamente em {now} via auto_update_claude_md.py**")
    lines.append("")
    lines.append("> ⚠️ **NÃO editar este arquivo manualmente.** Conteúdo regenerado a cada `/sincronizar-prodam`.")
    lines.append("> Para mudar **regras/seções fixas** → editar `scripts/auto_update_claude_md.py`.")
    lines.append("> Para mudar **métricas/devedores** → editar `PRODAM_DOCS/profiles.json` e rodar `py -3.12 scripts\\auto_update_claude_md.py`.")
    lines.append("")

    # === IDENTIDADE (ESTÁTICO) ===
    lines.append("## IDENTIDADE")
    lines.append("- **Advogado**: Gabriel Mar (OAB/AM 15.697)")
    lines.append("- **Escritório**: Gabriel Mar Sociedade Individual de Advocacia")
    lines.append("- **Contratante**: Brandão Ozores Advogados")
    lines.append("- **Cliente**: PRODAM S.A. (CNPJ 04.407.920/0001-80, economia mista, Lei 13.303/2016)")
    lines.append("- **Fee**: 20% sobre créditos recuperados")
    lines.append("- **Obrigações**: Relatórios quinzenais (R$500/dia atraso | 10% do crédito por prescrição perdida)")
    lines.append("")

    # === METRICAS ===
    lines.append("## MÉTRICAS DO PORTFÓLIO")
    lines.append(f"- {m['total']} devedores ({m['categorias'].get('GOV_DIRETA',0)} Gov Direta, {m['categorias'].get('GOV_INDIRETA',0)} Gov Indireta, {m['categorias'].get('EMPRESA_PRIVADA',0)} Privadas)")
    lines.append(f"- {fmt_brl(m['val_exig'])} exigível | {fmt_brl(m['val_atualizado'])} atualizado")
    lines.append(f"- {m['faturas_total']} faturas ({m['faturas_exig']} exigíveis, {m['faturas_presc']} prescritas)")
    lines.append(f"- Força: {m['forcas'].get('FORTE',0)} FORTE, {m['forcas'].get('MÉDIA',0)} MÉDIA, {m['forcas'].get('FRACA',0)} FRACA")
    lines.append("")
    
    # === PIPELINE ===
    lines.append("## PIPELINE POR PRÓXIMO PASSO")
    for pp, count in sorted(m["proximos"].items(), key=lambda x: -x[1]):
        lines.append(f"- {pp}: {count} devedores")
    lines.append("")
    
    # === TOP 10 ===
    lines.append("## TOP 10 DEVEDORES (por valor exigível)")
    for sigla, ve, fp, pp, d in m["top10"]:
        lines.append(f"- {sigla}: {fmt_brl(ve)} | {fp} | {pp}")
    lines.append("")
    
    # === PRESCRICAO ===
    if m["prescricao_urgente"]:
        lines.append("## ALERTAS DE PRESCRIÇÃO (<90 dias)")
        for sigla, dp, dias, ve in m["prescricao_urgente"]:
            emoji = "🔴" if dias <= 30 else "🟠" if dias <= 60 else "🟡"
            lines.append(f"- {emoji} {sigla}: {dp} ({dias} dias) — {fmt_brl(ve)}")
        lines.append("")
    
    # === ESTRUTURA ===
    lines.append("## ESTRUTURA DO PROJETO")
    lines.append("- `PRODAM_DOCS/_ANALISE/prodam.db` — DB **canônico** (gerado por `PRODAM_DOCS/build_sqlite.py`)")
    lines.append("- `prodam.db` (raiz) — cópia derivada, atualizada por `scripts/atualizar_db.py` (é a que `scripts/consultas.py` lê)")
    lines.append("- `PRODAM_DOCS/profiles.json` — SSOT dos devedores (fonte autoritativa)")
    lines.append("- `PRODAM_DOCS/REFERENCIA_JURIDICA/` — base jurídica (20 subpastas; consultar ANTES de qualquer parecer)")
    lines.append("- `PRODAM_DOCS/_SKILLS/` — skills jurídicas pareadas")
    lines.append("- `SPCF_EXTRACAO/` — web scraping SPCF (rate-limit `time.sleep(1.5)` entre requisições)")
    lines.append("- `scripts/` — scripts Python principais (consultas, pipeline, dossiês, sync, auto-update)")
    lines.append("- `tests/test_prodam_utils.py` — testes unitários (pytest)")
    lines.append("- `.github/workflows/tests.yml` — CI: pytest + compileall + valida `profiles.json` em push/PR")
    lines.append("")
    
    # === SQLITE ===
    lines.append("## SQLITE prodam.db")
    db_counts = _query_db_counts()
    if db_counts["ok"]:
        lines.append(f"Tabelas: {db_counts['tables']}")
        lines.append(f"Views: {db_counts['views']}")
    else:
        lines.append("Tabelas: spcf_contratos (362), spcf_empenhos (16.789), spcf_faturas (1.837), spcf_nfs (52.998), pendrive_docs (3.699), devedores (81), reclassificacao (1.261), cruzamento_spcf_pendrive (1.460)")
        lines.append("Views: v_fatura_completa, v_fatura_sem_empenho, v_nf_sem_pagamento, v_pendrive_por_devedor, v_cruzamento_nf")
        lines.append(f"> ⚠️ Contagens estáticas — `prodam.db` indisponível no momento da geração ({db_counts['reason']}).")
    lines.append("")
    
    # === REGRAS ===
    lines.append("## REGRAS JURÍDICAS OBRIGATÓRIAS")
    lines.append("1. **Decreto Estadual nº 53.464/2026** (substitui 51.084/2025) — verificar 4 exceções antes de qualquer ação contra Gov AM")
    lines.append("2. Silêncio do devedor **NÃO** interrompe prescrição — exige ato inequívoco (Art. 202 CC taxativo)")
    lines.append("3. Juros pós-**Lei 14.905/2024** — NÃO presumir 1% a.m.; verificar arts. 404-406 CC")
    lines.append("4. Índices por contrato: consultar `normalizador.py` (mapa contrato/ano → regime, SSOT real). ⚠️ Valores absolutos (SM vigente, teto RPV, custas, honorários) NÃO têm SSOT consolidada — hoje inline em scripts de cálculo. NÃO criar `config_prodam.py` sem auditoria prévia.")
    lines.append("5. Adm. Direta → precatório/RPV (Art. 100 CF) | Adm. Indireta concorrencial → penhora direta (Tema 253/STF)")
    lines.append("6. NFs do credor **NÃO** são marcos interruptivos (exige ato do devedor)")
    lines.append("7. Prescrição é por **FATURA individual** (Art. 189 + 206 §5º I CC), contada do **VENCIMENTO**")
    lines.append("8. FUHAM = Fund. Alfredo da Matta | FHAJ = Fund. Hosp. Adriano Jorge — **NUNCA** inverter")
    lines.append("9. Empenho (NE) = reconhecimento tácito (Art. 202 VI CC) — interrompe prescrição")
    lines.append("10. SELIC já inclui correção + juros — **NÃO** somar separado. IGPM = só correção (juros à parte)")
    lines.append("11. Art. 202 CC: interrupção ocorre **UMA VEZ** (unicidade — REsp 1.963.067/MS). Fazenda reinicia por metade (Decreto 20.910/1932 = 2,5 anos)")
    lines.append("12. Tema 1.109/STJ: gestor público **NÃO** renuncia tacitamente a prescrição")
    lines.append("13. Composição documental (Contrato+NE+NF+Atesto) = título executivo (REsp 793.969/RJ, Min. **José Delgado** — Teori Zavascki foi vencido; nunca citar Teori como relator) <!-- auditado 2026-05-12: cascata propagada em 7 arquivos (11 ocorrências); regra #13 sem citações errôneas remanescentes em .md/.py do projeto -->")
    lines.append("14. Fee: **20%** sobre créditos recuperados (não 30%). RPV AM estadual = 20 × SM vigente (Lei AM 2.748/2002)")
    lines.append("15. **SSOT**: `PRODAM_DOCS/profiles.json` é a fonte autoritativa privada (100+ campos por devedor). `profiles_resumo.csv` é snapshot público versionado (subset de 11 colunas) — mantido em sincronia via pipeline. NUNCA usar Demonstrativo Excel antigo")
    lines.append("16. Valores monetários: **Decimal**, nunca float. Formato BRL: `R$ 1.234,56`")
    lines.append("17. `PRECEDENTES_VERIFICADOS.md` é a única fonte de jurisprudência verificada (3 fabricados + 6 distorcidos listados em references/)")
    lines.append("18. NUNCA emita opinião jurídica sem consultar `REFERENCIA_JURIDICA/` antes")
    lines.append("")

    # === HIERARQUIA JURÍDICA ===
    lines.append("## HIERARQUIA DE FONTES JURÍDICAS (consultar nessa ordem)")
    lines.append("1. **Nota Metodológica** (`PRODAM_DOCS/REFERENCIA_JURIDICA/01_NOTA_METODOLOGICA/`) — corrige todos os demais")
    lines.append("2. **Estudo Consolidado** (002/2026) — adaptado ao contrato atual")
    lines.append("3. **Estudo Exaustivo** — matriz genérica com minutas")
    lines.append("4. **Pesquisa Jurisprudencial** — STJ/STF/TJAM (usar só precedentes verificados)")
    lines.append("5. **Extração Contratual** — cláusula a cláusula dos contratos dos devedores")
    lines.append("6. `REFERENCIA_JURIDICA/` (20 subpastas) — SSOT jurídica, ANTES de qualquer tarefa")
    lines.append("")
    
    # === BENCHMARK DETRAN ===
    lines.append("## BENCHMARK AUDITORIA — DETRAN/AM (referência A+)")
    lines.append("- **Score composto:** 94,0/100 → A+ (EXCEPCIONAL)")
    lines.append("- **Pasta consolidada:** `Desktop\\DETRAN_AUDITORIA_COMPLETA\\` (3,2 GB, **8.210 arquivos**)")
    lines.append("- **Estrutura:** 13 pastas tipo × 14 formatos (PDF/JSON/CSV/MD/HTML/XLSX/DOCX/TXT/PY/JSONL/PNG/LOG)")
    lines.append("- **Contratos ingeridos DB:** 13 (12 PDFs + 1 vigente)")
    lines.append("- **Índices mapeados:** IGPM (7 contratos) + IPCA (3 contratos)")
    lines.append("- **Valor contratual total:** R$ 244,46M | Exigível: R$ 31,7M")
    lines.append("")
    lines.append("### Distribuição DETRAN por formato")
    lines.append("| Formato | Arquivos | Uso |")
    lines.append("|---------|----------|-----|")
    lines.append("| PDF | 3.631 | Documentos originais (contratos, NEs, faturas, cobranças) |")
    lines.append("| JSON | 1.698 | Textos extraídos + campos estruturados p/ LLM |")
    lines.append("| HTML | 1.428 | Scraping SPCF + dashboards |")
    lines.append("| CSV | 861 | Dados tabulares (prescrição, inadimplentes, pagamentos) |")
    lines.append("| MD | 222 | Relatórios + documentação |")
    lines.append("| TXT | 209 | Texto bruto + logs |")
    lines.append("| XLSX | 90 | Planilhas auditoria |")
    lines.append("| PY | 34 | Scripts reutilizáveis |")
    lines.append("| DOCX | 17 | Cartas + minutas |")
    lines.append("| JSONL | 8 | Corpora RAG/LLM |")
    lines.append("")

    # === PLAYBOOK PARA OUTROS ÓRGÃOS ===
    lines.append("## PLAYBOOK REPLICÁVEL (outros órgãos)")
    lines.append("Ver `PLAYBOOK_ORGAOS_V2.md` (passo-a-passo completo)")
    lines.append("")
    lines.append("### Comando único")
    lines.append("```powershell")
    lines.append("py -3.12 scripts\\orgao_pipeline_completa.py --orgao SEDUC")
    lines.append("```")
    lines.append("")
    lines.append("### TOP 5 próximos órgãos (por valor exigível)")
    lines.append("1. SEDUC (R$ 49,2M) | FORTE | F0 — ANALISAR_DOCUMENTACAO")
    lines.append("2. DETRAN (R$ 31,7M) ✅ A+ | Petição pronta F5 — PROTOCOLAR")
    lines.append("3. SES/SUSAM (R$ 14,7M) | FORTE | F3 — ENVIAR_TRD")
    lines.append("4. SSP (R$ 4,6M) | FORTE | F5 — PROTOCOLAR")
    lines.append("5. SEAD (R$ 2,3M) | FORTE | F3 — ENVIAR_TRD")
    lines.append("")

    # === SCRIPTS ===
    lines.append("## SCRIPTS PRINCIPAIS (em `scripts/` — fix 2026-04-22)")
    lines.append("| Script | Função |")
    lines.append("|--------|--------|")
    lines.append("| `scripts/prodam_utils.py` | `norm()` unidecode + `brl()` + datas + `match_flex` |")
    lines.append("| `scripts/orgao_pipeline_completa.py` | **Pipeline genérica `--orgao`** (PDF→JSON, OCR, ingestão DB, score) |")
    lines.append("| `scripts/sincronizar_prodam.py` | Comando mestre (rebuild DB + auditoria + dossiês + valida skills) |")
    lines.append("| `scripts/atualizar_db.py` | Rebuild `prodam.db` (chama `PRODAM_DOCS/build_sqlite.py`) |")
    lines.append("| `scripts/consultas.py` | 15 queries forenses (CLI + export CSV em `_ANALISE/consultas_csv/`) |")
    lines.append("| `scripts/detran/*.py` | Templates DETRAN (copiar e adaptar para outros órgãos) |")
    lines.append("| `scripts/auditoria_completude_devedor.py` | Checklist 11 itens (69 devedores) |")
    lines.append("| `scripts/dossie_multiformato_devedor.py` | 5 formatos por devedor |")
    lines.append("| `scripts/reconciliar_orfaos_reversos.py` | Popular devedores sem faturas via `norm()` |")
    lines.append("| `scripts/auto_update_claude_md.py` | Regenera este `CLAUDE.md` a partir de `profiles.json` |")
    lines.append("")

    # === 12 DIMENSÕES SCORE ===
    lines.append("## SCORE COMPOSTO — 12 dimensões (peso%)")
    lines.append("1. Integridade de Dados (10%)")
    lines.append("2. Cadeia Documental 5 elos (15%) — REsp 793.969/RJ")
    lines.append("3. Prescrição & Marcos Interruptivos (15%) — Art. 202 VI CC")
    lines.append("4. Blindagem Pré-Execução (10%) — 22/22 itens")
    lines.append("5. Compliance Jurídico (10%) — regime/índice/título/modelo")
    lines.append("6. Evidências Documentais (8%)")
    lines.append("7. Reconhecimento Tácito (8%) — Art. 202 VI CC (empenhos)")
    lines.append("8. Atualização Monetária (6%) — IGPM/IPCA/SELIC via BCB")
    lines.append("9. Priorização (6%)")
    lines.append("10. Risco Processual (5%) — p_recuperação")
    lines.append("11. Valor Recuperável E[V] (4%)")
    lines.append("12. Urgência/Prazo (3%)")
    lines.append("")
    lines.append("**Classificação:** A+ ≥90 | A ≥85 | A- ≥80 | B+ ≥75 | B ≥70")
    lines.append("")

    # === USO ===
    lines.append("## COMANDOS ÚTEIS (PowerShell)")
    lines.append("```powershell")
    lines.append("py -3.12 scripts\\consultas.py --lista              # ver todas as queries")
    lines.append("py -3.12 scripts\\consultas.py resumo_geral         # visão geral")
    lines.append("py -3.12 scripts\\consultas.py top_devedores        # ranking por valor")
    lines.append("py -3.12 scripts\\orgao_pipeline_completa.py --orgao SEDUC  # audita novo órgão")
    lines.append("py -3.12 scripts\\auto_update_claude_md.py          # regenerar este CLAUDE.md")
    lines.append("py -3.12 scripts\\sincronizar_prodam.py             # sincronização completa")
    lines.append("py -3.12 -m pytest tests\\ -v                       # testes unitários")
    lines.append("py -3.12 -m pytest tests\\test_prodam_utils.py::test_fmt_brl -v  # rodar UM teste único")
    lines.append("```")
    lines.append("Slash command equivalente: `/sincronizar-prodam` (definido em `.claude\\commands\\sincronizar-prodam.md`).")
    lines.append("")

    # === DESENVOLVIMENTO ===
    lines.append("## DESENVOLVIMENTO")
    lines.append("- **Plataforma:** Windows + PowerShell (não usar bash). Python via launcher `py -3.12` (sem venv).")
    lines.append("- **Dependências:** `py -3.12 -m pip install -r requirements.txt` (essenciais: `openpyxl`, `polars`, `requests`; OCR/scraping são opt-in comentado).")
    lines.append("- **Testes:** `py -3.12 -m pytest tests\\ -v` — cobre `prodam_utils` (BRL, normalização, datas, prescrição).")
    lines.append("- **CI:** `.github\\workflows\\tests.yml` em push/PR para `main` — pytest + `compileall` (sintaxe) + valida `profiles.json` (≥50 devedores, todos com CNPJ, `_metadata` presente) + smoke test do `sincronizar_prodam.py`.")
    lines.append("- **Convenções de dados (críticas):**")
    lines.append("  - Valores monetários: **`Decimal`**, nunca `float`. Formato BRL `R$ 1.234,56` via `prodam_utils.fmt_brl`.")
    lines.append("  - CSV: separador **`;`** + encoding **`utf-8-sig`** (BOM) — abre direto no Excel.")
    lines.append("  - Salvar extrações em **JSON + XLSX + CSV** no mesmo script. JSON é a SSOT; XLSX/CSV são derivados.")
    lines.append("  - PDFs são prova jurídica — **nunca apagar originais**; backup em `_BACKUPS/` ou `_ARQUIVO_DRIFT/`.")
    lines.append("  - SPCF: `time.sleep(1.5)` entre requisições (rate limit obrigatório).")
    lines.append("  - Contratos têm 3 formatos coexistindo (`006/2021` em `spcf_contratos`/PDFs, `6/2021` em `profiles.json`, `2021/006` em outras fontes) — usar skill `normalizador-contratos-prodam` ANTES de qualquer JOIN.")
    lines.append("")

    # === SAFEGUARDS ===
    lines.append("## SAFEGUARDS (instalados 2026-05-12, commit a27c429)")
    lines.append("- **Pre-commit hook** (`.pre-commit-config.yaml`): `ruff-check` + validador `profiles.json`. Instalar local com `pre-commit install`.")
    lines.append("- **`.gitignore`**: `PRODAM_DOCS/` inteiro fora do repo (25,4 GB de PDFs + `profiles.json` privado, não versionado).")
    lines.append("- **Hook anti-delete PDF** (`.claude\\hooks\\block_pdf_delete.ps1`): bloqueia `rm`/`Remove-Item` em arquivos `*.pdf` (PDFs = prova jurídica).")
    lines.append("")

    # === PLUGINS / SKILLS / HOOKS EXTERNOS ===
    lines.append("## PLUGINS INSTALADOS (Claude Code)")
    lines.append("")
    lines.append("### Inventário")
    lines.append("**Local ao PROJETO_PRODAM** (`.claude\\settings.local.json`):")
    lines.append("- `superpowers@claude-plugins-official` v5.1.0 — instalado 08/05/2026 (source: `github.com/obra/superpowers.git`). 14 skills `superpowers:*`. Sem hooks.")
    lines.append("")
    lines.append("**Global ao usuário** (`~\\.claude\\`):")
    lines.append("- `get-shit-done-cc` (GSD) v1.41.0 — 66 skills `gsd-*`, 33 agents `gsd-*`, 12 hooks, statusline override, bundle CommonJS em `~\\.claude\\get-shit-done\\bin\\`.")
    lines.append("- `context-mode@context-mode` v1.0.111 — ~11 skills `context-mode:*` + MCP server `mcp__plugin_context-mode_*` (ctx_execute, ctx_batch_execute, ctx_doctor) + 2 hooks (PreToolUse + SessionStart).")
    lines.append("- 5 plugins user-scope habilitados em `enabledPlugins`: `commit-commands`, `claude-md-management`, `claude-code-setup`, `context7`, `pyright-lsp`.")
    lines.append("")

    # === ABRIR O DB ===
    lines.append("## ABRIR O prodam.db SEM CÓDIGO")
    lines.append("```powershell")
    lines.append("# Datasette (web UI):")
    lines.append("datasette serve \"PRODAM_DOCS\\_ANALISE\\prodam.db\" --open")
    lines.append("")
    lines.append("# DuckDB (SQL no terminal):")
    lines.append("duckdb -c \"SELECT * FROM spcf_faturas WHERE cliente='SEDUC' LIMIT 10\" \"PRODAM_DOCS\\_ANALISE\\prodam.db\"")
    lines.append("```")
    lines.append("Beekeeper Studio: File → Open → escolher `PRODAM_DOCS\\_ANALISE\\prodam.db`.")
    lines.append("")

    # === OUTROS MAPAS ===
    lines.append("## OUTROS MAPAS DO PROJETO (consultar quando relevante)")
    lines.append("| Arquivo | O que cobre |")
    lines.append("|---------|-------------|")
    lines.append("| `LEIAME.md` | Mapa de navegação curto: 3 pastas ativas, fontes canônicas, comandos para abrir o DB |")
    lines.append("| `.claude\\napkin.md` | **Runbook curado** — regras priorizadas, atualizado a cada leitura (gotchas PowerShell, Decimal, regex Select-String, comando literal) |")
    lines.append("| `.claude\\skills\\INDEX.md` | **Índice das skills do projeto** (versionado; gerado por `auto_update_claude_md.py` lendo `PRODAM_DOCS/_SKILLS/`) — nome + descrição curta |")
    lines.append("| `~\\.claude\\projects\\C--Users-gabri-Desktop-PROJETO-PRODAM\\memory\\MEMORY.md` | **Memória persistente entre sessões** — feedback do advogado, projeto, referências, decisões de tolerância |")
    lines.append("| `PRODAM_DOCS\\CLAUDE.md` | Detalhe OCR v4 + 78 pastas `_CONSOLIDADO` + dossiês multi-formato + reorganização Desktop |")
    lines.append("| `PLAYBOOK_ORGAOS_V2.md` | Passo-a-passo replicável (13 passos para auditar novo órgão; validado no DETRAN A+ 94/100) |")
    lines.append("| `HISTORICO_SESSOES.md` | Decisões recentes — **histórico, pode estar desatualizado** |")
    lines.append("| `PRODAM_DOCS\\REFERENCIA_JURIDICA\\01_NOTA_METODOLOGICA\\` | Corrige todos os demais estudos jurídicos |")
    lines.append("| `PRODAM_DOCS\\REFERENCIA_JURIDICA\\PRECEDENTES_VERIFICADOS.md` | Única fonte de jurisprudência verificada (3 fabricados + 6 distorcidos catalogados) |")
    lines.append("")

    # === AGENT SKILLS (setup-matt-pocock-skills) ===
    lines.append("## AGENT SKILLS (skills de engenharia)")
    lines.append("Convenções que skills genéricas (`to-issues`, `triage`, `to-prd`, `tdd`, `diagnose`, `grill-with-docs`) consomem neste repo. Detalhes em `docs/agents/*.md`.")
    lines.append("")
    lines.append("- **Issue tracker** → `_QUESTOES_CRITICAS/` (arquivos `NN_TITULO.md` numerados). Ver `docs/agents/issue-tracker.md`.")
    lines.append("- **Triage labels** → 5 canônicos (`needs-triage`/`needs-info`/`ready-for-agent`/`ready-for-human`/`wontfix`), aplicados como linha `Status:` no topo do arquivo. Ver `docs/agents/triage-labels.md`.")
    lines.append("- **Domain docs** → single-context: `CONTEXT.md` + `docs/adr/` no root (criados sob demanda por `grill-with-docs`). Ver `docs/agents/domain.md`.")
    lines.append("")

    return "\n".join(lines) + "\n"

def main():
    if not PROFILES.exists():
        print(f"ERRO: {PROFILES} nao encontrado")
        return

    n_skills = generate_skills_index()
    if n_skills:
        print(f"INDEX.md atualizado: {SKILLS_INDEX} ({n_skills} skills)")

    data = load_profiles()
    m = compute_metrics(data)
    content = generate_claude_md(m)

    # Escreve diretamente (sem backup — evita PermissionError em sandbox)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"CLAUDE.md atualizado: {OUTPUT}")
    if m["prescricao_urgente"]:
        print(f"  {len(m['prescricao_urgente'])} devedor(es) com prescricao urgente (<90 dias)")


if __name__ == "__main__":
    main()
