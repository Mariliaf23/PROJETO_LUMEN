# validador.py — Valida dados de entrada do sistema

import re  # Biblioteca para expressões regulares (validar padrões de texto)


def validar_email(email):
    """Verifica se o email tem formato válido (ex: usuario@dominio.com)"""
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Padrão regex para email
    return bool(re.match(padrao, email))   # Retorna True se o email bate no padrão


def validar_celular(celular):
    """Verifica se o celular tem 10 ou 11 dígitos"""
    numeros = re.sub(r'\D', '', celular)   # Remove tudo que não é número
    return len(numeros) in (10, 11)        # Retorna True se tem 10 ou 11 dígitos


def validar_contato(contato):
    """Verifica se o contato é um email ou celular válido"""
    if '@' in contato:                     # Se tem @, tratar como email
        return validar_email(contato)
    return validar_celular(contato)        # Senão, tratar como celular


def validar_isbn(isbn):
    """Verifica se o ISBN tem 10 ou 13 dígitos"""
    numeros = re.sub(r'\D', '', isbn)      # Remove tudo que não é número
    return len(numeros) in (10, 13)        # ISBN pode ter 10 ou 13 dígitos


def validar_data(data_str):
    """Verifica se a data está no formato AAAA-MM-DD com valores válidos"""
    padrao = r'^\d{4}-\d{2}-\d{2}$'       # Padrão: 4 dígitos - 2 dígitos - 2 dígitos
    if not re.match(padrao, data_str):     # Se não bate no padrão, é inválida
        return False
    try:
        partes = data_str.split('-')       # Divide "2026-06-27" em ["2026", "06", "27"]
        ano, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])  # Converte para números
        if mes < 1 or mes > 12:            # Mês precisa ser entre 1 e 12
            return False
        if dia < 1 or dia > 31:            # Dia precisa ser entre 1 e 31
            return False
        return True
    except (ValueError, IndexError):       # Se der erro ao converter para número
        return False


def validar_senha(senha, minimo=4):
    """Verifica se a senha tem pelo menos 'minimo' caracteres"""
    return len(senha) >= minimo            # Retorna True se a senha é longa o suficiente


def campo_obrigatorio(valor):
    """Verifica se o campo não está vazio ou só com espaços"""
    return bool(valor and valor.strip())   # strip() remove espaços; se sobrar algo, é válido
