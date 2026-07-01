# tela_cadastro_login.py — Tela de cadastro de nova conta (acesso público)

import os                  # Biblioteca para manipular caminhos
import sys                 # Biblioteca do sistema

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Configura caminho

import customtkinter as ctk                                        # Interface gráfica
from services.database_config import cadastrar_usuario             # Função para salvar usuário
from services.styles import (                                      # Estilos e cores
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_entry, criar_botao_preenchido, criar_botao, criar_label, criar_titulo
)
from services.database_config import cadastrar_usuario
import customtkinter as ctk
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LumenLoginApp(ctk.CTkFrame):
    """Tela de cadastro de nova conta para novos bibliotecários."""

    def __init__(self, master=None, controller=None):
        """Inicializa a tela de cadastro."""
        super().__init__(master, fg_color=COR_BG)   # Frame com fundo escuro
        self.controller = controller                 # Controlador de navegação
        self._construir_ui()                         # Monta a interface

    def _construir_ui(self):
        """Monta o formulário de cadastro centralizado na tela."""
        # Container centralizado na tela
        container = ctk.CTkFrame(self, fg_color=COR_BG)
        container.place(relx=0.5, rely=0.5, anchor="center")  # Centraliza

        # Título LUMEN
        criar_titulo(container, "LUMEN", font=FONTE_TITULO).pack(pady=(0, 5))
        criar_label(container, "Criar conta", font=FONTE_SUBTITULO,
                    text_color=COR_TEXTO).pack(pady=(0, 30))

        self.entry_nome = criar_entry(
            container, placeholder="Nome completo", width=300, height=42)
        self.entry_nome.pack(pady=(0, 12))

        self.entry_email = criar_entry(
            container, placeholder="Email", width=300, height=42)
        self.entry_email.pack(pady=(0, 12))

        self.entry_senha = criar_entry(
            container, placeholder="Senha", width=300, height=42, show="*")
        self.entry_senha.pack(pady=(0, 12))

        self.entry_confirmar = criar_entry(
            container, placeholder="Confirmar senha", width=300, height=42, show="*")
        self.entry_confirmar.pack(pady=(0, 25))

        # Botão cadastrar
        self.btn_cadastrar = criar_botao_preenchido(
            container, text="Cadastrar", command=self._cadastrar,
            width=300, height=44
        )
        self.btn_cadastrar.pack(pady=(0, 20))

        criar_botao(container, text="Voltar", command=self._voltar,
                    width=100, height=35).pack()

        self.lbl_notificacao = criar_label(
            container, "", text_color=COR_TEXTO2)

    def _cadastrar(self):
        """Valida os campos e inicia o cadastro."""
        nome = self.entry_nome.get().strip()       # Pega o nome
        email = self.entry_email.get().strip()     # Pega o email
        senha = self.entry_senha.get().strip()     # Pega a senha
        confirmar = self.entry_confirmar.get().strip()  # Pega a confirmação

        if not nome:                               # Se nome está vazio
            self._notificar("Informe o nome completo.")
            return
        if not email:                              # Se email está vazio
            self._notificar("Informe o email.")
            return
        if not senha:                              # Se senha está vazia
            self._notificar("Informe a senha.")
            return
        if senha != confirmar:                     # Se senhas não conferem
            self._notificar("As senhas nao conferem.")
            return

        self.btn_cadastrar.configure(text="Cadastrando...", state="disabled")  # Desabilita botão
        self.after(500, lambda: self._salvar(nome, email, senha))  # Espera 500ms e salva

    def _salvar(self, nome, email, senha):
        """Salva o novo usuário no banco de dados."""
        sucesso = cadastrar_usuario(nome, email, senha, tipo='bibliotecario')  # Cadastra como bibliotecário
        if sucesso:                                # Se deu certo
            self._notificar("Conta criada com sucesso!")
            self.after(1500, lambda: self.controller.voltar())  # Volta ao login após 1.5s
        else:                                      # Se deu erro
            self._notificar("Erro ao criar conta.")
        self.btn_cadastrar.configure(text="Cadastrar", state="normal")  # Reabilita botão

    def _notificar(self, mensagem):
        """Mostra uma mensagem de notificação por 3 segundos."""
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")  # Cor dourada suave
        self.lbl_notificacao.pack(pady=(10, 0))    # Mostra o label
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))  # Esconde após 3s

    def _voltar(self):
        """Volta para a tela anterior (login)."""
        self.controller.voltar()                   # Navega para trás
