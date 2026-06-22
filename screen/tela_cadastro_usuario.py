import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import cadastrar_usuario
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, FONTE_TITULO, FONTE_SUBTITULO,
    criar_entry, criar_botao_preenchido, criar_botao, criar_label, criar_titulo, criar_combo
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

        tipo_usuario = self.controller.usuario_logado.get('tipo', '') if self.controller.usuario_logado else ''

        if tipo_usuario == 'diretor':
            tipos = ["aluno", "professor", "bibliotecario"]
        else:
            tipos = ["aluno", "professor"]

        self.combo_tipo = criar_combo(container, values=tipos, width=320, height=42)
        self.combo_tipo.pack(pady=(0, 15))
        self.combo_tipo.set("aluno")
        self.combo_tipo.configure(command=self._tipo_mudou)

        self.entry_nome = criar_entry(container, placeholder="Nome completo", width=320, height=42)
        self.entry_nome.pack(pady=(0, 10))

        self.entry_contato = criar_entry(container, placeholder="Email ou celular (obrigatorio)", width=320, height=42)
        self.entry_contato.pack(pady=(0, 10))

        self.frame_senha = ctk.CTkFrame(container, fg_color="transparent")
        self.entry_senha = criar_entry(self.frame_senha, placeholder="Senha (obrigatorio)", width=320, height=42, show="*")
        self.entry_senha.pack()

        self.frame_aluno_prof = ctk.CTkFrame(container, fg_color="transparent")

        self.entry_sala = criar_entry(self.frame_aluno_prof, placeholder="Sala (opcional)", width=150, height=42)
        self.entry_sala.pack(side="left", padx=(0, 10))

        self.entry_turma = criar_entry(self.frame_aluno_prof, placeholder="Turma (opcional)", width=150, height=42)
        self.entry_turma.pack(side="left")

        self.frame_func = ctk.CTkFrame(container, fg_color="transparent")

        self.entry_funcao = criar_entry(self.frame_func, placeholder="Funcao (ex: diretor)", width=320, height=42)
        self.entry_funcao.pack()

        self.btn_cadastrar = criar_botao_preenchido(
            container, text="Cadastrar", command=self._cadastrar,
            width=320, height=44
        )
        self.btn_cadastrar.pack(pady=(15, 15))

        criar_botao(container, text="Voltar", command=self._voltar, width=100, height=35).pack()

        self.lbl_notificacao = criar_label(container, "", text_color=COR_TEXTO2)

    def _tipo_mudou(self, tipo):
        self.frame_senha.pack_forget()
        self.frame_aluno_prof.pack_forget()
        self.frame_func.pack_forget()
        if tipo in ("aluno", "professor"):
            self.frame_aluno_prof.pack(pady=(0, 5))
        elif tipo == "bibliotecario":
            self.frame_senha.pack(pady=(0, 10))
            self.frame_func.pack(pady=(0, 5))

    def _cadastrar(self):
        nome = self.entry_nome.get().strip()
        contato = self.entry_contato.get().strip()
        senha = self.entry_senha.get().strip()
        tipo = self.combo_tipo.get()

        if not nome:
            self._notificar("Informe o nome completo.")
            return
        if not contato:
            self._notificar("Informe o email ou celular.")
            return
        if tipo == "bibliotecario" and not senha:
            self._notificar("Senha e obrigatoria para bibliotecario.")
            return

        sala = self.entry_sala.get().strip() if tipo in ("aluno", "professor") else ""
        turma = self.entry_turma.get().strip() if tipo in ("aluno", "professor") else ""
        funcao = self.entry_funcao.get().strip() if tipo == "bibliotecario" else ""

        self.btn_cadastrar.configure(text="Cadastrando...", state="disabled")
        self.after(500, lambda: self._salvar(nome, contato, senha, tipo, sala, turma, funcao))

    def _salvar(self, nome, contato, senha, tipo, sala, turma, funcao):
        sucesso = cadastrar_usuario(
            nome, contato, senha or '', '', '', tipo, '', sala, turma, funcao
        )
        if sucesso:
            self._notificar("Conta criada com sucesso!")
            self.after(1500, lambda: self.controller.voltar())
        else:
            self._notificar("Erro ao criar conta (email duplicado?).")
        self.btn_cadastrar.configure(text="Cadastrar", state="normal")

    def _voltar(self):
        self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.pack(pady=(10, 0))
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))
