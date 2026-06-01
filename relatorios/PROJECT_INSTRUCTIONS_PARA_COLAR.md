# TEXTO PARA COLAR NAS PROJECT INSTRUCTIONS
# (Configurações do Projeto no Cowork → Project Instructions)
# Atualizado em 01/06/2026 — valores conferidos com CLAUDE.md (regen 30/05).
# Copie TUDO abaixo desta linha:
# ─────────────────────────────────────────────

Projeto PRODAM — Recuperação de créditos (Contrato 002/2026).
Escritório Brandão Ozores · Cliente PRODAM S.A. (estatal, Lei 13.303/2016).
Portfólio: 70 devedores · R$ 83.668.078,44 exigível (R$ 125.245.390,64 atualizado) · 3.477 faturas.
Fee: 20% do recuperado. Relatórios quinzenais (multa R$500/dia; 10% do crédito por prescrição perdida).

SSOT: PRODAM_DOCS/profiles.json (NUNCA usar Demonstrativo Excel antigo).
Base jurídica: PRODAM_DOCS/REFERENCIA_JURIDICA/ (20 subpastas) — consultar ANTES de qualquer parecer.
Banco: prodam.db (SQLite, 8 tabelas) via Connector sqlite-prodam. Queries: scripts/consultas.py.

REGRA 1 — JURÍDICO: nunca inventar jurisprudência/lei/precedente. Usar PRECEDENTES_VERIFICADOS.md.
REGRA 2 — DADOS: valores em Decimal (nunca float), BRL "R$ 1.234,56", UTF-8 BOM, CSV separador ";".
REGRA 3 — CLAUDE.md é auto-gerado: no início da sessão rodar `py -3.12 scripts/auto_update_claude_md.py`.
REGRA 4 — FATOS VERIFICADOS:
  - Fee 20% · RPV/AM estadual = 20 SM (Lei AM 2.748/2002) · prescrição por fatura individual.
  - REsp 793.969/RJ: relator p/ acórdão = José Delgado (Teori Zavascki foi vencido — nunca citar como relator).
  - Tema 1.109/STJ: gestor não renuncia tacitamente. Art. 202 CC: interrupção uma única vez (REsp 1.963.067/MS).
  - Empenho (NE) interrompe prescrição; NF do credor não. Decreto AM 53.464/2026 (substitui 51.084/2025; checar 4 exceções).
  - FUHAM = Fundação Alfredo da Matta · FHAJ = Fundação Hospital Adriano Jorge (nunca inverter).
REGRA 5 — Windows + PowerShell; Python `py -3.12` (sem venv); operações git destrutivas só com OK; PDFs são prova (não apagar).

⚠️ PENDÊNCIA Nº 1: a data de prescrição do profiles.json diverge do CSV e é internamente
inconsistente (SEDUC consta prescrito E com R$ 49,2M exigível). NÃO disparar cobrança em lote
por prazo sem antes reconciliar e decidir a fonte verdadeira.
