import sqlite3
import unicodedata

# O caminho para o seu banco de dados
NOME_BANCO_DE_DADOS = "app/agendha.db"

def _remover_acentos(texto: str) -> str:
    """Remove acentos de uma string, normalizando-a."""
    if not texto:
        return ""
    nfkd_form = unicodedata.normalize('NFD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalizar_municipios():
    """Lê todos os beneficiários, normaliza o campo 'municipio' e o atualiza."""
    
    print("Iniciando a normalização dos nomes de municípios...")
    conexao = None
    try:
        conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
        # Usamos sqlite3.Row para aceder às colunas pelo nome
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()

        # 1. Selecionar todos os beneficiários que precisam de atualização
        cursor.execute("SELECT id, municipio FROM beneficiarios WHERE municipio IS NOT NULL AND municipio != ''")
        beneficiarios = cursor.fetchall()
        
        total_a_atualizar = len(beneficiarios)
        print(f"Encontrados {total_a_atualizar} registros para verificar.")
        
        atualizados = 0
        for beneficiario in beneficiarios:
            id_beneficiario = beneficiario['id']
            municipio_original = beneficiario['municipio']
            
            # 2. Aplicar a mesma lógica de normalização dos filtros
            municipio_normalizado = _remover_acentos(municipio_original).upper().strip()
            
            # 3. Atualizar o registo apenas se houver mudança
            if municipio_original != municipio_normalizado:
                cursor.execute(
                    "UPDATE beneficiarios SET municipio = ? WHERE id = ?",
                    (municipio_normalizado, id_beneficiario)
                )
                atualizados += 1

        conexao.commit()
        print(f"\n✅ Normalização concluída! {atualizados} de {total_a_atualizar} registros foram atualizados.")

    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    normalizar_municipios()