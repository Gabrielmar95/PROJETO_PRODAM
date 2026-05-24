---
name: normalizador-contratos-prodam
description: Normaliza números de contratos do Projeto PRODAM entre os 3 formatos que coexistem no disco — '006/2021' (PDFs, spcf_contratos), '6/2021' (profiles.json keys), '6-2021' ou '6_2021' (nomes de arquivo/CSV). Inclui detecção de colisões conhecidas (CT 296/2025 e CT 3/2026 do DETRAN são o mesmo PDF, por exemplo), mapas auxiliares (aliases SPCF, typos de filename, objeto e regime por contrato) e função canônica reutilizável em Python e PowerShell. Use quando 'normalizar contrato', 'comparar contratos', 'joinar contratos entre fontes', 'contrato 006 ou 6', 'PDF vs profiles', 'chave canônica contrato', 'colisão de contrato', 'mapa objeto contrato', 'regime correção contrato', 'SPCF ID contrato', 'typo filename contrato'.
type: utility
version: 1.1
updated: 2026-04-23
triggers:
  - normalizar contrato
  - comparar contratos
  - 006 vs 6
  - chave canônica contrato
  - colisao contrato
  - join contratos
  - formato contrato
  - mapa objeto contrato
  - regime correção contrato
  - SPCF ID contrato
  - typo filename contrato
---

# SKILL — Normalizador de Números de Contrato PRODAM

> **Versão:** 1.1 — 23/04/2026
> **Origem:** mapeamento feito na §3.6 do CLAUDE.md do DETRAN (18 chaves vs 15 contratos-base · CT 296/2025 = CT 3/2026 mesmo PDF)
> **Objetivo:** eliminar a classe de erro "parecem contratos diferentes mas são o mesmo" e o inverso
> **Novidade v1.1:** mapas auxiliares extraídos de `rename_contratos_formal.py` (DETRAN) — aliases SPCF, typos de filename, objeto por contrato, regime de correção, função `parse_ct_num` consolidada

## Os 3 formatos encontrados no disco

| Formato | Exemplo | Onde aparece |
|---|---|---|
| **Com zero à esquerda** | `006/2021`, `022/2014` | PDFs originais, coluna `numero` de `spcf_contratos` |
| **Sem zero** | `6/2021`, `22/2014` | keys de `profiles.json` → `DETRAN.contratos.6/2021` |
| **Com separador não-barra** | `6-2021`, `6_2021`, `006.2021` | nomes de arquivo, exports CSV, dumps OCR |

## Forma canônica adotada

```
<numero_sem_zeros>/<ano_4_digitos>
```

Exemplos:
- `006/2021` → `6/2021`
- `22/2014`  → `22/2014`
- `003-2026` → `3/2026`
- `75_2022`  → `75/2022`

## Função Python (canônica)

```python
import re

def normalizar_contrato(valor: str) -> str:
    """
    Normaliza '006/2021', '6/2021', '6-2021', '006.2021' → '6/2021'.

    Retorna o valor original (trim) se não casar com padrão conhecido.
    """
    if not valor:
        return ""
    m = re.match(r"0*(\d+)[/\-_.](\d{4})", valor.strip())
    if not m:
        return valor.strip()
    return f"{m.group(1)}/{m.group(2)}"


# Testes
assert normalizar_contrato("006/2021") == "6/2021"
assert normalizar_contrato("6/2021")   == "6/2021"
assert normalizar_contrato("006-2021") == "6/2021"
assert normalizar_contrato("022.2014") == "22/2014"
assert normalizar_contrato("  3/2026 ") == "3/2026"
```

## Função PowerShell (equivalente)

```powershell
function Normalize-Contrato {
    param([string]$Valor)
    if ([string]::IsNullOrWhiteSpace($Valor)) { return "" }
    if ($Valor -match '0*(\d+)[/\-_.](\d{4})') {
        return "$($matches[1])/$($matches[2])"
    }
    return $Valor.Trim()
}

# Testes
Normalize-Contrato "006/2021"   # 6/2021
Normalize-Contrato "006-2021"   # 6/2021
Normalize-Contrato "022.2014"   # 22/2014
```

## Colisões conhecidas (mesmo contrato com 2 numerações)

Quando PRODAM renumera um contrato (assume novo ano orçamentário mantendo o objeto), os dois números apontam para a **mesma negociação**. A normalização canônica **NÃO** resolve isso automaticamente — é necessário um mapa explícito.

### DETRAN — `contratos_colisoes.json` (template)

```json
{
  "_meta": {
    "descricao": "Mapa de contratos que são fisicamente o mesmo documento/negociação, mas aparecem com 2 numerações por renumeração orçamentária.",
    "atualizado_em": "2026-04-23"
  },
  "DETRAN": [
    {
      "numeros": ["296/2025", "3/2026"],
      "pdf_base": "01_CONTRATOS/PDF/CT_003_2026_DETRAN.pdf",
      "motivo": "Renumeração entre anos orçamentários"
    }
  ]
}
```

### Detecção automática de candidatos a colisão

Se 2 contratos compartilham o mesmo PDF-base no disco, marcar para investigação:

```python
from collections import defaultdict
def detectar_colisoes_por_pdf(contratos: dict) -> list:
    """
    contratos: {numero_normalizado: {"pdf": path}}
    Retorna lista de tuplas (pdf_path, [numeros_que_apontam]).
    """
    inv = defaultdict(list)
    for num, meta in contratos.items():
        pdf = meta.get("pdf")
        if pdf:
            inv[pdf].append(num)
    return [(pdf, nums) for pdf, nums in inv.items() if len(nums) > 1]
```

## Mapas auxiliares — aliases SPCF, typos, objetos e regimes

> Extraído de `DETRAN_AUDITORIA_COMPLETA/10_SCRIPTS_PYTHON/rename_contratos_formal.py`
> (linhas 50-95 do script). DETRAN populado como ground truth; SES/SSP como templates vazios.

A normalização canônica resolve diferença de formato (`006/2021` vs `6/2021`), mas ela **não basta** em 3 cenários:

1. **ID SPCF cru no filename**: `contrato_DETRAN_12086` não traz o número do CT — só o ID interno do SPCF. É preciso um mapa explícito `SPCF_ID → (NNN, AAAA)`.
2. **Typo sem separador**: `Contrato 2762014` não bate com nenhum regex razoável — foi gerado com erro humano. Precisa mapa explícito.
3. **Enriquecimento semântico**: depois de identificar o contrato, frequentemente queremos o **objeto** ("Sistema SCIT", "Manutenção") e o **regime de correção** (IGPM+1%+2%, SELIC Lei 14.905, etc). Esses metadados moram em dicts pareados por `(NNN, AAAA)`.

### a) Aliases por ID SPCF (DETRAN)

```python
# Mapeamento explicito de IDs SPCF para (NNN, AAAA)
SPCF_ID_PARA_CT = {
    "12086": ("003", "2026"),   # contrato_DETRAN_12086 = CT 003/2026 (prop 14421)
}
```

### b) Typos conhecidos de filename (DETRAN)

```python
# Typos conhecidos no filesystem (filenames corrompidos)
FILENAME_TYPO_PARA_CT = {
    "2762014": ("027", "2014"),  # "Contrato 2762014" -> 27/2014 (typo sem separador)
}
```

### c) Objeto do contrato-base (DETRAN)

```python
# Mapa objeto de contrato-base por numero (validado em CLAUDE.md §3.6)
OBJETO_CONTRATO_DETRAN = {
    ("022", "2014"): "Sistema-SCIT-Processamento-Diario",
    ("025", "2014"): "Manutencao-de-Sistema",
    ("027", "2014"): "Servico-de-Rede",
    ("017", "2015"): "Data-Center",
    ("004", "2016"): "Sistema-de-Biometria",
    ("006", "2021"): "Rede-VPN-Firewall-MetroMao-Assessoria",
    ("010", "2021"): "SW-Gestao-de-Transito",
    ("012", "2021"): "Desenvolvimento-de-Sistemas",
    ("075", "2022"): "Sistema-SIGMO",
    ("083", "2022"): "Licenca-Talao-Eletronico",
    ("060", "2022"): "Proposta-Comercial",
    ("071", "2022"): "Proposta-Comercial",
    ("003", "2026"): "Assessoria-Tecnica-Prop-14421",
    ("296", "2025"): "Assessoria-Tecnica-Prop-14421",
}
```

> **Convenção de nomes**: ASCII puro, sem acentos, palavras separadas por hífen (`-`).
> Segue o padrão usado em `gerar_nome_formal` para compor filenames (`CT-006.2021_Contrato-Base_Rede-VPN-Firewall-MetroMao-Assessoria_Regime-IGPM-via-4TA.pdf`). Manter ASCII evita problemas de encoding em CSV, NTFS longo e tooling Windows.

### d) Regime de correção por contrato (DETRAN)

```python
# Regimes de correcao por contrato (CLAUDE.md §1.2 do DETRAN)
REGIME_DETRAN = {
    ("022", "2014"): "IGPM+1pct+2pct",
    ("025", "2014"): "IGPM+1pct+2pct",
    ("027", "2014"): "IGPM+1pct+2pct",
    ("017", "2015"): "Silente",
    ("004", "2016"): "Contratual",
    ("006", "2021"): "IGPM-via-4TA",
    ("010", "2021"): "Silente",
    ("012", "2021"): "IPCA-via-5TA",
    ("075", "2022"): "IPCA",
    ("083", "2022"): "IPCA",
    ("060", "2022"): "Silente",
    ("071", "2022"): "Silente",
    ("003", "2026"): "SELIC-Lei-14905",
    ("296", "2025"): "SELIC-Lei-14905",
}
```

> **Regimes canônicos** (7 variantes documentadas):
> `IGPM+1pct+2pct` · `Silente` · `Contratual` · `IGPM-via-4TA` · `IPCA` · `IPCA-via-5TA` · `SELIC-Lei-14905`
>
> - `Silente`: contrato não menciona índice — aplica-se o regime legal supletivo (SELIC a partir de 31/08/2024 via Lei 14.905/2024).
> - `IGPM-via-4TA`, `IPCA-via-5TA`: índice introduzido por termo aditivo posterior, não pelo contrato-base.
> - `SELIC-Lei-14905`: regime ex lege para contratos silentes após 31/08/2024.

### e) Função `parse_ct_num` consolidada

Cascata de estratégias em ordem de especificidade. Usa a forma canônica com zero-pad (`NNN` 3 dígitos, `AAAA` 4 dígitos) porque esses mapas auxiliares são chaveados por tupla `(NNN, AAAA)` — não pela forma canônica `normalizar_contrato` (que remove zeros). **Não confundir os dois mundos**:

- `normalizar_contrato` devolve `"6/2021"` — usada para **comparar** e **joinar** entre fontes (profiles.json usa essa forma).
- `parse_ct_num` devolve `("006", "2021")` — usada como **chave** nos dicts `OBJETO_*`, `REGIME_*`.

```python
import re

CT_NUM_RE = re.compile(
    r"(?:contrato|CT|ct)[\s_]*[Nn]?[ºo°\.]?[\s_]*0*(\d{1,3})[._\-/ ]+0*(\d{2,4})",
    re.IGNORECASE,
)
CT_NUM_SHORT_RE = re.compile(
    r"(?:^|[\s_])0*(\d{1,3})\.0*(\d{2,4})(?=[\s_\-.]|$)"
)  # "022.2014" / "22.14" / "83.22" -> (NNN, AAAA)
PROPOSTA_RE = re.compile(
    r"PROPOSTA[\s_]+0*(\d{1,3})[.\-/]0*(\d{2,4})", re.IGNORECASE
)


def parse_ct_num(nome: str) -> tuple[str, str] | None:
    """
    Retorna (NNN, AAAA) — ambos zero-padded — do contrato-base citado no nome.

    Ordem:
      1. SPCF_ID_PARA_CT (alias de ID cru)
      2. FILENAME_TYPO_PARA_CT (typos sem separador)
      3. CT_NUM_RE (prefixo 'Contrato'/'CT')
      4. PROPOSTA_RE (prefixo 'PROPOSTA')
      5. CT_NUM_SHORT_RE (padrão curto standalone) + sanity check 2010-2030

    Expande ano 2 dígitos (<80 = 20xx; >=80 = 19xx).
    """
    # 1. IDs SPCF conhecidos
    for spcf_id, ct in SPCF_ID_PARA_CT.items():
        if spcf_id in nome:
            return ct
    # 2. Typos conhecidos
    for typo, ct in FILENAME_TYPO_PARA_CT.items():
        if typo in nome:
            return ct
    # 3. variantes explicitas com prefixo "Contrato" / "CT"
    m = CT_NUM_RE.search(nome)
    if m:
        num = m.group(1).zfill(3)
        ano = m.group(2)
        if len(ano) == 2:
            ano = ("20" if int(ano) < 80 else "19") + ano
        return num, ano
    # 4. proposta
    m = PROPOSTA_RE.search(nome)
    if m:
        num = m.group(1).zfill(3)
        ano = m.group(2)
        if len(ano) == 2:
            ano = ("20" if int(ano) < 80 else "19") + ano
        return num, ano
    # 5. padrao curto standalone (com sanity check de ano)
    m = CT_NUM_SHORT_RE.search(nome)
    if m:
        num, ano = m.group(1).zfill(3), m.group(2)
        if len(ano) == 2:
            ano = ("20" if int(ano) < 80 else "19") + ano
        if 2010 <= int(ano) <= 2030:
            return num, ano
    return None


# Testes
assert parse_ct_num("contrato_DETRAN_12086.pdf") == ("003", "2026")
assert parse_ct_num("Contrato 2762014 - Prazo.pdf") == ("027", "2014")
assert parse_ct_num("CT 006_2021 MetroMao.pdf") == ("006", "2021")
assert parse_ct_num("PROPOSTA 075.2022 SIGMO.pdf") == ("075", "2022")
assert parse_ct_num("022.2014 - PRODAM - termo aditivo.pdf") == ("022", "2014")
assert parse_ct_num("relatorio_anual_2023.pdf") is None  # ano fora dos prefixos
```

### f) Como estender para outros devedores

Chave central: `MAPAS_POR_DEVEDOR`, um dict-de-dicts indexado por nome do devedor. Cada entrada agrega os 4 mapas auxiliares daquele devedor. DETRAN já está populado como ground truth; SES/SSP como templates vazios — quando começar a auditoria deles, **preencher in-place**, não criar arquivo novo.

```python
MAPAS_POR_DEVEDOR: dict[str, dict] = {
    "DETRAN": {
        "spcf_id": SPCF_ID_PARA_CT,
        "typos": FILENAME_TYPO_PARA_CT,
        "objeto": OBJETO_CONTRATO_DETRAN,
        "regime": REGIME_DETRAN,
    },
    "SES": {            # template — preencher quando começar a auditoria
        "spcf_id": {},
        "typos": {},
        "objeto": {},
        "regime": {},
    },
    "SSP": {            # template — preencher quando começar a auditoria
        "spcf_id": {},
        "typos": {},
        "objeto": {},
        "regime": {},
    },
}


def mapas_do_devedor(devedor: str) -> dict:
    """Retorna o bloco de mapas para um devedor, ou blocos vazios se não cadastrado."""
    return MAPAS_POR_DEVEDOR.get(devedor, {
        "spcf_id": {}, "typos": {}, "objeto": {}, "regime": {},
    })
```

## Algoritmo de comparação robusta

Para verificar se dois valores de contrato representam o mesmo contrato:

```python
def mesmo_contrato(a: str, b: str, colisoes: list[list[str]] | None = None) -> bool:
    """
    Retorna True se a e b são o mesmo contrato (após normalização + mapa de colisões).
    """
    na = normalizar_contrato(a)
    nb = normalizar_contrato(b)
    if na == nb:
        return True
    if colisoes:
        for grupo in colisoes:
            grupo_norm = {normalizar_contrato(g) for g in grupo}
            if na in grupo_norm and nb in grupo_norm:
                return True
    return False


# Exemplo DETRAN
colisoes_detran = [["296/2025", "3/2026"]]
assert mesmo_contrato("006/2021", "6/2021", colisoes_detran) is True
assert mesmo_contrato("296/2025", "3/2026", colisoes_detran) is True
assert mesmo_contrato("75/2022", "83/2022", colisoes_detran) is False
```

## Quando usar

Aplicar **em todo lugar** que contratos sejam joinados entre fontes distintas:

| Operação | Sem normalização | Com normalização |
|---|:---:|:---:|
| `profiles.json.contratos[x]` × `spcf_contratos.numero` | ❌ Erra em contratos com 0 à esquerda | ✅ Bate |
| Path de PDF × key de profile | ❌ Diferenças de separador quebram | ✅ Bate |
| Key de dashboard × linha de memorial | ❌ "022/2014" ≠ "22/2014" | ✅ Bate |
| Detecção de duplicatas em consolidados JSON | ❌ Conta 2 contratos distintos | ✅ Conta 1 |

## Anti-padrões (não fazer)

1. **Normalizar usando só `str.replace('0', '')`** — corrompe anos (`2010` → `21`).
2. **Normalizar usando só `int(numero)`** — perde o ano.
3. **Forçar zero à esquerda em todos os lados** — quebra joins com `profiles.json` que usa forma sem zero.
4. **Ignorar colisões** — trata CT 296/2025 e CT 3/2026 como 2 contratos distintos, duplicando valores no agregado.
5. **Inventar regime ou objeto por similaridade de nome** — sempre consultar `MAPAS_POR_DEVEDOR` ou retornar `None`/`""` quando ausente. Opinar sem dado documental é violação da Regra 18 (`REFERENCIA_JURIDICA/` como SSOT).
6. **Usar `normalizar_contrato("006/2021")` como chave em `REGIME_DETRAN`** — essa função devolve `"6/2021"`, mas o dict é chaveado por tupla `("006", "2021")`. Use `parse_ct_num` para essa finalidade.

## Integração

- Usado por: `auditoria-paridade-db-csv` (ao matching contratos), `validador-cadeia-documental-fatura` (elo 1), `montagem-dossie-comprobatorio`, `renomeador-pdfs-prodam` (`parse_ct_num` + `OBJETO_*` + `REGIME_*`)
- Pré-requisito para: qualquer função que faça `join` entre `profiles.json` e `spcf_contratos` ou `01_CONTRATOS/PDF/`
- Complementa: `schema-navigator-prodam`

## Arquivos da skill

| Arquivo | Função |
|---|---|
| `SKILL.md` | Este documento |
| `normalizador.py` | Módulo Python importável: `normalizar_contrato`, `mesmo_contrato`, `parse_ct_num`, `detectar_colisoes_por_pdf`, `mapas_do_devedor` + os 5 mapas (`SPCF_ID_PARA_CT`, `FILENAME_TYPO_PARA_CT`, `OBJETO_CONTRATO_DETRAN`, `REGIME_DETRAN`, `MAPAS_POR_DEVEDOR`) |
| `contratos_colisoes.json` | Mapa de colisões conhecidas por devedor (DETRAN populada, outros vazios) |

## Referências

- CLAUDE.md §3.6 DETRAN (tabela dos 18 contratos DETRAN × 15 base × 3 propostas/rescindidos)
- CLAUDE.md §1.2 DETRAN (tabela de regimes de correção por contrato)
- Caso DETRAN: CT 296/2025 + CT 3/2026 apontam para `CT_003_2026_DETRAN.pdf`
- Fonte dos mapas v1.1: `DETRAN_AUDITORIA_COMPLETA/10_SCRIPTS_PYTHON/rename_contratos_formal.py` (linhas 50-95)
- Memória: `project_detran_universos_db_csv.md` (padrões de numeração paralela)
