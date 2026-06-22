# import tkinter as tk 
# from PIL import Image, ImageTk
# janela=tk.Tk()
# janela.title("Teste")
# janela.geometry("800x700")
# imagem_backgraud = Image.open("assets/login fundo.jpg")
# imagem_redimencionada = imagem_backgraud.resize((800,700))
# bg_imagem = ImageTk.PhotoImage(imagem_redimencionada)
# label_imagem = tk.Label(janela, image=bg_imagem)
# label_imagem.place(relx=0, rely=0, relwidth=1, relheight=1)
# label_imagem.image = bg_imagem

# janela.mainloop()

import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk

class LumenApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LUMEN - Biblioteca")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1a140f")
        self.root.resizable(False, False)

        # Cores
        self.bg_color = "#1a140f"
        self.sidebar_bg = "#0f0a07"
        self.text_color = "#e8d5b8"
        self.hover_color = "#3c2a1f"
        self.active_color = "#d4a373"

        # ==================== Imagem de Fundo ====================
        try:
            self.bg_image = Image.open("/home/workdir/attachments/Captura de tela 2026-06-15 193119.png")
            self.bg_image = self.bg_image.resize((1200, 700), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        except:
            self.bg_photo = None

        self.canvas = tk.Canvas(self.root, width=1200, height=700, highlightthickness=0, bg=self.bg_color)
        self.canvas.pack(fill="both", expand=True)

        if self.bg_photo:
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        # ==================== Sidebar ====================
        self.sidebar = tk.Frame(self.root, bg=self.sidebar_bg, width=280, height=700)
        self.sidebar.place(x=0, y=0)

        # Logo LUMEN
        logo_font = tkfont.Font(family="Georgia", size=32, weight="bold")
        self.logo = tk.Label(self.sidebar, text="LUMEN", font=logo_font, 
                            fg="#d4b38a", bg=self.sidebar_bg)
        self.logo.pack(pady=(60, 80))

        # Menu Items
        self.create_menu_button("DASHBOARD", 0, active=True)
        self.create_menu_button("LIVROS", 1)
        self.create_menu_button("MEMBROS", 2)
        self.create_menu_button("EMPRÉSTIMOS", 3)
        self.create_menu_button("DEVOLUÇÕES", 4)
        self.create_menu_button("CONFIGURAÇÕES", 5)

        # Rodapé da sidebar
        footer = tk.Label(self.sidebar, text="Biblioteca LUMEN © 2026", 
                         font=("Arial", 9), fg="#6b5a47", bg=self.sidebar_bg)
        footer.pack(side="bottom", pady=30)

        self.root.mainloop()

    def create_menu_button(self, text, index, active=False):
        btn = tk.Label(self.sidebar, text=text, font=("Arial", 12, "bold"),
                      fg=self.text_color if not active else "#1a140f",
                      bg=self.active_color if active else self.sidebar_bg,
                      width=25, height=2, anchor="w", padx=40)
        
        btn.pack(pady=2)
        
        # Hover effect
        def on_enter(e):
            if not active:
                btn.config(bg=self.hover_color)
        def on_leave(e):
            if not active:
                btn.config(bg=self.sidebar_bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        # Clique (exemplo)
        btn.bind("<Button-1>", lambda e, t=text: self.menu_click(t))

    def menu_click(self, menu):
        print(f"Menu clicado: {menu}")
        # Aqui você pode trocar o conteúdo da área principal


if __name__ == "__main__":
    # pip install pillow
    app = LumenApp()
