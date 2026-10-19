"""System Drive usage card matching the visual reference design."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from core.localization import format_bytes, t
from ui.icons import create_vector_icon
from ui.theme import COLOR_ACCENT, COLOR_BORDER, COLOR_PROGRESS_BG, COLOR_TEXT_MUTED, COLOR_TEXT_PRIMARY


class SystemDriveCard(QFrame):
    """System drive progress and status bar widget."""

    clicked = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setProperty("class", "card_frame")
        self.setCursor(QCursor(Qt.PointingHandCursor))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Top Bar Row: Percent label, Progress Bar, Title + Icon
        bar_row = QHBoxLayout()
        bar_row.setSpacing(16)

        # Percent label on the left (or opposite side in RTL)
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 18px; font-weight: bold;"
        )
        bar_row.addWidget(self.percent_label)

        # Sleek Lime Green Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: {COLOR_PROGRESS_BG};
                border-radius: 5px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_ACCENT};
                border-radius: 5px;
            }}
            """
        )
        bar_row.addWidget(self.progress_bar, stretch=1)

        # Title + Disk Icon
        title_box = QHBoxLayout()
        title_box.setSpacing(8)

        self.title_label = QLabel(t("overview.system_drive_usage"))
        self.title_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        title_box.addWidget(self.title_label)

        self.disk_icon = QLabel()
        icon = create_vector_icon("storage", color=COLOR_ACCENT, size=20)
        self.disk_icon.setPixmap(icon.pixmap(20, 20))
        title_box.addWidget(self.disk_icon)

        bar_row.addLayout(title_box)
        layout.addLayout(bar_row)

        # Subtitle: detailed bytes used / total / free
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        layout.addWidget(self.status_label)

    def update_usage(self, percent: float, used_bytes: float, total_bytes: float, free_bytes: float):
        int_pct = int(round(percent))
        self.percent_label.setText(f"{int_pct}%")
        self.progress_bar.setValue(int_pct)

        status_text = t(
            "overview.system_drive_status",
            used=format_bytes(used_bytes),
            total=format_bytes(total_bytes),
            free=format_bytes(free_bytes),
        )
        self.status_label.setText(status_text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
