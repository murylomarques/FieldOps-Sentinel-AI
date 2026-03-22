from contextvars import ContextVar
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import func

from app.api.routes import auth, dashboard, monitoring, orders, recommendations, replay, simulations
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.rate_limit import InMemoryRateLimiter
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.decision import Decision
from app.models.metric import ModelMetric
from app.models.recommendation import Recommendation

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


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    db = SessionLocal()
    try:
        requests_count = db.query(ModelMetric).count()
        recommendations = db.query(Recommendation).count()
        approvals = db.query(Decision).filter(Decision.human_decision == "approved").count()
        rejections = db.query(Decision).filter(Decision.human_decision == "rejected").count()
        latency = db.query(func.avg(ModelMetric.latency_ms)).scalar() or 0.0
        loss_avoided = (
            db.query(func.sum(Recommendation.impact_score * 100)).scalar() or 0.0
        )
        override_rate = (rejections / (approvals + rejections)) * 100 if (approvals + rejections) else 0.0

        content = "\n".join(
            [
                f"fieldops_requests_total {requests_count}",
                f"fieldops_recommendations_total {recommendations}",
                f"fieldops_approvals_total {approvals}",
                f"fieldops_rejections_total {rejections}",
                f"fieldops_avg_latency_ms {float(latency):.4f}",
                f"fieldops_projected_loss_avoided_total {float(loss_avoided):.4f}",
                f"fieldops_override_rate {float(override_rate):.4f}",
            ]
        )
        return PlainTextResponse(content=content)
    finally:
        db.close()


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(orders.router, prefix=settings.api_v1_prefix)
app.include_router(recommendations.router, prefix=settings.api_v1_prefix)
app.include_router(dashboard.router, prefix=settings.api_v1_prefix)
app.include_router(monitoring.router, prefix=settings.api_v1_prefix)
app.include_router(simulations.router, prefix=settings.api_v1_prefix)
app.include_router(replay.router, prefix=settings.api_v1_prefix)
