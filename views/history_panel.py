from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QScrollArea, QHeaderView, QHBoxLayout, QLineEdit)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QCursor
from PySide6.QtWidgets import QLabel, QTableWidget, QHeaderView
from utils.setting import history_table_height, temp_deliminator
import datetime
from models.llm_client_worker import LLMResults

class CustomTableWidget(QTableWidget):
    item_selected = Signal(dict)

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

        # table should not be editable on double click
        self.setEditTriggers(QTableWidget.NoEditTriggers)

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
    # item_selected = Signal(dict)

    def __init__(self, db_manager, logger):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.db_manager = db_manager
        self.logger = logger

        # search
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        # self.search_input.setContentsMargins(0, 0, 0, 0)
        self.search_box.setPlaceholderText("Search History (Ctrl+F)")
        search_layout.addWidget(self.search_box)

        self.layout.addLayout(search_layout)

        # table
        self.table_widget = CustomTableWidget()
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(['Query', 'Response', 'Model', ''])
        
        # header
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # set the column width
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table_widget)
        
        self.layout.addWidget(scroll_area)


    def set_one_row_to_table(self, row:int, item:LLMResults):
        date_time = item.datetime.split('.')[0]
        date_time = datetime.datetime.fromisoformat(date_time)

        if date_time.date() == datetime.date.today():
            date_str = date_time.strftime("%H:%M")
        elif date_time.date() == datetime.date.today() - datetime.timedelta(days=1):
            date_str = "Yesterday"
        elif date_time.year == datetime.date.today().year:
            date_str = date_time.strftime("%m/%d")
        else:
            date_str = date_time.strftime("%Y/%m/%d")

        if item.temperature is None:
            datetime_model = item.model + "\n" + date_str
        else:
            datetime_model = item.model + f"{temp_deliminator}{str(item.temperature)}\n" + date_str

        # datetime_model = item.model + "\n" + date_str
        self.table_widget.setItem(row, 0, QTableWidgetItem(item.prompt))
        self.table_widget.setItem(row, 1, QTableWidgetItem(item.response))
        self.table_widget.setItem(row, 2, QTableWidgetItem(datetime_model))

        delete_label = QLabel()
        delete_label.setPixmap(QIcon.fromTheme('edit-delete').pixmap(16, 16))
        delete_label.setCursor(QCursor(Qt.PointingHandCursor))
        # delete_label.mousePressEvent = lambda event: self.on_delete_label_clicked(item.id)
        self.table_widget.setCellWidget(row, 3, delete_label)
