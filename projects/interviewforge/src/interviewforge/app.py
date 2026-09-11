"""API lifecycle, liveness, database readiness and request correlation."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from interviewforge.config import Settings, load_settings
from interviewforge.ui import router as ui_router

logger = logging.getLogger("interviewforge")


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings if settings is not None else load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = None
        if config.database_url is not None:
            engine = create_engine(
                config.database_url.get_secret_value(),
                connect_args={"connect_timeout": config.db_connect_timeout},
                pool_timeout=config.db_connect_timeout,
                pool_pre_ping=True,
            )
        app.state.engine = engine

        async def refresh_knowledge():
            from interviewforge.ai.rag import refresh

            while True:
                await asyncio.to_thread(refresh, config)
                await asyncio.sleep(3600)

        knowledge_task = (
            asyncio.create_task(refresh_knowledge())
            if config.environment != "test" and config.amazon_mcp_server_url
            else None
        )
        try:
            yield
        finally:
            if knowledge_task:
                knowledge_task.cancel()
                try:
                    await knowledge_task
                except asyncio.CancelledError:
                    pass
            if engine is not None:
                engine.dispose()

    app = FastAPI(
        title="InterviewForge API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if config.environment != "production" else None,
        redoc_url=None,
        openapi_url="/openapi.json" if config.environment != "production" else None,
    )
    app.state.settings = config
    package_dir = Path(__file__).resolve().parent
    app.mount("/static", StaticFiles(directory=package_dir / "static"), name="static")
    app.include_router(ui_router)

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        trace_id = uuid4().hex
        request.state.trace_id = trace_id
        started = perf_counter()
        try:
            response = await call_next(request)
        except Exception:  # Final HTTP boundary; exception details are deliberately hidden.
            # Exception strings may contain SQL, credentials or request content.
            response = JSONResponse(
                {"detail": "Internal server error", "trace_id": trace_id}, status_code=500
            )
        response.headers["X-Trace-ID"] = trace_id
        logger.info(
            json.dumps(
                {
                    "event": "request_completed",
                    "trace_id": trace_id,
                    "method": request.method,
                    "status": response.status_code,
                    "duration_ms": round((perf_counter() - started) * 1000, 2),
                }
            )
        )
        return response

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "interviewforge"}

    @app.get("/ready")
    def ready(request: Request):
        if request.app.state.engine is None:
            return JSONResponse(
                {
                    "status": "not_ready",
                    "database": "not_configured",
                    "trace_id": request.state.trace_id,
                },
                status_code=503,
            )
        try:
            with request.app.state.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
            return JSONResponse(
                {
                    "status": "not_ready",
                    "database": "unavailable",
                    "trace_id": request.state.trace_id,
                },
                status_code=503,
            )
        return {"status": "ready", "database": "available"}

    return app
