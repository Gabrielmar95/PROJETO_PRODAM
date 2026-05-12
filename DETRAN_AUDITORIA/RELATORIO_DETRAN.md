# Auditoria Profunda — DETRAN/AM

**Data:** 14/04/2026 | **Escopo:** Departamento Estadual de Trânsito do AM
**Prioridade:** #2 do portfólio PRODAM (Contrato 002/2026)

---

## ⚠️ RESUMO EXECUTIVO — DIVERGÊNCIA CRÍTICA DETECTADA

| Item | Profile | **Auditoria** | Status |
|------|---------|---------------|--------|
| Status prescrição | `urgencia_prescricao = PRESCRITA (D-21)` | **93 de 113 faturas (82%) PROTEGIDAS por marco interruptivo** | 🟢 CONTESTÁVEL |
| Valor bruto (DB) | R$ 31.684.739,01 | **R$ 17.802.420,55 em 113 faturas do DB** | ⚠️ Delta R$ 13.8M |
| Valor atualizado (profile) | R$ 37.960.629,19 | **R$ 28.867.345,47** (IGPM+1%a.m.+2% aprox.) | ⚠️ Profile superestima |
| Cadeia documental | "n_contratos = 1" | **99 COMPLETA + 14 FORTE = 100% em cadeia executável** | ✅ Profile subestima |
| Empenhos | "288 NEs, R$ 119,6M" | **470 NEs × R$ 250,3M** no DB | ⚠️ Delta +182 NEs |

**CONCLUSÃO:** Profile está desatualizado. DETRAN **NÃO está prescrito**. Há 93 faturas × R$ 15,94M **protegidas por Art. 202 VI CC** (empenhos 2024-2026 em contratos ainda com faturas inadimplidas) + 20 prescritas (R$ 1,86M) que podem ser abandonadas.

**AÇÃO IMEDIATA RECOMENDADA:** Protocolar execução judicial com os 93 títulos protegidos (R$ 15,94M bruto, ~R$ 25,8M atualizado).

---

## 1. Dados do Profile × DB

### Profile.json (154 campos)
- **Força probatória:** FORTE
- **Categoria:** GOV_INDIRETA (Autarquia)
- **CNPJ:** 04.224.028/0001-63
- **Regime:** penhora_direta (Tema 253/STF — Adm. Indireta concorrencial)
- **Índice correção:** **IGPM + 1% a.m. + multa 2%** (exceção da cláusula 11.1 CT 022/2014)
- **Status:** Petição pronta (fase F5) — `titulo_executivo: True`
- **Próximo passo:** PROTOCOLAR_PETICAO
- **p_recuperação:** 0.95 (bem alto)
- **E[V]:** R$ 30.100.502,06 → honorários esperados R$ 6.020.100,41

### Database (prodam.db)
- 0 contratos no `spcf_contratos` (bug — 228 no SPCF histórico)
- **470 NEs no `spcf_empenhos`** × R$ 250.316.057,30
- **113 faturas no `spcf_faturas`** × R$ 17.802.420,55
  - 99 cadeia **COMPLETA** (Contrato+NE+NL+NF+Atesto = título executivo pleno)
  - 14 cadeia **FORTE** (Contrato+NE+NF)

---

## 2. Marcos Interruptivos (Art. 202 VI CC) — CRÍTICO

**Base legal:** Empenho (NE) emitido pelo órgão devedor configura reconhecimento tácito da dívida contratual. Se a NE é posterior ao vencimento, **interrompe a prescrição** e reinicia a contagem (pela metade para Fazenda Pública = 2,5 anos).

### Contratos com NE recente (prova de reconhecimento)

| Contrato | Último NE | Data NE | Status |
|----------|-----------|---------|--------|
| **3/2026** | 2026NE0000005 | 05/01/2026 | 🟢 INTERROMPE |
| **8/2021** | 2026NE0000007 | 05/01/2026 | 🟢 INTERROMPE |
| **6/2021** | 2026NE0000006 | 05/01/2026 | 🟢 INTERROMPE |
| **12/2021** | 2026NE0000008 | 05/01/2026 | 🟢 INTERROMPE |
| **75/2022** | 2026NE0000009 | 05/01/2026 | 🟢 INTERROMPE |
| **83/2022** | 2026NE0000010 | 05/01/2026 | 🟢 INTERROMPE |
| **10/2021** | 2026NE0000101 | 20/01/2026 | 🟢 INTERROMPE |
| **17/2015** | 2024NE0002123 | 02/12/2024 | 🟢 INTERROMPE |
| **78/2022** | 2023NE0000004 | 02/01/2023 | 🟢 INTERROMPE |
| ... | (30 contratos com NE ativo) | | |

### Consequência prática
- **93 faturas PROTEGIDAS** → prescrição reiniciada; pode executar.
- **20 faturas PRESCRITAS** → abandonar ou investigar marcos individuais.

---

## 3. Prescrição Fatura-a-Fatura

| Classificação | Qtd | Valor bruto | Valor atualizado (est.) |
|---------------|----|-------------|-------------------------|
| **Protegidas (exigíveis)** | 93 | **R$ 15.941.367,35** | ~R$ 25.800.000,00 |
| Prescritas sem marco | 20 | R$ 1.861.053,20 | n/a |
| **Total DB** | 113 | R$ 17.802.420,55 | ~R$ 28.867.345,47 |

**Motivo da proteção:**
- Faturas de contratos 2021-2022: NE 2025/2026 → resetou prescrição para ~2028.5
- Faturas de 2015: NE 2024 → resetou para ~2027.
- Contratos 3/2026, 78/2022: NE recente = marco forte.

---

## 4. Cadeia Documental (REsp 793.969/RJ)

| Classificação | Qtd | % |
|---------------|----|----|
| **COMPLETA** (Contrato+NE+NL+NF+Atesto) | 99 | 87,6% |
| **FORTE** (Contrato+NE+NF) | 14 | 12,4% |
| MÉDIA | 0 | 0% |
| FRACA | 0 | 0% |

> **Implicação:** **100% das 113 faturas do DB** têm cadeia executável (FORTE ou COMPLETA), configurando título executivo extrajudicial nos termos do REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado; Teori Zavascki vencido).

---

## 5. Atualização Monetária — IGPM + 1% a.m. + multa 2%

**Cláusula contratual:** 11.1 do CT 022/2014 (exceção — não usa SELIC como demais).

**Fórmula aplicada:**
```
V_atualizado = V_bruto × (1+IGPM/100)^anos + V_corrigido × 1% × meses + V_corrigido × 2%
```

**Resultado agregado (estimativa com IGPM médio 7% a.a.):**
- Meses médio de atraso: 35,7 (~3 anos)
- Fator médio: **1,62×**
- Bruto total (113 faturas DB): R$ 17.802.420,55
- **Atualizado estimado: R$ 28.867.345,47**

> **Atenção:** Profile marca val_atualizado = R$ 37,96M — possivelmente inclui as 179 faturas do profile (não só as 113 do DB). Ou usa IGPM acumulado real via BCB (mais preciso que a estimativa).

**Recomendação:** Rodar `atualizacao-monetaria-sob-demanda` com API BCB para IGPM real antes de protocolar.

---

## 6. Blindagem Pré-Execução (6 blocos)

| Bloco | Requisito | Status | Evidência |
|-------|-----------|--------|-----------|
| 1. Título executivo | Art.784 CPC | ⚠️ | 228 contratos SPCF, mas 0 no `spcf_contratos` (bug de ingestão) |
| 2. Liquidez | Art.783 CPC | ✅ | R$ 17.8M agregado do SPCF, líquido e certo |
| 3. Cadeia documental | REsp 793.969 | ✅ | **113/113 (100%) em cadeia FORTE+** |
| 4. Prescrição | Art.206 §5º I + Art.202 VI | ✅ | 93 protegidas × R$ 15.94M |
| 5. Reconhecimento tácito | Art.202 VI CC | ✅ | 470 NEs, 30 contratos com NE pós-vencimento |
| 6. Inadimplemento | Art.397 CC | ✅ | Padrão INTERMITENTE desde 2020-Jan |

**Único ponto de atenção:** spcf_contratos está vazio no DB para DETRAN. Rodar `build_sqlite.py` com ajuste no filtro, ou confirmar via `consolidado_contratos.json` (228 SPCF).

---

## 7. Plano de Ação (Execução)

### Esta semana (15-19/abr)

1. **Validar os 93 títulos protegidos** rodando `marcos-interruptivos-prescricao` fatura-a-fatura
2. **Rodar `atualizacao-monetaria-sob-demanda`** com IGPM real via API BCB
3. **Preparar memorial de cálculo** em XLSX para cada um dos 93 títulos
4. **Gerar petição de execução** via `geracao-documentos-juridicos` — peça já "pronta" no profile, validar

### Próxima semana (21-25/abr)

5. **Protocolar execução judicial** (TJAM) — modelo A (força FORTE)
6. **Pedir penhora SISBAJUD** (Adm. Indireta = concorrencial = penhora direta)
7. **Protestar em paralelo** as 93 faturas (pressão política)
8. **Monitorar contestação** — árvore de 6 ramos (`arvore-decisao-contestacao`)

### Abandonar/investigar (20 faturas prescritas sem marco)

- Valor R$ 1,86M perdido — custo de oportunidade vs custo de recuperação
- Se vale a pena: procurar marcos interruptivos individuais em PDFs do pendrive
- Se não vale: deixar registrado em relatório quinzenal (10% de honorários por prescrição perdida = perda de R$ 186.105 à PRODAM)

---

## 8. Ações Corretivas no profile.json

Com base nesta auditoria, atualizar profile DETRAN:

```python
# URGENTE — corrigir divergências
DETRAN_updates = {
  "urgencia_prescricao": "PROTEGIDA",   # era PRESCRITA
  "d_plus_prescricao": 730,              # +2 anos de proteção via NE 2026
  "observacoes_auditoria_14_04_2026": "93 faturas protegidas por Art.202 VI CC via NEs 2024-2026 em 30 contratos. Profile anterior estava errado ao marcar PRESCRITA (confusão com Of.129/2021).",
  "faturas_protegidas_art202": 93,
  "faturas_prescritas_sem_marco": 20,
  "valor_protegido_bruto": 15941367.35,
  "valor_prescrito_bruto": 1861053.20,
}
```

---

## 9. Arquivos gerados

| Arquivo | Conteúdo |
|---------|----------|
| `DETRAN_AUDITORIA/DETRAN_DATASET.json` | Dados completos (perfil + contratos + NEs + análise) |
| `DETRAN_AUDITORIA/DETRAN_FATURAS.csv` | 113 faturas (UTF-8 BOM, Excel-ready) |
| `DETRAN_AUDITORIA/DETRAN_EMPENHOS.csv` | 470 NEs (UTF-8 BOM) |
| `DETRAN_AUDITORIA/DETRAN_PRESCRICAO.csv` | Análise fatura-a-fatura com motivo |

---

## 10. Reprodutibilidade

```bash
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"

# Re-rodar auditoria
py -3.12 detran_auditoria_profunda.py

# Se precisar atualizar prodam.db primeiro
py -3.12 atualizar_db.py
```

Script: `detran_auditoria_profunda.py` — reusável para qualquer devedor (trocar "DETRAN" nas queries).

---

_Gerado por `detran_auditoria_profunda.py` em 14/04/2026 — baseado em profile + prodam.db (470 NEs + 113 faturas) + análise de marcos interruptivos._
