"""Stat card widget inspired by modern mobile and desktop dashboard tiles."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QCursor, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.icons import create_vector_icon
from ui.theme import COLOR_ACCENT, COLOR_CARD_BG, COLOR_CARD_HOVER, COLOR_TEXT_MUTED, COLOR_TEXT_PRIMARY


class StatCard(QFrame):
    """Clickable dashboard tile with icon, title, description, and hover styling."""

    clicked = Signal()

    def __init__(
        self,
        title: str,
        description: str,
        icon_name: str,
        parent: QWidget = None,
        badge_text: str = "",
    ):
        super().__init__(parent)
        self.setProperty("class", "card_frame")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setObjectName("stat_card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Top row: Icon + optional badge
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel()
        icon = create_vector_icon(icon_name, color=COLOR_ACCENT, size=28)
        self.icon_label.setPixmap(icon.pixmap(28, 28))
        top_row.addWidget(self.icon_label)

        top_row.addStretch()

        if badge_text:
            self.badge = QLabel(badge_text)
            self.badge.setStyleSheet(
                f"background: rgba(199, 243, 107, 0.15); color: {COLOR_ACCENT}; "
                f"padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 11px;"
            )
            top_row.addWidget(self.badge)
        else:
            self.badge = None

        layout.addLayout(top_row)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 17px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(self.title_label)

        # Description
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)

    def set_title(self, text: str):
        self.title_label.setText(text)

    def set_description(self, text: str):
        self.desc_label.setText(text)

    def set_badge(self, text: str):
        if self.badge:
            self.badge.setText(text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
