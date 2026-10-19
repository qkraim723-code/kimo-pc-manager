"""Storage analyzer page with deep space scanning and visualization."""

from pathlib import Path
from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.localization import format_bytes, t
from core.storage_analyzer import StorageAnalyzer, StorageScanResult
from core.system_monitor import SystemMonitor
from ui.icons import create_vector_icon
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BG_PRIMARY,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_DANGER,
    COLOR_INPUT_BG,
    COLOR_PROGRESS_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
)


class StorageScanWorker(QObject):
    """Background worker for deep directory scanning."""

    finished = Signal(object)
    progress = Signal(int, str, int)  # files_count, current_path, total_size

    def __init__(self, analyzer: StorageAnalyzer, target_path: Path):
        super().__init__()
        self.analyzer = analyzer
        self.target_path = target_path

    def run(self):
        def on_progress(files, current_p, total_sz):
            self.progress.emit(files, current_p, total_sz)

        result = self.analyzer.scan(self.target_path, progress_callback=on_progress)
        self.finished.emit(result)


class StoragePage(QWidget):
    """Storage space analysis interface."""

    def __init__(self, monitor: SystemMonitor, parent: QWidget = None):
        super().__init__(parent)
        self.monitor = monitor
        self.analyzer = StorageAnalyzer()
        self.thread: QThread = None
        self.worker: StorageScanWorker = None

        self._build_ui()
        self._populate_drives()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header Title & Subtitle
        header = QVBoxLayout()
        header.setSpacing(4)
        self.title_label = QLabel(t("storage.title"))
        self.title_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        header.addWidget(self.title_label)

        self.subtitle_label = QLabel(t("storage.subtitle"))
        self.subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        header.addWidget(self.subtitle_label)
        main_layout.addLayout(header)

        # Control Bar: Target Selector + Browse + Start/Cancel
        ctrl_frame = QFrame()
        ctrl_frame.setProperty("class", "card_frame")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setContentsMargins(16, 12, 16, 12)
        ctrl_layout.setSpacing(12)

        lbl = QLabel(t("storage.select_target"))
        lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: 500;")
        ctrl_layout.addWidget(lbl)

        self.target_combo = QComboBox()
        self.target_combo.setMinimumWidth(220)
        ctrl_layout.addWidget(self.target_combo)

        self.btn_browse = QPushButton(t("storage.btn_browse_folder"))
        self.btn_browse.setIcon(create_vector_icon("folder", color=COLOR_ACCENT, size=16))
        self.btn_browse.clicked.connect(self._on_browse_folder)
        ctrl_layout.addWidget(self.btn_browse)

        ctrl_layout.addStretch()

        self.btn_scan = QPushButton(t("storage.btn_start_scan"))
        self.btn_scan.setIcon(create_vector_icon("search", color="#122019", size=16))
        self.btn_scan.setProperty("class", "accent_btn")
        self.btn_scan.clicked.connect(self._start_scan)
        ctrl_layout.addWidget(self.btn_scan)

        self.btn_cancel = QPushButton(t("storage.btn_cancel_scan"))
        self.btn_cancel.setIcon(create_vector_icon("trash", color=COLOR_DANGER, size=16))
        self.btn_cancel.setProperty("class", "danger_btn")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_scan)
        ctrl_layout.addWidget(self.btn_cancel)

        main_layout.addWidget(ctrl_frame)

        # Progress / Status Frame
        self.progress_frame = QFrame()
        self.progress_frame.setProperty("class", "card_frame")
        p_layout = QVBoxLayout(self.progress_frame)
        p_layout.setContentsMargins(16, 12, 16, 12)
        p_layout.setSpacing(8)

        self.status_label = QLabel(t("storage.no_scan_yet"))
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        p_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate while scanning
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setVisible(False)
        p_layout.addWidget(self.progress_bar)

        main_layout.addWidget(self.progress_frame)

        # Splitter: Left (Top Folders) & Right (Largest Files)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #354A40; width: 2px; }")

        # Top Folders Section
        folders_box = QWidget()
        f_layout = QVBoxLayout(folders_box)
        f_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_top_folders = QLabel(t("storage.top_folders"))
        self.lbl_top_folders.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        f_layout.addWidget(self.lbl_top_folders)

        self.table_folders = QTableWidget()
        self.table_folders.setColumnCount(3)
        self.table_folders.setHorizontalHeaderLabels([
            t("storage.col_folder"),
            t("storage.col_percent"),
            t("storage.col_size"),
        ])
        self.table_folders.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_folders.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_folders.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_folders.verticalHeader().setVisible(False)
        self.table_folders.setSelectionBehavior(QTableWidget.SelectRows)
        f_layout.addWidget(self.table_folders)
        splitter.addWidget(folders_box)

        # Top Files Section
        files_box = QWidget()
        files_layout = QVBoxLayout(files_box)
        files_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_top_files = QLabel(t("storage.top_files"))
        self.lbl_top_files.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        files_layout.addWidget(self.lbl_top_files)

        self.table_files = QTableWidget()
        self.table_files.setColumnCount(3)
        self.table_files.setHorizontalHeaderLabels([
            t("storage.col_file"),
            t("storage.col_path"),
            t("storage.col_size"),
        ])
        self.table_files.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_files.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_files.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_files.verticalHeader().setVisible(False)
        self.table_files.setSelectionBehavior(QTableWidget.SelectRows)
        files_layout.addWidget(self.table_files)
        splitter.addWidget(files_box)

        main_layout.addWidget(splitter, stretch=1)

    def _populate_drives(self):
        self.target_combo.clear()
        drives = self.monitor.get_all_disks()
        for d in drives:
            mount = d["mountpoint"]
            self.target_combo.addItem(f"{mount} ({format_bytes(d['total'])})", mount)

    def _on_browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, t("storage.btn_browse_folder"), str(Path.home()))
        if folder:
            self.target_combo.addItem(folder, folder)
            self.target_combo.setCurrentIndex(self.target_combo.count() - 1)

    def _start_scan(self):
        target_path_str = self.target_combo.currentData()
        if not target_path_str:
            return

        target_path = Path(target_path_str)
        self.btn_scan.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.status_label.setText(t("storage.scanning_status", path=str(target_path)))

        self.table_folders.setRowCount(0)
        self.table_files.setRowCount(0)

        self.thread = QThread()
        self.worker = StorageScanWorker(self.analyzer, target_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_scan_progress)
        self.worker.finished.connect(self._on_scan_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def _on_scan_progress(self, files_count: int, current_path: str, total_sz: int):
        self.status_label.setText(f"{t('storage.scanning_status', path=current_path)} ({format_bytes(total_sz)})")

    def _cancel_scan(self):
        self.analyzer.cancel()
        self.btn_cancel.setEnabled(False)

    def _on_scan_finished(self, result: StorageScanResult):
        self.btn_scan.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(False)

        if not result.is_completed:
            self.status_label.setText(t("storage.scan_cancelled"))
        else:
            self.status_label.setText(
                t("storage.scan_completed", count=result.total_files, size=format_bytes(result.total_size))
            )

        # Populate top folders
        sorted_folders = sorted(result.subfolder_sizes.items(), key=lambda x: x[1], reverse=True)[:25]
        self.table_folders.setRowCount(len(sorted_folders))
        for row, (fname, fsize) in enumerate(sorted_folders):
            pct = (fsize / result.total_size * 100.0) if result.total_size > 0 else 0.0

            item_name = QTableWidgetItem(fname)
            item_name.setIcon(create_vector_icon("folder", color=COLOR_ACCENT, size=16))

            item_pct = QTableWidgetItem(f"{pct:.1f}%")
            item_pct.setTextAlignment(Qt.AlignCenter)

            item_size = QTableWidgetItem(format_bytes(fsize))
            item_size.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.table_folders.setItem(row, 0, item_name)
            self.table_folders.setItem(row, 1, item_pct)
            self.table_folders.setItem(row, 2, item_size)

        # Populate largest files
        self.table_files.setRowCount(len(result.largest_files))
        for row, file_info in enumerate(result.largest_files):
            f_name = QTableWidgetItem(file_info["name"])
            f_name.setIcon(create_vector_icon("file", color=COLOR_TEXT_MUTED, size=16))

            f_path = QTableWidgetItem(file_info["path"])

            f_size = QTableWidgetItem(format_bytes(file_info["size"]))
            f_size.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.table_files.setItem(row, 0, f_name)
            self.table_files.setItem(row, 1, f_path)
            self.table_files.setItem(row, 2, f_size)

    def refresh_translations(self):
        self.title_label.setText(t("storage.title"))
        self.subtitle_label.setText(t("storage.subtitle"))
        self.btn_browse.setText(t("storage.btn_browse_folder"))
        self.btn_scan.setText(t("storage.btn_start_scan"))
        self.btn_cancel.setText(t("storage.btn_cancel_scan"))
        self.lbl_top_folders.setText(t("storage.top_folders"))
        self.lbl_top_files.setText(t("storage.top_files"))
        self.table_folders.setHorizontalHeaderLabels([
            t("storage.col_folder"),
            t("storage.col_percent"),
            t("storage.col_size"),
        ])
        self.table_files.setHorizontalHeaderLabels([
            t("storage.col_file"),
            t("storage.col_path"),
            t("storage.col_size"),
        ])
        self._populate_drives()
