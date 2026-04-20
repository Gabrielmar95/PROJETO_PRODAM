# Relatório Onda 2 — Effort Max continuado

**Data:** 14/04/2026 | **Sessão:** 2ª onda pós-auditoria
**Escopo:** 6 itens da pendência da Onda 1

---

## ✅ 7/12 — Fix normalização case+acento (unidecode)

Criado `prodam_utils.py` — módulo compartilhado com funções críticas:

- `norm(s)` — `POLÍCIA CIVIL` ≡ `Polícia Civil` ≡ `POLICIA CIVIL` → `"POLICIA CIVIL"`
- `norm_variants(s)` — `SES/SUSAM` → `{SES/SUSAM, SES, SUSAM}`
- `match_flex(alvo, candidatos, limiar)` — fuzzy match com unidecode
- `brl(s)`, `fmt_brl(v)`, `pct_diff(a,b)` — monetários com Decimal
- `parse_br_date`, `parse_comp`, `vencimento_30`, `esta_prescrita(venc, hoje=None)` — datas dinâmicas
- `is_metadata_key(k)`, `load_profiles(path, include_metadata=False)` — profile loading limpo
- `norm_id(x)`, `norm_contrato(c)` — IDs e contratos

Atualizado `auditoria_completude_devedor.py` para usar:
- `_contar_empenhos_db(sigla)` — query usando todas as variantes
- `_contar_faturas_db(sigla)` — compara via Python com `norm()` (cacheado)
- `_localizar_pastas(sigla)` — extrai lógica de pastas
- `_detectar_divergencias(profile, contagens, cobr_dev)` — extraído

## ✅ 8/12 — Cadastrados 3 devedores privados órfãos

| Devedor | CNPJ | Faturas | Valor exig (bruto) |
|---------|------|---------|--------------------|
| BRADESCO | 60.746.948/0001-12 | 115 | **R$ 2.226.517,80** |
| SALUX | (pendente) | 16 | **R$ 1.027.949,15** |
| BRADESCO FINANCIAMENTO | 07.207.996/0001-50 | 72 | **R$ 194.783,80** |
| **TOTAL novo no escopo** | | **203** | **R$ 3.449.250,75** |

Todos com:
- `categoria: EMPRESA_PRIVADA`
- `regime_execucao: penhora_direta`
- `modelo_notificacao: D`
- `status: NOVO_SPCF`, `fase_atual: F0`, `proximo_passo: CLASSIFICAR`
- Observação registrando origem (ANALISE_CLIENTES_ORFAOS.json)

Dossiês multi-formato gerados em `DOSSIES_MULTIFORMATO/<SIGLA>/` para cada um.

## ✅ 9/12 — Testes unitários: 49/49 passando

Criado `tests/test_prodam_utils.py` — 49 testes agrupados em 13 classes:

```
TestBrl (7 testes)               — valor monetário BRL parsing
TestFmtBrl (5 testes)             — formatação BRL
TestPctDiff (4 testes)            — percent diff
TestNorm (5 testes)               — normalização acentos+case
TestNormVariants (3 testes)       — variantes SES/SUSAM
TestMatchFlex (3 testes)          — fuzzy match com unidecode
TestParseBrDate (3 testes)        — datas BR
TestParseComp (2 testes)          — competências MM/AAAA
TestVencimento30 (2 testes)       — emissão + 30 dias
TestEstaPrescrita (4 testes)      — cutoff 5 anos dinâmico
TestIsMetadataKey (3 testes)      — detecta _metadata
TestNormId (5 testes)             — IDs com .0 artifact
TestNormContrato (3 testes)       — 018/2021 vs 18/2021
```

Executável via:
```bash
py -3.12 tests/test_prodam_utils.py       # standalone
py -3.12 -m pytest tests/ -v              # via pytest (requer install)
```

## ✅ 10/12 — Refatoração de funções >100 linhas

`auditar_devedor()` em `auditoria_completude_devedor.py` reduzida de **127 → ~50 linhas** extraindo:

1. `_contar_empenhos_db(sigla)` — 7 linhas
2. `_contar_faturas_db(sigla)` — 11 linhas (com cache)
3. `_localizar_pastas(sigla)` — 15 linhas
4. `_detectar_divergencias(profile, contagens, cobr_dev)` — 25 linhas

Benefício: testabilidade individual, reuso em outros scripts.

## ✅ 11/12 — Git cleanup com gc --aggressive

| Repo | Antes | Depois | Ganho |
|------|-------|--------|-------|
| `PRODAM_DOCS/.git` | 1.100 MB | **117 MB** | −89% |
| `SPCF_EXTRACAO/.git` | 131 MB | **103 MB** | −21% |
| **Total liberado** | — | — | **~1.011 MB** |

## ✅ 12/12 — Re-auditoria e delta final

| Métrica | Baseline | Onda 1 | **Onda 2** | Δ total |
|---------|----------|--------|------------|---------|
| Devedores auditados | 67 (c/ _metadata) | 66 | **69** | +2 reais |
| Sem CNPJ | 4 | 0 | **1 (SALUX)** | −3 |
| Sem faturas_exigiveis | 23 | 4 | **4** | −19 |
| Score médio | 36,9% | 37,5% | **37,0%**¹ | +0,1 |
| Gaps documentais | 465 | 454 | 478² | −11 |
| Testes unitários | 0 | 0 | **49 passando** | +49 |
| Git folders combined | 1.231 MB | 1.231 MB | **220 MB** | −1.011 MB |
| Órfãos clientes (DB sem profile) | 179 | 171 | **168** | −11 |

¹ Score ligeiramente menor porque os 3 novos cadastrados entram com score baixo inicial (falta pasta DOSSIE/CONSOLIDADO).

² Gaps subiram (+24 dos 3 novos × 8 itens cada que falta), mas isso é EXPECTED — novos devedores começam sem docs.

## Principais arquivos criados/modificados

**Novos:**
- `prodam_utils.py` — 220 linhas, módulo utilitário
- `tests/test_prodam_utils.py` — 260 linhas, 49 testes

**Modificados:**
- `PRODAM_DOCS/profiles.json` — +3 devedores (BRADESCO, SALUX, BRADESCO FINANCIAMENTO)
- `auditoria_completude_devedor.py` — importa prodam_utils, refatorado em 4 funções auxiliares
- `auto_update_claude_md.py` — +3 seções estáticas (identidade, 18 regras, hierarquia)

**Liberados espaço:**
- `PRODAM_DOCS/.git` — 983 MB liberados via `git gc --aggressive --prune=now`
- `SPCF_EXTRACAO/.git` — 28 MB liberados

## Pendências restantes

### 🟡 Menor prioridade
1. **CNPJ da SALUX** — requer busca manual (consultar contrato original)
2. **Rodar reconciliação profunda** para os 14 órfãos reversos (igual fiz com SES) — investigação individual por devedor
3. **Documentar que municipais (SEMAD-MANAUS, SEMED, Prefeituras) estão fora do escopo** — adicionar nota em `profiles._metadata`
4. **Aplicar `norm()` em outros scripts** — `reconciliacao_4_fontes.py`, `dossie_multiformato_devedor.py`, `ses_reconciliacao_completa.py`
5. **Testes unitários adicionais** para `dossie_multiformato_devedor.py` e `auditoria_completude_devedor.py`

### 🟢 Nice-to-have
6. Refatorar `reconciliar()` em `reconciliacao_4_fontes.py` (145 linhas)
7. Limpar `except: pass` em scripts subpastas `_SCRIPTS_IMPORTADOS/`
8. Criar `CI/workflow.yml` rodando pytest a cada commit

---

## Resumo executivo de 2 ondas

**Itens corrigidos:** 12 de 12 (100%)
**Linhas de código adicionadas:** ~500 (utils + testes)
**Espaço em disco liberado:** ~1 GB (git gc)
**Bugs críticos fechados:** 3 (/tmp/, HOJE hardcoded, _metadata)
**Novos devedores no escopo:** 3 (R$ 3,4 M em cobrança)
**CNPJs populados:** 4 (via fontes oficiais)
**Cowork operacional:** junction → PROJETO_PRODAM

**Próxima rodada (se houver):** aplicar `norm()` nos demais scripts, reconciliação dos 14 órfãos reversos, documentar municipais, CI/pytest.
