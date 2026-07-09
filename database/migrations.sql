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

