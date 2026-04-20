# Como Integrar o `sincronizar_prodam.py` ao Seu Fluxo

**TL;DR:** você tem 4 opções — escolha uma (ou várias).

---

## OPÇÃO 1 — Clicar e rodar (mais simples)

Já criei `SINCRONIZAR.bat` na raiz do projeto. **Clique duplo** no arquivo e pronto.

```
C:\Users\gabri\Desktop\PROJETO_PRODAM\SINCRONIZAR.bat
```

Para rodar só parte:
- `SINCRONIZAR.bat --so-db`
- `SINCRONIZAR.bat --so-audit`
- `SINCRONIZAR.bat --so-dossie`
- `SINCRONIZAR.bat --devedor "SES/SUSAM"`

Cria também um atalho no Desktop (manual): botão direito no `SINCRONIZAR.bat` → **Criar atalho** → arrastar para Desktop.

---

## OPÇÃO 2 — Slash Command no Claude Code (`/sincronizar-prodam`)

Quando você digita `/sincronizar-prodam` dentro do Claude Code, ele executa automaticamente.

**Precisa criar manualmente** (o Claude Code em dont-ask mode não cria pastas ocultas):

### Passo 1 — Crie a pasta
Abra o PowerShell (⊞+R → `powershell`) e rode:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\commands"
```

### Passo 2 — Crie o arquivo do comando

```powershell
@'
---
description: Roda sincronizacao completa do Projeto PRODAM
---

Execute o comando mestre de sincronizacao do Projeto PRODAM:

```bash
cd "C:\Users\gabri\Desktop\PROJETO_PRODAM"
py -3.12 sincronizar_prodam.py $ARGUMENTS
```

Flags disponiveis:
- Sem flags: roda tudo
- `--so-db`, `--so-audit`, `--so-dossie`
- `--pular-dossie`: tudo exceto dossies (rapido)
- `--devedor "SIGLA"`: dossie de um devedor

Ao final reporte: etapas OK, score medio, gaps, divergencias.
'@ | Out-File -FilePath "$env:USERPROFILE\.claude\commands\sincronizar-prodam.md" -Encoding utf8
```

Depois disso, em qualquer sessão do Claude Code você pode digitar:
```
/sincronizar-prodam
/sincronizar-prodam --devedor "SES/SUSAM"
/sincronizar-prodam --so-audit
```

### Versão projeto-local (compartilhável via git)

Se quiser que outros que clonem o repositório tenham o mesmo comando, crie em
`.claude/commands/` dentro do projeto (também requer PowerShell manual):

```powershell
New-Item -ItemType Directory -Force -Path "C:\Users\gabri\Desktop\PROJETO_PRODAM\.claude\commands"
# repetir o bloco do arquivo com o mesmo conteúdo, mas salvando em
# "C:\Users\gabri\Desktop\PROJETO_PRODAM\.claude\commands\sincronizar-prodam.md"
```

---

## OPÇÃO 3 — Skill (para Claude invocar automaticamente quando você pede)

Já criei 2 skills em `PRODAM_DOCS/_SKILLS/`:

- `pipeline-devedor-completo_SKILL.md` — workflow 7 etapas por devedor
- `auditoria-completude-devedor_SKILL.md` — gap finder

**Para o Claude reconhecê-las automaticamente**, elas precisam estar em
`C:\Users\gabri\.claude\skills\<nome-da-skill>\SKILL.md`.

Migração (rode no PowerShell uma vez):

```powershell
$src = "C:\Users\gabri\Desktop\PROJETO_PRODAM\PRODAM_DOCS\_SKILLS"
$dst = "$env:USERPROFILE\.claude\skills"

# pipeline-devedor-completo
New-Item -ItemType Directory -Force -Path "$dst\pipeline-devedor-completo"
Copy-Item "$src\pipeline-devedor-completo_SKILL.md" "$dst\pipeline-devedor-completo\SKILL.md"

# auditoria-completude-devedor
New-Item -ItemType Directory -Force -Path "$dst\auditoria-completude-devedor"
Copy-Item "$src\auditoria-completude-devedor_SKILL.md" "$dst\auditoria-completude-devedor\SKILL.md"
```

Depois disso, ao dizer "gera pipeline completo do DETRAN" ou "audita completude do SES",
o Claude invoca essas skills automaticamente.

---

## OPÇÃO 4 — Agendamento automático (cron / Windows Task Scheduler)

### 4a. Via Claude Code schedule (remoto)
Se você usa o Claude Code com agendamento remoto, crie um trigger:

```
/schedule cria um trigger que rode /sincronizar-prodam todos os dias às 07:00
```

### 4b. Via Windows Task Scheduler (local)
No PowerShell (admin):

```powershell
$action = New-ScheduledTaskAction -Execute "py" -Argument "-3.12 sincronizar_prodam.py --pular-dossie" -WorkingDirectory "C:\Users\gabri\Desktop\PROJETO_PRODAM"
$trigger = New-ScheduledTaskTrigger -Daily -At 7am
Register-ScheduledTask -TaskName "PRODAM_Sync_Diario" -Action $action -Trigger $trigger -Description "Sincronizacao diaria do projeto PRODAM"
```

Para rodar toda segunda-feira de manhã:
```powershell
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7am
```

---

## Como eu faria

1. **Hoje/agora:** use `SINCRONIZAR.bat` — já funciona (OPÇÃO 1)
2. **Esta semana:** rode os 2 blocos PowerShell da OPÇÃO 2 e OPÇÃO 3 para ter `/sincronizar-prodam` e as skills ativas
3. **Depois que estabilizar:** agende diário com Task Scheduler (OPÇÃO 4b) para manter tudo fresco automaticamente

---

## Arquivos criados nesta entrega

| Arquivo | Localização | Para que serve |
|---------|-------------|----------------|
| `sincronizar_prodam.py` | raiz do projeto | comando mestre |
| `auditoria_completude_devedor.py` | raiz do projeto | gaps + divergências |
| `dossie_multiformato_devedor.py` | raiz do projeto | dossiês multi-formato |
| `SINCRONIZAR.bat` | raiz do projeto | clique duplo roda tudo |
| `pipeline-devedor-completo_SKILL.md` | `PRODAM_DOCS/_SKILLS/` | skill workflow |
| `auditoria-completude-devedor_SKILL.md` | `PRODAM_DOCS/_SKILLS/` | skill auditoria |
| `COMO_INTEGRAR.md` | raiz do projeto | este arquivo |
