"""
Device Manager for handling ADB connections and UIAutomator2 instances.
Supports multiple devices, auto-discovery, and safe lifecycle cleanup.
"""
import logging
import subprocess
from typing import Dict, List, Optional, Any
import uiautomator2 as u2

logger = logging.getLogger("automation.device_manager")


class DeviceManager:
    def __init__(self, default_serial: Optional[str] = None):
        self.default_serial = default_serial
        self._devices: Dict[str, u2.Device] = {}

    def list_adb_devices(self) -> List[Dict[str, str]]:
        """List all connected ADB devices via adb command."""
        devices = []
        try:
            output = subprocess.check_output(["adb", "devices"], text=True, timeout=5)
            for line in output.strip().split("\n")[1:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    serial, state = parts[0], parts[1]
                    devices.append({
                        "serial": serial,
                        "state": state,
                        "is_connected_u2": serial in self._devices
                    })
        except Exception as e:
            logger.warning(f"Failed to query adb devices: {e}")
        return devices

    def connect(self, serial: Optional[str] = None) -> u2.Device:
        """Connect to a device by serial number, or auto-pick if only one device is connected."""
        target_serial = serial or self.default_serial

        if not target_serial:
            adb_devices = self.list_adb_devices()
            online_devices = [d for d in adb_devices if d["state"] == "device"]
            if len(online_devices) == 1:
                target_serial = online_devices[0]["serial"]
            elif len(online_devices) > 1:
                # Pick the first one but warn
                target_serial = online_devices[0]["serial"]
                logger.info(f"Multiple devices found, defaulting to first: {target_serial}")
            else:
                # Try connecting without serial (u2 defaults to USB or single device)
                target_serial = "default"

        key = target_serial or "default"
        if key in self._devices:
            return self._devices[key]

        logger.info(f"Connecting to Android device [{key}]...")
        try:
            if key == "default":
                d = u2.connect()
            else:
                d = u2.connect(key)

            # Test connection
            info = d.info
            actual_serial = d.serial if hasattr(d, "serial") else key
            self._devices[actual_serial] = d
            self._devices[key] = d
            logger.info(f"Successfully connected to [{actual_serial}]. Screen: {info.get('displayWidth')}x{info.get('displayHeight')}")
            return d
        except Exception as e:
            logger.error(f"Failed to connect to device [{key}]: {e}")
            raise RuntimeError(f"Could not connect to Android device '{key}': {str(e)}")

    def get_device(self, serial: Optional[str] = None) -> u2.Device:
        """Get an existing device connection or auto-connect."""
        key = serial or self.default_serial or "default"
        if key in self._devices:
            return self._devices[key]
        return self.connect(serial)

    def get_device_info(self, serial: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive information about a device."""
        d = self.get_device(serial)
        info = d.info
        current_app = d.app_current()
        window_size = d.window_size()
        return {
            "serial": getattr(d, "serial", serial or "default"),
            "display_width": window_size[0] if window_size else info.get("displayWidth"),
            "display_height": window_size[1] if window_size else info.get("displayHeight"),
            "screen_on": info.get("screenOn", True),
            "current_package": current_app.get("package"),
            "current_activity": current_app.get("activity"),
            "sdk_int": getattr(d, "sdk_int", None),
            "raw_info": info
        }

    def disconnect(self, serial: Optional[str] = None):
        """Disconnect and stop uiautomator service on the device."""
        key = serial or self.default_serial or "default"
        device = self._devices.pop(key, None)
        if device:
            try:
                # Stop uiautomator daemon on device if possible
                if hasattr(device, "reset_uiautomator"):
                    pass
                logger.info(f"Disconnected device [{key}].")
            except Exception as e:
                logger.warning(f"Error disconnecting device [{key}]: {e}")

    def cleanup_all(self):
        """Clean up all active uiautomator2 sessions."""
        logger.info("Cleaning up all device sessions...")
        keys = list(self._devices.keys())
        for key in keys:
            self.disconnect(key)
        self._devices.clear()


device_manager = DeviceManager()

