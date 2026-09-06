"""
Server Auto-Launcher for Automation Client.
Checks server health and spawns the automation server daemon in background if offline.
"""
import logging
import os
import subprocess
import sys
import time
from typing import Optional
import httpx

logger = logging.getLogger("automation.launcher")


class ServerLauncher:
    @staticmethod
    def _find_project_root() -> str:
        """Walk up from this file to find the directory containing server/app.py."""
        d = os.path.dirname(os.path.abspath(__file__))
        for _ in range(6):
            if os.path.isfile(os.path.join(d, "server", "app.py")):
                return d
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
        # Fallback: assume the server package is importable from the cwd
        return os.getcwd()

    @staticmethod
    def is_server_alive(base_url: str, timeout: float = 1.0) -> bool:
        """Check if server /health endpoint is responding."""
        try:
            resp = httpx.get(f"{base_url}/health", timeout=timeout)
            return resp.status_code == 200 and resp.json().get("status") == "ok"
        except Exception:
            return False

    @staticmethod
    def ensure_server_running(
        host: str = "127.0.0.1",
        port: int = 8765,
        idle_timeout: int = 60,
        serial: Optional[str] = None,
        max_wait_seconds: float = 15.0,
        server_module: str = "server.app",
    ) -> str:
        """Ensure automation server is running, auto-spawning it in background if necessary."""
        base_url = f"http://{host}:{port}"
        if ServerLauncher.is_server_alive(base_url):
            logger.debug(f"Automation server already running at {base_url}")
            return base_url

        logger.info(f"Automation server not detected at {base_url}. Auto-launching in background...")

        cmd = [
            sys.executable,
            "-m",
            server_module,
            "--host",
            host,
            "--port",
            str(port),
            "--idle-timeout",
            str(idle_timeout),
        ]
        if serial:
            cmd.extend(["--serial", serial])

        # Prepare detached process creation flags depending on OS
        kwargs = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
        }

        # Locate the project root (directory containing the server package) by
        # walking up from this file, so auto-launch works both from a repo
        # checkout (sdk/python/automation_client) and from an installed copy.
        project_root = ServerLauncher._find_project_root()

        env = os.environ.copy()
        python_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{project_root}{os.pathsep}{python_path}" if python_path else project_root

        if sys.platform == "win32":
            # DETACHED_PROCESS = 0x00000008, CREATE_NEW_PROCESS_GROUP = 0x00000200
            kwargs["creationflags"] = 0x00000008 | 0x00000200
        else:
            kwargs["start_new_session"] = True

        subprocess.Popen(cmd, cwd=project_root, env=env, **kwargs)

        # Wait for server to become healthy
        start_time = time.time()
        while time.time() - start_time < max_wait_seconds:
            time.sleep(0.5)
            if ServerLauncher.is_server_alive(base_url, timeout=0.5):
                logger.info(f"Automation server successfully launched and verified at {base_url}.")
                return base_url

        raise TimeoutError(
            f"Failed to auto-launch automation server at {base_url} within {max_wait_seconds}s."
        )

