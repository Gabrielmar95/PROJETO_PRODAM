#Requires -Version 7.0

# ============================================================================
# aplicar_correcoes.ps1
# Revisa interativamente cada proposta de correção gerada pelo Python
# e aplica apenas as que você aprovar. Faz backup antes de alterar.
# ============================================================================

$JsonPath = "$env:USERPROFILE\Desktop\PROJETO_PRODAM\PRODAM_DOCS\AUDITORIA_SKILLS\propostas_correcao.json"
$LogPath  = "$env:USERPROFILE\Desktop\PROJETO_PRODAM\PRODAM_DOCS\AUDITORIA_SKILLS\aplicacao_log.txt"
$BackupDir = "$env:USERPROFILE\Desktop\PROJETO_PRODAM\PRODAM_DOCS\AUDITORIA_SKILLS\backups_$(Get-Date -Format 'yyyy-MM-dd_HHmm')"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " APLICAÇÃO DE CORREÇÕES ÀS SKILLS PRODAM" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $JsonPath)) {
  Write-Host "[ERRO] Arquivo de propostas não encontrado:" -ForegroundColor Red
  Write-Host "       $JsonPath" -ForegroundColor Red
  Write-Host ""
  Write-Host "Você precisa rodar primeiro:" -ForegroundColor Yellow
  Write-Host "  python corrigir_skills_prodam.py" -ForegroundColor Yellow
  return
}

$dados = Get-Content $JsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
$total = $dados.propostas.Count

Write-Host "[OK] Carregadas $total propostas de $JsonPath" -ForegroundColor Green
Write-Host "[INFO] Backups serão salvos em: $BackupDir" -ForegroundColor Gray
Write-Host ""
Write-Host "Instruções para cada proposta:" -ForegroundColor White
Write-Host "  [A] Aprovar e aplicar" -ForegroundColor Green
Write-Host "  [P] Pular (não aplicar)" -ForegroundColor Yellow
Write-Host "  [V] Ver o arquivo completo no VS Code antes de decidir" -ForegroundColor Cyan
Write-Host "  [Q] Sair (salva progresso do que já foi aplicado)" -ForegroundColor Red
Write-Host ""
Write-Host "Tecle ENTER para começar..." -ForegroundColor White
Read-Host | Out-Null

# Garantir pasta de backups
New-Item -Path $BackupDir -ItemType Directory -Force | Out-Null

# Log header
"# Log de aplicação de correções — $(Get-Date -Format 'dd/MM/yyyy HH:mm')" | Out-File -FilePath $LogPath -Encoding UTF8
"" | Out-File -FilePath $LogPath -Append -Encoding UTF8

$aprovadas = 0
$puladas = 0
$erros = 0

for ($i = 0; $i -lt $total; $i++) {
  $p = $dados.propostas[$i]
  $pos = $i + 1

  Clear-Host
  Write-Host "============================================================" -ForegroundColor Cyan
  Write-Host " [$pos/$total] $($p.skill) — $($p.checagem)" -ForegroundColor Cyan
  Write-Host "============================================================" -ForegroundColor Cyan
  Write-Host ""
  Write-Host "Arquivo: $($p.arquivo)" -ForegroundColor Gray
  Write-Host "Tipo:    $($p.tipo)" -ForegroundColor Gray
  Write-Host "Origem:  $($p.origem)" -ForegroundColor Gray
  Write-Host ""

  if ($p.justificativa) {
    Write-Host "Justificativa:" -ForegroundColor White
    Write-Host "  $($p.justificativa)" -ForegroundColor Gray
    Write-Host ""
  }

  # Apresentação do diff varia por tipo
  if ($p.tipo -eq "substituicao_completa") {
    # Correção mecânica: mostra resumo
    Write-Host "Tipo: substituição mecânica (regex)" -ForegroundColor Cyan
    Write-Host "Número de ocorrências a substituir: $($p.n_substituicoes)" -ForegroundColor White

    # Diff linha-a-linha simples
    $linhasAntigas = $p.conteudo_antigo -split "`n"
    $linhasNovas = $p.conteudo_novo -split "`n"
    $mudancas = @()
    for ($j = 0; $j -lt $linhasAntigas.Count; $j++) {
      if ($j -lt $linhasNovas.Count -and $linhasAntigas[$j] -ne $linhasNovas[$j]) {
        $mudancas += @{ Linha = ($j + 1); Antiga = $linhasAntigas[$j]; Nova = $linhasNovas[$j] }
      }
    }
    Write-Host ""
    Write-Host "Mudanças detectadas:" -ForegroundColor White
    foreach ($m in $mudancas) {
      Write-Host ""
      Write-Host "  Linha $($m.Linha):" -ForegroundColor Gray
      Write-Host "    ANTES: " -ForegroundColor Red -NoNewline
      Write-Host $m.Antiga -ForegroundColor DarkRed
      Write-Host "    DEPOIS:" -ForegroundColor Green -NoNewline
      Write-Host " $($m.Nova)" -ForegroundColor DarkGreen
    }

  } elseif ($p.tipo -eq "substituicao_trecho") {
    # Reescrita: mostra trecho antigo vs novo
    Write-Host "ANTES:" -ForegroundColor Red
    Write-Host ("─" * 60) -ForegroundColor DarkGray
    Write-Host $p.trecho_antigo -ForegroundColor DarkRed
    Write-Host ("─" * 60) -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "DEPOIS:" -ForegroundColor Green
    Write-Host ("─" * 60) -ForegroundColor DarkGray
    Write-Host $p.trecho_novo -ForegroundColor DarkGreen
    Write-Host ("─" * 60) -ForegroundColor DarkGray

  } elseif ($p.tipo -eq "insercao") {
    # Inserção de texto novo
    Write-Host "INSERIR ANTES DA LINHA: $($p.linha_antes_de)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "TEXTO A INSERIR:" -ForegroundColor Green
    Write-Host ("─" * 60) -ForegroundColor DarkGray
    Write-Host $p.texto_a_inserir -ForegroundColor DarkGreen
    Write-Host ("─" * 60) -ForegroundColor DarkGray
  }

  Write-Host ""
  Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
  Write-Host "Aplicar esta correção?" -ForegroundColor White
  Write-Host "  [A]provar   [P]ular   [V]er arquivo   [Q]uit" -ForegroundColor White
  $resposta = (Read-Host "Resposta").ToUpper()

  if ($resposta -eq "Q") {
    Write-Host ""
    Write-Host "[INFO] Saindo. Aprovadas: $aprovadas | Puladas: $puladas | Erros: $erros" -ForegroundColor Yellow
    break
  }

  if ($resposta -eq "V") {
    code $p.arquivo
    Write-Host "VS Code aberto. Pressione ENTER depois de revisar..." -ForegroundColor Gray
    Read-Host | Out-Null
    # Repete a pergunta
    $i--
    continue
  }

  if ($resposta -eq "P") {
    $puladas++
    "[$pos] PULADA — $($p.skill) ($($p.checagem))" | Out-File -FilePath $LogPath -Append -Encoding UTF8
    continue
  }

  if ($resposta -ne "A") {
    Write-Host "[INFO] Resposta não reconhecida, pulando." -ForegroundColor Yellow
    $puladas++
    continue
  }

  # === APROVADA — aplicar a correção ===
  try {
    # 1. Backup
    $nomeBackup = "$($p.skill)_$($p.checagem)_$(Get-Date -Format 'HHmmss').md"
    $backupPath = Join-Path $BackupDir $nomeBackup
    Copy-Item $p.arquivo $backupPath -Force

    # 2. Aplicar conforme tipo
    if ($p.tipo -eq "substituicao_completa") {
      $p.conteudo_novo | Set-Content -Path $p.arquivo -Encoding UTF8 -NoNewline
    }
    elseif ($p.tipo -eq "substituicao_trecho") {
      $conteudo = Get-Content $p.arquivo -Raw -Encoding UTF8
      if ($conteudo.Contains($p.trecho_antigo)) {
        $novo = $conteudo.Replace($p.trecho_antigo, $p.trecho_novo)
        $novo | Set-Content -Path $p.arquivo -Encoding UTF8 -NoNewline
      } else {
        Write-Host "[ERRO] Trecho antigo não encontrado literalmente no arquivo." -ForegroundColor Red
        Write-Host "       Possível causa: o arquivo foi modificado desde a auditoria." -ForegroundColor Red
        $erros++
        "[$pos] ERRO — $($p.skill) ($($p.checagem)): trecho antigo não encontrado" | Out-File -FilePath $LogPath -Append -Encoding UTF8
        Write-Host "ENTER para continuar..." -ForegroundColor Gray
        Read-Host | Out-Null
        continue
      }
    }
    elseif ($p.tipo -eq "insercao") {
      $linhas = [System.Collections.ArrayList]@(Get-Content $p.arquivo -Encoding UTF8)
      $idxInserir = [int]$p.linha_antes_de - 1
      if ($idxInserir -lt 0) { $idxInserir = 0 }
      if ($idxInserir -gt $linhas.Count) { $idxInserir = $linhas.Count }
      $textoParaInserir = $p.texto_a_inserir -split "`n"
      for ($k = $textoParaInserir.Count - 1; $k -ge 0; $k--) {
        $linhas.Insert($idxInserir, $textoParaInserir[$k]) | Out-Null
      }
      $linhas | Set-Content -Path $p.arquivo -Encoding UTF8
    }

    Write-Host ""
    Write-Host "[OK] Aplicada. Backup em: $backupPath" -ForegroundColor Green
    $aprovadas++
    "[$pos] APROVADA — $($p.skill) ($($p.checagem)) — backup: $nomeBackup" | Out-File -FilePath $LogPath -Append -Encoding UTF8
    Start-Sleep -Milliseconds 800

  } catch {
    Write-Host ""
    Write-Host "[ERRO] Falha ao aplicar: $($_.Exception.Message)" -ForegroundColor Red
    $erros++
    "[$pos] ERRO — $($p.skill) ($($p.checagem)): $($_.Exception.Message)" | Out-File -FilePath $LogPath -Append -Encoding UTF8
    Write-Host "ENTER para continuar..." -ForegroundColor Gray
    Read-Host | Out-Null
  }
}

# Resumo final
Clear-Host
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " RESUMO FINAL" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Aprovadas e aplicadas: $aprovadas" -ForegroundColor Green
Write-Host "Puladas:               $puladas" -ForegroundColor Yellow
Write-Host "Erros:                 $erros" -ForegroundColor $(if ($erros -gt 0) { "Red" } else { "Gray" })
Write-Host ""
Write-Host "Backups salvos em: $BackupDir" -ForegroundColor Cyan
Write-Host "Log da sessão:     $LogPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para desfazer TUDO (voltar ao estado antes desta sessão):" -ForegroundColor Yellow
Write-Host "  Copie cada arquivo .md de $BackupDir de volta para o caminho original" -ForegroundColor Gray
Write-Host ""
Write-Host "Próximo passo sugerido: rodar novamente AUDITORIA_SKILLS_PRODAM.ps1" -ForegroundColor White
Write-Host "para confirmar que os erros foram corrigidos." -ForegroundColor White
Write-Host ""
