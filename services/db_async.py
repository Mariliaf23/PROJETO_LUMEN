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


_CALLBACK_BANNER = None


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


def carregar_em_fundo(root, fn_coleta, callback):
    """Executa fn_coleta numa daemon thread e chama callback(dados, erro).

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
                print(f"[db_async] erro no callback: {e}")

        try:
            if root is not None and root.winfo_exists():
                root.after(0, _aplicar)
            else:
                _aplicar()
        except Exception:
            _aplicar()

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

    try:
        if root is not None and root.winfo_exists():
            root.after(0, _aplicar)
        else:
            _aplicar()
    except Exception:
        _aplicar()