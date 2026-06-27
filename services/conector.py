# conector.py — Conecta o sistema ao banco de dados MySQL

import mysql.connector     # Biblioteca para conectar ao MySQL
import os                  # Biblioteca para manipular caminhos de arquivos
import hashlib             # Biblioteca para criptografar senhas
from dotenv import load_dotenv  # Biblioteca para ler variáveis do arquivo .env
from mysql.connector import Error  # Classe de erro do mysql.connector

# Carrega as variáveis de ambiente do arquivo .env (está na pasta raiz do projeto)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Configurações de conexão com o MySQL (lidas do arquivo .env)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),       # Endereço do servidor MySQL
    'user': os.getenv('DB_USER', 'root'),            # Usuário do MySQL
    'password': os.getenv('DB_PASSWORD', '')         # Senha do MySQL
}

DB_NAME = os.getenv('DB_NAME', 'biblioteca')         # Nome do banco de dados

DEFAULT_USER = os.getenv('DEFAULT_USER', 'admin')    # Usuário padrão admin
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD', 'admin123')  # Senha padrão do admin


def init_db():
    """
    Inicializa o banco de dados:
    1. Cria o banco se não existir
    2. Cria todas as tabelas usando o schema.sql
    3. Cria ou atualiza o usuário admin padrão
    """
    try:
        # Conecta ao MySQL SEM escolher banco (para poder criar o banco)
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()                      # Cria um cursor para executar comandos SQL

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
                            pass                   # Ignora erros (ex: tabela já existe)

        # Verifica se já existe o usuário admin
        cursor.execute("SELECT COUNT(*) FROM usuario")
        total = cursor.fetchone()[0]                # Pega a quantidade de usuários

        # Procura o usuário admin pelo nome
        cursor.execute("SELECT nome FROM usuario WHERE nome = %s", (DEFAULT_USER,))
        existente = cursor.fetchone()               # Retorna None se não encontrou

        # Criptografa a senha do admin com SHA-256
        senha_hash = hashlib.sha256(DEFAULT_PASSWORD.encode('utf-8')).hexdigest()

        if existente:                               # Se o admin já existe
            # Atualiza a senha e tipo do admin com os valores do .env
            cursor.execute(
                "UPDATE usuario SET senha = %s, tipo_usuario = 'diretor', funcao = 'admin' WHERE nome = %s",
                (senha_hash, DEFAULT_USER)
            )
            print(f"Usuario '{DEFAULT_USER}' atualizado com senha do .env")
        elif total == 0:                            # Se não tem nenhum usuário no banco
            # Cria o primeiro usuário admin
            cursor.execute(
                """INSERT INTO usuario (nome, email, senha, telefone, tipo_usuario, funcao, status)
                   VALUES (%s, %s, %s, %s, 'diretor', 'admin', 'ativo')""",
                (DEFAULT_USER, 'admin@lumen.com', senha_hash, '')
            )
            print(f"Usuario padrao criado: {DEFAULT_USER}/{DEFAULT_PASSWORD}")

        _inserir_dados_exemplo(cursor)              # Insere dados de exemplo (se necessário)

        conn.commit()                               # Salva todas as alterações no banco
        conn.close()                                # Fecha a conexão
        return True                                 # Sucesso
    except Error as e:                              # Se der erro de conexão
        print(f"Erro ao conectar ao MySQL: {e}")
        return False                                # Falha


def _inserir_dados_exemplo(cursor):
    """Função placeholder para inserir dados de exemplo (vazia por enquanto)."""
    pass                                            # Não faz nada por enquanto
