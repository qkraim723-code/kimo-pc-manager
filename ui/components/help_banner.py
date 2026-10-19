"""Compact, localized guidance shown at the bottom of each page."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from core.localization import t
from ui.icons import create_vector_icon
from ui.theme import COLOR_ACCENT, COLOR_BORDER, COLOR_CARD_BG, COLOR_TEXT_MUTED, COLOR_TEXT_PRIMARY


class HelpBanner(QFrame):
    def __init__(self, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self.setObjectName("page_help_banner")
        self.setStyleSheet(
            f"QFrame#page_help_banner {{ background: {COLOR_CARD_BG}; border: 1px solid {COLOR_BORDER}; "
            "border-right: 3px solid " + COLOR_ACCENT + "; border-radius: 10px; }}"
        )
        row = QHBoxLayout(self)
        row.setContentsMargins(14, 9, 14, 9)
        row.setSpacing(10)
        self.badge = QLabel()
        self.badge.setFixedSize(24, 24)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setPixmap(create_vector_icon("info", color=COLOR_ACCENT, size=16).pixmap(16, 16))
        self.badge.setStyleSheet(f"background: rgba(199,243,107,0.14); color: {COLOR_ACCENT}; border-radius: 12px; font-weight: bold;")
        row.addWidget(self.badge, 0)
        texts = QVBoxLayout()
        texts.setSpacing(2)
        self.title = QLabel()
        self.title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; background: transparent; font-size: 12px; font-weight: 700; border: none;")
        self.body = QLabel()
        self.body.setWordWrap(True)
        self.body.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent; font-size: 11px; border: none;")
        texts.addWidget(self.title)
        texts.addWidget(self.body)
        row.addLayout(texts, 1)
        self.refresh_translations()

    def refresh_translations(self):
        self.title.setText(t(f"help.{self.page_key}.title"))
        self.body.setText(t(f"help.{self.page_key}.body"))
