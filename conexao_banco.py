import mysql.connector
from mysql.connector import Error

# Aqui guardamos o "endereço" e a "chave" da nossa casinha (o banco de dados)
# host: onde o banco mora
# user: o nome de quem pode entrar
# password: a senha secreta
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': ''
}

# O nome da nossa pasta mágica onde guardaremos as informações
DB_NAME = 'lumen_db'

def get_connection(with_db=True):
    """
    Essa função é como um carteiro: ela tenta abrir um caminho para conversarmos 
    com o MySQL. Se o caminho estiver livre, ela nos dá a 'chave' (conexão).
    """
    try:
        config = DB_CONFIG.copy()
        if with_db:
            # Aqui dizemos que queremos entrar especificamente na nossa pasta 'lumen_db'
            config['database'] = DB_NAME
        
        # Tenta fazer o aperto de mão com o banco de dados
        conn = mysql.connector.connect(**config)
        return conn
    except Error as e:
        # Se algo der errado (como a senha estar errada), ele avisa aqui
        print(f"Ops! Não consegui conectar: {e}")
        return None
