# Parecer de Revisão Jurídica — Memorial Preliminar SEDUC (2026-06-11)

**Documento revisado:** `MEMORIAL_PRELIMINAR_SEDUC_2026-06-11.md` (SSOT `.json`)
**Veredito:** **APROVADO COM RESSALVAS** — aprovado para a apresentação interna à PRODAM de 12/06, condicionado às correções críticas 1-3 antes de qualquer uso externo (TRD/peça).

## Status das correções (aplicadas em 11/06, mesmo dia)

| # | Apontamento | Gravidade | Status |
|---|---|---|---|
| 1 | Vazamento de conteúdo interno (EV/Monte Carlo/blindagem/honorários) em doc com destinação ambígua | CRÍTICA | ✅ Tarja "USO INTERNO — não anexar à TRD/peça" no topo do MD, da ficha executiva e no `meta.classificacao` do JSON; instrução de supressão para versão externável |
| 2 | Contradição "cadeia COMPLETA/FORTE" (JSON) × "0 contratos PDF" (Ressalva 3) | CRÍTICA | ✅ Esclarecido: cadeia = classificação **registral no SPCF**; documentos físicos pendentes (legenda da tabela + Ressalva 3 reescrita) |
| 3 | Reconciliação 84→106 incompleta; "não integram o universo em aberto" impreciso | CRÍTICA | ✅ Texto trocado para "excluídas do universo de cobrança" + compromisso de conciliação id-a-id contra o prodam.db local (anexo) |
| 4 | Prescrição com delta 5×365 dias (≠ aniversário calendário, Art. 132 §3º CC) | MÉDIA | ✅ Gerador corrigido (`add_meses`: 60/30 meses calendário; 30/06/2023 → 30/06/2028) |
| 5 | SELIC mai/2026 possivelmente fechada e fora do cálculo | MÉDIA | ✅ Ressalva 7 reescrita: valores conservadores (a menor); atualizar cache na máquina local antes do protocolo (passo do RUNBOOK) |
| 6 | NEs-marco listadas só para 4 dos 6 contratos | MÉDIA | ✅ Tabela passa a listar os 6 CTs (14/2018 e 54/2017 com "NE não localizada; vinculação pendente"); Seção 2 diz "4 dos 6 contratos" |
| 7 | REsp 793.969 sem data de julgamento | COSMÉTICA | ✅ "j. 21/02/2006" acrescentado |
| 8 | `valor_bruto` sem 2 casas no JSON | COSMÉTICA | ✅ `quantize(0.01)` na serialização |
| 9 | "prova documental robusta" vago | COSMÉTICA | ✅ Reescrito: enfrentar com a cadeia Contrato+NE+NF+Atesto por fatura |

## Verificações com resultado positivo (do parecer original)
- **Citações** conferem com as Regras 1-14 do CLAUDE.md: REsp 793.969/RJ (Rel. p/ acórdão Min. José Delgado), REsp 1.963.067/MS, Tema 1.109/STJ, Art. 202 VI / 206 §5º I / 406 CC, Dec. 20.910/1932, Lei 14.905/2024, EC 113/2021 art. 3º, Decreto AM 53.464/2026. Sem Teori-como-relator, sem Lei 3.683/2012, sem 60 SM, sem multa 1%/dia.
- **Regra 9** (SELIC única, sem juros/multa somados) e **Regra 10** (regime presumido com ressalva dupla) atendidas.
- **Aritmética**: 6 faturas spot-checked exatas (ROUND_HALF_UP); totais e cenários cruzam exato (Conservador = Base − 2 Parcialmente Pagas).

## Pendências de verificação na máquina principal (fontes ausentes no clone)
1. Conferência formal contra `PRECEDENTES_VERIFICADOS.md` (Regra 13).
2. Confirmação no `PRODAM_DOCS/profiles.json` vivo: CNPJ SEDUC, números do snapshot (84 / 38,7M / 49,2M / 50,26M), EV e p50.
3. Materialização das evidências citadas: dossiê SPCF 10/06, as 38 NEs 2025-2026 (R$ 62.120.412,29) e o PDF do Of. 316/2020-GS/SEDUC.
4. Teor/vigência das 4 exceções do Decreto AM 53.464/2026 (`REFERENCIA_JURIDICA/16_AUXILIAR/`).
