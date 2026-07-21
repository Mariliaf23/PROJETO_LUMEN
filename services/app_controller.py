# app_controller.py — Controlador principal que gerencia navegação entre telas

import os
from PIL import Image
import customtkinter as ctk
from services.styles import cores


class AppController:
    """Gerencia a navegação entre telas, animações e controle de acesso."""

    # Telas que o bibliotecário pode acessar (diretor acessa todas)
    TELAS_BIBLIOTECARIO = {"dashboard", "livros", "exemplares", "emprestimos"}

    def __init__(self, root):
        """Configura a janela principal do aplicativo."""
        self.root = root                       # Referência à janela raiz do tkinter
        self.root.title("LUMEN")               # Título da janela
        self.root.geometry("960x680")          # Tamanho inicial da janela (largura x altura)
        self.root.minsize(800, 580)            # Tamanho mínimo permitido
        self.root.configure(fg_color=cores.COR_BG)   # Cor de fundo da janela

        # Container principal onde todas as telas são exibidas
        self._container = ctk.CTkFrame(root, fg_color=cores.COR_BG)  # Frame que segura as telas
        self._container.pack(fill="both", expand=True)          # Preenche toda a janela

        self._telas = {}           # Dicionário com todas as telas registradas (nome -> frame)
        self._tela_atual = None    # Nome da tela que está sendo exibida agora
        self._historico = []       # Lista de telas visitadas (para o botão voltar)
        self._animando = False     # True enquanto uma animação de transição está rodando
        self.usuario_logado = None # Dados do usuário logado (id, nome, tipo)

        self._modo_sidebar = False    # True quando o layout com sidebar está ativo
        self._sidebar_frame = None    # Frame da sidebar fixa
        self._botoes_nav = []         # Lista de (botao, chave) para atualizar item ativo
        self._btn_tema = None         # Botão de alternar tema na sidebar
        self._logo_img = None         # Imagem da logo (evita garbage collection)

        self._centralizar()        # Centraliza a janela na tela do computador

    def verificar_acesso(self, tela):
        """Verifica se o usuário logado pode acessar a tela solicitada."""
        if tela == "login":              # Tela de login sempre é acessível
            return True
        if not self.usuario_logado:      # Se ninguém está logado, não pode acessar
            return False
        tipo = self.usuario_logado.get('tipo', '')  # Pega o tipo do usuário (diretor/bibliotecario)
        if tipo == 'diretor':            # Diretor pode acessar qualquer tela
            return True
        if tipo == 'bibliotecario':     # Bibliotecário só pode acessar telas específicas
            return tela in self.TELAS_BIBLIOTECARIO
        return False                     # Outros tipos não têm acesso

    def _centralizar(self):
        """Centraliza a janela na tela do monitor."""
        self.root.update_idletasks()                    # Atualiza as medições da janela
        L = self.root.winfo_width()                     # Largura atual da janela
        A = self.root.winfo_height()                    # Altura atual da janela
        x = (self.root.winfo_screenwidth() - L) // 2   # Posição X para centralizar
        y = (self.root.winfo_screenheight() - A) // 2   # Posição Y para centralizar
        self.root.geometry(f"+{x}+{y}")                 # Aplica a posição calculada

    def registrar_tela(self, nome, classe_tela):
        """Registra uma tela no controlador para uso posterior na navegação."""
        frame = classe_tela(master=self._container, controller=self)  # Cria a tela
        self._telas[nome] = frame                     # Salva no dicionário pelo nome
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Posiciona preenchendo o container
        frame.place_forget()                          # Esconde a tela (será mostrada quando necessário)

    def navegar_para(self, nome, voltavel=True):
        """Navega para a tela indicada pelo nome."""
        if self._animando:
            return

        if self._tela_atual and self._tela_atual == nome:
            return

        if not self.verificar_acesso(nome):
            return

        if nome == "login":
            self._desativar_modo_sidebar()
            if voltavel and self._tela_atual:
                self._historico.append(self._tela_atual)
            antiga = self._tela_atual
            self._tela_atual = nome
            nova_tela = self._telas[nome]
            callback = nova_tela._ao_visitar if hasattr(nova_tela, '_ao_visitar') else None
            if antiga:
                self._animar_slide(self._telas[antiga], nova_tela, direcao="esquerda", callback=callback)
            else:
                nova_tela.place(relx=0, rely=0, relwidth=1, relheight=1)
                nova_tela.lift()
                if callback:
                    callback()
            return

        self._ativar_modo_sidebar()

        if voltavel and self._tela_atual:
            self._historico.append(self._tela_atual)

        antiga = self._tela_atual
        self._tela_atual = nome
        nova_tela = self._telas[nome]

        if antiga:
            tela_antiga = self._telas[antiga]
            tela_antiga.grid_forget()

        nova_tela.grid(row=0, column=1, sticky="nsew")
        nova_tela.lift()

        if hasattr(nova_tela, '_ao_visitar'):
            nova_tela._ao_visitar()

        self._atualizar_sidebar()

    def voltar(self):
        """Volta para a tela anterior (usando o histórico)."""
        if self._animando:
            return

        if not self._historico:
            return

        anterior = self._historico.pop()
        antiga = self._tela_atual
        self._tela_atual = anterior
        tela_volta = self._telas[anterior]

        if self._modo_sidebar:
            if antiga:
                self._telas[antiga].grid_forget()
            tela_volta.grid(row=0, column=1, sticky="nsew")
            tela_volta.lift()
            if hasattr(tela_volta, '_ao_visitar'):
                tela_volta._ao_visitar()
            self._atualizar_sidebar()
            return

        callback = tela_volta._ao_visitar if hasattr(tela_volta, '_ao_visitar') else None

        if antiga:
            self._animar_slide(self._telas[antiga], tela_volta, direcao="direita", callback=callback)
        else:
            tela_volta.place(relx=0, rely=0, relwidth=1, relheight=1)
            tela_volta.lift()
            if callback:
                callback()

    def _animar_slide(self, saindo, entrando, direcao="esquerda", duracao=250, callback=None):
        """Anima a transição entre telas com efeito de deslize."""
        self._animando = True
        saindo.update_idletasks()
        largura = saindo.winfo_width()

        if direcao == "esquerda":
            x_inicio_nova = largura
            x_fim_nova = 0
            x_inicio_velha = 0
            x_fim_velha = -largura
        else:
            x_inicio_nova = -largura
            x_fim_nova = 0
            x_inicio_velha = 0
            x_fim_velha = largura

        entrando.place(relx=0, rely=0, relwidth=1, relheight=1)
        entrando.place_configure(x=x_inicio_nova)
        entrando.lift()

        passos = 15
        intervalo = max(duracao // passos, 1)

        self._animar_passo(
            saindo, entrando,
            x_inicio_velha, x_fim_velha,
            x_inicio_nova, x_fim_nova,
            0, passos, intervalo, callback
        )

    def _animar_passo(self, saindo, entrando, x_sv, x_fv, x_sn, x_fn, passo, total, intervalo, callback=None):
        """Executa um quadro da animação de transição."""
        if passo >= total:
            saindo.place_forget()
            entrando.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._animando = False
            if callback:
                callback()
            return

        t = (passo + 1) / total
        t_suave = self._ease_out_cubic(t)

        x_velha = x_sv + (x_fv - x_sv) * t_suave
        x_nova = x_sn + (x_fn - x_sn) * t_suave

        saindo.place_configure(x=int(x_velha))
        entrando.place_configure(x=int(x_nova))

        self.root.after(intervalo, lambda: self._animar_passo(
            saindo, entrando, x_sv, x_fv, x_sn, x_fn,
            passo + 1, total, intervalo, callback
        ))

    def _ease_out_cubic(self, t):
        """Função de suavização que desacelera no final (ease-out cúbico)."""
        return 1 - (1 - t) ** 3

    # ===================== Sidebar persistente =====================

    def _ativar_modo_sidebar(self):
        """Configura o container com sidebar fixa à esquerda e conteúdo à direita."""
        if self._modo_sidebar:
            return
        self._modo_sidebar = True

        for widget in self._container.winfo_children():
            widget.place_forget()

        self._container.grid_columnconfigure(0, weight=0)
        self._container.grid_columnconfigure(1, weight=1)
        self._container.grid_rowconfigure(0, weight=1)

        self._sidebar_frame = ctk.CTkFrame(
            self._container, fg_color=cores.COR_SIDEBAR, width=260, corner_radius=0
        )
        self._sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self._sidebar_frame.grid_propagate(False)

        self._sidebar_borda = ctk.CTkFrame(
            self._container, fg_color=cores.COR_INPUT_BORDER, width=1, corner_radius=0
        )
        self._sidebar_borda.grid(row=0, column=0, sticky="ns", padx=(259, 0))

        cores.registrar_listener(self._reconstruir_sidebar)

        self._construir_sidebar()

    def _desativar_modo_sidebar(self):
        """Remove o layout com sidebar e volta ao modo normal."""
        if not self._modo_sidebar:
            return
        self._modo_sidebar = False

        cores.remover_listener(self._reconstruir_sidebar)

        if self._sidebar_frame:
            self._sidebar_frame.destroy()
            self._sidebar_frame = None
        if hasattr(self, '_sidebar_borda') and self._sidebar_borda:
            self._sidebar_borda.destroy()
            self._sidebar_borda = None

        for tela in self._telas.values():
            tela.grid_forget()

        self._container.pack(fill="both", expand=True)

    def _construir_sidebar(self):
        """Monta o menu lateral com logo e botões de navegação."""
        topo = ctk.CTkFrame(self._sidebar_frame, fg_color="transparent")
        topo.pack(fill="x", pady=(25, 5), padx=10)

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        if os.path.exists(logo_path):
            try:
                with Image.open(logo_path) as img:
                    self._logo_img = ctk.CTkImage(img.copy(), size=(180, 180))
                ctk.CTkLabel(topo, image=self._logo_img, text="").pack()
            except Exception:
                ctk.CTkLabel(topo, text="LUMEN", font=("Cinzel", 28, "bold"), text_color=cores.COR_DOURADO).pack()
        else:
            ctk.CTkLabel(topo, text="LUMEN", font=("Cinzel", 28, "bold"), text_color=cores.COR_DOURADO).pack()

        ctk.CTkFrame(self._sidebar_frame, fg_color=cores.COR_INPUT_BORDER, height=1).pack(fill="x", padx=25, pady=(15, 20))

        tipo_usuario = None
        if hasattr(self, 'usuario_logado') and self.usuario_logado:
            tipo_usuario = self.usuario_logado.get('tipo', '').lower()

        tela_atual = self._tela_atual or 'dashboard'

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
                self._sidebar_frame,
                text=nome,
                font=("Segoe UI", 15, "bold" if ativo else "normal"),
                fg_color=cores.COR_ATIVO if ativo else "transparent",
                text_color="#FFFFFF" if ativo else cores.COR_TEXTO2,
                hover_color=cores.COR_ATIVO,
                anchor="w",
                height=48,
                corner_radius=8,
                command=lambda k=chave: self.navegar_para(k)
            )
            btn.pack(fill="x", padx=15, pady=3)
            self._botoes_nav.append((btn, chave))

        ctk.CTkFrame(self._sidebar_frame, fg_color=cores.COR_INPUT_BORDER, height=1).pack(
            side="bottom", fill="x", padx=25, pady=(0, 0))

        ctk.CTkButton(
            self._sidebar_frame,
            text="🚪   Sair",
            font=("Segoe UI", 13),
            fg_color="transparent",
            text_color=cores.COR_TEXTO2,
            hover_color=cores.COR_ATIVO,
            anchor="center",
            height=38, corner_radius=8,
            command=self._sair
        ).pack(side="bottom", fill="x", padx=15, pady=(2, 2))

        self._btn_tema = ctk.CTkButton(
            self._sidebar_frame,
            text="🌙  Escuro" if cores.modo == "dark" else "☀️  Claro",
            font=("Segoe UI", 13),
            fg_color="transparent",
            text_color=cores.COR_TEXTO2,
            hover_color=cores.COR_ATIVO,
            anchor="center",
            height=38, corner_radius=8,
            command=self._alternar_tema
        )
        self._btn_tema.pack(side="bottom", fill="x", padx=15, pady=(4, 2))

        ctk.CTkLabel(self._sidebar_frame, text="v1.0 • LUMEN SYSTEM",
                     font=("Segoe UI", 11), text_color=cores.COR_TEXTO2).pack(side="bottom", pady=(4, 8))

    def _reconstruir_sidebar(self):
        """Reconstrói a sidebar quando o tema muda."""
        if not self._modo_sidebar or not self._sidebar_frame:
            return
        self._container.configure(fg_color=cores.COR_BG)
        self._sidebar_frame.configure(fg_color=cores.COR_SIDEBAR)
        if hasattr(self, '_sidebar_borda') and self._sidebar_borda:
            self._sidebar_borda.configure(fg_color=cores.COR_INPUT_BORDER)
        for widget in self._sidebar_frame.winfo_children():
            widget.destroy()
        self._construir_sidebar()

    def _atualizar_sidebar(self):
        """Atualiza cores/estilos dos botões da sidebar."""
        tela_atual = self._tela_atual or 'dashboard'
        for btn, chave in self._botoes_nav:
            ativo = (chave == tela_atual)
            btn.configure(
                font=("Segoe UI", 15, "bold" if ativo else "normal"),
                fg_color=cores.COR_ATIVO if ativo else "transparent",
                text_color=cores.COR_TEXTO if ativo else cores.COR_TEXTO2,
            )

    def _alternar_tema(self):
        """Alterna entre tema claro e escuro."""
        cores.alternar()

    def _sair(self):
        """Limpa sessão e volta para a tela de login."""
        self.usuario_logado = None
        self.navegar_para("login")
