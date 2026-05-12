# PreToolUse hook: bloqueia remoção de PDFs (provas jurídicas do Projeto PRODAM).
# Regra cardinal do CLAUDE.md global: "PDFs são provas jurídicas, nunca apagar".
#
# Estratégia em 2 camadas:
#   1. Comando combina verbo de remoção (Remove-Item/rm/del/ri/rmdir/::Delete) com `.pdf` explícito → BLOQUEIA.
#   2. Comando usa Remove-Item|rm com -Recurse / -rf / -R em pasta de evidência conhecida
#      (PRODAM, AUDITORIA, DETRAN, SEDUC, FUHAM, spcf, pdfs, _Certidoes, PRODAM_DOCS) → BLOQUEIA.
#
# Caminhos de fuga: se você precisa REALMENTE remover um PDF, faça via Explorer/Lixeira manualmente,
# ou desative temporariamente este hook em settings.json.

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

    $deleteVerb = '(?i)(\bRemove-Item\b|\brm\b|\bdel\b|\bri\b|\brmdir\b|::Delete\b)'
    $pdfRef     = '(?i)\.pdf\b'

    $reason = $null

    if ($cmd -match $deleteVerb -and $cmd -match $pdfRef) {
        $reason = "Comando contém verbo de remoção + referência a '.pdf'. PDFs são provas jurídicas (CLAUDE.md). Para apagar, use Explorer/Lixeira manualmente."
    }
    elseif ($cmd -match '(?i)(Remove-Item|rm)\b[^|]*?\s-(Recurse|rf|R)\b' -and
            $cmd -match '(?i)(PRODAM|AUDITORIA|DETRAN|SEDUC|FUHAM|PRODAM_DOCS|spcf|_Certidoes|\\pdfs?\\)') {
        $reason = "Remove-Item -Recurse em pasta de evidência (PRODAM/AUDITORIA/DETRAN/SEDUC/FUHAM/spcf/pdfs). Pode conter PDFs probatórios. Bloqueado por segurança."
    }

    if ($null -ne $reason) {
        $output = [ordered]@{
            hookSpecificOutput = [ordered]@{
                hookEventName            = 'PreToolUse'
                permissionDecision       = 'deny'
                permissionDecisionReason = $reason
            }
        }
        $output | ConvertTo-Json -Depth 6 -Compress
        exit 0
    }

    exit 0
}
catch {
    [Console]::Error.WriteLine("block_pdf_delete error: $($_.Exception.Message)")
    exit 0
}
