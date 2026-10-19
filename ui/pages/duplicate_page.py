"""Duplicate file finder page with group view and safe recycling."""

from pathlib import Path
from typing import List, Set
from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.duplicate_finder import DuplicateFinder, DuplicateGroup
from core.localization import format_bytes, t
from ui.components.dialogs import ConfirmDialog
from ui.icons import create_vector_icon
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_DANGER,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
)


class DuplicateScanWorker(QObject):
    finished = Signal(list)
    progress = Signal(str, int)

    def __init__(self, finder: DuplicateFinder, target_path: Path):
        super().__init__()
        self.finder = finder
        self.target_path = target_path

    def run(self):
        def on_prog(msg, count):
            self.progress.emit(msg, count)

        groups = self.finder.scan(self.target_path, progress_callback=on_prog)
        self.finished.emit(groups)


class DuplicatePage(QWidget):
    """Accurate duplicate detection with safe original preservation."""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.finder = DuplicateFinder()
        self.groups: List[DuplicateGroup] = []
        self.thread: QThread = None
        self.worker: DuplicateScanWorker = None

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        self.title_label = QLabel(t("duplicates.title"))
        self.title_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        header.addWidget(self.title_label)

        self.subtitle_label = QLabel(t("duplicates.subtitle"))
        self.subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        header.addWidget(self.subtitle_label)
        main_layout.addLayout(header)

        # Selection Card
        ctrl_frame = QFrame()
        ctrl_frame.setProperty("class", "card_frame")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setContentsMargins(16, 12, 16, 12)
        ctrl_layout.setSpacing(12)

        lbl = QLabel(t("duplicates.select_folder"))
        lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: 500;")
        ctrl_layout.addWidget(lbl)

        self.path_edit = QLineEdit(str(Path.home() / "Downloads"))
        ctrl_layout.addWidget(self.path_edit, stretch=1)

        self.btn_browse = QPushButton(t("duplicates.btn_browse"))
        self.btn_browse.setIcon(create_vector_icon("folder", color=COLOR_ACCENT, size=16))
        self.btn_browse.clicked.connect(self._on_browse)
        ctrl_layout.addWidget(self.btn_browse)

        self.btn_start = QPushButton(t("duplicates.btn_start"))
        self.btn_start.setIcon(create_vector_icon("search", color="#122019", size=16))
        self.btn_start.setProperty("class", "accent_btn")
        self.btn_start.clicked.connect(self._start_scan)
        ctrl_layout.addWidget(self.btn_start)

        self.btn_cancel = QPushButton(t("duplicates.btn_cancel"))
        self.btn_cancel.setProperty("class", "danger_btn")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_scan)
        ctrl_layout.addWidget(self.btn_cancel)

        main_layout.addWidget(ctrl_frame)

        # Status & Progress Frame
        status_frame = QFrame()
        status_frame.setProperty("class", "card_frame")
        s_layout = QVBoxLayout(status_frame)
        s_layout.setContentsMargins(16, 12, 16, 12)
        s_layout.setSpacing(8)

        self.status_label = QLabel(t("duplicates.status_idle"))
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        s_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setVisible(False)
        s_layout.addWidget(self.progress_bar)

        main_layout.addWidget(status_frame)

        # Action bar: Auto-select & Delete
        action_bar = QHBoxLayout()
        self.btn_auto_select = QPushButton(t("duplicates.btn_auto_select"))
        self.btn_auto_select.setIcon(create_vector_icon("copy", color=COLOR_ACCENT, size=16))
        self.btn_auto_select.setEnabled(False)
        self.btn_auto_select.clicked.connect(self._auto_select)
        action_bar.addWidget(self.btn_auto_select)

        action_bar.addStretch()

        self.btn_delete = QPushButton(t("duplicates.btn_delete_selected"))
        self.btn_delete.setIcon(create_vector_icon("trash", color="#FFFFFF", size=16))
        self.btn_delete.setProperty("class", "danger_btn")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self._on_delete_selected)
        action_bar.addWidget(self.btn_delete)

        main_layout.addLayout(action_bar)

        # Results Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([t("file_manager.col_name"), t("file_manager.col_size"), t("file_manager.properties_path")])
        self.tree.setColumnWidth(0, 300)
        self.tree.setColumnWidth(1, 120)
        main_layout.addWidget(self.tree, stretch=1)

        # Safety Note Banner
        safety_banner = QLabel(t("duplicates.safe_warning"))
        safety_banner.setStyleSheet(
            f"color: {COLOR_ACCENT}; background: rgba(199, 243, 107, 0.08); "
            f"border: 1px solid rgba(199, 243, 107, 0.2); border-radius: 8px; padding: 10px 14px;"
        )
        main_layout.addWidget(safety_banner)

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, t("duplicates.btn_browse"), str(Path.home()))
        if folder:
            self.path_edit.setText(folder)

    def _start_scan(self):
        target = Path(self.path_edit.text().strip())
        if not target.exists():
            return

        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_auto_select.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.tree.clear()

        self.thread = QThread()
        self.worker = DuplicateScanWorker(self.finder, target)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(lambda msg, cnt: self.status_label.setText(msg))
        self.worker.finished.connect(self._on_scan_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def _cancel_scan(self):
        self.finder.cancel()
        self.btn_cancel.setEnabled(False)

    def _on_scan_finished(self, groups: List[DuplicateGroup]):
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.groups = groups

        if not groups:
            self.status_label.setText(t("duplicates.no_duplicates"))
            return

        total_reclaimable = sum(g.reclaimable_size for g in groups)
        total_files = sum(len(g.files) for g in groups)

        self.status_label.setText(
            t(
                "duplicates.result_summary",
                groups=len(groups),
                files=total_files,
                saving=format_bytes(total_reclaimable),
            )
        )
        self.btn_auto_select.setEnabled(True)
        self.btn_delete.setEnabled(True)

        self.tree.clear()
        for idx, grp in enumerate(groups, start=1):
            header_text = t("duplicates.group_header", num=idx, size=format_bytes(grp.file_size), count=len(grp.files))
            group_item = QTreeWidgetItem(self.tree, [header_text, format_bytes(grp.reclaimable_size), ""])
            group_item.setIcon(0, create_vector_icon("duplicate", color=COLOR_ACCENT, size=16))
            group_item.setExpanded(True)

            for f_idx, fpath in enumerate(grp.files):
                is_original = (f_idx == 0)
                display_name = fpath.name + (" [Original - Protected]" if is_original else "")
                child = QTreeWidgetItem(group_item, [display_name, format_bytes(grp.file_size), str(fpath.parent)])
                child.setData(0, Qt.UserRole, str(fpath))
                child.setData(0, Qt.UserRole + 1, is_original)

                if is_original:
                    child.setFlags(child.flags() & ~Qt.ItemIsUserCheckable)
                    child.setIcon(0, create_vector_icon("shield", color=COLOR_ACCENT, size=14))
                else:
                    child.setCheckState(0, Qt.Unchecked)
                    child.setIcon(0, create_vector_icon("file", color=COLOR_TEXT_MUTED, size=14))

    def _auto_select(self):
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            grp_item = root.child(i)
            for j in range(grp_item.childCount()):
                child = grp_item.child(j)
                is_original = child.data(0, Qt.UserRole + 1)
                if not is_original:
                    child.setCheckState(0, Qt.Checked)

    def _on_delete_selected(self):
        root = self.tree.invisibleRootItem()
        selected_files: List[Path] = []
        protected_set: Set[Path] = set()

        for i in range(root.childCount()):
            grp_item = root.child(i)
            for j in range(grp_item.childCount()):
                child = grp_item.child(j)
                p_str = child.data(0, Qt.UserRole)
                if not p_str:
                    continue
                p = Path(p_str)
                is_orig = child.data(0, Qt.UserRole + 1)
                if is_orig:
                    protected_set.add(p)
                elif child.checkState(0) == Qt.Checked:
                    selected_files.append(p)

        if not selected_files:
            return

        approx_size = sum(f.stat().st_size for f in selected_files if f.exists())
        confirm = ConfirmDialog(
            title=t("duplicates.confirm_delete_title"),
            message=t("duplicates.confirm_delete_msg", count=len(selected_files), saving=format_bytes(approx_size)),
            is_danger=True,
            parent=self,
        )
        if confirm.exec_() == ConfirmDialog.Accepted:
            del_count, reclaimed, errors = self.finder.delete_selected(selected_files, protected_set)
            self._start_scan()

    def refresh_translations(self):
        self.title_label.setText(t("duplicates.title"))
        self.subtitle_label.setText(t("duplicates.subtitle"))
        self.btn_browse.setText(t("duplicates.btn_browse"))
        self.btn_start.setText(t("duplicates.btn_start"))
        self.btn_cancel.setText(t("duplicates.btn_cancel"))
        self.btn_auto_select.setText(t("duplicates.btn_auto_select"))
        self.btn_delete.setText(t("duplicates.btn_delete_selected"))
        self.tree.setHeaderLabels([t("file_manager.col_name"), t("file_manager.col_size"), t("file_manager.properties_path")])
