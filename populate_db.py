import random
import pymysql
from faker import Faker
from passlib.hash import bcrypt

fake = Faker('pt_BR')

# ---------- CONFIG BANCO ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1404",
    "database": "db_uscs_ic",
    "autocommit": True,
    "charset": "utf8mb4"
}

# ---------- GERADOR DE CPF VÁLIDO ----------

def gerar_cpf_valido() -> str:
    """Gera CPF no formato 000.000.000-00"""
    def calc_digito(digs):
        s = sum([int(d)*i for d, i in zip(digs, range(len(digs)+1, 1, -1))])
        r = (s*10) % 11
        return '0' if r == 10 else str(r)

    nove_digitos = [str(random.randint(0, 9)) for _ in range(9)]
    d1 = calc_digito(nove_digitos)
    d2 = calc_digito(nove_digitos + [d1])
    cpf = ''.join(nove_digitos) + d1 + d2
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

# ---------- INSERÇÕES ----------

def popular_cursos(cur, qtd=5):
    cursos = [fake.job() for _ in range(qtd)]
    for nome in cursos:
        cur.execute("INSERT INTO tb_curso (nome) VALUES (%s)", (nome,))
    return cursos


def popular_campus(cur, qtd=3):
    campuses = ['centro', 'conceição', 'barcelona']
    for c in campuses:
        cur.execute("INSERT INTO tb_campus (campus) VALUES (%s)", (c,))
    return campuses


def popular_orientadores(cur, qtd=10):
    orientadores = []
    for _ in range(qtd):
        nome = fake.name()
        email = fake.unique.email()
        cpf = gerar_cpf_valido()
        senha_hash = bcrypt.hash("123456")
        cur.execute("""
            INSERT INTO tb_cadastro_orientador (nome_completo, email, cpf, senha_hash)
            VALUES (%s, %s, %s, %s)
        """, (nome, email, cpf, senha_hash))
        orientadores.append(cur.lastrowid)
    return orientadores


def popular_alunos(cur, id_cursos, qtd=50):
    alunos = []
    for _ in range(qtd):
        nome = fake.name()
        email = fake.unique.email()
        cpf = gerar_cpf_valido()
        id_curso = random.choice(id_cursos)
        senha_hash = bcrypt.hash("123456")
        cur.execute("""
            INSERT INTO tb_cadastro_aluno (nome_completo, email, cpf, id_curso, senha_hash)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, email, cpf, id_curso, senha_hash))
        alunos.append(cur.lastrowid)
    return alunos


def popular_projetos(cur, orientadores, campuses, qtd=20):
    projetos = []
    for _ in range(qtd):
        titulo = fake.sentence(nb_words=6)
        resumo = fake.paragraph(nb_sentences=5)
        id_orientador = random.choice(orientadores) if random.random() < 0.8 else None
        id_campus = random.choice(campuses) if random.random() < 0.8 else None
        cur.execute("""
            INSERT INTO tb_novo_projeto (titulo_projeto, resumo, id_orientador, id_campus)
            VALUES (%s, %s, %s, %s)
        """, (titulo, resumo, id_orientador, id_campus))
        projetos.append(cur.lastrowid)
    return projetos


def popular_projeto_aluno(cur, alunos, projetos):
    for aluno_id in alunos:
        proj = random.choice(projetos)
        cur.execute("""
            INSERT IGNORE INTO tb_projeto_aluno (id_projeto, id_aluno)
            VALUES (%s, %s)
        """, (proj, aluno_id))


def popular_avaliadores(cur, qtd=15):
    for _ in range(qtd):
        cur.execute(
            """
            INSERT INTO TB_AVALIADOR_EXTERNO (nome, email, especialidade, subespecialidade, link_lattes)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                fake.name(),
                fake.unique.email(),
                fake.job(),
                fake.job(),
                f"https://lattes.cnpq.br/{fake.random_number(digits=15, fix_len=True)}"
            )
        )

# ---------- EXECUÇÃO PRINCIPAL ----------
if __name__ == "__main__":
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Popular cursos e campus primeiro para chaves estrangeiras
    popular_cursos(cur)
    popular_campus(cur)

    #conn.commit()

    # Obter IDs para FK
    cur.execute("SELECT id_curso FROM tb_curso")
    ids_cursos = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT id_campus FROM tb_campus")
    ids_campus = [row[0] for row in cur.fetchall()]

    orientadores_ids = popular_orientadores(cur)
    alunos_ids = popular_alunos(cur, ids_cursos)
    projetos_ids = popular_projetos(cur, orientadores_ids, ids_campus)
    popular_projeto_aluno(cur, alunos_ids, projetos_ids)
    popular_avaliadores(cur)

    conn.commit()
    cur.close()
    conn.close()
    print("Banco populado com sucesso!")