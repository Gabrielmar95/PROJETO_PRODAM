# Workflow de Cobrança — PROJETO PRODAM
_Pipeline end-to-end F0→F6. Atualizado em 26/05/2026 13:14._

Cada devedor avança pelas fases abaixo. O campo `fase_atual` em `profiles.json` rastreia o ponto vigente; `historico_fases` registra a trajetória.

## F0 — Triagem inicial
- **Objetivo**: identificar se o devedor está no portfólio e mapear documentação básica.
- **Skills**: `triage`, `decisao-documental-prodam` (cadeia 5 elos).
- **Gates documentais**: contrato vigente, CNPJ confirmado, categoria (Gov Direta/Indireta/Privada).
- **Prazo típico**: 1-3 dias.
- **Saída**: entrada em `profiles.json` com `categoria`, `forca_probatoria`, `score_composto` preliminar.

## F1 — Análise documental
- **Objetivo**: validar cadeia Contrato + NE + NF + Atesto (REsp 793.969/RJ).
- **Skills**: `auditoria_completude_devedor`, `dossie_multiformato_devedor`.
- **Gates**: 11 itens do checklist; identificação de marcos interruptivos (empenhos = Art. 202 VI CC).
- **Prazo típico**: 5-10 dias por devedor.
- **Saída**: dossiê multi-formato (JSON + XLSX + CSV + MD + PDF).

## F2 — Classificação e priorização
- **Objetivo**: definir `proximo_passo` e `prioridade_rank`.
- **Skills**: `classificacao-prodam`, score composto 12 dimensões.
- **Gates**: aprovação humana antes de mover devedor para F3+ (gate documental jurídico).
- **Prazo típico**: 1-2 dias.
- **Saída**: rank atualizado em `profiles.json`.

## F3 — Notificação extrajudicial (TRD)
- **Objetivo**: emitir Termo de Reconhecimento de Dívida ou notificação extrajudicial.
- **Skills**: `protocolo-juridico-prodam`, `trd-gerador-prodam`.
- **Gates**: mostrar diff antes de salvar; revisão humana; envio com AR ou e-mail certificado.
- **Prazo típico**: 15-30 dias entre emissão e resposta esperada.
- **Saída**: documento `.docx` em `DOCUMENTOS_GERADOS/`, registro em `historico_fases`.

## F4 — Negociação / Resposta
- **Objetivo**: acompanhar resposta do devedor (aceite, contraproposta, silêncio).
- **Skills**: `negociacao-prodam`.
- **Gates**: silêncio não interrompe prescrição (regra #2); registrar ato inequívoco se houver.
- **Prazo típico**: 30-60 dias.
- **Saída**: atualização de `ultima_interacao` e `evidencias_reconhecimento`.

## F5 — Protocolo judicial / Execução
- **Objetivo**: ajuizar ação ou pedir habilitação de crédito.
- **Skills**: `peticao-inicial-prodam`, `habilitacao-credito-prodam`.
- **Gates**: Adm. Direta → precatório/RPV (Art. 100 CF); Adm. Indireta concorrencial → penhora direta (Tema 253/STF).
- **Prazo típico**: 60-180 dias para distribuição inicial.
- **Saída**: `data_protocolo` preenchida; `via_processual_recomendada` definida.

## F6 — Recebimento / Encerramento
- **Objetivo**: confirmar pagamento, baixar do portfólio, calcular fee 20%.
- **Skills**: `controle-recebimento-prodam`.
- **Gates**: comprovante de depósito; cálculo de SELIC pós-trânsito; nota de honorários.
- **Prazo típico**: variável (precatório AM tem fila própria).
- **Saída**: `valor_recuperado` registrado; devedor marcado como encerrado.

## Princípios transversais
- **Prescrição é por fatura individual** (regra #7). Cada fase recalcula faturas em risco.
- **PDFs nunca são apagados** — prova jurídica. Backup em `_BACKUPS/`.
- **`profiles.json` é SSOT** — qualquer fase atualiza apenas via PR ou edit auditado.
- **Fee 20% recuperado**, RPV/AM = 20 SM (Lei AM 2.748/2002).

