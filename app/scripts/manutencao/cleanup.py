import shutil
from pathlib import Path

# Configuração
BASE_DIR = Path.cwd()
APP_DIR = BASE_DIR / "app"
SCRIPTS_DIR = APP_DIR / "scripts"
SENSITIVE_DIR = APP_DIR / "dados_sensiveis"
BACKUPS_DIR = BASE_DIR / "backups"

FILES_TO_MOVE = [
    "create_logs_table.py",
    "create_map_color_column.py",
    "create_map_table.py",
    "create_pedreiros_table.py",
    "debug_db.py",
    "debug_pedreiros.py",
    "test_pedreiros_backend.py",
    "update_map_schema.py",
    "verify_app.py",
    "iniciar_sistema.bat"
]

def ensure_dir(directory):
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Diretório criado: {directory}")
    else:
        print(f"Diretório já existe: {directory}")

def create_init(directory):
    init_file = directory / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print(f"Arquivo criado: {init_file}")

def move_files():
    print(f"Iniciando organização em: {BASE_DIR}")
    
    # 1. Garantir pastas destino
    ensure_dir(SCRIPTS_DIR)
    create_init(SCRIPTS_DIR)
    
    # 2. Mover arquivos de script
    moved_count = 0
    for filename in FILES_TO_MOVE:
        # Tenta achar na raiz do projeto
        src = BASE_DIR / filename
        # Tenta achar na raiz do app (caso o usuário tenha se enganado ou movido parcialmente)
        src_app = APP_DIR / filename
        
        target = SCRIPTS_DIR / filename
        
        if src.exists():
            try:
                shutil.move(str(src), str(target))
                print(f"[OK] Movido: {filename} -> app/scripts/")
                moved_count += 1
            except Exception as e:
                print(f"[ERRO] Falha ao mover {filename}: {e}")
        elif src_app.exists():
             try:
                shutil.move(str(src_app), str(target))
                print(f"[OK] Movido (de app/): {filename} -> app/scripts/")
                moved_count += 1
             except Exception as e:
                print(f"[ERRO] Falha ao mover {filename} de app/: {e}")
        else:
            print(f"[INFO] Arquivo não encontrado na raiz nem em app/: {filename}")

    # 3. Mover pasta backups
    if BACKUPS_DIR.exists():
        ensure_dir(SENSITIVE_DIR)
        target_backups = SENSITIVE_DIR / "backups"
        try:
            if target_backups.exists():
                 print(f"[INFO] Pasta backups já existe em {target_backups}. Mesclando/Movendo conteúdo...")
                 # Se já existe, move o conteúdo para não sobrescrever a pasta e dar erro
                 for item in BACKUPS_DIR.iterdir():
                     shutil.move(str(item), str(target_backups / item.name))
                 # Remove a pasta vazia original
                 BACKUPS_DIR.rmdir() 
            else:
                shutil.move(str(BACKUPS_DIR), str(target_backups))
            print("[OK] Pasta 'backups' movida para app/dados_sensiveis/")
        except Exception as e:
            print(f"[ERRO] Falha ao mover pasta backups: {e}")
    else:
        print("[INFO] Pasta 'backups' não encontrada na raiz.")

    print("--- Fim da Execução ---")

if __name__ == "__main__":
    move_files()
