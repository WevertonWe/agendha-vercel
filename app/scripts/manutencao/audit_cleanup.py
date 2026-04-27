import os
import shutil
from pathlib import Path

# Configuração Paths
BASE_DIR = Path.cwd()
TEMP_DIR = BASE_DIR / "temp_downloads"
UPLOADS_DIR = BASE_DIR / "app" / "uploads"
REPORT_FILE = BASE_DIR / "arquivos_temp_para_analise.txt"
VENV_BROKEN = BASE_DIR / "venv_broken"

def audit_temp_files():
    print("--- Iniciando Auditoria de Arquivos Temporários ---")
    
    if not TEMP_DIR.exists():
        print(f"Pasta temporária não encontrada: {TEMP_DIR}")
        return

    # Garantir que uploads existe para comparação
    if not UPLOADS_DIR.exists():
        print(f"Pasta de Uploads não encontrada: {UPLOADS_DIR}. Criando...")
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    files_to_review = []
    
    # Iterar sobre arquivos na pasta temp
    for item in TEMP_DIR.iterdir():
        if item.is_file():
            # Check ID: Verifica se existe arquivo com mesmo nome em uploads
            target_file = UPLOADS_DIR / item.name
            
            if target_file.exists():
                try:
                    os.remove(item)
                    print(f"[REMOVIDO] Duplicata encontrada: {item.name}")
                except Exception as e:
                    print(f"[ERRO] Falha ao remover {item.name}: {e}")
            else:
                print(f"[MANTER] Arquivo único: {item.name}")
                files_to_review.append(item.name)
    
    # Gerar Relatório
    if files_to_review:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write("--- Arquivos Temp Únicos (Não apagar antes de analisar) ---\n")
            for fname in files_to_review:
                f.write(f"{fname}\n")
        print(f"[RELATÓRIO] Lista salva em: {REPORT_FILE}")
    else:
        print("[LIMPEZA] Todos os arquivos eram duplicatas ou a pasta estava vazia.")

    # Remover pasta se estiver vazia? O usuário disse "Não apague a pasta temp... cegamente".
    # Mas se só sobraram duplicatas apagadas, ela fica vazia. Vou manter a pasta por segurança.

def cleanup_broken_venv():
    print("\n--- Limpeza de Diretórios ---")
    if VENV_BROKEN.exists():
        try:
            # shutil.rmtree é necessário para pastas não vazias
            shutil.rmtree(VENV_BROKEN)
            print(f"[SUCESSO] Pasta '{VENV_BROKEN.name}' removida completamente.")
        except Exception as e:
            print(f"[ERRO] Falha ao remover {VENV_BROKEN.name}: {e}")
    else:
        print(f"Pasta '{VENV_BROKEN.name}' não existe.")

if __name__ == "__main__":
    audit_temp_files()
    cleanup_broken_venv()
