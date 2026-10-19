"""Configuration and application state persistence for Kimo PC Manager."""

import json
import os
import sys
from pathlib import Path


class ConfigManager:
    """Manages persistent application settings in AppData directory."""

    DEFAULT_CONFIG = {
        "language": "ar",
        "theme": "dark",
        "refresh_interval": 2,
        "file_view_mode": "list",
        "custom_scan_dirs": [],
        "show_hidden_files": False,
    }

    def __init__(self):
        self.app_dir = self._resolve_app_dir()
        self.config_path = self.app_dir / "config.json"
        self.logs_dir = self.app_dir / "logs"
        self._ensure_directories()
        self.data = self._load()

    def _resolve_app_dir(self) -> Path:
        """Determines the standard persistent configuration directory on Windows."""
        appdata = os.environ.get("APPDATA")
        if appdata:
            base = Path(appdata)
        else:
            base = Path.home() / ".config"
        target = base / "KimoPCManager"
        return target

    def _ensure_directories(self):
        try:
            self.app_dir.mkdir(parents=True, exist_ok=True)
            self.logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def _load(self) -> dict:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    cfg = dict(self.DEFAULT_CONFIG)
                    cfg.update(loaded)
                    return cfg
            except Exception:
                pass
        return dict(self.DEFAULT_CONFIG)

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}", file=sys.stderr)

    def get(self, key: str, default=None):
        return self.data.get(key, default if default is not None else self.DEFAULT_CONFIG.get(key))

    def set(self, key: str, value):
        self.data[key] = value
        self.save()

    def reset_to_defaults(self):
        self.data = dict(self.DEFAULT_CONFIG)
        self.save()

    def get_logs_dir(self) -> Path:
        return self.logs_dir
