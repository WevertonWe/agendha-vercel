import requests
import json
import sys

def explorar_token_coletum(token: str):
    print("Investigando token no Coletum API (v2)...")
    
    headers = {
        "Token": token,
        "Accept": "application/json"
    }
    
    url_forms = "https://coletum.com/api/webservice/v2/forms"
    
    try:
        response = requests.get(url_forms, headers=headers, timeout=15)
        
        print(f"\nStatus Code (Formularios): {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            forms = data.get("data", [])
            print("SUCESSO! O token conseguiu acessar o Coletum.")
            print(f"Total de Formularios vinculados a esse token: {len(forms)}")
            
            for f in forms[:5]: # Mostrar só os 5 primeiros
                f_id = f.get('id', 'N/A')
                f_name = f.get('name', 'N/A')
                print(f" - ID: {f_id} | Nome: {f_name}")
                
            if forms:
                print("\n---------------------------------------------------------")
                primeiro_id = forms[0].get('id')
                print(f"Buscando as primeiras 5 respostas do formulario {primeiro_id}...")
                
                url_answers = f"https://coletum.com/api/webservice/v2/forms/{primeiro_id}/answers"
                res_ans = requests.get(url_answers, headers=headers, timeout=15)
                if res_ans.status_code == 200:
                    ans_data = res_ans.json()
                    answers = ans_data.get('data', [])
                    print(f"Total de respostas encontradas (paginacao): {ans_data.get('pagination', {}).get('total_items')}")
                    for ans in answers[:2]:
                        print("--- Resposta ---")
                        # print keys inside answer
                        print(json.dumps(ans.get('answer', {}), indent=2, ensure_ascii=False))
        else:
            print("Falha ao acessar. Verifique se o token esta correto.")
            print("Resposta da API:", response.text)
            
    except Exception as e:
        print(f"Erro ao tentar conectar na API do Coletum: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    explorar_token_coletum("517vrjljdboc8g0wwsw48k8co40cos8")
