import mysql.connector
import os
import hashlib
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

DB_NAME = os.getenv('DB_NAME', 'biblioteca')

DEFAULT_USER = os.getenv('DEFAULT_USER', 'admin')
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD', 'admin123')


def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
                for statement in schema.split(';'):
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except Error:
                            pass

        cursor.execute("SELECT COUNT(*) FROM usuario")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT nome FROM usuario WHERE nome = %s", (DEFAULT_USER,))
        existente = cursor.fetchone()

        senha_hash = hashlib.sha256(DEFAULT_PASSWORD.encode('utf-8')).hexdigest()

        if existente:
            cursor.execute(
                "UPDATE usuario SET senha = %s, tipo_usuario = 'diretor', funcao = 'admin' WHERE nome = %s",
                (senha_hash, DEFAULT_USER)
            )
            print(f"Usuario '{DEFAULT_USER}' atualizado com senha do .env")
        elif total == 0:
            cursor.execute(
                """INSERT INTO usuario (nome, email, senha, telefone, tipo_usuario, funcao, status)
                   VALUES (%s, %s, %s, %s, 'diretor', 'admin', 'ativo')""",
                (DEFAULT_USER, 'admin@lumen.com', senha_hash, '')
            )
            print(f"Usuario padrao criado: {DEFAULT_USER}/{DEFAULT_PASSWORD}")

        _inserir_dados_exemplo(cursor)

        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return False


def _inserir_dados_exemplo(cursor):
    pass
