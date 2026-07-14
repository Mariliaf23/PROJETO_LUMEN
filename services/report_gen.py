# report_gen.py — Gera relatórios em PDF do sistema de biblioteca

import os
from datetime import date
from services.database_config import (
    listar_livros, listar_emprestimos_ativos, listar_multas,
    listar_usuarios, listar_emprestimos, buscar_usuario_por_id,
    buscar_historico_usuario, buscar_exemplares_por_titulo,
    buscar_movimentacoes_periodo, listar_exemplares
)
from services.report_export import (
    RelatorioPDF, gerar_pdf_generico, COLUNAS_MAP
)


# ═══════════════════════════════════════════════════════════════════════════════
# MAPEAMENTO DE COLUNAS PARA RELATÓRIOS ANTIGOS
# ═══════════════════════════════════════════════════════════════════════════════

COLUNAS_LIVROS = ["ID", "Título", "ISBN", "Categoria", "Editora", "Ano"]
COLUNAS_EMPRESTIMOS = ["ID", "Usuário", "Livro", "Empréstimo", "Previsto", "Status"]
COLUNAS_MULTAS = ["ID", "Valor", "Dias", "Motivo", "Data", "Usuário", "Livro"]


def gerar_relatorio_livros(caminho):
    """Gera um PDF com a lista de todos os livros cadastrados."""
    dados = listar_livros()
    larguras = [18, 85, 43, 51, 51, 25]
    cards = [{'icone': '[T]', 'valor': len(dados), 'label': 'LIVROS'}]
    gerar_pdf_generico("Catálogo de Livros", COLUNAS_LIVROS, larguras, dados, caminho,
                      descricao='Relatório completo do catálogo de livros da biblioteca.',
                      cards_resumo=cards,
                      observacao='Todos os livros cadastrados no sistema aparecem neste relatório.')
    return caminho


def gerar_relatorio_emprestimos(caminho):
    """Gera um PDF com os empréstimos ativos."""
    dados = listar_emprestimos_ativos()
    larguras = [18, 62, 70, 44, 44, 35]
    cards = [{'icone': '[>>]', 'valor': len(dados), 'label': 'ATIVOS'}]
    gerar_pdf_generico("Empréstimos Ativos", COLUNAS_EMPRESTIMOS, larguras, dados, caminho,
                      descricao='Empréstimos em aberto no momento da geração.',
                      cards_resumo=cards,
                      observacao='Empréstimos com devolução pendente. Multas são geradas automaticamente em caso de atraso.')
    return caminho


def gerar_relatorio_multas(caminho):
    """Gera um PDF com as multas pendentes."""
    multas = listar_multas(status='pendente')
    larguras = [19, 34, 22, 34, 37, 65, 62]
    total = sum(float(m[1]) for m in multas)
    cards = [
        {'icone': '[!]', 'valor': len(multas), 'label': 'MULTAS'},
        {'icone': '[T]', 'valor': f'R$ {total:.2f}', 'label': 'TOTAL'}
    ]
    gerar_pdf_generico("Multas Pendentes", COLUNAS_MULTAS, larguras, multas, caminho,
                      descricao='Multas pendentes de pagamento no sistema.',
                      cards_resumo=cards,
                      observacao='Multas geradas por atraso na devolução. Valor: R$ 2,00 por dia de atraso.')
    return caminho


def gerar_relatorio_usuario(usuario_id, caminho):
    """Gera um PDF com o histórico completo de um usuário."""
    dados, resumo = buscar_historico_usuario(usuario_id)
    usuario = buscar_usuario_por_id(usuario_id)
    nome = usuario[1] if usuario else "Usuário"

    colunas = ["Patrimônio", "Livro", "Empréstimo", "Previsto", "Devolução"]
    larguras = [47, 82, 48, 48, 48]
    cards = [{'icone': '[U]', 'valor': resumo['total'], 'label': 'EMPRESTIMOS'}]

    gerar_pdf_generico(f"Histórico - {nome}", colunas, larguras, dados, caminho,
                      cards_resumo=cards,
                      descricao=f'Histórico completo de empréstimos do usuário {nome}.',
                      observacao='Relatório gerado a partir dos registros de empréstimos vinculados ao usuário.')
    return caminho


def gerar_relatorio_titulos_exemplares(caminho):
    """Gera um PDF com todos os títulos e seus exemplares."""
    dados = buscar_exemplares_por_titulo()
    colunas = ["Título", "ISBN", "Categoria", "Editora", "Exemplares"]
    larguras = [85, 43, 51, 51, 43]
    cards = [{'icone': '[T]', 'valor': len(dados), 'label': 'TITULOS'}]

    gerar_pdf_generico("Títulos e Exemplares", colunas, larguras, dados, caminho,
                      descricao='Títulos cadastrados com quantidade de exemplares.',
                      cards_resumo=cards,
                      observacao='Todos os títulos do acervo com suas cópias físicas vinculadas.')
    return caminho


def gerar_relatorio_usuarios(caminho, tipo_usuario=None):
    """Gera um PDF com a lista de usuários cadastrados."""
    usuarios = listar_usuarios(tipo=tipo_usuario)
    colunas = ["Nome", "Email", "Tipo", "Status", "Telefone"]
    larguras = [85, 75, 38, 28, 47]
    cards = [{'icone': '[U]', 'valor': len(usuarios), 'label': 'USUARIOS'}]

    titulo = 'Usuários Cadastrados'
    if tipo_usuario:
        titulo += f' ({tipo_usuario})'

    gerar_pdf_generico(titulo, colunas, larguras, usuarios, caminho,
                      cards_resumo=cards,
                      descricao='Lista de todos os usuários cadastrados no sistema.',
                      observacao='Todos os usuários ativos e inativos aparecem neste relatório.')
    return caminho


def gerar_relatorio_movimentacoes(caminho, data_inicio=None, data_fim=None):
    """Gera um PDF com as movimentações do período."""
    movimentacoes = buscar_movimentacoes_periodo(data_inicio, data_fim)
    colunas = ["Patrimônio", "Livro", "Usuário", "Data", "Prevista", "Status"]
    larguras = [38, 70, 53, 38, 38, 36]
    cards = [{'icone': '[>>]', 'valor': len(movimentacoes), 'label': 'MOVIMENTOS'}]

    periodo = ''
    if data_inicio and data_fim:
        periodo = f' ({data_inicio} a {data_fim})'

    gerar_pdf_generico(f"Movimentações{periodo}", colunas, larguras, movimentacoes, caminho,
                      cards_resumo=cards,
                      descricao='Empréstimos registrados no período informado.',
                      observacao='Todos os movimentos de empréstimos e devoluções do período.')
    return caminho
