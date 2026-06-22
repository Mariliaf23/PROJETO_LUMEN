import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import cadastrar_funcionario
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, FONTE_TITULO, FONTE_SUBTITULO,
    criar_entry, criar_botao_preenchido, criar_label, criar_titulo
)


class TelaCadastroMembros(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._construir_ui()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, fg_color=COR_BG)
        container.place(relx=0.5, rely=0.5, anchor="center")

        criar_titulo(container, "LUMEN", font=FONTE_TITULO).pack(pady=(0, 5))
        criar_label(container, "Cadastro de Membros", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(pady=(0, 30))

        self.entry_nome = criar_entry(container, placeholder="Nome completo", width=320, height=42)
        self.entry_nome.pack(pady=(0, 12))

        self.entry_email = criar_entry(container, placeholder="Email", width=320, height=42)
        self.entry_email.pack(pady=(0, 12))

        self.entry_telefone = criar_entry(container, placeholder="Telefone", width=320, height=42)
        self.entry_telefone.pack(pady=(0, 12))

        self.entry_cpf = criar_entry(container, placeholder="CPF", width=320, height=42)
        self.entry_cpf.pack(pady=(0, 12))

        frame_extras = ctk.CTkFrame(container, fg_color="transparent")
        frame_extras.pack(pady=(0, 20))

        self.entry_sala = criar_entry(frame_extras, placeholder="Sala", width=150, height=42)
        self.entry_sala.pack(side="left", padx=(0, 10))

        self.entry_turno = criar_entry(frame_extras, placeholder="Turno", width=150, height=42)
        self.entry_turno.pack(side="left")

        self.btn_cadastrar = criar_botao_preenchido(
            container, text="Cadastrar Membro", command=self._cadastrar,
            width=320, height=44
        )
        self.btn_cadastrar.pack(pady=(0, 20))

        frame_voltar = ctk.CTkFrame(container, fg_color="transparent")
        frame_voltar.pack()

        lbl_voltar = criar_label(frame_voltar, "Voltar")
        lbl_voltar.pack()
        lbl_voltar.bind("<Button-1>", lambda e: self.controller.voltar())
        lbl_voltar.configure(cursor="hand2")

        self.lbl_notificacao = criar_label(container, "", text_color=COR_TEXTO2)

    def _cadastrar(self):
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        telefone = self.entry_telefone.get().strip()
        cpf = self.entry_cpf.get().strip()
        sala = self.entry_sala.get().strip()
        turno = self.entry_turno.get().strip()

        if not nome:
            self._notificar("Informe o nome do membro.")
            return
        if not email:
            self._notificar("Informe o email do membro.")
            return
        if not cpf:
            self._notificar("Informe o CPF do membro.")
            return

        self.btn_cadastrar.configure(text="Cadastrando...", state="disabled")
        self.after(500, lambda: self._salvar(nome, email, telefone, cpf, sala, turno))

    def _salvar(self, nome, email, telefone, cpf, sala, turno):
        sucesso = cadastrar_funcionario(nome, email, '', telefone)
        if sucesso:
            self._notificar("Membro cadastrado com sucesso!")
            self._limpar_campos()
        else:
            self._notificar("Erro ao cadastrar membro.")
        self.btn_cadastrar.configure(text="Cadastrar Membro", state="normal")

    def _limpar_campos(self):
        for entry in [self.entry_nome, self.entry_email, self.entry_telefone,
                      self.entry_cpf, self.entry_sala, self.entry_turno]:
            entry.delete(0, "end")

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.pack(pady=(10, 0))
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))
