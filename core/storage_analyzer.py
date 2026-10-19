"""Deep storage analyzer service for disks and directory structures."""

from collections import defaultdict
import os
from pathlib import Path
import threading
from typing import Callable, Dict, List, Optional


class StorageScanResult:
    """Encapsulates the aggregated storage analysis results."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.total_size = 0
        self.total_files = 0
        self.total_dirs = 0
        self.skipped_count = 0
        self.subfolder_sizes: Dict[str, int] = {}
        self.largest_files: List[Dict[str, any]] = []  # [{name, path, size}]
        self.type_distribution: Dict[str, Dict[str, any]] = {}  # ext: {size, count}
        self.is_completed = False


class StorageAnalyzer:
    """Performs recursive space analysis with cancellation and progress reporting."""

    def __init__(self):
        self._cancel_requested = False

    def cancel(self):
        self._cancel_requested = True

    def scan(
        self,
        target_path: Path,
        progress_callback: Optional[Callable[[int, str, int], None]] = None,
    ) -> StorageScanResult:
        self._cancel_requested = False
        result = StorageScanResult(target_path)
        if not target_path.exists():
            return result

        top_files_heap: List[Dict[str, any]] = []
        ext_map = defaultdict(lambda: {"size": 0, "count": 0})
        direct_children_map = defaultdict(int)

        target_resolved = target_path.resolve()
        is_drive_root = (target_resolved.parent == target_resolved)

        # To avoid infinite recursion, track visited device/inode
        visited_dirs = set()

        last_progress_update = 0

        try:
            for root, dirs, files in os.walk(str(target_resolved), followlinks=False):
                if self._cancel_requested:
                    break

                root_p = Path(root)

                # Determine direct child association for folder breakdown
                rel_to_target = ""
                try:
                    rel_to_target = root_p.relative_to(target_resolved)
                except ValueError:
                    continue

                parts = rel_to_target.parts
                direct_child = parts[0] if parts else ""

                result.total_dirs += 1

                for fname in files:
                    if self._cancel_requested:
                        break

                    fpath = root_p / fname
                    result.total_files += 1

                    try:
                        # Use os.stat or lstat to prevent following symlinks
                        stat = fpath.stat()
                        fsize = stat.st_size
                        result.total_size += fsize

                        if direct_child:
                            direct_children_map[direct_child] += fsize
                        else:
                            direct_children_map[fname] += fsize

                        ext = fpath.suffix.lower() if fpath.suffix else "other"
                        ext_map[ext]["size"] += fsize
                        ext_map[ext]["count"] += 1

                        # Track largest files
                        top_files_heap.append({
                            "name": fname,
                            "path": str(fpath),
                            "size": fsize,
                        })

                    except (PermissionError, FileNotFoundError, OSError):
                        result.skipped_count += 1
                        continue

                    if result.total_files - last_progress_update >= 100:
                        last_progress_update = result.total_files
                        if progress_callback:
                            progress_callback(result.total_files, str(fpath), result.total_size)

        except (PermissionError, OSError):
            result.skipped_count += 1

        # Sort and trim top files (top 25)
        top_files_heap.sort(key=lambda x: x["size"], reverse=True)
        result.largest_files = top_files_heap[:25]

        # Format subfolders
        result.subfolder_sizes = dict(direct_children_map)
        result.type_distribution = dict(ext_map)
        result.is_completed = not self._cancel_requested
        return result
