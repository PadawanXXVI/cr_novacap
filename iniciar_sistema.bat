@echo off
setlocal enabledelayedexpansion

:: ======================================================
:: 🚀 INICIAR SISTEMA CR-NOVACAP (Flask + MySQL Remoto)
:: ======================================================
:: Banco central: 10.115.14.61
:: Cada usuário roda o sistema localmente e acessa pelo
:: IP da própria máquina (exemplo: http://10.115.14.22:5000)
:: ======================================================

cls
cd /d %~dp0

echo =====================================================
echo      INICIANDO O SISTEMA CR DA NOVACAP
echo =====================================================

:: -------------------------------------------------------
:: 🔍 1. Obter IP local da máquina onde o usuário está rodando
:: -------------------------------------------------------
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set IP_LOCAL=%%a
)
set IP_LOCAL=%IP_LOCAL: =%

echo IP da maquina atual: %IP_LOCAL%
echo.

:: -------------------------------------------------------
:: 🔍 2. Testar conexão com o banco remoto (10.115.14.61)
:: -------------------------------------------------------
set DB_HOST=10.115.14.61
echo Verificando acesso ao banco de dados em %DB_HOST% ...
ping -n 1 %DB_HOST% >nul

if errorlevel 1 (
    echo.
    echo [ERRO] Nao foi possivel conectar ao banco de dados: %DB_HOST%
    echo Verifique se o servidor do banco esta ligado e na rede.
    echo.
    pause
    exit /b
)

echo Banco acessivel
echo.

:: -------------------------------------------------------
:: 📦 3. Instalar/atualizar dependências se necessário
:: -------------------------------------------------------
echo Verificando dependencias Python...
pip install --disable-pip-version-check -r requirements.txt >nul

echo Dependencias OK
echo.

:: -------------------------------------------------------
:: ▶️ 4. Iniciar o sistema
:: -------------------------------------------------------
echo Iniciando servidor Flask...
python run.py

echo.
echo =====================================================
echo  SISTEMA CR-NOVACAP INICIADO COM SUCESSO!
echo =====================================================
echo.
echo Acesse pelo navegador utilizando:
echo.
echo     http://%IP_LOCAL%:5000
echo.
echo Ou localmente:
echo.
echo     http://127.0.0.1:5000
echo.
echo (Mantenha esta janela aberta enquanto o sistema estiver em uso.)
echo =====================================================
echo.

pause
