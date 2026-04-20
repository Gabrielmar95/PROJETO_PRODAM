# Changelog — 14/04/2026

**Sessão:** Auditoria global + Pipeline DETRAN + Generalização para outros órgãos

---

## 🎯 Grandes entregas

### 1. Auditoria Global em 2 ondas (67 → 69 devedores)
- 4 CNPJs populados via WebSearch (CASA CIVIL, COSAMA, CASA MILITAR, BANCO DAYCOVAL)
- 19 devedores com `faturas_exigiveis` populados
- 3 devedores novos cadastrados (BRADESCO +R$ 2,2M, SALUX +R$ 1M, BRADESCO FINANCIAMENTO +R$ 195K)
- 171 clientes órfãos em `spcf_faturas` identificados
- 14 órfãos reversos (em profile sem faturas) mapeados
- Pasta Cowork (`Projeto PRODAM` com espaço) → Junction apontando para `PROJETO_PRODAM`

### 2. Infra de código (reutilizável)
- `prodam_utils.py` (220 linhas) — norm() com unidecode, brl/fmt_brl, datas dinâmicas, match_flex
- `tests/test_prodam_utils.py` — **49 testes passando**
- Git cleanup: repos de 1,23 GB → 220 MB (-1 GB liberado)
- Refatoração `auditar_devedor()` 127 → 50 linhas (4 helpers)
- Fix `/tmp/` Windows (tempfile.gettempdir())
- Fix `HOJE` hardcoded → `date.today()`
- Skip `_metadata` em todos os scripts que iteram profiles.json

### 3. DETRAN — Pipeline PDF→JSON completo + Score A+
- **454/455 arquivos em JSON** (99,8% cobertura)
- **Tempo total:** 9 minutos (16s fast + 8,2 min OCR)
- **8 libs SOTA:** PyMuPDF, Tesseract PT, python-docx, openpyxl, xlrd, BeautifulSoup, pdf2image, pypdfium2 (disponíveis)
- **12 contratos ingeridos no DB** `spcf_contratos` (via `PDF_DETRAN_XXX_YYYY`)
- **10 contratos com índice granular** (IGPM:7, IPCA:3)
- Bug `data_emissao` corrigido (470 NEs agora distribuídas 2014-2026)
- **Score final:** 91,0 → 92,1 → 93,1 → **94,0 (A+)**

### 4. Generalização para outros órgãos
- **`orgao_pipeline_completa.py`** (500+ linhas) — pipeline parametrizada aceitando `--orgao`
- **`PLAYBOOK_AUDITORIA_ORGAO.md`** — passo-a-passo completo
- **Skill `orgao-auditoria-completa`** instalada em `~/.claude/skills/`

### 5. Correções pontuais
- `auto_update_claude_md.py` — preserva seções jurídicas estáticas (identidade, 18 regras, hierarquia)
- `build_sqlite.py` — paths relativos (`Path(__file__).parent`)
- `atualizar_db.py` — novo, wrapper para rebuild + cópia
- `.gitignore` + `requirements.txt` — criados

---

## 📁 Arquivos criados (inventário completo)

### Scripts principais
| Arquivo | Linhas | Função |
|---------|--------|--------|
| `prodam_utils.py` | 220 | Utilitários compartilhados |
| `tests/test_prodam_utils.py` | 260 | 49 testes unitários |
| `sincronizar_prodam.py` | 150 | Comando mestre |
| `atualizar_db.py` | 25 | Wrapper rebuild DB |
| `auditoria_completude_devedor.py` | 435 | Score + gaps + divergências |
| `dossie_multiformato_devedor.py` | 400 | 5 formatos por devedor |
| `reconciliar_orfaos_reversos.py` | 120 | Popular via norm() |
| **`orgao_pipeline_completa.py`** | **500+** | **Pipeline genérica para qualquer órgão** |

### Scripts específicos DETRAN (servem como template)
| Arquivo | Função |
|---------|--------|
| `detran_auditoria_profunda.py` | Auditoria profunda (NEs, faturas, cadeia) |
| `detran_consolidado_to_json_pipeline.py` | Pipeline v1 (deprecated → usar orgao_*) |
| `detran_pipeline_fast.py` | Fast-path PyMuPDF |
| `detran_ocr_fase2.py` | OCR Tesseract |
| `detran_pipeline_nao_pdf.py` | docx/xlsx/html/md/py/png |
| `detran_ingest_contratos_db.py` | Ingestão em spcf_contratos |
| `detran_score_auditor.py` | Score 12 dimensões |
| `detran_contratos_to_json.py` | Foco só contratos (pré-OCR) |
| `detran_ocr_contratos.py` | OCR específico contratos |

### Documentação
| Arquivo | Conteúdo |
|---------|----------|
| `PLAYBOOK_AUDITORIA_ORGAO.md` | **Passo-a-passo para replicar** |
| `COMO_INTEGRAR.md` | Opções de integração (slash, batch, cron) |
| `AUDITORIA_GLOBAL_DUAS_PASTAS.md` | Auditoria completa do projeto |
| `RELATORIO_CORRECOES_EFFORT_MAX.md` | Onda 1 de correções |
| `RELATORIO_CORRECOES_ONDA2.md` | Onda 2 de correções |
| `CHANGELOG_2026-04-14.md` | Este arquivo |

### DETRAN — relatórios específicos
| Arquivo | Conteúdo |
|---------|----------|
| `DETRAN_AUDITORIA/RELATORIO_DETRAN.md` | Relatório executivo |
| `DETRAN_AUDITORIA/NOTA_FINAL_DETRAN.md` | Score A+ detalhado |
| `DETRAN_AUDITORIA/SCORE_DETRAN.json` | Dados estruturados |
| `DETRAN_AUDITORIA/AUDITORIA_CRUZADA_DESKTOP_DETRAN.md` | Cross-ref com Desktop\DETRAN |
| `DETRAN_AUDITORIA/FIX_BUGS_DB_RELATORIO.md` | Correção dos 2 bugs DB |
| `DETRAN_CONSOLIDADO_JSON/COBERTURA_FINAL.md` | 99,8% cobertura |
| `DETRAN_CONSOLIDADO_JSON/RELATORIO_FINAL_PIPELINE.md` | Pipeline detalhada |
| `DETRAN_CONSOLIDADO_JSON/RELATORIO_FINAL_COMPLETO.md` | Consolidado |

### Skills
| Arquivo | Local |
|---------|-------|
| `pipeline-devedor-completo_SKILL.md` | `_SKILLS/` + `~/.claude/skills/` |
| `auditoria-completude-devedor_SKILL.md` | `_SKILLS/` + `~/.claude/skills/` |
| **`orgao-auditoria-completa_SKILL.md`** | `_SKILLS/` + `~/.claude/skills/` |

### Slash commands
| Comando | Local |
|---------|-------|
| `/sincronizar-prodam` | `~/.claude/commands/` |

---

## 🚀 Como replicar para outros órgãos

### Para 1 órgão
```bash
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"
py -3.12 orgao_pipeline_completa.py --orgao SEDUC
```

### Para TOP 5 devedores
```bash
for ORGAO in SEDUC "SES/SUSAM" SSP SEAD SEJUSC; do
    py -3.12 orgao_pipeline_completa.py --orgao "$ORGAO"
done
```

### Para TODOS os 78 devedores
```bash
py -3.12 orgao_pipeline_completa.py --listar | while read orgao; do
    py -3.12 orgao_pipeline_completa.py --orgao "$orgao"
done
```

### Para auditoria global
```bash
py -3.12 sincronizar_prodam.py
```

---

## 📊 Métricas finais da sessão

| Categoria | Número |
|-----------|--------|
| **Scripts Python criados** | 15 |
| **Testes unitários** | 49/49 passando ✅ |
| **Documentos MD de relatório** | 15+ |
| **JSONs estruturados gerados** | 454 (só DETRAN) |
| **Skills criadas** | 3 |
| **Slash commands criados** | 1 |
| **Devedores novos cadastrados** | 3 (+ R$ 3,4M) |
| **CNPJs populados** | 4 + 3 novos = 7 |
| **Bugs DB corrigidos** | 2 (data_emissao + contratos) |
| **Score DETRAN** | 91,0 → **94,0 (A+)** |
| **Git space liberado** | ~1 GB |
| **Tempo pipeline DETRAN** | 9 minutos |

---

## 🎯 Próxima sessão: replicar para SEDUC

SEDUC é o #1 do ranking (R$ 49,2M exigível). Rodar:
```bash
py -3.12 orgao_pipeline_completa.py --orgao SEDUC
```

Benchmark: se SEDUC tiver volume similar ao DETRAN, esperar ~8-12 min para cobertura completa + score A+ (presumindo blindagem 22/22 e cadeia FORTE).

---

## 🔁 Comandos de validação

```bash
# Testes unitários
py -3.12 tests/test_prodam_utils.py

# Sincronização global (valida tudo)
py -3.12 sincronizar_prodam.py

# Score DETRAN
py -3.12 detran_score_auditor.py

# Lista órgãos processáveis
py -3.12 orgao_pipeline_completa.py --listar
```

---

**Sessão encerrada:** 14/04/2026
**Total de commits mentais:** muitos 🎉
**Status projeto:** ✅ Pronto para execução em escala (78 devedores)
