from app.modules.agua_que_alimenta.routers.pedreiros import listar_pedreiros
from app.dependencies import get_db_connection  # noqa: F401
import sqlite3

# Mock connection
conn = sqlite3.connect('agendha.db')

try:
    print("Testing listar_pedreiros...")
    results = listar_pedreiros(db=conn)
    print(f"Found {len(results)} pedreiros.")
    if results:
        p = results[0]
        print(f"Sample: {p['nome_completo']}")
        print(f" - Total Obras: {p.get('total_obras')}")
        print(f" - Status Fin: {p.get('status_financeiro')}")
        print(f" - Ultima Prod: {p.get('ultima_producao')}")
    else:
        print("No pedreiros found to verify fields.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
