from views.text_edit_with_zoom import ResizableTextEdit

class OutputArea(ResizableTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText("Output will appear here.")
        self.text_edit.setAcceptRichText(False)

    def clear(self):
        self.text_edit.setPlainText("")

    def set_text(self, text:str, style:bool):
        self.text_edit.clear()
        self.text_edit.setStyleSheet("")

        if not style:
            self.text_edit.setPlainText(text)
            return

        else:
            self.text_edit.setMarkdown(text)