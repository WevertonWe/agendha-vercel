import os
import re

SKIP = {'node_modules', '.git', 'dist', 'build', '__pycache__', '.venv', 'venv', '.next'}
EXT = {'.py'}
pattern = re.compile(r'f"[^"]*(?:SELECT|INSERT|UPDATE|DELETE)[^"]*\{', re.IGNORECASE)

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        if 'nosec' in line.lower():
                            continue
                        if pattern.search(line):
                            print(f"{path}:{i}:{line.strip()}")
            except Exception:
                pass
