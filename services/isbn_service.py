# isbn_service.py — Serviço centralizado de consulta ISBN com fallback multi-API

import json
import re
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

logger = logging.getLogger("lumen.isbn_service")

TIMEOUT = 10  # segundos por consulta


def _limpar_isbn(isbn):
    return re.sub(r"\D", "", isbn or "")


def _abrir_url(url, timeout=TIMEOUT):
    try:
        req = Request(url, headers={"User-Agent": "LumenApp/2.0"})
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError, ValueError, OSError) as e:
        logger.warning("Falha ao acessar %s: %s", url, e)
        return None


def _extrair_ano(data_str):
    if not data_str:
        return None
    match = re.search(r"(\d{4})", data_str)
    return int(match.group(1)) if match else None


# ── ISBN-10 ↔ ISBN-13 Conversão ────────────────────────────────────────────────

def _isbn10_para_13(isbn10):
    """Converte ISBN-10 válido para ISBN-13."""
    isbn10 = _limpar_isbn(isbn10)
    if len(isbn10) != 10:
        return None
    if not _validar_isbn10(isbn10):
        return None
    base = "978" + isbn10[:9]
    return base + str(_calcular_check_digit_13(base))


def _isbn13_para_10(isbn13):
    """Converte ISBN-13 (começando com 978) para ISBN-10."""
    isbn13 = _limpar_isbn(isbn13)
    if len(isbn13) != 13 or not isbn13.startswith("978"):
        return None
    if not _validar_isbn13(isbn13):
        return None
    base = isbn13[3:12]
    return base + str(_calcular_check_digit_10(base))


def _validar_isbn10(isbn):
    isbn = _limpar_isbn(isbn)
    if len(isbn) != 10:
        return False
    try:
        total = sum((10 - i) * (10 if c == 'X' else int(c)) for i, c in enumerate(isbn))
        return total % 11 == 0
    except ValueError:
        return False


def _validar_isbn13(isbn):
    isbn = _limpar_isbn(isbn)
    if len(isbn) != 13:
        return False
    try:
        total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(isbn))
        return total % 10 == 0
    except ValueError:
        return False


def _calcular_check_digit_10(base9):
    total = sum((10 - i) * int(c) for i, c in enumerate(base9))
    remainder = total % 11
    check = 11 - remainder
    if check == 10:
        return 'X'
    if check == 11:
        return '0'
    return str(check)


def _calcular_check_digit_13(base12):
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(base12))
    remainder = total % 10
    return (10 - remainder) % 10


def _gerar_variacoes_isbn(isbn):
    """Gera lista de ISBNs para tentar (original + convertido se válido)."""
    isbn_limpo = _limpar_isbn(isbn)
    variacoes = [isbn_limpo]
    
    if len(isbn_limpo) == 10 and _validar_isbn10(isbn_limpo):
        isbn13 = _isbn10_para_13(isbn_limpo)
        if isbn13:
            variacoes.append(isbn13)
    elif len(isbn_limpo) == 13 and _validar_isbn13(isbn_limpo):
        isbn10 = _isbn13_para_10(isbn_limpo)
        if isbn10:
            variacoes.append(isbn10)
    
    return variacoes


# ── Open Library (PRIORIDADE 1 - Melhor cobertura BR) ──────────────────────────

def _buscar_open_library(isbn):
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    data = _abrir_url(url)
    if not data:
        return None

    book = data.get(f"ISBN:{isbn}")
    if not book or not isinstance(book, dict):
        return None

    title = book.get("title", "")
    if not title:
        return None

    authors = ", ".join(
        a.get("name", "") for a in book.get("authors", []) if a.get("name")
    )

    publishers = book.get("publishers") or []
    publisher = publishers[0].get("name", "") if publishers else ""

    cover = book.get("cover", {})
    cover_url = cover.get("medium", "") or cover.get("small", "")

    return {
        "isbn": isbn,
        "title": title,
        "subtitle": "",
        "authors": authors,
        "publisher": publisher,
        "year": _extrair_ano(book.get("publish_date", "")),
        "pages": None,
        "language": "",
        "category": "",
        "description": "",
        "cover_url": cover_url,
        "source": "Open Library",
    }


def _buscar_open_library_por_titulo_autor(titulo, autor=None):
    """Busca no Open Library por título e opcionalmente autor."""
    query_parts = [f"title:{quote(titulo)}"]
    if autor:
        query_parts.append(f"author:{quote(autor)}")
    query = "+".join(query_parts)
    url = f"https://openlibrary.org/search.json?q={query}&limit=5"
    data = _abrir_url(url)
    if not data or not data.get("docs"):
        return None
    
    doc = data["docs"][0]
    return {
        "isbn": doc.get("isbn", [""])[0] if doc.get("isbn") else "",
        "title": doc.get("title", ""),
        "subtitle": "",
        "authors": ", ".join(doc.get("author_name", [])),
        "publisher": doc.get("publisher", [""])[0] if doc.get("publisher") else "",
        "year": doc.get("first_publish_year"),
        "pages": doc.get("number_of_pages_median"),
        "language": doc.get("language", [""])[0] if doc.get("language") else "",
        "category": doc.get("subject", [""])[0] if doc.get("subject") else "",
        "description": "",
        "cover_url": f"https://covers.openlibrary.org/b/id/{doc.get('cover_i')}-M.jpg" if doc.get("cover_i") else "",
        "source": "Open Library (busca textual)",
    }


# ── Google Books (PRIORIDADE 2) ────────────────────────────────────────────────

def _buscar_google_books(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    data = _abrir_url(url)
    if not data or not isinstance(data.get("items"), list) or not data["items"]:
        return None

    volume = data["items"][0]
    info = volume.get("volumeInfo", {})

    authors = info.get("authors", [])
    authors_text = ", ".join(authors) if isinstance(authors, list) else str(authors or "")

    categories = info.get("categories", [])
    category = categories[0] if isinstance(categories, list) and categories else ""

    cover = info.get("imageLinks", {})
    cover_url = cover.get("thumbnail", "") or cover.get("smallThumbnail", "")

    return {
        "isbn": isbn,
        "title": info.get("title", ""),
        "subtitle": info.get("subtitle", ""),
        "authors": authors_text,
        "publisher": info.get("publisher", ""),
        "year": _extrair_ano(info.get("publishedDate", "")),
        "pages": info.get("pageCount"),
        "language": info.get("language", ""),
        "category": category,
        "description": info.get("description", ""),
        "cover_url": cover_url,
        "source": "Google Books",
    }


def _buscar_google_books_por_titulo_autor(titulo, autor=None):
    """Busca no Google Books por título e opcionalmente autor."""
    query_parts = [f"intitle:{quote(titulo)}"]
    if autor:
        query_parts.append(f"inauthor:{quote(autor)}")
    query = "+".join(query_parts)
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=5"
    data = _abrir_url(url)
    if not data or not isinstance(data.get("items"), list) or not data["items"]:
        return None
    
    volume = data["items"][0]
    info = volume.get("volumeInfo", {})
    authors = info.get("authors", [])
    authors_text = ", ".join(authors) if isinstance(authors, list) else str(authors or "")
    categories = info.get("categories", [])
    category = categories[0] if isinstance(categories, list) and categories else ""
    cover = info.get("imageLinks", {})
    cover_url = cover.get("thumbnail", "") or cover.get("smallThumbnail", "")
    
    isbns = info.get("industryIdentifiers", [])
    isbn13 = next((id["identifier"] for id in isbns if id["type"] == "ISBN_13"), "")
    isbn10 = next((id["identifier"] for id in isbns if id["type"] == "ISBN_10"), "")
    
    return {
        "isbn": isbn13 or isbn10,
        "title": info.get("title", ""),
        "subtitle": info.get("subtitle", ""),
        "authors": authors_text,
        "publisher": info.get("publisher", ""),
        "year": _extrair_ano(info.get("publishedDate", "")),
        "pages": info.get("pageCount"),
        "language": info.get("language", ""),
        "category": category,
        "description": info.get("description", ""),
        "cover_url": cover_url,
        "source": "Google Books (busca textual)",
    }


# ── ISBNsearch (PRIORIDADE 3) ──────────────────────────────────────────────────

def _buscar_isbnsearch(isbn):
    url = f"https://api.isbnsearch.org/isbn/{isbn}"
    data = _abrir_url(url)
    if not data or not isinstance(data, dict):
        return None

    title = data.get("title", "")
    if not title:
        return None

    authors = data.get("authors", [])
    authors_text = ", ".join(authors) if isinstance(authors, list) else str(authors or "")

    return {
        "isbn": isbn,
        "title": title,
        "subtitle": data.get("subtitle", ""),
        "authors": authors_text,
        "publisher": data.get("publisher", ""),
        "year": _extrair_ano(data.get("publish_date", "")),
        "pages": data.get("number_of_pages"),
        "language": data.get("language", ""),
        "category": data.get("subject", ""),
        "description": data.get("synopsis", ""),
        "cover_url": data.get("cover", ""),
        "source": "ISBNsearch",
    }


# ── Consulta com fallback ────────────────────────────────────────────────────

_APIS_ISBN = [
    ("Open Library", _buscar_open_library),
    ("Google Books", _buscar_google_books),
    ("ISBNsearch", _buscar_isbnsearch),
]

_APIS_TEXTUAL = [
    ("Open Library", _buscar_open_library_por_titulo_autor),
    ("Google Books", _buscar_google_books_por_titulo_autor),
]


def buscar_por_isbn(isbn):
    """Busca livro por ISBN em múltiplas bases. Tenta ISBN-10 e ISBN-13."""
    isbn_limpo = _limpar_isbn(isbn)
    if len(isbn_limpo) not in (10, 13):
        logger.warning("ISBN inválido: %s", isbn)
        return None

    variacoes = _gerar_variacoes_isbn(isbn_limpo)
    logger.info("Tentando ISBNs: %s", variacoes)

    for isbn_tentativa in variacoes:
        for nome_api, func in _APIS_ISBN:
            try:
                logger.info("Consultando %s para ISBN %s...", nome_api, isbn_tentativa)
                resultado = func(isbn_tentativa)
                if resultado and resultado.get("title"):
                    logger.info("Encontrado em %s: %s", nome_api, resultado["title"])
                    return resultado
                logger.info("%s: nenhum resultado para %s", nome_api, isbn_tentativa)
            except Exception as e:
                logger.error("Erro na API %s para ISBN %s: %s", nome_api, isbn_tentativa, e)

    logger.warning("ISBN %s não encontrado em nenhuma base", isbn_limpo)
    return None


def buscar_por_titulo_autor(titulo, autor=None):
    """Busca livro por título e autor (fallback textual)."""
    if not titulo or len(titulo.strip()) < 2:
        return None
    
    titulo = titulo.strip()
    autor = autor.strip() if autor else None
    logger.info("Busca textual: título='%s', autor='%s'", titulo, autor)

    for nome_api, func in _APIS_TEXTUAL:
        try:
            logger.info("Consultando %s (busca textual)...", nome_api)
            resultado = func(titulo, autor)
            if resultado and resultado.get("title"):
                logger.info("Encontrado em %s (textual): %s", nome_api, resultado["title"])
                return resultado
            logger.info("%s (textual): nenhum resultado", nome_api)
        except Exception as e:
            logger.error("Erro na API %s (busca textual): %s", nome_api, e)

    logger.warning("Nenhum resultado para busca textual: %s", titulo)
    return None


def buscar_livro(isbn=None, titulo=None, autor=None):
    """
    Busca unificada: tenta ISBN primeiro, depois busca textual.
    Pelo menos um de (isbn) ou (titulo) deve ser fornecido.
    """
    if isbn:
        resultado = buscar_por_isbn(isbn)
        if resultado:
            return resultado
    
    if titulo:
        return buscar_por_titulo_autor(titulo, autor)
    
    return None