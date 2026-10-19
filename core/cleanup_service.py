"""Conservative, safe cleanup service for temporary and cache files."""

import datetime
import os
from pathlib import Path
import shutil
import tempfile
from typing import Callable, Dict, List, Optional, Set, Tuple


class CleanupCategory:
    """Represents a categorized cleanup scan target."""

    def __init__(self, key: str, title_key: str, desc_key: str, paths: List[Path]):
        self.key = key
        self.title_key = title_key
        self.desc_key = desc_key
        self.paths = paths
        self.files: List[Path] = []
        self.total_size: int = 0
        self.is_enabled: bool = True


class SafeCleanupService:
    """Safely audits and cleans temporary files with strict guardrails."""

    # Never delete files under these critical system locations
    FORBIDDEN_ROOTS = {
        "system32",
        "syswow64",
        "winsxs",
        "installer",
        "driverstore",
        "boot",
        "recovery",
        "system volume information",
    }

    def __init__(self):
        self._cancel_requested = False

    def cancel(self):
        self._cancel_requested = True

    def get_categories(self) -> List[CleanupCategory]:
        """Discovers standard safe user-level temporary and cache locations."""
        categories = []

        # 1. User Temp Directory (%TEMP%)
        user_temp = Path(tempfile.gettempdir())
        categories.append(
            CleanupCategory(
                key="user_temp",
                title_key="cleanup.category_user_temp",
                desc_key="cleanup.category_user_temp_desc",
                paths=[user_temp],
            )
        )

        # 2. Windows Temp (User accessible parts)
        win_temp = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "Temp"
        if win_temp.exists() and os.access(win_temp, os.R_OK):
            categories.append(
                CleanupCategory(
                    key="windows_temp",
                    title_key="cleanup.category_windows_temp",
                    desc_key="cleanup.category_windows_temp_desc",
                    paths=[win_temp],
                )
            )

        # 3. Web Browser Cache (Static web cache only, never profiles, passwords, or cookies)
        local_app_data = os.environ.get("LOCALAPPDATA")
        browser_cache_paths = []
        if local_app_data:
            lap = Path(local_app_data)
            # Chrome safe cache
            chrome_cache = lap / "Google" / "Chrome" / "User Data" / "Default" / "Cache" / "Cache_Data"
            if chrome_cache.exists():
                browser_cache_paths.append(chrome_cache)
            # Edge safe cache
            edge_cache = lap / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache" / "Cache_Data"
            if edge_cache.exists():
                browser_cache_paths.append(edge_cache)

        if browser_cache_paths:
            categories.append(
                CleanupCategory(
                    key="browser_cache",
                    title_key="cleanup.category_browser_cache",
                    desc_key="cleanup.category_browser_cache_desc",
                    paths=browser_cache_paths,
                )
            )

        # 4. Windows Thumbnail Cache
        if local_app_data:
            thumb_cache = Path(local_app_data) / "Microsoft" / "Windows" / "Explorer"
            if thumb_cache.exists():
                categories.append(
                    CleanupCategory(
                        key="thumbnails",
                        title_key="cleanup.category_thumbnails",
                        desc_key="cleanup.category_thumbnails_desc",
                        paths=[thumb_cache],
                    )
                )

        return categories

    def is_path_safe(self, path: Path) -> bool:
        """Verifies that a given path is not inside a forbidden system directory."""
        try:
            resolved_str = str(path.resolve()).lower()
            for forbidden in self.FORBIDDEN_ROOTS:
                if f"\\{forbidden}\\" in resolved_str or resolved_str.endswith(f"\\{forbidden}"):
                    return False
            return True
        except Exception:
            return False

    def scan_category(
        self,
        category: CleanupCategory,
        min_age_hours: int = 1,  # Safe default: skip files created in the last hour
        progress_callback: Optional[Callable[[str], None]] = None,
    ):
        category.files.clear()
        category.total_size = 0
        now = datetime.datetime.now().timestamp()
        cutoff_time = now - (min_age_hours * 3600)

        for target_dir in category.paths:
            if not target_dir.exists():
                continue
            try:
                for root, _, files in os.walk(str(target_dir), followlinks=False):
                    if self._cancel_requested:
                        return
                    root_p = Path(root)

                    # Thumbnail cache files filter: only thumbcache_*.db
                    is_thumb_dir = category.key == "thumbnails"

                    for fname in files:
                        if self._cancel_requested:
                            return

                        if is_thumb_dir and not fname.lower().startswith("thumbcache_"):
                            continue

                        fpath = root_p / fname
                        if not self.is_path_safe(fpath):
                            continue

                        try:
                            stat = fpath.stat()
                            # Check age for user temp
                            if category.key in ["user_temp", "windows_temp"]:
                                if stat.st_mtime > cutoff_time:
                                    continue  # Still actively modified

                            fsize = stat.st_size
                            category.files.append(fpath)
                            category.total_size += fsize

                            if progress_callback and len(category.files) % 50 == 0:
                                progress_callback(fpath.name)
                        except (PermissionError, FileNotFoundError, OSError):
                            continue
            except (PermissionError, OSError):
                continue

    def execute_cleanup(
        self,
        categories: List[CleanupCategory],
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Tuple[int, int, int]:
        """Cleans audited files. Returns (cleaned_count, freed_bytes, skipped_count)."""
        cleaned_count = 0
        freed_bytes = 0
        skipped_count = 0
        total_items = sum(len(cat.files) for cat in categories if cat.is_enabled)
        current_idx = 0

        for cat in categories:
            if not cat.is_enabled:
                continue

            for fpath in cat.files:
                if self._cancel_requested:
                    break
                current_idx += 1
                if progress_callback:
                    progress_callback(fpath.name, current_idx)

                if not self.is_path_safe(fpath):
                    skipped_count += 1
                    continue

                try:
                    if fpath.is_file():
                        sz = fpath.stat().st_size
                        fpath.unlink(missing_ok=True)
                        cleaned_count += 1
                        freed_bytes += sz
                    elif fpath.is_dir():
                        shutil.rmtree(str(fpath), ignore_errors=True)
                except (PermissionError, OSError):
                    # Locked or in-use file safely skipped
                    skipped_count += 1

        return cleaned_count, freed_bytes, skipped_count
