# db_async.py — Executa consultas de banco em THREAD DE FUNDO
#
# Motivo: consultas síncronas na thread da interface (mainloop do tkinter)
# congelavam o sistema inteiro enquanto o MySQL remoto respondia. Este
# helper roda a consulta numa daemon thread e devolve o resultado para a
# thread da UI via root.after(0, ...).
#
# REGRA DE SEGURANÇA DO TKINTER:
#   - fn_coleta  (thread de fundo): SOMENTE banco/CPU. NUNCA mexa em widgets.
#   - callback   (thread da UI):   pode reconstruir telas, tabelas, etc.

import threading
import queue
import sys


_CALLBACK_BANNER = None
_UI_QUEUE = queue.Queue()
_QUEUE_POLL_ID = None


def registrar_callback_banner(callback):
    """Registra uma função(indisponivel: bool) chamada na thread da UI.

    É chamada com True quando uma consulta falha por erro de rede/MySQL
    (servidor indisponível) e com False quando uma consulta volta a funcionar.
    """
    global _CALLBACK_BANNER
    _CALLBACK_BANNER = callback


def _eh_erro_conexao(erro):
    """Indica se o erro veio do MySQL/da rede (não um bug da aplicação)."""
    import os
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
    """Processa callbacks na fila da UI (deve ser chamado periodicamente no mainloop)."""
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
    
    if root is not None and root.winfo_exists():
        _QUEUE_POLL_ID = root.after(50, _processar_fila_ui, root)


def iniciar_processamento_fila(root):
    """Inicia o processamento periódico da fila de callbacks da UI.
    
    Deve ser chamado uma vez após criar a janela principal, antes do mainloop.
    """
    global _QUEUE_POLL_ID
    if _QUEUE_POLL_ID is None:
        _processar_fila_ui(root)


def _agendar_na_ui(root, callback, *args, **kwargs):
    """Agenda callback para executar na thread da UI de forma segura."""
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

        print(f"[db_async] _rodar: agendando callback principal, root={root}, winfo_exists={root.winfo_exists() if root else None}", file=sys.stderr)
        if not _agendar_na_ui(root, _aplicar):
            # Fallback: se não conseguir agendar na UI, executa direto (pode falhar se tocar widgets)
            try:
                _aplicar()
            except Exception as e:  # noqa: BLE001
                print(f"[db_async] erro no callback (fallback): {e}", file=sys.stderr)

        print(f"[db_async] _rodar: chamando _notificar_banner, erro={erro}, CALLBACK_BANNER={_CALLBACK_BANNER}", file=sys.stderr)
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