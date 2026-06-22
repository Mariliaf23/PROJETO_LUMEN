import os
import sys
from PIL import Image

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
    COR_INPUT_BORDER, COR_ATIVO, FONTE_NAV, FONTE_LABEL,
    criar_label, criar_card
)

# Paleta refinada e alinhada com a identidade Lumen
COR_GRAF_AZUL = "#0091FF"
COR_GRAF_DOURADO = "#D4A373"
COR_GRAF_CLARO = "#E6C79C"
COR_GRAF_MUTED = "#334155"

MESES = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
DIAS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']


class Dashboard(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller

        # Configuração profissional para os gráficos Matplotlib
        plt.rcParams.update({
            'figure.facecolor': COR_CARD,
            'axes.facecolor': COR_CARD,
            'axes.edgecolor': 'none',
            'axes.labelcolor': COR_TEXTO2,
            'text.color': COR_TEXTO,
            'xtick.color': COR_TEXTO2,
            'ytick.color': COR_TEXTO2,
            'grid.color': COR_INPUT_BORDER,
            'grid.alpha': 0.15,
            'font.family': 'Segoe UI',
            'font.size': 11,
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
        sidebar = ctk.CTkFrame(self, fg_color=COR_SIDEBAR, width=260, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # === TOPO COM LOGO ===
        topo = ctk.CTkFrame(sidebar, fg_color="transparent")
        topo.pack(fill="x", pady=(25, 5), padx=10)

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "logo_lumen.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        if os.path.exists(logo_path):
            try:
                logo_img = ctk.CTkImage(Image.open(logo_path), size=(180, 180))
                lbl_logo = ctk.CTkLabel(topo, image=logo_img, text="")
                lbl_logo.pack()
            except Exception:
                ctk.CTkLabel(topo, text="LUMEN", font=("Cinzel", 28, "bold"), text_color=COR_DOURADO).pack()
        else:
            ctk.CTkLabel(topo, text="LUMEN", font=("Cinzel", 28, "bold"), text_color=COR_DOURADO).pack()

        separador = ctk.CTkFrame(sidebar, fg_color=COR_INPUT_BORDER, height=1)
        separador.pack(fill="x", padx=25, pady=(15, 20))

        # === MENU DE NAVEGAÇÃO ===
        itens = [
            ("🏠  Dashboard", True, "dashboard"),
            ("📚  Livros", False, "livros"),
            ("📦  Exemplares", False, "exemplares"),
            ("👨  Usuários", False, "cadastro_usuario"),
            ("🔄  Empréstimos", False, "emprestimos"),
            ("↩️  Devoluções", False, "devolucoes"),
            ("⚙️  Configurações", False, "configuracoes"),
        ]

        self._botoes_nav = []
        for nome, ativo, chave in itens:
            btn = ctk.CTkButton(
                sidebar,
                text=nome,
                font=("Segoe UI", 15, "bold" if ativo else "normal"),
                fg_color=COR_ATIVO if ativo else "transparent",
                text_color=COR_TEXTO if ativo else COR_TEXTO2,
                hover_color=COR_ATIVO,
                anchor="w",
                height=48,
                corner_radius=8,
                command=lambda k=chave: self._navegar(k)
            )
            btn.pack(fill="x", padx=15, pady=5)
            self._botoes_nav.append((btn, nome))

        # Rodapé corporativo
        ctk.CTkLabel(sidebar, text="v1.0 • LUMEN SYSTEM", font=("Segoe UI", 11), text_color=COR_INPUT_BORDER).pack(side="bottom", pady=20)

    def _criar_conteudo(self):
        self._conteudo = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self._conteudo.grid(row=0, column=1, sticky="nsew", padx=(25, 10), pady=30)
        self._conteudo.grid_columnconfigure(0, weight=1)

        self._criar_header()
        self._criar_cards(self._conteudo)
        self._criar_graficos(self._conteudo)

    def _criar_header(self):
        header = ctk.CTkFrame(self._conteudo, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 25), padx=10)

        ctk.CTkLabel(
            header,
            text="Visão Geral",
            font=("Segoe UI", 38, "bold"),
            text_color=COR_TEXTO
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Acompanhe métricas, acervos e fluxo de leitores em tempo real.",
            font=("Segoe UI", 15),
            text_color=COR_TEXTO2
        ).pack(anchor="w", pady=(2, 0))

    def _recriar_conteudo(self):
        for widget in self._conteudo.winfo_children():
            widget.destroy()
        self._criar_header()
        self._criar_cards(self._conteudo)
        self._criar_graficos(self._conteudo)

    def _criar_cards(self, parent):
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 25), padx=10)
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        cards = [
            ("TOTAL NO ACERVO", str(self._stats.get('livros', 0)), "Títulos catalogados", COR_GRAF_AZUL),
            ("EMPRÉSTIMOS ATIVOS", str(self._stats.get('emprestimos', 0)), "Livros em circulação", COR_GRAF_DOURADO),
            ("LEITORES ATIVOS", str(self._stats.get('usuarios', 0)), "Usuários na plataforma", COR_TEXTO),
            ("ALERTAS DE ATRASO", str(self._stats.get('atrasados', 0)), "Devoluções pendentes", "#EF4444"),
        ]

        for i, (titulo, valor, subtitulo, cor_valor) in enumerate(cards):
            card = criar_card(cards_frame)
            card.grid(row=0, column=i, padx=8, pady=0, sticky="nsew")

            criar_label(card, titulo, font=("Segoe UI", 11, "bold"), text_color=COR_TEXTO2).pack(anchor="center", pady=(20, 2))
            ctk.CTkLabel(card, text=valor, font=("Segoe UI", 58, "bold"), text_color=cor_valor).pack(anchor="center")
            criar_label(card, subtitulo, font=("Segoe UI", 12), text_color=COR_INPUT_BORDER).pack(anchor="center", pady=(0, 20))

    def _criar_graficos(self, parent):
        graficos_frame = ctk.CTkFrame(parent, fg_color="transparent")
        graficos_frame.grid(row=2, column=0, sticky="nsew", padx=10)
        graficos_frame.grid_columnconfigure((0, 1), weight=1)

        self._criar_grafico_barras_matplotlib(graficos_frame, "Movimentação Mensal", self._emp_mes, 0, 0)
        self._criar_grafico_pizza_matplotlib(graficos_frame, "Distribuição por Categoria", self._cat_livros, 0, 1)
        self._criar_grafico_semana_matplotlib(graficos_frame, "Fluxo de Empréstimos Diários", self._emp_semana, 1, 0, 2)

    def _criar_grafico_barras_matplotlib(self, parent, titulo, dados, row, col):
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 12, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=20, pady=(15, 10))

        if not dados:
            criar_label(card, "Sem movimentações registradas neste período.", font=("Segoe UI", 12)).pack(expand=True, pady=80)
            return

        fig = Figure(figsize=(5.0, 3.8), dpi=100)
        ax = fig.add_subplot(111)

        meses = [MESES[m] for m, _ in dados]
        valores = [v for _, v in dados]

        cores = [COR_GRAF_AZUL if v == max(valores) else COR_GRAF_MUTED for v in valores]
        barras = ax.bar(meses, valores, color=cores, width=0.55, edgecolor='none')

        for barra, valor in zip(barras, valores):
            ax.text(barra.get_x() + barra.get_width()/2., barra.get_height() + (max(valores)*0.02),
                    str(valor), ha='center', va='bottom', color=COR_TEXTO, fontsize=9, fontweight='bold')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(bottom=False, left=False, colors=COR_TEXTO2, labelsize=9)
        ax.set_ylim(0, max(valores) * 1.25 if max(valores) > 0 else 1)
        ax.grid(axis='y', alpha=0.1, color=COR_TEXTO2)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))
        plt.close(fig)

    def _criar_grafico_pizza_matplotlib(self, parent, titulo, dados, row, col):
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 12, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=20, pady=(15, 5))

        if not dados:
            criar_label(card, "Nenhum livro categorizado encontrado.", font=("Segoe UI", 12)).pack(expand=True, pady=80)
            return

        layout_container = ctk.CTkFrame(card, fg_color="transparent")
        layout_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        area_grafico = ctk.CTkFrame(layout_container, fg_color="transparent")
        area_grafico.pack(side="left", fill="both", expand=True)

        # CONFIGURAÇÃO DE TAMANHO SEGURO: Proporção retangular controlada para não esmagar verticalmente
        fig = Figure(figsize=(3.0, 2.5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Margem de segurança explícita para evitar cortes nas extremidades do canvas
        fig.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.10)

        categorias = [c for c, _ in dados]
        valores = [v for _, v in dados]
        cores = [COR_GRAF_AZUL, COR_GRAF_DOURADO, COR_GRAF_CLARO, COR_GRAF_MUTED, "#1E293B"]

        # AJUSTE NO RAIO (De 1.0 para 0.7): Reduz o tamanho do círculo para que caiba com folga no card vertical
        wedges, _ = ax.pie(
            valores, 
            colors=cores[:len(categorias)], 
            startangle=90, 
            radius=0.7,
            wedgeprops=dict(width=0.18, edgecolor=COR_CARD, linewidth=2)
        )

        canvas = FigureCanvasTkAgg(fig, master=area_grafico)
        canvas.draw()
        canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor="center")
        plt.close(fig)

        total = sum(valores)
        lbl_centro = ctk.CTkLabel(
            area_grafico, 
            text=f"TOTAL\n{total}\n100%", 
            font=("Segoe UI", 11, "bold"), 
            text_color=COR_TEXTO,
            justify="center"
        )
        lbl_centro.place(relx=0.5, rely=0.5, anchor="center")

        area_legenda = ctk.CTkFrame(layout_container, fg_color="transparent")
        area_legenda.pack(side="right", fill="y", padx=(10, 15), pady=25)
        
        ctk.CTkLabel(area_legenda, text="Categorias", font=("Segoe UI", 11, "bold"), text_color=COR_TEXTO2).pack(anchor="w", pady=(0, 8))

        for idx, cat in enumerate(categorias):
            item_frame = ctk.CTkFrame(area_legenda, fg_color="transparent")
            item_frame.pack(anchor="w", pady=4)

            marcador = ctk.CTkFrame(item_frame, width=12, height=12, fg_color=cores[idx % len(cores)], corner_radius=2)
            marcador.pack(side="left", padx=(0, 8))
            marcador.pack_propagate(False)

            ctk.CTkLabel(item_frame, text=cat, font=("Segoe UI", 12), text_color=COR_TEXTO).pack(side="left")

    def _criar_grafico_semana_matplotlib(self, parent, titulo, dados, row, col, colspan):
        card = criar_card(parent)
        card.grid(row=row, column=col, columnspan=colspan, padx=8, pady=12, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 12, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=20, pady=(15, 10))

        fig = Figure(figsize=(10, 3.6), dpi=100)
        ax = fig.add_subplot(111)

        dados_map = {d: 0 for d in DIAS}
        for dia, total in dados:
            if dia in dados_map:
                dados_map[dia] = total

        valores = [dados_map[d] for d in DIAS]
        max_val = max(valores) if valores else 1

        cores = [COR_GRAF_DOURADO if v == max_val and v > 0 else COR_GRAF_MUTED for v in valores]
        barras = ax.bar(DIAS, valores, color=cores, width=0.45, edgecolor='none')

        for barra, valor in zip(barras, valores):
            if valor > 0:
                ax.text(barra.get_x() + barra.get_width()/2., barra.get_height() + (max_val*0.03),
                        str(valor), ha='center', va='bottom', color=COR_TEXTO, fontsize=9, fontweight='bold')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(bottom=False, left=False, colors=COR_TEXTO2, labelsize=9)
        ax.set_ylim(0, max_val * 1.3 if max_val > 0 else 1)
        ax.grid(axis='y', alpha=0.1, color=COR_TEXTO2)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))
        plt.close(fig)

    def _navegar(self, nome):
        telas = {
            "livros": "livros",
            "exemplares": "exemplares",
            "cadastro_usuario": "cadastro_usuario",
            "emprestimos": "emprestimos",
            "devolucoes": "devolucoes",
            "configuracoes": "configuracoes",
        }
        if nome in telas:
            self.controller.navegar_para(telas[nome])