import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OPEN_LIBRARY_URL = "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"


def _limpar_isbn(isbn):
    return re.sub(r"\D", "", isbn or "")


def _abrir_url(url, timeout=10):
    try:
        req = Request(url, headers={"User-Agent": "LumenApp/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload)
    except (HTTPError, URLError, ValueError):
        return None


def _extrair_ano(data_str):
    if not data_str:
        return None
    match = re.search(r"(\d{4})", data_str)
    return int(match.group(1)) if match else None


def _extrair_openlibrary(book):
    if not isinstance(book, dict):
        return None

    title = book.get("title", "")
    authors = ", ".join([a.get("name", "") for a in book.get("authors", []) if a.get("name")])
    publisher = ""
    publishers = book.get("publishers") or []
    if publishers:
        publisher = publishers[0].get("name", "")
    year = _extrair_ano(book.get("publish_date", ""))

    return {
        "title": title,
        "authors": authors,
        "publisher": publisher,
        "year": year,
    }


def _extrair_google_books(volume):
    info = volume.get("volumeInfo", {})
    title = info.get("title", "")
    authors = info.get("authors", [])
    authors_text = ", ".join(authors) if isinstance(authors, list) else str(authors or "")
    publisher = info.get("publisher", "")
    year = _extrair_ano(info.get("publishedDate", ""))

    return {
        "title": title,
        "authors": authors_text,
        "publisher": publisher,
        "year": year,
    }


def buscar_livro_por_isbn(isbn):
    isbn_limpo = _limpar_isbn(isbn)
    if len(isbn_limpo) not in (10, 13):
        return None

    data = _abrir_url(OPEN_LIBRARY_URL.format(isbn=isbn_limpo))
    if data:
        livro = data.get(f"ISBN:{isbn_limpo}")
        if livro:
            resultado = _extrair_openlibrary(livro)
            if resultado and resultado.get("title"):
                return resultado

    data = _abrir_url(GOOGLE_BOOKS_URL.format(isbn=isbn_limpo))
    if data and isinstance(data.get("items"), list) and data["items"]:
        return _extrair_google_books(data["items"][0])

    return None
