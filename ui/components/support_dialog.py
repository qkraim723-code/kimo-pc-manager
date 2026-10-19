"""Support links and optional sponsor advertisement dialog."""

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from core.localization import t
from ui.components.dialogs import BaseStyledDialog
from ui.components.toggle_switch import ToggleSwitch
from ui.icons import create_vector_icon
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    set_button_variant,
)


BINANCE_ID = "1025369648"
PAYPAL_EMAIL = "karimqutb2005@gmail.com"
ADVERTISEMENT_URL = "https://uplcm.com/4/12074784"


class SupportDialog(BaseStyledDialog):
    def __init__(self, config=None, parent=None):
        super().__init__(t("support.title"), parent)
        self.config = config
        self.setMinimumWidth(620)
        self.setMaximumWidth(700)
        layout = self.main_layout
        layout.setSpacing(14)

        intro = QLabel(t("support.intro"))
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
        layout.addWidget(intro)

        methods = QHBoxLayout()
        methods.setSpacing(12)
        methods.addWidget(self._payment_card(
            "binance", "#F0B90B", t("support.binance"), BINANCE_ID,
            "binance_id", "support.copy_binance",
        ))
        methods.addWidget(self._payment_card(
            "paypal", "#009CDE", t("support.paypal"), PAYPAL_EMAIL,
            "paypal_email", "support.copy_paypal",
        ))
        layout.addLayout(methods)

        self.copy_status = QLabel("")
        self.copy_status.setStyleSheet(f"color: {COLOR_ACCENT}; background: transparent;")
        layout.addWidget(self.copy_status)

        self.ad_card = QFrame()
        self.ad_card.setObjectName("support_ad_card")
        self.ad_card.setStyleSheet(
            f"QFrame#support_ad_card {{ background: {COLOR_CARD_BG}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        ad_layout = QVBoxLayout(self.ad_card)
        ad_layout.setContentsMargins(14, 12, 14, 12)
        ad_layout.setSpacing(12)
        ad_header = QHBoxLayout()
        ad_header.setSpacing(12)
        ad_icon = QLabel()
        ad_icon.setPixmap(create_vector_icon("info", color=COLOR_ACCENT, size=22).pixmap(22, 22))
        ad_icon.setStyleSheet("background: transparent; border: none;")
        ad_header.addWidget(ad_icon)
        self.ad_text = QLabel(t("support.ad_description"))
        self.ad_text.setWordWrap(True)
        self.ad_text.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;")
        ad_header.addWidget(self.ad_text, 1)
        self.ad_button = QPushButton(t("support.open_ad"))
        self.ad_button.setIcon(create_vector_icon("forward", color="#122019", size=15))
        set_button_variant(self.ad_button, "accent_btn")
        self.ad_button.clicked.connect(self._open_ad)
        ad_header.addWidget(self.ad_button)
        ad_layout.addLayout(ad_header)
        ads_toggle_row = QHBoxLayout()
        self.ads_label = QLabel(t("support.ads_enabled"))
        self.ads_label.setWordWrap(True)
        self.ads_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none;")
        ads_toggle_row.addWidget(self.ads_label, 1)
        self.ads_switch = ToggleSwitch(
            config.get("support_ads_enabled", True) if config else True
        )
        self.ads_switch.setAccessibleName(t("support.ads_enabled"))
        self.ads_switch.setToolTip(t("support.ads_tooltip"))
        self.ads_switch.toggled.connect(self._on_ads_toggled)
        ads_toggle_row.addWidget(self.ads_switch)
        ad_layout.addLayout(ads_toggle_row)
        layout.addWidget(self.ad_card)

        close_button = QPushButton(t("common.close"))
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignRight)

    def _payment_card(self, icon_name, icon_color, title, value, copy_key, button_key):
        card = QFrame()
        card.setObjectName("support_payment_card")
        card.setStyleSheet(
            f"QFrame#support_payment_card {{ background: {COLOR_CARD_BG}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; }}"
        )
        box = QVBoxLayout(card)
        box.setContentsMargins(14, 14, 14, 14)
        box.setSpacing(8)
        row = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(create_vector_icon(icon_name, color=icon_color, size=42).pixmap(42, 42))
        icon.setFixedSize(44, 44)
        icon.setStyleSheet("background: transparent; border: none;")
        row.addWidget(icon)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; background: transparent; font-weight: 700; border: none;")
        row.addWidget(title_label)
        row.addStretch()
        box.addLayout(row)
        value_label = QLabel(value)
        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        value_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; background: transparent; border: none; font-weight: 600;")
        value_label.setWordWrap(True)
        box.addWidget(value_label)
        copy_button = QPushButton(t(button_key))
        copy_button.setMinimumHeight(42)
        copy_button.clicked.connect(lambda: self._copy_value(value, copy_key))
        box.addWidget(copy_button)
        return card

    def _copy_value(self, value, key):
        QApplication.clipboard().setText(value)
        self.copy_status.setText(t("support.copied", value=t(key)))

    def _open_ad(self):
        QDesktopServices.openUrl(QUrl(ADVERTISEMENT_URL))

    def _on_ads_toggled(self, enabled):
        if self.config is not None:
            self.config.set("support_ads_enabled", bool(enabled))
