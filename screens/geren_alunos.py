import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sys

from screens.cadastro_alunos import _PX1_R, _PX2_R, _PY1_R, _PY2_R, _SIDE_R
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connect import connect_to_database
from database_config import init_db

class TelaListaAlunos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        init_db()
        self.title("Lumen – Alunos Cadastrados")
        self.geometry("960x680")
        self.minsize(800, 560)
        
        self.largura_atual = 0
        self.altura_atual = 0
        
        caminho_fundo = os.path.join("assets", "cadastro_membros.png")
        self.img_fundo = (
            Image.open(caminho_fundo).convert("RGB")
            if os.path.exists(caminho_fundo)
            else Image.new("RGB", (1280, 832), "#1c1410")
        )
        
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg="#0d0905")
        self.canvas.pack(fill="both", expand=True)
        
        self._referencias = {}
        self._construir_ui()
        self.bind("<Configure>", self._ao_redimensionar)
        self.carregar_dados()

    def _construir_ui(self):
        self.tree = ttk.Treeview(
            self.canvas,
            columns=("ID", "CPF", "Nome", "Email", "Telefone", "Data Cadastro", "Status"),
            show="headings",
            height=15,
        )
        
        # Configure as colunas
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=0, stretch=False)  # esconder ID
        
        self.tree.heading("CPF", text="CPF")
        self.tree.column("CPF", anchor="center", width=120)
        
        self.tree.heading("Nome", text="Nome")
        self.tree.column("Nome", anchor="w", width=200)
        
        self.tree.heading("Email", text="Email")
        self.tree.column("Email", anchor="w", width=200)
        
        self.tree.heading("Telefone", text="Telefone")
        self.tree.column("Telefone", anchor="center", width=120)
        
        self.tree.heading("Data Cadastro", text="Data Cadastro")
        self.tree.column("Data Cadastro", anchor="center", width=120)
        
        # Botão Editar
        self.btn_editar = tk.Button(
            self.canvas,
            text="Editar Aluno",
            font=("Segoe UI Semibold", 11),
            fg="#b89a72", activeforeground="#ffffff",
            activebackground="#b89a72",
            bg="#2b1c0f", bd=1, relief="solid",
            cursor="hand2",
            command=self.editar_aluno,
        )
        
        # Botão Atualizar
        self.btn_atualizar = tk.Button(
            self.canvas,
            text="Atualizar Lista",
            font=("Segoe UI Semibold", 10),
            fg="#b89a72", activeforeground="#ffffff",
            activebackground="#b89a72",
            bg="#2b1c0f", bd=1, relief="solid",
            cursor="hand2",
            command=self.carregar_dados,
        )

    def _desenhar_painel(self, L, A):
        # Coordenadas proporcionais ao tamanho da janela
        px1 = int(L * _PX1_R)
        px2 = int(L * _PX2_R)
        py1 = int(A * _PY1_R)
        py2 = int(A * _PY2_R) 

        pw  = px2 - px1   # largura do painel
        ph  = py2 - py1   # altura do painel
        mx  = px1 + 30    # margem interna esquerda
        aw  = pw - 60     # largura útil dos campos

        # Painel escuro (mesmo tom da imagem) para cobrir uniformemente
        self.canvas.create_rectangle(px1, py1, px2, py2, fill="#1e1208", outline="")

        # Linha dourada no topo do painel
        self.canvas.create_line(px1, py1, px2, py1, fill="#b89a72", width=1)

        # --- Título --------------------------------------------------- #
        self.canvas.create_text(
            mx , py1 // 2 + A * 0.01,
            text="Cadastro de Alunos",
            font=("Segoe UI Light", 15),
            fill="#ffffff",
            anchor='w'
        )

        # --- Botão Voltar --------------------------------------------- #
        btn_v = self.canvas.create_text(
            mx, py1 + 30,
            text="← Voltar",
            font=("Segoe UI", 10),
            fill="#8a7e72",
            anchor="w",
        )
        self.canvas.tag_bind(btn_v, "<Button-1>", lambda e: self.destroy())
        self.canvas.tag_bind(btn_v, "<Enter>",  lambda e: self.canvas.itemconfig(btn_v, fill="#b89a72"))
        self.canvas.tag_bind(btn_v, "<Leave>",  lambda e: self.canvas.itemconfig(btn_v, fill="#8a7e72"))

        # --- Campos --------------------------------------------------- #
        h_entry  = 34
        # Espaço vertical distribuído proporcionalmente à altura do painel
        espaco_v = int(ph * 0.26)

        larg_full = aw
        larg_meio = (aw - 20) // 2
        x1  = mx
        x_r = x1 + larg_meio + 20

        # Primeiro campo: 18% da altura do painel abaixo do topo
        y0 = py1 + int(ph * 0.22)

        def campo( x, y, entry, largura):
            self.canvas.create_window(
                x + largura // 2, y,
                window=entry,
                width=largura,
                height=h_entry,
            )

            # TreeView
            self.canvas.create_window(
                px1 + pw // 2, py1 + int(ph * 0.55),
                window=self.tree,
                width=pw - 60, height=150,
            )

            # Botões editar / excluir / atualizar
            
            campo("Nome",     x1,  y0,            self.entry_nome,     larg_full)
            campo("Email",    x1,  y0 + espaco_v, self.entry_email,    larg_full)

            y2 = y0 + espaco_v * 2
            campo("Telefone", x1,  y2, self.entry_telefone, larg_meio)
            campo("CPF",      x_r, y2, self.entry_cpf,      larg_meio)

            y3 = y0 + espaco_v * 2 + int(ph * 0.15)
            campo("Sala",     x1,  y3, self.entry_sala,  larg_meio)
            campo("Turno",    x_r, y3, self.entry_turno, larg_meio)

            # Botão cadastrar — alinhado à direita, dentro do painel
        self.canvas.create_window(
            px2 - 30, y3 + int(ph * 0.13),
            window=self.btn_cadastrar,
            width=180, height=38,
            anchor="e",
        )
        self.canvas.create_window(mx, py2 - 40, window=self.btn_atualizar, width=100, height=30, anchor="w")
        self.canvas.create_window(mx + 110, py2 - 40, window=self.btn_editar, width=100, height=30, anchor="w")
        self.canvas.create_window(mx + 220, py2 - 40, window=self.btn_excluir, width=100, height=30, anchor="w")

    def _desenhar_sidebar(self, L, A):
        side_x = int(L * _SIDE_R / 2)   # centro horizontal da sidebar

        itens_nav = [
            ("DASHBOARD",    False),
            ("LIVROS",       False),
            ("MEMBROS",      True),
            ("EMPRÉSTIMOS",  False),
            ("DEVOLUÇÕES",   False),
            ("CONFIGURAÇÕES",False),
        ]

        y_nav = int(A * 0.32)
        passo = int(A * 0.085)

        for nome, ativo in itens_nav:
            cor_txt = "#c8a96e" if ativo else "#7a6a58"
            if ativo:
                # Destaque sutil no item ativo — retângulo pequeno e transparente
                self.canvas.create_rectangle(
                    4, y_nav - 12,
                    int(L * _SIDE_R) - 4, y_nav + 12,
                    fill="#2a1a08", outline="", stipple="gray50"
                )
            item = self.canvas.create_text(
                side_x, y_nav,
                text=nome,
                font=("Segoe UI", 9),
                fill=cor_txt,
            )
            self.canvas.tag_bind(item, "<Enter>",    lambda e, t=item: self.canvas.itemconfig(t, fill="#d4b896"))
            self.canvas.tag_bind(item, "<Leave>",    lambda e, t=item, c=cor_txt: self.canvas.itemconfig(t, fill=c))
            self.canvas.tag_bind(item, "<Button-1>", lambda e, n=nome: print(f"Navegar: {n}"))
            y_nav += passo

        self._referencias["side_x"] = side_x

