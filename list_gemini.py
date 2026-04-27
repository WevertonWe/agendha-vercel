import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(".env")
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("No GOOGLE_API_KEY found.")
    exit(1)

genai.configure(api_key=api_key)

try:
    models = genai.list_models()
    for m in models:
        if "generateContent" in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print("Error:", e)
