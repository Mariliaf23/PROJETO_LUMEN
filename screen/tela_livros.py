import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import (
    cadastrar_livro, listar_livros, excluir_livro,
    listar_categorias, cadastrar_categoria
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    criar_entry, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame, criar_combo
)

class TelaLivros(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._itens_lista = []
        self._selecionado = None
        self._cat_map = {}
        self._construir_ui()

    def _ao_visitar(self):
        self._carregar_categorias()
        self._carregar_tabela()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === HEADER COM LOGO AUMENTADA ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 15))

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")
        
        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y")

        # Logo expandida para 85x85 para destaque máximo no topo
        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(180, 180))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")

        criar_label(header_left, "|  Catálogo de Livros", font=("Segoe UI", 26, "bold"), text_color=COR_TEXTO).pack(side="left")

        # Botão voltar azul escuro sólido com texto branco
        btn_voltar = ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=130, height=45,
            fg_color="#0F172A", text_color="#FFFFFF", border_color=COR_INPUT_BORDER, border_width=1,
            hover_color="#1E293B", font=("Segoe UI", 16, "bold")
        )
        btn_voltar.pack(side="right")

        # === FORMULÁRIO DE CADASTRO ===
        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 15))

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=25, pady=25)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        # Inputs com altura confortável e texto grande (16px)
        self.entry_titulo = criar_entry(form_frame, placeholder="Título do Livro", height=50)
        self.entry_titulo.configure(font=("Segoe UI", 16))
        self.entry_titulo.grid(row=0, column=0, padx=(0, 15), pady=12, sticky="ew")

        self.entry_isbn = criar_entry(form_frame, placeholder="ISBN", height=50)
        self.entry_isbn.configure(font=("Segoe UI", 16))
        self.entry_isbn.grid(row=0, column=1, padx=(15, 0), pady=12, sticky="ew")

        # Categoria + Botão [+] em Azul
        cat_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        cat_frame.grid(row=1, column=0, padx=(0, 15), pady=12, sticky="ew")
        cat_frame.grid_columnconfigure(0, weight=1)

        self.combo_categoria = criar_combo(cat_frame, height=50, values=[])
        self.combo_categoria.configure(font=("Segoe UI", 16))
        self.combo_categoria.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        btn_add_cat = ctk.CTkButton(
            cat_frame, text="+", width=50, height=50,
            fg_color="#0052CC", text_color="#FFFFFF", # Azul Puro com Texto Branco
            hover_color="#003399", font=("Segoe UI", 24, "bold"),
            command=self._adicionar_categoria
        )
        btn_add_cat.grid(row=0, column=1)

        self.entry_editora = criar_entry(form_frame, placeholder="Editora", height=50)
        self.entry_editora.configure(font=("Segoe UI", 16))
        self.entry_editora.grid(row=1, column=1, padx=(15, 0), pady=12, sticky="ew")

        self.entry_ano = criar_entry(form_frame, placeholder="Ano de Publicação", height=50)
        self.entry_ano.configure(font=("Segoe UI", 16))
        self.entry_ano.grid(row=2, column=0, padx=(0, 15), pady=12, sticky="ew")

        self.entry_sinopse = criar_entry(form_frame, placeholder="Sinopse / Observações (opcional)", height=50)
        self.entry_sinopse.configure(font=("Segoe UI", 16))
        self.entry_sinopse.grid(row=2, column=1, padx=(15, 0), pady=12, sticky="ew")

        # Botões Principais de Ação (Ajustados para Azul Sólido Profundo)
        botoes_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_container.grid(row=3, column=0, columnspan=2, pady=(25, 0))

        self.btn_cadastrar = ctk.CTkButton(
            botoes_container, text="Cadastrar Título", command=self._cadastrar,
            width=240, height=50, 
            fg_color="#0052CC", text_color="#FFFFFF", # AZUL PURU SÓLIDO (Sem tom pastel)
            hover_color="#003399", font=("Segoe UI", 16, "bold")
        )
        self.btn_cadastrar.pack(side="left", padx=15)

        self.btn_excluir = ctk.CTkButton(
            botoes_container, text="Excluir Selecionado", command=self._excluir_selecionado,
            width=240, height=50, 
            fg_color="#7F1D1D", text_color="#FCA5A5", # Vermelho Sólido Fechado
            hover_color="#991B1B", font=("Segoe UI", 16, "bold")
        )
        self.btn_excluir.pack(side="left", padx=15)

        # === LISTA / TABELA ===
        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 25))

        self._proporcoes = [0.30, 0.18, 0.15, 0.15, 0.08, 0.14]
        colunas = ["Título", "ISBN", "Categoria", "Editora", "Ano", "Status"]

        header_tab = ctk.CTkFrame(lista_card, fg_color="transparent", height=45)
        header_tab.pack(fill="x", padx=20, pady=(15, 5))
        header_tab.pack_propagate(False)

        for i, (nome, pct) in enumerate(zip(colunas, self._proporcoes)):
            rel_x = sum(self._proporcoes[:i])
            lbl = ctk.CTkLabel(header_tab, text=nome.upper(), font=("Segoe UI", 14, "bold"), text_color=COR_DOURADO, anchor="w")
            lbl.place(relx=rel_x, rely=0.5, anchor="w", relwidth=pct-0.01)

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

    def _carregar_categorias(self):
        cats = listar_categorias()
        valores = [c[1] for c in cats]
        self._cat_map = {c[1]: c[0] for c in cats}
        self.combo_categoria.configure(values=valores)
        if valores: self.combo_categoria.set(valores[0])
        else: self.combo_categoria.set("Categoria")

    def _adicionar_categoria(self):
        dialog = ctk.CTkInputDialog(text="Nova Categoria:", title="Lumen System")
        nome = dialog.get_input()
        if nome and nome.strip():
            cadastrar_categoria(nome.strip())
            self._carregar_categorias()

    def _carregar_tabela(self):
        for widget in self.lista_frame.winfo_children(): widget.destroy()
        self._itens_lista.clear()
        livros = listar_livros()
        for livro in livros: self._criar_item(livro)

    def _criar_item(self, livro):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=6, height=48)
        item.pack(fill="x", pady=4)
        item.pack_propagate(False)

        item.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))

        dados = livro[1:] if len(livro) > 6 else livro

        for i, pct in enumerate(self._proporcoes):
            if i < len(dados):
                texto = dados[i]
                rel_x = sum(self._proporcoes[:i])
                
                cor_txt = COR_TEXTO
                if i == 5: 
                    status = str(texto).lower()
                    cor_txt = COR_DOURADO if "dispon" in status else COR_TEXTO2

                lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 15), text_color=cor_txt, anchor="w")
                lbl.place(relx=rel_x + 0.005, rely=0.5, anchor="w", relwidth=pct-0.01)
                lbl.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))

        self._itens_lista.append((item, livro))

    def _selecionar(self, livro):
        for item, l in self._itens_lista:
            # Highlight azul marinho profundo ao selecionar a linha
            item.configure(fg_color="#0F172A" if l == livro else COR_CARD)
        self._selecionado = livro

    def _cadastrar(self):
        titulo = self.entry_titulo.get().strip()
        isbn = self.entry_isbn.get().strip()
        cat_nome = self.combo_categoria.get()
        editora = self.entry_editora.get().strip()
        ano = self.entry_ano.get().strip()
        sinopse = self.entry_sinopse.get().strip()

        if not titulo or not isbn or cat_nome == "Categoria":
            self._notificar("Preencha os campos obrigatórios (*)")
            return

        id_categoria = self._cat_map.get(cat_nome)
        ano_pub = int(ano) if ano.isdigit() else None

        self.btn_cadastrar.configure(text="Processando...", state="disabled")
        self.after(400, lambda: self._salvar(titulo, isbn, id_categoria, editora, ano_pub, sinopse))

    def _salvar(self, t, i, c, e, a, s):
        if cadastrar_livro(t, i, c, e, a, s):
            self._notificar("Livro catalogado com sucesso!")
            self._limpar_campos()
            self._carregar_tabela()
        else:
            self._notificar("Erro: ISBN já existe no sistema.")
        self.btn_cadastrar.configure(text="Cadastrar Título", state="normal")

    def _excluir_selecionado(self):
        if not self._selecionado:
            self._notificar("Selecione um item na lista.")
            return
        if excluir_livro(self._selecionado[0]):
            self._notificar("Registro removido.")
            self._selecionado = None
            self._carregar_tabela()
        else:
            self._notificar("Erro ao excluir registro.")

    def _limpar_campos(self):
        for e in [self.entry_titulo, self.entry_isbn, self.entry_editora, self.entry_ano, self.entry_sinopse]:
            e.delete(0, "end")

    def _voltar(self):
        if self.controller: self.controller.voltar()

    def _notificar(self, msg):
        self.lbl_notificacao.configure(text=msg, text_color=COR_DOURADO, font=("Segoe UI", 15, "bold"))
        self.lbl_notificacao.place(relx=0.5, rely=0.96, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))