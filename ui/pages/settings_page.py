"""Settings and application preferences page."""

import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.config import ConfigManager
from core.localization import get_localization, t
from ui.components.dialogs import ConfirmDialog
from ui.icons import create_vector_icon
from ui.components.help_banner import HelpBanner
from ui.components.support_dialog import SupportDialog
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BG_PRIMARY,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    set_button_variant,
)


class SettingsPage(QWidget):
    """User preferences, language toggling, and diagnostics."""

    language_changed = Signal(str)
    refresh_interval_changed = Signal(int)

    def __init__(self, config: ConfigManager, parent: QWidget = None):
        super().__init__(parent)
        self.config = config
        from core.admin_helper import is_admin
        self.admin_active = is_admin()
        self.btn_elevate = None
        self._build_ui()

    def _build_ui(self):
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        page_layout.addWidget(self.scroll_area)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("settings_scroll_content")
        self.scroll_area.setWidget(self.scroll_content)
        main_layout = QVBoxLayout(self.scroll_content)
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
        self.combo_lang.setMinimumSize(240, 44)
        self.combo_lang.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; background: {COLOR_CARD_BG}; padding: 7px 12px;"
        )
        self.combo_lang.addItem(t("settings.lang_ar"), "ar")
        self.combo_lang.addItem(t("settings.lang_en"), "en")

        current_lang = self.config.get("language", "en")
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
        self.combo_refresh.setMinimumSize(240, 44)
        self.combo_refresh.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; background: {COLOR_CARD_BG}; padding: 7px 12px;"
        )
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

        # Permissions / Administrator Elevation
        perm_box = QVBoxLayout()
        perm_box.setSpacing(8)

        lbl_perm_title = QLabel(t("settings.permissions"))
        lbl_perm_title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; font-weight: bold;")
        perm_box.addWidget(lbl_perm_title)

        perm_row = QHBoxLayout()
        self.lbl_admin_status = QLabel(
            f"{t('settings.admin_status')} {t('settings.is_admin') if self.admin_active else t('settings.is_user')}"
        )
        self.lbl_admin_status.setWordWrap(True)
        self.lbl_admin_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.lbl_admin_status.setStyleSheet(
            f"color: {'#69DB7C' if self.admin_active else '#FFB84D'}; font-weight: 500;"
        )
        perm_row.addWidget(self.lbl_admin_status)

        if not self.admin_active:
            from core.admin_helper import restart_as_admin
            self.btn_elevate = QPushButton(t("settings.btn_elevate"))
            set_button_variant(self.btn_elevate, "accent_btn")
            self.btn_elevate.setIcon(create_vector_icon("shield", color="#122019", size=16))
            self.btn_elevate.clicked.connect(restart_as_admin)
            perm_row.addWidget(self.btn_elevate)

        perm_box.addLayout(perm_row)
        c_layout.addLayout(perm_box)

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

        self.reset_help_label = QLabel(t("settings.reset_help"))
        self.reset_help_label.setWordWrap(True)
        self.reset_help_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        c_layout.addWidget(self.reset_help_label)

        self.logs_help_label = QLabel(t("settings.logs_help"))
        self.logs_help_label.setWordWrap(True)
        self.logs_help_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        c_layout.addWidget(self.logs_help_label)

        main_layout.addWidget(card)

        # Support and optional startup advertisement
        support_card = QFrame()
        support_card.setProperty("class", "card_frame")
        support_layout = QVBoxLayout(support_card)
        support_layout.setContentsMargins(20, 16, 20, 16)
        support_layout.setSpacing(10)
        self.support_title = QLabel(t("support.title"))
        self.support_title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        support_layout.addWidget(self.support_title)
        self.support_description = QLabel(t("support.settings_description"))
        self.support_description.setWordWrap(True)
        self.support_description.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
        support_layout.addWidget(self.support_description)
        support_actions = QHBoxLayout()
        self.btn_support = QPushButton(t("support.open_support"))
        self.btn_support.setMinimumHeight(48)
        set_button_variant(self.btn_support, "accent_btn")
        self.btn_support.setIcon(create_vector_icon("heart", color="#122019", size=22))
        self.btn_support.clicked.connect(self._open_support_dialog)
        support_actions.addWidget(self.btn_support)
        self.btn_telegram = QPushButton(t("support.telegram"))
        self.btn_telegram.setMinimumHeight(48)
        self.btn_telegram.setIcon(create_vector_icon("telegram", color="#229ED9", size=24))
        self.btn_telegram.clicked.connect(self._open_telegram)
        support_actions.addWidget(self.btn_telegram)
        support_actions.addStretch()
        support_layout.addLayout(support_actions)
        main_layout.addWidget(support_card)

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
        self.help_banner = HelpBanner("settings")
        main_layout.addWidget(self.help_banner)

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
        self.refresh_interval_changed.emit(rate)

    def _open_support_dialog(self):
        SupportDialog(config=self.config, parent=self).exec()

    def _open_telegram(self):
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl("https://t.me/kimoAndroid2"))

    def _reset_defaults(self):
        confirm = ConfirmDialog(
            title=t("settings.reset_confirm_title"),
            message=t("settings.reset_confirm_msg"),
            parent=self,
        )
        if confirm.exec_() != ConfirmDialog.Accepted:
            return

        self.config.reset_to_defaults()
        language = self.config.get("language", "en")
        get_localization().set_language(language)
        self.combo_lang.blockSignals(True)
        self.combo_lang.setCurrentIndex(self.combo_lang.findData(language))
        self.combo_lang.blockSignals(False)
        refresh_rate = self.config.get("refresh_interval", 2)
        self.combo_refresh.blockSignals(True)
        self.combo_refresh.setCurrentIndex(self.combo_refresh.findData(refresh_rate))
        self.combo_refresh.blockSignals(False)
        self.language_changed.emit(language)
        self.refresh_interval_changed.emit(refresh_rate)

    def _open_logs(self):
        logs_p = self.config.get_logs_dir()
        try:
            logs_p.mkdir(parents=True, exist_ok=True)
            os.startfile(str(logs_p))
        except OSError as exc:
            QMessageBox.warning(
                self,
                t("common.error"),
                t("settings.logs_open_error", error=str(exc)),
            )

    def refresh_translations(self):
        self.help_banner.refresh_translations()
        self.title_label.setText(t("settings.title"))
        self.subtitle_label.setText(t("settings.subtitle"))
        self.support_title.setText(t("support.title"))
        self.support_description.setText(t("support.settings_description"))
        self.btn_support.setText(t("support.open_support"))
        self.btn_telegram.setText(t("support.telegram"))
        self.lbl_lang.setText(t("settings.language"))
        self.lbl_refresh.setText(t("settings.refresh_rate"))
        self.btn_reset.setText(t("settings.btn_reset_defaults"))
        self.btn_logs.setText(t("settings.btn_open_logs"))
        self.lbl_admin_status.setText(
            f"{t('settings.admin_status')} "
            f"{t('settings.is_admin') if self.admin_active else t('settings.is_user')}"
        )
        if self.btn_elevate:
            self.btn_elevate.setText(t("settings.btn_elevate"))
        self.reset_help_label.setText(t("settings.reset_help"))
        self.logs_help_label.setText(t("settings.logs_help"))
        selected_language = self.combo_lang.currentData()
        self.combo_lang.setItemText(0, t("settings.lang_ar"))
        self.combo_lang.setItemText(1, t("settings.lang_en"))
        self.combo_lang.setCurrentIndex(self.combo_lang.findData(selected_language))
        refresh_rate = self.combo_refresh.currentData()
        for index, key in enumerate(("settings.refresh_1s", "settings.refresh_2s", "settings.refresh_5s")):
            self.combo_refresh.setItemText(index, t(key))
        self.combo_refresh.setCurrentIndex(self.combo_refresh.findData(refresh_rate))
