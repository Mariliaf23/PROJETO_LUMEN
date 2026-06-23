import os
from mysql.connector import Error
from conexao_banco import get_connection, DB_CONFIG, DB_NAME

def init_db():
    """
    Essa função é como um construtor. Ela verifica se a nossa 'casinha' (banco de dados)
    já existe. Se não existir, ela cria uma nova e arruma todos os 'móveis' (tabelas).
    """
    try:
        # Primeiro, pedimos para entrar no MySQL, mas sem escolher uma pasta ainda
        conn = get_connection(with_db=False)
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Cria a pasta mágica se ela não existir
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        # Entra na pasta mágica
        cursor.execute(f"USE {DB_NAME}")
        
        # Aqui procuramos o 'mapa' (schema.sql) para saber como montar as tabelas
        schema_path = os.path.join(os.path.dirname(__file__), "database", "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
                # Lê o mapa pedaço por pedaço e vai montando tudo
                for statement in schema.split(';'):
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except Error:
                            pass
        
        # Salva todo o trabalho feito
        conn.commit()
        # Fecha a porta ao sair
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao arrumar a casinha: {e}")
        return False


def verificar_login(usuario, senha):
    """
    Essa função é como um segurança de festa. Ela recebe o nome e a senha
    e olha na lista de convidados para ver se a pessoa pode entrar.
    """
    try:
        # Abre a porta do banco de dados
        conn = get_connection(with_db=True)
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        # Pergunta para o banco: 'Tem alguém com esse nome e essa senha?'
        cursor.execute("SELECT nome FROM usuarios WHERE nome = %s AND senha = %s", (usuario, senha))
        # O banco responde quem ele achou
        resultado = cursor.fetchone()
        
        # Fecha a porta
        conn.close()
        
        return resultado
    except Error as e:
        print(f"Erro ao conferir o convidado: {e}")
        return None
