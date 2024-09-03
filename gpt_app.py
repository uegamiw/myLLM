from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QSplitter,
)
from PySide6.QtCore import Qt
from ui.menu_bar import MenuBar
from ui.history_panel import HistoryPanel
from ui.main_panel import MainPanel
from config_manager import ConfigManager
from api_client_manager import APIClientManager
from setting import window_title, db_path, spacing
import database

class GPTApp(QWidget):
    def __init__(
        self, config_manager: ConfigManager, clients: APIClientManager, logger
    ):
        super().__init__()
        self.config = config_manager.config
        self.clients = clients
        self.openai_models = self.config.get("openai_models", {})
        self.anthropic_models = self.config.get("anthropic_models", {})
        self.prompts = self.config.get("prompts", {})
        self.logger = logger

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(window_title)
        self.setGeometry(50, 50, 1200, 950)
        
        # database
        self.db_manager = database.DatabaseManager(self.logger, db_path)

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(spacing)
        
        # Create a splitter
        splitter = QSplitter(Qt.Horizontal)

        # history panel
        self.history_panel = HistoryPanel(self.db_manager, self.logger)
        self.history_panel.item_selected.connect(self.show_history_item)

        # main_panel
        self.main_panel = MainPanel(self.config, self.clients, self.history_panel, self.logger)

        # Add panels to the splitter
        splitter.addWidget(self.history_panel)
        splitter.addWidget(self.main_panel)

        # Set initial sizes (optional)
        splitter.setSizes([350, 600])  # Example: history panel 300px, main panel 900px

        main_layout.addWidget(splitter)

        # Menu bar
        self.menubar = MenuBar(self, self.prompts, self.logger)
        main_layout.setMenuBar(self.menubar)
        self.menubar.prompt_selected.connect(self.main_panel.insert_prompt)

        self.setLayout(main_layout)
        self.main_panel.prompt_input_panel.textarea.setFocus()
    
    def show_history_item(self, item):
        self.main_panel.prompt_input_panel.set_text(item['query'])
        self.main_panel.output_area.set_text(item['response'])
        self.main_panel.model_selection_panel.set_selected_model(item['model'])

    def closeEvent(self, event):
        self.db_manager.close()
        self.logger.info('App Closed')
        event.accept()