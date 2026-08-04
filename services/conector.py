# conector.py — Conecta o sistema ao banco de dados MySQL

import mysql.connector     # Biblioteca para conectar ao MySQL
import os                  # Biblioteca para manipular caminhos de arquivos
import hashlib             # Biblioteca para criptografar senhas
from dotenv import load_dotenv  # Biblioteca para ler variáveis do arquivo .env
from mysql.connector import Error  # Classe de erro do mysql.connector

# Carrega as variáveis de ambiente do arquivo .env (está na pasta raiz do projeto)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

port_str = os.getenv('DB_PORT')  # Porta do MySQL como string

DB_NAME = os.getenv('DB_NAME', '') # Nome do banco de dados

if not port_str:
    raise ValueError("A variável de ambiente DB_PORT não está definida no arquivo .env")

# Configurações de conexão com o MySQL (lidas do arquivo .env)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(port_str),  # Converte a porta para inteiro
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': DB_NAME
}


DEFAULT_USER = os.getenv('DEFAULT_USER', 'admin')    # Usuário padrão admin
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD', 'admin123')  # Senha padrão do admin

def init_db():
    try:
        # 1. Conecta direto no banco que já existe
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 2. Vai direto para a lógica de inserir/atualizar o usuário
        cursor.execute("SELECT nome FROM usuario WHERE nome = %s", (DEFAULT_USER,))
        existente = cursor.fetchone()

        senha_hash = hashlib.sha256(DEFAULT_PASSWORD.encode('utf-8')).hexdigest()

        if existente:
            cursor.execute(
                "UPDATE usuario SET senha = %s, tipo_usuario = 'diretor', funcao = 'admin' WHERE nome = %s",
                (senha_hash, DEFAULT_USER)
            )
            print(f"Usuario '{DEFAULT_USER}' atualizado.")
        else:
            cursor.execute(
                """INSERT IGNORE INTO usuario (nome, email, senha, telefone, tipo_usuario, funcao, status)
                   VALUES (%s, %s, %s, %s, 'diretor', 'admin', 'ativo')""",
                (DEFAULT_USER, 'admin@lumen.com', senha_hash, '')
            )
            print(f"Usuario padrao criado.")

        conn.commit()
        conn.close()
        return True
        
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return False