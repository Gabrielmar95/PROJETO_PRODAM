# Sessão 2026-05-08 — Sincronizador Jurídico (Opção B)

Continuação da Opção A (mesma data). Objetivo: rodar `etapa2_varredura.py` em modo `--strict` contra a base jurídica curada `PRODAM_DOCS/REFERENCIA_JURIDICA/`, isolada do CLAUDE.md raiz (cujos 6 hits CRÍTICO/ALTO já foram catalogados como FPs na Opção A).

## Comando executado

```powershell
py -3.12 "C:\Users\gabri\.claude\skills\sincronizador-juridico-matriz\scripts\etapa2_varredura.py" --corpus "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\REFERENCIA_JURIDICA" --strict
```

`--pattern` mantido no default (`*.md *.txt`) — não passei `.docx`/`.pdf` (bug Iter 14b ainda em aberto).

## Cabeçalho do output

```
etapa2_varredura: 182 skills, categorias={'operacional': 82, 'excluir': 53, 'nucleo': 39, 'referencia': 8}, strict=True, pendentes_validacao=['E04'], --corpus=229 arquivos, overrides={13 skills, 13 silenciamentos, 1 mudanças categoria}
hits totais: 2393  |  bloqueios: 2073  |  warnings: 106
```

- **229 arquivos** varridos em `REFERENCIA_JURIDICA` (`*.md` + `*.txt`).
- **2073 BLOQUEIOS** — em modo `--strict`, qualquer hit CRÍTICO/ALTO em tier `peca` ou `nucleo` vira EXIT_BLOCK.
- **106 WARN** — restantes (E04 `pendente_validacao`, hits silenciados por overrides, hits em tiers tolerantes).
- **EXIT=1, mas NÃO é EXIT_BLOCK natural**: o script crashou antes de chegar na linha de exit. Ver bug abaixo.

## Bug novo (não estava na Opção A) — UnicodeEncodeError

```
Traceback (most recent call last):
  File "...\etapa2_varredura.py", line 1494, in <module>
    sys.exit(main())
  File "...\etapa2_varredura.py", line 1482, in main
    return varrer(...)
  File "...\etapa2_varredura.py", line 1393, in varrer
    print(f"  {nome} ({tier}):")
  File "...\Python312\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
UnicodeEncodeError: 'charmap' codec can't encode character '‑' in position 184: character maps to <undefined>
```

- Console Windows usa `cp1252` por padrão. O caractere `‑` (NON-BREAKING HYPHEN) não existe em cp1252.
- O crash ocorreu no `print(f"  {nome} ({tier}):")` da função `varrer`, durante a impressão do detalhe por skill/peça.
- **Arquivo culpado identificado** (busca `Get-ChildItem ... | Where-Object { $_.Name.Contains([char]0x2011) }`):
  ```
  REFERENCIA_JURIDICA\14_ANALISES_INDIVIDUAIS_API\Análise crítica e verificação factual do PDF "Guia de Estudo e Plano de Pesquisa GPT‑1"_ANALISE.md
  REFERENCIA_JURIDICA\15_TEXTOS_EXTRAIDOS_API\Análise crítica e verificação factual do PDF "Guia de Estudo e Plano de Pesquisa GPT‑1".txt
  ```
  O hífen entre `GPT` e `1` é U+2011, não U+002D. Provavelmente artefato de OCR/conversão de PDF.
- **Consequência:** crash interrompeu a impressão do relatório completo. Vimos hits até aproximadamente metade da pasta `14_ANALISES_INDIVIDUAIS_API`; os arquivos de `15_*` em diante não foram impressos (mas foram contados nos totais).

## Diagnóstico de design — tier `peca` inadequado para base curada

Os 2073 bloqueios não indicam erros reais nas peças jurídicas — indicam **uso incorreto da varredura**.

- Hits visíveis no output: ~95% são **E01** (`prescrição`/`prescritas`/`prescricional`) e ~5% **E02** (`interrupção da prescrição`/`marco interruptivo`).
- Em **peça gerada** (TRD, notificação extrajudicial, petição), `prescrição` sem qualificador de cutoff é red flag — o detector E01 está desenhado para isso.
- Em **conteúdo educativo/catálogo** (`KNOWLEDGE_BASE_JURIDICO.md`, `CONSOLIDADO_02_PRESCRICAO.md`, `MAPA_COMPLETO_FASES_PROJETO.md`), a palavra é **o tema do documento**.
- O tier `peca` aplica os mesmos detectores aos dois universos. Em modo `--strict`, isso bloqueia toda a base curada por construção.

**Conclusão:** `--strict` contra `REFERENCIA_JURIDICA/` é uso incorreto. A varredura `--strict` deve rodar contra **artefatos gerados** (`DOCUMENTOS_GERADOS/`, peças em rascunho), não contra a base de estudos.

## Pendências para próxima sessão

Ver TODOs adicionados no sincronizador:

1. **Bug encoding cp1252 (item b)** — em `~/.claude/skills/sincronizador-juridico-matriz/TODO.md`, seção "Próximas iterações do sincronizador":
   - Sintoma: `UnicodeEncodeError 'charmap'` em U+2011 no nome de arquivo, linha 1393 do `etapa2_varredura.py`.
   - Fix proposto: `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` no início do `main`, OU `try/except UnicodeEncodeError` em volta dos `print()` críticos com fallback ASCII.
   - Risco: `reconfigure` pode falhar se stdout estiver redirecionado para arquivo já aberto sem buffer reconfigurável.

2. **Tier `peca` inadequado para base curada (item c)** — entrada separada no mesmo TODO.md:
   - Sintoma: 2073 FPs em `--strict` contra `REFERENCIA_JURIDICA/`, ~95% E01 em contexto educativo.
   - Causa raiz: tier `peca` foi desenhado para peças geradas, não para base curada de estudos jurídicos.
   - 2 alternativas de fix (não decidir agora, discutir antes):
     1. Criar novo tier `base_curada` com gravidades mais permissivas (E01 vira INFO ou WARN, não CRÍTICO).
     2. Marcar `REFERENCIA_JURIDICA/` como pasta excluída por padrão no `expandir_corpus()`, exigindo flag `--include-base-curada` para varrer.
   - Recomendação preliminar: **opção 2** (mais simples, reversível, e mais alinhada com o uso real — quem rodar varredura sobre a base curada quer fazê-lo deliberadamente).

3. **FP E06 negação contextual** (já registrado na Opção A, sessão 2026-05-08 anterior) — ainda em aberto.

4. **Iter 14b** (read_text com binários) — ainda em aberto, evitado por omissão (default `*.md *.txt`).

## Não-objetivos desta sessão

- Não houve commit. Sem alteração em `prodam.db`, `profiles.json`, ou qualquer arquivo do portfólio jurídico.
- Não corrigi o bug de encoding nem o tier — só registrei.
- Não renomeei os 2 arquivos com U+2011 no nome (são da `REFERENCIA_JURIDICA/`, não devem ser tocados sem decisão consciente; ver pendência cleanup OCR).
- Não rodei a variante alternativa (`--corpus CLAUDE.md REFERENCIA_JURIDICA --strict`) — confirmaria EXIT_BLOCK end-to-end mas é redundante após este achado.
