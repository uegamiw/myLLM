from PySide6.QtWidgets import QHBoxLayout, QRadioButton, QButtonGroup
from PySide6.QtGui import QShortcut, QKeySequence

class ModelSelectionPanel(QHBoxLayout):
    def __init__(self, openai_models, anthropic_models):
        super().__init__()
        self.model_group = QButtonGroup()

        if openai_models:
            self.add_model_buttons(openai_models)
        if anthropic_models:
            self.add_model_buttons(anthropic_models)

        if self.model_group.buttons():
            self.model_group.buttons()[0].setChecked(True)

            for i, button in enumerate(self.model_group.buttons()):
                button.shortcut = QShortcut(QKeySequence(f"Ctrl+Alt+{i+1}"), button)
                button.shortcut.activated.connect(button.click)

    def add_model_buttons(self, models):
        for model in models.keys():
            button = QRadioButton(model)
            self.addWidget(button)
            self.model_group.addButton(button)

    def selected_model(self):
        button = self.model_group.checkedButton()
        return button.text() if button else None