"""
High-Level Automation Client for Python.
"""
import base64
import logging
from typing import Any, Dict, List, Optional, Union
import httpx
from automation_client.launcher import ServerLauncher
from automation_client.models import LLMConfig, Selector

logger = logging.getLogger("automation.client")


class AutomationClient:
    """Client for controlling Android UI via the on-demand Automation Server."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8765,
        serial: Optional[str] = None,
        idle_timeout: int = 60,
        auto_start_server: bool = True,
        llm_config: Optional[LLMConfig] = None,
    ):
        self.host = host
        self.port = port
        self.serial = serial
        self.idle_timeout = idle_timeout
        self.auto_start_server = auto_start_server
        self.llm_config = llm_config
        self.base_url = f"http://{host}:{port}"
        self._http = httpx.Client(base_url=self.base_url, timeout=30.0)

        if self.auto_start_server:
            self._ensure_server()

    def _ensure_server(self):
        ServerLauncher.ensure_server_running(
            host=self.host,
            port=self.port,
            idle_timeout=self.idle_timeout,
            serial=self.serial,
        )

    def _request(self, method: str, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.auto_start_server and not ServerLauncher.is_server_alive(self.base_url):
            self._ensure_server()

        resp = self._http.request(method, endpoint, json=json)
        if resp.status_code >= 400:
            raise RuntimeError(f"Automation Server Error ({resp.status_code}): {resp.text}")
        return resp.json()

    def connect(self, serial: Optional[str] = None) -> Dict[str, Any]:
        """Connect to an Android device."""
        target_serial = serial or self.serial
        res = self._request("POST", "/device/connect", {"serial": target_serial})
        if res.get("device") and res["device"].get("serial"):
            self.serial = res["device"]["serial"]
        return res

    def get_device_info(self) -> Dict[str, Any]:
        """Get device hardware and screen info."""
        return self._request("GET", f"/device/info?serial={self.serial or ''}")

    def list_devices(self) -> List[Dict[str, Any]]:
        """List all connected ADB devices."""
        return self._request("GET", "/device/list").get("devices", [])

    def _build_selector(
        self,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        class_name: Optional[str] = None,
        description: Optional[str] = None,
        xpath: Optional[str] = None,
        index: Optional[int] = None,
        selector: Optional[Union[Selector, Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        if selector:
            if isinstance(selector, Selector):
                return selector.to_dict()
            return selector

        s = Selector(
            text=text,
            text_contains=text_contains,
            resource_id=resource_id,
            class_name=class_name,
            description=description,
            xpath=xpath,
            index=index,
        )
        d = s.to_dict()
        return d if d else None

    # UI Interaction Actions
    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        class_name: Optional[str] = None,
        description: Optional[str] = None,
        xpath: Optional[str] = None,
        index: Optional[int] = None,
        selector: Optional[Union[Selector, Dict[str, Any]]] = None,
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """Click on coordinates (x, y) or an element resolved by selector."""
        sel = self._build_selector(
            text=text,
            text_contains=text_contains,
            resource_id=resource_id,
            class_name=class_name,
            description=description,
            xpath=xpath,
            index=index,
            selector=selector,
        )
        payload = {
            "serial": self.serial,
            "x": x,
            "y": y,
            "selector": sel,
            "timeout": timeout,
        }
        return self._request("POST", "/ui/click", payload)

    def double_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        text: Optional[str] = None,
        resource_id: Optional[str] = None,
        selector: Optional[Union[Selector, Dict[str, Any]]] = None,
        duration: float = 0.1,
    ) -> Dict[str, Any]:
        """Double click on target."""
        sel = self._build_selector(text=text, resource_id=resource_id, selector=selector)
        payload = {"serial": self.serial, "x": x, "y": y, "selector": sel, "duration": duration}
        return self._request("POST", "/ui/double_click", payload)

    def long_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        text: Optional[str] = None,
        resource_id: Optional[str] = None,
        selector: Optional[Union[Selector, Dict[str, Any]]] = None,
        duration: float = 1.0,
    ) -> Dict[str, Any]:
        """Long click on target."""
        sel = self._build_selector(text=text, resource_id=resource_id, selector=selector)
        payload = {"serial": self.serial, "x": x, "y": y, "selector": sel, "duration": duration}
        return self._request("POST", "/ui/long_click", payload)

    def input(
        self,
        text: str,
        target_text: Optional[str] = None,
        resource_id: Optional[str] = None,
        selector: Optional[Union[Selector, Dict[str, Any]]] = None,
        clear: bool = True,
    ) -> Dict[str, Any]:
        """Input text into target element or current focus."""
        sel = self._build_selector(text=target_text, resource_id=resource_id, selector=selector)
        payload = {"serial": self.serial, "text": text, "selector": sel, "clear": clear}
        return self._request("POST", "/ui/input", payload)

    def clear_text(
        self,
        target_text: Optional[str] = None,
        resource_id: Optional[str] = None,
        selector: Optional[Union[Selector, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Clear text in target element or active focus."""
        sel = self._build_selector(text=target_text, resource_id=resource_id, selector=selector)
        payload = {"serial": self.serial, "selector": sel}
        return self._request("POST", "/ui/clear", payload)

    def swipe(self, sx: int, sy: int, ex: int, ey: int, duration: float = 0.5) -> Dict[str, Any]:
        """Swipe across screen."""
        payload = {"serial": self.serial, "sx": sx, "sy": sy, "ex": ex, "ey": ey, "duration": duration}
        return self._request("POST", "/ui/swipe", payload)

    def scroll(self, direction: str = "forward") -> Dict[str, Any]:
        """Scroll forward / backward / up / down / left / right."""
        payload = {"serial": self.serial, "direction": direction}
        return self._request("POST", "/ui/scroll", payload)

    def press(self, key: str = "back") -> Dict[str, Any]:
        """Press key (back, home, enter, etc.)."""
        payload = {"serial": self.serial, "key": key}
        return self._request("POST", "/ui/press", payload)

    def screenshot(
        self,
        format: str = "PNG",
        max_dim: Optional[int] = None,
        with_som_overlay: bool = False,
        save_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Capture screenshot as base64 and optionally save to file."""
        payload = {
            "serial": self.serial,
            "format": format,
            "max_dim": max_dim,
            "with_som_overlay": with_som_overlay,
        }
        res = self._request("POST", "/ui/screenshot", payload)
        if save_path and "base64" in res:
            with open(save_path, "wb") as f:
                f.write(base64.b64decode(res["base64"]))
        return res

    def dump(self, simplified: bool = True, include_xml: bool = False) -> Dict[str, Any]:
        """Dump UI hierarchy and interactive elements."""
        payload = {"serial": self.serial, "simplified": simplified, "include_xml": include_xml}
        return self._request("POST", "/ui/dump", payload)

    def exists(
        self,
        text: Optional[str] = None,
        resource_id: Optional[str] = None,
        selector: Optional[Union[Selector, Dict[str, Any]]] = None,
    ) -> bool:
        """Check if an element exists on screen."""
        sel = self._build_selector(text=text, resource_id=resource_id, selector=selector)
        if not sel:
            return False
        res = self._request("POST", "/ui/find", {"serial": self.serial, "selector": sel})
        return res.get("exists", False)

    def wait_for(
        self,
        text: Optional[str] = None,
        resource_id: Optional[str] = None,
        selector: Optional[Union[Selector, Dict[str, Any]]] = None,
        timeout: float = 10.0,
    ) -> bool:
        """Wait for an element to appear within timeout."""
        sel = self._build_selector(text=text, resource_id=resource_id, selector=selector)
        if not sel:
            return False
        res = self._request("POST", "/ui/wait", {"serial": self.serial, "selector": sel, "timeout": timeout})
        return res.get("found", False)

    # App Lifecycle
    def start_app(self, package_name: str, activity: Optional[str] = None, stop_first: bool = False) -> Dict[str, Any]:
        """Start an app by package name."""
        payload = {"serial": self.serial, "package_name": package_name, "activity": activity, "stop_first": stop_first}
        return self._request("POST", "/app/start", payload)

    def stop_app(self, package_name: str) -> Dict[str, Any]:
        """Stop an app."""
        payload = {"serial": self.serial, "package_name": package_name}
        return self._request("POST", "/app/stop", payload)

    def current_app(self) -> Dict[str, Any]:
        """Get current active app info."""
        return self._request("GET", f"/app/current?serial={self.serial or ''}").get("app", {})

    # AI Agent Capabilities
    def ai_understand(self, use_vision: bool = True) -> Dict[str, Any]:
        """Understand current screen semantically."""
        payload = {
            "serial": self.serial,
            "use_vision": use_vision,
            "llm": self.llm_config.model_dump(exclude_none=True) if self.llm_config else None,
        }
        return self._request("POST", "/ai/understand", payload)

    def ai_act(
        self,
        goal: str,
        max_steps: int = 8,
        use_vision: bool = True,
        step_delay: float = 1.0,
    ) -> Dict[str, Any]:
        """Autonomously execute a natural language goal on device."""
        payload = {
            "serial": self.serial,
            "goal": goal,
            "max_steps": max_steps,
            "use_vision": use_vision,
            "step_delay": step_delay,
            "llm": self.llm_config.model_dump(exclude_none=True) if self.llm_config else None,
        }
        return self._request("POST", "/ai/act", payload)

    def ai_debug(self, auto_fix: bool = False, use_vision: bool = True) -> Dict[str, Any]:
        """Inspect and debug screen issues (crashes, ANRs, popups)."""
        payload = {
            "serial": self.serial,
            "auto_fix": auto_fix,
            "use_vision": use_vision,
            "llm": self.llm_config.model_dump(exclude_none=True) if self.llm_config else None,
        }
        return self._request("POST", "/ai/debug", payload)

    # Server control
    def shutdown_server(self) -> Dict[str, Any]:
        """Manually trigger server shutdown."""
        return self._request("POST", "/shutdown")

