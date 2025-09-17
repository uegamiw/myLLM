from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt
from views.menu_bar import MenuBar
from views.history_panel import HistoryPanel
from views.center_panel import CenterPanel
from views.right_panel import RightPanel
from models.config_manager import Config
from models.api_client_manager import APIClientManager
from models.database_manager import DatabaseManager
from utils.setting import window_title, spacing, window_geometry
from logging import Logger

class MainWindow(QMainWindow):
    def __init__(
        self, config:Config, clients: APIClientManager, db: DatabaseManager, logger:Logger
    ):
        super().__init__()
        self.config: Config = config
        self.clients: APIClientManager = clients
        self.prompts: dict = self.config.prompts
        self.db: DatabaseManager = db
        self.logger: Logger = logger

        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle(window_title)
        self.setGeometry(*window_geometry)

        # Create a central widget and set it
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(spacing)

        # Create a splitter
        splitter: QSplitter = QSplitter(Qt.Orientation.Horizontal)

        # History panel
        self.history_panel = HistoryPanel(self.db, self.logger)

        # Center panel
        self.center_panel = CenterPanel(
            self.config, self.logger
        )

        self.right_panel = RightPanel(
            self.config, self.clients, self.history_panel, self.logger
        )

        # Add panels to the splitter
        splitter.addWidget(self.history_panel)
        splitter.addWidget(self.center_panel)
        splitter.addWidget(self.right_panel)

        # Set initial sizes (optional)
        splitter.setSizes([350, 600, 200])  # Example: history panel 300px, main panel 900px

        main_layout.addWidget(splitter)

        # Menu bar
        self.menubar = MenuBar(self, self.prompts, self.logger)
        self.setMenuBar(self.menubar)

        self.center_panel.input_panel.textarea.setFocus()

    def show_history_item(self, item):
        self.center_panel.input_panel.set_text(item["query"])
        self.center_panel.output_area.set_text(item["response"])
        self.right_panel.model_selection_panel.set_selected_model(item["model"])
        # TODO: check the scripts above

    def closeEvent(self, event) -> None:
        self.db.close()
        self.logger.info("App Closed")
        event.accept()