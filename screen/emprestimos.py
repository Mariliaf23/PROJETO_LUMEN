import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from datetime import date
from services.database_config import (
    cadastrar_emprestimo, listar_emprestimos, finalizar_emprestimo,
    listar_alunos, listar_exemplares_disponiveis, verificar_atrasos,
    cadastrar_reserva, listar_reservas, cancelar_reserva,
    listar_multas, pagar_multa, usuario_tem_multa_pendente,
    listar_livros, gerar_multa, listar_emprestimos_ativos
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_entry, criar_botao_preenchido, criar_botao, criar_label, criar_titulo,
    criar_card, criar_scroll_frame, criar_combo
)


class DetalheEmprestimo(ctk.CTkToplevel):
    def __init__(self, master, dados):
        super().__init__(master)
        self.title("Detalhes do Emprestimo")
        self.geometry("400x350")
        self.resizable(False, False)
        self.configure(fg_color=COR_BG)
        self.grab_set()

        criar_titulo(self, "LUMEN", font=("Cinzel", 20, "bold")).pack(pady=(20, 5))
        criar_label(self, "Detalhes do Emprestimo", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(pady=(0, 20))

        card = criar_card(self)
        card.pack(fill="x", padx=30, pady=(0, 10))

        id_emp, aluno, exemplar, livro, data_emp, data_prev, data_dev, status = dados

        campos = [
            ("ID", str(id_emp)),
            ("Aluno", str(aluno)),
            ("Livro", str(livro)),
            ("Exemplar", str(exemplar)),
            ("Data Emprestimo", str(data_emp)),
            ("Data Prevista", str(data_prev)),
            ("Data Devolucao", str(data_dev) if data_dev else "Pendente"),
            ("Status", str(status)),
        ]

        for rotulo, valor in campos:
            linha = ctk.CTkFrame(card, fg_color="transparent")
            linha.pack(fill="x", padx=15, pady=4)
            criar_label(linha, f"{rotulo}:", font=FONTE_LABEL, text_color=COR_DOURADO).pack(side="left")
            cor_valor = COR_TEXTO
            if rotulo == "Status":
                if valor == "atrasado":
                    cor_valor = "#8a4040"
                elif valor == "finalizado":
                    cor_valor = "#4a8a4a"
                elif valor == "ativo":
                    cor_valor = "#d4b896"
            criar_label(linha, valor, font=FONTE_LABEL, text_color=cor_valor).pack(side="right")

        criar_botao_preenchido(self, text="Fechar", command=self.destroy, width=120, height=36).pack(pady=15)


class TelaEmprestimos(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._aba_atual = "emprestimos"
        self._itens_lista = []
        self._selecionado = None
        self._construir_ui()

    def _ao_visitar(self):
        verificar_atrasos()
        self._mostrar_aba(self._aba_atual)

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        criar_titulo(header, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left")
        criar_label(header, "Emprestimos e Devolucoes", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(side="left", padx=(15, 0))

        btn_voltar = criar_botao(header, text="Voltar", command=self._voltar, width=100, height=35)
        btn_voltar.pack(side="right")

        abas_frame = ctk.CTkFrame(self, fg_color="transparent")
        abas_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 5))

        self._botoes_abas = []
        for nome in ["Emprestimos", "Reservas", "Multas"]:
            btn = ctk.CTkButton(
                abas_frame, text=nome, font=FONTE_LABEL,
                fg_color=COR_CARD if nome.lower() != self._aba_atual else COR_DOURADO,
                text_color=COR_TEXTO if nome.lower() != self._aba_atual else COR_BG,
                hover_color=COR_DOURADO,
                width=140, height=35,
                command=lambda n=nome.lower(): self._mostrar_aba(n)
            )
            btn.pack(side="left", padx=(0, 5))
            self._botoes_abas.append((btn, nome.lower()))

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

        self.lbl_notificacao = criar_label(self, "", text_color=COR_TEXTO2)

    def _mostrar_aba(self, nome):
        self._aba_atual = nome
        for btn, n in self._botoes_abas:
            if n == nome:
                btn.configure(fg_color=COR_DOURADO, text_color=COR_BG)
            else:
                btn.configure(fg_color=COR_CARD, text_color=COR_TEXTO)

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
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        form_card.grid_columnconfigure((0, 1), weight=1)

        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=15)
        form.grid_columnconfigure((0, 1), weight=1)

        criar_label(form, "Usuario", font=FONTE_LABEL).grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.combo_aluno = criar_combo(form, width=280, height=38)
        self.combo_aluno.grid(row=1, column=0, padx=(0, 10), sticky="ew")

        criar_label(form, "Livro (Acervo)", font=FONTE_LABEL).grid(row=0, column=1, sticky="w", pady=(0, 3))
        self.combo_exemplar = criar_combo(form, width=280, height=38)
        self.combo_exemplar.grid(row=1, column=1, padx=(10, 0), sticky="ew")

        criar_label(form, "Data Prevista (AAAA-MM-DD)", font=FONTE_LABEL).grid(row=2, column=0, sticky="w", pady=(10, 3))
        self.entry_vencimento = criar_entry(form, placeholder="AAAA-MM-DD", height=38)
        self.entry_vencimento.grid(row=3, column=0, padx=(0, 10), sticky="ew")

        botoes_frame = ctk.CTkFrame(form, fg_color="transparent")
        botoes_frame.grid(row=3, column=1, padx=(10, 0), sticky="ew")

        self.btn_cadastrar = criar_botao_preenchido(
            botoes_frame, text="Novo Emprestimo", command=self._cadastrar_emprestimo,
            width=160, height=38
        )
        self.btn_cadastrar.pack(side="left", padx=(0, 10))

        self.btn_devolver = criar_botao_preenchido(
            botoes_frame, text="Registrar Devolucao", command=self._devolver,
            width=180, height=38, fg_color="#4a8a4a", hover_color="#5a9a5a"
        )
        self.btn_devolver.pack(side="left")

        self.btn_detalhes = criar_botao(
            botoes_frame, text="Detalhes", command=self._abrir_detalhes,
            width=100, height=38
        )
        self.btn_detalhes.pack(side="left", padx=(10, 0))

        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_lista.pack(fill="x", padx=15, pady=(10, 5))

        self.entry_busca_emp = criar_entry(header_lista, placeholder="Buscar por usuario ou livro...", width=250, height=32)
        self.entry_busca_emp.pack(side="left", padx=(0, 10))
        self.entry_busca_emp.bind("<Return>", lambda e: self._buscar_emprestimos())

        ctk.CTkButton(
            header_lista, text="Buscar", width=70, height=32,
            fg_color=COR_DOURADO, text_color="#000",
            command=self._buscar_emprestimos
        ).pack(side="left")

        for col, txt in [("ID", 0.05), ("Usuario", 0.15), ("Exemplar", 0.12), ("Livro", 0.18), ("Emprestimo", 0.12), ("Previsto", 0.12), ("Devolucao", 0.13), ("Status", 0.1)]:
            criar_label(header_lista, txt, font=("Segoe UI", 9, "bold"), text_color=COR_DOURADO).pack(side="left", expand=True, fill="x")

        self.lista_emprestimos = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_emprestimos.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _construir_aba_reservas(self):
        frame = self._frame_reservas
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        form_card = criar_card(frame)
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=15)
        form.grid_columnconfigure((0, 1), weight=1)

        criar_label(form, "Usuario", font=FONTE_LABEL).grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.combo_reserva_aluno = criar_combo(form, width=280, height=38)
        self.combo_reserva_aluno.grid(row=1, column=0, padx=(0, 10), sticky="ew")

        criar_label(form, "Livro", font=FONTE_LABEL).grid(row=0, column=1, sticky="w", pady=(0, 3))
        self.combo_reserva_livro = criar_combo(form, width=280, height=38)
        self.combo_reserva_livro.grid(row=1, column=1, padx=(10, 0), sticky="ew")

        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        self.btn_reservar = criar_botao_preenchido(
            botoes, text="Reservar", command=self._reservar, width=160, height=38
        )
        self.btn_reservar.pack(side="left", padx=(0, 10))

        self.btn_cancelar_reserva = criar_botao(
            botoes, text="Cancelar", command=self._cancelar_reserva,
            width=120, height=38, border_color="#8a4040", text_color="#8a4040"
        )
        self.btn_cancelar_reserva.pack(side="left")

        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_lista.pack(fill="x", padx=15, pady=(10, 5))

        for col, txt in [("ID", 0.06), ("Usuario", 0.25), ("Livro", 0.3), ("Reserva", 0.12), ("Validade", 0.12), ("Status", 0.1)]:
            criar_label(header_lista, txt, font=("Segoe UI", 9, "bold"), text_color=COR_DOURADO).pack(side="left", expand=True, fill="x")

        self.lista_reservas = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_reservas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _construir_aba_multas(self):
        frame = self._frame_multas
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.btn_pagar = criar_botao_preenchido(
            header_frame, text="Registrar Pagamento", command=self._pagar_multa,
            width=200, height=38
        )
        self.btn_pagar.pack(side="left")

        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_lista.pack(fill="x", padx=15, pady=(10, 5))

        for col, txt in [("ID", 0.06), ("Valor", 0.1), ("Dias", 0.08), ("Motivo", 0.1), ("Status", 0.1), ("Data", 0.12), ("Aluno", 0.2), ("Livro", 0.15)]:
            criar_label(header_lista, txt, font=("Segoe UI", 9, "bold"), text_color=COR_DOURADO).pack(side="left", expand=True, fill="x")

        self.lista_multas = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_multas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _recarregar_emprestimos(self, emprestimos_filtrados=None):
        for widget in self.lista_emprestimos.winfo_children():
            widget.destroy()
        self._itens_lista = []
        self._selecionado = None

        alunos = listar_alunos()
        self._alunos_map = {}
        nomes_alunos = []
        for a in alunos:
            texto = f"{a[0]} - {a[1]}"
            self._alunos_map[texto] = a[0]
            nomes_alunos.append(texto)
        self.combo_aluno.configure(values=nomes_alunos if nomes_alunos else [" Selecione..."])
        if nomes_alunos:
            self.combo_aluno.set(nomes_alunos[0])
        else:
            self.combo_aluno.set(" Selecione...")

        exemplares = listar_exemplares_disponiveis()
        self._exemplares_map = {}
        nomes_exemplares = []
        for e in exemplares:
            texto = f"{e[2]} ({e[1]})"
            self._exemplares_map[texto] = e[0]
            nomes_exemplares.append(texto)
        self.combo_exemplar.configure(values=nomes_exemplares if nomes_exemplares else [" Selecione..."])
        if nomes_exemplares:
            self.combo_exemplar.set(nomes_exemplares[0])
        else:
            self.combo_exemplar.set(" Selecione...")

        if emprestimos_filtrados is not None:
            emprestimos = emprestimos_filtrados
        else:
            emprestimos = listar_emprestimos()
        for emp in emprestimos:
            self._criar_item_emp(emp)

    def _buscar_emprestimos(self):
        termo = self.entry_busca_emp.get().strip().lower()
        if not termo:
            self._recarregar_emprestimos()
            return
        todos = listar_emprestimos()
        filtrados = [e for e in todos if termo in str(e[1]).lower() or termo in str(e[3]).lower()]
        self._recarregar_emprestimos(filtrados)

    def _criar_item_emp(self, emp):
        item = ctk.CTkFrame(self.lista_emprestimos, fg_color=COR_CARD, corner_radius=8, height=40)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)
        item.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))

        colunas = [0.05, 0.15, 0.12, 0.18, 0.12, 0.12, 0.13, 0.1]
        x = 0
        for i, (texto, pct) in enumerate(zip(emp, colunas)):
            cor = COR_TEXTO
            if i == 7 and str(texto) in ("atrasado",):
                cor = "#8a4040"
            elif i == 7 and str(texto) == "ativo":
                cor = "#d4b896"
            elif i == 7 and str(texto) == "finalizado":
                cor = "#4a8a4a"
            lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 9), text_color=cor, anchor="w")
            lbl.place(relx=x + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            lbl.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))
            x += pct

        self._itens_lista.append((item, emp))

    def _selecionar(self, emp):
        for item, e in self._itens_lista:
            if e == emp:
                item.configure(fg_color="#2a1a08")
            else:
                item.configure(fg_color=COR_CARD)
        self._selecionado = emp

    def _abrir_detalhes(self):
        if not self._selecionado:
            self._notificar("Selecione um emprestimo para ver detalhes.")
            return
        DetalheEmprestimo(self, self._selecionado)

    def _cadastrar_emprestimo(self):
        aluno_sel = self.combo_aluno.get()
        exemplar_sel = self.combo_exemplar.get()
        vencimento = self.entry_vencimento.get().strip()

        if not aluno_sel or aluno_sel == " Selecione..." or aluno_sel not in self._alunos_map:
            self._notificar("Selecione um usuario valido.")
            return
        if not exemplar_sel or exemplar_sel == " Selecione..." or exemplar_sel not in self._exemplares_map:
            self._notificar("Selecione um exemplar disponivel.")
            return
        if not vencimento:
            self._notificar("Informe a data prevista de devolucao.")
            return

        id_usuario = self._alunos_map[aluno_sel]
        id_exemplar = self._exemplares_map[exemplar_sel]
        id_funcionario = self.controller.usuario_logado['id']

        if usuario_tem_multa_pendente(id_usuario):
            self._notificar("Usuario com multa pendente! Regularize primeiro.")
            return

        self.btn_cadastrar.configure(text="Criando...", state="disabled")
        self.after(500, lambda: self._salvar_emprestimo(id_usuario, id_exemplar, vencimento, id_funcionario))

    def _salvar_emprestimo(self, id_usuario, id_exemplar, vencimento, id_funcionario):
        sucesso = cadastrar_emprestimo(id_usuario, id_exemplar, vencimento, id_funcionario)
        if sucesso:
            self._notificar("Emprestimo realizado!")
            self.entry_vencimento.delete(0, "end")
            self._recarregar_emprestimos()
        else:
            self._notificar("Erro ao criar emprestimo.")
        self.btn_cadastrar.configure(text="Novo Emprestimo", state="normal")

    def _devolver(self):
        if not self._selecionado:
            self._notificar("Selecione um emprestimo para devolver.")
            return
        emp_id = self._selecionado[0]
        status = str(self._selecionado[6])
        if status == "finalizado":
            self._notificar("Este emprestimo ja foi finalizado.")
            return
        self.btn_devolver.configure(text="Processando...", state="disabled")
        self.after(500, lambda: self._processar_devolucao(emp_id))

    def _processar_devolucao(self, emp_id):
        data_prevista_str = str(self._selecionado[5])
        mensagem_multa = ""
        try:
            partes = data_prevista_str.split("-")
            data_prevista = date(int(partes[0]), int(partes[1]), int(partes[2]))
            hoje = date.today()
            dias_atraso = (hoje - data_prevista).days

            if dias_atraso > 0:
                gerar_multa(emp_id, dias_atraso, 'atraso')
                mensagem_multa = f" Multa: {dias_atraso} dias de atraso."
        except Exception:
            pass

        reserva_info = finalizar_emprestimo(emp_id)
        if reserva_info:
            id_res, nome_res, titulo_res = reserva_info
            self._notificar(f"Devolucao registrada!{mensagem_multa} Reserva: {nome_res} - {titulo_res}")
        elif mensagem_multa:
            self._notificar(f"Devolucao registrada!{mensagem_multa}")
        else:
            self._notificar("Devolucao registrada com sucesso!")

        self._selecionado = None
        self._recarregar_emprestimos()
        self.btn_devolver.configure(text="Registrar Devolucao", state="normal")

    def _recarregar_reservas(self):
        for widget in self.lista_reservas.winfo_children():
            widget.destroy()
        self._itens_reserva = []
        self._reserva_selecionada = None

        alunos = listar_alunos()
        self._reserva_alunos_map = {}
        nomes_alunos = []
        for a in alunos:
            texto = f"{a[0]} - {a[1]}"
            self._reserva_alunos_map[texto] = a[0]
            nomes_alunos.append(texto)
        self.combo_reserva_aluno.configure(values=nomes_alunos if nomes_alunos else [" Selecione..."])
        if nomes_alunos:
            self.combo_reserva_aluno.set(nomes_alunos[0])
        else:
            self.combo_reserva_aluno.set(" Selecione...")

        livros = listar_livros()
        self._reserva_livros_map = {}
        nomes_livros = []
        for l in livros:
            texto = f"{l[1]} ({l[2]})"
            self._reserva_livros_map[texto] = l[0]
            nomes_livros.append(texto)
        self.combo_reserva_livro.configure(values=nomes_livros if nomes_livros else [" Selecione..."])
        if nomes_livros:
            self.combo_reserva_livro.set(nomes_livros[0])
        else:
            self.combo_reserva_livro.set(" Selecione...")

        reservas = listar_reservas(status="ativa")
        for r in reservas:
            item = ctk.CTkFrame(self.lista_reservas, fg_color=COR_CARD, corner_radius=8, height=40)
            item.pack(fill="x", pady=2)
            item.pack_propagate(False)
            item.bind("<Button-1>", lambda e, v=r: self._selecionar_reserva(v))

            colunas = [0.06, 0.25, 0.3, 0.12, 0.12, 0.1]
            x = 0
            for texto, pct in zip(r, colunas):
                lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 9), text_color=COR_TEXTO, anchor="w")
                lbl.place(relx=x + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
                lbl.bind("<Button-1>", lambda e, v=r: self._selecionar_reserva(v))
                x += pct
            self._itens_reserva.append((item, r))

    def _selecionar_reserva(self, r):
        for item, v in self._itens_reserva:
            if v == r:
                item.configure(fg_color="#2a1a08")
            else:
                item.configure(fg_color=COR_CARD)
        self._reserva_selecionada = r

    def _reservar(self):
        aluno_sel = self.combo_reserva_aluno.get()
        livro_sel = self.combo_reserva_livro.get()

        if not aluno_sel or aluno_sel == " Selecione..." or aluno_sel not in self._reserva_alunos_map:
            self._notificar("Selecione um usuario valido.")
            return
        if not livro_sel or livro_sel == " Selecione..." or livro_sel not in self._reserva_livros_map:
            self._notificar("Selecione um livro valido.")
            return

        id_usuario = self._reserva_alunos_map[aluno_sel]
        id_livro = self._reserva_livros_map[livro_sel]

        self.btn_reservar.configure(text="Reservando...", state="disabled")
        self.after(500, lambda: self._salvar_reserva(id_usuario, id_livro))

    def _salvar_reserva(self, id_usuario, id_livro):
        sucesso = cadastrar_reserva(id_usuario, id_livro)
        if sucesso:
            self._notificar("Reserva realizada!")
            self._recarregar_reservas()
        else:
            self._notificar("Erro ao criar reserva.")
        self.btn_reservar.configure(text="Reservar", state="normal")

    def _cancelar_reserva(self):
        if not self._reserva_selecionada:
            self._notificar("Selecione uma reserva.")
            return
        id_reserva = self._reserva_selecionada[0]
        sucesso = cancelar_reserva(id_reserva)
        if sucesso:
            self._notificar("Reserva cancelada.")
            self._reserva_selecionada = None
            self._recarregar_reservas()
        else:
            self._notificar("Erro ao cancelar reserva.")

    def _recarregar_multas(self):
        for widget in self.lista_multas.winfo_children():
            widget.destroy()
        self._itens_multa = []
        self._multa_selecionada = None

        multas = listar_multas()
        for m in multas:
            item = ctk.CTkFrame(self.lista_multas, fg_color=COR_CARD, corner_radius=8, height=40)
            item.pack(fill="x", pady=2)
            item.pack_propagate(False)
            item.bind("<Button-1>", lambda e, v=m: self._selecionar_multa(v))

            colunas = [0.06, 0.1, 0.08, 0.1, 0.1, 0.12, 0.2, 0.15]
            x = 0
            for i, (texto, pct) in enumerate(zip(m, colunas)):
                cor = COR_TEXTO
                if i == 4 and texto == "pendente":
                    cor = "#d4b896"
                elif i == 4 and texto == "pago":
                    cor = "#4a8a4a"
                lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 9), text_color=cor, anchor="w")
                lbl.place(relx=x + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
                lbl.bind("<Button-1>", lambda e, v=m: self._selecionar_multa(v))
                x += pct
            self._itens_multa.append((item, m))

    def _selecionar_multa(self, m):
        for item, v in self._itens_multa:
            if v == m:
                item.configure(fg_color="#2a1a08")
            else:
                item.configure(fg_color=COR_CARD)
        self._multa_selecionada = m

    def _pagar_multa(self):
        if not self._multa_selecionada:
            self._notificar("Selecione uma multa.")
            return
        if self._multa_selecionada[4] == "pago":
            self._notificar("Esta multa ja foi paga.")
            return
        id_multa = self._multa_selecionada[0]
        sucesso = pagar_multa(id_multa)
        if sucesso:
            self._notificar("Multa paga!")
            self._multa_selecionada = None
            self._recarregar_multas()
        else:
            self._notificar("Erro ao pagar multa.")

    def _voltar(self):
        self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))
