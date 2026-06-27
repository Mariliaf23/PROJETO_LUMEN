# report_gen.py — Gera relatórios em PDF do sistema de biblioteca

import os                                        # Biblioteca para manipular caminhos de arquivos
from datetime import date                        # Biblioteca para obter a data atual
from fpdf import FPDF                            # Biblioteca para criar arquivos PDF
from services.database_config import (            # Funções que buscam dados do banco
    listar_livros,                               # Lista todos os livros cadastrados
    listar_emprestimos,                          # Lista todos os empréstimos
    listar_emprestimos_ativos,                   # Lista empréstimos em aberto
    listar_multas,                               # Lista multas
    buscar_stats_dashboard                       # Busca estatísticas gerais
)


class RelatorioPDF(FPDF):
    """Classe que cria o PDF com cabeçalho e rodapé personalizados."""

    def header(self):
        """Adiciona o cabeçalho em todas as páginas do PDF."""
        self.set_font('Helvetica', 'B', 16)      # Fonte Arial Negrito, tamanho 16
        self.cell(0, 10, 'LUMEN - Relatorio da Biblioteca', new_x="LMARGIN", new_y="NEXT", align='C')  # Título centralizado
        self.set_font('Helvetica', '', 9)         # Fonte Arial Normal, tamanho 9
        self.cell(0, 6, f'Gerado em: {date.today().strftime("%d/%m/%Y")}', new_x="LMARGIN", new_y="NEXT", align='C')  # Data de geração
        self.ln(5)                                # Espaço após o cabeçalho

    def footer(self):
        """Adiciona o rodapé com número de página em todas as páginas."""
        self.set_y(-15)                           # Posiciona a 15mm do fundo da página
        self.set_font('Helvetica', 'I', 8)        # Fonte Arial Itálico, tamanho 8
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', align='C')  # Número da página

    def titulo_secao(self, texto):
        """Adiciona um título de seção com fundo colorido."""
        self.set_font('Helvetica', 'B', 12)       # Fonte Arial Negrito, tamanho 12
        self.set_fill_color(184, 154, 114)        # Cor de fundo dourada
        self.set_text_color(0, 0, 0)              # Cor do texto: preto
        self.cell(0, 8, texto, new_x="LMARGIN", new_y="NEXT", fill=True)  # Célula com fundo preenchido
        self.ln(3)                                # Espaço após o título
        self.set_text_color(0, 0, 0)              # Volta cor do texto para preto


def gerar_relatorio_livros(caminho):
    """Gera um PDF com a lista de todos os livros cadastrados."""
    pdf = RelatorioPDF()                          # Cria o objeto PDF
    pdf.alias_nb_pages()                          # Habilita numeração de páginas
    pdf.add_page()                                # Adiciona a primeira página
    pdf.titulo_secao('Catalogo de Livros')        # Título da seção

    livros = listar_livros()                      # Busca todos os livros do banco
    if not livros:                                # Se não tem livros
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 8, 'Nenhum livro cadastrado.', new_x="LMARGIN", new_y="NEXT")
    else:                                         # Se tem livros
        # Cabeçalho da tabela
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(26, 18, 8)            # Cor de fundo escura
        pdf.set_text_color(255, 255, 255)        # Texto branco
        pdf.cell(8, 7, 'ID', border=1, fill=True)
        pdf.cell(60, 7, 'Titulo', border=1, fill=True)
        pdf.cell(30, 7, 'ISBN', border=1, fill=True)
        pdf.cell(35, 7, 'Categoria', border=1, fill=True)
        pdf.cell(35, 7, 'Editora', border=1, fill=True)
        pdf.cell(15, 7, 'Ano', border=1, fill=True)
        pdf.ln()                                  # Nova linha

        # Dados da tabela
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)              # Texto preto
        for l in livros:                          # Para cada livro
            pdf.cell(8, 6, str(l[0]), border=1)          # ID
            pdf.cell(60, 6, str(l[1])[:30], border=1)    # Título (máx 30 chars)
            pdf.cell(30, 6, str(l[2])[:15], border=1)    # ISBN (máx 15 chars)
            pdf.cell(35, 6, str(l[3])[:18], border=1)    # Categoria
            pdf.cell(35, 6, str(l[4] or '-')[:18], border=1)  # Editora
            pdf.cell(15, 6, str(l[5] or '-'), border=1)  # Ano
            pdf.ln()                              # Nova linha

    pdf.output(caminho)                           # Salva o PDF no caminho indicado
    return caminho                                # Retorna o caminho do arquivo


def gerar_relatorio_emprestimos(caminho):
    """Gera um PDF com os empréstimos ativos."""
    pdf = RelatorioPDF()                          # Cria o objeto PDF
    pdf.alias_nb_pages()                          # Habilita numeração
    pdf.add_page()                                # Nova página
    pdf.titulo_secao('Emprestimos Ativos')        # Título

    emprestimos = listar_emprestimos_ativos()     # Busca empréstimos ativos
    if not emprestimos:                           # Se não tem empréstimos
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 8, 'Nenhum emprestimo ativo.', new_x="LMARGIN", new_y="NEXT")
    else:
        # Cabeçalho da tabela
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(26, 18, 8)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(8, 7, 'ID', border=1, fill=True)
        pdf.cell(40, 7, 'Usuario', border=1, fill=True)
        pdf.cell(40, 7, 'Livro', border=1, fill=True)
        pdf.cell(25, 7, 'Emprestimo', border=1, fill=True)
        pdf.cell(25, 7, 'Previsto', border=1, fill=True)
        pdf.cell(20, 7, 'Status', border=1, fill=True)
        pdf.ln()

        # Dados da tabela
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        for e in emprestimos:                     # Para cada empréstimo
            pdf.cell(8, 6, str(e[0]), border=1)          # ID
            pdf.cell(40, 6, str(e[1])[:20], border=1)    # Nome do usuário
            pdf.cell(40, 6, str(e[3])[:20], border=1)    # Título do livro
            pdf.cell(25, 6, str(e[4]), border=1)         # Data do empréstimo
            pdf.cell(25, 6, str(e[5]), border=1)         # Data prevista
            pdf.cell(20, 6, str(e[6]), border=1)         # Status
            pdf.ln()

    pdf.output(caminho)                           # Salva o PDF
    return caminho


def gerar_relatorio_multas(caminho):
    """Gera um PDF com as multas pendentes."""
    pdf = RelatorioPDF()                          # Cria o PDF
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.titulo_secao('Multas Pendentes')          # Título

    multas = listar_multas(status='pendente')     # Busca multas pendentes
    if not multas:                                # Se não tem multas
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 8, 'Nenhuma multa pendente.', new_x="LMARGIN", new_y="NEXT")
    else:
        # Cabeçalho da tabela
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(26, 18, 8)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(8, 7, 'ID', border=1, fill=True)
        pdf.cell(20, 7, 'Valor', border=1, fill=True)
        pdf.cell(15, 7, 'Dias', border=1, fill=True)
        pdf.cell(20, 7, 'Motivo', border=1, fill=True)
        pdf.cell(25, 7, 'Data', border=1, fill=True)
        pdf.cell(40, 7, 'Usuario', border=1, fill=True)
        pdf.cell(40, 7, 'Livro', border=1, fill=True)
        pdf.ln()

        # Dados da tabela
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        total = 0                                 # Acumulador do valor total
        for m in multas:                          # Para cada multa
            pdf.cell(8, 6, str(m[0]), border=1)          # ID
            pdf.cell(20, 6, f'R$ {m[1]:.2f}', border=1) # Valor em reais
            pdf.cell(15, 6, str(m[2]), border=1)         # Dias de atraso
            pdf.cell(20, 6, str(m[3]), border=1)         # Motivo
            pdf.cell(25, 6, str(m[5]), border=1)         # Data
            pdf.cell(40, 6, str(m[6])[:20], border=1)    # Nome do usuário
            pdf.cell(40, 6, str(m[7])[:20], border=1)    # Título do livro
            pdf.ln()
            total += float(m[1])                 # Soma o valor da multa

        pdf.ln(5)                                # Espaço antes do total
        pdf.set_font('Helvetica', 'B', 11)       # Fonte negrita
        pdf.cell(0, 8, f'Total pendente: R$ {total:.2f}', new_x="LMARGIN", new_y="NEXT")  # Mostra total

    pdf.output(caminho)                           # Salva o PDF
    return caminho


def gerar_relatorio_geral(caminho):
    """Gera um PDF com o resumo geral e relatórios auxiliares."""
    pdf = RelatorioPDF()                          # Cria o PDF
    pdf.alias_nb_pages()
    pdf.add_page()

    stats = buscar_stats_dashboard()              # Busca estatísticas do dashboard
    pdf.titulo_secao('Resumo Geral')              # Título da seção
    pdf.set_font('Helvetica', '', 11)             # Fonte tamanho 11
    pdf.cell(0, 8, f"Total de Livros: {stats['livros']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Total de Emprestimos: {stats['emprestimos']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Alunos Cadastrados: {stats['usuarios']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Taxa de Retorno: {stats['taxa_retorno']}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)                                   # Espaço

    # Gera relatórios auxiliares com nomes diferentes
    gerar_relatorio_livros(caminho.replace('.pdf', '_livros.pdf'))
    gerar_relatorio_emprestimos(caminho.replace('.pdf', '_emprestimos.pdf'))
    gerar_relatorio_multas(caminho.replace('.pdf', '_multas.pdf'))

    pdf.output(caminho)                           # Salva o PDF principal
    return caminho
