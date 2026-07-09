import sys
sys.path.insert(0, '.')
with open('screen/tela_livros.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corrigir indentação do _criar_item (4 espacos -> 8 espacos)
old = '''    def _criar_item(self, livro, idx=0):
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

new = '''        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=6, height=48)
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

# Primeiro, remover o def errado
if '    def _criar_item(self, livro, idx=0):' in content:
    # Remover a linha do def e substituir pelo corpo correto
    content = content.replace(old, '    def _criar_item(self, livro, idx=0):\n' + new)
    print("OK: Indentacao corrigida")
else:
    print("FALHA: def _criar_item nao encontrado")

with open('screen/tela_livros.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Arquivo salvo!")
