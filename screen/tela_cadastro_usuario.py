import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import cadastrar_usuario
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_INPUT_BORDER,
    criar_entry, criar_label, criar_titulo, criar_card, criar_combo
)


class TelaCadastroUsuario(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._construir_ui()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === HEADER CORPORATIVO (LOGO + BOTÃO VOLTAR) ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 15))

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")
        
        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y")

        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(85, 85))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")

        criar_label(header_left, "|  Cadastro de Usuário", font=("Segoe UI", 26, "bold"), text_color=COR_TEXTO).pack(side="left")

        btn_voltar = ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=130, height=45,
            fg_color="#0F172A", text_color="#FFFFFF", border_color=COR_INPUT_BORDER, border_width=1,
            hover_color="#1E293B", font=("Segoe UI", 16, "bold")
        )
        btn_voltar.pack(side="right")

        # === CARD PRINCIPAL EXPANDIDO EM DUAS COLUNAS ===
        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 30))

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=35, pady=30)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        # Fileira 1: Tipo de Perfil e Nome Completo (Largos e nítidos)
        self.combo_tipo = criar_combo(form_frame, values=["aluno", "professor", "funcionario"], height=50)
        self.combo_tipo.configure(font=("Segoe UI", 16))
        self.combo_tipo.grid(row=0, column=0, padx=(0, 15), pady=12, sticky="ew")
        self.combo_tipo.set("aluno")
        self.combo_tipo.configure(command=self._tipo_mudou)

        self.entry_nome = criar_entry(form_frame, placeholder="Nome completo", height=50)
        self.entry_nome.configure(font=("Segoe UI", 16))
        self.entry_nome.grid(row=0, column=1, padx=(15, 0), pady=12, sticky="ew")

        # Fileira 2: E-mail e Senha
        self.entry_email = criar_entry(form_frame, placeholder="E-mail corporativo", height=50)
        self.entry_email.configure(font=("Segoe UI", 16))
        self.entry_email.grid(row=1, column=0, padx=(0, 15), pady=12, sticky="ew")

        self.entry_senha = criar_entry(form_frame, placeholder="Senha de acesso", height=50, show="*")
        self.entry_senha.configure(font=("Segoe UI", 16))
        self.entry_senha.grid(row=1, column=1, padx=(15, 0), pady=12, sticky="ew")

        # Fileira 3: Telefone e CPF
        self.entry_telefone = criar_entry(form_frame, placeholder="Telefone (opcional)", height=50)
        self.entry_telefone.configure(font=("Segoe UI", 16))
        self.entry_telefone.grid(row=2, column=0, padx=(0, 15), pady=12, sticky="ew")

        self.entry_cpf = criar_entry(form_frame, placeholder="CPF (opcional)", height=50)
        self.entry_cpf.configure(font=("Segoe UI", 16))
        self.entry_cpf.grid(row=2, column=1, padx=(15, 0), pady=12, sticky="ew")

        # === FILEIRA 4: CAMPOS DINÂMICOS (ALUNOS OU FUNCIONÁRIOS) ===
        # Container dinâmico que ocupa a largura total abaixo das colunas fixas
        self.dinamico_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.dinamico_container.grid(row=3, column=0, columnspan=2, pady=12, sticky="ew")
        self.dinamico_container.grid_columnconfigure((0, 1, 2), weight=1)

        # Elementos do Aluno (Organizados horizontalmente ocupando o espaço)
        self.entry_matricula = criar_entry(self.dinamico_container, placeholder="Matrícula", height=50)
        self.entry_matricula.configure(font=("Segoe UI", 16))
        
        self.entry_sala = criar_entry(self.dinamico_container, placeholder="Sala", height=50)
        self.entry_sala.configure(font=("Segoe UI", 16))
        
        self.entry_turno = criar_entry(self.dinamico_container, placeholder="Turno", height=50)
        self.entry_turno.configure(font=("Segoe UI", 16))

        # Elementos do Funcionário/Professor
        self.entry_funcao = criar_entry(self.dinamico_container, placeholder="Função (ex: Diretor / Professor Corregedor)", height=50)
        self.entry_funcao.configure(font=("Segoe UI", 16))

        # Inicia exibindo o layout do aluno por padrão
        self._exibir_campos_aluno()

        # === CONTAINER DO BOTÃO PRINCIPAL (AZUL SÓLIDO) ===
        botoes_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_container.grid(row=4, column=0, columnspan=2, pady=(25, 0))

        self.btn_cadastrar = ctk.CTkButton(
            botoes_container, text="Confirmar e Salvar Registro", command=self._cadastrar,
            width=300, height=52,
            fg_color="#0052CC", text_color="#FFFFFF", # Azul Puro Sólido
            hover_color="#003399", font=("Segoe UI", 16, "bold")
        )
        self.btn_cadastrar.pack()

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

    def _exibir_campos_aluno(self):
        self.entry_funcao.grid_forget()
        self.entry_matricula.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry_sala.grid(row=0, column=1, padx=(10, 10), sticky="ew")
        self.entry_turno.grid(row=0, column=2, padx=(10, 0), sticky="ew")

    def _exibir_campos_func(self):
        self.entry_matricula.grid_forget()
        self.entry_sala.grid_forget()
        self.entry_turno.grid_forget()
        self.entry_funcao.grid(row=0, column=0, columnspan=3, sticky="ew")

    def _tipo_mudou(self, tipo):
        if tipo == "aluno":
            self._exibir_campos_aluno()
        elif tipo in ("funcionario", "bibliotecario", "professor"):
            self._exibir_campos_func()

    def _cadastrar(self):
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()
        telefone = self.entry_telefone.get().strip()
        cpf = self.entry_cpf.get().strip()
        tipo = self.combo_tipo.get()

        if not nome or not email or not senha:
            self._notificar("Por favor, preencha Nome, E-mail e Senha.")
            return

        matricula = self.entry_matricula.get().strip() if tipo == "aluno" else ""
        sala = self.entry_sala.get().strip() if tipo == "aluno" else ""
        turno = self.entry_turno.get().strip() if tipo == "aluno" else ""
        funcao = self.entry_funcao.get().strip() if tipo in ("funcionario", "bibliotecario", "professor") else ""

        self.btn_cadastrar.configure(text="Processando...", state="disabled")
        self.after(400, lambda: self._salvar(
            nome, email, senha, telefone, cpf, tipo, matricula, sala, turno, funcao
        ))

    def _salvar(self, nome, email, senha, telefone, cpf, tipo, matricula, sala, turno, funcao):
        sucesso = cadastrar_usuario(
            nome, email, senha, telefone, cpf, tipo, matricula, sala, turno, funcao
        )
        if sucesso:
            self._notificar("Usuário registrado com sucesso!")
            self.after(1500, lambda: self._voltar())
        else:
            self._notificar("Erro: E-mail ou CPF já constam no banco.")
        self.btn_cadastrar.configure(text="Confirmar e Salvar Registro", state="normal")

    def _voltar(self):
        if self.controller:
            self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color=COR_DOURADO, font=("Segoe UI", 15, "bold"))
        self.lbl_notificacao.place(relx=0.5, rely=0.95, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))