"""File manager business logic, system operations, and safe file transactions."""

import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
import send2trash

CATEGORY_EXTENSIONS = {
    "photos": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg", ".ico"},
    "videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"},
    "audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"},
    "documents": {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt", ".rtf", ".csv", ".md"},
    "archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".iso"},
}


class FileItem:
    """Represents a filesystem entry with parsed metadata."""

    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.is_dir = False
        self.size = 0
        self.modified = 0.0
        self.created = 0.0
        self.ext = ""
        self.is_accessible = True
        self._populate()

    def _populate(self):
        try:
            stat = self.path.stat()
            self.is_dir = self.path.is_dir()
            self.size = 0 if self.is_dir else stat.st_size
            self.modified = stat.st_mtime
            self.created = stat.st_ctime
            self.ext = self.path.suffix.lower() if not self.is_dir else ""
        except (PermissionError, FileNotFoundError, OSError):
            self.is_accessible = False

    @property
    def category(self) -> str:
        if self.is_dir:
            return "folder"
        ext = self.ext
        for cat, extensions in CATEGORY_EXTENSIONS.items():
            if ext in extensions:
                return cat
        return "file"


class FileManagerService:
    """Provides file management operations and listing capabilities."""

    def __init__(self):
        pass

    def list_directory(
        self,
        folder_path: Path,
        search_query: str = "",
        sort_by: str = "name",
        sort_asc: bool = True,
        category_filter: str = "all",
    ) -> List[FileItem]:
        """Lists directory entries safely with search, filtering, and sorting."""
        if not folder_path.exists() or not folder_path.is_dir():
            return []

        items: List[FileItem] = []
        try:
            with os.scandir(folder_path) as entries:
                for entry in entries:
                    try:
                        p = Path(entry.path)
                        item = FileItem(p)

                        # Filter by search query
                        if search_query:
                            if search_query.lower() not in item.name.lower():
                                continue

                        # Filter by category
                        if category_filter != "all":
                            if category_filter == "large":
                                if item.is_dir or item.size < 100 * 1024 * 1024:
                                    continue
                            elif category_filter == "recent":
                                one_week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).timestamp()
                                if item.modified < one_week_ago:
                                    continue
                            elif item.category != category_filter:
                                continue

                        items.append(item)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            return []

        # Sort items: Folders always first unless sorting by size/type explicitly requested
        def sort_key(item: FileItem):
            is_folder = 0 if item.is_dir else 1
            if sort_by == "name":
                val = item.name.lower()
            elif sort_by == "size":
                val = item.size
            elif sort_by == "date":
                val = item.modified
            elif sort_by == "type":
                val = (item.ext if not item.is_dir else "")
            else:
                val = item.name.lower()
            return (is_folder, val)

        items.sort(key=sort_key, reverse=not sort_asc)
        return items

    def create_folder(self, parent_dir: Path, folder_name: str) -> Tuple[bool, str]:
        try:
            folder_name = folder_name.strip()
            if not folder_name or Path(folder_name).name != folder_name or folder_name in {".", ".."}:
                return False, "Folder name must be a single valid path component."
            target = parent_dir / folder_name
            if target.exists():
                return False, f"Folder '{folder_name}' already exists."
            target.mkdir(parents=False, exist_ok=False)
            return True, str(target)
        except Exception as e:
            return False, str(e)

    def rename_item(self, target_path: Path, new_name: str) -> Tuple[bool, str]:
        try:
            new_name = new_name.strip()
            if not new_name or Path(new_name).name != new_name or new_name in {".", ".."}:
                return False, "Invalid name."
            new_path = target_path.parent / new_name
            if new_path.exists():
                return False, f"Item '{new_name}' already exists."
            target_path.rename(new_path)
            return True, str(new_path)
        except Exception as e:
            return False, str(e)

    def delete_to_trash(self, paths: List[Path]) -> Tuple[int, List[str]]:
        """Moves items to Windows Recycle Bin using send2trash."""
        success_count = 0
        errors = []
        for p in paths:
            try:
                if p.exists():
                    send2trash.send2trash(str(p))
                    success_count += 1
            except Exception as e:
                errors.append(f"{p.name}: {str(e)}")
        return success_count, errors

    def copy_item(
        self,
        src: Path,
        dst_folder: Path,
        conflict_action: str = "rename",  # "rename", "overwrite", "skip"
    ) -> Tuple[bool, str]:
        try:
            if conflict_action not in {"rename", "overwrite", "skip"}:
                return False, "Invalid conflict action."
            if not src.exists() or not dst_folder.is_dir():
                return False, "Source or destination folder does not exist."
            if src.is_dir():
                source_resolved = src.resolve()
                destination_resolved = dst_folder.resolve()
                if destination_resolved == source_resolved or destination_resolved.is_relative_to(source_resolved):
                    return False, "Cannot copy a folder into itself."

            dest_path = dst_folder / src.name
            if dest_path.exists():
                if conflict_action == "skip":
                    return True, "Skipped"
                elif conflict_action == "rename":
                    dest_path = self._generate_unique_name(dst_folder, src.name, src.is_dir())
                # If overwrite, will proceed to copy and replace

            if src.is_dir():
                if dest_path.exists() and conflict_action == "overwrite":
                    if dest_path.is_dir():
                        shutil.rmtree(dest_path)
                    else:
                        dest_path.unlink()
                shutil.copytree(src, dest_path)
            else:
                shutil.copy2(src, dest_path)
            return True, str(dest_path)
        except Exception as e:
            return False, str(e)

    def move_item(
        self,
        src: Path,
        dst_folder: Path,
        conflict_action: str = "rename",
    ) -> Tuple[bool, str]:
        try:
            if conflict_action not in {"rename", "overwrite", "skip"}:
                return False, "Invalid conflict action."
            if not src.exists() or not dst_folder.is_dir():
                return False, "Source or destination folder does not exist."
            if src.is_dir():
                source_resolved = src.resolve()
                destination_resolved = dst_folder.resolve()
                if destination_resolved == source_resolved or destination_resolved.is_relative_to(source_resolved):
                    return False, "Cannot move a folder into itself."

            dest_path = dst_folder / src.name
            if dest_path.exists():
                if conflict_action == "skip":
                    return True, "Skipped"
                elif conflict_action == "rename":
                    dest_path = self._generate_unique_name(dst_folder, src.name, src.is_dir())
                elif conflict_action == "overwrite":
                    if dest_path.is_dir():
                        shutil.rmtree(dest_path)
                    else:
                        dest_path.unlink()

            shutil.move(str(src), str(dest_path))
            return True, str(dest_path)
        except Exception as e:
            return False, str(e)

    def _generate_unique_name(self, folder: Path, original_name: str, is_dir: bool) -> Path:
        base_name = original_name
        stem = Path(original_name).stem if not is_dir else original_name
        suffix = Path(original_name).suffix if not is_dir else ""
        counter = 1
        while True:
            candidate = folder / f"{stem} ({counter}){suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def open_with_default_app(self, path: Path) -> bool:
        try:
            os.startfile(str(path))
            return True
        except Exception:
            return False

    def open_as_administrator(self, path: Path) -> bool:
        """Starts an executable using the Windows UAC elevation prompt."""
        try:
            if not path.is_file() or path.suffix.lower() != ".exe":
                return False
            os.startfile(str(path), "runas")
            return True
        except Exception:
            return False

    def open_in_explorer(self, path: Path) -> bool:
        try:
            if path.is_file():
                subprocess.Popen(f'explorer /select,"{path.resolve()}"')
            else:
                subprocess.Popen(f'explorer "{path.resolve()}"')
            return True
        except Exception:
            return False

    def get_properties(self, path: Path) -> Dict[str, any]:
        try:
            stat = path.stat()
            is_dir = path.is_dir()
            size = stat.st_size
            item_count = 0
            if is_dir:
                try:
                    entries = list(path.iterdir())
                    item_count = len(entries)
                except Exception:
                    pass

            return {
                "name": path.name,
                "path": str(path.resolve()),
                "is_dir": is_dir,
                "size": size,
                "created": datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "item_count": item_count,
            }
        except Exception as e:
            return {
                "name": path.name,
                "path": str(path),
                "is_dir": False,
                "size": 0,
                "created": "-",
                "modified": "-",
                "item_count": 0,
                "error": str(e),
            }
