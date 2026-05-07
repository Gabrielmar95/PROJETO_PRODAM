---
description: Roda sincronização completa do Projeto PRODAM (rebuild DB + auditoria + dossiês + skills)
---

Execute o comando mestre de sincronização do Projeto PRODAM.

Rode no PowerShell:

```powershell
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"
py -3.12 scripts\sincronizar_prodam.py $ARGUMENTS
```

Flags disponíveis (passe como $ARGUMENTS):
- Sem flags: tudo (rebuild DB + auditoria + dossiês + CLAUDE.md + skills)
- `--so-db`: só rebuild prodam.db
- `--so-audit`: só auditoria de completude
- `--so-dossie`: só dossiês multi-formato
- `--pular-dossie`: tudo exceto dossiês (mais rápido)
- `--devedor "SIGLA"`: dossiê só de um devedor (ex: "SES/SUSAM")

Ao final, reporte de forma concisa:
1. Etapas que rodaram com sucesso (db, audit, dossie, claude)
2. Score médio de completude dos devedores
3. Quantidade de gaps documentais e divergências
4. Skills com paths desatualizados (se houver)
5. Caminho dos arquivos principais gerados
