"""Performance monitoring page displaying real hardware metrics and process lists."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
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
from ui.components.dialogs import ConfirmDialog
from ui.icons import create_vector_icon
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_DANGER,
    COLOR_INPUT_BG,
    COLOR_PROGRESS_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
)


class PerformancePage(QWidget):
    """Real-time system telemetry and safe process monitoring."""

    def __init__(self, monitor: SystemMonitor, parent: QWidget = None):
        super().__init__(parent)
        self.monitor = monitor

        self._build_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_metrics)
        self.timer.start(2000)

        self.refresh_metrics()

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

        # Specs & Process Table Splitter / Layout
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

        self.btn_kill = QPushButton(t("performance.btn_kill_process"))
        self.btn_kill.setIcon(create_vector_icon("trash", color=COLOR_DANGER, size=16))
        self.btn_kill.setProperty("class", "danger_btn")
        self.btn_kill.clicked.connect(self._on_kill_process)
        proc_header.addWidget(self.btn_kill)

        p_layout.addLayout(proc_header)

        self.proc_table = QTableWidget()
        self.proc_table.setColumnCount(4)
        self.proc_table.setHorizontalHeaderLabels([
            t("performance.col_pid"),
            t("performance.col_pname"),
            t("performance.col_pcpu"),
            t("performance.col_pmem"),
        ])
        self.proc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.proc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.proc_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.proc_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.proc_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.proc_table.setSelectionMode(QTableWidget.SingleSelection)
        self.proc_table.verticalHeader().setVisible(False)
        p_layout.addWidget(self.proc_table)

        main_layout.addWidget(proc_box, stretch=1)

    def refresh_metrics(self):
        """Refreshes hardware sensors and top processes."""
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

        # Top processes
        procs = self.monitor.get_top_processes(limit=12, sort_by="cpu")
        selected_pid = None
        selected_rows = self.proc_table.selectionModel().selectedRows()
        if selected_rows:
            cell = self.proc_table.item(selected_rows[0].row(), 0)
            if cell:
                try:
                    selected_pid = int(cell.text())
                except ValueError:
                    pass

        self.proc_table.setRowCount(len(procs))
        for row, p in enumerate(procs):
            pid_item = QTableWidgetItem(str(p["pid"]))
            pid_item.setTextAlignment(Qt.AlignCenter)

            name_item = QTableWidgetItem(p["name"])
            name_item.setData(Qt.UserRole, p)

            cpu_item = QTableWidgetItem(f"{p['cpu_percent']:.1f}%")
            cpu_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            mem_item = QTableWidgetItem(format_bytes(p["memory_bytes"]))
            mem_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.proc_table.setItem(row, 0, pid_item)
            self.proc_table.setItem(row, 1, name_item)
            self.proc_table.setItem(row, 2, cpu_item)
            self.proc_table.setItem(row, 3, mem_item)

            if selected_pid and p["pid"] == selected_pid:
                self.proc_table.selectRow(row)

    def _on_kill_process(self):
        selected_rows = self.proc_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        p_data = self.proc_table.item(row, 1).data(Qt.UserRole)
        if not p_data:
            return

        pid = p_data["pid"]
        name = p_data["name"]

        if p_data.get("is_protected"):
            # Protected Windows process
            return

        confirm = ConfirmDialog(
            title=t("performance.kill_confirm_title"),
            message=t("performance.kill_confirm_msg", name=name, pid=pid),
            is_danger=True,
            parent=self,
        )

        if confirm.exec_() == ConfirmDialog.Accepted:
            self.monitor.terminate_process(pid)
            self.refresh_metrics()

    def refresh_translations(self):
        self.title_label.setText(t("performance.title"))
        self.subtitle_label.setText(t("performance.subtitle"))
        self.lbl_cpu_title.setText(t("performance.cpu_usage"))
        self.lbl_ram_title.setText(t("performance.ram_usage"))
        self.lbl_io_title.setText(t("performance.disk_io"))
        self.lbl_top_proc.setText(t("performance.top_processes"))
        self.btn_kill.setText(t("performance.btn_kill_process"))
        self.proc_table.setHorizontalHeaderLabels([
            t("performance.col_pid"),
            t("performance.col_pname"),
            t("performance.col_pcpu"),
            t("performance.col_pmem"),
        ])
        self.refresh_metrics()
