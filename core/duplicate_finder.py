"""Accurate duplicate file finder using size grouping and SHA-256 chunk hashing."""

from collections import defaultdict
import hashlib
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple
import send2trash


class DuplicateGroup:
    """Group of files that share identical byte size and content hash."""

    def __init__(self, file_size: int, content_hash: str, files: List[Path]):
        self.file_size = file_size
        self.content_hash = content_hash
        self.files = files

    @property
    def reclaimable_size(self) -> int:
        if len(self.files) > 1:
            return (len(self.files) - 1) * self.file_size
        return 0


class DuplicateFinder:
    """Two-pass duplicate file detector with safety and cancellation."""

    def __init__(self):
        self._cancel_requested = False

    def cancel(self):
        self._cancel_requested = True

    def hash_file(self, file_path: Path, chunk_size: int = 65536) -> Optional[str]:
        """Calculates SHA-256 hash in streaming chunks to minimize memory consumption."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    if self._cancel_requested:
                        return None
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (PermissionError, FileNotFoundError, OSError):
            return None

    def scan(
        self,
        target_path: Path,
        min_size_bytes: int = 1,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[DuplicateGroup]:
        self._cancel_requested = False
        size_map = defaultdict(list)
        total_examined = 0

        # Pass 1: Group files by identical byte size
        for root, _, files in os.walk(str(target_path), followlinks=False):
            if self._cancel_requested:
                return []
            for fname in files:
                if self._cancel_requested:
                    return []
                fpath = Path(root) / fname
                try:
                    stat = fpath.stat()
                    size = stat.st_size
                    if size >= min_size_bytes:
                        size_map[size].append(fpath)
                    total_examined += 1
                    if total_examined % 50 == 0 and progress_callback:
                        progress_callback(f"Cataloging: {fname}", len(size_map))
                except (PermissionError, FileNotFoundError, OSError):
                    continue

        # Pass 2: Filter candidate sizes with 2 or more files and hash them
        candidate_sizes = [sz for sz, flist in size_map.items() if len(flist) > 1]
        duplicate_groups: List[DuplicateGroup] = []

        for sz in candidate_sizes:
            if self._cancel_requested:
                break
            files = size_map[sz]
            hash_map = defaultdict(list)
            for f in files:
                if self._cancel_requested:
                    break
                if progress_callback:
                    progress_callback(f"Analyzing: {f.name}", len(duplicate_groups))
                h = self.hash_file(f)
                if h:
                    hash_map[h].append(f)

            for h, matching_files in hash_map.items():
                if len(matching_files) > 1:
                    # Sort files so original (oldest or shortest path) is index 0
                    matching_files.sort(key=lambda p: (len(str(p)), str(p)))
                    duplicate_groups.append(DuplicateGroup(sz, h, matching_files))

        return duplicate_groups

    def auto_select_removable(self, groups: List[DuplicateGroup]) -> List[Path]:
        """Selects all duplicate files for removal except the first copy (original) in each group."""
        removable: List[Path] = []
        for grp in groups:
            if len(grp.files) > 1:
                # Keep index 0 safe, mark indices 1..n for removal
                removable.extend(grp.files[1:])
        return removable

    def delete_selected(self, files_to_delete: List[Path], protected_originals: Set[Path]) -> Tuple[int, int, List[str]]:
        """Safely moves duplicates to Recycle Bin, ensuring no protected original is ever deleted."""
        deleted_count = 0
        reclaimed_bytes = 0
        errors = []

        for fpath in files_to_delete:
            if fpath in protected_originals:
                continue  # Never delete protected original!
            try:
                if fpath.exists():
                    fsize = fpath.stat().st_size
                    send2trash.send2trash(str(fpath))
                    deleted_count += 1
                    reclaimed_bytes += fsize
            except Exception as e:
                errors.append(f"{fpath.name}: {str(e)}")

        return deleted_count, reclaimed_bytes, errors
