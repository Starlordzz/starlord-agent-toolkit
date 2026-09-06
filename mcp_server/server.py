"""
MCP Server exposing the Multi-UIAutomator2 Android automation service as MCP tools.

Layering:
    MCP Client (ZCode / Claude / Cursor ...)
        └── mcp_server (stdio, this file)
              └── automation_client SDK (auto-starts the automation server on demand)
                    └── Automation Server (FastAPI, port 8765, idle watchdog)
                          └── uiautomator2 / adb
                                └── Android device(s)

The MCP server itself is stateless and cheap: all device work is delegated to the
on-demand automation server, which exits after the idle timeout and is silently
re-spawned on the next tool call.

Environment variables:
    AUTOMATION_HOST          Host of the automation server   (default: 127.0.0.1)
    AUTOMATION_PORT          Port of the automation server   (default: 8765)
    AUTOMATION_SERIAL        Default device serial           (default: auto-detect)
    AUTOMATION_IDLE_TIMEOUT  Idle watchdog seconds           (default: 300, 0 = never)
    AUTOMATION_AUTO_START    Auto-spawn the server           (default: 1)
    OPENAI_API_KEY / OPENAI_BASE_URL / LLM_MODEL   For ai_* tools (inherited by the spawned server)
"""
import base64
import functools
import io
import json
import logging
import os
import sys
import threading
from typing import Annotated, Any, Literal, Optional

# Make `automation_client` (sdk/python) importable when running from a repo
# checkout without pip installation. Must happen before SDK imports.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_REPO_ROOT, os.path.join(_REPO_ROOT, "sdk", "python")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from mcp.server.fastmcp import FastMCP, Image
from PIL import Image as PILImage

from automation_client import AutomationClient

logger = logging.getLogger("mcp.android")

# ---------------------------------------------------------------------------
# Configuration & client lifecycle
# ---------------------------------------------------------------------------

HOST = os.getenv("AUTOMATION_HOST", "127.0.0.1")
PORT = int(os.getenv("AUTOMATION_PORT", "8765"))
IDLE_TIMEOUT = int(os.getenv("AUTOMATION_IDLE_TIMEOUT", "300"))
DEFAULT_SERIAL = os.getenv("AUTOMATION_SERIAL") or os.getenv("ANDROID_SERIAL") or None
AUTO_START = os.getenv("AUTOMATION_AUTO_START", "1").lower() not in ("0", "false", "no")

mcp = FastMCP(
    "android-device",
    instructions=(
        "Control real Android devices (taps, text input, navigation, screenshots, "
        "app lifecycle) through uiautomator2. Recommended loop for any task: "
        "1) observe with get_screen_elements (cheap, numbered element list) and/or "
        "screenshot (visual); 2) act with tap / input_text / press_key / swipe / "
        "start_app; 3) re-observe to verify the result. Element indices from "
        "get_screen_elements map to coordinates you can pass to tap(x, y). "
        "Selector-based actions (text / resource_id) are more robust than raw "
        "coordinates. ai_execute_goal delegates to a separate server-side LLM agent "
        "and needs OPENAI_API_KEY — prefer the primitive tools unless asked."
    ),
)

_client: Optional[AutomationClient] = None
_client_lock = threading.Lock()
_session_serial: Optional[str] = DEFAULT_SERIAL


class ToolError(Exception):
    """User-facing, actionable error surfaced to the MCP client."""


def get_client() -> AutomationClient:
    """Lazily create the SDK client; spawns the automation server on first use."""
    global _client
    with _client_lock:
        if _client is None:
            logger.info("Initializing AutomationClient at %s:%s", HOST, PORT)
            _client = AutomationClient(
                host=HOST,
                port=PORT,
                serial=_session_serial,
                idle_timeout=IDLE_TIMEOUT,
                auto_start_server=AUTO_START,
            )
        return _client


def _use_serial(serial: Optional[str]) -> Optional[str]:
    """Resolve the serial for this call and sync it with the SDK client."""
    global _session_serial
    target = serial or _session_serial
    get_client().serial = target
    _session_serial = target
    return target


def _json(res: Any) -> str:
    return json.dumps(res, ensure_ascii=False, indent=1, default=str)


def _tool(fn):
    """Wrap a tool: convert exceptions into concise, actionable error text."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ToolError as e:
            raise RuntimeError(str(e)) from e
        except Exception as e:
            logger.exception("Tool %s failed", fn.__name__)
            raise RuntimeError(f"{type(e).__name__}: {e}") from e

    return wrapper


def _selector(
    text: Optional[str],
    text_contains: Optional[str],
    resource_id: Optional[str],
    description: Optional[str],
    xpath: Optional[str],
    index: Optional[int],
) -> Optional[dict]:
    sel = {
        k: v
        for k, v in {
            "text": text,
            "text_contains": text_contains,
            "resource_id": resource_id,
            "description": description,
            "xpath": xpath,
            "index": index,
        }.items()
        if v is not None
    }
    return sel or None


def _require_target(
    x: Optional[int], y: Optional[int], sel: Optional[dict], action: str
) -> dict:
    if (x is None) != (y is None):
        raise ToolError(f"{action}: x and y must be provided together.")
    if x is None and not sel:
        raise ToolError(
            f"{action}: provide either x/y coordinates or at least one selector "
            "(text / text_contains / resource_id / description / xpath / index). "
            "Tip: call get_screen_elements first to discover targets."
        )
    return sel or {}


# ---------------------------------------------------------------------------
# System tools
# ---------------------------------------------------------------------------


@mcp.tool()
@_tool
def get_server_status() -> str:
    """Get automation-server status: uptime, idle-watchdog countdown and currently connected devices. The underlying server auto-starts on demand and exits after the idle timeout."""
    res = get_client()._request("GET", "/status")
    return _json(res)


@mcp.tool()
@_tool
def shutdown_automation_server() -> str:
    """Manually stop the background automation server to free resources. It is re-spawned automatically on the next tool call, so this is always safe."""
    try:
        return _json(get_client().shutdown_server())
    except Exception:
        # The server may drop the in-flight connection while stopping; the
        # shutdown signal itself was delivered, so treat this as success.
        return _json({
            "status": "success",
            "message": "Shutdown signal sent (server closed the connection while stopping).",
        })


# ---------------------------------------------------------------------------
# Device tools
# ---------------------------------------------------------------------------


@mcp.tool()
@_tool
def list_devices() -> str:
    """List all Android devices attached via ADB, with their online state and whether a uiautomator2 session is already established."""
    devices = get_client().list_devices()
    if not devices:
        return "No ADB devices attached. Check `adb devices` and USB debugging."
    return _json(devices)


@mcp.tool()
@_tool
def connect_device(serial: Annotated[Optional[str], "Device serial from list_devices. Omit to auto-pick when exactly one device is attached."] = None) -> str:
    """Connect to an Android device and remember it as the default for all subsequent tool calls in this session. Returns screen size and current app."""
    global _session_serial
    res = get_client().connect(serial)
    connected = (res.get("device") or {}).get("serial")
    _session_serial = connected or serial or _session_serial
    get_client().serial = _session_serial
    return _json(res)


@mcp.tool()
@_tool
def disconnect_device(serial: Optional[str] = None) -> str:
    """Disconnect a device and release its uiautomator2 session. Omit serial to disconnect the current default device."""
    _use_serial(serial)
    return _json(get_client()._request("POST", "/device/disconnect", {"serial": serial or _session_serial}))


@mcp.tool()
@_tool
def get_device_info() -> str:
    """Get info about the current device: serial, screen resolution, Android SDK level, screen-on state and the foreground app."""
    return _json(get_client().get_device_info())


# ---------------------------------------------------------------------------
# App tools
# ---------------------------------------------------------------------------


@mcp.tool()
@_tool
def start_app(
    package_name: Annotated[str, "Android package name, e.g. com.android.settings"],
    activity: Annotated[Optional[str], "Optional activity/class to launch directly, e.g. .Settings"] = None,
    stop_first: Annotated[bool, "Force-stop the app before launching (cold start)"] = False,
) -> str:
    """Launch an app on the current device by package name."""
    _use_serial(None)
    return _json(get_client().start_app(package_name, activity=activity, stop_first=stop_first))


@mcp.tool()
@_tool
def stop_app(package_name: str) -> str:
    """Force-stop an app by package name."""
    _use_serial(None)
    return _json(get_client().stop_app(package_name))


@mcp.tool()
@_tool
def clear_app_data(
    package_name: str,
    confirm: Annotated[bool, "Must be true to actually wipe the app's data"] = False,
) -> str:
    """DESTRUCTIVE: clear all user data of an app (logs the user out, wipes settings). Requires confirm=true."""
    if not confirm:
        raise ToolError("clear_app_data wipes all app data. Re-call with confirm=true to proceed.")
    _use_serial(None)
    client = get_client()
    return _json(client._request("POST", "/app/clear", {"serial": client.serial, "package_name": package_name}))


# ---------------------------------------------------------------------------
# Observation tools
# ---------------------------------------------------------------------------


@mcp.tool()
@_tool
def get_screen_elements(raw_json: Annotated[bool, "Also include the structured element list (slower to read for a model)"] = False) -> str:
    """Dump the current screen as a compact numbered list of interactive elements: [index] <type> text="..." id="..." [flags] center=(x,y). This is the cheapest way to observe the screen; use the center coordinates with tap(x, y) or the text/resource_id with selector-based actions."""
    _use_serial(None)
    res = get_client().dump(simplified=True)
    parts = [
        f"Window: {res.get('window_size', {}).get('width')}x{res.get('window_size', {}).get('height')} "
        f"| Interactive elements: {res.get('element_count')}",
        res.get("prompt_view", ""),
    ]
    if raw_json:
        parts.append("Structured elements:\n" + _json(res.get("elements", [])))
    return "\n".join(parts)


@mcp.tool()
@_tool
def screenshot(
    with_som: Annotated[bool, "Overlay numbered boxes matching the element indices from get_screen_elements (Set-of-Marks)"] = False,
    max_dim: Annotated[int, "Downscale so the long edge is at most this many pixels (keeps images small for the model)"] = 1280,
    save_path: Annotated[Optional[str], "Optionally also save the PNG to this absolute file path"] = None,
) -> list:
    """Capture the current screen as an image so you can visually verify state. Returns the image plus a text summary. Combine with_som=true with get_screen_elements to map numbered boxes to element indices."""
    _use_serial(None)
    res = get_client().screenshot(format="PNG", max_dim=None, with_som_overlay=with_som)
    img = PILImage.open(io.BytesIO(base64.b64decode(res["base64"])))
    if max_dim and max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), PILImage.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    if save_path:
        with open(save_path, "wb") as f:
            f.write(buf.getvalue())
    summary = (
        f"Screenshot {img.width}x{img.height}"
        + (f", {res.get('element_count')} interactive elements boxed with their indices" if with_som else "")
        + (f", saved to {save_path}" if save_path else "")
    )
    return [Image(data=buf.getvalue(), format="png"), summary]


# ---------------------------------------------------------------------------
# UI interaction tools
# ---------------------------------------------------------------------------


@mcp.tool()
@_tool
def tap(
    x: Annotated[Optional[int], "X coordinate (e.g. element center from get_screen_elements)"] = None,
    y: Annotated[Optional[int], "Y coordinate"] = None,
    text: Annotated[Optional[str], "Exact visible text of the element to click"] = None,
    text_contains: Annotated[Optional[str], "Substring of the visible text"] = None,
    resource_id: Annotated[Optional[str], "Element resource-id, e.g. com.android:id/button1 (suffix match allowed)"] = None,
    description: Annotated[Optional[str], "Element content-desc"] = None,
    xpath: Annotated[Optional[str], "UI XPath of the element"] = None,
    index: Annotated[Optional[int], "Element index from get_screen_elements"] = None,
    timeout: Annotated[float, "Seconds to wait for the element to appear"] = 10.0,
) -> str:
    """Tap the screen either at (x, y) coordinates or on an element found by selector. Provide coordinates OR at least one selector field."""
    sel = _selector(text, text_contains, resource_id, description, xpath, index)
    _require_target(x, y, sel, "tap")
    _use_serial(None)
    return _json(get_client().click(x=x, y=y, selector=sel, timeout=timeout))


@mcp.tool()
@_tool
def double_tap(
    x: Optional[int] = None,
    y: Optional[int] = None,
    text: Optional[str] = None,
    resource_id: Optional[str] = None,
    index: Optional[int] = None,
) -> str:
    """Double-tap at (x, y) or on an element found by selector (text / resource_id / index)."""
    sel = _selector(None, None, resource_id, None, None, index)
    if text is not None:
        sel = {"text": text, **(sel or {})}
    _require_target(x, y, sel, "double_tap")
    _use_serial(None)
    return _json(get_client().double_click(x=x, y=y, selector=sel))


@mcp.tool()
@_tool
def long_press(
    x: Optional[int] = None,
    y: Optional[int] = None,
    text: Optional[str] = None,
    text_contains: Optional[str] = None,
    resource_id: Optional[str] = None,
    index: Optional[int] = None,
    duration: Annotated[float, "Hold duration in seconds"] = 1.0,
) -> str:
    """Long-press at (x, y) or on an element found by selector (context menus, selection mode, drag handles)."""
    sel = _selector(None, text_contains, resource_id, None, None, index)
    if text is not None:
        sel = {"text": text, **(sel or {})}
    _require_target(x, y, sel, "long_press")
    _use_serial(None)
    return _json(get_client().long_click(x=x, y=y, selector=sel, duration=duration))


@mcp.tool()
@_tool
def input_text(
    content: Annotated[str, "The text to type into the field"],
    target_text: Annotated[Optional[str], "Exact visible text of the target field (omit to type into the currently focused field)"] = None,
    text_contains: Annotated[Optional[str], "Substring of the field's visible text"] = None,
    resource_id: Annotated[Optional[str], "Field resource-id"] = None,
    index: Annotated[Optional[int], "Field index from get_screen_elements"] = None,
    clear: Annotated[bool, "Clear the field before typing"] = True,
) -> str:
    """Type text into an input field found by selector, or into whatever field currently has focus when no selector is given."""
    sel = _selector(None, text_contains, resource_id, None, None, index)
    if target_text is not None:
        sel = {"text": target_text, **(sel or {})}
    _use_serial(None)
    return _json(get_client().input(content, selector=sel, clear=clear))


@mcp.tool()
@_tool
def clear_text(
    target_text: Optional[str] = None,
    text_contains: Optional[str] = None,
    resource_id: Optional[str] = None,
    index: Optional[int] = None,
) -> str:
    """Clear the text of an input field found by selector, or of the currently focused field when no selector is given."""
    sel = _selector(None, text_contains, resource_id, None, None, index)
    if target_text is not None:
        sel = {"text": target_text, **(sel or {})}
    _use_serial(None)
    return _json(get_client().clear_text(selector=sel))


@mcp.tool()
@_tool
def swipe(
    sx: Annotated[int, "Start X"],
    sy: Annotated[int, "Start Y"],
    ex: Annotated[int, "End X"],
    ey: Annotated[int, "End Y"],
    duration: Annotated[float, "Gesture duration in seconds; smaller = faster flick"] = 0.5,
) -> str:
    """Swipe/drag from (sx, sy) to (ex, ey). Get the screen size from get_device_info to compute coordinates."""
    _use_serial(None)
    return _json(get_client().swipe(sx, sy, ex, ey, duration))


@mcp.tool()
@_tool
def scroll(
    direction: Annotated[Literal["up", "down", "left", "right", "forward", "backward"], "forward/down scrolls content down (shows what's below), backward/up scrolls up"] = "down",
) -> str:
    """Scroll the current scrollable view in a direction without needing coordinates."""
    _use_serial(None)
    return _json(get_client().scroll(direction))


@mcp.tool()
@_tool
def press_key(
    key: Annotated[
        Literal[
            "home", "back", "enter", "delete", "recent", "menu", "search",
            "volume_up", "volume_down", "power", "camera", "center",
            "up", "down", "left", "right",
        ],
        "Physical/virtual key name",
    ],
) -> str:
    """Press a device key: home, back, enter, delete, recent (app switcher), menu, search, volume_up/down, power, camera, or D-pad keys."""
    _use_serial(None)
    return _json(get_client().press(key))


@mcp.tool()
@_tool
def find_element(
    text: Optional[str] = None,
    text_contains: Optional[str] = None,
    resource_id: Optional[str] = None,
    description: Optional[str] = None,
    index: Optional[int] = None,
) -> str:
    """Check whether an element matching the selector currently exists on screen. Provide at least one selector field."""
    sel = _selector(text, text_contains, resource_id, description, None, index)
    if not sel:
        raise ToolError("find_element: provide at least one selector (text / text_contains / resource_id / description / index).")
    _use_serial(None)
    return _json(get_client()._request("POST", "/ui/find", {"serial": get_client().serial, "selector": sel}))


@mcp.tool()
@_tool
def wait_for_element(
    text: Optional[str] = None,
    text_contains: Optional[str] = None,
    resource_id: Optional[str] = None,
    index: Optional[int] = None,
    timeout: Annotated[float, "Max seconds to wait"] = 10.0,
) -> str:
    """Block until an element matching the selector appears (e.g. after tapping a button, wait for the next page). Provide at least one selector field."""
    sel = _selector(None, text_contains, resource_id, None, None, index)
    if text is not None:
        sel = {"text": text, **(sel or {})}
    if not sel:
        raise ToolError("wait_for_element: provide at least one selector (text / text_contains / resource_id / index).")
    _use_serial(None)
    found = get_client().wait_for(selector=sel, timeout=timeout)
    return _json({"found": found, "timeout": timeout, "selector": sel})


# ---------------------------------------------------------------------------
# AI tools (require OPENAI_API_KEY / LLM_* env for the automation server)
# ---------------------------------------------------------------------------


@mcp.tool()
@_tool
def ai_understand_screen() -> str:
    """Ask the server-side LLM to semantically analyze the current screen: page type (login/form/list/dialog), purpose and key elements. Requires OPENAI_API_KEY (or LLM_API_KEY / OPENAI_BASE_URL / LLM_MODEL) to be configured; otherwise prefer get_screen_elements + screenshot and analyze yourself."""
    _use_serial(None)
    return _json(get_client().ai_understand(use_vision=True))


@mcp.tool()
@_tool
def ai_execute_goal(
    goal: Annotated[str, "Natural-language goal, e.g. 'open WiFi settings and turn WiFi on'"],
    max_steps: Annotated[int, "Max observe-act steps the server-side agent may take"] = 8,
) -> str:
    """Delegate a natural-language goal to the server-side AI agent, which runs its own observe-think-act loop on the device and returns a step log. Needs OPENAI_API_KEY (or LLM_API_KEY / OPENAI_BASE_URL / LLM_MODEL). Prefer the primitive tools (get_screen_elements + tap + input_text) unless the user explicitly asks to delegate."""
    _use_serial(None)
    return _json(get_client().ai_act(goal, max_steps=max_steps, use_vision=True))


@mcp.tool()
@_tool
def ai_debug_screen(
    auto_fix: Annotated[bool, "Let the server-side agent dismiss crash/ANR/permission dialogs automatically"] = False,
) -> str:
    """Diagnose the current screen for crashes, ANRs, permission blockers or unexpected overlays and report findings; with auto_fix=true it also attempts recovery. Requires OPENAI_API_KEY (or LLM_* env)."""
    _use_serial(None)
    return _json(get_client().ai_debug(auto_fix=auto_fix, use_vision=True))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    # MCP talks JSON-RPC over stdio: never log to stdout.
    logging.basicConfig(
        level=os.getenv("MCP_LOG_LEVEL", "INFO").upper(),
        stream=sys.stderr,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
