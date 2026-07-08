# dashboard.py — Tela principal do sistema (dashboard com gráficos e estatísticas)

import os                  # Biblioteca para manipular caminhos
import sys                 # Biblioteca do sistema
import math                # Biblioteca matemática (para cálculos dos gráficos)
from PIL import Image      # Biblioteca para abrir imagens

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Configura caminho

import customtkinter as ctk  # Interface gráfica

from services.database_config import (    # Funções que buscam dados do banco
    buscar_stats_dashboard,              # Estatísticas gerais
    buscar_emprestimos_por_mes,          # Empréstimos agrupados por mês
    buscar_livros_por_categoria,         # Livros agrupados por categoria
    buscar_emprestimos_semana            # Empréstimos da semana atual
)
from services.styles import (            # Estilos e cores
    COR_BG, COR_SIDEBAR, COR_CARD, COR_DOURADO, COR_TEXTO, COR_TEXTO2,
    COR_INPUT_BORDER, COR_ATIVO, FONTE_NAV, FONTE_LABEL,
    criar_label, criar_card
)

# Cores específicas para os gráficos
COR_GRAF_AZUL = "#0091FF"       # Azul vibrante
COR_GRAF_DOURADO = "#D4A373"    # Dourado
COR_GRAF_CLARO = "#E6C79C"      # Dourado claro
COR_GRAF_MUTED = "#334155"      # Cinza apagado

MESES = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']  # Nomes dos meses
DIAS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']  # Dias da semana
CORES_PIZZA = [COR_GRAF_AZUL, COR_GRAF_DOURADO, COR_GRAF_CLARO, COR_GRAF_MUTED, "#1E293B"]  # Cores do gráfico de pizza


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
        self._carregar_dados()                       # Recarrega dados do banco
        self._recriar_conteudo()                     # Redesenha o conteúdo
        self._recriar_sidebar()                      # Redesenha o menu lateral

    def _carregar_dados(self):
        """Busca todas as estatísticas do banco de dados."""
        self._stats = buscar_stats_dashboard()         # Totais gerais
        self._emp_mes = buscar_emprestimos_por_mes()   # Empréstimos por mês
        self._cat_livros = buscar_livros_por_categoria()  # Livros por categoria
        self._emp_semana = buscar_emprestimos_semana()  # Empréstimos da semana

    def _construir_ui(self):
        """Monta a estrutura principal: sidebar à esquerda, conteúdo à direita."""
        self.grid_columnconfigure(1, weight=1)       # Coluna 1 (conteúdo) expansível
        self.grid_rowconfigure(0, weight=1)          # Linha 0 expansível

        # Sidebar (menu lateral)
        self.sidebar_container = ctk.CTkFrame(self, fg_color=COR_SIDEBAR, width=260, corner_radius=0)
        self.sidebar_container.grid(row=0, column=0, sticky="nsew")   # Coluna 0
        self.sidebar_container.grid_propagate(False)  # Mantém a largura fixa de 260px

        self._criar_sidebar()                        # Monta o menu lateral
        self._criar_conteudo()                       # Monta o conteúdo principal

    def _recriar_sidebar(self):
        """Destrói e reconstrói a sidebar (para atualizar itens do menu)."""
        for widget in self.sidebar_container.winfo_children():  # Para cada widget na sidebar
            widget.destroy()                       # Remove ele
        self._criar_sidebar()                      # Reconstrói

    def _criar_sidebar(self):
        """Monta o menu lateral com logo e botões de navegação."""
        # Logo no topo da sidebar
        topo = ctk.CTkFrame(self.sidebar_container, fg_color="transparent")
        topo.pack(fill="x", pady=(25, 5), padx=10)

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")  # Caminho da logo

        if os.path.exists(logo_path):             # Se a logo existe
            try:
                logo_img = ctk.CTkImage(Image.open(logo_path), size=(180, 180))  # Carrega imagem
                lbl_logo = ctk.CTkLabel(topo, image=logo_img, text="")  # Label com imagem
                lbl_logo.pack()                    # Mostra
            except Exception:                     # Se deu erro
                ctk.CTkLabel(topo, text="LUMEN", font=("Cinzel", 28, "bold"), text_color=COR_DOURADO).pack()
        else:                                      # Se não tem logo
            ctk.CTkLabel(topo, text="LUMEN", font=("Cinzel", 28, "bold"), text_color=COR_DOURADO).pack()

        # Linha separadora
        separador = ctk.CTkFrame(self.sidebar_container, fg_color=COR_INPUT_BORDER, height=1)
        separador.pack(fill="x", padx=25, pady=(15, 20))

        # Verifica o tipo do usuário logado para mostrar menus adequados
        tipo_usuario = None
        if self.controller and hasattr(self.controller, 'usuario_logado') and self.controller.usuario_logado:
            tipo_usuario = self.controller.usuario_logado.get('tipo', '').lower()

        # Itens do menu (sempre visíveis)
        itens = [
            ("🏠   Dashboard", True, "dashboard"),   # Dashboard (ativo por padrão)
            ("📚   Livros", False, "livros"),         # Livros
        ]

        # Itens extras para admin/diretor
        if tipo_usuario in ('admin', 'diretor'):
            itens.extend([
                ("📦   Gerenciar Livros", False, "exemplares"),   # Gerenciar Livros
                ("🔄   Empréstimos", False, "emprestimos"),      # Empréstimos
                ("↩️   Devoluções", False, "devolucoes"),        # Devoluções
                ("👨   Usuários", False, "gerenciar_usuarios"),  # Gerenciar usuários
                ("⚙️   Configurações", False, "configuracoes"),  # Configurações
            ])

        self._botoes_nav = []                     # Lista de botões de navegação
        for nome, ativo, chave in itens:          # Para cada item do menu
            btn = ctk.CTkButton(
                self.sidebar_container,
                text=nome,                        # Texto do botão
                font=("Segoe UI", 15, "bold" if ativo else "normal"),  # Negrito se ativo
                fg_color=COR_ATIVO if ativo else "transparent",  # Fundo se ativo
                text_color=COR_TEXTO if ativo else COR_TEXTO2,   # Texto claro se ativo
                hover_color=COR_ATIVO,            # Cor ao passar o mouse
                anchor="w",                       # Alinhamento à esquerda
                height=48,                        # Altura do botão
                corner_radius=8,                  # Cantos arredondados
                command=lambda k=chave: self._navegar(k)  # Função ao clicar
            )
            btn.pack(fill="x", padx=15, pady=5)  # Empacota o botão
            self._botoes_nav.append((btn, nome))  # Salva na lista

        # Versão do sistema no rodapé
        ctk.CTkLabel(self.sidebar_container, text="v1.0 • LUMEN SYSTEM",
                     font=("Segoe UI", 11), text_color=COR_INPUT_BORDER).pack(side="bottom", pady=20)

    def _criar_conteudo(self):
        """Monta o conteúdo principal: header, cards e gráficos."""
        self._conteudo = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)  # Frame scrollável
        self._conteudo.grid(row=0, column=1, sticky="nsew", padx=(25, 10), pady=30)
        self._conteudo.grid_columnconfigure(0, weight=1)

        self._criar_header()                     # Título e subtítulo
        self._criar_cards(self._conteudo)         # Cards de estatísticas
        self._criar_graficos(self._conteudo)      # Gráficos

    def _criar_header(self):
        """Cria o cabeçalho com título e subtítulo."""
        header = ctk.CTkFrame(self._conteudo, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 25), padx=10)

        ctk.CTkLabel(                             # Título principal
            header,
            text="Visão Geral",
            font=("Segoe UI", 38, "bold"),
            text_color=COR_TEXTO
        ).pack(anchor="w")

        ctk.CTkLabel(                             # Subtítulo explicativo
            header,
            text="Acompanhe métricas, acervos e fluxo de leitores em tempo real.",
            font=("Segoe UI", 15),
            text_color=COR_TEXTO2
        ).pack(anchor="w", pady=(2, 0))

    def _recriar_conteudo(self):
        """Destrói e reconstrói todo o conteúdo (para atualizar dados)."""
        for widget in self._conteudo.winfo_children():  # Remove todos os widgets
            widget.destroy()
        self._criar_header()                     # Reconstrói header
        self._criar_cards(self._conteudo)         # Reconstrói cards
        self._criar_graficos(self._conteudo)      # Reconstrói gráficos

    def _criar_cards(self, parent):
        """Cria os 4 cards de estatísticas (livros, empréstimos, leitores, alertas)."""
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 25), padx=10)
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)  # 4 colunas iguais

        # Dados de cada card: (título, valor, subtítulo, cor do valor)
        cards = [
            ("TOTAL NO ACERVO", str(self._stats.get('livros', 0)), "Títulos catalogados", COR_GRAF_AZUL),
            ("EMPRÉSTIMOS ATIVOS", str(self._stats.get('emprestimos', 0)), "Livros em circulação", COR_GRAF_DOURADO),
            ("LEITORES ATIVOS", str(self._stats.get('usuarios', 0)), "Usuários na plataforma", COR_TEXTO),
            ("ALERTAS DE ATRASO", str(self._stats.get('atrasados', 0)), "Devoluções pendentes", "#EF4444"),
        ]

        for i, (titulo, valor, subtitulo, cor_valor) in enumerate(cards):  # Para cada card
            card = criar_card(cards_frame)        # Cria o card
            card.grid(row=0, column=i, padx=8, pady=0, sticky="nsew")  # Posiciona

            criar_label(card, titulo, font=("Segoe UI", 13, "bold"), text_color=COR_TEXTO2).pack(anchor="center", pady=(20, 2))  # Título
            ctk.CTkLabel(card, text=valor, font=("Segoe UI", 58, "bold"), text_color=cor_valor).pack(anchor="center")  # Valor grande
            criar_label(card, subtitulo, font=("Segoe UI", 12), text_color=COR_INPUT_BORDER).pack(anchor="center", pady=(0, 20))  # Subtítulo

    def _criar_graficos(self, parent):
        """Cria os gráficos: barras mensais, pizza por categoria, barras semanais."""
        graficos_frame = ctk.CTkFrame(parent, fg_color="transparent")
        graficos_frame.grid(row=2, column=0, sticky="nsew", padx=10)
        graficos_frame.grid_columnconfigure((0, 1), weight=1)  # 2 colunas iguais

        self._criar_grafico_barras(graficos_frame, "Movimentação Mensal", self._emp_mes, 0, 0)  # Gráfico de barras
        self._criar_grafico_pizza(graficos_frame, "Distribuição por Categoria", self._cat_livros, 0, 1)  # Gráfico de pizza
        self._criar_grafico_semana(graficos_frame, "Fluxo de Empréstimos Diários", self._emp_semana, 1, 0, 2)  # Barras semanais (2 colunas)

    def _criar_grafico_barras(self, parent, titulo, dados, row, col):
        """Cria um card com gráfico de barras."""
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 10))

        if not dados:                            # Se não tem dados
            criar_label(card, "Sem movimentações registradas neste período.", font=("Segoe UI", 12)).pack(expand=True, pady=80)
            return

        labels = [MESES[m] for m, _ in dados]    # Nomes dos meses
        valores = [v for _, v in dados]           # Valores numéricos

        canvas = GraficoBarras(card, valores, labels, height=260)  # Cria o gráfico
        canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))  # Posiciona

    def _criar_grafico_pizza(self, parent, titulo, dados, row, col):
        """Cria um card com gráfico de pizza e legenda."""
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 5))

        if not dados:                            # Se não tem dados
            criar_label(card, "Nenhum livro categorizado encontrado.", font=("Segoe UI", 12)).pack(expand=True, pady=80)
            return

        layout_container = ctk.CTkFrame(card, fg_color="transparent")  # Container flexível
        layout_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        area_grafico = ctk.CTkFrame(layout_container, fg_color="transparent")  # Lado esquerdo
        area_grafico.pack(side="left", fill="both", expand=True)

        canvas = GraficoPizza(area_grafico, dados)  # Gráfico de pizza
        canvas.pack(fill="both", expand=True)

        area_legenda = ctk.CTkFrame(layout_container, fg_color="transparent")  # Lado direito
        area_legenda.pack(side="right", fill="y", padx=(10, 15), pady=25)

        ctk.CTkLabel(area_legenda, text="Categorias", font=("Segoe UI", 11, "bold"), text_color=COR_TEXTO2).pack(anchor="w", pady=(0, 8))

        categorias = [c for c, _ in dados]       # Lista de nomes das categorias
        for idx, cat in enumerate(categorias):   # Para cada categoria
            item_frame = ctk.CTkFrame(area_legenda, fg_color="transparent")  # Linha da legenda
            item_frame.pack(anchor="w", pady=4)

            # Quadrado colorido indicador
            marcador = ctk.CTkFrame(item_frame, width=12, height=12, fg_color=CORES_PIZZA[idx % len(CORES_PIZZA)], corner_radius=2)
            marcador.pack(side="left", padx=(0, 8))
            marcador.pack_propagate(False)        # Mantém tamanho fixo

            ctk.CTkLabel(item_frame, text=cat, font=("Segoe UI", 12), text_color=COR_TEXTO).pack(side="left")

    def _criar_grafico_semana(self, parent, titulo, dados, row, col, colspan):
        """Cria um card com gráfico de barras da semana (ocupa 2 colunas)."""
        card = criar_card(parent)
        card.grid(row=row, column=col, columnspan=colspan, padx=8, pady=12, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 10))

        # Mapeia os dados para cada dia da semana (começa tudo zerado)
        dados_map = {d: 0 for d in DIAS}
        for dia, total in dados:                  # Para cada dia com dados
            if dia in dados_map:                  # Se é um dia válido
                dados_map[dia] = total            # Atualiza o valor

        valores = [dados_map[d] for d in DIAS]   # Lista de valores na ordem dos dias
        canvas = GraficoBarras(card, valores, DIAS,
                               cor_normal=COR_GRAF_MUTED, cor_destaque=COR_GRAF_DOURADO, height=240)
        canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _navegar(self, nome):
        """Navega para outra tela do sistema."""
        telas = {                                 # Mapeamento de nomes internos para nomes de registro
            "livros": "livros",
            "exemplares": "exemplares",
            "cadastro_usuario": "cadastro_usuario",
            "emprestimos": "emprestimos",
            "devolucoes": "devolucoes",
            "configuracoes": "configuracoes",
            "gerenciar_usuarios": "gerenciar_usuarios",
        }
        if nome in telas:                        # Se o nome é válido
            self.controller.navegar_para(telas[nome])  # Navega para a tela
