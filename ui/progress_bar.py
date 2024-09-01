from PySide6.QtWidgets import QProgressBar

class ProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)

    def start(self):
        self.setRange(0, 0)  # Set to indeterminate mode

    def stop(self):
        self.setRange(0, 100)
        self.setValue(100)

    def set_progress(self, value):
        self.setValue(value)