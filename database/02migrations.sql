-- Migração 02: Livros de exemplo e exemplares (seed inicial)
-- Insere livros de exemplo e suas cópias físicas (exemplares) com patrimônio PAT-XXXXX.
-- Todo o script é idempotente: pode ser executado novamente sem gerar duplicatas.

USE `LUMENDB`;

-- Garante que a tabela exemplar exista antes de popular
CREATE TABLE IF NOT EXISTS `LUMENDB`.`exemplar` (
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
    REFERENCES `LUMENDB`.`livro` (`id_livro`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Livros de exemplo (ISBNs sintéticos, sem conflito com acervo real)
-- =====================================================
INSERT INTO `LUMENDB`.`livro` (`titulo`, `isbn`, `editora`, `ano_publicacao`, `sinopse`, `id_categoria`)
SELECT 'Matemática Aplicada no Cotidiano', '9788500000001', 'Editora Moderna', 2018,
       'A matemática presente em situações do dia a dia, com exercícios práticos.',
       c.id_categoria
FROM `LUMENDB`.`categoria` c
WHERE c.nome_categoria = 'Matemática'
  AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000001');

INSERT INTO `LUMENDB`.`livro` (`titulo`, `isbn`, `editora`, `ano_publicacao`, `sinopse`, `id_categoria`)
SELECT 'Gramática Essencial da Língua Portuguesa', '9788500000002', 'Editora Ática', 2020,
       'Manual completo de gramática com exercícios e exemplos.',
       c.id_categoria
FROM `LUMENDB`.`categoria` c
WHERE c.nome_categoria = 'Português'
  AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000002');

INSERT INTO `LUMENDB`.`livro` (`titulo`, `isbn`, `editora`, `ano_publicacao`, `sinopse`, `id_categoria`)
SELECT 'História do Brasil Colônia', '9788500000003', 'Editora Saraiva', 2019,
       'Panorama do período colonial brasileiro, do descobrimento à independência.',
       c.id_categoria
FROM `LUMENDB`.`categoria` c
WHERE c.nome_categoria = 'História'
  AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000003');

INSERT INTO `LUMENDB`.`livro` (`titulo`, `isbn`, `editora`, `ano_publicacao`, `sinopse`, `id_categoria`)
SELECT 'O Sítio do Picapau Amarelo', '9788500000004', 'Editora Globo', 2005,
       'As aventuras de Emília, Pedrinho e a turma do Sítio do Picapau Amarelo.',
       c.id_categoria
FROM `LUMENDB`.`categoria` c
WHERE c.nome_categoria = 'Literatura Infantil'
  AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000004');

INSERT INTO `LUMENDB`.`livro` (`titulo`, `isbn`, `editora`, `ano_publicacao`, `sinopse`, `id_categoria`)
SELECT 'Vidas Secas', '9788500000005', 'Editora Record', 2008,
       'A dura vida de uma família de retirantes no sertão nordestino.',
       c.id_categoria
FROM `LUMENDB`.`categoria` c
WHERE c.nome_categoria = 'Literatura Brasileira'
  AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000005');

INSERT INTO `LUMENDB`.`livro` (`titulo`, `isbn`, `editora`, `ano_publicacao`, `sinopse`, `id_categoria`)
SELECT 'Atlas do Corpo Humano', '9788500000006', 'Editora Moderna', 2017,
       'Guia ilustrado dos sistemas do corpo humano.',
       c.id_categoria
FROM `LUMENDB`.`categoria` c
WHERE c.nome_categoria = 'Ciências'
  AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000006');

INSERT INTO `LUMENDB`.`livro` (`titulo`, `isbn`, `editora`, `ano_publicacao`, `sinopse`, `id_categoria`)
SELECT 'Introdução à Programação Python', '9788500000007', 'Editora Novatec', 2021,
       'Fundamentos de programação com a linguagem Python para iniciantes.',
       c.id_categoria
FROM `LUMENDB`.`categoria` c
WHERE c.nome_categoria = 'Informática'
  AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000007');

INSERT INTO `LUMENDB`.`livro` (`titulo`, `isbn`, `editora`, `ano_publicacao`, `sinopse`, `id_categoria`)
SELECT 'Amazônia: Floresta e Vida', '9788500000008', 'Editora Cultura Amazônica', 2016,
       'A biodiversidade amazônica e a cultura dos povos da região.',
       c.id_categoria
FROM `LUMENDB`.`categoria` c
WHERE c.nome_categoria = 'Amazônia'
  AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000008');

-- =====================================================
-- Exemplares (PAT-00001 a PAT-00020)
-- =====================================================
INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00001', 'disponivel', 'Estante A1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000001'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00001');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00002', 'disponivel', 'Estante A1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000001'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00002');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00003', 'disponivel', 'Estante A1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000001'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00003');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00004', 'disponivel', 'Estante A2', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000002'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00004');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00005', 'disponivel', 'Estante A2', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000002'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00005');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00006', 'disponivel', 'Estante A2', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000002'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00006');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00007', 'disponivel', 'Estante B1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000003'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00007');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00008', 'disponivel', 'Estante B1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000003'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00008');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00009', 'disponivel', 'Estante B1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000003'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00009');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00010', 'disponivel', 'Estante C1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000004'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00010');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00011', 'disponivel', 'Estante C1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000004'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00011');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00012', 'disponivel', 'Estante C2', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000005'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00012');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00013', 'disponivel', 'Estante C2', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000005'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00013');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00014', 'disponivel', 'Estante D1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000006'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00014');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00015', 'disponivel', 'Estante D1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000006'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00015');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00016', 'disponivel', 'Estante E1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000007'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00016');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00017', 'disponivel', 'Estante E1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000007'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00017');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00018', 'disponivel', 'Estante E1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000007'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00018');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00019', 'disponivel', 'Estante F1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000008'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00019');

INSERT INTO `LUMENDB`.`exemplar` (`codigo_patrimonio`, `status_exemplar`, `localizacao`, `id_livro`)
SELECT 'PAT-00020', 'disponivel', 'Estante F1', l.id_livro
FROM `LUMENDB`.`livro` l WHERE l.isbn = '9788500000008'
AND NOT EXISTS (SELECT 1 FROM `LUMENDB`.`exemplar` e WHERE e.codigo_patrimonio = 'PAT-00020');