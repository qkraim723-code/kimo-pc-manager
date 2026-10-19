"""Unit tests for installed applications manager and admin helper."""

from core.admin_helper import is_admin
from core.apps_manager import AppsManagerService, InstalledApp


def test_apps_manager_detection():
    apps = AppsManagerService.get_installed_apps()
    assert isinstance(apps, list)
    # On a normal Windows computer, there should be installed apps
    if len(apps) > 0:
        first = apps[0]
        assert isinstance(first, InstalledApp)
        assert bool(first.name) is True
        assert bool(first.uninstall_string) is True


def test_admin_helper():
    res = is_admin()
    assert isinstance(res, bool)
