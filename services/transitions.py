import customtkinter as ctk


class FadeTransition:
    def __init__(self, janela, direcao="entrar", duracao=150, callback=None):
        self.janela = janela
        self.direcao = direcao
        self.duracao = duracao
        self.callback = callback
        self._pasos = 8
        self._intervalo = duracao // self._pasos
        self._atual = 0
        self._alpha_inicial = 0.0 if direcao == "entrar" else 1.0
        self._alpha_final = 1.0 if direcao == "entrar" else 0.0

        self.janela.attributes("-alpha", self._alpha_inicial)
        self._animar()

    def _animar(self):
        if self._atual >= self._pasos:
            self.janela.attributes("-alpha", self._alpha_final)
            if self.direcao == "sair" and self.callback:
                self.callback()
            return

        progresso = (self._atual + 1) / self._pasos
        alpha = self._alpha_inicial + (self._alpha_final - self._alpha_inicial) * progresso
        self.janela.attributes("-alpha", alpha)
        self._atual += 1
        self.janela.after(self._intervalo, self._animar)


def transicao_sair(janela, callback=None, duracao=150):
    FadeTransition(janela, direcao="sair", duracao=duracao, callback=callback)


def transicao_entrar(janela, duracao=150):
    FadeTransition(janela, direcao="entrar", duracao=duracao)


def navegar_com_transicao(tela_atual, classe_tela, maximizado=False):
    def abrir():
        tela = classe_tela(master=tela_atual.master, maximizado=maximizado)
        tela.wait_window()
        if tela_atual.winfo_exists():
            tela_atual.deiconify()
            transicao_entrar(tela_atual)

    tela_atual.withdraw()
    transicao_entrar(tela_atual, duracao=0)
    tela_atual.after(50, abrir)
