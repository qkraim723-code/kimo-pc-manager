"""Accessible pill switch implemented as a native, keyboard-operable checkbox."""

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QCheckBox

from ui.theme import COLOR_ACCENT, COLOR_BORDER, COLOR_CARD_HOVER


class ToggleSwitch(QCheckBox):
    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)

    def sizeHint(self):
        return QSize(52, 30)

    def hitButton(self, position):
        return self.rect().contains(position)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        track = QRectF(2, 4, 48, 22)
        checked = self.isChecked()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(COLOR_ACCENT if checked else COLOR_BORDER))
        painter.drawRoundedRect(track, 11, 11)
        knob_x = 28 if checked else 4
        painter.setBrush(QColor("#122019" if checked else "#F2F7F4"))
        painter.drawEllipse(QRectF(knob_x, 6, 18, 18))
        if self.hasFocus():
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QColor(COLOR_CARD_HOVER))
            painter.drawRoundedRect(QRectF(0.5, 1.5, 51, 27), 13, 13)
