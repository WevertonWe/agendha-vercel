import os
import re

files_to_fix = [
    "app/modules/materiais/views.py",
    "app/modules/projetos/routers.py",
    "app/modules/mapa/routes.py",
    "app/modules/oficios/routes.py",
    "app/modules/fornecedores/views.py",
    "app/modules/financeiro/views.py",
    "app/modules/cotacoes/views.py",
    "app/modules/dashboard/views.py",
    "app/modules/bahia_sem_fome/views.py",
    "app/routers/views.py",
    "app/routers/admin_audit.py",
    "app/main.py",
    "app/modules/agua_que_alimenta/views.py",
    "app/modules/agua_que_alimenta/routers/pedreiros.py",
    "app/modules/agua_que_alimenta/routers/beneficiarios.py",
    "app/core/views.py",
]

replacement = """from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)"""

for filepath in files_to_fix:
    full_path = os.path.join(r"c:\Wev Dev\projetos\agendha_vercel", filepath)
    if not os.path.exists(full_path):
        continue
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    # Remove existing cache invalidation
    content = re.sub(r'templates\.env\.cache\s*=\s*None\n?', '', content)
    
    # Check if already using Environment
    if "from jinja2 import Environment" not in content:
        # Match variations of Jinja2Templates instantiation
        content = re.sub(
            r'templates\s*=\s*Jinja2Templates\([^)]+\)',
            replacement,
            content
        )
        
    if content != original_content:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filepath}")
