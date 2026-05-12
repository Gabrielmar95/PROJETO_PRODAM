# TEXTO PARA COLAR NAS PROJECT INSTRUCTIONS
# (Configurações do Projeto no Cowork → Project Instructions)
# Copie TUDO abaixo desta linha:
# ─────────────────────────────────────────────

Projeto PRODAM — Recuperação de créditos (Contrato 002/2026).
Escritório Brandão Ozores. Portfólio: ~67 devedores, ~R$ 121M exigível.

SSOT: PRODAM_DOCS/profiles.json (NUNCA usar Demonstrativo Excel).
Base jurídica: PRODAM_DOCS/REFERENCIA_JURIDICA/ (20 subpastas).
Banco: prodam.db (SQLite, 8 tabelas). Queries: consultas.py.

REGRA 1 — RACIOCÍNIO JURÍDICO:
Toda análise DEVE consultar REFERENCIA_JURIDICA/ antes de emitir parecer.
NUNCA invente jurisprudência, artigos de lei ou precedentes.
Use PRECEDENTES_VERIFICADOS.md como fonte verificada.

REGRA 2 — DADOS:
Valores em BRL (R$), Decimal (nunca float), UTF-8.
profiles.json é a fonte autoritativa para valores e status dos devedores.

REGRA 3 — CLAUDE.md AUTO-GERADO:
O CLAUDE.md da pasta do projeto é gerado por auto_update_claude_md.py.
NO INÍCIO DE CADA SESSÃO, rode: py -3.12 auto_update_claude_md.py
Isso garante que métricas, alertas e pipeline estejam atualizados.

REGRA 4 — CORREÇÕES VERIFICADAS:
- Fee: 20% (não 30%)
- RPV AM estadual: 20 SM / R$ 32.420 (não 60 SM federal)
- REsp 793.969/RJ relator: José Delgado p/ acórdão (Teori Zavascki foi vencido, não Luiz Fux)
- Tema 1.109/STJ: gestor NÃO renuncia tacitamente a prescrição
- Art. 202 CC: interrupção só ocorre UMA VEZ (unicidade)
- Decreto 53.464/2026 (NÃO CONFIRMADO — não usar sem verificar)
- Banco Master: habilitação em liquidação (não execução)

Para consultar dados: py -3.12 consultas.py <nome_query>
Para queries SQL diretas: sqlite3 no prodam.db.
