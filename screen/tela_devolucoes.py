import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from datetime import date
from services.database_config import (
    listar_emprestimos_ativos, finalizar_emprestimo, gerar_multa, verificar_atrasos
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_botao_preenchido, criar_label, criar_titulo,
    criar_card, criar_scroll_frame
)


class TelaDevolucoes(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
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

        # --- HEADER PRINCIPAL ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        # Adicionado o padrão do logo e barra vertical das telas anteriores
        criar_titulo(header, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left")
        criar_label(header, "|  Devoluções Pendentes", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(side="left", padx=(10, 0))

        btn_voltar = criar_botao_preenchido(header, text="Voltar", command=self._voltar, width=100, height=35)
        btn_voltar.pack(side="right")

        # --- CARD DE AÇÕES ---
        acoes_card = criar_card(self)
        acoes_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        acoes_frame = ctk.CTkFrame(acoes_card, fg_color="transparent")
        acoes_frame.pack(fill="x", padx=20, pady=15)

        self.btn_devolver = criar_botao_preenchido(
            acoes_frame, text="Registrar Devolução", command=self._devolver,
            width=220, height=42
        )
        self.btn_devolver.pack(side="left")

        criar_label(acoes_frame, "Selecione um empréstimo na lista abaixo", font=FONTE_LABEL).pack(side="left", padx=(20, 0))

        # --- CARD DA TABELA/LISTA ---
        lista_card = criar_card(self)
        lista_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 20))

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent", height=30)
        header_lista.pack(fill="x", padx=15, pady=(10, 5))
        header_lista.pack_propagate(False)

        # Ajuste no alinhamento do Cabeçalho para bater estritamente com os itens posicionados por relx
        colunas_larguras = [("ID", 0.06), ("Aluno", 0.2), ("Exemplar", 0.15), ("Livro", 0.2), ("Empréstimo", 0.12), ("Previsto", 0.12), ("Status", 0.1)]
        x_header = 0
        for txt, pct in colunas_larguras:
            lbl_h = criar_label(header_lista, txt.upper(), font=("Segoe UI", 9, "bold"), text_color=COR_DOURADO, anchor="w")
            lbl_h.place(relx=x_header + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            x_header += pct

        self.lista_frame = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

    def _carregar_tabela(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        self._itens_lista.clear()
        self._selecionado = None

        emprestimos = listar_emprestimos_actifs() if hasattr(self, '_mock') else listar_emprestimos_ativos()
        
        for emp in emprestimos:
            self._criar_item(emp)

        if not emprestimos:
            empty = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
            empty.pack(fill="both", expand=True)
            criar_label(empty, "Nenhuma devolução pendente", font=FONTE_LABEL).pack(expand=True)

    def _criar_item(self, emp):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COR_CARD, corner_radius=8, height=42)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)

        item.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))

        colunas = [0.06, 0.2, 0.15, 0.2, 0.12, 0.12, 0.1]
        x = 0
        for i, (texto, pct) in enumerate(zip(emp, colunas)):
            cor = COR_TEXTO
            if i == 6 and str(texto).lower() == "atrasado":
                cor = "#ea9999"  # Vermelho suave para legibilidade no tema escuro
            elif i == 6 and str(texto).lower() in ["ativo", "disponível", "disponivel"]:
                cor = COR_DOURADO
                
            lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 10), text_color=cor, anchor="w")
            lbl.place(relx=x + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            lbl.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))
            x += pct

        self._itens_lista.append((item, emp))

    def _selecionar(self, emp):
        for item, e in self._itens_lista:
            if e == emp:
                item.configure(fg_color="#2a1a08")  # Mantém a cor de seleção ativa padrão ouro escuro
            else:
                item.configure(fg_color=COR_CARD)
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
        self.lbl_notificacao.configure(text=mensagem, text_color=COR_DOURADO)
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))