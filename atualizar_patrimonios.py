"""
atualizar_patrimonios.py - Atualiza todos os códigos de patrimônio para o formato PAT-XXXXX
"""

import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error


def atualizar_patrimonios():
    """Atualiza todos os códigos de patrimônio para o formato PAT-XXXXX (5 dígitos)."""

    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path, override=True)

    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '')
    }
    DB_NAME = os.getenv('DB_NAME', 'biblioteca')

    try:
        print("🔄 Atualizando códigos de patrimônio...")

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(f"USE {DB_NAME}")

        # Busca todos os exemplares
        cursor.execute("""
            SELECT e.id_exemplar, e.codigo_patrimonio, e.id_livro, l.titulo
            FROM exemplar e
            JOIN livro l ON e.id_livro = l.id_livro
            ORDER BY e.id_exemplar
        """)
        exemplares = cursor.fetchall()

        print(f"📋 Encontrados {len(exemplares)} exemplares")

        # Usa um contador global para garantir unicidade
        contador_global = 1
        updates = []

        for id_exc, codigo_atual, id_livro, titulo in exemplares:
            novo_codigo = f"PAT-{contador_global:05d}"
            contador_global += 1

            # Só atualiza se o código mudou
            if codigo_atual != novo_codigo:
                updates.append((novo_codigo, id_exc))
                print(f"  [{titulo}] {codigo_atual} → {novo_codigo}")

        if updates:
            print(f"\n📝 Atualizando {len(updates)} códigos...")

            # Primeiro, limpa todos os patrimônios para evitar conflitos
            for i, (novo_codigo, id_exc) in enumerate(updates):
                temp_code = f"TEMP-{i:05d}"
                cursor.execute(
                    "UPDATE exemplar SET codigo_patrimonio = %s WHERE id_exemplar = %s",
                    (temp_code, id_exc)
                )

            # Agora atribui os códigos corretos
            for novo_codigo, id_exc in updates:
                cursor.execute(
                    "UPDATE exemplar SET codigo_patrimonio = %s WHERE id_exemplar = %s",
                    (novo_codigo, id_exc)
                )

            conn.commit()
            print(f"✅ {len(updates)} códigos atualizados com sucesso!")
        else:
            print("✅ Todos os códigos já estão no formato correto!")

        conn.close()
        return True

    except Error as e:
        print(f"❌ Erro ao atualizar patrimônios: {e}")
        return False


if __name__ == "__main__":
    atualizar_patrimonios()
