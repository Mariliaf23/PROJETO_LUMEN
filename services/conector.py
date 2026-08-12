# conector.py — Conecta o sistema ao banco de dados MySQL

import mysql.connector     # Biblioteca para conectar ao MySQL
import os                  # Biblioteca para manipular caminhos de arquivos
import hashlib             # Biblioteca para criptografar senhas
from dotenv import load_dotenv  # Biblioteca para ler variáveis do arquivo .env
from mysql.connector import Error  # Classe de erro do mysql.connector

# Carrega as variáveis de ambiente do arquivo .env (está na pasta raiz do projeto)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

DB_PORT = os.getenv('DB_PORT')  # Porta do MySQL como string

DB_NAME = os.getenv('DB_NAME')  # Nome do banco de dados

if not DB_PORT:
    raise ValueError("A variável de ambiente DB_PORT não está definida no arquivo .env")

# Configurações de conexão com o MySQL (lidas do arquivo .env)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(DB_PORT),  # Converte a porta para inteiro
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': DB_NAME,
    'connection_timeout': 10,  # Evita que a aplicação fique travada se o servidor não responder
}


DEFAULT_USER = os.getenv('DEFAULT_USER', 'admin')    # Usuário padrão admin
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD', 'admin123')  # Senha padrão do admin


def init_db():
    try:
        # 1. Conecta direto no banco que já existe
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 2. Valida um registro legado com nome vazio/corrompido que impedia o
        # INSERT IGNORE (email duplicado) e deixava o admin nunca criado.
        EMAIL_PADRAO = 'admin@lumen.com'
        senha_hash = hashlib.sha256(DEFAULT_PASSWORD.encode('utf-8')).hexdigest()

        # Busca por nome OU email — cobre registros legados e o caso de
        # troca de usuário/senha no .env em qualquer uma das formas
        cursor.execute(
            "SELECT id_usuario FROM usuario WHERE nome = %s OR email = %s",
            (DEFAULT_USER, EMAIL_PADRAO)
        )
        existente = cursor.fetchone()

        if existente:
            cursor.execute(
                """UPDATE usuario SET nome = %s, senha = %s, tipo_usuario = 'diretor',
                   funcao = 'admin', status = 'ativo' WHERE id_usuario = %s""",
                (DEFAULT_USER, senha_hash, existente[0])
            )
            print(f"Usuario '{DEFAULT_USER}' atualizado.")
        else:
            cursor.execute(
                """INSERT INTO usuario (nome, email, senha, telefone, tipo_usuario, funcao, status)
                   VALUES (%s, %s, %s, %s, 'diretor', 'admin', 'ativo')""",
                (DEFAULT_USER, EMAIL_PADRAO, senha_hash, '')
            )
            print(f"Usuario padrao criado.")

        conn.commit()
        conn.close()
        return True
        
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return False