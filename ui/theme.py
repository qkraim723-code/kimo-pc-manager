"""Design system, color tokens, and complete QSS stylesheet for Kimo PC Manager."""

import sys
from pathlib import Path

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


def set_button_variant(button, variant: str):
    """Apply a button variant directly so dialog-local styles cannot hide it."""
    button.setProperty("class", variant)
    if variant == "accent_btn":
        normal, hover, pressed, foreground, border = COLOR_ACCENT, COLOR_ACCENT_HOVER, "#9ECB45", COLOR_ACCENT_DARK, "none"
    elif variant == "danger_btn":
        normal, hover, pressed, foreground, border = "#C94855", "#B83D4A", "#9F303D", "#FFFFFF", "1px solid #E36A76"
    else:
        raise ValueError(f"Unknown button variant: {variant}")
    button.setStyleSheet(f"""
        QPushButton {{ background-color: {normal}; color: {foreground}; border: {border};
            border-radius: 10px; padding: 8px 16px; font-weight: 700; min-height: 20px; }}
        QPushButton:hover {{ background-color: {hover}; color: {foreground}; }}
        QPushButton:pressed {{ background-color: {pressed}; color: {foreground}; }}
        QPushButton:disabled {{ background-color: {COLOR_INPUT_BG}; color: {COLOR_TEXT_MUTED};
            border: 1px solid {COLOR_BORDER}; }}
    """)


def get_application_stylesheet() -> str:
    """Returns the comprehensive stylesheet for the entire application."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        assets_dir = Path(sys._MEIPASS) / "assets"
    else:
        assets_dir = Path(__file__).resolve().parent.parent / "assets"
    combo_arrow_path = (assets_dir / "chevron-down.svg").as_posix()
    return f"""
    * {{
        font-family: "Segoe UI", "Tahoma", "Arial", sans-serif;
        font-size: 13px;
        color: {COLOR_TEXT_PRIMARY};
    }}

    QMainWindow, QDialog, QWidget#root_container {{
        background-color: {COLOR_BG_PRIMARY};
    }}

    QLabel {{ color: {COLOR_TEXT_PRIMARY}; }}
    QCheckBox {{ color: {COLOR_TEXT_PRIMARY}; spacing: 8px; }}
    QCheckBox::indicator {{ width: 22px; height: 22px; border-radius: 6px; }}
    QCheckBox::indicator:unchecked {{ background: {COLOR_INPUT_BG}; border: 1px solid #668071; }}
    QCheckBox::indicator:unchecked:hover {{ border: 2px solid {COLOR_ACCENT}; }}
    QCheckBox::indicator:checked {{ background: {COLOR_ACCENT}; border: 2px solid {COLOR_ACCENT}; }}
    QComboBox QAbstractItemView {{ background: {COLOR_CARD_BG}; color: {COLOR_TEXT_PRIMARY}; selection-background-color: {COLOR_CARD_HOVER}; }}
    QAbstractItemView {{ background-color: {COLOR_CARD_BG}; color: {COLOR_TEXT_PRIMARY}; selection-background-color: {COLOR_CARD_HOVER}; selection-color: {COLOR_ACCENT}; }}
    QTableWidget QLineEdit {{ color: {COLOR_TEXT_PRIMARY}; background: {COLOR_INPUT_BG}; }}

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
    QFrame[class~="card_frame"] {{
        background-color: {COLOR_CARD_BG};
        border-radius: 14px;
        border: 1px solid {COLOR_BORDER};
    }}
    QFrame[class~="card_frame"]:hover {{
        background-color: {COLOR_CARD_HOVER};
        border: 1px solid rgba(199, 243, 107, 0.35);
    }}
    QFrame[class~="card_frame"][selected="true"] {{
        background-color: #2B4035;
        border: 1px solid {COLOR_ACCENT};
    }}

    /* Buttons */
    QPushButton {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 500;
        color: {COLOR_TEXT_PRIMARY};
        min-height: 20px;
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
        color: {COLOR_TEXT_MUTED};
        border-color: {COLOR_BORDER};
    }}

    /* Accent Action Button (Lime Green) */
    QPushButton[class~="accent_btn"] {{
        background-color: {COLOR_ACCENT};
        color: {COLOR_ACCENT_DARK};
        border: none;
        font-weight: bold;
    }}
    QPushButton[class~="accent_btn"]:hover {{
        background-color: {COLOR_ACCENT_HOVER};
        color: {COLOR_ACCENT_DARK};
    }}
    QPushButton[class~="accent_btn"]:pressed {{
        background-color: #9ECB45;
    }}

    /* Danger Button */
    QPushButton[class~="danger_btn"] {{
        background-color: #C94855;
        color: #FFFFFF;
        border: 1px solid #E36A76;
        font-weight: bold;
    }}
    QPushButton[class~="danger_btn"]:hover {{
        background-color: #B83D4A;
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
    QLineEdit::placeholder {{ color: {COLOR_TEXT_MUTED}; }}
    QComboBox::drop-down {{ background-color: {COLOR_INPUT_BG}; border-left: 1px solid {COLOR_BORDER}; width: 30px; }}
    QComboBox::down-arrow {{ image: url("{combo_arrow_path}"); width: 12px; height: 8px; }}

    /* Table & Tree Views */
    QTableWidget, QTreeWidget, QListWidget {{
        background-color: {COLOR_CARD_BG};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        gridline-color: transparent;
        padding: 4px;
        outline: none;
    }}
    QTableWidget::item, QTreeWidget::item, QListWidget::item {{
        color: {COLOR_TEXT_PRIMARY};
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
    QTableCornerButton::section {{ background-color: {COLOR_INPUT_BG}; border: none; }}
    QTableWidget:disabled, QTreeWidget:disabled {{ color: {COLOR_TEXT_MUTED}; }}
    QProgressBar::chunk {{ background-color: {COLOR_ACCENT}; }}

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

    /* Tab & Navigation Buttons */
    QPushButton[class~="nav_item"] {{
        background-color: transparent;
        border: none;
        border-radius: 10px;
        text-align: left;
        padding: 10px 14px;
        font-size: 13px;
        color: {COLOR_TEXT_MUTED};
    }}
    QPushButton[class~="nav_item"]:hover {{
        background-color: {COLOR_CARD_BG};
        color: {COLOR_TEXT_PRIMARY};
    }}
    QPushButton[class~="active"] {{
        background-color: {COLOR_CARD_BG};
        color: {COLOR_ACCENT};
        font-weight: bold;
        border: 1px solid {COLOR_BORDER};
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
