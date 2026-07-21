# styles.py — Estilos, cores e funções auxiliares para criar a interface do LUMEN

import customtkinter as ctk   # Biblioteca de interface gráfica moderna

COR_ERRO   = "#EF4444"   # borda vermelha de erro (não muda com tema)
COR_OK     = "#10B981"   # borda verde de sucesso (não muda com tema)


class _Cores:
    """Paletas de cores dinâmicas — alterna entre claro e escuro."""
    DARK = {
        "COR_BG"           : "#0B1220",
        "COR_CARD"         : "#1A1F2E",
        "COR_SIDEBAR"      : "#0F172A",
        "COR_DOURADO"      : "#D4A373",
        "COR_DOURADO_CLARO": "#E6C79C",
        "COR_TEXTO"        : "#FFFFFF",
        "COR_TEXTO2"       : "#CBD5E1",
        "COR_INPUT_BG"     : "#1A2235",
        "COR_INPUT_BORDER" : "#506070",
        "COR_HOVER"        : "#E6C79C",
        "COR_ATIVO"        : "#2B5CD4",
        "COR_AZUL_PRINCIPAL": "#2B5CD4",
        "COR_AZUL_HOVER"   : "#4B7BFF",
        "COR_SEL"          : "#4B7BFF",
        "COR_SUCESSO"      : "#10B981",
        "COR_AVISO"        : "#EAB308",
        "COR_PERIGO"       : "#EF4444",
        "COR_LINHA_PAR"    : "#1e1e2e",
        "COR_LINHA_IMPAR"  : "#16161f",
    }
    LIGHT = {
        "COR_BG"           : "#F5F7FA",
        "COR_CARD"         : "#FFFFFF",
        "COR_SIDEBAR"      : "#E2E8F0",
        "COR_DOURADO"      : "#8B6B00",
        "COR_DOURADO_CLARO": "#D4A373",
        "COR_TEXTO"        : "#0F172A",
        "COR_TEXTO2"       : "#1E293B",
        "COR_INPUT_BG"     : "#F1F5F9",
        "COR_INPUT_BORDER" : "#94A3B8",
        "COR_HOVER"        : "#D4A373",
        "COR_ATIVO"        : "#1D4ED8",
        "COR_AZUL_PRINCIPAL": "#1D4ED8",
        "COR_AZUL_HOVER"   : "#3B82F6",
        "COR_SEL"          : "#3B82F6",
        "COR_SUCESSO"      : "#059669",
        "COR_AVISO"        : "#A16207",
        "COR_PERIGO"       : "#DC2626",
        "COR_LINHA_PAR"    : "#F8FAFC",
        "COR_LINHA_IMPAR"  : "#F1F5F9",
    }

    def __init__(self):
        self._modo = "dark"
        self._paleta = dict(self.DARK)  # cópia inicial
        self._listeners = []            # callbacks registrados pelas telas abertas

    # ---------------- Observer de tema ----------------

    def registrar_listener(self, callback):
        """Registra uma função para ser chamada sempre que o tema mudar.

        Cada tela deve chamar isto no __init__, passando um método que
        reconstrói (ou reestiliza) seus widgets, ex: self._reconstruir_ui.
        """
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remover_listener(self, callback):
        """Remove um listener. Deve ser chamado quando a tela é destruída,
        para evitar chamadas em widgets que não existem mais."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notificar_listeners(self):
        # Itera sobre uma cópia da lista, pois callbacks podem se
        # registrar/remover durante a notificação.
        for callback in list(self._listeners):
            try:
                callback()
            except Exception as e:
                print(f"[styles] Erro ao notificar listener de tema: {e}")

    # ---------------------------------------------------

    def alternar(self):
        """Alterna entre claro e escuro, notifica todas as telas registradas
        e retorna o novo modo."""
        self._modo = "light" if self._modo == "dark" else "dark"
        self._paleta.clear()
        self._paleta.update(self.LIGHT if self._modo == "light" else self.DARK)
        ctk.set_appearance_mode(self._modo)
        self._notificar_listeners()
        return self._modo

    @property
    def modo(self):
        return self._modo

    def __getattr__(self, nome):
        if nome.startswith("_"):
            raise AttributeError(nome)
        return self._paleta.get(nome, "")


cores = _Cores()  # instância única — importe como: from services.styles import cores


def aplicar_validacao_focusout(entry, fn_validar, lbl_erro_global, todos_entries):
    entry._tocado = False
    entry._validacao_ativa = False  # bloqueia até janela estar pronta

    def _ao_sair(event=None):
        if not entry._tocado or not entry._validacao_ativa:
            return
        valor = entry.get().strip()
        if not valor:
            entry.configure(border_color=cores.COR_INPUT_BORDER)
            lbl_erro_global.configure(text="")
            return
        ok, msg = fn_validar(valor)
        entry.configure(border_color=COR_OK if ok else COR_ERRO)
        lbl_erro_global.configure(text="" if ok else msg, text_color=COR_ERRO)

    def _ao_entrar(event=None):
        entry._tocado = True
        entry._validacao_ativa = True
        for e in todos_entries:
            e.configure(border_color=cores.COR_INPUT_BORDER)
        lbl_erro_global.configure(text="")

    entry.bind("<FocusOut>", lambda e: _ao_sair())
    entry.bind("<FocusIn>",  lambda e: _ao_entrar())

ctk.set_appearance_mode("dark")              # Define o tema escuro para toda a aplicação
ctk.set_default_color_theme("dark-blue")     # Tema de cores padrão: azul escuro

# ======================== FONTES ========================

FONTE_TITULO = ("Cinzel", 26, "bold")               # Fonte para títulos grandes
FONTE_SUBTITULO = ("Segoe UI Light", 13)             # Fonte para subtítulos
FONTE_LABEL = ("Segoe UI", 11)                       # Fonte para labels (textos descritivos)
FONTE_INPUT = ("Segoe UI", 12)                       # Fonte para campos de entrada
FONTE_BOTAO = ("Segoe UI Semibold", 12)              # Fonte para botões
FONTE_BOTAO_PEQUENO = ("Segoe UI Semibold", 11)      # Fonte para botões pequenos
FONTE_NAV = ("Segoe UI", 11)                         # Fonte para navegação
FONTE_SMALL = ("Segoe UI", 10)                       # Fonte para textos pequenos


# ======================== FUNÇÕES AUXILIARES ========================

def criar_entry(parent, placeholder="", **kwargs):
    defaults = dict(
        placeholder_text=placeholder,
        font=FONTE_INPUT,
        fg_color=cores.COR_INPUT_BG,
        border_color=cores.COR_INPUT_BORDER,
        text_color=cores.COR_TEXTO,
        placeholder_text_color=cores.COR_TEXTO2,
        corner_radius=8,
        height=38,
    )
    defaults.update(kwargs)
    return ctk.CTkEntry(parent, **defaults)


def criar_botao(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text, font=FONTE_BOTAO,
        fg_color="transparent",
        border_color=cores.COR_DOURADO,
        border_width=1,
        text_color=cores.COR_DOURADO,
        corner_radius=8, height=40,
        command=command,
        hover_color=cores.COR_DOURADO,
    )
    defaults.update(kwargs)
    btn = ctk.CTkButton(parent, **defaults)

    def on_enter(e):
        btn.configure(fg_color=cores.COR_DOURADO, text_color=cores.COR_BG)

    def on_leave(e):
        btn.configure(fg_color="transparent", text_color=cores.COR_DOURADO)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def criar_botao_preenchido(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text, font=FONTE_BOTAO,
        fg_color=cores.COR_DOURADO,
        hover_color=cores.COR_HOVER,
        text_color=cores.COR_BG,
        corner_radius=8, height=40,
        command=command,
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def criar_label(parent, text, **kwargs):
    defaults = dict(
        text=text, font=FONTE_LABEL,
        text_color=cores.COR_TEXTO2,
    )
    defaults.update(kwargs)
    return ctk.CTkLabel(parent, **defaults)


def criar_titulo(parent, text, **kwargs):
    defaults = dict(
        text=text, font=FONTE_TITULO,
        text_color=cores.COR_DOURADO,
    )
    defaults.update(kwargs)
    return ctk.CTkLabel(parent, **defaults)


def criar_card(parent, **kwargs):
    defaults = dict(
        fg_color=cores.COR_CARD,
        corner_radius=20,
        border_width=1,
        border_color=cores.COR_INPUT_BORDER,
    )
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def criar_combo(parent, values=None, **kwargs):
    defaults = dict(
        values=values or [" Selecione..."],
        font=FONTE_INPUT,
        fg_color=cores.COR_INPUT_BG,
        button_color=cores.COR_AZUL_PRINCIPAL,
        button_hover_color=cores.COR_AZUL_HOVER,
        dropdown_fg_color=cores.COR_CARD,
        dropdown_hover_color=cores.COR_ATIVO,
        text_color=cores.COR_TEXTO,
        corner_radius=8, height=38,
    )
    defaults.update(kwargs)
    return ctk.CTkOptionMenu(parent, **defaults)


def criar_scroll_frame(parent, **kwargs):
    defaults = dict(
        fg_color=cores.COR_CARD,
        corner_radius=12,
        border_width=1,
        border_color=cores.COR_INPUT_BORDER,
    )
    defaults.update(kwargs)
    return ctk.CTkScrollableFrame(parent, **defaults)


def criar_botao_primario(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text, font=FONTE_BOTAO,
        fg_color=cores.COR_AZUL_PRINCIPAL,
        hover_color=cores.COR_AZUL_HOVER,
        text_color="#FFFFFF", corner_radius=8, height=38,
        command=command,
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def criar_botao_secundario(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text, font=FONTE_BOTAO,
        fg_color=cores.COR_SIDEBAR, text_color=cores.COR_TEXTO,
        border_color=cores.COR_INPUT_BORDER, border_width=1,
        hover_color=cores.COR_ATIVO, corner_radius=8, height=38,
        command=command,
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def criar_botao_perigo(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text, font=FONTE_BOTAO,
        fg_color="#7F1D1D", text_color="#FCA5A5",
        hover_color="#991B1B", corner_radius=8, height=38,
        command=command,
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)