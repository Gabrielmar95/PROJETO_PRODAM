# SESSÃO 2026-06-09 (noite) → 2026-06-10 (madrugada) — Notion: hub PRODAM, organização do workspace e conexões Google

> Sessão de infraestrutura/produtividade (não jurídica). Nenhum dado do projeto local foi alterado — apenas leitura de `STATUS_DEVEDORES.md`, `CLAUDE.md`, `WORKFLOW_COBRANCA.md` e `profiles.json`. Use este arquivo para retomar o assunto "Notion" em sessão futura.

## 1. O que foi feito (entregáveis)

1. **Hub "Projeto PRODAM — Recuperação de Créditos" criado no Notion** (workspace "Espaço de Gabriel Mar", seção Particular):
   - Página principal com KPIs (R$ 83.668.078,44 exigível · R$ 125.245.390,64 atualizado · 69 devedores), alertas de prescrição, pipeline e obrigações contratuais. ID: `37b3dbf2-f380-815d-9a6f-ea316dc00e46`.
   - Database **"Devedores PRODAM"** com os 69 devedores (valor exigível/atualizado em formato BRL, categoria, força, fase, próximo passo, dias de prescrição, alerta). Database ID: `a987407a-fad1-457c-a55f-5776b4af8c40` · data source: `628bfbe3-8272-43a8-9096-869098f5e893`.
   - 3 views: 🔄 kanban por Próximo Passo · 🚨 Alertas de Prescrição (filtrada, 13 devedores) · 📊 kanban por Fase F0→F6.
   - 3 páginas de apoio: Workflow F0→F6 · Regras Jurídicas (13 regras + vedações + hierarquia de fontes) · Fontes de Dados e Conciliação.
   - Sub-página **📝 Notas de Trabalho** com as 2 notas reais resgatadas: "Prodam/DETRAN — Auditoria (Lacuna B1)" e "Sessão — Sincronizador Jurídico de Skills (Lote E06)" (ex-"Projeto (novo)", renomeada).
2. **Workspace Notion organizado**: lixo de template (database "Projetos" com 4 exemplos falsos + 3 notas de reunião vazias) movido para a página **🗄️ Arquivo** (nada excluído — reversível). "Página inicial" é página de sistema e não pôde ser movida (limitação da API).
3. **Sincronização agendada** (tarefa "sync-prodam-notion" no Claude/Cowork): diária ~08h, lê `STATUS_DEVEDORES.md` + `CLAUDE.md` e atualiza o Notion só quando a data dos dados mudar. Nunca exclui registros; alerta classificado por regra fixa (🔴 ≤30d · 🟡 ≤90d · 🛡️ marco · Sem data · OK).
4. **Conexões Notion × Google concluídas** (conta admin do Workspace `admin-gabriel@gabrielmar.adv.br`):
   - Google Drive: 2/2 tipos (Visualização de link + Conector de IA).
   - Gmail: 2/2 tipos (Conector de IA para busca + Ação de automação para envio de e-mails).
   - Google Calendar: Conector de IA instalado.
   - Confirmado na aba Configurações → Conexões → Instalados.

## 2. O que aprendemos (lições para reutilizar)

1. **`profiles.json` chega truncado pelo mount do sandbox Linux** (arquivo grande regravado recentemente) — `json.load` falha com `Unterminated string`. **Workaround validado**: ler/grepar pelo caminho Windows com as ferramentas de arquivo (Read/Grep), fora do mount. Foi assim que extraímos `sigla → categoria` dos 69 devedores (26 Gov Direta · 21 Gov Indireta · 22 Privadas — bateu com o CLAUDE.md).
2. **`STATUS_DEVEDORES.md` é a melhor fonte para espelhos externos** (Notion, dashboards): pequeno, completo, regenerado pelo `auto_update_claude_md.py` e com data de corte na linha 2 — serve de "detector de mudança" para a sync.
3. **Notion aceita formato monetário BRL no DSL de criação de database**: `NUMBER FORMAT 'real'`.
4. **Conectores de IA do Notion (Drive/Gmail/Calendar) são apps do Google Workspace Marketplace** que exigem **conta com privilégio de administrador da organização** para instalar. Conta Gmail pessoal não se qualifica (requer Workspace pago). Fluxo: Notion → Conexões → card → "Iniciar conexão" → instalar no Marketplace logado como admin → Notion detecta sozinho (o botão "Confirmar conexão" às vezes nem é necessário).
5. **Relógio do agendador (host Windows) pode divergir do sandbox (~1h)**. Ao agendar `fireAt`, conferir o "(in X hours)" que o agendador devolve e ajustar pelo relógio do host — foi preciso corrigir o lembrete de 2h.
6. **Páginas de sistema do Notion** ("Página inicial", notas de reunião nativas) não podem ser movidas via API ("System blocks cannot be moved") — mover em lote falha inteiro; mover um-a-um isola o item problemático.
7. **Divergência DETRAN reconfirmada**: `profiles.json` registra R$ 0,00 exigível, mas o valor canônico do sub-projeto é **R$ 28.196.572,22** (já documentado no diagnóstico de 09/06 tarde — exigível real do portfólio ≈ R$ 111,9M). Anotado na página "Fontes de Dados e Conciliação" do hub para reconciliar.

## 3. O que erramos / falhou (e como foi corrigido)

| # | Erro/Falha | Correção/Workaround |
|---|---|---|
| 1 | Ler `profiles.json` pelo mount do sandbox → `JSONDecodeError` (truncamento) | Grep/Read pelo caminho Windows (lição 2.1) |
| 2 | URL direta `notion.so/my-connections` → página não encontrada | Caminho certo: app Notion → menu do workspace → Configurações → Conexões |
| 3 | Lembrete "daqui 2 horas" agendado com 1h de erro (offset calculado pelo relógio do sandbox) | `update_scheduled_task` com fireAt recalculado pelo relógio do host (lição 2.5) |
| 4 | Clique em "Adicionar conta" no menu de contas Google não abriu o login | Navegar direto para `accounts.google.com/AddSession?continue=<url>` |
| 5 | Mover 5 itens de template em lote no Notion → falha total ("System blocks cannot be moved" por causa da "Página inicial") | Mover individualmente; "Página inicial" permanece (inofensiva) |
| 6 | Extensão Claude in Chrome desconectou em alguns momentos (transiente) | Retry após alguns segundos resolveu em todos os casos |
| 7 | 1ª tentativa de conexão do Drive ficou pendente e foi pulada pelo usuário; descobrimos depois que a autorização tinha sido concluída ("1 de 2 instalados") | Sempre reabrir o card e checar o contador "X de N tipos instalados" antes de repetir fluxo |

## 4. Pendências para a próxima sessão

1. **Conta `gabrielmardasilva@gmail.com`**: (a) vincular o Drive pessoal via embed — colar link do Drive numa página do Notion → "Conectar outra conta"; (b) adicionar a agenda pessoal no app **Notion Calendar** (Configurações → Adicionar conta Google). Conector de IA é inviável para ela (exige Workspace pago).
2. **Pré-aprovar a tarefa agendada** `sync-prodam-notion`: clicar "Run now" na seção Scheduled do Claude uma vez, para gravar as permissões do Notion e a sync diária não travar em prompts.
3. **Reconciliar DETRAN** no `profiles.json` (R$ 0,00 × valor canônico R$ 28,2M) — afeta o headline do portfólio em todos os espelhos.
4. **9 devedores sem data de prescrição registrada** (AADESAM · BRADESCO · CASA MILITAR · CGE · FJJA · FMPES · SEJEL · SETRAB · UGPI) — registrar para destravar o monitoramento por prazo no Notion.
5. Lembrete one-shot "lembrete-conexoes-notion-google" ficou obsoleto (conexões concluídas) — desativar/excluir na seção Scheduled se ainda estiver armado.

## 5. Referências rápidas

- Hub Notion: https://app.notion.com/p/37b3dbf2f380815d9a6fea316dc00e46
- Database Devedores: https://app.notion.com/p/a987407afad1457ca55f5776b4af8c40
- Página Arquivo (lixo de template): https://app.notion.com/p/37b3dbf2f38081afbd6bd1104d131ac8
- Tarefa agendada: `C:\Users\gabri\Desktop\CLAUDE COWORK\Scheduled\sync-prodam-notion\SKILL.md`
- Login Notion: `contato@gabrielmar.adv.br` · Conexões Google instaladas com `admin-gabriel@gabrielmar.adv.br`
