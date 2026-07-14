# book_api.py — Consulta de livros por ISBN (compatibilidade com código existente)

from services.isbn_service import buscar_por_isbn as _buscar_isbn_service, _limpar_isbn


def buscar_livro_por_isbn(isbn):
    """Consulta livro por ISBN usando o serviço multi-API. Mantém compatibilidade."""
    resultado = _buscar_isbn_service(isbn)
    if resultado:
        # Retorna no formato esperado pelo código existente (sem campos extras)
        return {
            "title": resultado.get("title", ""),
            "authors": resultado.get("authors", ""),
            "publisher": resultado.get("publisher", ""),
            "year": resultado.get("year"),
        }
    return None
