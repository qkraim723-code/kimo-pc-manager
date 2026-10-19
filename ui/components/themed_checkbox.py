"""Checkbox with a high-contrast check mark across Windows themes."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QCheckBox, QStyle, QStyleOptionButton

from ui.theme import COLOR_ACCENT_DARK


class ThemedCheckBox(QCheckBox):
    """Paint an explicit check glyph so checked boxes never look like blank tiles."""

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.isChecked():
            return

        option = QStyleOptionButton()
        self.initStyleOption(option)
        rect = self.style().subElementRect(QStyle.SE_CheckBoxIndicator, option, self)
        if not rect.isValid():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(COLOR_ACCENT_DARK), max(2.0, rect.width() * 0.12))
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        mark = QPainterPath()
        mark.moveTo(rect.left() + rect.width() * 0.24, rect.top() + rect.height() * 0.53)
        mark.lineTo(rect.left() + rect.width() * 0.43, rect.top() + rect.height() * 0.72)
        mark.lineTo(rect.left() + rect.width() * 0.77, rect.top() + rect.height() * 0.31)
        painter.drawPath(mark)
