# conexao_banco.py — ARQUIVO LEGADO (não utilizado)
# O sistema agora usa services/conector.py para conexão com o banco.
# Este arquivo foi mantido apenas por referência.

import mysql.connector
from mysql.connector import Error

# Configurações de conexão (legado)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': ''
}

# Nome do banco de dados
DB_NAME = 'lumen_db'


def get_connection(with_db=True):
    """Cria uma conexão com o MySQL (função legada)."""
    try:
        config = DB_CONFIG.copy()                # Cópia das configurações
        if with_db:                              # Se quer conectar a um banco específico
            config['database'] = DB_NAME         # Adiciona o nome do banco
        conn = mysql.connector.connect(**config)  # Tenta conectar
        return conn                              # Retorna a conexão
    except Error as e:                           # Se der erro
        print(f"Ops! Não consegui conectar: {e}")
        return None                              # Retorna None
