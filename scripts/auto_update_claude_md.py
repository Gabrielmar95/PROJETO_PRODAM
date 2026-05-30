#!/usr/bin/env python3
"""
Auto-update CLAUDE.md (raiz) + 3 satélites + índice de skills a partir de profiles.json + prodam.db.

Gera 4 arquivos .md (+ INDEX.md quando há skills em _SKILLS/):
  1. CLAUDE.md                — root enxuto (~120 linhas), regras + métricas vivas
  2. STATUS_DEVEDORES.md      — todos os 70 devedores (além do Top 10)
  3. WORKFLOW_COBRANCA.md     — pipeline end-to-end F0→F6
  4. PLAYBOOK_ORGAOS_V2.md    — 13 passos validados no DETRAN A+ 94/100

Rodar:
  py -3.12 scripts\\auto_update_claude_md.py
"""
import json
import re
import sqlite3
from datetime import datetime, date
from pathlib import Path

# fix 2026-04-22: script movido para scripts/, BASE precisa subir 1 nivel se necessario
BASE = Path(__file__).resolve().parent
if BASE.name == "scripts":
    BASE = BASE.parent
PROFILES = BASE / "PRODAM_DOCS" / "profiles.json"
DB = BASE / "prodam.db"
OUTPUT = BASE / "CLAUDE.md"
OUTPUT_STATUS = BASE / "STATUS_DEVEDORES.md"
OUTPUT_WORKFLOW = BASE / "WORKFLOW_COBRANCA.md"
OUTPUT_PLAYBOOK = BASE / "PLAYBOOK_ORGAOS_V2.md"

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
        "all_items": [],
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

        fase = d.get("fase_atual", "N/A") or "N/A"
        m["fase_counts"][fase] = m["fase_counts"].get(fase, 0) + 1

        # Dias até prescrição (pode ser None)
        dias_presc = None
        dp = d.get("data_prescricao_proxima")
        if dp:
            try:
                dt = datetime.strptime(dp, "%Y-%m-%d").date()
                dias_presc = (dt - date.today()).days
                if 0 < dias_presc <= 90:
                    m["prescricao_urgente"].append((sigla, dp, dias_presc, ve))
            except (ValueError, TypeError):
                pass

        items.append((sigla, ve, fp, pp_short, d, dias_presc, fase))

    items.sort(key=lambda x: x[1], reverse=True)
    m["top10"] = items[:10]
    m["all_items"] = items
    m["prescricao_urgente"].sort(key=lambda x: x[2])
    return m


def generate_claude_md(m):
    """CLAUDE.md raiz enxuto (~120 linhas).

    10 seções: identidade, status portfolio, alertas prescrição <90d, link workflow,
    regras jurídicas, hierarquia de fontes, convenções técnicas, mapas, comandos, skills/MCP.
    Fatos jurídicos verdadeiros (REsp 793.969/José Delgado, RPV/AM Lei 2.748/2002, FUHAM≠FHAJ,
    fee 20%) migrados como conhecimento neutro nas Regras Jurídicas — sem camada de safeguard."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    L = []

    # ============ CABEÇALHO ============
    L.append("# PROJETO PRODAM — Recuperação de Créditos")
    L.append("## Contrato 002/2026 — PRODAM S.A. × Brandão Ozores Advogados")
    L.append(f"_Atualizado em {now} via `scripts/auto_update_claude_md.py`._")
    L.append("")
    L.append("> Conteúdo regenerado a cada `/sincronizar-prodam`. Para regras fixas → editar o gerador. Para métricas → editar `PRODAM_DOCS/profiles.json` e rodar `py -3.12 scripts\\auto_update_claude_md.py`.")
    L.append("")

    # ============ 1. IDENTIDADE ============
    L.append("## 1. IDENTIDADE")
    L.append("- **Advogado**: Gabriel Mar (OAB/AM 15.697) — Gabriel Mar Sociedade Individual de Advocacia")
    L.append("- **Contratante**: Brandão Ozores Advogados | **Cliente**: PRODAM S.A. (CNPJ 04.407.920/0001-80, economia mista, Lei 13.303/2016)")
    L.append("- **Fee**: 20% sobre créditos recuperados | **Obrigações**: relatórios quinzenais (R$500/dia atraso | 10% do crédito por prescrição perdida)")
    L.append("")

    # ============ 2. STATUS DO PORTFÓLIO ============
    L.append("## 2. STATUS DO PORTFÓLIO")
    L.append(f"- **{m['total']} devedores** ({m['categorias'].get('GOV_DIRETA',0)} Gov Direta, {m['categorias'].get('GOV_INDIRETA',0)} Gov Indireta, {m['categorias'].get('EMPRESA_PRIVADA',0)} Privadas)")
    L.append(f"- **{fmt_brl(m['val_exig'])} exigível** | {fmt_brl(m['val_atualizado'])} atualizado")
    L.append(f"- **{m['faturas_total']} faturas** ({m['faturas_exig']} exigíveis, {m['faturas_presc']} prescritas)")
    L.append(f"- **Força**: {m['forcas'].get('FORTE',0)} FORTE · {m['forcas'].get('MÉDIA',0)} MÉDIA · {m['forcas'].get('FRACA',0)} FRACA")
    L.append("")
    L.append("**Pipeline (próximo passo)**: " + " · ".join(f"{pp}={c}" for pp, c in sorted(m["proximos"].items(), key=lambda x: -x[1])))
    L.append("")
    L.append("**Top 10 devedores** (por valor exigível):")
    for sigla, ve, fp, pp, d, _dias, _fase in m["top10"]:
        L.append(f"- {sigla}: {fmt_brl(ve)} | {fp} | {pp}")
    L.append("")
    L.append("→ Lista completa em [`STATUS_DEVEDORES.md`](STATUS_DEVEDORES.md).")
    L.append("")

    # ============ 3. ALERTAS DE PRESCRIÇÃO <90 dias ============
    L.append("## 3. ALERTAS DE PRESCRIÇÃO (<90 dias)")
    if m["prescricao_urgente"]:
        for sigla, dp, dias, ve in m["prescricao_urgente"]:
            emoji = "🔴" if dias <= 30 else "🟠" if dias <= 60 else "🟡"
            L.append(f"- {emoji} **{sigla}**: {dp} ({dias} dias) — {fmt_brl(ve)}")
    else:
        L.append("- _(nenhum devedor com prescrição em até 90 dias na varredura atual)_")
    L.append("")

    # ============ 4. WORKFLOW (link) ============
    L.append("## 4. WORKFLOW DE COBRANÇA")
    L.append("Pipeline end-to-end F0→F6 (skills, gates documentais, prazos): [`WORKFLOW_COBRANCA.md`](WORKFLOW_COBRANCA.md).")
    L.append("")

    # ============ 5. REGRAS JURÍDICAS (fatos neutros — sem camada de safeguard) ============
    L.append("## 5. REGRAS JURÍDICAS")
    L.append("1. **Decreto Estadual AM nº 53.464/2026** (substitui 51.084/2025) — verificar 4 exceções antes de qualquer ação contra Gov AM.")
    L.append("2. Silêncio do devedor **não** interrompe prescrição — exige ato inequívoco (Art. 202 CC, rol taxativo).")
    L.append("3. Juros pós-**Lei 14.905/2024** — não presumir 1% a.m.; verificar arts. 404-406 CC.")
    L.append("4. **Índices por contrato**: consultar `scripts/normalizador.py` (mapa contrato/ano → regime, SSOT real). Valores absolutos (SM vigente, teto RPV, custas) hoje inline em scripts de cálculo — não criar `config_prodam.py` sem auditoria prévia.")
    L.append("5. Adm. Direta → precatório/RPV (Art. 100 CF) | Adm. Indireta concorrencial → penhora direta (Tema 253/STF).")
    L.append("6. NFs do credor **não** são marcos interruptivos (exige ato do devedor).")
    L.append("7. Prescrição é por **fatura individual** (Art. 189 + 206 §5º I CC), contada do **vencimento**.")
    L.append("8. **FUHAM** = Fundação Alfredo da Matta · **FHAJ** = Fundação Hospital Adriano Jorge — nomes distintos, nunca inverter.")
    L.append("9. Empenho (NE) = reconhecimento tácito (Art. 202 VI CC) — interrompe prescrição.")
    L.append("10. SELIC já inclui correção + juros — não somar separado. IGPM = só correção (juros à parte).")
    L.append("11. Art. 202 CC: interrupção ocorre **uma vez** (unicidade — REsp 1.963.067/MS). Fazenda Pública reinicia por metade (Decreto 20.910/1932 = 2,5 anos).")
    L.append("12. **Tema 1.109/STJ**: gestor público não renuncia tacitamente a prescrição.")
    L.append("13. Composição documental (Contrato + NE + NF + Atesto) = título executivo (**REsp 793.969/RJ**, Rel. p/ acórdão **Min. José Delgado**; Min. Teori Zavascki foi vencido).")
    L.append("14. **Fee = 20%** sobre créditos recuperados. **RPV/AM estadual = 20 × SM vigente**, fundamento **Lei AM 2.748/2002** (não Lei 3.683/2012).")
    L.append("15. `PRODAM_DOCS/profiles.json` é a **SSOT** dos devedores — nunca usar Demonstrativo Excel antigo.")
    L.append("16. Valores monetários: **Decimal**, nunca float. Formato BRL: `R$ 1.234,56`.")
    L.append("17. `PRODAM_DOCS/REFERENCIA_JURIDICA/PRECEDENTES_VERIFICADOS.md` é a única fonte de jurisprudência verificada (3 fabricados + 6 distorcidos catalogados).")
    L.append("18. Consultar `PRODAM_DOCS/REFERENCIA_JURIDICA/` antes de emitir opinião jurídica.")
    L.append("")

    # ============ 6. HIERARQUIA DE FONTES JURÍDICAS ============
    L.append("## 6. HIERARQUIA DE FONTES JURÍDICAS (consultar nessa ordem)")
    L.append("1. **Nota Metodológica** (`PRODAM_DOCS/REFERENCIA_JURIDICA/01_NOTA_METODOLOGICA/`) — corrige todos os demais.")
    L.append("2. **Estudo Consolidado** (002/2026) — adaptado ao contrato atual.")
    L.append("3. **Estudo Exaustivo** — matriz genérica com minutas.")
    L.append("4. **Pesquisa Jurisprudencial** — STJ/STF/TJAM (só precedentes verificados).")
    L.append("5. **Extração Contratual** — cláusula a cláusula dos contratos dos devedores.")
    L.append("6. `PRODAM_DOCS/REFERENCIA_JURIDICA/` (20 subpastas) — SSOT jurídica do projeto.")
    L.append("")

    # ============ 7. CONVENÇÕES TÉCNICAS ============
    L.append("## 7. CONVENÇÕES TÉCNICAS")
    L.append("- **Plataforma**: Windows + PowerShell. Python via `py -3.12` (sem venv). Bash não é usado.")
    L.append("- **Valores monetários**: `Decimal`, nunca `float`. Formato BRL via `prodam_utils.fmt_brl`.")
    L.append("- **CSV**: separador `;` + encoding `utf-8-sig` (BOM) — abre direto no Excel.")
    L.append("- **Salvar extrações** em **JSON + XLSX + CSV** no mesmo script. JSON é SSOT; XLSX/CSV são derivados.")
    L.append("- **PDFs** são prova jurídica — nunca apagar originais; backup em `_BACKUPS/` ou `_ARQUIVO_DRIFT/`.")
    L.append("- **SPCF**: `time.sleep(1.5)` entre requisições (rate limit obrigatório).")
    L.append("- **Contratos** têm 3 formatos coexistindo (`006/2021` em `spcf_contratos`, `6/2021` em `profiles.json`, `2021/006` em outras fontes) — normalizar antes de JOIN.")
    L.append("- **Testes**: `py -3.12 -m pytest tests\\ -v` cobre `prodam_utils` (BRL, normalização, datas, prescrição). CI em `.github/workflows/tests.yml` valida `profiles.json`.")
    L.append("- **Proteções do repo** (não desativar sem motivo):")
    L.append("  - `.claude/hooks/block_pdf_delete.ps1` — hook que impede o **Claude Code** de remover `*.pdf` (provas) via Bash/PowerShell. Não cobre exclusão manual no Explorer.")
    L.append("  - `.pre-commit-config.yaml` — `ruff-check` (E9/F63/F7/F82) em `scripts/`. A validação de `profiles.json` (≥50 devedores/CNPJ/`_metadata`) é no **CI**, não aqui.")
    L.append("  - `.gitignore` — fora do repo: `PRODAM_DOCS/` (com `profiles.json`), `*.pdf`, `*.db`, segredos.")
    L.append("")

    # ============ 8. MAPAS DO PROJETO ============
    L.append("## 8. MAPAS DO PROJETO")
    L.append("| Caminho | O que cobre |")
    L.append("|---------|-------------|")
    L.append("| `PRODAM_DOCS/profiles.json` | **SSOT** dos 70 devedores (privado, fora do repo) |")
    L.append("| `PRODAM_DOCS/_ANALISE/prodam.db` | DB canônico (gerado por `PRODAM_DOCS/build_sqlite.py`) |")
    L.append("| `prodam.db` (raiz) | Cópia derivada usada por `scripts/consultas.py` |")
    L.append("| `PRODAM_DOCS/REFERENCIA_JURIDICA/` | Base jurídica (20 subpastas; consultar antes de parecer) |")
    L.append("| `PRODAM_DOCS/_SKILLS/` | Skills jurídicas curadas |")
    L.append("| `SPCF_EXTRACAO/` | Web scraping SPCF (rate-limit obrigatório) |")
    L.append("| `scripts/` | Pipelines, consultas, dossiês, sincronização |")
    L.append("| `STATUS_DEVEDORES.md` | Lista completa dos 70 devedores |")
    L.append("| `WORKFLOW_COBRANCA.md` | Pipeline end-to-end F0→F6 |")
    L.append("| `PLAYBOOK_ORGAOS_V2.md` | 13 passos validados no DETRAN A+ 94/100 |")
    L.append("| `.claude/skills/INDEX.md` | Índice das skills do projeto (versionado) |")
    L.append("| `~/.claude/CLAUDE.md` | Preferências pessoais (PowerShell, identidade, anti-alucinação) |")
    L.append("")

    # ============ 9. COMANDOS ESSENCIAIS ============
    L.append("## 9. COMANDOS ESSENCIAIS")
    L.append("```powershell")
    L.append("py -3.12 scripts\\auto_update_claude_md.py          # regenera CLAUDE.md + 3 satélites + índice de skills")
    L.append("py -3.12 scripts\\sincronizar_prodam.py             # sincronização completa")
    L.append("py -3.12 scripts\\consultas.py --lista              # lista 15 queries forenses")
    L.append("py -3.12 scripts\\orgao_pipeline_completa.py --orgao SEDUC  # audita novo órgão")
    L.append("py -3.12 -m pytest tests\\ -v                       # testes unitários")
    L.append("```")
    L.append("Slash command equivalente: `/sincronizar-prodam` (`.claude\\commands\\sincronizar-prodam.md`).")
    L.append("")

    # ============ 10. AGENT SKILLS + DB ============
    L.append("## 10. AGENT SKILLS + DB")
    L.append("- **Skills do projeto**: [`.claude/skills/INDEX.md`](.claude/skills/INDEX.md) — índice versionado (nome + descrição curta).")
    L.append("- **Agent skills (engenharia)**: `to-issues`, `triage`, `to-prd`, `tdd`, `diagnose`, `grill-with-docs`. Issue tracker → `_QUESTOES_CRITICAS/` (`NN_TITULO.md`). Triage labels → 5 canônicos (`needs-triage`/`needs-info`/`ready-for-agent`/`ready-for-human`/`wontfix`).")
    db_counts = _query_db_counts()
    if db_counts["ok"]:
        L.append(f"- **`prodam.db`**: {db_counts['tables']}. Views: {db_counts['views']}.")
    else:
        L.append("- **`prodam.db`**: 8 tabelas (`spcf_contratos`, `spcf_empenhos`, `spcf_faturas`, `spcf_nfs`, `pendrive_docs`, `devedores`, `reclassificacao`, `cruzamento_spcf_pendrive`) + 5 views. Abrir sem código: `datasette serve PRODAM_DOCS\\_ANALISE\\prodam.db --open` ou Beekeeper Studio.")
    L.append("")

    return "\n".join(L) + "\n"


def generate_status_devedores(m):
    """STATUS_DEVEDORES.md — todos os 70 devedores ordenados por valor exigível.
    Colunas: sigla, exigível, atualizado, força, próximo_passo, dias_prescrição, fase."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    L = []
    L.append("# Status dos Devedores — PROJETO PRODAM")
    L.append(f"_Atualizado em {now} via `scripts/auto_update_claude_md.py`._")
    L.append("")
    L.append(f"**Total**: {m['total']} devedores · {fmt_brl(m['val_exig'])} exigível · {fmt_brl(m['val_atualizado'])} atualizado.")
    L.append("")
    L.append("Ordenação: valor exigível (descendente). Coluna **dias_presc** = dias até a próxima prescrição (vazio = sem data).")
    L.append("")
    L.append("| # | Sigla | Exigível | Atualizado | Força | Próximo passo | Dias presc. | Fase |")
    L.append("|---|-------|---------:|-----------:|-------|---------------|------------:|------|")
    for idx, (sigla, ve, fp, pp, d, dias, fase) in enumerate(m["all_items"], start=1):
        va = float(d.get("val_atualizado", 0) or 0)
        dias_txt = "—" if dias is None else (f"🔴 {dias}" if dias <= 30 else f"🟠 {dias}" if dias <= 60 else f"🟡 {dias}" if dias <= 90 else str(dias))
        # sanitiza pipes em texto (rara, mas defensivo)
        sigla_s = sigla.replace("|", "\\|")
        pp_s = (pp or "—").replace("|", "\\|")
        fase_s = (fase or "—").replace("|", "\\|")
        L.append(f"| {idx} | {sigla_s} | {fmt_brl(ve)} | {fmt_brl(va)} | {fp} | {pp_s} | {dias_txt} | {fase_s} |")
    L.append("")

    # Resumo por fase
    L.append("## Distribuição por fase atual")
    L.append("")
    L.append("| Fase | Devedores |")
    L.append("|------|----------:|")
    for fase, count in sorted(m["fase_counts"].items(), key=lambda x: -x[1]):
        L.append(f"| {fase} | {count} |")
    L.append("")

    return "\n".join(L) + "\n"


def generate_workflow_cobranca():
    """WORKFLOW_COBRANCA.md — pipeline end-to-end F0→F6. Hardcoded (não muda com dados)."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    L = []
    L.append("# Workflow de Cobrança — PROJETO PRODAM")
    L.append(f"_Pipeline end-to-end F0→F6. Atualizado em {now}._")
    L.append("")
    L.append("Cada devedor avança pelas fases abaixo. O campo `fase_atual` em `profiles.json` rastreia o ponto vigente; `historico_fases` registra a trajetória.")
    L.append("")

    L.append("## F0 — Triagem inicial")
    L.append("- **Objetivo**: identificar se o devedor está no portfólio e mapear documentação básica.")
    L.append("- **Skills**: `triage`, `decisao-documental-prodam` (cadeia 5 elos).")
    L.append("- **Gates documentais**: contrato vigente, CNPJ confirmado, categoria (Gov Direta/Indireta/Privada).")
    L.append("- **Prazo típico**: 1-3 dias.")
    L.append("- **Saída**: entrada em `profiles.json` com `categoria`, `forca_probatoria`, `score_composto` preliminar.")
    L.append("")

    L.append("## F1 — Análise documental")
    L.append("- **Objetivo**: validar cadeia Contrato + NE + NF + Atesto (REsp 793.969/RJ).")
    L.append("- **Skills**: `auditoria_completude_devedor`, `dossie_multiformato_devedor`.")
    L.append("- **Gates**: 11 itens do checklist; identificação de marcos interruptivos (empenhos = Art. 202 VI CC).")
    L.append("- **Prazo típico**: 5-10 dias por devedor.")
    L.append("- **Saída**: dossiê multi-formato (JSON + XLSX + CSV + MD + PDF).")
    L.append("")

    L.append("## F2 — Classificação e priorização")
    L.append("- **Objetivo**: definir `proximo_passo` e `prioridade_rank`.")
    L.append("- **Skills**: `classificacao-prodam`, score composto 12 dimensões.")
    L.append("- **Gates**: aprovação humana antes de mover devedor para F3+ (gate documental jurídico).")
    L.append("- **Prazo típico**: 1-2 dias.")
    L.append("- **Saída**: rank atualizado em `profiles.json`.")
    L.append("")

    L.append("## F3 — Notificação extrajudicial (TRD)")
    L.append("- **Objetivo**: emitir Termo de Reconhecimento de Dívida ou notificação extrajudicial.")
    L.append("- **Skills**: `protocolo-juridico-prodam`, `trd-gerador-prodam`.")
    L.append("- **Gates**: mostrar diff antes de salvar; revisão humana; envio com AR ou e-mail certificado.")
    L.append("- **Prazo típico**: 15-30 dias entre emissão e resposta esperada.")
    L.append("- **Saída**: documento `.docx` em `DOCUMENTOS_GERADOS/`, registro em `historico_fases`.")
    L.append("")

    L.append("## F4 — Negociação / Resposta")
    L.append("- **Objetivo**: acompanhar resposta do devedor (aceite, contraproposta, silêncio).")
    L.append("- **Skills**: `negociacao-prodam`.")
    L.append("- **Gates**: silêncio não interrompe prescrição (regra #2); registrar ato inequívoco se houver.")
    L.append("- **Prazo típico**: 30-60 dias.")
    L.append("- **Saída**: atualização de `ultima_interacao` e `evidencias_reconhecimento`.")
    L.append("")

    L.append("## F5 — Protocolo judicial / Execução")
    L.append("- **Objetivo**: ajuizar ação ou pedir habilitação de crédito.")
    L.append("- **Skills**: `peticao-inicial-prodam`, `habilitacao-credito-prodam`.")
    L.append("- **Gates**: Adm. Direta → precatório/RPV (Art. 100 CF); Adm. Indireta concorrencial → penhora direta (Tema 253/STF).")
    L.append("- **Prazo típico**: 60-180 dias para distribuição inicial.")
    L.append("- **Saída**: `data_protocolo` preenchida; `via_processual_recomendada` definida.")
    L.append("")

    L.append("## F6 — Recebimento / Encerramento")
    L.append("- **Objetivo**: confirmar pagamento, baixar do portfólio, calcular fee 20%.")
    L.append("- **Skills**: `controle-recebimento-prodam`.")
    L.append("- **Gates**: comprovante de depósito; cálculo de SELIC pós-trânsito; nota de honorários.")
    L.append("- **Prazo típico**: variável (precatório AM tem fila própria).")
    L.append("- **Saída**: `valor_recuperado` registrado; devedor marcado como encerrado.")
    L.append("")

    L.append("## Princípios transversais")
    L.append("- **Prescrição é por fatura individual** (regra #7). Cada fase recalcula faturas em risco.")
    L.append("- **PDFs nunca são apagados** — prova jurídica. Backup em `_BACKUPS/`.")
    L.append("- **`profiles.json` é SSOT** — qualquer fase atualiza apenas via PR ou edit auditado.")
    L.append("- **Fee 20% recuperado**, RPV/AM = 20 SM (Lei AM 2.748/2002).")
    L.append("")

    return "\n".join(L) + "\n"


def generate_playbook_orgaos():
    """PLAYBOOK_ORGAOS_V2.md — 13 passos validados no DETRAN A+ 94/100. Hardcoded."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    L = []
    L.append("# Playbook Replicável — Auditoria de Órgão (V2)")
    L.append(f"_13 passos validados no DETRAN/AM A+ 94/100. Atualizado em {now}._")
    L.append("")
    L.append("Use este playbook para auditar **qualquer novo órgão** do portfólio. Cada passo tem entrada, ferramenta e saída esperada. Score-alvo: A (≥85) — DETRAN atingiu 94 (A+).")
    L.append("")
    L.append("## Comando único (pipeline orquestrada)")
    L.append("```powershell")
    L.append("py -3.12 scripts\\orgao_pipeline_completa.py --orgao SEDUC")
    L.append("```")
    L.append("Esse script executa F1→F11 automaticamente. Os passos abaixo descrevem o que ele faz e o que validar manualmente.")
    L.append("")

    L.append("## Os 13 passos")
    L.append("")
    L.append("### Passo 1 — Localizar PDFs e organizar pastas")
    L.append("- **Entrada**: pasta `PRODAM_DOCS/<ORGAO>/` com PDFs originais.")
    L.append("- **Ferramenta**: organização manual ou `scripts/organizar_pdfs_orgao.py`.")
    L.append("- **Saída**: subpastas por tipo (CONTRATOS/, NES/, FATURAS/, NFs/, COBRANCAS/).")
    L.append("- **Critério**: nenhum PDF apagado; backup em `_BACKUPS/`.")
    L.append("")
    L.append("### Passo 2 — OCR completo dos PDFs")
    L.append("- **Entrada**: PDFs do passo 1.")
    L.append("- **Ferramenta**: `scripts/ocr_v4.py` (Tesseract + correção de layout).")
    L.append("- **Saída**: `.json` por PDF com texto + bounding boxes.")
    L.append("- **Critério**: ≥95% de páginas com texto extraído (verificar via `ocr_audit.py`).")
    L.append("")
    L.append("### Passo 3 — Ingestão no `prodam.db`")
    L.append("- **Entrada**: JSONs do passo 2.")
    L.append("- **Ferramenta**: `PRODAM_DOCS/build_sqlite.py` ou `scripts/atualizar_db.py`.")
    L.append("- **Saída**: registros em `spcf_contratos`, `spcf_empenhos`, `spcf_faturas`, `spcf_nfs`.")
    L.append("- **Critério**: contagens batem com o esperado por contrato.")
    L.append("")
    L.append("### Passo 4 — Normalização de contratos")
    L.append("- **Entrada**: 3 formatos coexistindo (`006/2021`, `6/2021`, `2021/006`).")
    L.append("- **Ferramenta**: `scripts/normalizador.py` (mapa contrato/ano → regime).")
    L.append("- **Saída**: coluna `contrato_normalizado` em todas as tabelas.")
    L.append("- **Critério**: zero contratos órfãos após reconciliação.")
    L.append("")
    L.append("### Passo 5 — Extração contratual cláusula-a-cláusula")
    L.append("- **Entrada**: contratos do passo 1.")
    L.append("- **Ferramenta**: `scripts/extracao_contratual.py`.")
    L.append("- **Saída**: JSON por contrato com cláusulas econômicas (índice, juros, multa, foro, prazos).")
    L.append("- **Critério**: índice de correção identificado (IGPM/IPCA/SELIC) por contrato.")
    L.append("")
    L.append("### Passo 6 — Reconciliação SPCF × Pendrive × DB")
    L.append("- **Entrada**: dados do passo 3 + pendrive (`pendrive_docs`).")
    L.append("- **Ferramenta**: `scripts/reconciliar_orfaos_reversos.py`.")
    L.append("- **Saída**: tabela `cruzamento_spcf_pendrive` + relatório de gaps.")
    L.append("- **Critério**: divergência <5% e gaps documentados.")
    L.append("")
    L.append("### Passo 7 — Cálculo de prescrição por fatura")
    L.append("- **Entrada**: `spcf_faturas` + vencimentos + marcos interruptivos.")
    L.append("- **Ferramenta**: `scripts/prescricao_por_fatura.py`.")
    L.append("- **Saída**: classificação `EXIGIVEL`/`PRESCRITA` por fatura + `data_prescricao_proxima` por devedor.")
    L.append("- **Critério**: regra Art. 202 VI CC aplicada (empenho interrompe; silêncio não).")
    L.append("")
    L.append("### Passo 8 — Atualização monetária")
    L.append("- **Entrada**: faturas exigíveis do passo 7.")
    L.append("- **Ferramenta**: `scripts/atualizacao_monetaria_bcb.py` (BCB live + Decimal).")
    L.append("- **Saída**: `val_atualizado` por devedor; índice aplicado (IGPM/IPCA/SELIC) conforme contrato.")
    L.append("- **Critério**: SELIC já inclui juros (não somar separado); IGPM = só correção.")
    L.append("")
    L.append("### Passo 9 — Score composto 12 dimensões")
    L.append("- **Entrada**: dados completos do devedor.")
    L.append("- **Ferramenta**: `scripts/score_composto.py`.")
    L.append("- **Saída**: `score_composto` (0-100) + classificação A+/A/A-/B+/B.")
    L.append("- **Critério**: cadeia documental 5 elos (15%), prescrição (15%), blindagem (10%), compliance (10%).")
    L.append("")
    L.append("### Passo 10 — Dossiê multi-formato")
    L.append("- **Entrada**: tudo dos passos 1-9.")
    L.append("- **Ferramenta**: `scripts/dossie_multiformato_devedor.py`.")
    L.append("- **Saída**: 5 formatos (JSON + XLSX + CSV + MD + PDF) em `DOSSIES/<ORGAO>/`.")
    L.append("- **Critério**: PDF assinável + JSON estruturado para LLM.")
    L.append("")
    L.append("### Passo 11 — Peça processual (TRD ou petição)")
    L.append("- **Entrada**: dossiê do passo 10.")
    L.append("- **Ferramenta**: `protocolo-juridico-prodam` (skill) + revisão humana.")
    L.append("- **Saída**: `.docx` em `DOCUMENTOS_GERADOS/<ORGAO>/`.")
    L.append("- **Critério**: diff revisado antes de salvar; sem alucinação de jurisprudência (consultar `PRECEDENTES_VERIFICADOS.md`).")
    L.append("")
    L.append("### Passo 12 — Blindagem pré-execução (22 itens)")
    L.append("- **Entrada**: peça do passo 11.")
    L.append("- **Ferramenta**: `scripts/blindagem_pre_execucao.py`.")
    L.append("- **Saída**: checklist 22 itens (legitimidade, competência, prescrição, título, índice, juros, multa, etc).")
    L.append("- **Critério**: 22/22 itens validados antes de protocolar.")
    L.append("")
    L.append("### Passo 13 — Atualização de `profiles.json` e commit")
    L.append("- **Entrada**: tudo dos passos anteriores.")
    L.append("- **Ferramenta**: edit manual ou `scripts/atualizar_profile.py --orgao <NOME>`.")
    L.append("- **Saída**: `profiles.json` atualizado + commit auditado.")
    L.append("- **Critério**: `_metadata.last_updated` atualizado; campos obrigatórios preenchidos; CI passa.")
    L.append("")

    L.append("## Benchmark DETRAN/AM (referência A+)")
    L.append("- **Score composto**: 94,0/100 → A+ (EXCEPCIONAL).")
    L.append("- **Pasta consolidada**: `Desktop\\DETRAN_AUDITORIA_COMPLETA\\` (3,2 GB, 8.210 arquivos).")
    L.append("- **Estrutura**: 13 pastas tipo × 14 formatos (PDF/JSON/CSV/MD/HTML/XLSX/DOCX/TXT/PY/JSONL/PNG/LOG).")
    L.append("- **Contratos ingeridos no DB**: 13 (12 PDFs + 1 vigente).")
    L.append("- **Índices mapeados**: IGPM (7 contratos) + IPCA (3 contratos).")
    L.append("- **Valor contratual total**: R$ 244,46M | Exigível: R$ 31,7M.")
    L.append("")
    L.append("### Distribuição DETRAN por formato")
    L.append("| Formato | Arquivos | Uso |")
    L.append("|---------|---------:|-----|")
    L.append("| PDF | 3.631 | Documentos originais (contratos, NEs, faturas, cobranças) |")
    L.append("| JSON | 1.698 | Textos extraídos + campos estruturados p/ LLM |")
    L.append("| HTML | 1.428 | Scraping SPCF + dashboards |")
    L.append("| CSV | 861 | Dados tabulares (prescrição, inadimplentes, pagamentos) |")
    L.append("| MD | 222 | Relatórios + documentação |")
    L.append("| TXT | 209 | Texto bruto + logs |")
    L.append("| XLSX | 90 | Planilhas auditoria |")
    L.append("| PY | 34 | Scripts reutilizáveis |")
    L.append("| DOCX | 17 | Cartas + minutas |")
    L.append("| JSONL | 8 | Corpora RAG/LLM |")
    L.append("")

    L.append("## Score composto — 12 dimensões (peso%)")
    L.append("1. Integridade de Dados (10%)")
    L.append("2. Cadeia Documental 5 elos (15%) — REsp 793.969/RJ")
    L.append("3. Prescrição & Marcos Interruptivos (15%) — Art. 202 VI CC")
    L.append("4. Blindagem Pré-Execução (10%) — 22/22 itens")
    L.append("5. Compliance Jurídico (10%) — regime/índice/título/modelo")
    L.append("6. Evidências Documentais (8%)")
    L.append("7. Reconhecimento Tácito (8%) — Art. 202 VI CC (empenhos)")
    L.append("8. Atualização Monetária (6%) — IGPM/IPCA/SELIC via BCB")
    L.append("9. Priorização (6%)")
    L.append("10. Risco Processual (5%) — p_recuperação")
    L.append("11. Valor Recuperável E[V] (4%)")
    L.append("12. Urgência/Prazo (3%)")
    L.append("")
    L.append("**Classificação**: A+ ≥90 · A ≥85 · A- ≥80 · B+ ≥75 · B ≥70.")
    L.append("")

    return "\n".join(L) + "\n"


def main():
    if not PROFILES.exists():
        print(f"ERRO: {PROFILES} nao encontrado")
        return

    n_skills = generate_skills_index()
    if n_skills:
        print(f"INDEX.md atualizado: {SKILLS_INDEX} ({n_skills} skills)")

    data = load_profiles()
    m = compute_metrics(data)

    # 4 .md (INDEX.md ja escrito acima por generate_skills_index, se houver skills)
    OUTPUT.write_text(generate_claude_md(m), encoding="utf-8")
    print(f"CLAUDE.md atualizado: {OUTPUT}")

    OUTPUT_STATUS.write_text(generate_status_devedores(m), encoding="utf-8")
    print(f"STATUS_DEVEDORES.md atualizado: {OUTPUT_STATUS}")

    OUTPUT_WORKFLOW.write_text(generate_workflow_cobranca(), encoding="utf-8")
    print(f"WORKFLOW_COBRANCA.md atualizado: {OUTPUT_WORKFLOW}")

    OUTPUT_PLAYBOOK.write_text(generate_playbook_orgaos(), encoding="utf-8")
    print(f"PLAYBOOK_ORGAOS_V2.md atualizado: {OUTPUT_PLAYBOOK}")

    if m["prescricao_urgente"]:
        print(f"  [ALERTA] {len(m['prescricao_urgente'])} devedor(es) com prescricao urgente (<90 dias)")


if __name__ == "__main__":
    main()
