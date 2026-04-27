import os
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path.cwd()
APP_DIR = BASE_DIR / "app"
SCRIPTS_PKG = APP_DIR / "scripts"
UPLOADS_DIR = APP_DIR / "uploads" # Confirmed existing path
TEMP_DIR = BASE_DIR / "temp_downloads"
REPORT_FILE = BASE_DIR / "arquivos_temp_para_analise.txt"

# Mapping for remaining scripts
# The user specified where each should go.
# Source could be Root, App, or App/Scripts (if I missed them, though list_dir showed empty)
MOVES_MAP = {
    "migracoes": [
        "corrigir_municipios.py",
        "importar_do_drive.py",
        "migracao.py",
        "migrar_dados.py",
        "migrar_mapa.py",
        "migrar_planilha.py",
        "seed_financeiro.py", # moved here as per instructions (or banco_de_dados) - User said "migracoes ou banco", I'll put in migracoes as it seems like one-off seed
        "semear_eventos.py"
    ],
    "banco_de_dados": [
        "create_finance_tables.py",
        "criar_banco.py",
        "criar_fila_validacao.py"
    ],
    "manutencao": [
        "limpar_dados_db.py",
        "scan_requirements.py", # Manually created before
        "organize_scripts.py",
        "audit_cleanup.py",
        "final_cleanup.py" # Self move
    ]
}

def rescue_data():
    print("--- 1. Resgate de Dados ---")
    if TEMP_DIR.exists():
        files = list(TEMP_DIR.glob("*.pdf"))
        print(f"Encontrados {len(files)} PDFs para resgate.")
        count = 0
        for f in files:
            target = UPLOADS_DIR / f.name
            try:
                shutil.move(str(f), str(target))
                count += 1
            except Exception as e:
                print(f"[ERRO] Falha ao mover {f.name}: {e}")
        print(f"Resgatados {count} arquivos para {UPLOADS_DIR}")
        
        # Cleanup temp
        try:
            shutil.rmtree(TEMP_DIR)
            print("Pasta temp_downloads removida.")
        except Exception as e:
            print(f"Erro ao remover temp_downloads: {e}")
            
    if REPORT_FILE.exists():
        try:
            os.remove(REPORT_FILE)
            print("Relatório temporário removido.")
        except:  # noqa: E722
            pass

def move_remaining_scripts():
    print("\n--- 2. Limpeza Final de Scripts ---")
    # Search locations: Root, App, App/Scripts (if any)
    search_dirs = [BASE_DIR, APP_DIR, SCRIPTS_PKG]
    
    for subfolder, filenames in MOVES_MAP.items():
        destination = SCRIPTS_PKG / subfolder
        if not destination.exists():
            destination.mkdir(parents=True)
            (destination/"__init__.py").touch()
            
        for fname in filenames:
            found = False
            for src_dir in search_dirs:
                src_file = src_dir / fname
                if src_file.exists():
                    try:
                        shutil.move(str(src_file), str(destination / fname))
                        print(f"[MOVIDO] {fname} -> app/scripts/{subfolder}")
                        found = True
                        break
                    except Exception as e:
                        print(f"[ERRO] Falha ao mover {fname}: {e}")
            
            if not found and fname != "final_cleanup.py":
                 print(f"[AVISO] {fname} não encontrado em lugar nenhum.")

if __name__ == "__main__":
    rescue_data()
    move_remaining_scripts()
