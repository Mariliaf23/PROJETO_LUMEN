-- Migração 001: Adiciona coluna 'turma' à tabela usuario
-- Esta migração foi criada para corrigir o erro: "Unknown column 'turma' in 'field list'"

USE `biblioteca`;

-- Adiciona a coluna 'turma' se ela não existir
ALTER TABLE `usuario` 
ADD COLUMN IF NOT EXISTS `turma` VARCHAR(10) DEFAULT NULL;

-- Adiciona a coluna 'turno' se ela não existir
ALTER TABLE `usuario`
ADD COLUMN IF NOT EXISTS `turno` VARCHAR(20) DEFAULT NULL;

-- Adiciona a coluna 'funcao' se ela não existir  
ALTER TABLE `usuario`
ADD COLUMN IF NOT EXISTS `funcao` VARCHAR(50) DEFAULT NULL;

-- Migração 003: Cria tabela turma e migra dados existentes
CREATE TABLE IF NOT EXISTS `biblioteca`.`turma` (
  `id_turma` INT NOT NULL AUTO_INCREMENT,
  `codigo` VARCHAR(20) NOT NULL,
  `turno` ENUM('Manhã', 'Tarde', 'Noite', 'Integral') NOT NULL,
  PRIMARY KEY (`id_turma`),
  UNIQUE KEY `codigo_turno_UNIQUE` (`codigo`, `turno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `usuario`
ADD COLUMN IF NOT EXISTS `id_turma` INT DEFAULT NULL,
ADD CONSTRAINT `fk_usuario_turma`
  FOREIGN KEY IF NOT EXISTS (`id_turma`)
  REFERENCES `biblioteca`.`turma` (`id_turma`)
  ON DELETE SET NULL ON UPDATE CASCADE;

-- Migração 002: Corrige datas_prevista inválidas nos empréstimos
-- Esta migração corrige registros com data_prevista inválida (ex: "1" ou valores não-data)

-- Atualiza empréstimos com data_prevista que é número ou inválida
-- Se data_prevista não é uma data válida, define como data_emprestimo + 14 dias
UPDATE `emprestimo`
SET `data_prevista` = DATE_ADD(`data_emprestimo`, INTERVAL 14 DAY)
WHERE `data_prevista` IS NULL
   OR `data_prevista` = ''
   OR `data_prevista` NOT LIKE '____-__-__'
   OR STR_TO_DATE(`data_prevista`, '%Y-%m-%d') IS NULL;


-- =====================================================
-- Migração 004: Empréstimo Multi-Livro (grupo_emprestimo)
-- =====================================================

-- Cria tabela de grupo de empréstimos
CREATE TABLE IF NOT EXISTS `biblioteca`.`grupo_emprestimo` (
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
    REFERENCES `biblioteca`.`usuario` (`id_usuario`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_grupo_funcionario`
    FOREIGN KEY (`id_funcionario`)
    REFERENCES `biblioteca`.`usuario` (`id_usuario`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Adiciona coluna id_grupo na tabela emprestimo (verifica se já existe)
SET @existe = (SELECT COUNT(*) FROM information_schema.COLUMNS
               WHERE TABLE_SCHEMA = 'biblioteca' AND TABLE_NAME = 'emprestimo' AND COLUMN_NAME = 'id_grupo');
SET @sql = IF(@existe = 0, 'ALTER TABLE `emprestimo` ADD COLUMN `id_grupo` INT DEFAULT NULL AFTER `id_funcionario`', 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Adiciona index para id_grupo (verifica se já existe)
SET @existe_idx = (SELECT COUNT(*) FROM information_schema.STATISTICS
                   WHERE TABLE_SCHEMA = 'biblioteca' AND TABLE_NAME = 'emprestimo' AND INDEX_NAME = 'fk_emprestimo_grupo_idx');
SET @sql_idx = IF(@existe_idx = 0, 'ALTER TABLE `emprestimo` ADD INDEX `fk_emprestimo_grupo_idx` (`id_grupo`)', 'SELECT 1');
PREPARE stmt_idx FROM @sql_idx;
EXECUTE stmt_idx;
DEALLOCATE PREPARE stmt_idx;

-- Adiciona constraint de chave estrangeira (verifica se já existe)
SET @existe_fk = (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
                  WHERE TABLE_SCHEMA = 'biblioteca' AND TABLE_NAME = 'emprestimo' AND CONSTRAINT_NAME = 'fk_emprestimo_grupo');
SET @sql_fk = IF(@existe_fk = 0, 'ALTER TABLE `emprestimo` ADD CONSTRAINT `fk_emprestimo_grupo` FOREIGN KEY (`id_grupo`) REFERENCES `biblioteca`.`grupo_emprestimo` (`id_grupo`) ON DELETE SET NULL ON UPDATE CASCADE', 'SELECT 1');
PREPARE stmt_fk FROM @sql_fk;
EXECUTE stmt_fk;
DEALLOCATE PREPARE stmt_fk;

