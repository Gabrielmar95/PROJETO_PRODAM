"""
detran_score_auditor.py — Auditoria final e atribuição de NOTA ao DETRAN.

Avalia em 12 dimensões ponderadas, cada uma com critérios objetivos 0-100.
Gera score composto final (0-100) + análise qualitativa de forças/fraquezas.

Dimensões (peso):
  1. Integridade de Dados          (10%)
  2. Cadeia Documental (5 elos)    (15%)
  3. Prescrição & Marcos           (15%)
  4. Blindagem Pré-Execução        (10%)
  5. Compliance Jurídico           (10%)
  6. Evidências Documentais         (8%)
  7. Reconhecimento Tácito          (8%)
  8. Atualização Monetária          (6%)
  9. Priorização (rank/valor)       (6%)
 10. Risco Processual              (5%)
 11. Valor Recuperável (E[V])     (4%)
 12. Urgência/Prazo                (3%)

Total: 100%
"""
from __future__ import annotations
import sys, json, sqlite3
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from prodam_utils import norm, norm_variants, fmt_brl, parse_br_date, parse_comp, esta_prescrita

DB = sqlite3.connect(str(ROOT / "prodam.db"))
DB.row_factory = sqlite3.Row
HOJE = date.today()

profile = json.load(open(ROOT / "PRODAM_DOCS" / "profiles.json", encoding='utf-8'))["DETRAN"]

# ============================================================
# Coleta dados do DB (DETRAN)
# ============================================================
empenhos_db = [dict(r) for r in DB.execute("""
    SELECT id, numero, contrato_ref, valor, situacao, data_emissao
    FROM spcf_empenhos WHERE cliente='DETRAN'
""").fetchall()]

faturas_db = [dict(r) for r in DB.execute("""
    SELECT id, nf, contrato_num, valor_bruto, competencia, situacao,
           cadeia_completude, total_empenhos_vinculados
    FROM spcf_faturas WHERE cliente='DETRAN'
""").fetchall()]

contratos_db = DB.execute("SELECT COUNT(*) FROM spcf_contratos WHERE UPPER(json_extract(dados_base,'$.Cliente')) LIKE '%DETRAN%' OR UPPER(cliente) LIKE '%DETRAN%'").fetchone()[0]

# ============================================================
# DIMENSÃO 1: INTEGRIDADE DE DADOS (10%)
# ============================================================
def score_integridade():
    detalhes = []
    pontos = 0
    max_p = 0

    # Profile completo (principais campos)
    campos_criticos = ["nome_completo","cnpj","categoria","forca_probatoria","val_exig",
                       "faturas_total","data_prescricao_proxima","regime_execucao","indice_correcao"]
    preenchidos = sum(1 for c in campos_criticos if profile.get(c))
    p = (preenchidos / len(campos_criticos)) * 20
    pontos += p; max_p += 20
    detalhes.append(f"Campos críticos do profile: {preenchidos}/{len(campos_criticos)} = {p:.1f}/20")

    # Índices granulares por contrato (nova dimensão)
    indices_granulares = profile.get("indices_correcao_por_contrato", {})
    if len(indices_granulares) >= 10:
        pontos += 15; detalhes.append(f"✅ {len(indices_granulares)} contratos com índice granular identificado = 15/15")
    elif len(indices_granulares) >= 5:
        pontos += 10; detalhes.append(f"🟡 {len(indices_granulares)} contratos com índice granular = 10/15")
    else:
        detalhes.append(f"⚠️ Só {len(indices_granulares)} contratos com índice identificado")
    max_p += 15

    # Pipeline JSON (novo)
    pipe = profile.get("pipeline_json_consolidado", {})
    if pipe.get("total_arquivos_processados", 0) >= 400:
        pontos += 20; detalhes.append(f"✅ {pipe['total_arquivos_processados']} PDFs em JSON estruturado = 20/20")
    elif pipe.get("total_arquivos_processados", 0) > 0:
        pontos += 10; detalhes.append(f"🟡 {pipe['total_arquivos_processados']} PDFs em JSON")
    else:
        detalhes.append("⚠️ Sem pipeline JSON — LLMs dependem só do profile")
    max_p += 20

    # Dados no DB
    fat_db = len(faturas_db)
    emp_db = len(empenhos_db)
    con_db = contratos_db
    p = 0
    if fat_db > 100: p += 8
    if emp_db > 200: p += 8
    if con_db > 0: p += 9
    else: detalhes.append("⚠️ 0 contratos no DB (228 no SPCF) — bug ingestão")
    pontos += p; max_p += 25
    detalhes.append(f"DB: {fat_db} faturas, {emp_db} NEs, {con_db} contratos = {p}/25")

    # Sessão 74 (fonte externa canônica)
    sess74 = profile.get("auditoria_cruzada_14_04_2026", {})
    if sess74.get("faturas_exigiveis_sessao74") == 202:
        pontos += 10; detalhes.append("✅ Sessão 74 integrada (202 faturas) = 10/10")
    else:
        detalhes.append("⚠️ Sessão 74 não integrada")
    max_p += 10

    # Ausência de bugs conhecidos
    if sess74.get("bug_db_data_emissao"):
        detalhes.append("⚠️ Bug DB: data_emissao errada = 0/10")
        max_p += 10
    else:
        pontos += 10; max_p += 10
        detalhes.append("✅ Sem bugs conhecidos")

    return round(pontos/max_p*100, 1), detalhes

# ============================================================
# DIMENSÃO 2: CADEIA DOCUMENTAL (5 elos) (15%)
# ============================================================
def score_cadeia():
    detalhes = []
    completa = sum(1 for f in faturas_db if f["cadeia_completude"] == "COMPLETA")
    forte = sum(1 for f in faturas_db if f["cadeia_completude"] == "FORTE")
    media = sum(1 for f in faturas_db if f["cadeia_completude"] == "MEDIA")
    fraca = sum(1 for f in faturas_db if f["cadeia_completude"] in ("FRACA","MUITO_FRACA"))
    total = len(faturas_db)
    if total == 0:
        return 0, ["Sem faturas no DB"]

    # Score ponderado: COMPLETA=100, FORTE=80, MEDIA=50, FRACA=20
    score_medio = (completa*100 + forte*80 + media*50 + fraca*20) / total
    detalhes.append(f"{completa} COMPLETA + {forte} FORTE + {media} MÉDIA + {fraca} FRACA / {total}")
    detalhes.append(f"Score ponderado médio: {score_medio:.1f}/100")
    return round(score_medio, 1), detalhes

# ============================================================
# DIMENSÃO 3: PRESCRIÇÃO & MARCOS (15%)
# ============================================================
def score_prescricao():
    detalhes = []
    sess74 = profile.get("auditoria_cruzada_14_04_2026", {})

    vigentes = sess74.get("faturas_vigentes", 0)
    atencao = sess74.get("faturas_atencao", 0)
    prescritas = sess74.get("faturas_prescritas_reais", 0)
    total_s74 = vigentes + atencao + prescritas

    if total_s74 == 0:
        # Fallback para DB
        prot = [f for f in faturas_db if f["cadeia_completude"] in ("COMPLETA","FORTE")]
        return 70, [f"Sessão 74 não disponível — DB tem {len(prot)}/{len(faturas_db)} protegíveis"]

    # Score: vigentes=100, atencao=70, prescritas=0
    score = (vigentes*100 + atencao*70 + prescritas*0) / total_s74
    detalhes.append(f"Sessão 74: {vigentes} VIGENTES + {atencao} ATENÇÃO + {prescritas} PRESCRITAS")
    detalhes.append(f"Score ponderado: {score:.1f}/100")

    # Bonus: marcos interruptivos robustos (Art.202 VI)
    nes_pos_2021 = sum(1 for e in empenhos_db if (e.get("data_emissao","") or "")[-4:] >= "2021")
    if nes_pos_2021 > 100:
        detalhes.append(f"✅ {nes_pos_2021} NEs pós-2021 — reconhecimento tácito massivo")
    return round(score, 1), detalhes

# ============================================================
# DIMENSÃO 4: BLINDAGEM PRÉ-EXECUÇÃO (10%)
# ============================================================
def score_blindagem():
    sess74 = profile.get("auditoria_cruzada_14_04_2026", {})
    status = sess74.get("blindagem_status", "")
    bloqueio = sess74.get("bloqueio_a3", "")

    detalhes = [f"Blindagem: {status}"]
    score = 100
    if "22/22" in status:
        detalhes.append("✅ 22/22 itens validados")
    else:
        score -= 20
    if bloqueio:
        detalhes.append(f"⚠️ {bloqueio}")
        score -= 25  # TRD faltando
    return max(score, 0), detalhes

# ============================================================
# DIMENSÃO 5: COMPLIANCE JURÍDICO (10%)
# ============================================================
def score_compliance():
    detalhes = []
    pontos = 0
    # Regime correto (Adm. Indireta concorrencial → penhora direta)
    if profile.get("regime_execucao") in ("penhora_direta", "penhora direta"):
        pontos += 25; detalhes.append("✅ Regime penhora_direta (Tema 253/STF correto)")
    else:
        detalhes.append(f"⚠️ Regime: {profile.get('regime_execucao')} — revisar")

    # Índice correto
    if "IGPM" in (profile.get("indice_correcao") or ""):
        pontos += 25; detalhes.append("✅ Índice IGPM+1%+2% (cláusula 11.1 CT 022/2014)")
    else:
        detalhes.append("⚠️ Índice não-IGPM — verificar")

    # Título executivo classificado
    if profile.get("titulo_executivo"):
        pontos += 25; detalhes.append("✅ titulo_executivo=True (Art.784 CPC)")
    else:
        detalhes.append("⚠️ Título executivo não confirmado")

    # Modelo de notificação coerente com força FORTE
    if profile.get("modelo_notificacao") == "A" and profile.get("forca_probatoria") == "FORTE":
        pontos += 25; detalhes.append("✅ Modelo A (força FORTE — coerente)")
    else:
        detalhes.append("⚠️ Modelo/força inconsistentes")
    return pontos, detalhes

# ============================================================
# DIMENSÃO 6: EVIDÊNCIAS DOCUMENTAIS (8%)
# ============================================================
def score_evidencias():
    detalhes = []
    ev = profile.get("evidencias_reconhecimento", 0) or 0
    pontos = min(ev / 3, 100)  # 300+ evidências = 100%
    detalhes.append(f"{ev} evidências de reconhecimento")

    ev_tipo = profile.get("evidencias_por_tipo", {})
    if isinstance(ev_tipo, dict) and len(ev_tipo) > 1:
        detalhes.append(f"Tipos: {dict(ev_tipo)}")

    # Classificação
    cls = profile.get("classificacao_reconhecimento", "")
    if "CONFIRMADO" in cls:
        detalhes.append(f"✅ {cls}")
    return round(pontos, 1), detalhes

# ============================================================
# DIMENSÃO 7: RECONHECIMENTO TÁCITO (8%)
# ============================================================
def score_reconhecimento():
    detalhes = []
    # NEs documentam reconhecimento tácito
    # Sessão 74: 500 NEs
    # DB: 470 NEs (com bug de data)
    sess74 = profile.get("auditoria_cruzada_14_04_2026", {})
    nes_total = sess74.get("nes_total_documentadas", len(empenhos_db))
    valor = sess74.get("nes_valor_historico", sum(float(e.get("valor") or 0) for e in empenhos_db))

    # 500+ NEs × R$ 284M — excepcional
    pontos = 100 if nes_total >= 500 else (80 if nes_total >= 300 else 60)
    detalhes.append(f"{nes_total} NEs × {fmt_brl(valor)}")
    detalhes.append(f"✅ Reconhecimento tácito massivo (Art.202 VI CC)")

    # Revisão formal
    if profile.get("reconhecimento_revisado"):
        detalhes.append("✅ reconhecimento_revisado preenchido")
    return pontos, detalhes

# ============================================================
# DIMENSÃO 8: ATUALIZAÇÃO MONETÁRIA (6%)
# ============================================================
def score_atualizacao():
    detalhes = []
    pontos = 50  # base

    def _to_num(v):
        if v is None: return 0
        if isinstance(v,(int,float)): return float(v)
        try: return float(str(v).replace(",",".").replace("R$","").strip())
        except: return 0

    val_exig = _to_num(profile.get("val_exig"))
    val_atualizado = _to_num(profile.get("val_atualizado"))
    if val_exig > 0 and val_atualizado > val_exig:
        fator = val_atualizado / val_exig
        pontos = 80 if fator < 2 else 70
        detalhes.append(f"Fator {fator:.2f}x (bruto→atualizado)")

    # Fonte sessão 74 com correção real
    sess74 = profile.get("auditoria_cruzada_14_04_2026", {})
    if sess74.get("valor_atualizado_sessao74"):
        pontos = 95
        detalhes.append(f"✅ IGPM+1%+2% aplicado (sessão 74): {fmt_brl(sess74['valor_atualizado_sessao74'])}")

    # Ideal: atualização em tempo real via BCB
    detalhes.append("ℹ️ Ideal: re-rodar atualizacao-monetaria-sob-demanda para IGPM real BCB")
    return pontos, detalhes

# ============================================================
# DIMENSÃO 9: PRIORIZAÇÃO (6%)
# ============================================================
def score_priorizacao():
    detalhes = []
    rank = profile.get("prioridade_rank") or profile.get("ranking_spcf") or 99
    score_comp = profile.get("score_composto", 0)
    # Rank 1-2 = top 3% → 100; 3-5 → 80; 6-10 → 60; >10 → 40
    if rank <= 2: pontos = 100
    elif rank <= 5: pontos = 85
    elif rank <= 10: pontos = 70
    else: pontos = 50
    detalhes.append(f"Ranking: #{rank} | score composto: {score_comp}")
    return pontos, detalhes

# ============================================================
# DIMENSÃO 10: RISCO PROCESSUAL (5%)
# ============================================================
def score_risco():
    detalhes = []
    p_rec = profile.get("p_recuperacao") or 0
    pontos = p_rec * 100
    detalhes.append(f"p_recuperação: {p_rec:.2%}")

    # Blindagem já validada reduz risco
    if "22/22" in (profile.get("auditoria_cruzada_14_04_2026",{}).get("blindagem_status","")):
        detalhes.append("✅ Blindagem 22/22 — risco processual minimizado")
    return round(pontos, 1), detalhes

# ============================================================
# DIMENSÃO 11: VALOR RECUPERÁVEL (E[V]) (4%)
# ============================================================
def score_ev():
    detalhes = []
    def _num(v):
        if v is None: return 0
        if isinstance(v,(int,float)): return float(v)
        try: return float(str(v).replace(",",".").replace("R$","").strip())
        except: return 0
    ev_val = _num(profile.get("ev_valor_esperado"))
    ev_hon = _num(profile.get("ev_honorarios"))
    detalhes.append(f"E[V]: {fmt_brl(ev_val)} | Honorários esperados: {fmt_brl(ev_hon)}")

    # Relativa ao portfolio (~R$ 121M total)
    pct = ev_val / 121_000_000 if ev_val else 0
    pontos = min(pct*400, 100)  # 25% portfolio = 100
    detalhes.append(f"{pct:.1%} do portfólio — peso {pontos:.1f}")
    return round(pontos, 1), detalhes

# ============================================================
# DIMENSÃO 12: URGÊNCIA/PRAZO (3%)
# ============================================================
def score_urgencia():
    detalhes = []
    sess74 = profile.get("auditoria_cruzada_14_04_2026", {})
    atencao = sess74.get("faturas_atencao", 0)
    prazo = sess74.get("faturas_atencao_prazo", {})

    if atencao > 0:
        primeira = prazo.get("primeira_prescricao","")
        detalhes.append(f"⚠️ {atencao} faturas em ATENÇÃO — primeira prescrição {primeira}")
        pontos = 50  # urgência média — ainda 200+ dias
    else:
        pontos = 90

    # Fase avançada (F5 = petição pronta)
    if profile.get("fase_atual") == "F5":
        detalhes.append("✅ Fase F5 — petição pronta")
        pontos = min(pontos + 20, 100)
    return pontos, detalhes

# ============================================================
# COMPUTAR TODAS
# ============================================================
DIMENSOES = [
    ("Integridade de Dados",    10, score_integridade),
    ("Cadeia Documental",        15, score_cadeia),
    ("Prescrição & Marcos",      15, score_prescricao),
    ("Blindagem Pré-Execução",   10, score_blindagem),
    ("Compliance Jurídico",      10, score_compliance),
    ("Evidências Documentais",    8, score_evidencias),
    ("Reconhecimento Tácito",     8, score_reconhecimento),
    ("Atualização Monetária",     6, score_atualizacao),
    ("Priorização",               6, score_priorizacao),
    ("Risco Processual",          5, score_risco),
    ("Valor Recuperável (E[V])",  4, score_ev),
    ("Urgência/Prazo",            3, score_urgencia),
]

resultados = []
score_total = 0
for nome, peso, fn in DIMENSOES:
    score, detalhes = fn()
    score_total += score * peso / 100
    resultados.append({
        "dimensao": nome,
        "peso_pct": peso,
        "score": score,
        "contribuicao": round(score * peso / 100, 2),
        "detalhes": detalhes,
    })

score_final = round(score_total, 1)

# Classificação
if score_final >= 90: conceito = "A+ (EXCEPCIONAL)"
elif score_final >= 85: conceito = "A (EXCELENTE)"
elif score_final >= 80: conceito = "A- (MUITO BOM)"
elif score_final >= 75: conceito = "B+ (BOM)"
elif score_final >= 70: conceito = "B (ACEITÁVEL)"
elif score_final >= 60: conceito = "C (RESSALVAS)"
else: conceito = "D (AÇÃO CORRETIVA URGENTE)"

# ============================================================
# OUTPUT
# ============================================================
print(f"\n{'='*70}")
print(f"  DETRAN — AUDITORIA FINAL COM SCORE (12 dimensões)")
print(f"{'='*70}\n")
print(f"{'Dimensão':<28}{'Peso':>6}{'Score':>7}{'Contr.':>8}")
print(f"{'-'*70}")
for r in resultados:
    print(f"{r['dimensao']:<28}{r['peso_pct']:>5}%{r['score']:>7.1f}{r['contribuicao']:>8.2f}")
print(f"{'-'*70}")
print(f"{'TOTAL':<28}{100:>5}%{'':>7}{score_final:>8.1f}")
print(f"\n{'='*70}")
print(f"  NOTA FINAL: {score_final}/100 → {conceito}")
print(f"{'='*70}\n")

# Salvar JSON detalhado
out = ROOT / "DETRAN_AUDITORIA" / "SCORE_DETRAN.json"
out.parent.mkdir(exist_ok=True)
json.dump({
    "data": HOJE.isoformat(),
    "score_final": score_final,
    "conceito": conceito,
    "dimensoes": resultados,
    "resumo_forcas": [r["dimensao"] for r in resultados if r["score"] >= 85],
    "resumo_fraquezas": [r["dimensao"] for r in resultados if r["score"] < 70],
}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"✅ Salvo: {out}")

# Detalhes
print("\n--- DETALHES POR DIMENSÃO ---")
for r in resultados:
    print(f"\n[{r['score']:>5.1f}] {r['dimensao']} (peso {r['peso_pct']}%)")
    for d in r['detalhes']:
        print(f"    {d}")
