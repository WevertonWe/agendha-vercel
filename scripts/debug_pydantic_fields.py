
from app.modules.bahia_sem_fome.models import BSFVisitaCreate, BSFVisitaBase, BSFVisita

def inspect_models():
    print("--- Introspecção de Modelos ---")
    
    # 1. BSFVisitaBase
    fields_base = BSFVisitaBase.__fields__
    print(f"\nBSFVisitaBase Fields: {list(fields_base.keys())}")
    if 'id' in fields_base:
        print("CRITICAL: 'id' found in BSFVisitaBase!")
    else:
        print("OK: 'id' NOT in BSFVisitaBase.")

    # 2. BSFVisitaCreate
    fields_create = BSFVisitaCreate.__fields__
    print(f"\nBSFVisitaCreate Fields: {list(fields_create.keys())}")
    if 'id' in fields_create:
        print("CRITICAL: 'id' found in BSFVisitaCreate!")
    else:
        print("OK: 'id' NOT in BSFVisitaCreate.")

    # 3. BSFVisita (Leitura)
    fields_read = BSFVisita.__fields__
    print(f"\nBSFVisita Fields: {list(fields_read.keys())}")
    if 'id' not in fields_read:
        print("WARNING: 'id' NOT found in BSFVisita (Expected for read model)!")
    else:
        print("OK: 'id' found in BSFVisita.")

if __name__ == "__main__":
    inspect_models()
