import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

def main():
    load_dotenv()
    db_string = os.getenv("SUPABASE_DB_STRING")
    if not db_string:
        print("ERRO: SUPABASE_DB_STRING não encontrada no .env!")
        return
        
    print("Conectando ao PostgreSQL do Supabase...")
    conn = psycopg2.connect(db_string)
    cursor = conn.cursor()
    
    try:
        print("Criando tabela 'documentos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documentos (
                id SERIAL PRIMARY KEY,
                nome_documento TEXT NOT NULL,
                descricao TEXT,
                nome_arquivo TEXT NOT NULL,
                caminho_arquivo TEXT NOT NULL,
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("Criando tabela 'eventos_grh'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eventos_grh (
                id SERIAL PRIMARY KEY,
                municipio_comunidade TEXT NOT NULL,
                dia_previsto TEXT NOT NULL,
                realizado BOOLEAN NOT NULL DEFAULT FALSE,
                observacao TEXT,
                link_formulario TEXT
            );
        """)
        
        print("Criando tabela 'bsf_atividades'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bsf_atividades (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL UNIQUE,
                descricao TEXT,
                meta_padrao INTEGER DEFAULT 0
            );
        """)
        
        print("Criando tabela 'bsf_metas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bsf_metas (
                id SERIAL PRIMARY KEY,
                municipio TEXT NOT NULL,
                mes INTEGER NOT NULL,
                ano INTEGER NOT NULL,
                meta_total INTEGER NOT NULL,
                UNIQUE(municipio, mes, ano)
            );
        """)
        
        print("Criando tabela 'bsf_metas_contrato'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bsf_metas_contrato (
                id SERIAL PRIMARY KEY,
                atividade_id INTEGER NOT NULL REFERENCES bsf_atividades(id) ON DELETE CASCADE,
                ano INTEGER NOT NULL,
                meta_mensal INTEGER DEFAULT 0,
                meta_anual INTEGER DEFAULT 0,
                UNIQUE(atividade_id, ano)
            );
        """)
        
        print("Criando tabela 'bsf_metas_composicao'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bsf_metas_composicao (
                id SERIAL PRIMARY KEY,
                meta_id INTEGER NOT NULL REFERENCES bsf_metas(id) ON DELETE CASCADE,
                atividade_id INTEGER NOT NULL REFERENCES bsf_atividades(id) ON DELETE CASCADE,
                valor_meta INTEGER NOT NULL DEFAULT 0
            );
        """)
        
        print("Criando tabela 'bsf_visitas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bsf_visitas (
                id SERIAL PRIMARY KEY,
                tecnico_id TEXT NOT NULL,
                beneficiario_id TEXT NOT NULL,
                municipio TEXT NOT NULL,
                comunidade TEXT,
                data_visita TEXT NOT NULL,
                status TEXT DEFAULT 'Realizada',
                atividade_id INTEGER,
                data_registro TEXT
            );
        """)
        
        print("Criando tabela 'bsf_metas_tecnicos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bsf_metas_tecnicos (
                id SERIAL PRIMARY KEY,
                tecnico_id TEXT NOT NULL,
                atividade_id INTEGER NOT NULL REFERENCES bsf_atividades(id) ON DELETE CASCADE,
                mes INTEGER NOT NULL,
                ano INTEGER NOT NULL,
                valor_meta INTEGER NOT NULL DEFAULT 0,
                UNIQUE(tecnico_id, atividade_id, mes, ano)
            );
        """)
        
        print("Fazendo Seed das atividades BSF...")
        atividades_contrato = [
            ("Reunião de Articulação com os Parceiros", "Reuniões com lideranças e parceiros", 1, 6),
            ("Levantamento Socioeconômico e Geolocalização", "Levantamento inicial de dados", 41, 490),
            ("Cadastro do Grupo Familiar", "Cadastro de famílias no sistema", 41, 490),
            ("Caracterização da UPF I (Inicial)", "Caracterização inicial da unidade", 41, 490),
            ("Caracterização da UPF II (Intermediária)", "Caracterização intermediária", 41, 490),
            ("Caracterização da UPF III (Final)", "Caracterização final da unidade", 41, 490),
            ("Visita Técnica Social", "Visitas de acompanhamento a famílias", 163, 1960),
            ("Elaboração do Plano Produtivo da UPF", "Elaboração de planos produtivos", 41, 490),
            ("Visita Técnica", "Visitas técnicas de campo", 898, 10771),
            ("Demonstração Didática", "Demonstrações práticas", 25, 300),
            ("Seminário Territorial", "Seminários territoriais", 1, 1),
            ("Seminário Final", "Seminários de encerramento", 1, 1),
            ("Excursão/Intercâmbio", "Visitas de intercâmbio entre comunidades", 1, 12),
            ("Curso", "Cursos de capacitação", 8, 93),
            ("Oficina Temática", "Oficinas e treinamentos temáticos", 8, 96),
            ("Dia de Campo", "Demonstração prática em campo", 8, 96),
        ]
        
        for nome, desc, meta_m, meta_a in atividades_contrato:
            cursor.execute("""
                INSERT INTO bsf_atividades (nome, descricao) 
                VALUES (%s, %s) 
                ON CONFLICT (nome) DO UPDATE SET descricao = EXCLUDED.descricao
                RETURNING id
            """, (nome, desc))
            res = cursor.fetchone()
            if res:
                atv_id = res[0]
                for ano in [2025, 2026]:
                    cursor.execute("""
                        INSERT INTO bsf_metas_contrato (atividade_id, ano, meta_mensal, meta_anual)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (atividade_id, ano) DO NOTHING
                    """, (atv_id, ano, meta_m, meta_a))
                    
        conn.commit()
        print("TUDO CRIADO E CONFIGURADO COM SUCESSO NO SUPABASE!")
        
    except Exception as e:
        conn.rollback()
        print(f"ERRO AO CRIAR TABELAS: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
