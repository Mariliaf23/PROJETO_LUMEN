import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import (
    listar_usuarios, buscar_usuario_por_id, atualizar_usuario,
    atualizar_senha_usuario, alternar_status_usuario, excluir_usuario,
    buscar_usuarios_por_nome, cadastrar_usuario
)
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_INPUT_BORDER, FONTE_TITULO, FONTE_SUBTITULO,
    criar_entry, criar_botao_preenchido, criar_botao, criar_label, criar_titulo, criar_combo
)


# ─────────────────────────────────────────────────────────────────────────────
#  Paleta auxiliar (adapte se já tiver constantes no styles.py)
# ─────────────────────────────────────────────────────────────────────────────
COR_LINHA_PAR   = "#1e1e2e"
COR_LINHA_IMPAR = "#16161f"
COR_PERIGO      = "#c0392b"
COR_SUCESSO     = "#27ae60"
COR_AVISO       = "#d4a017"


# ─────────────────────────────────────────────────────────────────────────────
#  Janela de edição / cadastro (reutilizável)
# ─────────────────────────────────────────────────────────────────────────────
class JanelaUsuario(ctk.CTkToplevel):
    """Abre um formulário para criar ou editar um usuário."""

    def __init__(self, master, on_salvo, id_usuario=None):
        super().__init__(master)
        self.on_salvo   = on_salvo
        self.id_usuario = id_usuario
        self.title("Editar Usuário" if id_usuario else "Novo Usuário")
        self.geometry("420x640")
        self.resizable(False, False)
        self.configure(fg_color=COR_BG)
        self.grab_set()
        self._construir()
        if id_usuario:
            self._carregar(id_usuario)

    # ── UI ──────────────────────────────────────────────────────────────────
    def _construir(self):
        pad = {"padx": 30}
        criar_titulo(self, "LUMEN", font=FONTE_TITULO).pack(pady=(20, 4), **pad)

        titulo = "Editar Usuário" if self.id_usuario else "Novo Usuário"
        criar_label(self, titulo, font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(pady=(0, 16), **pad)

        self.combo_tipo = criar_combo(
            self, values=["aluno", "professor", "bibliotecario"], width=340, height=40
        )
        self.combo_tipo.set("aluno")
        self.combo_tipo.configure(command=self._tipo_mudou)
        self.combo_tipo.pack(pady=(0, 10), **pad)

        self.combo_status = criar_combo(
            self, values=["ativo", "inativo"], width=340, height=40
        )
        self.combo_status.set("ativo")
        self.combo_status.pack(pady=(0, 10), **pad)

        self.entry_nome    = criar_entry(self, placeholder="Nome completo",      width=340, height=40)
        self.entry_contato = criar_entry(self, placeholder="Email ou celular",   width=340, height=40)

        self.frame_senha = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_senha = criar_entry(self.frame_senha, placeholder="Senha (obrigatorio)", width=340, height=40, show="*")
        self.entry_senha.pack()

        for w in (self.entry_nome, self.entry_contato):
            w.pack(pady=(0, 8), **pad)

        self.frame_aluno_prof = ctk.CTkFrame(self, fg_color="transparent")

        self.entry_sala  = criar_entry(self.frame_aluno_prof, placeholder="Turma",  width=160, height=40)
        self.entry_sala.pack(side="left", padx=(0, 8))
        self.entry_turma = criar_entry(self.frame_aluno_prof, placeholder="Turno", width=160, height=40)
        self.entry_turma.pack(side="left")

        self.frame_func = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_funcao = criar_entry(self.frame_func, placeholder="Função (ex: diretor)", width=340, height=40)
        self.entry_funcao.pack()

        self._tipo_mudou("aluno")

        criar_botao_preenchido(self, text="Salvar", command=self._salvar,
                               width=340, height=42).pack(pady=(14, 6), **pad)

        self.lbl_notif = criar_label(self, "", text_color=COR_TEXTO2)
        self.lbl_notif.pack()

    # ── lógica de tipo ───────────────────────────────────────────────────────
    def _tipo_mudou(self, tipo):
        self.frame_senha.pack_forget()
        self.frame_aluno_prof.pack_forget()
        self.frame_func.pack_forget()
        if tipo in ("aluno", "professor"):
            self.frame_aluno_prof.pack(pady=(0, 6), padx=30)
        elif tipo == "bibliotecario":
            self.frame_senha.pack(pady=(0, 8), padx=30)
            self.frame_func.pack(pady=(0, 6), padx=30)

    # ── preencher campos ao editar ───────────────────────────────────────────
    def _carregar(self, id_usuario):
        dados = buscar_usuario_por_id(id_usuario)
        if not dados:
            return
        _, nome, email, telefone, cpf, tipo, matricula, sala, turno, funcao, status = dados

        self.combo_tipo.set(tipo or "aluno")
        self.combo_status.set(status or "ativo")
        self._tipo_mudou(tipo or "aluno")

        def _set(entry, valor):
            entry.delete(0, "end")
            entry.insert(0, valor or "")

        _set(self.entry_nome,    nome)
        _set(self.entry_contato, email)
        _set(self.entry_sala,    sala)
        _set(self.entry_turma,   turno)
        _set(self.entry_funcao,  funcao)

    # ── salvar ───────────────────────────────────────────────────────────────
    def _salvar(self):
        nome    = self.entry_nome.get().strip()
        contato = self.entry_contato.get().strip()
        senha   = self.entry_senha.get().strip()
        tipo    = self.combo_tipo.get()
        status  = self.combo_status.get()

        sala   = self.entry_sala.get().strip()   if tipo in ("aluno", "professor") else ""
        turma  = self.entry_turma.get().strip()  if tipo in ("aluno", "professor") else ""
        funcao = self.entry_funcao.get().strip() if tipo == "bibliotecario" else ""

        if not nome:
            return self._notificar("Informe o nome.")
        if not contato:
            return self._notificar("Informe o email ou celular.")
        if tipo == "bibliotecario" and not senha:
            return self._notificar("Senha e obrigatoria para bibliotecario.")

        if self.id_usuario:
            ok = atualizar_usuario(
                self.id_usuario, nome, contato, '', '',
                tipo, '', sala, turma, funcao, status
            )
            if ok and senha:
                atualizar_senha_usuario(self.id_usuario, senha)
            msg_ok = "Usuario atualizado!"
        else:
            ok = cadastrar_usuario(nome, contato, senha or '', '', '',
                                   tipo, '', sala, turma, funcao)
            msg_ok = "Usuario cadastrado!"

        if ok:
            self._notificar(msg_ok)
            self.after(1000, lambda: (self.on_salvo(), self.destroy()))
        else:
            self._notificar("Erro ao salvar (e-mail/CPF duplicado?).")

    def _notificar(self, msg):
        self.lbl_notif.configure(text=msg)
        self.after(3000, lambda: self.lbl_notif.configure(text=""))


# ─────────────────────────────────────────────────────────────────────────────
#  Linha da tabela
# ─────────────────────────────────────────────────────────────────────────────
class LinhaUsuario(ctk.CTkFrame):
    COLUNAS = [
        ("ID",     40),
        ("Nome",  200),
        ("Contato",200),
        ("Tipo",   90),
        ("Status", 70),
        ("Acoes",  160),
    ]

    def __init__(self, master, dados, indice, on_editar, on_alternar, on_excluir, **kw):
        cor = COR_LINHA_PAR if indice % 2 == 0 else COR_LINHA_IMPAR
        super().__init__(master, fg_color=cor, corner_radius=0, **kw)

        id_u, nome, email, *_, tipo, _m, _s, _t, _f, status = dados

        valores = [str(id_u), nome, email, tipo, status]
        larguras = [c[1] for c in self.COLUNAS[:-1]]

        for val, larg in zip(valores, larguras):
            cor_val = COR_SUCESSO if val == "ativo" else (COR_PERIGO if val == "inativo" else COR_TEXTO)
            criar_label(self, val, text_color=cor_val, width=larg, anchor="w").pack(
                side="left", padx=(6, 0)
            )

        # Ações
        frame_acoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_acoes.pack(side="left", padx=8)

        ctk.CTkButton(
            frame_acoes, text="Editar", width=60, height=28,
            fg_color=COR_DOURADO, text_color="#000",
            command=lambda: on_editar(id_u)
        ).pack(side="left", padx=(0, 4))

        label_status = "Ativar" if status == "inativo" else "Desativar"
        cor_status   = COR_SUCESSO if status == "inativo" else COR_AVISO
        ctk.CTkButton(
            frame_acoes, text=label_status, width=72, height=28,
            fg_color=cor_status, text_color="#fff",
            command=lambda: on_alternar(id_u)
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            frame_acoes, text="✕", width=28, height=28,
            fg_color=COR_PERIGO, text_color="#fff",
            command=lambda: on_excluir(id_u, nome)
        ).pack(side="left")


# ─────────────────────────────────────────────────────────────────────────────
#  Cabeçalho da tabela
# ─────────────────────────────────────────────────────────────────────────────
class CabecalhoTabela(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color="#0d0d1a", corner_radius=0, **kw)
        for rotulo, largura in LinhaUsuario.COLUNAS:
            criar_label(self, rotulo, text_color=COR_DOURADO,
                        width=largura, anchor="w",
                        font=(FONTE_SUBTITULO[0], FONTE_SUBTITULO[1], "bold")
                        ).pack(side="left", padx=(6, 0))


# ─────────────────────────────────────────────────────────────────────────────
#  Diálogo de confirmação de exclusão
# ─────────────────────────────────────────────────────────────────────────────
class DialogoConfirmacao(ctk.CTkToplevel):
    def __init__(self, master, nome, on_confirmar):
        super().__init__(master)
        self.title("Confirmar exclusão")
        self.geometry("360x170")
        self.resizable(False, False)
        self.configure(fg_color=COR_BG)
        self.grab_set()

        criar_label(self, f'Excluir "{nome}" permanentemente?',
                    text_color=COR_TEXTO, wraplength=320).pack(pady=(30, 6), padx=20)
        criar_label(self, "Esta ação não pode ser desfeita.",
                    text_color=COR_TEXTO2, font=("", 11)).pack(pady=(0, 20))

        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack()

        ctk.CTkButton(
            frame_btns, text="Cancelar", width=130, height=36,
            fg_color="#333", command=self.destroy
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            frame_btns, text="Excluir", width=130, height=36,
            fg_color=COR_PERIGO,
            command=lambda: (on_confirmar(), self.destroy())
        ).pack(side="left", padx=8)


# ─────────────────────────────────────────────────────────────────────────────
#  Tela principal — CRUD de Usuários
# ─────────────────────────────────────────────────────────────────────────────
class TelaGerenciarUsuarios(ctk.CTkFrame):
    """
    Tela completa de gerenciamento de usuários.
    Integra: listagem, busca, filtro por tipo, cadastro, edição,
             ativar/desativar e exclusão permanente.
    """

    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller
        self._construir_ui()
        self._carregar()

    def _ao_visitar(self):
        self._carregar()

    # ── construção da UI ──────────────────────────────────────────────────────
    def _construir_ui(self):
        # ── Cabeçalho ──
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

        criar_label(header_left, "Gerenciar Usuários", font=FONTE_TITULO, text_color=COR_TEXTO).pack(side="left")

        criar_botao_preenchido(
            topo, text="+ Novo Usuário", command=self._abrir_cadastro,
            width=150, height=36
        ).pack(side="right")

        # ── Filtros ──
        filtros = ctk.CTkFrame(self, fg_color="transparent")
        filtros.pack(fill="x", padx=30, pady=(0, 10))

        self.entry_busca = criar_entry(filtros, placeholder="Buscar por nome…", width=260, height=36)
        self.entry_busca.pack(side="left", padx=(0, 10))
        self.entry_busca.bind("<Return>", lambda e: self._buscar())

        ctk.CTkButton(
            filtros, text="Buscar", width=80, height=36,
            fg_color=COR_DOURADO, text_color="#000",
            command=self._buscar
        ).pack(side="left", padx=(0, 16))

        self.combo_filtro = criar_combo(
            filtros,
            values=["Todos", "aluno", "professor", "bibliotecario"],
            width=160, height=36
        )
        self.combo_filtro.set("Todos")
        self.combo_filtro.configure(command=lambda _: self._carregar())
        self.combo_filtro.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            filtros, text="↺ Limpar", width=80, height=36,
            fg_color="#333",
            command=self._limpar_filtros
        ).pack(side="left")

        self.lbl_total = criar_label(filtros, "", text_color=COR_TEXTO2)
        self.lbl_total.pack(side="right")

        # ── Tabela (scroll) ──
        CabecalhoTabela(self).pack(fill="x", padx=30)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        rodape = ctk.CTkFrame(self, fg_color="transparent")
        rodape.pack(pady=(0, 10), padx=30)

        if self.controller:
            btn_voltar = ctk.CTkButton(
                rodape, text="Voltar", command=self.controller.voltar, width=130, height=45,
                fg_color="#0F172A", text_color="#FFFFFF", border_color=COR_INPUT_BORDER, border_width=1,
                hover_color="#1E293B", font=("Segoe UI", 16, "bold")
            )
            btn_voltar.pack()

        self.lbl_notif = criar_label(self, "", text_color=COR_TEXTO2)
        self.lbl_notif.pack(pady=(0, 8))

    # ── dados ─────────────────────────────────────────────────────────────────
    def _carregar(self, usuarios=None):
        """Renderiza a lista. Se `usuarios` for None, consulta o banco."""
        if usuarios is None:
            tipo = self.combo_filtro.get()
            tipo = None if tipo == "Todos" else tipo
            usuarios = listar_usuarios(tipo=tipo)

        # Limpa linhas anteriores
        for widget in self.scroll.winfo_children():
            widget.destroy()

        for i, u in enumerate(usuarios):
            LinhaUsuario(
                self.scroll, u, i,
                on_editar=self._abrir_edicao,
                on_alternar=self._alternar_status,
                on_excluir=self._confirmar_exclusao
            ).pack(fill="x", pady=(0, 1))

        total = len(usuarios)
        self.lbl_total.configure(
            text=f"{total} usuário{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
        )

    def _buscar(self):
        termo = self.entry_busca.get().strip()
        if not termo:
            self._carregar()
            return
        resultado = buscar_usuarios_por_nome(termo)
        self._carregar(resultado)

    def _limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.combo_filtro.set("Todos")
        self._carregar()

    # ── ações ─────────────────────────────────────────────────────────────────
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
        self.after(3000, lambda: self.lbl_notif.configure(text=""))
