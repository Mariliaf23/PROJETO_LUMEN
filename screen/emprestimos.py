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
    usuario_tem_multa_pendente, listar_livros, verificar_suspensao_expirada,
    gerar_multa, aluno_tem_max_emprestimos, livro_tem_emprestimo_ativo,
    livro_tem_reserva_ativa, renovar_emprestimo, listar_emprestimos_ativos
)
from services.notificacoes import enviar_notificacao
from services.styles import (
    cores,
    criar_entry, criar_label, criar_titulo, criar_card, criar_scroll_frame, criar_combo,
    criar_botao_preenchido, FONTE_LABEL, FONTE_SUBTITULO
)

COLUNAS_EMP = [
    ("ID",           1,  60,  6),
    ("Beneficiário", 3, 200, 30),
    ("Patrimônio",   2, 140, 16),
    ("Livro",        3, 200, 30),
    ("Vencimento",   2, 110, 12),
    ("Status",       1, 100, 12),
]
COMPENSA_SCROLLBAR = 18


def validar_e_converter_data(entrada):
    MAX_DIAS = 14
    entrada = entrada.strip()
    try:
        dias = int(entrada)
        if dias <= 0:
            return False, None, "Os dias devem ser um número positivo."
        if dias > MAX_DIAS:
            return False, None, f"O prazo máximo é de {MAX_DIAS} dias."
        data_futura = date.today() + timedelta(days=dias)
        return True, data_futura.strftime("%Y-%m-%d"), None
    except ValueError:
        pass
    try:
        partes = entrada.split("-")
        if len(partes) != 3:
            return False, None, "Formato inválido. Use AAAA-MM-DD ou número de dias."
        ano, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
        data_obj = date(ano, mes, dia)
        if data_obj <= date.today():
            return False, None, "A data deve ser posterior a hoje."
        dias_diff = (data_obj - date.today()).days
        if dias_diff > MAX_DIAS:
            return False, None, f"O prazo máximo é de {MAX_DIAS} dias."
        return True, data_obj.strftime("%Y-%m-%d"), None
    except (ValueError, AttributeError):
        return False, None, "Formato inválido."


class DetalheGrupo(ctk.CTkToplevel):
    """Modal de detalhes de um grupo de empréstimo."""
    def __init__(self, master, dados):
        super().__init__(master)
        self.title("Detalhes do Grupo de Empréstimo")
        self.geometry("500x450")
        self.resizable(False, False)
        self.configure(fg_color=cores.COR_BG)
        self.grab_set()

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(60, 60))
                ctk.CTkLabel(self, image=img_logo, text="").pack(pady=(10, 0))
            except:
                criar_titulo(self, "LUMEN", font=("Cinzel", 20, "bold"), text_color=cores.COR_DOURADO).pack(pady=(10, 0))
        else:
            criar_titulo(self, "LUMEN", font=("Cinzel", 20, "bold"), text_color=cores.COR_DOURADO).pack(pady=(10, 0))

        criar_label(self, "Detalhes do Grupo", font=("Segoe UI", 16, "bold"), text_color=cores.COR_TEXTO).pack(pady=(5, 10))

        # Cabeçalho do grupo
        card_header = criar_card(self)
        card_header.pack(fill="x", padx=20, pady=(0, 10))

        id_grupo = dados.get('id_grupo', '')
        nome_usuario = dados.get('nome_usuario', '')
        data_prevista = dados.get('data_prevista', '')
        status = dados.get('status', '')

        campos_header = [
            ("ID Grupo", str(id_grupo)),
            ("Beneficiário", str(nome_usuario)),
            ("Data Prevista", self._formatar_data(data_prevista)),
            ("Status", str(status)),
        ]

        for rotulo, valor in campos_header:
            linha = ctk.CTkFrame(card_header, fg_color="transparent")
            linha.pack(fill="x", padx=15, pady=3)
            criar_label(linha, f"{rotulo}:", font=("Segoe UI", 12, "bold"), text_color=cores.COR_TEXTO).pack(side="left")
            cor_valor = cores.COR_TEXTO
            if rotulo == "Status":
                s = str(valor).lower()
                if s == "atrasado":
                    cor_valor = cores.COR_PERIGO
                elif s == "finalizado":
                    cor_valor = cores.COR_SUCESSO
                elif s == "ativo":
                    cor_valor = cores.COR_AVISO
            criar_label(linha, valor, font=("Segoe UI", 12), text_color=cor_valor).pack(side="right")

        # Lista de livros do grupo
        criar_label(self, "Livros no Grupo:", font=("Segoe UI", 13, "bold"), text_color=cores.COR_TEXTO).pack(pady=(5, 5))

        card_livros = criar_card(self)
        card_livros.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Busca livros do grupo
        from services.database_config import listar_grupo_emprestimo
        livros = listar_grupo_emprestimo(id_grupo)

        for livro in livros:
            linha = ctk.CTkFrame(card_livros, fg_color="transparent")
            linha.pack(fill="x", padx=10, pady=2)

            titulo = livro.get('titulo', '')
            patrimonio = livro.get('codigo_patrimonio', '')
            status_livro = livro.get('status', '')

            cor_status = cores.COR_TEXTO
            if status_livro == "atrasado":
                cor_status = cores.COR_PERIGO
            elif status_livro == "finalizado":
                cor_status = cores.COR_SUCESSO
            elif status_livro == "ativo":
                cor_status = cores.COR_AVISO

            criar_label(linha, f"{titulo} ({patrimonio})", font=("Segoe UI", 11), text_color=cores.COR_TEXTO).pack(side="left")
            criar_label(linha, status_livro, font=("Segoe UI", 11, "bold"), text_color=cor_status).pack(side="right")

        ctk.CTkButton(self, text="Fechar", command=self.destroy, width=160, height=36,
                      fg_color=cores.COR_ATIVO, hover_color=cores.COR_AZUL_HOVER,
                      font=("Segoe UI", 13, "bold")).pack(pady=10)

    def _formatar_data(self, data):
        try:
            if hasattr(data, 'strftime'):
                return data.strftime("%d/%m/%Y")
            elif isinstance(data, str) and "20" in str(data):
                partes = str(data).split("-")
                if len(partes) == 3:
                    return f"{partes[2]}/{partes[1]}/{partes[0]}"
        except:
            pass
        return str(data) if data else "-"


class DetalheEmprestimo(ctk.CTkToplevel):
    def __init__(self, master, dados):
        super().__init__(master)
        self.title("Detalhes do Empréstimo")
        self.geometry("420x520")
        self.resizable(False, False)
        self.configure(fg_color=cores.COR_BG)
        self.grab_set()

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(80, 80))
                ctk.CTkLabel(self, image=img_logo, text="").pack(pady=(15, 0))
            except:
                criar_titulo(self, "LUMEN", font=("Cinzel", 24, "bold"), text_color=cores.COR_DOURADO).pack(pady=(15, 0))
        else:
            criar_titulo(self, "LUMEN", font=("Cinzel", 24, "bold"), text_color=cores.COR_DOURADO).pack(pady=(15, 0))

        criar_label(self, "Detalhes do Empréstimo", font=("Segoe UI", 16, "bold"), text_color=cores.COR_TEXTO).pack(pady=(5, 15))

        card = criar_card(self)
        card.pack(fill="x", padx=30, pady=(0, 10))

        id_emp, aluno, exemplar, livro, data_emp, data_prev, data_dev, status = dados

        campos = [
            ("ID", str(id_emp)),
            ("Aluno", str(aluno)),
            ("Livro", str(livro)),
            ("Exemplar", str(exemplar)),
            ("Data Empréstimo", self._formatar_data(data_emp)),
            ("Data Prevista", self._formatar_data(data_prev)),
            ("Data Devolução", self._formatar_data(data_dev) if data_dev else "Pendente"),
            ("Status", str(status)),
        ]

        for rotulo, valor in campos:
            linha = ctk.CTkFrame(card, fg_color="transparent")
            linha.pack(fill="x", padx=15, pady=4)
            criar_label(linha, f"{rotulo}:", font=("Segoe UI", 13, "bold"), text_color=cores.COR_TEXTO).pack(side="left")
            cor_valor = cores.COR_TEXTO
            if rotulo == "Status":
                s = str(valor).lower()
                if s == "atrasado":
                    cor_valor = cores.COR_PERIGO
                elif s == "finalizado":
                    cor_valor = cores.COR_SUCESSO
                elif s == "ativo":
                    cor_valor = cores.COR_AVISO
            criar_label(linha, valor, font=("Segoe UI", 13), text_color=cor_valor).pack(side="right")

        ctk.CTkButton(self, text="Fechar", command=self.destroy, width=160, height=40,
                      fg_color=cores.COR_ATIVO, hover_color=cores.COR_AZUL_HOVER,
                      font=("Segoe UI", 14, "bold")).pack(pady=15)

    def _formatar_data(self, data):
        try:
            if hasattr(data, 'strftime'):
                return data.strftime("%d/%m/%Y")
            elif isinstance(data, str) and "20" in str(data):
                partes = str(data).split("-")
                if len(partes) == 3:
                    return f"{partes[2]}/{partes[1]}/{partes[0]}"
        except:
            pass
        return str(data) if data else "-"


class TelaEmprestimos(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        self.cor_bg = str(cores.COR_BG)
        self.cor_card = str(cores.COR_CARD)
        self.cor_texto = str(cores.COR_TEXTO)
        self.cor_texto2 = str(cores.COR_TEXTO2)

        super().__init__(master, fg_color=self.cor_bg)
        self.controller = controller
        self._aba_atual = "emprestimos"
        self._itens_lista = []
        self._itens_reserva = []
        self._selecionado = None
        self._reserva_selecionada = None
        self._construir_ui()



    def _reconstruir_tema(self):
        """Reconstrói a tela ao trocar o tema claro/escuro."""
        if not self.winfo_exists():
            return
        # Recalcula as cores base, pois a paleta pode ter mudado
        self.cor_bg = str(cores.COR_BG)
        self.cor_card = str(cores.COR_CARD)
        self.cor_texto = str(cores.COR_TEXTO)
        self.cor_texto2 = str(cores.COR_TEXTO2)
        self.configure(fg_color=self.cor_bg)

        for widget in self.winfo_children():
            widget.destroy()
        self._construir_ui()

    def _ao_visitar(self):
        if getattr(self, "_tema_pendente", False):
            self._reconstruir_tema()
        verificar_atrasos()
        verificar_suspensao_expirada()
        self._verificar_suspensao()
        self._mostrar_aba(self._aba_atual)

    def _verificar_suspensao(self):
        """Verifica empréstimos atrasados e aplica suspenção automática."""
        from services.database_config import _conectar
        try:
            conn = _conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.id_usuario, DATEDIFF(CURDATE(), e.data_prevista) as dias_atraso
                FROM emprestimo e
                WHERE e.status = 'atrasado' AND e.data_prevista < CURDATE()
            """)
            atrasos = cursor.fetchall()
            for id_usuario, dias_atraso in atrasos:
                suspensao_dias = dias_atraso * 2
                cursor.execute("""
                    UPDATE usuario SET status = 'suspenso', data_suspensao = DATE_ADD(CURDATE(), INTERVAL %s DAY)
                    WHERE id_usuario = %s AND status != 'suspenso'
                """, (suspensao_dias, id_usuario))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # HEADER compactado (mesmo padrão das outras telas)
        header = ctk.CTkFrame(self, fg_color=cores.COR_CARD)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 8))

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y", padx=10, pady=5)

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(55, 55))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))

        titulo = criar_label(header_left, "Gerenciamento de Empréstimos", font=("Segoe UI", 24, "bold"), text_color=cores.COR_TEXTO)
        titulo.pack(side="left")

        btn_voltar = ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=100, height=36,
            fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 14, "bold")
        )
        btn_voltar.pack(side="right", padx=15, pady=5)

        # ABAS (apenas Empréstimos e Reservas)
        abas_frame = ctk.CTkFrame(self, fg_color="transparent")
        abas_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(5, 5))

        self._botoes_abas = []
        for nome in ["Empréstimos", "Reservas"]:
            tag = "emprestimos" if nome == "Empréstimos" else "reservas"
            is_atual = (tag == self._aba_atual)

            btn = ctk.CTkButton(
                abas_frame, text=nome, font=("Segoe UI", 14, "bold"),
                fg_color=cores.COR_AZUL_PRINCIPAL if is_atual else "transparent",
                text_color="#FFFFFF" if is_atual else self.cor_texto,
                border_color=cores.COR_AZUL_PRINCIPAL if is_atual else self.cor_bg,
                border_width=1 if is_atual else 0,
                hover_color=cores.COR_AZUL_HOVER,
                width=140, height=36,
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

        self._construir_aba_emprestimos()
        self._construir_aba_reservas()

        self.lbl_notificacao = criar_label(self, "", text_color=self.cor_texto2)

    def _mostrar_aba(self, nome):
        self._aba_atual = nome
        for btn, n in self._botoes_abas:
            if n == nome:
                btn.configure(fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
                              border_color=cores.COR_AZUL_PRINCIPAL, border_width=1)
            else:
                btn.configure(fg_color="transparent", text_color=self.cor_texto,
                              border_color=self.cor_bg, border_width=0)

        self._frame_emprestimos.grid_forget()
        self._frame_reservas.grid_forget()

        if nome == "emprestimos":
            self._frame_emprestimos.grid(row=0, column=0, sticky="nsew")
            self._recarregar_emprestimos()
        elif nome == "reservas":
            self._frame_reservas.grid(row=0, column=0, sticky="nsew")
            self._recarregar_reservas()

    def _construir_aba_emprestimos(self):
        frame = self._frame_emprestimos
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        form_card = criar_card(frame)
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=12)
        form.grid_columnconfigure((0, 1), weight=1)

        ALTURA_INPUT = 36
        FONTE_INPUT = ("Segoe UI", 14)

        # ISBN (leitor USB) — Linha 0
        criar_label(form, "ISBN (leitor ou digitação)", font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
        self.entry_isbn_emp = criar_entry(form, placeholder="Leia o código de barras ou digite o ISBN...", height=ALTURA_INPUT)
        self.entry_isbn_emp.configure(font=FONTE_INPUT)
        self.entry_isbn_emp.grid(row=1, column=0, columnspan=2, pady=(0, 8), sticky="ew")
        self.entry_isbn_emp.bind("<Return>", lambda e: self._buscar_isbn_emprestimo())

# Aluno — linha única (busca com sugestões suspensas)
        criar_label(form, "Aluno", font=("Segoe UI", 13, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 2))

        aluno_container = ctk.CTkFrame(form, fg_color="transparent")
        aluno_container.grid(row=3, column=0, padx=(0, 10), pady=(0, 10), sticky="ew")
        aluno_container.grid_columnconfigure(0, weight=1)

        self.entry_busca_aluno = criar_entry(aluno_container, placeholder="Buscar aluno...", height=ALTURA_INPUT)
        self.entry_busca_aluno.configure(font=FONTE_INPUT)
        self.entry_busca_aluno.grid(row=0, column=0, sticky="ew")
        self.entry_busca_aluno.bind("<KeyRelease>", self._atualizar_sugestoes_aluno)
        self.entry_busca_aluno.bind("<FocusOut>", lambda e: self.after(150, self._esconder_sugestoes_aluno))

        self._frame_sugestoes_aluno = ctk.CTkScrollableFrame(
            aluno_container, fg_color=cores.COR_INPUT_BG, height=120, corner_radius=8
        )
        self._aluno_selecionado_id = None

        # Exemplar — linha única (busca com sugestões suspensas)
        criar_label(form, "Exemplar", font=("Segoe UI", 13, "bold")).grid(row=2, column=1, sticky="w", pady=(0, 2))

        exemplar_container = ctk.CTkFrame(form, fg_color="transparent")
        exemplar_container.grid(row=3, column=1, padx=(10, 0), pady=(0, 10), sticky="ew")
        exemplar_container.grid_columnconfigure(0, weight=1)

        self.entry_busca_exemplar = criar_entry(exemplar_container, placeholder="Buscar exemplar...", height=ALTURA_INPUT)
        self.entry_busca_exemplar.configure(font=FONTE_INPUT)
        self.entry_busca_exemplar.grid(row=0, column=0, sticky="ew")
        self.entry_busca_exemplar.bind("<KeyRelease>", self._atualizar_sugestoes_exemplar)
        self.entry_busca_exemplar.bind("<FocusOut>", lambda e: self.after(150, self._esconder_sugestoes_exemplar))

        self._frame_sugestoes_exemplar = ctk.CTkScrollableFrame(
            exemplar_container, fg_color=cores.COR_INPUT_BG, height=120, corner_radius=8
        )
        self._exemplar_selecionado_id = None

        # Prazo — Linha 4
        criar_label(form, "Prazo para Devolução", font=("Segoe UI", 13, "bold")).grid(row=4, column=0, sticky="w", pady=(4, 2))
        self.entry_vencimento = criar_entry(form, placeholder="Ex: 7 ou 2026-12-31", height=ALTURA_INPUT)
        self.entry_vencimento.configure(font=FONTE_INPUT)
        self.entry_vencimento.grid(row=5, column=0, padx=(0, 10), sticky="ew")

        botoes_frame = ctk.CTkFrame(form, fg_color="transparent")
        botoes_frame.grid(row=5, column=1, padx=(10, 0), sticky="ew")

        botoes_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.btn_cadastrar = ctk.CTkButton(
            botoes_frame, text="Confirmar", command=self._cadastrar_emprestimo,
            height=ALTURA_INPUT, fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 12, "bold")
        )
        self.btn_cadastrar.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_finalizar = ctk.CTkButton(
            botoes_frame, text="Finalizar", command=self._finalizar_emprestimo,
            height=ALTURA_INPUT, fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 12, "bold")
        )
        self.btn_finalizar.grid(row=0, column=1, padx=(0, 4), sticky="ew")

        self.btn_renovar = ctk.CTkButton(
            botoes_frame, text="Renovar", command=self._renovar_emprestimo,
            height=ALTURA_INPUT, fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 12, "bold")
        )
        self.btn_renovar.grid(row=0, column=2, padx=(0, 4), sticky="ew")

        self.btn_detalhes = ctk.CTkButton(
            botoes_frame, text="Detalhes", command=self._abrir_detalhes,
            height=ALTURA_INPUT, fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 12, "bold")
        )
        self.btn_detalhes.grid(row=0, column=3, sticky="ew")

        # Tabela
        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        # Barra de filtro
        filtro_frame = ctk.CTkFrame(lista_card, fg_color="transparent")
        filtro_frame.pack(fill="x", padx=20, pady=(10, 0))

        self.entry_filtro_aluno = criar_entry(filtro_frame, placeholder="Filtrar por aluno...", height=34)
        self.entry_filtro_aluno.configure(font=("Segoe UI", 13))
        self.entry_filtro_aluno.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_filtro_aluno.bind("<KeyRelease>", lambda e: self._filtrar_tabela_emprestimos())

        ctk.CTkButton(
            filtro_frame, text="Limpar", width=80, height=34,
            fg_color=cores.COR_CARD, font=("Segoe UI", 12, "bold"),
            command=self._limpar_filtro_emprestimos
        ).pack(side="left")

        # Cabeçalho (grid)
        header_tab = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_tab.pack(fill="x", padx=(20, 20 + COMPENSA_SCROLLBAR), pady=(8, 2))

        for idx, (nome, peso, minsize, max_chars) in enumerate(COLUNAS_EMP):
            header_tab.grid_columnconfigure(idx, weight=peso, minsize=minsize)
            ctk.CTkLabel(header_tab, text=nome.upper(), font=("Segoe UI", 12, "bold"),
                         text_color=cores.COR_TEXTO, anchor="center"
                         ).grid(row=0, column=idx, sticky="ew", padx=(10, 4), pady=8)

        self.lista_emprestimos = criar_scroll_frame(lista_card, fg_color=cores.COR_CARD)
        self.lista_emprestimos.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    def _atualizar_sugestoes_aluno(self, event=None):
        termo = self.entry_busca_aluno.get().strip().lower()
        for w in self._frame_sugestoes_aluno.winfo_children():
            w.destroy()
        if not termo:
            self._esconder_sugestoes_aluno()
            return
        resultados = [n for n in self._alunos_map.keys() if termo in n.lower()]
        if not resultados:
            self._esconder_sugestoes_aluno()
            return
        self._frame_sugestoes_aluno.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        for nome in resultados[:20]:
            ctk.CTkButton(
                self._frame_sugestoes_aluno, text=nome, anchor="w",
                fg_color="transparent", text_color=self.cor_texto,
                hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 14),
                height=36, corner_radius=4,
                command=lambda n=nome: self._escolher_aluno(n)
            ).pack(fill="x", pady=1)

    def _escolher_aluno(self, nome):
        self._aluno_selecionado_id = self._alunos_map.get(nome)
        self.entry_busca_aluno.delete(0, "end")
        self.entry_busca_aluno.insert(0, nome)
        self._esconder_sugestoes_aluno()

    def _esconder_sugestoes_aluno(self):
        self._frame_sugestoes_aluno.grid_forget()

    def _atualizar_sugestoes_exemplar(self, event=None):
        termo = self.entry_busca_exemplar.get().strip().lower()
        for w in self._frame_sugestoes_exemplar.winfo_children():
            w.destroy()
        if not termo:
            self._esconder_sugestoes_exemplar()
            return
        resultados = [n for n in self._exemplares_map.keys() if termo in n.lower()]
        if not resultados:
            self._esconder_sugestoes_exemplar()
            return
        self._frame_sugestoes_exemplar.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        for nome in resultados[:20]:
            ctk.CTkButton(
                self._frame_sugestoes_exemplar, text=nome, anchor="w",
                fg_color="transparent", text_color=self.cor_texto,
                hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 14),
                height=36, corner_radius=4,
                command=lambda n=nome: self._escolher_exemplar(n)
            ).pack(fill="x", pady=1)

    def _escolher_exemplar(self, nome):
        self._exemplar_selecionado_id = self._exemplares_map.get(nome)
        self.entry_busca_exemplar.delete(0, "end")
        self.entry_busca_exemplar.insert(0, nome)
        self._esconder_sugestoes_exemplar()

    def _esconder_sugestoes_exemplar(self):
        self._frame_sugestoes_exemplar.grid_forget()




    def _construir_aba_reservas(self):
        frame = self._frame_reservas
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        form_card = criar_card(frame)
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=12)
        form.grid_columnconfigure((0, 1), weight=1)

        ALTURA_INPUT = 36
        FONTE_INPUT = ("Segoe UI", 14)

        criar_label(form, "Aluno", font=("Segoe UI", 13, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.entry_busca_res_aluno = criar_entry(form, placeholder="Buscar aluno...", height=ALTURA_INPUT)
        self.entry_busca_res_aluno.configure(font=FONTE_INPUT)
        self.entry_busca_res_aluno.grid(row=1, column=0, padx=(0, 10), pady=(0, 5), sticky="ew")
        self.entry_busca_res_aluno.bind("<KeyRelease>", lambda e: self._filtrar_dados(self.entry_busca_res_aluno.get(), self.combo_reserva_aluno, self._reserva_alunos_map))

        self.combo_reserva_aluno = criar_combo(form, height=ALTURA_INPUT)
        self.combo_reserva_aluno.grid(row=2, column=0, padx=(0, 10), pady=(0, 10), sticky="ew")

        criar_label(form, "Livro", font=("Segoe UI", 13, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self.entry_busca_res_livro = criar_entry(form, placeholder="Buscar livro...", height=ALTURA_INPUT)
        self.entry_busca_res_livro.configure(font=FONTE_INPUT)
        self.entry_busca_res_livro.grid(row=1, column=1, padx=(10, 0), pady=(0, 5), sticky="ew")
        self.entry_busca_res_livro.bind("<KeyRelease>", lambda e: self._filtrar_dados(self.entry_busca_res_livro.get(), self.combo_reserva_livro, self._reserva_livros_map))

        self.combo_reserva_livro = criar_combo(form, height=ALTURA_INPUT)
        self.combo_reserva_livro.grid(row=2, column=1, padx=(10, 0), pady=(0, 10), sticky="ew")

        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.grid(row=3, column=0, columnspan=2, pady=(5, 0))

        self.btn_reservar = ctk.CTkButton(
            botoes, text="Nova Reserva", command=self._reservar,
            height=ALTURA_INPUT, fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 13, "bold")
        )
        self.btn_reservar.pack(side="left", padx=(0, 8))

        self.btn_cancelar_reserva = ctk.CTkButton(
            botoes, text="Cancelar", command=self._cancelar_reserva,
            height=ALTURA_INPUT, fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 13, "bold")
        )
        self.btn_cancelar_reserva.pack(side="left")

        # Tabela
        lista_card = criar_card(frame)
        lista_card.grid(row=1, column=0, sticky="nsew")

        COLUNAS_RES = [
            ("ID",           1,  60,  6),
            ("Beneficiário", 3, 200, 30),
            ("Livro",        4, 280, 35),
            ("Solicitação",  2, 110, 12),
            ("Prazo",        2, 110, 12),
            ("Situação",     1, 100, 12),
        ]

        header_tab = ctk.CTkFrame(lista_card, fg_color="transparent")
        header_tab.pack(fill="x", padx=(20, 20 + COMPENSA_SCROLLBAR), pady=(8, 2))

        for idx, (nome, peso, minsize, max_chars) in enumerate(COLUNAS_RES):
            header_tab.grid_columnconfigure(idx, weight=peso, minsize=minsize)
            ctk.CTkLabel(header_tab, text=nome.upper(), font=("Segoe UI", 12, "bold"),
                         text_color=cores.COR_TEXTO, anchor="center"
                         ).grid(row=0, column=idx, sticky="ew", padx=(10, 4), pady=8)

        self.lista_reservas = criar_scroll_frame(lista_card, fg_color=cores.COR_CARD)
        self.lista_reservas.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    # ==================== MÉTODOS EMPRÉSTIMOS ====================

    def _cadastrar_emprestimo(self):
        aluno_sel = self.entry_busca_aluno.get().strip()
        exemplar_sel = self.entry_busca_exemplar.get().strip()
        vencimento = self.entry_vencimento.get().strip()

        if not aluno_sel or not self._aluno_selecionado_id:
            self._notificar("Selecione um aluno válido na lista de sugestões.")
            return
        if not exemplar_sel or not self._exemplar_selecionado_id:
            self._notificar("Selecione um exemplar disponível na lista de sugestões.")
            return
        if not vencimento:
            self._notificar("Informe a data de devolução.")
            return

        sucesso, data_convertida, erro = validar_e_converter_data(vencimento)
        if not sucesso:
            self._notificar(f"Erro na data: {erro}")
            return

        id_usuario = self._aluno_selecionado_id
        id_exemplar = self._exemplar_selecionado_id
        id_funcionario = self.controller.usuario_logado['id'] if self.controller and hasattr(self.controller, 'usuario_logado') else 1

        if usuario_tem_multa_pendente(id_usuario):
            self._notificar("Aluno com multa pendente! Regularize primeiro.")
            return

        if aluno_tem_max_emprestimos(id_usuario):
            self._notificar("Limite atingido! Máximo de 3 livros (empréstimos + reservas).")
            return

        self.btn_cadastrar.configure(text="Processando...", state="disabled")
        self._salvar_emprestimo(id_usuario, id_exemplar, data_convertida, id_funcionario)

    def _salvar_emprestimo(self, id_usuario, id_exemplar, vencimento, id_funcionario):
        sucesso = cadastrar_emprestimo(id_usuario, id_exemplar, vencimento, id_funcionario)
        if sucesso:
            self._notificar("Empréstimo registrado com sucesso!")

            # Notificação WhatsApp
            try:
                from services.database_config import _conectar
                conn = _conectar()
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT u.nome, l.titulo, e.codigo_patrimonio
                       FROM usuario u, livro l, exemplar e
                       WHERE u.id_usuario = %s AND e.id_exemplar = %s AND l.id_livro = e.id_livro""",
                    (id_usuario, id_exemplar)
                )
                dados = cursor.fetchone()
                conn.close()
                if dados:
                    from datetime import date, timedelta
                    data_emp = date.today().strftime("%d/%m/%Y")
                    try:
                        if "-" in str(vencimento):
                            partes = str(vencimento).split("-")
                            data_prev = f"{partes[2]}/{partes[1]}/{partes[0]}"
                        else:
                            data_prev = (date.today() + timedelta(days=int(vencimento))).strftime("%d/%m/%Y")
                    except Exception:
                        data_prev = str(vencimento)
                    enviar_notificacao(id_usuario, "emprestimo_realizado", {
                        "livro": dados[1],
                        "patrimonio": dados[2],
                        "emprestimo": data_emp,
                        "devolucao": data_prev,
                    })
            except Exception:
                pass

            self.entry_vencimento.delete(0, "end")
            self.entry_busca_aluno.delete(0, "end")
            self.entry_busca_exemplar.delete(0, "end")
            self._aluno_selecionado_id = None
            self._exemplar_selecionado_id = None
            self._recarregar_emprestimos()
        else:
            self._notificar("Erro ao salvar empréstimo.")
        self.btn_cadastrar.configure(text="Confirmar", state="normal")

    def _finalizar_emprestimo(self):
        if not self._selecionado:
            self._notificar("Selecione um registro na listagem.")
            return
        emp_id = self._selecionado[0]
        msg = "Empréstimo finalizado com sucesso!"

        try:
            data_prevista = self._selecionado[5]
            if hasattr(data_prevista, 'strftime'):
                data_prevista_obj = data_prevista
            else:
                data_str = str(data_prevista)
                partes = data_str.split()[0].split("-")
                data_prevista_obj = date(int(partes[0]), int(partes[1]), int(partes[2]))

            hoje = date.today()
            dias_atraso = (hoje - data_prevista_obj).days

            if dias_atraso > 0:
                gerar_multa(emp_id, dias_atraso, 'atraso')
                msg = f"Empréstimo finalizado! Multa: {dias_atraso} dias de atraso."
        except Exception:
            pass

        sucesso = finalizar_emprestimo(emp_id)
        if sucesso:
            self._notificar(msg)

            # Notificação WhatsApp — devolução
            try:
                if self._selecionado:
                    enviar_notificacao(None, "devolucao_realizada", {
                        "livro": self._selecionado[3] if len(self._selecionado) > 3 else "",
                        "patrimonio": self._selecionado[2] if len(self._selecionado) > 2 else "",
                    })
                    # Busca ID do usuário pelo nome para a notificação
                    nome_user = self._selecionado[1] if len(self._selecionado) > 1 else ""
                    if nome_user:
                        from services.database_config import _conectar
                        conn = _conectar()
                        cursor = conn.cursor()
                        cursor.execute("SELECT id_usuario FROM usuario WHERE nome = %s", (nome_user,))
                        row = cursor.fetchone()
                        conn.close()
                        if row:
                            enviar_notificacao(row[0], "devolucao_realizada", {
                                "livro": self._selecionado[3] if len(self._selecionado) > 3 else "",
                                "patrimonio": self._selecionado[2] if len(self._selecionado) > 2 else "",
                            })
            except Exception:
                pass

            self._selecionado = None
            self._recarregar_emprestimos()
        else:
            self._notificar("Erro ao processar devolução.")

    def _abrir_detalhes(self):
        if not self._selecionado:
            self._notificar("Selecione um empréstimo para ver detalhes.")
            return
        # Converte dados para formato do DetalheEmprestimo (8 campos)
        # listar_emprestimos_ativos() retorna 7 campos, precisamos adicionar data_devolucao=None
        emp = self._selecionado
        dados = (
            emp[0],  # id_emprestimo
            emp[1],  # nome
            emp[2],  # codigo_patrimonio
            emp[3],  # titulo
            emp[4],  # data_emprestimo
            emp[5],  # data_prevista
            None,    # data_devolucao (não disponível em empréstimos ativos)
            emp[6],  # status
        )
        DetalheEmprestimo(self, dados)

    def _renovar_emprestimo(self):
        if not self._selecionado:
            self._notificar("Selecione um empréstimo para renovar.")
            return
        emp_id = self._selecionado[0]
        status = str(self._selecionado[6]).lower() if len(self._selecionado) > 6 else ""
        if status != "ativo":
            self._notificar("Só é possível renovar empréstimos ativos.")
            return
        # Verifica se o livro tem reserva ativa
        id_exemplar = self._selecionado[2] if len(self._selecionado) > 2 else None
        if id_exemplar:
            from services.database_config import _conectar
            try:
                conn = _conectar()
                cursor = conn.cursor()
                cursor.execute("SELECT id_livro FROM exemplar WHERE codigo_patrimonio = %s", (id_exemplar,))
                result = cursor.fetchone()
                conn.close()
                if result and livro_tem_reserva_ativa(result[0]):
                    self._notificar("Não é possível renovar: livro possui reserva ativa!")
                    return
            except Exception:
                pass
        sucesso = renovar_emprestimo(emp_id)
        if sucesso:
            self._notificar("Empréstimo renovado por 7 dias!")
            self._recarregar_emprestimos()
        else:
            self._notificar("Erro ao renovar empréstimo.")

    def _recarregar_emprestimos(self, emprestimos_filtrados=None):
        for widget in self.lista_emprestimos.winfo_children():
            widget.destroy()
        self._itens_lista = []
        self._selecionado = None

        alunos = listar_alunos()
        self._alunos_map = {a[1]: a[0] for a in alunos}

        exemplares = listar_exemplares_disponiveis()
        self._exemplares_map = {}
        for e in exemplares:
            key = f"{e[2]} ({e[1]})" if len(e) > 2 else str(e[0])
            self._exemplares_map[key] = e[0]
        emprestimos = emprestimos_filtrados if emprestimos_filtrados is not None else listar_emprestimos_ativos()
        for emp in map(list, list(emprestimos)):
            self._criar_item_emp(emp)

    def _criar_item_emp(self, emp):
        item = ctk.CTkFrame(self.lista_emprestimos, fg_color=self.cor_card, corner_radius=6, height=40)
        item.pack(fill="x", pady=2)
        item.pack_propagate(False)
        item.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))

        # listar_emprestimos_ativos() retorna: id, nome, codigo_patrimonio, titulo, data_emprestimo, data_prevista, status
        # COLUNAS_EMP: ID, Beneficiário, Patrimônio, Livro, Vencimento, Status
        indices_exibir = [0, 1, 2, 3, 5, 6]

        for idx_col, (nome, peso, minsize, max_chars) in enumerate(COLUNAS_EMP):
            item.grid_columnconfigure(idx_col, weight=peso, minsize=minsize)
            db_idx = indices_exibir[idx_col]
            texto = emp[db_idx] if db_idx < len(emp) else ""

            if idx_col == 4:  # Vencimento
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

            texto_str = str(texto) if texto else "-"
            if len(texto_str) > max_chars:
                texto_str = texto_str[:max_chars - 1].rstrip() + "…"

            cor = self.cor_texto
            if nome == "Status":
                s = str(texto).lower() if texto else ""
                if s == "atrasado":
                    cor = cores.COR_PERIGO
                elif s == "ativo":
                    cor = cores.COR_AVISO
                elif s == "finalizado":
                    cor = cores.COR_SUCESSO

            lbl = ctk.CTkLabel(item, text=texto_str, font=("Segoe UI", 13), text_color=cor, anchor="center")
            lbl.grid(row=0, column=idx_col, sticky="ew", padx=(10, 4), pady=7)
            lbl.bind("<Button-1>", lambda e, v=emp: self._selecionar(v))

        self._itens_lista.append((item, emp))

    def _selecionar(self, emp):
        self._selecionado = emp
        for item, e in self._itens_lista:
            if e == emp:
                item.configure(fg_color=cores.COR_SEL)
                for widget in item.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color="#FFFFFF", fg_color=cores.COR_SEL)
            else:
                item.configure(fg_color=self.cor_card)
                for idx, widget in enumerate(item.winfo_children()):
                    if isinstance(widget, ctk.CTkLabel):
                        nome_col = COLUNAS_EMP[idx][0] if idx < len(COLUNAS_EMP) else ""
                        if nome_col == "Status":
                            st = str(e[7]).lower() if len(e) > 7 else ""
                            if st == "atrasado":
                                cor_st = cores.COR_PERIGO
                            elif st == "finalizado":
                                cor_st = cores.COR_SUCESSO
                            elif st == "ativo":
                                cor_st = cores.COR_AVISO
                            else:
                                cor_st = self.cor_texto
                            widget.configure(text_color=cor_st, fg_color=self.cor_card)
                        else:
                            widget.configure(text_color=self.cor_texto, fg_color=self.cor_card)
        self.lista_emprestimos.update_idletasks()

    def _filtrar_dados(self, termo, combo_alvo, mapa_referencia):
        termo = termo.lower().strip()
        opcoes_filtradas = [chave for chave in mapa_referencia.keys() if termo in chave.lower()]
        if opcoes_filtradas:
            combo_alvo.configure(values=opcoes_filtradas)
            combo_alvo.set(opcoes_filtradas[0])
        else:
            combo_alvo.configure(values=["Nenhum resultado"])
            combo_alvo.set("Nenhum resultado")

    def _filtrar_tabela_emprestimos(self):
        """Filtra a tabela de empréstimos pelo nome do aluno."""
        termo = self.entry_filtro_aluno.get().strip().lower()

        if not termo:
            self._recarregar_emprestimos()
            return

        emprestimos = listar_emprestimos_ativos()
        filtrados = []

        for emp in emprestimos:
            nome_aluno = str(emp[1]).lower() if emp[1] else ""
            if termo in nome_aluno:
                filtrados.append(emp)

        # Limpa e recarrega a tabela com os filtrados
        for widget in self.lista_emprestimos.winfo_children():
            widget.destroy()
        self._itens_lista = []
        self._selecionado = None

        for emp in map(list, filtrados):
            self._criar_item_emp(emp)

        if not filtrados:
            ctk.CTkLabel(self.lista_emprestimos, text="Nenhum empréstimo encontrado",
                         font=("Segoe UI", 14), text_color=self.cor_texto2
                         ).pack(pady=20)

    def _limpar_filtro_emprestimos(self):
        """Limpa o filtro e recarrega todos os empréstimos."""
        self.entry_filtro_aluno.delete(0, "end")
        self._recarregar_emprestimos()

    def _buscar_isbn_emprestimo(self):
        """Busca exemplares pelo ISBN lido (leitor USB ou digitação)."""
        import re
        isbn = re.sub(r'\D', '', self.entry_isbn_emp.get().strip())
        if not isbn:
            self._notificar("Informe um ISBN.")
            return

        from services.database_config import _conectar
        try:
            conn = _conectar()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT e.id_exemplar, e.codigo_patrimonio, l.titulo
                   FROM exemplar e
                   JOIN livro l ON e.id_livro = l.id_livro
                   WHERE l.isbn = %s AND e.status_exemplar = 'disponivel'""",
                (isbn,)
            )
            exemplares = cursor.fetchall()
            conn.close()
        except Exception:
            self._notificar("Erro ao buscar exemplares pelo ISBN.")
            return

        if not exemplares:
            self._notificar("Nenhum exemplar disponível para este ISBN.")
            return

        # Filtra o combo de exemplares para mostrar apenas os deste livro
        primeiro = exemplares[0]
        nome = f"{primeiro[1]} ({primeiro[2]})"
        self._exemplar_selecionado_id = primeiro[0]
        self.entry_busca_exemplar.delete(0, "end")
        self.entry_busca_exemplar.insert(0, nome)
        self._esconder_sugestoes_exemplar()

        titulo = primeiro[2]
        self._notificar(f"Encontrado: {titulo} ({len(exemplares)} disponível(is))")
        
    # ==================== MÉTODOS RESERVAS ====================

    def _recarregar_reservas(self):
        for widget in self.lista_reservas.winfo_children():
            widget.destroy()
        self._itens_reserva = []
        self._reserva_selecionada = None

        alunos = listar_alunos()
        self._reserva_alunos_map = {}
        nomes_alunos = [a[1] for a in alunos]  # Apenas o nome
        for a in alunos:
            self._reserva_alunos_map[a[1]] = a[0]
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

        COLUNAS_RES_DADOS = [
            ("ID",           1,  60,  6),
            ("Beneficiário", 3, 200, 30),
            ("Livro",        4, 280, 35),
            ("Solicitação",  2, 110, 12),
            ("Prazo",        2, 110, 12),
            ("Situação",     1, 100, 12),
        ]

        reservas = listar_reservas(status="ativa")
        for r in reservas:
            item = ctk.CTkFrame(self.lista_reservas, fg_color=self.cor_card, corner_radius=6, height=40)
            item.pack(fill="x", pady=2)
            item.pack_propagate(False)
            item.bind("<Button-1>", lambda e, v=r: self._selecionar_reserva(v))

            for idx_col, (nome, peso, minsize, max_chars) in enumerate(COLUNAS_RES_DADOS):
                item.grid_columnconfigure(idx_col, weight=peso, minsize=minsize)
                texto = r[idx_col] if idx_col < len(r) else "-"
                texto_str = str(texto) if texto else "-"
                if len(texto_str) > max_chars:
                    texto_str = texto_str[:max_chars - 1].rstrip() + "…"

                cor = self.cor_texto
                if nome == "Situação":
                    s = str(texto).lower() if texto else ""
                    if s == "ativa":
                        cor = cores.COR_AVISO
                    elif s == "cancelada":
                        cor = cores.COR_PERIGO

                lbl = ctk.CTkLabel(item, text=texto_str, font=("Segoe UI", 13), text_color=cor, anchor="center")
                lbl.grid(row=0, column=idx_col, sticky="ew", padx=(10, 4), pady=7)
                lbl.bind("<Button-1>", lambda e, v=r: self._selecionar_reserva(v))

            self._itens_reserva.append((item, r))

    def _selecionar_reserva(self, r):
        self._reserva_selecionada = r
        for item, v in self._itens_reserva:
            if v == r:
                item.configure(fg_color=cores.COR_SEL)
                for widget in item.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color="#FFFFFF", fg_color=cores.COR_SEL)
            else:
                item.configure(fg_color=self.cor_card)
                for widget in item.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color=self.cor_texto, fg_color=self.cor_card)

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

        if aluno_tem_max_emprestimos(id_usuario):
            self._notificar("Limite atingido! Máximo de 3 livros (empréstimos + reservas).")
            return

        if not livro_tem_emprestimo_ativo(id_livro):
            self._notificar("Só é possível reservar livros que estão emprestados!")
            return

        self.btn_reservar.configure(text="Salvando...", state="disabled")
        self._salvar_reserva(id_usuario, id_livro)

    def _salvar_reserva(self, id_usuario, id_livro):
        sucesso = cadastrar_reserva(id_usuario, id_livro)
        if sucesso:
            self._notificar("Reserva ativada com sucesso!")

            # Notificação WhatsApp — reserva criada
            try:
                from services.database_config import _conectar
                conn = _conectar()
                cursor = conn.cursor()
                cursor.execute("SELECT titulo FROM livro WHERE id_livro = %s", (id_livro,))
                row_livro = cursor.fetchone()
                conn.close()
                titulo_livro = row_livro[0] if row_livro else ""
                from datetime import date
                enviar_notificacao(id_usuario, "reserva_criada", {
                    "livro": titulo_livro,
                    "emprestimo": date.today().strftime("%d/%m/%Y"),
                })
            except Exception:
                pass

            self.entry_busca_res_aluno.delete(0, "end")
            self.entry_busca_res_livro.delete(0, "end")
            self._recarregar_reservas()
        else:
            self._notificar("Erro ao gerar reserva.")
        self.btn_reservar.configure(text="Nova Reserva", state="normal")

    def _cancelar_reserva(self):
        if not self._reserva_selecionada:
            self._notificar("Selecione uma reserva ativa.")
            return
        id_reserva = self._reserva_selecionada[0]
        sucesso = cancelar_reserva(id_reserva)
        if sucesso:
            self._notificar("Reserva removida!")
            self._reserva_selecionada = None
            self._recarregar_reservas()
        else:
            self._notificar("Erro ao cancelar reserva.")

    def _voltar(self):
        if self.controller:
            self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color=cores.COR_AZUL_HOVER)
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.lbl_notificacao.bind("<Button-1>", lambda e: self.lbl_notificacao.configure(text=""))
        self.after(5000, lambda: self.lbl_notificacao.configure(text=""))