from services.conector import init_db
from services.app_controller import AppController
import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _configurar_tela_cheia(root):
    """Faz a janela entrar em tela cheia de verdade (cobrindo até a barra
    de tarefas do Windows) sempre que o usuário clicar em maximizar.

    O truque de manter a barra de título e só ajustar o tamanho da janela
    NÃO cobre a barra de tarefas de forma confiável — o Windows sempre a
    redesenha por cima. A única forma garantida de cobrir tudo é usar o
    modo fullscreen real do sistema operacional, que remove a barra de
    título (sem botões de minimizar/fechar visíveis).

    Por isso, oferecemos duas formas de sair da tela cheia:
      - Tecla ESC: volta para janela normal (restaurada)
      - Tecla F11: alterna entre tela cheia e janela normal
    """
    _em_transicao = {"ativo": False}

    def _ao_configurar(event=None):
        if event is not None and event.widget is not root:
            return
        if _em_transicao["ativo"]:
            return
        if root.state() == "zoomed" and not root.attributes("-fullscreen"):
            _em_transicao["ativo"] = True
            root.attributes("-fullscreen", True)
            root.after(50, lambda: _em_transicao.__setitem__("ativo", False))

    def _sair_tela_cheia(event=None):
        if root.attributes("-fullscreen"):
            root.attributes("-fullscreen", False)
            root.state("normal")

    def _alternar_tela_cheia(event=None):
        root.attributes("-fullscreen", not root.attributes("-fullscreen"))

    root.bind("<Map>", _ao_configurar)
    root.bind("<Configure>", _ao_configurar)
    root.bind("<Escape>", _sair_tela_cheia)
    root.bind("<F11>", _alternar_tela_cheia)


if __name__ == "__main__":                            # Só executa se for o arquivo principal
    if not init_db():                                # Tenta criar/verificar o banco de dados
        print("ERRO: Falha ao inicializar o banco de dados. Verifique se o MySQL está rodando.")

    root = ctk.CTk()                                 # Cria a janela principal do aplicativo
    _configurar_tela_cheia(root)                     # Ativa tela cheia real ao maximizar
    controller = AppController(root)                  # Cria o controlador de navegação
    controller.usuario_logado = None                  # Nenhum usuário logado no início

    # Importação de todas as telas do sistema
    from screen.tela_login import TelaLogin                         # Tela de login
    from screen.dashboard import Dashboard                          # Tela principal (dashboard)
    from screen.tela_livros import TelaLivros                       # Tela de cadastro de livros
    from screen.tela_exemplares import TelaExemplares               # Tela de exemplares físicos
    from screen.tela_cadastro_usuario import TelaCadastroUsuario    # Tela de cadastro de usuários
    from screen.emprestimos import TelaEmprestimos                  # Tela de empréstimos
    from screen.tela_configuracoes import TelaConfiguracoes         # Tela de configurações
    from screen.tela_gerenciar_usuarios import TelaGerenciarUsuarios # Tela de gerenciar usuários
    from screen.tela_catalogo import TelaCatalogo                     # Tela de catálogo de livros
    from screen.tela_relatorios import TelaRelatorios                 # Tela de relatórios
    from screen.tela_notificacoes import TelaNotificacoes             # Central de notificações

    # Registra cada tela no controlador com um nome para navegação
    controller.registrar_tela("login", TelaLogin)                   # Tela de login
    controller.registrar_tela("dashboard", Dashboard)               # Dashboard principal
    controller.registrar_tela("livros", TelaLivros)                 # Gerenciamento de livros
    controller.registrar_tela("exemplares", TelaExemplares)         # Gerenciamento de exemplares
    controller.registrar_tela("cadastro_usuario", TelaCadastroUsuario) # Cadastro de usuários
    controller.registrar_tela("emprestimos", TelaEmprestimos)       # Gerenciamento de empréstimos
    controller.registrar_tela("configuracoes", TelaConfiguracoes)   # Configurações do sistema
    controller.registrar_tela("gerenciar_usuarios", TelaGerenciarUsuarios) # Gerenciar usuários
    controller.registrar_tela("catalogo", TelaCatalogo)             # Catálogo de livros
    controller.registrar_tela("relatorios", TelaRelatorios)         # Relatórios
    controller.registrar_tela("notificacoes", TelaNotificacoes)     # Central de notificações

    # Inicia o sistema na tela de login (voltavel=False para não poder voltar ao login pelo histórico)
    controller.navegar_para("login", voltavel=False)

    root.mainloop()                                  # Inicia o loop da interface gráfica