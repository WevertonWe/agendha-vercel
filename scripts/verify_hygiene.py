import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agendha.db")

def verify():
    print(f"📂 Verificando Banco: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Verificar contagem de atividades retornadas pela query do backend
    print("\n🔍 A. Simulação da Query do Backend (JOIN bsf_metas_contrato):")
    cursor.execute("""
        SELECT a.id, a.nome
        FROM bsf_atividades a
        JOIN bsf_metas_contrato mc ON mc.atividade_id = a.id
        GROUP BY a.id, a.nome
        ORDER BY MIN(mc.id)
    """)
    rows = cursor.fetchall()
    print(f"   Total retornado: {len(rows)}")
    for r in rows:
        print(f"   [{r[0]}] {r[1]}")

    if len(rows) != 16:
        print("\n❌ ERRO: Esperado 16 atividades, encontrado", len(rows))
    else:
        print("\n✅ SUCESSO: Exatamente 16 atividades oficiais retornadas.")

    # 2. Verificar se restou alguma atividade 'proibida'
    print("\n🔍 B. Procurando atividades proibidas (deleted):")
    proibidas = [
        "Cadastro Familiar", 
        "Reunião de Articulação", 
        "Implantação de Fomento", 
        "Monitoramento", 
        "Oficina de Capacitação"
    ]
    
    placeholders = ','.join('?' for _ in proibidas)
    cursor.execute(f"SELECT nome FROM bsf_atividades WHERE nome IN ({placeholders})", proibidas)  # nosec
    found = cursor.fetchall()
    
    if found:
        print(f"❌ ERRO: Atividades proibidas encontradas: {found}")
    else:
        print("✅ SUCESSO: Nenhuma atividade proibida encontrada.")

    # 3. Verificar migração de visitas
    print("\n🔍 C. Contagem de visitas na atividade unificada 'Cadastro do Grupo Familiar':")
    cursor.execute("SELECT id FROM bsf_atividades WHERE nome = 'Cadastro do Grupo Familiar'")
    try:
        new_id = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM bsf_visitas WHERE atividade_id = ?", (new_id,))
        count = cursor.fetchone()[0]
        print(f"   Total de visitas em 'Cadastro do Grupo Familiar' (ID {new_id}): {count}")
    except Exception as e:
        print(f"   Erro ao verificar: {e}")

    conn.close()

if __name__ == "__main__":
    verify()
