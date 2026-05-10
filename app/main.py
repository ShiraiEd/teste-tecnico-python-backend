import logging
import os
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.routes.diagnostico import router as diagnostico_router
from app.routes.registro_foco import limiter, router as registro_router
from app.storage.database import create_tables

load_dotenv()

_log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(level=_log_level, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executa create_tables() no startup para garantir que o banco existe antes
    de qualquer requisição. O yield separa startup de shutdown."""
    create_tables()
    yield


app = FastAPI(
    title="API de Log de Performance",
    version="1.0.0",
    description="Registra sessões de trabalho e entrega um diagnóstico inteligente de produtividade.",
    lifespan=lifespan,
)

# Registra o limiter e o handler de 429 para que o slowapi intercepte
# requisições que excedam o rate limit antes de chegarem às rotas.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Origens CORS lidas do ambiente; fallback para localhost de desenvolvimento.
_cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Loga método, path, status code e duração de cada requisição.

    Centralizado aqui para cobrir todos os endpoints automaticamente,
    sem instrumentar cada rota individualmente.
    """
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)"
    )
    return response


@app.exception_handler(Exception)
async def handler_erro_generico(request: Request, exc: Exception):
    """Captura exceções não tratadas e retorna 500 sem expor detalhes internos.

    O stack trace é logado no servidor mas não enviado ao cliente,
    evitando vazamento de informações sobre a implementação.
    """
    logger.error(f"Erro interno: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"detail": "Erro interno do servidor."}
    )


app.include_router(registro_router)
app.include_router(diagnostico_router)
