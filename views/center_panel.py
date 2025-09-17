from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt

from views.prompt_input_panel import PromptInputPanel
from views.output_area import OutputArea

from models.config_manager import Config

from utils.setting import spacing
import utils.messages as messages
from logging import Logger

class CenterPanel(QWidget):
    def __init__(self, config:Config, logger:Logger):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(spacing)
        self.main_layout.setContentsMargins(1, 1, 1, 1)
        self.config = config

        self.prompts = self.config.prompts

        self.logger = logger
        self.init_ui()
        self.output_area.set_text(messages.welcome_message, style=True)

    def init_ui(self) -> None:
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Prompt input
        self.input_panel = PromptInputPanel(self.prompts)

        # Output area
        self.output_area = OutputArea()

        splitter.addWidget(self.input_panel)
        splitter.addWidget(self.output_area)
        splitter.setSizes([300, 500])
        self.main_layout.addWidget(splitter)


    def clear_textboxes(self) -> None:
        self.input_panel.clear_text()
        self.output_area.text_edit.clear()
        self.output_area.set_text(messages.welcome_message, style=True)
        self.input_panel.textarea.setFocus()