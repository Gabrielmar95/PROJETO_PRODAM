# ================================================================
# RECONCILIACAO SSOT x PASTAS - PROJETO PRODAM
# Gerado em: 2026-04-22T03:48:25
# ================================================================
# ATENCAO: Este script faz RENOMES e MOVIMENTACOES.
# Ele NAO executa nada sem sua confirmacao (Read-Host).
# Revise cada bloco e comente/descomente conforme necessario.
# ================================================================

$ErrorActionPreference = 'Stop'
$BASE = 'C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS'
$BACKUP = 'C:\Users\gabri\Desktop\PROJETO_PRODAM\_BACKUP_RECONCILIACAO_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
$ARQUIVO_ORFA = Join-Path $BASE '_ARQUIVO_ORFA'

function Confirmar($msg) {
    $r = Read-Host "$msg [s/N]"
    return $r -eq 's' -or $r -eq 'S'
}

Write-Host '[1/4] Criando backup...' -ForegroundColor Cyan
if (Confirmar 'Criar snapshot do estado atual em ' + $BACKUP + '?') {
    New-Item -ItemType Directory -Path $BACKUP -Force | Out-Null
    Get-ChildItem $BASE -Directory | ForEach-Object {
        $nome = $_.Name
        "$BASE\$nome" | Out-File -FilePath (Join-Path $BACKUP 'estado_inicial.txt') -Append
    }
    Write-Host '  OK' -ForegroundColor Green
}

Write-Host '[2/4] A) Pastas fantasma (COMPOSITE_SPLIT) - requer decisao manual' -ForegroundColor Yellow
# --- SES/SUSAM ---
# Pastas afetadas: ['SES']
# SUGESTAO: Consolidar pastas [SES] em única canonical 'SESSUSAM' (ou manter como filhas e fazer profiles.json apontar para múltiplas)
# Descomente e ajuste:
# Rename-Item (Join-Path $BASE 'SES_CONSOLIDADO') '<NOVO_NOME>_CONSOLIDADO'

# --- FUAM/FUHAM ---
# Pastas afetadas: ['FUAM', 'FUHAM']
# SUGESTAO: Consolidar pastas [FUAM, FUHAM] em única canonical 'FUAMFUHAM' (ou manter como filhas e fazer profiles.json apontar para múltiplas)
# Descomente e ajuste:
# Rename-Item (Join-Path $BASE 'FUAM_CONSOLIDADO') '<NOVO_NOME>_CONSOLIDADO'
# Rename-Item (Join-Path $BASE 'FUHAM_CONSOLIDADO') '<NOVO_NOME>_CONSOLIDADO'

# --- FAAR/SEDEL ---
# Pastas afetadas: ['SEDEL', 'FAAR']
# SUGESTAO: Consolidar pastas [FAAR, SEDEL] em única canonical 'FAARSEDEL' (ou manter como filhas e fazer profiles.json apontar para múltiplas)
# Descomente e ajuste:
# Rename-Item (Join-Path $BASE 'SEDEL_CONSOLIDADO') '<NOVO_NOME>_CONSOLIDADO'
# Rename-Item (Join-Path $BASE 'FAAR_CONSOLIDADO') '<NOVO_NOME>_CONSOLIDADO'

# --- BANCO MASTER ---
# Pastas afetadas: ['MASTER']
# SUGESTAO: Consolidar pastas [MASTER] em única canonical 'BANCOMASTER' (ou manter como filhas e fazer profiles.json apontar para múltiplas)
# Descomente e ajuste:
# Rename-Item (Join-Path $BASE 'MASTER_CONSOLIDADO') '<NOVO_NOME>_CONSOLIDADO'

# --- IKM DE ---
# Pastas afetadas: ['IKM']
# SUGESTAO: Consolidar pastas [IKM] em única canonical 'IKMDE' (ou manter como filhas e fazer profiles.json apontar para múltiplas)
# Descomente e ajuste:
# Rename-Item (Join-Path $BASE 'IKM_CONSOLIDADO') '<NOVO_NOME>_CONSOLIDADO'

# --- B23 TECNOLOGIA ---
# Pastas afetadas: ['B23']
# SUGESTAO: Consolidar pastas [B23] em única canonical 'B23TECNOLOGIA' (ou manter como filhas e fazer profiles.json apontar para múltiplas)
# Descomente e ajuste:
# Rename-Item (Join-Path $BASE 'B23_CONSOLIDADO') '<NOVO_NOME>_CONSOLIDADO'

# --- PSA TECHNOLOGY ---
# Pastas afetadas: ['PSA']
# SUGESTAO: Consolidar pastas [PSA] em única canonical 'PSATECHNOLOGY' (ou manter como filhas e fazer profiles.json apontar para múltiplas)
# Descomente e ajuste:
# Rename-Item (Join-Path $BASE 'PSA_CONSOLIDADO') '<NOVO_NOME>_CONSOLIDADO'

Write-Host '[3/4] C) SSOT sem pasta - criar estrutura vazia (9 subpastas)' -ForegroundColor Yellow
$SUBPASTAS = @('01_CONTRATOS','02_EMPENHOS','03_FATURAS','04_NOTAS_LIQUIDACAO','05_ACEITES','06_COBRANCAS','07_SCRAPING_SPCF','08_PDFS_ORIGINAIS','09_RELATORIOS')
if (Confirmar 'Criar pasta ASSOCDEGESTAOINOVACAOERESEMSAUDE_CONSOLIDADO (SSOT: ASSOC. DE GESTÃO INOVAÇÃO E RES. EM SAÚDE)?') {
    $p = Join-Path $BASE 'ASSOCDEGESTAOINOVACAOERESEMSAUDE_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: ASSOCDEGESTAOINOVACAOERESEMSAUDE_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Criar pasta METADATA_CONSOLIDADO (SSOT: _metadata)?') {
    $p = Join-Path $BASE 'METADATA_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: METADATA_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Criar pasta UGPI_CONSOLIDADO (SSOT: UGPI)?') {
    $p = Join-Path $BASE 'UGPI_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: UGPI_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Criar pasta FMPES_CONSOLIDADO (SSOT: FMPES)?') {
    $p = Join-Path $BASE 'FMPES_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: FMPES_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Criar pasta SETRAB_CONSOLIDADO (SSOT: SETRAB)?') {
    $p = Join-Path $BASE 'SETRAB_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: SETRAB_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Criar pasta AADESAM_CONSOLIDADO (SSOT: AADESAM)?') {
    $p = Join-Path $BASE 'AADESAM_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: AADESAM_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Criar pasta FJJA_CONSOLIDADO (SSOT: FJJA)?') {
    $p = Join-Path $BASE 'FJJA_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: FJJA_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Criar pasta BANCODAYCOVAL_CONSOLIDADO (SSOT: BANCO DAYCOVAL)?') {
    $p = Join-Path $BASE 'BANCODAYCOVAL_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: BANCODAYCOVAL_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Criar pasta BRADESCO_CONSOLIDADO (SSOT: BRADESCO)?') {
    $p = Join-Path $BASE 'BRADESCO_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: BRADESCO_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Criar pasta SALUX_CONSOLIDADO (SSOT: SALUX)?') {
    $p = Join-Path $BASE 'SALUX_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: SALUX_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Criar pasta BRADESCOFINANCIAMENTO_CONSOLIDADO (SSOT: BRADESCO FINANCIAMENTO)?') {
    $p = Join-Path $BASE 'BRADESCOFINANCIAMENTO_CONSOLIDADO'
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    foreach ($sub in $SUBPASTAS) { New-Item -ItemType Directory -Path (Join-Path $p $sub) -Force | Out-Null }
    Write-Host '  Criada: BRADESCOFINANCIAMENTO_CONSOLIDADO' -ForegroundColor Green
}

Write-Host '[4/4] D) Pastas orfas - mover para _ARQUIVO_ORFA' -ForegroundColor Yellow
New-Item -ItemType Directory -Path $ARQUIVO_ORFA -Force | Out-Null
if (Confirmar 'Arquivar ALEAM_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'ALEAM_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'ALEAM_CONSOLIDADO') -Force
    Write-Host '  Arquivada: ALEAM_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar AMAZONASTUR_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'AMAZONASTUR_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'AMAZONASTUR_CONSOLIDADO') -Force
    Write-Host '  Arquivada: AMAZONASTUR_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar ASSOC_SAUDE_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'ASSOC_SAUDE_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'ASSOC_SAUDE_CONSOLIDADO') -Force
    Write-Host '  Arquivada: ASSOC_SAUDE_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar CIAMA_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'CIAMA_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'CIAMA_CONSOLIDADO') -Force
    Write-Host '  Arquivada: CIAMA_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar DEFESA_CIVIL_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'DEFESA_CIVIL_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'DEFESA_CIVIL_CONSOLIDADO') -Force
    Write-Host '  Arquivada: DEFESA_CIVIL_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar FAPEAM_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'FAPEAM_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'FAPEAM_CONSOLIDADO') -Force
    Write-Host '  Arquivada: FAPEAM_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar FEPIAM_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'FEPIAM_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'FEPIAM_CONSOLIDADO') -Force
    Write-Host '  Arquivada: FEPIAM_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar IMPRENSA_OFICIAL_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'IMPRENSA_OFICIAL_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'IMPRENSA_OFICIAL_CONSOLIDADO') -Force
    Write-Host '  Arquivada: IMPRENSA_OFICIAL_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar JUCEA_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'JUCEA_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'JUCEA_CONSOLIDADO') -Force
    Write-Host '  Arquivada: JUCEA_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar PGJ_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'PGJ_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'PGJ_CONSOLIDADO') -Force
    Write-Host '  Arquivada: PGJ_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar PROCON_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'PROCON_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'PROCON_CONSOLIDADO') -Force
    Write-Host '  Arquivada: PROCON_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar SECOM_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'SECOM_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'SECOM_CONSOLIDADO') -Force
    Write-Host '  Arquivada: SECOM_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar SEDURB_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'SEDURB_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'SEDURB_CONSOLIDADO') -Force
    Write-Host '  Arquivada: SEDURB_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar SEPA_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'SEPA_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'SEPA_CONSOLIDADO') -Force
    Write-Host '  Arquivada: SEPA_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar SUBCOMADEC_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'SUBCOMADEC_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'SUBCOMADEC_CONSOLIDADO') -Force
    Write-Host '  Arquivada: SUBCOMADEC_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar TCE_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'TCE_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'TCE_CONSOLIDADO') -Force
    Write-Host '  Arquivada: TCE_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar UEA_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'UEA_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'UEA_CONSOLIDADO') -Force
    Write-Host '  Arquivada: UEA_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar UGPE_CONSOLIDADO em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'UGPE_CONSOLIDADO') (Join-Path $ARQUIVO_ORFA 'UGPE_CONSOLIDADO') -Force
    Write-Host '  Arquivada: UGPE_CONSOLIDADO' -ForegroundColor Green
}
if (Confirmar 'Arquivar ALEAM_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'ALEAM_DOSSIE') (Join-Path $ARQUIVO_ORFA 'ALEAM_DOSSIE') -Force
    Write-Host '  Arquivada: ALEAM_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar AMAZONASTUR_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'AMAZONASTUR_DOSSIE') (Join-Path $ARQUIVO_ORFA 'AMAZONASTUR_DOSSIE') -Force
    Write-Host '  Arquivada: AMAZONASTUR_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar ASSOC_SAUDE_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'ASSOC_SAUDE_DOSSIE') (Join-Path $ARQUIVO_ORFA 'ASSOC_SAUDE_DOSSIE') -Force
    Write-Host '  Arquivada: ASSOC_SAUDE_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar CIAMA_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'CIAMA_DOSSIE') (Join-Path $ARQUIVO_ORFA 'CIAMA_DOSSIE') -Force
    Write-Host '  Arquivada: CIAMA_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar DEFESA_CIVIL_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'DEFESA_CIVIL_DOSSIE') (Join-Path $ARQUIVO_ORFA 'DEFESA_CIVIL_DOSSIE') -Force
    Write-Host '  Arquivada: DEFESA_CIVIL_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar DESCONHECIDO_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'DESCONHECIDO_DOSSIE') (Join-Path $ARQUIVO_ORFA 'DESCONHECIDO_DOSSIE') -Force
    Write-Host '  Arquivada: DESCONHECIDO_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar FAPEAM_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'FAPEAM_DOSSIE') (Join-Path $ARQUIVO_ORFA 'FAPEAM_DOSSIE') -Force
    Write-Host '  Arquivada: FAPEAM_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar FEPIAM_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'FEPIAM_DOSSIE') (Join-Path $ARQUIVO_ORFA 'FEPIAM_DOSSIE') -Force
    Write-Host '  Arquivada: FEPIAM_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar IMPRENSA_OFICIAL_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'IMPRENSA_OFICIAL_DOSSIE') (Join-Path $ARQUIVO_ORFA 'IMPRENSA_OFICIAL_DOSSIE') -Force
    Write-Host '  Arquivada: IMPRENSA_OFICIAL_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar JUCEA_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'JUCEA_DOSSIE') (Join-Path $ARQUIVO_ORFA 'JUCEA_DOSSIE') -Force
    Write-Host '  Arquivada: JUCEA_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar PGJ_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'PGJ_DOSSIE') (Join-Path $ARQUIVO_ORFA 'PGJ_DOSSIE') -Force
    Write-Host '  Arquivada: PGJ_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar PROCON_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'PROCON_DOSSIE') (Join-Path $ARQUIVO_ORFA 'PROCON_DOSSIE') -Force
    Write-Host '  Arquivada: PROCON_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar SECOM_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'SECOM_DOSSIE') (Join-Path $ARQUIVO_ORFA 'SECOM_DOSSIE') -Force
    Write-Host '  Arquivada: SECOM_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar SEDURB_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'SEDURB_DOSSIE') (Join-Path $ARQUIVO_ORFA 'SEDURB_DOSSIE') -Force
    Write-Host '  Arquivada: SEDURB_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar SEPA_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'SEPA_DOSSIE') (Join-Path $ARQUIVO_ORFA 'SEPA_DOSSIE') -Force
    Write-Host '  Arquivada: SEPA_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar SRMM_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'SRMM_DOSSIE') (Join-Path $ARQUIVO_ORFA 'SRMM_DOSSIE') -Force
    Write-Host '  Arquivada: SRMM_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar SUBCOMADEC_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'SUBCOMADEC_DOSSIE') (Join-Path $ARQUIVO_ORFA 'SUBCOMADEC_DOSSIE') -Force
    Write-Host '  Arquivada: SUBCOMADEC_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar TCE_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'TCE_DOSSIE') (Join-Path $ARQUIVO_ORFA 'TCE_DOSSIE') -Force
    Write-Host '  Arquivada: TCE_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar UEA_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'UEA_DOSSIE') (Join-Path $ARQUIVO_ORFA 'UEA_DOSSIE') -Force
    Write-Host '  Arquivada: UEA_DOSSIE' -ForegroundColor Green
}
if (Confirmar 'Arquivar UGPE_DOSSIE em _ARQUIVO_ORFA?') {
    Move-Item (Join-Path $BASE 'UGPE_DOSSIE') (Join-Path $ARQUIVO_ORFA 'UGPE_DOSSIE') -Force
    Write-Host '  Arquivada: UGPE_DOSSIE' -ForegroundColor Green
}

Write-Host 'Pronto. Rode sincronizar_prodam.py para validar.' -ForegroundColor Cyan