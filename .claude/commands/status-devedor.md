---
description: Ficha completa de um devedor a partir de profiles.json + prodam.db
argument-hint: <nome-do-devedor> (ex.: DETRAN, SES/SUSAM, SSP, SEDUC, SEAD)
---

Monte a ficha do devedor **$ARGUMENTS** usando SOMENTE as fontes autoritativas (nunca inventar; nunca usar o Demonstrativo Excel):

1. Localize a chave do devedor em `PRODAM_DOCS/profiles.json` (a chave pode diferir do nome falado — ex.: `SES/SUSAM`, `FUAM_FUHAM`; em caso de ambiguidade, liste as candidatas e pergunte).
2. Extraia e apresente:
   - Identificação: nome completo, CNPJ, categoria (Gov Direta / Indireta / Privada).
   - Situação: `fase_atual`, `proximo_passo`, `forca_probatoria`.
   - Valores: exigível, atualizado (com data-base) — formato `R$ 1.234,56`.
   - Prescrição: data registrada, dias restantes a partir de hoje, marco interruptivo (se houver, com tipo e data).
   - Contratos: número(s) e `regime_aplicavel` de cada um.
3. Confira em `prodam.db` (somente SELECT, via `py -3.12`) a contagem de faturas do devedor e compare com o profile — divergência deve ser destacada.
4. Verifique a cobertura documental: existe `AUDITORIA_COMPLETUDE/AUDITORIA_<devedor>.md`? `DOSSIES_MULTIFORMATO/<devedor>/`? `DOCUMENTOS_GERADOS/<devedor>/`? Liste o que falta.
5. Feche com: alertas (prescrição < 90 dias em 🔴) e o próximo passo recomendado em 1 linha.

Lembrete: prescrição é por fatura individual (Art. 189 + 206 §5º I CC); FUHAM = Alfredo da Matta, FHAJ = Adriano Jorge.
