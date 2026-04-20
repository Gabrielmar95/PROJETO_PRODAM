@echo off
REM SINCRONIZAR.bat — clique duplo para rodar sincronização completa
REM Executa: rebuild DB + auditoria + dossiês + CLAUDE.md + valida skills
cd /d "%~dp0"
py -3.12 scripts\sincronizar_prodam.py %*
pause
