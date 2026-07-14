# notificacoes.py — Central de Notificações do sistema LUMEN (WhatsApp Web)

import json
import os
import webbrowser
import urllib.parse
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
# CAMINHOS DE ARQUIVOS
# ═══════════════════════════════════════════════════════════════════════════════

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "data")
_CONFIG_PATH = os.path.join(_DATA_DIR, "notificacoes_config.json")
_TEMPLATES_PATH = os.path.join(_DATA_DIR, "notificacoes_templates.json")
_HISTORICO_PATH = os.path.join(_DATA_DIR, "notificacoes_historico.json")

os.makedirs(_DATA_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# EVENTOS SUPORTADOS
# ═══════════════════════════════════════════════════════════════════════════════

EVENTOS = {
    "emprestimo_realizado":  "Empréstimo realizado",
    "devolucao_realizada":   "Devolução realizada",
    "reserva_criada":        "Reserva criada",
    "reserva_disponivel":    "Reserva disponível",
    "aviso_devolucao":       "Aviso de devolução",
    "aviso_atraso":          "Aviso de atraso",
}

TEMPLATES_PADRAO = {
    "emprestimo_realizado": (
        "Olá {nome}! 📚\n\n"
        "Seu empréstimo foi registrado com sucesso!\n\n"
        "📖 Livro: {livro}\n"
        "📋 Patrimônio: {patrimonio}\n"
        "📅 Empréstimo: {emprestimo}\n"
        "📅 Devolução prevista: {devolucao}\n\n"
        "{historico_usuario}\n\n"
        "Obrigado por utilizar a biblioteca LUMEN!"
    ),
    "devolucao_realizada": (
        "Olá {nome}! ✅\n\n"
        "Sua devolução foi registrada com sucesso!\n\n"
        "📖 Livro: {livro}\n"
        "📋 Patrimônio: {patrimonio}\n\n"
        "{historico_usuario}\n\n"
        "Obrigado por devolver no prazo!"
    ),
    "reserva_criada": (
        "Olá {nome}! 📌\n\n"
        "Sua reserva foi realizada com sucesso!\n\n"
        "📖 Livro: {livro}\n"
        "📅 Reserva feita em: {emprestimo}\n\n"
        "{historico_usuario}\n\n"
        "Você será notificado quando o livro estiver disponível."
    ),
    "reserva_disponivel": (
        "Olá {nome}! 🎉\n\n"
        "O livro reservado está disponível para retirada!\n\n"
        "📖 Livro: {livro}\n"
        "📋 Patrimônio: {patrimonio}\n\n"
        "{historico_usuario}\n\n"
        "Retire na biblioteca em até 3 dias úteis."
    ),
    "aviso_devolucao": (
        "Olá {nome}! ⏰\n\n"
        "Lembrete: sua devolução está próxima!\n\n"
        "📖 Livro: {livro}\n"
        "📋 Patrimônio: {patrimonio}\n"
        "📅 Devolução prevista: {devolucao}\n\n"
        "{historico_usuario}\n\n"
        "Por favor, devolva dentro do prazo para evitar multas."
    ),
    "aviso_atraso": (
        "Olá {nome}! ⚠️\n\n"
        "Seu empréstimo está em atraso!\n\n"
        "📖 Livro: {livro}\n"
        "📋 Patrimônio: {patrimonio}\n"
        "📅 Devolução prevista: {devolucao}\n\n"
        "{historico_usuario}\n\n"
        "Por favor, devolva o mais breve possível para evitar multas."
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO (persistência em JSON)
# ═══════════════════════════════════════════════════════════════════════════════

_CONFIG_PADRAO = {
    "habilitado": True,
    "abrir_automatico": True,
    "registrar_historico": True,
    "incluir_resumo": True,
    "eventos_habilitados": {
        "emprestimo_realizado": True,
        "devolucao_realizada": True,
        "reserva_criada": True,
        "reserva_disponivel": True,
        "aviso_devolucao": True,
        "aviso_atraso": True,
    },
}


def carregar_config():
    """Carrega configurações do arquivo JSON. Retorna dict."""
    if os.path.exists(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # Garante que todas as chaves existem
            for k, v in _CONFIG_PADRAO.items():
                if k not in cfg:
                    cfg[k] = v
                elif isinstance(v, dict):
                    for ek, ev in v.items():
                        if ek not in cfg[k]:
                            cfg[k][ek] = ev
            return cfg
        except (json.JSONDecodeError, IOError):
            pass
    return dict(_CONFIG_PADRAO)


def salvar_config(cfg):
    """Salva configurações no arquivo JSON."""
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATES (persistência em JSON)
# ═══════════════════════════════════════════════════════════════════════════════

def carregar_templates():
    """Carrega templates do arquivo JSON. Se não existir, usa os padrões."""
    if os.path.exists(_TEMPLATES_PATH):
        try:
            with open(_TEMPLATES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return dict(TEMPLATES_PADRAO)


def salvar_templates(templates):
    """Salva templates no arquivo JSON."""
    with open(_TEMPLATES_PATH, "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)


def resetar_templates():
    """Restaura templates para os valores padrão."""
    salvar_templates(dict(TEMPLATES_PADRAO))
    return dict(TEMPLATES_PADRAO)


# ═══════════════════════════════════════════════════════════════════════════════
# HISTÓRICO (persistência em JSON)
# ═══════════════════════════════════════════════════════════════════════════════

def carregar_historico():
    """Carrega histórico de notificações."""
    if os.path.exists(_HISTORICO_PATH):
        try:
            with open(_HISTORICO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _salvar_historico(lista):
    """Salva a lista de histórico no arquivo JSON."""
    with open(_HISTORICO_PATH, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)


def registrar_historico(usuario_nome, evento, telefone, status, observacoes=""):
    """Registra uma notificação no histórico."""
    cfg = carregar_config()
    if not cfg.get("registrar_historico", True):
        return

    agora = datetime.now()
    registro = {
        "data": agora.strftime("%d/%m/%Y"),
        "hora": agora.strftime("%H:%M:%S"),
        "usuario": usuario_nome,
        "evento": EVENTOS.get(evento, evento),
        "telefone": telefone,
        "status": status,
        "observacoes": observacoes,
    }

    historico = carregar_historico()
    historico.insert(0, registro)  # Mais recente primeiro

    # Mantém no máximo 500 registros
    if len(historico) > 500:
        historico = historico[:500]

    _salvar_historico(historico)


def limpar_historico():
    """Limpa todo o histórico de notificações."""
    _salvar_historico([])


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATAÇÃO DE TELEFONE
# ═══════════════════════════════════════════════════════════════════════════════

def _formatar_telefone_para_whatsapp(telefone):
    """
    Converte telefone para formato WhatsApp (apenas dígitos, com código do país).
    Exemplos:
      (11) 98765-4321 -> 5511987654321
      11987654321     -> 5511987654321
      5511987654321   -> 5511987654321
    """
    import re
    digitos = re.sub(r'\D', '', telefone)
    if not digitos:
        return None
    # Se já começa com 55 (Brasil), mantém
    if digitos.startswith("55"):
        return digitos
    # Se tem 11 dígitos (DDD + número com 9), adiciona 55
    if len(digitos) == 11:
        return "55" + digitos
    # Se tem 10 dígitos (DDD + número sem 9), adiciona 55 e insere 9
    if len(digitos) == 10:
        return "55" + digitos[:2] + "9" + digitos[2:]
    # Se tem 8-9 dígitos (sem DDD), assume DDD 11
    if len(digitos) in (8, 9):
        return "5511" + digitos
    return digitos


# ═══════════════════════════════════════════════════════════════════════════════
# GERAÇÃO DE MENSAGEM E URL DO WHATSAPP
# ═══════════════════════════════════════════════════════════════════════════════

def montar_mensagem(evento, dados):
    """
    Monta a mensagem substituindo variáveis no template.

    Args:
        evento: chave do evento (ex: 'emprestimo_realizado')
        dados: dict com chaves: nome, livro, patrimonio, emprestimo, devolucao, resumo

    Returns:
        str com a mensagem formatada
    """
    templates = carregar_templates()
    template = templates.get(evento, "")

    variaveis = {
        "nome": dados.get("nome", ""),
        "livro": dados.get("livro", ""),
        "patrimonio": dados.get("patrimonio", ""),
        "emprestimo": dados.get("emprestimo", ""),
        "devolucao": dados.get("devolucao", ""),
        "resumo": dados.get("resumo", ""),
        "historico_usuario": dados.get("historico_usuario", ""),
    }

    mensagem = template
    for chave, valor in variaveis.items():
        mensagem = mensagem.replace("{" + chave + "}", str(valor))

    return mensagem.strip()


def gerar_url_whatsapp(telefone, mensagem):
    """
    Gera a URL do WhatsApp Web para abrir conversa com mensagem pronta.

    Args:
        telefone: telefone no formato Brasil (ex: 11987654321)
        mensagem: texto da mensagem

    Returns:
        str com a URL completa
    """
    telefone_formatado = _formatar_telefone_para_whatsapp(telefone)
    if not telefone_formatado:
        return None

    mensagem_encoded = urllib.parse.quote(mensagem)
    return f"https://wa.me/{telefone_formatado}?text={mensagem_encoded}"


def abrir_whatsapp(telefone, mensagem):
    """
    Abre o navegador padrão com a conversa do WhatsApp Web.

    Args:
        telefone: telefone do destinatário
        mensagem: texto da mensagem

    Returns:
        (bool, str) -> (sucesso, url_gerada)
    """
    url = gerar_url_whatsapp(telefone, mensagem)
    if not url:
        return False, "Telefone inválido ou ausente."

    try:
        webbrowser.open(url)
        return True, url
    except Exception as e:
        return False, str(e)


# ═══════════════════════════════════════════════════════════════════════════════
# API PRINCIPAL — chamada por outros módulos
# ═══════════════════════════════════════════════════════════════════════════════

def enviar_notificacao(usuario_id, evento, dados_extras=None):
    """
    Ponto de entrada para enviar notificações.
    Chamado por outros módulos do sistema.

    Args:
        usuario_id: ID do usuário destinatário
        evento: chave do evento (ex: 'emprestimo_realizado')
        dados_extras: dict opcional com dados adicionais (livro, patrimonio, etc.)

    Returns:
        dict com resultado: {sucesso, mensagem, url}
    """
    from services.database_config import buscar_usuario_por_id

    cfg = carregar_config()

    # Verifica se notificações estão habilitadas
    if not cfg.get("habilitado", True):
        return {"sucesso": False, "mensagem": "Notificações desabilitadas.", "url": None}

    # Verifica se o evento específico está habilitado
    eventos_hab = cfg.get("eventos_habilitados", {})
    if not eventos_hab.get(evento, False):
        return {"sucesso": False, "mensagem": f"Evento '{EVENTOS.get(evento, evento)}' desabilitado.", "url": None}

    # Busca dados do usuário
    dados_usuario = buscar_usuario_por_id(usuario_id)
    if not dados_usuario:
        return {"sucesso": False, "mensagem": "Usuário não encontrado.", "url": None}

    _, nome, email, telefone, cpf, tipo, matricula, id_turma, funcao, status = dados_usuario

    if not telefone:
        return {"sucesso": False, "mensagem": f"Usuário {nome} não possui telefone cadastrado.", "url": None}

    # Monta dados para o template
    extras = dados_extras or {}
    dados_msg = {
        "nome": nome,
        "livro": extras.get("livro", ""),
        "patrimonio": extras.get("patrimonio", ""),
        "emprestimo": extras.get("emprestimo", ""),
        "devolucao": extras.get("devolucao", ""),
        "resumo": "",
        "historico_usuario": _gerar_historico_usuario(usuario_id, nome),
    }

    # Monta mensagem
    mensagem = montar_mensagem(evento, dados_msg)

    # Abre WhatsApp
    sucesso, resultado = abrir_whatsapp(telefone, mensagem)

    # Registra no histórico
    status_hist = "Enviado" if sucesso else "Erro"
    obs = "WhatsApp Web aberto com sucesso" if sucesso else resultado
    registrar_historico(nome, evento, telefone, status_hist, obs)

    return {
        "sucesso": sucesso,
        "mensagem": "WhatsApp Web aberto." if sucesso else resultado,
        "url": resultado if sucesso else None,
    }


def _gerar_historico_usuario(usuario_id, nome):
    """Gera o bloco formatado de histórico do leitor para WhatsApp."""
    try:
        from services.database_config import _conectar
        conn = _conectar()
        cursor = conn.cursor()

        # Código do usuário (ID)
        codigo = usuario_id

        # Empréstimos ativos
        cursor.execute(
            "SELECT COUNT(*) FROM emprestimo WHERE id_usuario = %s AND status IN ('ativo', 'atrasado')",
            (usuario_id,)
        )
        emp_ativos = cursor.fetchone()[0]

        # Reservas ativas
        cursor.execute(
            "SELECT COUNT(*) FROM reserva WHERE id_usuario = %s AND status = 'ativa'",
            (usuario_id,)
        )
        reservas = cursor.fetchone()[0]

        # Total de livros devolvidos
        cursor.execute(
            "SELECT COUNT(*) FROM emprestimo WHERE id_usuario = %s AND status = 'finalizado'",
            (usuario_id,)
        )
        livros_devolvidos = cursor.fetchone()[0]

        # Total de empréstimos (todos os tempos)
        cursor.execute(
            "SELECT COUNT(*) FROM emprestimo WHERE id_usuario = %s",
            (usuario_id,)
        )
        total_emprestimos = cursor.fetchone()[0]

        # Em atraso
        cursor.execute(
            "SELECT COUNT(*) FROM emprestimo WHERE id_usuario = %s AND status = 'atrasado'",
            (usuario_id,)
        )
        em_atraso = cursor.fetchone()[0]

        # Última movimentação
        cursor.execute(
            """SELECT MAX(dt) FROM (
                SELECT MAX(data_emprestimo) AS dt FROM emprestimo WHERE id_usuario = %s
                UNION ALL
                SELECT MAX(data_devolucao) AS dt FROM emprestimo WHERE id_usuario = %s AND data_devolucao IS NOT NULL
                UNION ALL
                SELECT MAX(data_reserva) AS dt FROM reserva WHERE id_usuario = %s
            ) AS movimentacoes""",
            (usuario_id, usuario_id, usuario_id)
        )
        ultima_row = cursor.fetchone()
        if ultima_row and ultima_row[0]:
            from datetime import datetime as _dt
            ultima = ultima_row[0]
            if hasattr(ultima, 'strftime'):
                ultima_str = ultima.strftime("%d/%m/%Y")
            else:
                ultima_str = str(ultima)
        else:
            ultima_str = "Nenhuma"

        # Situação geral
        if em_atraso > 0:
            situacao = "⚠️ Em atraso"
        elif emp_ativos == 0 and reservas == 0:
            situacao = "✅ Regular"
        else:
            situacao = "✅ Regular"

        conn.close()

        # Monta o bloco formatado
        bloco = (
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📊 *SITUAÇÃO DO LEITOR*\n\n"
            f"👤 Nome:\n{nome}\n\n"
            f"🆔 Código:\n{codigo}\n\n"
            f"📚 Empréstimos ativos:\n{emp_ativos}\n\n"
            f"🔖 Reservas:\n{reservas}\n\n"
            f"📖 Livros devolvidos:\n{livros_devolvidos}\n\n"
            f"📚 Total de empréstimos:\n{total_emprestimos}\n\n"
            f"⏰ Em atraso:\n{em_atraso}\n\n"
            f"📅 Última movimentação:\n{ultima_str}\n\n"
            f"Situação:\n{situacao}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

        return bloco

    except Exception:
        return ""


# ═══════════════════════════════════════════════════════════════════════════════
# TESTE
# ═══════════════════════════════════════════════════════════════════════════════

def testar_whatsapp(telefone):
    """
    Envia uma mensagem de teste para o número informado.

    Args:
        telefone: número de telefone

    Returns:
        (bool, str)
    """
    mensagem = (
        "Olá! 👋\n\n"
        "Esta é uma mensagem de teste do sistema LUMEN.\n"
        "Se você recebeu esta mensagem, as notificações estão funcionando corretamente!\n\n"
        "📚 Sistema LUMEN — Biblioteca Escolar"
    )

    sucesso, resultado = abrir_whatsapp(telefone, mensagem)

    registrar_historico(
        "TESTE",
        "teste",
        telefone,
        "Enviado" if sucesso else "Erro",
        "Mensagem de teste" if sucesso else resultado,
    )

    return sucesso, resultado
