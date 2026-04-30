import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent.parent / ".env")

# Adicionar caminho raiz ao sys.path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from app.core.database import get_supabase

def main():
    print("=== LISTAGEM DE BUCKETS DO SUPABASE ===")
    try:
        supabase = get_supabase()
        buckets = supabase.storage.list_buckets()
        if not buckets:
            print("Nenhum bucket encontrado no Storage do Supabase.")
        else:
            for b in buckets:
                print(f"Bucket: {b.name} | Público: {b.public} | ID: {b.id}")
    except Exception as e:
        print(f"Erro ao listar buckets: {e}")

    print("\n=== VERIFICAÇÃO DE BENEFICIÁRIOS (PDFs) ===")
    try:
        res = supabase.table('beneficiarios').select('*').limit(1).execute()
        if res.data:
            row = res.data[0]
            print(f"Colunas encontradas: {list(row.keys())}")
            for k, v in row.items():
                if 'pdf' in k.lower() or 'doc' in k.lower() or 'arquivo' in k.lower():
                    print(f"Mapeamento potencial -> {k}: {v}")
        else:
            print("Nenhum beneficiário encontrado na tabela.")
    except Exception as e:
        print(f"Erro ao buscar beneficiários: {e}")

if __name__ == '__main__':
    main()
