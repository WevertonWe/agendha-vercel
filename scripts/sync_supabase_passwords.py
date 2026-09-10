import os
import sys
from dotenv import load_dotenv

# Load from .env if present
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("SUPABASE_URL or SUPABASE_KEY is missing in environment.")
    sys.exit(1)

try:
    from supabase import create_client
    supabase = create_client(supabase_url, supabase_key)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    sys.exit(1)

from passlib.context import CryptContext  # noqa: E402

# Use exact same config as the app
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", truncate_error=True)

password = "agendha2024"
hashed_password = pwd_context.hash(password)

print(f"Generated hash length: {len(hashed_password)}")

# Update all users
try:
    # Fetch all users
    users_res = supabase.table('users').select('id, username').execute()
    
    users = users_res.data
    if not users:
        print("Nenhum usuário encontrado na tabela 'users' do Supabase.")
        print("Criando o usuário admin padrão...")
        supabase.table('users').insert({
            'username': 'admin',
            'password_hash': hashed_password,
            'role': 'admin',
            'is_active': True,
            'full_name': 'Administrador do Sistema'
        }).execute()
        print("Usuário 'admin' criado com a senha 'agendha2024'.")
        sys.exit(0)
    
except Exception as e:
    print(f"Error updating users: {e}")
