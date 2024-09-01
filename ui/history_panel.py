from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, 
                               QScrollArea, QHeaderView)
from PySide6.QtCore import Signal
from setting import n_history

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

        self.table_widget = CustomTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['ID', 'Query', 'Response', 'Model', 'Del'])
        self.table_widget.cellClicked.connect(self.on_item_clicked)
        
        # header
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # set the column width
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table_widget)
        
        self.layout.addWidget(scroll_area)

        self.populate_table_from_db()

    def populate_table_from_db(self):
        items = self.db_manager.get_n_history(n_history)
        self.table_widget.setRowCount(len(items))
        for row, item in enumerate(items):
            self.add_item_to_table(row, item)

    def add_item_to_table(self, row, item):
        self.table_widget.setItem(row, 0, QTableWidgetItem(str(item['id'])))
        self.table_widget.setItem(row, 1, QTableWidgetItem(item['query']))
        self.table_widget.setItem(row, 2, QTableWidgetItem(item['response']))
        self.table_widget.setItem(row, 3, QTableWidgetItem(item['model']))

        delete_button = QPushButton('x')
        delete_button.clicked.connect(lambda _, item_id=item['id']: self.on_delete_button_clicked(item_id))
        self.table_widget.setCellWidget(row, 4, delete_button)

    def on_item_clicked(self, row, column):
        item_id = int(self.table_widget.item(row, 0).text())
        item = self.db_manager.get_selected_history(item_id)
        self.item_selected.emit(item)

    def on_delete_button_clicked(self, item_id):
        self.db_manager.delete_history(item_id)
        self.refresh_table()

    def refresh_table(self):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.populate_table_from_db()