import shutil
import os
from datetime import datetime
from app.config import settings

def realizar_backup_agora():
    """
    Realiza o backup do banco de dados SQLite imediatamente.
    """
    # Define a pasta de destino
    backup_dir = settings.BASE_DIR.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    # Gera o nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"agendha_backup_{timestamp}.db"
    destination = backup_dir / backup_filename

    # Copia o banco de dados
    try:
        shutil.copy2(settings.DB_PATH, destination)
    except Exception as e:
        print(f"Erro ao realizar backup: {e}")
        return None

    # Limpeza: Manter apenas os últimos 5 backups
    try:
        backups = sorted(backup_dir.glob("agendha_backup_*.db"), key=os.path.getmtime)
        limit = 5
        if len(backups) > limit:
            backups_to_remove = backups[:-limit]
            for backup_to_delete in backups_to_remove:
                os.remove(backup_to_delete)
            print(f"Limpeza de backup: {len(backups_to_remove)} arquivos antigos removidos.")
    except Exception as e:
        print(f"Erro ao limpar backups antigos: {e}")

    return backup_filename
