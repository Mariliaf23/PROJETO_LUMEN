# carteirinha.py — Geração de carteirinhas de usuário com código de barras
# Formato CR80 (cartão de crédito): 85,60 x 53,98 mm

import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import barcode
from barcode.writer import ImageWriter

# Carrega configurações
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path, override=True)

SCHOOL_NAME = os.getenv('SCHOOL_NAME', 'Biblioteca')

# Paleta institucional (mesma do report_export)
COR_AZUL_MARINHO = (11, 29, 52)      # #0B1D34
COR_DOURADO = (201, 162, 76)         # #C9A24C
COR_BRANCO = (255, 255, 255)
COR_CINZA_TEXTO = (100, 100, 100)
COR_CINZA_LINHA = (220, 215, 210)

# Cartão de crédito (CR80 - ISO/IEC 7810)
LARGURA_CARTAO = 85.6
ALTURA_CARTAO = 53.98

# Layout da página A4: 2 colunas x 4 linhas = 8 cartões por página
COLUNAS = 2
LINHAS = 4
CARTOES_POR_PAGINA = COLUNAS * LINHAS

MARGEM_X = 10
MARGEM_Y = 10


def _sanitizar(texto):
    """Remove caracteres fora do latin-1 para compatibilidade com o FPDF."""
    if texto is None:
        return ""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')


def _criar_barcode_png(codigo, pasta_destino):
    """Gera barcode Code 128 sem texto e retorna o caminho da imagem."""
    options = {
        'module_width': 0.3,
        'module_height': 15,
        'quiet_zone': 3,
        'font_size': 0,
        'text_distance': 0,
        'write_text': False,
    }
    writer = ImageWriter()
    code128 = barcode.get('code128', codigo, writer=writer)

    caminho_temp = os.path.join(pasta_destino, f"_temp_cartao_{codigo}")
    code128.save(caminho_temp, options)

    for ext in ['.png', '.jpg', '.gif', '']:
        if os.path.exists(caminho_temp + ext):
            return caminho_temp + ext
    return None


def _desenhar_cartao(pdf, x, y, usuario, pasta_temp):
    """
    Desenha uma carteirinha nas coordenadas (x, y) em mm.

    usuario: tupla (id_usuario, nome, email, telefone, cpf,
                     tipo_usuario, matricula, id_turma, funcao, status)
    """
    id_usuario, nome, email, telefone, cpf, tipo, matricula, id_turma, funcao, status = usuario
    codigo = str(matricula).strip() if matricula else str(id_usuario)
    label_codigo = "MATRÍCULA" if matricula else "CÓDIGO"

    # Fundo branco com borda
    pdf.set_fill_color(*COR_BRANCO)
    pdf.set_draw_color(*COR_AZUL_MARINHO)
    pdf.set_line_width(0.4)
    pdf.rect(x, y, LARGURA_CARTAO, ALTURA_CARTAO, 'DF')

    # Faixa superior azul-marinho com linha dourada
    pdf.set_fill_color(*COR_AZUL_MARINHO)
    pdf.rect(x, y, LARGURA_CARTAO, 10, 'F')
    pdf.set_draw_color(*COR_DOURADO)
    pdf.set_line_width(0.6)
    pdf.line(x, y + 10, x + LARGURA_CARTAO, y + 10)

    # Nome da escola
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(*COR_DOURADO)
    pdf.set_xy(x, y + 1.5)
    pdf.cell(LARGURA_CARTAO, 4, _sanitizar(SCHOOL_NAME.upper()), 0, 1, 'C')

    pdf.set_font('Helvetica', '', 6.5)
    pdf.set_text_color(230, 222, 200)
    pdf.cell(LARGURA_CARTAO, 3.5, 'SISTEMA LUMEN - CARTEIRINHA', 0, 1, 'C')

    # Nome do usuário
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(*COR_AZUL_MARINHO)
    pdf.set_xy(x, y + 12.5)
    nome_exib = _sanitizar(nome)
    if len(nome_exib) > 32:
        nome_exib = nome_exib[:31] + "..."
    pdf.cell(LARGURA_CARTAO, 6, nome_exib, 0, 1, 'C')

    # Linha divisória sutil
    pdf.set_draw_color(*COR_CINZA_LINHA)
    pdf.set_line_width(0.2)
    pdf.line(x + 6, y + 19.5, x + LARGURA_CARTAO - 6, y + 19.5)

    # Matrícula / código
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(*COR_CINZA_TEXTO)
    pdf.set_xy(x, y + 21)
    pdf.cell(LARGURA_CARTAO, 4.5, f'{label_codigo}: {codigo}', 0, 1, 'C')

    # Tipo de usuário
    tipo_exib = _sanitizar(tipo).upper() if tipo else ""
    if tipo_exib == 'ALUNO':
        tipo_exib = 'ALUNO (A)'
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(*COR_AZUL_MARINHO)
    pdf.set_xy(x, y + 25.5)
    pdf.cell(LARGURA_CARTAO, 4.5, tipo_exib, 0, 1, 'C')

    # Código de barras
    caminho_barcode = _criar_barcode_png(codigo, pasta_temp)
    if caminho_barcode:
        try:
            with Image.open(caminho_barcode) as img:
                largura_mm = 52
                ratio = largura_mm / (img.width * 25.4 / 96)
                altura_mm = min(img.height * 25.4 / 96 * ratio, 14)

                x_barcode = x + (LARGURA_CARTAO - largura_mm) / 2
                y_barcode = y + 30.5
                pdf.image(caminho_barcode, x=x_barcode, y=y_barcode,
                          w=largura_mm, h=altura_mm)

            # Número legível abaixo do barcode
            pdf.set_font('Helvetica', '', 7.5)
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(x, y_barcode + altura_mm + 0.2)
            pdf.cell(LARGURA_CARTAO, 4, codigo, 0, 1, 'C')
        finally:
            if os.path.exists(caminho_barcode):
                os.remove(caminho_barcode)


def gerar_pdf_carteirinhas(usuarios):
    """
    Gera um PDF com carteirinhas de todos os usuários cadastrados.

    Layout: 2 colunas x 4 linhas = 8 carteirinhas por página A4,
    cada uma no tamanho de um cartão de crédito (CR80).

    Args:
        usuarios: Lista de tuplas no formato de listar_usuarios().

    Returns:
        Lista com o caminho do PDF gerado (vazia em caso de erro).
    """
    try:
        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta_destino = os.path.join(caminho_base, "assets", "carteirinhas")
        os.makedirs(pasta_destino, exist_ok=True)

        pdf = FPDF()
        pdf.set_auto_page_break(auto=False)
        pdf.set_margins(0, 0, 0)

        # Espaçamento entre cartões para preencher a página A4 (210 x 297 mm)
        espaco_x = (210 - 2 * MARGEM_X - COLUNAS * LARGURA_CARTAO) / (COLUNAS - 1)
        espaco_y = (297 - 2 * MARGEM_Y - LINHAS * ALTURA_CARTAO) / (LINHAS - 1)

        for i, usuario in enumerate(usuarios):
            if i % CARTOES_POR_PAGINA == 0:
                pdf.add_page()

            idx = i % CARTOES_POR_PAGINA
            col = idx % COLUNAS
            lin = idx // COLUNAS

            x = MARGEM_X + col * (LARGURA_CARTAO + espaco_x)
            y = MARGEM_Y + lin * (ALTURA_CARTAO + espaco_y)

            _desenhar_cartao(pdf, x, y, usuario, pasta_destino)

        caminho_pdf = os.path.join(
            pasta_destino,
            f"carteirinhas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        pdf.output(caminho_pdf)

        print(f"[OK] PDF de carteirinhas gerado: {caminho_pdf}")
        return [caminho_pdf]

    except Exception as e:
        print(f"[ERRO] Falha ao gerar PDF de carteirinhas: {e}")
        return []