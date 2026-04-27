
import requests  # noqa: F401
import os  # noqa: F401

# Assuming running locally on default port if running main app.
# But here we will import the function and test logic directly or mocking.
# Since we are an agent, we can run a python script that imports app modules.

import sys
import sqlite3  # noqa: F401
sys.path.append('d:/Cursos/agendha')

from app.dependencies import get_db_connection
from app.modules.agua_que_alimenta.routers.beneficiarios import exportar_beneficiarios_kml

# Mock DB connection or use real one
try:
    conn_gen = get_db_connection()
    conn = next(conn_gen) # Get actual connection from generator
    print("Database connected.")
    
    # Test Parameters
    municipio = 'ABARE'
    status = 'IMPORTADO'
    
    # Call function (returns Response object)
    print(f"Testing KML generation for {municipio} - {status}...")
    
    # Needs to be mocked or adapted because it returns FastAPI Response
    # We can inspect the response object if we can instantiate it, 
    # but `exportar_beneficiarios_kml` returns a starlette Response.
    
    response = exportar_beneficiarios_kml(municipio=municipio, status=status, db=conn)
    
    content = response.body.decode('utf-8')
    
    print(f"Response Status Code: {response.status_code}")
    print(f"Content Length: {len(content)}")
    
    # Validation
    if "<kml" in content and "</kml>" in content:
        print("✅ KML Tags found.")
    else:
        print("❌ KML Tags NOT found.")
        
    if "man.png" in content:
        print("✅ Icon 'man.png' found.")
    else:
        print("❌ Icon 'man.png' NOT found.")
        
    if "<Placemark>" in content:
        print("✅ Placemarks found (Data exists).")
    else:
        print("⚠️ No Placemarks found (Query might be empty, but KML generated).")

    # Save to file for manual inspection if needed
    with open("test_output.kml", "w", encoding="utf-8") as f:
        f.write(content)
    print("File saved to test_output.kml")

except Exception as e:
    print(f"❌ Error: {e}")
