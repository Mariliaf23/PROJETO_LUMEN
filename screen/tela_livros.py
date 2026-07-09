import os
import sys
import threading
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.book_api import buscar_livro_por_isbn
from services.database_config import (
    cadastrar_livro, listar_livros, excluir_livro, buscar_livro_por_id,
    listar_categorias, cadastrar_categoria,
    listar_autores, listar_autores_livro, associar_autor_livro, desassociar_autor_livro
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    criar_entry, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame, criar_combo
)
from services.validador import validar_isbn

class TelaLivros(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._itens_lista = []
        self._selecionado = None
        self._cat_map = {}
        self._construir_ui()
        self._carregar_categorias()
        self._carregar_tabela()

    def _ao_visitar(self):
        self._carregar_categorias()
        self._carregar_tabela()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === HEADER COMPACTADO (Otimização de Espaço) ===
        header = ctk.CTkFrame(self, fg_color=COR_CARD)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 8))

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y", padx=10, pady=5)

        # Logo reduzida para 55x55 liberando preciosa altura vertical
        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(55, 55))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))

        # Título reduzido de 38 para 24
        criar_label(header_left, "Cadastro de Livros", font=("Segoe UI", 24, "bold"), text_color=COR_TEXTO).pack(side="left")

        # Botão voltar com dimensões mais equilibradas (height=36)
        btn_voltar = ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=100, height=36,
            fg_color="#0F172A", text_color="#FFFFFF", border_color=COR_INPUT_BORDER, border_width=1,
            hover_color="#1E293B", font=("Segoe UI", 14, "bold")
        )
        btn_voltar.pack(side="right", padx=15, pady=5)

        # === FORMULÁRIO DE CADASTRO COMPACTADO ===
        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(5, 10))

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=12)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        # Altura dos inputs reduzida de 50 para 36px. Pady reduzido de 12 para 6.
        ALTURA_INPUT = 36
        FONTE_INPUT = ("Segoe UI", 14)

        self.entry_titulo = criar_entry(form_frame, placeholder="Título do Livro", height=ALTURA_INPUT)
        self.entry_titulo.configure(font=FONTE_INPUT)
        self.entry_titulo.grid(row=0, column=0, padx=(0, 10), pady=6, sticky="ew")

        self.entry_isbn = criar_entry(form_frame, placeholder="ISBN", height=ALTURA_INPUT)
        self.entry_isbn.configure(font=FONTE_INPUT)
        self.entry_isbn.grid(row=0, column=1, padx=(10, 10), pady=6, sticky="ew")

        self.btn_buscar_isbn = ctk.CTkButton(
            form_frame, text="Buscar ISBN", width=110, height=ALTURA_INPUT,
            fg_color="#0F172A", text_color="#FFFFFF", border_color=COR_INPUT_BORDER, border_width=1,
            hover_color="#1E293B", font=("Segoe UI", 13, "bold"), command=self._buscar_isbn
        )
        self.btn_buscar_isbn.grid(row=0, column=2, padx=(0, 0), pady=6, sticky="ew")

        # Categoria + Botão [+] em Azul
        cat_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        cat_frame.grid(row=1, column=0, padx=(0, 10), pady=6, sticky="ew")
        cat_frame.grid_columnconfigure(0, weight=1)

        self.combo_categoria = criar_combo(cat_frame, height=ALTURA_INPUT, values=[])
        self.combo_categoria.configure(font=FONTE_INPUT)
        self.combo_categoria.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        btn_add_cat = ctk.CTkButton(
            cat_frame, text="+", width=40, height=ALTURA_INPUT,
            fg_color="#0052CC", text_color="#FFFFFF",
            hover_color="#003399", font=("Segoe UI", 18, "bold"),
            command=self._adicionar_categoria
        )
        btn_add_cat.grid(row=0, column=1)

        self.entry_editora = criar_entry(form_frame, placeholder="Editora", height=ALTURA_INPUT)
        self.entry_editora.configure(font=FONTE_INPUT)
        self.entry_editora.grid(row=1, column=1, columnspan=2, padx=(10, 0), pady=6, sticky="ew")

        self.entry_ano = criar_entry(form_frame, placeholder="Ano de Publicação", height=ALTURA_INPUT)
        self.entry_ano.configure(font=FONTE_INPUT)
        self.entry_ano.grid(row=2, column=0, padx=(0, 10), pady=6, sticky="ew")

        self.entry_sinopse = criar_entry(form_frame, placeholder="Autor", height=ALTURA_INPUT)
        self.entry_sinopse.configure(font=FONTE_INPUT)
        self.entry_sinopse.grid(row=2, column=1, columnspan=2, padx=(10, 0), pady=6, sticky="ew")

        # Botões Principais de Ação (Ajustados para altura 38 e menor espaçamento vertical)
        botoes_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_container.grid(row=3, column=0, columnspan=3, pady=(12, 0))

        self.btn_cadastrar = ctk.CTkButton(
            botoes_container, text="Cadastrar Livro", command=self._cadastrar,
            width=180, height=38,
            fg_color="#0052CC", text_color="#FFFFFF",
            hover_color="#003399", font=("Segoe UI", 14, "bold")
        )
        self.btn_cadastrar.pack(side="left", padx=6)

        self.btn_editar = ctk.CTkButton(
            botoes_container, text="Editar Selecionado", command=self._editar_selecionado,
            width=180, height=38,
            fg_color="#0F172A", text_color="#FFFFFF",
            border_color=COR_INPUT_BORDER, border_width=1,
            hover_color="#1E293B", font=("Segoe UI", 14, "bold")
        )
        self.btn_editar.pack(side="left", padx=6)

        self.btn_atualizar = ctk.CTkButton(
            botoes_container, text="Atualizar Lista", command=self._carregar_tabela,
            width=150, height=38,
            fg_color="#0F172A", text_color="#FFFFFF",
            border_color=COR_INPUT_BORDER, border_width=1,
            hover_color="#1E293B", font=("Segoe UI", 14, "bold")
        )
        self.btn_atualizar.pack(side="left", padx=6)

        self.btn_excluir = ctk.CTkButton(
            botoes_container, text="Excluir Selecionado", command=self._excluir_selecionado,
            width=180, height=38,
            fg_color="#7F1D1D", text_color="#FCA5A5",
            hover_color="#991B1B", font=("Segoe UI", 14, "bold")
        )
        self.btn_excluir.pack(side="left", padx=6)

        # === LISTA / TABELA (Espaço Maximizado) ===
        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(5, 20))

        self._proporcoes = [0.30, 0.18, 0.15, 0.15, 0.08, 0.14]
        colunas = ["Título", "ISBN", "Categoria", "Editora", "Ano", "Status"]

        header_tab = ctk.CTkFrame(lista_card, fg_color="transparent", height=35)
        header_tab.pack(fill="x", padx=20, pady=(10, 2))
        header_tab.pack_propagate(False)

        for i, (nome, pct) in enumerate(zip(colunas, self._proporcoes)):
            rel_x = sum(self._proporcoes[:i])
            lbl = ctk.CTkLabel(header_tab, text=nome.upper(), font=("Segoe UI", 12, "bold"), text_color=COR_TEXTO, anchor="w")
            lbl.place(relx=rel_x, rely=0.5, anchor="w", relwidth=pct-0.01)

        self.lista_frame = criar_scroll_frame(lista_card, fg_color=COR_CARD)
        self.lista_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

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
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        self._itens_lista.clear()
        livros = listar_livros()

        if not livros:
            criar_label(self.lista_frame, "Nenhum livro cadastrado encontrado.", font=("Segoe UI", 14), text_color=COR_TEXTO).pack(pady=30)
            self.lista_frame.update_idletasks()
            return

        for idx, livro in enumerate(livros):
            self._criar_item(livro, idx)

        self.lista_frame.update_idletasks()
        try:
            self.lista_frame._parent_canvas.configure(
                scrollregion=self.lista_frame._parent_canvas.bbox("all")
            )
        except Exception as e:
            pass

    def _criar_item(self, livro, idx=0):
        # Cada linha da tabela agora usa altura 40px (mais compacto)
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=6, height=40)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)
        item.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))

        dados = livro[1:] if len(livro) > 6 else livro
        colunas = ["Titulo", "ISBN", "Categoria", "Editora", "Ano", "Status"]
        proporcoes = [0.30, 0.18, 0.15, 0.15, 0.08, 0.14]

        x_atual = 0.005
        for i, nome_col in enumerate(colunas):
            if i < len(dados):
                texto = dados[i]
                cor_txt = COR_TEXTO
                if i == 5:
                    status = str(texto).lower()
                    cor_txt = COR_DOURADO if "dispon" in status else COR_TEXTO2
                lbl = ctk.CTkLabel(
                    item, text=str(texto) if texto else "-",
                    font=("Segoe UI", 14), text_color=cor_txt, anchor="w", padx=8
                )
                lbl.place(relx=x_atual, rely=0.5, anchor="w", relwidth=proporcoes[i] - 0.01)
                lbl.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))
                x_atual += proporcoes[i]

        self._itens_lista.append((item, livro))

    def _selecionar(self, livro):
        self._selecionado = livro
        
        for item, l in self._itens_lista:
            if l == livro:
                # --- LINHA SELECIONADA: Fundo Azul Escuro e Texto Branco Puro ---
                item.configure(fg_color="#0F172A")
                
                # Encontra todas as labels filhas desse frame e força o texto a ficar branco
                for widget in item.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color="#FFFFFF")
            else:
                # --- LINHAS NÃO SELECIONADAS: Retorna ao padrão original do CustomTkinter ---
                item.configure(fg_color=COR_CARD)
                
                # Recupera os dados originais para restaurar a cor correta da coluna de status
                dados = l[1:] if len(l) > 6 else l
                
                for idx, widget in enumerate(item.winfo_children()):
                    if isinstance(widget, ctk.CTkLabel):
                        # Se for a última coluna (Status) e contiver "dispon", volta a ser dourado
                        if idx == 5 and "dispon" in str(dados[5]).lower():
                            widget.configure(text_color=COR_DOURADO)
                        else:
                            widget.configure(text_color=COR_TEXTO)
                            
        # Força o tkinter a redesenhar a tabela imediatamente na tela
        self.lista_frame.update_idletasks()

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

        if not validar_isbn(isbn):
            self._notificar("ISBN inválido. Use 10 ou 13 dígitos.")
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
        self.btn_cadastrar.configure(text="Cadastrar Livro", state="normal")

    def _buscar_isbn(self):
        isbn = self.entry_isbn.get().strip()
        if not isbn:
            self._notificar("Informe um ISBN antes de buscar.")
            return

        if not validar_isbn(isbn):
            self._notificar("ISBN inválido. Use 10 ou 13 dígitos.")
            return

        self.btn_buscar_isbn.configure(text="Buscando...", state="disabled")
        threading.Thread(target=self._buscar_isbn_async, args=(isbn,), daemon=True).start()

    def _buscar_isbn_async(self, isbn):
        livro = buscar_livro_por_isbn(isbn)
        self.after(0, lambda: self._finalizar_busca_isbn(livro))

    def _finalizar_busca_isbn(self, livro):
        self.btn_buscar_isbn.configure(text="Buscar ISBN", state="normal")
        if not livro:
            self._notificar("Não foi possível localizar o livro pelo ISBN.")
            return

        self.entry_titulo.delete(0, "end")
        self.entry_titulo.insert(0, livro.get("title", ""))
        self.entry_editora.delete(0, "end")
        self.entry_editora.insert(0, livro.get("publisher", ""))
        self.entry_ano.delete(0, "end")
        self.entry_ano.insert(0, str(livro.get("year", "")) if livro.get("year") else "")

        autores = livro.get("authors", "")
        self.entry_sinopse.delete(0, "end")
        self.entry_sinopse.insert(0, autores)
        self._notificar("Dados preenchidos com base no ISBN.")

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

    def _editar_selecionado(self):
        if not self._selecionado:
            self._notificar("Selecione um livro para editar.")
            return
        id_livro = self._selecionado[0]
        dados = buscar_livro_por_id(id_livro)
        if not dados:
            self._notificar("Livro nao encontrado.")
            return
        _, titulo, isbn, id_cat, editora, ano, sinopse = dados
        self._limpar_campos()
        self.entry_titulo.insert(0, titulo or '')
        self.entry_isbn.insert(0, isbn or '')
        self.entry_editora.insert(0, editora or '')
        self.entry_ano.insert(0, str(ano) if ano else '')
        self.entry_sinopse.insert(0, sinopse or '')
        for nome, cid in self._cat_map.items():
            if cid == id_cat:
                self.combo_categoria.set(nome)
                break
        self.btn_cadastrar.configure(text="Salvar Alteracoes", command=self._salvar_edicao)
        self._editando_id = id_livro

    def _salvar_edicao(self):
        titulo = self.entry_titulo.get().strip()
        isbn = self.entry_isbn.get().strip()
        cat_nome = self.combo_categoria.get()
        editora = self.entry_editora.get().strip()
        ano = self.entry_ano.get().strip()
        sinopse = self.entry_sinopse.get().strip()

        if not titulo or not isbn:
            self._notificar("Titulo e ISBN sao obrigatorios.")
            return
        if cat_nome not in self._cat_map:
            self._notificar("Selecione uma categoria valida.")
            return

        from services.database_config import _conectar
        from mysql.connector import Error
        try:
            conn = _conectar()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE livro SET titulo=%s, isbn=%s, id_categoria=%s,
                   editora=%s, ano_publicacao=%s, sinopse=%s WHERE id_livro=%s""",
                (titulo, isbn, self._cat_map[cat_nome], editora or None,
                 int(ano) if ano.isdigit() else None, sinopse or None, self._editando_id)
            )
            conn.commit()
            conn.close()
            self._notificar("Livro atualizado com sucesso!")
            self._limpar_campos()
            self.btn_cadastrar.configure(text="Cadastrar Livro", command=self._cadastrar)
            self._editando_id = None
            self._carregar_tabela()
        except Error as e:
            self._notificar(f"Erro ao atualizar: {e}")

    def _gerenciar_autores(self):
        if not self._selecionado:
            self._notificar("Selecione um livro primeiro.")
            return
        JanelaAutoresLivro(self, self._selecionado[0], self._selecionado[1])

    def _limpar_campos(self):
        for e in [self.entry_titulo, self.entry_isbn, self.entry_editora, self.entry_ano, self.entry_sinopse]:
            e.delete(0, "end")

    def _voltar(self):
        if self.controller: self.controller.voltar()

    def _notificar(self, msg):
        self.lbl_notificacao.configure(text=msg, text_color=COR_DOURADO, font=("Segoe UI", 14, "bold"))
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))