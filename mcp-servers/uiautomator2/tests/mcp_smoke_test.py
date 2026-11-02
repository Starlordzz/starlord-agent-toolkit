"""
Protocol-level smoke test for the MCP server.

Run directly (not collected by pytest):
    uv run python tests/mcp_smoke_test.py

Spawns the MCP server over stdio exactly like a real client would, lists tools,
then exercises the error path and (if an ADB device is attached) a full
observe-act-verify loop against the real device. Non-destructive: only opens
Settings, presses Home/Back.
"""
import asyncio
import base64
import json
import os
import sys
from datetime import timedelta

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def show(label: str, res) -> None:
    text = res.content[0].text if res.content else ""
    print(f"\n=== {label} | isError={res.isError} ===")
    print(text[:600])


async def main() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
        cwd=ROOT,
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=180)) as session:
            await session.initialize()
            print("MCP session initialized.")

            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            print(f"\nTOOLS ({len(names)}):", ", ".join(names))

            # 1. Server status (triggers automation-server auto-start on first call)
            show("get_server_status", await session.call_tool("get_server_status", {}))

            # 2. Devices
            show("list_devices", await session.call_tool("list_devices", {}))

            # 3. Error path: tap without any target must be a clean tool error
            show("tap (no args, expect isError=True)", await session.call_tool("tap", {}))

            # 4. Destructive-tool guard
            show("clear_app_data (no confirm)", await session.call_tool("clear_app_data", {"package_name": "com.example"}))

            # --- Everything below touches the real device (skipped if none) ---
            devs = await session.call_tool("list_devices", {})
            online = [d for d in json.loads(devs.content[0].text) if d.get("state") == "device"]
            if not online:
                print("\nNo online ADB device — skipping device e2e section.")
                return

            show("connect_device", await session.call_tool("connect_device", {}))
            show("get_device_info", await session.call_tool("get_device_info", {}))

            # Open Settings via the app tool
            show("start_app settings", await session.call_tool("start_app", {"package_name": "com.android.settings"}))
            await asyncio.sleep(2)

            show("get_screen_elements", await session.call_tool("get_screen_elements", {}))

            # Screenshot: verify we get a real image back
            res = await session.call_tool("screenshot", {"with_som": True})
            img_items = [c for c in res.content if c.type == "image"]
            texts = [c.text for c in res.content if c.type == "text"]
            ok = bool(img_items) and img_items[0].mimeType == "image/png" and len(img_items[0].data) > 1000
            print(f"\n=== screenshot | isError={res.isError} | image={'yes' if img_items else 'no'} "
                  f"| mime={img_items[0].mimeType if img_items else '-'} | b64_len={len(img_items[0].data) if img_items else 0} ===")
            print(texts[0] if texts else "")
            if ok:
                png = base64.b64decode(img_items[0].data)
                out = os.path.join(ROOT, "tests", "_smoke_screenshot.png")
                with open(out, "wb") as f:
                    f.write(png)
                print(f"Saved decoded image to {out} ({len(png)} bytes, PNG magic={png[:4]!r})")

            # Navigate home again
            show("press_key home", await session.call_tool("press_key", {"key": "home"}))

            # Final status + graceful shutdown of the background automation server
            show("get_server_status (before shutdown)", await session.call_tool("get_server_status", {}))
            show("shutdown_automation_server", await session.call_tool("shutdown_automation_server", {}))

    print("\nSMOKE TEST COMPLETE")


if __name__ == "__main__":
    asyncio.run(main())
