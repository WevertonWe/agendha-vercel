
import sys
sys.path.append("c:/Wev Dev/projetos/agendha")
from app.main import app

print("--- DEBUG ROUTES ---")
for route in app.routes:
    print(f"Name: {route.name}, Path: {getattr(route, 'path', 'N/A')}")
print("--- END DEBUG ---")
