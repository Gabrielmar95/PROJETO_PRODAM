# Registro de Sessão — 2026-06-09
## Skill "organizador-arquivos-prodam" (File Organizer) + organização do acervo

## 1. Skill criada e instalada
- **Local:** `PRODAM_DOCS/_SKILLS/organizador-arquivos-prodam/`
  - `SKILL.md` · `scripts/planejar_organizacao.py` · `references/convencoes_prodam.md` · `evals/`
- **O que faz:** organiza um acervo POR DEVEDOR (cruzando nomes com `profiles.json`),
  detecta DUPLICATAS exatas (hash MD5) e arquivos fora do padrão, e RENOMEIA no
  padrão PRODAM — em modo **CÓPIA, não-destrutivo**.
- **Salvaguardas:** nunca apaga nem move originais (PDFs = provas); dry-run é o
  padrão (gera só o manifesto); só copia com `--aplicar`, conferindo MD5; gera
  manifesto auditável em JSON+CSV+XLSX. Não inventa nº de contrato/NE/NF.
- **Como usar (PowerShell):**
  ```
  py -3.12 PRODAM_DOCS\_SKILLS\organizador-arquivos-prodam\scripts\planejar_organizacao.py --origem "C:\pasta\baguncada" --destino "C:\pasta\ORGANIZADO"
  # revisar o manifesto, depois:
  py -3.12 ...\planejar_organizacao.py --origem "..." --destino "..." --aplicar
  ```
- **Reuso:** importa `prodam_utils` (`load_profiles`, `norm`, `match_flex`) com
  fallback stdlib; tem caminho absoluto de fallback para o projeto, então acha o
  `profiles.json` de qualquer lugar.
- **Registrar no índice:** rodar a sincronização (`py -3.12 scripts\auto_update_claude_md.py`
  ou `/sincronizar-prodam`) para a skill entrar no `INDEX.md` (não editar à mão).

## 2. Otimização da descrição (disparo)
- Conjunto de avaliação salvo em
  `PRODAM_DOCS/_SKILLS/organizador-arquivos-prodam/evals/trigger_eval_set.json`
  (10 queries que devem disparar + 10 near-misses que não devem).
- A descrição foi otimizada por análise (fechando disparos indevidos: gerar peças,
  renomear variável de código, consultar dados, "duplicata" jurídica, backup).
- O **loop medido** (mede taxa de disparo real) não rodou no ambiente Cowork
  porque o CLI `claude` não estava logado. Para rodar localmente, no Claude Code
  logado, a partir da pasta da skill-creator:
  ```
  py -3.12 -m scripts.run_loop --eval-set "...\trigger_eval_set.json" --skill-path "...\organizador-arquivos-prodam" --model claude-opus-4-8 --max-iterations 5 --verbose
  ```

## 3. Organização executada — "Arquivos Principais Projeto PRODAM"
- Resultado na própria pasta, em **`_ORGANIZADO/`** (originais intactos: 19 arquivos).
- **16 copiados** (MD5 conferido 16/16, 0 falhas) + **3 duplicatas** puladas.
- Estrutura: `DETRAN/07_NOTIFICACOES/` (2) + `_INSTITUCIONAL_CONTRATO-002-2026/`
  (14, por tipo). Manifesto em `_ORGANIZADO/_MANIFESTO/`.

### Decisões de revisão (detalhe em `_ORGANIZADO/_DECISOES_REVISAO.md`)
- **Reclassificação:** dos 18 "não identificados", só 1 era de devedor — a
  **Notificação Extrajudicial 001/2026 ao DETRAN** → movida para `DETRAN/`. Os 17
  demais são institucionais do Contrato 002/2026 (BOA×PRODAM) → balde renomeado
  para `_INSTITUCIONAL_CONTRATO-002-2026` (não eram "não identificados").
- **Duplicatas (conteúdo conferido nos PDFs):**
  - "Canal Comunicação Oficial.pdf" é, na verdade, o **Ofício PRESI/045/2026 da
    PRODAM** (resposta ao Ofício 001/2026) → renomeado e movido para `06_OFICIOS`.
  - Par "PROCURAÇÃO PROTOCOLO VIRTUAL"/"COBRANÇA DETREAN" = a notificação ao DETRAN.
  - `Relatorio_Quinzenal_003_2026ass (1).pdf` = cópia de download do `003ass`.
  - Versões assinada x não assinada NÃO são duplicatas (ambas preservadas).

## 4. Pendências / próximos passos
- Validar a pasta `_ORGANIZADO` antes de descartar, nos originais, as cópias de
  nome enganoso (Ofício PRESI/045 e a notificação DETRAN) e a cópia "(1)".
- Rodar o loop medido de descrição localmente (item 2), se desejado.
- Rodar a skill em outros acervos (DETRAN_AUDITORIA_COMPLETA, Downloads, etc.).

## Observações técnicas
- Neste ambiente (Cowork) o `rm` é bloqueado pelo mount; por isso podem restar
  subpastas vazias inofensivas e um `_artefato_teste_ignorar.txt` no `_MANIFESTO`.
- Ajuste relevante feito no script: "EXECUÇÃO" isolado deixou de classificar como
  PETIÇÃO (evita falso-positivo em "regime/blindagem de execução").
