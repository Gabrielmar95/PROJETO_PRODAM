# PROJETO PRODAM — Recuperação de Créditos
## Contrato 002/2026 — PRODAM S.A. × Brandão Ozores Advogados
_Atualizado em 08/06/2026 12:24 via `scripts/auto_update_claude_md.py`._

> Conteúdo regenerado a cada `/sincronizar-prodam`. Para regras fixas → editar o gerador. Para métricas → editar `PRODAM_DOCS/profiles.json` e rodar `py -3.12 scripts\auto_update_claude_md.py`.

## 1. IDENTIDADE
- **Advogado**: Gabriel Mar (OAB/AM 15.697) — Gabriel Mar Sociedade Individual de Advocacia
- **Contratante**: Brandão Ozores Advogados | **Cliente**: PRODAM S.A. (CNPJ 04.407.920/0001-80, economia mista, Lei 13.303/2016)
- **Fee**: 20% sobre créditos recuperados | **Obrigações**: relatórios quinzenais (R$500/dia atraso | 10% do crédito por prescrição perdida)

## 2. STATUS DO PORTFÓLIO
- **69 devedores** (26 Gov Direta, 21 Gov Indireta, 22 Privadas)
- **R$ 83.668.078,44 exigível** | R$ 125.245.390,64 atualizado
- **3477 faturas** (2326 exigíveis, 1082 prescritas)
- **Força**: 12 FORTE · 15 MÉDIA · 42 FRACA

**Pipeline (próximo passo)**: ANALISAR_DOCUMENTACAO=36 · CLASSIFICAR=17 · ENVIAR_TRD=9 · PROTOCOLAR_PETICAO=5 · HABILITAÇÃO DE CRÉDITO=1 · AVALIAR_SUCESSAO=1

**Top 10 devedores** (por valor exigível):
- SEDUC: R$ 49.215.512,48 | FORTE | ANALISAR_DOCUMENTACAO
- SES/SUSAM: R$ 4.783.356,52 | FORTE | ENVIAR_TRD
- SSP: R$ 4.553.230,80 | FORTE | PROTOCOLAR_PETICAO
- SEJUSC: R$ 2.589.660,12 | MÉDIA | ANALISAR_DOCUMENTACAO
- SEAD: R$ 2.339.702,20 | FORTE | ENVIAR_TRD
- BRADESCO: R$ 2.226.517,80 | FRACA | CLASSIFICAR
- CETAM: R$ 1.256.564,28 | FRACA | CLASSIFICAR
- SEDECTI: R$ 1.249.203,13 | MÉDIA | ANALISAR_DOCUMENTACAO
- SALUX: R$ 1.027.949,15 | FRACA | CLASSIFICAR
- POLÍCIA CIVIL: R$ 960.481,71 | MÉDIA | ANALISAR_DOCUMENTACAO

→ Lista completa em [`STATUS_DEVEDORES.md`](STATUS_DEVEDORES.md).

## 3. ALERTAS DE PRESCRIÇÃO (<90 dias)
- 🔴 **SSP**: 2026-06-30 (22 dias) — R$ 4.553.230,80
- 🟡 **SEJUSC**: 2026-08-31 (84 dias) — R$ 2.589.660,12

## 4. WORKFLOW DE COBRANÇA
Pipeline end-to-end F0→F6 (skills, gates documentais, prazos): [`WORKFLOW_COBRANCA.md`](WORKFLOW_COBRANCA.md).

## 5. REGRAS JURÍDICAS
1. **Decreto Estadual AM nº 53.464/2026** (substitui 51.084/2025) — verificar 4 exceções antes de qualquer ação contra Gov AM.
2. Silêncio do devedor **não** interrompe prescrição — exige ato inequívoco (Art. 202 CC, rol taxativo).
3. Juros pós-**Lei 14.905/2024** — não presumir 1% a.m.; verificar arts. 404-406 CC.
4. **Índices por contrato**: não há arquivo-SSOT de índices — `config_prodam.py` e `scripts/normalizador.py` **não existem** em código ativo (verificado 2026-06-08). Regime/índice (SELIC/IGPM/IPCA) é confirmado por contrato na cláusula econômica; correção SELIC via BCB live (série SGS 4390) em `scripts/ad_hoc/gerar_memorial_preliminar_ses.py`. Valores absolutos (SM vigente, teto RPV, custas) inline em scripts de cálculo — não criar `config_prodam.py`/`normalizador.py` sem auditoria prévia.
5. Adm. Direta → precatório/RPV (Art. 100 CF) | Adm. Indireta concorrencial → penhora direta (Tema 253/STF).
6. NFs do credor **não** são marcos interruptivos (exige ato do devedor).
7. Prescrição é por **fatura individual** (Art. 189 + 206 §5º I CC), contada do **vencimento**.
8. **FUHAM** = Fundação Alfredo da Matta · **FHAJ** = Fundação Hospital Adriano Jorge — nomes distintos, nunca inverter.
9. Empenho (NE) = reconhecimento tácito (Art. 202 VI CC) — interrompe prescrição.
10. SELIC já inclui correção + juros — não somar separado. IGPM = só correção (juros à parte).
11. Art. 202 CC: interrupção ocorre **uma vez** (unicidade — REsp 1.963.067/MS). Fazenda Pública reinicia por metade (Decreto 20.910/1932 = 2,5 anos).
12. **Tema 1.109/STJ**: gestor público não renuncia tacitamente a prescrição.
13. Composição documental (Contrato + NE + NF + Atesto) = título executivo (**REsp 793.969/RJ**, Rel. p/ acórdão **Min. José Delgado**; Min. Teori Zavascki foi vencido).
14. **Fee = 20%** sobre créditos recuperados. **RPV/AM estadual = 20 × SM vigente**, fundamento **Lei AM 2.748/2002** (não Lei 3.683/2012).
15. `PRODAM_DOCS/profiles.json` é a **SSOT** dos devedores — nunca usar Demonstrativo Excel antigo.
16. Valores monetários: **Decimal**, nunca float. Formato BRL: `R$ 1.234,56`.
17. `PRODAM_DOCS/REFERENCIA_JURIDICA/PRECEDENTES_VERIFICADOS.md` é a única fonte de jurisprudência verificada (3 fabricados + 6 distorcidos catalogados).
18. Consultar `PRODAM_DOCS/REFERENCIA_JURIDICA/` antes de emitir opinião jurídica.

## 6. HIERARQUIA DE FONTES JURÍDICAS (consultar nessa ordem)
1. **Nota Metodológica** (`PRODAM_DOCS/REFERENCIA_JURIDICA/01_NOTA_METODOLOGICA/`) — corrige todos os demais.
2. **Estudo Consolidado** (002/2026) — adaptado ao contrato atual.
3. **Estudo Exaustivo** — matriz genérica com minutas.
4. **Pesquisa Jurisprudencial** — STJ/STF/TJAM (só precedentes verificados).
5. **Extração Contratual** — cláusula a cláusula dos contratos dos devedores.
6. `PRODAM_DOCS/REFERENCIA_JURIDICA/` (20 subpastas) — SSOT jurídica do projeto.

## 7. CONVENÇÕES TÉCNICAS
- **Plataforma**: Windows + PowerShell. Python via `py -3.12` (sem venv). Bash não é usado.
- **Valores monetários**: `Decimal`, nunca `float`. Formato BRL via `prodam_utils.fmt_brl`.
- **CSV**: separador `;` + encoding `utf-8-sig` (BOM) — abre direto no Excel.
- **Salvar extrações** em **JSON + XLSX + CSV** no mesmo script. JSON é SSOT; XLSX/CSV são derivados.
- **PDFs** são prova jurídica — nunca apagar originais; backup em `_BACKUPS/` ou `_ARQUIVO_DRIFT/`.
- **SPCF**: `time.sleep(1.5)` entre requisições (rate limit obrigatório).
- **Contratos** têm 3 formatos coexistindo (`006/2021` em `spcf_contratos`, `6/2021` em `profiles.json`, `2021/006` em outras fontes) — normalizar antes de JOIN.
- **Testes**: `py -3.12 -m pytest tests\ -v` cobre `prodam_utils` (BRL, normalização, datas, prescrição). CI em `.github/workflows/tests.yml` valida `profiles.json`.
- **Proteções do repo** (não desativar sem motivo):
  - `.claude/hooks/block_pdf_delete.ps1` — hook que impede o **Claude Code** de remover `*.pdf` (provas) via Bash/PowerShell. Não cobre exclusão manual no Explorer.
  - `.pre-commit-config.yaml` — `ruff-check` (E9/F63/F7/F82) em `scripts/`. A validação de `profiles.json` (≥50 devedores/CNPJ/`_metadata`) é no **CI**, não aqui.
  - `.gitignore` — fora do repo: `PRODAM_DOCS/` (com `profiles.json`), `*.pdf`, `*.db`, segredos.

## 8. MAPAS DO PROJETO
| Caminho | O que cobre |
|---------|-------------|
| `PRODAM_DOCS/profiles.json` | **SSOT** dos 69 devedores (privado, fora do repo) |
| `PRODAM_DOCS/_ANALISE/prodam.db` | DB canônico (gerado por `PRODAM_DOCS/build_sqlite.py`) |
| `prodam.db` (raiz) | Cópia derivada usada por `scripts/consultas.py` |
| `PRODAM_DOCS/REFERENCIA_JURIDICA/` | Base jurídica (20 subpastas; consultar antes de parecer) |
| `PRODAM_DOCS/_SKILLS/` | Skills jurídicas curadas |
| `SPCF_EXTRACAO/` | Web scraping SPCF (rate-limit obrigatório) |
| `scripts/` | Pipelines, consultas, dossiês, sincronização |
| `STATUS_DEVEDORES.md` | Lista completa dos 69 devedores |
| `WORKFLOW_COBRANCA.md` | Pipeline end-to-end F0→F6 |
| `PLAYBOOK_ORGAOS_V2.md` | 13 passos validados no DETRAN A+ 94/100 |
| `.claude/skills/INDEX.md` | Índice das skills do projeto (versionado) |
| `~/.claude/CLAUDE.md` | Preferências pessoais (PowerShell, identidade, anti-alucinação) |

## 9. COMANDOS ESSENCIAIS
```powershell
py -3.12 scripts\auto_update_claude_md.py          # regenera CLAUDE.md + 3 satélites + índice de skills
py -3.12 scripts\sincronizar_prodam.py             # sincronização completa
py -3.12 scripts\consultas.py --lista              # lista 15 queries forenses
py -3.12 scripts\orgao_pipeline_completa.py --orgao SEDUC  # audita novo órgão
py -3.12 -m pytest tests\ -v                       # testes unitários
```
Slash command equivalente: `/sincronizar-prodam` (`.claude\commands\sincronizar-prodam.md`).

## 10. AGENT SKILLS + DB
- **Skills do projeto**: [`.claude/skills/INDEX.md`](.claude/skills/INDEX.md) — índice versionado (nome + descrição curta).
- **Agent skills (engenharia)**: `to-issues`, `triage`, `to-prd`, `tdd`, `diagnose`, `grill-with-docs`. Issue tracker → `_QUESTOES_CRITICAS/` (`NN_TITULO.md`). Triage labels → 5 canônicos (`needs-triage`/`needs-info`/`ready-for-agent`/`ready-for-human`/`wontfix`).
- **`prodam.db`**: cruzamento_spcf_pendrive (1.460), devedores (81), pendrive_docs (3.699), reclassificacao (1.261), spcf_contratos (362), spcf_empenhos (16.789), spcf_faturas (1.837), spcf_nfs (52.998). Views: v_cruzamento_nf, v_fatura_completa, v_fatura_sem_empenho, v_nf_sem_pagamento, v_pendrive_por_devedor.

