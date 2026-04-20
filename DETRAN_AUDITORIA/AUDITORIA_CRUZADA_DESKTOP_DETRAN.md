# DETRAN — Auditoria Cruzada com `Desktop\DETRAN`

**Data:** 14/04/2026 | **Escopo:** Investigação do workspace paralelo `C:\Users\gabri\Desktop\DETRAN` (2,7 GB) e cruzamento com `PROJETO_PRODAM`

---

## 🎯 Descoberta crítica

Existe um **workspace paralelo** em `Desktop\DETRAN` (2,7 GB) com:
- **Sessão 74 (10/04/2026)** — análise mais recente que a atual em `PROJETO_PRODAM`
- **500 NEs documentadas** (vs 470 no DB, vs 303 no profile antigo)
- **202 faturas exigíveis classificadas** (vs 113 no DB, vs 179 no profile)
- **DETRAN-AM/** — template de dossiê estruturado com 20 pastas (criado hoje 14:42)
- **42% (1,13 GB) DUPLICADO** com `PROJETO_PRODAM/PRODAM_DOCS/`

---

## 1. Comparação das 3 fontes de NEs

| Fonte | NEs | Valor total | Campos | Método | Cobertura |
|-------|-----|-------------|--------|--------|-----------|
| `Desktop\DETRAN\DETRAN_NES_CONSOLIDADO.json` | **115** | R$ 88.392.361,41 | 27 | OCR + PDF parsing | 2014-2026 (13 anos) |
| `Desktop\DETRAN\empenhos_COMPLETO.csv` (sessão 74) | **500** | **R$ 284.653.134,96** | 16 | SPCF exportado | 2014-2026 completo |
| `prodam.db/spcf_empenhos` (DETRAN) | **470** | R$ 250.316.057,30 | 11 | SPCF scrape | quase todas em 2026 (bug!) |

### 🔴 Bug detectado: `spcf_empenhos.data_emissao`

**462 de 470 NEs (98%)** estão com `data_emissao` em 2026 — valor claramente errado (deveria espalhar pelos 13 anos).

**Origem:** erro no scraper SPCF. A sessão 74 capturou datas corretas:

| Ano | NEs CSV (correto) | NEs DB (bugado) |
|-----|-------------------|-----------------|
| 2014 | 18 | 0 |
| 2015 | 41 | 0 |
| 2016 | 46 | 0 |
| 2017 | 35 | 0 |
| 2018 | 48 | 0 |
| 2019 | 46 | 0 |
| 2020 | 53 | 0 |
| 2021 | 22 | 0 |
| 2022 | 24 | 0 |
| 2023 | 57 | 0 |
| 2024 | 63 | 0 |
| 2025 | 34 | 0 |
| 2026 | 13 | **462** (all errado) |

**Fix:** Re-ingestar usando `empenhos_COMPLETO.csv` como fonte primária OU consertar o extrator de data no `build_sqlite.py`.

---

## 2. As 202 Faturas da Sessão 74 (fonte mais rica)

### Por contrato (top 7)

| Contrato | Faturas | Bruto | Atualizado IGPM+1%+2% | % do total |
|----------|---------|-------|------------------------|-----------|
| **C.10/2021** | 30 | R$ 10.890.724 | R$ 12.886.778 | **48,8%** |
| P.296/2025 | 4 | R$ 2.522.329 | R$ 2.713.347 | 10,3% |
| C.22/2014 | 12 | R$ 1.584.063 | R$ 2.480.268 | 9,4% |
| C.3/2026 | 3 | R$ 1.891.747 | R$ 1.969.348 | 7,5% |
| C.6/2021 | 79 | R$ 1.510.411 | R$ 1.852.350 | 7,0% |
| C.4/2016 | 5 | R$ 1.527.017 | R$ 986.909 | 3,7% |
| Outros (12) | 69 | R$ 2.771.637 | R$ 3.489.699 | 13,2% |

### Por prescrição (sessão 74)

| Status | Faturas | Bruto | Atualizado |
|--------|---------|-------|------------|
| VIGENTE | 148 | R$ 19.319.748,79 | R$ 21.821.557,41 |
| **ATENÇÃO** | **53** | R$ 3.375.010,89 | R$ 4.557.140,57 |
| PRESCRITA | 1 | R$ 3.169,53 | R$ 0 |
| **Total** | **202** | **R$ 22.697.929,21** | **R$ 26.378.697,98** |

### 53 faturas em ATENÇÃO — ação urgente

- Primeiro vencimento: 27/10/2026 (D+200 dias)
- Último vencimento: 17/03/2027 (D+341 dias)
- **R$ 4,56M em risco de prescrição próxima**

---

## 3. Divergência de valor — 3 fontes, 3 números

| Fonte | Valor exigível | Valor atualizado |
|-------|----------------|------------------|
| Sessão 74 CSVs (202 faturas) | R$ 22.697.929,21 | R$ 26.378.697,98 |
| `profiles.json` (antes auditoria) | R$ 31.684.739,01 | R$ 37.960.629,19 |
| Minha auditoria (113 DB faturas) | R$ 17.802.420,55 | ~R$ 28.867.345,47 |

**Divergência profile × sessão 74 = R$ 8,9M (+39,6%)**

### Hipótese mais provável

- **Profile** inclui fontes que não estão nos CSVs nem no DB:
  - `DADOS_5DEV/DETRAN/` (132K+ registros reconciliados)
  - Reconciliações anteriores (sessão 71)
  - PDFs individuais no pendrive

- **Sessão 74 CSVs** = snapshot SPCF limpo + correção IGPM aplicada
- **DB (113 faturas)** = subset do SPCF ativo em cobrança

**Recomendação:** sessão 74 CSVs são a fonte mais confiável para execução judicial (202 faturas com correção aplicada). Os R$ 8,9M extras do profile precisam de reconciliação em DADOS_5DEV antes de cobrar.

---

## 4. O que `Desktop\DETRAN` tem de ÚNICO

**1,6 GB não está em PROJETO_PRODAM:**

| Item | Tamanho | Observação |
|------|---------|------------|
| **DETRAN-AM/** (template) | 92 KB | 20 pastas estruturadas + 00_RESUMO. Criado hoje 14:42. Pronto para preenchimento. |
| **DETRAN_DADOS_SPCF/** | 1,1 GB | Dados SPCF brutos (JSON 613M + CSV 359M + TXT 86M). Não ingerido no prodam.db. |
| **DETRAN_NEs_169arquivos/** | 50 MB | 138 PDFs de NEs 2015-2026 — NÃO estão em `PROJETO_PRODAM/PRODAM_DOCS/DETRAN_CONSOLIDADO/` |
| **DETRAN_NEs_571arquivos/** | 175 MB | 516 PDFs (362 DETRAN + ~154 SSP misturados — investigar) |
| **DOSSIE_COMPLETO.json** | 231 MB | Snapshot 13/04 — mais recente que qualquer fatia do PROJETO_PRODAM |
| **DOSSIE_COMPLETO_SLIM.json** | 118 MB | Slim version |
| **11 relatórios MD** | ~250 KB | Sessão 73 (31K+75K), Sessão 74 (7K), NES (5K cada), DOSSIE v4 (18K) |

---

## 5. O que `Desktop\DETRAN` duplica (1,13 GB redundantes)

| Pasta | Em Desktop\DETRAN | Em PROJETO_PRODAM | Hash |
|-------|-------------------|-------------------|------|
| DETRAN/ | 1,1 MB | `PRODAM_DOCS/DETRAN/` | ✅ Idêntico |
| DETRAN_CONSOLIDADO/ | 1,1 GB | `PRODAM_DOCS/DETRAN_CONSOLIDADO/` | ✅ Idêntico |
| DETRAN_DOSSIE/ | 34 MB | `PRODAM_DOCS/DETRAN_DOSSIE/` | ✅ Idêntico |

---

## 6. Plano de Ação — consolidar e agir

### 🔴 Imediato (hoje/amanhã)

1. **Mover `DETRAN-AM/` para PROJETO_PRODAM** — template pronto para o dossiê
2. **Integrar sessão 74 (`empenhos_COMPLETO.csv`)** como fonte canônica de NEs (resolve bug de `data_emissao` no DB)
3. **Atualizar profile DETRAN** com dados da sessão 74:
   - `faturas_exigiveis: 202` (vs 179)
   - `faturas_em_atencao: 53` (com prescrição entre 27/10/2026 e 17/03/2027)
   - `val_atualizado_sessao74: 26378697.98`
4. **Documentar em `_metadata`** a divergência R$ 8,9M entre fontes

### 🟠 Esta semana

5. **Desduplicar 1,13 GB** — apagar cópias de `Desktop\DETRAN\DETRAN_CONSOLIDADO`, `DETRAN_DOSSIE`, `DETRAN/` (redundantes)
6. **OCR dos 169 PDFs de NEs** que não estão no PROJETO_PRODAM — podem conter evidências adicionais
7. **Investigar pasta 571arquivos** — separar DETRAN de SSP (mistura)
8. **Reconciliar R$ 8,9M** com `DADOS_5DEV` (verificar se há faturas pré-2019 ou contratos extintos)

### 🟡 Próxima semana

9. **PROTOCOLAR EXECUÇÃO** — 148 faturas VIGENTES (R$ 21,8M atualizado) com cadeia FORTE + marcos interruptivos validados
10. **Interromper prescrição** das 53 ATENÇÃO via protesto/notificação (D+200 a D+341)
11. **Abandonar 1 fatura PRESCRITA** (R$ 3.169 — irrisório)

---

## 7. Números consolidados — fonte de verdade

Após auditoria cruzada, o quadro mais preciso do DETRAN é:

| Métrica | Valor |
|---------|-------|
| **CNPJ** | 04.224.028/0001-63 |
| **Ranking** | #2 de 70 devedores |
| **Força probatória** | FORTE (score 0.9318) |
| **Regime** | Penhora direta (STF Tema 253/EREsp 1.725.030) |
| **Fase** | F5 — Petição pronta |
| **Blindagem** | **22/22 OK** |
| **NEs documentadas** | **500** (sessão 74) — reconhecimento tácito massivo |
| **Faturas exigíveis** | **202** (vs 179 profile, 113 DB) |
| **Valor bruto sessão 74** | R$ 22.697.929,21 |
| **Valor atualizado (IGPM+1%+2%)** | **R$ 26.378.697,98** |
| **Faturas VIGENTES** | 148 (R$ 21,8M atualizado) |
| **Faturas em ATENÇÃO** | 53 (venc. 10/2026-03/2027) |
| **Contrato com mais peso** | C.10/2021 — 30 faturas, 48,8% do total |
| **Maiores NEs (top 5 contratos)** | C.10/2021 (R$ 83,7M), C.22/2014 (R$ 40,4M), C.4/2016 (R$ 25,2M), C.12/2021 (R$ 18,7M), C.75/2022 (R$ 16,7M) |

---

## 8. Comparação com auditoria anterior (minha, de hoje de manhã)

| Métrica | Minha auditoria (PROJETO_PRODAM DB) | Sessão 74 CSVs (`Desktop\DETRAN`) |
|---------|--------------------------------------|------------------------------------|
| Faturas | 113 | **202** |
| Valor bruto | R$ 17,8M | R$ 22,7M |
| NEs | 470 | 500 |
| Contratos com NE | 30 | 18 |
| Faturas protegidas | 93 | 148 (VIGENTES) + 53 (ATENÇÃO) = 201 |
| Prescritas | 20 | 1 |

**Sessão 74 é mais completa** — considerando que era o snapshot SPCF exportado para CSV antes de bugs de ingestão.

**Ação:** tratar sessão 74 como **fonte primária** e usar DB como referência secundária após fix do bug de `data_emissao`.

---

## 9. Arquivos gerados nesta auditoria cruzada

| Arquivo | Local | Conteúdo |
|---------|-------|----------|
| `AUDITORIA_CRUZADA_DESKTOP_DETRAN.md` | PROJETO_PRODAM/DETRAN_AUDITORIA/ | Este relatório |
| `RELATORIO_DETRAN.md` | idem | Auditoria inicial (só PROJETO_PRODAM) |
| `DETRAN_DATASET.json`, CSVs | idem | Dados estruturados |
| `dashboard.html` | idem | Visual Chart.js |

---

_Auditoria cruzada executada por 2 agentes Explore em paralelo (14/04/2026, 14:45). Fontes: `Desktop\DETRAN` + `PROJETO_PRODAM` + `prodam.db`._
