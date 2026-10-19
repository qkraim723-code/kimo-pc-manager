"""Unit tests for system monitor telemetry and safety boundaries."""

from core.system_monitor import SystemMonitor


def test_system_monitor_metrics():
    monitor = SystemMonitor()

    # CPU percent should be >= 0
    cpu = monitor.get_cpu_percent()
    assert isinstance(cpu, float)
    assert 0.0 <= cpu <= 100.0

    # RAM should have non-zero total
    ram = monitor.get_ram_info()
    assert ram["total"] > 0
    assert 0.0 <= ram["percent"] <= 100.0

    # System drive should be detected
    sys_drive = monitor.get_system_drive()
    assert sys_drive is not None
    assert "mountpoint" in sys_drive

    # Protected process termination must be prevented
    # System PID 0 or 4
    assert monitor.terminate_process(0) is False
    assert monitor.terminate_process(4) is False
