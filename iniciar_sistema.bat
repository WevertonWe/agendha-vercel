@echo off
TITLE Antigravity - Gestão de Operações
cls

echo [1/3] Ativando Ambiente e Verificando Modulos...
call venv\Scripts\activate
:: Garante que as dependencias essenciais existam
python -m pip install pydantic-settings uvicorn fastapi --quiet

echo [2/3] Iniciando Tunel Ngrok...
:: Abre o ngrok em uma NOVA janela para podermos ver os logs dele separadamente
start ngrok http 8000

echo [3/3] Iniciando Servidor FastAPI...
echo --------------------------------------------------
echo Se o site nao carregar, verifique se ha erros abaixo:
echo --------------------------------------------------
:: Roda o uvicorn nesta janela principal para vermos os erros de Python
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause