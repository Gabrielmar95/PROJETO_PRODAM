---
name: agente-reconhecimento-tacito
description: >
  Agente E3.4 do Sistema Multi-Agente PRODAM. Varre extratos SPCF, empenhos, NLs, atos administrativos do devedor e identifica os 17 atos tácitos de reconhecimento de dívida catalogados em 4 categorias (orçamentário, administrativo, financeiro, comportamental). Classifica força (FORTÍSSIMO/FORTE/MÉDIO) para cada evidência encontrada. No DETRAN, deve enumerar ≥270 evidências (95% recall das 286 conhecidas).
version: 1.0-mvp
updated: 2026-04-19
triggers: ["reconhecimento tácito", "marcos de reconhecimento", "Art. 202 VI CC", "rodar E3.4"]
keywords: [reconhecimento tácito, Art. 202 VI, empenho, NL, E3.4]
---

# SKILL — Reconhecimento-Tácito (E3.4)

**Versão:** 1.0-mvp | **Esquadrão:** E3 Jurídico | **Papel:** cataloga atos do devedor que renovam prescrição.

## 0. Quando invocar
Pode rodar em paralelo com E3.2 e E3.3. Alimenta E3.3 com marcos identificados.

## 1. Input
- `dossie_unificado.json` (seção devedor)
- Extratos SPCF
- Empenhos, NLs e atos administrativos disponíveis

## 2. Lógica (17 atos catalogados em 4 categorias)
| Categoria | Exemplos |
|---|---|
| **Orçamentário** | Empenho inscrito em RP; LOA com reserva; abertura de crédito adicional |
| **Administrativo** | Ofício de reconhecimento; parecer da PGE/consultoria; portaria designando fiscal novo do CT |
| **Financeiro** | Pagamento parcial da NF; depósito em juízo; compensação autorizada |
| **Comportamental** | Solicitação de parcelamento; pedido de nova NF; aceite técnico emitido pós-mora |

Para cada evidência, classifica força:
- **FORTÍSSIMO**: ato formal escrito com assinatura e data (ex: NL, parecer da PGE)
- **FORTE**: ato documentado mas sem assinatura formal (ex: empenho inscrito em RP)
- **MÉDIO**: ato comportamental com contexto (ex: solicitação verbal registrada)

## 3. Output
- `19_ESTADO_AGENTES/03_JURIDICO/reconhecimentos.json` — lista de evidências com categoria, força, data, fonte.
- Alimenta `prescricao.json` (E3.3) com marcos interruptivos.

## 4. Integração
- Skills base: `reconhecimento-divida-tacito`, `revisar-reconhecimento-divida` (instaladas).

## 5. Status MVP
**WRAPPER** — invoca skills existentes.

## 6. Teste alvo (ajuste C tolerância)
DETRAN deve enumerar **≥ 270 evidências** (95% recall das 286 conhecidas). Evidências novas viram candidatas a revisão manual, não bug.

## 7. Restrições
- Cada evidência vem com ref ao documento/extrato fonte para auditoria.
- Perspectiva=credor implícita (marcos a favor). O adversarial E4.1 **ataca** esses marcos.
