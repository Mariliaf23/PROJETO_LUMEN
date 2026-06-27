# tela_cadastro_usuario.py — Tela de cadastro de usuários (alunos, professores, etc.)

import os                  # Biblioteca para manipular caminhos
import sys                 # Biblioteca do sistema
from PIL import Image      # Biblioteca para imagens

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Configura caminho

import customtkinter as ctk                                        # Interface gráfica
from services.database_config import cadastrar_usuario             # Função para salvar usuário
from services.styles import (                                      # Estilos e cores
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_INPUT_BORDER,
    criar_entry, criar_label, criar_titulo, criar_card, criar_combo
)


class TelaCadastroUsuario(ctk.CTkFrame):
    """Tela para cadastrar novos usuários (alunos, professores, funcionários)."""

    def __init__(self, master=None, controller=None):
        """Inicializa a tela de cadastro."""
        super().__init__(master, fg_color=COR_BG)   # Frame com fundo escuro
        self.controller = controller                 # Controlador de navegação
        self._construir_ui()                         # Monta a interface

    def _construir_ui(self):
        """Monta o formulário de cadastro de usuário."""
        self.grid_columnconfigure(0, weight=1)       # Coluna 0 expansível
        self.grid_rowconfigure(1, weight=1)          # Linha 1 expansível

        # ===== CABEÇALHO: Logo + Título + Botão Voltar =====
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 15))

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Pasta raiz
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")  # Caminho da logo

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y")

        if os.path.exists(logo_path):               # Se a logo existe
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(180, 180))  # Carrega logo
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")    # Mostra logo
                lbl_logo.pack(side="left", padx=(0, 15))
            except:                                  # Se deu erro
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")
        else:                                        # Se não tem logo
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")

        criar_label(header_left, "Cadastro de Usuário", font=("Segoe UI", 38, "bold"), text_color=COR_TEXTO).pack(side="left")

        # Botão voltar
        btn_voltar = ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=130, height=45,
            fg_color="#0F172A", text_color="#FFFFFF", border_color=COR_INPUT_BORDER, border_width=1,
            hover_color="#1E293B", font=("Segoe UI", 16, "bold")
        )
        btn_voltar.pack(side="right")

        # ===== CARD DO FORMULÁRIO =====
        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 30))

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=35, pady=30)
        form_frame.grid_columnconfigure((0, 1), weight=1)  # 2 colunas iguais

        # Linha 1: Tipo de perfil e Nome completo
        self.combo_tipo = criar_combo(form_frame, values=["aluno", "professor", "funcionario"], height=50)
        self.combo_tipo.configure(font=("Segoe UI", 16))
        self.combo_tipo.grid(row=0, column=0, padx=(0, 15), pady=12, sticky="ew")
        self.combo_tipo.set("aluno")                # Tipo padrão: aluno
        self.combo_tipo.configure(command=self._tipo_mudou)  # Atualiza campos ao mudar tipo

        self.entry_nome = criar_entry(form_frame, placeholder="Nome completo", height=50)
        self.entry_nome.configure(font=("Segoe UI", 16))
        self.entry_nome.grid(row=0, column=1, padx=(15, 0), pady=12, sticky="ew")

        # Linha 2: Email e Senha
        self.entry_email = criar_entry(form_frame, placeholder="E-mail corporativo", height=50)
        self.entry_email.configure(font=("Segoe UI", 16))
        self.entry_email.grid(row=1, column=0, padx=(0, 15), pady=12, sticky="ew")

        self.entry_senha = criar_entry(form_frame, placeholder="Senha de acesso", height=50, show="*")
        self.entry_senha.configure(font=("Segoe UI", 16))
        self.entry_senha.grid(row=1, column=1, padx=(15, 0), pady=12, sticky="ew")

        # Linha 3: Telefone e CPF (ambos opcionais)
        self.entry_telefone = criar_entry(form_frame, placeholder="Telefone (opcional)", height=50)
        self.entry_telefone.configure(font=("Segoe UI", 16))
        self.entry_telefone.grid(row=2, column=0, padx=(0, 15), pady=12, sticky="ew")

        self.entry_cpf = criar_entry(form_frame, placeholder="CPF (opcional)", height=50)
        self.entry_cpf.configure(font=("Segoe UI", 16))
        self.entry_cpf.grid(row=2, column=1, padx=(15, 0), pady=12, sticky="ew")

        # Linha 4: Campos dinâmicos (mudam conforme o tipo selecionado)
        self.dinamico_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.dinamico_container.grid(row=3, column=0, columnspan=2, pady=12, sticky="ew")
        self.dinamico_container.grid_columnconfigure((0, 1, 2), weight=1)  # 3 colunas

        # Campos para aluno
        self.entry_matricula = criar_entry(self.dinamico_container, placeholder="Matrícula", height=50)
        self.entry_matricula.configure(font=("Segoe UI", 16))

        self.entry_sala = criar_entry(self.dinamico_container, placeholder="Sala", height=50)
        self.entry_sala.configure(font=("Segoe UI", 16))

        self.entry_turno = criar_entry(self.dinamico_container, placeholder="Turno", height=50)
        self.entry_turno.configure(font=("Segoe UI", 16))

        # Campo para funcionário/professor
        self.entry_funcao = criar_entry(self.dinamico_container, placeholder="Função (ex: Diretor / Professor)", height=50)
        self.entry_funcao.configure(font=("Segoe UI", 16))

        self._exibir_campos_aluno()                 # Mostra campos de aluno por padrão

        # Botão de cadastro
        botoes_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_container.grid(row=4, column=0, columnspan=2, pady=(25, 0))

        self.btn_cadastrar = ctk.CTkButton(
            botoes_container, text="Confirmar e Salvar Registro", command=self._cadastrar,
            width=300, height=52,
            fg_color="#0052CC", text_color="#FFFFFF",   # Azul sólido
            hover_color="#003399", font=("Segoe UI", 16, "bold")
        )
        self.btn_cadastrar.pack()

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

    def _exibir_campos_aluno(self):
        """Mostra os campos específicos de aluno (matrícula, sala, turno)."""
        self.entry_funcao.grid_forget()             # Esconde campo de função
        self.entry_matricula.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry_sala.grid(row=0, column=1, padx=(10, 10), sticky="ew")
        self.entry_turno.grid(row=0, column=2, padx=(10, 0), sticky="ew")

    def _exibir_campos_func(self):
        """Mostra os campos específicos de funcionário (função)."""
        self.entry_matricula.grid_forget()          # Esconde campos de aluno
        self.entry_sala.grid_forget()
        self.entry_turno.grid_forget()
        self.entry_funcao.grid(row=0, column=0, columnspan=3, sticky="ew")  # Mostra função

    def _tipo_mudou(self, tipo):
        """Chamado quando o tipo de perfil muda — atualiza os campos visíveis."""
        if tipo == "aluno":                         # Se é aluno
            self._exibir_campos_aluno()             # Mostra matrícula, sala, turno
        elif tipo in ("funcionario", "bibliotecario", "professor"):  # Se é funcionário
            self._exibir_campos_func()              # Mostra função

    def _cadastrar(self):
        """Valida os campos e inicia o cadastro do usuário."""
        nome = self.entry_nome.get().strip()        # Nome completo
        email = self.entry_email.get().strip()      # Email
        senha = self.entry_senha.get().strip()      # Senha
        tipo = self.combo_tipo.get()                # Tipo de perfil
        telefone = self.entry_telefone.get().strip()  # Telefone
        cpf = self.entry_cpf.get().strip()          # CPF

        if not nome or not email or not senha:      # Campos obrigatórios
            self._notificar("Por favor, preencha Nome, E-mail e Senha.")
            return

        # Campos condicionais ao tipo
        matricula = self.entry_matricula.get().strip() if tipo == "aluno" else ""
        sala = self.entry_sala.get().strip() if tipo == "aluno" else ""
        turno = self.entry_turno.get().strip() if tipo == "aluno" else ""
        funcao = self.entry_funcao.get().strip() if tipo in ("funcionario", "bibliotecario", "professor") else ""

        self.btn_cadastrar.configure(text="Processando...", state="disabled")  # Desabilita botão
        self.after(400, lambda: self._salvar(nome, email, senha, telefone, cpf, tipo, matricula, sala, turno, funcao))

    def _salvar(self, nome, email, senha, telefone, cpf, tipo, matricula, sala, turno, funcao):
        """Salva o usuário no banco de dados."""
        sucesso = cadastrar_usuario(nome, email, senha, telefone, cpf, tipo, matricula, sala, turno, funcao)
        if sucesso:                                # Se deu certo
            self._notificar("Usuário registrado com sucesso!")
            self.after(1500, lambda: self._voltar())  # Volta após 1.5s
        else:                                      # Se deu erro
            self._notificar("Erro: E-mail ou CPF já constam no banco.")
        self.btn_cadastrar.configure(text="Confirmar e Salvar Registro", state="normal")

    def _voltar(self):
        """Volta para a tela anterior."""
        if self.controller:
            self.controller.voltar()

    def _notificar(self, mensagem):
        """Mostra uma mensagem de notificação por 3 segundos."""
        self.lbl_notificacao.configure(text=mensagem, text_color=COR_DOURADO, font=("Segoe UI", 15, "bold"))
        self.lbl_notificacao.place(relx=0.5, rely=0.95, anchor="center")  # Centraliza na parte inferior
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))  # Esconde após 3s
