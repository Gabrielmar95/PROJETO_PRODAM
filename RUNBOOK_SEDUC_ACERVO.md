# RUNBOOK — Auditoria documental SEDUC (execução noturna)

> **Para:** Gabriel (máquina Windows local — onde estão `prodam.db` real, pendrive, share DPCON e login SPCF).
> **Pipeline:** portada do DETRAN para `scripts/acervo/` (ver [`scripts/acervo/README.md`](scripts/acervo/README.md)).
> **Regra de ouro (NUNCA-1):** nenhum passo apaga/move/sobrescreve PDF — a pipeline só **cria** arquivos novos (`*.ocr.pdf`, CSVs, logs).
> Todos os scripts aceitam `--help` e `--dry-run`; em dúvida, rode com `--dry-run` antes.

Tempo total estimado da noite: **~3h a 4h30** (dominado pelo OCR e pelo lote SPCF).

---

## Passo 0 — Pré-flight (5 min)

```powershell
cd C:\Users\gabri    # NUNCA operar de dentro de _LIXO_NAO_USAR\_ARCHIVE

# A env var ativa cobraria a API do Console em vez do plano (NUNCA-8):
Test-Path Env:ANTHROPIC_API_KEY    # DEVE retornar False

cd C:\Users\gabri\Desktop\PROJETO_PRODAM
git fetch origin claude/seduc-debt-automation-8sabcb
git checkout claude/seduc-debt-automation-8sabcb
git log --oneline -3    # confirme que o commit "porta pipeline de acervo" aparece

# Dependências (só na primeira vez; ~5 min extras se faltar algo):
py -3.12 -m pip install pymupdf pdfplumber pypdf playwright
py -3.12 -m playwright install chromium
ocrmypdf --version    # se falhar: instalar ocrmypdf+tesseract (sem ele o OCR vira SKIP, não erro)
```

**Sucesso:** `Test-Path` = `False` · checkout sem conflito · `scripts\acervo\` existe com 7 arquivos · `py -3.12 scripts\acervo\inventario_pdfs.py --help` responde.

---

## Passo 1 — Memorial FINAL SEDUC (10-15 min)

Primeiro atualiza o cache de índices BCB usando o script do DETRAN (rede liberada lá), depois gera o memorial com o script da outra frente:

```powershell
py -3.12 C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\10_SCRIPTS_PYTHON\baixar_indices_bcb.py
py -3.12 scripts\gerar_memorial_devedor.py --orgao SEDUC --fonte db --data-base 2026-04-30
```

**Sucesso:** cache BCB atualizado até a competência corrente; memorial gerado sem fatura com índice ausente. Se `gerar_memorial_devedor.py` ainda não estiver na branch, pule e registre como pendência — o restante da noite NÃO depende dele.

---

## Passo 2 — Copiar DPCON do share para path local ASCII-safe (10-30 min, depende da rede)

Lição DETRAN: caracteres `ç`/`ã` vindos do driver SMB quebram poppler/ocrmypdf — sempre copiar para local antes. `/XJ` exclui junctions (lição §6.1 do DETRAN).

```powershell
robocopy "\\10.10.2.15\Prodam2\DPCON\SPCON\CLIENTES\SEDUC" `
         "C:\Users\gabri\Desktop\DPCON\SEDUC" `
         /E /XJ /R:2 /W:5 /NP /LOG:"C:\Users\gabri\Desktop\DPCON\__robocopy_SEDUC.log"
Get-Content C:\Users\gabri\Desktop\DPCON\__robocopy_SEDUC.log -Tail 15
```

**Sucesso:** rodapé do robocopy com `FAILED = 0` (códigos de saída 0-3 são OK); contagem de PDFs local ≈ contagem no share.

---

## Passo 3 — Copiar pendrive para o disco (5-15 min)

Nunca trabalhar direto no pendrive (risco de remoção acidental + lentidão USB). Ajuste `E:` para a letra real:

```powershell
$data = Get-Date -Format 'yyyy-MM-dd'
robocopy "E:\" "C:\Users\gabri\Desktop\PENDRIVE_PRODAM\$data" `
         /E /XJ /R:2 /W:5 /NP /LOG:"C:\Users\gabri\Desktop\PENDRIVE_PRODAM\__robocopy_$data.log"
Get-Content "C:\Users\gabri\Desktop\PENDRIVE_PRODAM\__robocopy_$data.log" -Tail 15
```

**Sucesso:** `FAILED = 0`; depois disso o pendrive pode ser ejetado.

---

## Passo 4 — Inventário + OCR + classificação (1-2h, dominado pelo OCR)

Roda sobre as DUAS pastas (DPCON e pendrive). Estimativa de OCR: **~8 min por 100 PDFs sem texto** (4 threads). O inventário em si é rápido (~1-2 min por 1.000 PDFs).

```powershell
cd C:\Users\gabri\Desktop\PROJETO_PRODAM
$OUT = "C:\Users\gabri\Desktop\SEDUC_AUDITORIA_COMPLETA\20_OCR_OUTPUT"
$data = Get-Date -Format 'yyyy-MM-dd'

# 4a. Inventário DPCON
py -3.12 scripts\acervo\inventario_pdfs.py --raiz C:\Users\gabri\Desktop\DPCON\SEDUC `
    --out "$OUT\__INV_DPCON" --threads 8

# 4b. Inventário pendrive
py -3.12 scripts\acervo\inventario_pdfs.py --raiz "C:\Users\gabri\Desktop\PENDRIVE_PRODAM\$data" `
    --out "$OUT\__INV_PENDRIVE" --threads 8

# Quantos PDFs sem texto? (dimensiona o tempo de OCR: ~8 min/100)
py -3.12 scripts\acervo\ocr_lote.py --universo "$OUT\__INV_DPCON\universo.csv"    --out "$OUT\__OCR_DPCON"    --dry-run
py -3.12 scripts\acervo\ocr_lote.py --universo "$OUT\__INV_PENDRIVE\universo.csv" --out "$OUT\__OCR_PENDRIVE" --dry-run

# 4c. OCR (gera *.ocr.pdf AO LADO dos originais — originais intocados)
py -3.12 scripts\acervo\ocr_lote.py --universo "$OUT\__INV_DPCON\universo.csv"    --out "$OUT\__OCR_DPCON"    --threads 4
py -3.12 scripts\acervo\ocr_lote.py --universo "$OUT\__INV_PENDRIVE\universo.csv" --out "$OUT\__OCR_PENDRIVE" --threads 4

# 4d. Classificação (índice lateral — NUNCA renomeia)
py -3.12 scripts\acervo\classificar_universo.py --universo "$OUT\__INV_DPCON\universo.csv" `
    --out "$OUT\classificados_v2_DPCON.csv" --orgao SEDUC
py -3.12 scripts\acervo\classificar_universo.py --universo "$OUT\__INV_PENDRIVE\universo.csv" `
    --out "$OUT\classificados_v2_PENDRIVE.csv" --orgao SEDUC
```

**Sucesso:** `universo.csv` das duas fontes gerados · `resultado_ocr.csv` com OK ≥ 95% (e zero status `SKIP` — SKIP significa ocrmypdf ausente) · `classificados_v2_*.csv` com maioria alta/média confiança · nos relatórios `.md`, % de PDFs com texto (originais + `.ocr.pdf`) ≥ 95%.

---

## Passo 5 — Cruzamento pendrive × SPCF (5 min)

Consulta SOMENTE LEITURA no `prodam.db` real (raiz do PROJETO_PRODAM):

```powershell
cd C:\Users\gabri\Desktop\PROJETO_PRODAM
py -3.12 scripts\acervo\cruzar_pendrive_spcf.py --db prodam.db --orgao SEDUC --out _SESSAO\SEDUC --dry-run   # confere plano
py -3.12 scripts\acervo\cruzar_pendrive_spcf.py --db prodam.db --orgao SEDUC --out _SESSAO\SEDUC
```

**Sucesso:** o script imprime os PRAGMAs e as colunas escolhidas; gera `_SESSAO\SEDUC\cruzamento_SEDUC_<ts>.csv` com as duas categorias (`FATURA_SEM_DOC_PENDRIVE` / `DOC_PENDRIVE_SEM_FATURA`) e total em R$ via Decimal. Se ele reclamar de coluna essencial, cole o PRAGMA impresso e ajuste a lista `CAND` do script (1 linha).

---

## Passo 6 — Lacunas SPCF: baixar NEs faltantes (30-60 min, depende do nº de lacunas)

Monte o CSV de faltantes (`;` + utf-8-sig, colunas `emp_id;num_ne;contrato`) a partir do cruzamento do Passo 5 / do CSV de lacunas da frente SEDUC. **Teste com 5 antes do lote** (rate 1,5 s obrigatório; login manual no browser que vai abrir):

```powershell
$env:SPCF_BASE_URL = 'https://spcf.prodam.am.gov.br'
$DEST = "C:\Users\gabri\Desktop\SEDUC_AUDITORIA_COMPLETA\02_NOTAS_EMPENHO\PDF"

# 6a. Dry-run + teste com 5
py -3.12 scripts\acervo\spcf_baixar_nes.py --cliente SEDUC --csv-faltantes _SESSAO\SEDUC\lacunas_ne_seduc.csv --out $DEST --dry-run
py -3.12 scripts\acervo\spcf_baixar_nes.py --cliente SEDUC --csv-faltantes _SESSAO\SEDUC\lacunas_ne_seduc.csv --out $DEST --apply --limit 5

# 6b. Lote completo (checkpoint a cada 10 — confirme com ENTER)
py -3.12 scripts\acervo\spcf_baixar_nes.py --cliente SEDUC --csv-faltantes _SESSAO\SEDUC\lacunas_ne_seduc.csv --out $DEST --apply

# 6c. Fallback _VIEW para os que falharam com "nenhum botao PDF" (Documento Comprovante vazio no SPCF):
#     filtre o log __SPCF_BAIXAR_NES_SEDUC_*.csv pelos FALHA e gere lacunas_ne_seduc_view.csv
py -3.12 scripts\acervo\spcf_captura_view.py --cliente SEDUC --csv-faltantes _SESSAO\SEDUC\lacunas_ne_seduc_view.csv --out $DEST --apply
```

**Sucesso:** log `__SPCF_BAIXAR_NES_SEDUC_<ts>.csv` com status OK + SHA256 preenchido para cada PDF; todo faltante coberto por Crystal Reports OU `_VIEW` (o `_VIEW` é captura de ficha oficial — documentar ao perito, lição DETRAN §5/§6).

---

## Passo 7 — Pós-processamento (30-45 min)

1. **Se houve qualquer `--apply` que gravou em DB** nesta noite → rodar a skill `sync-prodam-dbs` (sync DETRAN→PROJETO com backup + MD5). Os scripts de `scripts/acervo/` NÃO gravam em DB, mas confira o que a frente do memorial fez.
2. **Cláusulas dos 6 CTs SEDUC** → skill `extracao-clausulas-contratuais` sobre os contratos-base achados nos `classificados_v2_*.csv` (filtrar `tipo=CONTRATO` + confiança ≥ 0,8). **Prioridade: CT 14/2018 — 73 das 106 faturas SEDUC.**
3. Com regime confirmado em cláusula → atualizar `scripts\config\regimes_por_devedor.json` removendo o marcador `"presumido"` do que foi confirmado (backup do JSON antes).
4. **Localizar o Ofício 316/2020-GS/SEDUC** (negativa expressa — potencial marco/prova): filtrar `classificados_v2_*.csv` por `tipo=OFICIO` e `numero` contendo `316`, e busca textual nos `.ocr.pdf`:
   ```powershell
   Import-Csv "$OUT\classificados_v2_DPCON.csv" -Delimiter ';' | Where-Object { $_.tipo -eq 'OFICIO' -and $_.numero -like '*316*' } | Format-Table caminho,numero,data
   ```
5. Commit da sessão (o hook git faz push automático — nunca `git push` manual).

---

## Critérios de pronto (conferir antes de encerrar)

| Critério | Como verificar | Pronto? |
|---|---|---|
| `universo.csv` DPCON + pendrive gerados | `$OUT\__INV_DPCON\universo.csv` e `__INV_PENDRIVE\universo.csv` existem, linhas > 0 | ☐ |
| OCR completo, originais intocados | `resultado_ocr.csv`: OK ≥ 95%, zero `SKIP`; nenhum PDF original modificado (só `*.ocr.pdf` novos) | ☐ |
| % PDFs com texto ≥ 95% | relatório do inventário + OCR (com texto + OCRizados) / total | ☐ |
| `classificados_v2_*.csv` gerados (índice lateral) | dois CSVs com tipos distribuídos; NENHUM arquivo renomeado | ☐ |
| Cruzamento pendrive×SPCF | `cruzamento_SEDUC_<ts>.csv` com as 2 categorias + total R$ | ☐ |
| Lacunas SPCF cobertas | todo `emp_id` do CSV de faltantes com OK no log (Crystal ou `_VIEW`) | ☐ |
| Contratos-base dos 6 CTs SEDUC: achados OU declarados faltantes | lista achados (CT 14/2018 primeiro); faltantes anotados p/ Ofício LAI (modelo DETRAN 003/2026) | ☐ |
| Regimes confirmados | `regimes_por_devedor.json` sem `"presumido"` nos CTs com cláusula extraída | ☐ |
| Ofício 316/2020-GS/SEDUC localizado (ou esgotado) | caminho do PDF anotado; se não achado, registrar fontes varridas | ☐ |
| Memorial SEDUC gerado (Passo 1) | memorial em data-base 2026-04-30 sem índice ausente | ☐ |
| DBs sincronizados (se houve `--apply`) | skill `sync-prodam-dbs` rodada, MD5 idênticos | ☐ |
| Commit da sessão feito | `git log -1` na branch | ☐ |
