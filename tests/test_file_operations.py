"""Unit tests for file manager service on isolated temporary test directories."""

import os
from pathlib import Path
import pytest
import tempfile
import shutil

from core.file_manager_service import FileManagerService, FileItem


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp(prefix="kimo_test_fm_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


def test_create_and_rename_folder(temp_dir):
    service = FileManagerService()

    # 1. Create folder
    success, created_path = service.create_folder(temp_dir, "MyDocs")
    assert success is True
    assert Path(created_path).exists()
    assert Path(created_path).is_dir()

    # Create duplicate named folder should fail
    fail_succ, _ = service.create_folder(temp_dir, "MyDocs")
    assert fail_succ is False

    # 2. Rename folder
    ren_succ, new_path = service.rename_item(Path(created_path), "MyArchive")
    assert ren_succ is True
    assert Path(new_path).exists()
    assert not Path(created_path).exists()


def test_copy_and_move_with_conflicts(temp_dir):
    service = FileManagerService()
    src_folder = temp_dir / "src"
    dst_folder = temp_dir / "dst"
    src_folder.mkdir()
    dst_folder.mkdir()

    sample_file = src_folder / "test.txt"
    sample_file.write_text("hello world", encoding="utf-8")

    # Copy item
    succ, copied = service.copy_item(sample_file, dst_folder, conflict_action="rename")
    assert succ is True
    assert Path(copied).exists()
    assert Path(copied).read_text(encoding="utf-8") == "hello world"

    # Copy again with conflict -> auto-rename
    succ2, copied2 = service.copy_item(sample_file, dst_folder, conflict_action="rename")
    assert succ2 is True
    assert "test (1).txt" in Path(copied2).name
    assert Path(copied2).exists()

    # Move item
    another_file = src_folder / "move_me.txt"
    another_file.write_text("move content", encoding="utf-8")
    move_succ, moved = service.move_item(another_file, dst_folder)
    assert move_succ is True
    assert Path(moved).exists()
    assert not another_file.exists()


def test_file_categories_and_listing(temp_dir):
    service = FileManagerService()

    # Create varied files
    (temp_dir / "photo.jpg").write_bytes(b"\xFF\xD8\xFF" * 10)
    (temp_dir / "doc.pdf").write_bytes(b"%PDF" * 10)
    (temp_dir / "video.mp4").write_bytes(b"video" * 10)
    sub = temp_dir / "subfolder"
    sub.mkdir()

    # List all
    all_items = service.list_directory(temp_dir, category_filter="all")
    assert len(all_items) == 4
    # Folders listed first
    assert all_items[0].is_dir is True

    # Filter photos
    photo_items = service.list_directory(temp_dir, category_filter="photos")
    assert len(photo_items) == 1
    assert photo_items[0].name == "photo.jpg"

    # Filter documents
    doc_items = service.list_directory(temp_dir, category_filter="documents")
    assert len(doc_items) == 1
    assert doc_items[0].name == "doc.pdf"


def test_file_properties(temp_dir):
    service = FileManagerService()
    sample = temp_dir / "props_test.txt"
    sample.write_text("12345", encoding="utf-8")

    props = service.get_properties(sample)
    assert props["name"] == "props_test.txt"
    assert props["is_dir"] is False
    assert props["size"] == 5
    assert "path" in props
    assert "modified" in props


def test_reject_path_traversal_names(temp_dir):
    service = FileManagerService()

    success, _ = service.create_folder(temp_dir, "..\\outside")
    assert success is False

    source = temp_dir / "item.txt"
    source.write_text("safe", encoding="utf-8")
    success, _ = service.rename_item(source, "..\\outside.txt")
    assert success is False
    assert source.exists()


def test_reject_copying_folder_into_itself(temp_dir):
    service = FileManagerService()
    source = temp_dir / "source"
    source.mkdir()
    destination = source / "nested"
    destination.mkdir()

    success, message = service.copy_item(source, destination)
    assert success is False
    assert "itself" in message.lower()
