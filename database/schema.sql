-- -----------------------------------------------------
-- Schema biblioteca
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `biblioteca` DEFAULT CHARACTER SET utf8mb4;
USE `biblioteca`;

-- -----------------------------------------------------
-- Table `biblioteca`.`turma`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`turma` (
  `id_turma` INT NOT NULL AUTO_INCREMENT,
  `codigo` VARCHAR(20) NOT NULL,
  `turno` ENUM('Manhã', 'Tarde', 'Noite', 'Integral') NOT NULL,
  PRIMARY KEY (`id_turma`),
  UNIQUE KEY `codigo_turno_UNIQUE` (`codigo`, `turno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Table `biblioteca`.`usuario`
-- -----------------------------------------------------
-- Tabela unificada de usuarios: alunos, professores, funcionarios e bibliotecarios.
-- Substitui as tabelas antigas 'funcionario' e 'alunos'.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`usuario` (
  `id_usuario` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `senha` VARCHAR(255) NOT NULL,
  `telefone` CHAR(11) DEFAULT NULL,
  `cpf` VARCHAR(14) DEFAULT NULL,
  `tipo_usuario` ENUM('diretor', 'bibliotecario', 'aluno', 'professor') NOT NULL,
  `matricula` VARCHAR(20) DEFAULT NULL,
  `turma` VARCHAR(10) DEFAULT NULL,
  `turno` VARCHAR(20) DEFAULT NULL,
  `id_turma` INT DEFAULT NULL,
  `funcao` VARCHAR(50) DEFAULT NULL,
  `status` ENUM('ativo', 'inativo', 'bloqueado', 'suspenso') NOT NULL DEFAULT 'ativo',
  `data_suspensao` DATE DEFAULT NULL,
  `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `cpf_UNIQUE` (`cpf`),
  UNIQUE KEY `matricula_UNIQUE` (`matricula`),
  INDEX `fk_usuario_turma_idx` (`id_turma`),
  CONSTRAINT `fk_usuario_turma`
    FOREIGN KEY (`id_turma`)
    REFERENCES `biblioteca`.`turma` (`id_turma`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- Table `biblioteca`.`categoria`
-- -----------------------------------------------------
-- Categorias de livros (genero/assunto).
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`categoria` (
  `id_categoria` INT NOT NULL AUTO_INCREMENT,
  `nome_categoria` VARCHAR(50) NOT NULL,
  `descricao` TEXT DEFAULT NULL,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nome_categoria_UNIQUE` (`nome_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`autor`
-- -----------------------------------------------------
-- Autores de livros.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`autor` (
  `id_autor` INT NOT NULL AUTO_INCREMENT,
  `nome_autor` VARCHAR(100) NOT NULL,
  `nacionalidade` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`id_autor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`livro`
-- -----------------------------------------------------
-- Catalogo de livros da biblioteca.
-- Cada livro pertence a uma categoria e pode ter multiplos autores.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`livro` (
  `id_livro` INT NOT NULL AUTO_INCREMENT,
  `titulo` VARCHAR(150) NOT NULL,
  `isbn` VARCHAR(13) NOT NULL,
  `editora` VARCHAR(100) DEFAULT NULL,
  `ano_publicacao` YEAR DEFAULT NULL,
  `sinopse` TEXT DEFAULT NULL,
  `id_categoria` INT NOT NULL,
  `status_livro` ENUM('disponivel', 'indisponivel') NOT NULL DEFAULT 'disponivel',
  PRIMARY KEY (`id_livro`),
  UNIQUE KEY `isbn_UNIQUE` (`isbn`),
  INDEX `fk_livro_categoria_idx` (`id_categoria`),
  CONSTRAINT `fk_livro_categoria`
    FOREIGN KEY (`id_categoria`)
    REFERENCES `biblioteca`.`categoria` (`id_categoria`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`livro_autor`
-- -----------------------------------------------------
-- Tabela de juncao N:N entre livros e autores.
-- Um livro pode ter varios autores, um autor pode escrever varios livros.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`livro_autor` (
  `id_livro` INT NOT NULL,
  `id_autor` INT NOT NULL,
  PRIMARY KEY (`id_livro`, `id_autor`),
  INDEX `fk_livro_autor_autor_idx` (`id_autor`),
  CONSTRAINT `fk_livro_autor_livro`
    FOREIGN KEY (`id_livro`)
    REFERENCES `biblioteca`.`livro` (`id_livro`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_livro_autor_autor`
    FOREIGN KEY (`id_autor`)
    REFERENCES `biblioteca`.`autor` (`id_autor`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`exemplar`
-- -----------------------------------------------------
-- Copias fisicas de cada livro.
-- Um titulo pode ter varios exemplares (copias) em diferentes status.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`exemplar` (
  `id_exemplar` INT NOT NULL AUTO_INCREMENT,
  `codigo_patrimonio` VARCHAR(30) NOT NULL,
  `status_exemplar` ENUM('disponivel', 'emprestado', 'reservado', 'manutencao') NOT NULL DEFAULT 'disponivel',
  `localizacao` VARCHAR(50) DEFAULT NULL,
  `id_livro` INT NOT NULL,
  PRIMARY KEY (`id_exemplar`),
  UNIQUE KEY `codigo_patrimonio_UNIQUE` (`codigo_patrimonio`),
  INDEX `fk_exemplar_livro_idx` (`id_livro`),
  CONSTRAINT `fk_exemplar_livro`
    FOREIGN KEY (`id_livro`)
    REFERENCES `biblioteca`.`livro` (`id_livro`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`grupo_emprestimo`
-- -----------------------------------------------------
-- Agrupa multiplos emprestimos de um mesmo usuario.
-- Permite emprestimo multi-livro (ate 3 exemplares).
-- -----------------------------------------------------
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


-- -----------------------------------------------------
-- Table `biblioteca`.`emprestimo`
-- -----------------------------------------------------
-- Registro de emprestimos de exemplares.
-- Cada emprestimo vincula um usuario a um exemplar especifico.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`emprestimo` (
  `id_emprestimo` INT NOT NULL AUTO_INCREMENT,
  `data_emprestimo` DATE NOT NULL,
  `data_prevista` DATE NOT NULL,
  `data_devolucao` DATE DEFAULT NULL,
  `status` ENUM('ativo', 'finalizado', 'atrasado') NOT NULL DEFAULT 'ativo',
  `id_usuario` INT NOT NULL,
  `id_exemplar` INT NOT NULL,
  `id_funcionario` INT NOT NULL,
  `id_grupo` INT DEFAULT NULL,
  PRIMARY KEY (`id_emprestimo`),
  INDEX `fk_emprestimo_usuario_idx` (`id_usuario`),
  INDEX `fk_emprestimo_exemplar_idx` (`id_exemplar`),
  INDEX `fk_emprestimo_funcionario_idx` (`id_funcionario`),
  INDEX `fk_emprestimo_grupo_idx` (`id_grupo`),
  CONSTRAINT `fk_emprestimo_usuario`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `biblioteca`.`usuario` (`id_usuario`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_emprestimo_exemplar`
    FOREIGN KEY (`id_exemplar`)
    REFERENCES `biblioteca`.`exemplar` (`id_exemplar`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_emprestimo_funcionario`
    FOREIGN KEY (`id_funcionario`)
    REFERENCES `biblioteca`.`usuario` (`id_usuario`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_emprestimo_grupo`
    FOREIGN KEY (`id_grupo`)
    REFERENCES `biblioteca`.`grupo_emprestimo` (`id_grupo`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`reserva`
-- -----------------------------------------------------
-- Reservas de livros por usuarios.
-- Um usuario pode reservar um livro que esta indisponivel.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`reserva` (
  `id_reserva` INT NOT NULL AUTO_INCREMENT,
  `data_reserva` DATE NOT NULL,
  `data_validade` DATE NOT NULL,
  `status` ENUM('ativa', 'atendida', 'cancelada', 'expirada') NOT NULL DEFAULT 'ativa',
  `id_usuario` INT NOT NULL,
  `id_livro` INT NOT NULL,
  PRIMARY KEY (`id_reserva`),
  INDEX `fk_reserva_usuario_idx` (`id_usuario`),
  INDEX `fk_reserva_livro_idx` (`id_livro`),
  CONSTRAINT `fk_reserva_usuario`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `biblioteca`.`usuario` (`id_usuario`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_reserva_livro`
    FOREIGN KEY (`id_livro`)
    REFERENCES `biblioteca`.`livro` (`id_livro`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Table `biblioteca`.`multa`
-- -----------------------------------------------------
-- Multas geradas por atraso ou dano.
-- Vinculada a um emprestimo especifico.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`multa` (
  `id_multa` INT NOT NULL AUTO_INCREMENT,
  `valor` DECIMAL(10,2) NOT NULL,
  `dias_atraso` INT NOT NULL DEFAULT 0,
  `motivo` ENUM('atraso', 'dano', 'perda') NOT NULL DEFAULT 'atraso',
  `status_pagamento` ENUM('pendente', 'pago', 'isento') NOT NULL DEFAULT 'pendente',
  `data_geracao` DATE NOT NULL,
  `id_emprestimo` INT NOT NULL,
  PRIMARY KEY (`id_multa`),
  INDEX `fk_multa_emprestimo_idx` (`id_emprestimo`),
  CONSTRAINT `fk_multa_emprestimo`
    FOREIGN KEY (`id_emprestimo`)
    REFERENCES `biblioteca`.`emprestimo` (`id_emprestimo`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------
-- Dados iniciais: categorias
-- -----------------------------------------------------
INSERT INTO `biblioteca`.`categoria` (`nome_categoria`) VALUE
('Matemática'),
('Português'),
('Ciências'),
('História'),
('Geografia'),
('Literatura Infantil'),
('Literatura Juvenil'),
('Literatura Brasileira'),
('Informática'),
('Dicionários'),
('Enciclopédias'),
('Artes'),
('Educação Física'),
('Filosofia'),
('Sociologia'),
('Cultura Paraense'),
('Amazônia'),
('Educação Financeira'),
('Inclusão e Acessibilidade'),
('Romance'),
('Literatura classica');


