import os
import sys
from dotenv import load_dotenv

# Garantir que o diretório atual está no path para importar o app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.auth.utils import get_password_hash

def main():
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERRO: Variáveis SUPABASE_URL ou SUPABASE_KEY não encontradas no .env")
        return

    print("Gerando novo hash para a senha 'agendha2024'...")
    nova_senha = "agendha2024"
    novo_hash = get_password_hash(nova_senha)
    print(f"Hash gerado: {novo_hash[:15]}...")

    print("Conectando ao Supabase...")
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
    except ImportError:
        print("ERRO: Pacote 'supabase' não instalado. Execute: pip install supabase")
        return

    print("Buscando usuários para teste de leitura (RLS Test)...")
    
    try:
        users_res = supabase.table('users').select('id, username').execute()
        if not users_res.data:
            print("Nenhum usuário encontrado na tabela 'users' ou o RLS bloqueou a LEITURA.")
            print("Se você sabe que existem usuários, vá ao painel do Supabase e desative o RLS da tabela 'users'.")
            return
            
        print(f"Encontrados {len(users_res.data)} usuários. Iniciando atualização (RLS Test)...")
        sucessos = 0
        
        for u in users_res.data:
            try:
                update_res = supabase.table('users').update({'password_hash': novo_hash}).eq('id', u['id']).execute()
                if update_res.data:
                    sucessos += 1
                    print(f" [OK] Usuário {u.get('username')} atualizado.")
                else:
                    print(f" [FALHA] Usuário {u.get('username')}: Atualização silenciosamente ignorada (RLS Block).")
            except Exception as e:
                print(f" [ERRO] Falha ao atualizar usuário {u.get('username')}: {e}")
                
        print(f"\nFinalizado! {sucessos} de {len(users_res.data)} usuários atualizados.")
        if sucessos < len(users_res.data):
            print("\nATENÇÃO: A atualização falhou ou foi bloqueada.")
            print("MOTIVO PROVÁVEL: O 'Row Level Security' (RLS) está ativado na tabela 'users' e a SUPABASE_KEY atual (anon key) não tem permissão de UPDATE.")
            print("SOLUÇÃO 1: No painel do Supabase, vá em Table Editor -> users -> Turn off RLS temporariamente.")
            print("SOLUÇÃO 2: Altere a SUPABASE_KEY no seu .env para usar a 'service_role' (secret) key, que ignora RLS.")
        else:
            print("\nSucesso total! Todas as senhas foram redefinidas.")
            print("Você já pode testar o login com a senha: agendha2024")
            
    except Exception as e:
        print(f"\nERRO CRÍTICO ao tentar interagir com o Supabase: {e}")
        print("Verifique se as credenciais do .env estão corretas.")

if __name__ == "__main__":
    main()
