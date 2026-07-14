# app_controller.py — Controlador principal que gerencia navegação entre telas

import customtkinter as ctk   # Biblioteca de interface gráfica
from services.styles import COR_BG  # Cor de fundo do aplicativo


class AppController:
    """Gerencia a navegação entre telas, animações e controle de acesso."""

    # Telas que o bibliotecário pode acessar (diretor acessa todas)
    TELAS_BIBLIOTECARIO = {"dashboard", "livros", "exemplares", "emprestimos"}

    def __init__(self, root):
        """Configura a janela principal do aplicativo."""
        self.root = root                       # Referência à janela raiz do tkinter
        self.root.title("LUMEN")               # Título da janela
        self.root.geometry("960x680")          # Tamanho inicial da janela (largura x altura)
        self.root.minsize(800, 580)            # Tamanho mínimo permitido
        self.root.configure(fg_color=COR_BG)   # Cor de fundo da janela

        # Container principal onde todas as telas são exibidas
        self._container = ctk.CTkFrame(root, fg_color=COR_BG)  # Frame que segura as telas
        self._container.pack(fill="both", expand=True)          # Preenche toda a janela

        self._telas = {}           # Dicionário com todas as telas registradas (nome -> frame)
        self._tela_atual = None    # Nome da tela que está sendo exibida agora
        self._historico = []       # Lista de telas visitadas (para o botão voltar)
        self._animando = False     # True enquanto uma animação de transição está rodando
        self.usuario_logado = None # Dados do usuário logado (id, nome, tipo)

        self._centralizar()        # Centraliza a janela na tela do computador

    def verificar_acesso(self, tela):
        """Verifica se o usuário logado pode acessar a tela solicitada."""
        if tela == "login":              # Tela de login sempre é acessível
            return True
        if not self.usuario_logado:      # Se ninguém está logado, não pode acessar
            return False
        tipo = self.usuario_logado.get('tipo', '')  # Pega o tipo do usuário (diretor/bibliotecario)
        if tipo == 'diretor':            # Diretor pode acessar qualquer tela
            return True
        if tipo == 'bibliotecario':     # Bibliotecário só pode acessar telas específicas
            return tela in self.TELAS_BIBLIOTECARIO
        return False                     # Outros tipos não têm acesso

    def _centralizar(self):
        """Centraliza a janela na tela do monitor."""
        self.root.update_idletasks()                    # Atualiza as medições da janela
        L = self.root.winfo_width()                     # Largura atual da janela
        A = self.root.winfo_height()                    # Altura atual da janela
        x = (self.root.winfo_screenwidth() - L) // 2   # Posição X para centralizar
        y = (self.root.winfo_screenheight() - A) // 2   # Posição Y para centralizar
        self.root.geometry(f"+{x}+{y}")                 # Aplica a posição calculada

    def registrar_tela(self, nome, classe_tela):
        """Registra uma tela no controlador para uso posterior na navegação."""
        frame = classe_tela(master=self._container, controller=self)  # Cria a tela
        self._telas[nome] = frame                     # Salva no dicionário pelo nome
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Posiciona preenchendo o container
        frame.place_forget()                          # Esconde a tela (será mostrada quando necessário)

    def navegar_para(self, nome, voltavel=True):
        """Navega para a tela indicada pelo nome."""
        if self._animando:
            return

        if self._tela_atual and self._tela_atual == nome:
            return

        if not self.verificar_acesso(nome):
            return

        if voltavel and self._tela_atual:
            self._historico.append(self._tela_atual)

        antiga = self._tela_atual
        self._tela_atual = nome
        nova_tela = self._telas[nome]

        callback = nova_tela._ao_visitar if hasattr(nova_tela, '_ao_visitar') else None

        if antiga:
            self._animar_slide(self._telas[antiga], nova_tela, direcao="esquerda", callback=callback)
        else:
            nova_tela.place(relx=0, rely=0, relwidth=1, relheight=1)
            nova_tela.lift()
            if callback:
                callback()

    def voltar(self):
        """Volta para a tela anterior (usando o histórico)."""
        if self._animando:
            return

        if not self._historico:
            return

        anterior = self._historico.pop()
        antiga = self._tela_atual
        self._tela_atual = anterior
        tela_volta = self._telas[anterior]

        callback = tela_volta._ao_visitar if hasattr(tela_volta, '_ao_visitar') else None

        if antiga:
            self._animar_slide(self._telas[antiga], tela_volta, direcao="direita", callback=callback)
        else:
            tela_volta.place(relx=0, rely=0, relwidth=1, relheight=1)
            tela_volta.lift()
            if callback:
                callback()

    def _animar_slide(self, saindo, entrando, direcao="esquerda", duracao=250, callback=None):
        """Anima a transição entre telas com efeito de deslize."""
        self._animando = True
        saindo.update_idletasks()
        largura = saindo.winfo_width()

        if direcao == "esquerda":
            x_inicio_nova = largura
            x_fim_nova = 0
            x_inicio_velha = 0
            x_fim_velha = -largura
        else:
            x_inicio_nova = -largura
            x_fim_nova = 0
            x_inicio_velha = 0
            x_fim_velha = largura

        entrando.place(relx=0, rely=0, relwidth=1, relheight=1)
        entrando.place_configure(x=x_inicio_nova)
        entrando.lift()

        passos = 15
        intervalo = max(duracao // passos, 1)

        self._animar_passo(
            saindo, entrando,
            x_inicio_velha, x_fim_velha,
            x_inicio_nova, x_fim_nova,
            0, passos, intervalo, callback
        )

    def _animar_passo(self, saindo, entrando, x_sv, x_fv, x_sn, x_fn, passo, total, intervalo, callback=None):
        """Executa um quadro da animação de transição."""
        if passo >= total:
            saindo.place_forget()
            entrando.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._animando = False
            if callback:
                callback()
            return

        t = (passo + 1) / total
        t_suave = self._ease_out_cubic(t)

        x_velha = x_sv + (x_fv - x_sv) * t_suave
        x_nova = x_sn + (x_fn - x_sn) * t_suave

        saindo.place_configure(x=int(x_velha))
        entrando.place_configure(x=int(x_nova))

        self.root.after(intervalo, lambda: self._animar_passo(
            saindo, entrando, x_sv, x_fv, x_sn, x_fn,
            passo + 1, total, intervalo, callback
        ))

    def _ease_out_cubic(self, t):
        """Função de suavização que desacelera no final (ease-out cúbico)."""
        return 1 - (1 - t) ** 3                     # Fórmula: começa rápido, termina devagar
