import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import (
    listar_livros, listar_exemplares, cadastrar_exemplar,
    excluir_exemplar, atualizar_status_exemplar
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_entry, criar_botao_preenchido, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame, criar_combo
)


class TelaExemplares(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._itens_lista = []
        self._selecionado = None
        self._construir_ui()

    def _ao_visitar(self):
        self._carregar_livros()
        self._carregar_tabela()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        criar_titulo(header, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left")
        criar_label(header, "Gerenciar Exemplares", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(side="left", padx=(15, 0))

        btn_voltar = criar_botao(header, text="Voltar", command=self._voltar, width=100, height=35)
        btn_voltar.pack(side="right")

        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=15)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        criar_label(form_frame, "Livro", font=FONTE_LABEL).grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.combo_livro = criar_combo(form_frame, width=300, height=38, values=[])
        self.combo_livro.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        self.combo_livro.set("Selecione o livro")

        self.entry_patrimonio = criar_entry(form_frame, placeholder="Codigo patrimonio", height=38)
        self.entry_patrimonio.grid(row=1, column=1, padx=(10, 0), sticky="ew")

        self.entry_localizacao = criar_entry(form_frame, placeholder="Localizacao (estante, prateleira)", height=38)
        self.entry_localizacao.grid(row=2, column=0, padx=(0, 10), pady=(8, 0), sticky="ew")

        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.grid(row=2, column=1, padx=(10, 0), pady=(8, 0), sticky="ew")

        self.btn_adicionar = criar_botao_preenchido(
            botoes_frame, text="Adicionar Exemplar", command=self._adicionar,
            width=180, height=38
        )
        self.btn_adicionar.pack(side="left", padx=(0, 10))

        self.btn_excluir = criar_botao(
            botoes_frame, text="Excluir Selecionado", command=self._excluir_selecionado,
            width=160, height=38, border_color="#8a4040", text_color="#8a4040"
        )
        self.btn_excluir.pack(side="left")

        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 20))

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_lista.pack(fill="x", padx=15, pady=(10, 5))

        for col, txt in [("Patrimonio", 0.2), ("Livro", 0.3), ("Status", 0.15), ("Localizacao", 0.2)]:
            criar_label(header_lista, txt, font=("Segoe UI", 10, "bold"), text_color=COR_DOURADO).pack(side="left", expand=True, fill="x")

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

    def _carregar_livros(self):
        livros = listar_livros()
        self._livros_map = {}
        valores = []
        for l in livros:
            texto = f"{l[1]} ({l[2]})"
            valores.append(texto)
            self._livros_map[texto] = l[0]
        self.combo_livro.configure(values=valores)
        if valores:
            self.combo_livro.set(valores[0])

    def _carregar_tabela(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        self._itens_lista.clear()

        exemplares = listar_exemplares()
        for exc in exemplares:
            self._criar_item(exc)

        if not exemplares:
            empty = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
            empty.pack(fill="both", expand=True)
            criar_label(empty, "Nenhum exemplar cadastrado", font=FONTE_LABEL).pack(expand=True)

    def _criar_item(self, exc):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=8, height=42)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)

        item.bind("<Button-1>", lambda e, v=exc: self._selecionar(v))
        for child in item.winfo_children():
            child.bind("<Button-1>", lambda e, v=exc: self._selecionar(v))

        colunas = [0.2, 0.3, 0.15, 0.2]
        for i, (texto, pct) in enumerate(zip(exc, colunas)):
            cor = COR_TEXTO
            if i == 2:
                if texto == "emprestado":
                    cor = "#d4b896"
                elif texto == "manutencao":
                    cor = "#8a4040"
            lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 10), text_color=cor, anchor="w")
            lbl.place(relx=sum(colunas[:i]) + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            lbl.bind("<Button-1>", lambda e, v=exc: self._selecionar(v))

        self._itens_lista.append((item, exc))

    def _selecionar(self, exc):
        for item, e in self._itens_lista:
            if e == exc:
                item.configure(fg_color="#2a1a08")
            else:
                item.configure(fg_color=COR_CARD)
        self._selecionado = exc

    def _adicionar(self):
        livro_sel = self.combo_livro.get()
        patrimonio = self.entry_patrimonio.get().strip()
        localizacao = self.entry_localizacao.get().strip()

        if not livro_sel or livro_sel not in self._livros_map:
            self._notificar("Selecione um livro valido.")
            return
        if not patrimonio:
            self._notificar("Informe o codigo de patrimonio.")
            return

        id_livro = self._livros_map[livro_sel]

        self.btn_adicionar.configure(text="Adicionando...", state="disabled")
        self.after(500, lambda: self._salvar(patrimonio, id_livro, localizacao))

    def _salvar(self, patrimonio, id_livro, localizacao):
        sucesso = cadastrar_exemplar(patrimonio, id_livro, localizacao)
        if sucesso:
            self._notificar("Exemplar adicionado com sucesso!")
            self.entry_patrimonio.delete(0, "end")
            self.entry_localizacao.delete(0, "end")
            self._carregar_tabela()
        else:
            self._notificar("Erro (patrimonio duplicado?).")
        self.btn_adicionar.configure(text="Adicionar Exemplar", state="normal")

    def _excluir_selecionado(self):
        if not self._selecionado:
            self._notificar("Selecione um exemplar para excluir.")
            return
        id_exc = self._selecionado[0]
        status = self._selecionado[2]
        if status == "emprestado":
            self._notificar("Nao e possivel excluir exemplar emprestado.")
            return
        sucesso = excluir_exemplar(id_exc)
        if sucesso:
            self._notificar("Exemplar excluido.")
            self._selecionado = None
            self._carregar_tabela()
        else:
            self._notificar("Erro ao excluir exemplar.")

    def _voltar(self):
        self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))
