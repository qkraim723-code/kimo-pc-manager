"""Safe launchers for native Windows administrative and diagnostic utilities."""

import os
import subprocess
from typing import Dict, List


class WindowsToolItem:
    def __init__(self, key: str, title_key: str, desc_key: str, command: str):
        self.key = key
        self.title_key = title_key
        self.desc_key = desc_key
        self.command = command

    def launch(self) -> bool:
        try:
            if self.command.startswith("ms-settings:"):
                os.startfile(self.command)
            else:
                subprocess.Popen(self.command, shell=True)
            return True
        except Exception:
            return False


class WindowsToolsService:
    """Provides curated, secure access to built-in Windows utilities."""

    @staticmethod
    def get_tools() -> List[WindowsToolItem]:
        return [
            WindowsToolItem(
                key="taskmgr",
                title_key="tools.taskmgr_title",
                desc_key="tools.taskmgr_desc",
                command="taskmgr.exe",
            ),
            WindowsToolItem(
                key="storage_settings",
                title_key="tools.storage_settings_title",
                desc_key="tools.storage_settings_desc",
                command="start ms-settings:storagesense",
            ),
            WindowsToolItem(
                key="sysinfo",
                title_key="tools.sysinfo_title",
                desc_key="tools.sysinfo_desc",
                command="msinfo32.exe",
            ),
            WindowsToolItem(
                key="dfrgui",
                title_key="tools.dfrgui_title",
                desc_key="tools.dfrgui_desc",
                command="dfrgui.exe",
            ),
            WindowsToolItem(
                key="cleanmgr",
                title_key="tools.cleanmgr_title",
                desc_key="tools.cleanmgr_desc",
                command="cleanmgr.exe",
            ),
            WindowsToolItem(
                key="devmgmt",
                title_key="tools.devmgmt_title",
                desc_key="tools.devmgmt_desc",
                command="devmgmt.msc",
            ),
            WindowsToolItem(
                key="resmon",
                title_key="tools.resmon_title",
                desc_key="tools.resmon_desc",
                command="resmon.exe",
            ),
            WindowsToolItem(
                key="control_panel",
                title_key="tools.control_panel_title",
                desc_key="tools.control_panel_desc",
                command="control.exe",
            ),
        ]

    @staticmethod
    def open_recycle_bin() -> bool:
        try:
            subprocess.Popen("explorer.exe shell:RecycleBinFolder", shell=True)
            return True
        except Exception:
            return False
