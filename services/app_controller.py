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
        if self._animando:                            # Se está animando, bloqueia nova navegação
            return

        if self._tela_atual and self._tela_atual == nome:  # Se já está nessa tela, não faz nada
            return

        if not self.verificar_acesso(nome):           # Verifica se o usuário pode acessar
            return

        if voltavel and self._tela_atual:             # Se pode voltar e tem tela atual
            self._historico.append(self._tela_atual)  # Salva a tela atual no histórico

        antiga = self._tela_atual                     # Guarda a tela que está saindo
        self._tela_atual = nome                       # Atualiza a tela atual
        nova_tela = self._telas[nome]                 # Pega a nova tela do dicionário

        if antiga:                                    # Se tinha uma tela antes
            # Anima a transição deslizando da esquerda para a direita
            self._animar_slide(self._telas[antiga], nova_tela, direcao="esquerda")
        else:                                         # Primeira tela (sem animação)
            nova_tela.place(relx=0, rely=0, relwidth=1, relheight=1)  # Mostra a tela
            nova_tela.lift()                          # Coloca na frente

        # Chama _ao_visitar APÓS a tela estar visível
        if hasattr(nova_tela, '_ao_visitar'):
            nova_tela.after(50, nova_tela._ao_visitar)

    def voltar(self):
        """Volta para a tela anterior (usando o histórico)."""
        if self._animando:                            # Bloqueia se estiver animando
            return

        if not self._historico:                       # Se não tem histórico, não volta
            return

        anterior = self._historico.pop()              # Remove e pega a última tela do histórico
        antiga = self._tela_atual                     # Tela atual que vai sair
        self._tela_atual = anterior                   # Atualiza para a tela anterior
        tela_volta = self._telas[anterior]            # Pega o frame da tela anterior

        if antiga:                                    # Se tinha uma tela na frente
            # Anima a transição deslizando da direita para a esquerda (volta)
            self._animar_slide(self._telas[antiga], tela_volta, direcao="direita")
        else:                                         # Sem animação
            tela_volta.place(relx=0, rely=0, relwidth=1, relheight=1)
            tela_volta.lift()

        # Chama _ao_visitar APÓS a tela estar visível
        if hasattr(tela_volta, '_ao_visitar'):
            tela_volta.after(50, tela_volta._ao_visitar)

    def voltar_ao_inicio(self):
        """Volta para a tela de login e limpa o histórico."""
        self._historico.clear()                       # Limpa todo o histórico de navegação
        self.navegar_para("login", voltavel=False)    # Navega para o login sem salvar no histórico

    def _animar_slide(self, saindo, entrando, direcao="esquerda", duracao=250):
        """Anima a transição entre telas com efeito de deslize."""
        self._animando = True                         # Marca que está animando (bloqueia cliques)
        saindo.update_idletasks()                     # Atualiza medições da tela saindo
        largura = saindo.winfo_width()                # Largura da tela (para calcular o deslocamento)

        if direcao == "esquerda":                     # Animação para frente (esquerda)
            x_inicio_nova = largura                   # Nova tela começa fora, à direita
            x_fim_nova = 0                           # Nova tela termina no centro
            x_inicio_velha = 0                       # Tela antiga começa no centro
            x_fim_velha = -largura                   # Tela antiga termina fora, à esquerda
        else:                                         # Animação para trás (direita)
            x_inicio_nova = -largura                  # Nova tela começa fora, à esquerda
            x_fim_nova = 0                           # Nova tela termina no centro
            x_inicio_velha = 0                       # Tela antiga começa no centro
            x_fim_velha = largura                    # Tela antiga termina fora, à direita

        entrando.place(relx=0, rely=0, relwidth=1, relheight=1)  # Mostra a tela entrando
        entrando.place_configure(x=x_inicio_nova)    # Posiciona fora da tela
        entrando.lift()                              # Coloca na frente

        passos = 15                                  # Número de quadros da animação
        intervalo = max(duracao // passos, 1)        # Tempo entre cada quadro (em ms)

        # Inicia a animação passo a passo
        self._animar_passo(
            saindo, entrando,
            x_inicio_velha, x_fim_velha,             # Posições da tela saindo
            x_inicio_nova, x_fim_nova,               # Posições da tela entrando
            0, passos, intervalo                     # Passo atual, total, intervalo
        )

    def _animar_passo(self, saindo, entrando, x_sv, x_fv, x_sn, x_fn, passo, total, intervalo):
        """Executa um quadro da animação de transição."""
        if passo >= total:                            # Se chegou ao último passo
            saindo.place_forget()                     # Esconde a tela que saiu
            entrando.place(relx=0, rely=0, relwidth=1, relheight=1)  # Posiciona a nova tela
            self._animando = False                    # Libera a navegação
            return                                    # Fim da animação

        t = (passo + 1) / total                      # Progresso da animação (0.0 a 1.0)
        t_suave = self._ease_out_cubic(t)             # Aplica suavização (ease-out)

        x_velha = x_sv + (x_fv - x_sv) * t_suave    # Calcula posição da tela saindo
        x_nova = x_sn + (x_fn - x_sn) * t_suave     # Calcula posição da tela entrando

        saindo.place_configure(x=int(x_velha))       # Move a tela saindo
        entrando.place_configure(x=int(x_nova))      # Move a tela entrando

        # Agenda o próximo passo da animação
        self.root.after(intervalo, lambda: self._animar_passo(
            saindo, entrando, x_sv, x_fv, x_sn, x_fn,
            passo + 1, total, intervalo
        ))

    def _ease_out_cubic(self, t):
        """Função de suavização que desacelera no final (ease-out cúbico)."""
        return 1 - (1 - t) ** 3                     # Fórmula: começa rápido, termina devagar
