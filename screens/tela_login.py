import os
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_config import init_db, verificar_login


class TelaLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        init_db()
        self.title("Lumen")
        self.geometry("960x680")
        self.minsize(800, 580)

        self.current_w = 0
        self.current_h = 0

        bg_path = os.path.join("assets", "Login.png")
        self.bg_src = Image.open(bg_path).convert("RGB") if os.path.exists(bg_path) else Image.new("RGB", (1920, 1080), "#1c1410")

        # Canvas limpo sem bordas estruturais
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg="#120c08")
        self.canvas.pack(fill="both", expand=True)

        self._refs = {}
        self._build_ui()

        self.bind("<Configure>", self._on_resize)

    def _build_ui(self):
        # Caixa de usuário: Cor de fundo camuflada com o tom escuro das sombras dos livros
        self.entry_usuario = tk.Entry(
            self.canvas, font=("Segoe UI", 12), fg="#8a7e72",
            relief="flat", bd=0, justify="center", insertbackground="white",
            bg="#120c08"
        )
        self.entry_usuario.insert(0, "seu.usuario")
        self.entry_usuario.bind("<FocusIn>", lambda e: self._clear_placeholder(e, "seu.usuario"))
        self.entry_usuario.bind("<FocusOut>", lambda e: self._set_placeholder(e, "seu.usuario"))

        # Caixa de senha: Mesma cor de camuflagem para sumir com o bloco marrom claro
        self.entry_senha = tk.Entry(
            self.canvas, show="•", font=("Segoe UI", 12), fg="#8a7e72",
            relief="flat", bd=0, justify="center", insertbackground="white",
            bg="#120c08"
        )
        self.entry_senha.insert(0, "••••••••")
        self.entry_senha.bind("<FocusIn>", lambda e: self._clear_placeholder(e, "••••••••"))
        self.entry_senha.bind("<FocusOut>", lambda e: self._set_placeholder(e, "••••••••"))

        # Botão Entrar vazado (Fundo da cor do ambiente e borda dourada fina)
        self.btn_entrar = tk.Button(
            self.canvas, text="Entrar", font=("Segoe UI Semibold", 12),
            fg="#b89a72", activeforeground="#ffffff", activebackground="#b89a72",
            bg="#120c08", bd=1, relief="solid", cursor="hand2", command=self._login
        )

    def _on_resize(self, event=None):
        W = self.winfo_width()
        H = self.winfo_height()
        
        if W < 100 or H < 100:
            return

        if W == self.current_w and H == self.current_h:
            return
        self.current_w = W
        self.current_h = H

        # Processa e posiciona a imagem desfocada no Canvas principal
        bg = self.bg_src.resize((W, H), Image.Resampling.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=8))
        self._refs["bg"] = ImageTk.PhotoImage(bg)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._refs["bg"])

        cx, cy = W // 2, H // 2

        # Textos fixos superiores desenhados no Canvas
        self.canvas.create_text(cx, cy - 130, text="LUMEN", font=("Cinzel", 32, "bold"), fill="#b89a72")
        self.canvas.create_text(cx, cy - 75, text="Iniciar sessão", font=("Segoe UI Light", 12), fill="#ffffff")

        # Insere as janelas dos componentes por cima de tudo no Canvas sem sofrer bloqueio
        self.canvas.create_window(cx, cy - 15, window=self.entry_usuario, width=280, height=35)
        self.canvas.create_window(cx, cy + 35, window=self.entry_senha, width=280, height=35)
        self.canvas.create_window(cx, cy + 95, window=self.btn_entrar, width=280, height=40)

        # Texto clicável inferior de registro
        lbl_registrar = self.canvas.create_text(cx, cy + 155, text="Não tem conta? Registar", font=("Segoe UI", 10), fill="#8a7e72")
        self.canvas.tag_bind(lbl_registrar, "<Button-1>", lambda e: print("Navegar para registro"))

    def _clear_placeholder(self, event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.configure(fg="#ffffff")

    def _set_placeholder(self, event, placeholder):
        if event.widget.get() == "":
            event.widget.insert(0, placeholder)
            event.widget.configure(fg="#8a7e72")

    def _login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()
        
        if usuario == "seu.usuario" or usuario == "":
            self._toast("Informe o usuário.")
            return
        
        if senha == "••••••••" or senha == "":
            self._toast("Informe a senha.")
            return

        self.btn_entrar.configure(text="⏳ Carregando...", state="disabled")
        self.after(500, lambda: self._verificar_credenciais(usuario, senha))
    
    def _verificar_credenciais(self, usuario, senha):
        resultado = verificar_login(usuario, senha)
        
        if resultado:
            nome_usuario = resultado
            self._toast(f"✓ Bem-vindo, {nome_usuario}!")
        else:
            self._toast("✕ Usuário não encontrado.")
        
        self.btn_entrar.configure(text="Entrar", state="normal")

    def _toast(self, msg):
        t = tk.Label(self, text=msg, font=("Segoe UI", 11), fg="#ffffff", bg="#3d2c20", padx=20, pady=8)
        t.place(relx=0.5, rely=0.92, anchor="center")
        self.after(2500, t.destroy)


if __name__ == "__main__":
    TelaLogin().mainloop()
