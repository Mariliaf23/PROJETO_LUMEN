import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connect import connect_to_database
from database_config import init_db

_PX1_R = 300 / 1280
_PX2_R = 1265 / 1280
_PY1_R = 68 / 832
_PY2_R = 680 / 832
_SIDE_R = 235 / 1280


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
        self.after(200, self.carregar_dados)

    # ------------------------------------------------------------------ #
    # Widgets                                                             #
    # ------------------------------------------------------------------ #
    def _construir_ui(self):
        # Estilo da TreeView no tom marrom do Lumen
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Lumen.Treeview",
            background="#1e1208",
            foreground="#c8a96e",
            fieldbackground="#1e1208",
            rowheight=26,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Lumen.Treeview.Heading",
            background="#2b1c0f",
            foreground="#b89a72",
            font=("Segoe UI Semibold", 9),
            relief="flat",
        )
        style.map("Lumen.Treeview", background=[("selected", "#4a3020")])

        self.tree = ttk.Treeview(
            self.canvas,
            style="Lumen.Treeview",
            columns=("ID", "CPF", "Nome", "Email", "Telefone", "Sala", "Turno", "Cadastro"),
            show="headings",
        )

        colunas = {
            "ID": (0, False),
            "CPF": (120, True),
            "Nome": (180, True),
            "Email": (180, True),
            "Telefone": (110, True),
            "Turma": (60, True),
            "Turno": (80, True),
            "Cadastro": (100, True),
        }
        for col, (w, visivel) in colunas.items():
            self.tree.heading(col, text=col)
            if visivel:
                self.tree.column(col, anchor="center", width=w)
            else:
                self.tree.column(col, width=0, stretch=False)

        estilo_btn = dict(
            font=("Segoe UI Semibold", 10),
            fg="#b89a72",
            activeforeground="#ffffff",
            activebackground="#b89a72",
            bg="#2b1c0f",
            bd=1,
            relief="solid",
            cursor="hand2",
        )
        self.btn_atualizar = tk.Button(self.canvas, text="↻ Atualizar", command=self.carregar_dados, **estilo_btn)
        self.btn_editar = tk.Button(self.canvas, text="✎ Editar", command=self.editar_aluno, **estilo_btn)
        self.btn_excluir = tk.Button(self.canvas, text="✕ Excluir", command=self.excluir_aluno, **estilo_btn)

    # ------------------------------------------------------------------ #
    # Redimensionar                                                       #
    # ------------------------------------------------------------------ #
    def _ao_redimensionar(self, evento=None):
        L = self.winfo_width()
        A = self.winfo_height()

        if L < 100 or A < 100:
            return
        if L == self.largura_atual and A == self.altura_atual:
            return
        self.largura_atual = L
        self.altura_atual = A

        fundo = self.img_fundo.resize((L, A), Image.Resampling.LANCZOS)
        self._referencias["fundo"] = ImageTk.PhotoImage(fundo)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._referencias["fundo"])

        self._desenhar_sidebar(L, A)
        self._desenhar_painel(L, A)

    # ------------------------------------------------------------------ #
    # Sidebar                                                             #
    # ------------------------------------------------------------------ #
    def _desenhar_sidebar(self, L, A):
        side_x = int(L * _SIDE_R / 2)

        itens_nav = [
            ("DASHBOARD", False),
            ("LIVROS", False),
            ("MEMBROS", False),
            ("ALUNOS", True),
            ("EMPRÉSTIMOS", False),
            ("DEVOLUÇÕES", False),
            ("CONFIGURAÇÕES", False),
        ]

        y_nav = int(A * 0.32)
        passo = int(A * 0.085)

        for nome, ativo in itens_nav:
            cor_txt = "#c8a96e" if ativo else "#7a6a58"
            if ativo:
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
            self.canvas.tag_bind(item, "<Enter>", lambda e, t=item: self.canvas.itemconfig(t, fill="#d4b896"))
            self.canvas.tag_bind(item, "<Leave>", lambda e, t=item, c=cor_txt: self.canvas.itemconfig(t, fill=c))
            self.canvas.tag_bind(item, "<Button-1>", lambda e, n=nome: print(f"Navegar: {n}"))
            y_nav += passo

    # ------------------------------------------------------------------ #
    # Painel                                                              #
    # ------------------------------------------------------------------ #
    def _desenhar_painel(self, L, A):
        px1 = int(L * _PX1_R)
        px2 = int(L * _PX2_R)
        py1 = int(A * _PY1_R)
        py2 = int(A * _PY2_R)

        pw = px2 - px1
        ph = py2 - py1
        mx = px1 + 30

        # Painel escuro
        self.canvas.create_rectangle(px1, py1, px2, py2, fill="#1e1208", outline="")
        self.canvas.create_line(px1, py1, px2, py1, fill="#b89a72", width=1)

        # Título
        self.canvas.create_text(
            mx, py1 // 2 + A * 0.01,
            text="Alunos Cadastrados",
            font=("Segoe UI Light", 15),
            fill="#ffffff",
            anchor="w",
        )

        # Botão Voltar
        btn_v = self.canvas.create_text(
            mx, py1 + 28,
            text="← Voltar",
            font=("Segoe UI", 10),
            fill="#8a7e72",
            anchor="w",
        )
        self.canvas.tag_bind(btn_v, "<Button-1>", lambda e: self.destroy())
        self.canvas.tag_bind(btn_v, "<Enter>", lambda e: self.canvas.itemconfig(btn_v, fill="#b89a72"))
        self.canvas.tag_bind(btn_v, "<Leave>", lambda e: self.canvas.itemconfig(btn_v, fill="#8a7e72"))

        # TreeView — ocupa a maior parte do painel
        tree_y = py1 + 70
        tree_h = py2 - tree_y - 55
        self.canvas.create_window(
            px1 + pw // 2, tree_y + tree_h // 2,
            window=self.tree,
            width=pw - 60,
            height=tree_h,
        )

        # Botões na base do painel
        self.canvas.create_window(mx, py2 - 25, window=self.btn_atualizar, width=120, height=30, anchor="w")
        self.canvas.create_window(mx + 130, py2 - 25, window=self.btn_editar, width=120, height=30, anchor="w")
        self.canvas.create_window(mx + 260, py2 - 25, window=self.btn_excluir, width=120, height=30, anchor="w")

    # ------------------------------------------------------------------ #
    # Dados                                                               #
    # ------------------------------------------------------------------ #
    def carregar_dados(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
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
        except Exception as e:
            print(f"Erro ao carregar alunos: {e}")

    def editar_aluno(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um aluno para editar.")
            return
        valores = self.tree.item(sel[0])["values"]
        messagebox.showinfo("Aluno", f"Nome: {valores[2]}\nCPF: {valores[1]}\nEmail: {valores[3]}")

    def excluir_aluno(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um aluno para excluir.")
            return
        valores = self.tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirmar", f"Excluir aluno «{valores[2]}»?"):
            try:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM alunos WHERE id=%s", (valores[0],))
                conn.commit()
                conn.close()
                self.carregar_dados()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def _notificacao(self, mensagem):
        rotulo = tk.Label(
            self, text=mensagem,
            font=("Segoe UI", 11), fg="#ffffff",
            bg="#3d2c20", padx=20, pady=8,
        )
        rotulo.place(relx=0.5, rely=0.93, anchor="center")
        self.after(2500, rotulo.destroy)


if __name__ == "__main__":
    raiz = tk.Tk()
    raiz.withdraw()
    app = TelaListaAlunos(master=raiz)
    app.mainloop()