import sqlite3
from fastapi import HTTPException
from app.core.auth.models import TrocarSenhaSchema
from app.core.auth.utils import verify_password, get_password_hash

def mudar_senha(db: sqlite3.Connection, username: str, dados: TrocarSenhaSchema):
    cursor = db.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    current_hash = row['password_hash']
    
    if not verify_password(dados.senha_atual, current_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
        
    if dados.nova_senha != dados.confirmar_senha:
        raise HTTPException(status_code=400, detail="As novas senhas não conferem")
        
    new_hash = get_password_hash(dados.nova_senha)
    
    try:
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar senha: {e}")
