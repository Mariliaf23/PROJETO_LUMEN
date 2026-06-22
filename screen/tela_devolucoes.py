import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.conector import init_db
from services.database_config import (
    listar_emprestimos_ativos, finalizar_emprestimo
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_botao_preenchido, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame
)
from services.transitions import transicao_sair


class TelaDevolucoes(ctk.CTkToplevel):
    def __init__(self, master=None, maximizado=False):
        super().__init__(master)
        init_db()
        self.title("LUMEN - Devolucoes")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=COR_BG)
        if maximizado:
            self.after(10, self.state, "zoomed")

        self.after(100, self.lift)
        self._itens_lista = []
        self._selecionado = None
        self._construir_ui()
        self._carregar_tabela()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        criar_titulo(header, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left")
        criar_label(header, "Devolucoes Pendentes", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(side="left", padx=(15, 0))

        btn_voltar = criar_botao(header, text="Voltar", command=self._voltar, width=100, height=35)
        btn_voltar.pack(side="right")

        acoes_card = criar_card(self)
        acoes_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        acoes_frame = ctk.CTkFrame(acoes_card, fg_color="transparent")
        acoes_frame.pack(fill="x", padx=20, pady=15)

        self.btn_devolver = criar_botao_preenchido(
            acoes_frame, text="Registrar Devolucao", command=self._devolver,
            width=220, height=42
        )
        self.btn_devolver.pack(side="left")

        criar_label(acoes_frame, "Selecione um emprestimo na lista abaixo", font=FONTE_LABEL).pack(side="left", padx=(20, 0))

        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 20))

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_lista.pack(fill="x", padx=15, pady=(10, 5))

        for col, txt in [("ID", 0.06), ("Aluno", 0.24), ("Livro", 0.3), ("Emprestimo", 0.15), ("Vencimento", 0.15), ("Status", 0.1)]:
            criar_label(header_lista, txt, font=("Segoe UI", 10, "bold"), text_color=COR_DOURADO).pack(side="left", expand=True, fill="x")

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

    def _carregar_tabela(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        self._itens_lista.clear()

        emprestimos = listar_emprestimos_ativos()
        for emp in emprestimos:
            self._criar_item(emp)

        if not emprestimos:
            empty = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
            empty.pack(fill="both", expand=True)
            criar_label(empty, "Nenhuma devolucao pendente", font=FONTE_LABEL).pack(expand=True)

    def _criar_item(self, emp):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=8, height=42)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)

        item.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))

        colunas = [0.06, 0.24, 0.3, 0.15, 0.15, 0.1]
        x = 0
        for i, (texto, pct) in enumerate(zip(emp, colunas)):
            cor = COR_TEXTO
            if i == 5 and str(texto) == "ativo":
                cor = "#d4b896"
            lbl = ctk.CTkLabel(item, text=str(texto), font=("Segoe UI", 10), text_color=cor, anchor="w")
            lbl.place(relx=x + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            lbl.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))
            x += pct

        self._itens_lista.append((item, emp))

    def _selecionar(self, emp):
        for item, e in self._itens_lista:
            if e == emp:
                item.configure(fg_color="#2a1a08")
            else:
                item.configure(fg_color=COR_CARD)
        self._selecionado = emp

    def _devolver(self):
        if not self._selecionado:
            self._notificar("Selecione um emprestimo para devolver.")
            return
        emp_id = self._selecionado[0]
        self.btn_devolver.configure(text="Processando...", state="disabled")
        self.after(500, lambda: self._processar_devolucao(emp_id))

    def _processar_devolucao(self, emp_id):
        sucesso = finalizar_emprestimo(emp_id)
        if sucesso:
            self._notificar("Devolucao registrada com sucesso!")
            self._selecionado = None
            self._carregar_tabela()
        else:
            self._notificar("Erro ao registrar devolucao.")
        self.btn_devolver.configure(text="Registrar Devolucao", state="normal")

    def _voltar(self):
        transicao_sair(self, callback=self.destroy)

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = TelaDevolucoes(master=root)
    app.mainloop()
    root.destroy()
