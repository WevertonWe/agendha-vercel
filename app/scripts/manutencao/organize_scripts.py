import shutil
from pathlib import Path

BASE_DIR = Path.cwd()
SCRIPTS_DIR = BASE_DIR / "app" / "scripts"

# Mapa de Categorias
STRUCTURE = {
    "banco_de_dados": [
        "create_logs_table.py",
        "create_map_color_column.py",
        "create_map_table.py",
        "create_pedreiros_table.py",
        "update_map_schema.py",
    ],
    "migracoes": [
        # Adicionar se houver scripts de importação futuros
    ],
    "debug_testes": [
        "debug_db.py",
        "debug_pedreiros.py",
        "test_pedreiros_backend.py",
        "verify_app.py"
    ],
    "manutencao": [
        "iniciar_sistema.bat",
        "cleanup.py", 
        "audit_cleanup.py",
        "organize_scripts.py" # Self move at the end? careful. Let's move others.
    ]
}

def organize_scripts():
    print(f"Organizando scripts em: {SCRIPTS_DIR}")
    
    if not SCRIPTS_DIR.exists():
        print("Pasta app/scripts não encontrada.")
        return

    # 1. Criar Subpastas e Init
    for folder in STRUCTURE.keys():
        target_dir = SCRIPTS_DIR / folder
        if not target_dir.exists():
            target_dir.mkdir(parents=True)
            print(f"Criada pasta: {folder}")
        
        # Init
        (target_dir / "__init__.py").touch()
    
    # 2. Mover Arquivos
    # Procura tanto na raiz quanto em app/scripts para garantir
    search_dirs = [BASE_DIR, SCRIPTS_DIR]
    
    for folder, files in STRUCTURE.items():
        target_dir = SCRIPTS_DIR / folder
        
        for filename in files:
            moved = False
            for src_dir in search_dirs:
                src_file = src_dir / filename
                if src_file.exists():
                     try:
                        shutil.move(str(src_file), str(target_dir / filename))
                        print(f"[OK] {filename} -> {folder}/")
                        moved = True
                        break # Parar de procurar se já moveu
                     except Exception as e:
                         print(f"[ERRO] Falha ao mover {filename}: {e}")
            
            if not moved:
                 # Debug: Check if file exists in target already?
                 if (target_dir / filename).exists():
                     print(f"[INFO] {filename} já está em {folder}/")
                 elif filename not in ["cleanup.py", "audit_cleanup.py"]: # Ignore temp scripts
                     print(f"[AVISO] {filename} não encontrado para mover.")

if __name__ == "__main__":
    organize_scripts()
