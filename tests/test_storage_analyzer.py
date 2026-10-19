"""Tests for storage analyzer aggregation and invalid scan targets."""

from core.storage_analyzer import StorageAnalyzer


def test_scan_reports_direct_folder_totals_and_largest_files(tmp_path):
    nested = tmp_path / "Photos" / "Trips"
    nested.mkdir(parents=True)
    (nested / "one.jpg").write_bytes(b"1" * 10)
    (tmp_path / "Photos" / "two.jpg").write_bytes(b"2" * 20)
    (tmp_path / "loose.txt").write_bytes(b"3" * 5)

    result = StorageAnalyzer().scan(tmp_path)

    assert result.is_completed is True
    assert result.total_files == 3
    assert result.total_size == 35
    assert result.subfolder_sizes == {"Photos": 30}
    assert [item["name"] for item in result.largest_files] == [
        "two.jpg",
        "one.jpg",
        "loose.txt",
    ]


def test_scan_invalid_target_returns_visible_error(tmp_path):
    result = StorageAnalyzer().scan(tmp_path / "missing")

    assert result.is_completed is False
    assert result.error
