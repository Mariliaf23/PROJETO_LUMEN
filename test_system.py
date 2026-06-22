import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Verificando .env ===")
from dotenv import load_dotenv
load_dotenv('.env')
print(f"DEFAULT_USER: {os.getenv('DEFAULT_USER')}")
print(f"DEFAULT_PASSWORD: {os.getenv('DEFAULT_PASSWORD')}")

print("\n=== Iniciando banco (init_db) ===")
from services.conector import init_db, DEFAULT_USER, DEFAULT_PASSWORD
print(f"Constantes: DEFAULT_USER={DEFAULT_USER}, DEFAULT_PASSWORD={DEFAULT_PASSWORD}")
init_db()

print("\n=== Testando login com credenciais do .env ===")
from services.database_config import verificar_login
resultado = verificar_login(DEFAULT_USER, DEFAULT_PASSWORD)
if resultado:
    print(f"Login {DEFAULT_USER}/{DEFAULT_PASSWORD}: OK -> {resultado[0]}")
else:
    print(f"Login {DEFAULT_USER}/{DEFAULT_PASSWORD}: FALHOU")

print("\n=== Teste com credenciais erradas ===")
resultado2 = verificar_login("admin", "senha_errada")
print(f"Login admin/senha_errada: {'Rejeitado (OK)' if not resultado2 else 'ERRO'}")

print("\n=== Todos os testes OK ===")
