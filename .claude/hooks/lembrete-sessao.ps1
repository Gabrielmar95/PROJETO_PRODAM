# SessionStart hook (local/Windows): injeta as regras críticas do Projeto PRODAM
# no contexto da sessão. O par session-start.sh cobre apenas sessões remotas (cloud);
# este cobre o desenvolvimento primário (Windows + PowerShell).
#
# Invariante: SEMPRE exit 0 — um hook nunca pode derrubar ou atrasar a sessão.

$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

@"
=== REGRAS CRÍTICAS — PROJETO PRODAM (Contrato 002/2026) ===
1. PDFs são PROVAS JURÍDICAS: nunca apagar, mover ou renomear PDFs nem pastas de devedores.
2. Fontes autoritativas (SSOT): PRODAM_DOCS/profiles.json e prodam.db — nunca inventar dado de devedor; nunca usar o Demonstrativo Excel como fonte de valores.
3. REsp 793.969/RJ: citar SEMPRE 'Rel. p/ acórdão Min. José Delgado' (Min. Teori Zavascki foi VENCIDO).
4. RPV/AM: Lei estadual 2.748/2002 — teto de 20 salários mínimos (60 SM é o teto FEDERAL; não aplicar contra o Estado).
5. Correção DETRAN é POR CONTRATO (profiles.json -> DETRAN.contratos[*].regime_aplicavel): CT 022/2014 (e 025/027 de 2014) = IGPM + 1% a.m. + 2% (CDC); contratos silentes (10/2021, 17/2015, 60/2022, 71/2022) = Tema 810/STF + SELIC (Lei 14.905/2024).
6. NUNCA usar a multa de 1%/dia da Cláusula 12.3.2 — ela protege o DETRAN (contratante), não a PRODAM.
7. Jurisprudência: citar SÓ o catálogo REFERENCIA_JURIDICA/11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md — nunca inventar precedente, índice ou valor.
8. Valores BRL: Decimal sempre (nunca float); formatar via prodam_utils.fmt_brl.
9. Prescrição é por fatura individual, contada do vencimento — alertas vigentes: SSP e SUHAB em 30/06/2026; SEJUSC em 31/08/2026.
=============================================================
"@ | Write-Output

exit 0
