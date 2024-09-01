from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
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

        self.textbox = QLineEdit(
            self, placeholderText="Claude only. Enter the system (role) here."
        )
        layout.addWidget(self.textbox)

        self.textarea = TextEditWithZoom(self, placeholderText="Enter prompt here.")
        layout.addWidget(self.textarea)

    def append_text(self, text:str, deliminator:str=deliminator):
        if deliminator is not None:
            self.textarea.append_text(f"{deliminator} \n {text} \n")
        else:
            self.textarea.append_text(f"{text} \n")

    def clear_text(self):
        self.textbox.clear()
        self.textarea.clear()

    def set_disabled(self):
        self.textarea.setReadOnly(True)
        self.textbox.setDisabled(True)

    def get_text(self):
        return self.textbox.text(), self.textarea.toPlainText()
