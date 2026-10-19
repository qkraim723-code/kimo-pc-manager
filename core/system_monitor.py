"""System monitoring service using psutil and platform APIs."""

import datetime
import os
import platform
import time
from typing import Dict, List, Optional
import psutil


class SystemMonitor:
    """Collects real-time hardware, memory, CPU, disk and process telemetry."""

    PROTECTED_PROCESSES = {
        "system",
        "system idle process",
        "registry",
        "smss.exe",
        "csrss.exe",
        "wininit.exe",
        "services.exe",
        "lsass.exe",
        "winlogon.exe",
        "fontdrvhost.exe",
    }

    def __init__(self):
        self._last_disk_io = None
        self._last_disk_time = None
        # Prime psutil cpu measurement
        try:
            psutil.cpu_percent(interval=None)
        except Exception:
            pass

    def get_cpu_percent(self) -> float:
        try:
            return float(psutil.cpu_percent(interval=None))
        except Exception:
            return 0.0

    def get_ram_info(self) -> Dict[str, float]:
        try:
            mem = psutil.virtual_memory()
            return {
                "total": float(mem.total),
                "used": float(mem.used),
                "free": float(mem.available),
                "percent": float(mem.percent),
            }
        except Exception:
            return {"total": 0.0, "used": 0.0, "free": 0.0, "percent": 0.0}

    def get_all_disks(self) -> List[Dict[str, any]]:
        drives = []
        try:
            partitions = psutil.disk_partitions(all=False)
            for part in partitions:
                # Filter out cdrom/removable with no media
                if "cdrom" in part.opts or part.fstype == "":
                    continue
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    drives.append({
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "total": float(usage.total),
                        "used": float(usage.used),
                        "free": float(usage.free),
                        "percent": float(usage.percent),
                    })
                except (PermissionError, FileNotFoundError, OSError):
                    continue
        except Exception:
            pass
        return drives

    def get_system_drive(self) -> Optional[Dict[str, any]]:
        system_drive_letter = os.environ.get("SystemDrive", "C:")
        if not system_drive_letter.endswith("\\"):
            system_drive_letter += "\\"
        try:
            usage = psutil.disk_usage(system_drive_letter)
            return {
                "mountpoint": system_drive_letter,
                "total": float(usage.total),
                "used": float(usage.used),
                "free": float(usage.free),
                "percent": float(usage.percent),
            }
        except Exception:
            drives = self.get_all_disks()
            if drives:
                return drives[0]
            return {
                "mountpoint": "C:\\",
                "total": 0.0,
                "used": 0.0,
                "free": 0.0,
                "percent": 0.0,
            }

    def get_disk_io_rates(self) -> Dict[str, float]:
        """Calculates current read and write throughput in bytes/second."""
        now = time.time()
        try:
            io = psutil.disk_io_counters()
            if not io:
                return {"read_per_sec": 0.0, "write_per_sec": 0.0}

            if self._last_disk_io is not None and self._last_disk_time is not None:
                dt = now - self._last_disk_time
                if dt > 0.1:
                    read_rate = max(0.0, (io.read_bytes - self._last_disk_io.read_bytes) / dt)
                    write_rate = max(0.0, (io.write_bytes - self._last_disk_io.write_bytes) / dt)
                    self._last_disk_io = io
                    self._last_disk_time = now
                    return {"read_per_sec": read_rate, "write_per_sec": write_rate}

            self._last_disk_io = io
            self._last_disk_time = now
        except Exception:
            pass
        return {"read_per_sec": 0.0, "write_per_sec": 0.0}

    def get_system_info(self) -> Dict[str, any]:
        try:
            boot_timestamp = psutil.boot_time()
            boot_dt = datetime.datetime.fromtimestamp(boot_timestamp)
            uptime_seconds = int(time.time() - boot_timestamp)
            hours, remainder = divmod(uptime_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            uptime_str = f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"

            return {
                "os": f"{platform.system()} {platform.release()} ({platform.version()})",
                "hostname": platform.node(),
                "processor": platform.processor() or "x86_64",
                "cpu_cores_physical": psutil.cpu_count(logical=False) or 1,
                "cpu_cores_logical": psutil.cpu_count(logical=True) or 1,
                "boot_time": boot_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "uptime_str": uptime_str,
            }
        except Exception as e:
            return {
                "os": "Windows",
                "hostname": "PC",
                "processor": "Unknown",
                "cpu_cores_physical": 1,
                "cpu_cores_logical": 1,
                "boot_time": "Unknown",
                "uptime_str": "Unknown",
            }

    def get_top_processes(self, limit: int = 15, sort_by: str = "cpu") -> List[Dict[str, any]]:
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                info = p.info
                name = info["name"] or "Unknown"
                mem = info["memory_info"].rss if info.get("memory_info") else 0
                cpu = info.get("cpu_percent") or 0.0
                procs.append({
                    "pid": info["pid"],
                    "name": name,
                    "cpu_percent": float(cpu),
                    "memory_bytes": float(mem),
                    "is_protected": name.lower() in self.PROTECTED_PROCESSES or info["pid"] <= 4,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception:
                continue

        if sort_by == "cpu":
            procs.sort(key=lambda x: x["cpu_percent"], reverse=True)
        else:
            procs.sort(key=lambda x: x["memory_bytes"], reverse=True)
        return procs[:limit]

    def terminate_process(self, pid: int) -> bool:
        """Safely terminates a user process after ensuring it is not a protected system PID."""
        if pid <= 4:
            return False
        try:
            p = psutil.Process(pid)
            name = (p.name() or "").lower()
            if name in self.PROTECTED_PROCESSES:
                return False
            p.terminate()
            p.wait(timeout=2)
            return True
        except (psutil.NoSuchProcess, psutil.TimeoutExpired, psutil.AccessDenied):
            try:
                p.kill()
                return True
            except Exception:
                return False
        except Exception:
            return False
