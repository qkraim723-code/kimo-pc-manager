"""Duplicate file finder page with quick presets, group view, and safe recycling."""

from pathlib import Path
from typing import List, Set
from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal
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
from ui.components.help_banner import HelpBanner
from ui.components.refresh_feedback import animate_refresh
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_DANGER,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    set_button_variant,
)


class DuplicateScanWorker(QObject):
    finished = Signal(list, bool)
    progress = Signal(str, int)

    def __init__(self, finder: DuplicateFinder, target_path: Path):
        super().__init__()
        self.finder = finder
        self.target_path = target_path

    def run(self):
        def on_prog(msg, count):
            self.progress.emit(msg, count)

        groups = self.finder.scan(self.target_path, progress_callback=on_prog)
        self.finished.emit(groups, self.finder.cancel_requested)


class DuplicatePage(QWidget):
    """Accurate duplicate detection with quick presets and safe original preservation."""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.finder = DuplicateFinder()
        self.groups: List[DuplicateGroup] = []
        self.thread: QThread = None
        self.worker: DuplicateScanWorker = None
        self._pending_delete_summary = ""
        self._restart_when_idle = False

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

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

        # Quick Presets
        presets_frame = QFrame()
        presets_frame.setProperty("class", "card_frame")
        pr_layout = QHBoxLayout(presets_frame)
        pr_layout.setContentsMargins(14, 10, 14, 10)
        pr_layout.setSpacing(10)

        self.quick_scan_label = QLabel(t("duplicates.quick_scan"))
        self.quick_scan_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-weight: bold;")
        pr_layout.addWidget(self.quick_scan_label)

        self.btn_preset_desktop = QPushButton(t("duplicates.preset_desktop"))
        self.btn_preset_desktop.clicked.connect(lambda: self._start_scan_preset(Path.home() / "Desktop"))
        pr_layout.addWidget(self.btn_preset_desktop)

        self.btn_preset_downloads = QPushButton(t("duplicates.preset_downloads"))
        self.btn_preset_downloads.clicked.connect(lambda: self._start_scan_preset(Path.home() / "Downloads"))
        pr_layout.addWidget(self.btn_preset_downloads)

        self.btn_preset_documents = QPushButton(t("duplicates.preset_documents"))
        self.btn_preset_documents.clicked.connect(lambda: self._start_scan_preset(Path.home() / "Documents"))
        pr_layout.addWidget(self.btn_preset_documents)

        self.btn_preset_pictures = QPushButton(t("duplicates.preset_pictures"))
        self.btn_preset_pictures.clicked.connect(lambda: self._start_scan_preset(Path.home() / "Pictures"))
        pr_layout.addWidget(self.btn_preset_pictures)

        pr_layout.addStretch()
        main_layout.addWidget(presets_frame)

        # Folder Selection Card
        ctrl_frame = QFrame()
        ctrl_frame.setProperty("class", "card_frame")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setContentsMargins(16, 12, 16, 12)
        ctrl_layout.setSpacing(12)

        lbl = QLabel(t("duplicates.select_folder"))
        lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: 500;")
        ctrl_layout.addWidget(lbl)

        self.path_edit = QLineEdit(str(Path.home() / "Downloads"))
        self.path_edit.setClearButtonEnabled(True)
        self.path_edit.setPlaceholderText(t("duplicates.select_folder"))
        ctrl_layout.addWidget(self.path_edit, stretch=1)

        self.btn_browse = QPushButton(t("duplicates.btn_browse"))
        self.btn_browse.setIcon(create_vector_icon("folder", color=COLOR_ACCENT, size=16))
        self.btn_browse.clicked.connect(self._on_browse)
        ctrl_layout.addWidget(self.btn_browse)

        self.btn_start = QPushButton(t("duplicates.btn_start"))
        self.btn_start.setIcon(create_vector_icon("search", color="#122019", size=16))
        set_button_variant(self.btn_start, "accent_btn")
        self.btn_start.setMinimumSize(150, 42)
        self.btn_start.clicked.connect(self._start_scan)
        ctrl_layout.addWidget(self.btn_start)

        self.btn_cancel = QPushButton(t("duplicates.btn_cancel"))
        set_button_variant(self.btn_cancel, "danger_btn")
        self.btn_cancel.setMinimumSize(86, 42)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_scan)
        ctrl_layout.addWidget(self.btn_cancel)

        main_layout.addWidget(ctrl_frame)

        # Status & Progress Frame
        status_frame = QFrame()
        status_frame.setProperty("class", "card_frame")
        s_layout = QVBoxLayout(status_frame)
        s_layout.setContentsMargins(16, 10, 16, 10)
        s_layout.setSpacing(6)

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

        self.selection_label = QLabel(t("duplicates.selection_summary", count=0, size=format_bytes(0)))
        self.selection_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        action_bar.addWidget(self.selection_label)
        action_bar.addStretch()

        self.btn_delete = QPushButton(t("duplicates.btn_delete_selected"))
        self.btn_delete.setIcon(create_vector_icon("trash", color="#FFFFFF", size=16))
        set_button_variant(self.btn_delete, "danger_btn")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self._on_delete_selected)
        action_bar.addWidget(self.btn_delete)

        main_layout.addLayout(action_bar)

        # Results Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([t("file_manager.col_name"), t("file_manager.col_size"), t("file_manager.properties_path")])
        self.tree.setColumnWidth(0, 320)
        self.tree.setColumnWidth(1, 120)
        self.tree.itemChanged.connect(self._on_tree_item_changed)
        main_layout.addWidget(self.tree, stretch=1)

        # Safety Note Banner
        self.safety_banner = QLabel(t("duplicates.safe_warning"))
        self.safety_banner.setStyleSheet(
            f"color: {COLOR_ACCENT}; background: rgba(199, 243, 107, 0.08); "
            f"border: 1px solid rgba(199, 243, 107, 0.2); border-radius: 8px; padding: 10px 14px;"
        )
        main_layout.addWidget(self.safety_banner)
        self.help_banner = HelpBanner("duplicates")
        main_layout.addWidget(self.help_banner)

    def _start_scan_preset(self, path: Path):
        if path.exists():
            self.path_edit.setText(str(path))
            self._start_scan()

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, t("duplicates.btn_browse"), str(Path.home()))
        if folder:
            self.path_edit.setText(folder)
            self.status_label.setText(t("duplicates.folder_selected", path=folder))

    def _start_scan(self):
        target = Path(self.path_edit.text().strip())
        if not target.exists() or not target.is_dir():
            self.status_label.setText(t("duplicates.invalid_folder"))
            return

        if self.thread and self.thread.isRunning():
            self.finder.cancel()
            self._restart_when_idle = True
            self.btn_start.setEnabled(False)
            self.status_label.setText(t("duplicates.status_cancelling"))
            return

        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_auto_select.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText(t("duplicates.status_scanning", file=str(target)))
        self.tree.clear()
        self.btn_auto_select.setEnabled(False)
        self.btn_delete.setEnabled(False)

        self.thread = QThread()
        self.worker = DuplicateScanWorker(self.finder, target)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(lambda msg, cnt: self.status_label.setText(msg))
        self.worker.finished.connect(self._on_scan_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._on_thread_finished)

        self.thread.start()

    def _on_thread_finished(self):
        self.thread = None
        self.worker = None
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        if self._restart_when_idle:
            self._restart_when_idle = False
            QTimer.singleShot(0, self._start_scan)

    def _cancel_scan(self):
        self._restart_when_idle = False
        self.finder.cancel()
        self.btn_cancel.setEnabled(False)

    def _on_scan_finished(self, groups: List[DuplicateGroup], cancelled: bool):
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.groups = groups

        if cancelled:
            self._set_result_status(t("duplicates.scan_cancelled"))
            return

        if not groups:
            self._set_result_status(t("duplicates.no_duplicates"))
            self.btn_auto_select.setEnabled(False)
            self.btn_delete.setEnabled(False)
            return

        total_reclaimable = sum(g.reclaimable_size for g in groups)
        total_files = sum(len(g.files) for g in groups)

        self._set_result_status(
            t(
                "duplicates.result_summary",
                groups=len(groups),
                files=total_files,
                saving=format_bytes(total_reclaimable),
            )
        )
        self.btn_auto_select.setEnabled(True)

        self.tree.blockSignals(True)
        self.tree.clear()
        for idx, grp in enumerate(groups, start=1):
            header_text = t("duplicates.group_header", num=idx, size=format_bytes(grp.file_size), count=len(grp.files))
            group_item = QTreeWidgetItem(self.tree, [header_text, format_bytes(grp.reclaimable_size), ""])
            group_item.setIcon(0, create_vector_icon("duplicate", color=COLOR_ACCENT, size=16))
            group_item.setExpanded(True)

            for f_idx, fpath in enumerate(grp.files):
                is_original = (f_idx == 0)
                display_name = fpath.name + (f" [{t('duplicates.protected_original')}]" if is_original else "")
                child = QTreeWidgetItem(group_item, [display_name, format_bytes(grp.file_size), str(fpath.parent)])
                child.setData(0, Qt.UserRole, str(fpath))
                child.setData(0, Qt.UserRole + 1, is_original)

                if is_original:
                    child.setFlags(child.flags() & ~Qt.ItemIsUserCheckable)
                    child.setIcon(0, create_vector_icon("shield", color=COLOR_ACCENT, size=14))
                else:
                    child.setCheckState(0, Qt.Unchecked)
                    child.setIcon(0, create_vector_icon("file", color=COLOR_TEXT_MUTED, size=14))
        self.tree.blockSignals(False)
        self._update_delete_button_state()
        animate_refresh(self.tree)

    def _set_result_status(self, message: str):
        if self._pending_delete_summary:
            message = f"{self._pending_delete_summary} {message}"
            self._pending_delete_summary = ""
        self.status_label.setText(message)

    def _auto_select(self):
        self.tree.blockSignals(True)
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            grp_item = root.child(i)
            for j in range(grp_item.childCount()):
                child = grp_item.child(j)
                is_original = child.data(0, Qt.UserRole + 1)
                if not is_original:
                    child.setCheckState(0, Qt.Checked)
        self.tree.blockSignals(False)
        self._update_delete_button_state()

    def _on_tree_item_changed(self, item, column):
        self._update_delete_button_state()

    def _update_delete_button_state(self):
        checked_count = 0
        checked_size = 0
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            grp_item = root.child(i)
            for j in range(grp_item.childCount()):
                child = grp_item.child(j)
                if child.checkState(0) == Qt.Checked:
                    checked_count += 1
                    group_file_size = self.groups[i].file_size
                    checked_size += group_file_size
        self.selection_label.setText(
            t(
                "duplicates.selection_summary",
                count=checked_count,
                size=format_bytes(checked_size),
            )
        )
        self.btn_delete.setEnabled(checked_count > 0)

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

        size_by_path = {
            path: group.file_size
            for group in self.groups
            for path in group.files
        }
        approx_size = sum(size_by_path.get(path, 0) for path in selected_files)
        confirm = ConfirmDialog(
            title=t("duplicates.confirm_delete_title"),
            message=t("duplicates.confirm_delete_msg", count=len(selected_files), saving=format_bytes(approx_size)),
            is_danger=True,
            parent=self,
        )
        if confirm.exec_() == ConfirmDialog.Accepted:
            del_count, reclaimed, errors = self.finder.delete_selected(selected_files, protected_set)
            if errors:
                self._pending_delete_summary = (
                    t(
                        "duplicates.delete_result_with_errors",
                        deleted=del_count,
                        errors=len(errors),
                        detail=errors[0],
                    )
                )
            else:
                self._pending_delete_summary = (
                    t(
                        "duplicates.delete_result",
                        deleted=del_count,
                        saving=format_bytes(reclaimed),
                    )
                )
            self._start_scan()

    def refresh_translations(self):
        self.help_banner.refresh_translations()
        self.title_label.setText(t("duplicates.title"))
        self.subtitle_label.setText(t("duplicates.subtitle"))
        self.quick_scan_label.setText(t("duplicates.quick_scan"))
        self.btn_preset_desktop.setText(t("duplicates.preset_desktop"))
        self.btn_preset_downloads.setText(t("duplicates.preset_downloads"))
        self.btn_preset_documents.setText(t("duplicates.preset_documents"))
        self.btn_preset_pictures.setText(t("duplicates.preset_pictures"))
        self.safety_banner.setText(t("duplicates.safe_warning"))
        self.btn_browse.setText(t("duplicates.btn_browse"))
        self.btn_start.setText(t("duplicates.btn_start"))
        self.btn_cancel.setText(t("duplicates.btn_cancel"))
        self.btn_auto_select.setText(t("duplicates.btn_auto_select"))
        self.btn_delete.setText(t("duplicates.btn_delete_selected"))
        self.selection_label.setText(t("duplicates.selection_summary", count=0, size=format_bytes(0)))
        self.tree.setHeaderLabels([t("file_manager.col_name"), t("file_manager.col_size"), t("file_manager.properties_path")])
