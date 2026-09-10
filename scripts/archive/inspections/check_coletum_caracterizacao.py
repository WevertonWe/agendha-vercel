import asyncio
import pandas as pd
from app.services.coletum_service import buscar_respostas_formulario, extrair_data_coletum

async def main():
    print("Buscando respostas do formulário 37205 (Caracterização da UPF)...")
    respostas = await buscar_respostas_formulario("37205", limit=2000)
    print(f"Total de respostas baixadas da API: {len(respostas)}")
    
    dados = []
    for r in respostas:
        # extrair campos principais
        ans_id = r.get('id')
        created_at = r.get('created_at')
        updated_at = r.get('updated_at')
        ans_data = r.get('data', {})
        
        # Coletum fields vary by key
        dados.append({
            'answer_id': ans_id,
            'created_at': created_at,
            'raw_data': ans_data
        })
    
    # Salvar amostra para inspecionar chaves dos campos
    if dados:
        print("Exemplo de resposta data keys:", list(dados[0]['raw_data'].keys())[:10])

asyncio.run(main())
