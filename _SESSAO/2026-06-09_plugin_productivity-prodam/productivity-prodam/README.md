# Productivity PRODAM

Plugin de produtividade customizado para o Projeto PRODAM (Contrato 002/2026) — recuperação de créditos contra 69 devedores.

## Skills

### Originais (customizadas)
- **start** — Inicializa o sistema a partir de profiles.json
- **update** — Sincroniza tarefas e memória; no modo `--comprehensive` usa Gmail e Calendar
- **task-management** — Gestão do TASKS.md por devedor e fase
- **memory-management** — Memória em duas camadas (CLAUDE.md + memory/)

### Novas
- **painel-devedores** — Visão rápida do portfólio com alertas de urgência
- **alerta-prazos** — Monitora prescrições, respostas e prazos processuais; pode lançar eventos no Calendar
- **registro-acao-devedor** — Registra cada ação por devedor com histórico rastreável

## Conectores
- **Gmail** (conectado) — respostas de devedores, instruções da PRODAM, confirmação de notificações
- **Google Calendar** (conectado) — prazos de prescrição, audiências e reuniões viram eventos
- **Google Drive** (opcional) — dossiês, notificações assinadas, petições

Detalhes em `CONNECTORS.md`.

## Uso
1. Instale o plugin
2. Execute `/start` para inicializar a partir de profiles.json
3. Use `/painel-devedores` para ver o estado do portfólio
4. Use `/alerta-prazos` para verificar prazos críticos
5. Use `/registro-acao-devedor SES notificação enviada` para registrar ações
6. Execute `/update` (ou `/update --comprehensive`) periodicamente para sincronizar
