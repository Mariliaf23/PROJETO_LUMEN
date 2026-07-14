"""
run_migrations.py - Executa migrações SQL no banco de dados
"""

import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error


def run_migrations():
    """Executa as migrações para adicionar suporte a empréstimo multi-livro"""

    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path, override=True)

    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '')
    }
    DB_NAME = os.getenv('DB_NAME', 'biblioteca')

    try:
        print("🔄 Iniciando migrações do banco de dados...")

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(f"USE {DB_NAME}")

        # 1. Cria tabela grupo_emprestimo se não existir
        print("📋 Criando tabela grupo_emprestimo...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `grupo_emprestimo` (
                `id_grupo` INT NOT NULL AUTO_INCREMENT,
                `id_usuario` INT NOT NULL,
                `id_funcionario` INT NOT NULL,
                `data_emprestimo` DATE NOT NULL,
                `data_prevista` DATE NOT NULL,
                `data_devolucao` DATE DEFAULT NULL,
                `status` ENUM('ativo', 'finalizado', 'atrasado') NOT NULL DEFAULT 'ativo',
                PRIMARY KEY (`id_grupo`),
                INDEX `fk_grupo_usuario_idx` (`id_usuario`),
                INDEX `fk_grupo_funcionario_idx` (`id_funcionario`),
                CONSTRAINT `fk_grupo_usuario`
                    FOREIGN KEY (`id_usuario`)
                    REFERENCES `usuario` (`id_usuario`)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE,
                CONSTRAINT `fk_grupo_funcionario`
                    FOREIGN KEY (`id_funcionario`)
                    REFERENCES `usuario` (`id_usuario`)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✓ Tabela grupo_emprestimo criada/verificada")

        # 2. Adiciona coluna id_grupo na tabela emprestimo
        print("📋 Verificando coluna id_grupo na tabela emprestimo...")
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'emprestimo' AND COLUMN_NAME = 'id_grupo'
        """, (DB_NAME,))
        resultado = cursor.fetchone()

        if resultado[0] == 0:
            print("📋 Adicionando coluna id_grupo...")
            cursor.execute("""
                ALTER TABLE `emprestimo`
                ADD COLUMN `id_grupo` INT DEFAULT NULL AFTER `id_funcionario`
            """)
            print("✓ Coluna id_grupo adicionada")
        else:
            print("⏭ Coluna id_grupo já existe")

        # 3. Adiciona index para id_grupo
        print("📋 Verificando index fk_emprestimo_grupo_idx...")
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'emprestimo' AND INDEX_NAME = 'fk_emprestimo_grupo_idx'
        """, (DB_NAME,))
        resultado = cursor.fetchone()

        if resultado[0] == 0:
            print("📋 Adicionando index fk_emprestimo_grupo_idx...")
            cursor.execute("""
                ALTER TABLE `emprestimo`
                ADD INDEX `fk_emprestimo_grupo_idx` (`id_grupo`)
            """)
            print("✓ Index criado")
        else:
            print("⏭ Index já existe")

        # 4. Adiciona constraint de chave estrangeira
        print("📋 Verificando constraint fk_emprestimo_grupo...")
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'emprestimo' AND CONSTRAINT_NAME = 'fk_emprestimo_grupo'
        """, (DB_NAME,))
        resultado = cursor.fetchone()

        if resultado[0] == 0:
            print("📋 Adicionando constraint fk_emprestimo_grupo...")
            cursor.execute("""
                ALTER TABLE `emprestimo`
                ADD CONSTRAINT `fk_emprestimo_grupo`
                    FOREIGN KEY (`id_grupo`)
                    REFERENCES `grupo_emprestimo` (`id_grupo`)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE
            """)
            print("✓ Constraint criada")
        else:
            print("⏭ Constraint já existe")

        conn.commit()
        conn.close()

        print("\n✅ Migrações aplicadas com sucesso!")
        return True

    except Error as e:
        print(f"❌ Erro ao executar migração: {e}")
        return False


if __name__ == "__main__":
    run_migrations()
