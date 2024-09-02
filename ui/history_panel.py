from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, 
                               QScrollArea, QHeaderView, QHBoxLayout, QLineEdit)
from PySide6.QtCore import Signal, QTimer
from setting import n_history, search_delay
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtGui import QIcon

from PySide6.QtGui import QIcon, QCursor
from PySide6.QtWidgets import QLabel

from PySide6.QtCore import Qt

class CustomTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setItem(self, row, column, item):
        if item is not None:
            toolTipText = f"<span style='white-space:pre-wrap;'>{item.text()}</span>"
            item.setToolTip(toolTipText)
        super().setItem(row, column, item)

class HistoryPanel(QWidget):
    item_selected = Signal(dict)

    def __init__(self, db_manager, logger):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.db_manager = db_manager
        self.logger = logger

        # search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        # self.search_input.setContentsMargins(0, 0, 0, 0)
        self.search_input.setPlaceholderText("Search History (Ctrl+F)")
        self.search_input.textChanged.connect(self.on_search_input_changed)
        search_layout.addWidget(self.search_input)

        self.layout.addLayout(search_layout)

        # table
        self.table_widget = CustomTableWidget()
        self.table_widget.setSpan(0, 0, 0, 0)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(['Query', 'Response', 'Model', ''])
        self.table_widget.cellClicked.connect(self.on_item_clicked)
        
        # header
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # set the column width
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table_widget)
        
        self.layout.addWidget(scroll_area)

        self.populate_table_from_db()

        QShortcut(QKeySequence("Ctrl+f"), self).activated.connect(self.search_input.setFocus)

        # search timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

        self.search_input.textChanged.connect(self.on_search_input_changed)


    def populate_table_with_results(self, items):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(len(items))
        for row, item in enumerate(items):
            self.add_item_to_table(row, item)

    def populate_table_from_db(self):
        items = self.db_manager.get_n_history(n_history)
        self.table_widget.setRowCount(len(items))
        for row, item in enumerate(items):
            self.add_item_to_table(row, item)

    def add_item_to_table(self, row, item):
        self.table_widget.setItem(row, 0, QTableWidgetItem(item['query']))
        self.table_widget.setItem(row, 1, QTableWidgetItem(item['response']))
        self.table_widget.setItem(row, 2, QTableWidgetItem(item['model']))

        delete_label = QLabel()
        delete_label.setPixmap(QIcon.fromTheme('edit-delete').pixmap(16, 16))
        delete_label.setCursor(QCursor(Qt.PointingHandCursor))
        delete_label.mousePressEvent = lambda event: self.on_delete_label_clicked(item['id'])
        self.table_widget.setCellWidget(row, 3, delete_label)

    def on_item_clicked(self, row, column):
        query = self.table_widget.item(row, 0).text()
        response = self.table_widget.item(row, 1).text()
        model = self.table_widget.item(row, 2).text()

        item = {
            "query": query,
            "response": response,
            "model": model,
        }
        self.item_selected.emit(item)

    def on_delete_label_clicked(self, item_id):
        self.db_manager.delete_history(item_id)
        self.perform_search()

    def refresh_table(self):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.populate_table_from_db()

    def on_search_input_changed(self):
        self.search_timer.start(search_delay)

    def perform_search(self):
        search_text = self.search_input.text()
        self.logger.debug(f"perform_search, search_text: {search_text}")
        if search_text:
            search_results = self.db_manager.search(search_text)
            self.populate_table_with_results(search_results)
        else:
            self.populate_table_from_db()