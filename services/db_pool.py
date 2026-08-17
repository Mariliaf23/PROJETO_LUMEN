# db_pool.py — Pool de conexões MySQL
#
# PROBLEMA RESOLVIDO:
# Antes, CADA consulta abria uma conexão nova (TCP + TLS + handshake MySQL)
# com o servidor remoto (Aiven), o que travava a interface por vários
# segundos (e ~60s com rede lenta, pois várias consultas rodavam em
# sequência). Com o pool, as conexões ficam abertas e são reutilizadas:
# obter uma conexão custa milissegundos em vez de segundos.

import os
import threading
import time
import mysql.connector
from mysql.connector import pooling
from services.conector import DB_CONFIG

_POOL = None
_POOL_LOCK = threading.Lock()
_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '8'))

# Etapa 1 (diagnóstico): imprime o tempo gasto para obter cada conexão.
# Mantenha como '1' enquanto estiver validando a melhoria; depois pode
# desligar no .env (DB_LOG_TEMPOS=0).
_LOG_TEMPOS = os.getenv('DB_LOG_TEMPOS', '1') == '1'


def _criar_pool():
    """Cria o pool de conexões uma única vez (thread-safe)."""
    global _POOL
    with _POOL_LOCK:
        if _POOL is None:
            cfg = dict(DB_CONFIG)
            _POOL = pooling.MySQLConnectionPool(
                pool_name="lumen",
                pool_size=_POOL_SIZE,
                pool_reset_session=False,   # desabilita o reset de sessão a cada devolução (economia de ~1s por query)
                **cfg,
            )
    return _POOL


def obter_conexao():
    """Retorna uma conexão do pool (ou avulsa, se o pool estiver esgotado).

    O chamador deve usar conn.close() ao terminar — isso devolve a conexão
    ao pool em vez de fechá-la de verdade (as funções do sistema já fazem
    isso em todos os lugares).
    """
    t0 = time.perf_counter()
    try:
        pool = _criar_pool()
        conn = pool.get_connection()
    except Exception:
        # Pool esgotado ou falha momentânea: cria conexão avulsa
        conn = mysql.connector.connect(**DB_CONFIG)
    dt = (time.perf_counter() - t0) * 1000
    if _LOG_TEMPOS and dt > 15:
        print(f"[db_pool] conexão obtida em {dt:.0f}ms")
    return conn


def aquecer_pool():
    """Abre as conexões do pool em threads paralelas (daemon), em background.

    Sem isso, cada primeira consulta abre uma conexão nova (TCP + TLS +
    handshake até o servidor remoto), demorando 10s+ por conexão. Com o
    aquecimento, o pool já vem cheio e o primeiro uso sai em milissegundos.
    Falhas são silenciosas: o pool continua sendo preenchido sob demanda.
    """
    import threading

    def _abrir():
        try:
            conn = obter_conexao()
            conn.close()
        except Exception:
            pass

    threads = [threading.Thread(target=_abrir, daemon=True) for _ in range(max(_POOL_SIZE, 1))]
    for t in threads:
        t.start()


def esvaziar_pool():
    """Fecha todas as conexões do pool (útil ao trocar config de banco)."""
    global _POOL
    with _POOL_LOCK:
        if _POOL is not None:
            try:
                _POOL = None
            except Exception:
                pass
