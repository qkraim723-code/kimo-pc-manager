"""Safe launchers for native Windows administrative and diagnostic utilities."""

import os
import subprocess
from typing import List


class WindowsToolItem:
    def __init__(self, key: str, title_key: str, desc_key: str, command: str, category: str = "general"):
        self.key = key
        self.title_key = title_key
        self.desc_key = desc_key
        self.command = command
        self.category = category
        self.last_error = ""

    def launch(self) -> bool:
        try:
            command = self.command.removeprefix("start ").strip()
            if command.startswith("ms-settings:") or command.startswith("windowsdefender:"):
                os.startfile(command)
            else:
                subprocess.Popen(command, shell=True)
            return True
        except Exception as e:
            self.last_error = str(e)
            return False


class WindowsToolsService:
    """Provides curated, secure access to built-in Windows utilities."""

    @staticmethod
    def get_tools() -> List[WindowsToolItem]:
        return [
            # System Monitoring
            WindowsToolItem(
                key="taskmgr",
                title_key="tools.taskmgr_title",
                desc_key="tools.taskmgr_desc",
                command="taskmgr.exe",
                category="monitor",
            ),
            WindowsToolItem(
                key="resmon",
                title_key="tools.resmon_title",
                desc_key="tools.resmon_desc",
                command="resmon.exe",
                category="monitor",
            ),
            WindowsToolItem(
                key="sysinfo",
                title_key="tools.sysinfo_title",
                desc_key="tools.sysinfo_desc",
                command="msinfo32.exe",
                category="monitor",
            ),
            WindowsToolItem(
                key="eventvwr",
                title_key="tools.eventvwr_title",
                desc_key="tools.eventvwr_desc",
                command="eventvwr.msc",
                category="monitor",
            ),
            WindowsToolItem(
                key="task_scheduler",
                title_key="tools.task_scheduler_title",
                desc_key="tools.task_scheduler_desc",
                command="taskschd.msc",
                category="monitor",
            ),

            # Storage & Disk Management
            WindowsToolItem(
                key="storage_settings",
                title_key="tools.storage_settings_title",
                desc_key="tools.storage_settings_desc",
                command="start ms-settings:storagesense",
                category="storage",
            ),
            WindowsToolItem(
                key="diskmgmt",
                title_key="tools.diskmgmt_title",
                desc_key="tools.diskmgmt_desc",
                command="diskmgmt.msc",
                category="storage",
            ),
            WindowsToolItem(
                key="cleanmgr",
                title_key="tools.cleanmgr_title",
                desc_key="tools.cleanmgr_desc",
                command="cleanmgr.exe",
                category="storage",
            ),
            WindowsToolItem(
                key="dfrgui",
                title_key="tools.dfrgui_title",
                desc_key="tools.dfrgui_desc",
                command="dfrgui.exe",
                category="storage",
            ),

            # Software & Windows Settings
            WindowsToolItem(
                key="appwiz",
                title_key="tools.appwiz_title",
                desc_key="tools.appwiz_desc",
                command="appwiz.cpl",
                category="system",
            ),
            WindowsToolItem(
                key="winupdate",
                title_key="tools.winupdate_title",
                desc_key="tools.winupdate_desc",
                command="start ms-settings:windowsupdate",
                category="system",
            ),
            WindowsToolItem(
                key="services",
                title_key="tools.services_title",
                desc_key="tools.services_desc",
                command="services.msc",
                category="system",
            ),
            WindowsToolItem(
                key="msconfig",
                title_key="tools.msconfig_title",
                desc_key="tools.msconfig_desc",
                command="msconfig.exe",
                category="system",
            ),
            WindowsToolItem(
                key="system_restore",
                title_key="tools.restore_title",
                desc_key="tools.restore_desc",
                command="rstrui.exe",
                category="system",
            ),
            WindowsToolItem(
                key="startup_apps",
                title_key="tools.startup_title",
                desc_key="tools.startup_desc",
                command="ms-settings:startupapps",
                category="system",
            ),
            WindowsToolItem(
                key="installed_apps",
                title_key="tools.apps_settings_title",
                desc_key="tools.apps_settings_desc",
                command="ms-settings:appsfeatures",
                category="system",
            ),
            WindowsToolItem(
                key="memory_diagnostic",
                title_key="tools.memory_title",
                desc_key="tools.memory_desc",
                command="mdsched.exe",
                category="hardware",
            ),

            # Hardware & Network
            WindowsToolItem(
                key="devmgmt",
                title_key="tools.devmgmt_title",
                desc_key="tools.devmgmt_desc",
                command="devmgmt.msc",
                category="hardware",
            ),
            WindowsToolItem(
                key="ncpa",
                title_key="tools.ncpa_title",
                desc_key="tools.ncpa_desc",
                command="ncpa.cpl",
                category="hardware",
            ),
            WindowsToolItem(
                key="control_panel",
                title_key="tools.control_panel_title",
                desc_key="tools.control_panel_desc",
                command="control.exe",
                category="system",
            ),

            # Terminal & Security
            WindowsToolItem(
                key="cmd",
                title_key="tools.cmd_title",
                desc_key="tools.cmd_desc",
                command="start cmd.exe",
                category="terminal",
            ),
            WindowsToolItem(
                key="powershell",
                title_key="tools.powershell_title",
                desc_key="tools.powershell_desc",
                command="start powershell.exe",
                category="terminal",
            ),
            WindowsToolItem(
                key="defender",
                title_key="tools.defender_title",
                desc_key="tools.defender_desc",
                command="start windowsdefender:",
                category="system",
            ),
        ]

    @staticmethod
    def open_recycle_bin() -> bool:
        try:
            subprocess.Popen("explorer.exe shell:RecycleBinFolder", shell=True)
            return True
        except Exception:
            return False
