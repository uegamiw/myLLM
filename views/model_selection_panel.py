from PySide6.QtWidgets import QVBoxLayout, QRadioButton, QButtonGroup, QWidget
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QLabel, QSlider
from PySide6.QtCore import Qt

class ModelSelectionPanel(QWidget):
    def __init__(self, openai_models, anthropic_models, perplexity_models, logger):
        super().__init__()
        self.logger = logger
        self.model_group = QButtonGroup()
        self.openai_models = openai_models
        self.anthropic_models = anthropic_models
        self.perplexity_models = perplexity_models

        self.ms_layout = QVBoxLayout(self)
        self.setLayout(self.ms_layout)

        self.init_ui()


    def init_ui(self):
        # insert text
        self.ms_layout.addWidget(QLabel("Select Model:"))

        if self.openai_models:
            self.add_model_buttons(self.openai_models)
        if self.anthropic_models:
            self.add_model_buttons(self.anthropic_models)
        if self.perplexity_models:
            self.add_model_buttons(self.perplexity_models)

        if self.model_group.buttons():
            self.model_group.buttons()[0].setChecked(True)

            self.shortcuts = []
            for i, button in enumerate(self.model_group.buttons()):
                shortcut = QShortcut(QKeySequence(f"Ctrl+Alt+{i+1}"), button)
                shortcut.activated.connect(button.click)
                self.shortcuts.append(shortcut)

        # set space here
        self.ms_layout.addSpacing(5)

        # Temperature
        self.ms_layout.addWidget(QLabel("Temperature:"))
        # set a slider widget for temperature
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setMinimum(0)
        self.temperature_slider.setMaximum(10)
        self.temperature_slider.setSingleStep(1)
        self.temperature_slider.setValue(0)
        self.ms_layout.addWidget(self.temperature_slider)



    def add_model_buttons(self, models):
        for model in models.keys():
            button = QRadioButton(model)
            self.ms_layout.addWidget(button)
            self.model_group.addButton(button)

    def selected_model(self):
        button = self.model_group.checkedButton()
        return button.text() if button else None
    
    def set_selected_model(self, model_name):
        for button in self.model_group.buttons():
            if button.text() == model_name:
                button.setChecked(True)
                break
        else:
            self.model_group.buttons()[0].setChecked(True)
            self.logger.warning(f"Model '{model_name}' not found in the list of models.")