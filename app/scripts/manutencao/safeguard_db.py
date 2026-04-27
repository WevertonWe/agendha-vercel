import os
import shutil
from datetime import datetime

# Caminhos
# Caminhos relativos a partir da raiz (assumindo execução da raiz ou ajustando paths)
# Mas como o script mudou de lugar, melhor usar caminhos absolutos baseados no arquivo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

raiz_db = os.path.join(BASE_DIR, "agendha.db")
fantasma_db = os.path.join(BASE_DIR, "app/agendha.db")
backup_dir = os.path.join(BASE_DIR, "backups_emergencia")

def realizar_backup_seguro():
    if os.path.exists(fantasma_db):
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{backup_dir}/agendha_fantasma_BAK_{timestamp}.db"
        
        # Copia em vez de mover (Segurança dupla)
        shutil.copy2(fantasma_db, backup_path)
        print(f"✅ Backup do banco fantasma criado em: {backup_path}")
        
        # Renomeia o original para 'quarentena' em vez de deletar
        os.rename(fantasma_db, f"{fantasma_db}.quarentena")
        print("⚠️ Banco antigo movido para quarentena (app/agendha.db.quarentena)")
    else:
        print("ℹ️ Nenhum banco fantasma encontrado em /app. Sistema limpo!")

if __name__ == "__main__":
    realizar_backup_seguro()
