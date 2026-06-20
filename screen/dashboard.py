import os
import sys
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from PIL import Image, ImageTk, ImageFilter
from services.conector import init_db
from services.database_config import (
    buscar_stats_dashboard, buscar_emprestimos_por_mes,
    buscar_livros_por_categoria, buscar_emprestimos_semana
)

COR_BG = "#120c08"
COR_SIDEBAR = "#0d0905"
COR_CARD = "#1e1208"
COR_DOURADO = "#b89a72"
COR_TEXTO = "#ffffff"
COR_TEXTO2 = "#8a7e72"
COR_HOVER = "#d4b896"
COR_ATIVO = "#2a1a08"
COR_GRAF1 = "#b89a72"
COR_GRAF2 = "#d4b896"
COR_GRAF3 = "#8a7e72"
COR_GRAF4 = "#6b5a48"
COR_GRAF5 = "#4a3a28"

MESES = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
DIAS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']


class Dashboard(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("LUMEN - Dashboard")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=COR_BG)

        self.largura_atual = 0
        self.altura_atual = 0

        caminho_fundo = os.path.join("assets", "Login.png")
        self.img_fundo = (
            Image.open(caminho_fundo).convert("RGB")
            if os.path.exists(caminho_fundo)
            else Image.new("RGB", (1920, 1080), COR_BG)
        )

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=COR_BG)
        self.canvas.pack(fill="both", expand=True)

        self._referencias = {}
        self._itens_nav = []
        self._stats = {}
        self._emp_mes = []
        self._cat_livros = []
        self._emp_semana = []

        self.bind("<Configure>", self._ao_redimensionar)
        self._carregar_dados()

    def _carregar_dados(self):
        self._stats = buscar_stats_dashboard()
        self._emp_mes = buscar_emprestimos_por_mes()
        self._cat_livros = buscar_livros_por_categoria()
        self._emp_semana = buscar_emprestimos_semana()

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

        self._desenhar_sidebar(L, A)
        self._desenhar_header(L, A)
        self._desenhar_cards(L, A)
        self._desenhar_graficos(L, A)

    def _desenhar_sidebar(self, L, A):
        self.canvas.create_rectangle(0, 0, 200, A, fill=COR_SIDEBAR, outline="")

        self.canvas.create_text(100, 35, text="LUMEN", font=("Cinzel", 18, "bold"), fill=COR_DOURADO)
        self.canvas.create_line(20, 58, 180, 58, fill="#2a1a08", width=1)

        itens = [
            ("DASHBOARD", True),
            ("LIVROS", False),
            ("MEMBROS", False),
            ("EMPRESTIMOS", False),
            ("DEVOLUCOES", False),
            ("CONFIGURACOES", False),
        ]

        self._itens_nav = []
        y = 85
        for nome, ativo in itens:
            if ativo:
                self.canvas.create_rectangle(8, y - 14, 192, y + 14, fill=COR_ATIVO, outline="")

            cor = COR_DOURADO if ativo else COR_TEXTO2
            item = self.canvas.create_text(100, y, text=nome, font=("Segoe UI", 10), fill=cor)
            self.canvas.tag_bind(item, "<Enter>", lambda e, i=item: self.canvas.itemconfig(i, fill=COR_HOVER))
            self.canvas.tag_bind(item, "<Leave>", lambda e, i=item, c=cor: self.canvas.itemconfig(i, fill=c))
            self.canvas.tag_bind(item, "<Button-1>", lambda e, n=nome: print(f"Navegar: {n}"))
            self._itens_nav.append((item, cor))
            y += 42

    def _desenhar_header(self, L, A):
        self.canvas.create_text(230, 30, text="Dashboard", font=("Segoe UI Light", 20), fill=COR_TEXTO, anchor="w")
        self.canvas.create_line(200, 55, L, 55, fill="#2a1a08", width=1)

    def _desenhar_cards(self, L, A):
        card_y = 75
        card_h = 80
        card_gap = 15
        cards_x = 220
        card_w = (L - cards_x - 30 - card_gap * 3) // 4

        cards = [
            ("Total de Livros", str(self._stats['livros']), "#b89a72"),
            ("Emprestimos", str(self._stats['emprestimos']), "#d4b896"),
            ("Alunos", str(self._stats['alunos']), "#8a7e72"),
            ("Taxa de Retorno", f"{self._stats['taxa_retorno']}%", "#6b5a48"),
        ]

        for i, (titulo, valor, cor_icone) in enumerate(cards):
            x1 = cards_x + i * (card_w + card_gap)
            x2 = x1 + card_w
            y2 = card_y + card_h

            self.canvas.create_rectangle(x1, card_y, x2, y2, fill=COR_CARD, outline="#2a1a08", width=1)
            self.canvas.create_rectangle(x1, card_y, x1 + 4, y2, fill=cor_icone, outline="")

            self.canvas.create_text(x1 + 20, card_y + 22, text=titulo, font=("Segoe UI", 9), fill=COR_TEXTO2, anchor="w")
            self.canvas.create_text(x1 + 20, card_y + 55, text=valor, font=("Segoe UI Semibold", 22), fill=COR_TEXTO, anchor="w")

    def _desenhar_graficos(self, L, A):
        charts_x = 220
        charts_w = L - charts_x - 20
        charts_y = 170
        charts_h = A - charts_y - 20

        col1_w = charts_w * 0.5
        col2_w = charts_w * 0.5

        self._desenhar_grafico_emprestimos_mes(charts_x, charts_y, col1_w - 10, charts_h * 0.55)
        self._desenhar_grafico_livros_categoria(charts_x + col1_w + 10, charts_y, col2_w - 10, charts_h * 0.55)
        self._desenhar_grafico_emprestimos_semana(charts_x, charts_y + charts_h * 0.55 + 15, charts_w, charts_h * 0.42)

    def _desenhar_grafico_emprestimos_mes(self, x, y, w, h):
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=COR_CARD, outline="#2a1a08", width=1)
        self.canvas.create_text(x + 15, y + 15, text="Emprestimos por Mes", font=("Segoe UI", 10), fill=COR_TEXTO2, anchor="w")

        area_x = x + 40
        area_y = y + 40
        area_w = w - 60
        area_h = h - 65

        if not self._emp_mes:
            self.canvas.create_text(area_x + area_w // 2, area_y + area_h // 2, text="Sem dados", font=("Segoe UI", 10), fill=COR_TEXTO2)
            return

        max_val = max(v for _, v in self._emp_mes) if self._emp_mes else 1
        if max_val == 0:
            max_val = 1

        n = len(self._emp_mes)
        bar_w = max(8, (area_w - 10) // max(n, 1) - 4)

        for i, (mes, total) in enumerate(self._emp_mes):
            bx = area_x + 5 + i * (bar_w + 4)
            bar_h = int((total / max_val) * (area_h - 20))
            by1 = area_y + area_h - bar_h
            by2 = area_y + area_h

            self.canvas.create_rectangle(bx, by1, bx + bar_w, by2, fill=COR_GRAF1, outline="")
            self.canvas.create_text(bx + bar_w // 2, by2 + 12, text=MESES[mes], font=("Segoe UI", 7), fill=COR_TEXTO2)
            self.canvas.create_text(bx + bar_w // 2, by1 - 8, text=str(total), font=("Segoe UI", 7), fill=COR_TEXTO)

        self.canvas.create_line(area_x, area_y + area_h, area_x + area_w, area_y + area_h, fill="#2a1a08", width=1)

    def _desenhar_grafico_livros_categoria(self, x, y, w, h):
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=COR_CARD, outline="#2a1a08", width=1)
        self.canvas.create_text(x + 15, y + 15, text="Livros por Categoria", font=("Segoe UI", 10), fill=COR_TEXTO2, anchor="w")

        area_x = x + w // 2
        area_y = y + h // 2 + 15
        raio = min(w, h) // 2 - 40

        if not self._cat_livros:
            self.canvas.create_text(area_x, area_y, text="Sem dados", font=("Segoe UI", 10), fill=COR_TEXTO2)
            return

        total = sum(v for _, v in self._cat_livros)
        if total == 0:
            total = 1

        cores = [COR_GRAF1, COR_GRAF2, COR_GRAF3, COR_GRAF4, COR_GRAF5]
        angulo_inicio = -90

        for i, (cat, qtd) in enumerate(self._cat_livros):
            fatia = (qtd / total) * 360
            angulo_fim = angulo_inicio + fatia

            pontos = [area_x, area_y]
            for a in range(int(angulo_inicio), int(angulo_fim) + 1):
                rad = math.radians(a)
                px = area_x + raio * math.cos(rad)
                py = area_y + raio * math.sin(rad)
                pontos.extend([px, py])
            pontos.extend([area_x, area_y])

            if len(pontos) >= 6:
                self.canvas.create_polygon(pontos, fill=cores[i % len(cores)], outline=COR_CARD, width=2)

            angulo_inicio = angulo_fim

        leg_x = x + 15
        leg_y = y + h - 25 - len(self._cat_livros) * 18
        for i, (cat, qtd) in enumerate(self._cat_livros):
            cor = cores[i % len(cores)]
            self.canvas.create_rectangle(leg_x, leg_y + i * 18, leg_x + 10, leg_y + i * 18 + 10, fill=cor, outline="")
            self.canvas.create_text(leg_x + 15, leg_y + i * 18 + 5, text=f"{cat} ({qtd})", font=("Segoe UI", 8), fill=COR_TEXTO2, anchor="w")

    def _desenhar_grafico_emprestimos_semana(self, x, y, w, h):
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=COR_CARD, outline="#2a1a08", width=1)
        self.canvas.create_text(x + 15, y + 15, text="Emprestimos da Semana", font=("Segoe UI", 10), fill=COR_TEXTO2, anchor="w")

        area_x = x + 50
        area_y = y + 45
        area_w = w - 80
        area_h = h - 70

        dados_map = {d: 0 for d in DIAS}
        for dia, total in self._emp_semana:
            if dia in dados_map:
                dados_map[dia] = total

        valores = [dados_map[d] for d in DIAS]
        max_val = max(valores) if valores else 1
        if max_val == 0:
            max_val = 1

        n = len(DIAS)
        bar_w = max(10, (area_w - 20) // n - 8)

        for i, (dia, val) in enumerate(zip(DIAS, valores)):
            bx = area_x + 10 + i * (bar_w + 8)
            bar_h = int((val / max_val) * (area_h - 20))
            by1 = area_y + area_h - bar_h
            by2 = area_y + area_h

            cor = COR_GRAF1 if val == max_val and val > 0 else COR_GRAF3
            self.canvas.create_rectangle(bx, by1, bx + bar_w, by2, fill=cor, outline="")
            self.canvas.create_text(bx + bar_w // 2, by2 + 12, text=dia, font=("Segoe UI", 8), fill=COR_TEXTO2)
            self.canvas.create_text(bx + bar_w // 2, by1 - 10, text=str(val), font=("Segoe UI", 8), fill=COR_TEXTO)

        self.canvas.create_line(area_x, area_y + area_h, area_x + area_w, area_y + area_h, fill="#2a1a08", width=1)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = Dashboard(master=root)
    app.mainloop()
    root.destroy()
