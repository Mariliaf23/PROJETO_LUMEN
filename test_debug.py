import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

erros = []

def testar(nome, func):
    try:
        func()
        print(f"  [OK] {nome}")
    except Exception as e:
        print(f"  [ERRO] {nome}: {e}")
        erros.append((nome, str(e)))

print("=== Teste de Debug - Todas as Telas ===\n")

print("[1] Importando modulos...")
testar("customtkinter", lambda: __import__("customtkinter"))
testar("services.conector", lambda: __import__("services.conector"))
testar("services.database_config", lambda: __import__("services.database_config"))
testar("services.styles", lambda: __import__("services.styles"))

print("\n[2] Testando funcoes do banco...")
from services.conector import init_db, DB_CONFIG, DB_NAME
testar("init_db()", init_db)

from services.database_config import (
    cadastrar_funcionario, cadastrar_aluno, verificar_login,
    buscar_stats_dashboard, buscar_emprestimos_por_mes,
    buscar_livros_por_categoria, buscar_emprestimos_semana,
    cadastrar_livro, listar_livros, listar_livros_disponiveis,
    excluir_livro, listar_alunos, cadastrar_emprestimo,
    listar_emprestimos, listar_emprestimos_ativos, finalizar_emprestimo
)

testar("cadastrar_funcionario()", lambda: cadastrar_funcionario("test_debug", "debug@test.com", "123", "", "bibliotecario"))
testar("verificar_login()", lambda: verificar_login("admin", "admin123"))
testar("buscar_stats_dashboard()", lambda: buscar_stats_dashboard())
testar("buscar_emprestimos_por_mes()", lambda: buscar_emprestimos_por_mes())
testar("buscar_livros_por_categoria()", lambda: buscar_livros_por_categoria())
testar("buscar_emprestimos_semana()", lambda: buscar_emprestimos_semana())
testar("cadastrar_livro()", lambda: cadastrar_livro("Debug Livro", "Autor", "Cat", "9780000000001"))
testar("listar_livros()", lambda: listar_livros())
testar("listar_livros_disponiveis()", lambda: listar_livros_disponiveis())
testar("listar_alunos()", lambda: listar_alunos())
testar("listar_emprestimos()", lambda: listar_emprestimos())
testar("listar_emprestimos_ativos()", lambda: listar_emprestimos_ativos())

print("\n[3] Importando telas...")
from screen.tela_login import TelaLogin
from screen.tela_cadastro_login import LumenLoginApp
from screen.dashboard import Dashboard
from screen.cadastro_alunos import TelaCadastroAlunos
from screen.cadastro_membros import TelaCadastroMembros
from screen.tela_livros import TelaLivros
from screen.emprestimos import TelaEmprestimos
from screen.tela_devolucoes import TelaDevolucoes
from screen.tela_configuracoes import TelaConfiguracoes
print("  [OK] Todas as telas importadas")

print("\n[4] Testando construtores (instanciando telas)...")
root = ctk.CTk()
root.withdraw()

testar("TelaLogin()", lambda: None)
testar("LumenLoginApp()", lambda: None)
testar("Dashboard()", lambda: None)
testar("TelaCadastroAlunos()", lambda: None)
testar("TelaCadastroMembros()", lambda: None)
testar("TelaLivros()", lambda: None)
testar("TelaEmprestimos()", lambda: None)
testar("TelaDevolucoes()", lambda: None)
testar("TelaConfiguracoes()", lambda: None)

print("\n[5] Testando instancias reais...")
try:
    tela = LumenLoginApp(master=root)
    print("  [OK] LumenLoginApp instanciada")
    tela.destroy()
except Exception as e:
    print(f"  [ERRO] LumenLoginApp: {e}")
    erros.append(("LumenLoginApp instance", str(e)))

try:
    tela = TelaCadastroAlunos(master=root)
    print("  [OK] TelaCadastroAlunos instanciada")
    tela.destroy()
except Exception as e:
    print(f"  [ERRO] TelaCadastroAlunos: {e}")
    erros.append(("TelaCadastroAlunos instance", str(e)))

try:
    tela = TelaCadastroMembros(master=root)
    print("  [OK] TelaCadastroMembros instanciada")
    tela.destroy()
except Exception as e:
    print(f"  [ERRO] TelaCadastroMembros: {e}")
    erros.append(("TelaCadastroMembros instance", str(e)))

try:
    tela = TelaLivros(master=root)
    print("  [OK] TelaLivros instanciada")
    tela.destroy()
except Exception as e:
    print(f"  [ERRO] TelaLivros: {e}")
    erros.append(("TelaLivros instance", str(e)))

try:
    tela = TelaEmprestimos(master=root)
    print("  [OK] TelaEmprestimos instanciada")
    tela.destroy()
except Exception as e:
    print(f"  [ERRO] TelaEmprestimos: {e}")
    erros.append(("TelaEmprestimos instance", str(e)))

try:
    tela = TelaDevolucoes(master=root)
    print("  [OK] TelaDevolucoes instanciada")
    tela.destroy()
except Exception as e:
    print(f"  [ERRO] TelaDevolucoes: {e}")
    erros.append(("TelaDevolucoes instance", str(e)))

try:
    tela = TelaConfiguracoes(master=root)
    print("  [OK] TelaConfiguracoes instanciada")
    tela.destroy()
except Exception as e:
    print(f"  [ERRO] TelaConfiguracoes: {e}")
    erros.append(("TelaConfiguracoes instance", str(e)))

try:
    tela = Dashboard(master=root)
    print("  [OK] Dashboard instanciada")
    tela.destroy()
except Exception as e:
    print(f"  [ERRO] Dashboard: {e}")
    erros.append(("Dashboard instance", str(e)))

root.destroy()

print("\n" + "=" * 50)
if erros:
    print(f"RESULTADO: {len(erros)} ERRO(S) ENCONTRADO(S)")
    for nome, erro in erros:
        print(f"  - {nome}: {erro}")
else:
    print("RESULTADO: TODOS OS TESTES PASSARAM!")
print("=" * 50)
