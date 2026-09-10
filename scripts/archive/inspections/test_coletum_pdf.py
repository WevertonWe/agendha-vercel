import requests

def testar_pdf_coletum():
    headers = {
        "Token": "517vrjljdboc8g0wwsw48k8co40cos8",
        "Accept": "application/pdf"
    }
    
    # Tentando possíveis endpoints de PDF (comum em sistemas de formulários)
    urls = [
        "https://coletum.com/api/webservice/v2/forms/37226/answers/ABC-001/pdf",
        "https://coletum.com/api/webservice/v2/answers/ABC-001/pdf"
    ]
    
    # Mas precisamos de um ID de answer real. No log anterior, não imprimimos o ID real, só o answer object.
    # Vamos buscar o ID real da primeira answer.
    res_ans = requests.get("https://coletum.com/api/webservice/v2/forms/37226/answers", headers={"Token": "517vrjljdboc8g0wwsw48k8co40cos8"})
    if res_ans.status_code == 200:
        ans_data = res_ans.json()
        first_answer = ans_data.get('data', [])[0]
        ans_id = first_answer.get('id')
        print(f"Testando download de PDF para a resposta ID: {ans_id}")
        
        test_urls = [
            f"https://coletum.com/api/webservice/v2/forms/37226/answers/{ans_id}/pdf",
            f"https://coletum.com/api/webservice/v2/answers/{ans_id}/pdf",
            f"https://coletum.com/api/webservice/v2/forms/37226/answers/{ans_id}.pdf"
        ]
        
        for url in test_urls:
            r = requests.get(url, headers=headers)
            print(f"URL: {url} | Status: {r.status_code}")
            if r.status_code == 200:
                print("PDF ENCONTRADO!")
                break
    else:
        print("Falha ao buscar answers.")

if __name__ == "__main__":
    testar_pdf_coletum()
