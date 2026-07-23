import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import (
    listar_usuarios, buscar_usuario_por_id, atualizar_usuario,
    atualizar_senha_usuario, alternar_status_usuario, excluir_usuario,
    buscar_usuarios_por_nome, cadastrar_usuario, listar_turmas
)
from services.styles import (
    cores, FONTE_TITULO, FONTE_SUBTITULO,
    criar_entry, criar_botao_preenchido, criar_botao, criar_label, criar_titulo, criar_combo,
    aplicar_validacao_focusout
)
from services.validador import validar_nome, validar_email, validar_telefone, validar_senha

COMPENSA_SCROLLBAR = 18


def _truncar(valor, max_chars):
    texto = "-" if valor is None or valor == "" else str(valor)
    if len(texto) <= max_chars:
        return texto
    return texto[: max_chars - 1].rstrip() + "…"


# ─────────────────────────────────────────────────────────────────────────────
#  Janela de edição / cadastro (reutilizável)
# ─────────────────────────────────────────────────────────────────────────────
class JanelaUsuario(ctk.CTkToplevel):
    """Abre um formulário para criar ou editar um usuário."""

    def __init__(self, master, on_salvo, id_usuario=None):
        super().__init__(master)
        self.on_salvo   = on_salvo
        self.id_usuario = id_usuario
        self._turmas    = listar_turmas()  # [(id, codigo, turno), ...]
        self.title("Editar Usuário" if id_usuario else "Novo Usuário")
        self.geometry("420x580")
        self.resizable(False, False)
        self.configure(fg_color=cores.COR_BG)
        self.grab_set()
        self._construir()
        if id_usuario:
            self._carregar(id_usuario)

    # ── UI ──────────────────────────────────────────────────────────────────
    def _construir(self):
        pad = {"padx": 30}

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")
        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(180, 180))
                ctk.CTkLabel(self, image=img_logo, text="").pack(pady=(20, 0))
            except:
                ctk.CTkLabel(self, text="LUMEN", font=FONTE_TITULO, text_color=cores.COR_AZUL_PRINCIPAL).pack(pady=(20, 0), **pad)
        else:
            ctk.CTkLabel(self, text="LUMEN", font=FONTE_TITULO, text_color=cores.COR_AZUL_PRINCIPAL).pack(pady=(20, 0), **pad)

        titulo = "Editar Usuário" if self.id_usuario else "Novo Usuário"
        criar_label(self, titulo, font=FONTE_SUBTITULO, text_color=cores.COR_TEXTO).pack(pady=(0, 16), **pad)

        self.combo_tipo = criar_combo(
            self, values=["aluno", "professor", "bibliotecario"], width=340, height=40,
            button_color=cores.COR_AZUL_PRINCIPAL, button_hover_color=cores.COR_AZUL_HOVER
        )
        self.combo_tipo.set("aluno")
        self.combo_tipo.configure(command=self._tipo_mudou)
        self.combo_tipo.pack(pady=(0, 10), **pad)

        self.combo_status = criar_combo(
            self, values=["ativo", "inativo"], width=340, height=40,
            button_color=cores.COR_AZUL_PRINCIPAL, button_hover_color=cores.COR_AZUL_HOVER
        )
        self.combo_status.set("ativo")
        self.combo_status.pack(pady=(0, 10), **pad)

        self.entry_nome    = criar_entry(self, placeholder="Nome completo",    width=340, height=40)
        self.entry_email   = criar_entry(self, placeholder="E-mail corporativo", width=340, height=40)
        self.entry_telefone = criar_entry(self, placeholder="Telefone (opcional)", width=340, height=40)

        for w in (self.entry_nome, self.entry_email, self.entry_telefone):
            w.pack(pady=(0, 8), **pad)

        # Container para campos dinâmicos (sempre presente, controla espaço)
        self.frame_dinamico = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_dinamico.pack(fill="x", **pad)

        # Frame senha (dentro do dinâmico)
        self.frame_senha = ctk.CTkFrame(self.frame_dinamico, fg_color="transparent")
        self.entry_senha = criar_entry(self.frame_senha, placeholder="Senha (obrigatorio)", width=340, height=40, show="*")
        self.entry_senha.pack()

        # Frame aluno (dentro do dinâmico)
        self.frame_aluno_prof = ctk.CTkFrame(self.frame_dinamico, fg_color="transparent")
        turma_labels = [f"{c} - {t}" for _, c, t in self._turmas] if self._turmas else ["(nenhuma turma cadastrada)"]
        self.combo_turma = criar_combo(
            self.frame_aluno_prof, values=turma_labels, width=340, height=40,
            button_color=cores.COR_AZUL_PRINCIPAL, button_hover_color=cores.COR_AZUL_HOVER
        )
        self.combo_turma.set(turma_labels[0])
        self.combo_turma.pack()

        # Frame funcionário (dentro do dinâmico)
        self.frame_func = ctk.CTkFrame(self.frame_dinamico, fg_color="transparent")
        self.entry_funcao = criar_entry(self.frame_func, placeholder="Função (ex: diretor)", width=340, height=40)
        self.entry_funcao.pack()

        self._tipo_mudou("aluno")

        # Botão Salvar (sempre por último)
        ctk.CTkButton(self, text="Salvar", command=self._salvar,
                      width=340, height=42,
                      fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
                      hover_color=cores.COR_AZUL_HOVER).pack(pady=(14, 6), **pad)

        self.lbl_notif = criar_label(self, "", text_color=cores.COR_TEXTO2)
        self.lbl_notif.pack()

        # ── Label único de erro flutuante ──
        self._lbl_erro_campo = criar_label(self, "", font=("Segoe UI", 12))
        self._lbl_erro_campo.pack()

        _entries = [self.entry_nome, self.entry_email, self.entry_telefone, self.entry_senha]
        aplicar_validacao_focusout(self.entry_nome,     lambda v: validar_nome(v),                              self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_email,    lambda v: validar_email(v),                             self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_telefone, lambda v: validar_telefone(v),                          self._lbl_erro_campo, _entries)
        aplicar_validacao_focusout(self.entry_senha,    lambda v: validar_senha(v) if v else (True, ""),        self._lbl_erro_campo, _entries)

    # ── lógica de tipo ───────────────────────────────────────────────────────
    def _tipo_mudou(self, tipo):
        self.frame_senha.pack_forget()
        self.frame_aluno_prof.pack_forget()
        self.frame_func.pack_forget()
        if tipo == "aluno":
            self.frame_aluno_prof.pack(pady=(0, 6))
        elif tipo == "bibliotecario":
            self.frame_senha.pack(pady=(0, 8))
        elif tipo == "professor":
            pass  # Professor: sem senha, sem função

    # ── preencher campos ao editar ───────────────────────────────────────────
    def _carregar(self, id_usuario):
        dados = buscar_usuario_por_id(id_usuario)
        if not dados:
            return
        _, nome, email, telefone, cpf, tipo, matricula, id_turma, funcao, status = dados

        self.combo_tipo.set(tipo or "aluno")
        self.combo_status.set(status or "ativo")
        self._tipo_mudou(tipo or "aluno")

        def _set(entry, valor):
            entry.delete(0, "end")
            entry.insert(0, valor or "")

        _set(self.entry_nome,     nome)
        _set(self.entry_email,    email)
        _set(self.entry_telefone, telefone)
        _set(self.entry_funcao,   funcao)

        if id_turma and self._turmas:
            for tid, codigo, turno in self._turmas:
                if tid == id_turma:
                    self.combo_turma.set(f"{codigo} - {turno}")
                    break

    # ── salvar ───────────────────────────────────────────────────────────────
    def _salvar(self):
        nome     = self.entry_nome.get().strip()
        email    = self.entry_email.get().strip()
        telefone = self.entry_telefone.get().strip()
        senha    = self.entry_senha.get().strip()
        tipo     = self.combo_tipo.get()
        status   = self.combo_status.get()

        id_turma = self._get_id_turma() if tipo == "aluno" else None
        funcao   = ""  # Função não é utilizada nesta tela

        ok, msg = validar_nome(nome)
        if not ok:
            return self._notificar(msg)
        ok, msg = validar_email(email)
        if not ok:
            return self._notificar(msg)
        ok, msg = validar_telefone(telefone)
        if not ok:
            return self._notificar(msg)
        if tipo == "bibliotecario":
            if not self.id_usuario and not senha:
                return self._notificar("Senha é obrigatória para bibliotecário.")
            if senha:
                ok, msg = validar_senha(senha)
                if not ok:
                    return self._notificar(msg)
        elif senha:  # senha opcional para outros tipos, mas se preenchida valida
            ok, msg = validar_senha(senha)
            if not ok:
                return self._notificar(msg)

        if self.id_usuario:
            ok = atualizar_usuario(
                self.id_usuario, nome, email, telefone, '',
                tipo, '', id_turma, funcao, status
            )
            if ok and senha:
                atualizar_senha_usuario(self.id_usuario, senha)
            msg_ok = "Usuario atualizado!"
        else:
            ok = cadastrar_usuario(nome, email, senha or '', telefone, '',
                                   tipo, '', id_turma, funcao)
            msg_ok = "Usuario cadastrado!"

        if ok:
            self._notificar(msg_ok)
            self.after(1000, lambda: (self.on_salvo(), self.destroy()))
        else:
            self._notificar("Erro ao salvar (e-mail/CPF duplicado?).")

    def _get_id_turma(self):
        sel = self.combo_turma.get()
        for tid, codigo, turno in self._turmas:
            if f"{codigo} - {turno}" == sel:
                return tid
        return None

    def _notificar(self, msg):
        self.lbl_notif.configure(text=msg)
        self.lbl_notif.bind("<Button-1>", lambda e: self.lbl_notif.configure(text=""))
        self.after(5000, lambda: self.lbl_notif.configure(text=""))


# ─────────────────────────────────────────────────────────────────────────────
#  Linha da tabela
# ─────────────────────────────────────────────────────────────────────────────
class LinhaUsuario(ctk.CTkFrame):
    COLUNAS = [
        ("ID",      1, 50,  6),
        ("NOME",    5, 220, 28),
        ("EMAIL",   4, 180, 24),
        ("TELEFONE",3, 120, 16),
        ("TIPO",    2, 100, 12),
        ("TURMA",   2, 130, 15),
        ("STATUS",  1, 80,  8),
    ]

    LARGURA_BTN_EDITAR  = 90
    LARGURA_BTN_STATUS  = 90
    LARGURA_BTN_EXCLUIR = 36
    GAP_BOTOES          = 8
    PAD_BORDA_DIREITA   = 10

    LARGURA_COL_ACOES = (
        LARGURA_BTN_EDITAR + GAP_BOTOES +
        LARGURA_BTN_STATUS + GAP_BOTOES +
        LARGURA_BTN_EXCLUIR + PAD_BORDA_DIREITA
    )

    def __init__(self, master, dados, indice, on_editar, on_alternar, on_excluir, turmas_map=None, on_selecionar=None, **kw):
        cor = cores.COR_LINHA_PAR if indice % 2 == 0 else cores.COR_LINHA_IMPAR
        self._cor_original = cor
        super().__init__(master, fg_color=cor, corner_radius=0, **kw)

        id_u, nome, email, telefone, cpf, tipo, matricula, id_turma, funcao, status = dados

        turma_label = "-"
        if turmas_map and id_turma and id_turma in turmas_map:
            c, t = turmas_map[id_turma]
            turma_label = f"{c} - {t}"

        valores = [id_u, nome, email, telefone, tipo, turma_label, status]
        self._labels = []
        self._cores_originais = []

        for idx, ((rotulo, peso, minsize, max_chars), valor) in enumerate(
            zip(self.COLUNAS, valores)
        ):
            self.grid_columnconfigure(idx, weight=peso, minsize=minsize)
            texto = _truncar(valor, max_chars)
            cor_val = cores.COR_SUCESSO if valor == "ativo" else (cores.COR_PERIGO if valor == "inativo" else cores.COR_TEXTO)
            ancora = "w" if rotulo == "NOME" else "center"
            lbl = criar_label(self, texto, text_color=cor_val, anchor=ancora,
                        font=("Segoe UI", 15))
            lbl.grid(row=0, column=idx, sticky="ew", padx=(10, 4), pady=6)
            if on_selecionar:
                lbl.bind("<Button-1>", lambda e, s=on_selecionar: s(self))
            self._labels.append(lbl)
            self._cores_originais.append(cor_val)

        if on_selecionar:
            self.bind("<Button-1>", lambda e: on_selecionar(self))

        # ── coluna de ações ──
        col_acoes = len(self.COLUNAS)
        self.grid_columnconfigure(col_acoes, weight=0, minsize=self.LARGURA_COL_ACOES)

        frame_acoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_acoes.grid(row=0, column=col_acoes, sticky="e", padx=(4, self.PAD_BORDA_DIREITA), pady=4)

        ctk.CTkButton(
            frame_acoes, text="Editar", width=self.LARGURA_BTN_EDITAR, height=32,
            fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
            hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 13, "bold"),
            command=lambda: on_editar(id_u)
        ).pack(side="left", padx=(0, self.GAP_BOTOES))

        label_status = "Ativar" if status == "inativo" else "Desativar"
        cor_status   = cores.COR_SUCESSO if status == "inativo" else cores.COR_AVISO
        ctk.CTkButton(
            frame_acoes, text=label_status, width=self.LARGURA_BTN_STATUS, height=32,
            fg_color=cor_status, text_color="#fff", font=("Segoe UI", 13, "bold"),
            command=lambda: on_alternar(id_u)
        ).pack(side="left", padx=(0, self.GAP_BOTOES))

        ctk.CTkButton(
            frame_acoes, text="✕", width=self.LARGURA_BTN_EXCLUIR, height=32,
            fg_color=cores.COR_PERIGO, text_color="#fff", font=("Segoe UI", 13, "bold"),
            command=lambda: on_excluir(id_u, nome)
        ).pack(side="left")

    def selecionar(self):
        self.configure(fg_color=cores.COR_SEL)
        for lbl in self._labels:
            lbl.configure(fg_color=cores.COR_SEL, text_color="#FFFFFF")

    def desselecionar(self):
        self.configure(fg_color=self._cor_original)
        for lbl, cor in zip(self._labels, self._cores_originais):
            lbl.configure(fg_color=self._cor_original, text_color=cor)

        col_acoes = len(self.COLUNAS)
        self.grid_columnconfigure(col_acoes, weight=0, minsize=self.LARGURA_COL_ACOES)

        frame_acoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_acoes.grid(row=0, column=col_acoes, sticky="e", padx=(4, self.PAD_BORDA_DIREITA), pady=4)

        ctk.CTkButton(
            frame_acoes, text="Editar", width=self.LARGURA_BTN_EDITAR, height=32,
            fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
            hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 13, "bold"),
            command=lambda: on_editar(id_u)
        ).pack(side="left", padx=(0, self.GAP_BOTOES))

        label_status = "Ativar" if status == "inativo" else "Desativar"
        cor_status   = cores.COR_SUCESSO if status == "inativo" else cores.COR_AVISO
        ctk.CTkButton(
            frame_acoes, text=label_status, width=self.LARGURA_BTN_STATUS, height=32,
            fg_color=cor_status, text_color="#fff",
            font=("Segoe UI", 13, "bold"),
            command=lambda: on_alternar(id_u)
        ).pack(side="left", padx=(0, self.GAP_BOTOES))

        ctk.CTkButton(
            frame_acoes, text="✕", width=self.LARGURA_BTN_EXCLUIR, height=32,
            fg_color=cores.COR_PERIGO, text_color="#fff",
            font=("Segoe UI", 13, "bold"),
            command=lambda: on_excluir(id_u, nome)
        ).pack(side="left")


# ─────────────────────────────────────────────────────────────────────────────
#  Cabeçalho da tabela
# ─────────────────────────────────────────────────────────────────────────────
class CabecalhoTabela(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=cores.COR_SIDEBAR, corner_radius=0, **kw)

        for idx, (rotulo, peso, minsize, _max_chars) in enumerate(LinhaUsuario.COLUNAS):
            self.grid_columnconfigure(idx, weight=peso, minsize=minsize)
            criar_label(self, rotulo, text_color=cores.COR_TEXTO,
                        anchor="center",
                        font=("Segoe UI", 14, "bold")
                        ).grid(row=0, column=idx, sticky="ew", padx=(10, 4), pady=8)

        col_acoes = len(LinhaUsuario.COLUNAS)
        self.grid_columnconfigure(col_acoes, weight=0, minsize=LinhaUsuario.LARGURA_COL_ACOES)

        criar_label(self, "AÇÕES", text_color=cores.COR_TEXTO,
                    anchor="center",
                    font=("Segoe UI", 14, "bold")
                    ).grid(row=0, column=col_acoes, sticky="ew", padx=(4, 10), pady=8)


# ─────────────────────────────────────────────────────────────────────────────
#  Diálogo de confirmação de exclusão
# ─────────────────────────────────────────────────────────────────────────────
class DialogoConfirmacao(ctk.CTkToplevel):
    def __init__(self, master, nome, on_confirmar):
        super().__init__(master)
        self.title("Confirmar exclusão")
        self.geometry("360x170")
        self.resizable(False, False)
        self.configure(fg_color=cores.COR_BG)
        self.grab_set()

        criar_label(self, f'Excluir "{nome}" permanentemente?',
                    text_color=cores.COR_TEXTO, wraplength=320).pack(pady=(30, 6), padx=20)
        criar_label(self, "Esta ação não pode ser desfeita.",
                    text_color=cores.COR_TEXTO2, font=("", 11)).pack(pady=(0, 20))

        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack()

        ctk.CTkButton(
            frame_btns, text="Cancelar", width=130, height=36,
            fg_color=cores.COR_CARD, command=self.destroy
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            frame_btns, text="Excluir", width=130, height=36,
            fg_color=cores.COR_PERIGO,
            command=lambda: (on_confirmar(), self.destroy())
        ).pack(side="left", padx=8)


# ─────────────────────────────────────────────────────────────────────────────
#  Tela principal — CRUD de Usuários
# ─────────────────────────────────────────────────────────────────────────────
class TelaGerenciarUsuarios(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=cores.COR_BG)
        self.controller = controller
        self._linha_selecionada = None
        self._construir_ui()
        self._carregar()



    def _reconstruir_tema(self):
        """Reconstrói a tela ao trocar o tema claro/escuro."""
        if not self.winfo_exists():
            return
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=cores.COR_BG)
        self._construir_ui()
        self._carregar()

    def _ao_visitar(self):
        self._carregar()

    def _construir_ui(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=30, pady=(20, 10))

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        header_left = ctk.CTkFrame(topo, fg_color="transparent")
        header_left.pack(side="left", fill="y")

        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(180, 180))
                lbl_logo = ctk.CTkLabel(header_left, image=img_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 32, "bold")).pack(side="left")

        criar_label(header_left, "Gerenciar Usuários", font=FONTE_TITULO, text_color=cores.COR_TEXTO).pack(side="left")

        ctk.CTkButton(
            topo, text="Voltar", command=self.controller.voltar, width=130, height=45,
            fg_color=cores.COR_SIDEBAR, text_color="#FFFFFF", border_color=cores.COR_INPUT_BORDER, border_width=1,
            hover_color=cores.COR_INPUT_BG, font=("Segoe UI", 16, "bold")
        ).pack(side="right")

        linha_contador = ctk.CTkFrame(self, fg_color="transparent")
        linha_contador.pack(fill="x", padx=30, pady=(0, 4))

        self.lbl_total = criar_label(linha_contador, "", text_color=cores.COR_TEXTO2)
        self.lbl_total.pack(side="right")

        filtros = ctk.CTkFrame(self, fg_color="transparent")
        filtros.pack(fill="x", padx=30, pady=(0, 10))

        self.entry_busca = criar_entry(filtros, placeholder="Buscar por nome…", width=260, height=36)
        self.entry_busca.pack(side="left", fill="x", expand=False, padx=(0, 10))
        self.entry_busca.bind("<KeyRelease>", lambda e: self._buscar())

        ctk.CTkButton(
            filtros, text="Buscar", width=100, height=42,
            fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
            hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 16, "bold"),
            command=self._buscar
        ).pack(side="left", padx=(0, 16))

        self.combo_filtro = criar_combo(
            filtros,
            values=["Todos", "aluno", "professor", "bibliotecario"],
            width=160, height=36,
            button_color=cores.COR_AZUL_PRINCIPAL, button_hover_color=cores.COR_AZUL_HOVER
        )
        self.combo_filtro.set("Todos")
        self.combo_filtro.configure(command=lambda _: self._carregar())
        self.combo_filtro.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            filtros, text="↺ Limpar", width=100, height=42,
            fg_color=cores.COR_CARD, font=("Segoe UI", 16, "bold"),
            command=self._limpar_filtros
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            filtros, text="+ Novo Usuário", command=self._abrir_cadastro,
            width=160, height=42,
            fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
            hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 16, "bold")
        ).pack(side="left")

        CabecalhoTabela(self).pack(fill="x", padx=(30, 30 + COMPENSA_SCROLLBAR))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self.lbl_notif = criar_label(self, "", text_color=cores.COR_TEXTO2)
        self.lbl_notif.pack(pady=(0, 8))

    def _selecionar_linha(self, linha):
        if self._linha_selecionada and self._linha_selecionada != linha:
            self._linha_selecionada.desselecionar()
        self._linha_selecionada = linha
        linha.selecionar()

    def _carregar(self, usuarios=None):
        if usuarios is None:
            tipo = self.combo_filtro.get()
            tipo = None if tipo == "Todos" else tipo
            usuarios = listar_usuarios(tipo=tipo)

        turmas_map = {tid: (c, t) for tid, c, t in listar_turmas()}
        self._linha_selecionada = None

        for widget in self.scroll.winfo_children():
            widget.destroy()

        for i, u in enumerate(usuarios):
            linha = LinhaUsuario(
                self.scroll, u, i,
                on_editar=self._abrir_edicao,
                on_alternar=self._alternar_status,
                on_excluir=self._confirmar_exclusao,
                turmas_map=turmas_map,
                on_selecionar=self._selecionar_linha
            )
            linha.pack(fill="x", pady=(0, 1))

        total = len(usuarios)
        self.lbl_total.configure(
            text=f"{total} usuário{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
        )

    def _buscar(self):
        termo = self.entry_busca.get().strip()
        if not termo:
            self._carregar()
            return
        self._carregar(buscar_usuarios_por_nome(termo))

    def _limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.combo_filtro.set("Todos")
        self._carregar()

    def _abrir_cadastro(self):
        JanelaUsuario(self, on_salvo=self._carregar)

    def _abrir_edicao(self, id_usuario):
        JanelaUsuario(self, on_salvo=self._carregar, id_usuario=id_usuario)

    def _alternar_status(self, id_usuario):
        ok = alternar_status_usuario(id_usuario)
        if ok:
            self._notificar("Status alterado com sucesso.")
            self._carregar()
        else:
            self._notificar("Erro ao alterar status.")

    def _confirmar_exclusao(self, id_usuario, nome):
        def _excluir():
            ok = excluir_usuario(id_usuario)
            if ok:
                self._notificar(f'"{nome}" removido.')
                self._carregar()
            else:
                self._notificar("Não foi possível excluir (verifique empréstimos vinculados).")

        DialogoConfirmacao(self, nome, on_confirmar=_excluir)

    def _notificar(self, msg):
        self.lbl_notif.configure(text=msg)
        self.lbl_notif.bind("<Button-1>", lambda e: self.lbl_notif.configure(text=""))
        self.after(5000, lambda: self.lbl_notif.configure(text=""))