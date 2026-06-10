# PreToolUse hook (Edit|Write|MultiEdit): exige confirmação humana antes de
# editar as fontes autoritativas do Projeto PRODAM (profiles.json e prodam.db).
#
# Não bloqueia — devolve permissionDecision=ask, forçando o prompt de aprovação
# mesmo que a permissão estivesse em allow. Antes de aprovar, faça backup:
#   Copy-Item PRODAM_DOCS\profiles.json PRODAM_DOCS\profiles_BACKUP_ANTES_<motivo>.json
#
# Invariante: NUNCA derrubar a sessão — qualquer erro interno => exit 0.

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding  = [System.Text.UTF8Encoding]::new($false)

try {
    $stdin = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($stdin)) { exit 0 }

    $payload = $stdin | ConvertFrom-Json
    $tool = $payload.tool_name
    if ($tool -notin @('Edit', 'Write', 'MultiEdit', 'NotebookEdit')) { exit 0 }

    $filePath = $payload.tool_input.file_path
    if ([string]::IsNullOrEmpty($filePath)) { exit 0 }

    if ($filePath -match '(?i)(profiles\.json|prodam\.db)$') {
        $motivo = "ATENÇÃO (protege-fontes.ps1): '$filePath' é FONTE AUTORITATIVA (SSOT) do Projeto PRODAM. Antes de aprovar: (1) confirme que há backup (profiles_BACKUP_ANTES_<motivo>.json); (2) lembre que o CLAUDE.md e satélites são regenerados a partir dela; (3) prodam.db deve ser alterado por script com --apply + sync, nunca por edição direta."
        $out = @{
            hookSpecificOutput = @{
                hookEventName            = 'PreToolUse'
                permissionDecision       = 'ask'
                permissionDecisionReason = $motivo
            }
        } | ConvertTo-Json -Depth 5 -Compress
        Write-Output $out
        exit 0
    }

    exit 0
}
catch {
    exit 0
}
