import mysql.connector
import os
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': ''
}

DB_NAME = 'biblioteca'


def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                senha VARCHAR(255) NOT NULL
            )
        """)
        
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
        
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return False


def verificar_login(usuario, senha):
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT nome FROM usuarios WHERE nome = %s AND senha = %s", (usuario, senha))
        resultado = cursor.fetchone()
        
        conn.close()
        
        return resultado
    except Error as e:
        print(f"Erro ao verificar login: {e}")
        return None
