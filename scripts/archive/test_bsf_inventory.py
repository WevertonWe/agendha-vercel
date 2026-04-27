
import requests

BASE_URL = "http://localhost:8000"

def test_inventory_flow():
    # 1. Create Municipality
    print("1. Testing Create Bulk Municipality...")
    payload = {
        "municipio": "TestCity_Automated",
        "ano": 2026,
        "meta_mensal": 50,
        "tecnico_responsavel": "Robot Tech"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/projetos/ater-bahia-sem-fome/metas/bulk-municipio", json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            print(">> Creation Success")
        else:
            print(">> Creation Failed")
            return
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. Verify it exists
    # We can assume it worked if 200, but let's try to delete one month to verify delete logic
    # First we need an ID. Since we don't know IDs easily without listing, I'll trust the creation logic return or List.
    
    print("\n2. Testing Delete Logic (Cleanup)...")
    # Let's list to find the ID of one meta from TestCity_Automated
    try:
        r_list = requests.get(f"{BASE_URL}/api/projetos/ater-bahia-sem-fome/metas/?ano=2026")
        data = r_list.json()
        metas = data.get('metas', [])
        
        target_id = None
        for m in metas:
            if m['municipio'] == "TestCity_Automated":
                target_id = m['id']
                break
        
        if target_id:
            print(f"Found Meta ID {target_id} for TestCity_Automated. Deleting...")
            r_del = requests.delete(f"{BASE_URL}/api/projetos/ater-bahia-sem-fome/metas/{target_id}")
            print(f"Delete Status: {r_del.status_code}")  # nosec
            print(f"Delete Response: {r_del.json()}")  # nosec
        else:
            print("Could not find created municipality to test delete.")
            
    except Exception as e:
        print(f"Error in verification: {e}")

if __name__ == "__main__":
    test_inventory_flow()
