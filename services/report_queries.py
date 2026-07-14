# report_queries.py — Consultas SQL para todos os relatórios do LUMEN

from services.database_config import _conectar
from mysql.connector import Error


def buscar_usuario_por_nome_parcial(termo):
    """Busca usuários por nome parcial (para autocomplete)."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id_usuario, nome, email, telefone
               FROM usuario
               WHERE nome LIKE %s
               ORDER BY nome LIMIT 10""",
            (f"%{termo}%",)
        )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


def buscar_exemplar_por_patrimonio(termo):
    """Busca exemplares por patrimônio parcial."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT e.id_exemplar, e.codigo_patrimonio, l.titulo
               FROM exemplar e
               JOIN livro l ON e.id_livro = l.id_livro
               WHERE e.codigo_patrimonio LIKE %s
               ORDER BY e.codigo_patrimonio LIMIT 10""",
            (f"%{termo}%",)
        )
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error:
        return []


# ═══════════════════════════════════════════════════════════════════════════
# 1. INVENTÁRIO DO ACERVO
# ═══════════════════════════════════════════════════════════════════════════

def relatorio_inventario_acervo(filtros=None):
    """
    Retorna inventário completo do acervo.
    Filtros: categoria, situacao, autor, editora, data_inicio, data_fim
    """
    try:
        conn = _conectar()
        cursor = conn.cursor()

        sql = """
            SELECT e.codigo_patrimonio,
                   l.isbn, l.titulo,
                   GROUP_CONCAT(a.nome_autor SEPARATOR ', ') as autores,
                   l.editora, c.nome_categoria, e.localizacao,
                   e.status_exemplar
            FROM exemplar e
            JOIN livro l ON e.id_livro = l.id_livro
            LEFT JOIN livro_autor la ON l.id_livro = la.id_livro
            LEFT JOIN autor a ON la.id_autor = a.id_autor
            LEFT JOIN categoria c ON l.id_categoria = c.id_categoria
            WHERE 1=1
        """
        params = []

        if filtros:
            if filtros.get('categoria'):
                sql += " AND c.nome_categoria = %s"
                params.append(filtros['categoria'])
            if filtros.get('situacao'):
                sql += " AND e.status_exemplar = %s"
                params.append(filtros['situacao'])
            if filtros.get('autor'):
                sql += " AND a.nome_autor LIKE %s"
                params.append(f"%{filtros['autor']}%")
            if filtros.get('editora'):
                sql += " AND l.editora LIKE %s"
                params.append(f"%{filtros['editora']}%")
            if filtros.get('data_inicio'):
                sql += " AND l.ano_publicacao >= %s"
                params.append(filtros['data_inicio'])
            if filtros.get('data_fim'):
                sql += " AND l.ano_publicacao <= %s"
                params.append(filtros['data_fim'])

        sql += " GROUP BY e.id_exemplar ORDER BY e.codigo_patrimonio"

        cursor.execute(sql, tuple(params))
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error as e:
        print(f"Erro no relatório de inventário: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════
# 2. EXEMPLARES DISPONÍVEIS
# ═══════════════════════════════════════════════════════════════════════════

def relatorio_exemplares_disponiveis(filtros=None):
    """Retorna apenas exemplares disponíveis."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        sql = """
            SELECT e.codigo_patrimonio, l.isbn, l.titulo,
                   GROUP_CONCAT(a.nome_autor SEPARATOR ', ') as autores,
                   c.nome_categoria, e.localizacao
            FROM exemplar e
            JOIN livro l ON e.id_livro = l.id_livro
            LEFT JOIN livro_autor la ON l.id_livro = la.id_livro
            LEFT JOIN autor a ON la.id_autor = a.id_autor
            LEFT JOIN categoria c ON l.id_categoria = c.id_categoria
            WHERE e.status_exemplar = 'disponivel'
        """
        params = []

        if filtros:
            if filtros.get('categoria'):
                sql += " AND c.nome_categoria = %s"
                params.append(filtros['categoria'])
            if filtros.get('autor'):
                sql += " AND a.nome_autor LIKE %s"
                params.append(f"%{filtros['autor']}%")
            if filtros.get('patrimonio'):
                sql += " AND e.codigo_patrimonio LIKE %s"
                params.append(f"%{filtros['patrimonio']}%")
            if filtros.get('titulo'):
                sql += " AND l.titulo LIKE %s"
                params.append(f"%{filtros['titulo']}%")

        sql += " GROUP BY e.id_exemplar ORDER BY e.codigo_patrimonio"

        cursor.execute(sql, tuple(params))
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error as e:
        print(f"Erro no relatório de disponíveis: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════
# 3. EMPRÉSTIMOS POR PERÍODO
# ═══════════════════════════════════════════════════════════════════════════

def relatorio_emprestimos_periodo(data_inicio=None, data_fim=None):
    """Retorna empréstimos em um período com totais."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        sql = """
            SELECT ex2.codigo_patrimonio, l.titulo, u.nome,
                   COALESCE(u.email, '') as contato,
                   ex.data_emprestimo, ex.data_prevista, ex.data_devolucao, ex.status
            FROM emprestimo ex
            JOIN exemplar ex2 ON ex.id_exemplar = ex2.id_exemplar
            JOIN livro l ON ex2.id_livro = l.id_livro
            JOIN usuario u ON ex.id_usuario = u.id_usuario
            WHERE 1=1
        """
        params = []

        if data_inicio:
            sql += " AND ex.data_emprestimo >= %s"
            params.append(data_inicio)
        if data_fim:
            sql += " AND ex.data_emprestimo <= %s"
            params.append(data_fim)

        sql += " ORDER BY ex.data_emprestimo DESC"

        cursor.execute(sql, tuple(params))
        dados = cursor.fetchall()

        # Contadores
        total = len(dados)
        devolvidos = sum(1 for d in dados if d[7] == 'finalizado')
        abertos = total - devolvidos

        conn.close()
        return dados, {'total': total, 'devolvidos': devolvidos, 'abertos': abertos}
    except Error as e:
        print(f"Erro no relatório de empréstimos: {e}")
        return [], {'total': 0, 'devolvidos': 0, 'abertos': 0}


# ═══════════════════════════════════════════════════════════════════════════
# 4. EMPRÉSTIMOS EM ATRASO
# ═══════════════════════════════════════════════════════════════════════════

def relatorio_emprestimos_atraso():
    """Retorna empréstimos em atraso, ordenados do maior para o menor."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.nome, COALESCE(u.email, '') as contato,
                   e.codigo_patrimonio, l.titulo,
                   ex.data_prevista,
                   DATEDIFF(CURDATE(), ex.data_prevista) as dias_atraso
            FROM emprestimo ex
            JOIN usuario u ON ex.id_usuario = u.id_usuario
            JOIN exemplar e ON ex.id_exemplar = e.id_exemplar
            JOIN livro l ON e.id_livro = l.id_livro
            WHERE ex.status IN ('ativo', 'atrasado')
              AND ex.data_prevista < CURDATE()
            ORDER BY dias_atraso DESC
        """)

        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error as e:
        print(f"Erro no relatório de atrasos: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════
# 5. HISTÓRICO DE EMPRÉSTIMOS POR USUÁRIO
# ═══════════════════════════════════════════════════════════════════════════

def relatorio_historico_usuario(id_usuario):
    """Retorna histórico completo de empréstimos de um usuário."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.codigo_patrimonio, l.titulo,
                   ex.data_emprestimo, ex.data_prevista, ex.data_devolucao
            FROM emprestimo ex
            JOIN exemplar e ON ex.id_exemplar = e.id_exemplar
            JOIN livro l ON e.id_livro = l.id_livro
            WHERE ex.id_usuario = %s
            ORDER BY ex.data_emprestimo DESC
        """, (id_usuario,))

        dados = cursor.fetchall()

        # Totais
        total = len(dados)

        conn.close()
        return dados, {'total': total}
    except Error as e:
        print(f"Erro no histórico do usuário: {e}")
        return [], {'total': 0, 'devolucoes': 0, 'abertos': 0, 'renovacoes': 0}


# ═══════════════════════════════════════════════════════════════════════════
# 6. HISTÓRICO DE EMPRÉSTIMOS POR EXEMPLAR
# ═══════════════════════════════════════════════════════════════════════════

def relatorio_historico_exemplar(id_exemplar):
    """Retorna histórico de empréstimos de um exemplar."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.nome, COALESCE(u.email, '') as contato,
                   ex.data_emprestimo, ex.data_devolucao,
                   f.nome as funcionario
            FROM emprestimo ex
            JOIN usuario u ON ex.id_usuario = u.id_usuario
            LEFT JOIN usuario f ON ex.id_funcionario = f.id_usuario
            WHERE ex.id_exemplar = %s
            ORDER BY ex.data_emprestimo DESC
        """, (id_exemplar,))

        dados = cursor.fetchall()
        total = len(dados)
        conn.close()
        return dados, {'total': total}
    except Error as e:
        print(f"Erro no histórico do exemplar: {e}")
        return [], {'total': 0}


# ═══════════════════════════════════════════════════════════════════════════
# 7. LIVROS MAIS EMPRESTADOS
# ═══════════════════════════════════════════════════════════════════════════

def relatorio_livros_mais_emprestados(data_inicio=None, data_fim=None, limite=10):
    """Retorna ranking de livros mais emprestados."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        sql = """
            SELECT l.titulo,
                   GROUP_CONCAT(DISTINCT a.nome_autor SEPARATOR ', ') as autores,
                   l.isbn,
                   COUNT(ex.id_emprestimo) as total_emprestimos
            FROM emprestimo ex
            JOIN exemplar e ON ex.id_exemplar = e.id_exemplar
            JOIN livro l ON e.id_livro = l.id_livro
            LEFT JOIN livro_autor la ON l.id_livro = la.id_livro
            LEFT JOIN autor a ON la.id_autor = a.id_autor
            WHERE 1=1
        """
        params = []

        if data_inicio:
            sql += " AND ex.data_emprestimo >= %s"
            params.append(data_inicio)
        if data_fim:
            sql += " AND ex.data_emprestimo <= %s"
            params.append(data_fim)

        sql += """
            GROUP BY l.id_livro, l.titulo, l.isbn
            ORDER BY total_emprestimos DESC
            LIMIT %s
        """
        params.append(limite)

        cursor.execute(sql, tuple(params))
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error as e:
        print(f"Erro no relatório de livros mais emprestados: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════
# 8. TOP 10 LEITORES
# ═══════════════════════════════════════════════════════════════════════════

def relatorio_top_leitores(data_inicio=None, data_fim=None, limite=10):
    """Retorna ranking de usuários que mais emprestaram."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        sql = """
            SELECT u.nome, COALESCE(u.email, '') as contato,
                   COUNT(ex.id_emprestimo) as total_emprestimos
            FROM emprestimo ex
            JOIN usuario u ON ex.id_usuario = u.id_usuario
            WHERE u.tipo_usuario IN ('aluno', 'professor')
        """
        params = []

        if data_inicio:
            sql += " AND ex.data_emprestimo >= %s"
            params.append(data_inicio)
        if data_fim:
            sql += " AND ex.data_emprestimo <= %s"
            params.append(data_fim)

        sql += """
            GROUP BY u.id_usuario, u.nome, u.email
            ORDER BY total_emprestimos DESC
            LIMIT %s
        """
        params.append(limite)

        cursor.execute(sql, tuple(params))
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Error as e:
        print(f"Erro no relatório de top leitores: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════
# 9. NOVAS AQUISIÇÕES
# ═══════════════════════════════════════════════════════════════════════════

def relatorio_novas_aquisicoes(data_inicio=None, data_fim=None):
    """Retorna novos exemplares cadastrados no período."""
    try:
        conn = _conectar()
        cursor = conn.cursor()

        sql = """
            SELECT e.codigo_patrimonio, l.isbn, l.titulo,
                   GROUP_CONCAT(DISTINCT a.nome_autor SEPARATOR ', ') as autores,
                   l.editora, c.nome_categoria, l.ano_publicacao
            FROM exemplar e
            JOIN livro l ON e.id_livro = l.id_livro
            LEFT JOIN livro_autor la ON l.id_livro = la.id_livro
            LEFT JOIN autor a ON la.id_autor = a.id_autor
            LEFT JOIN categoria c ON l.id_categoria = c.id_categoria
            WHERE 1=1
        """
        params = []

        if data_inicio:
            sql += " AND e.id_exemplar IN (SELECT id_exemplar FROM exemplar WHERE id_exemplar IS NOT NULL)"
        if data_fim:
            sql += ""

        sql += " GROUP BY e.id_exemplar ORDER BY e.codigo_patrimonio"

        cursor.execute(sql, tuple(params))
        dados = cursor.fetchall()
        total = len(dados)
        conn.close()
        return dados, {'total': total}
    except Error as e:
        print(f"Erro no relatório de novas aquisições: {e}")
        return [], {'total': 0}


# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES PARA FILTROS
# ═══════════════════════════════════════════════════════════════════════════

def listar_categorias_para_filtro():
    """Lista categorias para combos de filtro."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome_categoria FROM categoria ORDER BY nome_categoria")
        dados = [r[0] for r in cursor.fetchall()]
        conn.close()
        return dados
    except Error:
        return []


def listar_autores_para_filtro():
    """Lista autores para combos de filtro."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome_autor FROM autor ORDER BY nome_autor")
        dados = [r[0] for r in cursor.fetchall()]
        conn.close()
        return dados
    except Error:
        return []


def listar_editoras_para_filtro():
    """Lista editoras para combos de filtro."""
    try:
        conn = _conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT editora FROM livro WHERE editora IS NOT NULL ORDER BY editora")
        dados = [r[0] for r in cursor.fetchall()]
        conn.close()
        return dados
    except Error:
        return []
