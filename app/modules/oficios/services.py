import sqlite3

def get_all_oficios(db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM oficios ORDER BY id DESC")
    return cursor.fetchall()

def create_oficio(db: sqlite3.Connection, dados: dict):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO oficios (numero_oficio, destinatario, data_envio, motivo_descricao, criado_por, caminho_arquivo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        dados.get('numero_oficio'),
        dados.get('destinatario'),
        dados.get('data_envio'),
        dados.get('motivo_descricao'),
        dados.get('criado_por'),
        dados.get('caminho_arquivo')
    ))
    db.commit()
    return cursor.lastrowid

def update_oficio(db: sqlite3.Connection, oficio_id: int, dados: dict):
    cursor = db.cursor()
    
    # Construir query dinâmica
    campos = []
    valores = []
    
    if 'numero_oficio' in dados:
        campos.append("numero_oficio = ?")
        valores.append(dados['numero_oficio'])
        
    if 'destinatario' in dados:
        campos.append("destinatario = ?")
        valores.append(dados['destinatario'])
        
    if 'data_envio' in dados:
        campos.append("data_envio = ?")
        valores.append(dados['data_envio'])
        
    if 'motivo_descricao' in dados:
        campos.append("motivo_descricao = ?")
        valores.append(dados['motivo_descricao'])

    if 'caminho_arquivo' in dados:
        campos.append("caminho_arquivo = ?")
        valores.append(dados['caminho_arquivo'])
        
    if not campos:
        return False
        
    valores.append(oficio_id)
    query = f"UPDATE oficios SET {', '.join(campos)} WHERE id = ?"  # nosec
    
    cursor.execute(query, valores)
    db.commit()
    return cursor.rowcount > 0

def delete_oficio(db: sqlite3.Connection, oficio_id: int):
    cursor = db.cursor()
    cursor.execute("DELETE FROM oficios WHERE id = ?", (oficio_id,))
    db.commit()
    return cursor.rowcount > 0
