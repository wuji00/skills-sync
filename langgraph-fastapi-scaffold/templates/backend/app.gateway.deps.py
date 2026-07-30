"""
Dependency Injection Bootstrap
===============================
Extracted from deer-flow's deps.py. Key patterns:

1. langgraph_runtime() — AsyncExitStack that creates ALL singletons at startup
   and stores them on app.state. Each singleton gets a corresponding getter.

2. Config hot-reload — get_config() returns live AppConfig (mtime-based reload).
   Startup-only singletons (engine, checkpointer) bind to the startup snapshot.

3. Per-request getters — each returns app.state.X or raises 503 if missing.

Usage in routers:
    @router.get("/threads")
    async def list_threads(config = Depends(get_config), ...):
        ...
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import AsyncExitStack, asynccontextmanager
from typing import TypeVar, cast

from fastapi import FastAPI, HTTPException, Request

from app.config.app_config import AppConfig, get_app_config
from app.runtime import RunContext, RunManager, StreamBridge

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ============================================================================
# Lifespan Bootstrap
# ============================================================================

@asynccontextmanager
async def langgraph_runtime(
    app: FastAPI, startup_config: AppConfig
) -> AsyncGenerator[None, None]:
    """Bootstrap and tear down all LangGraph runtime singletons.

    startup_config is the AppConfig snapshot taken once during lifespan().
    Infrastructure singletons (engine, checkpointer, store, bridge) bind to
    this snapshot since they hold live connections that can't hot-reload.

    Request-time code calls get_config() for hot-reloadable fields.
    """
    from app.persistence.engine import close_engine, get_session_factory, init_engine_from_config
    from app.runtime.checkpointer.provider import make_checkpointer
    from app.runtime.store.provider import make_store
    from app.runtime.stream_bridge.memory import MemoryStreamBridge

    async with AsyncExitStack() as stack:
        # 1. Stream bridge (decouples SSE producer from consumer)
        app.state.stream_bridge = MemoryStreamBridge()

        # 2. Persistence engine
        await init_engine_from_config(startup_config.database)

        # 3. LangGraph checkpointer
        app.state.checkpointer = await stack.enter_async_context(
            make_checkpointer(startup_config)
        )

        # 4. LangGraph store (long-term memory)
        app.state.store = await stack.enter_async_context(
            make_store(startup_config)
        )

        # 5. Repositories
        sf = get_session_factory()
        if sf is not None:
            from app.persistence.thread_meta.sql import SQLThreadMetaStore

            app.state.thread_store = SQLThreadMetaStore(sf)
        else:
            from app.persistence.thread_meta.memory import MemoryThreadMetaStore

            app.state.thread_store = MemoryThreadMetaStore()

        # 6. Run manager (in-flight run registry)
        app.state.run_manager = RunManager()

        try:
            yield
        finally:
            await close_engine()


# ============================================================================
# Generic getter factory
# ============================================================================

def _require(attr: str, label: str) -> Callable[[Request], T]:
    """Create a FastAPI dependency that returns app.state.<attr> or 503."""

    def dep(request: Request) -> T:
        val = getattr(request.app.state, attr, None)
        if val is None:
            raise HTTPException(
                status_code=503, detail=f"{label} not available"
            )
        return cast(T, val)

    dep.__name__ = f"get_{attr}"
    return dep


# ============================================================================
# Per-request getters
# ============================================================================

get_stream_bridge = _require("stream_bridge", "Stream bridge")
get_run_manager = _require("run_manager", "Run manager")
get_checkpointer = _require("checkpointer", "Checkpointer")
get_thread_store = _require("thread_store", "Thread metadata store")


def get_store(request: Request):
    """Return the LangGraph store (may be None)."""
    return getattr(request.app.state, "store", None)


def get_config() -> AppConfig:
    """Return the freshest AppConfig (hot-reload: re-reads config.yaml on change).

    Raises 503 if config is unavailable.
    """
    try:
        return get_app_config()
    except Exception as exc:
        logger.exception("Failed to load config at request time")
        raise HTTPException(status_code=503, detail="Configuration not available") from exc


def get_run_context(request: Request) -> RunContext:
    """Build a RunContext from app.state singletons for graph execution."""
    return RunContext(
        checkpointer=get_checkpointer(request),
        store=get_store(request),
        thread_store=get_thread_store(request),
        app_config=get_config(),
    )


# ============================================================================
# Auth helpers
# ============================================================================

async def get_current_user_from_request(request: Request):
    """Extract authenticated user from request.state (set by AuthMiddleware).

    Returns user or raises 401.
    """
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def require_admin_user(request: Request) -> None:
    """Require the authenticated user to be an admin (403 if not)."""
    user = await get_current_user_from_request(request)
    if getattr(user, "system_role", None) != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
