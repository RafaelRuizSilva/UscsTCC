# app/scripts/seed_secretaria.py
import argparse
from app.core.security import gerar_hash_senha
from app.dependencies.db import db_connection  # usa seu context manager

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nome", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--cpf", required=True)   # precisa estar no formato aceito pelo seu validador
    parser.add_argument("--senha", required=True)
    args = parser.parse_args()

    senha_hash = gerar_hash_senha(args.senha)

    with db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO tb_cadastro_secretaria (nome_completo, email, cpf, senha_hash)
                VALUES (%s, %s, %s, %s)
            """, (args.nome.lower(), args.email, args.cpf, senha_hash))
            conn.commit()
            print("✔ Secretária criada com sucesso. Faça login em /api/secretarias/login")
        except Exception as e:
            conn.rollback()
            print(f"✖ Falhou (duplicado ou dado inválido?): {e}")
        finally:
            cur.close()

if __name__ == "__main__":
    main()
