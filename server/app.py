"""
Multi-UIAutomator2 Automation Server Main Application.
"""
import argparse
import asyncio
from contextlib import asynccontextmanager
import logging
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from server.config import settings
from server.core.device_manager import device_manager
from server.lifecycle import IdleWatchdog, ActivityMiddleware
from server.routes.device import router as device_router
from server.routes.app_control import router as app_router
from server.routes.ui import router as ui_router
from server.routes.ai_agent import router as ai_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("automation.server")

# Instantiate global watchdog
watchdog = IdleWatchdog(
    idle_timeout=settings.idle_timeout,
    cleanup_callback=device_manager.cleanup_all,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Automation Server...")
    await watchdog.start()
    yield
    # Shutdown
    logger.info("Shutting down Automation Server...")
    await watchdog.stop()
    device_manager.cleanup_all()


app = FastAPI(
    title="Android UI Automation Service",
    description="On-demand cross-language Android UI automation & AI debug server",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Watchdog activity middleware
app.add_middleware(ActivityMiddleware, watchdog=watchdog)

# Include routers
app.include_router(device_router)
app.include_router(app_router)
app.include_router(ui_router)
app.include_router(ai_router)


@app.get("/health")
async def health():
    """Health check endpoint used by SDK auto-launchers."""
    return {
        "status": "ok",
        "service": "multi-uiautomator2-server",
        "version": "0.1.0",
    }


@app.get("/status")
async def server_status():
    """Get current server status and idle watchdog countdown."""
    return {
        "status": "running",
        "watchdog": watchdog.get_status(),
        "connected_devices": list(device_manager._devices.keys()),
    }


class SetTimeoutRequest(BaseModel):
    idle_timeout: int


@app.post("/config/idle-timeout")
async def set_idle_timeout(req: SetTimeoutRequest):
    """Dynamically configure idle timeout (in seconds). 0 disables auto-shutdown."""
    watchdog.set_timeout(req.idle_timeout)
    return {"status": "success", "idle_timeout": req.idle_timeout}


@app.post("/shutdown")
async def manual_shutdown():
    """Manually trigger graceful server shutdown."""
    asyncio.create_task(watchdog.trigger_shutdown())
    return {"status": "success", "message": "Server shutting down..."}


def main():
    parser = argparse.ArgumentParser(description="Start On-Demand Automation Server")
    parser.add_argument("--host", default=settings.host, help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=settings.port, help="Bind port (default: 8765)")
    parser.add_argument(
        "--idle-timeout",
        type=int,
        default=settings.idle_timeout,
        help="Idle auto-shutdown timeout in seconds (default: 60, 0 to disable)",
    )
    parser.add_argument("--serial", default=None, help="Default Android device serial")
    args = parser.parse_args()

    settings.host = args.host
    settings.port = args.port
    settings.idle_timeout = args.idle_timeout
    watchdog.idle_timeout = args.idle_timeout
    if args.serial:
        settings.default_serial = args.serial
        device_manager.default_serial = args.serial

    logger.info(f"Starting server on http://{settings.host}:{settings.port} (Idle Timeout: {settings.idle_timeout}s)")
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")


if __name__ == "__main__":
    main()

