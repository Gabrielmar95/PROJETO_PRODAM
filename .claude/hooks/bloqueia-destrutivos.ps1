# PreToolUse hook (Bash|PowerShell): bloqueia comandos destrutivos contra ativos críticos.
# Complementa block_pdf_delete.ps1 (que cuida só de PDFs): este cobre também
# prodam.db, profiles.json e as pastas de devedores/evidências.
#
# Regra cardinal do projeto: PDFs são provas jurídicas; profiles.json e prodam.db
# são as fontes autoritativas (SSOT). Nada disso pode ser apagado, movido ou
# sobrescrito por comando de shell sem ação humana deliberada.
#
# Saída: JSON com permissionDecision=deny (bloqueio) ou exit 0 silencioso (libera).
# Invariante: NUNCA derrubar a sessão — qualquer erro interno => exit 0.

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding  = [System.Text.UTF8Encoding]::new($false)

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }

    $payload = $stdin | ConvertFrom-Json
    $tool = $payload.tool_name
    if ($tool -ne 'Bash' -and $tool -ne 'PowerShell') { exit 0 }

    $cmd = $payload.tool_input.command
    if ([string]::IsNullOrEmpty($cmd)) { exit 0 }

    # Verbos destrutivos: remoção, movimentação e renomeação (shell sh e PowerShell).
    $verboDestrutivo = '(?i)(\bRemove-Item\b|\bMove-Item\b|\bRename-Item\b|\brm\b|\bdel\b|\bri\b|\brmdir\b|\brd\b|\bmv\b|\bmove\b|\bren\b|::Delete\b|::Move\b|\bshutil\.rmtree\b|\bos\.remove\b|\bos\.rename\b)'

    # Alvos protegidos: SSOT + pastas de devedores/evidências.
    $alvoProtegido = '(?i)(\.pdf\b|prodam\.db|profiles\.json|PRODAM_DOCS|DOSSIES_MULTIFORMATO|SPCF_EXTRACAO|AUDITORIA_COMPLETUDE|DOCUMENTOS_GERADOS|DETRAN_AUDITORIA|DETRAN_CONSOLIDADO|DETRAN_CONTRATOS|SEDUC_AUDITORIA|REFERENCIA_JURIDICA|_ARCHIVE\b)'

    if ($cmd -match $verboDestrutivo -and $cmd -match $alvoProtegido) {
        $motivo = "BLOQUEADO (bloqueia-destrutivos.ps1): comando destrutivo sobre ativo protegido do Projeto PRODAM (PDF, prodam.db, profiles.json ou pasta de devedor). PDFs são provas jurídicas e profiles.json/prodam.db são SSOT. Se a operação é realmente necessária, faça manualmente pelo Explorer ou desative este hook em .claude/settings.json com aprovação do advogado responsável."
        $out = @{
            hookSpecificOutput = @{
                hookEventName            = 'PreToolUse'
                permissionDecision       = 'deny'
                permissionDecisionReason = $motivo
            }
        } | ConvertTo-Json -Depth 5 -Compress
        Write-Output $out
        exit 0
    }

    exit 0
}
catch {
    # Falha interna do hook jamais bloqueia a sessão.
    exit 0
}
