from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtCore import Signal
from setting import deliminator

class MenuBar(QMenuBar):
    prompt_selected = Signal(str)
    def __init__(self, parent, prompts, logger):
        super().__init__(parent)
        self.prompts = prompts
        self.logger = logger
        self.setup_menu()

    def setup_menu(self):
        prompt_menu = QMenu("Prompts", self)
        self.addMenu(prompt_menu)

        if self.prompts:
            for prompt_name, prompt_text in self.prompts.items():
                prompt_text = f"{prompt_text} \n {deliminator} \n"

                action = prompt_menu.addAction(prompt_name)
                action.triggered.connect(lambda checked=False, p=prompt_text: self.insert_prompt(p))
                self.logger.debug(f"Added prompt to the menubar: {prompt_name}")

    def insert_prompt(self, prompt_text):
        self.prompt_selected.emit(prompt_text)