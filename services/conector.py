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

        cursor.execute("SELECT COUNT(*) FROM usuario")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT nome FROM usuario WHERE nome = %s", (DEFAULT_USER,))
        existente = cursor.fetchone()

        if existente:
            cursor.execute(
                "UPDATE usuario SET senha = %s, funcao = 'admin' WHERE nome = %s",
                (DEFAULT_PASSWORD, DEFAULT_USER)
            )
            print(f"Usuario '{DEFAULT_USER}' atualizado com senha do .env")
        elif total == 0:
            cursor.execute(
                """INSERT INTO usuario (nome, email, senha, telefone, tipo_usuario, funcao, status)
                   VALUES (%s, %s, %s, %s, 'bibliotecario', 'admin', 'ativo')""",
                (DEFAULT_USER, 'admin@lumen.com', DEFAULT_PASSWORD, '')
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
    try:
        cursor.execute("SELECT COUNT(*) FROM categoria")
        if cursor.fetchone()[0] > 0:
            return

        categorias = [
            ('Ficcao', 'Obras de ficcao e romance'),
            ('Nao-Ficcao', 'Obras informativas e academicas'),
            ('Infantil', 'Literatura infantil e juvenil'),
            ('Tecnico', 'Livros tecnicos e profissionais'),
            ('Historia', 'Historia e biografias'),
        ]
        for nome, desc in categorias:
            cursor.execute("INSERT IGNORE INTO categoria (nome_categoria, descricao) VALUES (%s, %s)", (nome, desc))

        autores = [
            ('Machado de Assis', 'Brasileiro'),
            ('Clarice Lispector', 'Brasileira'),
            ('Jorge Amado', 'Brasileiro'),
            ('Paulo Coelho', 'Brasileiro'),
            ('Monteiro Lobato', 'Brasileiro'),
        ]
        for nome, nac in autores:
            cursor.execute("INSERT IGNORE INTO autor (nome_autor, nacionalidade) VALUES (%s, %s)", (nome, nac))

        print("Dados de exemplo inseridos (categorias e autores)")
    except Error:
        pass
