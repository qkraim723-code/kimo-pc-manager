"""Clean vector icon generator for Kimo PC Manager using QPainter."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


def create_vector_icon(name: str, color: str = "#C7F36B", size: int = 32) -> QIcon:
    """Generates sharp, scalable vector icons dynamically."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    pen = QPen(QColor(color), max(2.0, size / 16.0))
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    painter.setPen(pen)

    brush = QBrush(QColor(color))

    # Icon drawing routines based on name
    if name in ["monitor", "computer"]:
        # Monitor frame
        rect = QRectF(size * 0.15, size * 0.18, size * 0.7, size * 0.5)
        painter.drawRoundedRect(rect, size * 0.08, size * 0.08)
        # Stand
        painter.drawLine(QPointF(size * 0.5, size * 0.68), QPointF(size * 0.5, size * 0.82))
        painter.drawLine(QPointF(size * 0.35, size * 0.82), QPointF(size * 0.65, size * 0.82))

    elif name == "folder":
        # Folder tab + body
        path = QPainterPath()
        path.moveTo(size * 0.15, size * 0.32)
        path.lineTo(size * 0.40, size * 0.32)
        path.lineTo(size * 0.48, size * 0.42)
        path.lineTo(size * 0.85, size * 0.42)
        path.quadTo(size * 0.88, size * 0.42, size * 0.88, size * 0.46)
        path.lineTo(size * 0.88, size * 0.78)
        path.quadTo(size * 0.88, size * 0.82, size * 0.84, size * 0.82)
        path.lineTo(size * 0.16, size * 0.82)
        path.quadTo(size * 0.12, size * 0.82, size * 0.12, size * 0.78)
        path.lineTo(size * 0.12, size * 0.36)
        path.quadTo(size * 0.12, size * 0.32, size * 0.15, size * 0.32)
        painter.drawPath(path)

    elif name == "file":
        path = QPainterPath()
        path.moveTo(size * 0.22, size * 0.16)
        path.lineTo(size * 0.62, size * 0.16)
        path.lineTo(size * 0.78, size * 0.32)
        path.lineTo(size * 0.78, size * 0.84)
        path.lineTo(size * 0.22, size * 0.84)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawLine(QPointF(size * 0.34, size * 0.45), QPointF(size * 0.66, size * 0.45))
        painter.drawLine(QPointF(size * 0.34, size * 0.58), QPointF(size * 0.66, size * 0.58))
        painter.drawLine(QPointF(size * 0.34, size * 0.71), QPointF(size * 0.52, size * 0.71))

    elif name in ["speed", "performance", "gauge"]:
        # Gauge arc
        rect = QRectF(size * 0.15, size * 0.18, size * 0.7, size * 0.7)
        painter.drawArc(rect, 35 * 16, 210 * 16)
        # Pointer
        painter.drawLine(QPointF(size * 0.5, size * 0.53), QPointF(size * 0.68, size * 0.35))
        painter.setBrush(brush)
        painter.drawEllipse(QPointF(size * 0.5, size * 0.53), size * 0.07, size * 0.07)

    elif name in ["storage", "disk"]:
        # Cylindrical disks
        painter.drawRoundedRect(QRectF(size * 0.18, size * 0.22, size * 0.64, size * 0.22), size * 0.08, size * 0.08)
        painter.drawRoundedRect(QRectF(size * 0.18, size * 0.52, size * 0.64, size * 0.22), size * 0.08, size * 0.08)
        painter.setBrush(brush)
        painter.drawEllipse(QPointF(size * 0.72, size * 0.33), size * 0.04, size * 0.04)
        painter.drawEllipse(QPointF(size * 0.72, size * 0.63), size * 0.04, size * 0.04)

    elif name in ["shield", "cleanup", "security"]:
        # Shield with checkmark
        path = QPainterPath()
        path.moveTo(size * 0.5, size * 0.15)
        path.lineTo(size * 0.82, size * 0.26)
        path.quadTo(size * 0.82, size * 0.62, size * 0.5, size * 0.85)
        path.quadTo(size * 0.18, size * 0.62, size * 0.18, size * 0.26)
        path.closeSubpath()
        painter.drawPath(path)
        # Check
        check = QPainterPath()
        check.moveTo(size * 0.36, size * 0.48)
        check.lineTo(size * 0.46, size * 0.58)
        check.lineTo(size * 0.64, size * 0.40)
        painter.drawPath(check)

    elif name in ["duplicate", "copy"]:
        painter.drawRoundedRect(QRectF(size * 0.18, size * 0.18, size * 0.48, size * 0.52), size * 0.06, size * 0.06)
        painter.drawRoundedRect(QRectF(size * 0.34, size * 0.32, size * 0.48, size * 0.52), size * 0.06, size * 0.06)

    elif name in ["settings", "gear"]:
        painter.drawEllipse(QPointF(size * 0.5, size * 0.5), size * 0.22, size * 0.22)
        for i in range(8):
            painter.save()
            painter.translate(size * 0.5, size * 0.5)
            painter.rotate(i * 45)
            painter.drawLine(QPointF(0, -size * 0.25), QPointF(0, -size * 0.38))
            painter.restore()

    elif name in ["tools", "wrench"]:
        # Wrench
        painter.save()
        painter.translate(size * 0.5, size * 0.5)
        painter.rotate(45)
        painter.drawLine(QPointF(0, size * 0.35), QPointF(0, -size * 0.15))
        painter.drawArc(QRectF(-size * 0.18, -size * 0.42, size * 0.36, size * 0.36), 30 * 16, 300 * 16)
        painter.restore()

    elif name in ["apps", "application", "applications"]:
        for x in (0.18, 0.55):
            for y in (0.18, 0.55):
                painter.drawRoundedRect(QRectF(size*x, size*y, size*0.26, size*0.26), size*0.05, size*0.05)

    elif name in ["info", "help"]:
        painter.drawEllipse(QPointF(size*0.5, size*0.5), size*0.36, size*0.36)
        painter.setBrush(brush)
        painter.drawEllipse(QPointF(size*0.5, size*0.32), size*0.035, size*0.035)
        painter.drawLine(QPointF(size*0.5, size*0.45), QPointF(size*0.5, size*0.69))

    elif name == "refresh":
        rect = QRectF(size * 0.2, size * 0.2, size * 0.6, size * 0.6)
        painter.drawArc(rect, 45 * 16, 270 * 16)
        arrow = QPainterPath()
        arrow.moveTo(size * 0.75, size * 0.25)
        arrow.lineTo(size * 0.85, size * 0.35)
        arrow.lineTo(size * 0.65, size * 0.42)
        arrow.closeSubpath()
        painter.setBrush(brush)
        painter.drawPath(arrow)

    elif name == "back":
        path = QPainterPath()
        path.moveTo(size * 0.62, size * 0.25)
        path.lineTo(size * 0.35, size * 0.5)
        path.lineTo(size * 0.62, size * 0.75)
        painter.drawPath(path)

    elif name == "forward":
        path = QPainterPath()
        path.moveTo(size * 0.38, size * 0.25)
        path.lineTo(size * 0.65, size * 0.5)
        path.lineTo(size * 0.38, size * 0.75)
        painter.drawPath(path)

    elif name == "up":
        path = QPainterPath()
        path.moveTo(size * 0.25, size * 0.62)
        path.lineTo(size * 0.5, size * 0.35)
        path.lineTo(size * 0.75, size * 0.62)
        painter.drawPath(path)

    elif name == "search":
        painter.drawEllipse(QPointF(size * 0.42, size * 0.42), size * 0.24, size * 0.24)
        painter.drawLine(QPointF(size * 0.58, size * 0.58), QPointF(size * 0.82, size * 0.82))

    elif name == "trash":
        # Bin body
        path = QPainterPath()
        path.moveTo(size * 0.25, size * 0.35)
        path.lineTo(size * 0.30, size * 0.82)
        path.lineTo(size * 0.70, size * 0.82)
        path.lineTo(size * 0.75, size * 0.35)
        painter.drawPath(path)
        # Lid
        painter.drawLine(QPointF(size * 0.18, size * 0.35), QPointF(size * 0.82, size * 0.35))
        painter.drawArc(QRectF(size * 0.4, size * 0.22, size * 0.2, size * 0.15), 0, 180 * 16)

    elif name == "heart":
        path = QPainterPath()
        path.moveTo(size * 0.5, size * 0.82)
        path.cubicTo(size * 0.36, size * 0.70, size * 0.16, size * 0.54, size * 0.16, size * 0.36)
        path.cubicTo(size * 0.16, size * 0.12, size * 0.44, size * 0.10, size * 0.5, size * 0.32)
        path.cubicTo(size * 0.56, size * 0.10, size * 0.84, size * 0.12, size * 0.84, size * 0.36)
        path.cubicTo(size * 0.84, size * 0.54, size * 0.64, size * 0.70, size * 0.5, size * 0.82)
        painter.drawPath(path)

    elif name == "plus":
        painter.drawLine(QPointF(size * 0.5, size * 0.25), QPointF(size * 0.5, size * 0.75))
        painter.drawLine(QPointF(size * 0.25, size * 0.5), QPointF(size * 0.75, size * 0.5))

    elif name == "list":
        for y in [0.3, 0.5, 0.7]:
            painter.drawLine(QPointF(size * 0.35, size * y), QPointF(size * 0.8, size * y))
            painter.drawEllipse(QPointF(size * 0.22, size * y), size * 0.04, size * 0.04)

    elif name == "grid":
        for x in [0.22, 0.55]:
            for y in [0.22, 0.55]:
                painter.drawRoundedRect(QRectF(size * x, size * y, size * 0.24, size * 0.24), size * 0.04, size * 0.04)

    elif name == "binance":
        # Binance's geometric mark: center diamond, four satellites, and
        # four small corner diamonds in the brand yellow.
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#F0B90B"))
        def diamond(cx, cy, radius):
            shape = QPainterPath()
            shape.moveTo(size * cx, size * (cy - radius))
            shape.lineTo(size * (cx + radius), size * cy)
            shape.lineTo(size * cx, size * (cy + radius))
            shape.lineTo(size * (cx - radius), size * cy)
            shape.closeSubpath()
            painter.drawPath(shape)
        diamond(.5, .5, .14)
        for cx, cy in ((.5, .21), (.79, .5), (.5, .79), (.21, .5)):
            diamond(cx, cy, .105)
        for cx, cy in ((.27, .27), (.73, .27), (.73, .73), (.27, .73)):
            diamond(cx, cy, .055)

    elif name == "paypal":
        # Layered PayPal P mark, using the recognizable navy and blue pair.
        def draw_paypal_p(offset_x, offset_y, scale, color):
            painter.save()
            painter.translate(size * offset_x, size * offset_y)
            painter.scale(scale, scale)
            mark = QPainterPath()
            mark.setFillRule(Qt.OddEvenFill)
            x = y = 0
            mark.moveTo(x + size*.25, y + size*.12)
            mark.lineTo(x + size*.70, y + size*.12)
            mark.cubicTo(x + size*.96, y + size*.12, x + size*.98, y + size*.34, x + size*.89, y + size*.53)
            mark.cubicTo(x + size*.81, y + size*.71, x + size*.66, y + size*.75, x + size*.47, y + size*.75)
            mark.lineTo(x + size*.40, y + size*.94)
            mark.lineTo(x + size*.17, y + size*.94)
            mark.closeSubpath()
            mark.moveTo(x + size*.43, y + size*.30)
            mark.lineTo(x + size*.66, y + size*.30)
            mark.cubicTo(x + size*.76, y + size*.30, x + size*.77, y + size*.37, x + size*.72, y + size*.47)
            mark.cubicTo(x + size*.68, y + size*.56, x + size*.61, y + size*.57, x + size*.51, y + size*.57)
            mark.lineTo(x + size*.36, y + size*.57)
            mark.closeSubpath()
            painter.fillPath(mark, QColor(color))
            painter.restore()
        painter.setPen(Qt.NoPen)
        draw_paypal_p(.105, .06, .88, "#003087")
        draw_paypal_p(0, 0, .94, "#009CDE")

    elif name == "telegram":
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#229ED9"))
        painter.drawEllipse(QRectF(size * .06, size * .06, size * .88, size * .88))
        plane = QPainterPath()
        plane.moveTo(size * .20, size * .48)
        plane.lineTo(size * .79, size * .25)
        plane.lineTo(size * .65, size * .77)
        plane.lineTo(size * .49, size * .63)
        plane.lineTo(size * .40, size * .72)
        plane.lineTo(size * .42, size * .56)
        plane.closeSubpath()
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawPath(plane)

    else:
        # Consistent fallback: outlined circle with a clear center mark.
        painter.drawEllipse(QPointF(size * 0.5, size * 0.5), size * 0.34, size * 0.34)
        painter.drawLine(QPointF(size*0.32, size*0.5), QPointF(size*0.68, size*0.5))

    painter.end()
    return QIcon(pixmap)
