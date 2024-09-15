from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox

from PySide6.QtCore import QThreadPool
from views.model_selection_panel import ModelSelectionPanel
from views.action_button_panel import ActionButtonsPanel

from models.api_client_manager import APIClientManager
from models.config_manager import Config

from utils.setting import spacing

class RightPanel(QWidget):
    def __init__(self, config:Config, clients: APIClientManager, history_panel, logger):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(spacing)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.config = config

        self.openai_clients = clients.openai_client
        self.anthropic_clients = clients.anthropic_client

        self.openai_models = self.config.openai_models
        self.anthropic_models = self.config.anthropic_models
        self.prompts = self.config.prompts

        self.logger = logger
        self.history_panel = history_panel
        self.threadpool = QThreadPool()

        self.init_ui()

    def init_ui(self):

        # Model Selection
        self.model_selection_panel = ModelSelectionPanel(
            self.openai_models, self.anthropic_models, self.logger
        )
        self.layout.addWidget(self.model_selection_panel)

        self.layout.addStretch()


        # Action buttons
        self.action_buttons_panel = ActionButtonsPanel()
        self.layout.addWidget(self.action_buttons_panel)

        self.layout.addStretch()

        self.style_switch = QCheckBox()
        self.style_switch.setText("Style")
        self.style_switch.setChecked(True)
        self.layout.addWidget(self.style_switch)

    def set_temperature(self, temp):
        if temp is None:
            temp = 0
        else:
            self.model_selection_panel.temperature_slider.setValue(temp)
