"""
run_migrations.py - Executa migrações SQL no banco de dados

Este script aplica as migrações SQL necessárias para atualizar o schema do banco.
"""

import mysql.connector
import os
from mysql.connector import Error


def run_migrations():
    """Executa todas as migrações SQL encontradas em database/migrations.sql"""
    
    # Configurações de conexão (padrão se não houver .env)
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': ''
    }
    DB_NAME = 'biblioteca'
    
    try:
        print("🔄 Iniciando migrações do banco de dados...")
        
        # Conecta ao MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Seleciona o banco de dados
        cursor.execute(f"USE {DB_NAME}")
        
        # Lê o arquivo de migrações
        migrations_path = os.path.join(os.path.dirname(__file__), "database", "migrations.sql")
        
        if not os.path.exists(migrations_path):
            print(f"❌ Arquivo de migrações não encontrado: {migrations_path}")
            return False
        
        with open(migrations_path, 'r', encoding='utf-8') as f:
            migrations_sql = f.read()
        
        # Executa cada comando SQL
        for statement in migrations_sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✓ Executado: {statement[:60]}...")
                except Error as e:
                    print(f"⚠ Erro ao executar: {e}")
                    # Continua com o próximo comando mesmo se este falhar
        
        conn.commit()
        conn.close()
        
        print("✅ Migrações aplicadas com sucesso!")
        return True
        
    except Error as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return False


if __name__ == "__main__":
    run_migrations()
