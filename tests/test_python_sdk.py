"""
Integration test for Python SDK AutomationClient.
"""
from automation_client import AutomationClient

def test_sdk_init():
    client = AutomationClient(
        host="127.0.0.1",
        port=8765,
        idle_timeout=60,
        auto_start_server=False,
    )
    assert client.base_url == "http://127.0.0.1:8765"
    assert client.idle_timeout == 60

if __name__ == "__main__":
    test_sdk_init()
    print("Python SDK test passed!")

