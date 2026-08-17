from services.conector import init_db
from services.app_controller import AppController
from services.styles import cores
import customtkinter as ctk
import tkinter.messagebox as mb
from PIL import Image
import sys
import tkinter.messagebox as tkmb
import os
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _criar_splash(root):
    """Cria e exibe uma janela de splash simples enquanto o sistema carrega."""
    splash = ctk.CTkToplevel(root)
    splash.overrideredirect(True)          # remove barra de título/bordas
    splash.attributes("-topmost", True)    # mantém sempre à frente

    largura, altura = 420, 320
    x = (splash.winfo_screenwidth() - largura) // 2
    y = (splash.winfo_screenheight() - altura) // 2
    splash.geometry(f"{largura}x{altura}+{x}+{y}")
    splash.configure(fg_color=cores.COR_SIDEBAR)

    container = ctk.CTkFrame(splash, fg_color="transparent")
    container.pack(expand=True, fill="both")

    caminho_base = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

    if os.path.exists(logo_path):
        try:
            img_logo = ctk.CTkImage(Image.open(logo_path), size=(140, 140))
            ctk.CTkLabel(container, image=img_logo, text="").pack(pady=(45, 10))
        except Exception:
            ctk.CTkLabel(container, text="LUMEN", font=("Cinzel", 30, "bold"),
                         text_color=cores.COR_DOURADO).pack(pady=(55, 10))
    else:
        ctk.CTkLabel(container, text="LUMEN", font=("Cinzel", 30, "bold"),
                     text_color=cores.COR_DOURADO).pack(pady=(55, 10))

    lbl_status = ctk.CTkLabel(
        container, text="Iniciando o sistema...",
        font=("Segoe UI", 13), text_color=cores.COR_TEXTO2
    )
    lbl_status.pack(pady=(5, 15))

    barra = ctk.CTkProgressBar(
        container, width=260, mode="indeterminate",
        progress_color=cores.COR_AZUL_PRINCIPAL
    )
    barra.pack(pady=(0, 10))
    barra.start()

    print("Splash screen created.") # Debug print
    splash.update_idletasks()
    return splash, lbl_status


def _atualizar_status(splash, lbl_status, texto):
    """Atualiza o texto do splash e força o redesenho antes de continuar."""
    lbl_status.configure(text=texto)
    print(f"Status atualizado: {texto}") # Debug print
    splash.update_idletasks()


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

    def _sair_tela_cheia(event=None):
        if root.attributes("-fullscreen"):
            _em_transicao["ativo"] = True
            root.attributes("-fullscreen", False)
            # Restaurar para o estado normal ou maximizado, dependendo da preferência
            # root.state("normal") # Ou "zoomed" se quiser que volte maximizado
            root.after(50, lambda: _em_transicao.__setitem__("ativo", False))

    def _alternar_tela_cheia(event=None):
        if root.attributes("-fullscreen"):
            _em_transicao["ativo"] = True
            root.attributes("-fullscreen", False)
            # Restaurar para o estado normal ou maximizado
            # root.state("normal")
            root.after(50, lambda: _em_transicao.__setitem__("ativo", False))
        else:
            _em_transicao["ativo"] = True
            root.attributes("-fullscreen", True)
            root.after(50, lambda: _em_transicao.__setitem__("ativo", False))

    root.bind("<Escape>", _sair_tela_cheia)
    root.bind("<F11>", _alternar_tela_cheia)

# O código abaixo foi movido para dentro de _configurar_tela_cheia para manter a lógica encapsulada.
# A função _sair_tela_cheia foi simplificada para apenas desativar o modo fullscreen,
# pois o Tkinter geralmente restaura a geometria anterior automaticamente.




if __name__ == "__main__":                            # Só executa se for o arquivo principal
    root = ctk.CTk()                                 # Cria a janela principal do aplicativo
    root.withdraw()                                  # Esconde a janela principal até terminar de carregar

    splash, lbl_status = _criar_splash(root)          # Mostra o splash de carregamento

    def _init_db_thread():
        """Executa init_db() em thread separada para não travar o splash."""
        try:
            sucesso = init_db()
            if not sucesso:
                # Erro será tratado na thread principal via root.after
                root.after(0, lambda: _handle_db_failure())
        except Exception as e:
            root.after(0, lambda: _handle_db_failure(e))

    def _handle_db_failure(erro=None):
        """Mostra erro de conexão e pergunta se usuário quer continuar."""
        msg = "Não foi possível conectar ao banco de dados."
        if erro:
            msg += f"\n\nDetalhe: {erro}"
        continuar = mb.askyesno(
            "LUMEN - Falha ao conectar",
            f"{msg}\n\n"
            "Verifique sua conexão com a internet, se a VPN está ativa\n"
            "e se o servidor Aiven está acessível.\n\n"
            "Deseja abrir o sistema mesmo assim?"
        )
        if not continuar:
            root.destroy()
        else:
            # Mesmo que o usuário escolha continuar, tenta avançar
            root.after(50, _etapa_2_telas)

    def _etapa_1_banco():
        print("Iniciando _etapa_1_banco") # Debug print
        _atualizar_status(splash, lbl_status, "Conectando ao banco de dados...")
        if not init_db():                            # Tenta criar/verificar o banco de dados
            tkmb.showerror("Erro Crítico", "Falha ao inicializar o banco de dados. Verifique se o MySQL está rodando e se as credenciais no arquivo .env estão corretas.")
            root.destroy() # Fecha a aplicação se o banco não inicializar
            return
        print("Banco de dados inicializado com sucesso.") # Debug print
        root.after(50, _etapa_2_telas)

    def _etapa_2_telas():
        global controller
        _atualizar_status(splash, lbl_status, "Carregando telas do sistema...")
        _configurar_tela_cheia(root)                 # Configura atalhos de tela cheia (F11/ESC)
        controller = AppController(root)              # Cria o controlador de navegação
        controller.usuario_logado = None              # Nenhum usuário logado no início
        print("AppController criado.") # Debug print
        root.after(50, _etapa_3_importar)

    def _etapa_3_importar():
        """Importação preguiçosa (lazy) das telas - evitam queries de rede
        durante o início. Cada tela será importada sob demanda ao navegar."""
        from screen import tela_login, dashboard, tela_livros, tela_exemplares
        from screen import tela_cadastro_usuario, emprestimos, tela_configuracoes
        from screen import tela_gerenciar_usuarios, tela_catalogo, tela_relatorios
        from screen import tela_notificacoes

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

        print("Telas importadas.") # Debug print
        root.after(50, _etapa_4_registrar)

    def _etapa_4_registrar():
        _atualizar_status(splash, lbl_status, "Preparando ambiente...")

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

        root.after(50, _etapa_5_finalizar)

    def _etapa_5_finalizar():
        # Inicia o sistema na tela de login (voltavel=False para não poder voltar ao login pelo histórico)
        controller.navegar_para("login", voltavel=False)

        splash.destroy()                              # Fecha o splash
        root.deiconify()                              # Mostra a janela principal
        root.lift()
        root.focus_force()

    # Encadeia as etapas de carregamento usando o próprio loop de eventos,
    # em vez de bloquear a thread principal antes do mainloop começar
    # (evita a tela de splash travar sem nunca abrir o sistema).
    _etapa_1_banco()

    root.mainloop()                                  # Inicia o loop da interface gráfica