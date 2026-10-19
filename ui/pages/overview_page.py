"""Overview dashboard page reflecting the reference design and live telemetry."""

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.localization import format_bytes, t
from core.system_monitor import SystemMonitor
from ui.components.drive_usage_card import SystemDriveCard
from ui.components.stat_card import StatCard
from ui.icons import create_vector_icon
from ui.theme import (
    COLOR_ACCENT,
    COLOR_ACCENT_DARK,
    COLOR_BG_PRIMARY,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
)


class OverviewPage(QWidget):
    """Main overview screen directly matching the user's screenshot."""

    navigate_to = Signal(str)  # Emits target page name

    def __init__(self, monitor: SystemMonitor, parent: QWidget = None):
        super().__init__(parent)
        self.monitor = monitor

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background: {COLOR_BG_PRIMARY}; border: none;")

        container = QWidget()
        container.setObjectName("root_container")
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(30, 24, 30, 24)
        self.main_layout.setSpacing(20)

        self._build_header()
        self._build_grid_cards()
        self._build_system_drive_section()
        self._build_quick_access_bar()

        scroll.setWidget(container)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll)

        # Telemetry Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_metrics)
        self.timer.start(2000)

        # Initial fetch
        self.refresh_metrics()

    def _build_header(self):
        """Builds top bar with title, subtitle, badge, and settings button."""
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)

        # Left side: Settings Gear Button
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(create_vector_icon("settings", color=COLOR_TEXT_MUTED, size=24))
        self.settings_btn.setFixedSize(42, 42)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setToolTip(t("nav.settings"))
        self.settings_btn.clicked.connect(lambda: self.navigate_to.emit("settings"))
        header_layout.addWidget(self.settings_btn)

        header_layout.addStretch()

        # Right side (or start side in RTL): Title, Subtitle, and Lime Green Icon Badge
        title_box = QVBoxLayout()
        title_box.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title_box.setSpacing(4)

        self.app_title_label = QLabel(t("app_title"))
        self.app_title_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 24px; font-weight: bold;"
        )
        self.app_title_label.setAlignment(Qt.AlignRight)
        title_box.addWidget(self.app_title_label)

        self.app_subtitle_label = QLabel(t("app_subtitle"))
        self.app_subtitle_label.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 13px;"
        )
        self.app_subtitle_label.setAlignment(Qt.AlignRight)
        title_box.addWidget(self.app_subtitle_label)

        header_layout.addLayout(title_box)

        # Lime Green Rounded Icon Badge (exactly as in the screenshot!)
        self.badge_frame = QFrame()
        self.badge_frame.setFixedSize(46, 46)
        self.badge_frame.setStyleSheet(
            f"background-color: {COLOR_ACCENT}; border-radius: 12px;"
        )
        badge_layout = QVBoxLayout(self.badge_frame)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setAlignment(Qt.AlignCenter)

        badge_icon_label = QLabel()
        badge_icon = create_vector_icon("monitor", color=COLOR_ACCENT_DARK, size=26)
        badge_icon_label.setPixmap(badge_icon.pixmap(26, 26))
        badge_layout.addWidget(badge_icon_label, alignment=Qt.AlignCenter)

        header_layout.addWidget(self.badge_frame)

        self.main_layout.addLayout(header_layout)

    def _build_grid_cards(self):
        """Constructs the 2x2 grid cards matching the visual layout."""
        self.grid = QGridLayout()
        self.grid.setSpacing(16)

        # 1. File Manager Card
        self.card_files = StatCard(
            title=t("overview.file_manager_title"),
            description=t("overview.file_manager_desc"),
            icon_name="folder",
        )
        self.card_files.clicked.connect(lambda: self.navigate_to.emit("file_manager"))
        self.grid.addWidget(self.card_files, 0, 0)

        # 2. Performance Card
        self.card_perf = StatCard(
            title=t("overview.performance_title"),
            description=t("overview.performance_desc"),
            icon_name="speed",
        )
        self.card_perf.clicked.connect(lambda: self.navigate_to.emit("performance"))
        self.grid.addWidget(self.card_perf, 0, 1)

        # 3. Storage Analyzer Card
        self.card_storage = StatCard(
            title=t("overview.storage_title"),
            description=t("overview.storage_desc"),
            icon_name="storage",
        )
        self.card_storage.clicked.connect(lambda: self.navigate_to.emit("storage_analyzer"))
        self.grid.addWidget(self.card_storage, 1, 0)

        # 4. Safe Cleanup Card
        self.card_cleanup = StatCard(
            title=t("overview.cleanup_title"),
            description=t("overview.cleanup_desc"),
            icon_name="shield",
        )
        self.card_cleanup.clicked.connect(lambda: self.navigate_to.emit("safe_cleanup"))
        self.grid.addWidget(self.card_cleanup, 1, 1)

        self.main_layout.addLayout(self.grid)

    def _build_system_drive_section(self):
        """Drive usage card at bottom of dashboard."""
        self.drive_card = SystemDriveCard()
        self.drive_card.clicked.connect(lambda: self.navigate_to.emit("storage_analyzer"))
        self.main_layout.addWidget(self.drive_card)

    def _build_quick_access_bar(self):
        """Quick buttons for Photos, Videos, Documents, Downloads, Duplicates, and Tools."""
        quick_frame = QFrame()
        quick_frame.setProperty("class", "card_frame")
        quick_layout = QHBoxLayout(quick_frame)
        quick_layout.setContentsMargins(16, 12, 16, 12)
        quick_layout.setSpacing(10)

        lbl = QLabel(t("overview.quick_actions") + ":")
        lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-weight: bold;")
        quick_layout.addWidget(lbl)

        # Duplicates Shortcut
        btn_dup = QPushButton(t("nav.duplicate_finder"))
        btn_dup.setIcon(create_vector_icon("duplicate", color=COLOR_ACCENT, size=16))
        btn_dup.clicked.connect(lambda: self.navigate_to.emit("duplicate_finder"))
        quick_layout.addWidget(btn_dup)

        # Windows Tools Shortcut
        btn_tools = QPushButton(t("nav.windows_tools"))
        btn_tools.setIcon(create_vector_icon("tools", color=COLOR_ACCENT, size=16))
        btn_tools.clicked.connect(lambda: self.navigate_to.emit("windows_tools"))
        quick_layout.addWidget(btn_tools)

        quick_layout.addStretch()

        # Telemetry Live Badges
        self.ram_badge = QLabel("")
        self.ram_badge.setStyleSheet(
            f"background: rgba(199, 243, 107, 0.12); color: {COLOR_ACCENT}; padding: 6px 12px; border-radius: 8px; font-weight: 500;"
        )
        quick_layout.addWidget(self.ram_badge)

        self.cpu_badge = QLabel("")
        self.cpu_badge.setStyleSheet(
            f"background: rgba(199, 243, 107, 0.12); color: {COLOR_ACCENT}; padding: 6px 12px; border-radius: 8px; font-weight: 500;"
        )
        quick_layout.addWidget(self.cpu_badge)

        self.main_layout.addWidget(quick_frame)

    def refresh_metrics(self):
        """Reads real hardware telemetry and updates labels."""
        # System drive
        sys_drive = self.monitor.get_system_drive()
        if sys_drive:
            self.drive_card.update_usage(
                percent=sys_drive["percent"],
                used_bytes=sys_drive["used"],
                total_bytes=sys_drive["total"],
                free_bytes=sys_drive["free"],
            )

        # CPU & RAM live badges
        ram = self.monitor.get_ram_info()
        cpu = self.monitor.get_cpu_percent()

        self.ram_badge.setText(f"RAM: {int(ram['percent'])}% ({format_bytes(ram['used'])} / {format_bytes(ram['total'])})")
        self.cpu_badge.setText(f"CPU: {int(cpu)}%")

    def refresh_translations(self):
        """Re-applies translations when user switches language."""
        self.app_title_label.setText(t("app_title"))
        self.app_subtitle_label.setText(t("app_subtitle"))
        self.card_files.set_title(t("overview.file_manager_title"))
        self.card_files.set_description(t("overview.file_manager_desc"))
        self.card_perf.set_title(t("overview.performance_title"))
        self.card_perf.set_description(t("overview.performance_desc"))
        self.card_storage.set_title(t("overview.storage_title"))
        self.card_storage.set_description(t("overview.storage_desc"))
        self.card_cleanup.set_title(t("overview.cleanup_title"))
        self.card_cleanup.set_description(t("overview.cleanup_desc"))
        self.drive_card.title_label.setText(t("overview.system_drive_usage"))
        self.refresh_metrics()
