"""Settings and application preferences page."""

import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.config import ConfigManager
from core.localization import get_localization, t
from ui.icons import create_vector_icon
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BG_PRIMARY,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
)


class SettingsPage(QWidget):
    """User preferences, language toggling, and diagnostics."""

    language_changed = Signal(str)

    def __init__(self, config: ConfigManager, parent: QWidget = None):
        super().__init__(parent)
        self.config = config
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        self.title_label = QLabel(t("settings.title"))
        self.title_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        header.addWidget(self.title_label)

        self.subtitle_label = QLabel(t("settings.subtitle"))
        self.subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        header.addWidget(self.subtitle_label)
        main_layout.addLayout(header)

        # Settings Card
        card = QFrame()
        card.setProperty("class", "card_frame")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(16)

        # Language Row
        lang_row = QHBoxLayout()
        self.lbl_lang = QLabel(t("settings.language"))
        self.lbl_lang.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; font-weight: 500;")
        lang_row.addWidget(self.lbl_lang)
        lang_row.addStretch()

        self.combo_lang = QComboBox()
        self.combo_lang.addItem(t("settings.lang_ar"), "ar")
        self.combo_lang.addItem(t("settings.lang_en"), "en")

        current_lang = self.config.get("language", "ar")
        idx = 0 if current_lang == "ar" else 1
        self.combo_lang.setCurrentIndex(idx)
        self.combo_lang.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.combo_lang)
        c_layout.addLayout(lang_row)

        c_layout.addWidget(self._make_divider())

        # Refresh Interval Row
        refresh_row = QHBoxLayout()
        self.lbl_refresh = QLabel(t("settings.refresh_rate"))
        self.lbl_refresh.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; font-weight: 500;")
        refresh_row.addWidget(self.lbl_refresh)
        refresh_row.addStretch()

        self.combo_refresh = QComboBox()
        self.combo_refresh.addItem(t("settings.refresh_1s"), 1)
        self.combo_refresh.addItem(t("settings.refresh_2s"), 2)
        self.combo_refresh.addItem(t("settings.refresh_5s"), 5)

        curr_rate = self.config.get("refresh_interval", 2)
        rate_idx = {1: 0, 2: 1, 5: 2}.get(curr_rate, 1)
        self.combo_refresh.setCurrentIndex(rate_idx)
        self.combo_refresh.currentIndexChanged.connect(self._on_refresh_rate_changed)
        refresh_row.addWidget(self.combo_refresh)
        c_layout.addLayout(refresh_row)

        c_layout.addWidget(self._make_divider())

        # Reset Defaults & Open Logs
        btn_row = QHBoxLayout()
        self.btn_reset = QPushButton(t("settings.btn_reset_defaults"))
        self.btn_reset.setIcon(create_vector_icon("refresh", color=COLOR_ACCENT, size=16))
        self.btn_reset.clicked.connect(self._reset_defaults)
        btn_row.addWidget(self.btn_reset)

        self.btn_logs = QPushButton(t("settings.btn_open_logs"))
        self.btn_logs.setIcon(create_vector_icon("folder", color=COLOR_ACCENT, size=16))
        self.btn_logs.clicked.connect(self._open_logs)
        btn_row.addWidget(self.btn_logs)

        btn_row.addStretch()
        c_layout.addLayout(btn_row)

        main_layout.addWidget(card)

        # About Card
        about_card = QFrame()
        about_card.setProperty("class", "card_frame")
        a_layout = QVBoxLayout(about_card)
        a_layout.setContentsMargins(20, 20, 20, 20)
        a_layout.setSpacing(10)

        about_title = QLabel(t("settings.app_info") + " - v1.0.0")
        about_title.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 16px; font-weight: bold;")
        a_layout.addWidget(about_title)

        about_desc = QLabel(t("settings.about_text"))
        about_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; line-height: 1.5;")
        about_desc.setWordWrap(True)
        a_layout.addWidget(about_desc)

        main_layout.addWidget(about_card)
        main_layout.addStretch()

    def _make_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {COLOR_BORDER}; max-height: 1px;")
        return line

    def _on_lang_changed(self, index: int):
        new_lang = self.combo_lang.currentData()
        self.config.set("language", new_lang)
        get_localization().set_language(new_lang)
        self.language_changed.emit(new_lang)

    def _on_refresh_rate_changed(self, index: int):
        rate = self.combo_refresh.currentData()
        self.config.set("refresh_interval", rate)

    def _reset_defaults(self):
        self.config.reset_to_defaults()
        self._on_lang_changed(0)

    def _open_logs(self):
        logs_p = self.config.get_logs_dir()
        try:
            os.startfile(str(logs_p))
        except Exception:
            pass

    def refresh_translations(self):
        self.title_label.setText(t("settings.title"))
        self.subtitle_label.setText(t("settings.subtitle"))
        self.lbl_lang.setText(t("settings.language"))
        self.lbl_refresh.setText(t("settings.refresh_rate"))
        self.btn_reset.setText(t("settings.btn_reset_defaults"))
        self.btn_logs.setText(t("settings.btn_open_logs"))
