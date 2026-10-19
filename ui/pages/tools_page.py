"""Windows native utilities launcher page."""

import os
from pathlib import Path
from PySide6.QtCore import QFileInfo, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QFileIconProvider,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.localization import t
from core.windows_tools import WindowsToolsService
from ui.icons import create_vector_icon
from ui.components.help_banner import HelpBanner
from ui.components.refresh_feedback import animate_refresh
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BG_PRIMARY,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
)


class ToolsPage(QWidget):
    """Grid of official Windows administration and maintenance utilities."""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.tools = WindowsToolsService.get_tools()
        self.tool_cards = []
        self.icon_provider = QFileIconProvider()
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        self.title_label = QLabel(t("tools.title"))
        self.title_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        header.addWidget(self.title_label)

        self.subtitle_label = QLabel(t("tools.subtitle"))
        self.subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        header.addWidget(self.subtitle_label)
        main_layout.addLayout(header)

        filters = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(t("tools.search"))
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._render_filtered_tools)
        filters.addWidget(self.search_edit, stretch=1)

        self.category_combo = QComboBox()
        self._populate_category_filter()
        self.category_combo.currentIndexChanged.connect(self._render_filtered_tools)
        filters.addWidget(self.category_combo)
        main_layout.addLayout(filters)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        main_layout.addWidget(self.status_label)

        # Scrollable Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background: {COLOR_BG_PRIMARY}; border: none;")

        container = QWidget()
        self.scroll_content = container
        grid = QGridLayout(container)
        grid.setSpacing(16)
        grid.setContentsMargins(0, 0, 0, 0)

        category_labels = {
            "monitor": "tools.tools_category_monitor",
            "storage": "tools.tools_category_storage",
            "system": "tools.tools_category_system",
            "hardware": "tools.tools_category_hardware",
            "terminal": "tools.tools_category_terminal",
            "general": "tools.tools_category_general",
        }
        category_icons = {
            "monitor": "monitor",
            "storage": "storage",
            "system": "settings",
            "hardware": "monitor",
            "terminal": "tools",
            "general": "tools",
        }
        for tool in self.tools:
            card = QFrame()
            card.setProperty("class", "card_frame")
            card.setMinimumHeight(170)
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(18, 16, 18, 16)
            c_layout.setSpacing(10)

            top_box = QHBoxLayout()
            icon_lbl = QLabel()
            icon = create_vector_icon(
                category_icons.get(tool.category, "tools"),
                color=COLOR_ACCENT,
                size=22,
            )
            icon_lbl.setPixmap(icon.pixmap(22, 22))
            top_box.addWidget(icon_lbl)
            top_box.addStretch()
            category_lbl = QLabel(t(category_labels.get(tool.category, category_labels["general"])))
            category_lbl.setStyleSheet(
                f"color: {COLOR_ACCENT}; background: rgba(199, 243, 107, 0.10); "
                "border-radius: 8px; padding: 4px 8px;"
            )
            top_box.addWidget(category_lbl)
            c_layout.addLayout(top_box)

            t_lbl = QLabel(t(tool.title_key))
            t_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
            t_lbl.setWordWrap(True)
            c_layout.addWidget(t_lbl)

            d_lbl = QLabel(t(tool.desc_key))
            d_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
            d_lbl.setWordWrap(True)
            c_layout.addWidget(d_lbl)

            c_layout.addStretch()

            btn = QPushButton(t("tools.launch"))
            btn.setIcon(create_vector_icon("forward", color=COLOR_ACCENT, size=14))
            btn.clicked.connect(lambda checked=False, selected=tool: self._launch_tool(selected))
            c_layout.addWidget(btn)

            self.tool_cards.append((card, tool, category_lbl, t_lbl, d_lbl))
        self.grid = grid
        self.empty_label = QLabel(t("tools.no_results"))
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; padding: 24px;")
        grid.addWidget(self.empty_label, 0, 0, 1, 3)

        scroll.setWidget(container)
        main_layout.addWidget(scroll, stretch=1)
        self.help_banner = HelpBanner("tools")
        main_layout.addWidget(self.help_banner)
        self._render_filtered_tools()

    def _native_tool_icon(self, command: str):
        command = command.removeprefix("start ").strip()
        if command.startswith(("ms-settings:", "windowsdefender:")):
            return QIcon()

        executable = command.split(maxsplit=1)[0].strip('"')
        system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        for directory in ("System32", "SysWOW64"):
            candidate = system_root / directory / executable
            if candidate.is_file():
                return self.icon_provider.icon(QFileInfo(str(candidate)))
        return QIcon()

    def _populate_category_filter(self):
        current_category = self.category_combo.currentData() if hasattr(self, "category_combo") else "all"
        self.category_combo.clear()
        self.category_combo.addItem(t("tools.filter_all"), "all")
        for category, key in [
            ("monitor", "tools.tools_category_monitor"),
            ("storage", "tools.tools_category_storage"),
            ("system", "tools.tools_category_system"),
            ("hardware", "tools.tools_category_hardware"),
            ("terminal", "tools.tools_category_terminal"),
            ("general", "tools.tools_category_general"),
        ]:
            if any(tool.category == category for tool in self.tools):
                self.category_combo.addItem(t(key), category)
        index = self.category_combo.findData(current_category)
        self.category_combo.setCurrentIndex(index if index >= 0 else 0)

    def _render_filtered_tools(self, *args):
        while self.grid.count():
            self.grid.takeAt(0)

        query = self.search_edit.text().strip().casefold()
        category = self.category_combo.currentData()
        visible_cards = []
        for card, tool, category_lbl, title_lbl, desc_lbl in self.tool_cards:
            title = t(tool.title_key)
            description = t(tool.desc_key)
            matches = (
                (category == "all" or tool.category == category)
                and (not query or query in title.casefold() or query in description.casefold())
            )
            card.setVisible(matches)
            if matches:
                visible_cards.append(card)

        for index, card in enumerate(visible_cards):
            self.grid.addWidget(card, index // 3, index % 3)
        self.empty_label.setVisible(not visible_cards)
        if not visible_cards:
            self.grid.addWidget(self.empty_label, 0, 0, 1, 3)
        animate_refresh(self.scroll_content, 160)

    def _launch_tool(self, tool):
        if tool.launch():
            self.status_label.setStyleSheet(f"color: {COLOR_ACCENT};")
            self.status_label.setText(t("tools.launch_success"))
        else:
            self.status_label.setStyleSheet(f"color: {COLOR_DANGER};")
            self.status_label.setText(
                t("tools.launch_failed", error=tool.last_error)
            )

    def refresh_translations(self):
        self.help_banner.refresh_translations()
        self.title_label.setText(t("tools.title"))
        self.subtitle_label.setText(t("tools.subtitle"))
        self.search_edit.setPlaceholderText(t("tools.search"))
        self._populate_category_filter()
        for card, tool, category_lbl, title_lbl, desc_lbl in self.tool_cards:
            category_key = {
                "monitor": "tools.tools_category_monitor",
                "storage": "tools.tools_category_storage",
                "system": "tools.tools_category_system",
                "hardware": "tools.tools_category_hardware",
                "terminal": "tools.tools_category_terminal",
                "general": "tools.tools_category_general",
            }.get(tool.category, "tools.tools_category_general")
            category_lbl.setText(t(category_key))
            title_lbl.setText(t(tool.title_key))
            desc_lbl.setText(t(tool.desc_key))
            button = card.findChild(QPushButton)
            if button:
                button.setText(t("tools.launch"))
        self.empty_label.setText(t("tools.no_results"))
        self._render_filtered_tools()
