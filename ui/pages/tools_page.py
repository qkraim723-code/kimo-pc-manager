"""Windows native utilities launcher page."""

from PySide6.QtCore import Qt
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

from core.localization import t
from core.windows_tools import WindowsToolsService
from ui.icons import create_vector_icon
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

        # Scrollable Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background: {COLOR_BG_PRIMARY}; border: none;")

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(16)
        grid.setContentsMargins(0, 0, 0, 0)

        for idx, tool in enumerate(self.tools):
            card = QFrame()
            card.setProperty("class", "card_frame")
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(18, 16, 18, 16)
            c_layout.setSpacing(10)

            top_box = QHBoxLayout()
            icon_lbl = QLabel()
            icon_lbl.setPixmap(create_vector_icon("tools", color=COLOR_ACCENT, size=22).pixmap(22, 22))
            top_box.addWidget(icon_lbl)
            top_box.addStretch()
            c_layout.addLayout(top_box)

            t_lbl = QLabel(t(tool.title_key))
            t_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
            c_layout.addWidget(t_lbl)

            d_lbl = QLabel(t(tool.desc_key))
            d_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
            d_lbl.setWordWrap(True)
            c_layout.addWidget(d_lbl)

            c_layout.addStretch()

            btn = QPushButton(t("tools.launch"))
            btn.setIcon(create_vector_icon("forward", color=COLOR_ACCENT, size=14))
            btn.clicked.connect(tool.launch)
            c_layout.addWidget(btn)

            row = idx // 2
            col = idx % 2
            grid.addWidget(card, row, col)

        scroll.setWidget(container)
        main_layout.addWidget(scroll, stretch=1)

    def refresh_translations(self):
        self.title_label.setText(t("tools.title"))
        self.subtitle_label.setText(t("tools.subtitle"))
