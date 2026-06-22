import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import (
    cadastrar_emprestimo, listar_emprestimos, finalizar_emprestimo,
    listar_alunos, listar_exemplares_disponiveis, verificar_atrasos,
    cadastrar_reserva, listar_reservas, cancelar_reserva,
    listar_multas, pagar_multa, usuario_tem_multa_pendente,
    listar_livros
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    criar_entry, criar_label, criar_titulo, criar_card, criar_scroll_frame, criar_combo,
    criar_botao_preenchido
)

# Definição das cores padrão azul corporativo (sem tons pastel)
COR_AZUL_PRINCIPAL = "#1E3A8A"
COR_AZUL_HOVER = "#1D4ED8"
COR_AZUL_CLARO = "#3B82F6"

class TelaEmprestimos(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        self.cor_bg = str(COR_BG)
        self.cor_card = str(COR_CARD)
        self.cor_dourado = str(COR_DOURADO)
        self.cor_texto = str(COR_TEXTO)
        self.cor_texto2 = str(COR_TEXTO2)
        self.cor_border = str(COR_INPUT_BORDER)

        super().__init__(master, fg_color=self.cor_bg)
        self.controller = controller
        self._aba_atual = "emprestimos"
        self._itens_lista = []
        self._itens_reserva = []
        self._itens_multa = []
        self._selecionado = None
        self._reserva_selecionada = None
        self._multa_selecionada = None
        self._construir_ui()

    def _ao_visitar(self):
        verificar_atrasos()
        self._mostrar_aba(self._aba_atual)

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
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(60, 60))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                pass
        
        # Título da tela ao lado do logo
        criar_titulo(header_left, "Gerenciamento de Empréstimos", font=("Segoe UI", 20, "bold")).pack(side="left")

        btn_voltar = ctk.CTkButton(
            header, text="Voltar", command=self._voltar, 
            width=100, height=35, fg_color=COR_AZUL_PRINCIPAL, hover_color=COR_AZUL_HOVER,
            font=("Segoe UI", 12, "bold")
        )
        btn_voltar.pack(side="right")

        # === SELETOR DE ABAS AZUL CORPORATIVO ===
        abas_frame = ctk.CTkFrame(self, fg_color="transparent")
        abas_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(5, 5))

        self._botoes_abas = []
        for nome in ["Empréstimos", "Reservas", "Multas"]:
            tag = "emprestimos" if nome == "Empréstimos" else nome.lower()
            is_atual = (tag == self._aba_atual)
            
            btn = ctk.CTkButton(
                abas_frame, text=nome, font=("Segoe UI", 12, "bold"),
                fg_color=COR_AZUL_PRINCIPAL if is_atual else "transparent",
                text_color="#FFFFFF" if is_atual else self.cor_texto,
                border_color=COR_AZUL_PRINCIPAL if is_atual else self.cor_bg, 
                border_width=1 if is_atual else 0,
                hover_color=COR_AZUL_HOVER,
                width=120, height=35,
                command=lambda n=tag: self._mostrar_aba(n)
            )
            btn.pack(side="left", padx=(0, 5))
            self._botoes_abas.append((btn, tag))

        # === CONTAINER PRINCIPAL DE CONTEÚDO ===
        self._frame_conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_conteudo.grid(row=2, column=0, sticky="nsew", padx=30, pady=(5, 20))
        self._frame_conteudo.grid_columnconfigure(0, weight=1)
        self._frame_conteudo.grid_rowconfigure(0, weight=1)

        self._frame_emprestimos = ctk.CTkFrame(self._frame_conteudo, fg_color="transparent")
        self._frame_reservas = ctk.CTkFrame(self._frame_conteudo, fg_color="transparent")
        self._frame_multas = ctk.CTkFrame(self._frame_conteudo, fg_color="transparent")

        self._construir_aba_emprestimos()
        self._construir_aba_reservas()
        self._construir_aba_multas()

        self.lbl_notificacao = criar_label(self, "", text_color=self.cor_texto2)

    def _mostrar_aba(self, nome):
        self._aba_atual = nome
        for btn, n in self._botoes_abas:
            if n == nome:
                btn.configure(
                    fg_color=COR_AZUL_PRINCIPAL, 
                    text_color="#FFFFFF", 
                    border_color=COR_AZUL_PRINCIPAL,
                    border_width=1
                )
            else:
                btn.configure(
                    fg_color="transparent", 
                    text_color=self.cor_texto, 
                    border_color=self.cor_bg,
                    border_width=0
                )

        self._frame_emprestimos.grid_forget()
        self._frame_reservas.grid_forget()
        self._frame_multas.grid_forget()

        if nome == "emprestimos":
            self._frame_emprestimos.grid(row=0, column=0, sticky="nsew")
            self._recarregar_emprestimos()
        elif nome == "reservas":
            self._frame_reservas.grid(row=0, column=0, sticky="nsew")
            self._recarregar_reservas()
        elif nome == "multas":
            self._frame_multas.grid(row=0, column=0, sticky="nsew")
            self._recarregar_multas()

    def _construir_aba_emprestimos(self):
        frame = self._frame_emprestimos
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        form_card = criar_card(frame)
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="x", padx=25, pady=20)
        form.grid_columnconfigure((0, 1), weight=1)

        criar_label(form, "Selecione o Aluno beneficiário", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.combo_aluno = criar_combo(form, height=40)
        self.combo_aluno.grid(row=1, column=0, padx=(0, 15), pady=(0, 10), sticky="ew")

        criar_label(form, "Selecione o Exemplar físico", font=("Segoe UI", 11)).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self.combo_exemplar = criar_combo(form, height=40)
        self.combo_exemplar.grid(row=1, column=1, padx=(15, 0), pady=(0, 10), sticky="ew")

        criar_label(form, "Prazo Limite para Devolução (AAAA-MM-DD)", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="w", pady=(5, 2))
        self.entry_vencimento = criar_entry(form, placeholder="Ex: 2026-12-31", height=40)
        self.entry_vencimento.grid(row=3, column=0, padx=(0, 15), sticky="ew")

        botoes_frame = ctk.CTkFrame(form, fg_color="transparent")
        botoes_frame.grid(row=3, column=1, padx=(15, 0), sticky="ew")

        self.btn_cadastrar = ctk.CTkButton(
            botoes_frame, text="Confirmar Empréstimo", command=self._cadastrar_emprestimo,
            width=180, height=40, fg_color=COR_AZUL_PRINCIPAL, hover_color=COR_AZUL_HOVER,
            font=("Segoe UI", 11, "bold")
        )
        self.btn_cadastrar.pack(side="left", padx=(0, 12))

        self.btn_finalizar = ctk.CTkButton(
            botoes_frame, text="Finalizar Selecionado", command=self._finalizar_emprestimo,
            width=160, height=40, fg_color="transparent", border_color=COR_AZUL_CLARO, border_width=1,
            hover_color="#0F172A", text_color=COR_AZUL_CLARO, font=("Segoe UI", 11, "bold")
        )
        self.btn_finalizar.pack(side="left")

        # Tabela
        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent", height=30)
        header_lista.pack(fill="x", padx=15, pady=(10, 5))
        header_lista.pack_propagate(False)

        colunas_ajustadas = [("ID", 0.06), ("Beneficiário", 0.22), ("Cód. Patrimônio", 0.16), ("Título do Livro", 0.22), ("Retirada", 0.12), ("Vencimento", 0.12), ("Status", 0.1)]
        x_header = 0
        for txt, pct in colunas_ajustadas:
            lbl_h = criar_label(header_lista, txt.upper(), font=("Segoe UI", 9, "bold"), text_color=COR_AZUL_CLARO, anchor="w")
            lbl_h.place(relx=x_header + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            x_header += pct

        self.lista_emprestimos = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_emprestimos.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _construir_aba_reservas(self):
        frame = self._frame_reservas
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        form_card = criar_card(frame)
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="x", padx=25, pady=20)
        form.grid_columnconfigure((0, 1), weight=1)

        criar_label(form, "Selecione o Aluno", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.combo_reserva_aluno = criar_combo(form, height=40)
        self.combo_reserva_aluno.grid(row=1, column=0, padx=(0, 15), pady=(0, 10), sticky="ew")

        criar_label(form, "Selecione a Obra / Livro", font=("Segoe UI", 11)).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self.combo_reserva_livro = criar_combo(form, height=40)
        self.combo_reserva_livro.grid(row=1, column=1, padx=(15, 0), pady=(0, 10), sticky="ew")

        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        self.btn_reservar = ctk.CTkButton(
            botoes, text="Efetuar Nova Reserva", command=self._reservar,
            width=180, height=40, fg_color=COR_AZUL_PRINCIPAL, hover_color=COR_AZUL_HOVER,
            font=("Segoe UI", 11, "bold")
        )
        self.btn_reservar.pack(side="left", padx=(0, 12))

        self.btn_cancelar_reserva = ctk.CTkButton(
            botoes, text="Cancelar Selecionada", command=self._cancelar_reserva,
            width=180, height=40, fg_color="transparent", border_color=COR_AZUL_CLARO, border_width=1,
            hover_color="#0F172A", text_color=COR_AZUL_CLARO, font=("Segoe UI", 11, "bold")
        )
        self.btn_cancelar_reserva.pack(side="left")

        # Tabela
        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent", height=30)
        header_lista.pack(fill="x", padx=15, pady=(10, 5))
        header_lista.pack_propagate(False)

        colunas_res = [("ID", 0.06), ("Beneficiário", 0.25), ("Obra Reservada", 0.3), ("Data Solicitação", 0.14), ("Prazo Retirada", 0.15), ("Situação", 0.1)]
        x_header = 0
        for txt, pct in colunas_res:
            lbl_h = criar_label(header_lista, txt.upper(), font=("Segoe UI", 9, "bold"), text_color=COR_AZUL_CLARO, anchor="w")
            lbl_h.place(relx=x_header + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            x_header += pct

        self.lista_reservas = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_reservas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _construir_aba_multas(self):
        frame = self._frame_multas
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 15))

        self.btn_pagar = ctk.CTkButton(
            header_frame, text="Dar Baixa / Registrar Pagamento", command=self._pagar_multa,
            width=260, height=42, fg_color=COR_AZUL_PRINCIPAL, hover_color=COR_AZUL_HOVER,
            font=("Segoe UI", 11, "bold")
        )
        self.btn_pagar.pack(side="left")

        # Tabela
        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent", height=30)
        header_lista.pack(fill="x", padx=15, pady=(10, 5))
        header_lista.pack_propagate(False)

        colunas_mul = [("ID", 0.06), ("Valor (R$)", 0.1), ("Dias", 0.08), ("Motivo Ocorrência", 0.14), ("Situação", 0.1), ("Geração", 0.12), ("Estudante", 0.22), ("Obra Atrelada", 0.18)]
        x_header = 0
        for txt, pct in colunas_mul:
            lbl_h = criar_label(header_lista, txt.upper(), font=("Segoe UI", 9, "bold"), text_color=COR_AZUL_CLARO, anchor="w")
            lbl_h.place(relx=x_header + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            x_header += pct

        self.lista_multas = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_multas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _recarregar_emprestimos(self):
        for widget in self.lista_emprestimos.winfo_children():
            widget.destroy()
        self._itens_lista = []
        self._selecionado = None

        alunos = listar_alunos()
        self._alunos_map = {}
        for a in alunos:
            texto = f"{a[0]} - {a[1]}"
            self._alunos_map[texto] = a[0]
        self.combo_aluno.configure(values=list(self._alunos_map.keys()))
        if self._alunos_map:
            self.combo_aluno.set(list(self._alunos_map.keys())[0])

        exemplares = listar_exemplares_disponiveis()
        self._exemplares_map = {}
        for e in exemplares:
            texto = f"{e[0]} - {e[1]}"
            self._exemplares_map[texto] = e[0]
        self.combo_exemplar.configure(values=list(self._exemplares_map.keys()))
        if self._exemplares_map:
            self.combo_exemplar.set(list(self._exemplares_map.keys())[0])

        emprestimos = listar_emprestimos()
        for emp in emprestimos:
            self._criar_item_emp(emp)

    def _criar_item_emp(self, emp):
        item = ctk.CTkFrame(self.lista_emprestimos, fg_color=self.cor_card, corner_radius=8, height=42)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)
        item.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))

        colunas = [0.06, 0.22, 0.16, 0.22, 0.12, 0.12, 0.1]
        x = 0
        for i, (texto, pct) in enumerate(zip(emp, colunas)):
            cor = self.cor_texto
            if i == 6 and str(texto).lower() == "atrasado":
                cor = "#EF4444" 
            elif i == 6 and str(texto).lower() == "ativo":
                cor = COR_AZUL_CLARO
            lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 10), text_color=cor, anchor="w")
            lbl.place(relx=x + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            lbl.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))
            x += pct

        self._itens_lista.append((item, emp))

    def _selecionar(self, emp):
        for item, e in self._itens_lista:
            if e == emp:
                item.configure(fg_color="#1E293B")
            else:
                item.configure(fg_color=self.cor_card)
        self._selecionado = emp

    def _cadastrar_emprestimo(self):
        aluno_sel = self.combo_aluno.get()
        exemplar_sel = self.combo_exemplar.get()
        vencimento = self.entry_vencimento.get().strip()

        if not aluno_sel or aluno_sel not in self._alunos_map:
            self._notificar("Selecione um aluno válido.")
            return
        if not exemplar_sel or exemplar_sel not in self._exemplares_map:
            self._notificar("Selecione um exemplar disponível.")
            return
        if not vencimento:
            self._notificar("Informe a data prevista de devolução.")
            return

        id_usuario = self._alunos_map[aluno_sel]
        id_exemplar = self._exemplares_map[exemplar_sel]
        id_funcionario = self.controller.usuario_logado['id'] if self.controller and hasattr(self.controller, 'usuario_logado') else 1

        if usuario_tem_multa_pendente(id_usuario):
            self._notificar("Aluno com multa pendente! Regularize primeiro.")
            return

        self.btn_cadastrar.configure(text="Processando...", state="disabled")
        self.after(500, lambda: self._salvar_emprestimo(id_usuario, id_exemplar, vencimento, id_funcionario))

    def _salvar_emprestimo(self, id_usuario, id_exemplar, vencimento, id_funcionario):
        sucesso = cadastrar_emprestimo(id_usuario, id_exemplar, vencimento, id_funcionario)
        if sucesso:
            self._notificar("Empréstimo registrado com sucesso!")
            self.entry_vencimento.delete(0, "end")
            self._recarregar_emprestimos()
        else:
            self._notificar("Erro operacional ao salvar empréstimo.")
        self.btn_cadastrar.configure(text="Confirmar Empréstimo", state="normal")

    def _finalizar_emprestimo(self):
        if not self._selecionado:
            self._notificar("Selecione um registro na listagem abaixo.")
            return
        emp_id = self._selecionado[0]
        sucesso = finalizar_emprestimo(emp_id)
        if sucesso:
            self._notificar("Empréstimo finalizado / Devolvido!")
            self._selecionado = None
            self._recarregar_emprestimos()
        else:
            self._notificar("Erro ao processar devolução.")

    def _recarregar_reservas(self):
        for widget in self.lista_reservas.winfo_children():
            widget.destroy()
        self._itens_reserva = []
        self._reserva_selecionada = None

        alunos = listar_alunos()
        self._reserva_alunos_map = {}
        for a in alunos:
            texto = f"{a[0]} - {a[1]}"
            self._reserva_alunos_map[texto] = a[0]
        self.combo_reserva_aluno.configure(values=list(self._reserva_alunos_map.keys()))
        if self._reserva_alunos_map:
            self.combo_reserva_aluno.set(list(self._reserva_alunos_map.keys())[0])

        livros = listar_livros()
        self._reserva_livros_map = {}
        for l in livros:
            texto = f"{l[1]} ({l[2]})"
            self._reserva_livros_map[texto] = l[0]
        self.combo_reserva_livro.configure(values=list(self._reserva_livros_map.keys()))
        if self._reserva_livros_map:
            self.combo_reserva_livro.set(list(self._reserva_livros_map.keys())[0])

        reservas = listar_reservas(status="ativa")
        for r in reservas:
            item = ctk.CTkFrame(self.lista_reservas, fg_color=self.cor_card, corner_radius=8, height=42)
            item.pack(fill="x", pady=2)
            item.pack_propagate(False)
            item.bind("<Button-1>", lambda e, v=r: self._selecionar_reserva(v))

            colunas = [0.06, 0.25, 0.3, 0.14, 0.15, 0.1]
            x = 0
            for texto, pct in zip(r, colunas):
                lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 10), text_color=self.cor_texto, anchor="w")
                lbl.place(relx=x + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
                lbl.bind("<Button-1>", lambda e, v=r: self._selecionar_reserva(v))
                x += pct
            self._itens_reserva.append((item, r))

    def _selecionar_reserva(self, r):
        for item, v in self._itens_reserva:
            if v == r:
                item.configure(fg_color="#1E293B")
            else:
                item.configure(fg_color=self.cor_card)
        self._reserva_selecionada = r

    def _reservar(self):
        aluno_sel = self.combo_reserva_aluno.get()
        livro_sel = self.combo_reserva_livro.get()

        if not aluno_sel or aluno_sel not in self._reserva_alunos_map:
            self._notificar("Selecione um aluno válido.")
            return
        if not livro_sel or livro_sel not in self._reserva_livros_map:
            self._notificar("Selecione uma obra válida.")
            return

        id_usuario = self._reserva_alunos_map[aluno_sel]
        id_livro = self._reserva_livros_map[livro_sel]

        self.btn_reservar.configure(text="Salvando...", state="disabled")
        self.after(500, lambda: self._salvar_reserva(id_usuario, id_livro))

    def _salvar_reserva(self, id_usuario, id_livro):
        sucesso = cadastrar_reserva(id_usuario, id_livro)
        if sucesso:
            self._notificar("Reserva ativada com sucesso!")
            self._recarregar_reservas()
        else:
            self._notificar("Erro ao gerar reserva para esta obra.")
        self.btn_reservar.configure(text="Efetuar Nova Reserva", state="normal")

    def _cancelar_reserva(self):
        if not self._reserva_selecionada:
            self._notificar("Selecione uma reserva ativa abaixo.")
            return
        id_reserva = self._reserva_selecionada[0]
        sucesso = cancelar_reserva(id_reserva)
        if sucesso:
            self._notificar("Reserva removida do sistema.")
            self._reserva_selecionada = None
            self._recarregar_reservas()
        else:
            self._notificar("Erro ao cancelar transação de reserva.")

    def _recarregar_multas(self):
        for widget in self.lista_multas.winfo_children():
            widget.destroy()
        self._itens_multa = []
        self._multa_selecionada = None

        multas = listar_multas()
        for m in multas:
            item = ctk.CTkFrame(self.lista_multas, fg_color=self.cor_card, corner_radius=8, height=42)
            item.pack(fill="x", pady=2)
            item.pack_propagate(False)
            item.bind("<Button-1>", lambda e, v=m: self._selecionar_multa(v))

            colunas = [0.06, 0.1, 0.08, 0.14, 0.1, 0.12, 0.22, 0.18]
            x = 0
            for i, (texto, pct) in enumerate(zip(m, colunas)):
                cor = self.cor_texto
                if i == 4 and str(texto).lower() == "pendente":
                    cor = "#EF4444"
                elif i == 4 and str(texto).lower() == "pago":
                    cor = "#10B981"
                lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 10), text_color=cor, anchor="w")
                lbl.place(relx=x + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
                lbl.bind("<Button-1>", lambda e, v=m: self._selecionar_multa(v))
                x += pct
            self._itens_multa.append((item, m))

    def _selecionar_multa(self, m):
        for item, v in self._itens_multa:
            if v == m:
                item.configure(fg_color="#1E293B")
            else:
                item.configure(fg_color=self.cor_card)
        self._multa_selecionada = m

    def _pagar_multa(self):
        if not self._multa_selecionada:
            self._notificar("Selecione uma multa na tabela.")
            return
        if str(self._multa_selecionada[4]).lower() == "pago":
            self._notificar("O débito selecionado já consta como pago.")
            return
        id_multa = self._multa_selecionada[0]
        sucesso = pagar_multa(id_multa)
        if sucesso:
            self._notificar("Baixa de pagamento registrada!")
            self._multa_selecionada = None
            self._recarregar_multas()
        else:
            self._notificar("Erro interno ao liquidar multa.")

    def _voltar(self):
        if self.controller:
            self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color=COR_AZUL_CLARO)
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))