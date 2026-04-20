Add-Type -AssemblyName Microsoft.VisualBasic
$msg = [Microsoft.VisualBasic.Interaction]::InputBox("O que voce fez nessa sessao?`n`nExemplo: revisei notificacao v5 e corrigi CT 075", "Fim de Sessao PRODAM", "")
if ([string]::IsNullOrWhiteSpace($msg)) {
    [System.Windows.Forms.MessageBox]::Show("Cancelado. Nada foi feito.", "Fim de Sessao PRODAM") | Out-Null
    exit
}
Set-Location "C:\Users\gabri\Desktop\PROJETO_PRODAM"
& "C:\Users\gabri\Desktop\PROJETO_PRODAM\FIM_SESSAO.ps1" $msg
Write-Host "`n`n=== PRESSIONE ENTER PARA FECHAR ===" -ForegroundColor Magenta
Read-Host
