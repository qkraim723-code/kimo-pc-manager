"""Unit tests for localization key parity and unit formatting."""

from core.localization import Localization, format_bytes, t


def test_localization_parity():
    loc = Localization()

    ar_data = loc.translations.get("ar", {})
    en_data = loc.translations.get("en", {})

    assert bool(ar_data) is True
    assert bool(en_data) is True

    # Check top level sections
    required_sections = ["nav", "overview", "file_manager", "storage", "duplicates", "cleanup", "performance", "tools", "settings", "common"]
    for sec in required_sections:
        assert sec in ar_data, f"Section '{sec}' missing from ar.json"
        assert sec in en_data, f"Section '{sec}' missing from en.json"

    # Check direction
    loc.set_language("ar")
    assert loc.is_rtl() is True

    loc.set_language("en")
    assert loc.is_rtl() is False


def test_format_bytes():
    loc = Localization()
    loc.set_language("en")

    assert "500 Bytes" in format_bytes(500)
    assert "1.0 KB" in format_bytes(1024)
    assert "5.0 MB" in format_bytes(5 * 1024 * 1024)
    assert "2.5 GB" in format_bytes(int(2.5 * 1024 * 1024 * 1024))
