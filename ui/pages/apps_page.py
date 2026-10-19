"""Installed applications manager and uninstaller page."""

from typing import List
from PySide6.QtCore import QFileInfo, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QFileIconProvider,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.apps_manager import AppsManagerService, InstalledApp
from core.localization import format_bytes, t
from ui.components.dialogs import ConfirmDialog
from ui.components.help_banner import HelpBanner
from ui.components.refresh_feedback import animate_refresh
from ui.icons import create_vector_icon
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BG_PRIMARY,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_DANGER,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    set_button_variant,
)


class AppsPage(QWidget):
    """View installed Windows programs and safely trigger uninstallers."""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.all_apps: List[InstalledApp] = []
        self.icon_provider = QFileIconProvider()
        self._build_ui()
        self.refresh_apps()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        self.title_label = QLabel(t("apps.title"))
        self.title_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        header.addWidget(self.title_label)

        self.subtitle_label = QLabel(t("apps.subtitle"))
        self.subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        header.addWidget(self.subtitle_label)
        main_layout.addLayout(header)

        # Control Bar: Search + Refresh + Count
        ctrl_frame = QFrame()
        ctrl_frame.setProperty("class", "card_frame")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setContentsMargins(16, 12, 16, 12)
        ctrl_layout.setSpacing(12)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(t("apps.search_placeholder"))
        self.search_edit.textChanged.connect(self._filter_apps)
        ctrl_layout.addWidget(self.search_edit, stretch=1)

        self.btn_refresh = QPushButton(t("apps.btn_refresh"))
        self.btn_refresh.setIcon(create_vector_icon("refresh", color=COLOR_ACCENT, size=16))
        self.btn_refresh.clicked.connect(self.refresh_apps)
        ctrl_layout.addWidget(self.btn_refresh)

        self.count_badge = QLabel("")
        self.count_badge.setStyleSheet(
            f"background: rgba(199, 243, 107, 0.12); color: {COLOR_ACCENT}; padding: 6px 12px; border-radius: 8px; font-weight: bold;"
        )
        ctrl_layout.addWidget(self.count_badge)

        main_layout.addWidget(ctrl_frame)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        main_layout.addWidget(self.status_label)
        self.refresh_progress = QProgressBar()
        self.refresh_progress.setRange(0, 0)
        self.refresh_progress.setFixedHeight(5)
        self.refresh_progress.setTextVisible(False)
        self.refresh_progress.hide()
        main_layout.addWidget(self.refresh_progress)

        # Apps Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            t("apps.col_name"),
            t("apps.col_publisher"),
            t("apps.col_version"),
            t("apps.col_size"),
            t("apps.col_date"),
            t("apps.col_action"),
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table, stretch=1)
        self.help_banner = HelpBanner("apps")
        main_layout.addWidget(self.help_banner)

    def refresh_apps(self):
        self.btn_refresh.setEnabled(False)
        self.table.setRowCount(0)
        self.status_label.setText(t("apps.refreshing"))
        self.refresh_progress.show()
        QApplication.processEvents()
        self.all_apps = AppsManagerService.get_installed_apps()
        self.count_badge.setText(t("apps.app_count", count=len(self.all_apps)))
        self._filter_apps(self.search_edit.text())
        self.btn_refresh.setEnabled(True)
        self.refresh_progress.hide()
        self.status_label.setText("")
        animate_refresh(self.table)

    def _filter_apps(self, query: str):
        query = query.lower().strip()
        filtered = [
            a for a in self.all_apps
            if not query or query in a.name.lower() or query in a.publisher.lower()
        ]
        self._populate_table(filtered)
        animate_refresh(self.table, 160)

    def _populate_table(self, apps: List[InstalledApp]):
        self.table.setRowCount(len(apps))
        for row, app in enumerate(apps):
            # Name
            name_item = QTableWidgetItem(app.name)
            name_item.setIcon(create_vector_icon("apps", color=COLOR_ACCENT, size=18))
            name_item.setData(Qt.UserRole, app)

            # Publisher
            pub_item = QTableWidgetItem(app.publisher)

            # Version
            ver_item = QTableWidgetItem(app.version if app.version else "-")
            ver_item.setTextAlignment(Qt.AlignCenter)

            # Size
            size_str = format_bytes(app.size_bytes) if app.size_bytes > 0 else "-"
            size_item = QTableWidgetItem(size_str)
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Date
            date_item = QTableWidgetItem(app.install_date if app.install_date else "-")
            date_item.setTextAlignment(Qt.AlignCenter)

            # Uninstall Action Button
            uninstall_btn = QPushButton(t("apps.btn_uninstall"))
            uninstall_btn.setIcon(create_vector_icon("trash", color=COLOR_DANGER, size=14))
            set_button_variant(uninstall_btn, "danger_btn")
            uninstall_btn.setMinimumSize(112, 36)
            uninstall_btn.clicked.connect(lambda ch=False, a=app: self._on_uninstall_clicked(a))

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, pub_item)
            self.table.setItem(row, 2, ver_item)
            self.table.setItem(row, 3, size_item)
            self.table.setItem(row, 4, date_item)
            self.table.setCellWidget(row, 5, uninstall_btn)
            self.table.setRowHeight(row, 46)

    def _on_uninstall_clicked(self, app: InstalledApp):
        confirm = ConfirmDialog(
            title=t("apps.uninstall_confirm_title"),
            message=t("apps.uninstall_confirm_msg", name=app.name),
            is_danger=True,
            parent=self,
        )
        if confirm.exec_() == ConfirmDialog.Accepted:
            success = app.uninstall()
            if success:
                self.status_label.setStyleSheet(f"color: {COLOR_ACCENT};")
                self.status_label.setText(t("apps.uninstall_launched"))
                QTimer.singleShot(3000, self.refresh_apps)
            else:
                self.status_label.setStyleSheet(f"color: {COLOR_DANGER};")
                self.status_label.setText(t("apps.uninstall_failed"))

    def refresh_translations(self):
        self.help_banner.refresh_translations()
        self.title_label.setText(t("apps.title"))
        self.subtitle_label.setText(t("apps.subtitle"))
        self.search_edit.setPlaceholderText(t("apps.search_placeholder"))
        self.btn_refresh.setText(t("apps.btn_refresh"))
        self.count_badge.setText(t("apps.app_count", count=len(self.all_apps)))
        self.table.setHorizontalHeaderLabels([
            t("apps.col_name"),
            t("apps.col_publisher"),
            t("apps.col_version"),
            t("apps.col_size"),
            t("apps.col_date"),
            t("apps.col_action"),
        ])
