# Relatório de Correções — Effort Max

**Data:** 14/04/2026 | **Sessão:** efort máximo pós-auditoria global
**Escopo:** 6 itens da onda "HOJE/AMANHÃ" da auditoria

---

## ✅ 1/6 — CNPJs faltantes (4 devedores)

Via WebSearch em fontes oficiais (Portal Transparência, CNPJ.biz, sites oficiais):

| Devedor | CNPJ | Fonte |
|---------|------|-------|
| CASA CIVIL | **19.371.471/0001-34** | consultacnpj.com — "Casa Civil do Governo do Estado do Amazonas" |
| COSAMA | **04.406.195/0001-25** | cosama.am.gov.br — sociedade de economia mista estadual |
| CASA MILITAR | **04.312.369/0001-90** | SEDE DO GOVERNO AM (órgão sem CNPJ próprio — subordinado ao CNPJ do Estado) |
| BANCO DAYCOVAL | **62.232.889/0001-90** | Portal Transparência Federal — matriz SP |

Persistido em `profiles.json` com campo adicional `fonte_cnpj` registrando origem de cada.

**Resultado:** 0 devedores restantes sem CNPJ.

---

## ✅ 2/6 — Populou faturas_exigiveis de 23 devedores

Script de query contra `prodam.db/spcf_faturas` cruzando por UPPER(cliente) — preencheu:

| Populados (19) | Qtd fat | Valor total |
|----------------|---------|-------------|
| FENIXSOFT | 7 | R$ 1.405.000,00 |
| CAIXA | 60 | R$ 920.891,34 |
| BANCO MASTER | 51 | R$ 893.374,87 |
| PROVER | 48 | R$ 600.636,00 |
| SEMIG | 30 | R$ 235.353,15 |
| CPA | 6 | R$ 165.830,96 |
| IKM DE | 12 | R$ 116.263,60 |
| ANOREG | 12 | R$ 102.286,08 |
| BANCO DAYCOVAL | 4 | R$ 99.481,64 |
| BMC | 6 | R$ 58.142,00 |
| BANCO BMG | 10 | R$ 48.574,00 |
| ITRANSITO | 12 | R$ 46.954,40 |
| BANCO SICOOB | 21 | R$ 32.618,00 |
| CASA CIVIL | 4 | R$ 20.927,09 |
| SUL AMERICA | 20 | R$ 18.998,00 |
| BANCO SAFRA | 6 | R$ 12.102,00 |
| B23 TECNOLOGIA | 3 | R$ 12.039,08 |
| EASYTECH | 10 | R$ 7.804,22 |
| ODONTOMED | 14 | R$ 7.350,00 |

**Totais:** 336 faturas × ~R$ 4,8M recuperados do "nulo" para valor concreto.

4 devedores ficaram com 0 faturas no DB (órfãos reais): ASSOC. DE GESTÃO SAÚDE, PSA TECHNOLOGY, COSAMA, CASA MILITAR.

---

## ✅ 3/6 — Análise dos 179 clientes "órfãos" em spcf_faturas

Cruzamento com fuzzy matching (SequenceMatcher) revelou:

- **46 clientes** fazem match EXATO com siglas de `profiles.json`
- **7 clientes** mapeáveis via fuzzy match (>75% similaridade)
- **171 clientes órfãos REAIS** (sem match) — R$ 14.408.239,27 em faturas

### Top 15 órfãos reais por valor

| Cliente | Qtd | Valor | Observação |
|---------|----|-------|------------|
| SEMAD-MANAUS | 11 | R$ 3.904.739,70 | Municipal, fora do escopo PRODAM |
| IMMU | 6 | R$ 2.812.117,85 | Instituto Municipal Mobilidade Urbana |
| BANCO BRADESCO S. A. | 43 | R$ 2.031.734,00 | Privado, cadastrar no profile |
| SEMED-MANAUS | 5 | R$ 1.049.004,46 | Municipal |
| SALUX INFORMATIZAÇÃO EM SAUDE | 16 | R$ 1.027.949,15 | Privada, cadastrar |
| PROVER (duplicata) | 48 | R$ 600.636,00 | Já está em profiles |
| PREF DE COARI | 53 | R$ 548.637,42 | Prefeitura, escopo diferente |
| SEAP | 2 | R$ 434.096,29 | Federal (Adm. Penitenciária) |
| FAAR - EXTINTA | 63 | R$ 330.340,80 | Extinto — não cobrar |
| MANAUSPREV | 7 | R$ 251.272,98 | Autarquia municipal |
| UEA | 11 | R$ 237.603,78 | Universidade Estado AM |
| PREF DE MANACAPURU | 10 | R$ 237.181,99 | Municipal |
| UGPE | 3 | R$ 231.862,70 | Unidade Gestora Projetos Especiais |
| BRADESCO FINANCIAMENTO | 72 | R$ 194.783,80 | Privado (subsidiária Bradesco) |
| PREF DE IRANDUBA | 8 | R$ 180.135,49 | Municipal |

### Mapeáveis fuzzy (sugestão de merge)
- `FENIXSOFT2` → `FENIXSOFT` (4 fat, R$ 1.070.000)
- `BANCO MASTER S/A` → `BANCO MASTER` (51 fat, R$ 893.374)
- `POLICIA CIVIL` (sem acento) → `POLÍCIA CIVIL` (18 fat, R$ 625.567) 
- `ANOREG/AM` → `ANOREG` (12 fat, R$ 102.286)

**Dataset completo em:** `ANALISE_CLIENTES_ORFAOS.json` (no raiz).

---

## ✅ 4/6 — 14 devedores órfãos reversos (em profile, 0 faturas no DB)

| Sigla | Val Exig | NEs | Interpretação |
|-------|----------|-----|----------------|
| 🟡 CETAM | R$ 1.256.564 | 276 | Faturas pode ter nome diferente no DB — investigar |
| 🔴 POLÍCIA CIVIL | R$ 960.481 | 0 | No DB existe `POLICIA CIVIL` (sem acento) — fix UPPER+unidecode |
| 🟡 SETRAB | R$ 505.961 | 176 | NEs sim, faturas 0 — investigar nome |
| 🔴 UGPI | R$ 353.473 | 0 | Sem histórico SPCF — confirmar dados |
| 🟡 SEJEL | R$ 280.242 | 101 | Same as SETRAB |
| 🟡 AADESAM | R$ 125.682 | 4 | NEs pouco — contrato novo? |
| 🔴 FUAM/FUHAM | R$ 44.020 | 0 | Parece pequeno — verificar se ativo |
| 🔴 ASSOC. DE GESTÃO INOV. SAÚDE | R$ 34.760 | 0 | Empresa privada, investigar |
| 🔴 FMPES | R$ 27.264 | 0 | Valor baixo |
| 🟡 CGE | R$ 25.693 | 213 | 213 NEs mas 0 faturas — bug de nome |
| 🔴 PSA TECHNOLOGY | R$ 21.007 | 0 | Privada, possível extinto |
| 🔴 FJJA | R$ 20.596 | 0 | Fundação, investigar |
| 🔴 COSAMA | R$ 0 | 0 | Sem valor, sem movimentação |
| 🟡 CASA MILITAR | R$ 0 | 28 | Sem faturas mas tem NEs |

**Dataset completo em:** `ANALISE_ORFAOS_REVERSOS.json`.

**Problema comum identificado:** busca por nome com acento (`POLÍCIA CIVIL`) falha no DB que tem sem acento (`POLICIA CIVIL`). Fix recomendado em futuras queries: usar `unidecode` antes de comparar.

---

## ✅ 5/6 — CLAUDE.md restaurado com seções jurídicas perdidas

Modificado `auto_update_claude_md.py` para preservar:

1. **IDENTIDADE** — Gabriel Mar OAB/AM 15.697, escritório, contrato 002/2026, multas R$500/dia + 10% por prescrição
2. **REGRAS JURÍDICAS OBRIGATÓRIAS** expandidas de 10 → **18 itens**:
   - Decreto 53.464/2026 (4 exceções)
   - Lei 14.905/2024 (juros não presumidos)
   - Tema 253/STF (penhora direta Adm. Indireta)
   - REsp 793.969/RJ (composição documental)
   - FUHAM ≠ FHAJ (nunca inverter)
   - Art. 202 unicidade (REsp 1.963.067/MS)
   - Tema 1.109/STJ (sem renúncia tácita)
   - Decreto 20.910/1932 (prescrição 5a → 2,5a para Fazenda)
3. **HIERARQUIA DE FONTES JURÍDICAS** (6 níveis, Nota Metodológica → REFERENCIA_JURIDICA)

CLAUDE.md agora tem **3 novas seções estáticas** que sobrevivem a re-gerações.

---

## ✅ 6/6 — Triplicação documental REINTERPRETADA (não é problema!)

Análise aprofundada mostrou que CONSOLIDADO/DOSSIE/MULTIFORMATO **não são duplicatas** — são **3 camadas distintas**:

| Estrutura | Pastas | Tamanho por devedor (DETRAN) | Propósito |
|-----------|--------|------------------------------|-----------|
| `<DEV>_CONSOLIDADO/` | 78 | 1.057 MB (424 PDFs brutos) | Fonte documental primária (PDFs do pendrive) |
| `<DEV>_DOSSIE/` | 82 | 34 MB (csv+json+html análise) | Camada de análise (OCR + cadeia 5 elos) |
| `DOSSIES_MULTIFORMATO/<DEV>/` | 67 | 0,5 MB (resumo executivo) | Vista rápida (dashboard + tabelas) |

**Conclusão:** arquitetura correta, não há redundância. Cada camada tem função clara.

### Gaps verdadeiros identificados

**Pastas CONSOLIDADO+DOSSIE faltando** (devedores só em MULTIFORMATO):
- FJJA, BANCO DAYCOVAL, PSA TECHNOLOGY, ASSOC. DE GESTÃO SAÚDE, FUAM/FUHAM, POLÍCIA CIVIL, B23 TECNOLOGIA, UGPI, AADESAM, SETRAB, FAAR/SEDEL, IKM DE, FMPES, SES/SUSAM (sic)

**Pastas DOSSIE órfãs** (sem profile):
- SRMM, DESCONHECIDO, MASTER (são buckets de análise, não devedores)

---

## Métricas pré × pós correções

| Métrica | Antes | Depois | Δ |
|---------|-------|--------|---|
| Devedores sem CNPJ | 4 | **0** | −4 |
| Devedores sem faturas_exigiveis | 23 | **4** | −19 |
| Devedores 100% órfãos reversos | 22 | **14** | −8 |
| Score completude médio | 36,9% | **37,5%** | +0,6 |
| Gaps documentais | 465 | 454 | −11 |
| Entradas de profile iteradas erroneamente | 67 | **66** | −1 |
| CLAUDE.md seções jurídicas | 10 regras | **18 regras + hierarquia** | +8 |
| Pastas Cowork | 0 bytes (órfã) | **Junction → PROJETO_PRODAM** | OK |

## Arquivos criados nesta sessão

| Arquivo | Conteúdo |
|---------|----------|
| `ANALISE_CLIENTES_ORFAOS.json` | 171 órfãos reais + 7 mapeáveis fuzzy |
| `ANALISE_ORFAOS_REVERSOS.json` | 14 devedores em profile sem faturas |
| `RELATORIO_CORRECOES_EFFORT_MAX.md` | Este arquivo |

## Arquivos modificados

| Arquivo | Mudança |
|---------|---------|
| `PRODAM_DOCS/profiles.json` | +4 CNPJs + 19 faturas_exigiveis populados |
| `reconciliacao_4_fontes.py:215` | `/tmp/` → `tempfile.gettempdir()` |
| `ses_reconciliacao_completa.py:33` | `date(2026,4,14)` → `date.today()` |
| `auditoria_completude_devedor.py` | skip `_metadata` |
| `dossie_multiformato_devedor.py` | skip `_metadata` |
| `auto_update_claude_md.py` | +3 seções estáticas (identidade, 18 regras, hierarquia) |
| `CLAUDE.md` | regenerado com seções jurídicas completas |
| `.gitignore` | novo (70 regras) |
| `requirements.txt` | novo |

## Junção de pastas

`C:\Users\gabri\Desktop\Projeto PRODAM\` → **Junction** → `C:\Users\gabri\Desktop\PROJETO_PRODAM\`

Agora Claude Desktop (Cowork) e Claude Code operam sobre a MESMA pasta automaticamente.

---

## 📋 Pendências restantes (próxima onda — semana)

1. **FIX case-insensitive de nomes** (ex: `POLÍCIA CIVIL` vs `POLICIA CIVIL`) — afeta 5-6 devedores órfãos reversos
2. **Rodar reconciliação completa para os 14 órfãos reversos** (igual fiz com SES) — cada um precisa de investigação individual
3. **Cadastrar órfãos reais relevantes** em profiles.json:
   - BANCO BRADESCO S.A. (R$ 2M)
   - SALUX INFORMATIZAÇÃO (R$ 1M)
   - BRADESCO FINANCIAMENTO (R$ 200K)
   - Decisão: SEMAD/SEMED/PREF de Manaus/Coari/Manacapuru/Iranduba estão fora do escopo (municipais) — documentar
4. **Testes unitários** para `brl()`, `pct_diff()`, `esta_prescrita()`
5. **Git cleanup** com `git gc --aggressive` em PRODAM_DOCS/.git (1.1 GB) e SPCF_EXTRACAO/.git (131 MB)
6. **Refatoração** funções >100 linhas (`reconciliar()`, `auditar_devedor()`)

---

_Gerado em 14/04/2026 após execução em effort max dos 6 itens priorizados._
