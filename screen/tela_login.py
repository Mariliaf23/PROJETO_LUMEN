import os
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.database_config import init_db, verificar_login


class TelaLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        init_db()
        self.title("Lumen")
        self.geometry("960x680")
        self.minsize(800, 580)

        self.largura_atual = 0
        self.altura_atual = 0

        caminho_fundo = os.path.join("assets", "Login.png")
        self.img_fundo = Image.open(caminho_fundo).convert("RGB") if os.path.exists(caminho_fundo) else Image.new("RGB", (1920, 1080), "#1c1410")

        # Canvas limpo sem bordas estruturais
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg="#120c08")
        self.canvas.pack(fill="both", expand=True)

        self._referencias = {}
        self._construir_ui()

        self.bind("<Configure>", self._ao_redimensionar)

    def _construir_ui(self):
        # Caixa de usuario: Cor de fundo camuflada com o tom escuro das sombras dos livros
        self.entry_usuario = tk.Entry(
            self.canvas, font=("Segoe UI", 12), fg="#8a7e72",
            relief="flat", bd=0, justify="center", insertbackground="white",
            bg="#120c08"
        )
        self.entry_usuario.insert(0, "seu.usuario")
        self.entry_usuario.bind("<FocusIn>", lambda e: self._limpar_marcador(e, "seu.usuario"))
        self.entry_usuario.bind("<FocusOut>", lambda e: self._definir_marcador(e, "seu.usuario"))

        # Caixa de senha: Mesma cor de camuflagem para sumir com o bloco marrom claro
        self.entry_senha = tk.Entry(
            self.canvas, show="*", font=("Segoe UI", 12), fg="#8a7e72",
            relief="flat", bd=0, justify="center", insertbackground="white",
            bg="#120c08"
        )
        self.entry_senha.insert(0, "********")
        self.entry_senha.bind("<FocusIn>", lambda e: self._limpar_marcador(e, "********"))
        self.entry_senha.bind("<FocusOut>", lambda e: self._definir_marcador(e, "********"))

        # Botao Entrar vazado (Fundo da cor do ambiente e borda dourada fina)
        self.btn_entrar = tk.Button(
            self.canvas, text="Entrar", font=("Segoe UI Semibold", 12),
            fg="#b89a72", activeforeground="#ffffff", activebackground="#b89a72",
            bg="#120c08", bd=1, relief="solid", cursor="hand2", command=self._entrar
        )

    def _ao_redimensionar(self, evento=None):
        L = self.winfo_width()
        A = self.winfo_height()

        if L < 100 or A < 100:
            return

        if L == self.largura_atual and A == self.altura_atual:
            return
        self.largura_atual = L
        self.altura_atual = A

        # Processa e posiciona a imagem desfocada no Canvas principal
        fundo = self.img_fundo.resize((L, A), Image.Resampling.LANCZOS)
        fundo = fundo.filter(ImageFilter.GaussianBlur(radius=8))
        self._referencias["fundo"] = ImageTk.PhotoImage(fundo)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._referencias["fundo"])

        cx, cy = L // 2, A // 2

        # Textos fixos superiores desenhados no Canvas
        self.canvas.create_text(cx, cy - 130, text="LUMEN", font=("Cinzel", 32, "bold"), fill="#b89a72")
        self.canvas.create_text(cx, cy - 75, text="Iniciar sessao", font=("Segoe UI Light", 12), fill="#ffffff")

        # Insere as janelas dos componentes por cima de tudo no Canvas sem sofrer bloqueio
        self.canvas.create_window(cx, cy - 15, window=self.entry_usuario, width=280, height=35)
        self.canvas.create_window(cx, cy + 35, window=self.entry_senha, width=280, height=35)
        self.canvas.create_window(cx, cy + 95, window=self.btn_entrar, width=280, height=40)

        # Texto clicavel inferior de registro
        rotulo_registrar = self.canvas.create_text(cx, cy + 155, text="Nao tem conta? Registar", font=("Segoe UI", 10), fill="#8a7e72")
        self.canvas.tag_bind(rotulo_registrar, "<Button-1>", lambda e: print("Navegar para registro"))

    def _limpar_marcador(self, evento, marcador):
        if evento.widget.get() == marcador:
            evento.widget.delete(0, tk.END)
            evento.widget.configure(fg="#ffffff")

    def _definir_marcador(self, evento, marcador):
        if evento.widget.get() == "":
            evento.widget.insert(0, marcador)
            evento.widget.configure(fg="#8a7e72")

    def _entrar(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if usuario == "seu.usuario" or usuario == "":
            self._notificacao("Informe o usuario.")
            return

        if senha == "********" or senha == "":
            self._notificacao("Informe a senha.")
            return

        self.btn_entrar.configure(text="⏳ Carregando...", state="disabled")
        self.after(500, lambda: self._verificar_credenciais(usuario, senha))

    def _verificar_credenciais(self, usuario, senha):
        resultado = verificar_login(usuario, senha)

        if resultado:
            nome_usuario = resultado
            self._notificacao(f"✓ Bem-vindo, {usuario}!")
        else:
            self._notificacao("✕ Usuario nao encontrado.")

        self.btn_entrar.configure(text="Entrar", state="normal")

    def _notificacao(self, mensagem):
        rotulo = tk.Label(self, text=mensagem, font=("Segoe UI", 11), fg="#ffffff", bg="#3d2c20", padx=20, pady=8)
        rotulo.place(relx=0.5, rely=0.92, anchor="center")
        self.after(2500, rotulo.destroy)


if __name__ == "__main__":
    TelaLogin().mainloop()
