"""
Basic UI Automation Demo using Python SDK.
Demonstrates auto-spawning the server, connecting to Android, clicking, inputting, and taking screenshots.
"""
import time
from automation_client import AutomationClient

def main():
    print("=== Step 1: Initializing Automation Client ===")
    # Client will automatically start server if it is not currently running
    client = AutomationClient(
        host="127.0.0.1",
        port=8765,
        idle_timeout=60,  # Will auto-shutdown 60s after last request
        auto_start_server=True,
    )

    print("=== Step 2: Connecting to Android Device ===")
    conn = client.connect()
    print("Connected:", conn)

    info = client.get_device_info()
    print(f"Device Info: {info['device']['serial']} ({info['device']['display_width']}x{info['device']['display_height']})")

    print("=== Step 3: Taking Screenshot ===")
    shot = client.screenshot(save_path="screen.png")
    print(f"Screenshot captured: {shot['width']}x{shot['height']}")

    print("=== Step 4: UI Hierarchy Dump ===")
    dump = client.dump(simplified=True)
    print(f"Found {dump['element_count']} interactive elements on screen.")
    print("First 3 elements:")
    for el in dump.get("elements", [])[:3]:
        print(f"  [{el['index']}] {el['type']} text='{el['text']}' center={el['center']}")

    print("=== Step 5: Performing Actions ===")
    # Press home
    client.press("home")
    time.sleep(1)

    print("=== Step 6: Querying Server Status ===")
    status = client._request("GET", "/status")
    print("Server Status:", status)

    print("\nDemo completed! The server will automatically shut down after 60s of inactivity.")

if __name__ == "__main__":
    main()

