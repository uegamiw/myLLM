from ui.text_edit_with_zoom import TextEditWithZoom
from time import time, sleep

class OutputArea(TextEditWithZoom):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Output will appear here.")
        self.setAcceptRichText(False)

        # flag to keep the status: counting up or not
        self.is_counting_up = False

    def clear(self):
        self.setPlainText("")

    def set_text(self, text):
        self.clear()
        self.append_text(text)
    
    def start_count_up(self):
        # display the time elapsed since this method was called
        self.is_counting_up = True
        start_time = time()

        while self.is_counting_up:
            elapsed_time = time() - start_time
            self.set_text(f"{elapsed_time} seconds elapsed")
            sleep(1)

        
