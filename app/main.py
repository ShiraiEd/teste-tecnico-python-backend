import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.routes.diagnostico import router as diagnostico_router
from app.routes.registro_foco import limiter, router as registro_router
from app.storage.database import create_tables

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="API de Log de Performance",
    version="1.0.0",
    description="Registra sessões de trabalho e entrega um diagnóstico inteligente de produtividade.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response


@app.exception_handler(Exception)
async def handler_erro_generico(request: Request, exc: Exception):
    logger.error(f"Erro interno: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor."})


app.include_router(registro_router)
app.include_router(diagnostico_router)
