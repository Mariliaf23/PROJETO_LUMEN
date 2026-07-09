import sys
sys.path.insert(0, '.')
with open('screen/tela_livros.py', 'r', encoding='utf-8') as f:
    c = f.readlines()

print("=== Verificando botao de teste ===")
for i, line in enumerate(c[160:200], start=161):
    if 'btn_teste' in line or 'btn_excluir' in line or 'btn_atualizar' in line:
        print(f"Linha {i}: {line.rstrip()}")

print("\n=== Verificando _carregar_tabela ===")
for i, line in enumerate(c, start=1):
    if '_carregar_tabela' in line:
        print(f"Linha {i}: {line.rstrip()}")

print("\n=== Verificando _criar_item ===")
for i, line in enumerate(c, start=1):
    if '_criar_item' in line:
        print(f"Linha {i}: {line.rstrip()}")

print("\n=== Verificando place() em _criar_item ===")
for i, line in enumerate(c, start=1):
    if 'item.place' in line:
        print(f"Linha {i}: {line.rstrip()}")
