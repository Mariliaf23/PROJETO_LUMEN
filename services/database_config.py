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


def buscar_stats_dashboard():
    stats = {'livros': 0, 'emprestimos': 0, 'alunos': 0, 'taxa_retorno': 0}
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM livro")
        stats['livros'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emprestimo")
        stats['emprestimos'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alunos")
        stats['alunos'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emprestimo WHERE status_emprestimo = 'finalizado'")
        finalizados = cursor.fetchone()[0]
        if stats['emprestimos'] > 0:
            stats['taxa_retorno'] = round((finalizados / stats['emprestimos']) * 100)

        conn.close()
    except Error:
        pass
    return stats


def buscar_emprestimos_por_mes():
    dados = []
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MONTH(lancamento) as mes, COUNT(*) as total
            FROM emprestimo
            GROUP BY MONTH(lancamento)
            ORDER BY mes
        """)
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados


def buscar_livros_por_categoria():
    dados = []
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT categoria, COUNT(*) as total FROM livro GROUP BY categoria ORDER BY total DESC")
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados


def buscar_emprestimos_semana():
    dados = []
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DAYNAME(lancamento) as dia, COUNT(*) as total
            FROM emprestimo
            WHERE YEARWEEK(lancamento) = YEARWEEK(CURDATE())
            GROUP BY DAYNAME(lancamento), DAYOFWEEK(lancamento)
            ORDER BY DAYOFWEEK(lancamento)
        """)
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados
