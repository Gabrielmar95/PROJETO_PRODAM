#!/usr/bin/env python3
"""
Auto-update CLAUDE.md from profiles.json + prodam.db.
Roda no inicio de cada sessao Cowork para manter CLAUDE.md sincronizado.
Gera metricas atualizadas automaticamente.
"""
import json
import sqlite3
import os
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path

BASE = Path(__file__).parent
PROFILES = BASE / "PRODAM_DOCS" / "profiles.json"
DB = BASE / "prodam.db"
OUTPUT = BASE / "CLAUDE.md"

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

def fmt_brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def generate_claude_md(m):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    lines = []
    lines.append("# PROJETO PRODAM — Recuperação de Créditos")
    lines.append(f"## Contrato 002/2026 — PRODAM S.A. × Brandão Ozores Advogados")
    lines.append(f"**Atualizado automaticamente em {now} via auto_update_claude_md.py**")
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
    lines.append("- `prodam.db` — SQLite (8 tabelas, 80k+ registros)")
    lines.append("- `PRODAM_DOCS/profiles.json` — SSOT dos devedores (fonte autoritativa)")
    lines.append("- `PRODAM_DOCS/REFERENCIA_JURIDICA/` — base jurídica (20 subpastas)")
    lines.append("- `PRODAM_DOCS/_SKILLS/` — skills jurídicas pareadas")
    lines.append("- `SPCF_EXTRACAO/` — web scraping SPCF")
    lines.append("- `consultas.py` — 15 queries forenses (CLI)")
    lines.append("")
    
    # === SQLITE ===
    lines.append("## SQLITE prodam.db")
    lines.append("Tabelas: spcf_contratos (362), spcf_empenhos (16.789), spcf_faturas (1.837), spcf_nfs (52.998), pendrive_docs (3.699), devedores (81), reclassificacao (1.261), cruzamento_spcf_pendrive (1.460)")
    lines.append("Views: v_fatura_completa, v_fatura_sem_empenho, v_nf_sem_pagamento, v_pendrive_por_devedor, v_cruzamento_nf")
    lines.append("")
    
    # === REGRAS ===
    lines.append("## REGRAS JURÍDICAS OBRIGATÓRIAS")
    lines.append("1. **Decreto Estadual nº 53.464/2026** (substitui 51.084/2025) — verificar 4 exceções antes de qualquer ação contra Gov AM")
    lines.append("2. Silêncio do devedor **NÃO** interrompe prescrição — exige ato inequívoco (Art. 202 CC taxativo)")
    lines.append("3. Juros pós-**Lei 14.905/2024** — NÃO presumir 1% a.m.; verificar arts. 404-406 CC")
    lines.append("4. Índices: consultar `config_prodam.py` — SELIC padrão, FUHAM=IGPM, DETRAN=IGPM+1%+2% (PRESUMIDO)")
    lines.append("5. Adm. Direta → precatório/RPV (Art. 100 CF) | Adm. Indireta concorrencial → penhora direta (Tema 253/STF)")
    lines.append("6. NFs do credor **NÃO** são marcos interruptivos (exige ato do devedor)")
    lines.append("7. Prescrição é por **FATURA individual** (Art. 189 + 206 §5º I CC), contada do **VENCIMENTO**")
    lines.append("8. FUHAM = Fund. Alfredo da Matta | FHAJ = Fund. Hosp. Adriano Jorge — **NUNCA** inverter")
    lines.append("9. Empenho (NE) = reconhecimento tácito (Art. 202 VI CC) — interrompe prescrição")
    lines.append("10. SELIC já inclui correção + juros — **NÃO** somar separado. IGPM = só correção (juros à parte)")
    lines.append("11. Art. 202 CC: interrupção ocorre **UMA VEZ** (unicidade — REsp 1.963.067/MS). Fazenda reinicia por metade (Decreto 20.910/1932 = 2,5 anos)")
    lines.append("12. Tema 1.109/STJ: gestor público **NÃO** renuncia tacitamente a prescrição")
    lines.append("13. Composição documental (Contrato+NE+NF+Atesto) = título executivo (REsp 793.969/RJ, Min. Teori Zavascki)")
    lines.append("14. Fee: **20%** sobre créditos recuperados (não 30%). RPV AM estadual = 20 salários mínimos (~R$ 32.420)")
    lines.append("15. `profiles.json` é a SSOT — NUNCA usar Demonstrativo Excel antigo")
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
    lines.append("```bash")
    lines.append("py -3.12 orgao_pipeline_completa.py --orgao SEDUC")
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
    lines.append("## SCRIPTS PRINCIPAIS (PROJETO_PRODAM/)")
    lines.append("| Script | Função |")
    lines.append("|--------|--------|")
    lines.append("| `prodam_utils.py` | norm() unidecode + brl() + datas + match_flex |")
    lines.append("| `orgao_pipeline_completa.py` | **Pipeline genérica `--orgao`** |")
    lines.append("| `sincronizar_prodam.py` | Comando mestre (rebuild + audit + dossiês) |")
    lines.append("| `atualizar_db.py` | Rebuild prodam.db |")
    lines.append("| `detran_*.py` | Templates DETRAN (copiar e adaptar) |")
    lines.append("| `auditoria_completude_devedor.py` | Checklist 11 itens (69 devedores) |")
    lines.append("| `dossie_multiformato_devedor.py` | 5 formatos por devedor |")
    lines.append("| `reconciliar_orfaos_reversos.py` | Popular via `norm()` |")
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
    lines.append("## COMANDOS ÚTEIS")
    lines.append("```")
    lines.append("py -3.12 consultas.py --lista              # ver todas as queries")
    lines.append("py -3.12 consultas.py resumo_geral         # visão geral")
    lines.append("py -3.12 consultas.py top_devedores        # ranking por valor")
    lines.append("py -3.12 orgao_pipeline_completa.py --orgao SEDUC  # audita novo órgão")
    lines.append("py -3.12 auto_update_claude_md.py          # regenerar este arquivo")
    lines.append("py -3.12 sincronizar_prodam.py             # sincronização completa")
    lines.append("```")

    return "\n".join(lines) + "\n"

def main():
    if not PROFILES.exists():
        print(f"ERRO: {PROFILES} nao encontrado")
        return
    
    data = load_profiles()
    m = compute_metrics(data)
    content = generate_claude_md(m)
    
    # Escreve diretamente (sem backup — evita PermissionError em sandbox)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"CLAUDE.md atualizado: {OUTPUT}")
    print(f"  {m['total']} devedores, {fmt_brl(m['val_exig'])} exigivel")
    if m["prescricao_urgente"]:
        print(f"  ALERTA: {len(m['prescricao_urgente'])} devedores com prescricao <90 dias")

if __name__ == "__main__":
    main()
