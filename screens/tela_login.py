import os
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageDraw
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
        self.configure(bg="#0a0806")

        self.card_w = 400
        self.card_h = 450
        self.radius = 20

        bg_path = os.path.join("assets", "login fundo.jpg")
        self.bg_src = Image.open(bg_path).convert("RGB") if os.path.exists(bg_path) else Image.new("RGB", (1920, 1080), "#1a1410")

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg="#0a0806")
        self.canvas.pack(fill="both", expand=True)

        self._refs = {}
        self.frm = tk.Frame(self.canvas, bg="#ffffff")
        self._build_ui()

        self.bind("<Configure>", self._on_resize)
        self.after(20, self._on_resize)

    def _on_resize(self, e=None):
        W = self.winfo_width()
        H = self.winfo_height()
        if W < 100 or H < 100:
            return

        bg = self.bg_src.resize((W, H), Image.Resampling.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=8))
        self._refs["bg"] = ImageTk.PhotoImage(bg)
        self.canvas.delete("bg")
        self.canvas.create_image(0, 0, anchor="nw", image=self._refs["bg"], tags="bg")

        cx, cy = W // 2, H // 2
        x1 = cx - self.card_w // 2
        y1 = cy - self.card_h // 2

        card = bg.crop((x1, y1, x1 + self.card_w, y1 + self.card_h))
        card = card.filter(ImageFilter.GaussianBlur(radius=20))
        card = card.convert("RGBA")

        overlay = Image.new("RGBA", (self.card_w, self.card_h), (255, 255, 255, 180))
        card = Image.alpha_composite(card, overlay)

        mask = Image.new("L", (self.card_w, self.card_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, self.card_w, self.card_h], radius=self.radius, fill=255)
        card.putalpha(mask)

        shadow = Image.new("RGBA", (self.card_w + 40, self.card_h + 40), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [10, 15, self.card_w + 30, self.card_h + 35],
            radius=self.radius + 5,
            fill=(0, 0, 0, 60)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=20))
        self._refs["shadow"] = ImageTk.PhotoImage(shadow)
        self.canvas.delete("shadow")
        self.canvas.create_image(cx, cy + 5, anchor="center", image=self._refs["shadow"], tags="shadow")

        self._refs["card"] = ImageTk.PhotoImage(card)
        self.canvas.delete("card")
        self.canvas.create_image(cx, cy, anchor="center", image=self._refs["card"], tags="card")
        self.canvas.delete("win")
        self.canvas.create_window(cx, cy, window=self.frm, tags="win", width=self.card_w - 30, height=self.card_h - 30)

    def _build_ui(self):
        f = self.frm
        f.grid_columnconfigure(0, weight=1)

        tk.Label(
            f, text="LUMEN", font=("Cinzel", 32, "bold"),
            fg="#b89a72", bg="#ffffff"
        ).grid(row=0, column=0, pady=(40, 8))

        tk.Label(f, text="Iniciar sessão", font=("Segoe UI Light", 12), fg="#8a7e72", bg="#ffffff").grid(row=1, column=0, pady=(0, 30))

        self.entry_usuario = tk.Entry(
            f, font=("Segoe UI", 12), fg="#1c1814", bg="#f5f1eb",
            relief="flat", bd=0, justify="center"
        )
        self.entry_usuario.insert(0, "seu.usuario")
        self.entry_usuario.configure(fg="#8a7e72")
        self.entry_usuario.bind("<FocusIn>", lambda e: self._clear_placeholder(e, "seu.usuario"))
        self.entry_usuario.bind("<FocusOut>", lambda e: self._set_placeholder(e, "seu.usuario"))
        self.entry_usuario.grid(row=2, column=0, padx=40, sticky="ew", ipady=10, pady=(0, 15))

        self.entry_senha = tk.Entry(
            f, show="•", font=("Segoe UI", 12), fg="#1c1814", bg="#f5f1eb",
            relief="flat", bd=0, justify="center"
        )
        self.entry_senha.insert(0, "••••••••")
        self.entry_senha.configure(fg="#8a7e72")
        self.entry_senha.bind("<FocusIn>", lambda e: self._clear_placeholder(e, "••••••••"))
        self.entry_senha.bind("<FocusOut>", lambda e: self._set_placeholder(e, "••••••••"))
        self.entry_senha.grid(row=3, column=0, padx=40, sticky="ew", ipady=10, pady=(0, 25))

        btn_entrar = tk.Button(
            f, text="Entrar", font=("Segoe UI Semibold", 13),
            fg="#ffffff", bg="#b89a72", activebackground="#d4b88c",
            border=0, cursor="hand2", command=self._login
        )
        btn_entrar.grid(row=4, column=0, padx=40, sticky="ew", ipady=12, pady=(0, 20))

        tk.Label(
            f, text="Não tem conta? Registar", font=("Segoe UI", 10),
            fg="#8a7e72", bg="#ffffff", cursor="hand2"
        ).grid(row=5, column=0, pady=(0, 30))

    def _clear_placeholder(self, event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.configure(fg="#1c1814")

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

        btn = self.nametowidget(str(self.frm.children["!button"]))
        btn.configure(text="⏳ Carregando...", bg="#8a7e72", state="disabled")
        
        self.after(500, lambda: self._verificar_credenciais(usuario, senha, btn))
    
    def _verificar_credenciais(self, usuario, senha, btn):
        resultado = verificar_login(usuario, senha)
        
        if resultado:
            nome_usuario = resultado[0]
            self._toast(f"✓ Bem-vindo, {nome_usuario}!")
            btn.configure(text="Entrar", bg="#b89a72", state="normal")
        else:
            self._toast("✕ Usuário não encontrado.")
            btn.configure(text="Entrar", bg="#b89a72", state="normal")

    def _toast(self, msg):
        t = tk.Label(self, text=msg, font=("Segoe UI", 11), fg="#ffffff", bg="#2a2218", padx=20, pady=8)
        t.place(relx=0.5, rely=0.92, anchor="center")
        self.after(2500, t.destroy)


if __name__ == "__main__":
    TelaLogin().mainloop()
