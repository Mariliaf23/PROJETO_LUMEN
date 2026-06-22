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


def cadastrar_livro(titulo, autor, categoria, isbn):
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO livro (titulo, autor, categoria, isbn, status_livro) VALUES (%s, %s, %s, %s, 'disponivel')",
            (titulo, autor, categoria, isbn)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar livro: {e}")
        return False


def listar_livros():
    dados = []
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT titulo, autor, categoria, isbn, status_livro FROM livro ORDER BY titulo")
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados


def listar_livros_disponiveis():
    dados = []
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id_livro, titulo FROM livro WHERE status_livro = 'disponivel' ORDER BY titulo")
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados


def editar_livro(isbn, titulo, autor, categoria):
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE livro SET titulo=%s, autor=%s, categoria=%s WHERE isbn=%s",
            (titulo, autor, categoria, isbn)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao editar livro: {e}")
        return False


def excluir_livro(isbn):
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livro WHERE isbn=%s", (isbn,))
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao excluir livro: {e}")
        return False


def listar_alunos():
    dados = []
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id_alunos, nome_aluno FROM alunos ORDER BY nome_aluno")
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados


def cadastrar_emprestimo(aluno_id, livro_id, vencimento):
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO emprestimo (lancamento, vencimento, status_emprestimo, alunos_id_alunos, funcionario_id_funcionario) VALUES (CURDATE(), %s, 'ativo', %s, 1)",
            (vencimento, aluno_id)
        )
        emp_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO emprestimo_has_livro (emprestimo_id_emprestimo, livro_id_livro) VALUES (%s, %s)",
            (emp_id, livro_id)
        )
        cursor.execute("UPDATE livro SET status_livro = 'emprestado' WHERE id_livro = %s", (livro_id,))
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar emprestimo: {e}")
        return False


def listar_emprestimos():
    dados = []
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id_emprestimo, a.nome_aluno, l.titulo, e.lancamento, e.vencimento, e.status_emprestimo
            FROM emprestimo e
            JOIN alunos a ON e.alunos_id_alunos = a.id_alunos
            JOIN emprestimo_has_livro eh ON e.id_emprestimo = eh.emprestimo_id_emprestimo
            JOIN livro l ON eh.livro_id_livro = l.id_livro
            ORDER BY e.id_emprestimo DESC
        """)
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados


def listar_emprestimos_ativos():
    dados = []
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id_emprestimo, a.nome_aluno, l.titulo, e.lancamento, e.vencimento, e.status_emprestimo
            FROM emprestimo e
            JOIN alunos a ON e.alunos_id_alunos = a.id_alunos
            JOIN emprestimo_has_livro eh ON e.id_emprestimo = eh.emprestimo_id_emprestimo
            JOIN livro l ON eh.livro_id_livro = l.id_livro
            WHERE e.status_emprestimo = 'ativo'
            ORDER BY e.vencimento ASC
        """)
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados


def finalizar_emprestimo(emp_id):
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'], user=DB_CONFIG['user'],
            password=DB_CONFIG['password'], database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE emprestimo SET status_emprestimo = 'finalizado' WHERE id_emprestimo = %s",
            (emp_id,)
        )
        cursor.execute("""
            UPDATE livro SET status_livro = 'disponivel'
            WHERE id_livro IN (
                SELECT livro_id_livro FROM emprestimo_has_livro WHERE emprestimo_id_emprestimo = %s
            )
        """, (emp_id,))
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao finalizar emprestimo: {e}")
        return False
