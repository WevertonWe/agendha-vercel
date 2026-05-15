import sys
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_supabase

client = TestClient(app)

def test_workflow():
    print("Iniciando testes de validação BSF Schema...")
    
    # 1. Connection Test: select().limit(1) na tabela bsf_atividades
    try:
        print("1. Testando conexão com bsf_atividades...")
        supabase = get_supabase()
        res = supabase.table("bsf_atividades").select("*").limit(1).execute()
        print(f"   [OK] Conexão bem sucedida. Dados: {res.data}")
    except Exception as e:
        print(f"   [ERRO] Falha ao consultar bsf_atividades: {e}")
        sys.exit(1)

    # 2. Setup: Criar beneficiario de teste
    print("2. Criando beneficiário de teste...")
    payload_ben = {
        "nome_completo": "Testador Automatizado BSF",
        "cpf": "00000000000",
        "municipio": "Salvador",
        "comunidade": "Centro",
        "tecnico": "Bot"
    }
    res_create = client.post("/api/bsf/beneficiarios", json=payload_ben)
    if res_create.status_code != 200:
        print(f"   [ERRO] Falha ao criar beneficiário: {res_create.text}")
        sys.exit(1)
        
    ben_data = res_create.json().get("data")
    ben_id = ben_data.get("id")
    print(f"   [OK] Beneficiário criado. ID: {ben_id}")

    # 3. Activity Log: Testar insert de atividade
    print("3. Inserindo atividade para o beneficiário...")
    payload_atv = {
        "tipo_atividade": "Visita",
        "data": "2026-05-14"
    }
    res_atv = client.post(f"/api/bsf/beneficiarios/{ben_id}/atividades", json=payload_atv)
    if res_atv.status_code != 200:
        print(f"   [ERRO] Falha ao criar atividade: {res_atv.text}")
        sys.exit(1)
        
    atv_data = res_atv.json()
    print(f"   [OK] Atividade inserida. ID: {atv_data.get('id')}")

    # 4. Delete Power Check: Remover o beneficiário
    print("4. Testando Delete Power Check (Cascata)...")
    res_del = client.delete(f"/api/bsf/beneficiarios/{ben_id}")
    if res_del.status_code != 200:
        print(f"   [ERRO] Falha ao deletar beneficiário: {res_del.text}")
        sys.exit(1)
    
    print(f"   [OK] Beneficiário {ben_id} excluído com sucesso.")

    # 5. Verificando se a atividade foi deletada em cascata
    print("5. Verificando integridade da exclusão em cascata...")
    res_check = supabase.table("bsf_atividades").select("id").eq("beneficiario_id", ben_id).execute()
    if len(res_check.data) == 0:
        print("   [OK] Atividades excluídas em cascata com sucesso (0 órfãos).")
    else:
        print("   [ERRO] Registros órfãos encontrados na tabela bsf_atividades!")
        sys.exit(1)

    print("\n✅ Todos os testes de validação do schema BSF passaram com sucesso!")

if __name__ == "__main__":
    test_workflow()
