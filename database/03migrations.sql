-- =====================================================
-- Migração 005: Código estável da carteirinha
-- =====================================================
-- Adiciona a coluna 'codigo_carteirinha' na tabela usuario.
-- O código (ex: BIB-7F3A91C2D4) é gerado uma única vez e persistido,
-- evitando que PDFs de carteirinhas sejam duplicados a cada clique
-- no botão "Carteirinhas".

USE `LUMENDB`;

-- Aumenta timeouts da SESSÃO para o ALTER TABLE não ser abortado
-- (erro 2013 "Lost connection" após 30s = net_read_timeout do servidor).
-- Rodar o script inteiro de uma vez para valer na mesma conexão.
SET SESSION net_read_timeout = 3600;
SET SESSION net_write_timeout = 3600;
SET SESSION wait_timeout = 3600;
SET SESSION interactive_timeout = 3600;
SET SESSION lock_wait_timeout = 3600;

-- Adiciona a coluna codigo_carteirinha (verifica se já existe)
-- ALGORITHM=INSTANT: adição instantânea no MySQL 8.0.12+ (sem rebuild da tabela)
SET @existe = (SELECT COUNT(*) FROM information_schema.COLUMNS
               WHERE TABLE_SCHEMA = 'LUMENDB' AND TABLE_NAME = 'usuario' AND COLUMN_NAME = 'codigo_carteirinha');
SET @sql = IF(@existe = 0,
              'ALTER TABLE `usuario` ADD COLUMN `codigo_carteirinha` VARCHAR(20) DEFAULT NULL AFTER `matricula`, ALGORITHM=INSTANT',
              'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Adiciona índice UNIQUE em codigo_carteirinha (verifica se já existe)
SET @existe_idx = (SELECT COUNT(*) FROM information_schema.STATISTICS
                   WHERE TABLE_SCHEMA = 'LUMENDB' AND TABLE_NAME = 'usuario' AND INDEX_NAME = 'codigo_carteirinha_UNIQUE');
SET @sql_idx = IF(@existe_idx = 0,
                  'ALTER TABLE `usuario` ADD UNIQUE KEY `codigo_carteirinha_UNIQUE` (`codigo_carteirinha`)',
                  'SELECT 1');
PREPARE stmt_idx FROM @sql_idx;
EXECUTE stmt_idx;
DEALLOCATE PREPARE stmt_idx;
