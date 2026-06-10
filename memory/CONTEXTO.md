# CONTEXTO VIVO — Projeto PRODAM
_Última atualização: 2026-06-09 (sessão de consolidação da estrutura `.claude`)._

> Complementa o `CLAUDE.md` (regenerado por script) com o que NÃO é derivável dos dados: decisões recentes, pendências nominais e correções confirmadas. Atualizar ao fim de cada sessão relevante.

## 1. Últimas decisões (2026-06-09)
- **`.claude` única na raiz**: as `.claude` de `PRODAM_DOCS/` e `SPCF_EXTRACAO/` foram movidas para `_ARCHIVE_CLAUDE/2026-06-09/` (nada apagado). As de `impeccable-main/` são de pacote de terceiro (vendored) e ficaram intocadas; a de `_BACKUPS/` é snapshot e ficou onde está.
- **Índice git**: sem entradas fantasma (verificado `git ls-files` × disco — zero divergências; os plugins backprop/build/caveman/check/spec não constam nem do índice nem do histórico). `scheduled_tasks.lock` foi removido do índice (`git rm --cached`) e entrou no `.gitignore` junto com `.claude/worktrees/`.
- **Regra 14 nova** (gerador + CLAUDE.md): correção DETRAN por contrato (CT 022/2014 e 025/027 = IGPM + 1% a.m. + 2% CDC; silentes = Tema 810/STF + SELIC, Lei 14.905/2024) e **vedação à multa de 1%/dia da Cláusula 12.3.2** (protege o DETRAN, não a PRODAM).
- **Novos guardrails**: hooks `bloqueia-destrutivos.ps1` (deny em comando destrutivo sobre PDF/prodam.db/profiles.json/pastas de devedores), `protege-fontes.ps1` (ask em Edit/Write de profiles.json/prodam.db) e `lembrete-sessao.ps1` (regras críticas no boot local); `permissions.deny` em Edit/Write de `*.pdf` e `*.db` no `settings.json`.
- **Subagentes**: `auditor-dados` (somente leitura, cruza fontes) e `revisor-juridico` (gate pré-envio). **Slash commands**: `/status-devedor`, `/proximo-passo`, `/auditoria-rapida`.
- **Skills**: mantido o design existente — fonte em `PRODAM_DOCS/_SKILLS/` (fora do repo) + `.claude/skills/INDEX.md` versionado como rastreio. Não foram movidas para `.claude/skills/` para não versionar conteúdo sensível.

## 2. Pendências abertas
- **B1 — 89 faturas a reconciliar (DETRAN)**: `DETRAN_AUDITORIA_COMPLETA/88_FATURAS_RECONCILIAR.csv` (89 linhas de dados, conferido em 09/06) — decisão jurídica fatura a fatura; backups do CSV preservados na mesma pasta.
- **Regenerar satélites no Windows**: rodar `py -3.12 scripts\auto_update_claude_md.py` para o gerador materializar a Regra 14 também nos satélites (a edição manual do CLAUDE.md desta sessão é espelho fiel, mas o gerador é a fonte).
- **DETRAN — divergência de valor**: `profiles.json` com exigível R$ 0,00 × valor canônico R$ 28.196.572,22 (`DETRAN.valor_canonico`, reconciliado em 20/04) — alinhar antes de qualquer peça nova.
- **Prescrições**: SSP e SUHAB em 30/06/2026; SEJUSC em 31/08/2026; cutoff NF 110654 (CT 179/2018) em 19/08/2026; marco DETRAN (2026-03-20) a reconfirmar.
- **Dr. Fábio**: briefing v5 (`_ATUALIZACAO_v5_PARA_DR_FABIO.md`, 6 decisões) e redução do Ofício LAI 003/2026 para 2 contratos (CT 023/2014 + CT 179/2018).
- **Infra**: o mount Linux do sandbox trunca arquivos grandes recém-gravados (ex.: `profiles.json` cortado no byte 343.730) — em sessões Cowork, ler dados críticos pelo filesystem Windows (Read/Grep) ou validar por cópia com nome novo.

## 3. Correções confirmadas (não regredir)
- **REsp 793.969/RJ**: Rel. p/ acórdão **Min. José Delgado** (Teori Zavascki foi vencido) — citação invertida é erro recorrente já corrigido.
- **RPV/AM**: Lei estadual **2.748/2002**, teto **20 SM** ("Lei 3.683/2012" e "Lei 2.478" são citações erradas conhecidas; 60 SM é teto federal).
- **Decreto 53.464/2026** *sucedeu* (não "revogou") o 51.084/2025 — efeitos exauridos em 2025; §5º preserva reduções.
- **FUHAM** = Fundação Alfredo da Matta · **FHAJ** = Fundação Hospital Adriano Jorge — nunca inverter.
- **Multa 1%/dia (Cláusula 12.3.2 DETRAN)**: nunca usar em favor da PRODAM.
- Jurisprudência só do catálogo `REFERENCIA_JURIDICA/11_PESQUISAS_ORIGINAIS/PRECEDENTES_VERIFICADOS.md` (3 precedentes fabricados + 6 distorcidos já catalogados).
