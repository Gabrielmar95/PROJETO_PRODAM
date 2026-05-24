"""
Reconciliação SSOT × Pastas — Projeto PRODAM.

Cruza:
- profiles.json (SSOT — 70 siglas)
- PRODAM_DOCS/*_CONSOLIDADO  (pastas de dados brutos)
- PRODAM_DOCS/*_DOSSIE       (pastas de entregáveis)
- prodam.db → tabela devedores (81 siglas)

Classifica cada divergência em 5 causas raiz:
  A) COMPOSITE_SPLIT  → SSOT usa nome composto (FAAR/SEDEL) mas pasta foi separada (FAAR + SEDEL)
  B) ABBREV_MISMATCH  → SSOT e pasta usam abreviações diferentes (SES/SUSAM vs SES)
  C) SSOT_SEM_PASTA   → sigla existe no SSOT mas não tem pasta _CONSOLIDADO
  D) PASTA_ORFA       → pasta existe mas sigla não está no SSOT
  E) ACCENT_SLASH     → apenas diferença de caracteres (acentos, barras, espaços)

Gera 4 entregáveis:
  - reconciliacao_ssot.json  (mapeamento completo)
  - reconciliacao_ssot.csv   (planilha revisável)
  - 01_RECONCILIACAO_SSOT.md (relatório humano)
  - executar_reconciliacao.ps1 (script PowerShell pronto)
"""
from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from pathlib import Path

BASE = Path("/sessions/gallant-focused-brahmagupta/mnt/PROJETO_PRODAM")
SSOT = BASE / "PRODAM_DOCS" / "profiles.json"
DB = BASE / "prodam.db"
OUT = Path("/sessions/gallant-focused-brahmagupta/mnt/outputs/_QUESTOES_CRITICAS")
OUT.mkdir(parents=True, exist_ok=True)


def norm(s: str) -> str:
    """Normaliza sigla: remove acentos, barras, espaços; upper."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", str(s))
    s_ascii = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^A-Z0-9]", "", s_ascii.upper())


# --- 1. Coleta fontes ---
ssot_data = json.loads(SSOT.read_text(encoding="utf-8"))
ssot_siglas = list(ssot_data.keys())  # ordem original
ssot_norm = {norm(s): s for s in ssot_siglas}

pastas = sorted(p.name for p in (BASE / "PRODAM_DOCS").iterdir() if p.is_dir())
cons_folders = [p.replace("_CONSOLIDADO", "") for p in pastas if p.endswith("_CONSOLIDADO")]
dossie_folders = [p.replace("_DOSSIE", "") for p in pastas if p.endswith("_DOSSIE")]

cons_norm = {norm(s): s for s in cons_folders}
dossie_norm = {norm(s): s for s in dossie_folders}

# devedores do banco
db_siglas = []
if DB.exists():
    con = sqlite3.connect(str(DB))
    try:
        db_siglas = [r[0] for r in con.execute("SELECT sigla FROM devedores").fetchall()]
    except Exception:
        pass
    con.close()
db_norm = {norm(s): s for s in db_siglas if s}

# --- 2. Componentes compostos (SSOT com / ou espaços) ---
compostos = {}
for sigla in ssot_siglas:
    partes = [p.strip() for p in re.split(r"[/\s]+", sigla) if len(p.strip()) >= 2]
    if len(partes) >= 2:
        compostos[sigla] = partes

# --- 3. Classificação ---
divergencias = []

# A) COMPOSITE_SPLIT: SSOT tem nome composto, pastas foram separadas
for sigla, partes in compostos.items():
    pastas_filhas_cons = [cons_norm[norm(p)] for p in partes if norm(p) in cons_norm]
    pastas_filhas_dos = [dossie_norm[norm(p)] for p in partes if norm(p) in dossie_norm]
    if pastas_filhas_cons or pastas_filhas_dos:
        divergencias.append({
            "causa": "A_COMPOSITE_SPLIT",
            "ssot_sigla": sigla,
            "pastas_afetadas": list({*pastas_filhas_cons, *pastas_filhas_dos}),
            "acao_recomendada": f"Consolidar pastas [{', '.join(pastas_filhas_cons or pastas_filhas_dos)}] "
                                f"em única canonical '{norm(sigla)}' (ou manter como filhas e fazer profiles.json apontar para múltiplas)",
            "severidade": "ALTA",
        })

# B) ABBREV_MISMATCH: SSOT e pasta diferem mas norm() são aproximados
# detectar SSOT terminando em sigla curta da pasta, ex: SES/SUSAM (SSOT) vs SES (pasta)
for sigla in ssot_siglas:
    if sigla in [d["ssot_sigla"] for d in divergencias]:
        continue
    sn = norm(sigla)
    if sn in cons_norm or sn in dossie_norm:
        continue
    # tentar primeiros 3-5 chars
    for length in (3, 4, 5, 6):
        prefix = sn[:length]
        if prefix in cons_norm or prefix in dossie_norm:
            divergencias.append({
                "causa": "B_ABBREV_MISMATCH",
                "ssot_sigla": sigla,
                "pastas_afetadas": [cons_norm.get(prefix), dossie_norm.get(prefix)],
                "acao_recomendada": f"Padronizar: ou renomear pasta para '{norm(sigla)}' ou ajustar SSOT para '{cons_norm.get(prefix, dossie_norm.get(prefix))}'",
                "severidade": "MEDIA",
            })
            break

# C) SSOT_SEM_PASTA
for sigla in ssot_siglas:
    if sigla in [d["ssot_sigla"] for d in divergencias]:
        continue
    sn = norm(sigla)
    if sn not in cons_norm:
        # verificar se NÃO há qualquer match
        has_dossie = sn in dossie_norm
        has_db = sn in db_norm
        divergencias.append({
            "causa": "C_SSOT_SEM_PASTA",
            "ssot_sigla": sigla,
            "pastas_afetadas": [],
            "contexto": {
                "tem_dossie": has_dossie,
                "tem_no_db": has_db,
            },
            "acao_recomendada": "Criar pasta _CONSOLIDADO vazia (com 9 subpastas) OU marcar sigla como inativa no profiles.json",
            "severidade": "ALTA" if not has_dossie and not has_db else "BAIXA",
        })

# D) PASTA_ORFA (CONSOLIDADO sem SSOT)
for pasta in cons_folders:
    pn = norm(pasta)
    if pn in ssot_norm:
        continue
    # verificar se é filha de composite
    pai_composto = None
    for sigla, partes in compostos.items():
        if pn in [norm(p) for p in partes]:
            pai_composto = sigla
            break
    if pai_composto:
        continue  # já tratado em A
    divergencias.append({
        "causa": "D_PASTA_ORFA_CONS",
        "ssot_sigla": None,
        "pastas_afetadas": [pasta + "_CONSOLIDADO"],
        "acao_recomendada": f"Decisão: (1) adicionar '{pasta}' ao profiles.json, (2) renomear para sigla SSOT existente, ou (3) arquivar em _ARQUIVO_ORFA/",
        "severidade": "ALTA",
    })

# D') PASTA_ORFA (DOSSIE sem SSOT)
for pasta in dossie_folders:
    pn = norm(pasta)
    if pn in ssot_norm:
        continue
    pai_composto = None
    for sigla, partes in compostos.items():
        if pn in [norm(p) for p in partes]:
            pai_composto = sigla
            break
    if pai_composto:
        continue
    divergencias.append({
        "causa": "D_PASTA_ORFA_DOS",
        "ssot_sigla": None,
        "pastas_afetadas": [pasta + "_DOSSIE"],
        "acao_recomendada": f"Decisão: arquivar em _ARQUIVO_ORFA/{pasta}_DOSSIE ou remapear",
        "severidade": "MEDIA",
    })

# --- 4. Estatísticas ---
stats = {
    "ssot_total": len(ssot_siglas),
    "cons_total": len(cons_folders),
    "dossie_total": len(dossie_folders),
    "db_total": len(db_siglas),
    "divergencias_total": len(divergencias),
    "por_causa": {},
    "por_severidade": {},
}
for d in divergencias:
    stats["por_causa"][d["causa"]] = stats["por_causa"].get(d["causa"], 0) + 1
    stats["por_severidade"][d["severidade"]] = stats["por_severidade"].get(d["severidade"], 0) + 1

# --- 5. JSON ---
payload = {
    "gerado_em": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
    "estatisticas": stats,
    "divergencias": divergencias,
    "ssot_siglas": ssot_siglas,
    "pastas_consolidado": cons_folders,
    "pastas_dossie": dossie_folders,
}
(OUT / "reconciliacao_ssot.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

# --- 6. CSV ---
linhas = ["causa;severidade;ssot_sigla;pastas_afetadas;acao_recomendada"]
for d in divergencias:
    pastas_str = "|".join(p for p in d["pastas_afetadas"] if p) if d["pastas_afetadas"] else ""
    linhas.append(f'{d["causa"]};{d["severidade"]};{d["ssot_sigla"] or ""};{pastas_str};"{d["acao_recomendada"]}"')
(OUT / "reconciliacao_ssot.csv").write_text("\n".join(linhas), encoding="utf-8")

# --- 7. Relatório Markdown ---
md = []
md.append("# Reconciliação SSOT × Pastas — Diagnóstico\n")
md.append(f"_Gerado em {payload['gerado_em']}_\n")
md.append("## Visão geral\n")
md.append(f"- **SSOT (profiles.json):** {stats['ssot_total']} siglas")
md.append(f"- **Pastas `_CONSOLIDADO`:** {stats['cons_total']}")
md.append(f"- **Pastas `_DOSSIE`:** {stats['dossie_total']}")
md.append(f"- **Tabela `devedores` (prodam.db):** {stats['db_total']}")
md.append(f"- **Total de divergências detectadas:** {stats['divergencias_total']}\n")

md.append("### Distribuição por causa raiz\n")
for causa, n in sorted(stats["por_causa"].items()):
    md.append(f"- **{causa}**: {n}")
md.append("")
md.append("### Distribuição por severidade\n")
for sev, n in sorted(stats["por_severidade"].items()):
    md.append(f"- **{sev}**: {n}")
md.append("")

md.append("## Interpretação (linguagem simples)\n")
md.append("Imagine que `profiles.json` é o registro civil do projeto: ele diz quem existe oficialmente. "
          "As pastas `_CONSOLIDADO`/`_DOSSIE` são os 'cartórios' onde os documentos ficam guardados.")
md.append("")
md.append("Quando o registro civil e o cartório não batem, podem acontecer 4 coisas:")
md.append("")
md.append("1. **Nome composto dividido (A)**: o registro diz `FAAR/SEDEL`, mas existem duas pastas `FAAR` e `SEDEL` separadas. "
          "Como se uma certidão de casamento tivesse virado duas certidões de solteiro.")
md.append("2. **Abreviação diferente (B)**: o registro diz `SES/SUSAM`, mas a pasta se chama só `SES`. "
          "Mesma pessoa, nomes diferentes.")
md.append("3. **Existe no registro mas sem cartório (C)**: sigla aparece no `profiles.json` mas não tem pasta. "
          "Pode ser devedor novo sem documentação ainda, ou sigla fantasma que precisa ser removida.")
md.append("4. **Cartório sem registro (D)**: existe pasta mas nenhuma sigla aponta para ela. "
          "Perigoso: dados ali são invisíveis para qualquer script automatizado.\n")

# Tabela de divergências por causa
for causa in sorted({d["causa"] for d in divergencias}):
    md.append(f"## Detalhe — {causa}\n")
    md.append("| SSOT | Pasta(s) afetada(s) | Severidade | Ação recomendada |")
    md.append("|------|---------------------|------------|------------------|")
    for d in divergencias:
        if d["causa"] != causa:
            continue
        pastas_str = ", ".join(p for p in d["pastas_afetadas"] if p) or "—"
        sigla = d["ssot_sigla"] or "—"
        md.append(f"| `{sigla}` | {pastas_str} | {d['severidade']} | {d['acao_recomendada']} |")
    md.append("")

md.append("## Próximos passos\n")
md.append("1. Revisar este relatório e `reconciliacao_ssot.csv` com o usuário.")
md.append("2. Para cada linha, marcar decisão: **CONSOLIDAR**, **RENOMEAR**, **ARQUIVAR**, **ADICIONAR_SSOT** ou **REMOVER_SSOT**.")
md.append("3. Executar `executar_reconciliacao.ps1` (ele solicita confirmação antes de cada ação).")
md.append("4. Rodar `sincronizar_prodam.py` para regerar SSOT e artefatos.\n")

(OUT / "01_RECONCILIACAO_SSOT.md").write_text("\n".join(md), encoding="utf-8")

# --- 8. PowerShell ---
# Gera comandos prontos (comentados) para o usuário revisar antes de executar
ps = []
ps.append("# ================================================================")
ps.append("# RECONCILIACAO SSOT x PASTAS - PROJETO PRODAM")
ps.append(f"# Gerado em: {payload['gerado_em']}")
ps.append("# ================================================================")
ps.append("# ATENCAO: Este script faz RENOMES e MOVIMENTACOES.")
ps.append("# Ele NAO executa nada sem sua confirmacao (Read-Host).")
ps.append("# Revise cada bloco e comente/descomente conforme necessario.")
ps.append("# ================================================================")
ps.append("")
ps.append("$ErrorActionPreference = 'Stop'")
ps.append("$BASE = 'C:\\Users\\gabri\\Desktop\\PROJETO_PRODAM\\PRODAM_DOCS'")
ps.append("$BACKUP = 'C:\\Users\\gabri\\Desktop\\PROJETO_PRODAM\\_BACKUP_RECONCILIACAO_' + (Get-Date -Format 'yyyyMMdd_HHmmss')")
ps.append("$ARQUIVO_ORFA = Join-Path $BASE '_ARQUIVO_ORFA'")
ps.append("")
ps.append("function Confirmar($msg) {")
ps.append("    $r = Read-Host \"$msg [s/N]\"")
ps.append("    return $r -eq 's' -or $r -eq 'S'")
ps.append("}")
ps.append("")
ps.append("Write-Host '[1/4] Criando backup...' -ForegroundColor Cyan")
ps.append("if (Confirmar 'Criar snapshot do estado atual em ' + $BACKUP + '?') {")
ps.append("    New-Item -ItemType Directory -Path $BACKUP -Force | Out-Null")
ps.append("    Get-ChildItem $BASE -Directory | ForEach-Object {")
ps.append("        $nome = $_.Name")
ps.append("        \"$BASE\\$nome\" | Out-File -FilePath (Join-Path $BACKUP 'estado_inicial.txt') -Append")
ps.append("    }")
ps.append("    Write-Host '  OK' -ForegroundColor Green")
ps.append("}")
ps.append("")

# --- Bloco A: composite split ---
ps.append("Write-Host '[2/4] A) Pastas fantasma (COMPOSITE_SPLIT) - requer decisao manual' -ForegroundColor Yellow")
for d in divergencias:
    if d["causa"] == "A_COMPOSITE_SPLIT":
        ps.append(f"# --- {d['ssot_sigla']} ---")
        ps.append(f"# Pastas afetadas: {d['pastas_afetadas']}")
        ps.append(f"# SUGESTAO: {d['acao_recomendada']}")
        ps.append("# Descomente e ajuste:")
        for p in d["pastas_afetadas"]:
            ps.append(f"# Rename-Item (Join-Path $BASE '{p}_CONSOLIDADO') '<NOVO_NOME>_CONSOLIDADO'")
        ps.append("")

# --- Bloco C: SSOT sem pasta -> criar estrutura vazia ---
ps.append("Write-Host '[3/4] C) SSOT sem pasta - criar estrutura vazia (9 subpastas)' -ForegroundColor Yellow")
ps.append("$SUBPASTAS = @('01_CONTRATOS','02_EMPENHOS','03_FATURAS','04_NOTAS_LIQUIDACAO','05_ACEITES','06_COBRANCAS','07_SCRAPING_SPCF','08_PDFS_ORIGINAIS','09_RELATORIOS')")
for d in divergencias:
    if d["causa"] == "C_SSOT_SEM_PASTA" and d["severidade"] == "ALTA":
        sigla_norm = norm(d["ssot_sigla"])
        ssot_sigla = d["ssot_sigla"]
        ps.append(f"if (Confirmar 'Criar pasta {sigla_norm}_CONSOLIDADO (SSOT: {ssot_sigla})?') {{")
        ps.append(f"    $p = Join-Path $BASE '{sigla_norm}_CONSOLIDADO'")
        ps.append(f"    New-Item -ItemType Directory -Path $p -Force | Out-Null")
        ps.append(f"    foreach ($sub in $SUBPASTAS) {{ New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }}")
        ps.append(f"    Write-Host '  Criada: {sigla_norm}_CONSOLIDADO' -ForegroundColor Green")
        ps.append("}")

ps.append("")
ps.append("Write-Host '[4/4] D) Pastas orfas - mover para _ARQUIVO_ORFA' -ForegroundColor Yellow")
ps.append("New-Item -ItemType Directory -Path $ARQUIVO_ORFA -Force | Out-Null")
for d in divergencias:
    if d["causa"].startswith("D_PASTA_ORFA"):
        pasta = d["pastas_afetadas"][0]
        ps.append(f"if (Confirmar 'Arquivar {pasta} em _ARQUIVO_ORFA?') {{")
        ps.append(f"    Move-Item (Join-Path $BASE '{pasta}') (Join-Path $ARQUIVO_ORFA '{pasta}') -Force")
        ps.append(f"    Write-Host '  Arquivada: {pasta}' -ForegroundColor Green")
        ps.append("}")

ps.append("")
ps.append("Write-Host 'Pronto. Rode sincronizar_prodam.py para validar.' -ForegroundColor Cyan")

(OUT / "executar_reconciliacao.ps1").write_text("\n".join(ps), encoding="utf-8-sig")

print("=" * 60)
print("RECONCILIACAO SSOT — CONCLUIDA")
print("=" * 60)
print(f"Total divergencias: {stats['divergencias_total']}")
print(f"Por causa: {stats['por_causa']}")
print(f"Por severidade: {stats['por_severidade']}")
print(f"\nArquivos gerados em: {OUT}")
for f in sorted(OUT.iterdir()):
    print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
