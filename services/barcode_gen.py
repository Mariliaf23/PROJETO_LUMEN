# barcode_gen.py — Geração de código de barras Code 128 para patrimônio

import os
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from fpdf import FPDF


def _criar_barcode_sem_texto(patrimonio, pasta_destino):
    """
    Gera barcode SEM texto abaixo.
    Retorna o caminho da imagem gerada.
    """
    # Configurações para remover o texto
    options = {
        'module_width': 0.3,
        'module_height': 15,
        'quiet_zone': 6.5,
        'font_size': 0,
        'text_distance': 0,
        'write_text': False,
    }

    writer = ImageWriter()
    code128 = barcode.get('code128', patrimonio, writer=writer)

    caminho_temp = os.path.join(pasta_destino, f"_temp_{patrimonio}")
    # Passa as opções no momento do save
    code128.save(caminho_temp, options)

    # Encontra o arquivo gerado
    for ext in ['.png', '.jpg', '.gif', '']:
        if os.path.exists(caminho_temp + ext):
            return caminho_temp + ext
    return None


def _obter_fonte(tamanho=16):
    """Tenta carregar uma fonte TrueType, senão usa a padrão."""
    fontes_tentativas = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/verdana.ttf",
        "arial.ttf",
        "Arial.ttf",
    ]
    for fonte in fontes_tentativas:
        try:
            return ImageFont.truetype(fonte, tamanho)
        except:
            continue
    return ImageFont.load_default()


def gerar_codigo_barras(patrimonio, titulo_livro=None, pasta_destino=None, forcar=False):
    """
    Gera imagem de código de barras Code 128 com título do livro acima.
    """
    try:
        if pasta_destino is None:
            caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pasta_destino = os.path.join(caminho_base, "assets", "barcodes")

        os.makedirs(pasta_destino, exist_ok=True)

        caminho_final = os.path.join(pasta_destino, f"{patrimonio}.png")

        if os.path.exists(caminho_final) and not forcar:
            return caminho_final

        # Gera barcode SEM texto
        caminho_barcode = _criar_barcode_sem_texto(patrimonio, pasta_destino)

        if not caminho_barcode or not os.path.exists(caminho_barcode):
            return None

        img_barcode = Image.open(caminho_barcode)

        # Adiciona título e patrimônio na imagem
        largura = max(img_barcode.width, 300)
        altura_titulo = 50 if titulo_livro else 10
        margem = 20
        nova_altura = altura_titulo + img_barcode.height + margem

        img_final = Image.new('RGB', (largura, nova_altura), 'white')
        draw = ImageDraw.Draw(img_final)

        if titulo_livro:
            fonte_titulo = _obter_fonte(14)
            titulo_truncado = titulo_livro[:45] + "..." if len(titulo_livro) > 45 else titulo_livro
            bbox = draw.textbbox((0, 0), titulo_truncado, font=fonte_titulo)
            largura_texto = bbox[2] - bbox[0]
            x_titulo = (largura - largura_texto) // 2
            draw.text((x_titulo, 8), titulo_truncado, fill='black', font=fonte_titulo)

        x_barcode = (largura - img_barcode.width) // 2
        y_barcode = altura_titulo + 5
        img_final.paste(img_barcode, (x_barcode, y_barcode))

        # Patrimônio abaixo do barcode
        fonte_patrimonio = _obter_fonte(12)
        bbox = draw.textbbox((0, 0), patrimonio, font=fonte_patrimonio)
        largura_texto = bbox[2] - bbox[0]
        x_patrimonio = (largura - largura_texto) // 2
        y_patrimonio = y_barcode + img_barcode.height + 5
        draw.text((x_patrimonio, y_patrimonio), patrimonio, fill='black', font=fonte_patrimonio)

        img_final.save(caminho_final, "PNG")

        # Remove temporário
        os.remove(caminho_barcode)

        return caminho_final

    except Exception as e:
        print(f"❌ Erro ao gerar código de barras: {e}")
        return None


def regenerar_barcode(patrimonio, titulo_livro=None):
    """Regenera o código de barras forçando a recriação."""
    return gerar_codigo_barras(patrimonio, titulo_livro, forcar=True)


def obter_caminho_barcode(patrimonio):
    """Retorna o caminho da imagem do código de barras se existir."""
    caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pasta_barcodes = os.path.join(caminho_base, "assets", "barcodes")
    caminho = os.path.join(pasta_barcodes, f"{patrimonio}.png")
    if os.path.exists(caminho):
        return caminho
    return None


def gerar_barcode_se_nao_existe(patrimonio, titulo_livro=None):
    """Gera o código de barras apenas se a imagem ainda não existir."""
    caminho_existente = obter_caminho_barcode(patrimonio)
    if caminho_existente:
        return caminho_existente
    return gerar_codigo_barras(patrimonio, titulo_livro)


class PDFEtiquetas(FPDF):
    """Classe para gerar PDF de etiquetas."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False)

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')


def gerar_pagina_etiquetas(exemplares, titulo_livro=None):
    """
    Gera um PDF com etiquetas de código de barras para impressão.

    Layout: 4 colunas x 8 linhas = 32 etiquetas por página A4

    Args:
        exemplares: Lista de tuplas (patrimonio, titulo_livro)
        titulo_livro: Título padrão se não fornecido por exemplar

    Returns:
        Lista com o caminho do PDF gerado.
    """
    try:
        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta_destino = os.path.join(caminho_base, "assets", "barcodes")
        os.makedirs(pasta_destino, exist_ok=True)

        # Configurações da página A4 em mm
        LARGURA_PAGINA = 210
        ALTURA_PAGINA = 297

        # Configurações das etiquetas
        COLUNAS = 4
        LINHAS = 8
        ETIQUETAS_POR_PAGINA = COLUNAS * LINHAS

        # Dimensões da etiqueta em mm (compacta)
        LARGURA_ETIQUETA = 45
        ALTURA_ETIQUETA = 32

        # Margens e espaçamento
        MARGEM_ESQUERDA = 12
        MARGEM_TOPO = 10
        ESPACO_X = (LARGURA_PAGINA - 2 * MARGEM_ESQUERDA - COLUNAS * LARGURA_ETIQUETA) / (COLUNAS - 1)
        ESPACO_Y = (ALTURA_PAGINA - 2 * MARGEM_TOPO - LINHAS * ALTURA_ETIQUETA) / (LINHAS - 1)

        # Cria o PDF
        pdf = PDFEtiquetas()
        pdf.set_margins(0, 0, 0)

        # Divide em páginas
        paginas = []
        for i in range(0, len(exemplares), ETIQUETAS_POR_PAGINA):
            paginas.append(exemplares[i:i + ETIQUETAS_POR_PAGINA])

        for num_pagina, etiquetas_pagina in enumerate(paginas):
            pdf.add_page()

            for idx, (patrimonio, titulo) in enumerate(etiquetas_pagina):
                col = idx % COLUNAS
                lin = idx // COLUNAS

                # Calcula posição da etiqueta
                x = MARGEM_ESQUERDA + col * (LARGURA_ETIQUETA + ESPACO_X)
                y = MARGEM_TOPO + lin * (ALTURA_ETIQUETA + ESPACO_Y)

                # Desenha borda da etiqueta
                pdf.set_draw_color(180, 180, 180)
                pdf.set_line_width(0.2)
                pdf.rect(x, y, LARGURA_ETIQUETA, ALTURA_ETIQUETA)

                # Título do livro (centralizado, fonte maior)
                titulo_exibicao = titulo or titulo_livro or ""
                pdf.set_font('Arial', 'B', 7)
                pdf.set_text_color(0, 0, 0)
                if titulo_exibicao:
                    titulo_truncado = titulo_exibicao[:22] + "..." if len(titulo_exibicao) > 22 else titulo_exibicao
                else:
                    titulo_truncado = ""
                pdf.set_xy(x, y + 1)
                pdf.cell(LARGURA_ETIQUETA, 4, titulo_truncado, 0, 1, 'C')

                # Patrimônio (centralizado, entre título e barcode)
                pdf.set_font('Arial', '', 7)
                pdf.set_xy(x, y + 5)
                pdf.cell(LARGURA_ETIQUETA, 3.5, patrimonio, 0, 1, 'C')

                # Gera o barcode como imagem SEM TEXTO
                caminho_barcode = _criar_barcode_sem_texto(patrimonio, pasta_destino)

                if caminho_barcode:
                    # Barcode ocupa a maior parte da etiqueta
                    img_barcode = Image.open(caminho_barcode)
                    largura_barcode_mm = LARGURA_ETIQUETA - 6
                    ratio = largura_barcode_mm / (img_barcode.width * 25.4 / 96)
                    nova_altura_mm = int(img_barcode.height * 25.4 / 96 * ratio)
                    nova_altura_mm = min(nova_altura_mm, 18)

                    # Salva barcode redimensionado
                    img_barcode_resized = img_barcode.resize(
                        (int(largura_barcode_mm * 96 / 25.4), int(nova_altura_mm * 96 / 25.4)),
                        Image.LANCZOS
                    )
                    caminho_temp_resized = os.path.join(pasta_destino, f"_temp_resized_{patrimonio}.png")
                    img_barcode_resized.save(caminho_temp_resized, "PNG")

                    # Cola o barcode centralizado
                    x_barcode = x + 3
                    y_barcode = y + 9
                    pdf.image(caminho_temp_resized, x=x_barcode, y=y_barcode,
                              w=largura_barcode_mm, h=nova_altura_mm)

                    # Remove temporários
                    os.remove(caminho_barcode)
                    if os.path.exists(caminho_temp_resized):
                        os.remove(caminho_temp_resized)

        # Salva o PDF
        caminho_pdf = os.path.join(pasta_destino, "etiquetas.pdf")
        pdf.output(caminho_pdf)

        print(f"✓ PDF de etiquetas gerado: {caminho_pdf}")
        return [caminho_pdf]

    except Exception as e:
        print(f"❌ Erro ao gerar PDF de etiquetas: {e}")
        return []
