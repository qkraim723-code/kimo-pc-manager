"""Installed Windows applications manager and uninstaller service."""

import os
import subprocess
import winreg
from typing import Dict, List, Optional


class InstalledApp:
    def __init__(
        self,
        name: str,
        publisher: str,
        version: str,
        install_date: str,
        size_bytes: int,
        uninstall_string: str,
        icon_path: str = "",
    ):
        self.name = name
        self.publisher = publisher or "Unknown"
        self.version = version or ""
        self.install_date = install_date or ""
        self.size_bytes = size_bytes
        self.uninstall_string = uninstall_string
        self.icon_path = icon_path

    def uninstall(self) -> bool:
        """Launches the official vendor uninstaller for this program."""
        if not self.uninstall_string:
            return False
        try:
            cmd = self.uninstall_string.strip()
            # If command starts with MsiExec.exe, launch directly
            subprocess.Popen(cmd, shell=True)
            return True
        except Exception as e:
            print(f"Error launching uninstaller for {self.name}: {e}")
            return False


class AppsManagerService:
    """Discovers installed desktop programs from 64-bit and 32-bit Windows Registry."""

    REG_PATHS = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", winreg.KEY_WOW64_64KEY),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", winreg.KEY_WOW64_32KEY),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0),
    ]

    @classmethod
    def get_installed_apps(cls) -> List[InstalledApp]:
        apps_map: Dict[str, InstalledApp] = {}

        for hive, subkey_path, flags in cls.REG_PATHS:
            try:
                access = winreg.KEY_READ | flags if flags else winreg.KEY_READ
                with winreg.OpenKey(hive, subkey_path, 0, access) as key:
                    num_subkeys = winreg.QueryInfoKey(key)[0]
                    for i in range(num_subkeys):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name, 0, access) as app_key:
                                app = cls._parse_registry_app(app_key)
                                if app and app.name:
                                    # Deduplicate by app name
                                    key_id = app.name.lower().strip()
                                    if key_id not in apps_map:
                                        apps_map[key_id] = app
                        except (OSError, PermissionError):
                            continue
            except (OSError, PermissionError):
                continue

        # Return sorted by application name
        result = list(apps_map.values())
        result.sort(key=lambda a: a.name.lower())
        return result

    @classmethod
    def _parse_registry_app(cls, app_key) -> Optional[InstalledApp]:
        try:
            # Skip system components and updates
            try:
                is_system, _ = winreg.QueryValueEx(app_key, "SystemComponent")
                if is_system == 1:
                    return None
            except FileNotFoundError:
                pass

            try:
                parent_key, _ = winreg.QueryValueEx(app_key, "ParentKeyName")
                if parent_key:
                    return None
            except FileNotFoundError:
                pass

            name = cls._get_reg_val(app_key, "DisplayName")
            if not name or len(name.strip()) < 2:
                return None

            uninstall = cls._get_reg_val(app_key, "UninstallString")
            if not uninstall:
                return None

            publisher = cls._get_reg_val(app_key, "Publisher")
            version = cls._get_reg_val(app_key, "DisplayVersion")
            install_date = cls._get_reg_val(app_key, "InstallDate")
            icon_path = cls._get_reg_val(app_key, "DisplayIcon")

            # Size in KB in registry
            size_bytes = 0
            try:
                size_kb, _ = winreg.QueryValueEx(app_key, "EstimatedSize")
                if isinstance(size_kb, int) and size_kb > 0:
                    size_bytes = size_kb * 1024
            except (FileNotFoundError, OSError):
                pass

            return InstalledApp(
                name=name.strip(),
                publisher=publisher.strip(),
                version=version.strip(),
                install_date=install_date.strip(),
                size_bytes=size_bytes,
                uninstall_string=uninstall.strip(),
                icon_path=icon_path.strip(),
            )
        except Exception:
            return None

    @staticmethod
    def _get_reg_val(key, val_name: str) -> str:
        try:
            val, _ = winreg.QueryValueEx(key, val_name)
            return str(val) if val is not None else ""
        except FileNotFoundError:
            return ""
