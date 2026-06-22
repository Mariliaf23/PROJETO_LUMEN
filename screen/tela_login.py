import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import verificar_login
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_INPUT, FONTE_BOTAO, FONTE_LABEL,
    criar_entry, criar_botao_preenchido, criar_label, criar_titulo
)


class TelaLogin(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._construir_ui()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, fg_color=COR_BG)
        container.place(relx=0.5, rely=0.5, anchor="center")

        criar_titulo(container, "LUMEN", font=FONTE_TITULO).pack(pady=(0, 5))
        criar_label(container, "Iniciar sessao", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(pady=(0, 30))

        self.entry_usuario = criar_entry(container, placeholder="Usuario", width=300, height=42)
        self.entry_usuario.pack(pady=(0, 15))

        self.entry_senha = criar_entry(container, placeholder="Senha", width=300, height=42, show="*")
        self.entry_senha.pack(pady=(0, 25))

        self.btn_entrar = criar_botao_preenchido(
            container, text="Entrar", command=self._entrar,
            width=300, height=44
        )
        self.btn_entrar.pack(pady=(0, 20))

        frame_registrar = ctk.CTkFrame(container, fg_color="transparent")
        frame_registrar.pack()

        lbl_registrar = criar_label(frame_registrar, "Nao tem conta? Registar", font=FONTE_LABEL)
        lbl_registrar.pack()
        lbl_registrar.bind("<Button-1>", lambda e: self.controller.navegar_para("cadastro_login"))
        lbl_registrar.configure(cursor="hand2")

        self.lbl_erro = criar_label(container, "", text_color=COR_TEXTO2, font=FONTE_LABEL)

    def _entrar(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()

        if not usuario:
            self._mostrar_erro("Informe o usuario.")
            return
        if not senha:
            self._mostrar_erro("Informe a senha.")
            return

        self.btn_entrar.configure(text="Carregando...", state="disabled")
        self.after(500, lambda: self._verificar(usuario, senha))

    def _verificar(self, usuario, senha):
        resultado = verificar_login(usuario, senha)

        if resultado:
            self.controller.navegar_para("dashboard", voltavel=False)
        else:
            self._mostrar_erro("Usuario nao encontrado.")

        self.btn_entrar.configure(text="Entrar", state="normal")

    def _mostrar_erro(self, mensagem):
        self.lbl_erro.configure(text=mensagem, text_color="#d4b896")
        self.lbl_erro.pack(pady=(5, 0))
        self.after(3000, lambda: self.lbl_erro.configure(text=""))
