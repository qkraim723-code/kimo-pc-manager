"""Safe cleanup center page with transparent audit and confirmation."""

from typing import List
from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.cleanup_service import CleanupCategory, SafeCleanupService
from core.localization import format_bytes, t
from core.windows_tools import WindowsToolsService
from ui.components.dialogs import ConfirmDialog
from ui.icons import create_vector_icon
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BG_PRIMARY,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_DANGER,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
)


class CleanupScanWorker(QObject):
    finished = Signal()
    progress = Signal(str)

    def __init__(self, service: SafeCleanupService, categories: List[CleanupCategory]):
        super().__init__()
        self.service = service
        self.categories = categories

    def run(self):
        for cat in self.categories:
            self.service.scan_category(cat, progress_callback=lambda fname: self.progress.emit(fname))
        self.finished.emit()


class CleanupExecWorker(QObject):
    finished = Signal(int, int, int)
    progress = Signal(str, int)

    def __init__(self, service: SafeCleanupService, categories: List[CleanupCategory]):
        super().__init__()
        self.service = service
        self.categories = categories

    def run(self):
        cleaned, freed, skipped = self.service.execute_cleanup(
            self.categories, progress_callback=lambda fn, idx: self.progress.emit(fn, idx)
        )
        self.finished.emit(cleaned, freed, skipped)


class CleanupPage(QWidget):
    """Conservative temporary cache cleaner with zero risk to personal files."""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.service = SafeCleanupService()
        self.categories = self.service.get_categories()
        self.thread: QThread = None
        self.category_widgets = []

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        self.title_label = QLabel(t("cleanup.title"))
        self.title_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        header.addWidget(self.title_label)

        self.subtitle_label = QLabel(t("cleanup.subtitle"))
        self.subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        header.addWidget(self.subtitle_label)
        main_layout.addLayout(header)

        # Action Buttons Card
        ctrl_frame = QFrame()
        ctrl_frame.setProperty("class", "card_frame")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setContentsMargins(16, 12, 16, 12)
        ctrl_layout.setSpacing(12)

        self.btn_scan = QPushButton(t("cleanup.btn_scan"))
        self.btn_scan.setIcon(create_vector_icon("search", color="#122019", size=16))
        self.btn_scan.setProperty("class", "accent_btn")
        self.btn_scan.clicked.connect(self._start_scan)
        ctrl_layout.addWidget(self.btn_scan)

        self.btn_clean = QPushButton(t("cleanup.btn_clean"))
        self.btn_clean.setIcon(create_vector_icon("trash", color="#122019", size=16))
        self.btn_clean.setProperty("class", "accent_btn")
        self.btn_clean.setEnabled(False)
        self.btn_clean.clicked.connect(self._confirm_and_clean)
        ctrl_layout.addWidget(self.btn_clean)

        ctrl_layout.addStretch()

        self.btn_recycle = QPushButton(t("cleanup.btn_open_recycle"))
        self.btn_recycle.setIcon(create_vector_icon("trash", color=COLOR_ACCENT, size=16))
        self.btn_recycle.clicked.connect(WindowsToolsService.open_recycle_bin)
        ctrl_layout.addWidget(self.btn_recycle)

        main_layout.addWidget(ctrl_frame)

        # Status & Progress Frame
        status_frame = QFrame()
        status_frame.setProperty("class", "card_frame")
        s_layout = QVBoxLayout(status_frame)
        s_layout.setContentsMargins(16, 12, 16, 12)
        s_layout.setSpacing(8)

        self.status_label = QLabel(t("cleanup.status_idle"))
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        s_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setVisible(False)
        s_layout.addWidget(self.progress_bar)

        main_layout.addWidget(status_frame)

        # Categories List Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background: {COLOR_BG_PRIMARY}; border: none;")

        cats_container = QWidget()
        self.cats_layout = QVBoxLayout(cats_container)
        self.cats_layout.setContentsMargins(0, 0, 0, 0)
        self.cats_layout.setSpacing(10)

        self._render_category_cards()

        scroll.setWidget(cats_container)
        main_layout.addWidget(scroll, stretch=1)

        # Safety Guarantee Shield
        shield_frame = QFrame()
        shield_layout = QHBoxLayout(shield_frame)
        shield_layout.setContentsMargins(14, 12, 14, 12)
        shield_layout.setSpacing(12)
        shield_frame.setStyleSheet(
            f"background: rgba(199, 243, 107, 0.08); border: 1px solid rgba(199, 243, 107, 0.2); border-radius: 10px;"
        )

        shield_icon = QLabel()
        shield_icon.setPixmap(create_vector_icon("shield", color=COLOR_ACCENT, size=24).pixmap(24, 24))
        shield_layout.addWidget(shield_icon)

        shield_text = QLabel(t("cleanup.safety_guarantee"))
        shield_text.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 12px; line-height: 1.4;")
        shield_text.setWordWrap(True)
        shield_layout.addWidget(shield_text, stretch=1)

        main_layout.addWidget(shield_frame)

    def _render_category_cards(self):
        for w in self.category_widgets:
            w.deleteLater()
        self.category_widgets.clear()

        for cat in self.categories:
            card = QFrame()
            card.setProperty("class", "card_frame")
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(16, 14, 16, 14)
            c_layout.setSpacing(14)

            cb = QCheckBox()
            cb.setChecked(cat.is_enabled)
            cb.toggled.connect(lambda checked, c=cat: self._on_category_toggled(c, checked))
            c_layout.addWidget(cb)

            info_layout = QVBoxLayout()
            info_layout.setSpacing(4)

            title_lbl = QLabel(t(cat.title_key))
            title_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
            info_layout.addWidget(title_lbl)

            desc_lbl = QLabel(t(cat.desc_key))
            desc_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
            info_layout.addWidget(desc_lbl)

            c_layout.addLayout(info_layout, stretch=1)

            # Size badge
            size_lbl = QLabel(format_bytes(cat.total_size))
            size_lbl.setStyleSheet(
                f"background: {COLOR_CARD_BG}; border: 1px solid {COLOR_BORDER}; "
                f"color: {COLOR_TEXT_PRIMARY}; padding: 6px 12px; border-radius: 8px; font-weight: bold;"
            )
            c_layout.addWidget(size_lbl)

            cat._size_label = size_lbl
            self.cats_layout.addWidget(card)
            self.category_widgets.append(card)

        self.cats_layout.addStretch()

    def _on_category_toggled(self, category: CleanupCategory, checked: bool):
        category.is_enabled = checked
        self._update_clean_button_state()

    def _update_clean_button_state(self):
        total_enabled_size = sum(c.total_size for c in self.categories if c.is_enabled)
        total_enabled_files = sum(len(c.files) for c in self.categories if c.is_enabled)
        self.btn_clean.setEnabled(total_enabled_files > 0)

    def _start_scan(self):
        self.btn_scan.setEnabled(False)
        self.btn_clean.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText(t("cleanup.status_scanning"))

        self.thread = QThread()
        self.worker = CleanupScanWorker(self.service, self.categories)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(lambda fname: self.status_label.setText(f"{t('cleanup.status_scanning')} ({fname})"))
        self.worker.finished.connect(self._on_scan_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def _on_scan_finished(self):
        self.btn_scan.setEnabled(True)
        self.progress_bar.setVisible(False)

        total_size = sum(c.total_size for c in self.categories)
        total_files = sum(len(c.files) for c in self.categories)

        for cat in self.categories:
            if hasattr(cat, "_size_label"):
                cat._size_label.setText(format_bytes(cat.total_size))

        self.status_label.setText(
            f"Found {total_files} safe temporary files totaling {format_bytes(total_size)}."
        )
        self._update_clean_button_state()

    def _confirm_and_clean(self):
        total_size = sum(c.total_size for c in self.categories if c.is_enabled)
        total_files = sum(len(c.files) for c in self.categories if c.is_enabled)

        confirm = ConfirmDialog(
            title=t("cleanup.confirm_cleanup_title"),
            message=t("cleanup.confirm_cleanup_msg", count=total_files, size=format_bytes(total_size)),
            is_danger=True,
            parent=self,
        )

        if confirm.exec_() == ConfirmDialog.Accepted:
            self.btn_scan.setEnabled(False)
            self.btn_clean.setEnabled(False)
            self.progress_bar.setVisible(True)

            self.thread = QThread()
            self.worker = CleanupExecWorker(self.service, self.categories)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.progress.connect(lambda fn, idx: self.status_label.setText(f"Cleaning: {fn}"))
            self.worker.finished.connect(self._on_clean_finished)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

    def _on_clean_finished(self, cleaned: int, freed: int, skipped: int):
        self.btn_scan.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(
            t("cleanup.status_clean_done", freed=format_bytes(freed), cleaned_files=cleaned)
        )
        # Re-scan to refresh values
        self._start_scan()

    def refresh_translations(self):
        self.title_label.setText(t("cleanup.title"))
        self.subtitle_label.setText(t("cleanup.subtitle"))
        self.btn_scan.setText(t("cleanup.btn_scan"))
        self.btn_clean.setText(t("cleanup.btn_clean"))
        self.btn_recycle.setText(t("cleanup.btn_open_recycle"))
        self._render_category_cards()
