import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import cadastrar_usuario
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, FONTE_TITULO, FONTE_SUBTITULO,
    criar_entry, criar_botao_preenchido, criar_label, criar_titulo, criar_combo
)


class TelaCadastroUsuario(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._construir_ui()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, fg_color=COR_BG)
        container.place(relx=0.5, rely=0.5, anchor="center")

        criar_titulo(container, "LUMEN", font=FONTE_TITULO).pack(pady=(0, 5))
        criar_label(container, "Cadastro de Usuario", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(pady=(0, 20))

        self.combo_tipo = criar_combo(container, values=["aluno", "professor", "funcionario"], width=320, height=42)
        self.combo_tipo.pack(pady=(0, 15))
        self.combo_tipo.set("aluno")
        self.combo_tipo.configure(command=self._tipo_mudou)

        self.entry_nome = criar_entry(container, placeholder="Nome completo", width=320, height=42)
        self.entry_nome.pack(pady=(0, 10))

        self.entry_email = criar_entry(container, placeholder="Email", width=320, height=42)
        self.entry_email.pack(pady=(0, 10))

        self.entry_senha = criar_entry(container, placeholder="Senha", width=320, height=42, show="*")
        self.entry_senha.pack(pady=(0, 10))

        self.entry_telefone = criar_entry(container, placeholder="Telefone (opcional)", width=320, height=42)
        self.entry_telefone.pack(pady=(0, 10))

        self.entry_cpf = criar_entry(container, placeholder="CPF (opcional)", width=320, height=42)
        self.entry_cpf.pack(pady=(0, 10))

        self.frame_aluno = ctk.CTkFrame(container, fg_color="transparent")
        self.frame_aluno.pack(pady=(0, 5))

        self.entry_matricula = criar_entry(self.frame_aluno, placeholder="Matricula", width=150, height=42)
        self.entry_matricula.pack(side="left", padx=(0, 10))

        self.entry_sala = criar_entry(self.frame_aluno, placeholder="Sala", width=70, height=42)
        self.entry_sala.pack(side="left", padx=(0, 10))

        self.entry_turno = criar_entry(self.frame_aluno, placeholder="Turno", width=70, height=42)
        self.entry_turno.pack(side="left")

        self.frame_func = ctk.CTkFrame(container, fg_color="transparent")

        self.entry_funcao = criar_entry(self.frame_func, placeholder="Funcao (ex: diretor)", width=320, height=42)
        self.entry_funcao.pack()

        self.btn_cadastrar = criar_botao_preenchido(
            container, text="Cadastrar", command=self._cadastrar,
            width=320, height=44
        )
        self.btn_cadastrar.pack(pady=(15, 15))

        frame_voltar = ctk.CTkFrame(container, fg_color="transparent")
        frame_voltar.pack()

        lbl_voltar = criar_label(frame_voltar, "Voltar")
        lbl_voltar.pack()
        lbl_voltar.bind("<Button-1>", lambda e: self.controller.voltar())
        lbl_voltar.configure(cursor="hand2")

        self.lbl_notificacao = criar_label(container, "", text_color=COR_TEXTO2)

    def _tipo_mudou(self, tipo):
        self.frame_aluno.pack_forget()
        self.frame_func.pack_forget()
        if tipo == "aluno":
            self.frame_aluno.pack(pady=(0, 5))
        elif tipo in ("funcionario", "bibliotecario"):
            self.frame_func.pack(pady=(0, 5))

    def _cadastrar(self):
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()
        telefone = self.entry_telefone.get().strip()
        cpf = self.entry_cpf.get().strip()
        tipo = self.combo_tipo.get()

        if not nome:
            self._notificar("Informe o nome completo.")
            return
        if not email:
            self._notificar("Informe o email.")
            return
        if not senha:
            self._notificar("Informe a senha.")
            return

        matricula = self.entry_matricula.get().strip() if tipo == "aluno" else ""
        sala = self.entry_sala.get().strip() if tipo == "aluno" else ""
        turno = self.entry_turno.get().strip() if tipo == "aluno" else ""
        funcao = self.entry_funcao.get().strip() if tipo in ("funcionario", "bibliotecario") else ""

        self.btn_cadastrar.configure(text="Cadastrando...", state="disabled")
        self.after(500, lambda: self._salvar(
            nome, email, senha, telefone, cpf, tipo, matricula, sala, turno, funcao
        ))

    def _salvar(self, nome, email, senha, telefone, cpf, tipo, matricula, sala, turno, funcao):
        sucesso = cadastrar_usuario(
            nome, email, senha, telefone, cpf, tipo, matricula, sala, turno, funcao
        )
        if sucesso:
            self._notificar("Conta criada com sucesso!")
            self.after(1500, lambda: self.controller.voltar())
        else:
            self._notificar("Erro ao criar conta (email ou CPF duplicado?).")
        self.btn_cadastrar.configure(text="Cadastrar", state="normal")

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.pack(pady=(10, 0))
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))
