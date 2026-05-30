# Napkin Runbook — PROJETO_PRODAM

## Curation Rules
- Re-prioritize on every read (maior → menor importância).
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead".

## Alertas Urgentes (Highest Priority)
1. **[2026-05-10] 🟡 SES/SUSAM prescreve 2026-08-31 (113 dias) — R$ 14.748.048,96**  <!-- corrigido 2026-05-10 via cascata profiles.json — fundamento PASSO6 (Of. 129/2021 reclassificado: ato do credor não interrompe prescrição) -->
   Do instead: monitorar status MEDIA; D+113 base 10/05/2026; verificar status ENVIAR_TRD em ciclos quinzenais.
2. **[2026-04-23] Multa R$500/dia por atraso de relatório quinzenal + 10% do crédito por prescrição perdida**
   Do instead: antes de decidir deprioritizar algo, calcular se há fatura prescrevendo em < 90 dias.

## Regras Jurídicas (Project-Specific)
1. **[2026-04-23] Decreto Estadual 53.464/2026 substitui 51.084/2025**
   Do instead: nunca citar 51.084 isoladamente — sempre 53.464/2026 + verificar 4 exceções antes de ação contra Gov AM.
2. **[2026-04-23] Silêncio do devedor NÃO interrompe prescrição (Art. 202 CC taxativo)**
   Do instead: exigir ato inequívoco do devedor. NFs emitidas pelo credor não contam. Empenho (NE) do devedor = Art. 202 VI CC.
3. **[2026-04-23] Art. 202 CC: interrupção ocorre UMA VEZ (REsp 1.963.067/MS)**
   Do instead: Fazenda Pública reinicia por METADE (Dec. 20.910/1932 = 2,5 anos), não 5 anos.
4. **[2026-04-23] Prescrição é por FATURA individual, contada do VENCIMENTO**
   Do instead: Art. 189 + 206 §5º I CC. Nunca somar faturas para calcular cutoff. Skill: `analise-prescricao-creditos`.
5. **[2026-04-23] SELIC = correção + juros (não somar). IGPM = só correção**
   Do instead: consultar `config_prodam.py` para índice por devedor (SELIC padrão, FUHAM=IGPM, DETRAN=IGPM+1%+2% PRESUMIDO). Lei 14.905/2024 mudou juros — não presumir 1% a.m.
6. **[2026-04-23] Composição documental (Contrato+NE+NF+Atesto) = título executivo (REsp 793.969/RJ)**
   Do instead: validar cadeia 5 elos antes de execução. Gov Direta → precatório/RPV (Art. 100 CF); Gov Indireta concorrencial → penhora direta (Tema 253/STF).
7. **[2026-04-23] Fee = 20% (não 30%). RPV AM estadual = 20 SM (~R$ 32.420)**
   Do instead: nunca usar 30% em simulação de honorários.

## Fontes & SSOT
1. **[2026-04-23] `PRODAM_DOCS/profiles.json` é a SSOT dos devedores**
   Do instead: nunca usar Demonstrativo Excel antigo. Toda decisão cruza profiles.json primeiro.
2. **[2026-04-23] `PRECEDENTES_VERIFICADOS.md` é única fonte de jurisprudência**
   Do instead: 3 precedentes fabricados + 6 distorcidos estão listados em `references/` — consultar ANTES de citar qualquer jurisprudência. Nunca inventar.
3. **[2026-04-23] `REFERENCIA_JURIDICA/` (20 subpastas) ANTES de qualquer opinião jurídica**
   Do instead: Hierarquia — Nota Metodológica → Estudo Consolidado 002/2026 → Estudo Exaustivo → Pesquisa Jurisprudencial → Extração Contratual.
4. **[2026-04-23] prodam.db: 8 tabelas principais (não recriar schema à toa)**
   Do instead: spcf_contratos (362), spcf_empenhos (16.789), spcf_faturas (1.837), spcf_nfs (52.998), pendrive_docs (3.699), devedores (81), reclassificacao (1.261), cruzamento_spcf_pendrive (1.460). Consultar skill `schema-navigator-prodam`.

## Domain Traps (Nomenclatura)
1. **[2026-04-23] FUHAM ≠ FHAJ — NUNCA inverter**
   Do instead: FUHAM = Fundação Alfredo da Matta; FHAJ = Fundação Hospital Adriano Jorge.
2. **[2026-04-23] DETRAN e 68+ órgãos são DEVEDORES dentro do PRODAM**
   Do instead: tratar como entry em `profiles.json`, não como projeto separado. Não duplicar skills por órgão.
3. **[2026-04-23] Contrato tem 3 formatos coexistindo no disco**
   Do instead: usar skill `normalizador-contratos-prodam` antes de JOIN — `006/2021` (PDFs/spcf_contratos), `6/2021` (profiles.json), `2021/006` (outras).

## Execução & Pipeline
1. **[2026-04-23] Pipeline genérica por órgão: `py -3.12 orgao_pipeline_completa.py --orgao SEDUC`**
   Do instead: preferir a pipeline genérica antes de criar script novo. Templates DETRAN (`detran_*.py`) são copiar-e-adaptar.
2. **[2026-04-23] Comando mestre: `py -3.12 sincronizar_prodam.py`**
   Do instead: roda rebuild DB + auditoria + dossiês + skills. Executar após mudanças estruturais em profiles.json ou ingestão de novos PDFs.
3. **[2026-04-23] Score composto: 12 dimensões com pesos fixos**
   Do instead: ver `CLAUDE.md` seção "SCORE COMPOSTO"; classificação A+ ≥90 (DETRAN = 94,0 A+ benchmark).
4. **[2026-05-28] Checkout limpo/cloud roda só o que NÃO depende de PRODAM_DOCS/prodam.db**
   Do instead: em cloud (Linux, sem dataset; usa `python3`, não `py -3.12`) rodar só `pytest tests/`, `python3 scripts/validar_citacoes.py`, `python3 scripts/alerta_prescricao.py --check` (lê `profiles_resumo.csv` commitado; exit 0/1=ok, 2=CSV faltando), `compileall`/`ruff`. Scripts com `sqlite3.connect("prodam.db")` no topo (`auditoria_completude_devedor.py:25`, `dossie_multiformato_devedor.py:37`, `consultas.py:16`) crasham no import; pipeline real (`sincronizar_prodam.py`) só na máquina local. Deps de teste: `pip install -r requirements-dev.txt`. NUNCA rodar `auto_update_claude_md.py` como smoke sem DB (regenera CLAUDE.md como placeholder).

## Execução Técnica (Shell & Dados)
1. **[2026-04-23] Python é `py -3.12`, NÃO `python` nem `python3`**
   Do instead: usar launcher `py -3.12` em todos os comandos. Windows sem venv ativo.
2. **[2026-04-23] Valores monetários em `Decimal`, formato BRL `R$ 1.234,56`**
   Do instead: `from decimal import Decimal`; formatar com skill `normalizador-valores-brl`. Nunca float.
3. **[2026-04-23] CSV padrão: `;` + UTF-8 com BOM**
   Do instead: `pd.to_csv(path, sep=";", encoding="utf-8-sig")`. Validar abrindo no Excel.
4. **[2026-04-23] Salvar extrações em JSON + XLSX + CSV (JSON = SSOT)**
   Do instead: três formatos no mesmo script; JSON é autoritativo, XLSX/CSV derivados.
5. **[2026-04-23] Rate limit SPCF: `time.sleep(1.5)` entre requisições**
   Do instead: delay ≥1.5s em qualquer loop batendo no SPCF. Web scraping vive em `SPCF_EXTRACAO/`.
6. **[2026-04-23] PDFs são provas jurídicas — NUNCA apagar originais**
   Do instead: copiar/renomear/derivar; manter original em `_ARQUIVO_DRIFT/` ou `_BACKUPS/`. Qualquer remoção exige confirmação explícita do usuário.

## User Directives
1. **[2026-04-23] Responder em pt-BR, tom didático (iniciante em programação)**
   Do instead: explicar erros como para não-programador; comandos sempre em PowerShell.
2. **[2026-04-23] Um bloco único de código por vez**
   Do instead: agrupar em um bloco pronto pra colar; se der erro, devolver correção completa, não patch parcial.
3. **[2026-05-30] SEMPRE validar e testar o código ANTES de qualquer ação definitiva (commit, push, ação externa)**
   Do instead: rodar pytest/validadores e **ver o verde** antes de commit/push/ação irreversível. Se a saída do shell estiver bufferando, **esperar o flush e confirmar** — nunca disparar push "às cegas", mesmo com script auto-guardado. Validação proporcional: mudança de código → testes; mudança só-docs → read-back + escopo (`git status`).
