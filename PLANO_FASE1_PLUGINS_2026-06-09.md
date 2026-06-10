# PLANO — FASE 1: Limpeza de plugins
**Data:** 09/06/2026 · Antecede a Fase 2 (consolidação de skills, em `PLANO_DE_EXECUCAO_SKILLS_2026-06-09.md`).
**Estado:** nada executado. Você aplica no painel; eu só classifico. **Desligar plugin é reversível** (reabilita no painel).

---

## Resumo

Você tem **~95 plugins** instalados (fonte: `DIAGNOSTICO_SKILLS2.txt`, bloco [B]). Classificação:

- **Manter (núcleo do seu trabalho + ferramentas):** ~6
- **Duplicados (resolver versão):** 6 casos
- **Decidir (jurídicos genéricos — você diz quais usa):** ~14
- **Desligar (sem relação aparente com Direito Administrativo/Licitações/Recuperação de Créditos):** ~65

> Eu **não afirmo** que os "desligar" estão sem uso — são candidatos. Tudo que estiver marcado *(confirmar)* depende de você usar ou não. Comece pelos duplicados (risco zero) e pelos "sem relação" óbvios.

### Como desligar (no app)
Abra **Configurações → Capacidades** (Capabilities). Cada plugin tem um interruptor liga/desliga (ou opção *Remover*). Desligue os marcados abaixo. Se a sua tela estiver diferente, me mande um print que eu te guio. **Não** edite o `config.json` à mão.

---

## ✅ DECISÃO FINAL (09/06) — confirmado: LGPD + societário são relevantes

**MANTER (~13):** `productivity-prodam` · `data 1.3.0-engeco` · `legal 1.5.0-engeco` · `cowork-plugin-management` (1 cópia) · `pdf-viewer` · `superpowers` · `regulatory-legal` · `litigation-legal` · `privacy-legal` · `corporate-legal` · `commercial-legal` · `kyc-screener`.

**DESLIGAR — jurídicos genéricos (8):** `cocounsel-legal` · `ai-governance-legal` · `employment-legal` · `ip-legal` · `product-legal` · `legal-clinic` · `legal-builder-hub` · `law-student`.

**DESLIGAR — duplicados/versões:** `data 1.1.0` (fica a `-engeco`) · `legal 1.3.0` (fica a `-engeco`) · `operations` (as duas) · `sp-global` (as duas) · `cockroachdb` (as duas cópias) · 1 cópia extra de `cowork-plugin-management`.

**DESLIGAR — sem relação (toda a seção D abaixo, ~65):** finanças, dev/infra, SaaS e pacotes de função.

**Resultado:** de ~95 para **~13 plugins ativos**. Tudo reversível no painel.

---

## A. MANTER (núcleo + ferramentas que sustentam o trabalho)

| Plugin | Por que manter |
|---|---|
| `productivity-prodam` | Seu — produtividade do Projeto PRODAM. |
| `data 1.3.0-engeco` | Seu — pacote de dados customizado do Engeco. |
| `legal 1.5.0-engeco` | Seu — pacote jurídico customizado do Engeco. |
| `cowork-plugin-management` | Ferramenta que ajuda a gerenciar/limpar plugins (útil agora). |
| `pdf-viewer` | Visualizar PDFs (provas) — útil no seu fluxo. |
| `superpowers` | Recebe as consolidações `brainstorming`/`writing-plans` da Fase 2. |

---

## B. DUPLICADOS (resolver — manter 1 versão, desligar a outra)

| Plugin | Versões instaladas | Recomendação |
|---|---|---|
| `data` | `1.1.0` e `1.3.0-engeco` | Manter a `-engeco` (sua); desligar a `1.1.0` genérica. |
| `legal` | `1.3.0` e `1.5.0-engeco` | Manter a `-engeco` (sua); desligar a `1.3.0` genérica. |
| `operations` | `0.1.0` e `1.3.0` | Manter no máximo 1; provavelmente desligar ambas (sem relação). |
| `sp-global` | `1.0.0` e `1.0.1` | Desligar ambas (dados financeiros) — ver seção D. |
| `cockroachdb` | instalado 2× | Desligar (banco de dados; ver seção D). |
| `cowork-plugin-management` | instalado 2× | Manter 1; remover a cópia. |

---

## C. DECIDIR — jurídicos genéricos (você diz quais servem ao seu nicho)

Marque os que fazem sentido para Direito Administrativo / Licitações / Recuperação de Créditos. Os demais, desligar.

| Plugin | Provável utilidade para você |
|---|---|
| `regulatory-legal` | Talvez — direito regulatório/administrativo. |
| `litigation-legal` | Talvez — contencioso (recuperação judicial de créditos). |
| `privacy-legal` | Talvez — LGPD (você cita LGPD no projeto Engeco). |
| `corporate-legal` | Talvez — societário (desconsideração de PJ, devedores privados). |
| `commercial-legal` | Talvez — contratos. |
| `kyc-screener` | Talvez — due diligence de devedores. |
| `cocounsel-legal` | Genérico (jurisprudência EUA). Provável desligar. |
| `ai-governance-legal` | Provável desligar (governança de IA). |
| `employment-legal` | Provável desligar (trabalhista). |
| `ip-legal` | Provável desligar (propriedade intelectual). |
| `product-legal` | Provável desligar (jurídico de produto/tech). |
| `legal-clinic` | Provável desligar. |
| `legal-builder-hub` | Provável desligar. |
| `law-student` | Provável desligar (estudo). |

---

## D. DESLIGAR — sem relação aparente (confirmar e desligar)

Agrupados por tema. Nenhum tem ligação evidente com seu trabalho jurídico.

**Finanças / investimentos / contabilidade**
`carta-cap-table` · `carta-crm` · `carta-investors` · `equity-research` · `investment-banking` · `private-equity` · `wealth-management` · `fund-admin` · `valuation-reviewer` · `earnings-reviewer` · `financial-analysis` · `finance` · `model-builder` · `month-end-closer` · `gl-reconciler` · `statement-auditor` · `lseg` · `sp-global` (x2) · `bigdata-com` · `daloopa`

**Desenvolvimento / infraestrutura / dados**
`cockroachdb` · `planetscale` · `prisma` · `base44` · `fastly-agent-toolkit` · `sanity` · `cloudinary` · `atlan` · `qodo-skills` · `enterprise-search` · `ai-firstify`

**SaaS / integrações / comunicação**
`twilio-developer-kit` · `zoom-plugin` · `intercom` · `slack-by-salesforce` · `zapier` *(confirmar — automação)* · `airtable` · `box` *(confirmar — armazenamento)* · `common-room` · `apollo` · `zoominfo` · `postiz` · `nimble` · `brightdata-plugin` · `adspirer-ads-agent` · `vpai`

**Pacotes de função / outras áreas**
`human-resources` · `marketing` · `sales` · `product-management` · `engineering` · `operations` · `customer-support` · `small-business` · `bio-research` · `brand-voice` · `product-tracking-skills` · `market-researcher` · `meeting-prep-agent` · `pitch-agent` · `productivity` *(genérico — você já tem o `-prodam`)* · `data` (genérico) · `design` · `searchfit-seo`

**Ferramentas visuais / Office (confirmar — só se você usa)**
`adobe-for-creativity` · `figma` · `miro` · `claude-for-msft-365-install` *(Office 365 — confirmar)* · `desktop-commander` *(controle de arquivos no PC — confirmar)* · `vanta` · `fluent`

---

## E. Ordem recomendada (segura)

1. **Duplicados (seção B):** risco zero — desligar as versões redundantes.
2. **Finanças + Dev + SaaS (seção D):** desligar em bloco; reversível.
3. **Jurídicos (seção C):** decidir 1 a 1 — me diga seu nicho que eu recomendo o corte.
4. **Ferramentas (confirmar):** só desligue o que tiver certeza de não usar.

Meta realista: de ~95 para **~10–15 plugins ativos**, deixando o assistente mais rápido e focado.

---

## F. Depois desta fase → Fase 2 (skills)

Concluída a limpeza de plugins, entro nas **12 consolidações + 2 aposentadorias** das suas 107 skills (documento `PLANO_DE_EXECUCAO_SKILLS_2026-06-09.md`). Para cada consolidação eu te entrego um arquivo **`.skill`** pronto (você clica "Salvar skill") e a lista do que remover no painel.

_Nada neste plano foi executado. Reversível. Aguardando você desligar os plugins e/ou me dizer seu corte nos jurídicos._
