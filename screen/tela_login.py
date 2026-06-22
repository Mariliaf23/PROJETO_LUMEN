import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import verificar_login
from services.styles import (
    COR_BG, COR_SIDEBAR, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    criar_entry, criar_label, criar_titulo
)


class TelaLogin(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._usuario_logado = None
        self._construir_ui()

    def _construir_ui(self):
        # Configura duas colunas iguais na tela inteira
        self.grid_columnconfigure(0, weight=1)  # Lado Esquerdo (Logo)
        self.grid_columnconfigure(1, weight=1)  # Lado Direito (Formulário)
        self.grid_rowconfigure(0, weight=1)

        # Encontra a logo
        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_logo = os.path.join(caminho_base, "logo_lumen.png")
        if not os.path.exists(caminho_logo):
            caminho_logo = os.path.join(os.path.dirname(__file__), "logo_lumen.png")

        # ---------------------------------------------------------------------
        # PAINEL ESQUERDO: Identidade Visual (Logo de Destaque Ampliada)
        # ---------------------------------------------------------------------
        painel_esquerdo = ctk.CTkFrame(self, fg_color=COR_SIDEBAR, corner_radius=0)
        painel_esquerdo.grid(row=0, column=0, sticky="nsew")
        
        container_logo = ctk.CTkFrame(painel_esquerdo, fg_color="transparent")
        container_logo.place(relx=0.5, rely=0.5, anchor="center")

        if os.path.exists(caminho_logo):
            try:
                # Aumentamos consideravelmente a logo para preencher melhor a metade esquerda (de 280 para 400)
                imagem_logo = ctk.CTkImage(
                    light_image=Image.open(caminho_logo),
                    dark_image=Image.open(caminho_logo),
                    size=(400, 400)
                )
                lbl_logo = ctk.CTkLabel(container_logo, image=imagem_logo, text="")
                lbl_logo.pack()
            except Exception as e:
                criar_titulo(container_logo, "LUMEN", font=("Cinzel", 60, "bold")).pack()
        else:
            criar_titulo(container_logo, "LUMEN", font=("Cinzel", 60, "bold")).pack()

        # ---------------------------------------------------------------------
        # PAINEL DIREITO: Formulário de Login (Fontes Encorpadas)
        # ---------------------------------------------------------------------
        painel_direito = ctk.CTkFrame(self, fg_color=COR_BG, corner_radius=0)
        painel_direito.grid(row=0, column=1, sticky="nsew")

        container_form = ctk.CTkFrame(painel_direito, fg_color="transparent")
        container_form.place(relx=0.5, rely=0.5, anchor="center")

        # Fontes de títulos e subtítulos aumentadas para maior imponência
        criar_titulo(container_form, "Bem-vindo", font=("Segoe UI", 42, "bold"), text_color=COR_TEXTO).pack(anchor="w", pady=(0, 5))
        criar_label(container_form, "Acesse a plataforma da biblioteca Lumen", font=("Segoe UI Light", 16), text_color=COR_TEXTO2).pack(anchor="w", pady=(0, 40))

        # Inputs maiores em largura (380) e com fontes internas mais legíveis (Tamanho 14)
        self.entry_usuario = criar_entry(container_form, placeholder="Usuário", width=380, height=50)
        self.entry_usuario.configure(font=("Segoe UI", 14))
        self.entry_usuario.pack(pady=(0, 20))

        self.entry_senha = criar_entry(container_form, placeholder="Senha", width=380, height=50, show="*")
        self.entry_senha.configure(font=("Segoe UI", 14))
        self.entry_senha.pack(pady=(0, 35))

        # --- BOTÃO CUSTOMIZADO COM ESTILO MODERNO E CORES VIVAS ---
        # Substituímos a função padrão para criar um botão com maior contraste visual
        # Usando um tom azul vibrante/elétrico extraído das páginas iluminadas do livro da logo
        COR_BOTAO_CUSTOM = "#0091FF" 
        COR_BOTAO_HOVER = "#0070C6"

        self.btn_entrar = ctk.CTkButton(
            container_form, 
            text="Entrar no Sistema", 
            command=self._entrar,
            font=("Segoe UI Semibold", 14),
            fg_color=COR_BOTAO_CUSTOM,
            hover_color=COR_BOTAO_HOVER,
            text_color="#FFFFFF",
            corner_radius=8,
            width=380, 
            height=50
        )
        self.btn_entrar.pack(pady=(0, 30))

        frame_registrar = ctk.CTkFrame(container_form, fg_color="transparent")
        frame_registrar.pack(anchor="center")

        lbl_registrar = criar_label(frame_registrar, "Não tem conta? Registrar agora", font=("Segoe UI", 13))
        lbl_registrar.pack()
        lbl_registrar.bind("<Button-1>", lambda e: self.controller.navegar_para("cadastro_login"))
        lbl_registrar.configure(cursor="hand2", text_color=COR_DOURADO) # Deixa o link em dourado para destacar

        self.lbl_erro = criar_label(container_form, "", text_color=COR_TEXTO2, font=("Segoe UI", 12))

    def _entrar(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()

        if not usuario:
            self._mostrar_erro("Informe o usuário.")
            return
        if not senha:
            self._mostrar_erro("Informe a senha.")
            return

        self.btn_entrar.configure(text="Carregando...", state="disabled")
        self.after(500, lambda: self._verificar(usuario, senha))

    def _verificar(self, usuario, senha):
        resultado = verificar_login(usuario, senha)

        if resultado:
            self._usuario_logado = {
                'id': resultado[0],
                'nome': resultado[1],
                'tipo': resultado[2]
            }
            self.controller.usuario_logado = self._usuario_logado
            self.controller.navegar_para("dashboard", voltavel=False)
        else:
            self._mostrar_erro("Usuário não encontrado.")

        self.btn_entrar.configure(text="Entrar no Sistema", state="normal")

    def _mostrar_erro(self, mensagem):
        self.lbl_erro.configure(text=mensagem, text_color="#d4b896")
        self.lbl_erro.pack(pady=(5, 0))
        self.after(3000, lambda: self.lbl_erro.configure(text=""))