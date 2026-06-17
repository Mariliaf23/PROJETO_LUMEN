import os
import sys
import tkinter as tk
from tkinter import font as tkfont, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageOps
from ..connect import connect_to_database

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_config import cadastrar_usuario

class LumenLoginApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LUMEN - Entrar")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Cores baseadas na imagem
        self.bg_color = "#2c1f17"
        self.form_bg = "#1a140f"  # tom escuro semi-transparente
        self.text_color = "#e8d5b8"
        self.accent_color = "#d4a373"
        
        # Carregar imagem de fundo
        try:
            # Construir caminho para a imagem em relação ao diretório do projeto
            img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "tela_cadastro.png")
            print(f"Carregando imagem de: {img_path}")
            self.bg_image = Image.open(img_path).convert("RGB")
            self.bg_image = self.bg_image.resize((1000, 700), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            print("Imagem de fundo carregada com sucesso!")
        except Exception as e:
            # Fallback caso a imagem não seja encontrada
            print(f"Imagem de fundo não encontrada: {e}. Usando cor sólida.")
            self.bg_photo = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # # Canvas principal para background
        self.canvas = tk.Canvas(self.root, width=1000, height=700, highlightthickness=0, bg=self.bg_color)
        self.canvas.pack(fill="both", expand=True)
        
        if self.bg_photo:
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        else:
            # Preencher com cor sólida se não houver imagem
            self.canvas.create_rectangle(0, 0, 1000, 700, fill=self.bg_color, outline="")
        
        # Overlay semi-transparente para o formulário (colocar no canvas)
        overlay_id = self.canvas.create_rectangle(320, 120, 700, 580, outline="")
        
        # Título LUMEN
        title_font = tkfont.Font(family="Georgia", size=28, weight="bold")
        self.canvas.create_text(510, 160, text="LUMEN", font=title_font, fill="#d4b38a")
        
        # Formulário
        form_y = 200
        
        # Nome
        self.canvas.create_text(350, form_y, text="Nome", font=("Arial", 10), fill=self.text_color, anchor="nw")
        self.entry_nome = tk.Entry(self.root, font=("Arial", 11), width=30, 
                                  bg="#2c2118",fg="white", insertbackground="white",
                                  relief="flat", highlightthickness=1, highlightcolor="#d4a373")
        self.entry_nome.insert(0, "João Silva")
        self.canvas.create_window(510, form_y + 25, window=self.entry_nome, width=320)
        
        # Email
        self.canvas.create_text(350, form_y + 70, text="Email", font=("Arial", 10), fill=self.text_color, anchor="nw")
        self.entry_email = tk.Entry(self.root, font=("Arial", 11), width=30, 
                                   bg="#2c2118", fg="white", insertbackground="white",
                                   relief="flat", highlightthickness=1, highlightcolor="#d4a373")
        self.entry_email.insert(0, "admin@email.com")
        self.canvas.create_window(510, form_y + 95, window=self.entry_email, width=320)
        
        # Nova Senha
        self.canvas.create_text(350, form_y + 140, text="Nova Senha", font=("Arial", 10), fill=self.text_color, anchor="nw")
        self.entry_senha = tk.Entry(self.root, font=("Arial", 11), width=30, show="●",
                                   bg="#2c2118", fg="white", insertbackground="white",
                                   relief="flat", highlightthickness=1, highlightcolor="#d4a373")
        self.entry_senha.insert(0, "12345678")
        self.canvas.create_window(510, form_y + 165, window=self.entry_senha, width=320)
        
        # Confirmação de Senha
        self.canvas.create_text(350, form_y + 210, text="Confirmação de Senha", font=("Arial", 10), fill=self.text_color, anchor="nw")
        self.entry_confirm = tk.Entry(self.root, font=("Arial", 11), width=30, show="●",
                                     bg="#2c2118", fg="white", insertbackground="white",
                                     relief="flat", highlightthickness=1, highlightcolor="#d4a373")
        self.entry_confirm.insert(0, "12345678")
        self.canvas.create_window(510, form_y + 235, window=self.entry_confirm, width=320)
        
        # Botão Cadastrar
        btn_font = tkfont.Font(family="Arial", size=12, weight="bold")
        self.btn_entrar = tk.Button(self.root, text="Cadastrar", font=btn_font, 
                                   bg="#8c5a2b", fg="white", activebackground="#a36d3f",
                                   activeforeground="white", relief="flat", height=2,
                                   command=self.on_login)
        self.canvas.create_window(510, form_y + 315, window=self.btn_entrar, width=320)
        
        # Efeito hover no botão
        self.btn_entrar.bind("<Enter>", lambda e: self.btn_entrar.config(bg="#a36d3f"))
        self.btn_entrar.bind("<Leave>", lambda e: self.btn_entrar.config(bg="#8c5a2b"))
   
    def on_login(self):
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()
        confirm = self.entry_confirm.get().strip()

        if not nome:
            messagebox.showerror("LUMEN", "Informe o nome.")
            return

        if not email:
            messagebox.showerror("LUMEN", "Informe o email.")
            return

        if not senha:
            messagebox.showerror("LUMEN", "Informe a senha.")
            return

        if senha != confirm:
            messagebox.showerror("LUMEN", "As senhas nao conferem.")
            return

        sucesso = cadastrar_usuario(nome, email, senha)
        if sucesso:
            messagebox.showinfo("LUMEN", "Cadastro realizado com sucesso!")
        else:
            messagebox.showerror("LUMEN", "Erro ao salvar no banco de dados.")


        dados = (nome, email, senha, confirm)

        cursor = self.conn.cursor()
        try:
            # Insere novo registro quando não há id definido.
            cursor.execute("""
                 "INSERT INTO funcionario (nome_funcionario, email_funcionario, password_funcionario, funcao) VALUES (%s, %s, %s, %s)"
                           """),dados

            self.conn.commit()
            self.carregar()
            self.limpar()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # Instalar Pillow se necessário: pip install pillow
    app = LumenLoginApp()
    app.run()