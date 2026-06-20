import mysql.connector
from mysql.connector import Error
from services.conector import DB_CONFIG, DB_NAME


def cadastrar_funcionario(nome, email, senha, telefone='', funcao='bibliotecario'):
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO funcionario (nome_funcionario, email_funcionario, password_funcionario, telefone_funcionario, funcao) VALUES (%s, %s, %s, %s, %s)",
            (nome, email, senha, telefone, funcao)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar funcionário: {e}")
        return False


def cadastrar_aluno(nome, email, telefone, cpf, sala, turno):
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alunos (nome_aluno, email_aluno, password_aluno, telefone_aluno, cpf, sala, turno) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (nome, email, '', telefone, cpf, sala, turno)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar aluno: {e}")
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

        cursor.execute("SELECT nome_funcionario FROM funcionario WHERE nome_funcionario = %s AND password_funcionario = %s", (usuario, senha))
        resultado = cursor.fetchone()

        conn.close()

        return resultado
    except Error as e:
        print(f"Erro ao verificar login: {e}")
        return None
