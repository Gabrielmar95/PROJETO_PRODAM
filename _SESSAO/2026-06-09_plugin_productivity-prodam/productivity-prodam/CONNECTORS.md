# Conectores Recomendados

O plugin funciona sem conectores (lê `profiles.json` e arquivos locais do projeto), mas dois conectores ampliam o `/update --comprehensive` e o `/alerta-prazos`.

## Gmail (conectado)
Usado para:
- Detectar respostas de devedores a notificações (move tarefas AGUARDANDO → EM ANDAMENTO)
- Capturar instruções da PRODAM / Brandão Ozores
- Confirmar envio/recebimento de notificações (AR, protocolo)

Skills que usam: `update --comprehensive`, `registro-acao-devedor`.

## Google Calendar (conectado)
Usado para:
- Criar eventos para prazos de prescrição (<90 dias) e prazos processuais
- Transformar audiências e reuniões (PRODAM, PGE) em tarefas de preparação
- Lembrar a entrega do relatório quinzenal

Skills que usam: `alerta-prazos`, `update --comprehensive`.

## Google Drive (opcional)
Usado para: armazenar dossiês, notificações assinadas e petições protocoladas.

> Gmail e Google Calendar são gerenciados pelo app via OAuth, por isso não têm URL fixa em `.mcp.json`. As categorias recomendadas (`email`, `calendar`, `documents`) ficam declaradas em `.mcp.json` para que a instalação ofereça a conexão.
