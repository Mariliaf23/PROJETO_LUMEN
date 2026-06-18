import os
import tkinter as tk
from PIL import Image, ImageTk
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connect import connect_to_database
from database_config import init_db

_PX1_R = 300 / 1280
_PX2_R = 1265 / 1280
_PY1_R = 68  / 832
_PY2_R = 680 / 832
_SIDE_R = 235 / 1280


class TelaCadastroAlunos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        init_db()
        self.title("Lumen – Cadastro de Alunos")
        self.geometry("960x680")
        self.minsize(800, 560)

        self.largura_atual = 0
        self.altura_atual  = 0

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

    # ------------------------------------------------------------------ #
    #  Widgets                                                             #
    # ------------------------------------------------------------------ #
    def _construir_ui(self):
        estilo = dict(
            font=("Segoe UI", 11),
            fg="#8a7e72",
            relief="flat",
            bd=0,
            insertbackground="white",
            bg="#2b1c0f",
            highlightthickness=1,
            highlightbackground="#4a3020",
            highlightcolor="#b89a72",
        )

        self.entry_nome     = tk.Entry(self.canvas, **estilo)
        self.entry_email    = tk.Entry(self.canvas, **estilo)
        self.entry_telefone = tk.Entry(self.canvas, **estilo)
        self.entry_cpf      = tk.Entry(self.canvas, **estilo)
        self.entry_sala     = tk.Entry(self.canvas, **estilo)
        self.entry_turno    = tk.Entry(self.canvas, **estilo)

        self._placeholder(self.entry_nome,     "João Silva")
        self._placeholder(self.entry_email,    "joao@email.com")
        self._placeholder(self.entry_telefone, "(91) 99999-9999")
        self._placeholder(self.entry_cpf,      "000.000.000-00")
        self._placeholder(self.entry_sala,     "Ex: 3")
        self._placeholder(self.entry_turno,    "Manhã / Tarde / Noite")

        self.btn_cadastrar = tk.Button(
            self.canvas,
            text="Cadastrar Aluno",
            font=("Segoe UI Semibold", 11),
            fg="#b89a72",
            activeforeground="#ffffff",
            activebackground="#b89a72",
            bg="#2b1c0f",
            bd=1,
            relief="solid",
            cursor="hand2",
            command=self._cadastrar,
        )

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

    # ------------------------------------------------------------------ #
    #  Sidebar                                                             #
    # ------------------------------------------------------------------ #
    def _desenhar_sidebar(self, L, A):
        side_x = int(L * _SIDE_R / 2)

        itens_nav = [
            ("DASHBOARD",     False),
            ("LIVROS",        False),
            ("MEMBROS",       True),
            ("EMPRÉSTIMOS",   False),
            ("DEVOLUÇÕES",    False),
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
            self.canvas.tag_bind(item, "<Enter>",    lambda e, t=item: self.canvas.itemconfig(t, fill="#d4b896"))
            self.canvas.tag_bind(item, "<Leave>",    lambda e, t=item, c=cor_txt: self.canvas.itemconfig(t, fill=c))
            self.canvas.tag_bind(item, "<Button-1>", lambda e, n=nome: print(f"Navegar: {n}"))
            y_nav += passo

    # ------------------------------------------------------------------ #
    #  Painel                                                              #
    # ------------------------------------------------------------------ #
    def _desenhar_painel(self, L, A):
        px1 = int(L * _PX1_R)
        px2 = int(L * _PX2_R)
        py1 = int(A * _PY1_R)
        py2 = int(A * _PY2_R)

        pw = px2 - px1
        ph = py2 - py1
        mx = px1 + 30
        aw = pw - 60

        # Painel escuro
        self.canvas.create_rectangle(px1, py1, px2, py2, fill="#1e1208", outline="")
        self.canvas.create_line(px1, py1, px2, py1, fill="#b89a72", width=1)

        # Título
        self.canvas.create_text(
            mx, py1 // 2 + A * 0.01,
            text="Cadastro de Alunos",
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
        self.canvas.tag_bind(btn_v, "<Enter>",  lambda e: self.canvas.itemconfig(btn_v, fill="#b89a72"))
        self.canvas.tag_bind(btn_v, "<Leave>",  lambda e: self.canvas.itemconfig(btn_v, fill="#8a7e72"))

        # --- Campos --------------------------------------------------- #
        h_entry  = 34
        espaco_v = int(ph * 0.14)

        larg_full = aw
        larg_meio = (aw - 20) // 2
        x1  = mx
        x_r = x1 + larg_meio + 20

        y0 = py1 + int(ph * 0.16)

        def campo(label, x, y, entry, largura):
            self.canvas.create_text(
                x, y - 26,
                text=label,
                font=("Segoe UI", 9),
                fill="#8a7e72",
                anchor="w",
            )
            self.canvas.create_window(
                x + largura // 2, y,
                window=entry,
                width=largura,
                height=h_entry,
            )

        campo("Nome",     x1,  y0,                self.entry_nome,     larg_full)
        campo("Email",    x1,  y0 + espaco_v,     self.entry_email,    larg_full)

        y2 = y0 + espaco_v * 2
        campo("Telefone", x1,  y2, self.entry_telefone, larg_meio)
        campo("CPF",      x_r, y2, self.entry_cpf,      larg_meio)

        y3 = y0 + espaco_v * 2 + int(ph * 0.15)
        campo("Sala",     x1,  y3, self.entry_sala,  larg_meio)
        campo("Turno",    x_r, y3, self.entry_turno, larg_meio)

        # Botão Cadastrar
        self.canvas.create_window(
            px2 - 30, y3 + int(ph * 0.13),
            window=self.btn_cadastrar,
            width=180, height=38,
            anchor="e",
        )

    # ------------------------------------------------------------------ #
    #  Lógica                                                              #
    # ------------------------------------------------------------------ #
    def _cadastrar(self):
        nome     = self._valor(self.entry_nome,     "João Silva")
        email    = self._valor(self.entry_email,    "joao@email.com")
        telefone = self._valor(self.entry_telefone, "(91) 99999-9999")
        cpf      = self._valor(self.entry_cpf,      "000.000.000-00")
        sala     = self._valor(self.entry_sala,      "Ex: 3")
        turno    = self._valor(self.entry_turno,    "Manhã / Tarde / Noite")

        if not nome:
            self._notificacao("Informe o nome do aluno.")
            return
        if not email:
            self._notificacao("Informe o e-mail do aluno.")
            return
        if not cpf:
            self._notificacao("Informe o CPF do aluno.")
            return

        self.btn_cadastrar.configure(text="⏳ Salvando...", state="disabled")
        self.after(400, lambda: self._salvar(nome, email, telefone, cpf, sala, turno))

    def _salvar(self, nome, email, telefone, cpf, sala, turno):
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alunos (nome, email, telefone, cpf, sala, turno)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, email, telefone, cpf, sala, turno))
            conn.commit()
            conn.close()
            self._notificacao(f"✓ Aluno «{nome}» cadastrado com sucesso!")
            self._limpar_campos()
        except Exception as erro:
            self._notificacao(f"✕ Erro ao cadastrar: {erro}")
        finally:
            self.btn_cadastrar.configure(text="Cadastrar Aluno", state="normal")

    # ------------------------------------------------------------------ #
    #  Utilitários                                                         #
    # ------------------------------------------------------------------ #
    def _valor(self, entry, placeholder):
        v = entry.get().strip()
        return "" if v == placeholder else v

    def _limpar_campos(self):
        pares = [
            (self.entry_nome,     "João Silva"),
            (self.entry_email,    "joao@email.com"),
            (self.entry_telefone, "(91) 99999-9999"),
            (self.entry_cpf,      "000.000.000-00"),
            (self.entry_sala,     "Ex: 3"),
            (self.entry_turno,    "Manhã / Tarde / Noite"),
        ]
        for entry, ph in pares:
            entry.delete(0, tk.END)
            entry.insert(0, ph)
            entry.configure(fg="#8a7e72")

    def _placeholder(self, entry, texto):
        entry.insert(0, texto)
        entry.configure(fg="#8a7e72")
        entry.bind("<FocusIn>",  lambda e: self._limpar_marcador(e, texto))
        entry.bind("<FocusOut>", lambda e: self._definir_marcador(e, texto))

    def _limpar_marcador(self, evento, marcador):
        if evento.widget.get() == marcador:
            evento.widget.delete(0, tk.END)
            evento.widget.configure(fg="#ffffff")

    def _definir_marcador(self, evento, marcador):
        if evento.widget.get() == "":
            evento.widget.insert(0, marcador)
            evento.widget.configure(fg="#8a7e72")

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
    app = TelaCadastroAlunos(master=raiz)
    app.mainloop()