"""
App Lifecycle Control Routes.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.core.device_manager import device_manager
from server.core.actions import ActionEngine

router = APIRouter(prefix="/app", tags=["App Control"])


class StartAppRequest(BaseModel):
    serial: Optional[str] = None
    package_name: str
    activity: Optional[str] = None
    stop_first: bool = False


class StopAppRequest(BaseModel):
    serial: Optional[str] = None
    package_name: str


class ClearAppRequest(BaseModel):
    serial: Optional[str] = None
    package_name: str


@router.post("/start")
async def start_app(req: StartAppRequest):
    """Start an Android application."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        res = engine.start_app(req.package_name, activity=req.activity, stop=req.stop_first)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_app(req: StopAppRequest):
    """Force stop an application."""
    try:
        d = device_manager.get_device(req.serial)
        engine = ActionEngine(d)
        res = engine.stop_app(req.package_name)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current")
async def current_app(serial: Optional[str] = None):
    """Get currently active package and activity."""
    try:
        d = device_manager.get_device(serial)
        engine = ActionEngine(d)
        res = engine.current_app()
        return {"status": "success", "app": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_app(req: ClearAppRequest):
    """Clear application user data."""
    try:
        d = device_manager.get_device(req.serial)
        d.app_clear(req.package_name)
        return {"status": "success", "package": req.package_name, "message": "App data cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

