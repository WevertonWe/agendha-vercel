import os
import ast
import sys
from pathlib import Path

# Mapa de Imports para Pacotes PyPI (quando o nome difere)
PACKAGE_MAP = {
    "jose": "python-jose",
    "dotenv": "python-dotenv",
    "pdfkit": "pdfkit",
    "reportlab": "reportlab",
    "apscheduler": "APScheduler",
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "bs4": "beautifulsoup4",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "multipart": "python-multipart",
    "dateutil": "python-dateutil"
}

# Lista de libs padrão para ignorar
IGNORE_STDLIB = sys.stdlib_module_names

def get_imports_from_file(filepath):
    imports = set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            root = ast.parse(f.read(), filename=filepath)
        
        for node in ast.walk(root):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    except Exception:
        # Pular arquivos com erro de syntax (comuns em templates mal formatados ou misturas)
        pass
    return imports

def scan_codebase():
    base_dir = Path.cwd() / "app"
    all_imports = set()

    for root, dirs, files in os.walk(base_dir):
        # Ignorar venvs e caches
        if "venv" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                all_imports.update(get_imports_from_file(path))

    # Filtrar
    requirements = set()
    for imp in all_imports:
        if imp in IGNORE_STDLIB:
            continue
        if imp == "app": # Self reference
            continue
            
        # Mapear nome
        pkg_name = PACKAGE_MAP.get(imp, imp)
        requirements.add(pkg_name)

    # Escrever
    with open("requirements.txt", "w", encoding="utf-8") as f:
        # Adicionar básicas garantidas
        f.write("# Auto-generated from code imports\n")
        f.write("fastapi\n")
        f.write("uvicorn\n")
        f.write("sqlalchemy\n")
        f.write("pydantic\n")
        
        for req in sorted(requirements):
            if req not in ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "typing", "datetime", "os", "sys", "json"]:
                f.write(f"{req}\n")
    
    print("requirements.txt gerado com sucesso!")

if __name__ == "__main__":
    scan_codebase()
