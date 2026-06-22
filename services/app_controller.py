import customtkinter as ctk
from services.styles import COR_BG


class AppController:
    def __init__(self, root):
        self.root = root
        self.root.title("LUMEN")
        self.root.geometry("960x680")
        self.root.minsize(800, 580)
        self.root.configure(fg_color=COR_BG)

        self._container = ctk.CTkFrame(root, fg_color=COR_BG)
        self._container.pack(fill="both", expand=True)

        self._telas = {}
        self._tela_atual = None
        self._historico = []
        self._animando = False

        self._centralizar()

    def _centralizar(self):
        self.root.update_idletasks()
        L = self.root.winfo_width()
        A = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - L) // 2
        y = (self.root.winfo_screenheight() - A) // 2
        self.root.geometry(f"+{x}+{y}")

    def registrar_tela(self, nome, classe_tela):
        frame = classe_tela(master=self._container, controller=self)
        self._telas[nome] = frame
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        frame.place_forget()

    def navegar_para(self, nome, voltavel=True):
        if self._animando:
            return

        if self._tela_atual and self._tela_atual == nome:
            return

        if voltavel and self._tela_atual:
            self._historico.append(self._tela_atual)

        antiga = self._tela_atual
        self._tela_atual = nome
        nova_tela = self._telas[nome]

        if hasattr(nova_tela, '_ao_visitar'):
            nova_tela._ao_visitar()

        if antiga:
            self._animar_slide(self._telas[antiga], nova_tela, direcao="esquerda")
        else:
            nova_tela.place(relx=0, rely=0, relwidth=1, relheight=1)
            nova_tela.lift()

    def voltar(self):
        if self._animando:
            return

        if not self._historico:
            return

        anterior = self._historico.pop()
        antiga = self._tela_atual
        self._tela_atual = anterior
        tela_volta = self._telas[anterior]

        if hasattr(tela_volta, '_ao_visitar'):
            tela_volta._ao_visitar()

        if antiga:
            self._animar_slide(self._telas[antiga], tela_volta, direcao="direita")
        else:
            tela_volta.place(relx=0, rely=0, relwidth=1, relheight=1)
            tela_volta.lift()

    def voltar_ao_inicio(self):
        self._historico.clear()
        self.navegar_para("login", voltavel=False)

    def _animar_slide(self, saindo, entrando, direcao="esquerda", duracao=250):
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
            0, passos, intervalo
        )

    def _animar_passo(self, saindo, entrando, x_sv, x_fv, x_sn, x_fn, passo, total, intervalo):
        if passo >= total:
            saindo.place_forget()
            entrando.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._animando = False
            return

        t = (passo + 1) / total
        t_suave = self._ease_out_cubic(t)

        x_velha = x_sv + (x_fv - x_sv) * t_suave
        x_nova = x_sn + (x_fn - x_sn) * t_suave

        saindo.place_configure(x=int(x_velha))
        entrando.place_configure(x=int(x_nova))

        self.root.after(intervalo, lambda: self._animar_passo(
            saindo, entrando, x_sv, x_fv, x_sn, x_fn,
            passo + 1, total, intervalo
        ))

    def _ease_out_cubic(self, t):
        return 1 - (1 - t) ** 3
