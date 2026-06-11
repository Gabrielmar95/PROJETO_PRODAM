# scripts/acervo/ — Pipeline de auditoria documental (portada do DETRAN, genérica por devedor)

Porte dos scripts de `DETRAN_AUDITORIA_COMPLETA/10_SCRIPTS_PYTHON/` para uso com qualquer
devedor (próximo: **SEDUC**). Paths hardcoded viraram argparse; dependências de skills
não versionadas foram removidas/reimplementadas inline.

**Regras herdadas do projeto (valem para todos):** nunca apagar/mover/sobrescrever PDF
(só criar arquivos novos, ex.: `*.ocr.pdf` ao lado do original) · CSV `;` + `utf-8-sig` ·
datas ISO · `Decimal` para BRL · rate-limit SPCF 1,5 s · todos têm `--help` e `--dry-run`.

## Ordem de uso (por devedor)

| # | Script | Faz o quê | Entrada → Saída |
|---|--------|-----------|------------------|
| 1 | `inventario_pdfs.py` | Varre o acervo (pymupdf): tem_texto, páginas, MD5, tamanho. **Só inventaria.** | `--raiz DIR --out DIR [--excluir X]...` → `universo.csv` |
| 2 | `ocr_lote.py` | OCR (ocrmypdf `--skip-text --deskew`) nos PDFs com `tem_texto=0`. Gera `*.ocr.pdf` ao lado; SKIP se binário ausente. | `--universo universo.csv --out DIR [--limit N]` → `resultado_ocr.csv` |
| 3 | `classificar_universo.py` (usa `classificador_v2.py`) | Classifica 16 tipos (NE/NF/CONTRATO/TA/CARTA...) com hints de pasta e detecção de página de assinatura e-Doc. **Índice lateral — nunca renomeia.** | `--universo universo.csv --out classificados_v2.csv [--orgao SEDUC]` |
| 4 | `cruzar_pendrive_spcf.py` | SQLite **somente leitura**: faturas do órgão sem doc de pendrive + docs de pendrive sem fatura. | `--db prodam.db --orgao SEDUC --out DIR` → `cruzamento_<ORGAO>_<ts>.csv` |
| 5 | `spcf_baixar_nes.py` | Baixa PDFs Crystal Reports das NEs faltantes (login **manual** headed, rate 1,5 s, valida %PDF/páginas/SHA256). | `--cliente SEDUC --csv-faltantes X.csv --out DIR --apply [--limit 5]` |
| 6 | `spcf_captura_view.py` | Fallback `_VIEW`: captura a ficha HTML do empenho como PDF A4 (CDP printToPDF) quando o SPCF não tem o Crystal Reports. | mesmos parâmetros do #5 |

Dependências (instalar uma vez): `py -3.12 -m pip install pymupdf pdfplumber pypdf playwright`
+ `py -3.12 -m playwright install chromium` + ocrmypdf/tesseract no PATH (passos 5-6 só playwright/pypdf).

Runbook completo da noite SEDUC: [`RUNBOOK_SEDUC_ACERVO.md`](../../RUNBOOK_SEDUC_ACERVO.md) na raiz do repo.
