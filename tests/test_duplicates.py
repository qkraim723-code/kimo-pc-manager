"""Unit tests for duplicate file finder and safety mechanisms."""

from pathlib import Path
import pytest
import shutil
import tempfile

from core.duplicate_finder import DuplicateFinder


@pytest.fixture
def temp_dup_dir():
    d = tempfile.mkdtemp(prefix="kimo_test_dup_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


def test_duplicate_detection_and_safety(temp_dup_dir):
    finder = DuplicateFinder()

    # Create dummy files
    content_a = b"Unique content for file group A" * 100
    content_b = b"Another different content" * 100

    # 3 files with content A
    f1 = temp_dup_dir / "file1.txt"
    f2 = temp_dup_dir / "file2.txt"
    sub = temp_dup_dir / "sub"
    sub.mkdir()
    f3 = sub / "file3_copy.txt"

    f1.write_bytes(content_a)
    f2.write_bytes(content_a)
    f3.write_bytes(content_a)

    # 1 unique file with content B
    f4 = temp_dup_dir / "unique.txt"
    f4.write_bytes(content_b)

    groups = finder.scan(temp_dup_dir)
    assert len(groups) == 1
    grp = groups[0]
    assert len(grp.files) == 3
    assert grp.reclaimable_size == len(content_a) * 2

    # Verify auto-select selects only 2 copies and preserves index 0
    removable = finder.auto_select_removable(groups)
    assert len(removable) == 2
    assert grp.files[0] not in removable

    # Ensure protected original is never deleted
    protected_set = {grp.files[0]}
    # Attempting to delete protected file should be safely prevented
    del_count, reclaimed, errors = finder.delete_selected([grp.files[0]], protected_set)
    assert del_count == 0
    assert grp.files[0].exists()
