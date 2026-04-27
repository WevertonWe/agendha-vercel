import sys
import os

# Adiciona o diretório atual ao path para simular a execução da raiz do projeto
sys.path.append(os.getcwd())

try:
    print("Tentando importar app.main...")
    print("Importação de app.main BEM SUCEDIDA!")
except Exception as e:
    print(f"FALHA na importação: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
