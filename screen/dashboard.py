import os
import sys
import math
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk

from services.database_config import (
    buscar_stats_dashboard, buscar_emprestimos_por_mes,
    buscar_livros_por_categoria, buscar_emprestimos_semana
)
from services.styles import (
    COR_BG, COR_SIDEBAR, COR_CARD, COR_DOURADO, COR_TEXTO, COR_TEXTO2,
    COR_INPUT_BORDER, COR_ATIVO, FONTE_NAV, FONTE_LABEL,
    criar_label, criar_card
)

COR_GRAF_AZUL = "#0091FF"
COR_GRAF_DOURADO = "#D4A373"
COR_GRAF_CLARO = "#E6C79C"
COR_GRAF_MUTED = "#334155"

MESES = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
DIAS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
CORES_PIZZA = [COR_GRAF_AZUL, COR_GRAF_DOURADO, COR_GRAF_CLARO, COR_GRAF_MUTED, "#1E293B"]


class GraficoBarras(ctk.CTkCanvas):
    def __init__(self, master, dados, labels, cor_normal=COR_GRAF_MUTED, cor_destaque=COR_GRAF_AZUL, **kw):
        super().__init__(master, bg=COR_CARD, highlightthickness=0, **kw)
        self.dados = dados
        self.labels = labels
        self.cor_normal = cor_normal
        self.cor_destaque = cor_destaque
        self.bind("<Configure>", self._desenhar)

    def _desenhar(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if not self.dados or w < 50 or h < 50:
            return

        max_val = max(self.dados) if max(self.dados) > 0 else 1
        n = len(self.dados)
        margem_esq, margem_dir, margem_topo, margem_base = 10, 10, 30, 40
        largura_util = w - margem_esq - margem_dir
        altura_util = h - margem_topo - margem_base
        espaco = largura_util / n
        largura_barra = espaco * 0.55

        for i, (valor, label) in enumerate(zip(self.dados, self.labels)):
            x_center = margem_esq + espaco * i + espaco / 2
            barra_h = (valor / max_val) * altura_util if max_val > 0 else 0
            x0 = x_center - largura_barra / 2
            y0 = h - margem_base
            x1 = x_center + largura_barra / 2
            y1 = y0 - barra_h

            cor = self.cor_destaque if valor == max(self.dados) else self.cor_normal
            self.create_rectangle(x0, y0, x1, y1, fill=cor, outline="", width=0)

            if valor > 0:
                self.create_text(x_center, y1 - 8, text=str(valor),
                                 fill=COR_TEXTO, font=("Segoe UI", 9, "bold"))

            self.create_text(x_center, h - margem_base + 15, text=label,
                             fill=COR_TEXTO2, font=("Segoe UI", 9))

        for i in range(1, 5):
            y = h - margem_base - (altura_util * i / 4)
            self.create_line(margem_esq, y, w - margem_dir, y,
                             fill=COR_INPUT_BORDER, dash=(3, 5))


class GraficoPizza(ctk.CTkCanvas):
    def __init__(self, master, dados, **kw):
        super().__init__(master, bg=COR_CARD, highlightthickness=0, **kw)
        self.dados = dados
        self.bind("<Configure>", self._desenhar)

    def _desenhar(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if not self.dados or w < 50 or h < 50:
            return

        total = sum(v for _, v in self.dados)
        if total == 0:
            return

        cx, cy = w / 2, h / 2
        raio = min(w, h) / 2 - 20
        raio_externo = raio
        raio_interno = raio * 0.55

        angulo_inicio = -90
        for i, (cat, valor) in enumerate(self.dados):
            fatia = (valor / total) * 360
            angulo_fim = angulo_inicio + fatia
            cor = CORES_PIZZA[i % len(CORES_PIZZA)]

            pontos = []
            for grau in range(int(angulo_inicio), int(angulo_fim) + 1):
                rad = math.radians(grau)
                pontos.append(cx + raio_externo * math.cos(rad))
                pontos.append(cy + raio_externo * math.sin(rad))
            for grau in range(int(angulo_fim), int(angulo_inicio) - 1, -1):
                rad = math.radians(grau)
                pontos.append(cx + raio_interno * math.cos(rad))
                pontos.append(cy + raio_interno * math.sin(rad))

            if len(pontos) >= 6:
                self.create_polygon(pontos, fill=cor, outline=COR_CARD, width=2)

            angulo_inicio = angulo_fim

        self.create_text(cx, cy - 8, text=str(total), fill=COR_TEXTO,
                         font=("Segoe UI", 12, "bold"))
        self.create_text(cx, cy + 10, text="100%", fill=COR_TEXTO2,
                         font=("Segoe UI", 9))


class Dashboard(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller

        self._carregar_dados()
        self._construir_ui()

    def _ao_visitar(self):
        self._carregar_dados()
        self._recriar_conteudo()
        self._recriar_sidebar()

    def _carregar_dados(self):
        self._stats = buscar_stats_dashboard()
        self._emp_mes = buscar_emprestimos_por_mes()
        self._cat_livros = buscar_livros_por_categoria()
        self._emp_semana = buscar_emprestimos_semana()

    def _construir_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_container = ctk.CTkFrame(self, fg_color=COR_SIDEBAR, width=260, corner_radius=0)
        self.sidebar_container.grid(row=0, column=0, sticky="nsew")
        self.sidebar_container.grid_propagate(False)

        self._criar_sidebar()
        self._criar_conteudo()

    def _recriar_sidebar(self):
        for widget in self.sidebar_container.winfo_children():
            widget.destroy()
        self._criar_sidebar()

    def _criar_sidebar(self):
        topo = ctk.CTkFrame(self.sidebar_container, fg_color="transparent")
        topo.pack(fill="x", pady=(25, 5), padx=10)

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

        separador = ctk.CTkFrame(self.sidebar_container, fg_color=COR_INPUT_BORDER, height=1)
        separador.pack(fill="x", padx=25, pady=(15, 20))

        tipo_usuario = None
        if self.controller and hasattr(self.controller, 'usuario_logado') and self.controller.usuario_logado:
            tipo_usuario = self.controller.usuario_logado.get('tipo', '').lower()

        itens = [
            ("🏠   Dashboard", True, "dashboard"),
            ("📚   Livros", False, "livros"),
        ]

        if tipo_usuario in ('admin', 'diretor'):
            itens.extend([
                ("📦   Exemplares", False, "exemplares"),
                ("🔄   Empréstimos", False, "emprestimos"),
                ("↩️   Devoluções", False, "devolucoes"),
                ("👨   Usuários", False, "gerenciar_usuarios"),
                ("⚙️   Configurações", False, "configuracoes"),
            ])

        self._botoes_nav = []
        for nome, ativo, chave in itens:
            btn = ctk.CTkButton(
                self.sidebar_container,
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

        ctk.CTkLabel(self.sidebar_container, text="v1.0 • LUMEN SYSTEM",
                     font=("Segoe UI", 11), text_color=COR_INPUT_BORDER).pack(side="bottom", pady=20)

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

            criar_label(card, titulo, font=("Segoe UI", 13, "bold"), text_color=COR_TEXTO2).pack(anchor="center", pady=(20, 2))
            ctk.CTkLabel(card, text=valor, font=("Segoe UI", 58, "bold"), text_color=cor_valor).pack(anchor="center")
            criar_label(card, subtitulo, font=("Segoe UI", 12), text_color=COR_INPUT_BORDER).pack(anchor="center", pady=(0, 20))

    def _criar_graficos(self, parent):
        graficos_frame = ctk.CTkFrame(parent, fg_color="transparent")
        graficos_frame.grid(row=2, column=0, sticky="nsew", padx=10)
        graficos_frame.grid_columnconfigure((0, 1), weight=1)

        self._criar_grafico_barras(graficos_frame, "Movimentação Mensal", self._emp_mes, 0, 0)
        self._criar_grafico_pizza(graficos_frame, "Distribuição por Categoria", self._cat_livros, 0, 1)
        self._criar_grafico_semana(graficos_frame, "Fluxo de Empréstimos Diários", self._emp_semana, 1, 0, 2)

    def _criar_grafico_barras(self, parent, titulo, dados, row, col):
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 10))

        if not dados:
            criar_label(card, "Sem movimentações registradas neste período.", font=("Segoe UI", 12)).pack(expand=True, pady=80)
            return

        labels = [MESES[m] for m, _ in dados]
        valores = [v for _, v in dados]

        canvas = GraficoBarras(card, valores, labels, height=260)
        canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _criar_grafico_pizza(self, parent, titulo, dados, row, col):
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 5))

        if not dados:
            criar_label(card, "Nenhum livro categorizado encontrado.", font=("Segoe UI", 12)).pack(expand=True, pady=80)
            return

        layout_container = ctk.CTkFrame(card, fg_color="transparent")
        layout_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        area_grafico = ctk.CTkFrame(layout_container, fg_color="transparent")
        area_grafico.pack(side="left", fill="both", expand=True)

        canvas = GraficoPizza(area_grafico, dados)
        canvas.pack(fill="both", expand=True)

        area_legenda = ctk.CTkFrame(layout_container, fg_color="transparent")
        area_legenda.pack(side="right", fill="y", padx=(10, 15), pady=25)

        ctk.CTkLabel(area_legenda, text="Categorias", font=("Segoe UI", 11, "bold"), text_color=COR_TEXTO2).pack(anchor="w", pady=(0, 8))

        categorias = [c for c, _ in dados]
        for idx, cat in enumerate(categorias):
            item_frame = ctk.CTkFrame(area_legenda, fg_color="transparent")
            item_frame.pack(anchor="w", pady=4)

            marcador = ctk.CTkFrame(item_frame, width=12, height=12, fg_color=CORES_PIZZA[idx % len(CORES_PIZZA)], corner_radius=2)
            marcador.pack(side="left", padx=(0, 8))
            marcador.pack_propagate(False)

            ctk.CTkLabel(item_frame, text=cat, font=("Segoe UI", 12), text_color=COR_TEXTO).pack(side="left")

    def _criar_grafico_semana(self, parent, titulo, dados, row, col, colspan):
        card = criar_card(parent)
        card.grid(row=row, column=col, columnspan=colspan, padx=8, pady=12, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 10))

        dados_map = {d: 0 for d in DIAS}
        for dia, total in dados:
            if dia in dados_map:
                dados_map[dia] = total

        valores = [dados_map[d] for d in DIAS]
        canvas = GraficoBarras(card, valores, DIAS,
                               cor_normal=COR_GRAF_MUTED, cor_destaque=COR_GRAF_DOURADO, height=240)
        canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _navegar(self, nome):
        telas = {
            "livros": "livros",
            "exemplares": "exemplares",
            "cadastro_usuario": "cadastro_usuario",
            "emprestimos": "emprestimos",
            "devolucoes": "devolucoes",
            "configuracoes": "configuracoes",
            "gerenciar_usuarios": "gerenciar_usuarios",
        }
        if nome in telas:
            self.controller.navegar_para(telas[nome])
