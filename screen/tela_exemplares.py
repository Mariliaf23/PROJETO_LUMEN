import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import (
    listar_livros, listar_exemplares, cadastrar_exemplar,
    excluir_exemplar, atualizar_status_exemplar
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    criar_entry, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame, criar_combo
)


class TelaExemplares(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._itens_lista = []
        self._selecionado = None
        self._livros_map = {}
        self._construir_ui()

    def _ao_visitar(self):
        self._carregar_livros()
        self._carregar_tabela()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === HEADER COM LOGO OFICIAL AMPLADA ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 15))

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")
        
        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y")

        # Logo expandida para 85x85 para destaque ideal
        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(85, 85))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")

        # Título com fonte aumentada para 26
        criar_label(header_left, "|  Gerenciar Exemplares", font=("Segoe UI", 26, "bold"), text_color=COR_TEXTO).pack(side="left")

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

        # Campo Seleção de Livro (Fontes de labels e inputs em 16px)
        lbl_livro = criar_label(form_frame, "Livro Vinculado", font=("Segoe UI", 16, "bold"))
        lbl_livro.grid(row=0, column=0, sticky="w", pady=(0, 4))
        
        self.combo_livro = criar_combo(form_frame, height=50, values=[])
        self.combo_livro.configure(font=("Segoe UI", 16))
        self.combo_livro.grid(row=1, column=0, padx=(0, 15), pady=(0, 12), sticky="ew")
        self.combo_livro.set("Selecione o livro")

        # Campo Código Patrimônio
        lbl_patrimonio = criar_label(form_frame, "Código Patrimônio", font=("Segoe UI", 16, "bold"))
        lbl_patrimonio.grid(row=0, column=1, sticky="w", pady=(0, 4))

        self.entry_patrimonio = criar_entry(form_frame, placeholder="Ex: PAT-00124", height=50)
        self.entry_patrimonio.configure(font=("Segoe UI", 16))
        self.entry_patrimonio.grid(row=1, column=1, padx=(15, 0), pady=(0, 12), sticky="ew")

        # Campo Localização
        lbl_localizacao = criar_label(form_frame, "Localização no Acervo", font=("Segoe UI", 16, "bold"))
        lbl_localizacao.grid(row=2, column=0, sticky="w", pady=(6, 4))

        self.entry_localizacao = criar_entry(form_frame, placeholder="Ex: Estante B, Prateleira 3", height=50)
        self.entry_localizacao.configure(font=("Segoe UI", 16))
        self.entry_localizacao.grid(row=3, column=0, padx=(0, 15), pady=(0, 12), sticky="ew")

        # Frame de Ações (Alinhamento perfeito ao lado da localização)
        botoes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botoes_frame.grid(row=3, column=1, padx=(15, 0), pady=(15, 0), sticky="ew")

        # Botão Adicionar - AZUL PURO SÓLIDO (Sem tom pastel)
        self.btn_adicionar = ctk.CTkButton(
            botoes_frame, text="Adicionar Exemplar", command=self._adicionar,
            width=220, height=50, 
            fg_color="#0052CC", text_color="#FFFFFF",
            hover_color="#003399", font=("Segoe UI", 16, "bold")
        )
        self.btn_adicionar.pack(side="left", padx=(0, 15))

        # Botão Excluir - VERMELHO ESCURO SÓLIDO
        self.btn_excluir = ctk.CTkButton(
            botoes_frame, text="Excluir Selecionado", command=self._excluir_selecionado,
            width=220, height=50, 
            fg_color="#7F1D1D", text_color="#FCA5A5",
            hover_color="#991B1B", font=("Segoe UI", 16, "bold")
        )
        self.btn_excluir.pack(side="left")

        # === TABELA DE EXIBIÇÃO DE EXEMPLARES ===
        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 25))

        # Distribuição das colunas
        self._proporcoes_colunas = [0.18, 0.42, 0.16, 0.24]
        colunas_nomes = ["Patrimônio", "Livro", "Status", "Localização"]

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent", height=45)
        header_lista.pack(fill="x", padx=20, pady=(15, 5))
        header_lista.pack_propagate(False)

        # Renderização do cabeçalho com fonte 14
        for i, (txt, pct) in enumerate(zip(colunas_nomes, self._proporcoes_colunas)):
            rel_x = sum(self._proporcoes_colunas[:i])
            lbl = criar_label(header_lista, txt, font=("Segoe UI", 14, "bold"), text_color=COR_DOURADO, anchor="w")
            lbl.place(relx=rel_x, rely=0.5, anchor="w", relwidth=pct - 0.01)

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

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
        else:
            self.combo_livro.set("Selecione o livro")

    def _carregar_tabela(self, exemplares=None):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        self._itens_lista.clear()

        if exemplares is None:
            exemplares = listar_exemplares()
        for exc in exemplares:
            self._criar_item(exc)

        if not exemplares:
            empty = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
            empty.pack(fill="both", expand=True)
            criar_label(empty, "Nenhum exemplar catalogado neste acervo.", font=("Segoe UI", 16)).pack(expand=True)

    def _criar_item(self, exc):
        # Linha da tabela maior (height=48) e fontes internas maiores (15px)
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=6, height=48)
        item.pack(fill="x", pady=4)
        item.pack_propagate(False)

        item.bind("<Button-1>", lambda e, v=exc: self._selecionar(v))

        dados_exibicao = exc[1:] if len(exc) > 4 else exc

        for i, pct in enumerate(self._proporcoes_colunas):
            if i < len(dados_exibicao):
                texto = dados_exibicao[i]
                rel_x = sum(self._proporcoes_colunas[:i])
                
                cor = COR_TEXTO
                if i == 2:  # Coluna Status
                    status_limpo = str(texto).strip().lower()
                    if "emprestado" in status_limpo:
                        cor = COR_DOURADO
                    elif "manutencao" in status_limpo or "manutenção" in status_limpo:
                        cor = "#EF4444"
                    else:
                        cor = "#10B981" # Verde puro para disponível

                lbl = ctk.CTkLabel(
                    item, 
                    text=str(texto) if texto is not None else "-", 
                    font=("Segoe UI", 15), 
                    text_color=cor, 
                    anchor="w"
                )
                lbl.place(relx=rel_x + 0.005, rely=0.5, anchor="w", relwidth=pct - 0.01)
                lbl.bind("<Button-1>", lambda e, v=exc: self._selecionar(v))

        self._itens_lista.append((item, exc))

    def _selecionar(self, exc):
        for item, e in self._itens_lista:
            # Highlight azul marinho profundo ao selecionar a linha
            item.configure(fg_color="#0F172A" if e == exc else COR_CARD)
        self._selecionado = exc

    def _adicionar(self):
        livro_sel = self.combo_livro.get()
        patrimonio = self.entry_patrimonio.get().strip()
        localizacao = self.entry_localizacao.get().strip()

        if not livro_sel or livro_sel == "Selecione o livro" or livro_sel not in self._livros_map:
            self._notificar("Selecione um livro válido do catálogo.")
            return
        if not patrimonio:
            self._notificar("Informe o código de patrimônio do exemplar.")
            return

        id_livro = self._livros_map[livro_sel]

        self.btn_adicionar.configure(text="Adicionando...", state="disabled")
        self.after(300, lambda: self._salvar(patrimonio, id_livro, localizacao))

    def _salvar(self, patrimonio, id_livro, localizacao):
        sucesso = cadastrar_exemplar(patrimonio, id_livro, localizacao)
        if sucesso:
            self._notificar("Exemplar adicionado com sucesso!")
            self.entry_patrimonio.delete(0, "end")
            self.entry_localizacao.delete(0, "end")
            self._carregar_tabela()
        else:
            self._notificar("Erro ao salvar (Código de patrimônio duplicado?).")
        self.btn_adicionar.configure(text="Adicionar Exemplar", state="normal")

    def _excluir_selecionado(self):
        if not self._selecionado:
            self._notificar("Selecione um exemplar na lista para excluir.")
            return
            
        id_exc = self._selecionado[0]
        status = str(self._selecionado[2]).strip().lower() if len(self._selecionado) > 2 else ""
        
        if "emprestado" in status:
            self._notificar("Não é possível excluir um exemplar com empréstimo ativo.")
            return
            
        sucesso = excluir_exemplar(id_exc)
        if sucesso:
            self._notificar("Exemplar excluído do acervo.")
            self._selecionado = None
            self._carregar_tabela()
        else:
            self._notificar("Erro ao excluir o exemplar.")

    def _voltar(self):
        if self.controller and hasattr(self.controller, 'voltar'):
            self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color=COR_DOURADO, font=("Segoe UI", 15, "bold"))
        self.lbl_notificacao.place(relx=0.5, rely=0.96, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))