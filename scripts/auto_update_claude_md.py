#!/usr/bin/env python3
"""
Auto-update CLAUDE.md (raiz) + 3 satélites + índice de skills a partir de profiles.json + prodam.db.

Gera 4 arquivos .md (+ INDEX.md quando há skills em _SKILLS/):
  1. CLAUDE.md                — root enxuto: NUNCA + regras (13) + métricas vivas
  2. STATUS_DEVEDORES.md      — todos os 69 devedores + prescrições vencidas + DB vivo
  3. WORKFLOW_COBRANCA.md     — pipeline end-to-end F0→F6
  4. PLAYBOOK_ORGAOS_V2.md    — 13 passos validados no DETRAN A+ 94/100

Refatorado em 2026-06-09 (auditoria de engenharia de contexto):
  - validate_profiles() fail-fast: nada é escrito se a fonte estiver quebrada (exit 1)
  - Decimal em todas as somas (NUNCA-2 / ex-Regra 16) via prodam_utils.brl
  - Alertas passam a EXPOR datas de prescrição vencidas/stale (antes o filtro
    0<dias<=90 as escondia em silêncio — risco de multa contratual de 10%)
  - 18 regras → bloco NUNCA (8) + 13 regras renumeradas, sem perda nominal
    (rastreabilidade: _AUDITORIA_CLAUDE_MD/FASE3_DIAGNOSTICO_2026-06-09.md)

Rodar:
  py -3.12 scripts\\auto_update_claude_md.py
"""
import json
import re
import sqlite3
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
OUTPUT_STATUS = BASE / "STATUS_DEVEDORES.md"
OUTPUT_WORKFLOW = BASE / "WORKFLOW_COBRANCA.md"
OUTPUT_PLAYBOOK = BASE / "PLAYBOOK_ORGAOS_V2.md"

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prodam_utils import fmt_brl, brl  # SSOT (NUNCA-2 / ex-Regra 16, Issue 11 Cat A)


def load_profiles():
    with open(PROFILES, "r", encoding="utf-8") as f:
        return json.load(f)


class ProfilesInvalidos(ValueError):
    """profiles.json estruturalmente quebrado — nada deve ser escrito."""


def validate_profiles(data):
    """Fail-fast ANTES de escrever qualquer .md (espelha a validação do CI).

    Sem isto, um profiles.json truncado/corrompido geraria CLAUDE.md lixo em
    silêncio e o /sincronizar-prodam reportaria sucesso.
    """
    if not isinstance(data, dict):
        raise ProfilesInvalidos("profiles.json não é um objeto JSON (dict)")
    if "_metadata" not in data:
        raise ProfilesInvalidos("chave _metadata ausente")
    devedores = {k: v for k, v in data.items() if not k.startswith("_")}
    if len(devedores) < 50:
        raise ProfilesInvalidos(
            f"apenas {len(devedores)} devedores (<50) — fonte truncada?")
    nao_dict = [k for k, v in devedores.items() if not isinstance(v, dict)][:5]
    if nao_dict:
        raise ProfilesInvalidos(f"perfis que não são dict: {nao_dict}")
    soma = sum((brl(d.get("val_exig")) for d in devedores.values()), Decimal(0))
    if soma <= 0:
        raise ProfilesInvalidos("soma de val_exig <= 0 — fonte corrompida?")
    return True


def _count_ref_juridica_dirs():
    """Conta subpastas de REFERENCIA_JURIDICA no disco (ex-'20 subpastas'
    hardcoded — em 2026-06-09 o disco tinha 18; contagem agora é dinâmica)."""
    ref = BASE / "PRODAM_DOCS" / "REFERENCIA_JURIDICA"
    if not ref.exists():
        return None
    try:
        return sum(1 for p in ref.iterdir() if p.is_dir())
    except OSError:
        return None


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
    # _metadata (e qualquer chave _*) não é devedor — excluir da contagem e dos
    # agregados (senão `total` vira 69+1=70 e injeta um fantasma "N/A" nas categorias).
    data = {k: v for k, v in data.items() if not k.startswith("_")}
    m = {
        "total": len(data),
        "val_exig": Decimal(0), "val_orig": Decimal(0), "val_atualizado": Decimal(0),
        "n_val_atualizado": 0,  # quantos devedores têm val_atualizado preenchido
        "faturas_total": 0, "faturas_exig": 0, "faturas_presc": 0,
        "categorias": {}, "forcas": {}, "proximos": {},
        "top10": [],
        "prescricao_urgente": [],   # 0 < dias <= 90 (futuras)
        "prescricao_vencida": [],   # dias <= 0 — data no passado/stale: EXPOR, nunca esconder
        "prescricao_vencida_protegida": [],  # idem, mas urgencia=PROTEGIDA_ART202_VI (marcos prevalecem)
        "prescricao_sem_data": [],  # campo ausente/null ou não parseável (ex.: 'N/A')
        "faturas_gap": [],          # conciliação: devedores com total ≠ exigíveis + prescritas
        "faturas_gap_total": 0,
        "fase_counts": {},
        "all_items": [],
    }
    items = []
    for sigla, d in data.items():
        # Somas em Decimal (NUNCA-2): brl() aceita None/str/num e devolve Decimal.
        ve = brl(d.get("val_exig"))
        vo = brl(d.get("val_orig"))
        va_raw = d.get("val_atualizado")
        va = brl(va_raw)
        if va_raw not in (None, ""):
            m["n_val_atualizado"] += 1
        m["val_exig"] += ve
        m["val_orig"] += vo
        m["val_atualizado"] += va
        ft = int(d.get("faturas_total", 0) or 0)
        fe = int(d.get("faturas_exigiveis", 0) or 0)
        fp_n = int(d.get("faturas_prescritas", 0) or 0)
        m["faturas_total"] += ft
        m["faturas_exig"] += fe
        m["faturas_presc"] += fp_n
        # Conciliação (2026-06-09): gap = faturas nem exigíveis nem prescritas
        # (canceladas/excluídas do universo) — era invisível e fazia 3477≠2326+1082.
        gap = ft - fe - fp_n
        if gap > 0:
            m["faturas_gap"].append((sigla, ft, fe, fp_n, gap))
            m["faturas_gap_total"] += gap

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

        # Dias até prescrição. Três destinos possíveis — nenhum é descartado:
        # urgente (futura <90d), vencida (passado/stale) ou sem_data.
        # Antes de 2026-06-09 o filtro era `0 < dias <= 90` e datas vencidas
        # sumiam em silêncio (22 devedores com 2026-03-20, incl. SEDUC R$49M).
        dias_presc = None
        dp = d.get("data_prescricao_proxima")
        if dp:
            try:
                dt = datetime.strptime(dp, "%Y-%m-%d").date()
                dias_presc = (dt - date.today()).days
                if 0 < dias_presc <= 90:
                    m["prescricao_urgente"].append((sigla, dp, dias_presc, ve))
                elif dias_presc <= 0:
                    # PROTEGIDA_ART202_VI: marco interruptivo registrado prevalece —
                    # não é risco 🔥, é data a reconfirmar (linha 🛡️ própria).
                    if (d.get("urgencia_prescricao") or "") == "PROTEGIDA_ART202_VI":
                        m["prescricao_vencida_protegida"].append((sigla, dp, dias_presc, ve))
                    else:
                        m["prescricao_vencida"].append((sigla, dp, dias_presc, ve))
            except (ValueError, TypeError):
                m["prescricao_sem_data"].append((sigla, str(dp)))
        else:
            m["prescricao_sem_data"].append((sigla, "—"))

        items.append((sigla, ve, fp, pp_short, d, dias_presc, fase))

    # sort estável e determinístico (idempotência): valor desc, sigla como desempate
    items.sort(key=lambda x: (-x[1], x[0]))
    m["top10"] = items[:10]
    m["all_items"] = items
    m["prescricao_urgente"].sort(key=lambda x: (x[2], x[0]))
    m["prescricao_vencida"].sort(key=lambda x: (-x[3], x[0]))  # maior exigível primeiro
    m["prescricao_vencida_protegida"].sort(key=lambda x: (-x[3], x[0]))
    m["prescricao_sem_data"].sort(key=lambda x: x[0])
    m["faturas_gap"].sort(key=lambda x: (-x[4], x[0]))
    return m


TOP_N = 5  # top-N do CLAUDE.md (lista completa fica no STATUS_DEVEDORES.md)


def generate_claude_md(m):
    """CLAUDE.md raiz enxuto.

    Seções 0-10: NUNCA (vedações), identidade, status, alertas de prescrição
    (futuras <90d + vencidas/stale + sem data), link workflow, 13 regras jurídicas,
    hierarquia de fontes, convenções técnicas, mapas, comandos, skills/DB.
    Fatos jurídicos verdadeiros (REsp 793.969/José Delgado, RPV/AM Lei 2.748/2002,
    FUHAM≠FHAJ, fee 20%) como conhecimento neutro — sem camada de safeguard."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    L = []

    # ============ CABEÇALHO ============
    L.append("# PROJETO PRODAM — Recuperação de Créditos")
    L.append("## Contrato 002/2026 — PRODAM S.A. × Brandão Ozores Advogados")
    L.append(f"_Atualizado em {now} via `scripts/auto_update_claude_md.py`._")
    L.append("")
    L.append("> Conteúdo regenerado a cada `/sincronizar-prodam`. Para regras fixas → editar o gerador. Para métricas → editar `PRODAM_DOCS/profiles.json` e rodar `py -3.12 scripts\\auto_update_claude_md.py`.")
    L.append("")

    # ============ 0. NUNCA (vedações de maior dano) ============
    # Consolidação 2026-06-09: vedações antes diluídas nas ex-Regras 4/8/15/16 e §7.
    # Item 8 (ANTHROPIC_API_KEY): env var ativa faz o Claude Code cobrar na API do
    # Console em vez do plano de assinatura — prejuízo real de ~US$100 já ocorrido.
    L.append("## 0. NUNCA (vedações — maior dano primeiro)")
    L.append("1. **Nunca apagar/mover/sobrescrever PDF** — prova jurídica (hook `block_pdf_delete.ps1` ativo; backups em `_BACKUPS/`).")
    L.append("2. **Nunca `float` em valores BRL** — `Decimal` sempre; formatar via `prodam_utils.fmt_brl` (`R$ 1.234,56`).")
    L.append("3. **Nunca citar lei/jurisprudência fora do catálogo verificado** (Regra 13).")
    L.append("4. **Nunca criar `config_prodam.py`/`normalizador.py`** sem auditoria prévia — não existem em código ativo.")
    L.append("5. **Nunca executar comandos de dentro de `_LIXO_NAO_USAR\\_ARCHIVE`** — antes de qualquer prompt no terminal: `cd C:\\Users\\gabri`.")
    L.append("6. **Nunca usar o Demonstrativo Excel como fonte de valores** — a SSOT é `PRODAM_DOCS/profiles.json`.")
    L.append("7. **Nunca inverter FUHAM × FHAJ** — FUHAM = Fundação Alfredo da Matta; FHAJ = Fundação Hospital Adriano Jorge.")
    L.append("8. **Antes de rodar Claude Code no terminal**: `Test-Path Env:ANTHROPIC_API_KEY` deve retornar `False` — a env var ativa cobra a API do Console em vez do plano.")
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
    L.append(f"- **{fmt_brl(m['val_exig'])} exigível** | {fmt_brl(m['val_atualizado'])} atualizado ({m['n_val_atualizado']}/{m['total']} com valor atualizado)")
    gap_txt = (f", {m['faturas_gap_total']} fora do universo exig./presc. — canceladas/excluídas, ver STATUS"
               if m["faturas_gap_total"] else "")
    L.append(f"- **{m['faturas_total']} faturas** ({m['faturas_exig']} exigíveis, {m['faturas_presc']} prescritas{gap_txt})")
    L.append(f"- **Força**: {m['forcas'].get('FORTE',0)} FORTE · {m['forcas'].get('MÉDIA',0)} MÉDIA · {m['forcas'].get('FRACA',0)} FRACA")
    L.append("")
    # tie-break por nome garante output idêntico entre execuções (idempotência)
    L.append("**Pipeline (próximo passo)**: " + " · ".join(f"{pp}={c}" for pp, c in sorted(m["proximos"].items(), key=lambda x: (-x[1], x[0]))))
    L.append("")
    L.append(f"**Top {TOP_N} devedores** (por valor exigível):")
    for sigla, ve, fp, pp, d, _dias, _fase in m["top10"][:TOP_N]:
        L.append(f"- {sigla}: {fmt_brl(ve)} | {fp} | {pp}")
    L.append("")
    L.append(f"→ Lista completa dos {m['total']} devedores: [`STATUS_DEVEDORES.md`](STATUS_DEVEDORES.md).")
    L.append("")

    # ============ 3. ALERTAS DE PRESCRIÇÃO ============
    # Três grupos, nenhum oculto (correção 2026-06-09 — antes datas vencidas sumiam):
    #   🔴🟠🟡 futuras <90d · 🔥 vencidas/stale (agregado; nominal no STATUS) · sem data.
    # Cautela jurídica: data no passado NÃO significa prescrição consumada — pode haver
    # marco interruptivo não registrado (Art. 202 VI CC) ou data stale por recalcular.
    L.append("## 3. ALERTAS DE PRESCRIÇÃO")
    if m["prescricao_urgente"]:
        for sigla, dp, dias, ve in m["prescricao_urgente"]:
            emoji = "🔴" if dias <= 30 else "🟠" if dias <= 60 else "🟡"
            L.append(f"- {emoji} **{sigla}**: {dp} ({dias} dias) — {fmt_brl(ve)}")
    else:
        L.append("- _(nenhuma prescrição futura em até 90 dias na varredura atual)_")
    if m["prescricao_vencida"]:
        tot_venc = sum((ve for _s, _dp, _di, ve in m["prescricao_vencida"]), Decimal(0))
        pior_sigla, _dp, _di, pior_ve = m["prescricao_vencida"][0]
        L.append(f"- 🔥 **{len(m['prescricao_vencida'])} devedores com data de prescrição no PASSADO/stale** (Σ exigível {fmt_brl(tot_venc)}; maior: {pior_sigla} {fmt_brl(pior_ve)}) — recalcular a data e conferir marcos interruptivos (Art. 202 VI CC) antes de tratar como perdida. Lista nominal: [`STATUS_DEVEDORES.md`](STATUS_DEVEDORES.md).")
    if m["prescricao_vencida_protegida"]:
        sig_p = " · ".join(s for s, _dp, _di, _ve in m["prescricao_vencida_protegida"])
        L.append(f"- 🛡️ **{len(m['prescricao_vencida_protegida'])} protegido(s) por marco interruptivo (Art. 202 VI CC)** com data registrada no passado — marco prevalece; reconfirmar e atualizar a data: {sig_p}.")
    if m["prescricao_sem_data"]:
        L.append(f"- _({len(m['prescricao_sem_data'])} devedores sem data de prescrição registrada — nomes no [`STATUS_DEVEDORES.md`](STATUS_DEVEDORES.md))_")
    L.append("")

    # ============ 4. WORKFLOW (link) ============
    L.append("## 4. WORKFLOW DE COBRANÇA")
    L.append("Pipeline end-to-end F0→F6 (skills, gates documentais, prazos): [`WORKFLOW_COBRANCA.md`](WORKFLOW_COBRANCA.md).")
    L.append("")

    # ============ 5. REGRAS JURÍDICAS (fatos neutros — sem camada de safeguard) ============
    # Renumeração 2026-06-09 (18 → 13; rastreabilidade completa em
    # _AUDITORIA_CLAUDE_MD/FASE3_DIAGNOSTICO_2026-06-09.md):
    #   ex-4 → R10 enxuta + NUNCA-4. Histórico da ex-4 preservado AQUI (fora do output):
    #     config_prodam.py e scripts/normalizador.py NÃO existem em código ativo
    #     (verificado 2026-06-08/09); correção SELIC live (BCB SGS 4390) implementada em
    #     scripts/ad_hoc/gerar_memorial_preliminar_ses.py; valores absolutos (SM vigente,
    #     teto RPV, custas) ficam inline nos scripts de cálculo, nunca no CLAUDE.md.
    #   ex-6 + ex-9 → R4 (marcos interruptivos, um assunto só).
    #   ex-8 → NUNCA-7 · ex-15 → NUNCA-6 · ex-16 → NUNCA-2.
    #   ex-14 dividida: fee 20% vive só na Seção 1; RPV vira R12.
    #     Lei AM 2.748/2002 CONFIRMADA em fonte oficial (ALEAM/SAPL + Legisla.AM,
    #     2026-06-09): pequeno valor = 20 SM perante a Fazenda ESTADUAL
    #     (15 SM Manaus; 10 SM demais municípios). A citação "Lei 3.683/2012" é
    #     armadilha conhecida (errada) — por isso a ressalva na R12.
    #   ex-17 + ex-18 → R13, com path CORRIGIDO: o catálogo fica em
    #     REFERENCIA_JURIDICA/11_PESQUISAS_ORIGINAIS/ (a ex-17 apontava para a raiz).
    L.append("## 5. REGRAS JURÍDICAS")
    # 2026-06-09: "revogou"→"sucedeu" — o teor oficial (REFERENCIA_JURIDICA/16_AUXILIAR/
    # DECRETO_53464_2026_TEOR_LEGISLA_AM.md) não tem cláusula revogatória expressa; o
    # 51.084/2025 teve efeitos exauridos em 2025 e o §5º do 53.464 preserva suas reduções.
    L.append("1. **Decreto Estadual AM nº 53.464/2026** (sucedeu o 51.084/2025, de efeitos exauridos em 2025) — verificar as 4 exceções (art. 1º §§1º-4º) antes de qualquer ação contra Gov AM; teor em `REFERENCIA_JURIDICA/16_AUXILIAR/`.")
    L.append("2. Prescrição é por **fatura individual** (Art. 189 + 206 §5º I CC), contada do **vencimento**.")
    L.append("3. Silêncio do devedor **não** interrompe prescrição — exige ato inequívoco (Art. 202 CC, rol taxativo).")
    L.append("4. Marcos interruptivos: **empenho (NE) = reconhecimento tácito** (Art. 202 VI CC) e interrompe; **NF emitida pelo credor não interrompe** (exige ato do devedor).")
    L.append("5. Interrupção ocorre **uma vez** (unicidade — REsp 1.963.067/MS); contra a Fazenda Pública o prazo reinicia **pela metade** (Decreto 20.910/1932 = 2,5 anos).")
    L.append("6. **Tema 1.109/STJ**: gestor público não renuncia tacitamente a prescrição.")
    L.append("7. Composição documental (Contrato + NE + NF + Atesto) = título executivo (**REsp 793.969/RJ**, Rel. p/ acórdão **Min. José Delgado**; Min. Teori Zavascki foi vencido).")
    L.append("8. Juros pós-**Lei 14.905/2024** — não presumir 1% a.m.; verificar arts. 404-406 CC.")
    L.append("9. SELIC já inclui correção + juros — não somar separado. IGPM = só correção (juros à parte).")
    L.append("10. **Índice de correção**: confirmar na **cláusula econômica do contrato** do devedor (SELIC/IGPM/IPCA); SELIC live via BCB (série SGS 4390). Não há arquivo-SSOT de índices (ver NUNCA-4).")
    L.append("11. Adm. Direta → precatório/RPV (Art. 100 CF) | Adm. Indireta concorrencial → penhora direta (Tema 253/STF).")
    L.append("12. **RPV/AM = 20 × SM vigente** (Lei AM 2.748/2002; a Lei 3.683/2012 é citação errada) — 60 SM é o teto **federal**, não aplicar contra o Estado.")
    L.append("13. Jurisprudência: citar **só** o catálogo `PRODAM_DOCS/REFERENCIA_JURIDICA/11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md` (3 fabricados + 6 distorcidos catalogados); antes de emitir opinião jurídica, consultar `REFERENCIA_JURIDICA/` na ordem da Seção 6.")
    L.append("")

    # ============ 6. HIERARQUIA DE FONTES JURÍDICAS ============
    L.append("## 6. HIERARQUIA DE FONTES JURÍDICAS (consultar nessa ordem)")
    L.append("1. **Nota Metodológica** (`PRODAM_DOCS/REFERENCIA_JURIDICA/01_NOTA_METODOLOGICA/`) — corrige todos os demais.")
    L.append("2. **Estudo Consolidado** (002/2026) — adaptado ao contrato atual.")
    L.append("3. **Estudo Exaustivo** — matriz genérica com minutas.")
    L.append("4. **Pesquisa Jurisprudencial** — STJ/STF/TJAM (só precedentes verificados).")
    L.append("5. **Extração Contratual** — cláusula a cláusula dos contratos dos devedores.")
    n_ref = _count_ref_juridica_dirs()
    ref_txt = f"({n_ref} subpastas)" if n_ref else "(subpastas numeradas)"
    L.append(f"6. `PRODAM_DOCS/REFERENCIA_JURIDICA/` {ref_txt} — SSOT jurídica do projeto.")
    L.append("")

    # ============ 7. CONVENÇÕES TÉCNICAS ============
    # 2026-06-09: removida a referência a `_ARQUIVO_DRIFT/` (pasta NÃO existe no disco;
    # única canônica é `_BACKUPS/`). Vedações de PDF/float migraram para NUNCA-1/2.
    L.append("## 7. CONVENÇÕES TÉCNICAS")
    L.append("- **Plataforma**: Windows + PowerShell. Python via `py -3.12` (sem venv). Bash não é usado.")
    L.append("- **BRL**: formatar via `prodam_utils.fmt_brl`; parse via `prodam_utils.brl` (vedação de float: NUNCA-2).")
    L.append("- **CSV**: separador `;` + encoding `utf-8-sig` (BOM) — abre direto no Excel.")
    L.append("- **Salvar extrações** em **JSON + XLSX + CSV** no mesmo script. JSON é SSOT; XLSX/CSV são derivados.")
    L.append("- **Arquivamento**: backups e quarentenas do projeto em `_BACKUPS/` (única pasta canônica). Acervo morto fica em `Desktop\\_LIXO_NAO_USAR\\_ARCHIVE` — só listar, nunca operar lá (NUNCA-5).")
    L.append("- **SPCF**: `time.sleep(1.5)` entre requisições (rate limit obrigatório).")
    L.append("- **Contratos** têm 3 formatos coexistindo (`006/2021` em `spcf_contratos`, `6/2021` em `profiles.json`, `2021/006` em outras fontes) — normalizar antes de JOIN.")
    L.append("- **Testes**: `py -3.12 -m pytest tests\\ -v`. CI (`.github/workflows/tests.yml`) valida `profiles.json` (≥50 devedores/CNPJ/`_metadata`).")
    L.append("- **Proteções do repo** (não desativar sem motivo): hook `.claude/hooks/block_pdf_delete.ps1` (bloqueia remoção de `*.pdf` via shell; não cobre o Explorer) · `.pre-commit-config.yaml` (`ruff-check` E9/F63/F7/F82 em `scripts/`) · `.gitignore` (mantém `PRODAM_DOCS/`, `*.pdf`, `*.db` e segredos fora do repo).")
    L.append("")

    # ============ 8. MAPAS DO PROJETO ============
    L.append("## 8. MAPAS DO PROJETO")
    L.append("| Caminho | O que cobre |")
    L.append("|---------|-------------|")
    L.append(f"| `PRODAM_DOCS/profiles.json` | **SSOT** dos {m['total']} devedores (privado, fora do repo) |")
    L.append("| `PRODAM_DOCS/_ANALISE/prodam.db` | DB canônico (gerado por `PRODAM_DOCS/build_sqlite.py`) |")
    L.append("| `prodam.db` (raiz) | Cópia derivada usada por `scripts/consultas.py` |")
    L.append("| `PRODAM_DOCS/REFERENCIA_JURIDICA/` | Base jurídica — consultar antes de qualquer parecer (Regra 13) |")
    L.append("| `PRODAM_DOCS/_SKILLS/` | Skills jurídicas curadas |")
    L.append("| `SPCF_EXTRACAO/` | Web scraping SPCF (rate-limit obrigatório) |")
    L.append("| `scripts/` | Pipelines, consultas, dossiês, sincronização |")
    L.append(f"| `STATUS_DEVEDORES.md` | Lista completa dos {m['total']} devedores |")
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
    # 2026-06-09: contagens vivas do DB saíram daqui (métrica, não instrução) e
    # moram no STATUS_DEVEDORES.md — economiza contexto em TODA conversa.
    L.append("- **`prodam.db`**: 8 tabelas + 5 views — contagens vivas em [`STATUS_DEVEDORES.md`](STATUS_DEVEDORES.md). Abrir sem código: `datasette serve PRODAM_DOCS\\_ANALISE\\prodam.db --open` ou Beekeeper Studio.")
    L.append("")

    return "\n".join(L) + "\n"


def generate_status_devedores(m):
    """STATUS_DEVEDORES.md — todos os 69 devedores ordenados por valor exigível,
    + prescrições vencidas/stale (nominal), devedores sem data, contagens vivas do DB.
    Colunas: sigla, exigível, atualizado, força, próximo_passo, dias_prescrição, fase."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    L = []
    L.append("# Status dos Devedores — PROJETO PRODAM")
    L.append(f"_Atualizado em {now} via `scripts/auto_update_claude_md.py`._")
    L.append("")
    L.append(f"**Total**: {m['total']} devedores · {fmt_brl(m['val_exig'])} exigível · {fmt_brl(m['val_atualizado'])} atualizado ({m['n_val_atualizado']}/{m['total']} com valor atualizado).")
    L.append("")
    L.append("Ordenação: valor exigível (descendente). Coluna **dias_presc** = dias até a próxima prescrição (🔥 = data no passado/stale; — = sem data).")
    L.append("")
    L.append("| # | Sigla | Exigível | Atualizado | Força | Próximo passo | Dias presc. | Fase |")
    L.append("|---|-------|---------:|-----------:|-------|---------------|------------:|------|")
    for idx, (sigla, ve, fp, pp, d, dias, fase) in enumerate(m["all_items"], start=1):
        va = brl(d.get("val_atualizado"))
        dias_txt = "—" if dias is None else (f"🔥 {dias}" if dias <= 0 else f"🔴 {dias}" if dias <= 30 else f"🟠 {dias}" if dias <= 60 else f"🟡 {dias}" if dias <= 90 else str(dias))
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
    for fase, count in sorted(m["fase_counts"].items(), key=lambda x: (-x[1], x[0])):
        L.append(f"| {fase} | {count} |")
    L.append("")

    # ====== Prescrições vencidas/stale — lista nominal (CLAUDE.md §3 traz o agregado) ======
    if m["prescricao_vencida"]:
        tot_venc = sum((ve for _s, _dp, _di, ve in m["prescricao_vencida"]), Decimal(0))
        L.append("## 🔥 Prescrições com data no PASSADO/stale — recalcular")
        L.append("")
        L.append(f"{len(m['prescricao_vencida'])} devedores · Σ exigível {fmt_brl(tot_venc)}. "
                 "Data vencida **não** significa prescrição consumada: pode haver marco interruptivo "
                 "não registrado (Art. 202 VI CC) ou data stale. Recalcular e atualizar `profiles.json`.")
        L.append("")
        L.append("| Sigla | Data registrada | Dias | Exigível |")
        L.append("|-------|-----------------|-----:|---------:|")
        for sigla, dp, dias, ve in m["prescricao_vencida"]:
            L.append(f"| {sigla.replace('|', chr(92) + '|')} | {dp} | {dias} | {fmt_brl(ve)} |")
        L.append("")

    if m["prescricao_vencida_protegida"]:
        L.append("## 🛡️ Protegidos por marco interruptivo (Art. 202 VI CC) — data a reconfirmar")
        L.append("")
        L.append("Marco registrado prevalece sobre a data abaixo (não é risco 🔥); atualizar `data_prescricao_proxima` quando o marco for revisado.")
        L.append("")
        L.append("| Sigla | Data registrada | Dias | Exigível |")
        L.append("|-------|-----------------|-----:|---------:|")
        for sigla, dp, dias, ve in m["prescricao_vencida_protegida"]:
            L.append(f"| {sigla} | {dp} | {dias} | {fmt_brl(ve)} |")
        L.append("")

    if m["prescricao_sem_data"]:
        L.append("## Devedores sem data de prescrição registrada")
        L.append("")
        nomes = " · ".join(f"{s}" + (f" (`{raw}`)" if raw != "—" else "") for s, raw in m["prescricao_sem_data"])
        L.append(f"{len(m['prescricao_sem_data'])} devedores: {nomes}.")
        L.append("")

    # ====== Conciliação de faturas (2026-06-09): explica o gap 3477 ≠ 2326+1082 ======
    if m["faturas_gap"]:
        L.append("## Conciliação de faturas (total ≠ exigíveis + prescritas)")
        L.append("")
        L.append(f"{m['faturas_gap_total']} faturas fora do universo exigível/prescrito — canceladas/excluídas "
                 "do universo de cobrança (ex.: SES/SUSAM tem 29 exclusões documentadas em "
                 "`faturas_exigiveis_breakdown` + canceladas SPCF). Itemização fatura a fatura pendente "
                 "(fonte: CSVs cruzados por devedor).")
        L.append("")
        L.append("| Sigla | Total | Exigíveis | Prescritas | Fora do universo |")
        L.append("|-------|------:|----------:|-----------:|-----------------:|")
        for sigla, ft, fe, fp_n, gap in m["faturas_gap"]:
            L.append(f"| {sigla} | {ft} | {fe} | {fp_n} | {gap} |")
        L.append("")

    # ====== Contagens vivas do prodam.db (migradas do CLAUDE.md §10 em 2026-06-09) ======
    db_counts = _query_db_counts()
    L.append("## prodam.db — contagens vivas")
    L.append("")
    if db_counts["ok"]:
        L.append(f"Tabelas: {db_counts['tables']}.")
        L.append("")
        L.append(f"Views: {db_counts['views']}.")
    else:
        L.append(f"_(DB indisponível nesta geração: {db_counts['reason']})_")
    L.append("")

    return "\n".join(L) + "\n"


def generate_workflow_cobranca():
    """WORKFLOW_COBRANCA.md — pipeline end-to-end F0→F6. Hardcoded (não muda com dados).

    2026-06-09: skills citadas passaram a ser SÓ as que existem em PRODAM_DOCS/_SKILLS/
    (antes citava trd-gerador-prodam, negociacao-prodam, peticao-inicial-prodam,
    habilitacao-credito-prodam, controle-recebimento-prodam, classificacao-prodam e
    decisao-documental-prodam — nenhuma existia). Refs de regra renumeradas (18→13)."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    L = []
    L.append("# Workflow de Cobrança — PROJETO PRODAM")
    L.append(f"_Pipeline end-to-end F0→F6. Atualizado em {now}._")
    L.append("")
    L.append("Cada devedor avança pelas fases abaixo. O campo `fase_atual` em `profiles.json` rastreia o ponto vigente; `historico_fases` registra a trajetória.")
    L.append("")

    L.append("## F0 — Triagem inicial")
    L.append("- **Objetivo**: identificar se o devedor está no portfólio e mapear documentação básica.")
    L.append("- **Skills**: `triage` (agent skill) · `classificacao-forca-probatoria` · `validador-cadeia-documental-fatura` (cadeia 5 elos).")
    L.append("- **Gates documentais**: contrato vigente, CNPJ confirmado, categoria (Gov Direta/Indireta/Privada).")
    L.append("- **Prazo típico**: 1-3 dias.")
    L.append("- **Saída**: entrada em `profiles.json` com `categoria`, `forca_probatoria`, `score_composto` preliminar.")
    L.append("")

    L.append("## F1 — Análise documental")
    L.append("- **Objetivo**: validar cadeia Contrato + NE + NF + Atesto (REsp 793.969/RJ).")
    L.append("- **Ferramentas**: `scripts/auditoria_completude_devedor.py`, `scripts/dossie_multiformato_devedor.py` + skill `auditoria-completude-devedor`.")
    L.append("- **Gates**: 11 itens do checklist; identificação de marcos interruptivos (empenhos = Art. 202 VI CC).")
    L.append("- **Prazo típico**: 5-10 dias por devedor.")
    L.append("- **Saída**: dossiê multi-formato (JSON + XLSX + CSV + MD + PDF).")
    L.append("")

    L.append("## F2 — Classificação e priorização")
    L.append("- **Objetivo**: definir `proximo_passo` e `prioridade_rank`.")
    L.append("- **Skills**: `classificacao-forca-probatoria` (score composto 12 dimensões) · `proximo-passo-advisor`.")
    L.append("- **Gates**: aprovação humana antes de mover devedor para F3+ (gate documental jurídico).")
    L.append("- **Prazo típico**: 1-2 dias.")
    L.append("- **Saída**: rank atualizado em `profiles.json`.")
    L.append("")

    L.append("## F3 — Notificação extrajudicial (TRD)")
    L.append("- **Objetivo**: emitir Termo de Reconhecimento de Dívida ou notificação extrajudicial.")
    L.append("- **Skills**: `protocolo-juridico-prodam` · `geracao-documentos-juridicos` (TRD/notificações) · `revisar-reconhecimento-divida` (gate antes do TRD).")
    L.append("- **Gates**: mostrar diff antes de salvar; revisão humana; envio com AR ou e-mail certificado.")
    L.append("- **Prazo típico**: 15-30 dias entre emissão e resposta esperada.")
    L.append("- **Saída**: documento `.docx` em `DOCUMENTOS_GERADOS/`, registro em `historico_fases`.")
    L.append("")

    L.append("## F4 — Negociação / Resposta")
    L.append("- **Objetivo**: acompanhar resposta do devedor (aceite, contraproposta, silêncio).")
    L.append("- **Skills**: `registro-interacoes-devedor` · `arvore-decisao-contestacao` (réplicas a contestações).")
    L.append("- **Gates**: silêncio não interrompe prescrição (Regra 3 do CLAUDE.md); registrar ato inequívoco se houver.")
    L.append("- **Prazo típico**: 30-60 dias.")
    L.append("- **Saída**: atualização de `ultima_interacao` e `evidencias_reconhecimento`.")
    L.append("")

    L.append("## F5 — Protocolo judicial / Execução")
    L.append("- **Objetivo**: ajuizar ação ou pedir habilitação de crédito.")
    L.append("- **Skills**: `blindagem-pre-execucao` (checklist pré-protocolo) · `montagem-dossie-comprobatorio` · `precatorios-rpv-fragmentacao` (Adm. Direta).")
    L.append("- **Gates**: Adm. Direta → precatório/RPV (Art. 100 CF); Adm. Indireta concorrencial → penhora direta (Tema 253/STF).")
    L.append("- **Prazo típico**: 60-180 dias para distribuição inicial.")
    L.append("- **Saída**: `data_protocolo` preenchida; `via_processual_recomendada` definida.")
    L.append("")

    L.append("## F6 — Recebimento / Encerramento")
    L.append("- **Objetivo**: confirmar pagamento, baixar do portfólio, calcular fee 20%.")
    L.append("- **Skills**: `registro-interacoes-devedor` (baixa e histórico) · `gerador-relatorio-quinzenal` (prestação de contas).")
    L.append("- **Gates**: comprovante de depósito; cálculo de SELIC pós-trânsito; nota de honorários.")
    L.append("- **Prazo típico**: variável (precatório AM tem fila própria).")
    L.append("- **Saída**: `valor_recuperado` registrado; devedor marcado como encerrado.")
    L.append("")

    L.append("## Princípios transversais")
    L.append("- **Prescrição é por fatura individual** (Regra 2 do CLAUDE.md). Cada fase recalcula faturas em risco.")
    L.append("- **PDFs nunca são apagados** — prova jurídica (NUNCA-1). Backup em `_BACKUPS/`.")
    L.append("- **`profiles.json` é SSOT** (NUNCA-6) — qualquer fase atualiza apenas via PR ou edit auditado.")
    L.append("- **Fee 20% recuperado**; RPV/AM = 20 × SM vigente (Lei AM 2.748/2002 — Regra 12).")
    L.append("")

    return "\n".join(L) + "\n"


def generate_playbook_orgaos():
    """PLAYBOOK_ORGAOS_V2.md — 13 passos validados no DETRAN A+ 94/100. Hardcoded.

    2026-06-09: ferramentas dos passos passaram a citar SÓ scripts/skills que existem
    no disco (antes citava ocr_v4.py, normalizador.py, extracao_contratual.py,
    prescricao_por_fatura.py, atualizacao_monetaria_bcb.py, score_composto.py,
    blindagem_pre_execucao.py, atualizar_profile.py, organizar_pdfs_orgao.py e
    ocr_audit.py — nenhum existia em scripts/, e normalizador.py contradizia a NUNCA-4)."""
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
    L.append("- **Ferramenta**: skill `organizador-arquivos-prodam` (modo cópia não-destrutivo) ou organização manual.")
    L.append("- **Saída**: subpastas por tipo (CONTRATOS/, NES/, FATURAS/, NFs/, COBRANCAS/).")
    L.append("- **Critério**: nenhum PDF apagado; backup em `_BACKUPS/`.")
    L.append("")
    L.append("### Passo 2 — OCR completo dos PDFs")
    L.append("- **Entrada**: PDFs do passo 1.")
    L.append("- **Ferramenta**: `scripts/ocr_lote_sem_texto_externo.py` + skill `ocr-pdfs-prodam` (pytesseract/pdf2image, 200 DPI, pt-BR).")
    L.append("- **Saída**: texto pesquisável por PDF (originais preservados como prova).")
    L.append("- **Critério**: ≥95% de páginas com texto extraído (relatório do próprio script).")
    L.append("")
    L.append("### Passo 3 — Ingestão no `prodam.db`")
    L.append("- **Entrada**: JSONs do passo 2.")
    L.append("- **Ferramenta**: `PRODAM_DOCS/build_sqlite.py` ou `scripts/atualizar_db.py`.")
    L.append("- **Saída**: registros em `spcf_contratos`, `spcf_empenhos`, `spcf_faturas`, `spcf_nfs`.")
    L.append("- **Critério**: contagens batem com o esperado por contrato.")
    L.append("")
    L.append("### Passo 4 — Normalização de contratos")
    L.append("- **Entrada**: 3 formatos coexistindo (`006/2021`, `6/2021`, `2021/006`).")
    L.append("- **Ferramenta**: normalização inline nos scripts de reconciliação (`scripts/reconciliacao_4_fontes.py`) — **não** criar `normalizador.py` (NUNCA-4).")
    L.append("- **Saída**: coluna `contrato_normalizado` em todas as tabelas.")
    L.append("- **Critério**: zero contratos órfãos após reconciliação.")
    L.append("")
    L.append("### Passo 5 — Extração contratual cláusula-a-cláusula")
    L.append("- **Entrada**: contratos do passo 1.")
    L.append("- **Ferramenta**: skill `extracao-clausulas-contratuais` + confirmação manual da cláusula econômica (Regra 10).")
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
    L.append("- **Ferramenta**: `scripts/alerta_prescricao.py` (buckets/alertas) + skill `analise-prescricao-creditos`.")
    L.append("- **Saída**: classificação `EXIGIVEL`/`PRESCRITA` por fatura + `data_prescricao_proxima` por devedor.")
    L.append("- **Critério**: regra Art. 202 VI CC aplicada (empenho interrompe; silêncio não).")
    L.append("")
    L.append("### Passo 8 — Atualização monetária")
    L.append("- **Entrada**: faturas exigíveis do passo 7.")
    L.append("- **Ferramenta**: `scripts/ad_hoc/gerar_memorial_preliminar_ses.py` (BCB live SGS 4390 + Decimal; adaptar por órgão) + skill `atualizacao-monetaria-sob-demanda`.")
    L.append("- **Saída**: `val_atualizado` por devedor; índice aplicado (IGPM/IPCA/SELIC) conforme contrato.")
    L.append("- **Critério**: SELIC já inclui juros (não somar separado); IGPM = só correção.")
    L.append("")
    L.append("### Passo 9 — Score composto 12 dimensões")
    L.append("- **Entrada**: dados completos do devedor.")
    L.append("- **Ferramenta**: skill `classificacao-forca-probatoria` (score gravado em `profiles.json`).")
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
    L.append("- **Ferramenta**: skill `blindagem-pre-execucao` (checklist pré-protocolo + 6 teses de embargos antecipadas).")
    L.append("- **Saída**: checklist completo (legitimidade, competência, prescrição, título, índice, juros, multa, etc).")
    L.append("- **Critério**: todos os itens do checklist validados antes de protocolar.")
    L.append("")
    L.append("### Passo 13 — Atualização de `profiles.json` e commit")
    L.append("- **Entrada**: tudo dos passos anteriores.")
    L.append("- **Ferramenta**: `scripts/atualizar_profiles_pos_acao.py` ou edição auditada (backup antes: `profiles_BACKUP_ANTES_<motivo>.json`).")
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
    # Fail-fast (2026-06-09): antes, profiles.json ausente retornava exit 0 (sucesso
    # falso p/ /sincronizar-prodam) e fonte corrompida gerava CLAUDE.md lixo.
    if not PROFILES.exists():
        print(f"ERRO: {PROFILES} nao encontrado — nada foi escrito.")
        sys.exit(1)

    data = load_profiles()
    try:
        validate_profiles(data)
    except ProfilesInvalidos as e:
        print(f"ERRO: profiles.json invalido — nada foi escrito. Motivo: {e}")
        sys.exit(1)

    n_skills = generate_skills_index()
    if n_skills:
        print(f"INDEX.md atualizado: {SKILLS_INDEX} ({n_skills} skills)")

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
    if m["prescricao_vencida"]:
        print(f"  [ALERTA] {len(m['prescricao_vencida'])} devedor(es) com data de prescricao no PASSADO/stale — ver STATUS_DEVEDORES.md")
    if m["prescricao_sem_data"]:
        print(f"  [INFO] {len(m['prescricao_sem_data'])} devedor(es) sem data de prescricao registrada")


if __name__ == "__main__":
    main()
