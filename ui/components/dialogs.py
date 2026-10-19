"""Custom styled modal dialogs for Kimo PC Manager."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.localization import format_bytes, t
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


class BaseStyledDialog(QDialog):
    """Base modal dialog with theme styling."""

    def __init__(self, title: str, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {COLOR_BG_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
            """
        )
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(16)


class ConfirmDialog(BaseStyledDialog):
    """Clean confirmation dialog with Cancel and Confirm buttons."""

    def __init__(self, title: str, message: str, is_danger: bool = False, parent: QWidget = None):
        super().__init__(title, parent)
        self.setMinimumWidth(380)

        # Message
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; line-height: 1.4;")
        self.main_layout.addWidget(msg_label)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)
        btn_box.addStretch()

        self.cancel_btn = QPushButton(t("common.cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton(t("common.ok"))
        if is_danger:
            self.confirm_btn.setProperty("class", "danger_btn")
        else:
            self.confirm_btn.setProperty("class", "accent_btn")
        self.confirm_btn.clicked.connect(self.accept)
        btn_box.addWidget(self.confirm_btn)

        self.main_layout.addLayout(btn_box)


class PromptDialog(BaseStyledDialog):
    """Text prompt input dialog for new folder name or rename."""

    def __init__(self, title: str, prompt_text: str, default_value: str = "", parent: QWidget = None):
        super().__init__(title, parent)
        self.setMinimumWidth(380)

        label = QLabel(prompt_text)
        label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 13px;")
        self.main_layout.addWidget(label)

        self.input_field = QLineEdit(default_value)
        self.input_field.selectAll()
        self.main_layout.addWidget(self.input_field)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)
        btn_box.addStretch()

        cancel_btn = QPushButton(t("common.cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        ok_btn = QPushButton(t("common.ok"))
        ok_btn.setProperty("class", "accent_btn")
        ok_btn.clicked.connect(self.accept)
        btn_box.addWidget(ok_btn)

        self.main_layout.addLayout(btn_box)

    def get_text(self) -> str:
        return self.input_field.text().strip()


class ConflictDialog(BaseStyledDialog):
    """File conflict resolution dialog (Rename, Overwrite, Skip)."""

    def __init__(self, file_name: str, parent: QWidget = None):
        super().__init__(t("file_manager.conflict_title"), parent)
        self.setMinimumWidth(440)
        self.chosen_action = "rename"

        msg = QLabel(t("file_manager.conflict_msg", name=file_name))
        msg.setWordWrap(True)
        msg.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 13px;")
        self.main_layout.addWidget(msg)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        btn_rename = QPushButton(t("file_manager.conflict_rename"))
        btn_rename.setProperty("class", "accent_btn")
        btn_rename.clicked.connect(lambda: self._select("rename"))
        btn_box.addWidget(btn_rename)

        btn_overwrite = QPushButton(t("file_manager.conflict_overwrite"))
        btn_overwrite.setProperty("class", "danger_btn")
        btn_overwrite.clicked.connect(lambda: self._select("overwrite"))
        btn_box.addWidget(btn_overwrite)

        btn_skip = QPushButton(t("file_manager.conflict_skip"))
        btn_skip.clicked.connect(lambda: self._select("skip"))
        btn_box.addWidget(btn_skip)

        self.main_layout.addLayout(btn_box)

    def _select(self, action: str):
        self.chosen_action = action
        self.accept()


class PropertiesDialog(BaseStyledDialog):
    """File or folder properties viewer dialog."""

    def __init__(self, props: dict, parent: QWidget = None):
        super().__init__(t("file_manager.properties_title", name=props.get("name", "")), parent)
        self.setMinimumWidth(440)

        grid = QVBoxLayout()
        grid.setSpacing(10)

        rows = [
            (t("file_manager.col_name"), props.get("name", "")),
            (t("file_manager.properties_path"), props.get("path", "")),
            (t("file_manager.properties_size"), format_bytes(props.get("size", 0))),
            (t("file_manager.properties_created"), props.get("created", "-")),
            (t("file_manager.properties_modified"), props.get("modified", "-")),
        ]

        if props.get("is_dir"):
            rows.append((t("file_manager.properties_contains"), f"{props.get('item_count', 0)} {t('file_manager.items_count', count='')}"))

        for label_text, val_text in rows:
            row_box = QHBoxLayout()
            lbl = QLabel(label_text + ":")
            lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-weight: bold; width: 100px;")
            val = QLabel(str(val_text))
            val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            val.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            row_box.addWidget(lbl)
            row_box.addWidget(val, stretch=1)
            grid.addLayout(row_box)

        self.main_layout.addLayout(grid)

        close_btn = QPushButton(t("common.close"))
        close_btn.setProperty("class", "accent_btn")
        close_btn.clicked.connect(self.accept)
        self.main_layout.addWidget(close_btn, alignment=Qt.AlignRight)
