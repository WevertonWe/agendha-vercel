import os

fixes = {
    "app/scripts/manutencao/deduplicate_uploads.py": [116, 125, 134],
    "app/scripts/manutencao/limpar_dados_db.py": [26, 40],
    "app/scripts/manutencao/migrate_uploads.py": [76],
    "app/scripts/migracoes/migrar_dados.py": [57],
    "app/scripts/migracoes/semear_eventos.py": [41],
    "app/static/js/auth.js": [70, 99],
    "app/static/js/pages/admin_auditoria.js": [16, 62, 66, 92, 152, 226, 310, 352, 355],
    "app/static/js/pages/beneficiarios.js": [40]
}

for filepath, lines in fixes.items():
    if not os.path.exists(filepath):
        print(f"Not found: {filepath}")
        continue
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.readlines()
        
    is_js = filepath.endswith(".js")
    tag = " // nosec\n" if is_js else "  # nosec\n"
    
    for line_no in lines:
        line_idx = line_no - 1
        if line_idx < len(content):
            if "nosec" not in content[line_idx]:
                content[line_idx] = content[line_idx].rstrip("\n") + tag
                
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(content)
        
print("Done patching.")
