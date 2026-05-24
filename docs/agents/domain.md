# Domain Docs

Como as skills de engenharia (`improve-codebase-architecture`, `diagnose`, `tdd`, `grill-with-docs`) consomem a documentação de domínio deste repo.

## Antes de explorar, ler:

- **`CONTEXT.md`** no root — glossário do domínio (devedor, NE, NL, regime, prescrição, fee, TRD, dossiê, fatura exigível, etc.)
- **`docs/adr/`** no root — decisões arquiteturais; ler ADRs que tocam a área onde vai trabalhar.

Se algum desses arquivos não existir, **seguir em silêncio**. Não sinalizar ausência nem sugerir criar antecipadamente — a skill `grill-with-docs` cria sob demanda quando termos ou decisões surgem.

## Layout

Single-context (este repo):

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-...
│   └── 0002-...
└── (subpastas: scripts/, PRODAM_DOCS/, SPCF_EXTRACAO/, detran_dashboard/, ...)
```

Sem `CONTEXT-MAP.md`, sem `CONTEXT.md` por subpasta. O vocabulário é unificado em volta do Contrato 002/2026 e dos 70 devedores.

## Use o vocabulário do glossário

Quando sua saída nomeia um conceito do domínio (título de issue, proposta de refactor, hipótese, nome de teste), use o termo como definido em `CONTEXT.md`. Não derivar para sinônimos que o glossário evita.

Se o conceito ainda não está no glossário, é um sinal — ou está inventando linguagem que o projeto não usa (reconsiderar), ou há lacuna real (anotar para `grill-with-docs`).

## Sinalizar conflitos com ADR

Se sua saída contradiz um ADR existente, surface explicitamente em vez de sobrescrever silenciosamente:

> _Contradiz ADR-0007 (xyz) — mas vale reabrir porque…_

## Atenção ao gate manual jurídico

Mesmo que uma skill peça mudança em `PRODAM_DOCS/`, `DOCUMENTOS_GERADOS/`, `DOSSIES/`, `PRECEDENTES_VERIFICADOS.md`, `profiles.json` ou `KNOWLEDGE_BASE_JURIDICO.md`, **não auto-aplicar**. Apresentar diff e aguardar "OK aplicar" explícito — ver `protocolo-juridico-prodam`.
