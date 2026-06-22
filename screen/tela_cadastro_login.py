import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import cadastrar_funcionario
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_entry, criar_botao_preenchido, criar_label, criar_titulo
)


class LumenLoginApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("LUMEN - Cadastrar")
        self.geometry("960x680")
        self.minsize(800, 580)
        self.configure(fg_color=COR_BG)

        self.after(100, self.lift)
        self._construir_ui()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, fg_color=COR_BG)
        container.place(relx=0.5, rely=0.5, anchor="center")

        criar_titulo(container, "LUMEN", font=FONTE_TITULO).pack(pady=(0, 5))
        criar_label(container, "Criar conta", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(pady=(0, 30))

        self.entry_nome = criar_entry(container, placeholder="Nome completo", width=300, height=42)
        self.entry_nome.pack(pady=(0, 12))

        self.entry_email = criar_entry(container, placeholder="Email", width=300, height=42)
        self.entry_email.pack(pady=(0, 12))

        self.entry_senha = criar_entry(container, placeholder="Senha", width=300, height=42, show="*")
        self.entry_senha.pack(pady=(0, 12))

        self.entry_confirmar = criar_entry(container, placeholder="Confirmar senha", width=300, height=42, show="*")
        self.entry_confirmar.pack(pady=(0, 25))

        self.btn_cadastrar = criar_botao_preenchido(
            container, text="Cadastrar", command=self._cadastrar,
            width=300, height=44
        )
        self.btn_cadastrar.pack(pady=(0, 20))

        frame_voltar = ctk.CTkFrame(container, fg_color="transparent")
        frame_voltar.pack()

        lbl_voltar = criar_label(frame_voltar, "Voltar", font=FONTE_LABEL)
        lbl_voltar.pack()
        lbl_voltar.bind("<Button-1>", lambda e: self._voltar())
        lbl_voltar.configure(cursor="hand2")

        self.lbl_notificacao = criar_label(container, "", text_color=COR_TEXTO2)

    def _cadastrar(self):
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()
        confirmar = self.entry_confirmar.get().strip()

        if not nome:
            self._notificar("Informe o nome completo.")
            return
        if not email:
            self._notificar("Informe o email.")
            return
        if not senha:
            self._notificar("Informe a senha.")
            return
        if senha != confirmar:
            self._notificar("As senhas nao conferem.")
            return

        self.btn_cadastrar.configure(text="Cadastrando...", state="disabled")
        self.after(500, lambda: self._salvar(nome, email, senha))

    def _salvar(self, nome, email, senha):
        sucesso = cadastrar_funcionario(nome, email, senha)
        if sucesso:
            self._notificar("Conta criada com sucesso!")
            self.after(1500, self._voltar)
        else:
            self._notificar("Erro ao criar conta.")
        self.btn_cadastrar.configure(text="Cadastrar", state="normal")

    def _voltar(self):
        self.destroy()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.pack(pady=(10, 0))
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = LumenLoginApp(master=root)
    app.mainloop()
    root.destroy()
