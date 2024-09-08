from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt

from views.prompt_input_panel import PromptInputPanel
from views.output_area import OutputArea

from models.config_manager import Config

from utils.setting import spacing
import utils.messages as messages


class CenterPanel(QWidget):
    def __init__(self, config:Config, logger):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(spacing)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.config = config


        self.prompts = self.config.prompts

        self.logger = logger
        self.init_ui()
        self.output_area.text_edit.setHtml(messages.welcome_message)

    def init_ui(self):
        splitter = QSplitter(Qt.Vertical)

        # Prompt input
        self.input_panel = PromptInputPanel(self.prompts)

        # Output area
        self.output_area = OutputArea()

        splitter.addWidget(self.input_panel)
        splitter.addWidget(self.output_area)
        splitter.setSizes([300, 500])
        self.layout.addWidget(splitter)


    def clear_textboxes(self):
        self.input_panel.clear_text()
        self.output_area.text_edit.clear()
        self.output_area.text_edit.setHtml(messages.welcome_message)
        self.input_panel.textarea.setFocus()