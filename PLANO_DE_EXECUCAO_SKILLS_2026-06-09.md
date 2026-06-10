# PLANO DE EXECUÇÃO — Consolidação e limpeza de skills
**Data:** 09/06/2026 · Complementa `AUDITORIA_SKILLS_2026-06-09.md`.
**Estado:** nada executado. Cada item abaixo só acontece com seu **"OK"** explícito.

---

## 0. Ponto técnico que define o "como" (leia primeiro)

A pasta onde o assistente enxerga as 106 skills é um **cache somente-leitura** do app. Editar/remover ali **não** altera de forma confiável a skill que você realmente usa (e some na próxima sincronização). Logo, a parte de **consolidar/aposentar skills ativas não pode ser feita por mim diretamente** — ela é aplicada por você no gerenciador de skills.

### Como descobrir de onde vêm suas skills (3 passos)
1. No app, abra **Configurações → Capacidades (Skills)**.
2. Veja se as skills jurídicas aparecem **avulsas** ou dentro de um **plugin** (há sinais de um pacote seu chamado `antigravity-prodam` em `PRODAM_DOCS\_SKILLS\antigravity-prodam.plugin`).
3. Me diga o que aparece. Aí eu adapto os passos exatos (remover no painel × reempacotar o plugin × instalar arquivo novo).

### Via segura enquanto isso (a que vou seguir)
Para cada **consolidação**, eu **gero o `SKILL.md` final já mesclado** (arquivo novo, numa pasta de proposta), você revisa o conteúdo e instala pela sua via; depois **desativa** a skill antiga. Para cada **aposentadoria**, é só desativar no painel. **Nenhum original é apagado** — a skill antiga fica arquivada por 30 dias antes de qualquer remoção definitiva.

> **Regra de rollback padrão (todos os itens):** a skill substituída é **desativada/arquivada, não apagada**. Se algo faltar, reativa-se em 1 minuto. Remoção definitiva só após 30 dias e com seu OK.

---

## 1. Consolidações (12) — aprovar item a item

Marque `[x]` no que aprovar. Eu só gero o arquivo mesclado dos itens aprovados.

### Bloco rápido (duplicatas técnicas, sem risco jurídico) — recomendo começar por aqui

- [ ] **C9 · `brainstorming` → plugin `superpowers:brainstorming`**
  Duplicata exata. Ação: desativar a standalone; usar a do plugin. Sem geração de arquivo.
- [ ] **C10 · `writing-plans` → plugin `superpowers:writing-plans`**
  Duplicata exata. Ação: desativar a standalone.
- [ ] **C11 · `create-viz` → `data-visualization`**
  Mesma função (gráficos Python). `data-visualization` é mais completa. Ajuste de gatilho: ela passa a responder a "viz/gráfico/visualização".
- [ ] **C12 · `write-query` → `sql-queries`**
  Mesma função (SQL). `sql-queries` é mais completa. Gatilho "query/SQL" concentrado nela.
- [ ] **C6 · `criar-skills` → `skill-creator`**
  `skill-creator` tem scripts + avaliação. `criar-skills` é a versão PT enxuta — vira atalho/gatilho dentro dela.
- [ ] **C7 · `writing-skills` → `skill-creator`**
  Também duplica o plugin `superpowers:writing-skills`. Consolidar numa única fonte (`skill-creator`).

### Bloco Engeco

- [ ] **C8 · `gerar-minuta-nda-engeco` → `engeco-nda-builder`**
  Ambas geram a minuta. `engeco-nda-builder` é o orquestrador (minuta + 9 anexos). Absorve o gerador docx da outra. Gatilho "gera o NDA / minuta" concentrado nela.

### Bloco juridicamente sensível (exige sua confirmação de base + revisão do conteúdo mesclado)

- [ ] **C1 · `atualizacao-monetaria-sob-demanda` → `atualizacao-monetaria-creditos`**
  *Motivo forte:* manter duas lógicas de cálculo = risco de valores divergentes na mesma cobrança. A base (em escala) absorve o **modo sob-demanda + memorial BCB (SELIC série 4390)**. **Ação extra:** adicionar o bloco jurídico à base (hoje falta). **Confirmar:** base = `...-creditos`.
- [ ] **C2 · `montagem-dossie-devedor-detalhado` → `montagem-dossie-comprobatorio`**
  Base = `comprobatorio` (7 tipos de peça + cadeia 5 elos + P1–P3). Absorve o **gerador multi-formato (docx/xlsx/json/md)** e as 11 seções da outra. **Confirmar a base** (a "detalhado" é maior em linhas; a "comprobatorio" é a integrada).
- [ ] **C3 · `workflow-pos-analise-devedor` → `pipeline-devedor-completo`**
  Mesmas 7 etapas. Base = `pipeline-devedor-completo` (integra 12+ skills). Reavaliar junto `workflow-orchestrator` (provável absorção).
- [ ] **C5 · `validacao-pos-geracao` → `auditoria-documentos-juridicos`**
  `validacao-pos-geracao` (63 linhas, valida vs profiles.json) é subconjunto do QA pré-envio. `guardrails-anti-alucinacao` **fica separada** (fact-check pré-geração) — só delimitamos a fronteira na description.
- [ ] **C4 · `tipografia-juridica-gabriel` → `tipografia-juridica`**
  Mesma identidade do escritório. A base ganha um **perfil "Honorários/Gabriel"**. `design-relatorio-quinzenal-prodam` **não** entra (identidade Brandão Ozores é outra coisa) — só separamos o gatilho.

---

## 2. Aposentadorias (2) — aprovar item a item

- [ ] **D1 · `cowork-plugin-customizer`** → função já entregue pelo plugin `cowork-plugin-management`. Ação: desativar (arquivar 30 dias).
- [ ] **D2 · `create-cowork-plugin`** → idem. Ação: desativar (arquivar 30 dias).

> Limpeza correlata (não é skill, é plugin): existem **2 cópias idênticas** de `cockroachdb` e de `cowork-plugin-management` instaladas. Remover 1 de cada — faço quando você confirmar que prefere assim.

---

## 3. Arquivamento das cópias legadas no disco (comando preparado — NÃO executado)

Você pediu para eu preparar isto. **Achado de segurança que muda o plano:** a maior pasta legada, `PRODAM_DOCS\_WORKFLOW_IMPORTADO`, tem **3.889 PDFs (3,5 GB)** misturados com as skills — **não vou mover essa pasta em massa** (risco a provas).

| Pasta legada | Tamanho | SKILL.md | PDFs | Decisão |
|---|---|---|---|---|
| `_WORKFLOW_IMPORTADO\SKILLS NOVA` | — | 106 | **0** | ✅ Seguro arquivar (só skills) |
| `_WORKFLOW_IMPORTADO` (resto) | 3,5 G | 15 | **3.889** | ❌ Não tocar (provas misturadas) |
| `PRODAM_DOCS\_SKILLS` | 2,1 M | 2 | 0 | ⚠️ Não tocar — é seu empacotador (`.skill`/`.plugin`) |
| `PROJETO_PRODAM\_SKILLS_NOVAS_20260423` | 148 K | 2 | 0 | ⏸️ Talvez instalar, não arquivar |
| `DETRAN\_SKILLS_NOVAS_20260420` | 104 K | 5 | 0 | ⏸️ O CLAUDE.md do DETRAN diz que faltam instalar |

**Conclusão:** a única pasta segura e desejável de arquivar agora é `SKILLS NOVA`. Comando preparado (ele mesmo **aborta se encontrar qualquer PDF**):

```powershell
$src = "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_WORKFLOW_IMPORTADO\SKILLS NOVA"
$dst = "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_ARCHIVE_SKILLS_LEGADAS_2026-06-09"
$pdf = (Get-ChildItem -LiteralPath $src -Recurse -Filter *.pdf -ErrorAction SilentlyContinue | Measure-Object).Count
if ($pdf -gt 0) {
    Write-Host "ABORTADO: $pdf PDF(s) na origem — nada foi movido." -ForegroundColor Red
} else {
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Move-Item -LiteralPath $src -Destination $dst
    Write-Host "OK: 'SKILLS NOVA' arquivada em $dst (reversivel: e so mover de volta)." -ForegroundColor Green
}
```

> Reversão: `Move-Item "$dst\SKILLS NOVA" "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_WORKFLOW_IMPORTADO\"`.
> Lembrete: `PRODAM_DOCS` é marcada "intocável" no seu CLAUDE.md — por isso deixo **você** decidir rodar (ou me dar OK para eu rodar pelo ambiente).

---

## 4. Ordem recomendada

1. **Agora:** você confirma a origem das skills (passo 0) e aprova o **bloco rápido** (C6, C7, C9–C12, D1, D2) — risco zero.
2. **Depois:** reviso e gero os mesclados do **bloco jurídico** (C1, C2, C3, C5) e do Engeco (C8); você confirma as bases (C1, C2).
3. **Bloco jurídico (separado):** aplicar a seção `FONTE JURÍDICA OBRIGATÓRIA` em `prodam-juridico` e `proximo-passo-advisor` (as 2 do spec que faltam) + as 9 substantivas listadas na auditoria.
4. **Opcional:** rodar o comando de arquivamento de `SKILLS NOVA`.

---

## 5. Próximas confirmações que preciso de você

- **OK para rodar o comando da Seção 3** (arquivar `SKILLS NOVA`)? Ou prefere rodar você mesmo?
- **Quais itens do bloco rápido aprovo** (C6, C7, C9, C10, C11, C12, D1, D2)?
- **Confirma as bases** de C1 (`atualizacao-monetaria-creditos`) e C2 (`montagem-dossie-comprobatorio`)?
- **Origem das skills** (resultado do passo 0) — para eu escrever os cliques exatos.

_Nada neste plano foi executado. Aguardando seu OK item a item._
