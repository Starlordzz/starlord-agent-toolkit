"""
Device Management API Routes.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.core.device_manager import device_manager

router = APIRouter(prefix="/device", tags=["Device"])


class ConnectRequest(BaseModel):
    serial: Optional[str] = None


class DisconnectRequest(BaseModel):
    serial: Optional[str] = None


@router.get("/list")
async def list_devices():
    """List all ADB devices connected to host."""
    devices = device_manager.list_adb_devices()
    return {"status": "success", "devices": devices}


@router.post("/connect")
async def connect_device(req: ConnectRequest = ConnectRequest()):
    """Connect to an Android device via UIAutomator2."""
    try:
        device_manager.connect(req.serial)
        info = device_manager.get_device_info(req.serial)
        return {"status": "success", "message": "Device connected successfully", "device": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_device_info(serial: Optional[str] = None):
    """Get device screen resolution, current app, and hardware info."""
    try:
        info = device_manager.get_device_info(serial)
        return {"status": "success", "device": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect")
async def disconnect_device(req: DisconnectRequest = DisconnectRequest()):
    """Disconnect and clean up UIAutomator2 session."""
    try:
        device_manager.disconnect(req.serial)
        return {"status": "success", "message": f"Device [{req.serial or 'default'}] disconnected."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

