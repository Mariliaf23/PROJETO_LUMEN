-- -----------------------------------------------------
-- Schema biblioteca
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `biblioteca` DEFAULT CHARACTER SET utf8mb4;
USE `biblioteca`;

-- -----------------------------------------------------
-- Table `biblioteca`.`funcionario`
-- -----------------------------------------------------
-- Tabela responsável por armazenar os dados dos funcionários da biblioteca.
-- Cada funcionário possui uma função (diretor ou bibliotecário) que define seu
-- nível de acesso e permissões no sistema. A senha é armazenada como hash.
--
-- ALTERAÇÕES:
--   - Charset alterado de utf8 para utf8mb4 (suporte completo a Unicode).
--   - Removido UNIQUE INDEX redundante em id_funcionario (já é PK).
--   - Renomeado nome do índice de id_bibliotecario_UNIQUE para id_funcionario_UNIQUE.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`funcionario` (
  `id_funcionario` INT NOT NULL AUTO_INCREMENT,
  `nome_funcionario` VARCHAR(100) NOT NULL,
  `email_funcionario` VARCHAR(100) NOT NULL,
  `password_funcionario` VARCHAR(255) NOT NULL,
  `telefone_funcionario` CHAR(11) NOT NULL,
  `funcao` ENUM('diretor', 'bibliotecario') NOT NULL,
  PRIMARY KEY (`id_funcionario`),
  UNIQUE KEY `id_funcionario_UNIQUE` (`id_funcionario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`livro`
-- -----------------------------------------------------
-- Tabela que armazena o catálogo de livros disponíveis na biblioteca.
-- Cada livro possui um ISBN único, título, autor, categoria e status atual
-- (disponível, emprestado ou reservado).
--
-- ALTERAÇÕES:
--   - isbn alterado de INT para VARCHAR(13) para suportar ISBNs de até 13 dígitos.
--   - Coluna título renomeada para titulo (remoção de acento).
--   - Adicionado AUTO_INCREMENT em id_livro.
--   - Removido UNIQUE INDEX redundante em id_livro (já é PK).
--   - Renomeado nome do índice de id_generetor_UNIQUE para id_livro_UNIQUE.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`livro` (
  `id_livro` INT NOT NULL AUTO_INCREMENT,
  `titulo` VARCHAR(150) NOT NULL,
  `autor` VARCHAR(100) NOT NULL,
  `categoria` VARCHAR(30) NOT NULL,
  `isbn` VARCHAR(13) NOT NULL,
  `status_livro` ENUM('disponivel', 'emprestado', 'reservado') NOT NULL,
  PRIMARY KEY (`id_livro`),
  UNIQUE KEY `isbn_UNIQUE` (`isbn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`alunos`
-- -----------------------------------------------------
-- Tabela que armazena os dados dos alunos cadastrados no sistema.
-- Cada aluno possui dados pessoais (nome, email, telefone, CPF), informações
-- acadêmicas (sala e turno) e a data de cadastro no sistema.
--
-- ALTERAÇÕES:
--   - Removida a tabela duplicada de alunos que conflitava com esta.
--   - Adicionados campos cpf, sala, turno e criado_em.
--   - UNIQUE KEY aplicado diretamente nas colunas cpf, email e telefone.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`alunos` (
  `id_alunos` INT NOT NULL AUTO_INCREMENT,
  `nome_aluno` VARCHAR(100) NOT NULL,
  `email_aluno` VARCHAR(100) NOT NULL,
  `password_aluno` VARCHAR(255) NOT NULL,
  `telefone_aluno` CHAR(11) NOT NULL,
  `cpf` VARCHAR(14) NOT NULL,
  `sala` VARCHAR(10) DEFAULT NULL,
  `turno` VARCHAR(20) DEFAULT NULL,
  `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_alunos`),
  UNIQUE KEY `email_aluno_UNIQUE` (`email_aluno`),
  UNIQUE KEY `telefone_aluno_UNIQUE` (`telefone_aluno`),
  UNIQUE KEY `cpf_UNIQUE` (`cpf`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`emprestimo`
-- -----------------------------------------------------
-- Tabela que registra os empréstimos de livros realizados na biblioteca.
-- Cada empréstimo é vinculado a um aluno e ao funcionário que realizou o
-- atendimento. Contém as datas de lançamento (empréstimo) e vencimento (devolução),
-- além do status atual.
--
-- ALTERAÇÕES:
--   - Corrigida a chave primária: antes era composta por 3 colunas, o que
--     impedia que um aluno tivesse mais de um empréstimo. Agora a PK é apenas
--     id_emprestimo.
--   - Coluna lançamento renomeada para lancamento (remoção de acento).
--   - Removido UNIQUE INDEX redundante (id_emprestimo já é PK).
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`emprestimo` (
  `id_emprestimo` INT NOT NULL AUTO_INCREMENT,
  `lancamento` DATE NOT NULL,
  `vencimento` DATE NOT NULL,
  `status_emprestimo` ENUM('ativo', 'finalizado', 'atrasado') NOT NULL,
  `alunos_id_alunos` INT NOT NULL,
  `funcionario_id_funcionario` INT NOT NULL,
  PRIMARY KEY (`id_emprestimo`),
  INDEX `fk_emprestimo_alunos1_idx` (`alunos_id_alunos`),
  INDEX `fk_emprestimo_funcionario1_idx` (`funcionario_id_funcionario`),
  CONSTRAINT `fk_emprestimo_alunos1`
    FOREIGN KEY (`alunos_id_alunos`)
    REFERENCES `biblioteca`.`alunos` (`id_alunos`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_emprestimo_funcionario1`
    FOREIGN KEY (`funcionario_id_funcionario`)
    REFERENCES `biblioteca`.`funcionario` (`id_funcionario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`emprestimo_has_livro`
-- -----------------------------------------------------
-- Tabela de junção (N:N) entre empréstimos e livros.
-- Cada empréstimo pode conter vários livros, e cada livro pode aparecer em
-- vários empréstimos ao longo do tempo. Permite rastrear quais livros foram
-- incluídos em cada empréstimo.
--
-- ALTERAÇÕES:
--   - Foreign key corrigida para referenciar corretamente a PK id_emprestimo.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`emprestimo_has_livro` (
  `emprestimo_id_emprestimo` INT NOT NULL,
  `livro_id_livro` INT NOT NULL,
  PRIMARY KEY (`emprestimo_id_emprestimo`, `livro_id_livro`),
  INDEX `fk_emprestimo_has_livro_livro1_idx` (`livro_id_livro`),
  INDEX `fk_emprestimo_has_livro_emprestimo_idx` (`emprestimo_id_emprestimo`),
  CONSTRAINT `fk_emprestimo_has_livro_emprestimo`
    FOREIGN KEY (`emprestimo_id_emprestimo`)
    REFERENCES `biblioteca`.`emprestimo` (`id_emprestimo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_emprestimo_has_livro_livro1`
    FOREIGN KEY (`livro_id_livro`)
    REFERENCES `biblioteca`.`livro` (`id_livro`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
