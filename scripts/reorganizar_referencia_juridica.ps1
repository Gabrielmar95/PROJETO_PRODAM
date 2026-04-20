# ============================================================
# REORGANIZAÇÃO — REFERENCIA_JURIDICA
# Projeto PRODAM (Contrato 002/2026)
# Data: 14/04/2026
# ============================================================
# PROBLEMA: 7 pastas com numeração duplicada (01-07 aparecem 2x)
# SOLUÇÃO: Renumerar conforme INDEX.md (00-17 sequencial)
# ============================================================

$ErrorActionPreference = "Stop"
$base = "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\REFERENCIA_JURIDICA"

Write-Host "`n=== REORGANIZAÇÃO REFERENCIA_JURIDICA ===" -ForegroundColor Cyan
Write-Host "Base: $base`n"

# PASSO 0: Remover diretórios fantasma vazios (criados por tentativa anterior)
$ghosts = @("09_NOTA_METODOLOGICA", "10_ESTUDOS_CONSOLIDADOS", "12_MINUTAS_MODELOS", "13_EXTRACAO_CONTRATUAL", "16_AUXILIAR", "test_dir")
foreach ($g in $ghosts) {
    $p = Join-Path $base $g
    if (Test-Path $p) {
        $count = (Get-ChildItem $p -Force | Measure-Object).Count
        if ($count -eq 0) {
            Remove-Item $p -Force
            Write-Host "[LIMPO] Removido diretorio fantasma vazio: $g" -ForegroundColor DarkGray
        } else {
            Write-Host "[AVISO] $g tem $count arquivos - NAO removido" -ForegroundColor Yellow
        }
    }
}

# PASSO 1: Renomear 5 pastas com numeração duplicada
Write-Host "`n--- PASSO 1: Renomear pastas duplicadas ---" -ForegroundColor Green

$renames = @(
    @{ From = "01_NOTA_METODOLOGICA";    To = "09_NOTA_METODOLOGICA" },
    @{ From = "02_ESTUDO_CONSOLIDADO";   To = "10_ESTUDOS_CONSOLIDADOS" },
    @{ From = "04_EXTRACAO_CONTRATUAL";  To = "13_EXTRACAO_CONTRATUAL" },
    @{ From = "05_MINUTAS_MODELOS";      To = "12_MINUTAS_MODELOS" },
    @{ From = "06_AUXILIAR";             To = "16_AUXILIAR" }
)

foreach ($r in $renames) {
    $src = Join-Path $base $r.From
    $dst = Join-Path $base $r.To
    if (Test-Path $src) {
        if (Test-Path $dst) {
            Write-Host "[SKIP] $($r.To) ja existe - verificar manualmente" -ForegroundColor Yellow
        } else {
            Rename-Item $src $dst
            Write-Host "[OK] $($r.From) -> $($r.To)" -ForegroundColor Green
        }
    } else {
        Write-Host "[SKIP] $($r.From) nao encontrada (ja renomeada?)" -ForegroundColor DarkGray
    }
}

# PASSO 2: Remover 03_PESQUISA_JURISPRUDENCIAL (conteúdo já em 08)
Write-Host "`n--- PASSO 2: Remover pasta duplicada 03_PESQUISA_JURISPRUDENCIAL ---" -ForegroundColor Green

$pasta03 = Join-Path $base "03_PESQUISA_JURISPRUDENCIAL"
$arquivo08 = Join-Path $base "08_PESQUISA_JURIDICA\pesquisa_juridica.md"

if (Test-Path $pasta03) {
    if (Test-Path $arquivo08) {
        # Arquivo já existe em 08 — seguro remover 03
        Remove-Item $pasta03 -Recurse -Force
        Write-Host "[OK] 03_PESQUISA_JURISPRUDENCIAL removida (conteudo ja em 08_PESQUISA_JURIDICA)" -ForegroundColor Green
    } else {
        # Mover arquivo para 08 antes de deletar
        $src = Join-Path $pasta03 "pesquisa_juridica.md"
        Copy-Item $src $arquivo08
        Remove-Item $pasta03 -Recurse -Force
        Write-Host "[OK] pesquisa_juridica.md movido para 08, pasta 03 removida" -ForegroundColor Green
    }
} else {
    Write-Host "[SKIP] 03_PESQUISA_JURISPRUDENCIAL nao encontrada" -ForegroundColor DarkGray
}

# PASSO 3: Remover 07_PESQUISAS_MAR2026 (conteúdo já mergeado em 11)
Write-Host "`n--- PASSO 3: Remover pasta mergeada 07_PESQUISAS_MAR2026 ---" -ForegroundColor Green

$pasta07 = Join-Path $base "07_PESQUISAS_MAR2026"
$pasta11 = Join-Path $base "11_PESQUISAS_ORIGINAIS"

if (Test-Path $pasta07) {
    # Verificar se 11 tem os arquivos
    $count11 = (Get-ChildItem $pasta11 | Measure-Object).Count
    if ($count11 -ge 87) {
        Remove-Item $pasta07 -Recurse -Force
        Write-Host "[OK] 07_PESQUISAS_MAR2026 removida ($count11 arquivos ja em 11_PESQUISAS_ORIGINAIS)" -ForegroundColor Green
    } else {
        # Copiar arquivos faltantes antes de deletar
        Get-ChildItem $pasta07 | ForEach-Object {
            $dest = Join-Path $pasta11 $_.Name
            if (-not (Test-Path $dest)) {
                Copy-Item $_.FullName $dest
            }
        }
        $countFinal = (Get-ChildItem $pasta11 | Measure-Object).Count
        Remove-Item $pasta07 -Recurse -Force
        Write-Host "[OK] 07 mergeada em 11 ($countFinal arquivos), pasta removida" -ForegroundColor Green
    }
} else {
    Write-Host "[SKIP] 07_PESQUISAS_MAR2026 nao encontrada" -ForegroundColor DarkGray
}

# RESULTADO
Write-Host "`n=== RESULTADO FINAL ===" -ForegroundColor Cyan
Get-ChildItem $base -Directory | Sort-Object Name | ForEach-Object {
    $count = (Get-ChildItem $_.FullName -Force | Measure-Object).Count
    Write-Host "  $($_.Name)/ ($count arquivos)"
}

Write-Host "`n[CONCLUIDO] Reorganizacao completa. Execute 'py -3.12 auto_update_claude_md.py' para atualizar CLAUDE.md" -ForegroundColor Cyan
