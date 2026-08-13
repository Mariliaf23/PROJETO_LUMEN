from services.conector import init_db
from services.app_controller import AppController
from services.styles import cores
import customtkinter as ctk
import tkinter.messagebox as mb
from PIL import Image
import sys
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

    splash.update_idletasks()
    return splash, lbl_status


def _atualizar_status(splash, lbl_status, texto):
    """Atualiza o texto do splash e força o redesenho antes de continuar."""
    lbl_status.configure(text=texto)
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
        """Inicia verificação de banco em thread separada."""
        # Limpa qualquer callback anterior e inicia nova thread
        _em_transicao = {"ativo": False}  # reset
        db_thread = threading.Thread(target=_init_db_thread, daemon=True)
        db_thread.start()
        # Segue adiante - o banco pode demorar mas o sistema continua carregando
        # as telas preguiçosamente. O resultado do banco é tratado depois.
        root.after(10, _etapa_2_telas)

    def _etapa_2_telas():
        global controller
        _atualizar_status(splash, lbl_status, "Carregando telas do sistema...")
        _configurar_tela_cheia(root)                 # Ativa tela cheia ao maximizar
        controller = AppController(root)              # Cria o controlador de navegação
        controller.usuario_logado = None              # Nenhum usuário logado no início
        root.after(10, _etapa_3_importar)

    def _etapa_3_importar():
        """Importação preguiçosa (lazy) das telas - evitam queries de rede
        durante o início. Cada tela será importada sob demanda ao navegar."""
        from screen import tela_login, dashboard, tela_livros, tela_exemplares
        from screen import tela_cadastro_usuario, emprestimos, tela_configuracoes
        from screen import tela_gerenciar_usuarios, tela_catalogo, tela_relatorios
        from screen import tela_notificacoes

        # Registra apenas as classes-base (as instâncias criam-se ao navegar)
        controller.registrar_tela("login", tela_login.TelaLogin)
        controller.registrar_tela("dashboard", dashboard.Dashboard)
        controller.registrar_tela("livros", tela_livros.TelaLivros)
        controller.registrar_tela("exemplares", tela_exemplares.TelaExemplares)
        controller.registrar_tela("cadastro_usuario", tela_cadastro_usuario.TelaCadastroUsuario)
        controller.registrar_tela("emprestimos", emprestimos.TelaEmprestimos)
        controller.registrar_tela("configuracoes", tela_configuracoes.TelaConfiguracoes)
        controller.registrar_tela("gerenciar_usuarios", tela_gerenciar_usuarios.TelaGerenciarUsuarios)
        controller.registrar_tela("catalogo", tela_catalogo.TelaCatalogo)
        controller.registrar_tela("relatorios", tela_relatorios.TelaRelatorios)
        controller.registrar_tela("notificacoes", tela_notificacoes.TelaNotificacoes)

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