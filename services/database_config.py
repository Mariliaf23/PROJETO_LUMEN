import mysql.connector
from mysql.connector import Error
from services.conector import DB_CONFIG, DB_NAME


def _conectar():
    return mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_NAME
    )


# ======================== AUTENTICACAO ========================

def verificar_login(usuario, senha):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_usuario, nome, tipo_usuario FROM usuario WHERE nome = %s AND senha = %s AND status = 'ativo'",
            (usuario, senha)
        )
        resultado = cursor.fetchone()
        conn.close()
        return resultado
    except Error as e:
        print(f"Erro ao verificar login: {e}")
        return None


def cadastrar_usuario(nome, email, senha, telefone='', cpf='', tipo='aluno',
                      matricula='', sala='', turno='', funcao=''):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO usuario (nome, email, senha, telefone, cpf, tipo_usuario,
               matricula, sala, turno, funcao)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (nome, email, senha, telefone or None, cpf or None, tipo,
             matricula or None, sala or None, turno or None, funcao or None)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar usuario: {e}")
        return False


def listar_usuarios(tipo=None):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        if tipo:
            cursor.execute(
                "SELECT id_usuario, nome, email, tipo_usuario, status FROM usuario WHERE tipo_usuario = %s ORDER BY nome",
                (tipo,)
            )
        else:
            cursor.execute("SELECT id_usuario, nome, email, tipo_usuario, status FROM usuario ORDER BY nome")
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def listar_alunos():
    return listar_usuarios(tipo='aluno')


def listar_funcionarios():
    return listar_usuarios(tipo='funcionario')


# ======================== CATEGORIA ========================

def cadastrar_categoria(nome, descricao=''):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categoria (nome_categoria, descricao) VALUES (%s, %s)",
            (nome, descricao or None)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar categoria: {e}")
        return False


def listar_categorias():
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_categoria, nome_categoria FROM categoria ORDER BY nome_categoria")
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


# ======================== AUTOR ========================

def cadastrar_autor(nome, nacionalidade=''):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO autor (nome_autor, nacionalidade) VALUES (%s, %s)",
            (nome, nacionalidade or None)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar autor: {e}")
        return False


def listar_autores():
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_autor, nome_autor FROM autor ORDER BY nome_autor")
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def listar_autores_livro(id_livro):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT a.id_autor, a.nome_autor FROM autor a
               JOIN livro_autor la ON a.id_autor = la.id_autor
               WHERE la.id_livro = %s ORDER BY a.nome_autor""",
            (id_livro,)
        )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def associar_autor_livro(id_livro, id_autor):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT IGNORE INTO livro_autor (id_livro, id_autor) VALUES (%s, %s)",
            (id_livro, id_autor)
        )
        conn.commit()
        conn.close()
        return True
    except Error:
        return False


def desassociar_autor_livro(id_livro, id_autor):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livro_autor WHERE id_livro = %s AND id_autor = %s", (id_livro, id_autor))
        conn.commit()
        conn.close()
        return True
    except Error:
        return False


# ======================== LIVRO ========================

def cadastrar_livro(titulo, isbn, id_categoria, editora='', ano_publicacao=None, sinopse=''):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO livro (titulo, isbn, editora, ano_publicacao, sinopse, id_categoria)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (titulo, isbn, editora or None, ano_publicacao, sinopse or None, id_categoria)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar livro: {e}")
        return False


def listar_livros():
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT l.id_livro, l.titulo, l.isbn, c.nome_categoria, l.editora, l.ano_publicacao, l.status_livro
               FROM livro l
               JOIN categoria c ON l.id_categoria = c.id_categoria
               ORDER BY l.titulo"""
        )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def listar_livros_disponiveis():
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT l.id_livro, l.titulo FROM livro l
               WHERE l.id_livro IN (SELECT id_livro FROM exemplar WHERE status_exemplar = 'disponivel')
               ORDER BY l.titulo"""
        )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def excluir_livro(id_livro):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livro WHERE id_livro = %s", (id_livro,))
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao excluir livro: {e}")
        return False


def buscar_livro_por_id(id_livro):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT l.id_livro, l.titulo, l.isbn, l.id_categoria, l.editora, l.ano_publicacao, l.sinopse
               FROM livro l WHERE l.id_livro = %s""",
            (id_livro,)
        )
        dados = cursor.fetchone()
        conn.close()
        return dados
    except Error:
        return None


# ======================== EXEMPLAR ========================

def cadastrar_exemplar(codigo_patrimonio, id_livro, localizacao=''):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO exemplar (codigo_patrimonio, id_livro, localizacao) VALUES (%s, %s, %s)",
            (codigo_patrimonio, id_livro, localizacao or None)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar exemplar: {e}")
        return False


def listar_exemplares(id_livro=None):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        if id_livro:
            cursor.execute(
                """SELECT e.id_exemplar, e.codigo_patrimonio, e.status_exemplar, e.localizacao, l.titulo
                   FROM exemplar e JOIN livro l ON e.id_livro = l.id_livro
                   WHERE e.id_livro = %s ORDER BY e.codigo_patrimonio""",
                (id_livro,)
            )
        else:
            cursor.execute(
                """SELECT e.id_exemplar, e.codigo_patrimonio, e.status_exemplar, e.localizacao, l.titulo
                   FROM exemplar e JOIN livro l ON e.id_livro = l.id_livro
                   ORDER BY l.titulo, e.codigo_patrimonio"""
            )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def listar_exemplares_disponiveis(id_livro=None):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        if id_livro:
            cursor.execute(
                """SELECT e.id_exemplar, e.codigo_patrimonio FROM exemplar e
                   WHERE e.id_livro = %s AND e.status_exemplar = 'disponivel' ORDER BY e.codigo_patrimonio""",
                (id_livro,)
            )
        else:
            cursor.execute(
                """SELECT e.id_exemplar, e.codigo_patrimonio, l.titulo FROM exemplar e
                   JOIN livro l ON e.id_livro = l.id_livro
                   WHERE e.status_exemplar = 'disponivel' ORDER BY l.titulo"""
            )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def atualizar_status_exemplar(id_exemplar, status):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE exemplar SET status_exemplar = %s WHERE id_exemplar = %s", (status, id_exemplar))
        conn.commit()
        conn.close()
        return True
    except Error:
        return False


def excluir_exemplar(id_exemplar):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM exemplar WHERE id_exemplar = %s", (id_exemplar,))
        conn.commit()
        conn.close()
        return True
    except Error:
        return False


# ======================== EMPRESTIMO ========================

def cadastrar_emprestimo(id_usuario, id_exemplar, data_prevista, id_funcionario):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO emprestimo (data_emprestimo, data_prevista, status, id_usuario, id_exemplar, id_funcionario)
               VALUES (CURDATE(), %s, 'ativo', %s, %s, %s)""",
            (data_prevista, id_usuario, id_exemplar, id_funcionario)
        )
        cursor.execute("UPDATE exemplar SET status_exemplar = 'emprestado' WHERE id_exemplar = %s", (id_exemplar,))
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar emprestimo: {e}")
        return False


def listar_emprestimos():
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT e.id_emprestimo, u.nome, ex.codigo_patrimonio, l.titulo,
                      e.data_emprestimo, e.data_prevista, e.data_devolucao, e.status
               FROM emprestimo e
               JOIN usuario u ON e.id_usuario = u.id_usuario
               JOIN exemplar ex ON e.id_exemplar = ex.id_exemplar
               JOIN livro l ON ex.id_livro = l.id_livro
               ORDER BY e.id_emprestimo DESC"""
        )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def listar_emprestimos_ativos():
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT e.id_emprestimo, u.nome, ex.codigo_patrimonio, l.titulo,
                      e.data_emprestimo, e.data_prevista, e.status
               FROM emprestimo e
               JOIN usuario u ON e.id_usuario = u.id_usuario
               JOIN exemplar ex ON e.id_exemplar = ex.id_exemplar
               JOIN livro l ON ex.id_livro = l.id_livro
               WHERE e.status IN ('ativo', 'atrasado')
               ORDER BY e.data_prevista ASC"""
        )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def finalizar_emprestimo(id_emprestimo):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE emprestimo SET status = 'finalizado', data_devolucao = CURDATE() WHERE id_emprestimo = %s",
            (id_emprestimo,)
        )
        cursor.execute(
            """UPDATE exemplar SET status_exemplar = 'disponivel'
               WHERE id_exemplar = (SELECT id_exemplar FROM emprestimo WHERE id_emprestimo = %s)""",
            (id_emprestimo,)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao finalizar emprestimo: {e}")
        return False


def verificar_atrasos():
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE emprestimo SET status = 'atrasado'
               WHERE status = 'ativo' AND data_prevista < CURDATE()"""
        )
        conn.commit()
        conn.close()
        return True
    except Error:
        return False


# ======================== RESERVA ========================

def cadastrar_reserva(id_usuario, id_livro, dias_validade=7):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO reserva (data_reserva, data_validade, status, id_usuario, id_livro)
               VALUES (CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s DAY), 'ativa', %s, %s)""",
            (dias_validade, id_usuario, id_livro)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar reserva: {e}")
        return False


def listar_reservas(status=None):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        if status:
            cursor.execute(
                """SELECT r.id_reserva, u.nome, l.titulo, r.data_reserva, r.data_validade, r.status
                   FROM reserva r
                   JOIN usuario u ON r.id_usuario = u.id_usuario
                   JOIN livro l ON r.id_livro = l.id_livro
                   WHERE r.status = %s ORDER BY r.data_reserva DESC""",
                (status,)
            )
        else:
            cursor.execute(
                """SELECT r.id_reserva, u.nome, l.titulo, r.data_reserva, r.data_validade, r.status
                   FROM reserva r
                   JOIN usuario u ON r.id_usuario = u.id_usuario
                   JOIN livro l ON r.id_livro = l.id_livro
                   ORDER BY r.data_reserva DESC"""
            )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def cancelar_reserva(id_reserva):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE reserva SET status = 'cancelada' WHERE id_reserva = %s", (id_reserva,))
        conn.commit()
        conn.close()
        return True
    except Error:
        return False


# ======================== MULTA ========================

def gerar_multa(id_emprestimo, dias_atraso, motivo='atraso'):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        valor = dias_atraso * 2.00
        cursor.execute(
            """INSERT INTO multa (valor, dias_atraso, motivo, status_pagamento, data_geracao, id_emprestimo)
               VALUES (%s, %s, %s, 'pendente', CURDATE(), %s)""",
            (valor, dias_atraso, motivo, id_emprestimo)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao gerar multa: {e}")
        return False


def listar_multas(status=None):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        if status:
            cursor.execute(
                """SELECT m.id_multa, m.valor, m.dias_atraso, m.motivo, m.status_pagamento,
                          m.data_geracao, u.nome, l.titulo
                   FROM multa m
                   JOIN emprestimo e ON m.id_emprestimo = e.id_emprestimo
                   JOIN usuario u ON e.id_usuario = u.id_usuario
                   JOIN exemplar ex ON e.id_exemplar = ex.id_exemplar
                   JOIN livro l ON ex.id_livro = l.id_livro
                   WHERE m.status_pagamento = %s ORDER BY m.data_geracao DESC""",
                (status,)
            )
        else:
            cursor.execute(
                """SELECT m.id_multa, m.valor, m.dias_atraso, m.motivo, m.status_pagamento,
                          m.data_geracao, u.nome, l.titulo
                   FROM multa m
                   JOIN emprestimo e ON m.id_emprestimo = e.id_emprestimo
                   JOIN usuario u ON e.id_usuario = u.id_usuario
                   JOIN exemplar ex ON e.id_exemplar = ex.id_exemplar
                   JOIN livro l ON ex.id_livro = l.id_livro
                   ORDER BY m.data_geracao DESC"""
            )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def pagar_multa(id_multa):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE multa SET status_pagamento = 'pago' WHERE id_multa = %s", (id_multa,))
        conn.commit()
        conn.close()
        return True
    except Error:
        return False


def usuario_tem_multa_pendente(id_usuario):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT COUNT(*) FROM multa m
               JOIN emprestimo e ON m.id_emprestimo = e.id_emprestimo
               WHERE e.id_usuario = %s AND m.status_pagamento = 'pendente'""",
            (id_usuario,)
        )
        total = cursor.fetchone()[0]
        conn.close()
        return total > 0
    except Error:
        return False


# ======================== DASHBOARD ========================

def buscar_stats_dashboard():
    stats = {'livros': 0, 'emprestimos': 0, 'usuarios': 0, 'taxa_retorno': 0}
    try:
        conn = _conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM livro")
        stats['livros'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emprestimo")
        stats['emprestimos'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuario WHERE tipo_usuario = 'aluno'")
        stats['usuarios'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emprestimo WHERE status = 'finalizado'")
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
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT MONTH(data_emprestimo) as mes, COUNT(*) as total
               FROM emprestimo GROUP BY MONTH(data_emprestimo) ORDER BY mes"""
        )
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados


def buscar_livros_por_categoria():
    dados = []
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT c.nome_categoria, COUNT(*) as total
               FROM livro l JOIN categoria c ON l.id_categoria = c.id_categoria
               GROUP BY c.nome_categoria ORDER BY total DESC"""
        )
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados


def buscar_emprestimos_semana():
    dados = []
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT DAYNAME(data_emprestimo) as dia, COUNT(*) as total
               FROM emprestimo
               WHERE YEARWEEK(data_emprestimo) = YEARWEEK(CURDATE())
               GROUP BY DAYNAME(data_emprestimo), DAYOFWEEK(data_emprestimo)
               ORDER BY DAYOFWEEK(data_emprestimo)"""
        )
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados

# ======================== USUARIO — CRUD COMPLETO ========================
# Adicione estas funções ao seu services/database_config.py

def cadastrar_usuario(nome, email, senha, telefone='', cpf='', tipo='aluno',
                      matricula='', sala='', turno='', funcao=''):
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO usuario (nome, email, senha, telefone, cpf, tipo_usuario,
               matricula, sala, turno, funcao)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (nome, email, senha, telefone or None, cpf or None, tipo,
             matricula or None, sala or None, turno or None, funcao or None)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar usuario: {e}")
        return False


def listar_usuarios(tipo=None, status=None):
    """Retorna lista de usuários com filtros opcionais por tipo e status."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        base = """SELECT id_usuario, nome, email, telefone, cpf,
                         tipo_usuario, matricula, sala, turno, funcao, status
                  FROM usuario"""
        condicoes = []
        valores = []

        if tipo:
            condicoes.append("tipo_usuario = %s")
            valores.append(tipo)
        if status:
            condicoes.append("status = %s")
            valores.append(status)

        if condicoes:
            base += " WHERE " + " AND ".join(condicoes)
        base += " ORDER BY nome"

        cursor.execute(base, valores)
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def buscar_usuario_por_id(id_usuario):
    """Retorna todos os campos de um usuário pelo ID."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id_usuario, nome, email, telefone, cpf,
                      tipo_usuario, matricula, sala, turno, funcao, status
               FROM usuario WHERE id_usuario = %s""",
            (id_usuario,)
        )
        dado = cursor.fetchone()
        conn.close()
        return dado
    except Error:
        return None


def atualizar_usuario(id_usuario, nome, email, telefone='', cpf='', tipo='aluno',
                      matricula='', sala='', turno='', funcao='', status='ativo'):
    """Atualiza todos os campos editáveis de um usuário (exceto senha)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE usuario
               SET nome=%s, email=%s, telefone=%s, cpf=%s, tipo_usuario=%s,
                   matricula=%s, sala=%s, turno=%s, funcao=%s, status=%s
               WHERE id_usuario=%s""",
            (nome, email, telefone or None, cpf or None, tipo,
             matricula or None, sala or None, turno or None, funcao or None,
             status, id_usuario)
        )
        conn.commit()
        alterado = cursor.rowcount > 0
        conn.close()
        return alterado
    except Error as e:
        print(f"Erro ao atualizar usuario: {e}")
        return False


def atualizar_senha_usuario(id_usuario, nova_senha):
    """Atualiza apenas a senha de um usuário."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET senha=%s WHERE id_usuario=%s",
            (nova_senha, id_usuario)
        )
        conn.commit()
        alterado = cursor.rowcount > 0
        conn.close()
        return alterado
    except Error as e:
        print(f"Erro ao atualizar senha: {e}")
        return False


def alternar_status_usuario(id_usuario):
    """Alterna o status do usuário entre 'ativo' e 'inativo'."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE usuario
               SET status = CASE WHEN status='ativo' THEN 'inativo' ELSE 'ativo' END
               WHERE id_usuario=%s""",
            (id_usuario,)
        )
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao alternar status: {e}")
        return False


def excluir_usuario(id_usuario):
    """
    Remove o usuário permanentemente.
    Use com cuidado: prefira alternar_status_usuario para desativar.
    Falha se o usuário possuir empréstimos vinculados (FK).
    """
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario WHERE id_usuario=%s", (id_usuario,))
        conn.commit()
        removido = cursor.rowcount > 0
        conn.close()
        return removido
    except Error as e:
        print(f"Erro ao excluir usuario: {e}")
        return False


def buscar_usuarios_por_nome(termo):
    """Busca usuários cujo nome contenha o termo informado (case-insensitive)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id_usuario, nome, email, tipo_usuario, status
               FROM usuario
               WHERE nome LIKE %s
               ORDER BY nome""",
            (f"%{termo}%",)
        )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


# Atalhos por tipo (mantém compatibilidade com código existente)
def listar_alunos():
    return listar_usuarios(tipo='aluno')


def listar_professores():
    return listar_usuarios(tipo='professor')


def listar_funcionarios():
    return listar_usuarios(tipo='funcionario')