from fastapi import FastAPI
from app.adapters.web.email_controller import router as email_router
from app.adapters.web.curso_controller import router as curso_controller
from app.adapters.web.aluno_controller import router as aluno_controller
from app.adapters.web.auth_controller import router as auth_controller
from app.adapters.web.orientador_controller import router as orientador_controller
from app.adapters.web.projeto_controller import router as projeto_controller
from app.adapters.web.inscricao_controller import router as inscricao_controller
from app.adapters.web.relatorio_controller import router as relatorio_controller
from app.adapters.web.avaliador_externo_controller import router as avaliador_externo_controller
from app.adapters.web.notificacao_controller import router as notificacao_controller
from app.adapters.web.campus_controller import router as campus_controller
from app.adapters.web.relatorio_mensal_controller import router as rel_mensal
import uvicorn

__author__ = 'Rafael Ruiz da Silva 22/05/2025'

app = FastAPI()

app.include_router(email_router)
app.include_router(curso_controller)
app.include_router(aluno_controller)
app.include_router(auth_controller)
app.include_router(orientador_controller)
app.include_router(projeto_controller)
app.include_router(inscricao_controller)
app.include_router(relatorio_controller)
app.include_router(avaliador_externo_controller)
app.include_router(notificacao_controller)
app.include_router(campus_controller)
app.include_router(rel_mensal)
#uvicorn.run(app, host='localhost', port=8001)
#uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
