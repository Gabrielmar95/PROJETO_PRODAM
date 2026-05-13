#Requires -Version 7.0

# ==========================================================================
# AUDITORIA JURIDICA DAS SKILLS - Projeto PRODAM
# ==========================================================================
# Referencia normativa: MANIFESTO_JURIDICO_v2026_04_rev2.md
# Gera: CSV (Excel) + MD (relatorio) + estatisticas na tela
# NAO altera nenhum arquivo. Apenas leitura.
# ==========================================================================

$inicio = Get-Date

# --- 1. CONFIGURACAO ---
$pastaSkills = "$env:USERPROFILE\.claude\skills"
$pastaSaida  = "$env:USERPROFILE\Desktop\PROJETO_PRODAM\PRODAM_DOCS\AUDITORIA_SKILLS"
$dataHoje    = Get-Date -Format "yyyy-MM-dd_HHmm"
$csvOut      = Join-Path $pastaSaida "auditoria_skills_$dataHoje.csv"
$mdOut       = Join-Path $pastaSaida "AUDITORIA_SKILLS_$dataHoje.md"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " AUDITORIA JURIDICA - PROJETO PRODAM" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# --- 2. VALIDACAO ---
if (-not (Test-Path $pastaSkills)) {
  Write-Host "[ERRO] Pasta de skills nao encontrada: $pastaSkills" -ForegroundColor Red
  Write-Host ""
  Write-Host "Possiveis causas:" -ForegroundColor Yellow
  Write-Host "  - Skills estao em outra pasta. Me passe o caminho."
  Write-Host "  - Voce ainda nao usou o Claude Code nesta maquina."
  Write-Host ""
  return
}

$skills = @(Get-ChildItem -Path $pastaSkills -Filter "SKILL.md" -Recurse -ErrorAction SilentlyContinue)

if ($skills.Count -eq 0) {
  Write-Host "[ERRO] Nenhum arquivo SKILL.md encontrado em $pastaSkills" -ForegroundColor Red
  return
}

Write-Host "[OK] Encontradas $($skills.Count) skills" -ForegroundColor Green
Write-Host "[INFO] Pasta auditada: $pastaSkills" -ForegroundColor Gray
Write-Host ""

# Criar pasta de saida (sem erro se ja existir)
New-Item -Path $pastaSaida -ItemType Directory -Force | Out-Null

# --- 3. FUNCAO AUXILIAR: NUMERO DA LINHA NO ARQUIVO ---
function Get-LinhaDoMatch {
  param([string]$Conteudo, [int]$Indice)
  # Conta quantas quebras de linha existem antes do indice
  $antes = $Conteudo.Substring(0, $Indice)
  return (($antes -split "`n").Count)
}

# --- 4. DEFINICAO DAS 8 CHECAGENS ---
# Cada checagem retorna: @{ tem_erro = bool; detalhes = string; linhas = int[] }

function Test-C01-TeoriSemDelgado {
  param([string]$Conteudo, [string]$NomeSkill)
  $r = @{ tem_erro = $false; detalhes = ""; linhas = @() }
  $matchesTeori = [regex]::Matches($Conteudo, 'Teori\s+(Albino\s+)?Zavascki', 'IgnoreCase')
  if ($matchesTeori.Count -gt 0) {
    if (-not ($Conteudo -match 'Jos[eé]\s+Delgado')) {
      $r.tem_erro = $true
      $r.detalhes = "Cita Teori Zavascki sem mencionar Jose Delgado (relator p/ acordao)"
      foreach ($hit in $matchesTeori) {
        $r.linhas += (Get-LinhaDoMatch -Conteudo $Conteudo -Indice $hit.Index)
      }
    }
  }
  return $r
}

function Test-C02-Lei2478Errada {
  param([string]$Conteudo, [string]$NomeSkill)
  $r = @{ tem_erro = $false; detalhes = ""; linhas = @() }
  $matches = [regex]::Matches($Conteudo, 'Lei\s*(n[º°\.]?\s*)?2\.?478[\/\-]?\s*200?2', 'IgnoreCase')
  if ($matches.Count -gt 0) {
    $r.tem_erro = $true
    $r.detalhes = "Cita 'Lei 2.478/2002' (ERRADO). Correto: Lei AM 2.748/2002"
    foreach ($hit in $matches) {
      $r.linhas += (Get-LinhaDoMatch -Conteudo $Conteudo -Indice $hit.Index)
    }
  }
  return $r
}

function Test-C03-TetoRPVDefasado {
  param([string]$Conteudo, [string]$NomeSkill)
  $r = @{ tem_erro = $false; detalhes = ""; linhas = @() }
  # R$ 30.360 ou 30360 (sem R$)
  $matches = [regex]::Matches($Conteudo, '(R\$\s*)?30\.?360(?!\d)')
  if ($matches.Count -gt 0) {
    $r.tem_erro = $true
    $r.detalhes = "Cita teto RPV/AM como R\$ 30.360 (defasado, era valor de 2025). Correto 2026: R\$ 32.420"
    foreach ($hit in $matches) {
      $r.linhas += (Get-LinhaDoMatch -Conteudo $Conteudo -Indice $hit.Index)
    }
  }
  return $r
}

function Test-C04-SMDefasado {
  param([string]$Conteudo, [string]$NomeSkill)
  $r = @{ tem_erro = $false; detalhes = ""; linhas = @() }
  # SM 2025 = 1518; SM 2026 = 1621
  $matches = [regex]::Matches($Conteudo, '(R\$\s*)?1\.?518(?!\d)')
  if ($matches.Count -gt 0) {
    $r.tem_erro = $true
    $r.detalhes = "Cita SM R\$ 1.518 (defasado, valor de 2025). SM 2026: R\$ 1.621"
    foreach ($hit in $matches) {
      $r.linhas += (Get-LinhaDoMatch -Conteudo $Conteudo -Indice $hit.Index)
    }
  }
  return $r
}

function Test-C05-Tema253Autarquia {
  param([string]$Conteudo, [string]$NomeSkill)
  $r = @{ tem_erro = $false; detalhes = ""; linhas = @() }
  $matchesTema = [regex]::Matches($Conteudo, 'Tema\s+253', 'IgnoreCase')
  if ($matchesTema.Count -gt 0) {
    # So flagra se a skill tambem menciona DETRAN ou autarquia
    if ($Conteudo -match 'DETRAN|autarqui') {
      $r.tem_erro = $true
      $r.detalhes = "Tema 253 STF combinado com DETRAN/autarquia. Tema 253 trata de economia mista, NAO se aplica a autarquia estadual. Autarquia segue Art. 100 CF (precatorio/RPV)"
      foreach ($hit in $matchesTema) {
        $r.linhas += (Get-LinhaDoMatch -Conteudo $Conteudo -Indice $hit.Index)
      }
    }
  }
  return $r
}

function Test-C06-Multa2pctCDC {
  param([string]$Conteudo, [string]$NomeSkill)
  $r = @{ tem_erro = $false; detalhes = ""; linhas = @() }
  $matches = [regex]::Matches($Conteudo, '(multa[\s_]*2\s*%\s*(flat|CDC)?|multa_cdc_2pct|multa[\s_]*flat)', 'IgnoreCase')
  if ($matches.Count -gt 0) {
    $r.tem_erro = $true
    $r.detalhes = "Cita multa 2% CDC/flat. Decisao 24/04/2026: tese nao aplicavel em contrato administrativo; rebaixar ou remover"
    foreach ($hit in $matches) {
      $r.linhas += (Get-LinhaDoMatch -Conteudo $Conteudo -Indice $hit.Index)
    }
  }
  return $r
}

function Test-C07-AusenciaADPF1211 {
  param([string]$Conteudo, [string]$NomeSkill)
  $r = @{ tem_erro = $false; detalhes = ""; linhas = @() }
  # Skills que DEVERIAM citar ADPF 1211/CODATA
  $skillsSensiveis = @(
    "classificacao-forca-probatoria",
    "prodam-juridico",
    "blindagem-pre-execucao",
    "montagem-dossie-comprobatorio",
    "montagem-dossie-devedor-detalhado"
  )
  if ($skillsSensiveis -contains $NomeSkill) {
    if (-not ($Conteudo -match 'ADPF\s*1\.?211' -or $Conteudo -match 'CODATA')) {
      $r.tem_erro = $true
      $r.detalhes = "Skill sensivel a natureza juridica da PRODAM nao menciona ADPF 1211/2025 (CODATA-PB, Rel. Min. Flavio Dino, 16/06/2025). Adicionar fundamentacao"
      $r.linhas = @(0)
    }
  }
  return $r
}

function Test-C08-AusenciaTema1368 {
  param([string]$Conteudo, [string]$NomeSkill)
  $r = @{ tem_erro = $false; detalhes = ""; linhas = @() }
  $skillsSensiveis = @(
    "atualizacao-monetaria-creditos",
    "atualizacao-monetaria-sob-demanda"
  )
  if ($skillsSensiveis -contains $NomeSkill) {
    if (-not ($Conteudo -match 'Tema\s+1\.?368')) {
      $r.tem_erro = $true
      $r.detalhes = "Skill de correcao monetaria nao menciona Tema 1.368 STJ (out/2025 - SELIC pre-Lei 14.905/2024). Adicionar"
      $r.linhas = @(0)
    }
  }
  return $r
}

# Tabela de todas as checagens (id -> funcao)
$todasChecagens = @(
  @{ Id = "C01"; Nome = "REsp 793.969 sem Jose Delgado";                 Funcao = 'Test-C01-TeoriSemDelgado' },
  @{ Id = "C02"; Nome = "Lei 2.478 errada (correta: 2.748)";             Funcao = 'Test-C02-Lei2478Errada' },
  @{ Id = "C03"; Nome = "Teto RPV defasado (R\$ 30.360)";                Funcao = 'Test-C03-TetoRPVDefasado' },
  @{ Id = "C04"; Nome = "SM defasado (R\$ 1.518 - era 2025)";            Funcao = 'Test-C04-SMDefasado' },
  @{ Id = "C05"; Nome = "Tema 253 aplicado a autarquia";                 Funcao = 'Test-C05-Tema253Autarquia' },
  @{ Id = "C06"; Nome = "Multa 2% CDC/flat contra DETRAN";               Funcao = 'Test-C06-Multa2pctCDC' },
  @{ Id = "C07"; Nome = "Ausencia de ADPF 1211 em skill sensivel";       Funcao = 'Test-C07-AusenciaADPF1211' },
  @{ Id = "C08"; Nome = "Ausencia de Tema 1.368 em skill de correcao";   Funcao = 'Test-C08-AusenciaTema1368' }
)

# --- 5. LOOP PRINCIPAL ---
Write-Host "[INFO] Executando $($todasChecagens.Count) checagens em $($skills.Count) skills..." -ForegroundColor Cyan
Write-Host ""

$resultados = @()
$contador = 0

foreach ($skill in $skills) {
  $contador++
  $nomeSkill = (Split-Path (Split-Path $skill.FullName) -Leaf)
  Write-Progress -Activity "Auditando skills" -Status "$contador / $($skills.Count) - $nomeSkill" -PercentComplete (($contador / $skills.Count) * 100)

  try {
    $conteudo = Get-Content $skill.FullName -Raw -Encoding UTF8 -ErrorAction Stop
  } catch {
    Write-Host "[WARN] Falha ao ler $($skill.FullName)" -ForegroundColor Yellow
    continue
  }

  if ([string]::IsNullOrEmpty($conteudo)) { continue }

  foreach ($check in $todasChecagens) {
    try {
      $resultado = & $check.Funcao -Conteudo $conteudo -NomeSkill $nomeSkill
      $resultados += [PSCustomObject]@{
        Skill      = $nomeSkill
        Arquivo    = $skill.FullName
        ChecagemId = $check.Id
        Checagem   = $check.Nome
        TemErro    = $resultado.tem_erro
        Linhas     = ($resultado.linhas -join "; ")
        Detalhes   = $resultado.detalhes
      }
    } catch {
      Write-Host "[WARN] Erro em $($check.Id) na skill $nomeSkill`: $($_.Exception.Message)" -ForegroundColor Yellow
    }
  }
}
Write-Progress -Activity "Auditando skills" -Completed

# --- 6. EXPORTAR CSV ---
$resultados | Export-Csv -Path $csvOut -Delimiter ";" -Encoding UTF8BOM -NoTypeInformation
Write-Host "[OK] CSV gerado: $csvOut" -ForegroundColor Green

# --- 7. ESTATISTICAS ---
$totalSkills   = $skills.Count
$skillsComErro = @($resultados | Where-Object TemErro | Select-Object -ExpandProperty Skill -Unique).Count
$totalErros    = @($resultados | Where-Object TemErro).Count
$pctAfetadas   = if ($totalSkills -gt 0) { [math]::Round($skillsComErro/$totalSkills*100,1) } else { 0 }

$distribPorCheck = $resultados | Where-Object TemErro | Group-Object Checagem | Select-Object Name, Count | Sort-Object Count -Descending
$rankingSkills   = $resultados | Where-Object TemErro | Group-Object Skill | Select-Object Name, Count | Sort-Object Count -Descending

# --- 8. GERAR RELATORIO MARKDOWN ---
$dataBR = Get-Date -Format "dd/MM/yyyy HH:mm"

$md = @"
# AUDITORIA JURIDICA DAS SKILLS — Projeto PRODAM

**Data da auditoria:** $dataBR
**Referencia normativa:** MANIFESTO_JURIDICO_v2026_04_rev2.md
**Pasta auditada:** `` $pastaSkills ``
**Skills analisadas:** $totalSkills

---

## RESUMO EXECUTIVO

| Metrica | Valor |
|---|---|
| Skills auditadas | $totalSkills |
| Skills com pelo menos 1 erro | $skillsComErro ($pctAfetadas%) |
| Total de erros detectados | $totalErros |

---

## DISTRIBUICAO POR TIPO DE ERRO

| Checagem | Skills afetadas |
|---|---|
"@

if ($distribPorCheck.Count -eq 0) {
  $md += "`n| (nenhum erro detectado) | 0 |"
} else {
  foreach ($d in $distribPorCheck) {
    $md += "`n| $($d.Name) | $($d.Count) |"
  }
}

$md += @"


---

## RANKING — SKILLS POR NUMERO DE ERROS (prioridade de correcao)

| Posicao | Skill | Erros |
|---|---|---|
"@

if ($rankingSkills.Count -eq 0) {
  $md += "`n| - | (nenhuma skill com erro) | - |"
} else {
  $pos = 0
  foreach ($r in $rankingSkills) {
    $pos++
    $md += "`n| $pos | ``$($r.Name)`` | $($r.Count) |"
  }
}

$md += @"


---

## DETALHAMENTO POR SKILL (apenas skills com erro)

"@

$skillsAfetadas = $resultados | Where-Object TemErro | Select-Object -ExpandProperty Skill -Unique | Sort-Object
if ($skillsAfetadas.Count -eq 0) {
  $md += "`n*Nenhuma skill apresentou erro. Todas estao alinhadas com o Manifesto v2026.04 rev.2.*`n"
} else {
  foreach ($skillNome in $skillsAfetadas) {
    $erros = @($resultados | Where-Object { $_.Skill -eq $skillNome -and $_.TemErro })
    $md += "`n### ``$skillNome`` ($($erros.Count) erro(s))`n"
    foreach ($e in $erros) {
      $linhaInfo = if ($e.Linhas -and $e.Linhas -ne "0") { " _(linha(s): $($e.Linhas))_" } else { "" }
      $md += "`n- **$($e.ChecagemId) — $($e.Checagem)**$linhaInfo`n  $($e.Detalhes)`n"
    }
  }
}

$md += @"


---

## PROXIMO PASSO — Passo 3 do plano (correcao assistida)

Este relatorio alimenta a **correcao assistida das skills com Opus 4.7**:

1. Para cada skill listada acima, o Opus 4.7 recebe:
   - A description atual da skill
   - O item correspondente do MANIFESTO_JURIDICO_v2026_04_rev2.md
   - Os trechos problematicos das linhas identificadas

2. O Opus propoe um **diff** (trecho antigo vs trecho novo) citando a fonte do Manifesto.

3. Voce, como advogado, **aprova ou ajusta cada diff** antes de aplicar.

4. So depois da revisao humana, a alteracao e aplicada ao SKILL.md.

**Custo estimado do Passo 3:** ~R\$ 15-25 em API (considerando prompt caching).

---

## LEGENDA DAS CHECAGENS

- **C01** — REsp 793.969 sem Jose Delgado: pede alteracao para "Rel. Min. Teori Zavascki, Rel. p/ acordao Min. Jose Delgado"
- **C02** — Lei 2.478 errada: corrigir para "Lei AM 2.748/2002"
- **C03** — Teto RPV defasado: substituir "R\$ 30.360" por "R\$ 32.420" (20 x SM 2026)
- **C04** — SM defasado: substituir "R\$ 1.518" por "R\$ 1.621"
- **C05** — Tema 253 em autarquia: Tema 253 aplica-se a economia mista, nao a DETRAN (autarquia -> precatorio/RPV)
- **C06** — Multa 2% CDC: tese rebaixada, nao aplicar em execucao contra DETRAN
- **C07** — Ausencia de ADPF 1211: skills sensiveis a natureza juridica da PRODAM precisam citar
- **C08** — Ausencia de Tema 1.368: skills de correcao monetaria precisam citar (SELIC pre-Lei 14.905/2024)

---

*Relatorio gerado automaticamente em $dataBR. Este arquivo NAO substitui a revisao juridica humana.*
"@

$md | Set-Content -Path $mdOut -Encoding UTF8

Write-Host "[OK] Relatorio MD gerado: $mdOut" -ForegroundColor Green

# --- 9. RESUMO NA TELA ---
$duracao = ((Get-Date) - $inicio).TotalSeconds
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " RESULTADO" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Skills auditadas:              $totalSkills" -ForegroundColor White
$corErro = if ($skillsComErro -eq 0) { "Green" } else { "Yellow" }
Write-Host "Skills com erro:               $skillsComErro ($pctAfetadas%)" -ForegroundColor $corErro
Write-Host "Total de erros detectados:     $totalErros" -ForegroundColor $corErro
Write-Host ""
if ($distribPorCheck.Count -gt 0) {
  Write-Host "Distribuicao por tipo de erro:" -ForegroundColor White
  foreach ($d in $distribPorCheck) {
    Write-Host "  - $($d.Name): $($d.Count) skills" -ForegroundColor Gray
  }
  Write-Host ""
}
Write-Host "Arquivos gerados:" -ForegroundColor White
Write-Host "  - CSV: $csvOut" -ForegroundColor Cyan
Write-Host "  - MD:  $mdOut" -ForegroundColor Cyan
Write-Host ""
Write-Host "Auditoria concluida em $([math]::Round($duracao,2))s" -ForegroundColor Green
Write-Host ""
