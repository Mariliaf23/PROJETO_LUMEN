import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import (
    cadastrar_livro, listar_livros, excluir_livro,
    listar_categorias, cadastrar_categoria
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_entry, criar_botao_preenchido, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame, criar_combo
)


class TelaLivros(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._itens_lista = []
        self._selecionado = None
        self._construir_ui()

    def _ao_visitar(self):
        self._carregar_categorias()
        self._carregar_tabela()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        criar_titulo(header, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left")
        criar_label(header, "Catalogo de Livros", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(side="left", padx=(15, 0))

        btn_voltar = criar_botao(header, text="Voltar", command=self._voltar, width=100, height=35)
        btn_voltar.pack(side="right")

        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))
        form_card.grid_columnconfigure((0, 1), weight=1)

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=15)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        self.entry_titulo = criar_entry(form_frame, placeholder="Titulo", height=38)
        self.entry_titulo.grid(row=0, column=0, padx=(0, 10), pady=3, sticky="ew")

        self.entry_isbn = criar_entry(form_frame, placeholder="ISBN", height=38)
        self.entry_isbn.grid(row=0, column=1, padx=(10, 0), pady=3, sticky="ew")

        self.combo_categoria = criar_combo(form_frame, width=200, height=38, values=[])
        self.combo_categoria.grid(row=1, column=0, padx=(0, 10), pady=3, sticky="ew")
        self.combo_categoria.set("Categoria")

        btn_add_cat = ctk.CTkButton(
            form_frame, text="+", width=38, height=38,
            fg_color=COR_DOURADO, text_color=COR_BG,
            hover_color="#c9a96c", command=self._adicionar_categoria
        )
        btn_add_cat.grid(row=1, column=1, padx=(10, 0), pady=3, sticky="e")

        self.entry_editora = criar_entry(form_frame, placeholder="Editora", height=38)
        self.entry_editora.grid(row=2, column=0, padx=(0, 10), pady=3, sticky="ew")

        self.entry_ano = criar_entry(form_frame, placeholder="Ano publicacao", height=38)
        self.entry_ano.grid(row=2, column=1, padx=(10, 0), pady=3, sticky="ew")

        self.entry_sinopse = criar_entry(form_frame, placeholder="Sinopse (opcional)", height=38)
        self.entry_sinopse.grid(row=3, column=0, columnspan=2, pady=3, sticky="ew")

        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.grid(row=4, column=0, columnspan=2, pady=(8, 0))

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

        for col, txt in [("Titulo", 0.3), ("ISBN", 0.15), ("Categoria", 0.15), ("Editora", 0.15), ("Ano", 0.08), ("Status", 0.1)]:
            criar_label(header_lista, txt, font=("Segoe UI", 10, "bold"), text_color=COR_DOURADO).pack(side="left", expand=True, fill="x")

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

    def _carregar_categorias(self):
        cats = listar_categorias()
        valores = [c[1] for c in cats]
        self._cat_map = {c[1]: c[0] for c in cats}
        self.combo_categoria.configure(values=valores)
        if valores:
            self.combo_categoria.set(valores[0])

    def _adicionar_categoria(self):
        dialog = ctk.CTkInputDialog(text="Nome da nova categoria:", title="Nova Categoria")
        nome = dialog.get_input()
        if nome and nome.strip():
            cadastrar_categoria(nome.strip())
            self._carregar_categorias()

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

        colunas = [0.3, 0.15, 0.15, 0.15, 0.08, 0.1]
        for i, (texto, pct) in enumerate(zip(livro, colunas)):
            lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 10), text_color=COR_TEXTO, anchor="w")
            lbl.place(relx=sum(colunas[:i]) + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
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
        isbn = self.entry_isbn.get().strip()
        cat_nome = self.combo_categoria.get()
        editora = self.entry_editora.get().strip()
        ano = self.entry_ano.get().strip()
        sinopse = self.entry_sinopse.get().strip()

        if not titulo:
            self._notificar("Informe o titulo do livro.")
            return
        if not isbn:
            self._notificar("Informe o ISBN do livro.")
            return
        if not cat_nome or cat_nome not in self._cat_map:
            self._notificar("Selecione uma categoria valida.")
            return

        id_categoria = self._cat_map[cat_nome]
        ano_pub = int(ano) if ano.isdigit() else None

        self.btn_cadastrar.configure(text="Cadastrando...", state="disabled")
        self.after(500, lambda: self._salvar(titulo, isbn, id_categoria, editora, ano_pub, sinopse))

    def _salvar(self, titulo, isbn, id_categoria, editora, ano_pub, sinopse):
        sucesso = cadastrar_livro(titulo, isbn, id_categoria, editora, ano_pub, sinopse)
        if sucesso:
            self._notificar("Livro cadastrado com sucesso!")
            self._limpar_campos()
            self._carregar_tabela()
        else:
            self._notificar("Erro ao cadastrar livro (ISBN duplicado?).")
        self.btn_cadastrar.configure(text="Cadastrar Livro", state="normal")

    def _excluir_selecionado(self):
        if not self._selecionado:
            self._notificar("Selecione um livro para excluir.")
            return
        id_livro = self._selecionado[0]
        sucesso = excluir_livro(id_livro)
        if sucesso:
            self._notificar("Livro excluido.")
            self._selecionado = None
            self._carregar_tabela()
        else:
            self._notificar("Erro ao excluir livro.")

    def _limpar_campos(self):
        for entry in [self.entry_titulo, self.entry_isbn, self.entry_editora, self.entry_ano, self.entry_sinopse]:
            entry.delete(0, "end")

    def _voltar(self):
        self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))
