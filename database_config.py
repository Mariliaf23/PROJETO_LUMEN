# database_config.py (raiz) — ARQUIVO LEGADO (não utilizado)
# O sistema agora usa services/database_config.py para operações no banco.
# Este arquivo foi mantido apenas por referência.

import os
from mysql.connector import Error
from conexao_banco import get_connection, DB_CONFIG, DB_NAME


def init_db():
    """Função legada para inicializar o banco de dados."""
    try:
        conn = get_connection(with_db=False)       # Conecta sem banco
        if not conn:
            return False
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")  # Cria o banco
        cursor.execute(f"USE {DB_NAME}")           # Usa o banco

        # Procura e executa o schema SQL
        schema_path = os.path.join(os.path.dirname(__file__), "database", "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
                for statement in schema.split(';'):
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except Error:
                            pass

        conn.commit()                              # Salva alterações
        conn.close()                               # Fecha conexão
        return True
    except Error as e:
        print(f"Erro ao arrumar a casinha: {e}")
        return False


def verificar_login(usuario, senha):
    """Função legada para verificar login."""
    try:
        conn = get_connection(with_db=True)         # Conecta ao banco
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE nome = %s AND senha = %s", (usuario, senha))
        resultado = cursor.fetchone()              # Busca o usuário
        conn.close()                               # Fecha conexão
        return resultado
    except Error as e:
        print(f"Erro ao conferir o convidado: {e}")
        return None
