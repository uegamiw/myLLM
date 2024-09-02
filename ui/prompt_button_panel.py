from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal
from PySide6.QtGui import QShortcut, QKeySequence
from setting import deliminator, n_prompt_buttons

class PromptButtonsPanel(QWidget):
    prompt_selected = Signal(str)

    def __init__(self, prompts, parent=None):
        super().__init__(parent)
        self.prompts = prompts

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        for i, (prompt_name, prompt_text) in enumerate(self.prompts.items()):
            if i+1 > n_prompt_buttons:
                break
            button = self.create_prompt_button(prompt_name, prompt_text, i)
            layout.addWidget(button)

    def create_prompt_button(self, prompt_name, prompt_text, index):
        button = QPushButton(prompt_name, self)
        prompt_text = f"{prompt_text} \n {deliminator} \n"

        def on_button_clicked(checked=False, p=prompt_text):
            self.prompt_selected.emit(p)

        button.clicked.connect(on_button_clicked)
        shortcut = QShortcut(QKeySequence(f"Ctrl+{index+1}"), self)
        shortcut.activated.connect(on_button_clicked)
        return button