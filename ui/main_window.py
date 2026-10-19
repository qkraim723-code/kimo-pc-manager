"""Main Application Window for Kimo PC Manager."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.config import ConfigManager
from core.file_manager_service import FileManagerService
from core.localization import get_localization, t
from core.system_monitor import SystemMonitor
from ui.icons import create_vector_icon
from ui.pages.cleanup_page import CleanupPage
from ui.pages.duplicate_page import DuplicatePage
from ui.pages.file_manager_page import FileManagerPage
from ui.pages.overview_page import OverviewPage
from ui.pages.performance_page import PerformancePage
from ui.pages.settings_page import SettingsPage
from ui.pages.storage_page import StoragePage
from ui.pages.tools_page import ToolsPage
from ui.theme import (
    COLOR_ACCENT,
    COLOR_ACCENT_DARK,
    COLOR_BG_PRIMARY,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
)


class MainWindow(QMainWindow):
    """Primary application frame hosting the navigation sidebar and views."""

    def __init__(self, config: ConfigManager):
        super().__init__()
        self.config = config
        self.loc = get_localization()

        self.monitor = SystemMonitor()
        self.file_service = FileManagerService()

        self.setWindowTitle("Kimo PC Manager")
        self.setWindowIcon(create_vector_icon("monitor", color=COLOR_ACCENT, size=48))
        self.resize(1120, 720)
        self.setMinimumSize(950, 600)

        self._build_ui()
        self._apply_direction()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root_container")
        self.setCentralWidget(root)

        self.root_layout = QHBoxLayout(root)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 1. Navigation Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(230)
        self.sidebar.setStyleSheet(
            f"background-color: {COLOR_CARD_BG}; border-right: 1px solid {COLOR_BORDER};"
        )
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(14, 20, 14, 20)
        self.sidebar_layout.setSpacing(6)

        # Brand at top of sidebar
        brand_box = QHBoxLayout()
        brand_box.setSpacing(10)

        brand_badge = QFrame()
        brand_badge.setFixedSize(36, 36)
        brand_badge.setStyleSheet(f"background-color: {COLOR_ACCENT}; border-radius: 8px;")
        bb_layout = QVBoxLayout(brand_badge)
        bb_layout.setContentsMargins(0, 0, 0, 0)
        b_icon = QLabel()
        b_icon.setPixmap(create_vector_icon("monitor", color=COLOR_ACCENT_DARK, size=20).pixmap(20, 20))
        bb_layout.addWidget(b_icon, alignment=Qt.AlignCenter)
        brand_box.addWidget(brand_badge)

        self.brand_title = QLabel(t("app_name"))
        self.brand_title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        brand_box.addWidget(self.brand_title)
        brand_box.addStretch()

        self.sidebar_layout.addLayout(brand_box)
        self.sidebar_layout.addSpacing(16)

        # Nav Buttons list
        self.nav_buttons = {}
        nav_items = [
            ("overview", "monitor", "nav.overview"),
            ("file_manager", "folder", "nav.file_manager"),
            ("storage_analyzer", "storage", "nav.storage_analyzer"),
            ("safe_cleanup", "shield", "nav.safe_cleanup"),
            ("performance", "speed", "nav.performance"),
            ("duplicate_finder", "duplicate", "nav.duplicate_finder"),
            ("windows_tools", "tools", "nav.windows_tools"),
            ("settings", "settings", "nav.settings"),
        ]

        for key, icon_name, label_key in nav_items:
            btn = QPushButton(t(label_key))
            btn.setProperty("class", "nav_item")
            btn.setIcon(create_vector_icon(icon_name, color=COLOR_TEXT_MUTED, size=18))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=key: self.navigate_to(k))
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = (btn, icon_name, label_key)

        self.sidebar_layout.addStretch()

        self.root_layout.addWidget(self.sidebar)

        # 2. Stacked Pages
        self.pages_stack = QStackedWidget()
        self.pages_stack.setStyleSheet(f"background-color: {COLOR_BG_PRIMARY};")

        # Instantiate Pages
        self.page_overview = OverviewPage(self.monitor)
        self.page_overview.navigate_to.connect(self.navigate_to)
        self.pages_stack.addWidget(self.page_overview)

        self.page_files = FileManagerPage(self.file_service, self.monitor)
        self.pages_stack.addWidget(self.page_files)

        self.page_storage = StoragePage(self.monitor)
        self.pages_stack.addWidget(self.page_storage)

        self.page_cleanup = CleanupPage()
        self.pages_stack.addWidget(self.page_cleanup)

        self.page_performance = PerformancePage(self.monitor)
        self.pages_stack.addWidget(self.page_performance)

        self.page_duplicates = DuplicatePage()
        self.pages_stack.addWidget(self.page_duplicates)

        self.page_tools = ToolsPage()
        self.pages_stack.addWidget(self.page_tools)

        self.page_settings = SettingsPage(self.config)
        self.page_settings.language_changed.connect(self._on_language_changed)
        self.pages_stack.addWidget(self.page_settings)

        self.page_indices = {
            "overview": 0,
            "file_manager": 1,
            "storage_analyzer": 2,
            "safe_cleanup": 3,
            "performance": 4,
            "duplicate_finder": 5,
            "windows_tools": 6,
            "settings": 7,
        }

        self.root_layout.addWidget(self.pages_stack, stretch=1)

        # Select Overview initially
        self.navigate_to("overview")

    def navigate_to(self, page_key: str):
        idx = self.page_indices.get(page_key, 0)
        self.pages_stack.setCurrentIndex(idx)

        # Update active nav button state
        for k, (btn, icon_name, _) in self.nav_buttons.items():
            if k == page_key:
                btn.setProperty("class", "nav_item active")
                btn.setIcon(create_vector_icon(icon_name, color=COLOR_ACCENT, size=18))
            else:
                btn.setProperty("class", "nav_item")
                btn.setIcon(create_vector_icon(icon_name, color=COLOR_TEXT_MUTED, size=18))
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _apply_direction(self):
        is_rtl = self.loc.is_rtl()
        direction = Qt.RightToLeft if is_rtl else Qt.LeftToRight
        QApplication.instance().setLayoutDirection(direction)

    def _on_language_changed(self, new_lang: str):
        self._apply_direction()

        # Update window title and sidebar labels
        self.brand_title.setText(t("app_name"))
        for k, (btn, icon_name, label_key) in self.nav_buttons.items():
            btn.setText(t(label_key))

        # Propagate to all pages
        self.page_overview.refresh_translations()
        self.page_files.refresh_translations()
        self.page_storage.refresh_translations()
        self.page_cleanup.refresh_translations()
        self.page_performance.refresh_translations()
        self.page_duplicates.refresh_translations()
        self.page_tools.refresh_translations()
        self.page_settings.refresh_translations()
