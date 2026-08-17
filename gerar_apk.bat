@echo off
REM Gera o APK do Fincheck. Usa o toolchain instalado em C:\Users\Usuario\dev.
setlocal
set "ROOT=%~dp0"
set "DEV=C:\Users\Usuario\dev"

set "JAVA_HOME=%DEV%\jdk17"
set "ANDROID_HOME=%DEV%\android-sdk"
set "ANDROID_SDK_ROOT=%ANDROID_HOME%"
set "PATH=%DEV%\flutter\bin;%JAVA_HOME%\bin;%ANDROID_HOME%\platform-tools;%PATH%"

if not exist "%JAVA_HOME%\bin\java.exe"          goto :faltando
if not exist "%DEV%\flutter\bin\flutter.bat"     goto :faltando
if not exist "%ANDROID_HOME%\platform-tools"     goto :faltando

"%ROOT%.venv\Scripts\flet.exe" build apk "%ROOT%meu_app_financeiro" ^
  --project fincheck ^
  --product "Fincheck" ^
  --company "Fincheck" ^
  --org "com.fincheck" ^
  --bundle-id "com.fincheck.app" ^
  --description "Controle de despesas e investimentos" ^
  --copyright "Copyright (c) 2026 Fincheck" ^
  --build-version "1.0.0" ^
  --build-number 1 ^
  --splash-color "#104535" ^
  --splash-dark-color "#104535" ^
  --android-adaptive-icon-background "#104535" ^
  --use-color-emoji

if errorlevel 1 goto :erro
echo.
echo APK gerado em: %ROOT%meu_app_financeiro\build\apk\
pause
exit /b 0

:faltando
echo.
echo Toolchain Android nao encontrado em %DEV%.
echo Esperado: %DEV%\jdk17, %DEV%\flutter e %DEV%\android-sdk
pause
exit /b 1

:erro
echo.
echo A build falhou. Rode com -v no final do comando para ver o detalhe.
pause
exit /b 1
