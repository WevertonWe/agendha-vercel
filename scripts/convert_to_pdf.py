import os
from pathlib import Path
from PIL import Image

base_path = Path(r'C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\técnicos')
image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

converted = 0
errors = 0

print(f"Iniciando varredura em: {base_path}")

for root, _, files in os.walk(base_path):
    for file in files:
        ext = Path(file).suffix.lower()
        if ext in image_extensions:
            img_path = Path(root) / file
            pdf_path = img_path.with_suffix('.pdf')
            
            if pdf_path.exists():
                print(f"Ignorando {img_path.name} pois {pdf_path.name} ja existe.")
                continue
                
            try:
                with Image.open(img_path) as img:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(pdf_path, format='PDF', quality=100)
                
                os.remove(img_path)
                print(f"Convertido: {img_path.name} -> {pdf_path.name}")
                converted += 1
            except Exception as e:
                print(f"Erro ao converter {img_path}: {e}")
                errors += 1

print(f"\n--- Resumo ---")
print(f"Arquivos convertidos com sucesso: {converted}")
print(f"Erros encontrados: {errors}")
