import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
from services.conector import init_db
from services.database_config import cadastrar_aluno


class TelaCadastroAlunos(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        init_db()
        self.title("Lumen - Cadastro de Alunos")
        self.geometry("960x680")
        self.minsize(800, 580)

        self.largura_atual = 0
        self.altura_atual = 0

        caminho_fundo = os.path.join("assets", "Login.png")
        self.img_fundo = (
            Image.open(caminho_fundo).convert("RGB")
            if os.path.exists(caminho_fundo)
            else Image.new("RGB", (1920, 1080), "#1c1410")
        )

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg="#120c08")
        self.canvas.pack(fill="both", expand=True)

        self._referencias = {}
        self._construir_ui()
        self.bind("<Configure>", self._ao_redimensionar)

    def _construir_ui(self):
        estilo = dict(
            font=("Segoe UI", 12), fg="#8a7e72",
            relief="flat", bd=0, justify="center", insertbackground="white",
            bg="#120c08"
        )

        self.entry_nome = tk.Entry(self.canvas, **estilo)
        self._placeholder(self.entry_nome, "Nome completo")

        self.entry_email = tk.Entry(self.canvas, **estilo)
        self._placeholder(self.entry_email, "Email")

        self.entry_telefone = tk.Entry(self.canvas, **estilo)
        self._placeholder(self.entry_telefone, "Telefone")

        self.entry_cpf = tk.Entry(self.canvas, **estilo)
        self._placeholder(self.entry_cpf, "CPF")

        self.entry_sala = tk.Entry(self.canvas, **estilo)
        self._placeholder(self.entry_sala, "Sala")

        self.entry_turno = tk.Entry(self.canvas, **estilo)
        self._placeholder(self.entry_turno, "Turno")

        self.btn_cadastrar = tk.Button(
            self.canvas, text="Cadastrar Aluno", font=("Segoe UI Semibold", 12),
            fg="#b89a72", activeforeground="#ffffff", activebackground="#b89a72",
            bg="#120c08", bd=1, relief="solid", cursor="hand2", command=self._cadastrar
        )
        self.btn_cadastrar.bind("<Enter>", lambda e: self.btn_cadastrar.config(bg="#b89a72", fg="#120c08"))
        self.btn_cadastrar.bind("<Leave>", lambda e: self.btn_cadastrar.config(bg="#120c08", fg="#b89a72"))
        self.btn_cadastrar.bind("<ButtonPress-1>", lambda e: self.btn_cadastrar.config(bg="#d4b896", fg="#120c08"))
        self.btn_cadastrar.bind("<ButtonRelease-1>", lambda e: self.btn_cadastrar.config(bg="#b89a72", fg="#120c08"))

        self.rotulo_voltar = None

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
        fundo = fundo.filter(ImageFilter.GaussianBlur(radius=8))
        self._referencias["fundo"] = ImageTk.PhotoImage(fundo)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._referencias["fundo"])

        cx, cy = L // 2, A // 2

        self.canvas.create_text(cx, cy - 220, text="LUMEN", font=("Cinzel", 32, "bold"), fill="#b89a72")
        self.canvas.create_text(cx, cy - 165, text="Cadastro de Alunos", font=("Segoe UI Light", 12), fill="#ffffff")

        self.canvas.create_window(cx, cy - 115, window=self.entry_nome, width=280, height=35)
        self.canvas.create_window(cx, cy - 75, window=self.entry_email, width=280, height=35)
        self.canvas.create_window(cx, cy - 35, window=self.entry_telefone, width=280, height=35)
        self.canvas.create_window(cx, cy + 5, window=self.entry_cpf, width=280, height=35)
        self.canvas.create_window(cx, cy + 45, window=self.entry_sala, width=280, height=35)
        self.canvas.create_window(cx, cy + 85, window=self.entry_turno, width=280, height=35)
        self.canvas.create_window(cx, cy + 135, window=self.btn_cadastrar, width=280, height=40)

        self.rotulo_voltar = self.canvas.create_text(cx, cy + 190, text="Voltar", font=("Segoe UI", 10), fill="#8a7e72")
        self.canvas.tag_bind(self.rotulo_voltar, "<Button-1>", lambda e: self._efeito_clique_voltar())
        self.canvas.tag_bind(self.rotulo_voltar, "<Enter>", lambda e: self.canvas.itemconfig(self.rotulo_voltar, fill="#d4b896", font=("Segoe UI", 10, "underline")))
        self.canvas.tag_bind(self.rotulo_voltar, "<Leave>", lambda e: self.canvas.itemconfig(self.rotulo_voltar, fill="#8a7e72", font=("Segoe UI", 10)))

    def _efeito_clique_voltar(self):
        self.canvas.itemconfig(self.rotulo_voltar, fill="#ffffff")
        self.after(150, lambda: self.canvas.itemconfig(self.rotulo_voltar, fill="#d4b896"))
        self.after(300, self.destroy)

    def _placeholder(self, entry, texto):
        entry.insert(0, texto)
        entry.configure(fg="#8a7e72")
        entry.bind("<FocusIn>", lambda e: self._limpar_marcador(e, texto))
        entry.bind("<FocusOut>", lambda e: self._definir_marcador(e, texto))

    def _limpar_marcador(self, evento, marcador):
        if evento.widget.get() == marcador:
            evento.widget.delete(0, tk.END)
            evento.widget.configure(fg="#ffffff")

    def _definir_marcador(self, evento, marcador):
        if evento.widget.get() == "":
            evento.widget.insert(0, marcador)
            evento.widget.configure(fg="#8a7e72")

    def _valor(self, entry, placeholder):
        v = entry.get().strip()
        return "" if v == placeholder else v

    def _cadastrar(self):
        nome = self._valor(self.entry_nome, "Nome completo")
        email = self._valor(self.entry_email, "Email")
        telefone = self._valor(self.entry_telefone, "Telefone")
        cpf = self._valor(self.entry_cpf, "CPF")
        sala = self._valor(self.entry_sala, "Sala")
        turno = self._valor(self.entry_turno, "Turno")

        if not nome:
            self._notificacao("Informe o nome do aluno.")
            return
        if not email:
            self._notificacao("Informe o e-mail do aluno.")
            return
        if not cpf:
            self._notificacao("Informe o CPF do aluno.")
            return

        self.btn_cadastrar.configure(text="Carregando...", state="disabled")
        self.after(500, lambda: self._salvar(nome, email, telefone, cpf, sala, turno))

    def _salvar(self, nome, email, telefone, cpf, sala, turno):
        sucesso = cadastrar_aluno(nome, email, telefone, cpf, sala, turno)
        if sucesso:
            self._notificacao("Aluno cadastrado com sucesso!")
            self._limpar_campos()
        else:
            self._notificacao("Erro ao cadastrar aluno.")
        self.btn_cadastrar.configure(text="Cadastrar Aluno", state="normal")

    def _limpar_campos(self):
        for entry, ph in [
            (self.entry_nome, "Nome completo"), (self.entry_email, "Email"),
            (self.entry_telefone, "Telefone"), (self.entry_cpf, "CPF"),
            (self.entry_sala, "Sala"), (self.entry_turno, "Turno"),
        ]:
            entry.delete(0, tk.END)
            entry.insert(0, ph)
            entry.configure(fg="#8a7e72")

    def _notificacao(self, mensagem):
        rotulo = tk.Label(self, text=mensagem, font=("Segoe UI", 11), fg="#ffffff", bg="#3d2c20", padx=20, pady=8)
        rotulo.place(relx=0.5, rely=0.92, anchor="center")
        self.after(2500, rotulo.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = TelaCadastroAlunos(master=root)
    app.mainloop()
    root.destroy()
