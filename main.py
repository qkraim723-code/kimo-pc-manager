"""Entry point for Kimo PC Manager."""

import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from core.config import ConfigManager
from core.localization import get_localization
from ui.main_window import MainWindow
from ui.theme import get_application_stylesheet


def main():
    # Windows high-DPI and platform integration
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("Kimo PC Manager")
    app.setOrganizationName("KimoSoft")

    # Load persistent user settings
    config = ConfigManager()
    user_lang = config.get("language", "ar")

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

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
