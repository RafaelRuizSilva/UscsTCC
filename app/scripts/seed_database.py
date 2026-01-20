import hashlib
from faker import Faker
from datetime import date
from io import BytesIO
import zipfile

from app.dependencies.db import db_connection  # ajuste se seu caminho for diferente

fake = Faker("pt_BR")


# =====================================================
# 📌 Funções utilitárias
# =====================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def fake_pdf_bytes():
    return b"%PDF-1.4 Fake PDF Conteudo Teste..."


def fake_docx_bytes():
    """
    Gera um DOCX mínimo válido apenas para seed.
    O Word consegue abrir normalmente.
    """
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml",
                      """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                      <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
                        <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
                        <Default Extension="xml" ContentType="application/xml"/>
                        <Override PartName="/word/document.xml"
                          ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
                      </Types>""")

        docx.writestr("_rels/.rels",
                      """<?xml version="1.0" encoding="UTF-8"?>
                      <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
                        <Relationship Id="rId1"
                         Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
                         Target="word/document.xml"/>
                      </Relationships>""")

        docx.writestr("word/document.xml",
                      """<?xml version="1.0" encoding="UTF-8"?>
                      <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                        <w:body>
                          <w:p><w:r><w:t>Documento gerado automaticamente.</w:t></w:r></w:p>
                        </w:body>
                      </w:document>""")

    return buffer.getvalue()


# =====================================================
# 📌 Inserts
# =====================================================

def insert_cursos(cursor):
    cursos = ["Direito", "Psicologia", "Engenharia de Software", "Publicidade", "Administração"]
    cursor.executemany("INSERT INTO tb_curso (nome) VALUES (%s)", [(c,) for c in cursos])
    return len(cursos)


def insert_campus(cursor):
    campus = ["Paulista", "Barcelona", "Centro", "Santo André"]
    cursor.executemany("INSERT INTO tb_campus (campus) VALUES (%s)", [(c,) for c in campus])
    return len(campus)


def insert_orientadores(cursor, qtd=5):
    for _ in range(qtd):
        cursor.execute("""
            INSERT INTO tb_cadastro_orientador
            (nome_completo, email, cpf, senha_hash, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            fake.name(),
            fake.unique.email(),
            fake.unique.cpf(),
            hash_password("123456"),
            "APROVADO"
        ))
    return qtd


def insert_alunos(cursor, qtd=20):
    cursor.execute("SELECT id_curso FROM tb_curso")
    cursos = [row[0] for row in cursor.fetchall()]

    for _ in range(qtd):
        cursor.execute("""
            INSERT INTO tb_cadastro_aluno
            (nome_completo, email, cpf, id_curso, possui_trabalho_remunerado,
             status, senha_hash, pdf_file, possui_bolsa)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            fake.name(),
            fake.unique.email(),
            fake.unique.cpf(),
            fake.random_element(cursos),
            fake.boolean(),
            "APROVADO",
            hash_password("123456"),
            fake_pdf_bytes(),
            fake.boolean()
        ))
    return qtd


def insert_projetos(cursor, qtd=20):
    cursor.execute("SELECT id_orientador FROM tb_cadastro_orientador")
    orientadores = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id_campus FROM tb_campus")
    campus = [row[0] for row in cursor.fetchall()]

    for i in range(qtd):
        cursor.execute("""
            INSERT INTO tb_novo_projeto
            (cod_projeto, titulo_projeto, resumo, id_orientador, id_campus,
             ideia_inicial, ideia_inicial_pdf, concluido)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            f"PRJ-{1000+i}",
            fake.sentence(nb_words=6),
            fake.text(max_nb_chars=400),
            fake.random_element(orientadores),
            fake.random_element(campus),
            fake_docx_bytes(),     # DOCX válido
            fake_pdf_bytes(),      # PDF válido
            False
        ))
    return qtd


def insert_projeto_alunos(cursor):
    cursor.execute("SELECT id_projeto FROM tb_novo_projeto")
    projetos = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id_aluno FROM tb_cadastro_aluno")
    alunos = [row[0] for row in cursor.fetchall()]

    for aluno in alunos:
        projeto = fake.random_element(projetos)
        cursor.execute("""
            INSERT IGNORE INTO tb_projeto_aluno
            (id_aluno, id_projeto, status_aluno)
            VALUES (%s, %s, %s)
        """, (aluno, projeto, fake.boolean()))


def insert_avaliadores(cursor, qtd=5):
    for _ in range(qtd):
        cursor.execute("""
            INSERT INTO TB_AVALIADOR_EXTERNO
            (nome, email, especialidade, subespecialidade, link_lattes)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            fake.name(),
            fake.unique.email(),
            fake.job(),
            fake.job(),
            fake.url()
        ))
    return qtd


def insert_bolsas(cursor):
    # tipo de bolsa
    cursor.execute("""
        INSERT INTO tb_tipo_bolsa (tipo_bolsa) VALUES
        ('PIBIC'), ('PIBITI'), ('Voluntário')
        ON DUPLICATE KEY UPDATE tipo_bolsa = tipo_bolsa
    """)

    cursor.execute("SELECT id_tipo_bolsa FROM tb_tipo_bolsa")
    tipos = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id_aluno FROM tb_cadastro_aluno")
    alunos = [row[0] for row in cursor.fetchall()]

    for aluno in alunos:
        if fake.boolean(chance_of_getting_true=30):
            cursor.execute("""
                INSERT IGNORE INTO tb_bolsa (id_aluno, id_tipo_bolsa)
                VALUES (%s, %s)
            """, (aluno, fake.random_element(tipos)))


def insert_relatorios(cursor):
    cursor.execute("SELECT id_projeto, id_orientador FROM tb_novo_projeto")
    projetos = cursor.fetchall()

    for project_id, orientador_id in projetos:
        for mes in [1, 2, 3]:
            cursor.execute("""
                INSERT IGNORE INTO tb_relatorio_mensal
                (id_projeto, id_orientador, mes_referencia, ok)
                VALUES (%s, %s, %s, %s)
            """, (
                project_id,
                orientador_id,
                date(2024, mes, 1),
                1
            ))

def insert_inscricoes(cursor):
    """
    Popula a tabela tb_inscricao_projeto com inscrições simples:
    cada aluno se inscreve em 1 projeto aleatório.
    """

    cursor.execute("SELECT id_aluno FROM tb_cadastro_aluno")
    alunos = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id_projeto FROM tb_novo_projeto")
    projetos = [row[0] for row in cursor.fetchall()]

    for aluno in alunos:
        projeto_escolhido = fake.random_element(projetos)

        cursor.execute("""
            INSERT IGNORE INTO tb_inscricao_projeto (id_aluno, id_projeto)
            VALUES (%s, %s)
        """, (aluno, projeto_escolhido))

    return len(alunos)


# =====================================================
# 📌 Execução Principal
# =====================================================

def popular_banco():
    with db_connection() as conn:
        cursor = conn.cursor()

        print("Inserindo cursos...")
        insert_cursos(cursor)

        print("Inserindo campus...")
        insert_campus(cursor)

        print("Inserindo orientadores...")
        insert_orientadores(cursor)

        print("Inserindo alunos...")
        insert_alunos(cursor)

        print("Inserindo projetos...")
        insert_projetos(cursor)

        print("Vinculando alunos a projetos...")
        insert_projeto_alunos(cursor)

        print("Inserindo inscrições dos alunos (tb_inscricao_projeto)...")
        insert_inscricoes(cursor)

        print("Inserindo avaliadores externos...")
        insert_avaliadores(cursor)

        print("Inserindo bolsas...")
        insert_bolsas(cursor)

        print("Inserindo relatórios mensais...")
        insert_relatorios(cursor)

        conn.commit()
        print("\n✔ Banco populado com sucesso!")

def main():
    print("\n=== INICIANDO SEED COMPLETO DO BANCO ===\n")
    popular_banco()
    print("\n=== SEED FINALIZADO ===\n")


if __name__ == "__main__":
    main()
