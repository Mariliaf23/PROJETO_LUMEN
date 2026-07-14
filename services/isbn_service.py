# isbn_service.py — Serviço centralizado de consulta ISBN com fallback multi-API

import json
import re
import logging
from urllib.error import HTTPError, URLError
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


# ── Google Books ─────────────────────────────────────────────────────────────

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


# ── Open Library ─────────────────────────────────────────────────────────────

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


# ── ISBNsearch ───────────────────────────────────────────────────────────────

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

# Lista de APIs na ordem de prioridade
_APIS = [
    ("Google Books", _buscar_google_books),
    ("Open Library", _buscar_open_library),
    ("ISBNsearch", _buscar_isbnsearch),
]


def buscar_por_isbn(isbn):
    """Busca livro por ISBN em múltiplas bases. Retorna dict normalizado ou None."""
    isbn_limpo = _limpar_isbn(isbn)
    if len(isbn_limpo) not in (10, 13):
        logger.warning("ISBN inválido: %s", isbn)
        return None

    for nome_api, func in _APIS:
        try:
            logger.info("Consultando %s para ISBN %s...", nome_api, isbn_limpo)
            resultado = func(isbn_limpo)
            if resultado and resultado.get("title"):
                logger.info("Encontrado em %s: %s", nome_api, resultado["title"])
                return resultado
            logger.info("%s: nenhum resultado para %s", nome_api, isbn_limpo)
        except Exception as e:
            logger.error("Erro na API %s para ISBN %s: %s", nome_api, isbn_limpo, e)

    logger.warning("ISBN %s não encontrado em nenhuma base", isbn_limpo)
    return None
