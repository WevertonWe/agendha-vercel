@echo off
TITLE Agendha - Gestão de Operações Local
cls

:: Adiciona os DLLs do QGIS ao PATH para resolver a DLL do _sqlite3
set "PATH=C:\Program Files\QGIS 3.44.12\bin;%PATH%"

set "PYTHON_CMD="

:: 1. Tenta comando python global
where python >nul 2>nul
if %errorlevel%==0 set "PYTHON_CMD=python"

:: 2. Tenta launcher py
if not defined PYTHON_CMD (
    where py >nul 2>nul
    if %errorlevel%==0 set "PYTHON_CMD=py"
)

:: 3. Tenta caminhos conhecidos no Windows (ex: QGIS, AppData, C:\Python)
if not defined PYTHON_CMD (
    if exist "C:\Program Files\QGIS 3.44.12\apps\Python312\python.exe" (
        set "PYTHON_CMD=C:\Program Files\QGIS 3.44.12\apps\Python312\python.exe"
    )
)

if not defined PYTHON_CMD (
    for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%D\python.exe" set "PYTHON_CMD=%%D\python.exe"
    )
)

if not defined PYTHON_CMD (
    for /d %%D in ("C:\Python*") do (
        if exist "%%D\python.exe" set "PYTHON_CMD=%%D\python.exe"
    )
)

if not defined PYTHON_CMD (
    echo ==================================================
    echo [ERRO] Python nao encontrado no PATH do Windows.
    echo Baixe/instale o Python em https://www.python.org
    echo ou marque a opcao "Add Python to PATH" durante a instalacao.
    echo ==================================================
    pause
    exit /b 1
)

echo Python encontrado: "%PYTHON_CMD%"

if not exist .env (
    if exist .env.example (
        echo Criando arquivo .env a partir de .env.example...
        copy .env.example .env >nul
    )
)

echo [1/2] Verificando Ambiente Virtual (venv)...
if not exist venv (
    echo Criando ambiente virtual Python...
    "%PYTHON_CMD%" -m venv venv
)
call venv\Scripts\activate.bat

echo Garantindo todas as dependencias do projeto (requirements.txt)...
python -m pip install -r requirements.txt --quiet

echo.
echo [2/2] Iniciando Servidor Agendha...
echo --------------------------------------------------
echo Acesse no navegador: http://localhost:8000
echo --------------------------------------------------
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause