from PySide6.QtWidgets import QHBoxLayout, QPushButton
from PySide6.QtCore import Signal

class ActionButtonsPanel(QHBoxLayout):
    send_signal = Signal()
    append_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_signal.emit)
        self.addWidget(self.send_button)

        self.append_button = QPushButton("↑")
        self.append_button.clicked.connect(self.append_signal.emit)
        self.addWidget(self.append_button)

    def disable_buttons(self):
        self.send_button.setEnabled(False)
        self.append_button.setEnabled(False)

    def enable_buttons(self):
        self.send_button.setEnabled(True)
        self.append_button.setEnabled(True)