# tela_relatorios.py — Tela completa de relatórios do sistema LUMEN

import os
import sys
import threading
from PIL import Image
from datetime import date, datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.report_queries import (
    buscar_usuario_por_nome_parcial,
    relatorio_inventario_acervo, relatorio_exemplares_disponiveis,
    relatorio_emprestimos_periodo, relatorio_emprestimos_atraso,
    relatorio_historico_usuario,
    relatorio_livros_mais_emprestados, relatorio_top_leitores,
    listar_categorias_para_filtro
)
from services.report_export import (
    gerar_pdf_generico, gerar_excel_generico, SCHOOL_NAME
)
from services.styles import (
    cores,
    criar_entry, criar_label, criar_titulo, criar_card, criar_combo,
    criar_scroll_frame
)



# Colunas para cada relatório
COLUNAS_INVENTARIO = ["Patrimônio", "ISBN", "Título", "Autores", "Editora", "Categoria", "Localização", "Situação"]
COLUNAS_DISPONIVEIS = ["Patrimônio", "ISBN", "Título", "Autores", "Categoria", "Localização"]
COLUNAS_EMPRESTIMOS = ["Patrimônio", "Livro", "Usuário", "Contato", "Empréstimo", "Previsto", "Devolução", "Status"]
COLUNAS_ATRASO = ["Nome", "Contato", "Patrimônio", "Livro", "Previsto", "Dias Atraso"]
COLUNAS_HISTORICO_USU = ["Patrimônio", "Livro", "Empréstimo", "Previsto", "Devolução"]
COLUNAS_MAIS_EMP = ["Ranking", "Livro", "Autores", "ISBN", "Empréstimos"]
COLUNAS_TOP_LEIT = ["Ranking", "Nome", "Contato", "Empréstimos"]


class TelaRelatorios(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=cores.COR_BG)
        self.controller = controller
        self._aba_atual = "inventario"
        self._alunos_map = {}
        self._construir_ui()



    def _reconstruir_tema(self):
        """Reconstrói a tela ao trocar o tema claro/escuro."""
        if not self.winfo_exists():
            return
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=cores.COR_BG)
        self._construir_ui()

    def _ao_visitar(self):
        if getattr(self, "_tema_pendente", False):
            self._reconstruir_tema()

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color=cores.COR_CARD)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 8))

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y", padx=10, pady=5)

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(55, 55))
                ctk.CTkLabel(header_left, image=img_logo, text="").pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))

        criar_label(header_left, "Relatórios da Biblioteca",
                    font=("Segoe UI", 24, "bold"), text_color=cores.COR_TEXTO).pack(side="left")

        ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=100, height=36,
            fg_color=cores.COR_SIDEBAR, text_color="#FFFFFF", border_color=cores.COR_INPUT_BORDER, border_width=1,
            hover_color=cores.COR_INPUT_BG, font=("Segoe UI", 14, "bold")
        ).pack(side="right", padx=15, pady=5)

        # Abas (scroll horizontal)
        abas_container = ctk.CTkFrame(self, fg_color="transparent")
        abas_container.grid(row=1, column=0, sticky="ew", padx=30, pady=(5, 5))

        self._botoes_abas = []
        abas = [
            ("Inventário", "inventario"),
            ("Disponíveis", "disponiveis"),
            ("Empréstimos", "emprestimos"),
            ("Atrasos", "atrasos"),
            ("Hist. Usuário", "historico_usu"),
            ("Mais Emprestados", "mais_emp"),
            ("Top Leitores", "top_leit"),
        ]

        for nome, tag in abas:
            is_atual = (tag == self._aba_atual)
            btn = ctk.CTkButton(
                abas_container, text=nome, font=("Segoe UI", 11, "bold"),
                fg_color=cores.COR_AZUL_PRINCIPAL if is_atual else cores.COR_INPUT_BG,
                text_color="#FFFFFF" if is_atual else cores.COR_TEXTO2,
                border_color=cores.COR_AZUL_PRINCIPAL if is_atual else cores.COR_INPUT_BORDER,
                border_width=1 if is_atual else 0,
                hover_color=cores.COR_AZUL_HOVER,
                width=110, height=30,
                command=lambda n=tag: self._mostrar_aba(n)
            )
            btn.pack(side="left", padx=(0, 3))
            self._botoes_abas.append((btn, tag))

        # Container principal
        self._frame_conteudo = ctk.CTkFrame(self, fg_color=cores.COR_BG)
        self._frame_conteudo.grid(row=2, column=0, sticky="nsew", padx=30, pady=(5, 20))
        self._frame_conteudo.grid_columnconfigure(0, weight=1)
        self._frame_conteudo.grid_rowconfigure(0, weight=1)

        # Frames para cada relatório
        self._frames = {}
        for tag in [t[1] for t in abas]:
            frame = ctk.CTkFrame(self._frame_conteudo, fg_color=cores.COR_BG)
            self._frames[tag] = frame

        self._construir_aba_inventario()
        self._construir_aba_disponiveis()
        self._construir_aba_emprestimos()
        self._construir_aba_atrasos()
        self._construir_aba_historico_usuario()
        self._construir_aba_mais_emprestados()
        self._construir_aba_top_leitores()

        self.lbl_notificacao = criar_label(self, "", text_color=cores.COR_TEXTO2)

        # Mostra a primeira aba
        self._mostrar_aba("inventario")

    def _mostrar_aba(self, nome):
        self._aba_atual = nome
        for btn, n in self._botoes_abas:
            if n == nome:
                btn.configure(fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
                              border_color=cores.COR_AZUL_PRINCIPAL, border_width=1)
            else:
                btn.configure(fg_color=cores.COR_INPUT_BG, text_color=cores.COR_TEXTO2,
                              border_color=cores.COR_INPUT_BORDER, border_width=0)

        for tag, frame in self._frames.items():
            frame.grid_forget()

        if nome in self._frames:
            self._frames[nome].grid(row=0, column=0, sticky="nsew")

    # ═══════════════════════════════════════════════════════════════════════
    # 1. INVENTÁRIO DO ACERVO
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_inventario(self):
        frame = self._frames["inventario"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Filtros
        filtro_card = criar_card(frame)
        filtro_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        filtro = ctk.CTkFrame(filtro_card, fg_color="transparent")
        filtro.pack(fill="x", padx=15, pady=10)

        # Categoria
        criar_label(filtro, "Categoria:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=(0, 5))
        categorias = ["Todos"] + listar_categorias_para_filtro()
        self.combo_inv_categoria = criar_combo(filtro, values=categorias, width=150, height=30)
        self.combo_inv_categoria.grid(row=0, column=1, padx=(0, 10))
        self.combo_inv_categoria.set("Todos")

        # Situação
        criar_label(filtro, "Situação:", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, padx=(0, 5))
        self.combo_inv_situacao = criar_combo(filtro, values=["Todos", "disponivel", "emprestado", "manutencao"], width=120, height=30)
        self.combo_inv_situacao.grid(row=0, column=3, padx=(0, 10))
        self.combo_inv_situacao.set("Todos")

        # Botões
        self.btn_inv_pesquisar = ctk.CTkButton(filtro, text="Pesquisar", command=lambda: self._pesquisar_inventario(),
                                                width=90, height=30, fg_color=cores.COR_AZUL_PRINCIPAL, font=("Segoe UI", 11, "bold"))
        self.btn_inv_pesquisar.grid(row=0, column=4, padx=3)

        ctk.CTkButton(filtro, text="Limpar", command=lambda: self._limpar_inventario(),
                       width=70, height=30, fg_color=cores.COR_CARD, font=("Segoe UI", 11)).grid(row=0, column=5, padx=3)

        self.btn_inv_pdf = ctk.CTkButton(filtro, text="PDF", command=lambda: self._exportar_inventario_pdf(),
                                          width=50, height=30, fg_color=cores.COR_PERIGO, font=("Segoe UI", 11, "bold"))
        self.btn_inv_pdf.grid(row=0, column=6, padx=3)

        self.btn_inv_excel = ctk.CTkButton(filtro, text="Excel", command=lambda: self._exportar_inventario_excel(),
                                            width=50, height=30, fg_color=cores.COR_SUCESSO, font=("Segoe UI", 11, "bold"))
        self.btn_inv_excel.grid(row=0, column=7, padx=3)

        # Tabela
        self.lista_inv = criar_scroll_frame(frame, fg_color=cores.COR_CARD)
        self.lista_inv.grid(row=1, column=0, sticky="nsew")

        # Carrega dados iniciais
        self._pesquisar_inventario()

    def _pesquisar_inventario(self):
        filtros = {}
        cat = self.combo_inv_categoria.get()
        if cat and cat != "Todos":
            filtros['categoria'] = cat
        sit = self.combo_inv_situacao.get()
        if sit and sit != "Todos":
            filtros['situacao'] = sit

        dados = relatorio_inventario_acervo(filtros if filtros else None)
        self._preencher_tabela(self.lista_inv, COLUNAS_INVENTARIO, dados)

    def _limpar_inventario(self):
        self.combo_inv_categoria.set("Todos")
        self.combo_inv_situacao.set("Todos")
        self._pesquisar_inventario()

    def _exportar_inventario_pdf(self):
        dados = relatorio_inventario_acervo()
        caminho = self._caminho_saida("inventario_acervo.pdf")
        larguras = [31, 31, 50, 44, 31, 31, 31, 24]
        gerar_pdf_generico("Inventario do Acervo", COLUNAS_INVENTARIO, larguras, dados, caminho,
                          descricao='Relatorio completo do acervo bibliografico da instituicao.',
                          observacao='Os dados apresentados refletem o estado atual do acervo no momento da geracao deste relatorio.')
        self._abrir_arquivo(caminho)

    def _exportar_inventario_excel(self):
        dados = relatorio_inventario_acervo()
        caminho = self._caminho_saida("inventario_acervo.xlsx")
        gerar_excel_generico("Inventário do Acervo", COLUNAS_INVENTARIO, dados, caminho)
        self._abrir_arquivo(caminho)

    # ═══════════════════════════════════════════════════════════════════════
    # 2. EXEMPLARES DISPONÍVEIS
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_disponiveis(self):
        frame = self._frames["disponiveis"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        filtro_card = criar_card(frame)
        filtro_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        filtro = ctk.CTkFrame(filtro_card, fg_color="transparent")
        filtro.pack(fill="x", padx=15, pady=10)

        criar_label(filtro, "Buscar:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=(0, 5))
        self.entry_disp_busca = criar_entry(filtro, placeholder="Digite o título...", width=300, height=30)
        self.entry_disp_busca.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.entry_disp_busca.bind("<KeyRelease>", lambda e: self._filtrar_disponiveis())

        ctk.CTkButton(filtro, text="Limpar", command=lambda: self._limpar_disponiveis(),
                       width=70, height=30, fg_color=cores.COR_CARD, font=("Segoe UI", 11)).grid(row=0, column=2, padx=3)
        ctk.CTkButton(filtro, text="PDF", command=lambda: self._exportar_disponiveis_pdf(),
                       width=50, height=30, fg_color=cores.COR_PERIGO, font=("Segoe UI", 11, "bold")).grid(row=0, column=3, padx=3)
        ctk.CTkButton(filtro, text="Excel", command=lambda: self._exportar_disponiveis_excel(),
                       width=50, height=30, fg_color=cores.COR_SUCESSO, font=("Segoe UI", 11, "bold")).grid(row=0, column=4, padx=3)

        self.lista_disp = criar_scroll_frame(frame, fg_color=cores.COR_CARD)
        self.lista_disp.grid(row=1, column=0, sticky="nsew")
        self._todos_disp = relatorio_exemplares_disponiveis()
        self._preencher_tabela(self.lista_disp, COLUNAS_DISPONIVEIS, self._todos_disp)

    def _filtrar_disponiveis(self):
        termo = self.entry_disp_busca.get().strip().lower()
        if not termo:
            dados = self._todos_disp
        else:
            dados = [d for d in self._todos_disp if termo in str(d[2] or "").lower()]
        self._preencher_tabela(self.lista_disp, COLUNAS_DISPONIVEIS, dados)

    def _limpar_disponiveis(self):
        self.entry_disp_busca.delete(0, "end")
        self._preencher_tabela(self.lista_disp, COLUNAS_DISPONIVEIS, self._todos_disp)

    def _exportar_disponiveis_pdf(self):
        dados = relatorio_exemplares_disponiveis()
        caminho = self._caminho_saida("exemplares_disponiveis.pdf")
        larguras = [35, 35, 63, 56, 43, 41]
        gerar_pdf_generico("Exemplares Disponiveis", COLUNAS_DISPONIVEIS, larguras, dados, caminho,
                          descricao='Exemplares disponiveis para emprestimo no acervo.',
                          observacao='Os exemplares apresentados encontram-se disponiveis no momento da geracao deste relatorio.')
        self._abrir_arquivo(caminho)

    def _exportar_disponiveis_excel(self):
        dados = relatorio_exemplares_disponiveis()
        caminho = self._caminho_saida("exemplares_disponiveis.xlsx")
        gerar_excel_generico("Exemplares Disponíveis", COLUNAS_DISPONIVEIS, dados, caminho)
        self._abrir_arquivo(caminho)

    # ═══════════════════════════════════════════════════════════════════════
    # 3. EMPRÉSTIMOS POR PERÍODO
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_emprestimos(self):
        frame = self._frames["emprestimos"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        # Filtros
        filtro_card = criar_card(frame)
        filtro_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        filtro = ctk.CTkFrame(filtro_card, fg_color="transparent")
        filtro.pack(fill="x", padx=15, pady=10)

        criar_label(filtro, "Data Início:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=(0, 5))
        self.entry_emp_data_inicio = criar_entry(filtro, placeholder="DD/MM/AAAA", width=120, height=30)
        self.entry_emp_data_inicio.grid(row=0, column=1, padx=(0, 10))
        self.entry_emp_data_inicio.bind("<KeyRelease>", lambda e: self._formatar_data_ddmmaaaa(self.entry_emp_data_inicio))

        criar_label(filtro, "Data Fim:", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, padx=(0, 5))
        self.entry_emp_data_fim = criar_entry(filtro, placeholder="DD/MM/AAAA", width=120, height=30)
        self.entry_emp_data_fim.grid(row=0, column=3, padx=(0, 10))
        self.entry_emp_data_fim.bind("<KeyRelease>", lambda e: self._formatar_data_ddmmaaaa(self.entry_emp_data_fim))

        ctk.CTkButton(filtro, text="Pesquisar", command=lambda: self._pesquisar_emprestimos(),
                       width=90, height=30, fg_color=cores.COR_AZUL_PRINCIPAL, font=("Segoe UI", 11, "bold")).grid(row=0, column=4, padx=3)
        ctk.CTkButton(filtro, text="Limpar", command=lambda: self._limpar_emprestimos(),
                       width=70, height=30, fg_color=cores.COR_CARD, font=("Segoe UI", 11)).grid(row=0, column=5, padx=3)
        ctk.CTkButton(filtro, text="PDF", command=lambda: self._exportar_emprestimos_pdf(),
                       width=50, height=30, fg_color=cores.COR_PERIGO, font=("Segoe UI", 11, "bold")).grid(row=0, column=6, padx=3)
        ctk.CTkButton(filtro, text="Excel", command=lambda: self._exportar_emprestimos_excel(),
                       width=50, height=30, fg_color=cores.COR_SUCESSO, font=("Segoe UI", 11, "bold")).grid(row=0, column=7, padx=3)

        self.lbl_emp_resumo = criar_label(frame, "", font=("Segoe UI", 11, "bold"), text_color=cores.COR_TEXTO)
        self.lbl_emp_resumo.grid(row=0, column=0, sticky="se", padx=15, pady=5)

        # Campo de busca por usuário
        busca_card = criar_card(frame)
        busca_card.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        busca_frame = ctk.CTkFrame(busca_card, fg_color="transparent")
        busca_frame.pack(fill="x", padx=15, pady=8)

        criar_label(busca_frame, "Buscar usuário:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 5))
        self.entry_emp_busca_usuario = criar_entry(busca_frame, placeholder="Digite o nome", width=250, height=30)
        self.entry_emp_busca_usuario.pack(side="left", padx=(0, 10))
        self.entry_emp_busca_usuario.bind("<KeyRelease>", lambda e: self._filtrar_emprestimos_usuario())

        self.lista_emp = criar_scroll_frame(frame, fg_color=cores.COR_CARD)
        self.lista_emp.grid(row=2, column=0, sticky="nsew")
        self._todos_emp = []
        self._pesquisar_emprestimos()

    def _formatar_data_ddmmaaaa(self, entry):
        """Formata automaticamente a data para DD/MM/AAAA."""
        texto = entry.get().replace("/", "")
        if len(texto) > 8:
            texto = texto[:8]
        if len(texto) >= 2 and len(texto) < 3:
            texto = texto[:2] + "/"
        elif len(texto) >= 5 and len(texto) < 6:
            texto = texto[:2] + "/" + texto[2:5] + "/"
        elif len(texto) >= 8:
            texto = texto[:2] + "/" + texto[2:4] + "/" + texto[4:8]
        entry.delete(0, "end")
        entry.insert(0, texto)

    def _converter_data_ddmmaaaa_para_aaaa_mm_dd(self, data_ddmmaaaa):
        """Converte DD/MM/AAAA para AAAA-MM-DD."""
        partes = data_ddmmaaaa.split("/")
        if len(partes) == 3 and len(partes[0]) == 2 and len(partes[1]) == 2 and len(partes[2]) == 4:
            return f"{partes[2]}-{partes[1]}-{partes[0]}"
        return None

    def _pesquisar_emprestimos(self):
        inicio_str = self.entry_emp_data_inicio.get().strip()
        fim_str = self.entry_emp_data_fim.get().strip()
        inicio = self._converter_data_ddmmaaaa_para_aaaa_mm_dd(inicio_str) if inicio_str else None
        fim = self._converter_data_ddmmaaaa_para_aaaa_mm_dd(fim_str) if fim_str else None
        self._todos_emp, resumo = relatorio_emprestimos_periodo(inicio, fim)
        self._preencher_tabela(self.lista_emp, COLUNAS_EMPRESTIMOS, self._todos_emp)
        self.lbl_emp_resumo.configure(text=f"Total: {resumo['total']} | Devolvidos: {resumo['devolvidos']} | Abertos: {resumo['abertos']}")

    def _filtrar_emprestimos_usuario(self):
        termo = self.entry_emp_busca_usuario.get().strip().lower()
        if not termo:
            dados = self._todos_emp
        else:
            dados = [d for d in self._todos_emp if termo in str(d[2] or "").lower()]
        self._preencher_tabela(self.lista_emp, COLUNAS_EMPRESTIMOS, dados)

    def _limpar_emprestimos(self):
        self.entry_emp_data_inicio.delete(0, "end")
        self.entry_emp_data_fim.delete(0, "end")
        self.entry_emp_busca_usuario.delete(0, "end")
        self._pesquisar_emprestimos()

    def _exportar_emprestimos_pdf(self):
        dados, resumo = relatorio_emprestimos_periodo(
            self.entry_emp_data_inicio.get().strip() or None,
            self.entry_emp_data_fim.get().strip() or None
        )
        caminho = self._caminho_saida("emprestimos_periodo.pdf")
        larguras = [31, 48, 35, 41, 31, 31, 31, 25]
        gerar_pdf_generico("Emprestimos por Periodo", COLUNAS_EMPRESTIMOS, larguras, dados, caminho,
                          resumo=resumo,
                          descricao='Movimentacao de emprestimos no periodo informado.',
                          observacao='Os emprestimos foram registrados no sistema no periodo indicado neste relatorio.')
        self._abrir_arquivo(caminho)

    def _exportar_emprestimos_excel(self):
        dados, resumo = relatorio_emprestimos_periodo(
            self.entry_emp_data_inicio.get().strip() or None,
            self.entry_emp_data_fim.get().strip() or None
        )
        caminho = self._caminho_saida("emprestimos_periodo.xlsx")
        gerar_excel_generico("Empréstimos por Período", COLUNAS_EMPRESTIMOS, dados, caminho, resumo)
        self._abrir_arquivo(caminho)

    # ═══════════════════════════════════════════════════════════════════════
    # 4. EMPRÉSTIMOS EM ATRASO
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_atrasos(self):
        frame = self._frames["atrasos"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        filtro_card = criar_card(frame)
        filtro_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        filtro = ctk.CTkFrame(filtro_card, fg_color="transparent")
        filtro.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(filtro, text="Pesquisar", command=lambda: self._pesquisar_atrasos(),
                       width=90, height=30, fg_color=cores.COR_AZUL_PRINCIPAL, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=3)
        ctk.CTkButton(filtro, text="PDF", command=lambda: self._exportar_atrasos_pdf(),
                       width=50, height=30, fg_color=cores.COR_PERIGO, font=("Segoe UI", 11, "bold")).grid(row=0, column=1, padx=3)
        ctk.CTkButton(filtro, text="Excel", command=lambda: self._exportar_atrasos_excel(),
                       width=50, height=30, fg_color=cores.COR_SUCESSO, font=("Segoe UI", 11, "bold")).grid(row=0, column=2, padx=3)

        self.lista_atrasos = criar_scroll_frame(frame, fg_color=cores.COR_CARD)
        self.lista_atrasos.grid(row=1, column=0, sticky="nsew")
        self._pesquisar_atrasos()

    def _pesquisar_atrasos(self):
        dados = relatorio_emprestimos_atraso()
        self._preencher_tabela(self.lista_atrasos, COLUNAS_ATRASO, dados)

    def _exportar_atrasos_pdf(self):
        dados = relatorio_emprestimos_atraso()
        caminho = self._caminho_saida("emprestimos_atraso.pdf")
        larguras = [50, 59, 37, 59, 37, 31]
        gerar_pdf_generico("Emprestimos em Atraso", COLUNAS_ATRASO, larguras, dados, caminho,
                          descricao='Emprestimos com devolucao em atraso.',
                          observacao='Atrasos superiores a 30 dias estao destacados em vermelho. Multas sao geradas automaticamente.')
        self._abrir_arquivo(caminho)

    def _exportar_atrasos_excel(self):
        dados = relatorio_emprestimos_atraso()
        caminho = self._caminho_saida("emprestimos_atraso.xlsx")
        gerar_excel_generico("Empréstimos em Atraso", COLUNAS_ATRASO, dados, caminho)
        self._abrir_arquivo(caminho)

    # ═══════════════════════════════════════════════════════════════════════
    # 5. HISTÓRICO POR USUÁRIO
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_historico_usuario(self):
        frame = self._frames["historico_usu"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        filtro_card = criar_card(frame)
        filtro_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        filtro = ctk.CTkFrame(filtro_card, fg_color="transparent")
        filtro.pack(fill="x", padx=15, pady=10)

        criar_label(filtro, "Usuário:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=(0, 5))
        self.entry_hist_usu_nome = criar_entry(filtro, placeholder="Digite o nome...", width=200, height=30)
        self.entry_hist_usu_nome.grid(row=0, column=1, padx=(0, 5))
        self.entry_hist_usu_nome.bind("<KeyRelease>", self._autocomplete_usuario)

        self.lbl_hist_usu_selecionado = criar_label(filtro, "", font=("Segoe UI", 10), text_color=cores.COR_SUCESSO)
        self.lbl_hist_usu_selecionado.grid(row=0, column=2, padx=(0, 10))

        ctk.CTkButton(filtro, text="Pesquisar", command=lambda: self._pesquisar_historico_usuario(),
                       width=90, height=30, fg_color=cores.COR_AZUL_PRINCIPAL, font=("Segoe UI", 11, "bold")).grid(row=0, column=3, padx=3)
        ctk.CTkButton(filtro, text="PDF", command=lambda: self._exportar_hist_usu_pdf(),
                       width=50, height=30, fg_color=cores.COR_PERIGO, font=("Segoe UI", 11, "bold")).grid(row=0, column=4, padx=3)
        ctk.CTkButton(filtro, text="Excel", command=lambda: self._exportar_hist_usu_excel(),
                       width=50, height=30, fg_color=cores.COR_SUCESSO, font=("Segoe UI", 11, "bold")).grid(row=0, column=5, padx=3)

        self.lbl_hist_usu_resumo = criar_label(frame, "", font=("Segoe UI", 11, "bold"), text_color=cores.COR_TEXTO)
        self.lbl_hist_usu_resumo.grid(row=0, column=0, sticky="se", padx=15, pady=5)

        self.lista_hist_usu = criar_scroll_frame(frame, fg_color=cores.COR_CARD)
        self.lista_hist_usu.grid(row=1, column=0, sticky="nsew")

    def _autocomplete_usuario(self, event=None):
        termo = self.entry_hist_usu_nome.get().strip()
        if len(termo) < 2:
            return
        usuarios = buscar_usuario_por_nome_parcial(termo)
        if usuarios:
            self._alunos_map = {u[1]: u[0] for u in usuarios}
            nomes = [u[1] for u in usuarios]
            self.entry_hist_usu_nome.delete(0, "end")
            self.entry_hist_usu_nome.insert(0, nomes[0])
            self.lbl_hist_usu_selecionado.configure(text=f"ID: {usuarios[0][0]}")

    def _pesquisar_historico_usuario(self):
        nome = self.entry_hist_usu_nome.get().strip()
        if not nome or nome not in self._alunos_map:
            self._notificar("Selecione um usuário válido.")
            return
        id_usuario = self._alunos_map[nome]
        dados, resumo = relatorio_historico_usuario(id_usuario)
        self._preencher_tabela(self.lista_hist_usu, COLUNAS_HISTORICO_USU, dados)
        self.lbl_hist_usu_resumo.configure(
            text=f"Total: {resumo['total']} registros"
        )

    def _exportar_hist_usu_pdf(self):
        nome = self.entry_hist_usu_nome.get().strip()
        if not nome or nome not in self._alunos_map:
            self._notificar("Selecione um usuário.")
            return
        dados, resumo = relatorio_historico_usuario(self._alunos_map[nome])
        caminho = self._caminho_saida(f"historico_{nome.replace(' ', '_')}.pdf")
        larguras = [47, 82, 48, 48, 48]
        gerar_pdf_generico(f"Historico de Emprestimos - {nome}", COLUNAS_HISTORICO_USU, larguras, dados, caminho,
                          descricao=f'Historico completo de emprestimos do usuario {nome}.',
                          observacao='Relatorio gerado a partir dos registros de emprestimos vinculados ao usuario.')
        self._abrir_arquivo(caminho)

    def _exportar_hist_usu_excel(self):
        nome = self.entry_hist_usu_nome.get().strip()
        if not nome or nome not in self._alunos_map:
            self._notificar("Selecione um usuário.")
            return
        dados, resumo = relatorio_historico_usuario(self._alunos_map[nome])
        caminho = self._caminho_saida(f"historico_{nome.replace(' ', '_')}.xlsx")
        gerar_excel_generico(f"Histórico de Empréstimos - {nome}", COLUNAS_HISTORICO_USU, dados, caminho, resumo)
        self._abrir_arquivo(caminho)

    # ═══════════════════════════════════════════════════════════════════════
    # 6. LIVROS MAIS EMPRESTADOS
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_mais_emprestados(self):
        frame = self._frames["mais_emp"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        filtro_card = criar_card(frame)
        filtro_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        filtro = ctk.CTkFrame(filtro_card, fg_color="transparent")
        filtro.pack(fill="x", padx=15, pady=10)

        criar_label(filtro, "Buscar:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=(0, 5))
        self.entry_me_busca = criar_entry(filtro, placeholder="Digite o título", width=300, height=30)
        self.entry_me_busca.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.entry_me_busca.bind("<KeyRelease>", lambda e: self._filtrar_mais_emp())

        ctk.CTkButton(filtro, text="Limpar", command=lambda: self._limpar_mais_emp(),
                       width=70, height=30, fg_color=cores.COR_CARD, font=("Segoe UI", 11)).grid(row=0, column=2, padx=3)
        ctk.CTkButton(filtro, text="PDF", command=lambda: self._exportar_mais_emp_pdf(),
                       width=50, height=30, fg_color=cores.COR_PERIGO, font=("Segoe UI", 11, "bold")).grid(row=0, column=3, padx=3)
        ctk.CTkButton(filtro, text="Excel", command=lambda: self._exportar_mais_emp_excel(),
                       width=50, height=30, fg_color=cores.COR_SUCESSO, font=("Segoe UI", 11, "bold")).grid(row=0, column=4, padx=3)

        self.lista_mais_emp = criar_scroll_frame(frame, fg_color=cores.COR_CARD)
        self.lista_mais_emp.grid(row=1, column=0, sticky="nsew")
        self._todos_mais_emp = []
        self._pesquisar_mais_emprestados()

    def _pesquisar_mais_emprestados(self):
        dados = relatorio_livros_mais_emprestados()
        self._todos_mais_emp = [(i + 1,) + d for i, d in enumerate(dados)]
        self._preencher_tabela(self.lista_mais_emp, COLUNAS_MAIS_EMP, self._todos_mais_emp)

    def _filtrar_mais_emp(self):
        termo = self.entry_me_busca.get().strip().lower()
        if not termo:
            dados = self._todos_mais_emp
        else:
            dados = [d for d in self._todos_mais_emp if termo in str(d[1] or "").lower()]
        self._preencher_tabela(self.lista_mais_emp, COLUNAS_MAIS_EMP, dados)

    def _limpar_mais_emp(self):
        self.entry_me_busca.delete(0, "end")
        self._preencher_tabela(self.lista_mais_emp, COLUNAS_MAIS_EMP, self._todos_mais_emp)

    def _exportar_mais_emp_pdf(self):
        dados = relatorio_livros_mais_emprestados()
        dados_com_ranking = [(i + 1,) + d for i, d in enumerate(dados)]
        caminho = self._caminho_saida("livros_mais_emprestados.pdf")
        larguras = [26, 89, 70, 44, 44]
        gerar_pdf_generico("Livros Mais Emprestados", COLUNAS_MAIS_EMP, larguras, dados_com_ranking, caminho,
                          descricao='Ranking dos livros mais emprestados no acervo.',
                          observacao='O ranking e baseado na quantidade de emprestimos registrados no sistema.')
        self._abrir_arquivo(caminho)

    def _exportar_mais_emp_excel(self):
        dados = relatorio_livros_mais_emprestados()
        dados_com_ranking = [(i + 1,) + d for i, d in enumerate(dados)]
        caminho = self._caminho_saida("livros_mais_emprestados.xlsx")
        gerar_excel_generico("Livros Mais Emprestados", COLUNAS_MAIS_EMP, dados_com_ranking, caminho)
        self._abrir_arquivo(caminho)

    # ═══════════════════════════════════════════════════════════════════════
    # 8. TOP 10 LEITORES
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_top_leitores(self):
        frame = self._frames["top_leit"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        filtro_card = criar_card(frame)
        filtro_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        filtro = ctk.CTkFrame(filtro_card, fg_color="transparent")
        filtro.pack(fill="x", padx=15, pady=10)

        criar_label(filtro, "Buscar:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=(0, 5))
        self.entry_tl_busca = criar_entry(filtro, placeholder="Digite o nome", width=300, height=30)
        self.entry_tl_busca.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.entry_tl_busca.bind("<KeyRelease>", lambda e: self._filtrar_top_leitores())

        ctk.CTkButton(filtro, text="Limpar", command=lambda: self._limpar_top_leitores(),
                       width=70, height=30, fg_color=cores.COR_CARD, font=("Segoe UI", 11)).grid(row=0, column=2, padx=3)
        ctk.CTkButton(filtro, text="PDF", command=lambda: self._exportar_top_leit_pdf(),
                       width=50, height=30, fg_color=cores.COR_PERIGO, font=("Segoe UI", 11, "bold")).grid(row=0, column=3, padx=3)
        ctk.CTkButton(filtro, text="Excel", command=lambda: self._exportar_top_leit_excel(),
                       width=50, height=30, fg_color=cores.COR_SUCESSO, font=("Segoe UI", 11, "bold")).grid(row=0, column=4, padx=3)

        self.lista_top_leit = criar_scroll_frame(frame, fg_color=cores.COR_CARD)
        self.lista_top_leit.grid(row=1, column=0, sticky="nsew")
        self._todos_top_leit = []
        self._pesquisar_top_leitores()

    def _pesquisar_top_leitores(self):
        dados = relatorio_top_leitores()
        self._todos_top_leit = [(i + 1,) + d for i, d in enumerate(dados)]
        self._preencher_tabela(self.lista_top_leit, COLUNAS_TOP_LEIT, self._todos_top_leit)

    def _filtrar_top_leitores(self):
        termo = self.entry_tl_busca.get().strip().lower()
        if not termo:
            dados = self._todos_top_leit
        else:
            dados = [d for d in self._todos_top_leit if termo in str(d[1] or "").lower()]
        self._preencher_tabela(self.lista_top_leit, COLUNAS_TOP_LEIT, dados)

    def _limpar_top_leitores(self):
        self.entry_tl_busca.delete(0, "end")
        self._preencher_tabela(self.lista_top_leit, COLUNAS_TOP_LEIT, self._todos_top_leit)

    def _exportar_top_leit_pdf(self):
        dados = relatorio_top_leitores()
        dados_com_ranking = [(i + 1,) + d for i, d in enumerate(dados)]
        caminho = self._caminho_saida("top_leitores.pdf")
        larguras = [35, 94, 82, 62]
        cards = [{'icone': '[*]', 'valor': len(dados), 'label': 'LEITORES'}]
        gerar_pdf_generico("Top 10 Leitores", COLUNAS_TOP_LEIT, larguras, dados_com_ranking, caminho,
                          descricao='Ranking dos leitores que mais utilizaram a biblioteca.',
                          cards_resumo=cards,
                          observacao='O ranking é baseado na quantidade de empréstimos realizados por cada usuário.')
        self._abrir_arquivo(caminho)

    def _exportar_top_leit_excel(self):
        dados = relatorio_top_leitores()
        dados_com_ranking = [(i + 1,) + d for i, d in enumerate(dados)]
        caminho = self._caminho_saida("top_leitores.xlsx")
        gerar_excel_generico("Top 10 Leitores", COLUNAS_TOP_LEIT, dados_com_ranking, caminho)
        self._abrir_arquivo(caminho)

    # ═══════════════════════════════════════════════════════════════════════
    # FUNÇÕES UTILITÁRIAS
    # ═══════════════════════════════════════════════════════════════════════

    def _preencher_tabela(self, frame, colunas, dados):
        """Preenche um frame scrollável com dados em formato tabela."""
        for w in frame.winfo_children():
            w.destroy()

        if not dados:
            ctk.CTkLabel(frame, text="Nenhum registro encontrado.",
                         font=("Segoe UI", 14), text_color=cores.COR_TEXTO2).pack(pady=30)
            return

        num_colunas = len(colunas)
        pesos = self._calcular_pesos(colunas, dados)

        # Container principal da tabela
        tabela = ctk.CTkFrame(frame, fg_color="transparent")
        tabela.pack(fill="x", expand=True, padx=10, pady=5)

        # Configura colunas UMA ÚNICA VEZ no container principal
        for i, peso in enumerate(pesos):
            tabela.grid_columnconfigure(i, weight=peso, minsize=60)

        # ── Cabeçalho (cada coluna é um widget separado no grid da tabela) ──
        for i, col in enumerate(colunas):
            cell = ctk.CTkFrame(tabela, fg_color=cores.COR_ATIVO, corner_radius=4)
            cell.grid(row=0, column=i, sticky="ew", padx=1, pady=(0, 2))
            ctk.CTkLabel(cell, text=col.upper(), font=("Segoe UI", 12, "bold"),
                         text_color="#FFFFFF", anchor="center").pack(
                fill="x", padx=2, pady=6)

        # ── Dados (cada célula é um widget separado no grid da tabela) ──
        for r, linha in enumerate(dados):
            cor_fundo = cores.COR_LINHA_PAR if r % 2 == 0 else cores.COR_LINHA_IMPAR
            for c, val in enumerate(linha):
                texto = str(val) if val else "-"
                if len(texto) > 35:
                    texto = texto[:32] + "…"

                cell = ctk.CTkFrame(tabela, fg_color=cor_fundo, corner_radius=3)
                cell.grid(row=r + 1, column=c, sticky="ew", padx=1, pady=1)
                ctk.CTkLabel(cell, text=texto, font=("Segoe UI", 12),
                             text_color=cores.COR_TEXTO, anchor="center").pack(
                    fill="x", padx=3, pady=4)

        # Total
        ctk.CTkLabel(frame, text=f"Total: {len(dados)} registros",
                     font=("Segoe UI", 12, "bold"), text_color=cores.COR_TEXTO).pack(pady=8)

    def _calcular_pesos(self, colunas, dados):
        """Calcula pesos para cada coluna baseado no conteúdo."""
        pesos = []
        for i, col in enumerate(colunas):
            max_len = len(col)
            for linha in dados[:20]:
                if i < len(linha):
                    valor = str(linha[i]) if linha[i] else ""
                    max_len = max(max_len, len(valor))
            # Peso maior para colunas de texto longo
            peso = max(1, min(max_len // 6, 5))
            # Reduz peso para colunas de título/livro
            col_lower = col.lower()
            if "título" in col_lower or "titulo" in col_lower or "livro" in col_lower:
                peso = max(1, peso - 1)
            pesos.append(peso)
        return pesos

    def _caminho_saida(self, nome_arquivo):
        """Gera caminho completo para o arquivo de saída."""
        pasta = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "relatorios")
        os.makedirs(pasta, exist_ok=True)
        return os.path.join(pasta, nome_arquivo)

    def _abrir_arquivo(self, caminho):
        """Abre arquivo com o visualizador padrão."""
        try:
            import subprocess
            import platform
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(caminho)
            elif sistema == "Darwin":
                subprocess.run(["open", caminho])
            else:
                subprocess.run(["xdg-open", caminho])
            self._notificar("Arquivo gerado e aberto!")
        except Exception as e:
            self._notificar(f"Erro ao abrir: {e}")

    def _voltar(self):
        if self.controller:
            self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color=cores.COR_AZUL_PRINCIPAL)
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.lbl_notificacao.bind("<Button-1>", lambda e: self.lbl_notificacao.configure(text=""))
        self.after(5000, lambda: self.lbl_notificacao.configure(text=""))