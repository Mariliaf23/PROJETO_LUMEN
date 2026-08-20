# db_async.py — Executa consultas de banco em THREAD DE FUNDO
#
# Motivo: consultas síncronas na thread da interface (mainloop do tkinter)
# congelavam o sistema inteiro enquanto o MySQL remoto respondia. Este
# helper roda a consulta numa daemon thread e devolve o resultado para a
# thread da UI via uma FILA processada periodicamente no mainloop.
#
# REGRA DE SEGURANÇA DO TKINTER:
#   - fn_coleta  (thread de fundo): SOMENTE banco/CPU. NUNCA mexa em widgets.
#   - callback   (thread da UI):   pode reconstruir telas, tabelas, etc.
#
# IMPLEMENTAÇÃO:
#   Em vez de usar root.after(0, ...) diretamente da thread de fundo (que
#   pode falhar com "main thread is not in main loop" se a janela estiver
#   sendo reconstruída), usamos uma fila thread-safe. O mainloop processa
#   a fila a cada 50ms, garantindo que TODOS os callbacks executem na
#   thread principal — nunca na thread de fundo.

import threading
import queue
import sys


_CALLBACK_BANNER = None
_UI_QUEUE = queue.Queue()
_QUEUE_POLL_ID = None
_POLL_MS = 50  # intervalo de checagem da fila


def registrar_callback_banner(callback):
    """Registra uma função(indisponivel: bool) chamada na thread da UI.

    É chamada com True quando uma consulta falha por erro de rede/MySQL
    (servidor indisponível) e com False quando uma consulta volta a funcionar.
    """
    global _CALLBACK_BANNER
    _CALLBACK_BANNER = callback


def _eh_erro_conexao(erro):
    """Indica se o erro veio do MySQL/da rede (não um bug da aplicação)."""
    import socket
    cls = type(erro).__name__
    if isinstance(erro, OSError) or isinstance(erro, socket.timeout):
        return True
    try:
        import mysql.connector
        if isinstance(erro, mysql.connector.Error):
            return True
    except Exception:
        pass
    return cls in ("InterfaceError", "OperationalError", "DatabaseError",
                   "ProgrammingError", "ConnectionError", "TimeoutError")


def _processar_fila_ui(root):
    """Processa callbacks na fila da UI.

    Deve ser chamado periodicamente no mainloop (reagenda a si mesmo).
    NUNCA é chamado por thread de fundo — sempre pela thread principal.
    """
    global _QUEUE_POLL_ID
    try:
        while True:
            callback, args, kwargs = _UI_QUEUE.get_nowait()
            try:
                callback(*args, **kwargs)
            except Exception as e:  # noqa: BLE001
                print(f"[db_async] erro no callback da fila: {e}", file=sys.stderr)
    except queue.Empty:
        pass
    except Exception as e:  # noqa: BLE001
        print(f"[db_async] erro ao processar fila UI: {e}", file=sys.stderr)

    # Reagenda a próxima checagem (se a janela ainda existir)
    try:
        if root is not None and root.winfo_exists():
            _QUEUE_POLL_ID = root.after(_POLL_MS, _processar_fila_ui, root)
        else:
            _QUEUE_POLL_ID = None
    except Exception:
        _QUEUE_POLL_ID = None


def iniciar_processamento_fila(root):
    """Inicia o processamento periódico da fila de callbacks da UI.

    Deve ser chamado UMA vez após criar a janela principal, antes do mainloop.
    Garante que callbacks de threads de fundo executem sempre na thread da UI.
    """
    global _QUEUE_POLL_ID
    if _QUEUE_POLL_ID is None and root is not None and root.winfo_exists():
        _processar_fila_ui(root)


def _agendar_na_ui(root, callback, *args, **kwargs):
    """Coloca callback na fila para execução na thread da UI.

    Retorna True se agendou com sucesso, False se a janela não existe mais
    (nesse caso o chamador pode decidir descartar o resultado — NÃO executa
    na thread de fundo, evitando o bug 'main thread is not in main loop').
    """
    try:
        if root is not None and root.winfo_exists():
            _UI_QUEUE.put((callback, args, kwargs))
            return True
    except Exception:
        pass
    return False


def carregar_em_fundo(root, fn_coleta, callback):
    """Executa fn_coleta numa daemon thread e chama callback(dados, erro) na thread da UI.

    Args:
        root: janela tkinter usada para agendar o retorno na thread da UI.
        fn_coleta: função sem argumentos que retorna os dados (consulta).
        callback:  função(dados, erro) executada na thread da UI. 'erro'
                   será None em caso de sucesso, ou a exceção capturada.

    SEGURANÇA: o callback NUNCA é executado na thread de fundo. Se a janela
    foi destruída antes da thread terminar, o resultado é simplesmente
    descartado (não há como atualizar uma UI inexistente).
    """
    def _rodar():
        try:
            dados, erro = fn_coleta(), None
        except Exception as e:  # noqa: BLE001
            dados, erro = None, e

        def _aplicar():
            try:
                callback(dados, erro)
            except Exception as e:  # noqa: BLE001
                print(f"[db_async] erro no callback: {e}", file=sys.stderr)

        # Agenda na fila da UI — se a janela sumiu, descarta silenciosamente
        _agendar_na_ui(root, _aplicar)

        # Notifica o banner de conexão (se registrado)
        _notificar_banner(root, erro)

    threading.Thread(target=_rodar, daemon=True).start()


def _notificar_banner(root, erro):
    """Avisa a UI se o servidor de banco está indisponível (ou voltou)."""
    global _CALLBACK_BANNER
    if _CALLBACK_BANNER is None:
        return
    indisponivel = erro is not None and _eh_erro_conexao(erro)

    def _aplicar():
        try:
            _CALLBACK_BANNER(indisponivel)
        except Exception:  # noqa: BLE001
            pass

    _agendar_na_ui(root, _aplicar)
