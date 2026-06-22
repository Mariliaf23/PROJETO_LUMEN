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

    from screen.tela_login import TelaLogin
    from screen.dashboard import Dashboard
    from screen.tela_livros import TelaLivros
    from screen.cadastro_alunos import TelaCadastroAlunos
    from screen.cadastro_membros import TelaCadastroMembros
    from screen.emprestimos import TelaEmprestimos
    from screen.tela_devolucoes import TelaDevolucoes
    from screen.tela_configuracoes import TelaConfiguracoes
    from screen.tela_cadastro_login import LumenLoginApp

    controller.registrar_tela("login", TelaLogin)
    controller.registrar_tela("dashboard", Dashboard)
    controller.registrar_tela("livros", TelaLivros)
    controller.registrar_tela("cadastro_alunos", TelaCadastroAlunos)
    controller.registrar_tela("cadastro_membros", TelaCadastroMembros)
    controller.registrar_tela("emprestimos", TelaEmprestimos)
    controller.registrar_tela("devolucoes", TelaDevolucoes)
    controller.registrar_tela("configuracoes", TelaConfiguracoes)
    controller.registrar_tela("cadastro_login", LumenLoginApp)

    controller.navegar_para("login", voltavel=False)

    root.mainloop()
