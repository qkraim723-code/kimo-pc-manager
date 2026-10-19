"""Localization and internationalization engine for Kimo PC Manager."""

import json
from pathlib import Path
from typing import Any, Dict


class Localization:
    """Manages translations, text directions, and unit formatting."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, current_lang: str = "ar"):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.current_lang = current_lang
        self.translations: Dict[str, Dict[str, Any]] = {}
        self._load_locales()
        self._initialized = True

    def _load_locales(self):
        # Locales directory relative to this file or PyInstaller bundle
        import sys
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base_dir = Path(sys._MEIPASS) / "locales"
        else:
            base_dir = Path(__file__).resolve().parent.parent / "locales"

        for lang in ["ar", "en"]:
            file_path = base_dir / f"{lang}.json"
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.translations[lang] = json.load(f)
                except Exception as e:
                    print(f"Error loading {lang}.json: {e}")
                    self.translations[lang] = {}
            else:
                self.translations[lang] = {}

    def set_language(self, lang: str):
        if lang in ["ar", "en"]:
            self.current_lang = lang

    def get_language(self) -> str:
        return self.current_lang

    def is_rtl(self) -> bool:
        return self.current_lang == "ar"

    def t(self, key_path: str, **kwargs) -> str:
        """Looks up a translation key with fallback.
        Supports dotted paths, e.g., 'overview.system_drive_usage'.
        """
        keys = key_path.split(".")
        current = self.translations.get(self.current_lang, {})
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                # Fallback to English if not found in current language
                fallback = self.translations.get("en", {})
                for fb_k in keys:
                    if isinstance(fallback, dict) and fb_k in fallback:
                        fallback = fallback[fb_k]
                    else:
                        return key_path
                current = fallback
                break

        if isinstance(current, str):
            if kwargs:
                try:
                    return current.format(**kwargs)
                except Exception:
                    return current
            return current
        return key_path

    def format_bytes(self, size_bytes: float) -> str:
        """Formats byte sizes into human readable strings with translated units."""
        if size_bytes < 0:
            return f"0 {self.t('common.bytes')}"
        units = [
            ("common.bytes", 1),
            ("common.kb", 1024),
            ("common.mb", 1024 ** 2),
            ("common.gb", 1024 ** 3),
            ("common.tb", 1024 ** 4),
        ]
        selected_unit = "common.bytes"
        divider = 1
        for unit_key, threshold in units:
            if size_bytes >= threshold:
                selected_unit = unit_key
                divider = threshold
            else:
                break
        value = size_bytes / divider
        if divider == 1:
            return f"{int(value)} {self.t(selected_unit)}"
        return f"{value:.1f} {self.t(selected_unit)}"


# Global convenience accessor
_loc_instance = None


def get_localization() -> Localization:
    global _loc_instance
    if _loc_instance is None:
        _loc_instance = Localization()
    return _loc_instance


def t(key_path: str, **kwargs) -> str:
    return get_localization().t(key_path, **kwargs)


def format_bytes(size_bytes: float) -> str:
    return get_localization().format_bytes(size_bytes)
