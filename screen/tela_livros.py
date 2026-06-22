import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import (
    cadastrar_livro, listar_livros, excluir_livro
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_entry, criar_botao_preenchido, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame
)


class TelaLivros(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._itens_lista = []
        self._selecionado = None
        self._construir_ui()

    def _ao_visitar(self):
        self._carregar_tabela()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        criar_titulo(header, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left")
        criar_label(header, "Cadastro de Livros", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(side="left", padx=(15, 0))

        btn_voltar = criar_botao(header, text="Voltar", command=self._voltar, width=100, height=35)
        btn_voltar.pack(side="right")

        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))
        form_card.grid_columnconfigure((0, 1), weight=1)

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=15)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        self.entry_titulo = criar_entry(form_frame, placeholder="Titulo", height=38)
        self.entry_titulo.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

        self.entry_autor = criar_entry(form_frame, placeholder="Autor", height=38)
        self.entry_autor.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")

        self.entry_categoria = criar_entry(form_frame, placeholder="Categoria", height=38)
        self.entry_categoria.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="ew")

        self.entry_isbn = criar_entry(form_frame, placeholder="ISBN", height=38)
        self.entry_isbn.grid(row=1, column=1, padx=(10, 0), pady=5, sticky="ew")

        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        self.btn_cadastrar = criar_botao_preenchido(
            botoes_frame, text="Cadastrar Livro", command=self._cadastrar,
            width=180, height=38
        )
        self.btn_cadastrar.pack(side="left", padx=(0, 10))

        self.btn_excluir = criar_botao(
            botoes_frame, text="Excluir Selecionado", command=self._excluir_selecionado,
            width=180, height=38, border_color="#8a4040", text_color="#8a4040"
        )
        self.btn_excluir.pack(side="left")

        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 20))

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_lista.pack(fill="x", padx=15, pady=(10, 5))

        for col, txt in [("Titulo", 0.3), ("Autor", 0.25), ("Categoria", 0.2), ("ISBN", 0.15), ("Status", 0.1)]:
            criar_label(header_lista, txt, font=("Segoe UI", 10, "bold"), text_color=COR_DOURADO).pack(side="left", expand=True, fill="x")

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

    def _carregar_tabela(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        self._itens_lista.clear()

        livros = listar_livros()
        for livro in livros:
            self._criar_item(livro)

    def _criar_item(self, livro):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=8, height=40)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)

        item.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))
        for child in item.winfo_children():
            child.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))

        for i, (texto, pct) in enumerate(zip(livro, [0.3, 0.25, 0.2, 0.15, 0.1])):
            lbl = ctk.CTkLabel(item, text=str(texto), font=("Segoe UI", 10), text_color=COR_TEXTO, anchor="w")
            lbl.place(relx=sum([0.3, 0.25, 0.2, 0.15, 0.1][:i]) + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            lbl.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))

        self._itens_lista.append((item, livro))

    def _selecionar(self, livro):
        for item, l in self._itens_lista:
            if l == livro:
                item.configure(fg_color="#2a1a08")
            else:
                item.configure(fg_color=COR_CARD)
        self._selecionado = livro

    def _cadastrar(self):
        titulo = self.entry_titulo.get().strip()
        autor = self.entry_autor.get().strip()
        categoria = self.entry_categoria.get().strip()
        isbn = self.entry_isbn.get().strip()

        if not titulo:
            self._notificar("Informe o titulo do livro.")
            return
        if not autor:
            self._notificar("Informe o autor do livro.")
            return
        if not isbn:
            self._notificar("Informe o ISBN do livro.")
            return

        self.btn_cadastrar.configure(text="Cadastrando...", state="disabled")
        self.after(500, lambda: self._salvar(titulo, autor, categoria, isbn))

    def _salvar(self, titulo, autor, categoria, isbn):
        sucesso = cadastrar_livro(titulo, autor, categoria, isbn)
        if sucesso:
            self._notificar("Livro cadastrado com sucesso!")
            self._limpar_campos()
            self._carregar_tabela()
        else:
            self._notificar("Erro ao cadastrar livro (ISBN duplicado?).")
        self.btn_cadastrar.configure(text="Cadastrar Livro", state="normal")

    def _excluir_selecionado(self):
        if not hasattr(self, '_selecionado') or not self._selecionado:
            self._notificar("Selecione um livro para excluir.")
            return
        isbn = self._selecionado[3]
        sucesso = excluir_livro(isbn)
        if sucesso:
            self._notificar("Livro excluido.")
            self._selecionado = None
            self._carregar_tabela()
        else:
            self._notificar("Erro ao excluir livro.")

    def _limpar_campos(self):
        for entry in [self.entry_titulo, self.entry_autor, self.entry_categoria, self.entry_isbn]:
            entry.delete(0, "end")

    def _voltar(self):
        self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))
