# tela_login.py — Tela de login do sistema LUMEN

import os                  # Biblioteca para manipular caminhos
import sys                 # Biblioteca para acessar variáveis do sistema
from PIL import Image      # Biblioteca para abrir imagens

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Configura caminho

import customtkinter as ctk                                        # Interface gráfica
from services.database_config import verificar_login                # Função para verificar login
from services.styles import (                                       # Estilos e cores
    cores,
    criar_entry, criar_label, criar_titulo
)


class TelaLogin(ctk.CTkFrame):
    """Tela de login dividida em dois painéis: logo à esquerda, formulário à direita."""

    def __init__(self, master=None, controller=None):
        """Inicializa a tela de login."""
        super().__init__(master, fg_color=cores.COR_BG)   # Frame com fundo escuro
        self.controller = controller                 # Controlador de navegação
        self._usuario_logado = None                  # Usuário que fez login
        self._construir_ui()                         # Monta a interface

        cores.registrar_listener(self._reconstruir_tema)
        self.bind("<Destroy>", self._ao_destruir)

    def _ao_destruir(self, event=None):
        if event is not None and event.widget is not self:
            return
        cores.remover_listener(self._reconstruir_tema)

    def _reconstruir_tema(self):
        """Reconstrói a tela ao trocar o tema claro/escuro."""
        if not self.winfo_exists():
            return
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=cores.COR_BG)
        self._construir_ui()

    def _construir_ui(self):
        """Monta toda a interface da tela de login."""
        # Configura duas colunas iguais (esquerda = logo, direita = formulário)
        self.grid_columnconfigure(0, weight=1)       # Coluna 0: lado esquerdo
        self.grid_columnconfigure(1, weight=1)       # Coluna 1: lado direito
        self.grid_rowconfigure(0, weight=1)          # Linha 0: ocupa toda a altura

        # Procura o arquivo da logo
        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Pasta raiz
        caminho_logo = os.path.join(caminho_base, "assets", "logo_lumen.png")  # Caminho da logo (mesmo padrão das outras telas)

        # ===== PAINEL ESQUERDO: Logo grande =====
        painel_esquerdo = ctk.CTkFrame(self, fg_color=cores.COR_SIDEBAR, corner_radius=0)  # Fundo azul escuro
        painel_esquerdo.grid(row=0, column=0, sticky="nsew")  # Preenche toda a coluna esquerda

        container_logo = ctk.CTkFrame(painel_esquerdo, fg_color="transparent")  # Container centralizado
        container_logo.place(relx=0.5, rely=0.5, anchor="center")  # Centraliza na tela

        if os.path.exists(caminho_logo):             # Se a logo existe
            try:
                # Abre e redimensiona a logo para 400x400 pixels
                imagem_logo = ctk.CTkImage(
                    light_image=Image.open(caminho_logo),   # Imagem para tema claro
                    dark_image=Image.open(caminho_logo),    # Imagem para tema escuro
                    size=(400, 400)                         # Tamanho da logo
                )
                lbl_logo = ctk.CTkLabel(container_logo, image=imagem_logo, text="")  # Label com a imagem
                lbl_logo.pack()                    # Mostra a logo
            except Exception as e:                 # Se deu erro ao carregar a imagem
                criar_titulo(container_logo, "LUMEN", font=("Cinzel", 60, "bold")).pack()  # Mostra texto
        else:                                      # Se não encontrou o arquivo da logo
            criar_titulo(container_logo, "LUMEN", font=("Cinzel", 60, "bold")).pack()  # Mostra texto

        # ===== PAINEL DIREITO: Formulário de Login =====
        painel_direito = ctk.CTkFrame(self, fg_color=cores.COR_BG, corner_radius=0)  # Fundo escuro
        painel_direito.grid(row=0, column=1, sticky="nsew")  # Preenche toda a coluna direita

        container_form = ctk.CTkFrame(painel_direito, fg_color="transparent")  # Container centralizado
        container_form.place(relx=0.5, rely=0.5, anchor="center")  # Centraliza

        # Título "Bem-vindo"
        criar_titulo(container_form, "Bem-vindo", font=("Segoe UI", 42, "bold"), text_color=cores.COR_TEXTO).pack(anchor="w", pady=(0, 5))
        # Subtítulo explicativo
        criar_label(container_form, "Acesse a plataforma da biblioteca Lumen", font=("Segoe UI Light", 16), text_color=cores.COR_TEXTO2).pack(anchor="w", pady=(0, 40))

        # Campo de entrada: Usuário
        self.entry_usuario = criar_entry(container_form, placeholder="Usuário", width=380, height=50)
        self.entry_usuario.configure(font=("Segoe UI", 14))  # Fonte maior
        self.entry_usuario.pack(pady=(0, 20))       # Espaço abaixo

        # Campo de entrada: Senha (com asteriscos)
        self.entry_senha = criar_entry(container_form, placeholder="Senha", width=380, height=50, show="*")
        self.entry_senha.configure(font=("Segoe UI", 14))
        self.entry_senha.pack(pady=(0, 35))

        # Botão "Entrar" com cor azul vibrante
        COR_BOTAO_CUSTOM = "#0091FF"                # Azul vibrante
        COR_BOTAO_HOVER = "#0070C6"                 # Azul um pouco mais escuro (hover)

        self.btn_entrar = ctk.CTkButton(
            container_form,
            text="Entrar no Sistema",               # Texto do botão
            command=self._entrar,                    # Função chamada ao clicar
            font=("Segoe UI Semibold", 14),          # Fonte negrita
            fg_color=COR_BOTAO_CUSTOM,               # Cor de fundo: azul
            hover_color=COR_BOTAO_HOVER,             # Cor ao passar o mouse
            text_color="#FFFFFF",                    # Texto branco
            corner_radius=8,                         # Cantos arredondados
            width=380,                               # Largura
            height=50                                # Altura
        )
        self.btn_entrar.pack(pady=(0, 30))

        
        # Label para mensagens de erro (inicialmente vazio)
        self.lbl_erro = criar_label(container_form, "", text_color=cores.COR_TEXTO2, font=("Segoe UI", 12))

    def _entrar(self):
        """ Chamado ao clicar no botão 'Entrar' — valida campos e verifica login."""
        usuario = self.entry_usuario.get().strip()   # Pega o texto do campo usuário
        senha = self.entry_senha.get().strip()       # Pega o texto do campo senha

        if not usuario:                              # Se usuário está vazio
            self._mostrar_erro("Informe o usuário.")  # Mostra erro
            return                                   # Para aqui
        if not senha:                                # Se senha está vazia
            self._mostrar_erro("Informe a senha.")   # Mostra erro
            return

        self.btn_entrar.configure(text="Carregando...", state="disabled")
        self._verificar(usuario, senha)

    def _verificar(self, usuario, senha):
        """Verifica se o usuário e senha estão corretos no banco de dados."""
        try:
            resultado = verificar_login(usuario, senha)  # Consulta o banco

            if resultado:                           # Se encontrou o usuário
                self._usuario_logado = {             # Salva os dados do usuário
                    'id': resultado[0],              # ID no banco
                    'nome': resultado[1],            # Nome do usuário
                    'tipo': resultado[2]             # Tipo (diretor/bibliotecario/aluno)
                }
                self.controller.usuario_logado = self._usuario_logado  # Salva no controlador
                self.controller.navegar_para("dashboard", voltavel=False)  # Vai para o dashboard
            else:                                    # Se não encontrou
                self._mostrar_erro("Usuário ou senha incorretos.")  # Erro de login
        except Exception as e:                       # Se der erro de conexão
            self._mostrar_erro(f"Erro de conexão: {e}")
        finally:
            self.btn_entrar.configure(text="Entrar no Sistema", state="normal")  # Reabilita botão

    def _mostrar_erro(self, mensagem):
        """Mostra uma mensagem de erro por 3 segundos."""
        self.lbl_erro.configure(text=mensagem, text_color="#d4b896")  # Cor dourada suave
        self.lbl_erro.pack(pady=(5, 0))              # Mostra o label
        self.after(3000, lambda: self.lbl_erro.configure(text=""))  # Esconde após 3 segundos