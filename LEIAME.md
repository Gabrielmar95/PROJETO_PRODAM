# PROJETO PRODAM — Mapa de Navegação

**Atualizado:** 2026-04-18
**Responsável:** Gabriel Mar (OAB/AM 15.697) — Brandão Ozores Advogados
**Contrato:** 002/2026 — Recuperação de créditos PRODAM S.A.

## ⚡ Regra de ouro

A única pasta ativa é esta: `C:\Users\gabri\Desktop\PROJETO_PRODAM\`.
Trabalho jurídico por devedor fica em:
- `C:\Users\gabri\Desktop\DETRAN_AUDITORIA_COMPLETA\`
- `C:\Users\gabri\Desktop\SEDUC_AUDITORIA_COMPLETA\`

Qualquer pasta fora dessas 3 é histórico ou lixo.

## 📊 Fontes canônicas

- `PROJETO_PRODAM\PRODAM_DOCS\_ANALISE\prodam.db` — banco SQLite canônico (91 MB)
  - 9 tabelas, ~78k registros
  - Principais: devedores, spcf_contratos, spcf_faturas, spcf_empenhos, spcf_nfs, pendrive_docs, cruzamento_spcf_pendrive
- `PROJETO_PRODAM\PRODAM_DOCS\profiles.json` — autoritativo dos devedores
- `PROJETO_PRODAM\SPCF_EXTRACAO\dados\consolidado_faturas.json` — faturas consolidadas

## 🔧 Abrir o banco

Datasette (web):
```
datasette serve "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_ANALISE\prodam.db" --open
```

Beekeeper Studio: File → Open → escolher prodam.db acima.

DuckDB (SQL no terminal):
```
duckdb -c "SELECT * FROM spcf_faturas WHERE cliente = 'SEDUC' LIMIT 10" "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_ANALISE\prodam.db"
```

## 📝 Pendências técnicas (não urgentes)

- Migrar SEDUC_AUDITORIA_COMPLETA de git-backups local pra GitHub privado
- Commitar 277 skills órfãs (se _ARCHIVE for recuperado do _LIXO)
- Adicionar `.gitignore` no SPCF_EXTRACAO pra excluir OCR_JSON_*, por_devedor/, por_formato/
- Commitar `_scripts/baixar_gaps_faturas.js` do SPCF_EXTRACAO
- Investigar discrepância: 81 devedores no DB vs 69 no profiles.json
- Investigar: pendrive_docs tem 3.699 no DB mas memória diz 7.929 classificados
