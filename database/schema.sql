-- Schema do banco de dados Lumen
-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS lumen_db;
USE lumen_db;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(100) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir usuário admin padrão
INSERT INTO usuarios (nome,email, senha) VALUES ('adm', 'kkk@example.com', '1234567')
