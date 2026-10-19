"""Small fade feedback for refreshed and filtered result views."""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect


def animate_refresh(widget, duration=220):
    old = getattr(widget, "_refresh_animation", None)
    if old is not None:
        old.stop()
    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(0.42)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(duration)
    animation.setStartValue(0.42)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    def finish():
        widget.setGraphicsEffect(None)
        widget._refresh_animation = None
        animation.deleteLater()

    animation.finished.connect(finish)
    widget._refresh_animation = animation
    animation.start()
