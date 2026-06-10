---
description: Próximo passo de cobrança de um devedor conforme o pipeline F0→F6
argument-hint: <nome-do-devedor>
---

Determine o próximo passo de cobrança para **$ARGUMENTS**:

1. Leia `fase_atual`, `proximo_passo`, `forca_probatoria` e prescrição do devedor em `PRODAM_DOCS/profiles.json` (SSOT — não presumir).
2. Cruze com o pipeline oficial em `WORKFLOW_COBRANCA.md` (F0→F6, gates documentais e prazos) e, para órgãos públicos, com o `PLAYBOOK_ORGAOS_V2.md`.
3. Antes de recomendar qualquer medida contra órgão do Governo do AM, verifique as 4 exceções do Decreto Estadual 53.464/2026 (art. 1º §§1º-4º; teor em `PRODAM_DOCS/REFERENCIA_JURIDICA/16_AUXILIAR/`).
4. Responda com:
   - **Próximo passo** (1 linha, acionável).
   - **Gate documental**: o que precisa existir antes (ex.: trio NE+NF+aceite para execução — REsp 793.969/RJ, Rel. p/ acórdão Min. José Delgado).
   - **Prazo/risco**: prescrição (data e dias restantes), SLA aplicável e risco de esperar.
   - **Valor envolvido** (exigível, formato BRL).
5. Se a fase do profile e o próximo passo registrados forem inconsistentes entre si ou com o workflow, aponte a inconsistência em vez de escolher silenciosamente.

Não proponha medida que dependa de documento inexistente na pasta do devedor — liste o documento faltante como pré-requisito.
