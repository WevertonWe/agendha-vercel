import sqlite3
import shutil
import os

# Define locations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # app/
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "agendha.db") # root/agendha.db
UPLOADS_ROOT = os.path.join(BASE_DIR, "static", "uploads") # Wait, static/uploads or app/uploads?
# Config.py said: UPLOAD_FOLDER: Path = APP_DIR / "uploads" -> app/uploads
# But file lists showed app/uploads...
# Let's verify BASE_DIR/app/uploads

PROJECT_ROOT = os.path.dirname(BASE_DIR)
APP_UPLOADS = os.path.join(BASE_DIR, "uploads")
TARGET_DIR = os.path.join(APP_UPLOADS, "beneficiarios_docs")

print(f"DB Path: {DB_PATH}")
print(f"Uploads Root: {APP_UPLOADS}")
print(f"Target Dir: {TARGET_DIR}")

def migrate():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"Created target directory: {TARGET_DIR}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Find legacy records
    cursor.execute("SELECT id, doc_status FROM beneficiarios WHERE doc_status LIKE 'uploads/%' AND doc_status NOT LIKE 'uploads/beneficiarios_docs/%'")
    records = cursor.fetchall()
    
    print(f"Found {len(records)} records to migrate.")
    
    moved_count = 0
    updated_count = 0
    
    for ben_id, old_path in records:
        # old_path looks like "uploads/filename.pdf"
        filename = os.path.basename(old_path)
        
        # Physical paths
        src_file = os.path.join(PROJECT_ROOT, "app", old_path) # d:\Cursos\agendha\app\uploads\file.pdf
        dst_file = os.path.join(TARGET_DIR, filename)
        
        # New DB Path
        new_db_path = f"uploads/beneficiarios_docs/{filename}"
        
        file_moved = False
        
        if os.path.exists(src_file):
            shutil.move(src_file, dst_file)
            file_moved = True
        elif os.path.exists(dst_file):
             # Already moved, just update DB
             file_moved = True
             print(f"File {filename} already in target.")
        else:
            print(f"WARNING: File missing for ID {ben_id}: {src_file}")
            # We assume we update DB anyway? Or keep it broken?
            # Better to update if we want consistency, but maybe flag it? 
            # Let's Skip update if file missing to avoid pointing to empty space?
            # User said "Mova todos os arquivos PDF... Execute script para atualizar".
            # If file is gone, maybe we shouldn't touch valid legacy path?
            # But legacy path is also broken if file missing.
            # Let's skip update for missing files to be safe.
            continue
            
        if file_moved:
            cursor.execute("UPDATE beneficiarios SET doc_status = ? WHERE id = ?", (new_db_path, ben_id))
            updated_count += 1
            moved_count += 1

    conn.commit()
    conn.close()
    print(f"Migration Complete. Moved: {moved_count}, Updated DB: {updated_count}")  # nosec

if __name__ == "__main__":
    migrate()
