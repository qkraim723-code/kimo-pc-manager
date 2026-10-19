"""Administrator privileges checker and elevation helper for Windows."""

import ctypes
import os
import sys


def is_admin() -> bool:
    """Returns True if the current process has Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def restart_as_admin():
    """Relaunches the current application with elevated Administrator rights."""
    if is_admin():
        return True

    # If running as compiled exe
    if getattr(sys, "frozen", False):
        exe_path = sys.executable
        params = " ".join('"' + arg.replace('"', '\\"') + '"' for arg in sys.argv[1:])
    else:
        exe_path = sys.executable
        args = [sys.argv[0], *sys.argv[1:]]
        params = " ".join('"' + arg.replace('"', '\\"') + '"' for arg in args)

    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            exe_path,
            params,
            os.getcwd(),
            1,  # SW_SHOWNORMAL
        )
        if ret > 32:
            sys.exit(0)
            return True
        return False
    except Exception:
        return False
