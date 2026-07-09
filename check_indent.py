import sys
sys.path.insert(0, '.')
with open('screen/tela_livros.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== Verificando linhas 230-240 ===")
for i, line in enumerate(lines[228:240], start=229):
    print(f"{i}: {repr(line)}")
