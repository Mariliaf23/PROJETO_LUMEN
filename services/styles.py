# styles.py — Estilos, cores e funções auxiliares para criar a interface do LUMEN

import customtkinter as ctk   # Biblioteca de interface gráfica moderna

ctk.set_appearance_mode("dark")              # Define o tema escuro para toda a aplicação
ctk.set_default_color_theme("dark-blue")     # Tema de cores padrão: azul escuro

# ======================== CORES ========================

COR_BG = "#0B1220"              # Cor de fundo principal (azul muito escuro)
COR_CARD = "#111827"            # Cor dos cards e painéis (cinza escuro)
COR_SIDEBAR = "#0F172A"         # Cor da barra lateral (azul marinho escuro)
COR_DOURADO = "#D4A373"         # Cor dourada (destaques e botões)
COR_DOURADO_CLARO = "#E6C79C"   # Cor dourada clara (hover)
COR_TEXTO = "#F8FAFC"           # Cor do texto principal (branco quase puro)
COR_TEXTO2 = "#94A3B8"          # Cor do texto secundário (cinza claro)
COR_INPUT_BG = "#1E293B"        # Fundo dos campos de entrada (cinza azulado)
COR_INPUT_BORDER = "#334155"    # Borda dos campos de entrada
COR_HOVER = "#E6C79C"           # Cor ao passar o mouse sobre botões
COR_ATIVO = "#1E293B"           # Cor de fundo do item ativo no menu

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
    """Cria um campo de entrada de texto com estilo padronizado."""
    defaults = dict(
        placeholder_text=placeholder,      # Texto placeholder (dica ao usuário)
        font=FONTE_INPUT,                  # Fonte do campo
        fg_color=COR_INPUT_BG,            # Cor de fundo
        border_color=COR_INPUT_BORDER,    # Cor da borda
        text_color=COR_TEXTO,             # Cor do texto digitado
        placeholder_text_color=COR_TEXTO2, # Cor do placeholder
        corner_radius=8,                  # Arredondamento dos cantos
        height=38,                        # Altura do campo
    )
    defaults.update(kwargs)                # Permite sobrescrever qualquer configuração
    return ctk.CTkEntry(parent, **defaults)  # Retorna o campo de entrada


def criar_botao(parent, text, command=None, **kwargs):
    """Cria um botão com borda dourada e efeito hover (inverter cores ao passar o mouse)."""
    defaults = dict(
        text=text,                        # Texto do botão
        font=FONTE_BOTAO,                # Fonte
        fg_color="transparent",           # Fundo transparente (só borda visível)
        border_color=COR_DOURADO,         # Borda dourada
        border_width=1,                   # Espessura da borda
        text_color=COR_DOURADO,           # Texto dourado
        corner_radius=8,                  # Cantos arredondados
        height=40,                        # Altura do botão
        command=command,                  # Função chamada ao clicar
        hover_color=COR_DOURADO,          # Cor ao passar o mouse
    )
    defaults.update(kwargs)               # Permite personalizar
    btn = ctk.CTkButton(parent, **defaults)  # Cria o botão

    # Efeito hover: inverte as cores quando o mouse entra/sai
    original_enter = btn.bind("<Enter>", lambda e: None)  # Remove binding padrão
    original_leave = btn.bind("<Leave>", lambda e: None)  # Remove binding padrão

    def on_enter(e):
        """Quando o mouse entra no botão: fundo dourado, texto escuro."""
        btn.configure(fg_color=COR_DOURADO, text_color=COR_BG)

    def on_leave(e):
        """Quando o mouse sai do botão: fundo transparente, texto dourado."""
        btn.configure(fg_color="transparent", text_color=COR_DOURADO)

    btn.bind("<Enter>", on_enter)         # Liga o evento de entrada do mouse
    btn.bind("<Leave>", on_leave)         # Liga o evento de saída do mouse

    return btn                             # Retorna o botão


def criar_botao_preenchido(parent, text, command=None, **kwargs):
    """Cria um botão com fundo dourado sólido (preenchido)."""
    defaults = dict(
        text=text,                        # Texto do botão
        font=FONTE_BOTAO,                # Fonte
        fg_color=COR_DOURADO,            # Fundo dourado
        hover_color=COR_HOVER,           # Cor ao passar o mouse
        text_color=COR_BG,               # Texto escuro (contraste com fundo dourado)
        corner_radius=8,                  # Cantos arredondados
        height=40,                        # Altura
        command=command,                  # Ação ao clicar
    )
    defaults.update(kwargs)               # Permite personalizar
    return ctk.CTkButton(parent, **defaults)  # Retorna o botão


def criar_label(parent, text, **kwargs):
    """Cria um rótulo de texto com estilo padronizado."""
    defaults = dict(
        text=text,                        # Texto do label
        font=FONTE_LABEL,                # Fonte padrão
        text_color=COR_TEXTO2,           # Cor cinza clara
    )
    defaults.update(kwargs)
    return ctk.CTkLabel(parent, **defaults)  # Retorna o label


def criar_titulo(parent, text, **kwargs):
    """Cria um título grande com cor dourada."""
    defaults = dict(
        text=text,                        # Texto do título
        font=FONTE_TITULO,               # Fonte grande e negrita
        text_color=COR_DOURADO,          # Cor dourada
    )
    defaults.update(kwargs)
    return ctk.CTkLabel(parent, **defaults)  # Retorna o label de título


def criar_card(parent, **kwargs):
    """Cria um card (painel) com fundo escuro e borda sutil."""
    defaults = dict(
        fg_color=COR_CARD,               # Fundo cinza escuro
        corner_radius=20,                # Cantos bem arredondados (moderno)
        border_width=1,                  # Borda fina
        border_color=COR_INPUT_BORDER,   # Cor da borda
    )
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)  # Retorna o frame/card


def criar_combo(parent, values=None, **kwargs):
    """Cria um menu suspenso (dropdown) com estilo padronizado."""
    defaults = dict(
        values=values or [" Selecione..."],  # Opções disponíveis
        font=FONTE_INPUT,                     # Fonte
        fg_color=COR_INPUT_BG,               # Fundo do campo
        button_color=COR_DOURADO,            # Cor do botão de abertura
        button_hover_color=COR_HOVER,         # Cor ao passar o mouse no botão
        dropdown_fg_color=COR_CARD,           # Fundo da lista suspensa
        dropdown_hover_color=COR_ATIVO,       # Cor ao passar mouse nas opções
        text_color=COR_TEXTO,                 # Cor do texto selecionado
        corner_radius=8,                      # Cantos arredondados
        height=38,                            # Altura
    )
    defaults.update(kwargs)
    return ctk.CTkOptionMenu(parent, **defaults)  # Retorna o menu suspenso


def criar_switch(parent, text, **kwargs):
    """Cria um interruptor (toggle) com estilo padronizado."""
    defaults = dict(
        text=text,                        # Texto ao lado do switch
        font=FONTE_LABEL,                # Fonte
        text_color=COR_TEXTO2,           # Cor do texto
        fg_color=COR_INPUT_BORDER,       # Cor quando desligado
        progress_color=COR_DOURADO,      # Cor quando ligado
        button_color=COR_DOURADO,        # Cor do botão deslizante
        button_hover_color=COR_HOVER,    # Cor do botão ao passar o mouse
    )
    defaults.update(kwargs)
    return ctk.CTkSwitch(parent, **defaults)  # Retorna o switch


def criar_scroll_frame(parent, **kwargs):
    """Cria um frame com barra de rolagem."""
    defaults = dict(
        fg_color=COR_CARD,               # Fundo cinza escuro
        corner_radius=12,                # Cantos arredondados
        border_width=1,                  # Borda fina
        border_color=COR_INPUT_BORDER,   # Cor da borda
    )
    defaults.update(kwargs)
    return ctk.CTkScrollableFrame(parent, **defaults)  # Retorna o frame scrollável


def criar_item_lista(parent, dados, on_click=None, **kwargs):
    """Cria uma linha de lista com várias colunas de dados."""
    frame = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=8, height=45)  # Frame da linha

    labels = []                          # Lista para guardar os labels criados
    colunas = len(dados)                 # Quantidade de colunas
    largura_col = 1.0 / colunas if colunas > 0 else 1  # Largura proporcional de cada coluna

    for i, (texto, _) in enumerate(dados):  # Para cada coluna (texto, dados extras)
        lbl = ctk.CTkLabel(
            frame, text=texto, font=FONTE_SMALL,   # Label com fonte pequena
            text_color=COR_TEXTO, anchor="w"       # Texto branco, alinhado à esquerda
        )
        # Posiciona o label na posição correta
        lbl.place(relx=i * largura_col + 0.01, rely=0.5, anchor="w", relwidth=largura_col - 0.02)
        labels.append(lbl)               # Salva o label na lista

    if on_click:                         # Se tem função de clique
        frame.bind("<Button-1>", lambda e: on_click())  # Clique no frame
        for lbl in labels:               # Para cada label
            lbl.bind("<Button-1>", lambda e: on_click())  # Clique no label também

    frame.pack(fill="x", padx=5, pady=2)  # Posiciona a linha
    return frame
