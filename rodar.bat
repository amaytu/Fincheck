@echo off
REM Abre o Meu App Financeiro. Cria o ambiente virtual na primeira execucao.
setlocal
set "ROOT=%~dp0"
set "VENV=%ROOT%.venv\Scripts\python.exe"

if not exist "%VENV%" (
    echo Criando ambiente virtual...
    py -m venv "%ROOT%.venv" || goto :erro
    "%VENV%" -m pip install --upgrade pip || goto :erro
    "%VENV%" -m pip install -r "%ROOT%meu_app_financeiro\requirements.txt" || goto :erro
)

"%VENV%" "%ROOT%meu_app_financeiro\main.py"
exit /b 0

:erro
echo.
echo Falhou. Confira se o Python esta instalado rodando:  py --version
pause
exit /b 1
