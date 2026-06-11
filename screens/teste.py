import tkinter as tk 
from PIL import Image, ImageTk
janela=tk.Tk()
janela.title("Teste")
janela.geometry("800x700")
imagem_backgraud = Image.open("assets/login fundo.jpg")
imagem_redimencionada = imagem_backgraud.resize((800,700))
bg_imagem = ImageTk.PhotoImage(imagem_redimencionada)
label_imagem = tk.Label(janela, image=bg_imagem)
label_imagem.place(relx=0, rely=0, relwidth=1, relheight=1)
label_imagem.image = bg_imagem






janela.mainloop()
