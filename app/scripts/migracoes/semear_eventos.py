# scripts/semear_eventos.py
import sqlite3

NOME_BANCO_DE_DADOS = "agendha.db"
NOME_TABELA = "eventos_grh"

# Dados extraídos da sua imagem 'MONITORAMENTO GRH'
# 1 = Realizado (check marcado), 0 = Não Realizado (check vazio)
eventos_iniciais = [
    {"municipio": "CHORROCHÓ", "dia": "3 e 4/07", "realizado": 1},
    {"municipio": "PAULO AFONSO", "dia": "21 e 22/07", "realizado": 1},
    {"municipio": "PAULO AFONSO", "dia": "23 e 24/07", "realizado": 1},
    {"municipio": "CHORROCHÓ", "dia": "29 e 30/07", "realizado": 1},
    {"municipio": "MACURURÉ", "dia": "31/07 e 01/08", "realizado": 1},
    {"municipio": "GLÓRIA", "dia": "5 e 6/08", "realizado": 1},
    {"municipio": "GLÓRIA", "dia": "7 e 8/08", "realizado": 1},
    {"municipio": "PAULO AFONSO", "dia": "14 e 15/08", "realizado": 1},
    {"municipio": "MACURURÉ", "dia": "19 e 20/08", "realizado": 1},
    {"municipio": "ABARÉ", "dia": "21 e 22/08", "realizado": 1},
    {"municipio": "ABARÉ", "dia": "26 e 27/08", "realizado": 1},
    {"municipio": "GLÓRIA", "dia": "28 e 29/08", "realizado": 1},
    {"municipio": "GLÓRIA", "dia": "4 e 5/09", "realizado": 1},
    {"municipio": "ABARÉ", "dia": "9 e 10/09", "realizado": 1},
    {"municipio": "RODELAS", "dia": "11 e 12/09", "realizado": 0},
    {"municipio": "ABARÉ", "dia": "16 e 17/09", "realizado": 0},
    {"municipio": "ABARÉ", "dia": "18 e 19/09", "realizado": 0},
    {"municipio": "ABARÉ", "dia": "23 e 24/09", "realizado": 0},
]


def semear_dados():
    """Insere os dados iniciais na tabela de eventos."""
    conexao = None
    try:
        conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
        cursor = conexao.cursor()

        # Limpa a tabela antes de inserir para evitar
        # duplicatas ao rodar de novo
        print(f"Limpando dados antigos da tabela '{NOME_TABELA}'...")
        cursor.execute(f"DELETE FROM {NOME_TABELA};")  # nosec
        print("Dados antigos removidos.")

        print(f"Inserindo {len(eventos_iniciais)} registros de eventos...")
        for evento in eventos_iniciais:
            cursor.execute(
                f"""
                INSERT INTO {NOME_TABELA} (municipio_comunidade,
                dia_previsto, realizado)
                VALUES (?, ?, ?)
                """,
                (evento["municipio"], evento["dia"], evento["realizado"])
            )

        conexao.commit()
        print("\n✅ 'Semeadura' de dados concluída com sucesso!")

    except sqlite3.Error as e:
        print(f"❌ ERRO ao semear o banco de dados: {e}")
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    semear_dados()
