# ========================================================
# ROTINA DE FIM DE SESSAO — PROJETO PRODAM
# Uso: ./FIM_SESSAO.ps1 "descricao curta do que fiz hoje"
# ========================================================

param([string]$msg = "")

if ([string]::IsNullOrWhiteSpace($msg)) {
    Write-Host "ERRO: voce precisa descrever o que fez." -ForegroundColor Red
    Write-Host "Exemplo: ./FIM_SESSAO.ps1 ""revisei notificacao v5 + gerei anexo III""" -ForegroundColor Yellow
    exit 1
}

$raiz = "C:\Users\gabri\Desktop\PROJETO_PRODAM"
Set-Location $raiz

Write-Host "`n=== ETAPA 1/4: checagem rapida da junction ===" -ForegroundColor Cyan
$pj = "C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\PRODAM_DOCS"
if (Test-Path $pj) {
    $item = Get-Item $pj -Force
    if ($item.LinkType -eq "Junction") {
        Write-Host "OK: junction intacta" -ForegroundColor Green
    } else {
        Write-Host "ALERTA: PRODAM_DOCS dentro de DETRAN virou pasta fisica de novo!" -ForegroundColor Red
        Write-Host "Avise o Claude na proxima sessao antes de fazer qualquer coisa." -ForegroundColor Red
    }
}

Write-Host "`n=== ETAPA 2/4: status do Git ===" -ForegroundColor Cyan
git status -sb

Write-Host "`n=== ETAPA 3/4: commit + push ===" -ForegroundColor Cyan
git add -A
$changes = git status --porcelain
if ($changes) {
    git commit -m "sessao: $msg"
    if ($LASTEXITCODE -eq 0) {
        git push
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: commit e push concluidos" -ForegroundColor Green
        } else {
            Write-Host "AVISO: commit OK mas push falhou — tente 'git push' manualmente" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "Nada para commitar. Sessao sem alteracoes versionadas." -ForegroundColor Yellow
}

Write-Host "`n=== ETAPA 4/4: espaco em disco ===" -ForegroundColor Cyan
Get-PSDrive C | Select-Object @{N='Livre_GB';E={[math]::Round($_.Free/1GB,1)}} | Format-Table -AutoSize

Write-Host "=== LEMBRETE FINAL ===" -ForegroundColor Magenta
Write-Host "Se mudou ESTRUTURA (nova pasta, novo SSOT, novo devedor),"
Write-Host "peca ao Claude para atualizar o CLAUDE.md antes de fechar."
Write-Host ""
Write-Host "Se so mexeu em arquivos existentes, pode fechar tranquilo." -ForegroundColor Green
Write-Host ""
