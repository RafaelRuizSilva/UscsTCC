CREATE DATABASE db_uscs_ic;

USE db_uscs_ic;

CREATE TABLE IF NOT EXISTS tb_curso (
    id_curso INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_cadastro_aluno (
    id_aluno INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    id_curso INT NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_curso)
        REFERENCES tb_curso(id_ctb_campusurso)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tb_cadastro_orientador (
    id_orientador INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    senha_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_campus (
    id_campus INT AUTO_INCREMENT PRIMARY KEY,
    campus VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_novo_projeto (
    id_projeto INT AUTO_INCREMENT PRIMARY KEY,
    titulo_projeto VARCHAR(255) NOT NULL,
    resumo VARCHAR(1000) NOT NULL,
    id_orientador int,
    id_campus int,
	FOREIGN KEY (id_orientador) REFERENCES tb_cadastro_orientador(id_orientador) ON DELETE SET NULL,
	FOREIGN KEY (id_campus) REFERENCES tb_campus(id_campus) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tb_projeto_aluno (
    id_projeto INT,
    id_aluno INT,
    PRIMARY KEY (id_projeto, id_aluno),
    FOREIGN KEY (id_projeto) REFERENCES tb_novo_projeto(id_projeto) ON DELETE CASCADE,
    FOREIGN KEY (id_aluno) REFERENCES tb_cadastro_aluno(id_aluno) ON DELETE CASCADE
);
