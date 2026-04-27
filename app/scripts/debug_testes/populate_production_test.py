import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "agendha.db"

def populate_test_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Find beneficiaries with a mason assigned
        cursor.execute("SELECT id, nome_completo, pedreiro_id FROM beneficiarios WHERE pedreiro_id IS NOT NULL LIMIT 3")
        rows = cursor.fetchall()

        if len(rows) < 3:
            print(f"Alerta: Encontrados apenas {len(rows)} beneficiários com pedreiros. Tentando atribuir pedreiros a alguns...")
            
            # Find a mason
            cursor.execute("SELECT id FROM pedreiros LIMIT 1")
            pedreiro = cursor.fetchone()
            if not pedreiro:
                print("Erro: Nenhum pedreiro encontrado no banco. Crie um pedreiro primeiro.")
                return
            
            pedreiro_id = pedreiro[0]
            
            # Update some beneficiaries without mason
            cursor.execute("SELECT id FROM beneficiarios WHERE pedreiro_id IS NULL LIMIT 3")
            rows_to_update = cursor.fetchall()
            for r in rows_to_update:
                cursor.execute("UPDATE beneficiarios SET pedreiro_id = ? WHERE id = ?", (pedreiro_id, r[0]))
            
            conn.commit()
            
            # Re-fetch
            cursor.execute("SELECT id, nome_completo, pedreiro_id FROM beneficiarios WHERE pedreiro_id IS NOT NULL LIMIT 3")
            rows = cursor.fetchall()

        print(f"Selecionados {len(rows)} beneficiários para teste.")

        # 2. Update them
        for row in rows:
            ben_id = row[0]
            nome = row[1]
            
            # Random date in the last 30 days
            days_ago = random.randint(1, 30)
            data_conclusao = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            print(f"Atualizando Beneficiário: {nome} (ID: {ben_id})")
            print(f" -> Data Conclusão: {data_conclusao}")
            print(" -> Status Pagamento: PENDENTE")
            
            cursor.execute("""
                UPDATE beneficiarios 
                SET data_conclusao = ?, 
                    status_pagamento = 'PENDENTE',
                    status = 'CONSTRUÍDA'
                WHERE id = ?
            """, (data_conclusao, ben_id))

        conn.commit()
        print("\nSucesso! Dados populados.")
        print("Vá para a tela de Gestão de Pedreiros e verifique se o badge 'Pendente' (Amarelo) aparece.")

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    populate_test_data()
