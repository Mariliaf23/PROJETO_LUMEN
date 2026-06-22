
# This file is like the "Start" button on a video game console. 
# It tells the computer to open our special toy box!

import sys
import os

# This part helps the computer find all our toy folders, like a map of the house.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from screens.tela_login import TelaLogin

# This is where the magic starts!
if __name__ == "__main__":
    # We create our login screen, which is like the front door of our house.
    app = TelaLogin()
    # This keeps the door open so we can stay and play.
    app.mainloop()


import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from services.app_controller import AppController
from services.conector import init_db

if __name__ == "__main__":
    init_db()

    root = ctk.CTk()
    controller = AppController(root)
    controller.usuario_logado = None

    from screen.tela_login import TelaLogin
    from screen.dashboard import Dashboard
    from screen.tela_livros import TelaLivros
    from screen.tela_exemplares import TelaExemplares
    from screen.tela_cadastro_usuario import TelaCadastroUsuario
    from screen.emprestimos import TelaEmprestimos
    from screen.tela_devolucoes import TelaDevolucoes
    from screen.tela_configuracoes import TelaConfiguracoes
    from screen.tela_gerenciar_usuarios import TelaGerenciarUsuarios

    controller.registrar_tela("login", TelaLogin)
    controller.registrar_tela("dashboard", Dashboard)
    controller.registrar_tela("livros", TelaLivros)
    controller.registrar_tela("exemplares", TelaExemplares)
    controller.registrar_tela("cadastro_usuario", TelaCadastroUsuario)
    controller.registrar_tela("emprestimos", TelaEmprestimos)
    controller.registrar_tela("devolucoes", TelaDevolucoes)
    controller.registrar_tela("configuracoes", TelaConfiguracoes)
    controller.registrar_tela("gerenciar_usuarios", TelaGerenciarUsuarios)

    controller.navegar_para("login", voltavel=False)

    root.mainloop()

