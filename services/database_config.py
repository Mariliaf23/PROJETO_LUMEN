# database_config.py — Camada de acesso ao banco de dados (todas as operações SQL)

import mysql.connector     # Biblioteca para conectar ao MySQL
import hashlib             # Biblioteca para criptografar senhas
from mysql.connector import Error  # Tipo de erro do MySQL
from services.conector import DB_CONFIG, DB_NAME  # Configurações de conexão do conector


def _conectar():
    """Cria e retorna uma conexão com o banco de dados MySQL."""
    return mysql.connector.connect(
        host=DB_CONFIG['host'],         # Endereço do servidor (ex: localhost)
        user=DB_CONFIG['user'],         # Usuário do MySQL
        password=DB_CONFIG['password'], # Senha do MySQL
        database=DB_NAME               # Nome do banco (ex: biblioteca)
    )


# ======================== AUTENTICAÇÃO ========================

def _hash_senha(senha):
    """Criptografa a senha usando SHA-256 (nunca salvar senha em texto puro!)."""
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()  # Converte para hash hexadecimal


def verificar_login(usuario, senha):
    """Verifica se o usuário e senha estão corretos no banco. Retorna (id, nome, tipo) ou None."""
    try:
        conn = _conectar()                      # Abre conexão com o banco
        cursor = conn.cursor()                  # Cria cursor para executar SQL
        senha_hash = _hash_senha(senha)          # Criptografa a senha informada

        # Busca o usuário por nome, email ou matricula — e verifica se a senha confere
        cursor.execute(
            """SELECT id_usuario, nome, tipo_usuario FROM usuario
               WHERE (nome = %s OR email = %s OR matricula = %s) AND senha = %s AND status = 'ativo'""",
            (usuario, usuario, usuario, senha_hash)  # 4 parâmetros para busca
        )
        resultado = cursor.fetchone()           # Pega o primeiro resultado (ou None)
        conn.close()                            # Fecha a conexão
        return resultado                        # Retorna os dados do usuário
    except Error as e:                          # Se der erro
        print(f"Erro ao verificar login: {e}")
        return None                             # Retorna None (falha)


def cadastrar_usuario(nome, email, senha, telefone='', cpf='', tipo='aluno',
                      matricula='', turma='', turno='', funcao=''):
    """Cadastra um novo usuário no banco de dados. Retorna True se deu certo."""
    try:
        conn = _conectar()                      # Abre conexão
        cursor = conn.cursor()
        senha_hash = _hash_senha(senha) if senha else ''  # Criptografa senha (ou vazio)

        # Insere o novo usuário na tabela
        cursor.execute(
            """INSERT INTO usuario (nome, email, senha, telefone, cpf, tipo_usuario,
               matricula, turma, turno, funcao)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (nome, email, senha_hash, telefone or None, cpf or None, tipo,
             matricula or None, turma or None, turno or None, funcao or None)
        )
        conn.commit()                           # Salva no banco
        conn.close()                            # Fecha conexão
        return True                             # Sucesso
    except Error as e:                          # Se der erro (ex: email duplicado)
        print(f"Erro ao cadastrar usuario: {e}")
        return False                            # Falha


def listar_alunos():
    """Lista todos os alunos e professores ativos. Retorna lista de (id, nome, email, tipo, status)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        # Seleciona apenas alunos e professores com status ativo
        cursor.execute(
            "SELECT id_usuario, nome, email, tipo_usuario, status FROM usuario WHERE tipo_usuario IN ('aluno', 'professor') AND status = 'ativo' ORDER BY nome"
        )
        resultados = cursor.fetchall()          # Pega todos os resultados
        conn.close()
        return resultados                       # Retorna a lista
    except Error as e:
        print(f"Erro ao listar alunos: {e}")
        return []                               # Retorna lista vazia em caso de erro


def listar_bibliotecarios():
    """Lista todos os bibliotecários (delega para listar_usuarios com filtro)."""
    return listar_usuarios(tipo='bibliotecario')  # Chama listar_usuarios filtrando por tipo


# ======================== CATEGORIA ========================

def cadastrar_categoria(nome, descricao=''):
    """Cadastra uma nova categoria de livro. Retorna True se deu certo."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categoria (nome_categoria, descricao) VALUES (%s, %s)",
            (nome, descricao or None)           # Descrição pode ser vazia
        )
        conn.commit()                           # Salva no banco
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar categoria: {e}")
        return False


def listar_categorias():
    """Lista todas as categorias ordenadas por nome. Retorna lista de (id, nome)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_categoria, nome_categoria FROM categoria ORDER BY nome_categoria")
        dados = cursor.fetchall()               # Pega todos os resultados
        conn.close()
        return dados
    except Error:
        return []                               # Lista vazia em caso de erro


# ======================== AUTOR ========================

def cadastrar_autor(nome, nacionalidade=''):
    """Cadastra um novo autor. Retorna True se deu certo."""
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
    """Lista todos os autores ordenados por nome. Retorna lista de (id, nome)."""
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
    """Lista os autores vinculados a um livro específico (via tabela N:N)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        # Junta autor com a tabela de relação livro_autor
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
    """Vincula um autor a um livro (insere na tabela N:N). IGNORE evita duplicatas."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT IGNORE INTO livro_autor (id_livro, id_autor) VALUES (%s, %s)",
            (id_livro, id_autor)                # IGNORE: se já existe, não dá erro
        )
        conn.commit()
        conn.close()
        return True
    except Error:
        return False


def desassociar_autor_livro(id_livro, id_autor):
    """Remove a vinculação entre um autor e um livro."""
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
    """Cadastra um novo livro no catálogo. Retorna True se deu certo."""
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
    """Lista todos os livros com sua categoria. Retorna lista de (id, titulo, isbn, categoria, editora, ano, status)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        # Junta livro com categoria para mostrar o nome da categoria
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
    """Lista livros que pelo menos um exemplar disponível. Retorna (id, titulo)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        # Subconsulta: livros que têm exemplar com status 'disponivel'
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
    """Exclui um livro do catálogo pelo ID. Retorna True se conseguiu."""
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
    """Busca um livro pelo ID. Retorna todos os dados ou None se não encontrar."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT l.id_livro, l.titulo, l.isbn, l.id_categoria, l.editora, l.ano_publicacao, l.sinopse
               FROM livro l WHERE l.id_livro = %s""",
            (id_livro,)
        )
        dados = cursor.fetchone()               # Pega um único resultado
        conn.close()
        return dados
    except Error:
        return None


# ======================== EXEMPLAR ========================

def cadastrar_exemplar(codigo_patrimonio, id_livro, localizacao=''):
    """Cadastra uma cópia física (exemplar) de um livro. Retorna True se deu certo."""
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
    """Lista exemplares. Se id_livro for informado, filtra por livro."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        if id_livro:                             # Se quer exemplares de um livro específico
            cursor.execute(
                """SELECT e.id_exemplar, e.codigo_patrimonio, e.status_exemplar, e.localizacao, l.titulo
                   FROM exemplar e JOIN livro l ON e.id_livro = l.id_livro
                   WHERE e.id_livro = %s ORDER BY e.codigo_patrimonio""",
                (id_livro,)
            )
        else:                                    # Lista todos
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
    """Lista apenas exemplares com status 'disponivel'."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        if id_livro:                             # Filtra por livro
            cursor.execute(
                """SELECT e.id_exemplar, e.codigo_patrimonio FROM exemplar e
                   WHERE e.id_livro = %s AND e.status_exemplar = 'disponivel' ORDER BY e.codigo_patrimonio""",
                (id_livro,)
            )
        else:                                    # Lista todos disponíveis
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


def exemplar_tem_historico_emprestimo(id_exemplar):
    """Verifica se o exemplar já participou de algum empréstimo (qualquer status)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM emprestimo WHERE id_exemplar = %s",
            (id_exemplar,)
        )
        total = cursor.fetchone()[0]
        conn.close()
        return total > 0
    except Error:
        return False


def atualizar_status_exemplar(id_exemplar, status):
    """Atualiza o status de um exemplar (disponivel, emprestado, etc)."""
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
    """Exclui um exemplar do banco. Retorna True se conseguiu."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM emprestimo WHERE id_exemplar = %s",
            (id_exemplar,)
        )
        total_emprestimos = cursor.fetchone()[0]
        if total_emprestimos > 0:
            conn.close()
            print(f"Não é possível excluir exemplar {id_exemplar}: histórico de {total_emprestimos} empréstimos")
            return False

        cursor.execute("DELETE FROM exemplar WHERE id_exemplar = %s", (id_exemplar,))
        sucesso = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return sucesso
    except Error as e:
        print(f"Erro ao excluir exemplar: {e}")
        return False


# ======================== EMPRÉSTIMO ========================

def cadastrar_emprestimo(id_usuario, id_exemplar, data_prevista, id_funcionario):
    """Registra um novo empréstimo e marca o exemplar como 'emprestado'."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        # Insere o empréstimo com data de hoje como data de empréstimo
        cursor.execute(
            """INSERT INTO emprestimo (data_emprestimo, data_prevista, status, id_usuario, id_exemplar, id_funcionario)
               VALUES (CURDATE(), %s, 'ativo', %s, %s, %s)""",
            (data_prevista, id_usuario, id_exemplar, id_funcionario)
        )
        # Atualiza o status do exemplar para "emprestado"
        cursor.execute("UPDATE exemplar SET status_exemplar = 'emprestado' WHERE id_exemplar = %s", (id_exemplar,))
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Erro ao cadastrar emprestimo: {e}")
        return False


def listar_emprestimos():
    """Lista todos os empréstimos (ativo, finalizado, atrasado) com dados do usuário e livro."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        # Junta 4 tabelas: empréstimo + usuário + exemplar + livro
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
    """Lista apenas empréstimos ativos ou atrasados (pendentes de devolução)."""
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
    """Finaliza um empréstimo: marca como 'finalizado', libera o exemplar, e verifica se tem reserva."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        # 1. Busca o exemplar vinculado ao empréstimo
        cursor.execute("SELECT id_exemplar FROM emprestimo WHERE id_emprestimo = %s", (id_emprestimo,))
        resultado = cursor.fetchone()
        
        if not resultado:
            print(f"Aviso: Empréstimo {id_emprestimo} não encontrado")
            conn.close()
            return False
            
        id_exemplar = resultado[0]
        
        if not id_exemplar:
            print(f"Aviso: Exemplar não vinculado ao empréstimo {id_emprestimo}")
            conn.close()
            return False

        # 2. Marca o empréstimo como finalizado com data de hoje
        cursor.execute(
            "UPDATE emprestimo SET status = 'finalizado', data_devolucao = CURDATE() WHERE id_emprestimo = %s",
            (id_emprestimo,)
        )
        
        atualizacoes = cursor.rowcount
        if atualizacoes == 0:
            print(f"Aviso: Nenhuma linha atualizada para empréstimo {id_emprestimo}")
        
        # 3. Libera o exemplar (volta a ficar disponível)
        cursor.execute(
            "UPDATE exemplar SET status_exemplar = 'disponivel' WHERE id_exemplar = %s",
            (id_exemplar,)
        )
        
        atualizacoes_ex = cursor.rowcount
        if atualizacoes_ex == 0:
            print(f"Aviso: Nenhuma linha atualizada para exemplar {id_exemplar}")

        # 4. Verifica se alguém reservou esse livro (simples - apenas id_reserva e título)
        reserva_info = None
        cursor.execute(
            """SELECT r.id_reserva, l.titulo
               FROM reserva r
               JOIN livro l ON r.id_livro = l.id_livro
               WHERE r.id_livro = (SELECT id_livro FROM exemplar WHERE id_exemplar = %s)
               AND r.status = 'ativa'
               ORDER BY r.data_reserva ASC LIMIT 1""",
            (id_exemplar,)
        )
        reserva_info = cursor.fetchone()

        conn.commit()
        conn.close()
        
        print(f"✓ Empréstimo {id_emprestimo} finalizado com sucesso")
        if reserva_info:
            print(f"  ⚠ Há reserva ativa: {reserva_info}")
        return True
        
    except Error as e:
        print(f"❌ Erro ao finalizar emprestimo {id_emprestimo}: {e}")
        if 'conn' in locals():
            try:
                conn.close()
            except:
                pass
        return False


def verificar_atrasos():
    """Marca como 'atrasado' todos os empréstimos cuja data prevista já passou."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        # Atualiza empréstimos ativos que estão com data prevista no passado
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
    """Cria uma reserva de livro para o usuário. Padrão: válida por 7 dias."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        # Insere com data de hoje e validade = hoje + dias_validade
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
    """Lista reservas. Se status for informado, filtra por ele (ativa, cancelada, etc)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        if status:                               # Com filtro de status
            cursor.execute(
                """SELECT r.id_reserva, u.nome, l.titulo, r.data_reserva, r.data_validade, r.status
                   FROM reserva r
                   JOIN usuario u ON r.id_usuario = u.id_usuario
                   JOIN livro l ON r.id_livro = l.id_livro
                   WHERE r.status = %s ORDER BY r.data_reserva DESC""",
                (status,)
            )
        else:                                    # Sem filtro
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
    """Cancela uma reserva pelo ID."""
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
    """Gera uma multa por atraso. Valor = R$ 2,00 por dia de atraso."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        valor = dias_atraso * 2.00               # Calcula o valor da multa
        
        print(f"Gerando multa: emp_id={id_emprestimo}, dias={dias_atraso}, valor=R${valor:.2f}")
        
        cursor.execute(
            """INSERT INTO multa (valor, dias_atraso, motivo, status_pagamento, data_geracao, id_emprestimo)
               VALUES (%s, %s, %s, 'pendente', CURDATE(), %s)""",
            (valor, dias_atraso, motivo, id_emprestimo)
        )
        conn.commit()
        conn.close()
        print(f"✓ Multa criada com sucesso: R${valor:.2f}")
        return True
    except Error as e:
        print(f"❌ Erro ao gerar multa: {e}")
        if 'conn' in locals():
            try:
                conn.close()
            except:
                pass
        return False


def listar_multas(status=None):
    """Lista multas. Se status for informado, filtra (pendente, pago, isento)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        if status:                               # Com filtro
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
        else:                                    # Sem filtro
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
    """Registra o pagamento de uma multa (muda status para 'pago')."""
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
    """Verifica se o usuário tem multa pendente (impede novo empréstimo)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        # Conta multas pendentes do usuário
        cursor.execute(
            """SELECT COUNT(*) FROM multa m
               JOIN emprestimo e ON m.id_emprestimo = e.id_emprestimo
               WHERE e.id_usuario = %s AND m.status_pagamento = 'pendente'""",
            (id_usuario,)
        )
        total = cursor.fetchone()[0]             # Pega o número
        conn.close()
        return total > 0                         # True se tem multa pendente
    except Error:
        return False


# ======================== DASHBOARD ========================

def buscar_stats_dashboard():
    """Busca estatísticas gerais para o dashboard: livros, empréstimos totais, ativos, usuários, taxa de retorno."""
    stats = {
        'livros': 0,
        'emprestimos': 0,
        'emprestimos_ativos': 0,
        'usuarios': 0,
        'atrasados': 0,
        'taxa_retorno': 0
    }  # Valores padrão
    try:
        conn = _conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM livro")           # Conta livros
        stats['livros'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emprestimo")      # Conta empréstimos totais
        stats['emprestimos'] = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM emprestimo WHERE status IN ('ativo', 'atrasado')"
        )  # Conta empréstimos em aberto
        stats['emprestimos_ativos'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emprestimo WHERE status = 'atrasado'")  # Conta empréstimos atrasados
        stats['atrasados'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuario WHERE tipo_usuario = 'aluno'")  # Conta alunos
        stats['usuarios'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emprestimo WHERE status = 'finalizado'")  # Empréstimos devolvidos
        finalizados = cursor.fetchone()[0]
        if stats['emprestimos'] > 0:             # Se tem empréstimos
            stats['taxa_retorno'] = round((finalizados / stats['emprestimos']) * 100)  # Calcula %

        conn.close()
    except Error:
        pass                                   # Se der erro, retorna zeros
    return stats                                # Retorna o dicionário com estatísticas


def buscar_emprestimos_por_mes():
    """Conta empréstimos agrupados por mês. Retorna [(mês, total), ...]."""
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
    """Conta livros agrupados por categoria. Retorna [(nome_categoria, total), ...]."""
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
    """Conta empréstimos da semana atual, agrupados por dia da semana."""
    dados = []
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT DAYOFWEEK(data_emprestimo) as dia_semana, COUNT(*) as total
               FROM emprestimo
               WHERE YEARWEEK(data_emprestimo) = YEARWEEK(CURDATE())
               GROUP BY DAYOFWEEK(data_emprestimo)
               ORDER BY DAYOFWEEK(data_emprestimo)"""
        )
        dados = cursor.fetchall()
        conn.close()
    except Error:
        pass
    return dados

# ======================== USUÁRIO — CRUD COMPLETO ========================


def listar_usuarios(tipo=None, status=None):
    """Lista usuários com filtros opcionais por tipo e status. Retorna lista completa de dados."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        # Consulta base
        base = """SELECT id_usuario, nome, email, telefone, cpf,
                         tipo_usuario, matricula, turma, turno, funcao, status
                  FROM usuario"""
        condicoes = []                          # Lista de condições WHERE
        valores = []                            # Lista de valores para os parâmetros

        if tipo:                                # Se tem filtro de tipo
            condicoes.append("tipo_usuario = %s")
            valores.append(tipo)
        if status:                              # Se tem filtro de status
            condicoes.append("status = %s")
            valores.append(status)

        if condicoes:                           # Se tem alguma condição
            base += " WHERE " + " AND ".join(condicoes)  # Junta com AND
        base += " ORDER BY nome"                # Ordena por nome

        cursor.execute(base, valores)           # Executa com os parâmetros
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def buscar_usuario_por_id(id_usuario):
    """Busca um usuário pelo ID. Retorna tupla com todos os campos ou None."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id_usuario, nome, email, telefone, cpf,
                      tipo_usuario, matricula, turma, turno, funcao, status
               FROM usuario WHERE id_usuario = %s""",
            (id_usuario,)
        )
        dado = cursor.fetchone()                # Pega o resultado
        conn.close()
        return dado
    except Error:
        return None


def atualizar_usuario(id_usuario, nome, email, telefone='', cpf='', tipo='aluno',
                      matricula='', turma='', turno='', funcao='', status='ativo'):
    """Atualiza todos os campos editáveis de um usuário (exceto senha)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE usuario
               SET nome=%s, email=%s, telefone=%s, cpf=%s, tipo_usuario=%s,
                   matricula=%s, turma=%s, turno=%s, funcao=%s, status=%s
               WHERE id_usuario=%s""",
            (nome, email, telefone or None, cpf or None, tipo,
             matricula or None, turma or None, turno or None, funcao or None,
             status, id_usuario)
        )
        conn.commit()                           # Salva as alterações
        alterado = cursor.rowcount > 0          # Verifica se alguma linha foi alterada
        conn.close()
        return alterado                         # True se alterou algo
    except Error as e:
        print(f"Erro ao atualizar usuario: {e}")
        return False


def atualizar_senha_usuario(id_usuario, nova_senha):
    """Atualiza apenas a senha de um usuário (com hash SHA-256)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        senha_hash = _hash_senha(nova_senha)     # Criptografa a nova senha
        cursor.execute(
            "UPDATE usuario SET senha=%s WHERE id_usuario=%s",
            (senha_hash, id_usuario)
        )
        conn.commit()
        alterado = cursor.rowcount > 0           # True se atualizou
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
        # Usa CASE do SQL para alternar: se é ativo vira inativo, e vice-versa
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
    """Remove um usuário permanentemente. Falha se tiver empréstimos vinculados (chave estrangeira)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario WHERE id_usuario=%s", (id_usuario,))
        conn.commit()
        removido = cursor.rowcount > 0          # True se removeu
        conn.close()
        return removido
    except Error as e:
        print(f"Erro ao excluir usuario: {e}")
        return False


def buscar_usuarios_por_nome(termo):
    """Busca usuários cujo nome contém o termo (busca parcial, sem diferencia maiúsculas)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        # LIKE com % nos dois lados = busca parcial
        cursor.execute(
            """SELECT id_usuario, nome, email, telefone, cpf,
                      tipo_usuario, matricula, turma, turno, funcao, status
               FROM usuario
               WHERE nome LIKE %s
               ORDER BY nome""",
            (f"%{termo}%",)                     # Ex: "%João" busca qualquer nome com "João"
        )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []
