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
    succ0, _ = monitor.terminate_process(0)
    succ4, _ = monitor.terminate_process(4)
    assert succ0 is False
    assert succ4 is False


def test_process_entries_include_executable_path_field():
    processes = SystemMonitor().get_top_processes(limit=5)

    assert processes
    assert all("exe" in process for process in processes)
