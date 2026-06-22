import os
import sys
from PIL import Image
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import (
    listar_emprestimos_ativos, finalizar_emprestimo, gerar_multa, verificar_atrasos
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_entry, criar_label, criar_titulo, criar_card, criar_scroll_frame
)

# Definição das cores padrão azul corporativo (sem tons pastel)
COR_AZUL_PRINCIPAL = "#1E3A8A"
COR_AZUL_HOVER = "#1D4ED8"
COR_AZUL_CLARO = "#3B82F6"

class TelaDevolucoes(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        self.cor_bg = str(COR_BG)
        self.cor_card = str(COR_CARD)
        self.cor_dourado = str(COR_DOURADO)
        self.cor_texto = str(COR_TEXTO)
        self.cor_texto2 = str(COR_TEXTO2)
        self.cor_border = str(COR_INPUT_BORDER)

        super().__init__(master, fg_color=self.cor_bg)
        self.controller = controller
        self._itens_lista = []
        self._selecionado = None
        self._construir_ui()

    def _ao_visitar(self):
        verificar_atrasos()
        self._carregar_tabela()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === HEADER PADRONIZADO (LOGO MAIOR E SEM TEXTO LUMEN) ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y")

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")
        
        if os.path.exists(logo_path):
            try:
                # Logo no tamanho maior (60x60) idêntico ao cadastro de usuários
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(180, 180))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                pass
        
        # Título da tela ao lado do logo
        criar_titulo(header_left, "Devoluções Pendentes", font=("Segoe UI", 20, "bold")).pack(side="left")

        btn_voltar = ctk.CTkButton(
            header, text="Voltar", command=self._voltar, 
            width=100, height=35, fg_color=COR_AZUL_PRINCIPAL, hover_color=COR_AZUL_HOVER,
            font=("Segoe UI", 12, "bold")
        )
        btn_voltar.pack(side="right")

        # === CARD DE AÇÕES (AZUL CORPORATIVO) ===
        acoes_card = criar_card(self)
        acoes_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        acoes_frame = ctk.CTkFrame(acoes_card, fg_color="transparent")
        acoes_frame.pack(fill="x", padx=20, pady=15)

        self.btn_devolver = ctk.CTkButton(
            acoes_frame, text="Registrar Devolução", command=self._devolver,
            width=220, height=42, fg_color=COR_AZUL_PRINCIPAL, hover_color=COR_AZUL_HOVER,
            font=("Segoe UI", 12, "bold")
        )
        self.btn_devolver.pack(side="left")

        criar_label(acoes_frame, "Selecione um empréstimo na lista abaixo", font=FONTE_LABEL).pack(side="left", padx=(20, 0))

        # === CARD DA TABELA/LISTA ===
        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 20))

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent", height=30)
        header_lista.pack(fill="x", padx=15, pady=(10, 5))
        header_lista.pack_propagate(False)

        colunas_larguras = [("ID", 0.06), ("Aluno", 0.2), ("Exemplar", 0.15), ("Livro", 0.2), ("Empréstimo", 0.12), ("Previsto", 0.12), ("Status", 0.1)]
        x_header = 0
        for txt, pct in colunas_larguras:
            lbl_h = criar_label(header_lista, txt.upper(), font=("Segoe UI", 9, "bold"), text_color=COR_AZUL_CLARO, anchor="w")
            lbl_h.place(relx=x_header + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            x_header += pct

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.lbl_notificacao = criar_label(self, "", text_color=self.cor_texto2)

    def _carregar_tabela(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        self._itens_lista.clear()
        self._selecionado = None

        emprestimos = listar_emprestimos_ativos()
        
        for emp in emprestimos:
            self._criar_item(emp)

        if not emprestimos:
            empty = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
            empty.pack(fill="both", expand=True)
            criar_label(empty, "Nenhuma devolução pendente", font=FONTE_LABEL).pack(expand=True)

    def _criar_item(self, emp):
        item = ctk.CTkFrame(self.lista_frame, fg_color=self.cor_card, corner_radius=8, height=42)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)
        item.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))

        colunas = [0.06, 0.2, 0.15, 0.2, 0.12, 0.12, 0.1]
        x = 0
        for i, (texto, pct) in enumerate(zip(emp, colunas)):
            cor = self.cor_texto
            if i == 6 and str(texto).lower() == "atrasado":
                cor = "#EF4444"  # Vermelho corporativo vivo/limpo (removido pastel)
            elif i == 6 and str(texto).lower() in ["ativo", "disponível", "disponivel"]:
                cor = COR_AZUL_CLARO
                
            lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 10), text_color=cor, anchor="w")
            lbl.place(relx=x + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            lbl.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))
            x += pct

        self._itens_lista.append((item, emp))

    def _selecionar(self, emp):
        for item, e in self._itens_lista:
            if e == emp:
                item.configure(fg_color="#1E293B")  # Seleção em tom azul/cinza escuro corporativo
            else:
                item.configure(fg_color=self.cor_card)
        self._selecionado = emp

    def _devolver(self):
        if not self._selecionado:
            self._notificar("Selecione um empréstimo para devolver.")
            return
        emp_id = self._selecionado[0]
        self.btn_devolver.configure(text="Processando...", state="disabled")
        self.after(500, lambda: self._processar_devolucao(emp_id))

    def _processar_devolucao(self, emp_id):
        data_prevista_str = str(self._selecionado[5])
        try:
            partes = data_prevista_str.split("-")
            data_prevista = date(int(partes[0]), int(partes[1]), int(partes[2]))
            hoje = date.today()
            dias_atraso = (hoje - data_prevista).days

            if dias_atraso > 0:
                gerar_multa(emp_id, dias_atraso, 'atraso')
                self._notificar(f"Devolução registrada! Multa gerada: {dias_atraso} dias de atraso.")
            else:
                self._notificar("Devolução registrada com sucesso!")
        except Exception:
            self._notificar("Devolução registrada com sucesso!")

        sucesso = finalizar_emprestimo(emp_id)
        if sucesso:
            self._selecionado = None
            self._carregar_tabela()
        else:
            self._notificar("Erro ao finalizar empréstimo.")
        self.btn_devolver.configure(text="Registrar Devolução", state="normal")

    def _voltar(self):
        self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color=COR_AZUL_CLARO)
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))