import sys
sys.path.insert(0, '.')
with open('screen/tela_livros.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remover botao de teste
marker = '''        # === BOTÃO TESTE RENDERIZAÇÃO ===
        self.btn_teste = ctk.CTkButton(
            botoes_container, text="🧪 Teste Renderização",
            command=self._toggle_modo_renderizacao,
            width=220, height=50,
            fg_color="#065F46", text_color="#FFFFFF",
            hover_color="#047857", font=("Segoe UI", 16, "bold")
        )
        self.btn_teste.pack(side="left", padx=10)
        self._modo_teste = False  # Modo original (scroll) ativado'''

if marker in content:
    content = content.replace(marker, '')
    print("OK: Botao de teste removido")
else:
    print("AVISO: Botao de teste nao encontrado (ja pode ter sido removido)")

# 2. Remover metodo _toggle_modo_renderizacao
old_toggle = '''    def _toggle_modo_renderizacao(self):
        """Alterna entre modo original (CTkScrollableFrame) e modo teste (CTkFrame comum)"""
        self._modo_teste = not self._modo_teste
        modo = "SIMPLE (sem scroll)" if self._modo_teste else "SCROLL (original)"
        print(f"\\n[MODO TESTE] Alterado para: {modo}")
        self._carregar_tabela()

    '''

if old_toggle in content:
    content = content.replace(old_toggle, '')
    print("OK: Metodo _toggle_modo_renderizacao removido")
else:
    print("AVISO: _toggle nao encontrado")

# 3. Aplicar correcao do place() nos itens
old_criar = '''    def _criar_item(self, livro, idx=0):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=6, height=48)
        item.pack(fill="x", pady=4)
        item.pack_propagate(False)
        item.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))

        dados = livro[1:] if len(livro) > 6 else livro

        item.grid_columnconfigure(0, weight=30)
        item.grid_columnconfigure(1, weight=18)
        item.grid_columnconfigure(2, weight=15)
        item.grid_columnconfigure(3, weight=15)
        item.grid_columnconfigure(4, weight=8)
        item.grid_columnconfigure(5, weight=14)

        for i, nome_col in enumerate(["Titulo", "ISBN", "Categoria", "Editora", "Ano", "Status"]):
            if i < len(dados):
                texto = dados[i]
                cor_txt = COR_TEXTO
                if i == 5:
                    status = str(texto).lower()
                    cor_txt = COR_DOURADO if "dispon" in status else COR_TEXTO2
                lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 15), text_color=cor_txt, anchor="w", padx=8)
                lbl.grid(row=0, column=i, sticky="ew", padx=(4, 0))
                lbl.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))

        self._itens_lista.append((item, livro))'''

new_criar = '''    def _criar_item(self, livro, idx=0):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=6, height=48)
        item.place(x=0, y=idx * 52, relwidth=1.0, height=48)
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
                    font=("Segoe UI", 15), text_color=cor_txt, anchor="w", padx=8
                )
                lbl.place(relx=x_atual, rely=0.5, anchor="w", relwidth=proporcoes[i] - 0.01)
                lbl.bind("<Button-1>", lambda e, l=livro: self._selecionar(l))
                x_atual += proporcoes[i]

        self._itens_lista.append((item, livro))'''

if old_criar in content:
    content = content.replace(old_criar, new_criar)
    print("OK: _criar_item atualizado com place()")
else:
    print("FALHA: _criar_item antigo nao encontrado")

with open('screen/tela_livros.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Arquivo salvo!")
