import os
from PIL import Image

base = "app/static/imagens"
if os.path.exists(base):
    for f in os.listdir(base):
        if f.startswith("logo-") and f.endswith(("jpg", "jpeg", "png")):
            caminho_orig = os.path.join(base, f)
            nome_base = f.split(".")[0]
            caminho_dest = os.path.join(base, f"{nome_base}.webp")
            try:
                img = Image.open(caminho_orig).convert("RGB")
                img.save(caminho_dest, "WEBP", quality=80)
                print(f"Convertido: {caminho_dest} ({os.path.getsize(caminho_dest)} bytes)")
            except Exception as e:
                print(f"Erro ao converter {f}: {e}")
print("Finalizado.")
