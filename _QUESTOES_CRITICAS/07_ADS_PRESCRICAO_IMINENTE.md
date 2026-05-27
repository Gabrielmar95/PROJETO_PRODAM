# ADS — Decisão jurídica iminente (R$ 211.657,47, prescreve em 3 dias)

**Status:** ⚠️ JANELA CRÍTICA (3 dias) — aguarda pipeline + decisão
**Aberto em:** 2026-05-27
**Decisor:** Gabriel Mar
**Prazo:** Decisão em até **48h** (margem para enviar AR em D-1 da prescrição)

## O que sabemos do CSV

```csv
ADS,GOV_INDIRETA,FRACA,211657.47,211657.47,CLASSIFICAR,119,0,CRITICA_IMINENTE,3,
```

- Categoria: GOV_INDIRETA (penhora direta possível, Tema 253/STF)
- Força probatória: **FRACA** (auditoria documental possivelmente incompleta)
- val_exig = val_atualizado = R$ 211.657,47 (sem correção monetária aplicada)
- 119 faturas exigíveis no DB, 0 prescritas (toda exposição está nas 119)
- Próximo passo declarado: **CLASSIFICAR** (nem triada)
- `p_rec` vazio (sem estimativa de probabilidade de recuperação)

## Por que decidir antes de saber se vale a pena?

Porque a janela é menor que o ciclo de auditoria completa. Em 3 dias não dá pra rodar todo o pipeline + parecer + AR. Por isso a **rota recomendada é híbrida**: rodar pipeline AGORA (24h) + gerar notificação no mesmo dia + enviar AR em D+1.

## Comando para rodar (sua máquina Windows)

```powershell
cd C:\Users\gabri\Desktop\PROJETO_PRODAM

# 1. Rodar pipeline genérica para ADS (estima 1-2h dependendo da volume de PDFs)
py -3.12 scripts\orgao_pipeline_completa.py --orgao ADS 2>&1 | Tee-Object -FilePath _QUESTOES_CRITICAS\ADS_pipeline_run.log

# 2. Após rodar, verificar o que apareceu
py -3.12 scripts\auditoria_completude_devedor.py --devedor ADS
py -3.12 scripts\consultas.py top_devedores | findstr /I "ADS"

# 3. Re-gerar dossiê multiformato pós-pipeline
py -3.12 scripts\dossie_multiformato_devedor.py --devedor ADS

# 4. Conferir auditoria atualizada
type AUDITORIA_COMPLETUDE\AUDITORIA_ADS.md
```

## Checklist do que esperar do pipeline

| Item | O que confirma | Se sim → | Se não → |
|---|---|---|---|
| Contrato em PDF | Existência do título base | Cadeia documental OK | Bloqueio: sem título, não há peça |
| ≥1 Nota de Empenho (NE) | Marco interruptivo (Art. 202 VI CC) | Prescrição interrompida → ainda exigível | Crédito sem marco → prescrição em 3d |
| Notas Fiscais emitidas | Faturamento real | Compõe título executivo (REsp 793.969/RJ) | Só contrato é fraco |
| Aceite/atesto técnico | Reconhecimento de prestação | + força probatória | FRACA mantida |
| Cobranças anteriores | Tentativa documentada | Útil em peça | Sem inércia documentada |

## Árvore de decisão (após pipeline rodar)

```
auditoria_score >= 60% E ≥1 NE encontrada
    └─ A. Notificação extrajudicial + protesto (Recomendado)
       - Gate: decisao-documental-prodam + adversarial-meta-auditor
       - AR em D+1 da prescrição (sobra 48h de margem)

auditoria_score < 60% E há ≥1 NE
    └─ B. Notificação por AR sem protesto
       - Custo baixo, suspende inércia adversarial
       - Sem custo de cartório

ZERO marcos (NE) encontrados
    └─ C. Arquivar como perda
       - Parecer arquivando em _QUESTOES_CRITICAS/
       - Calcular 10% multa contratual (~R$ 21.165,75)
       - Documentar Tema 1.109/STJ (gestor público não renuncia tacitamente)

Pipeline trava ou inconclusivo
    └─ D. Notificação genérica em D+1 + auditoria pós-protocolo
       - Enviar AR mesmo sem cadeia completa (custo: opcional)
       - Refinar no contraditório
```

## Por que NÃO simplesmente arquivar

1. R$ 211K é 0,2% da carteira mas é 100% da multa contratual incidente (10% = R$ 21K)
2. Inércia documentada PIORA a posição em peças futuras contra GOV_INDIRETA
3. Notificação cancela início do prazo: mesmo se ADS for "perda real", o esforço de R$ 0 (AR) suspende a discussão

## O que vou fazer depois da sua resposta

**Se você rodar o pipeline e responder com o resultado**:
- Eu monto o documento jurídico (TRD ou notificação) com gate `adversarial-meta-auditor` integrado
- Você revisa, aprova, e envia AR

**Se você não conseguir rodar o pipeline em 24h**:
- Eu monto **notificação genérica** (fundamento Art. 202 II CC — protesto extrajudicial) usando dados do CSV
- Aceita-se imprecisão; o objetivo é PARAR a inércia, não ganhar a causa amanhã

## Referências

- `scripts/orgao_pipeline_completa.py` — pipeline genérica
- `scripts/auditoria_completude_devedor.py` — score 11 itens
- `adversarial-meta-auditor` (`.claude/agents/`) — gate obrigatório antes de envio
- CLAUDE.md regra #11 (unicidade Art. 202 CC, REsp 1.963.067/MS)
- CLAUDE.md regra #12 (Tema 1.109/STJ, gestor público não renuncia)
