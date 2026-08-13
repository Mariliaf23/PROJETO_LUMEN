# app_controller.py — Controlador principal

import os
from PIL import Image
import customtkinter as ctk
from services.styles import cores, COR_ERRO


class AppController:
    TELAS_BIBLIOTECARIO = {"dashboard", "livros", "exemplares", "emprestimos"}

    def __init__(self, root):
        self.root = root
        self.root.title("LUMEN")
        self.root.geometry("960x680")
        self.root.minsize(800, 580)
        self.root.configure(fg_color=cores.COR_BG)

        self._container = ctk.CTkFrame(root, fg_color=cores.COR_BG)
        self._container.pack(fill="both", expand=True)

        self._telas = {}
        self._tela_atual = None
        self._historico = []
        self._animando = False
        self.usuario_logado = None

        self._modo_sidebar = False
        self._sidebar_frame = None
        self._botoes_nav = []
        self._btn_tema = None
        self._logo_img = None

        cores.registrar_listener(self._ao_tema_mudou)
        self._centralizar()

    def _ao_alterar_banner(self, indisponivel):
        """Mostra/oculta a faixa de 'servidor indisponível' conforme as consultas em fundo."""
        if indisponivel and not self._banner_visivel:
            self._banner_visivel = True
            self._tk_banner.place(relx=0, rely=0, relwidth=1)
            self._tk_banner.lift()
        elif not indisponivel and self._banner_visivel:
            self._banner_visivel = False
            self._tk_banner.place_forget()

    def verificar_acesso(self, tela):
        if tela == "login":
            return True
        if not self.usuario_logado:
            return False
        tipo = self.usuario_logado.get("tipo", "")
        if tipo == "diretor":
            return True
        if tipo == "bibliotecario":
            return tela in self.TELAS_BIBLIOTECARIO
        return False

    def _centralizar(self):
        self.root.update_idletasks()
        L = self.root.winfo_width()
        A = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - L) // 2
        y = (self.root.winfo_screenheight() - A) // 2
        self.root.geometry(f"+{x}+{y}")

    def registrar_tela(self, nome, classe_tela):
        frame = classe_tela(master=self._container, controller=self)
        self._telas[nome] = frame
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        frame.place_forget()

    def _garantir_tela(self, nome):
        if nome in self._telas:
            return self._telas[nome]
        return None

    def navegar_para(self, nome, voltavel=True):
        if self._animando:
            return

        if self._tela_atual and self._tela_atual == nome:
            tela = self._telas.get(nome)
            if tela and hasattr(tela, "_ao_visitar"):
                tela._ao_visitar()
            self._atualizar_sidebar()
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
            callback = getattr(nova_tela, "_ao_visitar", None)
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
        nova_tela = self._garantir_tela(nome)
        if nova_tela is None:
            self._tela_atual = antiga
            return

        if antiga and antiga in self._telas:
            self._telas[antiga].grid_forget()

        nova_tela.grid(row=0, column=1, sticky="nsew")
        nova_tela.lift()

        if hasattr(nova_tela, "_ao_visitar"):
            nova_tela._ao_visitar()

        self._atualizar_sidebar()

    def voltar(self):
        if self._animando:
            return
        self.navegar_para("dashboard", voltavel=False)

    def _animar_slide(self, saindo, entrando, direcao="esquerda", duracao=250, callback=None):
        self._animando = True
        saindo.update_idletasks()
        largura = saindo.winfo_width() or 800

        if direcao == "esquerda":
            x_inicio_nova, x_fim_nova = largura, 0
            x_inicio_velha, x_fim_velha = 0, -largura
        else:
            x_inicio_nova, x_fim_nova = -largura, 0
            x_inicio_velha, x_fim_velha = 0, largura

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
        if passo >= total:
            try:
                saindo.place_forget()
            except Exception:
                pass
            entrando.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._animando = False
            if callback:
                callback()
            return

        t = (passo + 1) / total
        t_suave = 1 - (1 - t) ** 3

        x_velha = x_sv + (x_fv - x_sv) * t_suave
        x_nova = x_sn + (x_fn - x_sn) * t_suave

        try:
            saindo.place_configure(x=int(x_velha))
            entrando.place_configure(x=int(x_nova))
        except Exception:
            pass

        self.root.after(intervalo, lambda: self._animar_passo(
            saindo, entrando, x_sv, x_fv, x_sn, x_fn,
            passo + 1, total, intervalo, callback
        ))

    def _ativar_modo_sidebar(self):
        if self._modo_sidebar:
            return
        self._modo_sidebar = True

        for widget in self._container.winfo_children():
            try:
                widget.place_forget()
            except Exception:
                pass

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

        self._construir_sidebar()

    def _desativar_modo_sidebar(self):
        if not self._modo_sidebar:
            return
        self._modo_sidebar = False

        if self._sidebar_frame:
            self._sidebar_frame.destroy()
            self._sidebar_frame = None
        if hasattr(self, "_sidebar_borda") and self._sidebar_borda:
            self._sidebar_borda.destroy()
            self._sidebar_borda = None

        for tela in self._telas.values():
            try:
                tela.grid_forget()
            except Exception:
                pass

        self._container.pack(fill="both", expand=True)

    def _construir_sidebar(self):
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
                ctk.CTkLabel(topo, text="LUMEN", font=("Cinzel", 28, "bold"),
                             text_color=cores.COR_DOURADO).pack()
        else:
            ctk.CTkLabel(topo, text="LUMEN", font=("Cinzel", 28, "bold"),
                         text_color=cores.COR_DOURADO).pack()

        ctk.CTkFrame(self._sidebar_frame, fg_color=cores.COR_INPUT_BORDER, height=1).pack(
            fill="x", padx=25, pady=(15, 20)
        )

        tipo_usuario = None
        if self.usuario_logado:
            tipo_usuario = self.usuario_logado.get("tipo", "").lower()

        tela_atual = self._tela_atual or "dashboard"

        itens = [
            ("🏠   Dashboard", "dashboard"),
            ("📚   Livros",    "livros"),
            ("🔍   Catálogo",  "catalogo"),
        ]
        if tipo_usuario in ("admin", "diretor"):
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
            side="bottom", fill="x", padx=25
        )

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

        ctk.CTkLabel(
            self._sidebar_frame, text="v1.0 • LUMEN SYSTEM",
            font=("Segoe UI", 11), text_color=cores.COR_TEXTO2
        ).pack(side="bottom", pady=(4, 8))

    def _ao_tema_mudou(self):
        """Chamado automaticamente quando o tema muda."""
        self.root.configure(fg_color=cores.COR_BG)

        if self._modo_sidebar and self._sidebar_frame:
            self._container.configure(fg_color=cores.COR_BG)
            self._sidebar_frame.configure(fg_color=cores.COR_SIDEBAR)
            if hasattr(self, "_sidebar_borda") and self._sidebar_borda:
                self._sidebar_borda.configure(fg_color=cores.COR_INPUT_BORDER)

            for widget in list(self._sidebar_frame.winfo_children()):
                try:
                    widget.destroy()
                except Exception:
                    pass
            self._construir_sidebar()

        # Marca todas as telas como pendentes
        for tela in self._telas.values():
            tela._tema_pendente = True

        # Reconstrói a tela atual imediatamente
        if self._tela_atual and self._tela_atual in self._telas:
            tela = self._telas[self._tela_atual]

            if hasattr(tela, "_reconstruir_tema"):
                tela._reconstruir_tema()
            elif hasattr(tela, "_reconstruir_ui"):
                tela._reconstruir_ui()
            elif hasattr(tela, "_reconstruir"):
                tela._reconstruir()

            tela._tema_pendente = False

            if self._modo_sidebar:
                try:
                    tela.grid(row=0, column=1, sticky="nsew")
                except Exception:
                    pass
            tela.lift()

    def _atualizar_sidebar(self):
        tela_atual = self._tela_atual or "dashboard"
        for btn, chave in self._botoes_nav:
            ativo = (chave == tela_atual)
            btn.configure(
                font=("Segoe UI", 15, "bold" if ativo else "normal"),
                fg_color=cores.COR_ATIVO if ativo else "transparent",
                text_color="#FFFFFF" if ativo else cores.COR_TEXTO2,
            )

    def _alternar_tema(self):
        cores.alternar()

    def _sair(self):
        self.usuario_logado = None
        self.navegar_para("login")