# FENIXSOFT2 — Investigação (R$ 1,07M fora do SSOT)

**Status:** investigar — aguarda dados locais (PRODAM_DOCS)
**Aberto em:** 2026-05-27
**Origem:** `.continue-here.md` linhas 69-73 (Rota B 12/05) declara emergência; CSV atual só tem FENIXSOFT (NORMAL, d+1271)
**Decisor:** Gabriel Mar

## O que sabemos

Da `.continue-here.md` (Rota B, 2026-05-12):

> ### FENIXSOFT2 — R$ 1,07M — EMERGENCIA
> - 4 faturas D- em contratos 1/2020 e 2/2020
> - ZERO empenhos em qualquer fonte. ZERO marcos.
> - Empresa privada (5 anos). Ja prescrito ha ~100 dias.
> - ACAO IMEDIATA NECESSARIA

E no resumo Rota B:

> | FENIXSOFT2 | 4 | 0 | 0 | 4 | R$ 1.070.000 | DESCOBERTA — EMERGENCIA |
> | FENIXSOFT | 1 | 0 | 0 | 1 | R$ 135.000 | DESCOBERTA |

Ou seja, em 12/05 a Rota B identificou **duas entidades distintas**: FENIXSOFT (R$ 135K, 1 fatura) e FENIXSOFT2 (R$ 1,07M, 4 faturas). No CSV atual (27/05) só existe **FENIXSOFT** com R$ 888.250,00 — não bate com nenhum dos dois valores.

## Hipóteses

| Hip. | Descrição | Como confirmar |
|---|---|---|
| H1 | **Entidades distintas** (FENIXSOFT e FENIXSOFT2 são empresas diferentes — CNPJs distintos, contratos diferentes) | Buscar CNPJ raiz em SPCF dos contratos 1/2020 e 2/2020 e comparar |
| H2 | **Mesmo CNPJ, sub-divisão por contrato** | Pode ser que FENIXSOFT2 era nome alternativo para os contratos 1/2020 e 2/2020 da mesma empresa |
| H3 | **Erro de digitação na Rota B** que se propagou | Verificar se "FENIXSOFT2" aparece em algum PDF original ou só no script `rota_b_analise.py` |
| H4 | **Consolidação posterior** mergeou as duas em uma só "FENIXSOFT" no CSV | Verificar se R$ 135.000 + R$ 1.070.000 = R$ 1.205.000 (não bate com R$ 888.250 do CSV; logo, H4 isolado não explica) |

## Investigação a fazer (na máquina do Gabriel, com PRODAM_DOCS acessível)

### Passo 1 — Procurar "FENIXSOFT" em todas as fontes
```powershell
cd C:\Users\gabri\Desktop\PROJETO_PRODAM

# 1. No DB
duckdb -c "SELECT DISTINCT cliente FROM spcf_contratos WHERE cliente LIKE '%FENIX%'" PRODAM_DOCS\_ANALISE\prodam.db

# 2. Em PDFs (filename pattern)
Get-ChildItem -Path PRODAM_DOCS\ -Recurse -Filter "*FENIX*" -File | Select-Object FullName, Length, LastWriteTime

# 3. No profiles.json original (entradas FENIX*)
py -3.12 -c "import json; p=json.load(open('PRODAM_DOCS/profiles.json')); [print(k, '->', v.get('cnpj'), v.get('nome_completo')) for k,v in p.items() if 'FENIX' in k.upper()]"

# 4. No script rota_b_analise.py
Select-String -Path scripts\auditoria_DE\rota_b_analise.py -Pattern "FENIXSOFT"
```

### Passo 2 — Confirmar CNPJ dos contratos 1/2020 e 2/2020
```powershell
duckdb -c "SELECT contrato, cliente, cnpj, vigencia_inicio, valor FROM spcf_contratos WHERE contrato IN ('1/2020', '2/2020', '01/2020', '02/2020', '2020/001', '2020/002')" PRODAM_DOCS\_ANALISE\prodam.db
```

### Passo 3 — Cruzar com cobranças e NFs
```powershell
duckdb -c "SELECT * FROM spcf_faturas WHERE cliente LIKE '%FENIX%' ORDER BY dt_vencimento" PRODAM_DOCS\_ANALISE\prodam.db
duckdb -c "SELECT COUNT(*), SUM(valor) FROM spcf_nfs WHERE cliente LIKE '%FENIX%'" PRODAM_DOCS\_ANALISE\prodam.db
```

### Passo 4 — Auditoria física dos PDFs
- Abrir 5-10 PDFs aleatórios em `PRODAM_DOCS\FENIXSOFT*_CONSOLIDADO\` (ou pasta-mãe similar) e identificar:
  - CNPJ na nota fiscal
  - Razão social completa
  - Contrato referenciado

## Decisão esperada

Após investigação, decidir entre:

**A. Confirmar 2 entidades distintas (H1)**
- Criar linha FENIXSOFT2 no `profiles_resumo.csv`
- Criar perfil em `profiles.json` com CNPJ, evidências, etc.
- Plano: notificação extrajudicial com AR + protesto (privado, R$ 1,07M, ~100d prescrita)
- Justificativa: cada dia agrava argumento de inércia adversarial

**B. Confirmar entidade única (H2/H3/H4)**
- Atualizar valor de FENIXSOFT no CSV (de R$ 888K para R$ 1,205M se for soma)
- Mover faturas dos contratos 1/2020 e 2/2020 para o perfil único
- Atualizar `.continue-here.md` removendo menção a FENIXSOFT2
- Recalcular `d_plus_prescricao` (CSV diz NORMAL d+1271; Rota B diz prescrita há 100d — divergência)

## Risco se não decidir

- **R$ 1,07M sem CNPJ canônico** = peça jurídica fica com fundamento fraco
- Multa contratual (10% por prescrição perdida) pode incidir = ~R$ 107K adicional
- Cada dia que passa = +1 dia de inércia adversarial documentável

## Próximo passo

Gabriel roda Passos 1-3 acima e responde:
- "FENIXSOFT2 confirmada com CNPJ X" → ação A
- "FENIXSOFT2 é typo de FENIXSOFT" → ação B
- "Resultado inconclusivo" → terceira sessão de auditoria física

## Referências

- `.continue-here.md` (raiz, sessão Rota B 12/05/2026)
- `scripts/auditoria_DE/rota_b_analise.py` (gerador da tabela)
- `PRODAM_DOCS/_QUESTOES_CRITICAS/auditoria_DE_2026-05-12/` (relatórios S1.1 e prescricoes_triagem.md, se acessível localmente)
