import re


def validar_email(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(padrao, email))


def validar_celular(celular):
    numeros = re.sub(r'\D', '', celular)
    return len(numeros) in (10, 11)


def validar_contato(contato):
    if '@' in contato:
        return validar_email(contato)
    return validar_celular(contato)


def validar_isbn(isbn):
    numeros = re.sub(r'\D', '', isbn)
    return len(numeros) in (10, 13)


def validar_data(data_str):
    padrao = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(padrao, data_str):
        return False
    try:
        partes = data_str.split('-')
        ano, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
        if mes < 1 or mes > 12:
            return False
        if dia < 1 or dia > 31:
            return False
        return True
    except (ValueError, IndexError):
        return False


def validar_senha(senha, minimo=4):
    return len(senha) >= minimo


def campo_obrigatorio(valor):
    return bool(valor and valor.strip())
