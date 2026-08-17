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
    'host': os.getenv('DB_HOST'),
    'port': int(DB_PORT),  # Converte a porta para inteiro
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': DB_NAME,
    'connection_timeout': 10,  # Evita que a aplicação fique travada se o servidor não responder
}


DEFAULT_USER = os.getenv('DEFAULT_USER')    # Usuário padrão admin
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD')  # Senha padrão do admin


def init_db():
    try:
        # 1. Usa pool de conexões (mais rápido: reutiliza TCP/TLS handshake)
        from services.db_pool import obter_conexao as _obter_conexao
        conn = _obter_conexao()
        cursor = conn.cursor()

<<<<<<< HEAD
        # Cria o banco de dados se não existir
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        # Seleciona o banco para usar
        cursor.execute(f"USE {DB_NAME}")

        # Procura o arquivo schema.sql que define as tabelas
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "schema.sql")
        if os.path.exists(schema_path):             # Se o arquivo existe
            with open(schema_path, 'r', encoding='utf-8') as f:  # Abre o arquivo
                schema = f.read()                   # Lê todo o conteúdo SQL
                # Separa cada comando SQL pelo ";" e executa um por um
                for statement in schema.split(';'):
                    if statement.strip():           # Se o comando não está vazio
                        try:
                            cursor.execute(statement)  # Executa o comando SQL
                        except Error:
                            print(f"AVISO: Erro ao executar statement SQL (ignorado): {statement[:50]}... Erro: {Error}") # Log ignored errors

        # Verifica se já existe o usuário admin
        cursor.execute("SELECT COUNT(*) FROM usuario")
        total = cursor.fetchone()[0]                # Pega a quantidade de usuários

        # Procura o usuário admin pelo nome
        cursor.execute("SELECT nome FROM usuario WHERE nome = %s", (DEFAULT_USER,))
        existente = cursor.fetchone()               # Retorna None se não encontrou

        # Criptografa a senha do admin com SHA-256
=======
        # 2. Valida um registro legado com nome vazio/corrompido que impedia o
        # INSERT IGNORE (email duplicado) e deixava o admin nunca criado.
        EMAIL_PADRAO = os.getenv('DEFAULT_EMAIL')  # Email padrão do admin' 
>>>>>>> b35129e58331882189d6362e275b375f732cdd14
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