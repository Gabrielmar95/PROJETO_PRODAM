# Rastreabilidade Forense Completa — Dashboards PRODAM

**Projeto:** Recuperacao de Creditos PRODAM S.A. — Contrato 002/2026
**Escritorio:** Brandao Ozores Advogados
**Data:** 10 de abril de 2026
**Autor:** Manus AI

---

## Objetivo

Este diretorio contem o rastreamento completo e minucioso de **todos os 15 dashboards** criados para o projeto PRODAM, desde o primeiro prototipo ate a versao v8.0 final. Para cada dashboard, esta documentado:

1. De onde veio cada informacao (arquivo, campo, sistema original)
2. Qual o formato de cada fonte (JSON, CSV, Markdown, Excel, OCR)
3. Como os dados foram transformados (scripts Python/JS)
4. A evolucao entre versoes (o que foi adicionado, removido, reestruturado)
5. A cadeia de custodia completa (do pendrive ao grafico)

---

## Estrutura de Pastas

| Pasta | Conteudo | Documentacao |
|-------|----------|--------------|
| `01_DASHBOARDS/` | Todos os 15 dashboards HTML organizados em 5 fases cronologicas | `LEIA-ME.md` com descricao de cada versao |
| `02_FONTES_DE_DADOS/` | Todos os arquivos-fonte organizados por tipo (JSON, CSV, MD, PY, JS) | `LEIA-ME.md` com procedencia de cada arquivo |
| `03_RASTREABILIDADE_POR_SECAO/` | Mapeamento de cada secao do dashboard ate sua fonte | Tabelas campo-a-campo |
| `04_RASTREABILIDADE_POR_DEVEDOR/` | Mapeamento de onde encontrar dados de cada devedor | Top 6 detalhados + 19 com CSV |
| `05_EVOLUCAO_VERSOES/` | O que mudou de uma versao para outra | Transicoes detalhadas |
| `06_CADEIA_DE_CUSTODIA/` | Fluxo completo: origem bruta ate apresentacao | 5 estagios documentados |

---

## Inventario dos Dashboards

| Versao | Arquivo | Tamanho | Graficos | Devedores | Fase | Conversa |
|--------|---------|---------|----------|-----------|------|----------|
| Corporativo | DASHBOARD_PRODAM_CORPORATIVO.html | 42 KB | 4 | 0 | Prototipo | Outra |
| Sessao 54 | DASHBOARD_PRODAM_SESSAO54_JURIDICO.html | 59 KB | 5 | 0 | Prototipo | Outra |
| 2026-04-09 | dashboard_prodam_2026-04-09.html | 51 KB | 4 | 66 | Prototipo | Outra |
| v1 | DASHBOARD_PRODAM_v1_BRANDAO_OZORES.html | 1.299 KB | 4 | 15 | Consolidacao | Outra |
| v4 | DASHBOARD_PRODAM_v4_ENRIQUECIDO.html | 82 KB | 11 | 71 | Consolidacao | Outra |
| v4.1 | DASHBOARD_PRODAM_v4.1_BRANDAO_OZORES.html | 84 KB | 11 | 71 | Consolidacao | Outra |
| v5.0 | DASHBOARD_PRODAM_v5.0_BRANDAO_OZORES.html | 114 KB | 11 | 71 | Redesign | Esta (Manus) |
| v5.1 | DASHBOARD_PRODAM_v5.1_BRANDAO_OZORES.html | 149 KB | 17 | 71 | Redesign | Esta (Manus) |
| v5.2 | DASHBOARD_PRODAM_v5.2_BRANDAO_OZORES.html | 177 KB | 25 | 91 | Redesign | Esta (Manus) |
| v5.3 | DASHBOARD_PRODAM_v5.3_BRANDAO_OZORES.html | 87 KB | 20 | 71 | Redesign | Esta (Manus) |
| v6.0 | DASHBOARD_PRODAM_v6.0_BRANDAO_OZORES.html | 1.156 KB | 4 | 70 | Corporativo | Outra |
| v6.1 | DASHBOARD_PRODAM_v6.1_BRANDAO_OZORES.html | 1.162 KB | 4 | 70 | Corporativo | Outra |
| v6.2 | DASHBOARD_PRODAM_v6.2_BRANDAO_OZORES.html | 788 KB | 4 | 15 | Corporativo | Outra |
| v6.3 | DASHBOARD_PRODAM_v6.3_BRANDAO_OZORES.html | 997 KB | 4 | 15 | Corporativo | Outra |
| v8.0 | DASHBOARD_PRODAM_v8.0_BRANDAO_OZORES.html | 4.021 KB | 10 | 116 | Final | Outra |

---

## Fontes de Dados — Resumo

| Tipo | Quantidade | Exemplos | Origem Original |
|------|-----------|----------|-----------------|
| **JSON** | 13 | profiles.json, BLOCO_*.json, reconciliacao_*.json | Pendrive (OCR) + SPCF (download) + Scripts Python |
| **CSV** | 19 | SEDUC_FATURAS_CRUZADAS.csv (58 colunas cada) | Cruzamento de 14 fontes |
| **Markdown** | 13 | RECONCILIACAO_SPCF_MAR2026.md, MEMORIAL_CORRECAO.md | Relatorios e metodologias |
| **Python** | 7 | build_dashboard_v53.py, analyze_spcf_complete.py | Scripts de construcao e analise |
| **JavaScript** | 1 | dashboard_script_v50.js | Logica de renderizacao |
| **Total** | **53 arquivos-fonte** | | |

---

## Numeros Consolidados do Projeto

| Metrica | Valor | Fonte |
|---------|-------|-------|
| Devedores mapeados | 71 (v4.1-v5.3) a 116 (v8.0) | profiles.json |
| Valor exigivel total | R$ 121,5M | profiles.json (soma val_exig) |
| Valor atualizado (SELIC) | R$ 195,4M | profiles.json (soma val_atualizado) |
| Fee estimado (20%) | R$ 4,8M a R$ 16,8M | DASHBOARD_DADOS_FINAIS.json |
| Faturas cruzadas | 1.764 (58 colunas cada) | 19 CSVs |
| Registros SPCF processados | 900.537 | 247 CSVs do SPCF |
| Meses de serie historica | 87 (Jan/2019 a Mar/2026) | BLOCO_B_SERIE_HISTORICA.json |
| Dashboards criados | 15 versoes | Este inventario |
