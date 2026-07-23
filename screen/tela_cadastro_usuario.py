# tela_cadastro_usuario.py — Tela de cadastro de usuários (alunos, professores, etc.)

import os                  # Biblioteca para manipular caminhos
import sys                 # Biblioteca do sistema
from PIL import Image      # Biblioteca para imagens

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Configura caminho

import customtkinter as ctk                                        # Interface gráfica
from services.database_config import cadastrar_usuario, listar_turmas  # Funções do banco
from services.styles import (                                      # Estilos e cores
    cores,
    criar_entry, criar_label, criar_titulo, criar_card, criar_combo,
    aplicar_validacao_focusout
)
from services.validador import validar_nome, validar_email, validar_telefone, validar_senha


class TelaCadastroUsuario(ctk.CTkFrame):
    """Tela para cadastrar novos usuários (alunos, professores, funcionários)."""

    def __init__(self, master=None, controller=None):
        """Inicializa a tela de cadastro."""
        super().__init__(master, fg_color=cores.COR_BG)   # Frame com fundo escuro
        self.controller = controller                 # Controladora de navegação
        self._turmas = listar_turmas()               # Carrega turmas do banco
        self._turma_map = {f"{c} - {t}": tid for tid, c, t in self._turmas} if self._turmas else {}
        self._construir_ui()                         # Monta a interface



    def _reconstruir_tema(self):
        """Reconstrói a tela ao trocar o tema claro/escuro."""
        if not self.winfo_exists():
            return
        self._turmas = listar_turmas()
        self._turma_map = {f"{c} - {t}": tid for tid, c, t in self._turmas} if self._turmas else {}
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=cores.COR_BG)
        self._construir_ui()

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

        criar_label(header_left, "Cadastro de Usuário", font=("Segoe UI", 38, "bold"), text_color=cores.COR_TEXTO).pack(side="left")

        # Botão voltar
        btn_voltar = ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=130, height=45,
            fg_color=cores.COR_SIDEBAR, text_color="#FFFFFF", border_color=cores.COR_INPUT_BORDER, border_width=1,
            hover_color=cores.COR_INPUT_BG, font=("Segoe UI", 16, "bold")
        )
        btn_voltar.pack(side="right")

        # ===== CARD DO FORMULÁRIO =====
        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="nsew", padx=30, pady=(10, 30))

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=35, pady=30)
        form_frame.grid_columnconfigure((0, 1), weight=1)  # 2 colunas perfeitamente iguais e expansíveis

        # Linha 1: Tipo de perfil e Nome completo
        self.combo_tipo = criar_combo(form_frame, values=["aluno", "professor", "bibliotecario", "diretor"], height=50)
        self.combo_tipo.configure(font=("Segoe UI", 16))
        self.combo_tipo.grid(row=0, column=0, padx=(0, 15), pady=12, sticky="ew")
        self.combo_tipo.set("aluno")                # Tipo padrão: aluno
        self.combo_tipo.configure(command=self._tipo_mudou)  # Atualiza campos ao mudar tipo

        self.entry_nome = criar_entry(form_frame, placeholder="Nome completo", height=50)
        self.entry_nome.configure(font=("Segoe UI", 16))
        self.entry_nome.grid(row=0, column=1, padx=(15, 0), pady=12, sticky="ew")

        # Linha 2: Email e Senha (senha só para bibliotecário e diretor)
        self.entry_email = criar_entry(form_frame, placeholder="E-mail corporativo", height=50)
        self.entry_email.configure(font=("Segoe UI", 16))
        self.entry_email.grid(row=1, column=0, padx=(0, 15), pady=12, sticky="ew")

        self.entry_senha = criar_entry(form_frame, placeholder="Senha de acesso", height=50, show="*")
        self.entry_senha.configure(font=("Segoe UI", 16))
        self.entry_senha.grid(row=1, column=1, padx=(15, 0), pady=12, sticky="ew")

        # Linha 3: Telefone e CPF
        self.entry_telefone = criar_entry(form_frame, placeholder="Telefone (opcional)", height=50)
        self.entry_telefone.configure(font=("Segoe UI", 16))
        self.entry_telefone.grid(row=2, column=0, padx=(0, 15), pady=12, sticky="ew")

        self.entry_cpf = criar_entry(form_frame, placeholder="CPF (opcional)", height=50)
        self.entry_cpf.configure(font=("Segoe UI", 16))
        self.entry_cpf.grid(row=2, column=1, padx=(15, 0), pady=12, sticky="ew")

        # Linha 4: Campos dinâmicos (Ocupa as duas colunas do form_frame para manter simetria)
        self.dinamico_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.dinamico_container.grid(row=3, column=0, columnspan=2, pady=12, sticky="ew")
        self.dinamico_container.grid_columnconfigure((0, 1, 2), weight=1)  # 3 subcolunas com divisão matemática perfeita

        # Campos para aluno
        self.entry_matricula = criar_entry(self.dinamico_container, placeholder="Matrícula", height=50)
        self.entry_matricula.configure(font=("Segoe UI", 16))

        # Combo de turma (selecionar turma existente)
        turma_labels = [f"{c} - {t}" for _, c, t in self._turmas] if self._turmas else ["(nenhuma turma)"]
        self.combo_turma = criar_combo(self.dinamico_container, values=turma_labels, height=50)
        self.combo_turma.configure(font=("Segoe UI", 16))
        if turma_labels:
            self.combo_turma.set(turma_labels[0])

        self.entry_turno = criar_entry(self.dinamico_container, placeholder="Turno", height=50)
        self.entry_turno.configure(font=("Segoe UI", 16))

        # Campo para funcionário/professor
        self.entry_funcao = criar_entry(self.dinamico_container, placeholder="Função (ex: Diretor / Professor)", height=50)
        self.entry_funcao.configure(font=("Segoe UI", 16))

        self._tipo_mudou("aluno")                    # Aplica estado inicial dos campos

        # Botão de cadastro
        botoes_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_container.grid(row=4, column=0, columnspan=2, pady=(25, 0), sticky="ew")

        self.btn_cadastrar = ctk.CTkButton(
            botoes_container, text="Confirmar e Salvar Registro", command=self._cadastrar,
            width=300, height=52,
            fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",   # Azul sólido
            hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 16, "bold")
        )
        self.btn_cadastrar.pack(pady=10)

        self.lbl_notificacao = criar_label(self, "", text_color=cores.COR_TEXTO2)

        # Validações em tempo real (focusout)
        self._lbl_erro_campo = criar_label(form_frame, "", font=("Segoe UI", 12))
        self._lbl_erro_campo.grid(row=5, column=0, columnspan=2, pady=(5, 0))

        _entries = [self.entry_nome, self.entry_email, self.entry_senha,
                    self.entry_telefone, self.entry_cpf]
        aplicar_validacao_focusout(self.entry_nome,     lambda v: validar_nome(v),                              self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_email,    lambda v: validar_email(v),                             self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_senha,    lambda v: validar_senha(v) if v else (True, ""),        self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_telefone, lambda v: validar_telefone(v),                          self._lbl_erro_campo, _entries)

    def _exibir_campos_aluno(self):
        """Mostra os campos específicos de aluno equilibrando as margens laterais externas."""
        self.entry_funcao.grid_forget()             # Esconde campo de função
        self.entry_matricula.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.combo_turma.grid(row=0, column=1, padx=(10, 10), sticky="ew")
        self.entry_turno.grid(row=0, column=2, padx=(10, 0), sticky="ew")

    def _exibir_campos_func(self):
        """Mostra o campo de função expandido na largura total do container."""
        self.entry_matricula.grid_forget()          # Esconde campos de aluno
        self.combo_turma.grid_forget()
        self.entry_turno.grid_forget()
        self.entry_funcao.grid(row=0, column=0, columnspan=3, padx=0, sticky="ew")  # Totalmente esticado

    def _tipo_mudou(self, tipo):
        """Chamado quando o tipo de perfil muda — atualiza os campos visíveis."""
        # Esconde tudo primeiro
        self.entry_senha.grid_forget()
        self.entry_matricula.grid_forget()
        self.combo_turma.grid_forget()
        self.entry_turno.grid_forget()
        self.entry_funcao.grid_forget()

        if tipo == "aluno":
            # Aluno: sem senha, com matrícula, turma, turno
            self.entry_matricula.grid(row=0, column=0, padx=(0, 10), sticky="ew")
            self.combo_turma.grid(row=0, column=1, padx=(10, 10), sticky="ew")
            self.entry_turno.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        elif tipo == "professor":
            # Professor: sem senha, sem função
            pass
        elif tipo == "bibliotecario":
            # Bibliotecário: com senha, sem função (ser bibliotecário já é a função)
            self.entry_senha.grid(row=1, column=1, padx=(15, 0), pady=12, sticky="ew")
        elif tipo == "diretor":
            # Diretor: com senha e com campo função
            self.entry_senha.grid(row=1, column=1, padx=(15, 0), pady=12, sticky="ew")
            self.entry_funcao.grid(row=0, column=0, columnspan=3, padx=0, sticky="ew")

    def _cadastrar(self):
        """Valida os campos e inicia o cadastro do usuário."""
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()
        tipo = self.combo_tipo.get()
        telefone = self.entry_telefone.get().strip()
        cpf = self.entry_cpf.get().strip()

        # Validações usando os validadores
        ok, msg = validar_nome(nome)
        if not ok:
            return self._notificar(msg)

        ok, msg = validar_email(email)
        if not ok:
            return self._notificar(msg)

        ok, msg = validar_telefone(telefone)
        if not ok:
            return self._notificar(msg)

        # Senha só é obrigatória para bibliotecário e diretor
        if tipo in ("bibliotecario", "diretor"):
            ok, msg = validar_senha(senha)
            if not ok:
                return self._notificar(msg)
        else:
            senha = ""

        # Campos condicionados ao tipo
        matricula = self.entry_matricula.get().strip() if tipo == "aluno" else ""
        funcao = self.entry_funcao.get().strip() if tipo == "diretor" else ""

        # Obtém id_turma do combo (se aluno)
        id_turma = None
        if tipo == "aluno":
            turma_sel = self.combo_turma.get().strip()
            id_turma = self._turma_map.get(turma_sel)

        self.btn_cadastrar.configure(text="Processando...", state="disabled")
        self._salvar(nome, email, senha, telefone, cpf, tipo, matricula, id_turma, funcao)

    def _salvar(self, nome, email, senha, telefone, cpf, tipo, matricula, id_turma, funcao):
        """Salva o usuário no banco de dados."""
        sucesso = cadastrar_usuario(nome, email, senha, telefone, cpf, tipo, matricula, id_turma, funcao)
        if sucesso:
            self._notificar("Usuário registrado com sucesso!")
            self.after(1500, lambda: self._voltar())
        else:
            self._notificar("Erro: E-mail ou CPF já constam no banco.")
        self.btn_cadastrar.configure(text="Confirmar e Salvar Registro", state="normal")

    def _voltar(self):
        """Volta para a tela anterior."""
        if self.controller:
            self.controller.voltar()

    def _notificar(self, mensagem):
        """Mostra uma mensagem de notificação temporária centralizada na base."""
        self.lbl_notificacao.configure(text=mensagem, text_color=cores.COR_DOURADO, font=("Segoe UI", 15, "bold"))
        self.lbl_notificacao.place(relx=0.5, rely=0.95, anchor="center")
        self.lbl_notificacao.bind("<Button-1>", lambda e: self.lbl_notificacao.configure(text=""))
        self.after(5000, lambda: self.lbl_notificacao.configure(text=""))