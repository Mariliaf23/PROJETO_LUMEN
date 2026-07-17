# dashboard.py — Tela principal do sistema (dashboard com gráficos e estatísticas)

import os
import sys
import math
from datetime import datetime
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Configura caminho

import customtkinter as ctk  # Interface gráfica

from services.database_config import (    # Funções que buscam dados do banco
    buscar_stats_dashboard,              # Estatísticas gerais
    buscar_top_alunos_emprestimos,       # Top alunos com mais empréstimos
    buscar_ranking_turmas_emprestimos,   # Ranking de turmas
    buscar_livros_por_categoria_exemplares  # Livros por categoria (exemplares)
)
from services.styles import (            # Estilos e cores
    COR_BG, COR_SIDEBAR, COR_CARD, COR_DOURADO, COR_TEXTO, COR_TEXTO2,
    COR_INPUT_BORDER, COR_ATIVO, FONTE_NAV, FONTE_LABEL,
    criar_label, criar_card
)

# Cores específicas para os gráficos
COR_GRAF_AZUL    = "#0091FF"
COR_GRAF_DOURADO = "#D4A373"
COR_GRAF_CLARO   = "#E6C79C"
COR_GRAF_MUTED   = "#334155"

MESES = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
DIAS  = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
CORES_PIZZA = [COR_GRAF_AZUL, COR_GRAF_DOURADO, COR_GRAF_CLARO, COR_GRAF_MUTED, "#1E293B"]

# Definição visual dos 4 cards: (chave_stat, título, ícone, subtítulo, cor_acento)
CARDS_CONFIG = [
    ("livros",            "TOTAL NO ACERVO",    "📚", "Títulos catalogados",  COR_GRAF_AZUL),
    ("emprestimos_ativos","EMPRÉSTIMOS ATIVOS", "🔄", "Livros em circulação", COR_GRAF_DOURADO),
    ("usuarios",          "LEITORES ATIVOS",    "👥", "Usuários na plataforma",COR_TEXTO),
    ("atrasados",         "ALERTAS DE ATRASO",  "⚠️", "Devoluções pendentes",  "#EF4444"),
]


class CardEstatistica(ctk.CTkFrame):
    """Card de estatística com ícone, valor animado, barra lateral colorida e hover."""

    def __init__(self, master, titulo, icone, subtitulo, cor_acento, valor_final, **kw):
        super().__init__(master, fg_color=COR_CARD, corner_radius=16,
                         border_width=1, border_color=COR_INPUT_BORDER, **kw)
        self._cor_acento  = cor_acento
        self._valor_final = int(valor_final) if str(valor_final).isdigit() else 0
        self._valor_atual = 0

        # Barra lateral colorida
        barra = ctk.CTkFrame(self, fg_color=cor_acento, width=5, corner_radius=0)
        barra.pack(side="left", fill="y")
        barra.pack_propagate(False)

        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.pack(side="left", fill="both", expand=True, padx=(14, 16), pady=14)

        # Linha topo: ícone + título centralizados
        topo = ctk.CTkFrame(corpo, fg_color="transparent")
        topo.pack(fill="x")
        ctk.CTkLabel(topo, text=icone, font=("Segoe UI", 22), text_color=cor_acento).pack(side="left")
        ctk.CTkLabel(topo, text=titulo, font=("Segoe UI", 12, "bold"),
                     text_color=COR_TEXTO2).pack(side="left", padx=(8, 0))

        # Valor numérico (animado) — centralizado
        self._lbl_valor = ctk.CTkLabel(corpo, text="0",
                                       font=("Segoe UI", 52, "bold"), text_color=cor_acento,
                                       justify="center")
        self._lbl_valor.pack(fill="x", pady=(4, 0))

        # Subtítulo centralizado
        ctk.CTkLabel(corpo, text=subtitulo, font=("Segoe UI", 12),
                     text_color=COR_INPUT_BORDER, justify="center").pack(fill="x")

        # Hover: borda colorida ao entrar/sair (propaga para filhos)
        for w in (self, barra, corpo, topo):
            w.bind("<Enter>", lambda e: self.configure(border_color=cor_acento, border_width=2))
            w.bind("<Leave>", lambda e: self.configure(border_color=COR_INPUT_BORDER, border_width=1))

        # Inicia animação de contagem após 100ms (garante que o widget está visível)
        self.after(100, self._animar)

    def atualizar_valor(self, novo_valor):
        """Atualiza o valor final e reinicia a animação de contagem."""
        self._valor_final = int(novo_valor) if str(novo_valor).isdigit() else 0
        self._valor_atual = 0
        self._lbl_valor.configure(text="0")
        self.after(100, self._animar)

    def _animar(self):
        """Conta do 0 até valor_final em ~600ms."""
        if self._valor_atual < self._valor_final:
            passo = max(1, self._valor_final // 20)
            self._valor_atual = min(self._valor_atual + passo, self._valor_final)
            self._lbl_valor.configure(text=str(self._valor_atual))
            self.after(30, self._animar)
        else:
            self._lbl_valor.configure(text=str(self._valor_final))


class GraficoBarras(ctk.CTkCanvas):
    """Gráfico de barras desenhado em um Canvas do tkinter."""

    def __init__(self, master, dados, labels, cor_normal=COR_GRAF_MUTED, cor_destaque=COR_GRAF_AZUL, **kw):
        """Inicializa o gráfico de barras."""
        super().__init__(master, bg=COR_CARD, highlightthickness=0, **kw)  # Canvas com fundo escuro
        self.dados = dados                    # Valores numéricos de cada barra
        self.labels = labels                  # Rótulos abaixo de cada barra
        self.cor_normal = cor_normal          # Cor das barras normais
        self.cor_destaque = cor_destaque      # Cor da barra com maior valor
        self.bind("<Configure>", self._desenhar)  # Redesenha quando o tamanho muda

    def atualizar_dados(self, novos_dados, novos_labels=None):
        """Atualiza dados e redesenha o gráfico."""
        self.dados = novos_dados
        if novos_labels is not None:
            self.labels = novos_labels
        self._desenhar()

    def _desenhar(self, event=None):
        """Desenha o gráfico de barras no canvas."""
        self.delete("all")                    # Limpa tudo que estava desenhado
        w = self.winfo_width()                # Largura atual do canvas
        h = self.winfo_height()               # Altura atual do canvas
        if not self.dados or w < 50 or h < 50:  # Se não tem dados ou é muito pequeno
            return                            # Não desenha nada

        max_val = max(self.dados) if max(self.dados) > 0 else 1  # Maior valor (para escala)
        n = len(self.dados)                   # Quantidade de barras
        margem_esq, margem_dir, margem_topo, margem_base = 10, 10, 30, 40  # Margens
        largura_util = w - margem_esq - margem_dir  # Largura útil para barras
        altura_util = h - margem_topo - margem_base  # Altura útil para barras
        espaco = largura_util / n             # Espaço disponível para cada barra
        largura_barra = espaco * 0.55         # Barra ocupa 55% do espaço

        # Desenha cada barra
        for i, (valor, label) in enumerate(zip(self.dados, self.labels)):
            x_center = margem_esq + espaco * i + espaco / 2  # Centro da barra
            barra_h = (valor / max_val) * altura_util if max_val > 0 else 0  # Altura proporcional
            x0 = x_center - largura_barra / 2   # Canto superior esquerdo X
            y0 = h - margem_base                 # Canto inferior Y (base)
            x1 = x_center + largura_barra / 2   # Canto inferior direito X
            y1 = y0 - barra_h                   # Canto superior Y

            # Se é a maior barra, usa cor de destaque; senão, cor normal
            cor = self.cor_destaque if valor == max(self.dados) else self.cor_normal
            self.create_rectangle(x0, y0, x1, y1, fill=cor, outline="", width=0)  # Desenha a barra

            if valor > 0:                       # Se tem valor
                self.create_text(x_center, y1 - 8, text=str(valor),  # Número acima da barra
                                 fill=COR_TEXTO, font=("Segoe UI", 9, "bold"))

            self.create_text(x_center, h - margem_base + 15, text=label,  # Rótulo abaixo
                             fill=COR_TEXTO2, font=("Segoe UI", 9))

        # Desenha linhas de grade (4 linhas horizontais)
        for i in range(1, 5):
            y = h - margem_base - (altura_util * i / 4)  # Posição Y da linha
            self.create_line(margem_esq, y, w - margem_dir, y,  # Linha tracejada
                             fill=COR_INPUT_BORDER, dash=(3, 5))


class GraficoPizza(ctk.CTkCanvas):
    """Gráfico de pizza (donut) desenhado em um Canvas."""

    def __init__(self, master, dados, **kw):
        """Inicializa o gráfico de pizza."""
        super().__init__(master, bg=COR_CARD, highlightthickness=0, **kw)  # Canvas escuro
        self.dados = dados                    # Lista de (categoria, valor)
        self.bind("<Configure>", self._desenhar)  # Redesenha quando muda o tamanho

    def atualizar_dados(self, novos_dados):
        """Atualiza dados e redesenha o gráfico."""
        self.dados = novos_dados
        self._desenhar()

    def _desenhar(self, event=None):
        """Desenha o gráfico de pizza (formato donut)."""
        self.delete("all")                    # Limpa o canvas
        w = self.winfo_width()                # Largura
        h = self.winfo_height()               # Altura
        if not self.dados or w < 50 or h < 50:  # Se não tem dados
            return

        total = sum(v for _, v in self.dados)  # Soma todos os valores
        if total == 0:                        # Se o total é zero
            return                            # Não desenha nada

        cx, cy = w / 2, h / 2                # Centro do gráfico
        raio = min(w, h) / 2 - 20             # Raio externo
        raio_externo = raio                   # Raio de fora
        raio_interno = raio * 0.55            # Raio de dentro (formato donut)

        angulo_inicio = -90                   # Começa no topo (12 horas)
        for i, (cat, valor) in enumerate(self.dados):  # Para cada fatia
            fatia = (valor / total) * 360     # Ângulo da fatia em graus
            angulo_fim = angulo_inicio + fatia  # Ângulo final
            cor = CORES_PIZZA[i % len(CORES_PIZZA)]  # Cor ciclca

            pontos = []                       # Lista de pontos do polígono
            # Parte externa da fatia
            for grau in range(int(angulo_inicio), int(angulo_fim) + 1):
                rad = math.radians(grau)      # Converte graus para radianos
                pontos.append(cx + raio_externo * math.cos(rad))  # Ponto X externo
                pontos.append(cy + raio_externo * math.sin(rad))  # Ponto Y externo
            # Parte interna da fatia (volta no sentido contrário)
            for grau in range(int(angulo_fim), int(angulo_inicio) - 1, -1):
                rad = math.radians(grau)
                pontos.append(cx + raio_interno * math.cos(rad))  # Ponto X interno
                pontos.append(cy + raio_interno * math.sin(rad))  # Ponto Y interno

            if len(pontos) >= 6:              # Se tem pontos suficientes
                self.create_polygon(pontos, fill=cor, outline=COR_CARD, width=2)  # Desenha a fatia

            angulo_inicio = angulo_fim        # Próxima fatia começa onde esta terminou

        # Texto no centro: total e porcentagem
        self.create_text(cx, cy - 8, text=str(total), fill=COR_TEXTO,
                         font=("Segoe UI", 12, "bold"))
        self.create_text(cx, cy + 10, text="100%", fill=COR_TEXTO2,
                         font=("Segoe UI", 9))


class Dashboard(ctk.CTkFrame):
    """Tela principal do sistema com sidebar, cards de estatísticas e gráficos."""

    def __init__(self, master=None, controller=None):
        """Inicializa o dashboard."""
        super().__init__(master, fg_color=COR_BG)  # Frame com fundo escuro
        self.controller = controller                 # Controlador de navegação

        self._carregar_dados()                       # Busca dados do banco
        self._construir_ui()                         # Monta a interface

    def _ao_visitar(self):
        """Chamado quando o usuário navega para esta tela — atualiza tudo."""
        if self.controller:
            self.controller.tela_atual = 'dashboard'
        self._carregar_dados()
        self._atualizar_conteudo()
        self._recriar_sidebar()

    def _carregar_dados(self):
        """Busca todas as estatísticas do banco de dados."""
        self._stats = buscar_stats_dashboard()
        self._top_alunos = buscar_top_alunos_emprestimos(10)
        self._ranking_turmas = buscar_ranking_turmas_emprestimos()
        self._cat_livros = buscar_livros_por_categoria_exemplares()

    def _construir_ui(self):
        """Monta a estrutura principal: sidebar à esquerda, conteúdo à direita."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_container = ctk.CTkFrame(self, fg_color=COR_SIDEBAR, width=260, corner_radius=0)
        self.sidebar_container.grid(row=0, column=0, sticky="nsew")
        self.sidebar_container.grid_propagate(False)

        self._criar_sidebar()
        self._criar_conteudo()

    def _recriar_sidebar(self):
        """Destrói e reconstrói a sidebar (usado apenas na construção inicial)."""
        for widget in self.sidebar_container.winfo_children():
            widget.destroy()
        self._criar_sidebar()

    def _atualizar_sidebar(self):
        """Atualiza cores/estilos dos botões da sidebar sem destruir widgets."""
        tela_atual = getattr(self.controller, 'tela_atual', 'dashboard') if self.controller else 'dashboard'
        for btn, chave in self._botoes_nav:
            ativo = (chave == tela_atual)
            btn.configure(
                font=("Segoe UI", 15, "bold" if ativo else "normal"),
                fg_color=COR_ATIVO if ativo else "transparent",
                text_color=COR_TEXTO if ativo else COR_TEXTO2,
            )

    def _criar_sidebar(self):
        """Monta o menu lateral com logo e botões de navegação."""
        # Logo no topo da sidebar
        topo = ctk.CTkFrame(self.sidebar_container, fg_color="transparent")
        topo.pack(fill="x", pady=(25, 5), padx=10)

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")  # Caminho da logo

        if os.path.exists(logo_path):
            try:
                with Image.open(logo_path) as img:
                    self._logo_img = ctk.CTkImage(img.copy(), size=(180, 180))
                lbl_logo = ctk.CTkLabel(topo, image=self._logo_img, text="")
                lbl_logo.pack()
            except Exception:
                ctk.CTkLabel(topo, text="LUMEN", font=("Cinzel", 28, "bold"), text_color=COR_DOURADO).pack()
        else:
            ctk.CTkLabel(topo, text="LUMEN", font=("Cinzel", 28, "bold"), text_color=COR_DOURADO).pack()

        # Linha separadora
        ctk.CTkFrame(self.sidebar_container, fg_color=COR_INPUT_BORDER, height=1).pack(fill="x", padx=25, pady=(15, 20))

        # Verifica o tipo do usuário logado
        tipo_usuario = None
        if self.controller and hasattr(self.controller, 'usuario_logado') and self.controller.usuario_logado:
            tipo_usuario = self.controller.usuario_logado.get('tipo', '').lower()

        # Tela atual para marcar item ativo
        tela_atual = getattr(self.controller, 'tela_atual', 'dashboard') if self.controller else 'dashboard'

        itens = [
            ("🏠   Dashboard", "dashboard"),
            ("📚   Livros",    "livros"),
            ("🔍   Catálogo",  "catalogo"),
        ]
        if tipo_usuario in ('admin', 'diretor'):
            itens.extend([
                ("📦   Exemplares",    "exemplares"),
                ("🔄   Empréstimos",   "emprestimos"),
                ("👥   Usuários",      "gerenciar_usuarios"),
                ("📊   Relatórios",    "relatorios"),
                ("📲   Notificações",  "notificacoes"),
                ("⚙️   Configurações", "configuracoes"),
            ])

        self._botoes_nav = []
        for nome, chave in itens:
            ativo = (chave == tela_atual)
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
            btn.pack(fill="x", padx=15, pady=3)
            self._botoes_nav.append((btn, chave))

        # Separador acima do rodapé
        ctk.CTkFrame(self.sidebar_container, fg_color=COR_INPUT_BORDER, height=1).pack(
            side="bottom", fill="x", padx=25, pady=(0, 0))
        ctk.CTkLabel(self.sidebar_container, text="v1.0 • LUMEN SYSTEM",
                     font=("Segoe UI", 11), text_color=COR_INPUT_BORDER).pack(side="bottom", pady=(12, 8))

    def _criar_conteudo(self):
        """Monta o conteúdo principal: header, cards e gráficos."""
        self._conteudo = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self._conteudo.grid(row=0, column=1, sticky="nsew", padx=(25, 10), pady=30)
        self._conteudo.grid_columnconfigure(0, weight=1)

        self._criar_header()
        self._criar_cards(self._conteudo)
        self._criar_graficos(self._conteudo)

    def _criar_header(self):
        """Cria o cabeçalho com título, subtítulo, data/hora e botão atualizar."""
        header = ctk.CTkFrame(self._conteudo, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20), padx=10)
        header.grid_columnconfigure(0, weight=1)

        # Linha superior: título + botão atualizar
        linha_topo = ctk.CTkFrame(header, fg_color="transparent")
        linha_topo.pack(fill="x")
        linha_topo.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            linha_topo, text="Visão Geral",
            font=("Segoe UI", 38, "bold"), text_color=COR_TEXTO
        ).pack(side="left")

        ctk.CTkButton(
            linha_topo, text="↻  Atualizar",
            font=("Segoe UI", 13, "bold"),
            fg_color=COR_CARD, hover_color=COR_ATIVO,
            text_color=COR_TEXTO2, border_width=1, border_color=COR_INPUT_BORDER,
            width=130, height=36, corner_radius=8,
            command=self._atualizar
        ).pack(side="right", pady=(8, 0))

        # Subtítulo + data/hora
        linha_sub = ctk.CTkFrame(header, fg_color="transparent")
        linha_sub.pack(fill="x", pady=(2, 0))

        ctk.CTkLabel(
            linha_sub,
            text="Acompanhe métricas, acervos e fluxo de leitores em tempo real.",
            font=("Segoe UI", 15), text_color=COR_TEXTO2
        ).pack(side="left")

        self._lbl_hora = ctk.CTkLabel(
            linha_sub, text="",
            font=("Segoe UI", 13), text_color=COR_INPUT_BORDER
        )
        self._lbl_hora.pack(side="right")
        self._atualizar_hora()

        # Separador abaixo do header
        ctk.CTkFrame(header, fg_color=COR_INPUT_BORDER, height=1).pack(fill="x", pady=(12, 0))

    def _atualizar_hora(self):
        """Atualiza o label de data/hora a cada minuto."""
        if not self._lbl_hora.winfo_exists():
            return
        agora = datetime.now().strftime("%d/%m/%Y  %H:%M")
        self._lbl_hora.configure(text=agora)
        self._lbl_hora.after(60_000, self._atualizar_hora)

    def _atualizar(self):
        """Botão Atualizar: recarrega dados e atualiza na tela."""
        self._carregar_dados()
        self._atualizar_conteudo()

    def _atualizar_conteudo(self):
        """Atualiza dados dos cards e gráficos na tela."""
        for i, (_, _, _, _, _) in enumerate(CARDS_CONFIG):
            if i < len(self._cards):
                valor = self._stats.get(CARDS_CONFIG[i][0], 0)
                self._cards[i].atualizar_valor(valor)

        if self._graf_pizza:
            dados_pizza = [(cat, total) for cat, total, _ in self._cat_livros]
            self._graf_pizza.atualizar_dados(dados_pizza)

        # Reconstrói os rankings (barras horizontais não suportam atualização in-place)
        if getattr(self, '_frame_ranking_alunos', None):
            for widget in self._frame_ranking_alunos.winfo_children():
                widget.destroy()
            self._criar_lista_ranking(self._frame_ranking_alunos, self._top_alunos)

        if getattr(self, '_frame_ranking_turmas', None):
            for widget in self._frame_ranking_turmas.winfo_children():
                widget.destroy()
            self._criar_lista_ranking(self._frame_ranking_turmas, self._ranking_turmas)

    def _criar_cards(self, parent):
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 25), padx=10)
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._cards = []
        for i, (chave, titulo, icone, subtitulo, cor) in enumerate(CARDS_CONFIG):
            valor = self._stats.get(chave, 0)
            card = CardEstatistica(cards_frame, titulo, icone, subtitulo, cor, valor)
            card.grid(row=0, column=i, padx=8, pady=0, sticky="nsew", ipadx=0, ipady=4)
            self._cards.append(card)

    def _criar_graficos(self, parent):
        """Cria os gráficos: ranking de alunos, ranking de turmas, pizza por categoria."""
        graficos_frame = ctk.CTkFrame(parent, fg_color="transparent")
        graficos_frame.grid(row=2, column=0, sticky="nsew", padx=10)
        graficos_frame.grid_columnconfigure((0, 1), weight=1)

        _, self._frame_ranking_alunos = self._criar_grafico_barras_h(graficos_frame, "Top 10 Alunos — Empréstimos", self._top_alunos, 0, 0)
        _, self._frame_ranking_turmas = self._criar_grafico_barras_h(graficos_frame, "Ranking de Turmas — Empréstimos", self._ranking_turmas, 0, 1)
        self._graf_pizza = self._criar_grafico_pizza(graficos_frame, "Exemplares por Categoria", self._cat_livros, 1, 0, 2)

    def _criar_grafico_barras(self, parent, titulo, dados, row, col):
        """Cria um card com gráfico de barras."""
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 10))

        if not dados:
            criar_label(card, "Sem movimentações registradas neste período.", font=("Segoe UI", 12)).pack(expand=True, pady=80)
            return None

        labels = [MESES[m] for m, _ in dados]
        valores = [v for _, v in dados]

        canvas = GraficoBarras(card, valores, labels, height=260)
        canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        return canvas

    def _criar_grafico_pizza(self, parent, titulo, dados, row, col, colspan=1):
        """Cria um card com gráfico de pizza e legenda com percentual."""
        card = criar_card(parent)
        card.grid(row=row, column=col, columnspan=colspan, padx=8, pady=8, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 5))

        if not dados:
            criar_label(card, "Nenhum exemplar categorizado.", font=("Segoe UI", 12)).pack(expand=True, pady=80)
            return None

        layout_container = ctk.CTkFrame(card, fg_color="transparent")
        layout_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        area_grafico = ctk.CTkFrame(layout_container, fg_color="transparent")
        area_grafico.pack(side="left", fill="both", expand=True)

        dados_pizza = [(cat, total) for cat, total, _ in dados]
        canvas = GraficoPizza(area_grafico, dados_pizza)
        canvas.pack(fill="both", expand=True)

        area_legenda = ctk.CTkFrame(layout_container, fg_color="transparent")
        area_legenda.pack(side="right", fill="y", padx=(10, 15), pady=25)

        ctk.CTkLabel(area_legenda, text="Categorias", font=("Segoe UI", 11, "bold"), text_color=COR_TEXTO2).pack(anchor="w", pady=(0, 8))

        for idx, (cat, total, perc) in enumerate(dados):
            item_frame = ctk.CTkFrame(area_legenda, fg_color="transparent")
            item_frame.pack(anchor="w", pady=4)

            marcador = ctk.CTkFrame(item_frame, width=12, height=12, fg_color=CORES_PIZZA[idx % len(CORES_PIZZA)], corner_radius=2)
            marcador.pack(side="left", padx=(0, 8))
            marcador.pack_propagate(False)

            ctk.CTkLabel(item_frame, text=f"{cat} ({total})", font=("Segoe UI", 12), text_color=COR_TEXTO).pack(side="left")
            ctk.CTkLabel(item_frame, text=f"{perc}%", font=("Segoe UI", 11), text_color=COR_TEXTO2).pack(side="left", padx=(8, 0))

        return canvas

    def _criar_grafico_barras_h(self, parent, titulo, dados, row, col):
        """Cria um card com gráfico de barras horizontal (ranking)."""
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 10))

        if not dados:
            criar_label(card, "Sem dados disponíveis.", font=("Segoe UI", 12)).pack(expand=True, pady=80)
            return None, None

        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent", height=260)
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self._criar_lista_ranking(scroll, dados)

        return card, scroll

    def _criar_lista_ranking(self, scroll, dados):
        """Preenche um scroll frame com barras de ranking."""
        max_val = max(t for _, t in dados) if dados else 1
        cores = [COR_GRAF_AZUL, COR_GRAF_DOURADO, COR_GRAF_CLARO, COR_GRAF_MUTED, "#1E293B"]

        for idx, (nome, total) in enumerate(dados):
            barra_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            barra_frame.pack(fill="x", pady=2)

            lbl_nome = ctk.CTkLabel(barra_frame, text=f"{idx+1}. {nome}", font=("Segoe UI", 12), text_color=COR_TEXTO, anchor="w", width=180)
            lbl_nome.pack(side="left")

            barra_bg = ctk.CTkFrame(barra_frame, fg_color=COR_GRAF_MUTED, height=20, corner_radius=4)
            barra_bg.pack(side="left", fill="x", expand=True, padx=(10, 10))
            barra_bg.pack_propagate(False)

            largura = (total / max_val) if max_val > 0 else 0
            barra_fill = ctk.CTkFrame(barra_bg, fg_color=cores[idx % len(cores)], corner_radius=4)
            barra_fill.place(relx=0, rely=0, relwidth=largura, relheight=1)

            ctk.CTkLabel(barra_frame, text=str(total), font=("Segoe UI", 12, "bold"), text_color=COR_TEXTO, width=40).pack(side="right")

    def _navegar(self, nome):
        """Navega para outra tela e atualiza o item ativo na sidebar."""
        if self.controller:
            self.controller.tela_atual = nome
            self._atualizar_sidebar()
            self.controller.navegar_para(nome)
