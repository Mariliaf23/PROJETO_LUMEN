import os
from datetime import date
from fpdf import FPDF
from services.database_config import (
    listar_livros, listar_emprestimos, listar_emprestimos_ativos,
    listar_multas, buscar_stats_dashboard
)


class RelatorioPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'LUMEN - Relatorio da Biblioteca', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_font('Helvetica', '', 9)
        self.cell(0, 6, f'Gerado em: {date.today().strftime("%d/%m/%Y")}', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', align='C')

    def titulo_secao(self, texto):
        self.set_font('Helvetica', 'B', 12)
        self.set_fill_color(184, 154, 114)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, texto, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(3)
        self.set_text_color(0, 0, 0)


def gerar_relatorio_livros(caminho):
    pdf = RelatorioPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.titulo_secao('Catalogo de Livros')

    livros = listar_livros()
    if not livros:
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 8, 'Nenhum livro cadastrado.', new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(26, 18, 8)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(8, 7, 'ID', border=1, fill=True)
        pdf.cell(60, 7, 'Titulo', border=1, fill=True)
        pdf.cell(30, 7, 'ISBN', border=1, fill=True)
        pdf.cell(35, 7, 'Categoria', border=1, fill=True)
        pdf.cell(35, 7, 'Editora', border=1, fill=True)
        pdf.cell(15, 7, 'Ano', border=1, fill=True)
        pdf.ln()

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        for l in livros:
            pdf.cell(8, 6, str(l[0]), border=1)
            pdf.cell(60, 6, str(l[1])[:30], border=1)
            pdf.cell(30, 6, str(l[2])[:15], border=1)
            pdf.cell(35, 6, str(l[3])[:18], border=1)
            pdf.cell(35, 6, str(l[4] or '-')[:18], border=1)
            pdf.cell(15, 6, str(l[5] or '-'), border=1)
            pdf.ln()

    pdf.output(caminho)
    return caminho


def gerar_relatorio_emprestimos(caminho):
    pdf = RelatorioPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.titulo_secao('Emprestimos Ativos')

    emprestimos = listar_emprestimos_ativos()
    if not emprestimos:
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 8, 'Nenhum emprestimo ativo.', new_x="LMARGIN", new_y="NEXT")
    else:
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

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        for e in emprestimos:
            pdf.cell(8, 6, str(e[0]), border=1)
            pdf.cell(40, 6, str(e[1])[:20], border=1)
            pdf.cell(40, 6, str(e[3])[:20], border=1)
            pdf.cell(25, 6, str(e[4]), border=1)
            pdf.cell(25, 6, str(e[5]), border=1)
            pdf.cell(20, 6, str(e[6]), border=1)
            pdf.ln()

    pdf.output(caminho)
    return caminho


def gerar_relatorio_multas(caminho):
    pdf = RelatorioPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.titulo_secao('Multas Pendentes')

    multas = listar_multas(status='pendente')
    if not multas:
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 8, 'Nenhuma multa pendente.', new_x="LMARGIN", new_y="NEXT")
    else:
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

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        total = 0
        for m in multas:
            pdf.cell(8, 6, str(m[0]), border=1)
            pdf.cell(20, 6, f'R$ {m[1]:.2f}', border=1)
            pdf.cell(15, 6, str(m[2]), border=1)
            pdf.cell(20, 6, str(m[3]), border=1)
            pdf.cell(25, 6, str(m[5]), border=1)
            pdf.cell(40, 6, str(m[6])[:20], border=1)
            pdf.cell(40, 6, str(m[7])[:20], border=1)
            pdf.ln()
            total += float(m[1])

        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 8, f'Total pendente: R$ {total:.2f}', new_x="LMARGIN", new_y="NEXT")

    pdf.output(caminho)
    return caminho


def gerar_relatorio_geral(caminho):
    pdf = RelatorioPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    stats = buscar_stats_dashboard()
    pdf.titulo_secao('Resumo Geral')
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f"Total de Livros: {stats['livros']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Total de Emprestimos: {stats['emprestimos']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Alunos Cadastrados: {stats['usuarios']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Taxa de Retorno: {stats['taxa_retorno']}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    gerar_relatorio_livros(caminho.replace('.pdf', '_livros.pdf'))
    gerar_relatorio_emprestimos(caminho.replace('.pdf', '_emprestimos.pdf'))
    gerar_relatorio_multas(caminho.replace('.pdf', '_multas.pdf'))

    pdf.output(caminho)
    return caminho
