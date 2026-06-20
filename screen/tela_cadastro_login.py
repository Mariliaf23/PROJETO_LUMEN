import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
from services.database_config import cadastrar_funcionario


class LumenLoginApp(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("LUMEN - Cadastrar")
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
        estilo_entry = dict(
            font=("Segoe UI", 12), fg="#8a7e72",
            relief="flat", bd=0, justify="center", insertbackground="white",
            bg="#120c08"
        )

        self.entry_nome = tk.Entry(self.canvas, **estilo_entry)
        self._placeholder(self.entry_nome, "Nome completo")

        self.entry_email = tk.Entry(self.canvas, **estilo_entry)
        self._placeholder(self.entry_email, "Email")

        self.entry_senha = tk.Entry(self.canvas, **estilo_entry)
        self._placeholder_senha(self.entry_senha, "Senha")

        self.entry_confirm = tk.Entry(self.canvas, **estilo_entry)
        self._placeholder_senha(self.entry_confirm, "Confirmar senha")

        self.btn_cadastrar = tk.Button(
            self.canvas, text="Cadastrar", font=("Segoe UI Semibold", 12),
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

        self.canvas.create_text(cx, cy - 160, text="LUMEN", font=("Cinzel", 32, "bold"), fill="#b89a72")
        self.canvas.create_text(cx, cy - 105, text="Criar conta", font=("Segoe UI Light", 12), fill="#ffffff")

        self.canvas.create_window(cx, cy - 55, window=self.entry_nome, width=280, height=35)
        self.canvas.create_window(cx, cy - 15, window=self.entry_email, width=280, height=35)
        self.canvas.create_window(cx, cy + 25, window=self.entry_senha, width=280, height=35)
        self.canvas.create_window(cx, cy + 65, window=self.entry_confirm, width=280, height=35)
        self.canvas.create_window(cx, cy + 115, window=self.btn_cadastrar, width=280, height=40)

        self.rotulo_voltar = self.canvas.create_text(cx, cy + 170, text="Ja tem conta? Entrar", font=("Segoe UI", 10), fill="#8a7e72")
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

    def _placeholder_senha(self, entry, texto):
        entry.insert(0, texto)
        entry.configure(fg="#8a7e72")
        entry.bind("<FocusIn>", lambda e: self._limpar_marcador_senha(e, texto))
        entry.bind("<FocusOut>", lambda e: self._definir_marcador_senha(e, texto))

    def _limpar_marcador_senha(self, evento, marcador):
        if evento.widget.get() == marcador:
            evento.widget.delete(0, tk.END)
            evento.widget.configure(fg="#ffffff", show="*")

    def _definir_marcador_senha(self, evento, marcador):
        if evento.widget.get() == "":
            evento.widget.configure(show="")
            evento.widget.insert(0, marcador)
            evento.widget.configure(fg="#8a7e72")

    def _cadastrar(self):
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()
        confirm = self.entry_confirm.get().strip()

        if not nome or nome == "Nome completo":
            self._notificacao("Informe o nome.")
            return
        if not email or email == "Email":
            self._notificacao("Informe o email.")
            return
        if not senha or senha == "Senha":
            self._notificacao("Informe a senha.")
            return
        if senha != confirm:
            self._notificacao("As senhas nao conferem.")
            return

        self.btn_cadastrar.configure(text="Carregando...", state="disabled")
        self.after(500, lambda: self._salvar(nome, email, senha))

    def _salvar(self, nome, email, senha):
        sucesso = cadastrar_funcionario(nome, email, senha)
        if sucesso:
            self._notificacao("Cadastro realizado com sucesso!")
            self.after(1500, self.destroy)
        else:
            self._notificacao("Erro ao salvar no banco de dados.")
            self.btn_cadastrar.configure(text="Cadastrar", state="normal")

    def _notificacao(self, mensagem):
        rotulo = tk.Label(self, text=mensagem, font=("Segoe UI", 11), fg="#ffffff", bg="#3d2c20", padx=20, pady=8)
        rotulo.place(relx=0.5, rely=0.92, anchor="center")
        self.after(2500, rotulo.destroy)


if __name__ == "__main__":
    app = LumenLoginApp()
    app.mainloop()
