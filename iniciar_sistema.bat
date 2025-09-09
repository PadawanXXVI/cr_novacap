@echo off
setlocal

:: ================================================
:: INICIAR SISTEMA CR-NOVACAP (Flask + MySQL)
:: Dependências devem estar instaladas via pip global
:: Banco de dados: 10.233.208.22 (NOVACAPSV022)
:: ================================================

cd /d %~dp0

echo ============================================
echo  INICIANDO O SISTEMA CR-NOVACAP
echo ============================================

echo Instalando dependências...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Iniciando aplicação...
python run.py

echo.
echo ============================================
echo SISTEMA FINALIZADO (verifique mensagens acima)
pause
