---
name: memory-management
description: "Sistema de memória em duas camadas para o Projeto PRODAM — glossário jurídico, devedores, contratos e contexto do portfólio de recuperação de créditos."
user_invocable: false
---

# Gestão de Memória — Projeto PRODAM

Sistema de memória em duas camadas que permite ao Claude entender o vocabulário jurídico, siglas, nomes de devedores, órgãos e termos específicos do Projeto PRODAM (Contrato 002/2026) como um colega de escritório faria.

## Arquitetura de Duas Camadas

### Camada 1: CLAUDE.md (memória quente — ~80 linhas)

Carregado automaticamente em toda sessão. Contém o essencial para operar sem consulta adicional:

- **Top 12 devedores** por valor exigível (sigla, nome, valor, fase, prescrição, força)
- **Glossário rápido** (~30 termos mais usados)
- **Pessoas-chave** (Gabriel Mar, PRODAM, Brandão Ozores)
- **Fases do workflow** (F0-F9)
- **Índices de correção** (SELIC geral; IGPM para FUHAM; IGPM+1%+2% para DETRAN — sempre confirmar por contrato)
- **Alertas ativos** (prescrições iminentes, prazos vencidos)
- **Regras de ouro** (profiles.json é SSOT, nunca fabricar dados, etc.)

### Camada 2: memory/ (armazenamento profundo)

Consultado quando CLAUDE.md não resolve:

```
memory/
├── glossario.md              # Dicionário completo (~100 termos jurídicos)
├── devedores/
│   ├── seduc.md              # Perfil completo + histórico de ações
│   ├── ses-susam.md
│   └── ...                   # 1 arquivo por devedor (69 total)
├── projetos/
│   ├── pipeline-analise.md   # Status da pipeline de análise massiva
│   └── spcf-scraping.md      # Status do web scraping SPCF
├── contexto/
│   ├── contrato-002-2026.md  # Termos do contrato com PRODAM
│   └── ferramentas.md        # Scripts, skills, pipelines disponíveis
└── referencias/
    ├── legislacao.md          # Leis-chave
    └── jurisprudencia.md      # Precedentes verificados
```

## Fluxo de Consulta

1. **Usuário menciona termo/sigla** → Verificar CLAUDE.md (cobre 90%)
2. **Não encontrado** → Consultar `memory/glossario.md`
3. **Ainda não encontrado** → Perguntar ao usuário e salvar

## Regras de Promoção/Rebaixamento

- **Promover para CLAUDE.md:** termo ou devedor mencionado 3+ vezes em sessões diferentes
- **Rebaixar para memory/:** devedor concluído (F9), termo não usado há 30+ dias
- **Limite CLAUDE.md:** ~80 linhas. Se ultrapassar, rebaixar itens menos usados

## Regras Específicas PRODAM

1. **Nunca inventar dados.** Se não está em CLAUDE.md ou memory/, NÃO fabricar.
2. **profiles.json é SSOT.** Quando conflitar com memória, profiles.json prevalece.
3. **Valores em BRL:** Sempre R$ X.XXX,XX com Decimal, nunca float.
4. **Datas absolutas:** Converter "semana que vem" para data exata ao salvar.
5. **Procedência:** Anotar fonte (P1=documento, P2=parcial, P3=SPCF).
