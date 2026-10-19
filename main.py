"""Entry point for Kimo PC Manager."""

import os
import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from core.config import ConfigManager
from core.localization import get_localization
from ui.main_window import MainWindow
from ui.theme import get_application_stylesheet


def configure_application_logging(logs_dir: Path):
    """Write bounded diagnostic logs for startup and unhandled application errors."""
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger("kimo_pc_manager")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = RotatingFileHandler(
                logs_dir / "kimo-pc-manager.log",
                maxBytes=2 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
            logger.addHandler(handler)
        sys.excepthook = lambda exc_type, exc_value, exc_traceback: logger.critical(
            "Unhandled application exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )
        logger.info("Application started")
    except OSError as exc:
        print(f"Could not initialize application logs: {exc}", file=sys.stderr)


def main():
    # Windows high-DPI and platform integration
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("Kimo PC Manager")
    app.setOrganizationName("KimoSoft")
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor("#17251F"))
    palette.setColor(QPalette.WindowText, QColor("#F2F7F4"))
    palette.setColor(QPalette.Base, QColor("#1C2D25"))
    palette.setColor(QPalette.AlternateBase, QColor("#263830"))
    palette.setColor(QPalette.Text, QColor("#F2F7F4"))
    palette.setColor(QPalette.Button, QColor("#263830"))
    palette.setColor(QPalette.ButtonText, QColor("#F2F7F4"))
    palette.setColor(QPalette.Highlight, QColor("#C7F36B"))
    palette.setColor(QPalette.HighlightedText, QColor("#122019"))
    app.setPalette(palette)

    # Load persistent user settings
    config = ConfigManager()
    configure_application_logging(config.get_logs_dir())
    user_lang = config.get("language", "en")

    # Initialize localization
    loc = get_localization()
    loc.set_language(user_lang)

    # Set layout direction (Arabic -> RightToLeft, English -> LeftToRight)
    direction = Qt.RightToLeft if loc.is_rtl() else Qt.LeftToRight
    app.setLayoutDirection(direction)

    # Apply global modern dark green stylesheet
    app.setStyleSheet(get_application_stylesheet())

    # Launch main window
    window = MainWindow(config)
    window.show()
    if config.get("support_ads_enabled", True):
        QTimer.singleShot(700, window.show_startup_support)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
