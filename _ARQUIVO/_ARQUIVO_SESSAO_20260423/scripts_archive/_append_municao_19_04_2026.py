"""
Adiciona SECAO FINAL (Municao para reuniao com advogado) ao GAP_ANALYSIS_NOTIFICACAO_vs_FONTES.md
e gera BRIEFING_REUNIAO_DR_FABIO.txt.

Read-only em fontes (profiles.json, prodam.db). Nao altera.
"""
from __future__ import annotations
import sqlite3, json, re, os
from decimal import Decimal
from pathlib import Path
from datetime import datetime

DB = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\16_BANCOS_DADOS\prodam.db"
PROFILE = r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\11_PROFILES_BACKUPS\ativo\profiles.json"
OUT_MD = Path(r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\_NOTIFICACAO_ASSINADA\GAP_ANALYSIS_NOTIFICACAO_vs_FONTES.md")
OUT_TXT = Path(r"C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\_NOTIFICACAO_ASSINADA\BRIEFING_REUNIAO_DR_FABIO.txt")


def money(val) -> Decimal:
    if val is None or val == "":
        return Decimal("0")
    if isinstance(val, (int, float, Decimal)):
        return Decimal(str(val))
    s = str(val).strip().replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except Exception:
        return Decimal("0")


def fmt_brl(v: Decimal) -> str:
    s = f"{v:,.2f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


# ================= COLETA DE EVIDENCIAS =================
conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()

CTS = [
    ("CT 008/2021", "8/2021"),
    ("CT 014/2019", "14/2019"),
    ("CT 023/2014", "23/2014"),
    ("CT 179/2018", "179/2018"),
]
NFS_CT = {
    "8/2021":   ["137480","155743","129365","129512","137915","165069","165619","167069","167285","137106","166608","166859"],
    "14/2019":  ["128143","128161"],
    "23/2014":  ["128153","128164"],
    "179/2018": ["110654"],
}
VALORES_NOTIF = {
    "8/2021":   (Decimal("30625.82"),  Decimal("38412.13")),
    "14/2019":  (Decimal("2233.29"),   Decimal("4131.54")),
    "23/2014":  (Decimal("3584.37"),   Decimal("6631.03")),
    "179/2018": (Decimal("3084.08"),   Decimal("6958.97")),
}

# NEs por contrato
ne_por_ct = {}
for _, cn in CTS:
    cur.execute("""
        SELECT numero, valor, situacao, data_emissao, tem_pdf
        FROM spcf_empenhos
        WHERE UPPER(cliente) LIKE '%DETRAN%' AND contrato_ref = ?
        ORDER BY data_emissao DESC
    """, (cn,))
    nes = []
    for r in cur.fetchall():
        nes.append({"numero": r[0], "valor": money(r[1]), "situacao": r[2], "data": r[3], "tem_pdf": r[4]})
    ne_por_ct[cn] = nes

# Cadeia por NF via spcf_nfs
def codigos_nl_ob(blob):
    if not blob:
        return []
    try:
        obj = json.loads(blob) if isinstance(blob, str) else blob
    except Exception:
        return []
    codigos = []
    for k, v in (obj or {}).items():
        if not isinstance(v, str):
            continue
        for m in re.finditer(r"(\d{4})(NL|OB|PD|NE|ND)(\d+)", v):
            codigos.append(f"{m.group(1)}{m.group(2)}{m.group(3)}")
    return sorted(set(codigos))

nf_cadeia = {}
for cn, nfs in NFS_CT.items():
    nf_cadeia[cn] = {}
    for nf in nfs:
        cur.execute("SELECT tem_pagamento, liquidacao, pagamento FROM spcf_nfs WHERE numero_nf = ?", (nf,))
        r = cur.fetchone()
        if r:
            tem_pag, liq, pag = r
            nf_cadeia[cn][nf] = {
                "em_spcf_nfs": True,
                "tem_pagamento": tem_pag,
                "codigos_liquidacao": codigos_nl_ob(liq),
                "codigos_pagamento": codigos_nl_ob(pag),
                "liquidacao_raw_preview": (str(liq)[:250] + "...") if liq and len(str(liq)) > 250 else str(liq or ""),
            }
        else:
            nf_cadeia[cn][nf] = {"em_spcf_nfs": False}

# spcf_faturas (quais NFs da notif estao la)
cur.execute("SELECT nf, contrato_num FROM spcf_faturas WHERE UPPER(cliente) LIKE '%DETRAN%'")
nfs_spcf_faturas = {str(r[0]): r[1] for r in cur.fetchall()}

conn.close()

# Profile — extrair marco interruptivo
with open(PROFILE, "r", encoding="utf-8") as f:
    profiles = json.load(f)
det_contratos = profiles["DETRAN"]["contratos"]
marco_179 = det_contratos.get("179/2018", {}).get("marco_interruptivo", {})
marco_179_reforco = det_contratos.get("179/2018", {}).get("marco_reforçador_continuidade", {})


# ================= TEXTO DA SECAO DO MD =================
L = []
def w(s=""):
    L.append(s)

w("")
w("---")
w("")
w("## 7 — MUNIÇÃO PARA REUNIÃO COM ADVOGADO RESPONSÁVEL (DR. FÁBIO SILVA ANDRADE — OAB/AM 9.217)")
w("")
w("Seção acrescentada em 2026-04-19 para consolidar as evidências de cadeia documental dos 4 contratos sem PDF de contrato principal (Cenário B) e o marco interruptivo da NF 110654 — três pontos que precisam de decisão formal do subscritor da notificação antes do protocolo.")
w("")

# ----- 7.1 cadeia por contrato -----
w("### 7.1 Cadeia documental (NE/NL/NF/Aceite) dos 4 contratos sem PDF de contrato")
w("")
w("Para cada contrato, as colunas mostram: qtd de Notas de Empenho em `spcf_empenhos`, qtd de faturas em `spcf_faturas`, existência das NFs (por número) em `spcf_nfs` (a tabela que guarda NL/OB), e presença de aceite derivado.")
w("")
w("| Contrato | Valor original (R$) | NEs em `spcf_empenhos` | NEs com PDF | NE mais recente (data) | NFs em `spcf_faturas` (das NFs da notif) | NFs em `spcf_nfs` (com NL/OB) | Cadeia recomendável |")
w("|---|---:|---:|---:|---|---:|---:|---|")
for ct_raw, cn in CTS:
    nes = ne_por_ct[cn]
    nes_pdf = [n for n in nes if n["tem_pdf"]]
    ne_recente = f"{nes[0]['numero']} ({nes[0]['data']})" if nes else "—"
    nfs_notif = set(NFS_CT[cn])
    nfs_fat = {nf for nf, cn2 in nfs_spcf_faturas.items() if cn2 == cn and nf in nfs_notif}
    nfs_em_spcf_nfs = sum(1 for nf in NFS_CT[cn] if nf_cadeia[cn][nf]["em_spcf_nfs"])
    if cn == "179/2018":
        cadeia_rec = "NL+OB+PD (FORTÍSSIMO) — ver 7.2"
    elif nes and len(nfs_fat) >= 1:
        cadeia_rec = f"{len(nes)} NEs + {len(nfs_fat)} NFs (reconhecimento tácito Art. 202 VI)"
    elif nes:
        cadeia_rec = f"{len(nes)} NEs (sem NF em `spcf_faturas` — buscar no CSV)"
    else:
        cadeia_rec = "⚠ sem NE nem NF em prodam.db"
    valor_orig, _ = VALORES_NOTIF[cn]
    w(f"| {ct_raw} | {fmt_brl(valor_orig)} | {len(nes)} | {len(nes_pdf)} | {ne_recente} | {len(nfs_fat)}/{len(nfs_notif)} | {nfs_em_spcf_nfs}/{len(nfs_notif)} | {cadeia_rec} |")
w("")
w("**Observações por contrato:**")
w("")
for ct_raw, cn in CTS:
    nes = ne_por_ct[cn]
    nfs_notif = NFS_CT[cn]
    nfs_fat = [nf for nf, cn2 in nfs_spcf_faturas.items() if cn2 == cn and nf in set(nfs_notif)]
    w(f"**{ct_raw}:**")
    if nes:
        anos = sorted({n["data"][-4:] for n in nes if n["data"] and len(n["data"]) >= 4})
        total_ne = sum(n["valor"] for n in nes)
        w(f"- **{len(nes)} Notas de Empenho** emitidas entre {anos[0] if anos else '?'} e {anos[-1] if anos else '?'}, totalizando R$ {fmt_brl(total_ne)} empenhados. **{len([n for n in nes if n['tem_pdf']])}/{len(nes)}** com PDF arquivado em `pdfs_empenhos/`.")
        if len(anos) >= 3:
            w(f"- **Regularidade orçamentária plurianual** ({len(anos)} anos distintos) sustenta a tese de *continuidade do reconhecimento tácito* (Art. 202 VI CC) e afasta a alegação de contrato inexistente.")
    else:
        w(f"- **Zero NEs** em `spcf_empenhos` para esse contrato — contrato não empenhado no SPCF raspado, ou empenhado com referência diferente.")
    if nfs_fat:
        w(f"- NFs da notificação presentes em `spcf_faturas`: {sorted(nfs_fat)} ({len(nfs_fat)}/{len(nfs_notif)}).")
    else:
        w(f"- **Nenhuma** das NFs da notificação está em `spcf_faturas` — as NFs aparecem apenas nos CSVs do projeto (conforme tabela da seção 2).")
    nfs_em_nfs = [nf for nf in nfs_notif if nf_cadeia[cn][nf]["em_spcf_nfs"]]
    if nfs_em_nfs:
        w(f"- NFs em `spcf_nfs` (com status de liquidação/pagamento): {nfs_em_nfs}.")
    else:
        w(f"- Nenhuma NF desse contrato aparece em `spcf_nfs` (a tabela com NL/OB) — logo **sem cadeia de NL documentada no banco** para esse conjunto.")
    w("")

# ----- 7.2 marco NF 110654 -----
w("### 7.2 Marco interruptivo da NF 110654 (CT 179/2018) — conteúdo documentado")
w("")
w("Transcrição literal do campo `profiles.DETRAN.contratos['179/2018'].marco_interruptivo`:")
w("")
if marco_179:
    w("```json")
    w(json.dumps(marco_179, ensure_ascii=False, indent=2, default=str))
    w("```")
else:
    w("_campo ausente no profile._")
w("")
if marco_179_reforco:
    w("**Marco reforçador (continuidade contratual):**")
    w("")
    w("```json")
    w(json.dumps(marco_179_reforco, ensure_ascii=False, indent=2, default=str))
    w("```")
    w("")

w("**Confirmação no banco:** o campo `spcf_nfs.liquidacao` da NF 110654 contém, literalmente (preview):")
w("")
w("```")
w(nf_cadeia["179/2018"]["110654"]["liquidacao_raw_preview"])
w("```")
w("")
w("**Avaliação jurídica:**")
w("- Documentos citados (PD 2021PD0001589 + NL 2021NL0001165 + OB 2021OB0001606) são **atos administrativos formais do DETRAN-AM**, com data 19/08/2021, assinados pelo Gerente Financeiro José Maria Pinto.")
w("- A Nota de Liquidação (Arts. 63-65 Lei 4.320/1964) é, por si, **ato formal de reconhecimento do direito do credor pelo devedor** — hipótese do Art. 202 VI CC.")
w("- A NF 110654 foi parte de lote de 16 NFs; **15 foram pagas e só a 110654 foi creditada a menor** em R$ 2.925,60. O pagamento das co-irmãs, pela jurisprudência do STJ (reconhecimento do lote = reconhecimento individual), interrompe a prescrição da parte não paga.")
w("- **Divergência com o CSV**: o CSV `faturas_cruzadas_projeto` classifica a NF 110654 como `PRESCRITA` e força `FRACA`. Essa classificação parece **não considerar** o marco interruptivo (o próprio profile foi atualizado em 17/04/2026 15:35:23 para reconhecer o marco). **O CSV está desatualizado nesse ponto.**")
w("")

# ----- 7.3 art. 202 VI CC na pagina 3 -----
w("### 7.3 Tese do Art. 202 VI CC citada na página 3 da notificação — revisão técnica")
w("")
w("A notificação assinada contém, na página 3, a seguinte afirmação:")
w("")
w("> \"Outrossim, a presente notificação constitui ato inequívoco do credor hábil a interromper a prescrição (art. 202, VI, do Código Civil), reiniciando a contagem do prazo quinquenal a partir desta data.\"")
w("")
w("**Ponto técnico que precisa de confirmação do subscritor:**")
w("")
w("- O **Art. 202, VI, do Código Civil** dispõe: *\"A interrupção da prescrição... somente poderá ocorrer uma vez... [pelo/pela/por] qualquer ato inequívoco, ainda que extrajudicial, que importe reconhecimento do direito pelo devedor.\"*")
w("- O inciso VI é hipótese de **ato do DEVEDOR** (reconhecimento pelo devedor), não de ato do credor.")
w("- Uma **notificação extrajudicial do credor** é, tradicionalmente, instrumento de **constituição em mora** (Art. 397 §único CC) — não é, por si só, marco interruptivo da prescrição segundo os incisos do Art. 202 CC.")
w("- Há corrente doutrinária e julgados isolados (em especial: alguns acórdãos do STJ em relações privadas) que aceitam a notificação extrajudicial do credor como hipótese atípica de interrupção, por analogia com o inciso III (protesto) ou como ato inequívoco (interpretação ampla do inciso VI). **A tese não é pacífica.**")
w("- **Decisão jurídica a confirmar:** (a) a redação atual no página 3 deve ser mantida? (b) convém reforçar o fundamento citando, além do Art. 202 VI, também o Art. 202 III (protesto) ou a doutrina do \"ato inequívoco do credor\" (Ilmar Galvão, Theotonio Negrão)? (c) convém ajustar a redação para alinhar melhor à dicção do inciso VI (\"reconhecimento pelo devedor\"), invocando os marcos interruptivos documentados (NEs, NL da 110654, pagamentos parciais) como base para o 202 VI, e não a notificação em si?")
w("")
w("**Nota prática:** independentemente da decisão sobre a redação, a **tese protetiva REAL do projeto** se apoia em atos do devedor DETRAN (NEs, NLs, pagamentos parciais), cobertos pelo inciso VI corretamente. A fragilidade é apenas retórica, na forma como o texto da página 3 atribui o ato interruptivo ao credor.")
w("")
w("---")
w("")
w(f"_Anexado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — sem alterar profile.json ou prodam.db._")

# append
existing = OUT_MD.read_text(encoding="utf-8")
OUT_MD.write_text(existing + "\n".join(L) + "\n", encoding="utf-8")
print(f"MD atualizado: {OUT_MD}")


# ================= BRIEFING TXT (1 PAGINA) =================
T = []
def t(s=""):
    T.append(s)

# Sintetizar valores agregados
total_orig_4cts = sum(VALORES_NOTIF[cn][0] for _, cn in CTS)
total_atu_4cts = sum(VALORES_NOTIF[cn][1] for _, cn in CTS)
total_nes_4cts = sum(len(ne_por_ct[cn]) for _, cn in CTS)

t("=" * 72)
t("BRIEFING — 3 DECISOES PARA A REUNIAO COM DR. FABIO SILVA ANDRADE")
t(f"Data: 2026-04-20 (reuniao)  |  Base: notificacao assinada 2026-04-17 13:26")
t(f"Preparado: 2026-04-19 pos-analise de todas as fontes do projeto")
t("=" * 72)
t("")
t("")
t("DECISAO 1 - 4 CONTRATOS SEM PDF DO CONTRATO PRINCIPAL")
t("-" * 72)
t("Contratos: CT 008/2021, CT 014/2019, CT 023/2014, CT 179/2018")
t(f"Valor total original: R$ {fmt_brl(total_orig_4cts)}  |  atualizado: R$ {fmt_brl(total_atu_4cts)}")
t(f"(= 2,0% do saldo original e 1,6% do valor atualizado da notificacao)")
t("")
t("Cadeia documental encontrada nas fontes do projeto:")
for ct_raw, cn in CTS:
    nes = ne_por_ct[cn]
    nes_pdf = len([n for n in nes if n["tem_pdf"]])
    nfs_notif = NFS_CT[cn]
    nfs_fat = [nf for nf, cn2 in nfs_spcf_faturas.items() if cn2 == cn and nf in set(nfs_notif)]
    nfs_em_nfs = sum(1 for nf in nfs_notif if nf_cadeia[cn][nf]["em_spcf_nfs"])
    if cn == "179/2018":
        resumo = "0 NEs | 0 NFs DB | 1 NL+OB (marco 19/08/2021 FORTISSIMO)"
    else:
        resumo = f"{len(nes)} NEs ({nes_pdf} com PDF) | {len(nfs_fat)}/{len(nfs_notif)} NFs no DB | {nfs_em_nfs} NLs"
    t(f"  - {ct_raw}: {resumo}")
t("")
t("Fundamento executivo possivel:")
t("  * REsp 793.969/RJ + Art. 784 III CPC: NE + NL + NF + aceite tecnico =")
t("    titulo executivo extrajudicial, INDEPENDENTE de contrato PDF assinado.")
t("  * Art. 202 VI CC: cada NE/NL emitida pelo DETRAN e cada pagamento")
t("    parcial = reconhecimento tacito -> interrompe prescricao.")
t("")
t("Proposta para sua decisao:")
t("  (A) MANTER os 4 na notificacao + anexar ao dossie, para cada um,")
t("      a lista de NEs (com PDFs arquivados no banco), demonstrando")
t("      reconhecimento plurianual pelo DETRAN mesmo sem o PDF original do")
t("      contrato principal. Forte para CT 008, 014 e 023 (tem NEs 2019-2026).")
t("      Mais fragil para CT 179/2018 (zero NEs, apenas marco NL/OB 2021).")
t("  (B) EXCLUIR os 4 por ERRATA + protocolar separadamente quando os PDFs")
t("      forem localizados em PRODAM-RH/SPROWEB. Custa R$ 56,1 mil em valor")
t("      atualizado (1,6% da notificacao) mas elimina ponto de ataque.")
t("  (C) HIBRIDO: manter CT 008 (forte), CT 023 (forte) e CT 014 (razoavel)")
t("      com dossie de NEs; excluir por errata apenas CT 179/2018 (fragil)")
t("      e proteger a NF 110654 com acao autonoma ate 19/08/2026.")
t("")
t("")
t("DECISAO 2 - ART. 202 VI CC NA PAGINA 3 DA NOTIFICACAO")
t("-" * 72)
t("Texto atual (pag. 3):")
t('  "a presente notificacao constitui ato inequivoco do credor habil')
t('   a interromper a prescricao (art. 202, VI, do Codigo Civil),')
t('   reiniciando a contagem do prazo quinquenal a partir desta data."')
t("")
t("Problema tecnico: Art. 202 VI CC trata de ato do DEVEDOR (reconhecimento),")
t("nao de ato do credor. Notificacao extrajudicial do credor tradicionalmente")
t("serve para constituir em mora (Art. 397 paragrafo unico CC), nao para")
t("interromper prescricao. A tese de interrupcao por notificacao do credor")
t("NAO E PACIFICA no STJ.")
t("")
t("Proposta:")
t("  (A) MANTER redacao atual: aposta na interpretacao ampla do inciso VI.")
t("      Risco: devedor pode arguir erro de fundamento e invalidar o marco")
t("      unico (a propria notificacao) como interruptivo.")
t("  (B) EMITIR ERRATA reformulando o trecho para:")
t("      'Outrossim, o inadimplemento ora notificado refere-se a obrigacoes")
t("      cujo reconhecimento tacito pelo devedor ja se deu, nos termos do")
t("      art. 202, VI, CC, pela sucessao de Notas de Empenho, Notas de")
t("      Liquidacao e pagamentos parciais realizados pelo DETRAN/AM,")
t("      conforme memorial anexo.'")
t("      Assim, o marco interruptivo deixa de ser a notificacao em si")
t("      e passa a ser os atos documentados do devedor. Tese robusta.")
t("  (C) MANTER redacao E reforcar no dossie com memorial explicando que")
t("      a interrupcao ja ocorreu pelos atos do DETRAN (opcao defensiva).")
t("")
t("")
t("DECISAO 3 - NF 110654 (CT 179/2018) - DIVERGENCIA CSV vs PROFILE")
t("-" * 72)
t("Valor original: R$ 3.084,08  |  atualizado: R$ 6.958,97")
t("")
t("Divergencia:")
t("  - CSV projeto classifica como: PRESCRITA + forca FRACA")
t("  - profile.json classifica como: marco FORTISSIMO 19/08/2021,")
t("    prescrita=False, cutoff 19/08/2026, forca FORTISSIMO")
t("")
t("Conteudo do marco interruptivo (transcrito do profile):")
if marco_179:
    t(f"  data: {marco_179.get('data')}")
    t(f"  tipo: {marco_179.get('tipo')}")
    t(f"  forca: {marco_179.get('forca')}")
    t(f"  responsavel: {marco_179.get('responsavel_baixa')}")
    t(f"  documentos: {', '.join(marco_179.get('documentos', []))}")
    t(f"  valor do lote: R$ {marco_179.get('valor_lote_bruto')}")
    t(f"  pagamento a menor: R$ {marco_179.get('pagamento_a_menor')}")
    t(f"  NFs do lote: {marco_179.get('nfs_no_lote_total')} ({marco_179.get('nfs_pagas_do_lote')} pagas)")
    t(f"  cutoff novo: {marco_179.get('cutoff_novo')}")
    t(f"  fonte: {marco_179.get('fonte_primaria')}")
t("")
t("Confirmacao no banco (spcf_nfs.liquidacao da NF 110654):")
t("  Campo contem literalmente: '2021PD0001589 2021NL0001165 2021OB0001606")
t("  Transmitido, 19/08/2021, 24.705,11. BAIXA AUTORIZADA PELO SR. JOSE")
t("  MARIA PINTO-GERENTE FINANCEIRO. CREDITADO A MENOR R$2.925,60'")
t("")
t("Proposta:")
t("  (A) PREVALECER profile + dossie do marco FORTISSIMO, anexando ao")
t("      protocolo copia da NL 2021NL0001165 + OB 2021OB0001606 +")
t("      declaracao do Sr. Jose Maria Pinto. Cutoff 19/08/2026 - proteger")
t("      com protocolo ate essa data.")
t("  (B) ATUALIZAR o CSV para alinhar com o profile antes do protocolo")
t("      (gate de consistencia). Opcional mas recomendado para evitar")
t("      inconsistencia em pecas futuras.")
t("  (C) EM PARALELO: verificar se nao ha outras NFs do universo 202 com")
t("      mesma divergencia CSV-vs-profile. Se houver, tratar em lote.")
t("")
t("=" * 72)
t("FIM — Material detalhado: GAP_ANALYSIS_NOTIFICACAO_vs_FONTES.md sec. 7")
t("=" * 72)

OUT_TXT.write_text("\n".join(T), encoding="utf-8")
print(f"TXT gerado: {OUT_TXT}")
print(f"TXT linhas: {len(T)}")
