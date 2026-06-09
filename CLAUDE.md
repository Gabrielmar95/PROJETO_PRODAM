# PROJETO PRODAM — Recuperação de Créditos
## Contrato 002/2026 — PRODAM S.A. × Brandão Ozores Advogados
_Atualizado em 09/06/2026 19:28 via `scripts/auto_update_claude_md.py`._

> Conteúdo regenerado a cada `/sincronizar-prodam`. Para regras fixas → editar o gerador. Para métricas → editar `PRODAM_DOCS/profiles.json` e rodar `py -3.12 scripts\auto_update_claude_md.py`.

## 0. NUNCA (vedações — maior dano primeiro)
1. **Nunca apagar/mover/sobrescrever PDF** — prova jurídica (hook `block_pdf_delete.ps1` ativo; backups em `_BACKUPS/`).
2. **Nunca `float` em valores BRL** — `Decimal` sempre; formatar via `prodam_utils.fmt_brl` (`R$ 1.234,56`).
3. **Nunca citar lei/jurisprudência fora do catálogo verificado** (Regra 13).
4. **Nunca criar `config_prodam.py`/`normalizador.py`** sem auditoria prévia — não existem em código ativo.
5. **Nunca executar comandos de dentro de `_LIXO_NAO_USAR\_ARCHIVE`** — antes de qualquer prompt no terminal: `cd C:\Users\gabri`.
6. **Nunca usar o Demonstrativo Excel como fonte de valores** — a SSOT é `PRODAM_DOCS/profiles.json`.
7. **Nunca inverter FUHAM × FHAJ** — FUHAM = Fundação Alfredo da Matta; FHAJ = Fundação Hospital Adriano Jorge.
8. **Antes de rodar Claude Code no terminal**: `Test-Path Env:ANTHROPIC_API_KEY` deve retornar `False` — a env var ativa cobra a API do Console em vez do plano.

## 1. IDENTIDADE
- **Advogado**: Gabriel Mar (OAB/AM 15.697) — Gabriel Mar Sociedade Individual de Advocacia
- **Contratante**: Brandão Ozores Advogados | **Cliente**: PRODAM S.A. (CNPJ 04.407.920/0001-80, economia mista, Lei 13.303/2016)
- **Fee**: 20% sobre créditos recuperados | **Obrigações**: relatórios quinzenais (R$500/dia atraso | 10% do crédito por prescrição perdida)

## 2. STATUS DO PORTFÓLIO
- **69 devedores** (26 Gov Direta, 21 Gov Indireta, 22 Privadas)
- **R$ 83.668.078,44 exigível** | R$ 125.245.390,64 atualizado (65/69 com valor atualizado)
- **3477 faturas** (2326 exigíveis, 1082 prescritas, 69 fora do universo exig./presc. — canceladas/excluídas, ver STATUS)
- **Força**: 12 FORTE · 15 MÉDIA · 42 FRACA

**Pipeline (próximo passo)**: ANALISAR_DOCUMENTACAO=36 · CLASSIFICAR=17 · ENVIAR_TRD=9 · PROTOCOLAR_PETICAO=5 · AVALIAR_SUCESSAO=1 · HABILITAÇÃO DE CRÉDITO=1

**Top 5 devedores** (por valor exigível):
- SEDUC: R$ 49.215.512,48 | FORTE | ANALISAR_DOCUMENTACAO
- SES/SUSAM: R$ 4.783.356,52 | FORTE | ENVIAR_TRD
- SSP: R$ 4.553.230,80 | FORTE | PROTOCOLAR_PETICAO
- SEJUSC: R$ 2.589.660,12 | MÉDIA | ANALISAR_DOCUMENTACAO
- SEAD: R$ 2.339.702,20 | FORTE | ENVIAR_TRD

→ Lista completa dos 69 devedores: [`STATUS_DEVEDORES.md`](STATUS_DEVEDORES.md).

## 3. ALERTAS DE PRESCRIÇÃO
- 🔴 **SSP**: 2026-06-30 (21 dias) — R$ 4.553.230,80
- 🔴 **SUHAB**: 2026-06-30 (21 dias) — R$ 840.061,15
- 🟡 **SEJUSC**: 2026-08-31 (83 dias) — R$ 2.589.660,12
- 🛡️ **1 protegido(s) por marco interruptivo (Art. 202 VI CC)** com data registrada no passado — marco prevalece; reconfirmar e atualizar a data: DETRAN.
- _(9 devedores sem data de prescrição registrada — nomes no [`STATUS_DEVEDORES.md`](STATUS_DEVEDORES.md))_

## 4. WORKFLOW DE COBRANÇA
Pipeline end-to-end F0→F6 (skills, gates documentais, prazos): [`WORKFLOW_COBRANCA.md`](WORKFLOW_COBRANCA.md).

## 5. REGRAS JURÍDICAS
1. **Decreto Estadual AM nº 53.464/2026** (sucedeu o 51.084/2025, de efeitos exauridos em 2025) — verificar as 4 exceções (art. 1º §§1º-4º) antes de qualquer ação contra Gov AM; teor em `REFERENCIA_JURIDICA/16_AUXILIAR/`.
2. Prescrição é por **fatura individual** (Art. 189 + 206 §5º I CC), contada do **vencimento**.
3. Silêncio do devedor **não** interrompe prescrição — exige ato inequívoco (Art. 202 CC, rol taxativo).
4. Marcos interruptivos: **empenho (NE) = reconhecimento tácito** (Art. 202 VI CC) e interrompe; **NF emitida pelo credor não interrompe** (exige ato do devedor).
5. Interrupção ocorre **uma vez** (unicidade — REsp 1.963.067/MS); contra a Fazenda Pública o prazo reinicia **pela metade** (Decreto 20.910/1932 = 2,5 anos).
6. **Tema 1.109/STJ**: gestor público não renuncia tacitamente a prescrição.
7. Composição documental (Contrato + NE + NF + Atesto) = título executivo (**REsp 793.969/RJ**, Rel. p/ acórdão **Min. José Delgado**; Min. Teori Zavascki foi vencido).
8. Juros pós-**Lei 14.905/2024** — não presumir 1% a.m.; verificar arts. 404-406 CC.
9. SELIC já inclui correção + juros — não somar separado. IGPM = só correção (juros à parte).
10. **Índice de correção**: confirmar na **cláusula econômica do contrato** do devedor (SELIC/IGPM/IPCA); SELIC live via BCB (série SGS 4390). Não há arquivo-SSOT de índices (ver NUNCA-4).
11. Adm. Direta → precatório/RPV (Art. 100 CF) | Adm. Indireta concorrencial → penhora direta (Tema 253/STF).
12. **RPV/AM = 20 × SM vigente** (Lei AM 2.748/2002; a Lei 3.683/2012 é citação errada) — 60 SM é o teto **federal**, não aplicar contra o Estado.
13. Jurisprudência: citar **só** o catálogo `PRODAM_DOCS/REFERENCIA_JURIDICA/11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md` (3 fabricados + 6 distorcidos catalogados); antes de emitir opinião jurídica, consultar `REFERENCIA_JURIDICA/` na ordem da Seção 6.

## 6. HIERARQUIA DE FONTES JURÍDICAS (consultar nessa ordem)
1. **Nota Metodológica** (`PRODAM_DOCS/REFERENCIA_JURIDICA/01_NOTA_METODOLOGICA/`) — corrige todos os demais.
2. **Estudo Consolidado** (002/2026) — adaptado ao contrato atual.
3. **Estudo Exaustivo** — matriz genérica com minutas.
4. **Pesquisa Jurisprudencial** — STJ/STF/TJAM (só precedentes verificados).
5. **Extração Contratual** — cláusula a cláusula dos contratos dos devedores.
6. `PRODAM_DOCS/REFERENCIA_JURIDICA/` (18 subpastas) — SSOT jurídica do projeto.

## 7. CONVENÇÕES TÉCNICAS
- **Plataforma**: Windows + PowerShell. Python via `py -3.12` (sem venv). Bash não é usado.
- **BRL**: formatar via `prodam_utils.fmt_brl`; parse via `prodam_utils.brl` (vedação de float: NUNCA-2).
- **CSV**: separador `;` + encoding `utf-8-sig` (BOM) — abre direto no Excel.
- **Salvar extrações** em **JSON + XLSX + CSV** no mesmo script. JSON é SSOT; XLSX/CSV são derivados.
- **Arquivamento**: backups e quarentenas do projeto em `_BACKUPS/` (única pasta canônica). Acervo morto fica em `Desktop\_LIXO_NAO_USAR\_ARCHIVE` — só listar, nunca operar lá (NUNCA-5).
- **SPCF**: `time.sleep(1.5)` entre requisições (rate limit obrigatório).
- **Contratos** têm 3 formatos coexistindo (`006/2021` em `spcf_contratos`, `6/2021` em `profiles.json`, `2021/006` em outras fontes) — normalizar antes de JOIN.
- **Testes**: `py -3.12 -m pytest tests\ -v`. CI (`.github/workflows/tests.yml`) valida `profiles.json` (≥50 devedores/CNPJ/`_metadata`).
- **Proteções do repo** (não desativar sem motivo): hook `.claude/hooks/block_pdf_delete.ps1` (bloqueia remoção de `*.pdf` via shell; não cobre o Explorer) · `.pre-commit-config.yaml` (`ruff-check` E9/F63/F7/F82 em `scripts/`) · `.gitignore` (mantém `PRODAM_DOCS/`, `*.pdf`, `*.db` e segredos fora do repo).

## 8. MAPAS DO PROJETO
| Caminho | O que cobre |
|---------|-------------|
| `PRODAM_DOCS/profiles.json` | **SSOT** dos 69 devedores (privado, fora do repo) |
| `PRODAM_DOCS/_ANALISE/prodam.db` | DB canônico (gerado por `PRODAM_DOCS/build_sqlite.py`) |
| `prodam.db` (raiz) | Cópia derivada usada por `scripts/consultas.py` |
| `PRODAM_DOCS/REFERENCIA_JURIDICA/` | Base jurídica — consultar antes de qualquer parecer (Regra 13) |
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
- **`prodam.db`**: 8 tabelas + 5 views — contagens vivas em [`STATUS_DEVEDORES.md`](STATUS_DEVEDORES.md). Abrir sem código: `datasette serve PRODAM_DOCS\_ANALISE\prodam.db --open` ou Beekeeper Studio.

