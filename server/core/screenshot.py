"""
Screenshot capture, base64 encoding, and visual grounding (Set-of-Marks) overlay.
"""
import base64
import io
import logging
from typing import Any, Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont
import uiautomator2 as u2

logger = logging.getLogger("automation.screenshot")


class ScreenshotManager:
    @staticmethod
    def capture_image(d: u2.Device) -> Image.Image:
        """Capture raw PIL Image from device."""
        return d.screenshot()

    @staticmethod
    def image_to_base64(image: Image.Image, format: str = "PNG", quality: int = 85) -> str:
        """Convert PIL Image to base64 data URL or raw base64 string."""
        buffered = io.BytesIO()
        if format.upper() == "JPEG":
            # Convert RGBA to RGB if needed
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            image.save(buffered, format="JPEG", quality=quality)
        else:
            image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @staticmethod
    def capture_base64(d: u2.Device, format: str = "PNG", max_dim: Optional[int] = None) -> str:
        """Capture screenshot and return base64 string, with optional downscaling."""
        img = d.screenshot()
        if max_dim and (img.width > max_dim or img.height > max_dim):
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        return ScreenshotManager.image_to_base64(img, format=format)

    @staticmethod
    def draw_som_overlay(
        image: Image.Image,
        elements: List[Dict[str, Any]],
        box_color: str = "#FF0055",
        text_bg: str = "#FF0055",
        text_color: str = "#FFFFFF",
    ) -> Image.Image:
        """
        Draw Set-of-Marks (SoM) bounding boxes and index tags over the screenshot
        for multimodal AI models to accurately ground UI elements.
        """
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)

        try:
            # Use default font
            font = ImageFont.load_default()
        except Exception:
            font = None

        for el in elements:
            idx = el.get("index")
            bounds = el.get("bounds")
            if not bounds or idx is None:
                continue

            x1, y1, x2, y2 = bounds
            # Draw bounding box
            draw.rectangle([x1, y1, x2, y2], outline=box_color, width=2)

            # Draw label tag at top-left
            tag_text = f" {idx} "
            tag_w = len(tag_text) * 7 + 4
            tag_h = 16
            tag_box = [x1, max(0, y1 - tag_h), x1 + tag_w, max(0, y1 - tag_h) + tag_h]
            draw.rectangle(tag_box, fill=text_bg)
            draw.text((x1 + 2, max(0, y1 - tag_h) + 1), tag_text, fill=text_color, font=font)

        return annotated

