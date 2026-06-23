# # import tkinter as tk 
# # from PIL import Image, ImageTk
# # janela=tk.Tk()
# # janela.title("Teste")
# # janela.geometry("800x700")
# # imagem_backgraud = Image.open("assets/login fundo.jpg")
# # imagem_redimencionada = imagem_backgraud.resize((800,700))
# # bg_imagem = ImageTk.PhotoImage(imagem_redimencionada)
# # label_imagem = tk.Label(janela, image=bg_imagem)
# # label_imagem.place(relx=0, rely=0, relwidth=1, relheight=1)
# # label_imagem.image = bg_imagem

# # janela.mainloop()

# import tkinter as tk
# from tkinter import font as tkfont
# from PIL import Image, ImageTk

# class LumenApp:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.root.title("LUMEN - Biblioteca")
#         self.root.geometry("1200x700")
#         self.root.configure(bg="#1a140f")
#         self.root.resizable(False, False)

#         # Cores
#         self.bg_color = "#1a140f"
#         self.sidebar_bg = "#0f0a07"
#         self.text_color = "#e8d5b8"
#         self.hover_color = "#3c2a1f"
#         self.active_color = "#d4a373"

#         # ==================== Imagem de Fundo ====================
#         try:
#             self.bg_image = Image.open("/home/workdir/attachments/Captura de tela 2026-06-15 193119.png")
#             self.bg_image = self.bg_image.resize((1200, 700), Image.Resampling.LANCZOS)
#             self.bg_photo = ImageTk.PhotoImage(self.bg_image)
#         except:
#             self.bg_photo = None

#         self.canvas = tk.Canvas(self.root, width=1200, height=700, highlightthickness=0, bg=self.bg_color)
#         self.canvas.pack(fill="both", expand=True)

#         if self.bg_photo:
#             self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

#         # ==================== Sidebar ====================
#         self.sidebar = tk.Frame(self.root, bg=self.sidebar_bg, width=280, height=700)
#         self.sidebar.place(x=0, y=0)

#         # Logo LUMEN
#         logo_font = tkfont.Font(family="Georgia", size=32, weight="bold")
#         self.logo = tk.Label(self.sidebar, text="LUMEN", font=logo_font, 
#                             fg="#d4b38a", bg=self.sidebar_bg)
#         self.logo.pack(pady=(60, 80))

#         # Menu Items
#         self.create_menu_button("DASHBOARD", 0, active=True)
#         self.create_menu_button("LIVROS", 1)
#         self.create_menu_button("MEMBROS", 2)
#         self.create_menu_button("EMPRÉSTIMOS", 3)
#         self.create_menu_button("DEVOLUÇÕES", 4)
#         self.create_menu_button("CONFIGURAÇÕES", 5)

#         # Rodapé da sidebar
#         footer = tk.Label(self.sidebar, text="Biblioteca LUMEN © 2026", 
#                          font=("Arial", 9), fg="#6b5a47", bg=self.sidebar_bg)
#         footer.pack(side="bottom", pady=30)

#         self.root.mainloop()

#     def create_menu_button(self, text, index, active=False):
#         btn = tk.Label(self.sidebar, text=text, font=("Arial", 12, "bold"),
#                       fg=self.text_color if not active else "#1a140f",
#                       bg=self.active_color if active else self.sidebar_bg,
#                       width=25, height=2, anchor="w", padx=40)
        
#         btn.pack(pady=2)
        
#         # Hover effect
#         def on_enter(e):
#             if not active:
#                 btn.config(bg=self.hover_color)
#         def on_leave(e):
#             if not active:
#                 btn.config(bg=self.sidebar_bg)
        
#         btn.bind("<Enter>", on_enter)
#         btn.bind("<Leave>", on_leave)
        
#         # Clique (exemplo)
#         btn.bind("<Button-1>", lambda e, t=text: self.menu_click(t))

#     def menu_click(self, menu):
#         print(f"Menu clicado: {menu}")
#         # Aqui você pode trocar o conteúdo da área principal


# if __name__ == "__main__":
#     # pip install pillow
#     app = LumenApp()

import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from screens.cadastro_alunos import _PX1_R, _PX2_R, _PY1_R, _PY2_R, _SIDE_R
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

        self.tree.heading("Status", text="Status")
        self.tree.column("Status", anchor="center", width=80)

    # ------------------------------------------------------------------ #
    #  Redimensionar                                                       #
    # ------------------------------------------------------------------ #
    def _ao_redimensionar(self, evento=None):
        L = self.winfo_width()
        A = self.winfo_height()

        if L < 100 or A < 100:
            return
        if L == self.largura_atual and A == self.altura_atual:
            return
        self.largura_atual = L
        self.altura_atual  = A

        fundo = self.img_fundo.resize((L, A), Image.Resampling.LANCZOS)
        self._referencias["fundo"] = ImageTk.PhotoImage(fundo)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._referencias["fundo"])

        self._desenhar_sidebar(L, A)
        self._desenhar_painel(L, A)



    def _desenhar_painel(self, L, A):
        px1 = int(L * _PX1_R)
        px2 = int(L * _PX2_R)
        py1 = int(A * _PY1_R)
        py2 = int(A * _PY2_R)
        pw = px2 - px1
        ph = py2 - py1
        mx = px1 + 30

        self.canvas.create_rectangle(px1, py1, px2, py2, fill="#1e1208", outline="")
        self.canvas.create_line(px1, py1, px2, py1, fill="#b89a72", width=1)

        self.canvas.create_text(
            mx, py1 + 20,
            text="Alunos Cadastrados",
            font=("Segoe UI Light", 15),
            fill="#ffffff", anchor="w",
        )

        # Voltar
        btn_v = self.canvas.create_text(
            mx, py1 + 50,
            text="← Voltar",
            font=("Segoe UI", 10),
            fill="#8a7e72", anchor="w",
        )
        self.canvas.tag_bind(btn_v, "<Button-1>", lambda e: self.destroy())
        self.canvas.tag_bind(btn_v, "<Enter>", lambda e: self.canvas.itemconfig(btn_v, fill="#b89a72"))
        self.canvas.tag_bind(btn_v, "<Leave>", lambda e: self.canvas.itemconfig(btn_v, fill="#8a7e72"))

        # TreeView
        self.canvas.create_window(
            px1 + pw // 2, py1 + ph // 2 + 20,
            window=self.tree,
            width=pw - 60, height=ph - 120,
        )

        # Botões
        self.canvas.create_window(
            mx, py2 - 30,
            window=self.btn_atualizar, width=130, height=35, anchor="w",
        )
        self.canvas.create_window(
            px2 - 30, py2 - 30,
            window=self.btn_editar, width=130, height=35, anchor="e",
        )
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

    def carregar_dados(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, cpf, nome, email, telefone, 
                DATE_FORMAT(criado_em, '%d/%m/%Y'), status
            FROM alunos
            ORDER BY nome
        """)
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def editar_aluno(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um aluno.")
            return
        
        valores = self.tree.item(sel[0])['values']
        messagebox.showinfo(
            "Aluno Selecionado",
            f"Nome: {valores[2]}\nCPF: {valores[1]}\nEmail: {valores[3]}"
        )

if __name__ == "__main__":
    raiz = tk.Tk()
    raiz.withdraw()
    app = TelaListaAlunos(master=raiz)
    app.mainloop()





