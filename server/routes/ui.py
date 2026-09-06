"""
UI Automation and Interaction API Routes.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field
from server.core.device_manager import device_manager
from server.core.actions import ActionEngine
from server.core.hierarchy import HierarchyParser
from server.core.screenshot import ScreenshotManager

router = APIRouter(prefix="/ui", tags=["UI Interaction"])


class SelectorParams(BaseModel):
    text: Optional[str] = None
    text_contains: Optional[str] = None
    text_matches: Optional[str] = None
    resource_id: Optional[str] = None
    resource_id_matches: Optional[str] = None
    class_name: Optional[str] = None
    description: Optional[str] = None
    description_contains: Optional[str] = None
    xpath: Optional[str] = None
    index: Optional[int] = None


class ClickRequest(BaseModel):
    serial: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    selector: Optional[SelectorParams] = None
    timeout: float = 10.0


class DoubleClickRequest(BaseModel):
    serial: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    selector: Optional[SelectorParams] = None
    duration: float = 0.1


class LongClickRequest(BaseModel):
    serial: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    selector: Optional[SelectorParams] = None
    duration: float = 1.0


class InputRequest(BaseModel):
    serial: Optional[str] = None
    text: str
    selector: Optional[SelectorParams] = None
    clear: bool = True


class ClearTextRequest(BaseModel):
    serial: Optional[str] = None
    selector: Optional[SelectorParams] = None


class SwipeRequest(BaseModel):
    serial: Optional[str] = None
    sx: int
    sy: int
    ex: int
    ey: int
    duration: float = 0.5


class ScrollRequest(BaseModel):
    serial: Optional[str] = None
    direction: str = "forward"  # forward, backward, up, down, left, right


class PressKeyRequest(BaseModel):
    serial: Optional[str] = None
    key: str  # back, home, enter, volume_up, power, etc.


class ScreenshotRequest(BaseModel):
    serial: Optional[str] = None
    format: str = "PNG"
    max_dim: Optional[int] = None
    with_som_overlay: bool = False


class DumpRequest(BaseModel):
    serial: Optional[str] = None
    simplified: bool = True
    include_xml: bool = False


class FindRequest(BaseModel):
    serial: Optional[str] = None
    selector: SelectorParams


class WaitRequest(BaseModel):
    serial: Optional[str] = None
    selector: SelectorParams
    timeout: float = 10.0


@router.post("/click")
async def click(req: ClickRequest):
    """Click on coordinates (x, y) or an element resolved by selector."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        selector_dict = req.selector.model_dump(exclude_none=True) if req.selector else None
        res = engine.click(x=req.x, y=req.y, selector_params=selector_dict, timeout=req.timeout)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/double_click")
async def double_click(req: DoubleClickRequest):
    """Double click on target."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        selector_dict = req.selector.model_dump(exclude_none=True) if req.selector else None
        res = engine.double_click(x=req.x, y=req.y, selector_params=selector_dict, duration=req.duration)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/long_click")
async def long_click(req: LongClickRequest):
    """Long click on target."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        selector_dict = req.selector.model_dump(exclude_none=True) if req.selector else None
        res = engine.long_click(x=req.x, y=req.y, selector_params=selector_dict, duration=req.duration)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/input")
async def input_text(req: InputRequest):
    """Input text into selector target or current focus."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        selector_dict = req.selector.model_dump(exclude_none=True) if req.selector else None
        res = engine.input_text(text=req.text, selector_params=selector_dict, clear=req.clear)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_text(req: ClearTextRequest):
    """Clear text in target element or active focus."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        selector_dict = req.selector.model_dump(exclude_none=True) if req.selector else None
        res = engine.clear_text(selector_params=selector_dict)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/swipe")
async def swipe(req: SwipeRequest):
    """Swipe across the screen."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        res = engine.swipe(sx=req.sx, sy=req.sy, ex=req.ex, ey=req.ey, duration=req.duration)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scroll")
async def scroll(req: ScrollRequest):
    """Scroll in a specified direction."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        res = engine.scroll(direction=req.direction)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/press")
async def press_key(req: PressKeyRequest):
    """Press a physical/virtual key."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        res = engine.press_key(key=req.key)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/screenshot")
async def take_screenshot(req: ScreenshotRequest = ScreenshotRequest()):
    """Capture screen and return base64 string or Set-of-Marks overlay."""
    try:
        d = device_manager.get_device(req.serial)
        if req.with_som_overlay:
            raw_img = ScreenshotManager.capture_image(d)
            w, h = d.window_size()
            xml = d.dump_hierarchy()
            elements = HierarchyParser.extract_interactive_elements(xml, w, h)
            som_img = ScreenshotManager.draw_som_overlay(raw_img, elements)
            b64 = ScreenshotManager.image_to_base64(som_img, format=req.format)
            return {
                "status": "success",
                "format": req.format,
                "width": som_img.width,
                "height": som_img.height,
                "base64": b64,
                "element_count": len(elements),
            }
        else:
            b64 = ScreenshotManager.capture_base64(d, format=req.format, max_dim=req.max_dim)
            w, h = d.window_size()
            return {
                "status": "success",
                "format": req.format,
                "width": w,
                "height": h,
                "base64": b64,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dump")
async def dump_ui(req: DumpRequest = DumpRequest()):
    """Dump screen UI hierarchy and extract indexed interactive elements."""
    try:
        d = device_manager.get_device(req.serial)
        w, h = d.window_size()
        xml = d.dump_hierarchy()

        result: Dict[str, Any] = {"status": "success", "window_size": {"width": w, "height": h}}

        if req.simplified:
            elements = HierarchyParser.extract_interactive_elements(xml, w, h)
            result["elements"] = elements
            result["element_count"] = len(elements)
            result["prompt_view"] = HierarchyParser.format_elements_for_prompt(elements)

        if req.include_xml:
            result["xml"] = xml

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find")
async def find_element(req: FindRequest):
    """Find element matching selector and return its existence and position."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        selector_dict = req.selector.model_dump(exclude_none=True)
        exists = engine.exists(selector_dict)
        return {"status": "success", "exists": exists, "selector": selector_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wait")
async def wait_element(req: WaitRequest):
    """Wait for an element matching selector to appear within timeout."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        selector_dict = req.selector.model_dump(exclude_none=True)
        exists = engine.exists(selector_dict, timeout=req.timeout)
        return {"status": "success", "found": exists, "timeout": req.timeout, "selector": selector_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

