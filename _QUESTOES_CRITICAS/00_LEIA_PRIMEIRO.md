# Questões Críticas — Pacote de Resolução

_Gerado em 2026-04-22 — Projeto PRODAM (Contrato 002/2026)_

## O que este pacote faz

Diagnóstico e scripts prontos para resolver as **duas questões críticas** identificadas
no diagnóstico da pasta mãe (`DIAGNOSTICO_PASTA_MAE.docx`):

1. **Divergência SSOT × Pastas** — `profiles.json` não bate com `PRODAM_DOCS/*_CONSOLIDADO`
2. **Drift entre scripts duplicados** — mesmo script existe em múltiplos locais

> ⚠️ **Nada foi executado.** Os arquivos `.ps1` são scripts prontos que **pedem
> sua confirmação antes de cada ação**. Você decide se e quando rodar.

## Resumo em uma linha (TL;DR)

| Problema | Impacto | Divergências | Script de resolução |
|----------|---------|--------------|---------------------|
| SSOT × Pastas | Dados invisíveis para scripts automatizados | **57** | `executar_reconciliacao.ps1` |
| Drift de scripts | Correções não se propagam | **5 grupos** (4 críticos) | `consolidar_scripts.ps1` |

## Arquivos deste pacote

```
_QUESTOES_CRITICAS/
├── 00_LEIA_PRIMEIRO.md              ← este arquivo
├── 01_RECONCILIACAO_SSOT.md          ← diagnóstico detalhado (SSOT × pastas)
├── 02_DRIFT_SCRIPTS.md               ← diagnóstico detalhado (drift)
├── reconciliacao_ssot.json           ← dados brutos para auditoria
├── reconciliacao_ssot.csv            ← planilha revisável
├── drift_scripts.json                ← dados brutos para auditoria
├── drift_scripts.csv                 ← planilha revisável
├── reconciliar_ssot.py               ← script Python que gerou a análise (reproduzível)
├── analisar_drift_scripts.py         ← idem (drift)
├── executar_reconciliacao.ps1        ← PowerShell pronto p/ resolver SSOT
└── consolidar_scripts.ps1            ← PowerShell pronto p/ resolver drift
```

## Questão 1 — Divergência SSOT × Pastas (a mais urgente)

### Achado

O `profiles.json` (a fonte autoritativa) tem **70 siglas**.
As pastas `_CONSOLIDADO` são **78** (mais 82 `_DOSSIE`).

Isso gerou **57 divergências**, divididas em 4 causas raiz:

| Causa | Quantidade | Gravidade | Exemplo |
|-------|-----------|-----------|---------|
| **A) Nome composto dividido** | 7 | 🔴 ALTA | SSOT diz `SES/SUSAM`, existe pasta só `SES` |
| **C) SSOT sem pasta** | 12 | 🔴 ALTA | Sigla `AADESAM` no profiles.json, sem pasta |
| **D) Pasta órfã (CONSOLIDADO)** | 18 | 🔴 ALTA | Pasta `DESCONHECIDO_CONSOLIDADO` sem sigla no SSOT |
| **D) Pasta órfã (DOSSIE)** | 20 | 🟡 MÉDIA | Pasta `MASTER_DOSSIE` sem sigla correspondente |

### Por que é crítico

Quando você roda `orgao_pipeline_completa.py --orgao SES`, o script lê o SSOT e depois
procura a pasta. Se o SSOT tem `SES/SUSAM` e a pasta é `SES_CONSOLIDADO`, o match falha
silenciosamente — você acha que processou o órgão, mas o script nem abriu os arquivos.

### Como resolver (leia antes de executar)

Abra `01_RECONCILIACAO_SSOT.md` e revise a tabela caso a caso. Para cada linha,
decida entre 5 ações: **CONSOLIDAR**, **RENOMEAR**, **ARQUIVAR**, **ADICIONAR_SSOT**, **REMOVER_SSOT**.

Depois execute no PowerShell:

```powershell
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"
powershell -ExecutionPolicy Bypass -File "_QUESTOES_CRITICAS\executar_reconciliacao.ps1"
```

Ele vai:
1. Criar backup do estado atual em `_BACKUP_RECONCILIACAO_<timestamp>/`.
2. Para cada **composite split** (causa A): mostrar as pastas afetadas e pedir confirmação para renomear.
3. Para cada **SSOT sem pasta** (causa C): perguntar se cria a estrutura vazia com 9 subpastas.
4. Para cada **pasta órfã** (causa D): perguntar se move para `_ARQUIVO_ORFA/`.

Cada ação individual pede `[s/N]`. Se você digitar `N` ou Enter, ele pula.

## Questão 2 — Drift de scripts duplicados

### Achado

De **362 scripts** `.py` analisados (excluindo `_legado`, `_archive`), encontrei **5 grupos** com nome duplicado, dos quais **4 estão listados no `CLAUDE.md` como canônicos**:

| Script | Status | Cópias | Decisão |
|--------|--------|--------|---------|
| `auto_update_claude_md.py` | ✅ IDÊNTICAS | 3 | Deletar 2 cópias |
| `prodam_utils.py` | ✅ IDÊNTICAS | 2 | Deletar 1 cópia |
| `consultas.py` | ⚠️ DRIFT_LEVE | 2 | Arquivar versão antiga (só diferença de path) |
| `orgao_pipeline_completa.py` | ⚠️ DRIFT_LEVE | 2 | Arquivar versão antiga (só diferença de path) |

### Diferença real

Investiguei `consultas.py` e `orgao_pipeline_completa.py` com `diff`. A diferença é
**apenas no caminho relativo** — a versão em `scripts/` foi ajustada para o subdiretório.
Não há lógica divergente.

Mas manter duas cópias significa que se você corrigir uma consulta, precisa lembrar
de corrigir a outra. Alto risco de bug silencioso.

### Como resolver

```powershell
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"
powershell -ExecutionPolicy Bypass -File "_QUESTOES_CRITICAS\consolidar_scripts.ps1"
```

Para cada grupo:
- **IDÊNTICAS**: pergunta se pode deletar as cópias (mantém só a mais recente, que é a de `scripts/`).
- **DRIFT_LEVE**: pergunta se pode arquivar as antigas em `_ARQUIVO_DRIFT/` (preserva o arquivo com slug do caminho original).

## Ordem recomendada

1. Abrir `01_RECONCILIACAO_SSOT.md` em VS Code, ler a seção "Interpretação".
2. Abrir `reconciliacao_ssot.csv` em Excel e fazer anotações.
3. Executar `executar_reconciliacao.ps1` (com confirmações).
4. Rodar `py -3.12 sincronizar_prodam.py` para regerar o SSOT.
5. Depois repetir passos 1–3 para o drift (`02_DRIFT_SCRIPTS.md` + `consolidar_scripts.ps1`).
6. Ao final: `py -3.12 auto_update_claude_md.py` para atualizar o `CLAUDE.md`.

## Se algo der errado

Todos os `.ps1` são **não destrutivos** por padrão:
- Pastas órfãs vão para `_ARQUIVO_ORFA/` (não deletadas).
- Scripts com drift vão para `_ARQUIVO_DRIFT/` (não deletados).
- Só scripts **idênticos** são deletados (e você pode sempre recuperá-los do Git / OneDrive).

Se quiser desfazer algo:

```powershell
# Reverter pasta do _ARQUIVO_ORFA
Move-Item "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_ARQUIVO_ORFA\<nome>" `
          "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\<nome>"
```

## Perguntas frequentes

**— Posso rodar só a parte A (composite split) e deixar o resto para depois?**
Sim. O script é modular: cada pergunta é independente. Basta responder `N` para as que quer pular.

**— E se eu acidentalmente deletar algo importante?**
Os `IDENTICOS` são realmente idênticos (md5 igual). A cópia que sobra tem exatamente os mesmos bytes — nada é perdido.

**— Preciso rodar `sincronizar_prodam.py` entre as etapas?**
Não obrigatório, mas recomendado. Ele reconstrói o SSOT após cada rodada grande de mudanças de pasta.
