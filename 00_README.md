# Kit de Setup — Projeto Cowork "PRODAM — Recuperação de Créditos"

_Gerado em 08/06/2026. Base de dados de referência: snapshot do projeto de 30/05/2026 (última execução de `scripts/auto_update_claude_md.py`)._

Esta pasta reúne os arquivos para montar (ou reconfigurar) o projeto **PRODAM — Recuperação de Créditos** dentro do Cowork. Foi escrita para apontar para esta mesma pasta de trabalho (`PROJETO_PRODAM`), que continua sendo a fonte real dos dados.

## O que tem aqui

| Arquivo | Para que serve | Onde usar no Cowork |
|---------|----------------|---------------------|
| `00_README.md` | Este guia — explica o kit e como instalar | Referência sua; opcional subir |
| `01_CONTEXTO.md` | Contexto completo do caso (partes, portfólio, status, fontes, pendências) | Subir como **conhecimento** do projeto |
| `02_INSTRUCOES.md` | Como o assistente deve se comportar (rigor, confidencialidade, fontes, saídas) | Colar no **campo de instruções** do projeto |
| `03_GLOSSARIO.md` | Siglas dos órgãos, termos (NE, NL, TRD, RPV...) e classificações | Subir como **conhecimento** |
| `04_GUIA_RAPIDO_JURIDICO.md` | Síntese das regras jurídicas já consolidadas, com dispositivo legal | Subir como **conhecimento** |

## Como montar o projeto no Cowork

1. **Crie um projeto novo** no Cowork e selecione esta pasta (`PROJETO_PRODAM`) como pasta de trabalho. Assim o assistente lê os dados reais (`profiles.json`, `prodam.db`, `REFERENCIA_JURIDICA/`) direto da origem.
2. **Instruções do projeto**: copie o conteúdo de `02_INSTRUCOES.md` para o campo de instruções. É o texto curto e operacional — as regras detalhadas e os dados vivem nos arquivos de conhecimento e nas fontes da pasta.
3. **Conhecimento**: suba `01_CONTEXTO.md`, `03_GLOSSARIO.md` e `04_GUIA_RAPIDO_JURIDICO.md`. São estáveis e dão ao assistente o panorama sem precisar varrer a pasta inteira a cada conversa.
4. **Não suba** bancos (`*.db`), PDFs de prova nem o `.env`. Eles ficam na pasta e são lidos sob demanda; não devem virar anexo de projeto.

## Hierarquia: o que manda sobre o quê

Se houver conflito, vale sempre a fonte mais "de baixo" (mais próxima do dado bruto):

1. `02_INSTRUCOES.md` — comportamento do assistente.
2. `PRODAM_DOCS/profiles.json` — **SSOT** dos devedores (valores, força, prescrição, próximo passo).
3. `PRODAM_DOCS/REFERENCIA_JURIDICA/` — base jurídica; jurisprudência só a verificada em `11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md`.
4. `prodam.db` — base SQLite (canônico: `PRODAM_DOCS/_ANALISE/prodam.db`).
5. `01_CONTEXTO.md`, `03_GLOSSARIO.md`, `04_GUIA_RAPIDO_JURIDICO.md` — panorama estável (este kit).
6. `CLAUDE.md` (raiz) — regras e métricas auto-geradas do projeto, úteis como referência de origem.

Os números deste kit (70 devedores, R$ 83,7M exigíveis, etc.) são um **retrato de 30/05/2026**. Para qualquer ação concreta — protocolar, atualizar valor, conferir prazo — o dado vale é o de `profiles.json` no momento, não o número fixado aqui.

## Como manter atualizado

- O portfólio muda via `profiles.json` (SSOT) e é resumido pelos scripts do projeto (`scripts/auto_update_claude_md.py` regenera `CLAUDE.md`, `STATUS_DEVEDORES.md`, etc.).
- Este kit é estável: revise `01_CONTEXTO.md` quando o portfólio mudar de forma relevante (novos devedores, mudança de fase de prioritários, fechamento de pendências críticas) e `04_GUIA_RAPIDO_JURIDICO.md` quando houver alteração de norma, índice ou precedente.
- Datas de prescrição **não** devem ser lidas deste kit como se fossem de hoje: são contagens do snapshot. Recalcule sempre na fonte.

## Confidencialidade

Estes arquivos contêm dados reais do cliente (nomes de órgãos, valores, prazos). Trate como sigiloso (sigilo profissional + LGPD): não suba para serviços fora do seu controle, não cole em exemplos públicos e não exponha o `.env`. Se um dia precisar de uma versão sem dados sensíveis (para compartilhar a metodologia), peça que eu gero uma cópia anonimizada.
