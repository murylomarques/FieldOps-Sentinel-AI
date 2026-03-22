from contextvars import ContextVar
from uuid import uuid4

import structlog
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, dashboard, monitoring, orders, recommendations
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.rate_limit import InMemoryRateLimiter
from app.db.init_db import init_db

setup_logging()
logger = structlog.get_logger()
settings = get_settings()
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

app = FastAPI(
    title="FIELDOPS SENTINEL AI",
    description="An agentic operations intelligence platform for field service teams.",
    version="1.0.0",
)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = InMemoryRateLimiter(settings.rate_limit_per_minute)


@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", f"REQ-{uuid4().hex[:12]}")
    request_id_ctx.set(request_id)
    request.state.request_id = request_id
    try:
        await limiter(request)
        response = await call_next(request)
    except Exception as exc:
        logger.exception("request_failed", request_id=request_id, path=request.url.path)
        if hasattr(exc, "status_code"):
            return JSONResponse(status_code=exc.status_code, content={"detail": str(exc.detail), "request_id": request_id})
        return JSONResponse(status_code=500, content={"detail": "Unexpected error", "request_id": request_id})

    response.headers["x-request-id"] = request_id
    logger.info(
        "request_completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    return response


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "fieldops-sentinel-ai"}


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(orders.router, prefix=settings.api_v1_prefix)
app.include_router(recommendations.router, prefix=settings.api_v1_prefix)
app.include_router(dashboard.router, prefix=settings.api_v1_prefix)
app.include_router(monitoring.router, prefix=settings.api_v1_prefix)
