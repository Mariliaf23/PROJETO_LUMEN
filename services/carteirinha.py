import os
import uuid
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk # Keep ttk for standalone GUI

from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


# ============================================================
# CONFIGURAÇÕES
# ============================================================

LARGURA_CARTAO = 860
ALTURA_CARTAO = 540

PASTA_SAIDA = "carteirinhas"
PASTA_TEMP = "temp_carteirinhas"

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ASSETS_DIR = os.path.join(_BASE_DIR, "assets")
_LOGO_ESCOLA_PATH = os.path.join(_ASSETS_DIR, "logo_escola.png")

os.makedirs(PASTA_SAIDA, exist_ok=True)
os.makedirs(PASTA_TEMP, exist_ok=True)


# ============================================================
# GERADOR DE CÓDIGO ÚNICO
# ============================================================

def gerar_codigo_usuario():
    """
    Gera um código único para o usuário.

    Exemplo:
        BIB-7F3A91C2D4
    """

    identificador = uuid.uuid4().hex[:10].upper()

    return f"BIB-{identificador}"


# ============================================================
# GERAÇÃO DO CÓDIGO DE BARRAS
# ============================================================

def gerar_codigo_barras(codigo_usuario):
    """
    Gera um código de barras Code128.

    O valor armazenado no código de barras é o código interno
    do usuário, por exemplo:

        BIB-7F3A91C2D4
    """

    nome_arquivo = os.path.join(
        PASTA_TEMP,
        codigo_usuario
    )

    classe_barcode = barcode.get_barcode_class("code128")

    codigo = classe_barcode(
        codigo_usuario,
        writer=ImageWriter()
    )

    caminho = codigo.save(
        nome_arquivo,
        options={
            "write_text": True,
            "module_width": 0.25,
            "module_height": 15,
            "font_size": 10,
            "quiet_zone": 2,
        }
    )

    return caminho


# ============================================================
# CARREGAR FOTO
# ============================================================

# Variáveis globais para os widgets de entrada, definidas apenas quando a GUI é criada
entrada_foto = None

def selecionar_foto():
    caminho = filedialog.askopenfilename(
        title="Selecionar foto",
        filetypes=[
            ("Imagens", "*.jpg *.jpeg *.png"),
            ("Todos os arquivos", "*.*")
        ]
    )

    if caminho:
        if entrada_foto: # Verifica se o widget de entrada existe
            entrada_foto.delete(0, tk.END)
            entrada_foto.insert(0, caminho)


# ============================================================
# FONTE
# ============================================================

def obter_fonte(tamanho, negrito=False):
    """
    Tenta utilizar uma fonte comum do sistema.
    """

    fontes = []

    if os.name == "nt":
        if negrito:
            fontes = [
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/calibrib.ttf",
            ]
        else:
            fontes = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
            ]

    else:
        if negrito:
            fontes = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            ]
        else:
            fontes = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]

    for fonte in fontes:
        if os.path.exists(fonte):
            return ImageFont.truetype(fonte, tamanho)

    return ImageFont.load_default()


# ============================================================
# AJUSTAR FOTO
# ============================================================

def preparar_foto(caminho, largura, altura):
    """
    Redimensiona a foto mantendo proporção e recorta o excesso.
    """

    imagem = Image.open(caminho).convert("RGB")

    proporcao_original = imagem.width / imagem.height
    proporcao_destino = largura / altura

    if proporcao_original > proporcao_destino:
        # Imagem mais larga
        nova_altura = altura
        nova_largura = int(altura * proporcao_original)
    else:
        # Imagem mais alta
        nova_largura = largura
        nova_altura = int(largura / proporcao_original)

    imagem = imagem.resize(
        (nova_largura, nova_altura),
        Image.Resampling.LANCZOS
    )

    esquerda = (nova_largura - largura) // 2
    superior = (nova_altura - altura) // 2

    imagem = imagem.crop(
        (
            esquerda,
            superior,
            esquerda + largura,
            superior + altura
        )
    )

    return imagem


# ============================================================
# GERAR IMAGEM DA CARTEIRINHA
# ============================================================

def criar_carteirinha(
    nome,
    tipo_usuario,
    validade,
    caminho_foto,
    codigo_usuario
):
    """
    Cria a imagem da carteirinha.
    """

    cartao = Image.new(
        "RGB",
        (LARGURA_CARTAO, ALTURA_CARTAO),
        "white"
    )

    desenho = ImageDraw.Draw(cartao)

    # --------------------------------------------------------
    # Borda
    # --------------------------------------------------------

    desenho.rounded_rectangle(
        (5, 5, LARGURA_CARTAO - 5, ALTURA_CARTAO - 5),
        radius=25,
        outline="#333333",
        width=4
    )

    # --------------------------------------------------------
    # Cabeçalho
    # --------------------------------------------------------

    desenho.rounded_rectangle(
        (5, 5, LARGURA_CARTAO - 5, 105),
        radius=25,
        fill="#1F4E78"
    )

    fonte_titulo = obter_fonte(32, negrito=True)

    desenho.text(
        (40, 28),
        "CARTEIRINHA DE USUÁRIO",
        fill="white",
        font=fonte_titulo
    )

    # --------------------------------------------------------
    # Logo da Escola
    # --------------------------------------------------------
    if os.path.exists(_LOGO_ESCOLA_PATH):
        try:
            logo_escola_img = Image.open(_LOGO_ESCOLA_PATH).convert("RGBA") # Suporta transparência
            # Redimensiona a logo para uma altura maior (2x o tamanho anterior)
            logo_height = 280
            logo_width = int(logo_escola_img.width * (logo_height / logo_escola_img.height))
            logo_escola_img = logo_escola_img.resize((logo_width, logo_height), Image.LANCZOS)

            # Calcula a posição para a logo no canto superior direito, abaixo do cabeçalho
            # 20px de padding da borda direita
            logo_x = LARGURA_CARTAO - logo_width - 20
            # Centraliza a logo verticalmente ao lado da foto do usuário
            logo_y = 145 + (230 - logo_height) // 2 # y_foto + (altura_foto - altura_logo) / 2
            cartao.paste(logo_escola_img, (logo_x, logo_y), logo_escola_img) # Usa a própria imagem como máscara para transparência
        except Exception as e:
            print(f"Erro ao carregar ou colar logo da escola na carteirinha: {e}")

    # --------------------------------------------------------
    # Área da foto
    # --------------------------------------------------------

    x_foto = 45
    y_foto = 145
    largura_foto = 190
    altura_foto = 230

    desenho.rectangle(
        (
            x_foto,
            y_foto,
            x_foto + largura_foto,
            y_foto + altura_foto
        ),
        outline="#555555",
        width=3,
        fill="#EEEEEE"
    )

    if caminho_foto and os.path.exists(caminho_foto):

        foto = preparar_foto(
            caminho_foto,
            largura_foto,
            altura_foto
        )

        cartao.paste(
            foto,
            (x_foto, y_foto)
        )

        desenho.rectangle(
            (
                x_foto,
                y_foto,
                x_foto + largura_foto,
                y_foto + altura_foto
            ),
            outline="#555555",
            width=3
        )

    else:

        fonte_foto = obter_fonte(22, negrito=True)

        texto = "FOTO"

        caixa = desenho.textbbox(
            (0, 0),
            texto,
            font=fonte_foto
        )

        largura_texto = caixa[2] - caixa[0]
        altura_texto = caixa[3] - caixa[1]

        desenho.text(
            (
                x_foto + (largura_foto - largura_texto) / 2,
                y_foto + (altura_foto - altura_texto) / 2
            ),
            texto,
            fill="#777777",
            font=fonte_foto
        )

    # --------------------------------------------------------
    # Informações
    # --------------------------------------------------------

    fonte_label = obter_fonte(18, negrito=True)
    fonte_valor = obter_fonte(27, negrito=False)

    x_info = 280

    # Nome
    desenho.text(
        (x_info, 145),
        "NOME",
        fill="#555555",
        font=fonte_label
    )

    desenho.text(
        (x_info, 175),
        nome,
        fill="#111111",
        font=fonte_valor
    )

    # Tipo de usuário
    desenho.text(
        (x_info, 240),
        "TIPO DE USUÁRIO",
        fill="#555555",
        font=fonte_label
    )

    desenho.text(
        (x_info, 270),
        tipo_usuario,
        fill="#111111",
        font=fonte_valor
    )

    # Validade
    desenho.text(
        (x_info, 335),
        "VALIDADE",
        fill="#555555",
        font=fonte_label
    )

    desenho.text(
        (x_info, 365),
        validade,
        fill="#111111",
        font=fonte_valor
    )

    # --------------------------------------------------------
    # Código interno
    # --------------------------------------------------------

    fonte_codigo = obter_fonte(16)

    desenho.text(
        (45, 440),
        f"Código: {codigo_usuario}",
        fill="#555555",
        font=fonte_codigo
    )

    # --------------------------------------------------------
    # Código de barras
    # --------------------------------------------------------

    caminho_barra = gerar_codigo_barras(
        codigo_usuario
    )

    codigo_img = Image.open(
        caminho_barra
    ).convert("RGB")

    codigo_img.thumbnail(
        (470, 80),
        Image.Resampling.LANCZOS
    )

    x_barra = 345
    y_barra = 425

    cartao.paste(
        codigo_img,
        (x_barra, y_barra)
    )

    # --------------------------------------------------------
    # Rodapé
    # --------------------------------------------------------

    fonte_rodape = obter_fonte(14)

    desenho.text(
        (45, 500),
        "Documento de identificação do usuário da biblioteca",
        fill="#666666",
        font=fonte_rodape
    )

    return cartao


# ============================================================
# EXPORTAR PARA PDF
# ============================================================

def salvar_pdf(imagem, codigo_usuario):
    """
    Salva a carteirinha como PDF.
    """

    caminho_png = os.path.join(
        PASTA_SAIDA,
        f"{codigo_usuario}.png"
    )

    caminho_pdf = os.path.join(
        PASTA_SAIDA,
        f"{codigo_usuario}.pdf"
    )

    imagem.save(
        caminho_png,
        "PNG"
    )

    largura_pdf = 8.6 * 28.3465
    altura_pdf = 5.4 * 28.3465

    pdf = canvas.Canvas(
        caminho_pdf,
        pagesize=(largura_pdf, altura_pdf)
    )

    pdf.drawImage(
        ImageReader(imagem),
        0,
        0,
        width=largura_pdf,
        height=altura_pdf
    )

    pdf.save()

    return caminho_pdf


# ============================================================
# PROCESSAR CARTEIRINHA
# ============================================================

def _gerar_carteirinha_from_gui():

    nome = entrada_nome.get().strip()
    tipo_usuario = entrada_tipo.get().strip()
    validade = entrada_validade.get().strip()
    caminho_foto = entrada_foto.get().strip()

    if not nome:
        messagebox.showwarning(
            "Atenção",
            "Informe o nome do usuário."
        )
        return

    if not tipo_usuario:
        messagebox.showwarning(
            "Atenção",
            "Informe o tipo de usuário."
        )
        return

    if not validade:
        messagebox.showwarning(
            "Atenção",
            "Informe a validade da carteirinha."
        )
        return

    # Gera identificador único.
    codigo_usuario = gerar_codigo_usuario()

    try:

        imagem = criar_carteirinha(
            nome=nome,
            tipo_usuario=tipo_usuario,
            validade=validade,
            caminho_foto=caminho_foto,
            codigo_usuario=codigo_usuario
        )

        caminho_pdf = salvar_pdf(
            imagem,
            codigo_usuario
        )

        messagebox.showinfo(
            "Carteirinha gerada",
            f"Carteirinha criada com sucesso!\n\n"
            f"Código: {codigo_usuario}\n\n"
            f"Arquivo:\n{caminho_pdf}"
        )

    except Exception as erro:

        messagebox.showerror(
            "Erro",
            f"Não foi possível gerar a carteirinha.\n\n{erro}"
        )


# ============================================================
# GERAÇÃO DE CARTEIRINHAS PARA MÚLTIPLOS USUÁRIOS (SEM GUI)
# ============================================================

def gerar_imagem_carteirinha(user_data, codigo_usuario):
    """
    Gera a imagem (PIL) da carteirinha para um usuário.

    Args:
        user_data: Tupla no formato retornado por database_config.listar_usuarios:
                   (id_usuario, nome, email, telefone, cpf, tipo_usuario, matricula, id_turma, funcao, status)
        codigo_usuario: Código único (ex: BIB-7F3A91C2D4) impresso na carteirinha.

    Returns:
        PIL.Image com a carteirinha pronta.
    """
    nome = (user_data[1] or "").strip() or "SEM NOME"
    tipo_usuario = (user_data[5] or "outro").capitalize()

    caminho_foto = ""  # Não há caminho de foto nos dados de listar_usuarios
    validade = "31/12/2026"  # Validade padrão

    return criar_carteirinha(
        nome=nome,
        tipo_usuario=tipo_usuario,
        validade=validade,
        caminho_foto=caminho_foto,
        codigo_usuario=codigo_usuario
    )


def salvar_pdf_unico(imagens_codigos, nome_arquivo="todas_carteirinhas"):
    """
    Gera um único PDF (A4) com as carteirinhas dispostas 2 por página.

    Args:
        imagens_codigos: Lista de tuplas (imagem_PIL, codigo_usuario).
        nome_arquivo: Nome base do arquivo gerado em PASTA_SAIDA.

    Returns:
        Caminho do PDF gerado.
    """
    import math

    LARGURA_PDF = 595.28
    ALTURA_PDF = 841.89

    LARGURA_CARTAO_PDF = 8.6 * 28.3465
    ALTURA_CARTAO_PDF = 5.4 * 28.3465

    ESPACO = 14.17

    pdf = canvas.Canvas(
        os.path.join(PASTA_SAIDA, f"{nome_arquivo}.pdf"),
        pagesize=(LARGURA_PDF, ALTURA_PDF)
    )

    cartoes_por_pagina = 2
    total_paginas = max(1, math.ceil(len(imagens_codigos) / cartoes_por_pagina))

    altura_dupla = (2 * ALTURA_CARTAO_PDF) + ESPACO
    y_inicio = (ALTURA_PDF - altura_dupla) / 2

    for pagina in range(total_paginas):
        for posicao in range(cartoes_por_pagina):
            indice = pagina * cartoes_por_pagina + posicao
            if indice >= len(imagens_codigos):
                break

            imagem, codigo = imagens_codigos[indice]

            x = (LARGURA_PDF - LARGURA_CARTAO_PDF) / 2
            y = y_inicio + ALTURA_CARTAO_PDF
            if posicao == 1:
                y = y_inicio

            pdf.drawImage(
                ImageReader(imagem),
                x, y,
                width=LARGURA_CARTAO_PDF,
                height=ALTURA_CARTAO_PDF
            )

        pdf.showPage()

    pdf.save()
    return os.path.join(PASTA_SAIDA, f"{nome_arquivo}.pdf")


def gerar_pdf_carteirinhas(usuarios_data):
    """
    Gera carteirinhas em PDF para uma lista de usuários (um PDF por usuário).
    Esta função é destinada a ser usada por outros módulos (ex: tela de gerenciar usuários)
    e não inicia a interface gráfica.

    Args:
        usuarios_data: Lista de tuplas/dicts com dados do usuário.
                       Assume o formato retornado por database_config.listar_usuarios:
                       (id_usuario, nome, email, telefone, cpf, tipo_usuario, matricula, id_turma, funcao, status)

    Returns:
        Lista de caminhos para os PDFs gerados.
    """
    caminhos_gerados = []
    for user_data in usuarios_data:
        try:
            codigo_usuario = gerar_codigo_usuario()  # Gera um código único para cada usuário
            imagem = gerar_imagem_carteirinha(user_data, codigo_usuario)
            caminho_pdf = salvar_pdf(imagem, codigo_usuario)
            caminhos_gerados.append(caminho_pdf)
        except Exception as e:
            print(f"Erro ao gerar carteirinha para {user_data[1]}: {e}")
            # Em um sistema real, você pode querer registrar este erro ou notificar o usuário.
    return caminhos_gerados


# ============================================================
# INTERFACE
# ============================================================

def _run_standalone_gui():
    """
    Cria e executa a interface gráfica para geração de carteirinhas.
    Esta função só é chamada quando o script carteirinha.py é executado diretamente.
    """
    global entrada_nome, entrada_tipo, entrada_validade, entrada_foto

    janela = tk.Tk()
    janela.title("Carteirinha de Usuário - Biblioteca")
    janela.geometry("650x500")
    janela.resizable(False, False)

    frame = ttk.Frame(janela, padding=25)
    frame.pack(fill="both", expand=True)

    # ------------------------------------------------------------
    # Nome
    # ------------------------------------------------------------
    ttk.Label(frame, text="Nome do usuário:").pack(anchor="w")
    entrada_nome = ttk.Entry(frame, width=70)
    entrada_nome.pack(fill="x", pady=(5, 15))

    # ------------------------------------------------------------
    # Tipo de usuário
    # ------------------------------------------------------------
    ttk.Label(frame, text="Tipo de usuário:").pack(anchor="w")
    entrada_tipo = ttk.Combobox(frame, values=["Aluno", "Professor", "Servidor", "Comunidade", "Pesquisador", "Outro"], state="normal")
    entrada_tipo.pack(fill="x", pady=(5, 15))

    # ------------------------------------------------------------
    # Validade
    # ------------------------------------------------------------
    ttk.Label(frame, text="Validade:").pack(anchor="w")
    entrada_validade = ttk.Entry(frame, width=70)
    entrada_validade.insert(0, "31/12/2026")
    entrada_validade.pack(fill="x", pady=(5, 15))

    # ------------------------------------------------------------
    # Foto
    # ------------------------------------------------------------
    ttk.Label(frame, text="Foto:").pack(anchor="w")
    frame_foto = ttk.Frame(frame)
    frame_foto.pack(fill="x", pady=(5, 20))
    entrada_foto = ttk.Entry(frame_foto)
    entrada_foto.pack(side="left", fill="x", expand=True)
    ttk.Button(frame_foto, text="Selecionar foto", command=selecionar_foto).pack(side="left", padx=(10, 0))

    # ------------------------------------------------------------
    # Botão
    # ------------------------------------------------------------
    ttk.Button(frame, text="GERAR CARTEIRINHA", command=_gerar_carteirinha_from_gui).pack(pady=25, ipadx=30, ipady=10)

    # ------------------------------------------------------------
    # Informações
    # ------------------------------------------------------------
    ttk.Label(frame, text=("A carteirinha não possui matrícula.\nUm código único será gerado automaticamente " "e transformado em código de barras."), justify="center").pack(pady=10)

    janela.mainloop()

# ============================================================
# INICIAR
# ============================================================

if __name__ == '__main__':
    _run_standalone_gui()
