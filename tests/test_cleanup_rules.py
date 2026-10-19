"""Unit tests for safe cleanup exclusions and safety boundaries."""

from pathlib import Path
import pytest
import shutil
import tempfile

from core.cleanup_service import CleanupCategory, SafeCleanupService


def test_forbidden_system_paths():
    cleaner = SafeCleanupService()

    # Critical system paths must ALWAYS be rejected
    assert cleaner.is_path_safe(Path("C:\\Windows\\System32\\calc.exe")) is False
    assert cleaner.is_path_safe(Path("C:\\Windows\\SysWOW64\\drivers\\etc")) is False
    assert cleaner.is_path_safe(Path("C:\\Windows\\WinSxS\\manifest.xml")) is False
    assert cleaner.is_path_safe(Path("C:\\Windows\\Installer\\$PatchCache$")) is False
    assert cleaner.is_path_safe(Path("C:\\System Volume Information\\tracking")) is False

    # Safe user temp directory should pass
    safe_path = Path("C:\\Users\\user\\AppData\\Local\\Temp\\test.tmp")
    assert cleaner.is_path_safe(safe_path) is True


def test_mock_cleanup_execution():
    cleaner = SafeCleanupService()
    temp_dir = tempfile.mkdtemp(prefix="kimo_test_clean_")
    temp_p = Path(temp_dir)

    # Create dummy disposable files
    f1 = temp_p / "temp_cache_1.tmp"
    f2 = temp_p / "temp_cache_2.tmp"
    f1.write_bytes(b"temp1")
    f2.write_bytes(b"temp2")

    mock_category = CleanupCategory(
        key="mock_temp",
        title_key="cleanup.category_user_temp",
        desc_key="cleanup.category_user_temp_desc",
        paths=[temp_p],
    )
    mock_category.files = [f1, f2]
    mock_category.is_enabled = True

    cleaned, freed, skipped = cleaner.execute_cleanup([mock_category])
    assert cleaned == 2
    assert freed == 10
    assert not f1.exists()
    assert not f2.exists()

    shutil.rmtree(temp_dir, ignore_errors=True)
