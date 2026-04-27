import sqlite3
import sys
import os

# Add app to path
sys.path.append(os.getcwd())

from app.modules.agua_que_alimenta.services.logistica_service import calculate_logistics_preview, get_abare_candidates
from app.modules.agua_que_alimenta.services.pdf_service_abare import gerar_pdf_cotacao_logistica

def test_logic():
    print("--- Testando Lógica de PDF e Dados Abaré ---")
    conn = sqlite3.connect('agendha.db')
    conn.row_factory = sqlite3.Row # CRITICAL FIX for dict conversion
    
    # 1. Testar Query
    print("\n1. Buscando Candidatos 'ABARE'...")
    try:
        candidatos = get_abare_candidates(conn)
        print(f"Candidatos encontrados: {len(candidatos)}")
        if len(candidatos) > 0:
            print(f"Exemplo: {candidatos[0]['nome_completo']} ({candidatos[0]['municipio']})")
    except Exception as e:
        print(f"ERRO Query: {e}")
        return

    # 2. Testar Calculo
    print("\n2. Calculando Prévia Logística...")
    try:
        dados = calculate_logistics_preview(conn)
        print(f"Resumo: {dados.get('resumo', 'OK')}")
        print(f"Custo Total: {dados.get('custo_total_estimado', 'N/A')}")
        print(f"Total Candidatos no JSON: {dados.get('total_candidatos', 'N/A')}")
    except Exception as e:
        print(f"ERRO Calculo: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Testar Geração PDF
    print("\n3. Gerando PDF (Em memória)...")
    try:
        if not dados:
            print("DADOS VAZIOS!")
        else:
            print(f"Dados chaves: {dados.keys()}")
            
        pdf_buffer = gerar_pdf_cotacao_logistica(dados)
        size = pdf_buffer.getbuffer().nbytes
        print(f"PDF Gerado com sucesso! Tamanho: {size} bytes")
    except Exception as e:
        print(f"ERRO PDF: {e}")
        import traceback
        traceback.print_exc()

    conn.close()

if __name__ == "__main__":
    test_logic()
