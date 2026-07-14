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
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    criar_entry, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame, criar_combo, aplicar_validacao_focusout
)
from services.validador import validar_patrimonio, validar_texto

COR_SEL        = "#1D4ED8"
COR_VERDE      = "#10B981"   # disponivel
COR_AMARELO    = "#EAB308"   # emprestado, manutencao
COR_VERMELHO   = "#EF4444"   # (reservado para uso futuro)

COLUNAS_EXEMPLARES = [
    ("Patrimônio",  2, 140, 16),
    ("Livro",       4, 280, 35),
    ("Status",      2, 140, 12),
    ("Localização", 2, 140, 18),
]
COMPENSA_SCROLLBAR = 18


class JanelaBarcode(ctk.CTkToplevel):
    """Janela para visualizar e imprimir código de barras do exemplar."""
    def __init__(self, master, patrimonio, caminho_imagem):
        super().__init__(master)
        self.title(f"Código de Barras - {patrimonio}")
        self.geometry("350x420")
        self.resizable(False, False)
        self.configure(fg_color=COR_BG)
        self.grab_set()

        # Logo
        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")
        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(50, 50))
                ctk.CTkLabel(self, image=img_logo, text="").pack(pady=(15, 5))
            except:
                pass

        criar_titulo(self, "LUMEN", font=("Cinzel", 18, "bold"), text_color="#1E3A8A").pack()

        criar_label(self, "Código de Barras", font=("Segoe UI", 14, "bold"),
                    text_color=COR_TEXTO).pack(pady=(5, 10))

        # Card com barcode
        card = criar_card(self)
        card.pack(fill="x", padx=30, pady=(0, 10))

        try:
            img = Image.open(caminho_imagem)
            # Redimensiona para caber na janela
            largura_max = 300
            ratio = largura_max / img.width
            nova_altura = int(img.height * ratio)
            img = img.resize((largura_max, nova_altura), Image.LANCZOS)

            img_ctk = ctk.CTkImage(img, size=(largura_max, nova_altura))
            lbl_img = ctk.CTkLabel(card, image=img_ctk, text="")
            lbl_img.pack(padx=20, pady=15)
            lbl_img.image = img_ctk  # Referência para não ser coletado pelo GC
        except Exception as e:
            criar_label(card, f"Erro ao carregar imagem: {e}",
                        font=("Segoe UI", 12), text_color="#EF4444").pack(pady=20)

        # Código abaixo do barcode
        criar_label(self, patrimonio, font=("Consolas", 16, "bold"),
                    text_color=COR_TEXTO).pack(pady=(0, 15))

        # Botões
        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.pack(pady=(0, 15))

        ctk.CTkButton(
            botoes, text="Imprimir", width=120, height=36,
            fg_color="#1E3A8A", hover_color="#1D4ED8",
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._imprimir(caminho_imagem, patrimonio)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes, text="Fechar", width=120, height=36,
            fg_color="#333", hover_color="#444",
            font=("Segoe UI", 13, "bold"),
            command=self.destroy
        ).pack(side="left")

    def _imprimir(self, caminho_imagem, patrimonio):
        """Abre a imagem com o visualizador padrão do sistema para impressão."""
        try:
            import subprocess
            import platform

            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(caminho_imagem)
            elif sistema == "Darwin":  # macOS
                subprocess.run(["open", caminho_imagem])
            else:  # Linux
                subprocess.run(["xdg-open", caminho_imagem])
        except Exception as e:
            criar_label(self, f"Erro ao abrir: {e}",
                        font=("Segoe UI", 11), text_color="#EF4444").pack()


class TelaExemplares(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller      = controller
        self._itens_lista    = []
        self._selecionado    = None
        self._livros_map     = {}
        self._editando_id    = None
        self._construir_ui()

    def _ao_visitar(self):
        self._carregar_livros()
        self._carregar_tabela()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header compactado (mesmo padrão da tela de livros)
        header = ctk.CTkFrame(self, fg_color=COR_CARD)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 8))

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path    = os.path.join(caminho_base, "assets", "logo_lumen.png")

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y", padx=10, pady=5)

        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(55, 55))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))

        criar_label(header_left, "Gerenciamento de Exemplares",
                    font=("Segoe UI", 24, "bold"), text_color=COR_TEXTO).pack(side="left")

        ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=100, height=36,
            fg_color="#0F172A", text_color="#FFFFFF", border_color=COR_INPUT_BORDER, border_width=1,
            hover_color="#1E293B", font=("Segoe UI", 14, "bold")
        ).pack(side="right", padx=15, pady=5)

        # Formulário compactado
        form_card = criar_card(self)
        form_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(5, 10))

        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=12)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        ALTURA_INPUT = 36
        FONTE_INPUT = ("Segoe UI", 14)

        criar_label(form_frame, "Livro Vinculado", font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 2))

        livro_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        livro_container.grid(row=1, column=0, padx=(0, 10), pady=(0, 6), sticky="ew")
        livro_container.grid_columnconfigure(0, weight=1)

        self.entry_busca_livro = criar_entry(livro_container, placeholder="Digite o título do livro…", height=ALTURA_INPUT)
        self.entry_busca_livro.configure(font=FONTE_INPUT)
        self.entry_busca_livro.grid(row=0, column=0, sticky="ew")
        self.entry_busca_livro.bind("<KeyRelease>", self._atualizar_sugestoes)
        self.entry_busca_livro.bind("<FocusOut>", lambda e: self.after(150, self._esconder_sugestoes))

        self._frame_sugestoes = ctk.CTkScrollableFrame(
            livro_container, fg_color="#1E293B", height=120, corner_radius=8
        )
        self._livro_selecionado_id = None

        criar_label(form_frame, "Código Patrimônio", font=("Segoe UI", 13, "bold")).grid(
            row=0, column=1, sticky="w", pady=(0, 2))

        patrimonio_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        patrimonio_container.grid(row=1, column=1, padx=(10, 0), pady=(0, 6), sticky="ew")
        patrimonio_container.grid_columnconfigure(1, weight=1)

        # Prefixo PAT-
        lbl_prefixo = ctk.CTkLabel(patrimonio_container, text="PAT-", font=("Segoe UI", 14, "bold"),
                                    text_color="#1E3A8A", width=50)
        lbl_prefixo.grid(row=0, column=0, padx=(0, 2))

        self.entry_patrimonio = criar_entry(patrimonio_container, placeholder="00001", height=ALTURA_INPUT)
        self.entry_patrimonio.configure(font=FONTE_INPUT)
        self.entry_patrimonio.grid(row=0, column=1, sticky="ew")

        criar_label(form_frame, "Localização no Acervo", font=("Segoe UI", 13, "bold")).grid(
            row=2, column=0, sticky="w", pady=(4, 2))
        self.entry_localizacao = criar_entry(form_frame, placeholder="Ex: Estante B, Prateleira 3", height=ALTURA_INPUT)
        self.entry_localizacao.configure(font=FONTE_INPUT)
        self.entry_localizacao.grid(row=3, column=0, padx=(0, 10), pady=(0, 0), sticky="ew")

        # Botões compactados
        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.grid(row=3, column=1, padx=(10, 0), sticky="ew")
        botoes_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        BTN_H = ALTURA_INPUT
        BTN_FONT = ("Segoe UI", 12, "bold")

        self.btn_adicionar = ctk.CTkButton(
            botoes_frame, text="+ Adicionar", command=self._adicionar,
            height=BTN_H, fg_color="#0052CC", text_color="#FFFFFF",
            hover_color="#003399", font=BTN_FONT
        )
        self.btn_adicionar.grid(row=0, column=0, padx=(0, 3), sticky="ew")

        self.btn_editar = ctk.CTkButton(
            botoes_frame, text="✎ Editar", command=self._editar_selecionado,
            height=BTN_H, fg_color="#0F172A", text_color="#FFFFFF",
            border_color=COR_INPUT_BORDER, border_width=1,
            hover_color="#1E293B", font=BTN_FONT
        )
        self.btn_editar.grid(row=0, column=1, padx=(0, 3), sticky="ew")

        self.btn_barcode = ctk.CTkButton(
            botoes_frame, text="⊞ Barcode", command=self._ver_barcode,
            height=BTN_H, fg_color="#065F46", text_color="#FFFFFF",
            hover_color="#047857", font=BTN_FONT
        )
        self.btn_barcode.grid(row=0, column=2, padx=(0, 3), sticky="ew")

        self.btn_imprimir_etiquetas = ctk.CTkButton(
            botoes_frame, text="🖨 Etiquetas", command=self._imprimir_etiquetas,
            height=BTN_H, fg_color="#7C3AED", text_color="#FFFFFF",
            hover_color="#6D28D9", font=BTN_FONT
        )
        self.btn_imprimir_etiquetas.grid(row=0, column=3, padx=(0, 3), sticky="ew")

        self.btn_excluir = ctk.CTkButton(
            botoes_frame, text="✕ Excluir", command=self._excluir_selecionado,
            height=BTN_H, fg_color="#7F1D1D", text_color="#FCA5A5",
            hover_color="#991B1B", font=BTN_FONT
        )
        self.btn_excluir.grid(row=0, column=4, sticky="ew")

        # Tabela
        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(5, 20))

        # Barra de busca da tabela
        busca_frame = ctk.CTkFrame(lista_card, fg_color="transparent")
        busca_frame.pack(fill="x", padx=20, pady=(12, 0))

        self.entry_filtro = criar_entry(busca_frame, placeholder="Buscar na lista por patrimônio, livro ou localização…", height=34)
        self.entry_filtro.configure(font=("Segoe UI", 13))
        self.entry_filtro.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_filtro.bind("<KeyRelease>", lambda e: self._filtrar_tabela())

        ctk.CTkButton(
            busca_frame, text="↺ Limpar", width=90, height=34,
            fg_color="#333", font=("Segoe UI", 13, "bold"),
            command=self._limpar_filtro
        ).pack(side="left")

        # Cabeçalho da tabela (grid)
        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_lista.pack(fill="x", padx=(20, 20 + COMPENSA_SCROLLBAR), pady=(8, 2))

        for idx, (nome, peso, minsize, max_chars) in enumerate(COLUNAS_EXEMPLARES):
            header_lista.grid_columnconfigure(idx, weight=peso, minsize=minsize)
            criar_label(header_lista, nome.upper(), font=("Segoe UI", 12, "bold"),
                        text_color=COR_TEXTO, anchor="center"
                        ).grid(row=0, column=idx, sticky="ew", padx=(10, 4), pady=8)

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

        # ── Label único de erro flutuante ──
        self._lbl_erro_campo = criar_label(form_card, "", font=("Segoe UI", 12))
        self._lbl_erro_campo.place(relx=0.01, rely=0.97, anchor="sw")

        _entries = [self.entry_patrimonio, self.entry_localizacao]
        aplicar_validacao_focusout(self.entry_patrimonio,  lambda v: validar_patrimonio(v),                                        self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_localizacao, lambda v: validar_texto(v, "Localização", min_len=3, obrigatorio=False), self._lbl_erro_campo, _entries)

    # ── dados ─────────────────────────────────────────────────────────────────
    def _carregar_livros(self):
        livros = listar_livros()
        self._livros_map = {}
        self._livros_lista = []
        for l in livros:
            texto = f"{l[1]} ({l[2]})"
            self._livros_map[texto] = l[0]
            self._livros_lista.append(texto)

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
                fg_color="transparent", text_color=COR_TEXTO,
                hover_color="#1D4ED8", font=("Segoe UI", 14),
                height=36, corner_radius=4,
                command=lambda t=texto: self._escolher_livro(t)
            )
            btn.pack(fill="x", pady=1)

    def _escolher_livro(self, texto):
        self._livro_selecionado_id = self._livros_map[texto]
        self.entry_busca_livro.delete(0, "end")
        self.entry_busca_livro.insert(0, texto)
        self._esconder_sugestoes()

        # Auto-preenche o próximo patrimônio para este livro
        proximo = obter_proximo_patrimonio(self._livro_selecionado_id)
        # Remove o prefixo "PAT-" para o campo de entrada
        self.entry_patrimonio.delete(0, "end")
        self.entry_patrimonio.insert(0, proximo.replace("PAT-", ""))

    def _esconder_sugestoes(self):
        self._frame_sugestoes.grid_forget()

    def _carregar_tabela(self, exemplares=None):
        for w in self.lista_frame.winfo_children():
            w.destroy()
        self._itens_lista.clear()
        self._selecionado = None

        if exemplares is None:
            self._todos_exemplares = listar_exemplares()
            exemplares = self._todos_exemplares
        self._renderizar(exemplares)

    def _renderizar(self, exemplares):
        for w in self.lista_frame.winfo_children():
            w.destroy()
        self._itens_lista.clear()
        self._selecionado = None

        if not exemplares:
            criar_label(self.lista_frame, "Nenhum exemplar encontrado.",
                        font=("Segoe UI", 14), text_color=COR_TEXTO).pack(pady=30)
            return
        for exc in exemplares:
            self._criar_item(exc)
        self.lista_frame.update_idletasks()

    def _filtrar_tabela(self):
        termo = self.entry_filtro.get().strip().lower()
        if not termo:
            self._renderizar(self._todos_exemplares)
            return
        resultado = [
            e for e in self._todos_exemplares
            if termo in str(e[1]).lower()
            or termo in str(e[4]).lower()
            or termo in str(e[3]).lower()
        ]
        self._renderizar(resultado)
        if resultado:
            self._selecionar(self._itens_lista[0][1])

    def _limpar_filtro(self):
        self.entry_filtro.delete(0, "end")
        self._renderizar(self._todos_exemplares)
        if self._itens_lista:
            self._selecionar(self._itens_lista[0][1])

    def _criar_item(self, exc):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=6, height=40)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)
        item._dados = exc
        item.bind("<Button-1>", lambda e, it=item: self._selecionar(it))

        # [id, codigo_patrimonio, status_exemplar, localizacao, titulo]
        dados_exibicao = [exc[1], exc[4], exc[2], exc[3]] if len(exc) > 4 else exc

        for idx_col, (nome, peso, minsize, max_chars) in enumerate(COLUNAS_EXEMPLARES):
            item.grid_columnconfigure(idx_col, weight=peso, minsize=minsize)
            valor = dados_exibicao[idx_col] if idx_col < len(dados_exibicao) else None
            texto = "-" if valor is None or valor == "" else str(valor)
            if len(texto) > max_chars:
                texto = texto[:max_chars - 1].rstrip() + "…"
            if nome == "Status":
                s = str(valor).strip().lower() if valor else ""
                if "disponivel" in s:
                    cor = COR_VERDE
                elif "emprestado" in s or "manutenc" in s:
                    cor = COR_AMARELO
                else:
                    cor = COR_TEXTO
            else:
                cor = COR_TEXTO
            lbl = ctk.CTkLabel(item, text=texto, font=("Segoe UI", 14), text_color=cor, anchor="center")
            lbl.grid(row=0, column=idx_col, sticky="ew", padx=(10, 4), pady=7)
            lbl.bind("<Button-1>", lambda e, it=item: self._selecionar(it))

        self._itens_lista.append((item, exc))

    # ── seleção (mesmo esquema da tela de livros) ─────────────────────────────
    def _selecionar(self, item):
        self._selecionado = item._dados

        for linha, exc in self._itens_lista:
            selecionado = linha == item
            dados_exibicao = [exc[1], exc[4], exc[2], exc[3]] if len(exc) > 4 else exc

            if selecionado:
                linha.configure(fg_color=COR_SEL)
                for widget in linha.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color="#FFFFFF", fg_color=COR_SEL)
            else:
                linha.configure(fg_color=COR_CARD)
                for i, widget in enumerate(linha.winfo_children()):
                    if isinstance(widget, ctk.CTkLabel):
                        if i == 2:
                            s = str(dados_exibicao[2]).strip().lower()
                            if "disponivel" in s:
                                cor = COR_VERDE
                            elif "emprestado" in s or "manutenc" in s:
                                cor = COR_AMARELO
                            else:
                                cor = COR_TEXTO
                        else:
                            cor = COR_TEXTO
                        widget.configure(text_color=cor, fg_color=COR_CARD)

        self.lista_frame.update_idletasks()

    # ── ações ─────────────────────────────────────────────────────────────────
    def _adicionar(self):
        numero = self.entry_patrimonio.get().strip()
        localizacao = self.entry_localizacao.get().strip()

        if not self._livro_selecionado_id:
            self._notificar("Selecione um livro válido do catálogo.")
            return

        # Valida o número (deve ter até 5 dígitos)
        if not numero.isdigit() or len(numero) > 5:
            self._notificar("O código deve ser um número de até 5 dígitos (ex: 00001).")
            return

        # Monta o patrimônio completo com prefixo
        patrimonio = f"PAT-{numero.zfill(5)}"

        ok, msg = validar_texto(localizacao, "Localização", min_len=3, obrigatorio=False)
        if not ok:
            self._notificar(msg); return
        if exemplar_patrimonio_duplicado(patrimonio, self._livro_selecionado_id):
            self._notificar("Já existe um exemplar com esse patrimônio para este livro!")
            return

        self.btn_adicionar.configure(text="Adicionando...", state="disabled")
        self._salvar_novo(patrimonio, self._livro_selecionado_id, localizacao)

    def _salvar_novo(self, patrimonio, id_livro, localizacao):
        if cadastrar_exemplar(patrimonio, id_livro, localizacao):
            # Obtém o título do livro para o barcode
            titulo_livro = self.entry_busca_livro.get().split(" (")[0] if self.entry_busca_livro.get() else None
            # Gera o código de barras automaticamente
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

        # Preenche apenas o campo de localização
        self.entry_localizacao.delete(0, "end")
        self.entry_localizacao.insert(0, exc[3] or "")
        self.entry_localizacao.focus()

        # Desabilita outros campos
        self.entry_busca_livro.configure(state="disabled")
        self.entry_patrimonio.configure(state="disabled")

        self.btn_adicionar.configure(text="💾 Salvar Edição", command=self._salvar_edicao)

    def _salvar_edicao(self):
        localizacao = self.entry_localizacao.get().strip()

        ok, msg = validar_texto(localizacao, "Localização", min_len=3, obrigatorio=False)
        if not ok:
            self._notificar(msg); return

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
        """Cancela a edição e restaura o estado normal."""
        self._editando_id = None
        self.btn_adicionar.configure(text="+ Adicionar", command=self._adicionar)

        # Reabilita os campos
        self.entry_busca_livro.configure(state="normal")
        self.entry_patrimonio.configure(state="normal")

        # Limpa os campos
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
        """Abre janela com o código de barras do exemplar selecionado."""
        if not self._selecionado:
            self._notificar("Selecione um exemplar na lista.")
            return

        patrimonio = self._selecionado[1] if len(self._selecionado) > 1 else None
        titulo_livro = self._selecionado[4] if len(self._selecionado) > 4 else None
        if not patrimonio:
            self._notificar("Patrimônio não encontrado.")
            return

        # Regenera o barcode com o título
        caminho = regenerar_barcode(patrimonio, titulo_livro)
        if not caminho:
            self._notificar("Erro ao gerar código de barras.")
            return

        # Abre janela de visualização
        JanelaBarcode(self, patrimonio, caminho)

    def _imprimir_etiquetas(self):
        """Gera e abre páginas de etiquetas para todos os exemplares disponíveis."""
        # Busca todos os exemplares com seu livro
        exemplares = listar_exemplares()

        if not exemplares:
            self._notificar("Nenhum exemplar cadastrado.")
            return

        # Prepara a lista de (patrimonio, titulo)
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

        # Gera as páginas
        caminhos = gerar_pagina_etiquetas(lista_etiquetas)

        self.btn_imprimir_etiquetas.configure(text="🖨 Etiquetas", state="normal")

        if caminhos:
            self._notificar(f"{len(caminhos)} página(s) gerada(s)! Abrindo...")
            # Abre a primeira página
            self._abrir_imagem(caminhos[0])
        else:
            self._notificar("Erro ao gerar etiquetas.")

    def _abrir_imagem(self, caminho):
        """Abre a imagem com o visualizador padrão do sistema."""
        try:
            import subprocess
            import platform

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
        self.lbl_notificacao.configure(text=mensagem, text_color=COR_DOURADO, font=("Segoe UI", 15, "bold"))
        self.lbl_notificacao.place(relx=0.5, rely=0.96, anchor="center")
        self.lbl_notificacao.bind("<Button-1>", lambda e: self.lbl_notificacao.configure(text=""))
        self.after(5000, lambda: self.lbl_notificacao.configure(text=""))
