# Workflow de Cobrança — PROJETO PRODAM
_Pipeline end-to-end F0→F6. Atualizado em 10/06/2026 21:32._

Cada devedor avança pelas fases abaixo. O campo `fase_atual` em `profiles.json` rastreia o ponto vigente; `historico_fases` registra a trajetória.

## F0 — Triagem inicial
- **Objetivo**: identificar se o devedor está no portfólio e mapear documentação básica.
- **Skills**: `triage` (agent skill) · `classificacao-forca-probatoria` · `validador-cadeia-documental-fatura` (cadeia 5 elos).
- **Gates documentais**: contrato vigente, CNPJ confirmado, categoria (Gov Direta/Indireta/Privada).
- **Prazo típico**: 1-3 dias.
- **Saída**: entrada em `profiles.json` com `categoria`, `forca_probatoria`, `score_composto` preliminar.

## F1 — Análise documental
- **Objetivo**: validar cadeia Contrato + NE + NF + Atesto (REsp 793.969/RJ).
- **Ferramentas**: `scripts/auditoria_completude_devedor.py`, `scripts/dossie_multiformato_devedor.py` + skill `auditoria-completude-devedor`.
- **Gates**: 11 itens do checklist; identificação de marcos interruptivos (empenhos = Art. 202 VI CC).
- **Prazo típico**: 5-10 dias por devedor.
- **Saída**: dossiê multi-formato (JSON + XLSX + CSV + MD + PDF).

## F2 — Classificação e priorização
- **Objetivo**: definir `proximo_passo` e `prioridade_rank`.
- **Skills**: `classificacao-forca-probatoria` (score composto 12 dimensões) · `proximo-passo-advisor`.
- **Gates**: aprovação humana antes de mover devedor para F3+ (gate documental jurídico).
- **Prazo típico**: 1-2 dias.
- **Saída**: rank atualizado em `profiles.json`.

## F3 — Notificação extrajudicial (TRD)
- **Objetivo**: emitir Termo de Reconhecimento de Dívida ou notificação extrajudicial.
- **Skills**: `protocolo-juridico-prodam` · `geracao-documentos-juridicos` (TRD/notificações) · `revisar-reconhecimento-divida` (gate antes do TRD).
- **Gates**: mostrar diff antes de salvar; revisão humana; envio com AR ou e-mail certificado.
- **Prazo típico**: 15-30 dias entre emissão e resposta esperada.
- **Saída**: documento `.docx` em `DOCUMENTOS_GERADOS/`, registro em `historico_fases`.

## F4 — Negociação / Resposta
- **Objetivo**: acompanhar resposta do devedor (aceite, contraproposta, silêncio).
- **Skills**: `registro-interacoes-devedor` · `arvore-decisao-contestacao` (réplicas a contestações).
- **Gates**: silêncio não interrompe prescrição (Regra 3 do CLAUDE.md); registrar ato inequívoco se houver.
- **Prazo típico**: 30-60 dias.
- **Saída**: atualização de `ultima_interacao` e `evidencias_reconhecimento`.

## F5 — Protocolo judicial / Execução
- **Objetivo**: ajuizar ação ou pedir habilitação de crédito.
- **Skills**: `blindagem-pre-execucao` (checklist pré-protocolo) · `montagem-dossie-comprobatorio` · `precatorios-rpv-fragmentacao` (Adm. Direta).
- **Gates**: Adm. Direta → precatório/RPV (Art. 100 CF); Adm. Indireta concorrencial → penhora direta (Tema 253/STF).
- **Prazo típico**: 60-180 dias para distribuição inicial.
- **Saída**: `data_protocolo` preenchida; `via_processual_recomendada` definida.

## F6 — Recebimento / Encerramento
- **Objetivo**: confirmar pagamento, baixar do portfólio, calcular fee 20%.
- **Skills**: `registro-interacoes-devedor` (baixa e histórico) · `gerador-relatorio-quinzenal` (prestação de contas).
- **Gates**: comprovante de depósito; cálculo de SELIC pós-trânsito; nota de honorários.
- **Prazo típico**: variável (precatório AM tem fila própria).
- **Saída**: `valor_recuperado` registrado; devedor marcado como encerrado.

## Princípios transversais
- **Prescrição é por fatura individual** (Regra 2 do CLAUDE.md). Cada fase recalcula faturas em risco.
- **PDFs nunca são apagados** — prova jurídica (NUNCA-1). Backup em `_BACKUPS/`.
- **`profiles.json` é SSOT** (NUNCA-6) — qualquer fase atualiza apenas via PR ou edit auditado.
- **Fee 20% recuperado**; RPV/AM = 20 × SM vigente (Lei AM 2.748/2002 — Regra 12).

