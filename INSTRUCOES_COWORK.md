# Instruções do Projeto — Recuperação de Créditos PRODAM (Contrato 002/2026)

> Texto para o campo de instruções do projeto no Cowork. As regras detalhadas vivem no `CLAUDE.md` (autoridade máxima); aqui ficam só o objeto, as fontes da verdade, a higiene de pastas e as travas de segurança.

## OBJETO
Recuperação de créditos da PRODAM (Processamento de Dados Amazonas S.A.) contra órgãos e entes do Estado do Amazonas e devedores privados.

**Frente atual: administrativa.** Priorize a cobrança extrajudicial — TRD, notificações, compensação administrativa, protesto, certidões. A via judicial (execução, monitória, habilitação de crédito) entra nos casos já maduros para isso ou quando a administrativa se esgota; antes de mudar de via, avise.

## FONTES DA VERDADE (leia antes de agir; não afirme o que não estiver nelas)
Consulte nesta ordem — o item de cima corrige o de baixo:

1. `CLAUDE.md` — regras, método e métricas do projeto (autoridade máxima; é auto-gerado).
2. `PRODAM_DOCS/profiles.json` — SSOT dos devedores (valores, força, prescrição, próximo passo).
3. `PRODAM_DOCS/REFERENCIA_JURIDICA/` — base jurídica (subpastas temáticas; comece pelo `INDEX.md`). Consulte ANTES de qualquer parecer. Jurisprudência: só a verificada em `11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md`.
4. `WORKFLOW_COBRANCA.md` — fluxo de cobrança F0→F6.
5. `PLAYBOOK_ORGAOS_V2.md` — tratamento por órgão.
6. `STATUS_DEVEDORES.md` — estágio e dados de cada devedor.
7. `prodam.db` — base SQLite. **Canônico**: `PRODAM_DOCS/_ANALISE/prodam.db`. O `prodam.db` da raiz é cópia derivada usada por `scripts/consultas.py`.
8. `PRODAM_DOCS/` e `OCR_PESQUISAVEL_CONSOLIDADO/` — documentos-fonte digitalizados (provas).
9. `knowledge-agents.md` e `HISTORICO_SESSOES.md` — contexto acumulado.

**Se essas fontes divergirem entre si, pare e pergunte — não escolha sozinho.** Divergências já conhecidas: a data de prescrição no `profiles.json` diverge do CSV; e o `LEIAME.md` (de 18/04) está desatualizado quanto à localização de algumas pastas. Na dúvida sobre qual fonte vale, confirme comigo.

## PASTAS — TRABALHE vs. IGNORE
**Trabalhe a partir de:** `dados/`, `PRODAM_DOCS/`, `DETALHAMENTO_FATURAS/`, `DOSSIES/`, `DOSSIES_MULTIFORMATO/`, `DOCUMENTOS_GERADOS/`, `relatorios/`, `scripts/`, `SPCF_EXTRACAO/`, `AUDITORIA_COMPLETUDE/`, `OCR_PESQUISAVEL_CONSOLIDADO/` e as pastas por órgão em MAIÚSCULAS (ex.: `DETRAN_*`).

**IGNORE como histórico/lixo** (não use como fonte, não edite):

- qualquer pasta iniciada por `_` — `_ARQUIVO_*`, `_BACKUPS`, `_BACKUP_*`, `_SESSAO`, `_legado`, `_QUESTOES_CRITICAS`, `_AUDITORIA_FISICA`, etc.;
- qualquer arquivo de **backup** — com `.bak`, `.backup`, `BAK` ou `BACKUP` no nome (ex.: `CLAUDE.md.bak.*`, `CLAUDE_BACKUP_*.md`, `profiles.json.bak.*`, `*.backup-manus`, `prodam_BAK_*.db`);
- arquivos **temporários ou de sessão** — `_tmp_*.py`, `_out_*.txt`, `_notificacao_texto_extraido.txt`, `.fuse_hidden*`, `.continue-here.md`.

Regra prática: o que não está na lista de "trabalhe" e tem cara de backup, tmp ou sessão é lixo — não trate como fonte nem edite.

## PROTEÇÃO DE DADOS (crítico)
- NUNCA apague, sobrescreva ou mova `prodam.db` (raiz ou `PRODAM_DOCS/_ANALISE/`), arquivos em `PRODAM_DOCS/`, em `OCR_PESQUISAVEL_CONSOLIDADO/` ou qualquer backup sem a minha confirmação explícita ("OK"). PDFs são prova — nunca apagar originais.
- Antes de rodar scripts que alterem o banco (`RECONCILIADOR.py`, `reconciliar_*.py`, `scripts/reconcil*.py`), explique exatamente o que vão mudar e espere meu "OK".
- Há um `.env` na raiz com segredos: nunca leia, exiba, copie nem inclua o conteúdo dele em arquivos, saídas ou commits.

## SAÍDAS
- Peças e documentos → `DOCUMENTOS_GERADOS/`.
- Relatórios → `relatorios/`.
- Dossiês → `DOSSIES/` (ou `DOSSIES_MULTIFORMATO/` quando houver versões em vários formatos).
- Mantenha nomenclatura consistente de devedores, valores e referências contratuais entre todos os arquivos gerados. Valores em `Decimal`, formato BRL `R$ 1.234,56`; CSV com separador `;` e `utf-8-sig` (BOM).

## IDIOMA, ESTILO E RIGOR
- Responda em português do Brasil, objetivo e sem preâmbulo. Comandos de terminal em bloco único para PowerShell no Windows (`py -3.12`, sem venv).
- Rigor jurídico: não invente lei, jurisprudência, súmula, prazo, índice ou valor. Sem fonte segura, diga isso e aponte o que preciso verificar. Sinalize prazos e riscos.

## ANTES DE REDIGIR
Confirme comigo os fatos essenciais que não estiverem claros nas fontes (partes, valores, datas, número de processo, foro) antes de produzir qualquer peça.
