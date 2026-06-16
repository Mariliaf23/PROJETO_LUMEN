-- -----------------------------------------------------
-- Schema biblioteca
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `biblioteca` DEFAULT CHARACTER SET utf8 ;
USE `biblioteca` ;

-- -----------------------------------------------------
-- Table `biblioteca`.`funcionario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`funcionario` (
  `id_funcionario` INT NOT NULL AUTO_INCREMENT,
  `nome_funcionario` VARCHAR(100) NOT NULL,
  `email_funcionario` VARCHAR(100) NOT NULL,
  `password_funcionario` VARCHAR(255) NOT NULL,
  `telefone_funcionario` CHAR(11) NOT NULL,
  `funcao` ENUM('diretor', 'bibliotecario') NOT NULL,
  PRIMARY KEY (`id_funcionario`),
  UNIQUE INDEX `id_bibliotecario_UNIQUE` (`id_funcionario` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `biblioteca`.`livro`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`livro` (
  `id_livro` INT NOT NULL,
  `título` VARCHAR(150) NOT NULL,
  `autor` VARCHAR(100) NOT NULL,
  `categoria` VARCHAR(30) NOT NULL,
  `isbn` INT NOT NULL,
  `status_livro` ENUM('disponivel', 'emprestado', 'reservado') NOT NULL,
  PRIMARY KEY (`id_livro`),
  UNIQUE INDEX `isbn_UNIQUE` (`isbn` ASC) VISIBLE,
  UNIQUE INDEX `id_generetor_UNIQUE` (`id_livro` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `biblioteca`.`alunos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`alunos` (
  `id_alunos` INT NOT NULL AUTO_INCREMENT,
  `nome_aluno` VARCHAR(100) NOT NULL,
  `email_aluno` VARCHAR(100) NOT NULL,
  `password_aluno` VARCHAR(255) NOT NULL,
  `telefone_aluno` CHAR(11) NOT NULL,
  PRIMARY KEY (`id_alunos`),
  UNIQUE INDEX `id_alunos_UNIQUE` (`id_alunos` ASC) VISIBLE,
  UNIQUE INDEX `email_aluno_UNIQUE` (`email_aluno` ASC) VISIBLE,
  UNIQUE INDEX `telefone_aluno_UNIQUE` (`telefone_aluno` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `biblioteca`.`emprestimo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`emprestimo` (
  `id_emprestimo` INT NOT NULL AUTO_INCREMENT,
  `lançamento` DATE NOT NULL,
  `vencimento` DATE NOT NULL,
  `status_emprestimo` ENUM('ativo', 'finalizado', 'atrasado') NOT NULL,
  `alunos_id_alunos` INT NOT NULL,
  `funcionario_id_funcionario` INT NOT NULL,
  PRIMARY KEY (`id_emprestimo`, `alunos_id_alunos`, `funcionario_id_funcionario`),
  UNIQUE INDEX `id_emprestimo_UNIQUE` (`id_emprestimo` ASC) VISIBLE,
  INDEX `fk_emprestimo_alunos1_idx` (`alunos_id_alunos` ASC) VISIBLE,
  INDEX `fk_emprestimo_funcionario1_idx` (`funcionario_id_funcionario` ASC) VISIBLE,
  CONSTRAINT `fk_emprestimo_alunos1`
    FOREIGN KEY (`alunos_id_alunos`)
    REFERENCES `biblioteca`.`alunos` (`id_alunos`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_emprestimo_funcionario1`
    FOREIGN KEY (`funcionario_id_funcionario`)
    REFERENCES `biblioteca`.`funcionario` (`id_funcionario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `biblioteca`.`emprestimo_has_livro`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `biblioteca`.`emprestimo_has_livro` (
  `emprestimo_id_emprestimo` INT NOT NULL,
  `livro_id_livro` INT NOT NULL,
  PRIMARY KEY (`emprestimo_id_emprestimo`, `livro_id_livro`),
  INDEX `fk_emprestimo_has_livro_livro1_idx` (`livro_id_livro` ASC) VISIBLE,
  INDEX `fk_emprestimo_has_livro_emprestimo_idx` (`emprestimo_id_emprestimo` ASC) VISIBLE,
  CONSTRAINT `fk_emprestimo_has_livro_emprestimo`
    FOREIGN KEY (`emprestimo_id_emprestimo`)
    REFERENCES `biblioteca`.`emprestimo` (`id_emprestimo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_emprestimo_has_livro_livro1`
    FOREIGN KEY (`livro_id_livro`)
    REFERENCES `biblioteca`.`livro` (`id_livro`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;
