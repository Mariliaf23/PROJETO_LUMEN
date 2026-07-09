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
