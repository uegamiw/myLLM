from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from views.text_edit_with_zoom import TextEditWithZoom
from views.prompt_button_panel import PromptButtonsPanel
from utils.setting import deliminator, spacing

class PromptInputPanel(QWidget):
    prompt_entered = Signal(str)

    def __init__(self, prompts, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(spacing)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.prompts = prompts

        self.init_ui()

    def init_ui(self):

        # prompt buttons
        self.prompt_buttons_panel = PromptButtonsPanel(self.prompts, self)
        self.layout.addWidget(self.prompt_buttons_panel)

        # Input area
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
        self.layout.addWidget(self.textarea)

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

    def set_focus(self):
        self.textarea.setFocus()
        cursor = self.textarea.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.textarea.setTextCursor(cursor)
