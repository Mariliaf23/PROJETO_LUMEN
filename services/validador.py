# validador.py — Validações de entrada do sistema LUMEN

import re
from datetime import date


def validar_isbn(isbn):
    """Valida ISBN-10 ou ISBN-13 com checksum. Retorna (ok, mensagem)."""
    numeros = re.sub(r'\D', '', isbn)
    if len(numeros) == 13:
        # ISBN-13: soma ponderada (pesos 1,3,1,3,...), módulo 10 deve ser 0
        soma = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(numeros))
        if soma % 10 != 0:
            return False, "ISBN-13 inválido (checksum incorreto)."
        return True, ""
    elif len(numeros) == 10:
        # ISBN-10: soma ponderada (pesos 10,9,...,2), módulo 11
        soma = 0
        for i, d in enumerate(numeros[:9]):
            soma += int(d) * (10 - i)
        ultimo = 11 - (soma % 11)
        digito_esperado = 'X' if ultimo == 11 else str(ultimo)
        if numeros[9].upper() != digito_esperado:
            return False, "ISBN-10 inválido (checksum incorreto)."
        return True, ""
    elif len(numeros) == 0:
        return False, "ISBN é obrigatório."
    else:
        return False, "ISBN deve ter 10 ou 13 dígitos."


def validar_ano(ano_str):
    """Ano entre 1000 e ano_atual+1. Retorna (ok, mensagem)."""
    if not ano_str.strip():
        return True, ""          # campo opcional
    if not ano_str.strip().isdigit():
        return False, "Ano deve conter apenas números."
    ano = int(ano_str.strip())
    if ano < 1000 or ano > date.today().year + 1:
        return False, f"Ano inválido. Use entre 1000 e {date.today().year + 1}."
    return True, ""


def validar_contato(contato):
    """Aceita e-mail válido OU celular com 8–11 dígitos. Retorna (ok, mensagem)."""
    contato = contato.strip()
    if not contato:
        return False, "Informe o e-mail ou celular."
    # Testa e-mail
    if "@" in contato:
        padrao = r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$'
        if re.match(padrao, contato):
            return True, ""
        return False, "E-mail inválido. Ex: nome@dominio.com"
    # Testa celular (só dígitos, 8–11)
    digitos = re.sub(r'\D', '', contato)
    if 8 <= len(digitos) <= 11:
        return True, ""
    return False, "Celular inválido. Use 8 a 11 dígitos. Ex: 11987654321"


def validar_email(email):
    """Valida e-mail. Retorna (ok, mensagem)."""
    email = email.strip()
    if not email:
        return False, "Informe o e-mail."
    padrao = r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$'
    if re.match(padrao, email):
        return True, ""
    return False, "E-mail inválido. Ex: nome@dominio.com"


def validar_telefone(telefone):
    """Valida telefone (opcional). Se preenchido, aceita 8–11 dígitos. Retorna (ok, mensagem)."""
    telefone = telefone.strip()
    if not telefone:
        return True, ""  # Telefone é opcional
    digitos = re.sub(r'\D', '', telefone)
    if 8 <= len(digitos) <= 11:
        return True, ""
    return False, "Telefone inválido. Use 8 a 11 dígitos. Ex: 11987654321"


def validar_nome(nome):
    """Mínimo 3 caracteres, apenas letras, espaços e acentos. Retorna (ok, mensagem)."""
    nome = nome.strip()
    if len(nome) < 3:
        return False, "Nome deve ter pelo menos 3 caracteres."
    if not re.match(r"^[A-Za-zÀ-ÿ\s\-']+$", nome):
        return False, "Nome deve conter apenas letras e espaços."
    return True, ""


def validar_senha(senha):
    """Mínimo 6 caracteres. Retorna (ok, mensagem)."""
    if len(senha) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres."
    return True, ""


def validar_patrimonio(codigo):
    """Mínimo 3 chars, sem espaços. Retorna (ok, mensagem)."""
    codigo = codigo.strip()
    if len(codigo) < 3:
        return False, "Código de patrimônio deve ter pelo menos 3 caracteres."
    if " " in codigo:
        return False, "Código de patrimônio não pode conter espaços."
    return True, ""


def validar_autor(autor):
    """Autor opcional, mas se preenchido só aceita letras, espaços e acentos."""
    autor = autor.strip()
    if not autor:
        return True, ""
    if not re.match(r"^[A-Za-zÀ-ÿ\s\-\.,']+$", autor):
        return False, "Autor deve conter apenas letras e espaços."
    if len(autor) < 2:
        return False, "Autor deve ter pelo menos 2 caracteres."
    return True, ""


def validar_texto(texto, campo="Campo", min_len=2, obrigatorio=True):
    """Validação genérica de texto. Retorna (ok, mensagem)."""
    texto = texto.strip()
    if not texto:
        if obrigatorio:
            return False, f"{campo} é obrigatório."
        return True, ""
    if len(texto) < min_len:
        return False, f"{campo} deve ter pelo menos {min_len} caracteres."
    return True, ""
