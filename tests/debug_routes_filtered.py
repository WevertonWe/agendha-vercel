
import sys
sys.path.append("c:/Wev Dev/projetos/agendha")
from app.main import app

print("--- DEBUG ROUTES (FILTERED) ---")
found_static = False
for route in app.routes:
    if route.name == "static":
        print(f"FOUND: Name: {route.name}, Path: {getattr(route, 'path', 'N/A')}")
        found_static = True
    if route.name == "uploads":
        print(f"FOUND: Name: {route.name}, Path: {getattr(route, 'path', 'N/A')}")

if not found_static:
    print("❌ STATIC ROUTE NOT FOUND IN app.routes")
else:
    print("✅ STATIC ROUTE FOUND")
print("--- END DEBUG ---")
