"""Design system, color tokens, and complete QSS stylesheet for Kimo PC Manager."""

# Color Palette inspired by the reference screenshot
COLOR_BG_PRIMARY = "#17251F"       # Main deep dark green background
COLOR_CARD_BG = "#263830"          # Card container background
COLOR_CARD_HOVER = "#2D4339"       # Hovered card background
COLOR_BORDER = "#354A40"           # Subtle border and separators
COLOR_ACCENT = "#C7F36B"           # Vibrant lime green accent
COLOR_ACCENT_HOVER = "#B3DE58"     # Lime green hover
COLOR_ACCENT_DARK = "#122019"      # Dark text for on-lime badges
COLOR_TEXT_PRIMARY = "#F2F7F4"     # Bright readable text
COLOR_TEXT_MUTED = "#98B1A4"       # Gentle sage green muted text
COLOR_INPUT_BG = "#1C2D25"         # Input field background
COLOR_PROGRESS_BG = "#1A2B23"      # Background track for progress bars
COLOR_DANGER = "#FF6B6B"           # Delete / kill process alert
COLOR_SUCCESS = "#69DB7C"          # Success confirmation


def get_application_stylesheet() -> str:
    """Returns the comprehensive stylesheet for the entire application."""
    return f"""
    * {{
        font-family: "Segoe UI", "Tahoma", "Arial", sans-serif;
        font-size: 13px;
        color: {COLOR_TEXT_PRIMARY};
    }}

    QMainWindow, QDialog, QWidget#root_container {{
        background-color: {COLOR_BG_PRIMARY};
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        border: none;
        background: {COLOR_BG_PRIMARY};
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLOR_BORDER};
        min-height: 25px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLOR_TEXT_MUTED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        border: none;
        background: {COLOR_BG_PRIMARY};
        height: 8px;
        margin: 0px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLOR_BORDER};
        min-width: 25px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {COLOR_TEXT_MUTED};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* Cards */
    QFrame.card_frame {{
        background-color: {COLOR_CARD_BG};
        border-radius: 14px;
        border: 1px solid {COLOR_BORDER};
    }}
    QFrame.card_frame:hover {{
        background-color: {COLOR_CARD_HOVER};
        border: 1px solid rgba(199, 243, 107, 0.35);
    }}

    /* Buttons */
    QPushButton {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 500;
        color: {COLOR_TEXT_PRIMARY};
    }}
    QPushButton:hover {{
        background-color: {COLOR_CARD_HOVER};
        border: 1px solid {COLOR_ACCENT};
        color: {COLOR_ACCENT};
    }}
    QPushButton:pressed {{
        background-color: {COLOR_INPUT_BG};
    }}
    QPushButton:disabled {{
        background-color: {COLOR_INPUT_BG};
        color: {COLOR_BORDER};
        border-color: {COLOR_BORDER};
    }}

    /* Accent Action Button (Lime Green) */
    QPushButton.accent_btn {{
        background-color: {COLOR_ACCENT};
        color: {COLOR_ACCENT_DARK};
        border: none;
        font-weight: bold;
    }}
    QPushButton.accent_btn:hover {{
        background-color: {COLOR_ACCENT_HOVER};
        color: {COLOR_ACCENT_DARK};
    }}
    QPushButton.accent_btn:pressed {{
        background-color: #9ECB45;
    }}

    /* Danger Button */
    QPushButton.danger_btn {{
        background-color: rgba(255, 107, 107, 0.15);
        color: {COLOR_DANGER};
        border: 1px solid rgba(255, 107, 107, 0.4);
    }}
    QPushButton.danger_btn:hover {{
        background-color: {COLOR_DANGER};
        color: #FFFFFF;
    }}

    /* Inputs & Search */
    QLineEdit, QComboBox {{
        background-color: {COLOR_INPUT_BG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
        padding: 7px 12px;
        color: {COLOR_TEXT_PRIMARY};
        selection-background-color: {COLOR_ACCENT};
        selection-color: {COLOR_ACCENT_DARK};
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {COLOR_ACCENT};
    }}

    /* Table & Tree Views */
    QTableWidget, QTreeWidget, QListWidget {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        gridline-color: transparent;
        padding: 4px;
        outline: none;
    }}
    QTableWidget::item, QTreeWidget::item, QListWidget::item {{
        padding: 8px;
        border-radius: 6px;
        margin: 2px 4px;
    }}
    QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {{
        background-color: rgba(199, 243, 107, 0.15);
        color: {COLOR_ACCENT};
    }}
    QTableWidget::item:hover, QTreeWidget::item:hover, QListWidget::item:hover {{
        background-color: {COLOR_CARD_HOVER};
    }}
    QHeaderView::section {{
        background-color: {COLOR_INPUT_BG};
        color: {COLOR_TEXT_MUTED};
        padding: 6px 10px;
        border: none;
        border-bottom: 1px solid {COLOR_BORDER};
        font-weight: 600;
    }}

    /* Progress Bars */
    QProgressBar {{
        background-color: {COLOR_PROGRESS_BG};
        border: none;
        border-radius: 6px;
        height: 10px;
        text-align: center;
        color: transparent;
    }}
    QProgressBar::chunk {{
        background-color: {COLOR_ACCENT};
        border-radius: 6px;
    }}

    /* Checkboxes */
    QCheckBox {{
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid {COLOR_BORDER};
        background: {COLOR_INPUT_BG};
    }}
    QCheckBox::indicator:checked {{
        background: {COLOR_ACCENT};
        border-color: {COLOR_ACCENT};
    }}

    /* Tab & Navigation Buttons */
    QPushButton.nav_item {{
        background-color: transparent;
        border: none;
        border-radius: 10px;
        text-align: left;
        padding: 10px 14px;
        font-size: 13px;
        color: {COLOR_TEXT_MUTED};
    }}
    QPushButton.nav_item:hover {{
        background-color: {COLOR_CARD_BG};
        color: {COLOR_TEXT_PRIMARY};
    }}
    QPushButton.nav_item.active {{
        background-color: {COLOR_CARD_BG};
        color: {COLOR_ACCENT};
        font-weight: bold;
        border-left: 3px solid {COLOR_ACCENT};
    }}

    /* Tooltips */
    QToolTip {{
        background-color: {COLOR_CARD_BG};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 5px;
    }}
    """
