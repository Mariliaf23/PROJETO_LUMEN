import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import (
    listar_livros, listar_exemplares, cadastrar_exemplar,
    excluir_exemplar, atualizar_status_exemplar,
    exemplar_tem_historico_emprestimo, exemplar_patrimonio_duplicado,
    obter_proximo_patrimonio
)
from services.barcode_gen import (
    gerar_codigo_barras, obter_caminho_barcode, regenerar_barcode,
    gerar_pagina_etiquetas
)
from services.styles import (
    cores,
    criar_entry, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame, criar_combo, aplicar_validacao_focusout
)
from services.validador import validar_patrimonio, validar_texto
from services.db_async import carregar_em_fundo


COLUNAS_EXEMPLARES = [
    ("Patrimônio",  2, 140, 16),
    ("Livro",       4, 280, 35),
    ("Status",      2, 140, 12),
    ("Localização", 2, 140, 18),
]
COMPENSA_SCROLLBAR = 18


class JanelaBarcode(ctk.CTkToplevel):
    def __init__(self, master, patrimonio, caminho_imagem):
        super().__init__(master)
        self.title(f"Código de Barras - {patrimonio}")
        self.geometry("350x420")
        self.resizable(False, False)
        self.configure(fg_color=cores.COR_BG)
        self.grab_set()

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")
        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(50, 50))
                ctk.CTkLabel(self, image=img_logo, text="").pack(pady=(15, 5))
            except Exception:
                pass

        criar_titulo(self, "LUMEN", font=("Cinzel", 18, "bold"), text_color=cores.COR_DOURADO).pack()
        criar_label(self, "Código de Barras", font=("Segoe UI", 14, "bold"),
                    text_color=cores.COR_TEXTO).pack(pady=(5, 10))

        card = criar_card(self)
        card.pack(fill="x", padx=30, pady=(0, 10))

        try:
            img = Image.open(caminho_imagem)
            largura_max = 300
            ratio = largura_max / img.width
            nova_altura = int(img.height * ratio)
            img = img.resize((largura_max, nova_altura), Image.LANCZOS)
            img_ctk = ctk.CTkImage(img, size=(largura_max, nova_altura))
            lbl_img = ctk.CTkLabel(card, image=img_ctk, text="")
            lbl_img.pack(padx=20, pady=15)
            lbl_img.image = img_ctk
        except Exception as e:
            criar_label(card, f"Erro ao carregar imagem: {e}",
                        font=("Segoe UI", 12), text_color=cores.COR_PERIGO).pack(pady=20)

        criar_label(self, patrimonio, font=("Consolas", 16, "bold"),
                    text_color=cores.COR_TEXTO).pack(pady=(0, 15))

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.pack(pady=(0, 15))

        ctk.CTkButton(
            botoes, text="Imprimir", width=120, height=36,
            fg_color=cores.COR_ATIVO, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._imprimir(caminho_imagem, patrimonio)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes, text="Fechar", width=120, height=36,
            fg_color=cores.COR_CARD, hover_color=cores.COR_INPUT_BG,
            font=("Segoe UI", 13, "bold"),
            command=self.destroy
        ).pack(side="left")

    def _imprimir(self, caminho_imagem, patrimonio):
        try:
            import subprocess, platform
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(caminho_imagem)
            elif sistema == "Darwin":
                subprocess.run(["open", caminho_imagem])
            else:
                subprocess.run(["xdg-open", caminho_imagem])
        except Exception as e:
            criar_label(self, f"Erro ao abrir: {e}",
                        font=("Segoe UI", 11), text_color=cores.COR_PERIGO).pack()


class TelaExemplares(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=cores.COR_BG)
        self.controller = controller
        self._itens_lista = []
        self._selecionado = None
        self._livros_map = {}
        self._livros_lista = []
        self._editando_id = None
        self._after_ids = set()
        self._tema_pendente = False
        self._todos_exemplares = []

        self._construir_ui()
        self._carregar_livros()
        self._carregar_tabela()

    # ── Controle de after() e tema ────────────────────────────────────────────
    def _cancelar_afters(self):
        for after_id in list(getattr(self, "_after_ids", set())):
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self._after_ids.clear()

    def _agendar_after(self, ms, callback):
        def executar():
            self._after_ids.discard(after_id)
            if not self.winfo_exists():
                return
            try:
                callback()
            except Exception:
                pass
        after_id = self.after(ms, executar)
        self._after_ids.add(after_id)
        return after_id

    def _reconstruir_tema(self):
        """Reconstrói a interface após troca de tema e recarrega os dados."""
        if not self.winfo_exists():
            return

        self._cancelar_afters()

        # Destrói tudo com segurança
        for widget in list(self.winfo_children()):
            try:
                widget.destroy()
            except Exception:
                pass

        self.configure(fg_color=cores.COR_BG)

        # Reconstrói a interface
        self._construir_ui()

        # Carrega dados com um pequeno delay para garantir que o CTkScrollableFrame
        # e o canvas interno já estejam estáveis (evita lista vazia / TclError)
        self._agendar_after(40, self._recarregar_apos_tema)

    def _recarregar_apos_tema(self):
        """Chamado após a reconstrução do tema."""
        if not self.winfo_exists():
            return
        try:
            self._carregar_livros()
            self._carregar_tabela()
        except Exception as e:
            print(f"[TelaExemplares] Erro ao recarregar após tema: {e}")

    def _ao_visitar(self):
        """Chamado sempre que a tela fica visível."""
        if not self.winfo_exists():
            return

        if getattr(self, "_tema_pendente", False):
            self._tema_pendente = False
            self._reconstruir_tema()
            return

        self._carregar_livros()
        self._carregar_tabela()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color=cores.COR_CARD)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 8))

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y", padx=10, pady=5)

        criar_label(header_left, "Gerenciamento de Exemplares",
                    font=("Segoe UI", 26, "bold"), text_color=cores.COR_TEXTO).pack(side="left")

        ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=100, height=36,
            fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            text_color="#FFFFFF", font=("Segoe UI", 14, "bold")
        ).pack(side="right", padx=15, pady=5)

        # Formulário
        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(5, 10))

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=12)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        ALTURA_INPUT = 38
        FONTE_INPUT = ("Segoe UI", 14)

        # Livro Vinculado
        criar_label(form_frame, "Livro Vinculado", font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 2))

        livro_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        livro_container.grid(row=1, column=0, padx=(0, 10), pady=(0, 6), sticky="ew")
        livro_container.grid_columnconfigure(0, weight=1)

        self.entry_busca_livro = criar_entry(livro_container, placeholder="Digite o título do livro…", height=ALTURA_INPUT)
        self.entry_busca_livro.configure(font=FONTE_INPUT)
        self.entry_busca_livro.grid(row=0, column=0, sticky="ew")
        self.entry_busca_livro.bind("<KeyRelease>", self._atualizar_sugestoes)
        self.entry_busca_livro.bind("<FocusOut>", lambda e: self._agendar_after(150, self._esconder_sugestoes))

        self._frame_sugestoes = ctk.CTkScrollableFrame(
            livro_container, fg_color=cores.COR_INPUT_BG, height=120, corner_radius=8
        )
        self._livro_selecionado_id = None

        # Código Patrimônio
        criar_label(form_frame, "Código Patrimônio", font=("Segoe UI", 13, "bold")).grid(
            row=0, column=1, sticky="w", pady=(0, 2))

        patrimonio_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        patrimonio_container.grid(row=1, column=1, padx=(10, 0), pady=(0, 6), sticky="ew")
        patrimonio_container.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(patrimonio_container, text="PAT-", font=("Segoe UI", 14, "bold"),
                    text_color=cores.COR_TEXTO, width=50).grid(row=0, column=0, padx=(0, 2))

        self.entry_patrimonio = criar_entry(patrimonio_container, placeholder="00001", height=ALTURA_INPUT)
        self.entry_patrimonio.configure(font=FONTE_INPUT)
        self.entry_patrimonio.grid(row=0, column=1, sticky="ew")

        # Localização
        criar_label(form_frame, "Localização no Acervo", font=("Segoe UI", 13, "bold")).grid(
            row=2, column=0, sticky="w", pady=(4, 2))
        self.entry_localizacao = criar_entry(form_frame, placeholder="Ex: Estante B, Prateleira 3", height=ALTURA_INPUT)
        self.entry_localizacao.configure(font=FONTE_INPUT)
        self.entry_localizacao.grid(row=3, column=0, padx=(0, 10), pady=(0, 0), sticky="ew")

        # Botões (sem Editar) — todos azuis, fonte maior e padronizados
        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.grid(row=3, column=1, padx=(10, 0), sticky="ew")
        botoes_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        BTN_H = 38
        BTN_FONT = ("Segoe UI", 13, "bold")   # fonte maior

        self.btn_adicionar = ctk.CTkButton(
            botoes_frame, text="+ Adicionar", command=self._adicionar,
            height=BTN_H, fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
            hover_color=cores.COR_AZUL_HOVER, font=BTN_FONT
        )
        self.btn_adicionar.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_barcode = ctk.CTkButton(
            botoes_frame, text="⊞ Barcode", command=self._ver_barcode,
            height=BTN_H, fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
            hover_color=cores.COR_AZUL_HOVER, font=BTN_FONT
        )
        self.btn_barcode.grid(row=0, column=1, padx=(0, 4), sticky="ew")

        self.btn_imprimir_etiquetas = ctk.CTkButton(
            botoes_frame, text="🖨 Etiquetas", command=self._imprimir_etiquetas,
            height=BTN_H, fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
            hover_color=cores.COR_AZUL_HOVER, font=BTN_FONT
        )
        self.btn_imprimir_etiquetas.grid(row=0, column=2, padx=(0, 4), sticky="ew")

        self.btn_excluir = ctk.CTkButton(
            botoes_frame, text="✕ Excluir", command=self._excluir_selecionado,
            height=BTN_H, fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
            hover_color=cores.COR_AZUL_HOVER, font=BTN_FONT
        )
        self.btn_excluir.grid(row=0, column=3, sticky="ew")

        # Tabela
        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(5, 20))

        # Barra de busca + Limpar (campo mais largo + botão azul padronizado)
        busca_frame = ctk.CTkFrame(lista_card, fg_color="transparent")
        busca_frame.pack(fill="x", padx=20, pady=(12, 0))

        self.entry_filtro = criar_entry(
            busca_frame,
            placeholder="Buscar na lista por patrimônio, livro ou localização…",
            height=36
        )
        self.entry_filtro.configure(font=("Segoe UI", 13))
        self.entry_filtro.pack(side="left", fill="x", expand=True, padx=(0, 10))  # agora bem mais largo
        self.entry_filtro.bind("<KeyRelease>", lambda e: self._filtrar_tabela())

        ctk.CTkButton(
            busca_frame, text="↺ Limpar", width=110, height=36,
            fg_color=cores.COR_AZUL_PRINCIPAL,          # azul forte
            hover_color=cores.COR_AZUL_HOVER,
            text_color="#FFFFFF",
            font=("Segoe UI", 13, "bold"),
            command=self._limpar_filtro
        ).pack(side="left")

        # Cabeçalho da tabela
        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_lista.pack(fill="x", padx=(20, 20 + COMPENSA_SCROLLBAR), pady=(8, 2))

        for idx, (nome, peso, minsize, max_chars) in enumerate(COLUNAS_EXEMPLARES):
            header_lista.grid_columnconfigure(idx, weight=peso, minsize=minsize)
            criar_label(header_lista, nome.upper(), font=("Segoe UI", 14, "bold"),
                        text_color=cores.COR_TEXTO, anchor="center"
                        ).grid(row=0, column=idx, sticky="ew", padx=(10, 4), pady=8)

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.lbl_notificacao = criar_label(self, "", text_color=cores.COR_TEXTO2)

        self._lbl_erro_campo = criar_label(form_card, "", font=("Segoe UI", 12))
        self._lbl_erro_campo.place(relx=0.01, rely=0.97, anchor="sw")

        _entries = [self.entry_patrimonio, self.entry_localizacao]
        aplicar_validacao_focusout(self.entry_patrimonio, lambda v: validar_patrimonio(v),
                                self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_localizacao,
                                lambda v: validar_texto(v, "Localização", min_len=3, obrigatorio=False),
                                self._lbl_erro_campo, _entries)
    # ── Dados ─────────────────────────────────────────────────────────────────
    def _carregar_livros(self):
        try:
            livros = listar_livros()
            self._livros_map = {}
            self._livros_lista = []
            for l in livros:
                texto = f"{l[1]} ({l[2]})"
                self._livros_map[texto] = l[0]
                self._livros_lista.append(texto)
        except Exception as e:
            print(f"[TelaExemplares] Erro ao carregar livros: {e}")

    def _atualizar_sugestoes(self, event=None):
        termo = self.entry_busca_livro.get().strip().lower()
        for w in self._frame_sugestoes.winfo_children():
            w.destroy()

        if not termo:
            self._esconder_sugestoes()
            return

        resultados = [t for t in self._livros_lista if termo in t.lower()]
        if not resultados:
            self._esconder_sugestoes()
            return

        self._frame_sugestoes.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        for texto in resultados[:20]:
            btn = ctk.CTkButton(
                self._frame_sugestoes, text=texto, anchor="w",
                fg_color="transparent", text_color=cores.COR_TEXTO,
                hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 16),
                height=36, corner_radius=4,
                command=lambda t=texto: self._escolher_livro(t)
            )
            btn.pack(fill="x", pady=1)

    def _escolher_livro(self, texto):
        self._livro_selecionado_id = self._livros_map.get(texto)
        self.entry_busca_livro.delete(0, "end")
        self.entry_busca_livro.insert(0, texto)
        self._esconder_sugestoes()

        if self._livro_selecionado_id:
            proximo = obter_proximo_patrimonio(self._livro_selecionado_id)
            self.entry_patrimonio.delete(0, "end")
            self.entry_patrimonio.insert(0, proximo.replace("PAT-", ""))

    def _esconder_sugestoes(self):
        try:
            self._frame_sugestoes.grid_forget()
        except Exception:
            pass

    def _carregar_tabela(self, exemplares=None):
        if not hasattr(self, "lista_frame") or not self.lista_frame.winfo_exists():
            return

        for w in self.lista_frame.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass

        self._itens_lista.clear()
        self._selecionado = None

        if exemplares is None:
            try:
                self._todos_exemplares = listar_exemplares() or []
            except Exception as e:
                print(f"[TelaExemplares] Erro ao listar exemplares: {e}")
                self._todos_exemplares = []
            exemplares = self._todos_exemplares

        self._renderizar(exemplares)

    def _renderizar(self, exemplares):
        if not hasattr(self, "lista_frame") or not self.lista_frame.winfo_exists():
            return

        for w in self.lista_frame.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass

        self._itens_lista.clear()
        self._selecionado = None

        if not exemplares:
            criar_label(self.lista_frame, "Nenhum exemplar encontrado.",
                        font=("Segoe UI", 16), text_color=cores.COR_TEXTO).pack(pady=30)
            return

        for exc in exemplares:
            self._criar_item(exc)

        try:
            self.lista_frame.update_idletasks()
        except Exception:
            pass

    def _filtrar_tabela(self):
        termo = self.entry_filtro.get().strip().lower()
        if not termo:
            self._renderizar(self._todos_exemplares)
            return

        resultado = [
            e for e in self._todos_exemplares
            if termo in str(e[1]).lower()
            or (len(e) > 4 and termo in str(e[4]).lower())
            or termo in str(e[3]).lower()
        ]
        self._renderizar(resultado)
        if resultado and self._itens_lista:
            self._selecionar(self._itens_lista[0][0])

    def _limpar_filtro(self):
        self.entry_filtro.delete(0, "end")
        self._renderizar(self._todos_exemplares)
        if self._itens_lista:
            self._selecionar(self._itens_lista[0][0])

    def _criar_item(self, exc):
        item = ctk.CTkFrame(self.lista_frame, fg_color=cores.COR_CARD, corner_radius=6, height=40)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)
        item._dados = exc
        item.bind("<Button-1>", lambda e, it=item: self._selecionar(it))

        # [id, codigo_patrimonio, status, localizacao, titulo]
        dados_exibicao = [exc[1], exc[4], exc[2], exc[3]] if len(exc) > 4 else list(exc)

        for idx_col, (nome, peso, minsize, max_chars) in enumerate(COLUNAS_EXEMPLARES):
            item.grid_columnconfigure(idx_col, weight=peso, minsize=minsize)
            valor = dados_exibicao[idx_col] if idx_col < len(dados_exibicao) else None
            texto = "-" if valor is None or valor == "" else str(valor)
            if len(texto) > max_chars:
                texto = texto[:max_chars - 1].rstrip() + "…"

            if nome == "Status":
                s = str(valor).strip().lower() if valor else ""
                if "disponivel" in s:
                    cor = cores.COR_SUCESSO
                elif "emprestado" in s or "manutenc" in s:
                    cor = cores.COR_AVISO
                else:
                    cor = cores.COR_TEXTO
            else:
                cor = cores.COR_TEXTO

            lbl = ctk.CTkLabel(item, text=texto, font=("Segoe UI", 14),
                               text_color=cor, anchor="center")
            lbl.grid(row=0, column=idx_col, sticky="ew", padx=(10, 4), pady=7)
            lbl.bind("<Button-1>", lambda e, it=item: self._selecionar(it))

        self._itens_lista.append((item, exc))

    def _selecionar(self, item):
        if not hasattr(item, "_dados"):
            return
        self._selecionado = item._dados

        for linha, exc in self._itens_lista:
            selecionado = linha == item
            dados_exibicao = [exc[1], exc[4], exc[2], exc[3]] if len(exc) > 4 else list(exc)

            if selecionado:
                linha.configure(fg_color=cores.COR_SEL)
                for widget in linha.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color="#FFFFFF", fg_color=cores.COR_SEL)
            else:
                linha.configure(fg_color=cores.COR_CARD)
                for i, widget in enumerate(linha.winfo_children()):
                    if isinstance(widget, ctk.CTkLabel):
                        if i == 2:  # coluna Status
                            s = str(dados_exibicao[2]).strip().lower() if len(dados_exibicao) > 2 else ""
                            if "disponivel" in s:
                                cor = cores.COR_SUCESSO
                            elif "emprestado" in s or "manutenc" in s:
                                cor = cores.COR_AVISO
                            else:
                                cor = cores.COR_TEXTO
                        else:
                            cor = cores.COR_TEXTO
                        widget.configure(text_color=cor, fg_color=cores.COR_CARD)

        try:
            self.lista_frame.update_idletasks()
        except Exception:
            pass

    # ── Ações ─────────────────────────────────────────────────────────────────
    def _adicionar(self):
        numero = self.entry_patrimonio.get().strip()
        localizacao = self.entry_localizacao.get().strip()

        if not self._livro_selecionado_id:
            self._notificar("Selecione um livro válido do catálogo.")
            return

        if not numero.isdigit() or len(numero) > 5:
            self._notificar("O código deve ser um número de até 5 dígitos (ex: 00001).")
            return

        patrimonio = f"PAT-{numero.zfill(5)}"

        ok, msg = validar_texto(localizacao, "Localização", min_len=3, obrigatorio=False)
        if not ok:
            self._notificar(msg)
            return

        if exemplar_patrimonio_duplicado(patrimonio, self._livro_selecionado_id):
            self._notificar("Já existe um exemplar com esse patrimônio para este livro!")
            return

        self.btn_adicionar.configure(text="Adicionando...", state="disabled")
        self._salvar_novo(patrimonio, self._livro_selecionado_id, localizacao)

    def _salvar_novo(self, patrimonio, id_livro, localizacao):
        if cadastrar_exemplar(patrimonio, id_livro, localizacao):
            titulo_livro = self.entry_busca_livro.get().split(" (")[0] if self.entry_busca_livro.get() else None
            gerar_codigo_barras(patrimonio, titulo_livro)
            self._notificar("Exemplar adicionado com sucesso!")
            self.entry_busca_livro.delete(0, "end")
            self._livro_selecionado_id = None
            self.entry_patrimonio.delete(0, "end")
            self.entry_localizacao.delete(0, "end")
            self._carregar_tabela()
        else:
            self._notificar("Erro ao salvar (código de patrimônio duplicado?).")
        self.btn_adicionar.configure(text="+ Adicionar", state="normal")

    def _editar_selecionado(self):
        if not self._selecionado:
            self._notificar("Selecione um exemplar para editar.")
            return

        exc = self._selecionado
        self._editando_id = exc[0]

        self.entry_localizacao.delete(0, "end")
        self.entry_localizacao.insert(0, exc[3] or "")
        self.entry_localizacao.focus()

        self.entry_busca_livro.configure(state="disabled")
        self.entry_patrimonio.configure(state="disabled")

        self.btn_adicionar.configure(text="💾 Salvar Edição", command=self._salvar_edicao)

    def _salvar_edicao(self):
        localizacao = self.entry_localizacao.get().strip()

        ok, msg = validar_texto(localizacao, "Localização", min_len=3, obrigatorio=False)
        if not ok:
            self._notificar(msg)
            return

        from services.database_config import _conectar
        from mysql.connector import Error
        try:
            conn = _conectar()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE exemplar SET localizacao=%s WHERE id_exemplar=%s",
                (localizacao or None, self._editando_id)
            )
            conn.commit()
            conn.close()
            self._notificar("Localização atualizada com sucesso!")
        except Error as e:
            self._notificar(f"Erro ao atualizar: {e}")

        self._editar_cancelar()

    def _editar_cancelar(self):
        self._editando_id = None
        self.btn_adicionar.configure(text="+ Adicionar", command=self._adicionar)
        self.entry_busca_livro.configure(state="normal")
        self.entry_patrimonio.configure(state="normal")
        self.entry_busca_livro.delete(0, "end")
        self.entry_patrimonio.delete(0, "end")
        self.entry_localizacao.delete(0, "end")
        self._livro_selecionado_id = None
        self._carregar_tabela()

    def _excluir_selecionado(self):
        if not self._selecionado:
            self._notificar("Selecione um exemplar na lista para excluir.")
            return

        id_exc = self._selecionado[0]
        status = str(self._selecionado[2]).strip().lower() if len(self._selecionado) > 2 else ""

        if "emprestado" in status:
            self._notificar("Não é possível excluir um exemplar com empréstimo ativo.")
            return
        if exemplar_tem_historico_emprestimo(id_exc):
            self._notificar("Não é possível excluir: exemplar tem histórico de empréstimos.")
            return

        if excluir_exemplar(id_exc):
            self._notificar("Exemplar excluído do acervo.")
            self._selecionado = None
            self._carregar_tabela()
        else:
            self._notificar(f"Erro ao excluir o exemplar {id_exc}.")

    def _ver_barcode(self):
        if not self._selecionado:
            self._notificar("Selecione um exemplar na lista.")
            return

        patrimonio = self._selecionado[1] if len(self._selecionado) > 1 else None
        titulo_livro = self._selecionado[4] if len(self._selecionado) > 4 else None
        if not patrimonio:
            self._notificar("Patrimônio não encontrado.")
            return

        caminho = regenerar_barcode(patrimonio, titulo_livro)
        if not caminho:
            self._notificar("Erro ao gerar código de barras.")
            return

        JanelaBarcode(self, patrimonio, caminho)

    def _imprimir_etiquetas(self):
        exemplares = listar_exemplares()
        if not exemplares:
            self._notificar("Nenhum exemplar cadastrado.")
            return

        lista_etiquetas = []
        for exc in exemplares:
            patrimonio = exc[1] if len(exc) > 1 else None
            titulo = exc[4] if len(exc) > 4 else None
            if patrimonio:
                lista_etiquetas.append((patrimonio, titulo))

        if not lista_etiquetas:
            self._notificar("Nenhum patrimônio encontrado.")
            return

        self._notificar("Gerando etiquetas...")
        self.btn_imprimir_etiquetas.configure(text="Gerando...", state="disabled")

        caminhos = gerar_pagina_etiquetas(lista_etiquetas)

        self.btn_imprimir_etiquetas.configure(text="🖨 Etiquetas", state="normal")

        if caminhos:
            self._notificar(f"{len(caminhos)} página(s) gerada(s)! Abrindo...")
            self._abrir_imagem(caminhos[0])
        else:
            self._notificar("Erro ao gerar etiquetas.")

    def _abrir_imagem(self, caminho):
        try:
            import subprocess, platform
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(caminho)
            elif sistema == "Darwin":
                subprocess.run(["open", caminho])
            else:
                subprocess.run(["xdg-open", caminho])
        except Exception as e:
            self._notificar(f"Erro ao abrir: {e}")

    def _voltar(self):
        if self.controller:
            self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(
            text=mensagem, text_color=cores.COR_DOURADO, font=("Segoe UI", 15, "bold")
        )
        self.lbl_notificacao.place(relx=0.5, rely=0.96, anchor="center")
        self.lbl_notificacao.bind("<Button-1>", lambda e: self.lbl_notificacao.configure(text=""))
        self._agendar_after(5000, lambda: self.lbl_notificacao.configure(text=""))