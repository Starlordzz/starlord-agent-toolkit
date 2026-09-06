"""
Unit tests for Idle Watchdog lifecycle and auto-shutdown.
"""
import asyncio
import time
from server.lifecycle import IdleWatchdog

def test_watchdog_status():
    dog = IdleWatchdog(idle_timeout=10)
    status = dog.get_status()
    assert status["idle_timeout"] == 10
    assert status["remaining_seconds"] <= 10

def test_watchdog_update():
    dog = IdleWatchdog(idle_timeout=10)
    old_time = dog.last_activity_time
    time.sleep(0.05)
    dog.update_activity()
    assert dog.last_activity_time > old_time

async def test_watchdog_shutdown_callback():
    cleaned_up = False

    def mock_cleanup():
        nonlocal cleaned_up
        cleaned_up = True

    # Use 1 second timeout
    dog = IdleWatchdog(idle_timeout=1, cleanup_callback=mock_cleanup)
    
    # Override trigger_shutdown to not kill the test process
    original_trigger = dog.trigger_shutdown
    async def fake_shutdown():
        if dog.cleanup_callback:
            dog.cleanup_callback()
        dog.is_running = False

    dog.trigger_shutdown = fake_shutdown

    await dog.start()
    assert dog.is_running is True

    # Wait for timeout to elapse
    await asyncio.sleep(2.5)

    assert cleaned_up is True
    assert dog.is_running is False
    await dog.stop()

if __name__ == "__main__":
    test_watchdog_status()
    test_watchdog_update()
    asyncio.run(test_watchdog_shutdown_callback())
    print("All lifecycle tests passed!")

