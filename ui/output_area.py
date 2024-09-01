from ui.text_edit_with_zoom import ResizableTextEdit

class OutputArea(ResizableTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText("Output will appear here.")
        self.text_edit.setAcceptRichText(False)

    def clear(self):
        self.text_edit.setPlainText("")

    def set_text(self, text):
        self.text_edit.clear()
        self.text_edit.append_text(text)
    