import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

COR_BG = "#0B1220"
COR_CARD = "#111827"
COR_SIDEBAR = "#0F172A"
COR_DOURADO = "#D4A373"
COR_DOURADO_CLARO = "#E6C79C"
COR_TEXTO = "#F8FAFC"
COR_TEXTO2 = "#94A3B8"
COR_INPUT_BG = "#1E293B"
COR_INPUT_BORDER = "#334155"
COR_HOVER = "#E6C79C"
COR_ATIVO = "#1E293B"

FONTE_TITULO = ("Cinzel", 26, "bold")
FONTE_SUBTITULO = ("Segoe UI Light", 13)
FONTE_LABEL = ("Segoe UI", 11)
FONTE_INPUT = ("Segoe UI", 12)
FONTE_BOTAO = ("Segoe UI Semibold", 12)
FONTE_BOTAO_PEQUENO = ("Segoe UI Semibold", 11)
FONTE_NAV = ("Segoe UI", 11)
FONTE_SMALL = ("Segoe UI", 10)


def criar_entry(parent, placeholder="", **kwargs):
    defaults = dict(
        placeholder_text=placeholder,
        font=FONTE_INPUT,
        fg_color=COR_INPUT_BG,
        border_color=COR_INPUT_BORDER,
        text_color=COR_TEXTO,
        placeholder_text_color=COR_TEXTO2,
        corner_radius=8,
        height=38,
    )
    defaults.update(kwargs)
    return ctk.CTkEntry(parent, **defaults)


def criar_botao(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text,
        font=FONTE_BOTAO,
        fg_color="transparent",
        border_color=COR_DOURADO,
        border_width=1,
        text_color=COR_DOURADO,
        corner_radius=8,
        height=40,
        command=command,
        hover_color=COR_DOURADO,
    )
    defaults.update(kwargs)

    btn = ctk.CTkButton(parent, **defaults)

    original_enter = btn.bind("<Enter>", lambda e: None)
    original_leave = btn.bind("<Leave>", lambda e: None)

    def on_enter(e):
        btn.configure(fg_color=COR_DOURADO, text_color=COR_BG)

    def on_leave(e):
        btn.configure(fg_color="transparent", text_color=COR_DOURADO)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn


def criar_botao_preenchido(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text,
        font=FONTE_BOTAO,
        fg_color=COR_DOURADO,
        hover_color=COR_HOVER,
        text_color=COR_BG,
        corner_radius=8,
        height=40,
        command=command,
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def criar_label(parent, text, **kwargs):
    defaults = dict(
        text=text,
        font=FONTE_LABEL,
        text_color=COR_TEXTO2,
    )
    defaults.update(kwargs)
    return ctk.CTkLabel(parent, **defaults)


def criar_titulo(parent, text, **kwargs):
    defaults = dict(
        text=text,
        font=FONTE_TITULO,
        text_color=COR_DOURADO,
    )
    defaults.update(kwargs)
    return ctk.CTkLabel(parent, **defaults)


def criar_card(parent, **kwargs):
    defaults = dict(
        fg_color=COR_CARD,
        corner_radius=20,      # mais moderno
        border_width=1,
        border_color=COR_INPUT_BORDER,
    )
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def criar_combo(parent, values=None, **kwargs):
    defaults = dict(
        values=values or [],
        font=FONTE_INPUT,
        fg_color=COR_INPUT_BG,
        button_color=COR_DOURADO,
        button_hover_color=COR_HOVER,
        dropdown_fg_color=COR_CARD,
        dropdown_hover_color=COR_ATIVO,
        text_color=COR_TEXTO,
        corner_radius=8,
        height=38,
    )
    defaults.update(kwargs)
    return ctk.CTkOptionMenu(parent, **defaults)


def criar_switch(parent, text, **kwargs):
    defaults = dict(
        text=text,
        font=FONTE_LABEL,
        text_color=COR_TEXTO2,
        fg_color=COR_INPUT_BORDER,
        progress_color=COR_DOURADO,
        button_color=COR_DOURADO,
        button_hover_color=COR_HOVER,
    )
    defaults.update(kwargs)
    return ctk.CTkSwitch(parent, **defaults)


def criar_scroll_frame(parent, **kwargs):
    defaults = dict(
        fg_color=COR_CARD,
        corner_radius=12,
        border_width=1,
        border_color=COR_INPUT_BORDER,
    )
    defaults.update(kwargs)
    return ctk.CTkScrollableFrame(parent, **defaults)


def criar_item_lista(parent, dados, on_click=None, **kwargs):
    frame = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=8, height=45)

    labels = []
    colunas = len(dados)
    largura_col = 1.0 / colunas if colunas > 0 else 1

    for i, (texto, _) in enumerate(dados):
        lbl = ctk.CTkLabel(
            frame, text=texto, font=FONTE_SMALL,
            text_color=COR_TEXTO, anchor="w"
        )
        lbl.place(relx=i * largura_col + 0.01, rely=0.5, anchor="w", relwidth=largura_col - 0.02)
        labels.append(lbl)

    if on_click:
        frame.bind("<Button-1>", lambda e: on_click())
        for lbl in labels:
            lbl.bind("<Button-1>", lambda e: on_click())

    frame.pack(fill="x", padx=5, pady=2)
    return frame
