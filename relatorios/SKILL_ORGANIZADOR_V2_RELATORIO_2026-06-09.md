# Skill `organizador-arquivos-prodam` v2.0 — Relatório de melhoria (2026-06-09)

## O que foi feito

Auditoria em 5 fases: (1) leitura integral da skill v1; (2) inventário real do acervo
por 5 subagentes em paralelo (~140 mil arquivos visíveis, ~27,8 mil PDFs — não os
~7,9 mil presumidos); (3) diagnóstico com 8 melhorias aprovadas pelo usuário;
(4) implementação; (5) bateria de testes sintéticos (25 verificações, todas passando).

## Melhorias implementadas (M1–M8)

| # | Melhoria | Evidência que a motivou |
|---|----------|------------------------|
| M1 | Pula `*_ARCHIVE*` (inegociável), `node_modules`, `.git`, `_MANIFESTO`, junctions/symlinks; avisa organização anterior | `_archive` real em SPCF_EXTRACAO; node_modules com 49.309 arquivos; junction de 25 GB documentada |
| M2 | 0 bytes nunca é duplicata (flag `ZERO_BYTES`); `stat()` protegido | ~140 arquivos 0-byte reais seriam descartados como "cópias" |
| M3 | Idempotência em colisão de nome (sufixo determinístico `_h<md5-6>`, visível no dry-run; confere MD5 de `_dup-*` legados) | re-rodar `--aplicar` criava `_dup-03`, `_dup-04`... |
| M4 | Caminhos longos: prefixo `\\?\` + flag `CAMINHO_LONGO` + truncamento de nome | 2.601 caminhos >180 chars só em PRODAM_DOCS |
| M5 | Cache de MD5 (`cache_md5.json`, chave caminho+tamanho+data) | origens reais têm 24–57 mil arquivos; rehash total a cada rodada |
| M6 | Modo `--inventario` (raio-X sem criar nada) + quase-duplicatas listadas para revisão humana | triplicata real de 203 MB no OCR_CONSOLIDADO |
| M7 | Modo `--auditar` (pasta organizada): devedor/tipo errado, manifesto × disco, exit 1 com desvio | `_ORGANIZADO` real já existente em "Arquivos Principais" |
| M8 | Devedor pelo caminho completo (não só pasta-pai) + tipos COBRANCA/EMAIL/IMAGEM/TECNICO | 2.658 arquivos em `Evidências de cobrança/<órgão>/...` caíam em `_NAO_IDENTIFICADO` |

Transversais: exit codes 0/1/2, log em arquivo, timestamps com milissegundos,
`parents[3]` protegido contra IndexError, env var `PRODAM_ROOT` como alternativa
ao caminho fixo. Compatibilidade total com as flags v1 (`--origem`, `--destino`,
`--profiles`, `--aplicar`, `--sem-subtipo`, `--limiar`).

## O que ficou de fora (de propósito)

1. **Renomeação canônica via prodam.db/SPCF** (`NE-…_CT-…`): risco de inventar ID;
   já existe fluxo dedicado (`reconciliacao-spcf-pipeline`); histórico de renomeação
   em massa destruindo naming canônico.
2. **Flag SEM_TEXTO por extração de conteúdo**: duplicaria `ocr-pdfs-prodam` e abriria
   27 mil PDFs. Caminho futuro: consultar `OCR_CONSOLIDADO.db` em vez de reextrair.
3. **Qualquer limpeza automática** do que o inventário encontra: só sinalização.

## Testes executados (sandbox Linux, lógica idêntica)

Pasta sintética com 17 arquivos válidos + lixo: 3 devedores (DETRAN, SES/SUSAM via
alias SUSAM **e** SES, SEDUC em pasta profunda), ambíguo, sem devedor, duplicata MD5,
quase-dup, 2× zero-bytes, acento, nome de 180+ chars, colisão de nome, node_modules,
`_archive`, symlink, desktop.ini, carta de cobrança, .msg. Sequência: dry-run →
`--aplicar` → `--aplicar` de novo (0 recópias, tudo `JA_EXISTE`, cache com hits) →
MD5 origem=destino → `--inventario` (4 quase-dup em 2 grupos) → `--auditar` limpa
(exit 0) → `--auditar` com 2 desvios plantados (exit 1, ambos detectados).
**Resultado: 25/25 verificações passando.**

## Como testar de novo no futuro (no Windows)

```powershell
# smoke do ambiente real (deve imprimir v2.0.0):
py -3.12 "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_SKILLS\organizador-arquivos-prodam\scripts\planejar_organizacao.py" --versao
# raio-X inofensivo de qualquer pasta (não cria nem altera nada na origem):
py -3.12 ...\planejar_organizacao.py --origem "C:\caminho\Pasta" --inventario
# ciclo completo numa pasta de teste descartável: dry-run → revisar CSV → --aplicar → --aplicar de novo (esperar 0 cópias)
```

## Arquivos e versões

- Fonte atualizada: `PRODAM_DOCS\_SKILLS\organizador-arquivos-prodam\` (script v2.0.0
  + SKILL.md + references + evals com 4 gatilhos novos).
- v1 preservada em `PRODAM_DOCS\_SKILLS\organizador-arquivos-prodam\_BACKUP_PRE_v2_20260609\`.
- **A cópia instalada no Claude é um cache separado**: para ativar a v2, instale o
  pacote `organizador-arquivos-prodam.skill` entregue na conversa (botão "Save skill")
  ou re-aponte a skill em Configurações → Capacidades.
