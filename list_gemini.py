import os
from google import genai
from dotenv import load_dotenv

load_dotenv(".env")
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("No GOOGLE_API_KEY found.")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    # No novo SDK, a listagem de modelos é feita via client.models.list()
    for m in client.models.list():
        # Verificamos se o modelo suporta geração de conteúdo
        if "generateContent" in m.supported_generation_methods:
            print(f"Modelo: {m.name} | Display: {m.display_name}")
except Exception as e:
    print("Error:", e)
