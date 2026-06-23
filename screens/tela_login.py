# This file is like the front door of our clubhouse. 
# It asks for your name and a secret password before letting you in!

import os
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter
import sys

# This helps the computer find the path to our other toy boxes, like a map of the house.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_config import init_db, verificar_login


# This class is like a drawing of our login screen.
class TelaLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        # We start our database, which is like opening our big book of secrets.
        init_db()
        self.title("Lumen")
        # We set the size of our window, like picking the size of our paper.
        self.geometry("960x680")
        self.minsize(800, 580)

        self.largura_atual = 0
        self.altura_atual = 0

        # We look for a pretty picture to use as a background.
        caminho_fundo = os.path.join("assets", "Login.png")
        self.img_fundo = Image.open(caminho_fundo).convert("RGB") if os.path.exists(caminho_fundo) else Image.new("RGB", (1920, 1080), "#1c1410")

        # This canvas is like an empty board where we can draw anything!
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg="#120c08")
        self.canvas.pack(fill="both", expand=True)

        self._referencias = {}
        # We start building all the buttons and boxes on our screen.
        self._construir_ui()

        # This tells the computer to redraw everything if we change the window size.
        self.bind("<Configure>", self._ao_redimensionar)

    def _construir_ui(self):
        # This is the box where you type your name.
        self.entry_usuario = tk.Entry(
            self.canvas, font=("Segoe UI", 12), fg="#8a7e72",
            relief="flat", bd=0, justify="center", insertbackground="white",
            bg="#120c08"
        )
        self.entry_usuario.insert(0, "seu.usuario")
        # These help the box show or hide "seu.usuario" when you click it.
        self.entry_usuario.bind("<FocusIn>", lambda e: self._limpar_marcador(e, "seu.usuario"))
        self.entry_usuario.bind("<FocusOut>", lambda e: self._definir_marcador(e, "seu.usuario"))

        # This is the secret box where you type your password. It shows stars instead of letters!
        self.entry_senha = tk.Entry(
            self.canvas, show="*", font=("Segoe UI", 12), fg="#8a7e72",
            relief="flat", bd=0, justify="center", insertbackground="white",
            bg="#120c08"
        )
        self.entry_senha.insert(0, "********")
        self.entry_senha.bind("<FocusIn>", lambda e: self._limpar_marcador(e, "********"))
        self.entry_senha.bind("<FocusOut>", lambda e: self._definir_marcador(e, "********"))

        # This is the "Enter" button. It's like the handle on the door!
        self.btn_entrar = tk.Button(
            self.canvas, text="Entrar", font=("Segoe UI Semibold", 12),
            # These colors make the button look pretty when you hover over it.
            fg="#b89a72", activeforeground="#ffffff", activebackground="#b89a72",
            bg="#120c08", bd=1, relief="solid", cursor="hand2", command=self._entrar
        )

    def _ao_redimensionar(self, evento=None):
        # This function acts like a camera lens, adjusting the picture when the window changes size.
        L = self.winfo_width()
        A = self.winfo_height()

        if L < 100 or A < 100:
            return

        if L == self.largura_atual and A == self.altura_atual:
            return
        self.largura_atual = L
        self.altura_atual = A

        # We make the background picture fit the screen and add a little bit of magic blur.
        fundo = self.img_fundo.resize((L, A), Image.Resampling.LANCZOS)
        fundo = fundo.filter(ImageFilter.GaussianBlur(radius=8))
        self._referencias["fundo"] = ImageTk.PhotoImage(fundo)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._referencias["fundo"])

        cx, cy = L // 2, A // 2

        # We draw the name of our app and some helpful text.
        self.canvas.create_text(cx, cy - 130, text="LUMEN", font=("Cinzel", 32, "bold"), fill="#b89a72")
        self.canvas.create_text(cx, cy - 75, text="Iniciar sessao", font=("Segoe UI Light", 12), fill="#ffffff")

        # We place our name box, password box, and button right in the middle.
        self.canvas.create_window(cx, cy - 15, window=self.entry_usuario, width=280, height=35)
        self.canvas.create_window(cx, cy + 35, window=self.entry_senha, width=280, height=35)
        self.canvas.create_window(cx, cy + 95, window=self.btn_entrar, width=280, height=40)

        # This is a little text you can click if you don't have a name in our book yet.
        rotulo_registrar = self.canvas.create_text(cx, cy + 155, text="Nao tem conta? Registar", font=("Segoe UI", 10), fill="#8a7e72")
        self.canvas.tag_bind(rotulo_registrar, "<Button-1>", lambda e: print("Navegar para registro"))

    # This function cleans the box when you click it, like wiping a chalkboard.
    def _limpar_marcador(self, evento, marcador):
        if evento.widget.get() == marcador:
            evento.widget.delete(0, tk.END)
            evento.widget.configure(fg="#ffffff")

    # This function puts the help text back if you leave the box empty.
    def _definir_marcador(self, evento, marcador):
        if evento.widget.get() == "":
            evento.widget.insert(0, marcador)
            evento.widget.configure(fg="#8a7e72")

    # This function runs when you click the "Enter" button. It's like knocking on the door!
    def _entrar(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if usuario == "seu.usuario" or usuario == "":
            self._notificacao("Informe o usuario.")
            return

        if senha == "********" or senha == "":
            self._notificacao("Informe a senha.")
            return

        # We show a little hourglass while we check if your name is in our book.
        self.btn_entrar.configure(text="⏳ Carregando...", state="disabled")
        self.after(500, lambda: self._verificar_credenciais(usuario, senha))

    # This function checks our secret book to see if your name and password are correct.
    def _verificar_credenciais(self, usuario, senha):
        resultado = verificar_login(usuario, senha)

        if resultado:
            nome_usuario = resultado
            # If everything is correct, we say hello!
            self._notificacao(f"✓ Bem-vindo, {usuario}!")
        else:
            # If we can't find your name, we let you know.
            self._notificacao("✕ Usuario nao encontrado.")

        self.btn_entrar.configure(text="Entrar", state="normal")

    # This function shows a little message at the bottom of the screen, like a sticky note.
    def _notificacao(self, mensagem):
        rotulo = tk.Label(self, text=mensagem, font=("Segoe UI", 11), fg="#ffffff", bg="#3d2c20", padx=20, pady=8)
        rotulo.place(relx=0.5, rely=0.92, anchor="center")
        self.after(2500, rotulo.destroy)


if __name__ == "__main__":
    # This part starts our screen so we can see it.
    TelaLogin().mainloop()
