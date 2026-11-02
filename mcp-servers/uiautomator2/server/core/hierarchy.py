"""
UI Hierarchy parser, JSON transformer, and AI-optimized element indexer.
"""
import logging
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("automation.hierarchy")


def parse_bounds(bounds_str: str) -> Optional[Tuple[int, int, int, int]]:
    """Parse bounds string '[x1,y1][x2,y2]' into (x1, y1, x2, y2)."""
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
    if match:
        return (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            int(match.group(4)),
        )
    return None


class HierarchyParser:
    """Parses uiautomator XML dump and extracts clean, AI-ready interactive element lists."""

    @staticmethod
    def xml_to_dict(element: ET.Element) -> Dict[str, Any]:
        """Convert an XML element tree recursively to a clean dictionary."""
        attrib = dict(element.attrib)
        bounds = attrib.get("bounds")
        if bounds:
            parsed_bounds = parse_bounds(bounds)
            if parsed_bounds:
                attrib["parsed_bounds"] = {
                    "left": parsed_bounds[0],
                    "top": parsed_bounds[1],
                    "right": parsed_bounds[2],
                    "bottom": parsed_bounds[3],
                    "center_x": (parsed_bounds[0] + parsed_bounds[2]) // 2,
                    "center_y": (parsed_bounds[1] + parsed_bounds[3]) // 2,
                    "width": parsed_bounds[2] - parsed_bounds[0],
                    "height": parsed_bounds[3] - parsed_bounds[1],
                }

        node: Dict[str, Any] = {
            "tag": element.tag,
            "attributes": attrib,
            "children": [HierarchyParser.xml_to_dict(child) for child in element],
        }
        return node

    @classmethod
    def extract_interactive_elements(
        cls,
        xml_content: str,
        screen_width: int = 1080,
        screen_height: int = 2400,
        only_visible: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Extract meaningful, interactive, or text-bearing UI elements
        and assign sequential indices for AI and selector lookup.
        """
        try:
            root = ET.fromstring(xml_content)
        except Exception as e:
            logger.error(f"Failed to parse UI hierarchy XML: {e}")
            return []

        elements: List[Dict[str, Any]] = []
        index_counter = 1

        def traverse(node: ET.Element):
            nonlocal index_counter
            attrib = node.attrib
            bounds_str = attrib.get("bounds", "")
            bounds = parse_bounds(bounds_str)

            text = attrib.get("text", "").strip()
            content_desc = attrib.get("content-desc", "").strip()
            resource_id = attrib.get("resource-id", "").strip()
            class_name = attrib.get("class", "").split(".")[-1]
            clickable = attrib.get("clickable", "false") == "true"
            scrollable = attrib.get("scrollable", "false") == "true"
            checkable = attrib.get("checkable", "false") == "true"
            editable = attrib.get("editable", "false") == "true" or "EditText" in class_name

            # Check visibility
            is_valid_size = False
            if bounds:
                x1, y1, x2, y2 = bounds
                w, h = x2 - x1, y2 - y1
                # Must have positive size and be within or partially within screen
                if w > 0 and h > 0 and x1 < screen_width and y1 < screen_height and x2 > 0 and y2 > 0:
                    is_valid_size = True

            # Decide if this element is meaningful for AI / automation
            is_meaningful = (
                clickable
                or editable
                or scrollable
                or checkable
                or bool(text)
                or bool(content_desc)
            )

            if is_valid_size and is_meaningful:
                cx = (bounds[0] + bounds[2]) // 2
                cy = (bounds[1] + bounds[3]) // 2

                elem_data = {
                    "index": index_counter,
                    "type": class_name,
                    "text": text,
                    "content_desc": content_desc,
                    "resource_id": resource_id,
                    "clickable": clickable,
                    "editable": editable,
                    "scrollable": scrollable,
                    "checkable": checkable,
                    "bounds": [bounds[0], bounds[1], bounds[2], bounds[3]],
                    "center": [cx, cy],
                    "size": [bounds[2] - bounds[0], bounds[3] - bounds[1]],
                }
                elements.append(elem_data)
                index_counter += 1

            for child in node:
                traverse(child)

        traverse(root)
        return elements

    @classmethod
    def format_elements_for_prompt(cls, elements: List[Dict[str, Any]]) -> str:
        """Format the extracted elements into a compact, human-readable prompt string for LLM."""
        if not elements:
            return "No interactive UI elements detected on screen."

        lines = ["--- Screen UI Elements ---"]
        for el in elements:
            idx = el["index"]
            elem_type = el["type"]
            text_part = f' text="{el["text"]}"' if el["text"] else ""
            desc_part = f' desc="{el["content_desc"]}"' if el["content_desc"] else ""
            id_part = f' id="{el["resource_id"]}"' if el["resource_id"] else ""
            flags = []
            if el["clickable"]:
                flags.append("click")
            if el["editable"]:
                flags.append("edit")
            if el["scrollable"]:
                flags.append("scroll")
            flags_str = f" [{','.join(flags)}]" if flags else ""
            cx, cy = el["center"]
            lines.append(
                f"[{idx}] <{elem_type}>{text_part}{desc_part}{id_part}{flags_str} center=({cx},{cy})"
            )
        lines.append("--------------------------")
        return "\n".join(lines)

