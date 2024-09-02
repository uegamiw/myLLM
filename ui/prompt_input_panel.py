from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from ui.text_edit_with_zoom import TextEditWithZoom
from setting import deliminator

class PromptInputPanel(QWidget):
    prompt_entered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.textarea = TextEditWithZoom(self, placeholderText="Enter prompt here.")

        self.textarea.setStyleSheet("""
            QTextEdit {
                border: 1px solid gray;
                padding: 5px;
            }
            QTextEdit:focus {
                border: 2px solid blue;
            }
        """)
        layout.addWidget(self.textarea)

    def append_text(self, text:str, deliminator:str=deliminator):
        if deliminator is not None:
            self.textarea.append_text(f"{deliminator} \n {text} \n")
        else:
            self.textarea.append_text(f"{text} \n")

    def clear_text(self):
        self.textarea.clear()

    def set_disabled(self):
        self.textarea.setReadOnly(True)

    def get_text(self):
        return self.textarea.toPlainText()

    def set_text(self, text):
        self.textarea.clear()
        self.textarea.setPlainText(text)
