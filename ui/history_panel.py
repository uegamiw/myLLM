from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QScrollArea, QHeaderView, QHBoxLayout, QLineEdit)
from PySide6.QtCore import Signal, QTimer, Qt
from setting import n_history, search_delay
from PySide6.QtGui import QShortcut, QKeySequence, QIcon, QCursor
from PySide6.QtWidgets import QLabel, QTableWidget, QHeaderView
from setting import history_table_height
import datetime

class CustomTableWidget(QTableWidget):
    item_selected = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set row height
        self.verticalHeader().setDefaultSectionSize(history_table_height * 20)

        # Style the table
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid;
            }
            QHeaderView::section {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #3a3a3a;
            }
        """)

        # Set header properties
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setHighlightSections(False)
        self.verticalHeader().setVisible(False)

        # Set selection behavior
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)

        # Enable sorting
        # self.setSortingEnabled(True)

    def setItem(self, row, column, item):
        if item is not None:
            toolTipText = f"<span style='white-space:pre-wrap;'>{item.text()}</span>"
            item.setToolTip(toolTipText)
            
            # Set a custom font
            font = item.font()
            font.setPointSize(10)
            item.setFont(font)
            
        super().setItem(row, column, item)

    def resizeEvent(self, event):
        # Adjust column widths when the table is resized
        width = self.viewport().width()
        for column in range(self.columnCount()):
            self.setColumnWidth(column, width / self.columnCount())
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down:
            current_row = self.currentRow()
            if event.key() == Qt.Key_Up and current_row > 0:
                self.setCurrentCell(current_row - 1, 0)
            elif event.key() == Qt.Key_Down and current_row < self.rowCount() - 1:
                self.setCurrentCell(current_row + 1, 0)
            
            self.item_selected.emit(self.currentRow())
            event.accept()
        else:
            super().keyPressEvent(event)

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
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(['Query', 'Response', 'Model', ''])
        self.table_widget.cellClicked.connect(self.on_item_clicked)
        self.table_widget.item_selected.connect(self.on_item_selected)
        
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

        # set focus to the table
        QShortcut(QKeySequence("Ctrl+d"), self).activated.connect(lambda: self.table_widget.setFocus())

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
        date_time = datetime.datetime.fromisoformat(item['datetime'].split('.')[0])

        if date_time.date() == datetime.date.today():
            date_str = date_time.strftime("%H:%M")
        elif date_time.date() == datetime.date.today() - datetime.timedelta(days=1):
            date_str = "Yesterday"
        elif date_time.year == datetime.date.today().year:
            date_str = date_time.strftime("%m/%d")
        else:
            date_str = date_time.strftime("%Y/%m/%d")

        datetime_model = item['model'] + "\n" + date_str
        self.table_widget.setItem(row, 0, QTableWidgetItem(item['query']))
        self.table_widget.setItem(row, 1, QTableWidgetItem(item['response']))
        self.table_widget.setItem(row, 2, QTableWidgetItem(datetime_model))

        delete_label = QLabel()
        delete_label.setPixmap(QIcon.fromTheme('edit-delete').pixmap(16, 16))
        delete_label.setCursor(QCursor(Qt.PointingHandCursor))
        delete_label.mousePressEvent = lambda event: self.on_delete_label_clicked(item['id'])
        self.table_widget.setCellWidget(row, 3, delete_label)

    def on_item_clicked(self, row, column):
        query = self.table_widget.item(row, 0).text()
        response = self.table_widget.item(row, 1).text()
        model_datetime = self.table_widget.item(row, 2).text()
        model = model_datetime.split('\n')[0]

        item = {
            "query": query,
            "response": response,
            "model": model,
        }
        self.item_selected.emit(item)

    def on_item_selected(self, row):
        self.on_item_clicked(row, 0)

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
