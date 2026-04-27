import os
import hashlib
import sqlite3
import argparse
import sys

# Setup Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # app/
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "agendha.db")
TARGET_DIR = os.path.join(BASE_DIR, "uploads", "beneficiarios_docs") # d:\Cursos\agendha\app\uploads\beneficiarios_docs

def get_file_hash(filepath):
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def get_active_documents(db_path):
    """Get set of active document paths from DB."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT doc_status FROM beneficiarios WHERE doc_status LIKE 'uploads/beneficiarios_docs/%'")
    rows = cursor.fetchall()
    conn.close()
    
    # Extract filename only for comparison, assuming flat directory in target
    # doc_status example: "uploads/beneficiarios_docs/uuid_file.pdf"
    active_files = set()
    for row in rows:
        if row[0]:
            active_files.add(os.path.basename(row[0]))
    return active_files

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def main():
    parser = argparse.ArgumentParser(description="Deduplicate files in uploads folder.")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be deleted without deleting.")
    args = parser.parse_args()

    if not os.path.exists(TARGET_DIR):
        print(f"Directory not found: {TARGET_DIR}")
        sys.exit(1)

    print(f"Scanning directory: {TARGET_DIR}")
    print(f"Database: {DB_PATH}")
    
    active_docs = get_active_documents(DB_PATH)
    print(f"Active documents in DB: {len(active_docs)}")

    files_by_hash = {}
    
    # 1. Scan and Hash
    all_files = [f for f in os.listdir(TARGET_DIR) if os.path.isfile(os.path.join(TARGET_DIR, f))]
    print(f"Total files found: {len(all_files)}")
    
    for filename in all_files:
        filepath = os.path.join(TARGET_DIR, filename)
        file_hash = get_file_hash(filepath)
        
        if file_hash not in files_by_hash:
            files_by_hash[file_hash] = []
        files_by_hash[file_hash].append(filename)

    # 2. Analyze Duplicates
    duplicates_found = 0
    bytes_saved = 0
    to_delete = []

    for file_hash, filenames in files_by_hash.items():
        if len(filenames) > 1:
            duplicates_found += 1
            # Sort by modification time (oldest first) just in case
            # But primary criteria is DB Active
            
            # Identify which ones are active
            active_in_group = [f for f in filenames if f in active_docs]
            
            keepers = []
            candidates = []
            
            if active_in_group:
                # If some are active, keep ALL active ones (edge case: multiple users pointing to diff copies of same file? no, logic says keep active)
                # If multiple are active, we must keep all active ones to not break links
                keepers.extend(active_in_group)
                # The rest are undefined junk
                candidates = [f for f in filenames if f not in active_docs]
            else:
                # None are active. All are orphans.
                # Keep the most recent one? Or oldest?
                # Let's keep the most recently created/modified as "survivor"
                # Sort by mtime descending
                filenames.sort(key=lambda x: os.path.getmtime(os.path.join(TARGET_DIR, x)), reverse=True)
                keepers.append(filenames[0])
                candidates = filenames[1:]
            
            for c in candidates:
                fullpath = os.path.join(TARGET_DIR, c)
                size = os.path.getsize(fullpath)
                to_delete.append((c, size))
                bytes_saved += size

    # 3. Report & Action
    print("\nAnalysis Complete.")
    print(f"Duplicate Groups: {duplicates_found}")
    print(f"Files to Delete: {len(to_delete)}")  # nosec
    print(f"Potential Space Reclaimed: {format_size(bytes_saved)}")
    
    if len(to_delete) > 0:
        print("\n--- Deletion Candidates ---")
        for fname, size in to_delete:
            status = "(Orphan)"
            if fname in active_docs:
                status = "(ACTIVE - WARNING)" # Should not happen via logic above
            print(f"[DELETE] {fname} ({format_size(size)}) {status}")  # nosec

        if args.dry_run:
            print("\n[DRY RUN] No files were deleted.")
        else:
            print("\nDeleting files...")
            for fname, _ in to_delete:
                try:
                    os.remove(os.path.join(TARGET_DIR, fname))
                    print(f"Deleted: {fname}")  # nosec
                except Exception as e:
                    print(f"Error deleting {fname}: {e}")
            print("Cleanup finished.")
    else:
        print("\nNo duplicates to delete.")

if __name__ == "__main__":
    main()
