# ================================================================
# CONSOLIDACAO DE SCRIPTS DUPLICADOS - PROJETO PRODAM
# Gerado em: 2026-04-22T03:51:16
# ================================================================
# Estrategia:
#   IDENTICOS  -> deleta copias, mantem canonical
#   DRIFT_LEVE -> arquiva copias antigas em _ARQUIVO_DRIFT
#   DRIFT_GRAVE -> arquiva copias antigas, AVISA p/ revisao manual
# Cada acao pede confirmacao.
# ================================================================

$ErrorActionPreference = 'Stop'
$BASE = 'C:\Users\gabri\Desktop\PROJETO_PRODAM'
$ARQUIVO_DRIFT = Join-Path $BASE '_ARQUIVO_DRIFT'

function Confirmar($msg) {
    $r = Read-Host "$msg [s/N]"
    return $r -eq 's' -or $r -eq 'S'
}

New-Item -ItemType Directory -Path $ARQUIVO_DRIFT -Force | Out-Null

$total_deletados = 0
$total_arquivados = 0

# ===== auto_update_claude_md.py (IDENTICOS, 3 copias) =====
# Canonical: auto_update_claude_md.py
if (Confirmar 'DELETAR 2 copia(s) identica(s) de auto_update_claude_md.py?') {
    Remove-Item (Join-Path $BASE 'PRODAM_DOCS\auto_update_claude_md.py') -Force
    Write-Host '  deletado: PRODAM_DOCS\auto_update_claude_md.py' -ForegroundColor Yellow
    $total_deletados++
    Remove-Item (Join-Path $BASE 'scripts\auto_update_claude_md.py') -Force
    Write-Host '  deletado: scripts\auto_update_claude_md.py' -ForegroundColor Yellow
    $total_deletados++
}

# ===== consultas.py (DRIFT_LEVE, 2 copias) =====
# Canonical: scripts\consultas.py
if (Confirmar 'ARQUIVAR 1 copia(s) com drift de consultas.py em _ARQUIVO_DRIFT?') {
    Move-Item (Join-Path $BASE 'PRODAM_DOCS\consultas.py') (Join-Path $ARQUIVO_DRIFT 'PRODAM_DOCS_consultas.py') -Force
    Write-Host '  arquivado: PRODAM_DOCS\consultas.py' -ForegroundColor Cyan
    $total_arquivados++
}

# ===== gerar_trd_sead.py (DRIFT_LEVE, 2 copias) =====
# Canonical: PRODAM_DOCS\_SKILLS\dossie-juridico-prodam-workspace\iteration-1\eval-3-trd-sead\gerar_trd_sead.py
if (Confirmar 'ARQUIVAR 1 copia(s) com drift de gerar_trd_sead.py em _ARQUIVO_DRIFT?') {
    Move-Item (Join-Path $BASE 'scripts\gerar_trd_sead.py') (Join-Path $ARQUIVO_DRIFT 'scripts_gerar_trd_sead.py') -Force
    Write-Host '  arquivado: scripts\gerar_trd_sead.py' -ForegroundColor Cyan
    $total_arquivados++
}

# ===== orgao_pipeline_completa.py (DRIFT_LEVE, 2 copias) =====
# Canonical: scripts\orgao_pipeline_completa.py
if (Confirmar 'ARQUIVAR 1 copia(s) com drift de orgao_pipeline_completa.py em _ARQUIVO_DRIFT?') {
    Move-Item (Join-Path $BASE 'PRODAM_DOCS\orgao_pipeline_completa.py') (Join-Path $ARQUIVO_DRIFT 'PRODAM_DOCS_orgao_pipeline_completa.py') -Force
    Write-Host '  arquivado: PRODAM_DOCS\orgao_pipeline_completa.py' -ForegroundColor Cyan
    $total_arquivados++
}

# ===== prodam_utils.py (IDENTICOS, 2 copias) =====
# Canonical: PRODAM_DOCS\prodam_utils.py
if (Confirmar 'DELETAR 1 copia(s) identica(s) de prodam_utils.py?') {
    Remove-Item (Join-Path $BASE 'scripts\prodam_utils.py') -Force
    Write-Host '  deletado: scripts\prodam_utils.py' -ForegroundColor Yellow
    $total_deletados++
}

Write-Host ''
Write-Host "[OK] Deletados: $total_deletados | Arquivados: $total_arquivados" -ForegroundColor Green
Write-Host 'Rode: py -3.12 sincronizar_prodam.py para validar.' -ForegroundColor Cyan