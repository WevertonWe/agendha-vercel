import os

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

for filepath in files_to_fix:
    full_path = os.path.join(r"c:\Wev Dev\projetos\agendha_vercel", filepath)
    if not os.path.exists(full_path):
        continue
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    fixed_content = content.replace("templates = Jinja2Templates(env=_env))", "templates = Jinja2Templates(env=_env)")
    
    if fixed_content != content:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)
        print(f"Fixed syntax in {filepath}")
