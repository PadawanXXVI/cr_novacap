@echo off
setlocal

:: Vai até a pasta do sistema
cd /d %~dp0

echo ============================================
echo  INICIANDO O SISTEMA CR-NOVACAP
echo ============================================

:: Instala/atualiza dependências
echo Instalando dependências...
pip install --upgrade pip
pip install -r requirements.txt

:: Inicia o sistema Flask
echo.
echo Iniciando aplicação...
python run.py

echo.
echo ============================================
echo SISTEMA FINALIZADO (verifique mensagens acima)
pause
