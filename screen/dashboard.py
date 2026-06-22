import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from services.database_config import (
    buscar_stats_dashboard, buscar_emprestimos_por_mes,
    buscar_livros_por_categoria, buscar_emprestimos_semana
)
from services.styles import (
    COR_BG, COR_SIDEBAR, COR_CARD, COR_DOURADO, COR_TEXTO, COR_TEXTO2,
    COR_INPUT_BORDER, COR_ATIVO, FONTE_TITULO, FONTE_NAV, FONTE_LABEL,
    criar_label, criar_titulo, criar_card
)

COR_GRAF1 = "#b89a72"
COR_GRAF2 = "#d4b896"
COR_GRAF3 = "#8a7e72"
COR_GRAF4 = "#6b5a48"
COR_GRAF5 = "#4a3a28"

MESES = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
DIAS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']


class Dashboard(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller

        plt.rcParams.update({
            'figure.facecolor': COR_CARD,
            'axes.facecolor': COR_CARD,
            'axes.edgecolor': COR_INPUT_BORDER,
            'axes.labelcolor': COR_TEXTO2,
            'text.color': COR_TEXTO,
            'xtick.color': COR_TEXTO2,
            'ytick.color': COR_TEXTO2,
            'grid.color': COR_INPUT_BORDER,
            'grid.alpha': 0.3,
            'font.family': 'Segoe UI',
            'font.size': 9,
        })

        self._carregar_dados()
        self._construir_ui()

    def _ao_visitar(self):
        self._carregar_dados()
        self._recriar_conteudo()

    def _carregar_dados(self):
        self._stats = buscar_stats_dashboard()
        self._emp_mes = buscar_emprestimos_por_mes()
        self._cat_livros = buscar_livros_por_categoria()
        self._emp_semana = buscar_emprestimos_semana()

    def _construir_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._criar_sidebar()
        self._criar_conteudo()

    def _criar_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=COR_SIDEBAR, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        criar_titulo(sidebar, "LUMEN", font=("Cinzel", 20, "bold")).pack(pady=(25, 5))

        separador = ctk.CTkFrame(sidebar, fg_color=COR_INPUT_BORDER, height=1)
        separador.pack(fill="x", padx=20, pady=(5, 20))

        itens = [
            ("DASHBOARD", True),
            ("LIVROS", False),
            ("CADASTRO ALUNOS", False),
            ("CADASTRO MEMBROS", False),
            ("EMPRESTIMOS", False),
            ("DEVOLUCOES", False),
            ("CONFIGURACOES", False),
        ]

        self._botoes_nav = []
        for nome, ativo in itens:
            btn = ctk.CTkButton(
                sidebar, text=nome, font=FONTE_NAV,
                fg_color=COR_ATIVO if ativo else "transparent",
                text_color=COR_DOURADO if ativo else COR_TEXTO2,
                hover_color=COR_ATIVO,
                anchor="w", height=38,
                command=lambda n=nome: self._navegar(n)
            )
            btn.pack(fill="x", padx=15, pady=2)
            self._botoes_nav.append((btn, nome))

    def _criar_conteudo(self):
        self._conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self._conteudo.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self._conteudo.grid_columnconfigure(0, weight=1)
        self._conteudo.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self._conteudo, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        criar_label(header, "Dashboard", font=("Segoe UI Light", 22), text_color=COR_TEXTO).pack(anchor="w")

        self._criar_cards(self._conteudo)
        self._criar_graficos(self._conteudo)

    def _recriar_conteudo(self):
        for widget in self._conteudo.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self._conteudo, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        criar_label(header, "Dashboard", font=("Segoe UI Light", 22), text_color=COR_TEXTO).pack(anchor="w")

        self._criar_cards(self._conteudo)
        self._criar_graficos(self._conteudo)

    def _criar_cards(self, parent):
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        cards = [
            ("Total de Livros", str(self._stats['livros']), COR_DOURADO),
            ("Emprestimos", str(self._stats['emprestimos']), COR_TEXTO2),
            ("Alunos", str(self._stats['alunos']), "#6b5a48"),
            ("Taxa de Retorno", f"{self._stats['taxa_retorno']}%", "#4a3a28"),
        ]

        for i, (titulo, valor, cor) in enumerate(cards):
            card = criar_card(cards_frame)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

            indicator = ctk.CTkFrame(card, fg_color=cor, width=4, corner_radius=2)
            indicator.pack(side="left", fill="y", padx=(10, 5), pady=10)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

            criar_label(info, titulo, font=FONTE_LABEL).pack(anchor="w")
            criar_label(info, valor, font=("Segoe UI Semibold", 24), text_color=COR_TEXTO).pack(anchor="w")

    def _criar_graficos(self, parent):
        graficos_frame = ctk.CTkFrame(parent, fg_color="transparent")
        graficos_frame.grid(row=2, column=0, sticky="nsew")
        graficos_frame.grid_columnconfigure((0, 1), weight=1)
        graficos_frame.grid_rowconfigure(0, weight=1)
        graficos_frame.grid_rowconfigure(1, weight=1)

        self._criar_grafico_barras_matplotlib(graficos_frame, "Emprestimos por Mes", self._emp_mes, 0, 0)
        self._criar_grafico_pizza_matplotlib(graficos_frame, "Livros por Categoria", self._cat_livros, 0, 1)
        self._criar_grafico_semana_matplotlib(graficos_frame, "Emprestimos da Semana", self._emp_semana, 1, 0, 2)

    def _criar_grafico_barras_matplotlib(self, parent, titulo, dados, row, col):
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        criar_label(card, titulo, font=FONTE_LABEL).pack(anchor="w", padx=15, pady=(12, 5))

        if not dados:
            criar_label(card, "Sem dados disponiveis").pack(expand=True, pady=50)
            return

        fig = Figure(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor(COR_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(COR_CARD)

        meses = [MESES[m] for m, _ in dados]
        valores = [v for _, v in dados]

        cores = [COR_GRAF1 if v == max(valores) else COR_GRAF3 for v in valores]
        barras = ax.bar(meses, valores, color=cores, edgecolor=COR_INPUT_BORDER, linewidth=0.5, width=0.6)

        for barra, valor in zip(barras, valores):
            ax.text(barra.get_x() + barra.get_width()/2., barra.get_height() + 0.1,
                    str(valor), ha='center', va='bottom', color=COR_TEXTO, fontsize=8, fontweight='bold')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COR_INPUT_BORDER)
        ax.spines['bottom'].set_color(COR_INPUT_BORDER)
        ax.tick_params(colors=COR_TEXTO2, labelsize=8)
        ax.set_ylim(0, max(valores) * 1.2 if max(valores) > 0 else 1)
        ax.grid(axis='y', alpha=0.2, color=COR_INPUT_BORDER)

        fig.tight_layout(pad=1.5)

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        plt.close(fig)

    def _criar_grafico_pizza_matplotlib(self, parent, titulo, dados, row, col):
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        criar_label(card, titulo, font=FONTE_LABEL).pack(anchor="w", padx=15, pady=(12, 5))

        if not dados:
            criar_label(card, "Sem dados disponiveis").pack(expand=True, pady=50)
            return

        fig = Figure(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor(COR_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(COR_CARD)

        categorias = [c for c, _ in dados]
        valores = [v for _, v in dados]
        cores = [COR_GRAF1, COR_GRAF2, COR_GRAF3, COR_GRAF4, COR_GRAF5]

        wedges, texts, autotexts = ax.pie(
            valores, labels=categorias, autopct='%1.0f%%',
            colors=cores[:len(categorias)],
            startangle=90, pctdistance=0.75,
            wedgeprops=dict(width=0.5, edgecolor=COR_CARD, linewidth=2)
        )

        for text in texts:
            text.set_color(COR_TEXTO2)
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_color(COR_TEXTO)
            autotext.set_fontsize(7)
            autotext.set_fontweight('bold')

        centre_circle = plt.Circle((0, 0), 0.35, fc=COR_CARD)
        ax.add_artist(centre_circle)

        total = sum(valores)
        ax.text(0, 0, str(total), ha='center', va='center', fontsize=14, fontweight='bold', color=COR_TEXTO)

        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        plt.close(fig)

    def _criar_grafico_semana_matplotlib(self, parent, titulo, dados, row, col, colspan):
        card = criar_card(parent)
        card.grid(row=row, column=col, columnspan=colspan, padx=5, pady=5, sticky="nsew")

        criar_label(card, titulo, font=FONTE_LABEL).pack(anchor="w", padx=15, pady=(12, 5))

        fig = Figure(figsize=(10, 3), dpi=100)
        fig.patch.set_facecolor(COR_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(COR_CARD)

        dados_map = {d: 0 for d in DIAS}
        for dia, total in dados:
            if dia in dados_map:
                dados_map[dia] = total

        valores = [dados_map[d] for d in DIAS]
        max_val = max(valores) if valores else 1

        cores = [COR_GRAF1 if v == max_val and v > 0 else COR_GRAF3 for v in valores]
        barras = ax.bar(DIAS, valores, color=cores, edgecolor=COR_INPUT_BORDER, linewidth=0.5, width=0.5)

        for barra, valor in zip(barras, valores):
            if valor > 0:
                ax.text(barra.get_x() + barra.get_width()/2., barra.get_height() + 0.1,
                        str(valor), ha='center', va='bottom', color=COR_TEXTO, fontsize=9, fontweight='bold')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COR_INPUT_BORDER)
        ax.spines['bottom'].set_color(COR_INPUT_BORDER)
        ax.tick_params(colors=COR_TEXTO2, labelsize=9)
        ax.set_ylim(0, max_val * 1.3 if max_val > 0 else 1)
        ax.grid(axis='y', alpha=0.2, color=COR_INPUT_BORDER)

        fig.tight_layout(pad=2.0)

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        plt.close(fig)

    def _navegar(self, nome):
        telas = {
            "LIVROS": "livros",
            "CADASTRO ALUNOS": "cadastro_alunos",
            "CADASTRO MEMBROS": "cadastro_membros",
            "EMPRESTIMOS": "emprestimos",
            "DEVOLUCOES": "devolucoes",
            "CONFIGURACOES": "configuracoes",
        }
        tela = telas.get(nome)
        if tela:
            self.controller.navegar_para(tela)
