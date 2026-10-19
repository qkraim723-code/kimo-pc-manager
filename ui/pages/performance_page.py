"""Enhanced performance monitoring and user task manager page."""

from PySide6.QtCore import QFileInfo, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QFileIconProvider,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.localization import format_bytes, t
from core.system_monitor import SystemMonitor
from core.config import ConfigManager
from ui.components.dialogs import ConfirmDialog
from ui.components.help_banner import HelpBanner
from ui.components.themed_checkbox import ThemedCheckBox
from ui.components.refresh_feedback import animate_refresh
from ui.icons import create_vector_icon
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    set_button_variant,
)


class PerformancePage(QWidget):
    """Real-time system telemetry and interactive task manager."""

    def __init__(
        self,
        monitor: SystemMonitor,
        parent: QWidget = None,
        config: ConfigManager = None,
    ):
        super().__init__(parent)
        self.monitor = monitor
        self.config = config
        self.icon_provider = QFileIconProvider()
        self.process_icons = {}

        self._build_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_metrics)
        self.timer.start(self._refresh_interval_ms())

        self.refresh_metrics()
        self.refresh_processes()

    def _refresh_interval_ms(self) -> int:
        seconds = self.config.get("refresh_interval", 2) if self.config else 2
        return int(seconds) * 1000

    def set_refresh_interval(self, seconds: int):
        self.timer.setInterval(seconds * 1000)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        self.title_label = QLabel(t("performance.title"))
        self.title_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        header.addWidget(self.title_label)

        self.subtitle_label = QLabel(t("performance.subtitle"))
        self.subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        header.addWidget(self.subtitle_label)
        main_layout.addLayout(header)

        # 3 Metrics Cards (CPU, RAM, Disk I/O)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        # CPU Card
        cpu_card = QFrame()
        cpu_card.setProperty("class", "card_frame")
        cpu_layout = QVBoxLayout(cpu_card)
        cpu_layout.setContentsMargins(18, 16, 18, 16)
        cpu_layout.setSpacing(10)

        cpu_title_box = QHBoxLayout()
        self.lbl_cpu_title = QLabel(t("performance.cpu_usage"))
        self.lbl_cpu_title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 15px;")
        cpu_title_box.addWidget(self.lbl_cpu_title)
        cpu_icon = QLabel()
        cpu_icon.setPixmap(create_vector_icon("speed", color=COLOR_ACCENT, size=20).pixmap(20, 20))
        cpu_title_box.addWidget(cpu_icon)
        cpu_layout.addLayout(cpu_title_box)

        self.lbl_cpu_val = QLabel("0%")
        self.lbl_cpu_val.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 28px; font-weight: bold;")
        cpu_layout.addWidget(self.lbl_cpu_val)

        self.pb_cpu = QProgressBar()
        self.pb_cpu.setRange(0, 100)
        self.pb_cpu.setValue(0)
        self.pb_cpu.setFixedHeight(8)
        cpu_layout.addWidget(self.pb_cpu)

        cards_layout.addWidget(cpu_card)

        # RAM Card
        ram_card = QFrame()
        ram_card.setProperty("class", "card_frame")
        ram_layout = QVBoxLayout(ram_card)
        ram_layout.setContentsMargins(18, 16, 18, 16)
        ram_layout.setSpacing(10)

        ram_title_box = QHBoxLayout()
        self.lbl_ram_title = QLabel(t("performance.ram_usage"))
        self.lbl_ram_title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 15px;")
        ram_title_box.addWidget(self.lbl_ram_title)
        ram_icon = QLabel()
        ram_icon.setPixmap(create_vector_icon("gauge", color=COLOR_ACCENT, size=20).pixmap(20, 20))
        ram_title_box.addWidget(ram_icon)
        ram_layout.addLayout(ram_title_box)

        self.lbl_ram_val = QLabel("0%")
        self.lbl_ram_val.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 28px; font-weight: bold;")
        ram_layout.addWidget(self.lbl_ram_val)

        self.pb_ram = QProgressBar()
        self.pb_ram.setRange(0, 100)
        self.pb_ram.setValue(0)
        self.pb_ram.setFixedHeight(8)
        ram_layout.addWidget(self.pb_ram)

        self.lbl_ram_detail = QLabel("0 / 0 GB")
        self.lbl_ram_detail.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        ram_layout.addWidget(self.lbl_ram_detail)

        cards_layout.addWidget(ram_card)

        # Disk Throughput Card
        io_card = QFrame()
        io_card.setProperty("class", "card_frame")
        io_layout = QVBoxLayout(io_card)
        io_layout.setContentsMargins(18, 16, 18, 16)
        io_layout.setSpacing(10)

        io_title_box = QHBoxLayout()
        self.lbl_io_title = QLabel(t("performance.disk_io"))
        self.lbl_io_title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 15px;")
        io_title_box.addWidget(self.lbl_io_title)
        io_icon = QLabel()
        io_icon.setPixmap(create_vector_icon("storage", color=COLOR_ACCENT, size=20).pixmap(20, 20))
        io_title_box.addWidget(io_icon)
        io_layout.addLayout(io_title_box)

        self.lbl_io_read = QLabel("Read: 0 KB/s")
        self.lbl_io_read.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 16px; font-weight: bold;")
        io_layout.addWidget(self.lbl_io_read)

        self.lbl_io_write = QLabel("Write: 0 KB/s")
        self.lbl_io_write.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 16px; font-weight: bold;")
        io_layout.addWidget(self.lbl_io_write)

        cards_layout.addWidget(io_card)

        main_layout.addLayout(cards_layout)

        # Process Task Manager Box
        proc_box = QFrame()
        proc_box.setProperty("class", "card_frame")
        p_layout = QVBoxLayout(proc_box)
        p_layout.setContentsMargins(16, 14, 16, 14)
        p_layout.setSpacing(10)

        proc_header = QHBoxLayout()
        self.lbl_top_proc = QLabel(t("performance.top_processes"))
        self.lbl_top_proc.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        proc_header.addWidget(self.lbl_top_proc)

        proc_header.addStretch()

        self.cb_user_only = ThemedCheckBox(t("performance.user_apps_only"))
        self.cb_user_only.setChecked(True)
        self.cb_user_only.toggled.connect(self.refresh_processes)
        proc_header.addWidget(self.cb_user_only)

        self.btn_refresh_processes = QPushButton(t("apps.btn_refresh"))
        self.btn_refresh_processes.setIcon(create_vector_icon("refresh", color=COLOR_ACCENT, size=16))
        self.btn_refresh_processes.clicked.connect(self.refresh_processes)
        proc_header.addWidget(self.btn_refresh_processes)

        self.btn_kill = QPushButton(t("performance.btn_kill_process"))
        self.btn_kill.setIcon(create_vector_icon("trash", color=COLOR_DANGER, size=16))
        set_button_variant(self.btn_kill, "danger_btn")
        self.btn_kill.setMinimumSize(180, 42)
        self.btn_kill.setToolTip(t("performance.kill_button_hint"))
        self.btn_kill.setEnabled(False)
        self.btn_kill.clicked.connect(self._on_kill_selected_process)
        proc_header.addWidget(self.btn_kill)

        p_layout.addLayout(proc_header)

        # Status / Feedback label
        self.proc_status_lbl = QLabel("")
        self.proc_status_lbl.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 12px; font-weight: bold;")
        p_layout.addWidget(self.proc_status_lbl)

        self.proc_table = QTableWidget()
        self.proc_table.setColumnCount(6)
        self.proc_table.setHorizontalHeaderLabels([
            t("performance.col_select"),
            t("performance.col_pid"),
            t("performance.col_pname"),
            t("performance.col_pcpu"),
            t("performance.col_pmem"),
            t("performance.col_action"),
        ])
        self.proc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.proc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.proc_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.proc_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.proc_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.proc_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.proc_table.setColumnWidth(0, 64)
        self.proc_table.setColumnWidth(1, 72)
        self.proc_table.setColumnWidth(3, 76)
        self.proc_table.setColumnWidth(4, 96)
        self.proc_table.setColumnWidth(5, 132)
        self.proc_table.setSelectionMode(QTableWidget.NoSelection)
        self.proc_table.verticalHeader().setVisible(False)
        p_layout.addWidget(self.proc_table)

        main_layout.addWidget(proc_box, stretch=1)
        self.help_banner = HelpBanner("performance")
        main_layout.addWidget(self.help_banner)

    def refresh_metrics(self):
        # CPU
        cpu_pct = self.monitor.get_cpu_percent()
        self.lbl_cpu_val.setText(f"{int(round(cpu_pct))}%")
        self.pb_cpu.setValue(int(round(cpu_pct)))

        # RAM
        ram = self.monitor.get_ram_info()
        self.lbl_ram_val.setText(f"{int(round(ram['percent']))}%")
        self.pb_ram.setValue(int(round(ram['percent'])))
        self.lbl_ram_detail.setText(f"{format_bytes(ram['used'])} / {format_bytes(ram['total'])}")

        # Disk IO
        io = self.monitor.get_disk_io_rates()
        self.lbl_io_read.setText(t("performance.disk_read", val=f"{format_bytes(io['read_per_sec'])}/s"))
        self.lbl_io_write.setText(t("performance.disk_write", val=f"{format_bytes(io['write_per_sec'])}/s"))

    def refresh_processes(self):
        """Refresh usage in place so process rows stay where the user found them."""
        checked_pids = {
            int(self.proc_table.item(row, 1).text())
            for row in range(self.proc_table.rowCount())
            if self.proc_table.item(row, 1)
            and (checkbox := self.proc_table.cellWidget(row, 0)) is not None
            and checkbox.isChecked()
        }
        self.btn_refresh_processes.setEnabled(False)
        self.proc_status_lbl.setText(t("performance.refreshing"))
        QApplication.processEvents()
        try:
            procs = self.monitor.get_top_processes(
                limit=100, sort_by="cpu", user_apps_only=self.cb_user_only.isChecked(),
            )
        except Exception as exc:
            self.btn_refresh_processes.setEnabled(True)
            self.proc_status_lbl.setStyleSheet(f"color: {COLOR_DANGER}; font-weight: bold;")
            self.proc_status_lbl.setText(t("performance.refresh_failed", error=str(exc)))
            return
        existing = {
            int(self.proc_table.item(row, 1).text()): row
            for row in range(self.proc_table.rowCount()) if self.proc_table.item(row, 1)
        }
        current_pids = {p["pid"] for p in procs}
        for pid, row in sorted(existing.items(), key=lambda item: item[1], reverse=True):
            if pid not in current_pids:
                self.proc_table.removeRow(row)
        existing = {
            int(self.proc_table.item(row, 1).text()): row
            for row in range(self.proc_table.rowCount()) if self.proc_table.item(row, 1)
        }
        self.proc_table.blockSignals(True)
        for p in procs:
            row = existing.get(p["pid"])
            if row is None:
                row = self.proc_table.rowCount()
                self.proc_table.insertRow(row)
            checkbox = self.proc_table.cellWidget(row, 0)
            if checkbox is None:
                checkbox = ThemedCheckBox()
                checkbox.setAccessibleName(t("performance.select_process", name=p["name"]))
                checkbox.setToolTip(t("performance.select_process", name=p["name"]))
                checkbox.stateChanged.connect(self._on_table_selection_changed)
                self.proc_table.setCellWidget(row, 0, checkbox)
            else:
                checkbox.setAccessibleName(t("performance.select_process", name=p["name"]))
                checkbox.setToolTip(t("performance.select_process", name=p["name"]))
            checkbox.blockSignals(True)
            checkbox.setChecked(p["pid"] in checked_pids)
            checkbox.blockSignals(False)
            pid_item = QTableWidgetItem(str(p["pid"]))
            pid_item.setTextAlignment(Qt.AlignCenter)
            name_item = QTableWidgetItem(p["name"])
            name_item.setData(Qt.UserRole, p)
            if p.get("exe"):
                icon = self.process_icons.get(p["exe"])
                if icon is None:
                    icon = self.icon_provider.icon(QFileInfo(p["exe"]))
                    self.process_icons[p["exe"]] = icon
                name_item.setIcon(icon)
            cpu_item = QTableWidgetItem(f"{p['cpu_percent']:.1f}%")
            cpu_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            mem_item = QTableWidgetItem(format_bytes(p["memory_bytes"]))
            mem_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.proc_table.setItem(row, 1, pid_item)
            self.proc_table.setItem(row, 2, name_item)
            self.proc_table.setItem(row, 3, cpu_item)
            self.proc_table.setItem(row, 4, mem_item)
            button = self.proc_table.cellWidget(row, 5)
            if button is None:
                button = QPushButton(t("performance.quick_action"))
                button.setMinimumSize(116, 38)
                set_button_variant(button, "danger_btn")
                button.clicked.connect(lambda checked=False, b=button: self._kill_button_process(b))
                self.proc_table.setCellWidget(row, 5, button)
            button.setProperty("pid", p["pid"])
            button.setProperty("process_name", p["name"])
            button.setEnabled(not p.get("is_protected", False))
            button.setToolTip(
                t("performance.protected_process") if p.get("is_protected", False)
                else t("performance.quick_action")
            )
            button.setText(t("performance.quick_action"))
            self.proc_table.setRowHeight(row, 50)
        self.proc_table.blockSignals(False)
        self.btn_refresh_processes.setEnabled(True)
        self.proc_status_lbl.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 12px; font-weight: bold;")
        self._on_table_selection_changed()
        animate_refresh(self.proc_table, 160)

    def _kill_button_process(self, button):
        self._confirm_and_kill(button.property("pid"), button.property("process_name"))

    def _on_table_selection_changed(self):
        selected = self._checked_processes()
        self.btn_kill.setEnabled(any(not process.get("is_protected") for process in selected))
        self.proc_status_lbl.setText(
            t("performance.selection_status", count=len(selected)) if selected else ""
        )

    def _checked_processes(self):
        processes = []
        for row in range(self.proc_table.rowCount()):
            checkbox = self.proc_table.cellWidget(row, 0)
            process_item = self.proc_table.item(row, 2)
            if checkbox and checkbox.isChecked() and process_item:
                process = process_item.data(Qt.UserRole)
                if process:
                    processes.append(process)
        return processes

    def _on_kill_selected_process(self):
        selected_processes = self._checked_processes()
        selected_processes = [
            process for process in selected_processes
            if not process.get("is_protected")
        ]
        if len(selected_processes) == 1:
            process = selected_processes[0]
            self._confirm_and_kill(process["pid"], process["name"])
        elif selected_processes:
            self._confirm_and_kill_multiple(selected_processes)

    def _confirm_and_kill_multiple(self, processes):
        names = ", ".join(process["name"] for process in processes[:5])
        if len(processes) > 5:
            names += f" (+{len(processes) - 5})"
        confirm = ConfirmDialog(
            title=t("performance.kill_confirm_title"),
            message=t(
                "performance.kill_confirm_multiple_msg",
                count=len(processes),
                names=names,
            ),
            is_danger=True,
            parent=self,
        )

        if confirm.exec_() == ConfirmDialog.Accepted:
            terminated = 0
            errors = 0
            for process in processes:
                success, _ = self.monitor.terminate_process(process["pid"])
                if success:
                    terminated += 1
                else:
                    errors += 1
            result_key = (
                "performance.kill_batch_result_with_errors"
                if errors
                else "performance.kill_batch_result"
            )
            self.proc_status_lbl.setStyleSheet(
                f"color: {COLOR_DANGER if errors else COLOR_SUCCESS}; font-weight: bold;"
            )
            self.proc_status_lbl.setText(
                t(result_key, count=terminated, errors=errors)
            )
            self.refresh_metrics()
            self.refresh_processes()

    def _confirm_and_kill(self, pid: int, name: str):
        confirm = ConfirmDialog(
            title=t("performance.kill_confirm_title"),
            message=t("performance.kill_confirm_msg", name=name, pid=pid),
            is_danger=True,
            parent=self,
        )

        if confirm.exec_() == ConfirmDialog.Accepted:
            success, msg = self.monitor.terminate_process(pid)
            if success:
                self.proc_status_lbl.setStyleSheet(f"color: {COLOR_SUCCESS}; font-weight: bold;")
                self.proc_status_lbl.setText(t("performance.kill_success", name=name))
            else:
                self.proc_status_lbl.setStyleSheet(f"color: {COLOR_DANGER}; font-weight: bold;")
                self.proc_status_lbl.setText(t("performance.kill_failed", name=name, error=msg))
            self.refresh_metrics()
            self.refresh_processes()

    def refresh_translations(self):
        self.help_banner.refresh_translations()
        self.title_label.setText(t("performance.title"))
        self.subtitle_label.setText(t("performance.subtitle"))
        self.lbl_cpu_title.setText(t("performance.cpu_usage"))
        self.lbl_ram_title.setText(t("performance.ram_usage"))
        self.lbl_io_title.setText(t("performance.disk_io"))
        self.lbl_top_proc.setText(t("performance.top_processes"))
        self.cb_user_only.setText(t("performance.user_apps_only"))
        self.btn_kill.setText(t("performance.btn_kill_process"))
        self.btn_kill.setToolTip(t("performance.kill_button_hint"))
        self.btn_refresh_processes.setText(t("apps.btn_refresh"))
        self.proc_table.setHorizontalHeaderLabels([
            t("performance.col_select"),
            t("performance.col_pid"),
            t("performance.col_pname"),
            t("performance.col_pcpu"),
            t("performance.col_pmem"),
            t("performance.col_action"),
        ])
        self.refresh_metrics()
        for row in range(self.proc_table.rowCount()):
            button = self.proc_table.cellWidget(row, 5)
            if button:
                button.setText(t("performance.quick_action"))
