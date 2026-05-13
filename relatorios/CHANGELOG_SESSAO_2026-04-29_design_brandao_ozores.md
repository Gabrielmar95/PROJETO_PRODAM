# Sessão 2026-04-29 — Design Brandão Ozores: Relatório Quinzenal 004/2026 + decisão institucional

**Operador:** Gabriel Mar (OAB/AM 15.697)
**Tema:** geração do REV01 do Relatório Quinzenal nº 004/2026 sob design Brandão Ozores (DOCX + PDF) + decisão institucional permanente sobre nota "Elaboração técnica" + consolidação da skill de design.
**Session ID:** ffa004b4-7208-4026-8bfc-db6e4c42e042

---

## 1. Ponto de partida

Sessão começou com pedido de skill-creator para registrar o relatório quinzenal mais atualizado como skill reutilizável. O fluxo foi redirecionado para:
1. Exportar a skill `design-brandao-ozores` para o Desktop (download)
2. Gerar versões DOCX + PDF do Relatório Quinzenal 004/2026 (REV01) aplicando o design Brandão Ozores, mas mantendo **literalmente** o conteúdo do REV01.docx fornecido pelo usuário
3. Tomar decisão institucional permanente: remover para sempre a nota "Elaboração técnica" do design Brandão Ozores

Estado anterior do design: skill `design-brandao-ozores` v1.0 já consolidava `tipografia-premium-brandao-ozores` + `design-relatorio-quinzenal-prodam` (migração ocorrida em sessão anterior, 29/04/2026).

---

## 2. Descobertas críticas

### 2.1 Divergência conteúdo × design no primeiro draft

Primeira tentativa de geração inseriu elementos não presentes no REV01 fonte:
- `caixa_sintese()` no topo (não existia no fonte)
- `assinatura_coautoria()` (REV01 fonte tem só Fábio + nota Gabriel)
- Item 4 com alíneas ponto-mediano em vez do formato `Label: Valor` original

Correção: reescrita do script para reproduzir literalmente os 63 parágrafos do REV01, com formato `Label: Valor` (label em bold) e assinatura solo Fábio.

### 2.2 Decisão institucional — proibição permanente "Elaboração técnica"

Usuário determinou: nota "Elaboração técnica: [nome]" subordinada à assinatura **NUNCA** mais aparece em documentos do design Brandão Ozores. Razão: cria hierarquia visual implícita que conflita com a paridade institucional do escritório. Decisão de assinatura é binária:
- `assinatura_fabio()` — solo Fábio
- `assinatura_gabriel()` — solo Gabriel
- `assinatura_coautoria()` — Fábio + Gabriel cossignatários

Quem só auxilia não consta. Auxiliar = não aparece.

### 2.3 Confirmação de unicidade da skill de design

Verificação confirmou: skill `design-relatorio-quinzenal-prodam` **já não existe** como skill ativa no Claude Code. Pasta `~/.claude/skills/design-relatorio-quinzenal-prodam/` ausente; lista de skills disponíveis tem apenas `design-brandao-ozores`. Cópias residuais (5 locais) sobrevivem em `AppData/`, `BACKUP_SEGURANCA_20260418/`, `Desktop/PROJETO_PRODAM/...SKILLS_ORGANIZADAS_v2/` — todas inertes para o catálogo do Claude Code.

### 2.4 REV01 preservado intacto após geração de REV02

Hash SHA-256 do REV01 antes e depois da geração do REV02: `3bf2057f953232f5cb7c874cf41cdd40040a4dd5ce07388dcf2641a6eaa7d6f1` — idêntico, validando que o pipeline unpack→regex→repack não tocou no fonte.

---

## 3. Ações tomadas

### 3.1 Script `gerar_relatorio_004.py`

Local: `C:\Users\gabri\work_rev_design\gerar_relatorio_004.py` (~30 KB)

Pipeline:
1. Hash do template antes da execução
2. `unpack` do `Ppael_timbrado_brandao_ozores.docx` via `scripts/office/unpack.py`
3. Limpeza de `settings.xml.rels` + remoção de `<w:attachedTemplate/>`
4. Geração do XML do corpo com helpers de `design-brandao-ozores/scripts/gerador.py`:
   - `titulo()`, `separador_dourado()`, `secao(num, text)`, `subsecao(num, text)`, `corpo(content)`
   - Helpers locais: `linha_centralizada(texto, italic, size)`, `linha_resumo(label, valor)`, `alinea_romana(label, texto)`
   - `_fecho()` + `_bloco_signatario(nome, oab, cargo)` + `_escritorio_dourado()` (assinatura solo Fábio)
   - `footer_paginacao()` para footer2.xml
5. Substituição de `<w:body>` no document.xml
6. Repack via `pack.py` da skill `docx-official` (`subprocess`)
7. Hash do output

### 3.2 Geração do REV02 (REV01 sem "Elaboração técnica")

Pipeline alternativo, partindo do REV01 fornecido pelo usuário:
1. Hash do REV01 antes (`3bf2057f...`)
2. `unpack` do REV01 para diretório temporário
3. Regex para identificar e remover o parágrafo P63 contendo "Elaboração técnica: Gabriel Mar — OAB/AM nº 15.697"
4. Repack via `pack.py`
5. Hash do REV01 depois (idêntico ao antes — fonte preservado)
6. Hash do REV02 (`20399de8...`)

Resultado: 1 parágrafo removido (~347 bytes a menos no document.xml, ~610 bytes a menos no DOCX zipado).

### 3.3 Atualização da skill `design-brandao-ozores`

Adição na seção "Lista negativa (PROIBIDO no design)" do `SKILL.md`:

> Notas de "Elaboração técnica" subordinadas após a assinatura. Quem participa do documento ou cossigna formalmente (via `assinatura_coautoria()`) ou não aparece. Não existe figura de "redator técnico" ou "elaboração técnica" subordinada ao signatário principal. Decisão institucional: cossignatário cossigna; quem só auxilia não consta.

### 3.4 Memória persistente da decisão

Criação de memória feedback permanente em `~/.claude/projects/C--Users-gabri/memory/design_brandao_ozores_proibicoes.md` com:
- Rule + Why (paridade institucional, decisão 29/04/2026)
- How to apply (3 sub-regras: não criar `nota_elaboracao()`, escolha binária de assinatura, REV/FINAL externo deve ter linha removida na regeração)

Indexada em `MEMORY.md`.

### 3.5 Conversão DOCX → PDF

Conversão via `docx2pdf` 0.1.8 (Word COM) para os 2 outputs principais.

---

## 4. Arquivos gerados

### Outputs principais (Desktop)
| Arquivo | Bytes | SHA-256 |
|---------|-------|---------|
| `Relatorio_Quinzenal_004_2026_BRANDAO_OZORES.docx` | 55.342 | `5663200c240d8df39ade10ced3895bf90dc0d8d1bebf2b27db5dc9aa0610451e` |
| `Relatorio_Quinzenal_004_2026_BRANDAO_OZORES.pdf` | 161.871 | `3c5d54b15a5031dbb1cfe955b3014f90d7c0601ab866929b5c206f8a5f9ca539` |
| `Relatorio_Quinzenal_004_2026_REV02.docx` | 43.555 | `20399de88a8e40b2d53db3f48e92ae134da2b40a124cf407ecbe63b6a9a74928` |

### Export da skill (Desktop)
- `design-brandao-ozores_export_20260429/` — 11 arquivos, 704 KB total
  - `SKILL.md`, `TODO_pos_migracao.md`, `MANIFEST_SHA256.txt`
  - `template/Ppael_timbrado_brandao_ozores.docx`
  - `scripts/{gerador.py, gerar_demo.py, render_demo.py, test_smoke.py}`
  - `exemplos/Notificacao_DETRAN_002_2026_DEMO.{docx, pdf, jpg}`

### Scripts (work_rev_design/)
- `gerar_relatorio_004.py` — script de geração validado, ~30 KB

### Skill modificada
- `~/.claude/skills/design-brandao-ozores/SKILL.md` — adição na Lista negativa

### Memória persistente
- `~/.claude/projects/C--Users-gabri/memory/design_brandao_ozores_proibicoes.md` (novo)
- `~/.claude/projects/C--Users-gabri/memory/MEMORY.md` (linha de índice adicionada)

---

## 5. Pendências para próxima sessão

1. **Limpeza de cópias residuais (opcional)** — decidir entre 3 cenários:
   - **(A)** Não fazer nada — estado já correto, só `design-brandao-ozores` ativa
   - **(B)** Apagar só `Desktop/PROJETO_PRODAM/PRODAM_DOCS/_WORKFLOW_IMPORTADO/SKILLS NOVA/SKILLS_ORGANIZADAS_v2/design-relatorio-quinzenal-prodam/`
   - **(C)** Limpar todas as 5 cópias residuais (não recomendado — mexe em backup e cache do Claude Desktop)

2. **Skill nova de relatório quinzenal** — pendente. Pedido original: "crie uma skill de relatório quinzenal" para encapsular o pipeline validado em `gerar_relatorio_004.py`. Há 2 skills antigas que podem ser consolidadas:
   - `relatorio-quinzenal-garamond-prodam` (v1.0, validada no Relatório 003/2026)
   - `gerador-relatorio-quinzenal` (v1.0, GAP-14 P1)
   - Decidir: substituir as antigas, criar paralela, ou consolidar tudo em `relatorio-quinzenal-prodam-v2`?
   - Invocação correta: `Skill: skill-creator:skill-creator` (memória `feedback_skill_criacao.md` já registra delegação obrigatória).

3. **Reaplicação do design Brandão Ozores em outros documentos do projeto** — agora que o design está estabilizado e a proibição de "Elaboração técnica" está formalizada, identificar peças anteriores que precisam ser regeradas.

---

## 6. Urgências de prescrição (recalculadas em 29/04/2026)

| Devedor | Prescrição | Dias restantes (de hoje) | Valor exigível |
|---------|-----------|--------------------------|----------------|
| 🔴 SES/SUSAM | 2026-05-13 | **14 dias** | R$ 14.748.048,96 |

(SES/SUSAM continua única urgência <90 dias do portfólio, conforme CLAUDE.md.)

---

## 7. Observações ao Sistema Multi-Agente

- O design Brandão Ozores agora tem **única skill ativa** (`design-brandao-ozores`). Qualquer agente gerador de documento jurídico do escritório (`agente-gerador-notificacao`, `agente-gerador-trd`, `agente-gerador-oficios`, `agente-gerador-memorial`, `agente-gerador-dossie`) deve usar essa skill como dependência de design.
- A regra "sem Elaboração técnica" é vinculante para todos esses agentes. Validar pós-geração via `validacao-pos-geracao` que NÃO há linha "Elaboração técnica:" remanescente.
- O script `gerar_relatorio_004.py` é o exemplo de referência canônico do pipeline `unpack → edit → pack` para o design Brandão Ozores.
