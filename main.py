from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Routers
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
from app.adapters.web.secretaria_controller import router as secretaria_controller
from app.adapters.web.bolsa_controller import router as bolsa_controller
from app.adapters.web.projeto_envio_controller import router as projeto_envio_controller
from app.adapters.web.envio_avaliadores import router as envio_avaliadores
from app.adapters.web.tipos_bolsa_controller import router as tipos_bolsa_controller

app = FastAPI(
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Ping (raiz) – opcional
@app.get("/__ping")
def __ping_root():
    return {"ok": True}

# Ping com /api
@app.get("/api/__ping")
def __ping_api():
    return {"ok": True}

# ====== Todas as rotas sob /api ======
api = APIRouter(prefix="/api")

api.include_router(email_router)
api.include_router(curso_controller)
api.include_router(aluno_controller)
api.include_router(auth_controller)
api.include_router(orientador_controller)
api.include_router(projeto_controller)
api.include_router(inscricao_controller)
api.include_router(relatorio_controller)
api.include_router(avaliador_externo_controller)
api.include_router(notificacao_controller)   # agora também em /api
api.include_router(campus_controller)
api.include_router(rel_mensal)
api.include_router(secretaria_controller)
api.include_router(bolsa_controller)
api.include_router(projeto_envio_controller)
api.include_router(envio_avaliadores)
api.include_router(tipos_bolsa_controller)

app.include_router(api)

# ====== CORS ======
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:4200",
    "https://meu-frontend.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)