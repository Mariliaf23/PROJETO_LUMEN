import mysql.connector
import os
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

        cursor.execute("SELECT COUNT(*) FROM funcionario")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT nome_funcionario FROM funcionario WHERE nome_funcionario = %s", (DEFAULT_USER,))
        existente = cursor.fetchone()

        if existente:
            cursor.execute(
                "UPDATE funcionario SET password_funcionario = %s, funcao = 'admin' WHERE nome_funcionario = %s",
                (DEFAULT_PASSWORD, DEFAULT_USER)
            )
            print(f"Usuario '{DEFAULT_USER}' atualizado com senha do .env")
        elif total == 0:
            cursor.execute(
                "INSERT INTO funcionario (nome_funcionario, email_funcionario, password_funcionario, telefone_funcionario, funcao) VALUES (%s, %s, %s, %s, %s)",
                (DEFAULT_USER, 'admin@lumen.com', DEFAULT_PASSWORD, '', 'admin')
            )
            print(f"Usuario padrao criado: {DEFAULT_USER}/{DEFAULT_PASSWORD}")

        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return False