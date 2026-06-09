import os
import sys
import pytest
import sqlite3
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Adjust sys.path to find app packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.dependencies import get_db
from app.core.auth.dependencies import get_admin_user
from app.core.utils.crypto import encrypt_password, decrypt_password
from app.routers.admin_assets import execute_query, row_to_dict

# ------------------------------------------------------------------------------
# 1. UNIT TESTS FOR CRYPTOGRAPHY HELPERS
# ------------------------------------------------------------------------------

def test_crypto_helpers():
    print("Running unit tests for cryptography helpers...")
    plain = "SuperSecretPBI123!"
    
    # Encrypt and decrypt cycle
    encrypted = encrypt_password(plain)
    assert encrypted != plain
    assert len(encrypted) > 0
    
    decrypted = decrypt_password(encrypted)
    assert decrypted == plain
    print("   [OK] Encrypt/Decrypt cycle passed successfully.")
    
    # Null and empty safety
    assert encrypt_password("") == ""
    assert decrypt_password("") == ""
    assert encrypt_password(None) == ""
    assert decrypt_password(None) == ""
    print("   [OK] Null and empty values handled safely.")
    
    # Invalid decryption handling
    corrupted = encrypted[:-4] + "AAAA"
    # Should safely return an empty string or handle gracefully rather than crashing
    assert decrypt_password(corrupted) == ""
    print("   [OK] Corrupted cipher text handles safely.")


# ------------------------------------------------------------------------------
# 2. UNIT TESTS FOR DATABASE COMPATIBILITY ROUTINES
# ------------------------------------------------------------------------------

def test_execute_query_compatibility():
    print("Running unit tests for database query translation...")
    
    # Define connection classes with required names to test class-name inspection
    class Connection:
        def __init__(self):
            self.cursor_mock = MagicMock()
        def cursor(self):
            return self.cursor_mock
            
    class RealDictConnection:
        def __init__(self):
            self.cursor_mock = MagicMock()
        def cursor(self):
            return self.cursor_mock
    
    sqlite_conn = Connection()
    pg_conn = RealDictConnection()
    
    query = "SELECT * FROM my_table WHERE id = ? AND status = ?"
    
    # Test SQLite preserves "?"
    cursor_sqlite = execute_query(sqlite_conn, query, (1, "active"))
    sqlite_conn.cursor_mock.execute.assert_called_once_with(query, (1, "active"))
    print("   [OK] Preserves '?' for SQLite connection name.")
    
    # Test PostgreSQL translates "?" to "%s"
    cursor_pg = execute_query(pg_conn, query, (1, "active"))
    pg_conn.cursor_mock.execute.assert_called_once_with("SELECT * FROM my_table WHERE id = %s AND status = %s", (1, "active"))
    print("   [OK] Translates '?' to '%s' for non-sqlite connection class names.")


# ------------------------------------------------------------------------------
# 3. INTEGRATION TESTS FOR CRUD ENDPOINTS WITH IN-MEMORY SQLITE
# ------------------------------------------------------------------------------

# Temporary in-memory test database fixture
@pytest.fixture
def test_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create the identical target tables for assets test suite
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bsf_powerbi_credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_projeto TEXT NOT NULL,
        email_login TEXT NOT NULL,
        senha TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Ativo',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendha_dispositivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        marca_modelo TEXT NOT NULL,
        numero_serie_imei TEXT UNIQUE NOT NULL,
        responsavel_atual TEXT,
        status TEXT NOT NULL DEFAULT 'Disponível',
        url_termo_pdf TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    yield conn
    conn.close()


def test_admin_assets_endpoints(test_db):
    print("Running integration tests for Admin Assets endpoints...")
    
    # Setup dependency overrides for TestClient
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
            
    def override_get_admin_user():
        return {"username": "admin_test", "role": "admin"}
        
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_admin_user] = override_get_admin_user
    
    client = TestClient(app)
    
    # -- TEST A: POWERBI CRUD --
    print("Testing PowerBI Credentials workflow...")
    # List initial empty table
    response = client.get("/api/admin/powerbi")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
    # Create credential
    payload_pbi = {
        "nome_projeto": "Projeto AQA",
        "email_login": "aqa@agendha.org",
        "senha": "super_secret_pbi_password",
        "status": "Ativo"
    }
    response = client.post("/api/admin/powerbi", json=payload_pbi)
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    
    # List after insertion (Verify password masking)
    response = client.get("/api/admin/powerbi")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nome_projeto"] == "Projeto AQA"
    assert data[0]["email_login"] == "aqa@agendha.org"
    assert data[0]["senha"] == "********"  # Masked password assertion
    created_id = data[0]["id"]
    print("   [OK] PowerBI credential created and masked listed successfully.")
    
    # Reveal endpoint
    response = client.get(f"/api/admin/powerbi/{created_id}/reveal")
    assert response.status_code == 200
    assert response.json()["senha"] == "super_secret_pbi_password"
    print("   [OK] Password reveal is secure and decrypts correctly.")
    
    # Update credential
    payload_update = {
        "nome_projeto": "Projeto AQA Atualizado",
        "senha": "new_secret_password"
    }
    response = client.put(f"/api/admin/powerbi/{created_id}", json=payload_update)
    assert response.status_code == 200
    
    # Reveal updated password
    response = client.get(f"/api/admin/powerbi/{created_id}/reveal")
    assert response.json()["senha"] == "new_secret_password"
    print("   [OK] PowerBI updates and dynamic re-encryption verified.")
    
    # -- TEST B: DEVICES CRUD --
    print("Testing Device Inventory workflow...")
    # List initial empty table
    response = client.get("/api/admin/dispositivos")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
    # Create Device
    payload_device = {
        "tipo": "Notebook",
        "marca_modelo": "Dell Vostro 15",
        "numero_serie_imei": "NS-DELL-123456",
        "responsavel_atual": "João Silva",
        "status": "Disponível"
    }
    response = client.post("/api/admin/dispositivos", json=payload_device)
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    
    # Verify uniqueness of Serial/IMEI
    response = client.post("/api/admin/dispositivos", json=payload_device)
    assert response.status_code == 400
    print("   [OK] Device uniqueness rule validated.")
    
    # List devices
    response = client.get("/api/admin/dispositivos")
    assert response.status_code == 200
    devices = response.json()
    assert len(devices) == 1
    device_id = devices[0]["id"]
    assert devices[0]["marca_modelo"] == "Dell Vostro 15"
    assert devices[0]["responsavel_atual"] == "João Silva"
    print("   [OK] Device list details verified.")
    
    # Update Device
    payload_device_up = {
        "responsavel_atual": "Maria Santos",
        "status": "Emprestado"
    }
    response = client.put(f"/api/admin/dispositivos/{device_id}", json=payload_device_up)
    assert response.status_code == 200
    
    response = client.get("/api/admin/dispositivos")
    assert response.json()[0]["responsavel_atual"] == "Maria Santos"
    assert response.json()[0]["status"] == "Emprestado"
    print("   [OK] Device information update validated.")
    
    # Clean up overrides
    app.dependency_overrides.clear()
    print("   [OK] Dependency overrides cleaned up successfully.")


if __name__ == "__main__":
    # Run tests using pytest framework to handle dependency injection of fixtures
    sys.exit(pytest.main([__file__]))
