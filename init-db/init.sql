CREATE DATABASE IF NOT EXISTS db_uscs_ic;

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
        REFERENCES tb_curso(id_curso)
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
    id_inscricao INT AUTO_INCREMENT PRIMARY KEY,
    id_aluno INT NOT NULL,                         
    id_projeto INT NOT NULL,                       
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY tb_projeto_aluno(id_projeto) REFERENCES tb_novo_projeto(id_projeto) ON DELETE CASCADE,
    FOREIGN KEY (id_aluno) REFERENCES tb_cadastro_aluno(id_aluno) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS TB_AVALIADOR_EXTERNO (
    id_avaliador INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    especialidade VARCHAR(100),
    subespecialidade VARCHAR(100),
    link_lattes TEXT
);

CREATE TABLE IF NOT EXISTS tb_notificacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(100) NOT NULL,
    mensagem TEXT NOT NULL,
    destinatario VARCHAR(100) NOT NULL,
    lida BOOLEAN DEFAULT FALSE,
    data_criacao DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_relatorio_mensal (
  id_relatorio     INT AUTO_INCREMENT PRIMARY KEY,
  id_projeto       INT NOT NULL,
  id_orientador    INT NOT NULL,
  mes_referencia   DATE NOT NULL,               -- sempre dia 1 do mês
  ok               TINYINT(1) NOT NULL DEFAULT 1,
  observacao       VARCHAR(500) NULL,
  confirmado_em    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_relatorio_projeto_mes (id_projeto, mes_referencia),
  CONSTRAINT fk_rm_projeto    FOREIGN KEY (id_projeto)    REFERENCES tb_novo_projeto(id_projeto),
  CONSTRAINT fk_rm_orientador FOREIGN KEY (id_orientador) REFERENCES tb_cadastro_orientador(id_orientador)
);

CREATE TABLE IF NOT EXISTS tb_cadastro_secretaria (
  id_secretaria INT AUTO_INCREMENT PRIMARY KEY,
  nome_completo VARCHAR(255) NOT NULL,
  email         VARCHAR(255) NOT NULL UNIQUE,
  cpf           VARCHAR(14)  NOT NULL UNIQUE,
  senha_hash    VARCHAR(255) NOT NULL
);




