import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import listar_livros, listar_categorias
from services.styles import (
    cores, FONTE_TITULO, criar_entry, criar_label, criar_titulo, criar_card
)

COLUNAS = [
    ("TÍTULO",     5, 280, 36),
    ("ISBN",       2, 140, 16),
    ("CATEGORIA",  2, 140, 18),
    ("EDITORA",    2, 140, 18),
    ("ANO",        1,  60,  6),
    ("STATUS",     1,  90,  10),
]
COMPENSA_SCROLLBAR = 18


def _truncar(valor, max_chars):
    texto = "-" if valor is None or valor == "" else str(valor)
    if len(texto) <= max_chars:
        return texto
    return texto[: max_chars - 1].rstrip() + "…"


class CabecalhoCatalogo(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=cores.COR_SIDEBAR, corner_radius=0, **kw)
        for idx, (rotulo, peso, minsize, _) in enumerate(COLUNAS):
            self.grid_columnconfigure(idx, weight=peso, minsize=minsize)
            criar_label(self, rotulo, text_color=cores.COR_TEXTO,
                        anchor="center", font=("Segoe UI", 14, "bold")
                        ).grid(row=0, column=idx, sticky="ew", padx=(10, 4), pady=8)

class LinhaLivro(ctk.CTkFrame):
    def __init__(self, master, dados, indice, **kw):
        cor = cores.COR_LINHA_PAR if indice % 2 == 0 else cores.COR_LINHA_IMPAR
        super().__init__(master, fg_color=cor, corner_radius=0, **kw)

        id_livro, titulo, isbn, categoria, editora, ano, status, *_ = dados
        valores = [titulo, isbn, categoria, editora, ano, status]

        for idx, ((rotulo, peso, minsize, max_chars), valor) in enumerate(zip(COLUNAS, valores)):
            self.grid_columnconfigure(idx, weight=peso, minsize=minsize)
            texto = _truncar(valor, max_chars)
            if rotulo == "STATUS":
                s = str(valor).lower()
                if s == "disponivel":
                    cor_txt = cores.COR_SUCESSO
                elif s in ("emprestado", "manutencao"):
                    cor_txt = cores.COR_AVISO
                elif s in ("atrasado", "inativo", "cancelada"):
                    cor_txt = cores.COR_PERIGO
                else:
                    cor_txt = cores.COR_TEXTO2
            else:
                cor_txt = cores.COR_TEXTO
            ancora = "w" if rotulo == "TÍTULO" else "center"
            criar_label(self, texto, text_color=cor_txt, anchor=ancora,
                        font=("Segoe UI", 14)).grid(
                row=0, column=idx, sticky="ew", padx=(10, 4), pady=7
            )


class TelaCatalogo(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=cores.COR_BG)
        self.controller = controller
        self._todos_livros = []
        self._categorias   = []
        self._construir_ui()



    def _reconstruir_tema(self):
        """Reconstrói a tela ao trocar o tema claro/escuro."""
        if not self.winfo_exists():
            return
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=cores.COR_BG)
        self._construir_ui()

    def _ao_visitar(self):
        self._carregar_dados()

    def _construir_ui(self):
        # ── Cabeçalho ──
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=30, pady=(20, 10))

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        header_left = ctk.CTkFrame(topo, fg_color="transparent")
        header_left.pack(side="left", fill="y")

        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(180, 180))
                ctk.CTkLabel(header_left, image=img_logo, text="").pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")

        criar_label(header_left, "Catálogo de Livros", font=FONTE_TITULO,
                    text_color=cores.COR_TEXTO).pack(side="left")

        ctk.CTkButton(
            topo, text="Voltar", command=self._voltar, width=130, height=45,
            fg_color=cores.COR_SIDEBAR, text_color="#FFFFFF", border_color=cores.COR_INPUT_BORDER, border_width=1,
            hover_color=cores.COR_INPUT_BG, font=("Segoe UI", 16, "bold")
        ).pack(side="right")

        # ── Contador ──
        linha_contador = ctk.CTkFrame(self, fg_color="transparent")
        linha_contador.pack(fill="x", padx=30, pady=(0, 4))
        self.lbl_total = criar_label(linha_contador, "", text_color=cores.COR_TEXTO2)
        self.lbl_total.pack(side="right")

        # ── Filtros ──
        filtros = ctk.CTkFrame(self, fg_color="transparent")
        filtros.pack(fill="x", padx=30, pady=(0, 10))

        self.entry_titulo = criar_entry(filtros, placeholder="Buscar por título…", width=300, height=40)
        self.entry_titulo.pack(side="left", padx=(0, 10))
        self.entry_titulo.bind("<KeyRelease>", lambda e: self._filtrar())

        self.entry_categoria = criar_entry(filtros, placeholder="Filtrar por categoria…", width=220, height=40)
        self.entry_categoria.pack(side="left", padx=(0, 10))
        self.entry_categoria.bind("<KeyRelease>", lambda e: self._filtrar())

        ctk.CTkButton(
            filtros, text="↺ Limpar", width=100, height=40,
            fg_color=cores.COR_CARD, font=("Segoe UI", 15, "bold"),
            command=self._limpar
        ).pack(side="left")

        # ── Tabela ──
        CabecalhoCatalogo(self).pack(fill="x", padx=(30, 30 + COMPENSA_SCROLLBAR))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self._carregar_dados()

    def _carregar_dados(self):
        self._todos_livros = listar_livros()
        self._filtrar()

    def _filtrar(self):
        termo_titulo    = self.entry_titulo.get().strip().lower()
        termo_categoria = self.entry_categoria.get().strip().lower()

        resultado = [
            l for l in self._todos_livros
            if termo_titulo    in str(l[1]).lower()
            and termo_categoria in str(l[3]).lower()
        ]

        for w in self.scroll.winfo_children():
            w.destroy()

        for i, livro in enumerate(resultado):
            LinhaLivro(self.scroll, livro, i).pack(fill="x", pady=(0, 1))

        total = len(resultado)
        self.lbl_total.configure(
            text=f"{total} livro{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
        )

    def _limpar(self):
        self.entry_titulo.delete(0, "end")
        self.entry_categoria.delete(0, "end")
        self._filtrar()

    def _voltar(self):
        if self.controller:
            self.controller.voltar()