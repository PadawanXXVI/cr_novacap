@echo off
setlocal enabledelayedexpansion

:: ================================================
:: INICIAR SISTEMA CR-NOVACAP (Flask + MySQL)
:: ================================================
:: Banco de dados remoto: 10.115.14.84 (máquina local com banco)
:: O servidor MySQL precisa estar acessível antes de iniciar
:: ================================================

cd /d %~dp0

echo ============================================
echo  INICIANDO O SISTEMA CR-NOVACAP
echo ============================================

:: Verificando conectividade com o banco de dados
set DB_HOST=10.115.14.84
echo Verificando conexão com o banco de dados em %DB_HOST% ...
ping -n 2 %DB_HOST% >nul
if errorlevel 1 (
    echo.
    echo [ERRO] Banco de dados inacessível: %DB_HOST%
    echo Verifique se a máquina do banco está ligada e conectada à rede.
    echo.
    echo ============================================
    echo ENCERRANDO O SISTEMA...
    echo ============================================
    pause
    exit /b
)

:: Instala/atualiza dependências globais
echo.
echo Instalando/atualizando dependências do Python...
pip install --upgrade pip
pip install -r requirements.txt

:: Inicia o sistema Flask
echo.
echo Iniciando aplicação Flask...
python run.py

echo.
echo ============================================
echo SISTEMA FINALIZADO (verifique mensagens acima)
echo ============================================
pause
