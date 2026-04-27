
import sys
sys.path.append("c:/Wev Dev/projetos/agendha")
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def verify_styling_fix():
    print("--- VERIFICANDO CORREÇÃO DE ESTILOS BSF ---")
    
    # 1. Verificar Stylesheet Links via url_for em base.html
    # (Indireta: verifica se a página carrega sem erro 500, o que indicaria erro de syntax no template)
    try:
        resp = client.get("/projetos/ater-bahia-sem-fome/producao")
        if resp.status_code == 200:
            print("✅ Página carregada com sucesso (Template Syntax OK)")
            
            content = resp.text
            if "cdn.tailwindcss.com" in content:
                 print("✅ Tailwind CDN injetado no HTML")
            else:
                 print("❌ Tailwind CDN NÃO encontrado")
                 
            if "backdrop-blur-lg" in content:
                 print("✅ Classes Glassmorphism presentes")
            else:
                 print("❌ Classes Glassmorphism ausentes")
                 
            if "static/css/style.css" in content:
                 print("✅ Link estático style.css encontrado (caminho renderizado)")
            else:
                 print("⚠️ Link estático style.css não verificado (pode ser relativo)")

        else:
            print(f"❌ Erro ao carregar página: {resp.status_code}")
    except Exception as e:
        print(f"❌ Exceção ao carregar página: {e}")

if __name__ == "__main__":
    verify_styling_fix()
