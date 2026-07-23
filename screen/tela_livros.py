from email import header
import os
import sys
import threading
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.isbn_service import buscar_por_isbn
from services.database_config import (
    cadastrar_livro, listar_livros, excluir_livro, buscar_livro_por_id,
    listar_categorias, cadastrar_categoria,
    listar_autores, listar_autores_livro, associar_autor_livro, desassociar_autor_livro
)
from services.styles import (
    cores,
    criar_entry, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame, criar_combo, aplicar_validacao_focusout,
    criar_botao_primario, criar_botao_secundario, criar_botao_perigo
)
from services.validador import validar_isbn, validar_ano, validar_texto, validar_autor

class TelaLivros(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=cores.COR_BG)
        self.controller = controller
        self._itens_lista = []
        self._selecionado = None
        self._cat_map = {}
        self._construir_ui()
        self._carregar_categorias()
        self._carregar_tabela()



    def _reconstruir_tema(self):
        """Reconstrói a tela ao trocar o tema claro/escuro."""
        if not self.winfo_exists():
            return
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=cores.COR_BG)
        self._construir_ui()
        self._carregar_categorias()
        self._carregar_tabela()

    def _ao_visitar(self):
        self._carregar_categorias()
        self._carregar_tabela()
        self._limpar_campos()
        for e in [self.entry_titulo, self.entry_isbn, self.entry_editora,
                  self.entry_ano, self.entry_sinopse]:
            e._tocado = False
            e._validacao_ativa = False
            e.configure(border_color=cores.COR_INPUT_BORDER)
        self.after(100, self._forcar_placeholder)

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === HEADER COMPACTADO (Otimização de Espaço) ===
        header = ctk.CTkFrame(self, fg_color=cores.COR_CARD)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 8))

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y", padx=10, pady=5)

        # Logo reduzida para 55x55
        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(55, 55))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))

        criar_label(header_left, "Cadastro de Livros", font=("Segoe UI", 24, "bold"), text_color=cores.COR_TEXTO).pack(side="left")

        criar_botao_secundario(header, "Voltar", command=self._voltar, width=100, height=36).pack(side="right", padx=15, pady=5)

        # === FORMULÁRIO DE CADASTRO ===
        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(5, 10))

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=12)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        ALTURA_INPUT = 36
        FONTE_INPUT = ("Segoe UI", 14)

        self.entry_titulo = criar_entry(form_frame, placeholder="Título do Livro", height=ALTURA_INPUT)
        self.entry_titulo.configure(font=FONTE_INPUT)
        self.entry_titulo.grid(row=0, column=0, padx=(0, 10), pady=6, sticky="ew")

        self.entry_isbn = criar_entry(form_frame, placeholder="ISBN", height=ALTURA_INPUT)
        self.entry_isbn.configure(font=FONTE_INPUT)
        self.entry_isbn.grid(row=0, column=1, padx=(10, 10), pady=6, sticky="ew")
        self.entry_isbn.bind("<Return>", lambda e: self._buscar_isbn())

        self.btn_buscar_isbn = criar_botao_secundario(
            form_frame, text="Buscar ISBN", command=self._buscar_isbn, width=110, height=ALTURA_INPUT
        )
        self.btn_buscar_isbn.grid(row=0, column=2, padx=(0, 0), pady=6, sticky="ew")

        # Categoria
        cat_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        cat_frame.grid(row=1, column=0, padx=(0, 10), pady=6, sticky="ew")
        cat_frame.grid_columnconfigure(0, weight=1)

        self.entry_busca_cat = criar_entry(cat_frame, placeholder="Categoria (digite para buscar)", height=ALTURA_INPUT)
        self.entry_busca_cat.configure(font=FONTE_INPUT)
        self.entry_busca_cat.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.entry_busca_cat.bind("<KeyRelease>", self._atualizar_sugestoes_cat)
        self.entry_busca_cat.bind("<FocusOut>", lambda e: self.after(150, self._esconder_sugestoes_cat))

        self._frame_sugestoes_cat = ctk.CTkScrollableFrame(cat_frame, fg_color=cores.COR_INPUT_BG, height=120, corner_radius=8)
        self._cat_selecionada_id = None

        btn_add_cat = ctk.CTkButton(
            cat_frame, text="+", width=40, height=ALTURA_INPUT,
            fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF", hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 18, "bold"), command=self._adicionar_categoria
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

        # === BOTÕES DE AÇÃO ===
        botoes_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_container.grid(row=3, column=0, columnspan=3, pady=(12, 0))

        self.btn_cadastrar = criar_botao_primario(
            botoes_container, "Cadastrar Livro", command=self._cadastrar, width=180
        )
        self.btn_cadastrar.pack(side="left", padx=6)

        self.btn_editar = criar_botao_secundario(
            botoes_container, "Editar Selecionado", command=self._editar_selecionado, width=180
        )
        self.btn_editar.pack(side="left", padx=6)

        self.btn_atualizar = criar_botao_secundario(
            botoes_container, "Atualizar Lista", command=self._carregar_tabela, width=150
        )
        self.btn_atualizar.pack(side="left", padx=6)

        self.btn_excluir = criar_botao_perigo(
            botoes_container, "Excluir Selecionado", command=self._excluir_selecionado, width=180
        )
        self.btn_excluir.pack(side="left", padx=6)

        # === LISTA / TABELA ===
        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(5, 20))

        COLUNAS_LIVROS = [
            ("Título",     3, 250, 35),
            ("ISBN",       2, 150, 16),
            ("Categoria",  2, 150, 18),
            ("Editora",    2, 150, 18),
            ("Ano",        1,  70,  6),
            ("Autor",      2, 150, 22),
            ("Status",     1, 100, 12),
        ]
        COMPENSA_SCROLLBAR = 18

        busca_frame = ctk.CTkFrame(lista_card, fg_color="transparent")
        busca_frame.pack(fill="x", padx=20, pady=(12, 0))

        self.entry_filtro = criar_entry(busca_frame, placeholder="Buscar na lista por título, ISBN ou categoria…", height=40, width=300)
        self.entry_filtro.configure(font=("Segoe UI", 13))
        self.entry_filtro.pack(side="left", fill="x", expand=False, padx=(0, 8))
        self.entry_filtro.bind("<KeyRelease>", lambda e: self._filtrar_tabela())

        ctk.CTkButton(
            busca_frame, text="↺ Limpar", width=90, height=34,
            fg_color=cores.COR_CARD, font=("Segoe UI", 13, "bold"), command=self._limpar_filtro
        ).pack(side="left")

        # Cabeçalho
        header_tab = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_tab.pack(fill="x", padx=(20, 20 + COMPENSA_SCROLLBAR), pady=(8, 2))

        for idx, (nome, peso, minsize, max_chars) in enumerate(COLUNAS_LIVROS):
            header_tab.grid_columnconfigure(idx, weight=peso, minsize=minsize)
            ctk.CTkLabel(header_tab, text=nome.upper(), font=("Segoe UI", 12, "bold"),
                         text_color=cores.COR_TEXTO, anchor="center").grid(row=0, column=idx, sticky="ew", padx=(10, 4), pady=8)

        self.lista_frame = criar_scroll_frame(lista_card, fg_color=cores.COR_CARD)
        self.lista_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self._colunas_livros = COLUNAS_LIVROS

        self.lbl_notificacao = criar_label(self, "", text_color=cores.COR_TEXTO2)
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")

        # Validações
        self._lbl_erro_campo = criar_label(form_card, "", font=("Segoe UI", 12))
        self._lbl_erro_campo.place(relx=0.01, rely=0.97, anchor="sw")

        _entries = [self.entry_titulo, self.entry_isbn, self.entry_editora, self.entry_ano, self.entry_sinopse]
        aplicar_validacao_focusout(self.entry_titulo,  lambda v: validar_texto(v, "Título", min_len=2), self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_isbn,    lambda v: validar_isbn(v), self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_editora, lambda v: validar_texto(v, "Editora", min_len=2, obrigatorio=False), self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_ano,     lambda v: validar_ano(v), self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_sinopse, lambda v: validar_autor(v), self._lbl_erro_campo, _entries)

        self.after(300, self._forcar_placeholder)
    def _forcar_placeholder(self):
        """Força redesenho dos placeholders — workaround para CustomTkinter no Python 3.14."""
        entries = [self.entry_titulo, self.entry_isbn, self.entry_editora,
                   self.entry_ano, self.entry_sinopse, self.entry_busca_cat]
        for e in entries:
            try:
                ph = e._placeholder_text
                e.delete(0, "end")
                e.configure(placeholder_text=ph)
            except Exception:
                pass

    def _carregar_categorias(self):
        cats = listar_categorias()
        self._cat_map = {c[1]: c[0] for c in cats}
        self._cat_lista = list(self._cat_map.keys())

    def _atualizar_sugestoes_cat(self, event=None):
        termo = self.entry_busca_cat.get().strip().lower()
        for w in self._frame_sugestoes_cat.winfo_children():
            w.destroy()
        if not termo:
            self._esconder_sugestoes_cat()
            return
        resultados = [c for c in self._cat_lista if termo in c.lower()]
        if not resultados:
            self._esconder_sugestoes_cat()
            return
        self._frame_sugestoes_cat.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        for cat in resultados[:15]:
            ctk.CTkButton(
                self._frame_sugestoes_cat, text=cat, anchor="w",
                fg_color="transparent", text_color=cores.COR_TEXTO,
                hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 13),
                height=30, corner_radius=4,
                command=lambda c=cat: self._escolher_categoria(c)
            ).pack(fill="x", pady=1)

    def _escolher_categoria(self, cat):
        self._cat_selecionada_id = self._cat_map[cat]
        self.entry_busca_cat.delete(0, "end")
        self.entry_busca_cat.insert(0, cat)
        self._esconder_sugestoes_cat()

    def _esconder_sugestoes_cat(self):
        self._frame_sugestoes_cat.grid_forget()

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
        self._todos_livros = listar_livros()
        self._renderizar(self._todos_livros)

    def _filtrar_tabela(self):
        termo = self.entry_filtro.get().strip().lower()
        if not termo:
            self._renderizar(self._todos_livros)
            return
        resultado = [
            l for l in self._todos_livros
            if termo in str(l[1]).lower()
            or termo in str(l[2]).lower()
            or termo in str(l[3]).lower()
        ]
        self._renderizar(resultado)
        if resultado:
            self._selecionar(resultado[0])

    def _limpar_filtro(self):
        self.entry_filtro.delete(0, "end")
        self._renderizar(self._todos_livros)
        if self._todos_livros:
            self._selecionar(self._todos_livros[0])

    def _renderizar(self, livros):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        self._itens_lista.clear()
        if not livros:
            criar_label(self.lista_frame, "Nenhum livro encontrado.",
                        font=("Segoe UI", 14), text_color=cores.COR_TEXTO).pack(pady=30)
            return
        for idx, livro in enumerate(livros):
            self._criar_item(livro, idx)
        self.lista_frame.update_idletasks()

    def _criar_item(self, livro, idx=0):
        item = ctk.CTkFrame(self.lista_frame, fg_color=cores.COR_CARD, corner_radius=6, height=40)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)
        item.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))

        # banco: (id, titulo, isbn, categoria, editora, ano, status_livro, sinopse)
        _, titulo, isbn, categoria, editora, ano, status_livro, sinopse, *_ = (*livro, None, None)
        # exibição: Título, ISBN, Categoria, Editora, Ano, Autor(sinopse), Status
        dados = [titulo, isbn, categoria, editora, ano, sinopse, status_livro]

        for idx_col, (nome, peso, minsize, max_chars) in enumerate(self._colunas_livros):
            item.grid_columnconfigure(idx_col, weight=peso, minsize=minsize)
            valor = dados[idx_col]
            texto = "-" if valor is None or valor == "" else str(valor)
            if len(texto) > max_chars:
                texto = texto[:max_chars - 1].rstrip() + "…"
            cor_txt = cores.COR_TEXTO
            if nome == "Status":
                s = str(dados[idx_col]).lower() if dados[idx_col] else ""
                if "dispon" in s:
                    cor_txt = cores.COR_SUCESSO
                elif "emprestado" in s or "manutenc" in s:
                    cor_txt = cores.COR_AVISO
                elif "atrasado" in s or "inativo" in s:
                    cor_txt = cores.COR_PERIGO
                else:
                    cor_txt = cores.COR_TEXTO2
            ancora = "w" if nome == "Título" else "center"
            lbl = ctk.CTkLabel(item, text=texto, font=("Segoe UI", 14), text_color=cor_txt, anchor=ancora)
            lbl.grid(row=0, column=idx_col, sticky="ew", padx=(10, 4), pady=7)
            lbl.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))

        self._itens_lista.append((item, livro))

    def _selecionar(self, livro):
        self._selecionado = livro

        for item, l in self._itens_lista:
            selecionado = l == livro
            dados = l[1:] if len(l) > 6 else l

            if selecionado:
                item.configure(fg_color=cores.COR_AZUL_HOVER, border_width=0)
                for widget in item.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color="#FFFFFF", fg_color=cores.COR_AZUL_HOVER)
            else:
                item.configure(fg_color=cores.COR_CARD, border_width=0)
                for idx, widget in enumerate(item.winfo_children()):
                    if isinstance(widget, ctk.CTkLabel):
                        _, _, _, _, _, _, status_l, *_ = (*l, None, None)
                        if idx == 6:
                            s = str(status_l).lower() if status_l else ""
                            if "dispon" in s:
                                cor = cores.COR_SUCESSO
                            elif "emprestado" in s or "manutenc" in s:
                                cor = cores.COR_AVISO
                            elif "atrasado" in s or "inativo" in s:
                                cor = cores.COR_PERIGO
                            else:
                                cor = cores.COR_TEXTO2
                        else:
                            cor = cores.COR_TEXTO
                        widget.configure(text_color=cor, fg_color=cores.COR_CARD)

        self.lista_frame.update_idletasks()

    def _cadastrar(self):
        titulo   = self.entry_titulo.get().strip()
        isbn     = self.entry_isbn.get().strip()
        editora  = self.entry_editora.get().strip()
        ano      = self.entry_ano.get().strip()
        sinopse  = self.entry_sinopse.get().strip()

        ok, msg = validar_texto(titulo, "Título", min_len=2)
        if not ok:
            self._notificar(msg); return
        if not isbn:
            self._notificar("ISBN é obrigatório."); return
        ok_isbn, msg_isbn = validar_isbn(isbn)
        if not ok_isbn:
            self._notificar(msg_isbn); return
        if not self._cat_selecionada_id:
            self._notificar("Selecione uma categoria."); return
        ok, msg = validar_ano(ano)
        if not ok:
            self._notificar(msg); return
        ok, msg = validar_texto(editora, "Editora", min_len=2, obrigatorio=False)
        if not ok:
            self._notificar(msg); return
        ok, msg = validar_autor(sinopse)
        if not ok:
            self._notificar(msg); return

        ano_pub = int(ano) if ano else None
        self.btn_cadastrar.configure(text="Processando...", state="disabled")
        self._salvar(titulo, isbn, self._cat_selecionada_id, editora, ano_pub, sinopse)

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
        print(f"ISBN digitado: '{isbn}'")
        if not isbn:
            self._notificar("Informe um ISBN antes de buscar.")
            return

        ok_isbn, msg_isbn = validar_isbn(isbn)
        print(f"Validação ISBN: ok={ok_isbn}, msg={msg_isbn}")
        if not ok_isbn:
            self._notificar(msg_isbn)
            return

        self.btn_buscar_isbn.configure(text="Buscando...", state="disabled")
        self.lbl_notificacao.configure(text="Consultando bases de dados...", text_color=cores.COR_AZUL_HOVER)
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        threading.Thread(target=self._buscar_isbn_async, args=(isbn,), daemon=True).start()

    def _buscar_isbn_async(self, isbn):
        resultado = buscar_por_isbn(isbn)
        print(f"Resultado da busca: {resultado}")
        self.after(0, lambda: self._finalizar_busca_isbn(resultado))

    def _finalizar_busca_isbn(self, resultado):
        self.btn_buscar_isbn.configure(text="Buscar ISBN", state="normal")
        if not resultado:
            self._notificar("Livro não encontrado nas bases consultadas. Cadastre manualmente.")
            return

        self.entry_titulo.delete(0, "end")
        self.entry_titulo.insert(0, resultado.get("title", ""))
        self.entry_editora.delete(0, "end")
        self.entry_editora.insert(0, resultado.get("publisher", ""))
        self.entry_ano.delete(0, "end")
        self.entry_ano.insert(0, str(resultado.get("year", "")) if resultado.get("year") else "")
        self.entry_sinopse.delete(0, "end")
        self.entry_sinopse.insert(0, resultado.get("authors", ""))

        fonte = resultado.get("source", "desconhecida")
        self._notificar(f"Encontrado via {fonte}!")

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
        dados = buscar_livro_por_id(self._selecionado[0])
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
        # Preenche o campo de categoria
        for nome, cid in self._cat_map.items():
            if cid == id_cat:
                self._cat_selecionada_id = cid
                self.entry_busca_cat.delete(0, "end")
                self.entry_busca_cat.insert(0, nome)
                break
        self.btn_cadastrar.configure(text="Salvar Alterações", command=self._salvar_edicao)
        self._editando_id = self._selecionado[0]

    def _salvar_edicao(self):
        titulo  = self.entry_titulo.get().strip()
        isbn    = self.entry_isbn.get().strip()
        editora = self.entry_editora.get().strip()
        ano     = self.entry_ano.get().strip()
        sinopse = self.entry_sinopse.get().strip()

        ok, msg = validar_texto(titulo, "Título", min_len=2)
        if not ok:
            self._notificar(msg); return
        if not isbn:
            self._notificar("ISBN é obrigatório."); return
        ok_isbn, msg_isbn = validar_isbn(isbn)
        if not ok_isbn:
            self._notificar(msg_isbn); return
        if not self._cat_selecionada_id:
            self._notificar("Selecione uma categoria válida."); return
        ok, msg = validar_ano(ano)
        if not ok:
            self._notificar(msg); return

        from services.database_config import _conectar
        from mysql.connector import Error
        try:
            conn = _conectar()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE livro SET titulo=%s, isbn=%s, id_categoria=%s,
                   editora=%s, ano_publicacao=%s, sinopse=%s WHERE id_livro=%s""",
                (titulo, isbn, self._cat_selecionada_id, editora or None,
                 int(ano) if ano else None, sinopse or None, self._editando_id)
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
        self.entry_busca_cat.delete(0, "end")
        self._cat_selecionada_id = None

    def _voltar(self):
        if self.controller: self.controller.voltar()

    def _notificar(self, msg):
        self.lbl_notificacao.configure(text=msg, text_color=cores.COR_DOURADO, font=("Segoe UI", 14, "bold"))
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.lbl_notificacao.bind("<Button-1>", lambda e: self.lbl_notificacao.configure(text=""))
        self.after(5000, lambda: self.lbl_notificacao.configure(text=""))