"""Comprehensive, full-featured file manager page."""

import os
from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QAction, QCursor, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.file_manager_service import FileManagerService, FileItem
from core.localization import format_bytes, t
from core.system_monitor import SystemMonitor
from ui.components.dialogs import ConfirmDialog, ConflictDialog, PromptDialog, PropertiesDialog
from ui.icons import create_vector_icon
from ui.theme import (
    COLOR_ACCENT,
    COLOR_BG_PRIMARY,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_DANGER,
    COLOR_INPUT_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
)


class FileManagerPage(QWidget):
    """Modern file manager with navigation, category filters, and safe operations."""

    def __init__(self, service: FileManagerService, monitor: SystemMonitor, parent: QWidget = None):
        super().__init__(parent)
        self.service = service
        self.monitor = monitor

        self.current_path: Path = Path.home()
        self.history_stack: List[Path] = [self.current_path]
        self.history_index: int = 0
        self.current_items: List[FileItem] = []
        self.clipboard_paths: List[Path] = []
        self.clipboard_action: str = ""  # "copy" or "move"

        self.current_category = "all"
        self.current_sort_by = "name"
        self.current_sort_asc = True

        self._build_ui()
        self._load_sidebar_drives()
        self.navigate_to(self.current_path)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(12)

        # 1. Navigation & Path Toolbar
        nav_toolbar = QHBoxLayout()
        nav_toolbar.setSpacing(8)

        self.btn_back = QPushButton()
        self.btn_back.setIcon(create_vector_icon("back", color=COLOR_ACCENT, size=18))
        self.btn_back.setToolTip(t("file_manager.btn_back"))
        self.btn_back.clicked.connect(self._on_back)
        nav_toolbar.addWidget(self.btn_back)

        self.btn_forward = QPushButton()
        self.btn_forward.setIcon(create_vector_icon("forward", color=COLOR_ACCENT, size=18))
        self.btn_forward.setToolTip(t("file_manager.btn_forward"))
        self.btn_forward.clicked.connect(self._on_forward)
        nav_toolbar.addWidget(self.btn_forward)

        self.btn_up = QPushButton()
        self.btn_up.setIcon(create_vector_icon("up", color=COLOR_ACCENT, size=18))
        self.btn_up.setToolTip(t("file_manager.btn_up"))
        self.btn_up.clicked.connect(self._on_up)
        nav_toolbar.addWidget(self.btn_up)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setIcon(create_vector_icon("refresh", color=COLOR_ACCENT, size=18))
        self.btn_refresh.setToolTip(t("file_manager.btn_refresh"))
        self.btn_refresh.clicked.connect(self.refresh_current_folder)
        nav_toolbar.addWidget(self.btn_refresh)

        # Path input box
        self.path_edit = QLineEdit(str(self.current_path))
        self.path_edit.returnPressed.connect(self._on_path_entered)
        nav_toolbar.addWidget(self.path_edit, stretch=1)

        # Search bar
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(t("file_manager.search_placeholder"))
        self.search_edit.setFixedWidth(200)
        self.search_edit.textChanged.connect(self._on_search_changed)
        nav_toolbar.addWidget(self.search_edit)

        main_layout.addLayout(nav_toolbar)

        # 2. Action Toolbar: New Folder, Delete, Sort combo, Category filter
        action_bar = QHBoxLayout()
        action_bar.setSpacing(10)

        self.btn_new_folder = QPushButton(t("file_manager.btn_new_folder"))
        self.btn_new_folder.setIcon(create_vector_icon("plus", color=COLOR_ACCENT, size=16))
        self.btn_new_folder.clicked.connect(self._on_new_folder)
        action_bar.addWidget(self.btn_new_folder)

        self.btn_delete = QPushButton(t("file_manager.btn_delete"))
        self.btn_delete.setIcon(create_vector_icon("trash", color=COLOR_DANGER, size=16))
        self.btn_delete.setProperty("class", "danger_btn")
        self.btn_delete.clicked.connect(self._on_delete_selected)
        action_bar.addWidget(self.btn_delete)

        action_bar.addStretch()

        # Category Filter Dropdown
        cat_label = QLabel(t("file_manager.categories") + ":")
        cat_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        action_bar.addWidget(cat_label)

        self.cat_combo = QComboBox()
        self.cat_combo.addItems([
            t("file_manager.cat_all"),
            t("file_manager.cat_photos"),
            t("file_manager.cat_videos"),
            t("file_manager.cat_audio"),
            t("file_manager.cat_documents"),
            t("file_manager.cat_archives"),
            t("file_manager.cat_large"),
            t("file_manager.cat_recent"),
        ])
        self.cat_combo.currentIndexChanged.connect(self._on_category_changed)
        action_bar.addWidget(self.cat_combo)

        # Sort Order Dropdown
        sort_label = QLabel(t("file_manager.sort_by") + ":")
        sort_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        action_bar.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            t("file_manager.sort_name"),
            t("file_manager.sort_size"),
            t("file_manager.sort_date"),
            t("file_manager.sort_type"),
        ])
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        action_bar.addWidget(self.sort_combo)

        main_layout.addLayout(action_bar)

        # 3. Main Content Splitter: Sidebar (Drives + Quick Folders) & File Table
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #354A40; width: 2px; }")

        # Left Sidebar (Tree)
        self.sidebar_tree = QTreeWidget()
        self.sidebar_tree.setHeaderHidden(True)
        self.sidebar_tree.setFixedWidth(200)
        self.sidebar_tree.itemClicked.connect(self._on_sidebar_item_clicked)
        splitter.addWidget(self.sidebar_tree)

        # Right File Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            t("file_manager.col_name"),
            t("file_manager.col_type"),
            t("file_manager.col_size"),
            t("file_manager.col_date"),
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        splitter.addWidget(self.table)
        splitter.setStretchFactor(1, 4)
        main_layout.addWidget(splitter, stretch=1)

        # 4. Status Bar
        self.status_bar = QHBoxLayout()
        self.status_count_label = QLabel(t("file_manager.items_count", count=0))
        self.status_count_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        self.status_bar.addWidget(self.status_count_label)

        self.status_selected_label = QLabel("")
        self.status_selected_label.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 12px;")
        self.status_bar.addWidget(self.status_selected_label)

        self.status_bar.addStretch()
        main_layout.addLayout(self.status_bar)

    def _load_sidebar_drives(self):
        """Populates quick access shortcuts and system drives in sidebar."""
        self.sidebar_tree.clear()

        # Quick Access Group
        quick_group = QTreeWidgetItem([t("file_manager.quick_access")])
        quick_group.setFlags(quick_group.flags() & ~Qt.ItemIsSelectable)
        self.sidebar_tree.addTopLevelItem(quick_group)

        user_home = Path.home()
        shortcuts = [
            ("Desktop", user_home / "Desktop", "monitor"),
            ("Downloads", user_home / "Downloads", "folder"),
            ("Documents", user_home / "Documents", "file"),
            ("Pictures", user_home / "Pictures", "folder"),
            ("Videos", user_home / "Videos", "folder"),
            ("Music", user_home / "Music", "folder"),
        ]

        for name, p, icon_type in shortcuts:
            if p.exists():
                item = QTreeWidgetItem([name])
                item.setData(0, Qt.UserRole, str(p))
                item.setIcon(0, create_vector_icon(icon_type, color=COLOR_ACCENT, size=16))
                quick_group.addChild(item)

        # Drives Group
        drives_group = QTreeWidgetItem([t("file_manager.drives")])
        drives_group.setFlags(drives_group.flags() & ~Qt.ItemIsSelectable)
        self.sidebar_tree.addTopLevelItem(drives_group)

        drives = self.monitor.get_all_disks()
        for d in drives:
            mount = d["mountpoint"]
            label = f"{mount} ({format_bytes(d['free'])} free)"
            d_item = QTreeWidgetItem([label])
            d_item.setData(0, Qt.UserRole, mount)
            d_item.setIcon(0, create_vector_icon("storage", color=COLOR_ACCENT, size=16))
            drives_group.addChild(d_item)

        quick_group.setExpanded(True)
        drives_group.setExpanded(True)

    def navigate_to(self, target_path: Path, add_to_history: bool = True):
        """Navigates to a specific directory safely and renders entries."""
        try:
            target_path = Path(target_path).resolve()
        except Exception:
            return

        if not target_path.exists() or not target_path.is_dir():
            return

        self.current_path = target_path
        self.path_edit.setText(str(self.current_path))

        if add_to_history:
            if self.history_index < len(self.history_stack) - 1:
                self.history_stack = self.history_stack[:self.history_index + 1]
            self.history_stack.append(self.current_path)
            self.history_index = len(self.history_stack) - 1

        self.btn_back.setEnabled(self.history_index > 0)
        self.btn_forward.setEnabled(self.history_index < len(self.history_stack) - 1)

        self.refresh_current_folder()

    def refresh_current_folder(self):
        """Fetches and displays directory items matching active filter & sort."""
        query = self.search_edit.text().strip()
        items = self.service.list_directory(
            folder_path=self.current_path,
            search_query=query,
            sort_by=self.current_sort_by,
            sort_asc=self.current_sort_asc,
            category_filter=self.current_category,
        )
        self.current_items = items
        self._populate_table(items)

    def _populate_table(self, items: List[FileItem]):
        self.table.setRowCount(0)
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            # Name with icon
            icon_name = "folder" if item.is_dir else "file"
            icon = create_vector_icon(icon_name, color=COLOR_ACCENT if item.is_dir else COLOR_TEXT_MUTED, size=18)

            name_item = QTableWidgetItem(item.name)
            name_item.setIcon(icon)
            name_item.setData(Qt.UserRole, item)

            type_desc = t("file_manager.folder") if item.is_dir else (item.ext.upper()[1:] if item.ext else t("file_manager.file"))
            type_item = QTableWidgetItem(type_desc)
            type_item.setTextAlignment(Qt.AlignCenter)

            size_desc = "-" if item.is_dir else format_bytes(item.size)
            size_item = QTableWidgetItem(size_desc)
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            import datetime
            date_desc = datetime.datetime.fromtimestamp(item.modified).strftime("%Y-%m-%d %H:%M") if item.modified else "-"
            date_item = QTableWidgetItem(date_desc)
            date_item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, type_item)
            self.table.setItem(row, 2, size_item)
            self.table.setItem(row, 3, date_item)

        self.status_count_label.setText(t("file_manager.items_count", count=len(items)))
        self.status_selected_label.setText("")

    def _on_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.navigate_to(self.history_stack[self.history_index], add_to_history=False)

    def _on_forward(self):
        if self.history_index < len(self.history_stack) - 1:
            self.history_index += 1
            self.navigate_to(self.history_stack[self.history_index], add_to_history=False)

    def _on_up(self):
        parent = self.current_path.parent
        if parent != self.current_path:
            self.navigate_to(parent)

    def _on_path_entered(self):
        target = Path(self.path_edit.text().strip())
        if target.exists() and target.is_dir():
            self.navigate_to(target)
        else:
            self.path_edit.setText(str(self.current_path))

    def _on_sidebar_item_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.UserRole)
        if data:
            self.navigate_to(Path(data))

    def _on_item_double_clicked(self, table_item: QTableWidgetItem):
        row = table_item.row()
        name_cell = self.table.item(row, 0)
        file_item: FileItem = name_cell.data(Qt.UserRole)
        if not file_item:
            return

        if file_item.is_dir:
            self.navigate_to(file_item.path)
        else:
            self.service.open_with_default_app(file_item.path)

    def _on_selection_changed(self):
        selected_rows = len(self.table.selectionModel().selectedRows())
        if selected_rows > 0:
            self.status_selected_label.setText(t("file_manager.selected_count", count=selected_rows))
        else:
            self.status_selected_label.setText("")

    def _on_search_changed(self, text: str):
        self.refresh_current_folder()

    def _on_category_changed(self, index: int):
        cat_map = {
            0: "all",
            1: "photos",
            2: "videos",
            3: "audio",
            4: "documents",
            5: "archives",
            6: "large",
            7: "recent",
        }
        self.current_category = cat_map.get(index, "all")
        self.refresh_current_folder()

    def _on_sort_changed(self, index: int):
        sort_map = {0: "name", 1: "size", 2: "date", 3: "type"}
        self.current_sort_by = sort_map.get(index, "name")
        self.refresh_current_folder()

    def _get_selected_items(self) -> List[FileItem]:
        selected_rows = self.table.selectionModel().selectedRows()
        items = []
        for index in selected_rows:
            cell = self.table.item(index.row(), 0)
            if cell:
                file_item = cell.data(Qt.UserRole)
                if file_item:
                    items.append(file_item)
        return items

    def _show_context_menu(self, pos):
        selected_items = self._get_selected_items()
        menu = QMenu(self)
        menu.setStyleSheet(
            f"""
            QMenu {{
                background-color: {COLOR_CARD_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 16px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: rgba(199, 243, 107, 0.2);
                color: {COLOR_ACCENT};
            }}
            """
        )

        if selected_items:
            first = selected_items[0]
            action_open = menu.addAction(t("file_manager.btn_open"))
            action_open.triggered.connect(lambda: self._on_item_double_clicked(self.table.item(self.table.currentRow(), 0)))

            action_explorer = menu.addAction(t("file_manager.btn_open_explorer"))
            action_explorer.triggered.connect(lambda: self.service.open_in_explorer(first.path))

            menu.addSeparator()

            action_copy = menu.addAction(t("file_manager.btn_copy"))
            action_copy.triggered.connect(self._copy_selected)

            action_rename = menu.addAction(t("file_manager.btn_rename"))
            action_rename.triggered.connect(self._rename_selected)

            action_copy_path = menu.addAction(t("file_manager.btn_copy_path"))
            action_copy_path.triggered.connect(lambda: self._copy_path_to_clipboard(first.path))

            menu.addSeparator()

            action_delete = menu.addAction(t("file_manager.btn_delete"))
            action_delete.triggered.connect(self._on_delete_selected)

            action_props = menu.addAction(t("file_manager.btn_properties"))
            action_props.triggered.connect(self._show_properties)

        else:
            action_new_folder = menu.addAction(t("file_manager.btn_new_folder"))
            action_new_folder.triggered.connect(self._on_new_folder)

            action_refresh = menu.addAction(t("file_manager.btn_refresh"))
            action_refresh.triggered.connect(self.refresh_current_folder)

        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def _copy_path_to_clipboard(self, path: Path):
        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(str(path.resolve()))

    def _copy_selected(self):
        items = self._get_selected_items()
        if items:
            self.clipboard_paths = [it.path for it in items]
            self.clipboard_action = "copy"

    def _on_new_folder(self):
        dialog = PromptDialog(
            title=t("file_manager.new_folder_dialog_title"),
            prompt_text=t("file_manager.new_folder_prompt"),
            default_value=t("file_manager.new_folder_default"),
            parent=self,
        )
        if dialog.exec_() == PromptDialog.Accepted:
            name = dialog.get_text()
            if name:
                success, msg = self.service.create_folder(self.current_path, name)
                if success:
                    self.refresh_current_folder()

    def _rename_selected(self):
        items = self._get_selected_items()
        if not items:
            return
        target = items[0]
        dialog = PromptDialog(
            title=t("file_manager.rename_dialog_title"),
            prompt_text=t("file_manager.rename_prompt"),
            default_value=target.name,
            parent=self,
        )
        if dialog.exec_() == PromptDialog.Accepted:
            new_name = dialog.get_text()
            if new_name and new_name != target.name:
                success, msg = self.service.rename_item(target.path, new_name)
                if success:
                    self.refresh_current_folder()

    def _on_delete_selected(self):
        items = self._get_selected_items()
        if not items:
            return
        confirm = ConfirmDialog(
            title=t("file_manager.delete_confirm_title"),
            message=t("file_manager.delete_confirm_msg", count=len(items)),
            is_danger=True,
            parent=self,
        )
        if confirm.exec_() == ConfirmDialog.Accepted:
            paths = [it.path for it in items]
            self.service.delete_to_trash(paths)
            self.refresh_current_folder()

    def _show_properties(self):
        items = self._get_selected_items()
        if not items:
            return
        props = self.service.get_properties(items[0].path)
        dlg = PropertiesDialog(props, parent=self)
        dlg.exec_()

    def refresh_translations(self):
        self.table.setHorizontalHeaderLabels([
            t("file_manager.col_name"),
            t("file_manager.col_type"),
            t("file_manager.col_size"),
            t("file_manager.col_date"),
        ])
        self.btn_new_folder.setText(t("file_manager.btn_new_folder"))
        self.btn_delete.setText(t("file_manager.btn_delete"))
        self._load_sidebar_drives()
        self.refresh_current_folder()
