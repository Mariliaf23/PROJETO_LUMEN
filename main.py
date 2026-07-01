
from services.conector import init_db
from services.app_controller import AppController
import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":                            # Só executa se for o arquivo principal
    if not init_db():                                # Tenta criar/verificar o banco de dados
        print("ERRO: Falha ao inicializar o banco de dados. Verifique se o MySQL está rodando.")

    root = ctk.CTk()                                 # Cria a janela principal do aplicativo
    controller = AppController(root)                  # Cria o controlador de navegação
    controller.usuario_logado = None                  # Nenhum usuário logado no início

    # Importação de todas as telas do sistema
    from screen.tela_login import TelaLogin                         # Tela de login
    from screen.dashboard import Dashboard                          # Tela principal (dashboard)
    from screen.tela_livros import TelaLivros                       # Tela de cadastro de livros
    from screen.tela_exemplares import TelaExemplares               # Tela de exemplares físicos
    from screen.tela_cadastro_usuario import TelaCadastroUsuario    # Tela de cadastro de usuários
    from screen.emprestimos import TelaEmprestimos                  # Tela de empréstimos
    from screen.tela_devolucoes import TelaDevolucoes               # Tela de devoluções
    from screen.tela_configuracoes import TelaConfiguracoes         # Tela de configurações
    from screen.tela_gerenciar_usuarios import TelaGerenciarUsuarios # Tela de gerenciar usuários

    # Registra cada tela no controlador com um nome para navegação
    controller.registrar_tela("login", TelaLogin)                   # Tela de login
    controller.registrar_tela("dashboard", Dashboard)               # Dashboard principal
    controller.registrar_tela("livros", TelaLivros)                 # Gerenciamento de livros
    controller.registrar_tela("exemplares", TelaExemplares)         # Gerenciamento de exemplares
    controller.registrar_tela("cadastro_usuario", TelaCadastroUsuario) # Cadastro de usuários
    controller.registrar_tela("emprestimos", TelaEmprestimos)       # Gerenciamento de empréstimos
    controller.registrar_tela("devolucoes", TelaDevolucoes)         # Gerenciamento de devoluções
    controller.registrar_tela("configuracoes", TelaConfiguracoes)   # Configurações do sistema
    controller.registrar_tela("gerenciar_usuarios", TelaGerenciarUsuarios) # Gerenciar usuários

    # Inicia o sistema na tela de login (voltavel=False para não poder voltar ao login pelo histórico)
    controller.navegar_para("login", voltavel=False)

    root.mainloop()                                  # Inicia o loop da interface gráfica
