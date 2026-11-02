"""
Lifecycle and Idle Watchdog Manager for Automation Server.
Monitors activity and triggers graceful auto-shutdown when idle.
"""
import asyncio
import logging
import os
import signal
import sys
import time
from typing import Optional, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("automation.lifecycle")


class IdleWatchdog:
    def __init__(self, idle_timeout: int = 60, cleanup_callback: Optional[Callable] = None):
        self.idle_timeout = idle_timeout
        self.cleanup_callback = cleanup_callback
        self.last_activity_time = time.time()
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self._active_requests = 0
        self._lock = asyncio.Lock()

    def update_activity(self):
        """Update last activity timestamp to prevent timeout."""
        self.last_activity_time = time.time()

    def set_timeout(self, seconds: int):
        """Dynamically update idle timeout."""
        self.idle_timeout = seconds
        self.update_activity()
        logger.info(f"Idle timeout updated to {seconds} seconds.")

    def get_status(self) -> dict:
        idle_seconds = round(time.time() - self.last_activity_time, 1)
        remaining = max(0.0, round(self.idle_timeout - idle_seconds, 1)) if self.idle_timeout > 0 else -1
        return {
            "idle_timeout": self.idle_timeout,
            "idle_seconds": idle_seconds,
            "remaining_seconds": remaining,
            "active_requests": self._active_requests,
        }

    async def start(self):
        """Start the watchdog background monitor loop."""
        if self.idle_timeout <= 0:
            logger.info("Idle auto-shutdown is disabled (idle_timeout <= 0).")
            return

        self.is_running = True
        self.last_activity_time = time.time()
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Idle Watchdog started (timeout: {self.idle_timeout}s).")

    async def stop(self):
        """Stop the watchdog monitor loop."""
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self):
        while self.is_running:
            await asyncio.sleep(2)
            if self.idle_timeout <= 0:
                continue

            if self._active_requests > 0:
                self.update_activity()
                continue

            idle_duration = time.time() - self.last_activity_time
            if idle_duration >= self.idle_timeout:
                logger.warning(
                    f"Idle timeout ({self.idle_timeout}s) exceeded with no active requests. "
                    "Initiating graceful auto-shutdown..."
                )
                await self.trigger_shutdown()
                break

    async def trigger_shutdown(self):
        """Gracefully cleanup resources and terminate server process."""
        self.is_running = False
        if self.cleanup_callback:
            try:
                if asyncio.iscoroutinefunction(self.cleanup_callback):
                    await self.cleanup_callback()
                else:
                    self.cleanup_callback()
            except Exception as e:
                logger.error(f"Error during shutdown cleanup callback: {e}", exc_info=True)

        logger.info("Shutdown complete. Terminating process.")
        # Trigger process termination
        if sys.platform == "win32":
            os.kill(os.getpid(), signal.SIGTERM)
        else:
            os.kill(os.getpid(), signal.SIGINT)


class ActivityMiddleware(BaseHTTPMiddleware):
    """FastAPI/Starlette middleware to touch watchdog on every HTTP request."""

    def __init__(self, app, watchdog: IdleWatchdog):
        super().__init__(app)
        self.watchdog = watchdog

    async def dispatch(self, request: Request, call_next):
        # We don't reset timer on lightweight health checks if specifically excluded,
        # but for simplicity all actual API interactions refresh the lease.
        self.watchdog._active_requests += 1
        try:
            self.watchdog.update_activity()
            response: Response = await call_next(request)
            return response
        finally:
            self.watchdog._active_requests = max(0, self.watchdog._active_requests - 1)
            self.watchdog.update_activity()

