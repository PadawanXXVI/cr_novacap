@echo off
setlocal enabledelayedexpansion

:: ======================================================
:: 🚀 INICIAR SISTEMA CR-NOVACAP (Flask + MySQL Remoto)
:: ======================================================
:: Banco central: 10.115.14.61
:: Cada usuário roda o sistema localmente e acessa pelo
:: IP da própria máquina (ex: http://10.115.14.22:5000)
:: ======================================================

cls
cd /d %~dp0

echo =====================================================
echo      INICIANDO O SISTEMA CR DA NOVACAP
echo =====================================================
echo.

:: -------------------------------------------------------
:: 🔍 1. Obter IP local da máquina
:: -------------------------------------------------------
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set IP_LOCAL=%%a
)
set IP_LOCAL=%IP_LOCAL: =%

echo IP da maquina atual: %IP_LOCAL%
echo.

:: -------------------------------------------------------
:: 🔍 2. Testar conexão com o banco remoto
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
    exit /b 1
)

echo Banco acessivel.
echo.

:: -------------------------------------------------------
:: 📦 3. Instalar/atualizar dependências
:: -------------------------------------------------------
echo Verificando dependencias Python...
pip install --disable-pip-version-check --quiet -r requirements.txt

if errorlevel 1 (
    echo [AVISO] Houve um problema ao instalar dependencias.
    echo Continuando mesmo assim...
) else (
    echo Dependencias OK.
)
echo.

:: -------------------------------------------------------
:: ▶️ 4. Iniciar o sistema (acessível pela rede)
:: -------------------------------------------------------
echo Iniciando servidor Flask na rede local...
echo.
echo =====================================================
echo  SISTEMA CR-NOVACAP INICIADO COM SUCESSO!
echo =====================================================
echo.
echo Acesse pelo navegador utilizando:
echo.
echo     http://%IP_LOCAL%:5000
echo.
echo Ou localmente nesta maquina:
echo     http://127.0.0.1:5000
echo.
echo (Mantenha esta janela aberta enquanto o sistema estiver em uso.)
echo =====================================================
echo.

:: =========================================================
:: Inicia o Flask escutando em toda a rede (0.0.0.0)
:: =========================================================

:: Tenta primeiro com "flask run" (forma recomendada)
flask run --host=0.0.0.0 --port=5000

:: Se o comando acima falhar, tenta a forma alternativa:
if errorlevel 1 (
    echo.
    echo [AVISO] "flask run" nao funcionou. Tentando com python...
    echo.
    python -m flask run --host=0.0.0.0 --port=5000
)

:: Se ainda assim não funcionar, tenta rodar diretamente o run.py
if errorlevel 1 (
    echo.
    echo [AVISO] Tentando executar diretamente pelo run.py...
    python run.py
)

echo.
echo =====================================================
echo  SISTEMA FINALIZADO
echo =====================================================
pause