import shutil
from pathlib import Path

# Config
BASE_DIR = Path.cwd()
ROOT_SCRIPTS = BASE_DIR / "scripts"
APP_SCRIPTS = BASE_DIR / "app" / "scripts"

# Mapeamento (baseado no pedido original)
MOVES = {
    "corrigir_municipios.py": "migracoes",
    "importar_do_drive.py": "migracoes",
    "migracao.py": "migracoes",
    "migrar_dados.py": "migracoes",
    "migrar_mapa.py": "migracoes",
    "migrar_planilha.py": "migracoes",
    "seed_financeiro.py": "migracoes",
    "semear_eventos.py": "migracoes",
    "create_finance_tables.py": "banco_de_dados",
    "criar_banco.py": "banco_de_dados",
    "criar_fila_validacao.py": "banco_de_dados",
    "limpar_dados_db.py": "manutencao"
}

def move_root_scripts():
    print(f"--- Movendo scripts de {ROOT_SCRIPTS} para {APP_SCRIPTS} ---")
    
    if not ROOT_SCRIPTS.exists():
        print("Pasta scripts na raiz não encontrada.")
        return

    # Iterar sobre arquivos na pasta scripts da raiz
    for item in ROOT_SCRIPTS.iterdir():
        if item.is_file():
            # Determinar destino
            subfolder = MOVES.get(item.name, "migracoes") # Default para migracoes se desconhecido
            target_dir = APP_SCRIPTS / subfolder
            
            if not target_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.move(str(item), str(target_dir / item.name))
                print(f"[MOVIDO] {item.name} -> app/scripts/{subfolder}/")
            except Exception as e:
                print(f"[ERRO] Falha ao mover {item.name}: {e}")

    # Remover a pasta se estiver vazia
    try:
        ROOT_SCRIPTS.rmdir()
        print("Pasta raiz 'scripts' removida com sucesso.")
    except Exception as e:
        print(f"Não foi possível remover a pasta 'scripts' (pode não estar vazia): {e}")

if __name__ == "__main__":
    move_root_scripts()
