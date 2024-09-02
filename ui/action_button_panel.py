from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon

class ActionButtonsPanel(QWidget):
    send_signal = Signal()
    append_signal = Signal()


    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.send_button = QPushButton()
        send_icon = QIcon.fromTheme("mail-send")
        self.send_button.setIcon(send_icon)
        self.send_button.setText("Send (Ctrl+Return)")
        self.send_button.clicked.connect(self.send_signal.emit)
        self.layout.addWidget(self.send_button)

        # self.append_button = QPushButton("↑")
        # self.append_button.clicked.connect(self.append_signal.emit)
        # self.layout.addWidget(self.append_button)

        self.append_button = QPushButton()
        append_icon = QIcon.fromTheme("list-add")  # または "arrow-up" を試しても良い
        self.append_button.setIcon(append_icon)
        self.append_button.setText("Append (Alt+Return)")  # テキストを設定
        # self.append_button.setIconSize(QSize(16, 16))  # アイコンのサイズを設定
        self.append_button.clicked.connect(self.append_signal.emit)
        self.layout.addWidget(self.append_button)

    def disable_buttons(self):
        self.send_button.setEnabled(False)
        self.append_button.setEnabled(False)

    def enable_buttons(self):
        self.send_button.setEnabled(True)
        self.append_button.setEnabled(True)