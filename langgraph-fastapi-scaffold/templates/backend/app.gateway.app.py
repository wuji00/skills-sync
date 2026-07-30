"""
FastAPI Application Factory
============================
Extracted from deer-flow's app.py. Creates a FastAPI gateway with:
- Lifespan-managed LangGraph runtime singletons
- Auth, CSRF, CORS, Trace middleware stack
- Modular router includes for auth, threads, runs, health

This is the ENTRY POINT for uvicorn:
    uv run uvicorn app.gateway.app:app --reload --port 8001
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Adjust imports to match your project layout ---
from app.config.app_config import AppConfig, get_app_config
from app.gateway.auth_middleware import AuthMiddleware
from app.gateway.csrf_middleware import CSRFMiddleware
from app.gateway.deps import langgraph_runtime
from app.gateway.routers import auth, health, runs, thread_runs, threads

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — bootstrap and teardown all runtime singletons."""
    startup_config = get_app_config()
    logger.info("Configuration loaded (log_level=%s)", startup_config.log_level)

    # Bootstrap LangGraph runtime (checkpointer, store, stream bridge, run manager)
    async with langgraph_runtime(app, startup_config):
        logger.info("LangGraph runtime initialized")

        # First-boot admin check
        await _ensure_admin_user(app)

        yield

    logger.info("Gateway shutdown complete")


async def _ensure_admin_user(app: FastAPI) -> None:
    """Check if admin exists; log setup instructions if first boot."""
    try:
        from app.gateway.local_auth import get_local_provider
        provider = get_local_provider()
    except Exception:
        return

    admin_count = await provider.count_admin_users()
    if admin_count == 0:
        logger.info("=" * 60)
        logger.info("  First boot — no admin account exists.")
        logger.info("  Visit /setup to create the first admin.")
        logger.info("=" * 60)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="LangGraph + FastAPI Gateway",
        description="API Gateway for LangGraph-based AI agent applications.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # --- Middleware stack (order matters) ---
    app.add_middleware(AuthMiddleware)
    app.add_middleware(CSRFMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Routers ---
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(threads.router)
    app.include_router(thread_runs.router)
    app.include_router(runs.router)

    return app


# Module-level app instance for uvicorn
app = create_app()
