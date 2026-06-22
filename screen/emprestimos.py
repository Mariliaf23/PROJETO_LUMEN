import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.conector import init_db
from services.database_config import (
    cadastrar_emprestimo, listar_emprestimos, finalizar_emprestimo,
    listar_alunos, listar_livros_disponiveis
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_entry, criar_botao_preenchido, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame, criar_combo
)
from services.transitions import transicao_sair


class TelaEmprestimos(ctk.CTkToplevel):
    def __init__(self, master=None, maximizado=False):
        super().__init__(master)
        init_db()
        self.title("LUMEN - Emprestimos")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=COR_BG)
        if maximizado:
            self.after(10, self.state, "zoomed")

        self.after(100, self.lift)
        self._itens_lista = []
        self._selecionado = None
        self._construir_ui()
        self._carregar_dados()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        criar_titulo(header, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left")
        criar_label(header, "Emprestimos", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(side="left", padx=(15, 0))

        btn_voltar = criar_botao(header, text="Voltar", command=self._voltar, width=100, height=35)
        btn_voltar.pack(side="right")

        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=15)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        criar_label(form_frame, "Aluno", font=FONTE_LABEL).grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.combo_aluno = criar_combo(form_frame, width=280, height=38)
        self.combo_aluno.grid(row=1, column=0, padx=(0, 10), sticky="ew")

        criar_label(form_frame, "Livro", font=FONTE_LABEL).grid(row=0, column=1, sticky="w", pady=(0, 3))
        self.combo_livro = criar_combo(form_frame, width=280, height=38)
        self.combo_livro.grid(row=1, column=1, padx=(10, 0), sticky="ew")

        criar_label(form_frame, "Vencimento (AAAA-MM-DD)", font=FONTE_LABEL).grid(row=2, column=0, sticky="w", pady=(10, 3))
        self.entry_vencimento = criar_entry(form_frame, placeholder="AAAA-MM-DD", height=38)
        self.entry_vencimento.grid(row=3, column=0, padx=(0, 10), sticky="ew")

        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.grid(row=3, column=1, padx=(10, 0), sticky="ew")

        self.btn_cadastrar = criar_botao_preenchido(
            botoes_frame, text="Novo Emprestimo", command=self._cadastrar,
            width=160, height=38
        )
        self.btn_cadastrar.pack(side="left", padx=(0, 10))

        self.btn_finalizar = criar_botao(
            botoes_frame, text="Finalizar", command=self._finalizar,
            width=120, height=38, border_color="#4a8a4a", text_color="#4a8a4a"
        )
        self.btn_finalizar.pack(side="left")

        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 20))

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_lista.pack(fill="x", padx=15, pady=(10, 5))

        for col, txt in [("ID", 0.06), ("Aluno", 0.24), ("Livro", 0.3), ("Emprestimo", 0.15), ("Vencimento", 0.15), ("Status", 0.1)]:
            criar_label(header_lista, txt, font=("Segoe UI", 10, "bold"), text_color=COR_DOURADO).pack(side="left", expand=True, fill="x")

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

    def _carregar_dados(self):
        alunos = listar_alunos()
        self._alunos_map = {}
        if alunos:
            valores = [f"{a[0]} - {a[1]}" for a in alunos]
            self.combo_aluno.configure(values=valores)
            self.combo_aluno.set(valores[0])
            self._alunos_map = {f"{a[0]} - {a[1]}": a[0] for a in alunos}

        livros = listar_livros_disponiveis()
        self._livros_map = {}
        if livros:
            valores = [f"{l[0]} - {l[1]}" for l in livros]
            self.combo_livro.configure(values=valores)
            self.combo_livro.set(valores[0])
            self._livros_map = {f"{l[0]} - {l[1]}": l[0] for l in livros}

        self._carregar_tabela()

    def _carregar_tabela(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        self._itens_lista.clear()

        emprestimos = listar_emprestimos()
        for emp in emprestimos:
            self._criar_item(emp)

    def _criar_item(self, emp):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=8, height=40)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)

        item.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))

        colunas = [0.06, 0.24, 0.3, 0.15, 0.15, 0.1]
        x = 0
        for i, (texto, pct) in enumerate(zip(emp, colunas)):
            lbl = ctk.CTkLabel(item, text=str(texto), font=("Segoe UI", 10), text_color=COR_TEXTO, anchor="w")
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

    def _cadastrar(self):
        aluno_sel = self.combo_aluno.get()
        livro_sel = self.combo_livro.get()
        vencimento = self.entry_vencimento.get().strip()

        if not aluno_sel or not self._alunos_map:
            self._notificar("Selecione um aluno.")
            return
        if not livro_sel or not self._livros_map:
            self._notificar("Selecione um livro disponivel.")
            return
        if not vencimento:
            self._notificar("Informe a data de vencimento.")
            return

        aluno_id = self._alunos_map.get(aluno_sel)
        livro_id = self._livros_map.get(livro_sel)

        self.btn_cadastrar.configure(text="Criando...", state="disabled")
        self.after(500, lambda: self._salvar(aluno_id, livro_id, vencimento))

    def _salvar(self, aluno_id, livro_id, vencimento):
        sucesso = cadastrar_emprestimo(aluno_id, livro_id, vencimento)
        if sucesso:
            self._notificar("Emprestimo realizado!")
            self.entry_vencimento.delete(0, "end")
            self._carregar_dados()
        else:
            self._notificar("Erro ao criar emprestimo.")
        self.btn_cadastrar.configure(text="Novo Emprestimo", state="normal")

    def _finalizar(self):
        if not self._selecionado:
            self._notificar("Selecione um emprestimo.")
            return
        emp_id = self._selecionado[0]
        sucesso = finalizar_emprestimo(emp_id)
        if sucesso:
            self._notificar("Emprestimo finalizado!")
            self._selecionado = None
            self._carregar_dados()
        else:
            self._notificar("Erro ao finalizar emprestimo.")

    def _voltar(self):
        transicao_sair(self, callback=self.destroy)

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = TelaEmprestimos(master=root)
    app.mainloop()
    root.destroy()
