=======
# 📘 SGPIC — Sistema de Gestão de Projetos de Iniciação Científica
*Universidade Municipal de São Caetano do Sul (USCS)*

O **SGPIC** é um sistema desenvolvido para **organizar, gerenciar e acompanhar** todo o fluxo de Projetos de Iniciação Científica (IC) da USCS, centralizando operações como:
- Cadastro de projetos
- Gestão de alunos vinculados a orientadores
- Fluxo de aprovação
- Envio de e-mails automáticos (SMTP)
- Persistência de dados em banco MySQL
- Comunicação assíncrona via RabbitMQ
- Execução totalmente conteinerizada com Docker

---

## 🏗️ Arquitetura

O projeto segue uma arquitetura limpa e organizada em camadas:

```
app/
│
├── adapters/            # Interfaces externas e integrações
│   ├── email/           # Envio de emails (SMTP)
│   ├── message/         # RabbitMQ
│   ├── repositories/    # Acesso a banco / persistência
│   ├── web/             # Rotas da API
│   └── configs/         # Arquivo settings.py
│
├── core/
│   ├── models/          # Entidades de domínio
│   ├── ports/           # Interfaces (contratos)
│   └── use_cases/       # Regras de negócio
│
├── dependencies/        # Conexões e factories
├── htmlcov/             # Relatórios
├── init-db/             # Scripts de inicialização do banco
├── templates/           # Templates HTML/Jinja
└── venv/                # Ambiente virtual
```

---

## 🚀 Como Rodar o Projeto

### **1. Pré‑requisitos**
- **Docker Desktop** instalado  
- Criar o arquivo obrigatório:
```
app/adapters/configs/settings.py
```

---

## 📂 Estrutura obrigatória do `settings.py`

```python
SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 587,
    "from": "seu_email@gmail.com",
    "password": "senha_de_app_google",
    "use_tls": True
}

DB_CONFIG = {
    "host": "db",
    "user": "root",
    "password": "senha_mysql",
    "database": "db_uscs_ic",
    "port": 3306,
}

SECRET_KEY = "sua_secret_key"

RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"

DATABASE_URL = "mysql+pymysql://root:senha@db:3306/db_uscs_ic"

TEMPLATE_DIRS = ["templates"]
```

---

## ▶️ Como iniciar o sistema

Na raiz do projeto, execute:

```bash
docker compose up --build
```

O Docker irá:
- Subir o MySQL  
- Subir a API (FastAPI)  
- Subir o RabbitMQ  
- Carregar scripts de banco  
- Disponibilizar o sistema em:

```
http://localhost:8000
```

---

## 🧱 Serviços Incluídos

| Serviço       | Porta | Descrição |
|--------------|-------|-----------|
| API SGPIC    | 8000  | Backend FastAPI |
| MySQL        | 3306  | Banco de dados |
| RabbitMQ     | 5672  | Mensageria |
| Rabbit Admin | 15672 | Painel de administração |

---

## 📮 Envio de Emails (SMTP)

O SGPIC utiliza Gmail via **Senha de App**.

A senha de app deve ser configurada no `settings.py`.

---

## 🗃️ Banco de Dados

Scripts de criação:

```
init-db/init.sql
init-db/script_create_tables.sql
```

---

## 📬 Mensageria com RabbitMQ

Eventos (ex.: atualização de alunos do projeto) são enviados via RabbitMQ:

```
app/adapters/message/
```

---

## 🧠 Core (Domínio)

Regras de negócio:

```
app/core/use_cases/
```

Entidades:

```
app/core/models/
```

---

## 🔐 Segurança

- Nunca comitar credenciais  
- `settings.py` está no .gitignore  
- SECRET_KEY protegida  
- SMTP com TLS  

---

## 📌 Checklist

✔ Criou `settings.py`?  
✔ Preencheu SMTP com senha de app?  
✔ Configurou senha do MySQL?  
✔ Docker Desktop está rodando?  

---

## 👥 Sobre o Projeto

O **SGPIC** foi criado para digitalizar e otimizar a gestão de Projetos de Iniciação Científica da **USCS**, atendendo:
- Secretaria  
- Alunos  
- Orientadores  
- Coordenação  

Automatizando comunicações, operações e validações essenciais.

---
>>>>>>> API/completa
