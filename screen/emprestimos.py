import os
import sys
from PIL import Image
from datetime import date, timedelta

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
    criar_botao_preenchido, FONTE_LABEL, FONTE_SUBTITULO
)

# Definição das cores padrão azul corporativo
COR_AZUL_PRINCIPAL = "#1E3A8A"
COR_AZUL_HOVER = "#1D4ED8"
COR_AZUL_CLARO = "#3B82F6"


def validar_e_converter_data(entrada):
    """
    Valida e converte entrada de data:
    - Se for número: interpreta como dias a partir de hoje (ex: "1" = amanhã)
    - Se for AAAA-MM-DD: valida o formato
    
    Retorna: (sucesso, data_formatada, mensagem_erro)
    """
    entrada = entrada.strip()
    
    # Tenta interpretar como número de dias
    try:
        dias = int(entrada)
        if dias <= 0:
            return False, None, "Os dias devem ser um número positivo (ex: 1, 7, 14)."
        data_futura = date.today() + timedelta(days=dias)
        return True, data_futura.strftime("%Y-%m-%d"), None
    except ValueError:
        pass
    
    # Tenta validar como data AAAA-MM-DD
    try:
        partes = entrada.split("-")
        if len(partes) != 3:
            return False, None, "Formato inválido. Use AAAA-MM-DD (ex: 2026-12-31) ou número de dias (ex: 7)."
        
        ano, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
        data_obj = date(ano, mes, dia)
        
        if data_obj <= date.today():
            return False, None, "A data deve ser posterior a hoje."
        
        return True, data_obj.strftime("%Y-%m-%d"), None
    except (ValueError, AttributeError):
        return False, None, "Formato inválido. Use AAAA-MM-DD (ex: 2026-12-31) ou número de dias (ex: 7)."


class DetalheEmprestimo(ctk.CTkToplevel):
    def __init__(self, master, dados):
        super().__init__(master)
        self.title("Detalhes do Empréstimo")
        self.geometry("400x350")
        self.resizable(False, False)
        self.configure(fg_color=COR_BG)
        self.grab_set()

        criar_titulo(self, "LUMEN", font=("Cinzel", 20, "bold")).pack(pady=(20, 5))
        criar_label(self, "Detalhes do Empréstimo", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(pady=(0, 20))

        card = criar_card(self)
        card.pack(fill="x", padx=30, pady=(0, 10))

        id_emp, aluno, exemplar, livro, data_emp, data_prev, data_dev, status = dados

        campos = [
            ("ID", str(id_emp)),
            ("Aluno", str(aluno)),
            ("Livro", str(livro)),
            ("Exemplar", str(exemplar)),
            ("Data Empréstimo", str(data_emp)),
            ("Data Prevista", str(data_prev)),
            ("Data Devolução", str(data_dev) if data_dev else "Pendente"),
            ("Status", str(status)),
        ]

        for rotulo, valor in campos:
            linha = ctk.CTkFrame(card, fg_color="transparent")
            linha.pack(fill="x", padx=15, pady=4)
            criar_label(linha, f"{rotulo}:", font=FONTE_LABEL, text_color=COR_DOURADO).pack(side="left")
            cor_valor = COR_TEXTO
            if rotulo == "Status":
                if str(valor).lower() == "atrasado":
                    cor_valor = "#EF4444"
                elif str(valor).lower() == "finalizado":
                    cor_valor = "#10B981"
                elif str(valor).lower() == "ativo":
                    cor_valor = COR_AZUL_CLARO
            criar_label(linha, valor, font=FONTE_LABEL, text_color=cor_valor).pack(side="right")

        ctk.CTkButton(self, text="Fechar", command=self.destroy, width=160, height=50,
                      fg_color=COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
                      hover_color=COR_AZUL_HOVER, font=("Segoe UI", 16, "bold")).pack(pady=15)


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

        # HEADER
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y")

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")
        
        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(180, 180))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                pass
        
        titulo = criar_titulo(header_left, "Gerenciamento de Empréstimos", font=("Segoe UI", 38, "bold"))
        titulo.configure(text_color="white")
        titulo.pack(side="left")

        btn_voltar = ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=130, height=45,
            fg_color="#0F172A", text_color="#FFFFFF", border_color=COR_INPUT_BORDER, border_width=1,
            hover_color="#1E293B", font=("Segoe UI", 16, "bold")
        )
        btn_voltar.pack(side="right")

        # ABAS
        abas_frame = ctk.CTkFrame(self, fg_color="transparent")
        abas_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(5, 5))

        self._botoes_abas = []
        for nome in ["Empréstimos", "Reservas", "Multas"]:
            tag = "emprestimos" if nome == "Empréstimos" else nome.lower()
            is_atual = (tag == self._aba_atual)
            
            btn = ctk.CTkButton(
                abas_frame, text=nome, font=("Segoe UI", 16, "bold"),
                fg_color=COR_AZUL_PRINCIPAL if is_atual else "transparent",
                text_color="#FFFFFF" if is_atual else self.cor_texto,
                border_color=COR_AZUL_PRINCIPAL if is_atual else self.cor_bg, 
                border_width=1 if is_atual else 0,
                hover_color=COR_AZUL_HOVER,
                width=140, height=42,
                command=lambda n=tag: self._mostrar_aba(n)
            )
            btn.pack(side="left", padx=(0, 5))
            self._botoes_abas.append((btn, tag))

        # CONTAINER PRINCIPAL
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
                btn.configure(fg_color=COR_AZUL_PRINCIPAL, text_color="#FFFFFF", 
                              border_color=COR_AZUL_PRINCIPAL, border_width=1)
            else:
                btn.configure(fg_color="transparent", text_color=self.cor_texto, 
                              border_color=self.cor_bg, border_width=0)

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

        # --- SEÇÃO ALUNO COM FILTRO ---
        criar_label(form, "Selecione o Aluno beneficiário", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.entry_busca_aluno = criar_entry(form, placeholder="Digite para buscar o aluno...", height=35)
        self.entry_busca_aluno.grid(row=1, column=0, padx=(0, 15), pady=(0, 5), sticky="ew")
        self.entry_busca_aluno.bind("<KeyRelease>", lambda e: self._filtrar_dados(self.entry_busca_aluno.get(), self.combo_aluno, self._alunos_map))

        self.combo_aluno = criar_combo(form, height=40)
        self.combo_aluno.grid(row=2, column=0, padx=(0, 15), pady=(0, 10), sticky="ew")

        # --- SEÇÃO EXEMPLAR COM FILTRO ---
        criar_label(form, "Selecione o Exemplar físico", font=("Segoe UI", 14, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self.entry_busca_exemplar = criar_entry(form, placeholder="Digite para buscar o exemplar...", height=35)
        self.entry_busca_exemplar.grid(row=1, column=1, padx=(15, 0), pady=(0, 5), sticky="ew")
        self.entry_busca_exemplar.bind("<KeyRelease>", lambda e: self._filtrar_dados(self.entry_busca_exemplar.get(), self.combo_exemplar, self._exemplares_map))

        self.combo_exemplar = criar_combo(form, height=40)
        self.combo_exemplar.grid(row=2, column=1, padx=(15, 0), pady=(0, 10), sticky="ew")

        # --- PRAZO LIMITE ---
        criar_label(form, "Prazo Limite para Devolução", font=("Segoe UI", 16, "bold")).grid(row=3, column=0, sticky="w", pady=(5, 2))
        criar_label(form, "(Digite dias: 1, 7, 14... ou data: 2026-12-31)", font=("Segoe UI", 12), text_color=COR_TEXTO2).grid(row=3, column=1, sticky="e", pady=(5, 2))
        self.entry_vencimento = criar_entry(form, placeholder="Ex: 7 ou 2026-12-31", height=40)
        self.entry_vencimento.grid(row=4, column=0, padx=(0, 15), sticky="ew")

        botoes_frame = ctk.CTkFrame(form, fg_color="transparent")
        botoes_frame.grid(row=4, column=1, padx=(15, 0), sticky="ew")

        self.btn_cadastrar = ctk.CTkButton(
            botoes_frame, text="Confirmar Empréstimo", command=self._cadastrar_emprestimo,
            width=220, height=50, fg_color=COR_AZUL_PRINCIPAL, hover_color=COR_AZUL_HOVER,
            font=("Segoe UI", 16, "bold")
        )
        self.btn_cadastrar.pack(side="left", padx=(0, 12))

        self.btn_finalizar = ctk.CTkButton(
            botoes_frame, text="Finalizar Selecionado", command=self._finalizar_emprestimo,
            width=200, height=50, fg_color="transparent", border_color=COR_AZUL_CLARO, border_width=1,
            hover_color="#0F172A", text_color=COR_AZUL_CLARO, font=("Segoe UI", 16, "bold")
        )
        self.btn_finalizar.pack(side="left", padx=(0, 12))

        self.btn_detalhes = ctk.CTkButton(
            botoes_frame, text="Ver Detalhes", command=self._abrir_detalhes,
            width=180, height=50, fg_color="transparent", border_color=COR_AZUL_CLARO, border_width=1,
            hover_color="#0F172A", text_color=COR_AZUL_CLARO, font=("Segoe UI", 16, "bold")
        )
        self.btn_detalhes.pack(side="left")

        # Tabela
        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent", height=45)
        header_lista.pack(fill="x", padx=20, pady=(15, 5))
        header_lista.pack_propagate(False)

        colunas_ajustadas = [("ID", 0.06), ("Beneficiário", 0.22), ("Cód. Patrimônio", 0.16), ("Título do Livro", 0.22), ("Retirada", 0.12), ("Vencimento", 0.12), ("Status", 0.1)]
        x_header = 0
        for txt, pct in colunas_ajustadas:
            lbl_h = criar_label(header_lista, txt.upper(), font=("Segoe UI", 14, "bold"), text_color=COR_TEXTO, anchor="w")
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

        # --- ALUNO RESERVA COM FILTRO ---
        criar_label(form, "Selecione o Aluno", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.entry_busca_res_aluno = criar_entry(form, placeholder="Digite para buscar o aluno...", height=35)
        self.entry_busca_res_aluno.grid(row=1, column=0, padx=(0, 15), pady=(0, 5), sticky="ew")
        self.entry_busca_res_aluno.bind("<KeyRelease>", lambda e: self._filtrar_dados(self.entry_busca_res_aluno.get(), self.combo_reserva_aluno, self._reserva_alunos_map))

        self.combo_reserva_aluno = criar_combo(form, height=40)
        self.combo_reserva_aluno.grid(row=2, column=0, padx=(0, 15), pady=(0, 10), sticky="ew")

        # --- LIVRO RESERVA COM FILTRO ---
        criar_label(form, "Selecione a Obra / Livro", font=("Segoe UI", 14, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self.entry_busca_res_livro = criar_entry(form, placeholder="Digite para buscar a obra...", height=35)
        self.entry_busca_res_livro.grid(row=1, column=1, padx=(15, 0), pady=(0, 5), sticky="ew")
        self.entry_busca_res_livro.bind("<KeyRelease>", lambda e: self._filtrar_dados(self.entry_busca_res_livro.get(), self.combo_reserva_livro, self._reserva_livros_map))

        self.combo_reserva_livro = criar_combo(form, height=40)
        self.combo_reserva_livro.grid(row=2, column=1, padx=(15, 0), pady=(0, 10), sticky="ew")

        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        self.btn_reservar = ctk.CTkButton(
            botoes, text="Efetuar Nova Reserva", command=self._reservar,
            width=220, height=50, fg_color=COR_AZUL_PRINCIPAL, hover_color=COR_AZUL_HOVER,
            font=("Segoe UI", 16, "bold")
        )
        self.btn_reservar.pack(side="left", padx=(0, 12))

        self.btn_cancelar_reserva = ctk.CTkButton(
            botoes, text="Cancelar Selecionada", command=self._cancelar_reserva,
            width=220, height=50, fg_color="transparent", border_color=COR_AZUL_CLARO, border_width=1,
            hover_color="#0F172A", text_color=COR_AZUL_CLARO, font=("Segoe UI", 16, "bold")
        )
        self.btn_cancelar_reserva.pack(side="left")

        # Tabela
        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent", height=45)
        header_lista.pack(fill="x", padx=20, pady=(15, 5))
        header_lista.pack_propagate(False)

        colunas_res = [("ID", 0.06), ("Beneficiário", 0.25), ("Obra Reservada", 0.3), ("Data Solicitação", 0.14), ("Prazo Retirada", 0.15), ("Situação", 0.1)]
        x_header = 0
        for txt, pct in colunas_res:
            lbl_h = criar_label(header_lista, txt.upper(), font=("Segoe UI", 14, "bold"), text_color=COR_TEXTO, anchor="w")
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
            width=340, height=50, fg_color=COR_AZUL_PRINCIPAL, hover_color=COR_AZUL_HOVER,
            font=("Segoe UI", 16, "bold")
        )
        self.btn_pagar.pack(side="left")

        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        header_lista = ctk.CTkFrame(lista_card, fg_color="transparent", height=45)
        header_lista.pack(fill="x", padx=20, pady=(15, 5))
        header_lista.pack_propagate(False)

        colunas_mul = [("ID", 0.06), ("Valor (R$)", 0.1), ("Dias", 0.08), ("Motivo Ocorrência", 0.14), ("Situação", 0.1), ("Geração", 0.12), ("Estudante", 0.22), ("Obra Atrelada", 0.18)]
        x_header = 0
        for txt, pct in colunas_mul:
            lbl_h = criar_label(header_lista, txt.upper(), font=("Segoe UI", 14, "bold"), text_color=COR_TEXTO, anchor="w")
            lbl_h.place(relx=x_header + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            x_header += pct

        self.lista_multas = criar_scroll_frame(lista_card, fg_color="transparent")
        self.lista_multas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ==================== MÉTODOS ====================

    def _finalizar_emprestimo(self):
        if not self._selecionado:
            self._notificar("Selecione um registro na listagem abaixo.")
            return
        emp_id = self._selecionado[0]
        sucesso = finalizar_emprestimo(emp_id)
        if sucesso:
            self._notificar("Empréstimo finalizado / Devolvido com sucesso!")
            self._selecionado = None
            self._recarregar_emprestimos()
        else:
            self._notificar("Erro ao processar devolução.")

    def _abrir_detalhes(self):
        if not self._selecionado:
            self._notificar("Selecione um empréstimo para ver detalhes.")
            return
        DetalheEmprestimo(self, self._selecionado)

    def _recarregar_emprestimos(self, emprestimos_filtrados=None):
        for widget in self.lista_emprestimos.winfo_children():
            widget.destroy()
        self._itens_lista = []
        self._selecionado = None

        alunos = listar_alunos()
        self._alunos_map = {}
        nomes_alunos = [f"{a[0]} - {a[1]}" for a in alunos]
        for a in alunos:
            self._alunos_map[f"{a[0]} - {a[1]}"] = a[0]
        self.combo_aluno.configure(values=nomes_alunos if nomes_alunos else ["Selecione..."])
        if nomes_alunos:
            self.combo_aluno.set(nomes_alunos[0])

        exemplares = listar_exemplares_disponiveis()
        self._exemplares_map = {}
        nomes_exemplares = [f"{e[2]} ({e[1]})" if len(e) > 2 else str(e[0]) for e in exemplares]
        for e in exemplares:
            key = f"{e[2]} ({e[1]})" if len(e) > 2 else str(e[0])
            self._exemplares_map[key] = e[0]
        self.combo_exemplar.configure(values=nomes_exemplares if nomes_exemplares else ["Selecione..."])
        if nomes_exemplares:
            self.combo_exemplar.set(nomes_exemplares[0])

        emprestimos = emprestimos_filtrados if emprestimos_filtrados is not None else listar_emprestimos()
        for emp in map(list, list(emprestimos)):
            self._criar_item_emp(emp)

    def _criar_item_emp(self, emp):
        item = ctk.CTkFrame(self.lista_emprestimos, fg_color=self.cor_card, corner_radius=8, height=42)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)
        item.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))

        colunas_display = [0.06, 0.22, 0.16, 0.22, 0.12, 0.12, 0.1]
        indices_exibir = [0, 1, 2, 3, 4, 5, 7]
        
        x = 0
        for col_idx, db_idx in enumerate(indices_exibir):
            texto = emp[db_idx] if db_idx < len(emp) else ""
            pct = colunas_display[col_idx]
            cor = self.cor_texto
            
            if col_idx in [4, 5]:
                try:
                    if texto:
                        if hasattr(texto, 'strftime'):
                            texto = texto.strftime("%d/%m/%Y")
                        elif isinstance(texto, str) and "20" in str(texto):
                            partes = str(texto).split("-")
                            if len(partes) == 3:
                                texto = f"{partes[2]}/{partes[1]}/{partes[0]}"
                except:
                    pass
            
            if col_idx == 6:
                status_texto = str(texto).lower()
                if status_texto == "atrasado":
                    cor = "#EF4444" 
                elif status_texto == "ativo":
                    cor = COR_AZUL_CLARO
                elif status_texto == "finalizado":
                    cor = "#10B981"
                
            lbl = ctk.CTkLabel(item, text=str(texto) if texto else "-", font=("Segoe UI", 10), text_color=cor, anchor="w")
            lbl.place(relx=x + 0.01, rely=0.5, anchor="w", relwidth=pct - 0.02)
            lbl.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))
            x += pct

        self._itens_lista.append((item, emp))

    def _selecionar(self, emp):
        self._selecionado = emp
        for item, e in self._itens_lista:
            if e == emp:
                # Destaque de linha selecionada de alto contraste
                item.configure(fg_color="#0F172A")
                for widget in item.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color="#FFFFFF")
            else:
                item.configure(fg_color=self.cor_card)
                for idx, widget in enumerate(item.winfo_children()):
                    if isinstance(widget, ctk.CTkLabel):
                        if idx == 6: # Restaura cores originais dos status
                            st = str(e[7]).lower()
                            widget.configure(text_color="#EF4444" if st == "atrasado" else "#10B981" if st == "finalizado" else COR_AZUL_CLARO)
                        else:
                            widget.configure(text_color=self.cor_texto)
        self.lista_emprestimos.update_idletasks()

    def _filtrar_dados(self, termo, combo_alvo, mapa_referencia):
        """Filtra as opções mapeadas nos dicionários em tempo real com base no texto digitado."""
        termo = termo.lower().strip()
        opcoes_filtradas = [chave for chave in mapa_referencia.keys() if termo in chave.lower()]
        
        if opcoes_filtradas:
            combo_alvo.configure(values=opcoes_filtradas)
            combo_alvo.set(opcoes_filtradas[0])
        else:
            combo_alvo.configure(values=["Nenhum resultado encontrado"])
            combo_alvo.set("Nenhum resultado encontrado")

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
            self._notificar("Informe a data prevista de devolução (AAAA-MM-DD) ou número de dias (ex: 7).")
            return

        sucesso, data_convertida, erro = validar_e_converter_data(vencimento)
        if not sucesso:
            self._notificar(f"Erro na data: {erro}")
            return

        id_usuario = self._alunos_map[aluno_sel]
        id_exemplar = self._exemplares_map[exemplar_sel]
        id_funcionario = self.controller.usuario_logado['id'] if self.controller and hasattr(self.controller, 'usuario_logado') else 1

        if usuario_tem_multa_pendente(id_usuario):
            self._notificar("Aluno com multa pendente! Regularize primeiro.")
            return

        self.btn_cadastrar.configure(text="Processando...", state="disabled")
        self.after(500, lambda: self._salvar_emprestimo(id_usuario, id_exemplar, data_convertida, id_funcionario))

    def _salvar_emprestimo(self, id_usuario, id_exemplar, vencimento, id_funcionario):
        sucesso = cadastrar_emprestimo(id_usuario, id_exemplar, vencimento, id_funcionario)
        if sucesso:
            self._notificar("Empréstimo registrado com sucesso!")
            self.entry_vencimento.delete(0, "end")
            self.entry_busca_aluno.delete(0, "end")
            self.entry_busca_exemplar.delete(0, "end")
            self._recarregar_emprestimos()
        else:
            self._notificar("Erro operacional ao salvar empréstimo.")
        self.btn_cadastrar.configure(text="Confirmar Empréstimo", state="normal")

    def _recarregar_reservas(self):
        for widget in self.lista_reservas.winfo_children():
            widget.destroy()
        self._itens_reserva = []
        self._reserva_selecionada = None

        alunos = listar_alunos()
        self._reserva_alunos_map = {}
        nomes_alunos = [f"{a[0]} - {a[1]}" for a in alunos]
        for a in alunos:
            self._reserva_alunos_map[f"{a[0]} - {a[1]}"] = a[0]
        self.combo_reserva_aluno.configure(values=nomes_alunos if nomes_alunos else ["Selecione..."])
        if nomes_alunos:
            self.combo_reserva_aluno.set(nomes_alunos[0])

        livros = listar_livros()
        self._reserva_livros_map = {}
        nomes_livros = [f"{l[1]} ({l[2]})" for l in livros]
        for l in livros:
            self._reserva_livros_map[f"{l[1]} ({l[2]})"] = l[0]
        self.combo_reserva_livro.configure(values=nomes_livros if nomes_livros else ["Selecione..."])
        if nomes_livros:
            self.combo_reserva_livro.set(nomes_livros[0])

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
        self._reserva_selecionada = r
        for item, v in self._itens_reserva:
            if v == r:
                item.configure(fg_color="#0F172A")
                for widget in item.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color="#FFFFFF")
            else:
                item.configure(fg_color=self.cor_card)
                for widget in item.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color=self.cor_texto)

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
        if friendship := sucesso:
            self._notificar("Reserva ativada com sucesso!")
            self.entry_busca_res_aluno.delete(0, "end")
            self.entry_busca_res_livro.delete(0, "end")
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
        self._multa_selecionada = m
        for item, v in self._itens_multa:
            if v == m:
                item.configure(fg_color="#0F172A")
                for widget in item.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color="#FFFFFF")
            else:
                item.configure(fg_color=self.cor_card)
                for idx, widget in enumerate(item.winfo_children()):
                    if isinstance(widget, ctk.CTkLabel):
                        if idx == 1:
                            st = str(v[4]).lower()
                            widget.configure(text_color="#EF4444" if st == "pendente" else "#10B981")
                        else:
                            widget.configure(text_color=self.cor_texto)

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