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
from services.styles import (
    cores, FONTE_NAV, FONTE_LABEL,
    criar_label, criar_card
)

COR_GRAF_AZUL = cores.COR_AZUL_PRINCIPAL

MESES = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
DIAS  = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']


def _cores_pizza():
    return [COR_GRAF_AZUL, cores.COR_DOURADO, cores.COR_DOURADO_CLARO, cores.COR_INPUT_BORDER, cores.COR_TEXTO2]


def _cards_config():
    return [
        ("livros",            "TOTAL NO ACERVO",    "📚", "Títulos catalogados",  COR_GRAF_AZUL),
        ("emprestimos_ativos","EMPRÉSTIMOS ATIVOS", "🔄", "Livros em circulação", cores.COR_DOURADO),
        ("usuarios",          "LEITORES ATIVOS",    "👥", "Usuários na plataforma", cores.COR_TEXTO),
        ("atrasados",         "ALERTAS DE ATRASO",  "⚠️", "Devoluções pendentes",  cores.COR_PERIGO),
    ]


class CardEstatistica(ctk.CTkFrame):
    """Card de estatística com ícone, valor animado, barra lateral colorida e hover."""

    def __init__(self, master, titulo, icone, subtitulo, cor_acento, valor_final, **kw):
        super().__init__(master, fg_color=cores.COR_CARD, corner_radius=16,
                         border_width=1, border_color=cores.COR_INPUT_BORDER, **kw)
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
                     text_color=cores.COR_TEXTO2).pack(side="left", padx=(8, 0))

        # Valor numérico (animado) — centralizado
        self._lbl_valor = ctk.CTkLabel(corpo, text="0",
                                       font=("Segoe UI", 52, "bold"), text_color=cor_acento,
                                       justify="center")
        self._lbl_valor.pack(fill="x", pady=(4, 0))

        # Subtítulo centralizado
        ctk.CTkLabel(corpo, text=subtitulo, font=("Segoe UI", 12),
                     text_color=cores.COR_TEXTO2, justify="center").pack(fill="x")

        # Hover: borda colorida ao entrar/sair (propaga para filhos)
        for w in (self, barra, corpo, topo):
            w.bind("<Enter>", lambda e: self.configure(border_color=cor_acento, border_width=2))
            w.bind("<Leave>", lambda e: self.configure(border_color=cores.COR_INPUT_BORDER, border_width=1))

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

    def __init__(self, master, dados, labels, cor_normal=None, cor_destaque=None, **kw):
        """Inicializa o gráfico de barras."""
        super().__init__(master, bg=cores.COR_CARD, highlightthickness=0, **kw)
        self.dados = dados
        self.labels = labels
        self.cor_normal = cor_normal if cor_normal is not None else cores.COR_INPUT_BORDER
        self.cor_destaque = cor_destaque if cor_destaque is not None else COR_GRAF_AZUL
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
                                 fill=cores.COR_TEXTO, font=("Segoe UI", 9, "bold"))

            self.create_text(x_center, h - margem_base + 15, text=label,  # Rótulo abaixo
                             fill=cores.COR_TEXTO2, font=("Segoe UI", 9))

        # Desenha linhas de grade (4 linhas horizontais)
        for i in range(1, 5):
            y = h - margem_base - (altura_util * i / 4)  # Posição Y da linha
            self.create_line(margem_esq, y, w - margem_dir, y,  # Linha tracejada
                             fill=cores.COR_INPUT_BORDER, dash=(3, 5))


class GraficoPizza(ctk.CTkCanvas):
    """Gráfico de pizza (donut) desenhado em um Canvas."""

    def __init__(self, master, dados, **kw):
        """Inicializa o gráfico de pizza."""
        super().__init__(master, bg=cores.COR_CARD, highlightthickness=0, **kw)  # Canvas escuro
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
            cor = _cores_pizza()[i % len(_cores_pizza())]  # Cor ciclca

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
                self.create_polygon(pontos, fill=cor, outline=cores.COR_CARD, width=2)  # Desenha a fatia

            angulo_inicio = angulo_fim        # Próxima fatia começa onde esta terminou

        # Texto no centro: total e porcentagem
        self.create_text(cx, cy - 8, text=str(total), fill=cores.COR_TEXTO,
                         font=("Segoe UI", 12, "bold"))
        self.create_text(cx, cy + 10, text="100%", fill=cores.COR_TEXTO2,
                         font=("Segoe UI", 9))


class Dashboard(ctk.CTkFrame):
    """Tela principal do sistema com sidebar, cards de estatísticas e gráficos."""

    def __init__(self, master=None, controller=None):
        """Inicializa o dashboard."""
        super().__init__(master, fg_color=cores.COR_BG)  # Frame com fundo escuro
        self.controller = controller                 # Controlador de navegação

        self._carregar_dados()                       # Busca dados do banco
        self._construir_ui()                         # Monta a interface



    def _reconstruir_ui(self):
        """Destrói e reconstrói toda a tela para aplicar o tema atual.

        Se o dashboard não estiver visível no momento (usuário está em
        outra tela), a reconstrução é adiada para a próxima visita —
        evita reconstruir uma tela escondida a cada troca de tema.
        """
        if not self.winfo_exists():
            return
        if not self.winfo_ismapped():
            self._tema_pendente = True
            return
        self._aplicar_reconstrucao_tema()

    def _aplicar_reconstrucao_tema(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=cores.COR_BG)
        self._construir_ui()
        self._tema_pendente = False

    def _ao_visitar(self):
        """Chamado quando o usuário navega para esta tela — atualiza tudo."""
        if getattr(self, "_tema_pendente", False):
            self._aplicar_reconstrucao_tema()
        self._carregar_dados()
        self._atualizar_conteudo()

    def _carregar_dados(self):
        """Busca todas as estatísticas do banco de dados."""
        self._stats = buscar_stats_dashboard()
        self._top_alunos = buscar_top_alunos_emprestimos(10)
        self._ranking_turmas = buscar_ranking_turmas_emprestimos()
        self._cat_livros = buscar_livros_por_categoria_exemplares()

    def _construir_ui(self):
        """Monta a estrutura principal: apenas conteúdo (sidebar fica no controller)."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._criar_conteudo()

    # Sidebar removida — agora é gerenciada pelo AppController como elemento persistente

    def _criar_conteudo(self):
        """Monta o conteúdo principal: header, cards e gráficos."""
        self._conteudo = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self._conteudo.grid(row=0, column=0, sticky="nsew", padx=(25, 10), pady=30)
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
            font=("Segoe UI", 38, "bold"), text_color=cores.COR_TEXTO
        ).pack(side="left")

        # Subtítulo + data/hora
        linha_sub = ctk.CTkFrame(header, fg_color="transparent")
        linha_sub.pack(fill="x", pady=(2, 0))

        ctk.CTkLabel(
            linha_sub,
            text="Acompanhe métricas, acervos e fluxo de leitores em tempo real.",
            font=("Segoe UI", 15), text_color=cores.COR_TEXTO2
        ).pack(side="left")

        self._lbl_hora = ctk.CTkLabel(
            linha_sub, text="",
            font=("Segoe UI", 13), text_color=cores.COR_TEXTO2
        )
        self._lbl_hora.pack(side="right")
        self._atualizar_hora()

        # Separador abaixo do header
        ctk.CTkFrame(header, fg_color=cores.COR_INPUT_BORDER, height=1).pack(fill="x", pady=(12, 0))

    def _atualizar_hora(self):
        """Atualiza o label de data/hora a cada minuto."""
        if not self._lbl_hora.winfo_exists():
            return
        agora = datetime.now().strftime("%d/%m/%Y  %H:%M")
        self._lbl_hora.configure(text=agora)
        self._lbl_hora.after(60_000, self._atualizar_hora)

    def _atualizar_conteudo(self):
        """Atualiza dados dos cards e gráficos na tela."""
        for i, cfg in enumerate(_cards_config()):
            if i < len(self._cards):
                valor = self._stats.get(cfg[0], 0)
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
        for i, (chave, titulo, icone, subtitulo, cor) in enumerate(_cards_config()):
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

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=cores.COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 10))

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

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=cores.COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 5))

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

        ctk.CTkLabel(area_legenda, text="Categorias", font=("Segoe UI", 11, "bold"), text_color=cores.COR_TEXTO2).pack(anchor="w", pady=(0, 8))

        for idx, (cat, total, perc) in enumerate(dados):
            item_frame = ctk.CTkFrame(area_legenda, fg_color="transparent")
            item_frame.pack(anchor="w", pady=4)

            marcador = ctk.CTkFrame(item_frame, width=12, height=12, fg_color=_cores_pizza()[idx % len(_cores_pizza())], corner_radius=2)
            marcador.pack(side="left", padx=(0, 8))
            marcador.pack_propagate(False)

            ctk.CTkLabel(item_frame, text=f"{cat} ({total})", font=("Segoe UI", 12), text_color=cores.COR_TEXTO).pack(side="left")
            ctk.CTkLabel(item_frame, text=f"{perc}%", font=("Segoe UI", 11), text_color=cores.COR_TEXTO2).pack(side="left", padx=(8, 0))

        return canvas

    def _criar_grafico_barras_h(self, parent, titulo, dados, row, col):
        """Cria um card com gráfico de barras horizontal (ranking)."""
        card = criar_card(parent)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        criar_label(card, titulo.upper(), font=("Segoe UI", 16, "bold"), text_color=cores.COR_TEXTO).pack(anchor="center", padx=20, pady=(15, 10))

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
        paleta_cores = _cores_pizza()

        for idx, (nome, total) in enumerate(dados):
            barra_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            barra_frame.pack(fill="x", pady=2)

            lbl_nome = ctk.CTkLabel(barra_frame, text=f"{idx+1}. {nome}", font=("Segoe UI", 12), text_color=cores.COR_TEXTO, anchor="w", width=180)
            lbl_nome.pack(side="left")

            barra_bg = ctk.CTkFrame(barra_frame, fg_color=cores.COR_INPUT_BORDER, height=20, corner_radius=4)
            barra_bg.pack(side="left", fill="x", expand=True, padx=(10, 10))
            barra_bg.pack_propagate(False)

            largura = (total / max_val) if max_val > 0 else 0
            barra_fill = ctk.CTkFrame(barra_bg, fg_color=paleta_cores[idx % len(paleta_cores)], corner_radius=4)
            barra_fill.place(relx=0, rely=0, relwidth=largura, relheight=1)

            ctk.CTkLabel(barra_frame, text=str(total), font=("Segoe UI", 12, "bold"), text_color=cores.COR_TEXTO, width=40).pack(side="right")