"""
Core Action Execution Engine for UIAutomator2.
Handles selector resolution, low-level gestures, text input, key events, and app lifecycle.
"""
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import uiautomator2 as u2
from server.core.hierarchy import HierarchyParser

logger = logging.getLogger("automation.actions")


class ActionEngine:
    """Executes automation actions on a given uiautomator2 Device instance."""

    def __init__(self, device: u2.Device):
        self.d = device

    def resolve_selector(
        self,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        text_matches: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_id_matches: Optional[str] = None,
        class_name: Optional[str] = None,
        description: Optional[str] = None,
        description_contains: Optional[str] = None,
        xpath: Optional[str] = None,
        index: Optional[int] = None,
    ) -> Any:
        """
        Build a UIAutomator2 UiObject or XPathSelector based on given parameters.
        If index is provided, dumps hierarchy and finds the indexed element.
        """
        if xpath:
            return self.d.xpath(xpath)

        if index is not None:
            xml = self.d.dump_hierarchy()
            w, h = self.d.window_size()
            elements = HierarchyParser.extract_interactive_elements(xml, w, h)
            target = next((el for el in elements if el["index"] == index), None)
            if target:
                cx, cy = target["center"]
                # Return a virtual coordinate clicker
                return {"type": "point", "x": cx, "y": cy, "bounds": target["bounds"], "raw": target}
            raise ValueError(f"Element with index [{index}] not found on screen.")

        kwargs = {}
        if text is not None:
            kwargs["text"] = text
        if text_contains is not None:
            kwargs["textContains"] = text_contains
        if text_matches is not None:
            kwargs["textMatches"] = text_matches
        if resource_id is not None:
            kwargs["resourceId"] = resource_id
        if resource_id_matches is not None:
            kwargs["resourceIdMatches"] = resource_id_matches
        if class_name is not None:
            kwargs["className"] = class_name
        if description is not None:
            kwargs["description"] = description
        if description_contains is not None:
            kwargs["descriptionContains"] = description_contains

        if not kwargs:
            return None

        return self.d(**kwargs)

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        selector_params: Optional[Dict[str, Any]] = None,
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """Click on coordinates or a resolved selector."""
        if x is not None and y is not None:
            self.d.click(x, y)
            return {"status": "success", "action": "click", "target": {"x": x, "y": y}}

        if selector_params:
            obj = self.resolve_selector(**selector_params)
            if isinstance(obj, dict) and obj.get("type") == "point":
                self.d.click(obj["x"], obj["y"])
                return {"status": "success", "action": "click", "target": obj}

            if obj is not None:
                if hasattr(obj, "click"):
                    # XPath or UIObject
                    if hasattr(obj, "wait"):
                        if not obj.wait(timeout=timeout):
                            raise TimeoutError(f"Element matching {selector_params} did not appear within {timeout}s.")
                    obj.click()
                    return {"status": "success", "action": "click", "target": selector_params}

        raise ValueError("Must provide either (x, y) coordinates or valid selector parameters.")

    def double_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        selector_params: Optional[Dict[str, Any]] = None,
        duration: float = 0.1,
    ) -> Dict[str, Any]:
        """Double click on target."""
        if x is not None and y is not None:
            self.d.double_click(x, y, duration=duration)
            return {"status": "success", "action": "double_click", "target": {"x": x, "y": y}}

        if selector_params:
            obj = self.resolve_selector(**selector_params)
            if isinstance(obj, dict) and obj.get("type") == "point":
                self.d.double_click(obj["x"], obj["y"], duration=duration)
                return {"status": "success", "action": "double_click", "target": obj}
            if obj is not None:
                obj.double_click(duration=duration)
                return {"status": "success", "action": "double_click", "target": selector_params}

        raise ValueError("Must provide either (x, y) coordinates or valid selector parameters.")

    def long_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        selector_params: Optional[Dict[str, Any]] = None,
        duration: float = 1.0,
    ) -> Dict[str, Any]:
        """Long click on target."""
        if x is not None and y is not None:
            self.d.long_click(x, y, duration=duration)
            return {"status": "success", "action": "long_click", "target": {"x": x, "y": y}}

        if selector_params:
            obj = self.resolve_selector(**selector_params)
            if isinstance(obj, dict) and obj.get("type") == "point":
                self.d.long_click(obj["x"], obj["y"], duration=duration)
                return {"status": "success", "action": "long_click", "target": obj}
            if obj is not None:
                obj.long_click(duration=duration)
                return {"status": "success", "action": "long_click", "target": selector_params}

        raise ValueError("Must provide either (x, y) coordinates or valid selector parameters.")

    def input_text(
        self,
        text: str,
        selector_params: Optional[Dict[str, Any]] = None,
        clear: bool = True,
    ) -> Dict[str, Any]:
        """Input text into focused element or element matching selector."""
        if selector_params:
            obj = self.resolve_selector(**selector_params)
            if isinstance(obj, dict) and obj.get("type") == "point":
                self.d.click(obj["x"], obj["y"])
                time.sleep(0.2)
                if clear:
                    self.d.clear_text()
                self.d.send_keys(text)
                return {"status": "success", "action": "input", "text": text, "target": obj}

            if obj is not None:
                if clear:
                    obj.clear_text()
                obj.set_text(text)
                return {"status": "success", "action": "input", "text": text, "target": selector_params}

        # If no selector, type into current active focus
        if clear:
            self.d.clear_text()
        self.d.send_keys(text)
        return {"status": "success", "action": "input", "text": text, "target": "current_focus"}

    def clear_text(self, selector_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Clear text on target element or active focus."""
        if selector_params:
            obj = self.resolve_selector(**selector_params)
            if obj is not None and hasattr(obj, "clear_text"):
                obj.clear_text()
                return {"status": "success", "action": "clear_text", "target": selector_params}
        self.d.clear_text()
        return {"status": "success", "action": "clear_text", "target": "current_focus"}

    def swipe(
        self,
        sx: int,
        sy: int,
        ex: int,
        ey: int,
        duration: float = 0.5,
    ) -> Dict[str, Any]:
        """Swipe from (sx, sy) to (ex, ey)."""
        self.d.swipe(sx, sy, ex, ey, duration=duration)
        return {
            "status": "success",
            "action": "swipe",
            "start": {"x": sx, "y": sy},
            "end": {"x": ex, "y": ey},
            "duration": duration,
        }

    def scroll(self, direction: str = "forward") -> Dict[str, Any]:
        """Scroll forward/backward/up/down."""
        direction = direction.lower()
        w, h = self.d.window_size()
        cx = w // 2
        if direction in ("forward", "down"):
            self.d.swipe(cx, int(h * 0.75), cx, int(h * 0.25), duration=0.4)
        elif direction in ("backward", "up"):
            self.d.swipe(cx, int(h * 0.25), cx, int(h * 0.75), duration=0.4)
        elif direction == "left":
            self.d.swipe(int(w * 0.8), h // 2, int(w * 0.2), h // 2, duration=0.4)
        elif direction == "right":
            self.d.swipe(int(w * 0.2), h // 2, int(w * 0.8), h // 2, duration=0.4)
        else:
            raise ValueError(f"Unsupported scroll direction: {direction}")

        return {"status": "success", "action": "scroll", "direction": direction}

    def press_key(self, key: str) -> Dict[str, Any]:
        """Press physical or virtual key (home, back, enter, volume_up, power, etc.)."""
        self.d.press(key.lower())
        return {"status": "success", "action": "press_key", "key": key}

    def exists(self, selector_params: Dict[str, Any], timeout: float = 0.0) -> bool:
        """Check if an element exists."""
        obj = self.resolve_selector(**selector_params)
        if isinstance(obj, dict) and obj.get("type") == "point":
            return True
        if obj is not None:
            if timeout > 0 and hasattr(obj, "wait"):
                return bool(obj.wait(timeout=timeout))
            return bool(obj.exists)
        return False

    # App Control
    def start_app(self, package_name: str, activity: Optional[str] = None, stop: bool = False) -> Dict[str, Any]:
        """Start an application by package name."""
        self.d.app_start(package_name, activity=activity, stop=stop)
        return {"status": "success", "action": "start_app", "package": package_name, "activity": activity}

    def stop_app(self, package_name: str) -> Dict[str, Any]:
        """Stop an application."""
        self.d.app_stop(package_name)
        return {"status": "success", "action": "stop_app", "package": package_name}

    def current_app(self) -> Dict[str, Any]:
        """Get current running app details."""
        return self.d.app_current()

