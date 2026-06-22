import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.conector import init_db
from services.database_config import verificar_login
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_INPUT, FONTE_BOTAO, FONTE_LABEL,
    criar_entry, criar_botao_preenchido, criar_label, criar_titulo
)
from services.transitions import transicao_entrar, transicao_sair


class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        init_db()
        self.title("LUMEN")
        self.geometry("960x680")
        self.minsize(800, 580)
        self.configure(fg_color=COR_BG)

        self._centralizar()
        self._construir_ui()

    def _centralizar(self):
        self.update_idletasks()
        L = self.winfo_width()
        A = self.winfo_height()
        x = (self.winfo_screenwidth() - L) // 2
        y = (self.winfo_screenheight() - A) // 2
        self.geometry(f"+{x}+{y}")

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
        lbl_registrar.bind("<Button-1>", lambda e: self._abrir_cadastro())
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
            def abrir_dashboard():
                from screen.dashboard import Dashboard
                dashboard = Dashboard(self)
                dashboard.wait_window()
                if self.winfo_exists():
                    self.deiconify()
                    transicao_entrar(self)

            transicao_sair(self, callback=abrir_dashboard)
        else:
            self._mostrar_erro("Usuario nao encontrado.")

        self.btn_entrar.configure(text="Entrar", state="normal")

    def _abrir_cadastro(self):
        def abrir():
            from screen.tela_cadastro_login import LumenLoginApp
            cadastro = LumenLoginApp(self)
            cadastro.wait_window()
            if self.winfo_exists():
                self.deiconify()
                transicao_entrar(self)

        transicao_sair(self, callback=abrir)

    def _mostrar_erro(self, mensagem):
        self.lbl_erro.configure(text=mensagem, text_color="#d4b896")
        self.lbl_erro.pack(pady=(5, 0))
        self.after(3000, lambda: self.lbl_erro.configure(text=""))


if __name__ == "__main__":
    app = TelaLogin()
    app.mainloop()
