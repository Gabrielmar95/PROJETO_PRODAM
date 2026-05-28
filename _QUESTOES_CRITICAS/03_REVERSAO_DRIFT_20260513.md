# 03 — Reversão de Drift 13/05/2026 — Auditoria forense

> Status: needs-human-decision (BLOQUEIA item 1.6 do roadmap — envio TRD SES/SUSAM)
> Aberto em: 2026-05-28 (Janela 1 item 1.2)
> Origem: Ressalva 5 do plano + arquivo `_BACKUPS/profiles_PRE-REVERSAO-DRIFT-20260513-155115.json` (334 KB)
> Decisor: Gabriel Mar (gate humano obrigatório)

## TL;DR

A "reversão de drift" de 13/05/2026 **desfez silenciosamente** uma reconciliação metodológica validada na **Sessão TRD SES/SUSAM (12/05)**. O CSV atual contém os valores **anteriores** à reconciliação, e o TRD em `DOCUMENTOS_GERADOS/SES_SUSAM/TRD_SES_SUSAM_2026-05-12.docx` foi gerado com os valores **posteriores** — **as duas fontes não batem**, e enviar o TRD nessas condições é risco jurídico material.

| Métrica | Backup 12/05 (reconciliado) | CSV atual (reversed) | Delta |
|---|---:|---:|---:|
| SES/SUSAM val_exig | R$ 4.783.356,52 | R$ 14.748.048,96 | **+R$ 9,96M** (+208%) |
| SES/SUSAM val_atualizado | R$ 8.230.061,40 | R$ 43.921.619,17 | **+R$ 35,69M** (+434%) |
| SES/SUSAM fat_exig | 82 | 144 | +62 faturas |
| SES/SUSAM status | "TRD protocolado" | proximo_passo: `ENVIAR_TRD` | **contradição lógica** |

## Metodologia da auditoria

1. Diff de chaves (siglas) entre backup JSON e CSV atual: **0 sumidas, 0 entradas** (conjunto idêntico de 69 devedores).
2. Diff de campos críticos (`val_exig`, `val_atualizado`, `faturas_exigiveis`, `faturas_prescritas`): **4 siglas com divergências materiais**.
3. Forensics nos campos `*_anterior` do backup (rastro de reconciliações intermediárias).
4. Cruzamento com `DOCUMENTOS_GERADOS/SES_SUSAM/` e `.continue-here.md`.

## Achados

### A. SES/SUSAM — reversão DOCUMENTADA pela própria estrutura do backup

O backup preserva **12 campos `*_anterior`** para SES/SUSAM, que registram exatamente a história da reconciliação:

| Campo | Valor | Significado |
|---|---|---|
| `val_exig_anterior` | R$ 14.748.048,96 | **Idêntico ao CSV atual** — base pré-reconciliação |
| `val_exig` | R$ 4.783.356,52 | Novo valor pós-reconciliação 12/05 |
| `val_atualizado_v1_anterior` | R$ 43.921.619,17 | **Idêntico ao CSV atual** |
| `val_atualizado_v2_anterior` | R$ 8.135.935,19 | Versão intermediária da reconciliação |
| `val_atualizado` | R$ 8.230.061,40 | Final pós-reconciliação |
| `faturas_exigiveis_anterior` | 144 | **Idêntico ao CSV atual** |
| `faturas_exigiveis` | 82 | Final pós-reconciliação |
| `val_atualizado_metodologia` | "SELIC série BCB 4390 acumulada mensal, fator médio ponderado 1.720562x, data-base 2026-05-12, CÁLCULO FATURA-A-FATURA via `scripts/ad_hoc/gerar_memorial_preliminar_ses.py`" | **Documenta a metodologia rigorosa do novo valor** |
| `data_prescricao_proxima_v1_anterior` | 2026-08-31 | Versão antes do fix de parsing DD/MM/YYYY |
| `data_prescricao_proxima_v2_anterior` | 2028-09-30 | Versão corrigida |
| `faturas_exigiveis_breakdown` | dict com tier1/tier2 | **Composição rigorosa**: 3 Tier1 (D+141, contrato 74/2021 sem NE protetora, Art. 206 §5º I CC) + 79 Tier2 (ressuscitadas por NE 2026, D+851-878, Decreto 20.910/1932) |
| `cenario_monte_carlo_p50_v1/v2_anterior` | R$ 7,79M / R$ 1,44M | Cenários de recuperação simulados |

**Diagnóstico mecânico**: a reconciliação 12/05 reduziu a base de R$ 14,75M (soma bruta de todas faturas com saldo) para R$ 4,78M (cálculo fatura-a-fatura considerando tier1 com risco real iminente + tier2 ressuscitadas por NE 2026, descartando 50 faturas canceladas + 12 com prescrição confirmada).

**Após 13/05**: o JSON foi regerado a partir de fonte pré-reconciliação (provavelmente SPCF bruto ou CSV antigo), perdendo o trabalho metodológico. O TRD em disco usa os valores reconciliados; o "SSOT" atual (CSV) usa os anteriores.

### B. SSP — divergência sutil de bucketing (15 faturas)

| Campo | Backup | CSV | Delta |
|---|---:|---:|---:|
| faturas_total | 181 | (não comparável) | — |
| faturas_exigiveis | 66 | 81 | **+15 no CSV** |
| faturas_prescritas | 114 | 115 | +1 |
| val_exig | R$ 4.553.230,80 | R$ 4.553.230,80 | **0** (idêntico) |

O valor monetário não muda, mas **15 faturas adicionais foram classificadas como "exigíveis" no CSV** sem alterar o total. Hipótese: o backup tinha bucketing mais conservador (provavelmente excluindo faturas com NE expirada ou status duvidoso); o CSV regenerado tem bucketing mais largo.

**Perda colateral grave**: o backup tinha `evidencias_reconhecimento: 125` e `reconhecimento_revisado` (dict completo classificando as 125 evidências por tipo: 117 tipo E, 3 tipo F, 2 tipo H, 1 cada B/D/G; classificação "CONFIRMADO — RD no AFI"). **Esse é o fundamento Art. 202 VI CC para reabrir a prescrição do SSP** — perdido no CSV (não há coluna correspondente).

### C. SEJUSC e FENIXSOFT — divergências menores em contagem de faturas

| Sigla | Δ fat_exig (CSV - backup) | Δ fat_presc | Δ val_exig | Status |
|---|---:|---:|---:|---|
| SEJUSC | -4 | -7 | ~0 | Análise pendente / ANALISAR_DOCUMENTACAO |
| FENIXSOFT | -5 (5 prescritas viraram exigíveis?) | -5 | 0 | Backup: 2 exig + 5 presc = 7 total; CSV: 7 exig + 0 presc = 7 total |

**FENIXSOFT é particularmente confuso**: backup tem 2 exigíveis + 5 prescritas; CSV tem **7 exigíveis e 0 prescritas**. Significa que **5 faturas prescritas no backup foram reclassificadas como exigíveis no CSV** — sem justificativa documental. Combinado com a Issue `06_FENIXSOFT2_INVESTIGACAO.md` (R$ 1,07M na Rota B 12/05 versus R$ 888.250 no CSV), o FENIXSOFT é uma **bagunça de 3 versões diferentes** que precisa ser fechada antes de qualquer notificação extrajudicial.

### D. Perda informacional massiva — schema JSON → CSV

O JSON do backup tem **128 campos por devedor** (exemplo SSP: 128 campos); o CSV tem **11 colunas**. Foram perdidos no SSOT atual, para cada devedor:

- `evidencias_reconhecimento` (contagem de marcos interruptivos Art. 202 VI CC)
- `reconhecimento_revisado` (estrutura tipo + classificação)
- `cnpj` (identificador fiscal!)
- `modelo_notificacao` (A/B/C — qual template usar)
- `regime_execucao` (precatório/penhora direta)
- `indice_correcao`, `juros_mora`, `multa`
- `score_composto`, `p_recuperacao`, `ev_valor_esperado`, `ev_honorarios`, `esforco_estimado` (toda a modelagem de priorização)
- `val_orig`, `val_servicos_spcf_mar2026` (baselines)
- `*_anterior` e `*_metodologia` (rastros de mudanças)
- `observacoes_*`, `ultima_interacao`, `classificacao_reconhecimento`

**Implicação**: nenhuma decisão jurídica "definitiva" sobre prescrição/notificação/petição pode ser tomada apenas com base no CSV. O CSV é triagem; o JSON era a fonte real. **O CSV não é SSOT — é um índice resumido**.

### E. Outras siglas — apenas arredondamento decimal

As 27 outras siglas com "divergência" no diff inicial são todas **diferenças de precisão decimal** (backup com 15 dígitos significativos do float Python; CSV truncado para 2 casas). Delta absoluto < R$ 1,00 em todos os casos. Não é problema material — é apenas falta de quantização consistente.

### F. Outras siglas com rastro de reconciliação interrompida

Além de SES/SUSAM (12 campos `*_anterior`), apenas **DETRAN** tem 1 campo `*_anterior` (`cenario_monte_carlo_p50_anterior`). Nenhuma outra sigla tem evidência de reconciliação interrompida.

## Riscos imediatos

| # | Risco | Janela 1 item afetado | Severidade |
|---|---|---|---|
| 1 | Enviar TRD SES/SUSAM com valores R$ 4,78M (do .docx) contradiz "SSOT" CSV (R$ 14,75M). Adversário usa inconsistência para derrubar credibilidade. | **1.6 BLOQUEADO** | 🚨 |
| 2 | Atualizar TRD para R$ 14,75M (alinhar com CSV) perde a fundamentação metodológica do tier1/tier2, deixa demanda inflada sem cálculo fatura-a-fatura | **1.6 BLOQUEADO** | 🚨 |
| 3 | Decidir sobre SSP (1.1) sem as 125 evidências de reconhecimento (perdidas no CSV) significa decidir sobre Art. 202 VI CC às cegas | **1.1 LIMITADO** | 🔴 |
| 4 | Notificar FENIXSOFT (1.3) com 3 versões diferentes do valor (R$ 888K/R$ 1,07M/etc.) sem CNPJ canônico → peça frágil | **1.3 BLOQUEADO** | 🔴 |
| 5 | Multa contratual R$ 500/dia + 10% perda incide a partir do momento em que prescrição se consuma; cada dia parado sem decisão = exposição maior | (todos) | 🟡 |

## Decisões pendentes (gate humano obrigatório)

### Decisão 1 — Qual valor SES/SUSAM é o "real"?

| Opção | Valor | Fundamento | Risco |
|---|---|---|---|
| **A. R$ 4,78M (backup 12/05)** | exigível R$ 4.78M / atualizado R$ 8.23M / 82 faturas | Cálculo fatura-a-fatura, tier1 (Art. 206 §5º I CC) + tier2 (Decreto 20.910/1932 NE+2,5a), metodologia SELIC documentada | Pode ser questionado se 12/05 incluiu erros |
| **B. R$ 14,75M (CSV atual)** | exigível R$ 14.75M / atualizado R$ 43.92M / 144 faturas | Soma bruta SPCF de todas faturas com saldo > 0 | Inflado, sem reconciliação fatura-a-fatura, sem justificativa metodológica |

**Recomendo Opção A** porque: (i) é a única com metodologia documentada (`val_atualizado_metodologia` no backup), (ii) é defensável adversarialmente (tier1+tier2 com fundamentação jurídica), (iii) preserva o trabalho de uma sessão TRD validada.

### Decisão 2 — Restaurar profiles.json a partir do backup?

| Opção | Ação | Consequência |
|---|---|---|
| **R1. Restauração total** | `cp _BACKUPS/profiles_PRE-REVERSAO-DRIFT-20260513-155115.json PRODAM_DOCS/profiles.json` (na máquina local com PRODAM_DOCS) e regerar CSV a partir do JSON | Recupera 128 campos por devedor, restabelece SSOT real |
| **R2. Restauração seletiva** | Copiar para o JSON local apenas os 4 devedores divergentes (SES/SUSAM, SSP, SEJUSC, FENIXSOFT) e regerar CSV | Menos invasivo, mas perde os 117 campos dos outros 65 devedores |
| **R3. Migrar para CSV definitivamente** | Expandir esquema do CSV para incluir os campos críticos (cnpj, evidencias_reconhecimento, modelo_notificacao, etc.) e abandonar JSON. Backup vira `_ARQUIVO_HISTORICO/` | Solução estrutural; exige mudança no `auto_update_claude_md.py` e tooling |

**Recomendo Opção R1** como ação imediata (1 comando, reversível via git) + R3 como projeto da Janela 3.

### Decisão 3 — Investigar SSP e FENIXSOFT antes de qualquer ação

- **SSP**: validar que as 125 evidências de reconhecimento são SUSTENTÁVEIS adversarialmente (documentadas em PDFs originais, não apenas planilha). Critério: pelo menos 60% das evidências devem ser tipo "E" ou "B" (atos formais com data).
- **FENIXSOFT**: fechar Issue 06 com decisão sobre as 3 versões conflitantes (888K backup vs 1,07M Rota B vs 888K CSV com bucketing diferente). Sem PRODAM_DOCS local, fica bloqueado.

## Causa raiz provável

O script `scripts/auto_update_claude_md.py` ou um pipeline equivalente (não identificado) provavelmente regenerou o JSON a partir do CSV/SPCF entre 12/05 e 13/05, apagando os campos `*_anterior` e os 117 campos extras do schema rico. Como o auto_update é "all-or-nothing" (bug D4 do plano), perdas de campos manuais são esperadas — mas dessa vez aconteceu **sem changelog em `HISTORICO_SESSOES.md`** e **sem alerta humano**.

**Mitigação estrutural** (já planejada na Janela 2 item 2.6 e Janela 3 item 3.2):
- Refactor `auto_update_claude_md.py` para preservar campos via tags `<!-- manual:start --> ... <!-- manual:end -->`
- Hook PostToolUse que dispara auto_update quando CSV muda
- CI job que regenera CLAUDE.md em push

Mas **a falha real foi de governança**: a reconciliação 12/05 não foi commitada com a metodologia clara, e a reversão 13/05 não foi explicada. Sem `_QUESTOES_CRITICAS/03/` aberta na época, o achado escapou por 15 dias.

## Próximos passos

1. **Gabriel decide** Decisões 1 + 2 acima (gate humano).
2. **Se R1** (restauração): rodar na máquina local
   ```powershell
   cd C:\Users\gabri\Desktop\PROJETO_PRODAM
   Copy-Item PRODAM_DOCS\profiles.json PRODAM_DOCS\profiles.json.bak.before-restore-20260528
   Copy-Item _BACKUPS\profiles_PRE-REVERSAO-DRIFT-20260513-155115.json PRODAM_DOCS\profiles.json
   py -3.12 scripts\auto_update_claude_md.py    # regenerar CLAUDE.md
   # Validar diff manual antes de commitar
   git diff CLAUDE.md
   ```
3. **Se A** (valor R$ 4,78M aceito): item 1.6 destravado, TRD pode ser enviado como está.
4. **Investigar SSP** com 125 evidências (item 1.1) usando o JSON restaurado.
5. **Fechar Issue 06** com decisão definitiva sobre FENIXSOFT/FENIXSOFT2.

## Critério de fechamento desta issue

- [ ] Decisão 1 registrada (A ou B) com justificativa
- [ ] Decisão 2 registrada (R1, R2 ou R3) e executada
- [ ] CSV atual reflete a decisão tomada (regerado a partir do JSON restaurado, se R1)
- [ ] TRD SES/SUSAM atualizado se decisão B; mantido se decisão A
- [ ] `HISTORICO_SESSOES.md` ganha entrada explicando a auditoria de 28/05 e a decisão
- [ ] Item 1.6 do roadmap pode prosseguir

## Anexos

- `_BACKUPS/profiles_PRE-REVERSAO-DRIFT-20260513-155115.json` — 334 KB, 70 keys (69 devedores + _metadata)
- `profiles_resumo.csv` — 71 linhas (70 devedores + _metadata + header)
- `DOCUMENTOS_GERADOS/SES_SUSAM/TRD_SES_SUSAM_2026-05-12.docx` — peça pronta usando valores R$ 4,78M (reconciliados)
- `_QUESTOES_CRITICAS/06_FENIXSOFT2_INVESTIGACAO.md` — issue relacionada, bloqueada por PRODAM_DOCS
