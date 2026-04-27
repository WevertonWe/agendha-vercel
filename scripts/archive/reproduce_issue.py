
import os  # noqa: F401
import sys
# Add project root to path
sys.path.append("c:/Wev Dev/projetos/agendha")

from fastapi.testclient import TestClient
from app.main import app
from app.core.auth.utils import create_access_token

# Generate a token for admin user
admin_token = create_access_token({"sub": "admin", "role": "admin"})

client = TestClient(app)

print("--- ATTEMPTING TO CREATE USER 'thiago.agendha' ---")
try:
    response = client.post(
        "/api/users",
        json={
            "username": "thiago.agendha",
            "password": "password123",
            "full_name": "Thiago Coordinator",
            "role": "admin"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")
except Exception as e:
    print(f"CRASHED: {e}")
